import streamlit as st
import pandas as pd
import sys
from datetime import date

# BPM-tarieven per CO₂-uitstoot en jaar (2013-2025)
BPM_TARIEVEN = {
    2013: [(0, 95, 125), (95, 140, 150), (140, 200, 200)],
    2014: [(0, 88, 130), (88, 135, 155), (135, 180, 210)],
    2015: [(0, 82, 140), (82, 130, 165), (130, 170, 225)],
    2016: [(0, 79, 150), (79, 120, 175), (120, 160, 240)],
    2017: [(0, 76, 160), (76, 115, 185), (115, 155, 250)],
    2018: [(0, 73, 170), (73, 110, 195), (110, 150, 260)],
    2019: [(0, 70, 180), (70, 105, 205), (105, 145, 270)],
    2020: [(0, 67, 190), (67, 100, 215), (100, 140, 280)],
    2021: [(0, 65, 200), (65, 95, 225), (95, 135, 290)],
    2022: [(0, 62, 210), (62, 90, 235), (90, 130, 300)],
    2023: [(0, 60, 220), (60, 85, 245), (85, 125, 310)],
    2024: [(0, 58, 230), (58, 80, 255), (80, 120, 320)],
    2025: [(0, 55, 240), (55, 75, 265), (75, 115, 330)]
}

# Forfaitaire afschrijvingstabellen per jaar
Afschrijvingstabellen = {
    year: [0, 12, 20, 27, 33, 42, 51, 57, 62, 67, 72, 75, 78, 81] for year in range(2013, 2026)
}

# BPM berekening
@st.cache_data
def calculate_bpm(co2_emission, fuel_type, eerste_toelating):
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
    fuel_type = st.selectbox("Brandstofsoort", ["Benzine", "Diesel", "PHEV", "EV"])
    
    if st.button("Bereken BPM"):
        bruto_bpm, rest_bpm_tabel = calculate_bpm(co2_emission, fuel_type, eerste_toelating)
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
