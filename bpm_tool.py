import streamlit as st
import pandas as pd
import sys
from datetime import date

# BPM-tarieven per CO2-uitstoot categorie en jaar
BPM_TARIEVEN = {
    2013: 45.2, 2014: 45.2, 2015: 42.3, 2016: 40.0, 2017: 37.7,
    2018: 35.7, 2019: 34.2, 2020: 32.5, 2021: 31.0, 2022: 30.0,
    2023: 29.0, 2024: 28.0, 2025: 27.4
}

# Forfaitaire afschrijvingstabellen per jaar
Afschrijvingstabellen = {
    2022: [0, 12, 20, 27, 33, 42, 51, 57, 62, 67, 72, 75, 78, 81],
    2023: [0, 12, 21, 28, 34, 43, 52, 58, 63, 68, 73, 76, 79, 82],
    2024: [0, 12, 22, 29, 36, 45, 54, 60, 65, 70, 75, 78, 81, 84],
    2025: [0, 12, 23, 30, 37, 46, 55, 61, 66, 71, 76, 79, 82, 85]
}

# BPM berekening
@st.cache_data
def calculate_bpm(co2_emission, fuel_type, eerste_toelating):
    year = eerste_toelating.year
    bpm_tarieven = BPM_TARIEVEN.get(int(year), BPM_TARIEVEN[2025])
    afschrijving_tabel = Afschrijvingstabellen.get(year, Afschrijvingstabellen[2025])
    
    if eerste_toelating > date.today():
        return None, "Fout: Eerste toelating kan niet in de toekomst liggen."
    
    # Bruto BPM berekenen
    bruto_bpm = 0
    for grens, max_co2, tarief in bpm_tarieven:
        if co2_emission > grens:
            bruto_bpm = (co2_emission - grens) * tarief
    
    # Leeftijd berekenen in maanden
    today = date.today()
    leeftijd_in_maanden = max((today.year - eerste_toelating.year) * 12 + today.month - eerste_toelating.month, 0)
    
    # Afschrijvingspercentage bepalen
    afschrijving_index = min(leeftijd_in_maanden // 6, len(afschrijving_tabel) - 1)
    afschrijving_percentage = afschrijving_tabel[afschrijving_index]
    
    # Rest BPM berekenen
    rest_bpm_tabel = bruto_bpm * ((100 - afschrijving_percentage) / 100)
    
    return round(bruto_bpm, 2), round(rest_bpm_tabel, 2)

# Streamlit UI
st.set_page_config(page_title="BPM Taxatie Calculator", layout="wide")
st.title("BPM Taxatie Indicatie Calculator")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.header("Bereken BPM")
    eerste_toelating = st.date_input("Eerste toelating voertuig", min_value=date(2013, 1, 1), max_value=date.today())
    
    co2_emission = st.number_input("CO₂-uitstoot (g/km)", min_value=0, max_value=500, value=100)
    fuel_type = st.selectbox("BPM-tarief jaar", list(BPM_TARIEVEN.keys()))
    
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
    ("Rest BPM op basis van Afschrijvingstabel", "blue", st.session_state.get("rest_bpm_tabel", 0))
]:
    formatted_value = f"{value:.2f}" if isinstance(value, (int, float)) else value
    st.markdown(f"""
    <div style='text-align: left; font-weight: bold; padding-top: 5px;'>{label}</div>
    <div style='padding: 10px; border-radius: 5px; border: 2px solid {color}; width: 50%; text-align: left; font-size: 18px;'>
        {formatted_value}
    </div>
    """, unsafe_allow_html=True)

st.write(f"Python versie: {sys.version}")
