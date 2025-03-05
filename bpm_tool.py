import streamlit as st
import pandas as pd
import sys
from datetime import date

# BPM-tarieven per CO₂-uitstoot en jaar (2013-2025)
BPM_TARIEVEN = {
    2013: [(0, 95, 12.52), (96, 140, 25.57), (141, 200, 50.14)],
    2014: [(0, 95, 13.00), (96, 140, 26.50), (141, 200, 52.00)],
    2015: [(0, 95, 13.50), (96, 140, 27.45), (141, 200, 54.00)],
    2016: [(0, 95, 14.00), (96, 140, 28.50), (141, 200, 56.00)],
    2017: [(0, 95, 14.50), (96, 140, 29.50), (141, 200, 58.00)],
    2018: [(0, 95, 15.00), (96, 140, 30.50), (141, 200, 60.00)],
    2019: [(0, 95, 15.50), (96, 140, 31.50), (141, 200, 62.00)],
    2020: [(0, 95, 16.00), (96, 140, 32.50), (141, 200, 64.00)],
    2021: [(0, 95, 16.50), (96, 140, 33.50), (141, 200, 66.00)],
    2022: [(0, 95, 17.00), (96, 140, 34.50), (141, 200, 68.00)],
    2023: [(0, 95, 17.50), (96, 140, 35.50), (141, 200, 70.00)],
    2024: [(0, 95, 18.00), (96, 140, 36.50), (141, 200, 72.00)],
    2025: [(0, 95, 18.50), (96, 140, 37.50), (141, 200, 74.00)]
}

# Forfaitaire afschrijvingstabellen per jaar
Afschrijvingstabellen = {
    2013: [0, 12, 20, 27, 33, 42, 51, 57, 62, 67, 72, 75, 78, 81],
    2014: [0, 13, 21, 28, 34, 43, 52, 58, 63, 68, 73, 76, 79, 82],
    2015: [0, 14, 22, 29, 35, 44, 53, 59, 64, 69, 74, 77, 80, 83],
    2016: [0, 15, 23, 30, 36, 45, 54, 60, 65, 70, 75, 78, 81, 84],
    2017: [0, 16, 24, 31, 37, 46, 55, 61, 66, 71, 76, 79, 82, 85],
    2018: [0, 17, 25, 32, 38, 47, 56, 62, 67, 72, 77, 80, 83, 86],
    2019: [0, 18, 26, 33, 39, 48, 57, 63, 68, 73, 78, 81, 84, 87],
    2020: [0, 19, 27, 34, 40, 49, 58, 64, 69, 74, 79, 82, 85, 88],
    2021: [0, 20, 28, 35, 41, 50, 59, 65, 70, 75, 80, 83, 86, 89],
    2022: [0, 21, 29, 36, 42, 51, 60, 66, 71, 76, 81, 84, 87, 90],
    2023: [0, 22, 30, 37, 43, 52, 61, 67, 72, 77, 82, 85, 88, 91],
    2024: [0, 23, 31, 38, 44, 53, 62, 68, 73, 78, 83, 86, 89, 92],
    2025: [0, 24, 32, 39, 45, 54, 63, 69, 74, 79, 84, 87, 90, 93]
}

# UI voor invoer
st.set_page_config(page_title="BPM Taxatie Calculator", layout="wide")
st.title("BPM Taxatie Indicatie Calculator")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.header("Bereken BPM")
    eerste_toelating = st.date_input("Eerste toelating voertuig", min_value=date(2013, 1, 1), max_value=date.today())
    co2_emission = st.number_input("CO₂-uitstoot (g/km)", min_value=0, max_value=500, value=100)
    fuel_type = st.selectbox("Brandstofsoort", ["Benzine", "Diesel", "PHEV", "EV"])
    
    if st.button("Bereken BPM"):
        bruto_bpm, rest_bpm_tabel = calculate_bpm(co2_emission, eerste_toelating)
        st.session_state.bruto_bpm = bruto_bpm
        st.session_state.rest_bpm_tabel = rest_bpm_tabel
        st.rerun()

# UI voor resultaten
st.subheader("Resultaten")
for label, color, value in [
    ("Historische Bruto BPM", "green", st.session_state.get("bruto_bpm", 0)),
    ("Rest BPM op basis van Afschrijvingstabel", "blue", st.session_state.get("rest_bpm_tabel", 0))
]:
    st.write(f"{label}: €{value:.2f}")
