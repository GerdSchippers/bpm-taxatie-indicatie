import streamlit as st
import pandas as pd
import sys
from datetime import date

# Laad BPM-gegevens uit pdf
@st.cache_data
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

# Forfaitaire afschrijvingstabel
@st.cache_data
def forfaitaire_afschrijving(leeftijd):
    afschrijvingstabellen = [
        (0, 1, 0, 12),
        (1, 3, 12, 4),
        (3, 5, 20, 3.5),
        (5, 9, 27, 1.5),
        (9, 18, 33, 1),
        (18, 30, 42, 0.75),
        (30, 42, 51, 0.5),
        (42, 54, 57, 0.42),
        (54, 66, 62, 0.42),
        (66, 78, 67, 0.42),
        (78, 90, 72, 0.25),
        (90, 102, 75, 0.25),
        (102, 114, 78, 0.25),
        (114, 999, 81, 0.19)
    ]
    
    for min_m, max_m, base, per_m in afschrijvingstabellen:
        if leeftijd >= min_m and leeftijd < max_m:
            return base + ((leeftijd - min_m) * per_m)
    return 81  # Max afschrijving

# BPM berekening
@st.cache_data
def calculate_bpm(co2_emission, fuel_type, eerste_toelating):
    df = load_bpm_data()
    year = eerste_toelating.year
    row = df[df["Jaar"] == year].iloc[0]
    
    if eerste_toelating > date.today():
        return None, "Fout: Eerste toelating kan niet in de toekomst liggen."
    
    base_bpm = 0
    if co2_emission > row["BPM Vrijstelling (g/km CO₂)"]:
        base_bpm = (co2_emission - row["BPM Vrijstelling (g/km CO₂)"]) * row["Eerste schijf (€ per gram)"]
        if co2_emission > 150:
            base_bpm += (co2_emission - 150) * (row["Hoogste schijf (€ per gram)"] - row["Eerste schijf (€ per gram)"])
    
    diesel_surcharge = 0
    if fuel_type == "Diesel" and co2_emission > row["Dieseltoeslag (g/km drempel)"]:
        diesel_surcharge = (co2_emission - row["Dieseltoeslag (g/km drempel)"]) * row["Dieseltoeslag (€ per gram)"]
    
    bruto_bpm = base_bpm + diesel_surcharge
    
    # Leeftijd berekenen op basis van eerste toelating
    today = date.today()
    leeftijd_in_maanden = max((today.year - eerste_toelating.year) * 12 + today.month - eerste_toelating.month, 0)
    afschrijving_percentage = forfaitaire_afschrijving(leeftijd_in_maanden)
    rest_bpm_tabel = bruto_bpm * ((100 - afschrijving_percentage) / 100)
    
    return max(bruto_bpm, 0), max(rest_bpm_tabel, 0)

# Streamlit UI
st.set_page_config(page_title="BPM Taxatie Calculator", layout="wide")
st.title("BPM Taxatie Indicatie Calculator")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.header("Bereken BPM")
    eerste_toelating = st.date_input("Eerste toelating voertuig (dag/maand/jaar)", min_value=date(1990, 1, 1), max_value=date.today())
    co2_emission = st.number_input("CO₂-uitstoot (g/km)", min_value=0, max_value=500, value=100)
    fuel_type = st.selectbox("Brandstofsoort", ["Benzine", "Diesel", "PHEV", "EV"])
    
    if st.button("Bereken BPM"):
        bruto_bpm, rest_bpm_tabel = calculate_bpm(co2_emission, fuel_type, eerste_toelating)
        if bruto_bpm is None:
            st.error(rest_bpm_tabel)
        else:
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
    formatted_value = f"{value:.2f}" if isinstance(value, (int, float)) else value
    st.markdown(f"""
    <div style='text-align: left; font-weight: bold; padding-top: 5px;'>{label}</div>
    <div style='padding: 10px; border-radius: 5px; border: 2px solid {color}; width: 50%; text-align: left; font-size: 18px;'>
        {formatted_value}
    </div>
    """, unsafe_allow_html=True)

st.write(f"Python versie: {sys.version}")
