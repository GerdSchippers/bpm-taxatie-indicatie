import streamlit as st
import pandas as pd
import sys
from datetime import date

# BPM-tarieven per CO₂-uitstoot en jaar (2013-2025)
BPM_TARIEVEN = {
    2013: [(0, 100, 14.52)],
    2014: [(0, 100, 15.00)],
    2015: [(0, 100, 15.50)],
    2016: [(0, 100, 16.00)],
    2017: [(0, 100, 16.50)],
    2018: [(0, 100, 17.00)],
    2019: [(0, 100, 17.50)],
    2020: [(0, 100, 18.00)],
    2021: [(0, 100, 18.50)],
    2022: [(0, 100, 19.00)],
    2023: [(0, 100, 19.50)],
    2024: [(0, 100, 20.00)],
    2025: [(0, 100, 20.50)]
}

# Forfaitaire afschrijvingstabellen per jaar
Afschrijvingstabellen = {
    year: [0, 12, 20, 27, 33, 42, 51, 57, 62, 67, 72, 75, 78, 81] for year in range(2013, 2026)
}

# BPM berekening
@st.cache_data
def calculate_bpm(co2_emission, eerste_toelating):
    year = eerste_toelating.year
    bpm_tarieven = BPM_TARIEVEN.get(year, BPM_TARIEVEN[2025])
    afschrijving_tabel = Afschrijvingstabellen.get(year, Afschrijvingstabellen[2025])
    
    bruto_bpm = sum((co2_emission - grens) * tarief for grens, max_co2, tarief in bpm_tarieven if co2_emission > grens)
    
    today = date.today()
    leeftijd_in_maanden = max((today.year - eerste_toelating.year) * 12 + today.month - eerste_toelating.month, 0)
    afschrijving_index = min(leeftijd_in_maanden // 6, len(afschrijving_tabel) - 1)
    afschrijving_percentage = afschrijving_tabel[afschrijving_index]
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
    
    if st.button("Bereken BPM"):
        bruto_bpm, rest_bpm_tabel = calculate_bpm(co2_emission, eerste_toelating)
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
