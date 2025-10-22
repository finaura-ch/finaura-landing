# FINAURA UI Demo — v1.0.0 (2025-10-18, Europe/Zurich)
# CHANGE: Initiales UX-Template mit Header, Cards, Spalten-Layout, Footer.
# Ablagepfad: ~/Downloads/finaura_app  (verknüpft mit  ~/Documents/Finaura/app)
# Install:    pip install streamlit altair pandas
# Run:        streamlit run finaura_ui_demo_v1_0_0.py

from __future__ import annotations

__version__ = "1.0.0"

import streamlit as st
import pandas as pd
import altair as alt

# FINAURA UI-Module (du hast die Datei bereits hinzugefügt)
from finaura_ui import render_header, finaura_card

# ---- App-Setup ----
st.set_page_config(page_title=f"FINAURA UI Demo v{__version__}", layout="wide")
st.sidebar.markdown(f"**FINAURA** — UI Demo v{__version__}")
st.sidebar.caption("Ablage: ~/Downloads/finaura_app → ~/Documents/Finaura/app")

# ---- Header ----
render_header("UI Demo", version=__version__,
              subtitle="Einheitliches FINAURA-Design als Template",
              logo="🎛️")

# ---- Intro Cards ----
finaura_card("Willkommen", "Dieses Template zeigt das FINAURA-Designsystem (Header, Cards, Spalten & Chart).", tone="info")
finaura_card("Tipp", "Nutze diese Datei als Startpunkt für neue Module (IK, BVG, 3a, Budget, etc.).", tone="success")

# ---- Layout: Zwei Spalten ----
left, right = st.columns([1, 1])

with left:
    st.subheader("📂 Links: Interaktionen / Uploads")
    finaura_card("Upload", "Hier könnten deine Uploader, Formulare oder Filter stehen.", tone="info")
    uploaded = st.file_uploader("Beispiel-Upload (CSV)", type=["csv"])
    if uploaded:
        df_up = pd.read_csv(uploaded)
        st.dataframe(df_up, use_container_width=True)

with right:
    st.subheader("📈 Rechts: Auswertung / Visualisierung")
    # Beispiel-Daten:
    df = pd.DataFrame({
        "Jahr": [2019, 2020, 2021, 2022, 2023],
        "Wert": [80, 95, 90, 110, 120],
    })
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(x="Jahr:O", y="Wert:Q", tooltip=["Jahr", "Wert"])
        .properties(height=280)
    )
    st.altair_chart(chart, use_container_width=True)
    finaura_card("Hinweis", "Rechts können Tabellen, Charts, KPIs etc. erscheinen.", tone="warning")

# ---- Footer ----
st.markdown("---")
st.caption("© FINAURA — Swiss Precision UX · Dieses Template ist die Grundlage für alle zukünftigen Module.")

