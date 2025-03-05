import streamlit as st
import pandas as pd
import sys
from datetime import date

# BPM-tarieven per CO₂-uitstoot en jaar (2013-2025)
BPM_TARIEVEN = {
    2013: [(0, 96, 12.52), (96, 140, 25.57), (140, 200, 50.14)],
    2014: [(0, 96, 13.00), (96, 140, 26.50), (140, 200, 52.00)],
    2015: [(0, 96, 13.50), (96, 140, 27.45), (140, 200, 54.00)],
    2016: [(0, 96, 14.00), (96, 140, 28.50), (140, 200, 56.00)],
    2017: [(0, 96, 14.50), (96, 140, 29.50), (140, 200, 58.00)],
    2018: [(0, 96, 15.00), (96, 140, 30.50), (140, 200, 60.00)],
    2019: [(0, 96, 15.50), (96, 140, 31.50), (140, 200, 62.00)],
    2020: [(0, 96, 16.00), (96, 140, 32.50), (140, 200, 64.00)],import streamlit as st
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

# BPM berekening
@st.cache_data
def calculate_bpm(co2_emission, eerste_toelating):
    year = eerste_toelating.year
    bpm_tarieven = BPM_TARIEVEN.get(year, BPM_TARIEVEN[2025])
    afschrijving_tabel = Afschrijvingstabellen.get(year, Afschrijvingstabellen[2025])
    
    bruto_bpm = sum((min(co2_emission, max_co2) - grens) * tarief for grens, max_co2, tarief in bpm_tarieven if co2_emission > grens)
    
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

    2021: [(0, 96, 16.50), (96, 140, 33.50), (140, 200, 66.00)],
    2022: [(0, 96, 17.00), (96, 140, 34.50), (140, 200, 68.00)],
    2023: [(0, 96, 17.50), (96, 140, 35.50), (140, 200, 70.00)],
    2024: [(0, 96, 18.00), (96, 140, 36.50), (140, 200, 72.00)],
    2025: [(0, 96, 18.50), (96, 140, 37.50), (140, 200, 74.00)]
}

# Forfaitaire afschrijvingstabellen per jaar
Afschrijvingstabellen = {
    2013: [0, 12, 19, 26, 32, 40, 48, 54, 59, 64, 69, 72, 75, 78],
    2014: [0, 12, 20, 27, 33, 41, 49, 55, 60, 65, 70, 73, 76, 79],
    2015: [0, 12, 21, 28, 34, 42, 50, 56, 61, 66, 71, 74, 77, 80],
    2016: [0, 12, 22, 29, 35, 43, 51, 57, 62, 67, 72, 75, 78, 81],
    2017: [0, 12, 23, 30, 36, 44, 52, 58, 63, 68, 73, 76, 79, 82],
    2018: [0, 12, 24, 31, 37, 45, 53, 59, 64, 69, 74, 77, 80, 83],
    2019: [0, 12, 25, 32, 38, 46, 54, 60, 65, 70, 75, 78, 81, 84],
    2020: [0, 12, 26, 33, 39, 47, 55, 61, 66, 71, 76, 79, 82, 85],
    2021: [0, 12, 27, 34, 40, 48, 56, 62, 67, 72, 77, 80, 83, 86],
    2022: [0, 12, 28, 35, 41, 49, 57, 63, 68, 73, 78, 81, 84, 87],
    2023: [0, 12, 29, 36, 42, 50, 58, 64, 69, 74, 79, 82, 85, 88],
    2024: [0, 12, 30, 37, 43, 51, 59, 65, 70, 75, 80, 83, 86, 89],
    2025: [0, 12, 31, 38, 44, 52, 60, 66, 71, 76, 81, 84, 87, 90]
}

# BPM berekening
@st.cache_data
def calculate_bpm(co2_emission, eerste_toelating):
    year = eerste_toelating.year
    bpm_tarieven = BPM_TARIEVEN.get(year, BPM_TARIEVEN[2025])
    afschrijving_tabel = Afschrijvingstabellen.get(year, Afschrijvingstabellen[2025])
    
    bruto_bpm = sum((min(co2_emission, max_co2) - grens) * tarief for grens, max_co2, tarief in bpm_tarieven if co2_emission > grens)
    
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
