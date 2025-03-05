import streamlit as st
import pandas as pd

def load_bpm_data():
    data = {
        "Jaar": list(range(2013, 2026)),
        "Testmethode": [
            "NEDC", "NEDC", "NEDC", "NEDC", "NEDC", "NEDC", "NEDC/WLTP", "NEDC/WLTP", 
            "WLTP", "WLTP", "WLTP", "WLTP", "WLTP"
        ],
        "BPM Vrijstelling (g/km CO₂)": [95, 89, 82, 79, 76, 73, 71, 71, 0, 0, 0, 0, 0],
        "Eerste schijf (€ per gram)": [125, 126, 126, 128, 130, 132, 133, 134, 1, 2, 2, 2, 2],
        "Hoogste schijf (€ per gram)": [551, 553, 555, 560, 567, 573, 580, 585, 408, 424, 432, 449, 568],
        "Dieseltoeslag (g/km drempel)": [70, 70, 67, 67, 67, 67, 67, 67, 80, 77, 74, 71, 65],
        "Dieseltoeslag (€ per gram)": [56, 72, 86, 86, 89, 89, 90, 90, 78, 83, 86, 95, 105]
    }
    return pd.DataFrame(data)

def forfaitaire_afschrijving(leeftijd):
    """Bereken de afschrijving volgens de forfaitaire tabel."""
    afschrijvingstabellen = {
        1: 0.91, 2: 0.81, 3: 0.72, 4: 0.63, 5: 0.55, 6: 0.47,
        7: 0.40, 8: 0.33, 9: 0.27, 10: 0.21, 11: 0.16, 12: 0.11
    }
    return afschrijvingstabellen.get(leeftijd, 0.11)  # Minimaal 11% restwaarde

def calculate_bpm(year, co2_emission, fuel_type, leeftijd):
    df = load_bpm_data()
    row = df[df["Jaar"] == year].iloc[0]
    
    # Stap 1: Bruto BPM berekenen zonder afschrijving
    base_bpm = 0
    if co2_emission > row["BPM Vrijstelling (g/km CO₂)"]:
        base_bpm = (co2_emission - row["BPM Vrijstelling (g/km CO₂)"]) * row["Eerste schijf (€ per gram)"]
        if co2_emission > 150:
            base_bpm += (co2_emission - 150) * (row["Hoogste schijf (€ per gram)"] - row["Eerste schijf (€ per gram)"])
    
    diesel_surcharge = 0
    if fuel_type == "Diesel" and co2_emission > row["Dieseltoeslag (g/km drempel)"]:
        diesel_surcharge = (co2_emission - row["Dieseltoeslag (g/km drempel)"]) * row["Dieseltoeslag (€ per gram)"]
    
    bruto_bpm = base_bpm + diesel_surcharge
    
    # Stap 2: Correcte afschrijving toepassen
    afschrijving_factor = forfaitaire_afschrijving(leeftijd)
    rest_bpm_tabel = bruto_bpm * (1 - afschrijving_factor)  # Correcte toepassing van afschrijving
    
    return max(bruto_bpm, 0), max(rest_bpm_tabel, 0)  # Zorg ervoor dat BPM niet negatief wordt

def main():
    st.set_page_config(page_title="BPM Taxatie Indicatie Calculator", layout="wide")
    
    st.title("BPM Taxatie Indicatie Calculator")
    
    if "bruto_bpm" not in st.session_state:
        st.session_state.bruto_bpm = None
        st.session_state.rest_bpm_tabel = None
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.header("Bereken BPM")
        year = st.selectbox("Selecteer Jaar", list(range(2013, 2026)))
        co2_emission = st.number_input("CO₂-uitstoot (g/km)", min_value=0, max_value=500, value=100)
        fuel_type = st.selectbox("Brandstofsoort", ["Benzine", "Diesel", "PHEV", "EV"])
        leeftijd = st.number_input("Leeftijd voertuig (maanden)", min_value=1, max_value=12, value=6)
        
        if st.button("Bereken BPM"):
            st.session_state.bruto_bpm, st.session_state.rest_bpm_tabel = calculate_bpm(year, co2_emission, fuel_type, leeftijd)
            st.experimental_rerun()
        
    if st.session_state.bruto_bpm is not None:
        st.subheader("Resultaten")
        st.write(f"**Historische Bruto BPM:** €{st.session_state.bruto_bpm:,.2f}")
        st.write(f"**Actuele Bruto BPM:** Nog niet beschikbaar")
        st.write(f"**Rest BPM op basis van Afschrijvingstabel:** €{st.session_state.rest_bpm_tabel:,.2f}")
        st.write(f"**Rest BPM op basis van Taxatie:** Later beschikbaar")

if __name__ == "__main__":
    main()
