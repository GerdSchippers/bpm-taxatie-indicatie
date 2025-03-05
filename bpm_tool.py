import streamlit as st
import pandas as pd
import sys

# Laad BPM-gegevens uit pdf
@st.cache_data
def load_bpm_data():
    # BPM tarieven op basis van de PDF
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

# Afschrijvingstabel
@st.cache_data
def forfaitaire_afschrijving(leeftijd):
    afschrijvingstabellen = {
        1: 0.91, 2: 0.81, 3: 0.72, 4: 0.63, 5: 0.55, 6: 0.47,
        7: 0.40, 8: 0.33, 9: 0.27, 10: 0.21, 11: 0.16, 12: 0.11
    }
    return afschrijvingstabellen.get(leeftijd, 0.11)

# BPM berekening
@st.cache_data
def calculate_bpm(year, co2_emission, fuel_type, leeftijd):
    df = load_bpm_data()
    row = df[df["Jaar"] == year].iloc[0]
    
    base_bpm = 0
    if co2_emission > row["BPM Vrijstelling (g/km CO₂)"]:
        base_bpm = (co2_emission - row["BPM Vrijstelling (g/km CO₂)"]) * row["Eerste schijf (€ per gram)"]
        if co2_emission > 150:
            base_bpm += (co2_emission - 150) * (row["Hoogste schijf (€ per gram)"] - row["Eerste schijf (€ per gram)"])
    
    diesel_surcharge = 0
    if fuel_type == "Diesel" and co2_emission > row["Dieseltoeslag (g/km drempel)"]:
        diesel_surcharge = (co2_emission - row["Dieseltoeslag (g/km drempel)"]) * row["Dieseltoeslag (€ per gram)"]
    
    bruto_bpm = base_bpm + diesel_surcharge
    afschrijving_factor = forfaitaire_afschrijving(leeftijd)
    rest_bpm_tabel = bruto_bpm * (1 - afschrijving_factor)
    
    return max(bruto_bpm, 0), max(rest_bpm_tabel, 0)

# Streamlit UI
st.set_page_config(page_title="BPM Taxatie Calculator", layout="wide")
st.title("BPM Taxatie Indicatie Calculator")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.header("Bereken BPM")
    year = st.selectbox("Selecteer Jaar", list(range(2013, 2026)))
    co2_emission = st.number_input("CO₂-uitstoot (g/km)", min_value=0, max_value=500, value=100)
    fuel_type = st.selectbox("Brandstofsoort", ["Benzine", "Diesel", "PHEV", "EV"])
    leeftijd = st.number_input("Leeftijd voertuig (maanden)", min_value=1, max_value=12, value=6)
    
    if st.button("Bereken BPM"):
        bruto_bpm, rest_bpm_tabel = calculate_bpm(year, co2_emission, fuel_type, leeftijd)
        st.session_state.bruto_bpm = bruto_bpm
        st.session_state.rest_bpm_tabel = rest_bpm_tabel
        st.rerun()

st.subheader("Resultaten")
for label, color, value in [
    ("Historische Bruto BPM", "green", st.session_state.get("bruto_bpm", 0)),
    ("Actuele Bruto BPM", "orange", "Nog niet beschikbaar"),
    ("Rest BPM op basis van Afschrijvingstabel", "blue", st.session_state.get("rest_bpm_tabel", 0)),
    ("Rest BPM op basis van Taxatie", "red", "Later beschikbaar")
]:
    st.markdown(f"""
    <div style='padding: 10px; border-radius: 5px; border: 2px solid {color}; width: 100%; text-align: center;'>
        <b>{label}</b><br>
        {value}
    </div>
    """, unsafe_allow_html=True)

st.write(f"Python versie: {sys.version}")
