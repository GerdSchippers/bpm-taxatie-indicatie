import streamlit as st
import pandas as pd
import sys
from datetime import date

# BPM-tarieven per CO₂-uitstoot categorie en jaar (2013-2025)
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
    2013: [0, 12, 20, 27, 33, 42, 51, 57, 62, 67, 72, 75, 78, 81],
    2014: [0, 12, 21, 28, 34, 43, 52, 58, 63, 68, 73, 76, 79, 82],
    2015: [0, 12, 22, 29, 36, 45, 54, 60, 65, 70, 75, 78, 81, 84],
    2016: [0, 12, 23, 30, 37, 46, 55, 61, 66, 71, 76, 79, 82, 85],
    2017: [0, 12, 24, 31, 38, 47, 56, 62, 67, 72, 77, 80, 83, 86],
    2018: [0, 12, 25, 32, 39, 48, 57, 63, 68, 73, 78, 81, 84, 87],
    2019: [0, 12, 26, 33, 40, 49, 58, 64, 69, 74, 79, 82, 85, 88],
    2020: [0, 12, 27, 34, 41, 50, 59, 65, 70, 75, 80, 83, 86, 89],
    2021: [0, 12, 28, 35, 42, 51, 60, 66, 71, 76, 81, 84, 87, 90],
    2022: [0, 12, 29, 36, 43, 52, 61, 67, 72, 77, 82, 85, 88, 91],
    2023: [0, 12, 30, 37, 44, 53, 62, 68, 73, 78, 83, 86, 89, 92],
    2024: [0, 12, 31, 38, 45, 54, 63, 69, 74, 79, 84, 87, 90, 93],
    2025: [0, 12, 32, 39, 46, 55, 64, 70, 75, 80, 85, 88, 91, 94]
}

# BPM berekening
@st.cache_data
def calculate_bpm(co2_emission, fuel_type, eerste_toelating):
    year = eerste_toelating.year
    bpm_tarieven = BPM_TARIEVEN.get(year, [(0, 95, 125)])
    afschrijving_tabel = Afschrijvingstabellen.get(year, Afschrijvingstabellen[2025])
    
    bruto_bpm = sum((co2_emission - grens) * tarief for grens, max_co2, tarief in bpm_tarieven if co2_emission > grens)
    
    today = date.today()
    leeftijd_in_maanden = max((today.year - eerste_toelating.year) * 12 + today.month - eerste_toelating.month, 0)
    afschrijving_index = min(leeftijd_in_maanden // 6, len(afschrijving_tabel) - 1)
    afschrijving_percentage = afschrijving_tabel[afschrijving_index]
    rest_bpm_tabel = bruto_bpm * ((100 - afschrijving_percentage) / 100)
    
    return round(bruto_bpm, 2), round(rest_bpm_tabel, 2)

# UI wordt hier toegevoegd
