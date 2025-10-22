# FINAURA – AHV Vorbezug (Free Flagship)
# Version: 0.1.0    Date: 2025-10-20 (Europe/Zurich)
# Change: Initial public free flagship for AHV-Vorbezug (hyper-simpel UI, monatsgenau, Übergangsgeneration-Option).
# Project path: ~/Documents/Finaura/app
#
# QUICK START (copy/paste or run in terminal):
#   pip install streamlit altair pandas
#   streamlit run finaura_ahv_vorbezug_app_v0_1_0.py

from __future__ import annotations

__version__ = "0.1.0"

import math
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

# -----------------------------
# Swiss Precision – UI Settings
# -----------------------------
st.set_page_config(page_title="FINAURA – AHV Vorbezug (Free)", page_icon="🇨🇭", layout="wide")

# Minimalist Swiss Fintech styling
SWISS_BLUE = "#155E9A"
SWISS_GREY = "#E9EDF2"

# Custom CSS for clean look and 'disabled' 65 chip
st.markdown(f"""
<style>
    .title {{
        font-weight: 700; font-size: 26px; letter-spacing: 0.2px;
    }}
    .subtitle {{
        color: #4A5568; font-size: 14px;
    }}
    .chip {{ 
        display: inline-block; padding: 10px 16px; border-radius: 999px;
        margin-right: 8px; font-weight: 600; border: 1px solid {SWISS_BLUE};
        cursor: pointer; user-select: none;
    }}
    .chip.active {{ background: {SWISS_BLUE}; color: white; }}
    .chip.inactive {{ background: white; color: {SWISS_BLUE}; }}
    .chip.disabled {{ background: {SWISS_GREY}; color: #7B8694; border-color: {SWISS_GREY}; cursor: not-allowed; }}
    .hint {{ color:#6B7280; font-size: 12px; }}
    .muted-badge {{ background:{SWISS_GREY}; color:#4B5563; border-radius:12px; padding:2px 8px; font-size:12px; margin-left:6px; }}
    .metric {{ font-size: 18px; font-weight: 700; }}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>FINAURA · AHV Vorbezug (Free)</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Hyper-simpel. Monatsgenau. Übergangsgeneration berücksichtigbar. Swiss Precision.</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ℹ️ Info")
    st.write(f"Version **{__version__}** · Stand **2025-10-20** (Europe/Zurich)")
    st.write("Dies ist die freie Flagship-Version. Für Detailfälle folgt eine Pro-Version.")
    st.markdown("---")
    st.write("**Hinweis zur Übergangsgeneration**")
    st.caption("Die monatliche Reduktion kann je nach Jahrgang abweichen. Hier kannst du den Monats‑Satz anpassen.")

# -----------------------------
# Inputs (left) · Output (right)
# -----------------------------
left, right = st.columns([0.45, 0.55])

with left:
    st.markdown("#### Frühbezugsalter")
    # Age selection logic with two active chips (63/64) and a disabled 65 chip as visual reference
    if "age_choice" not in st.session_state:
        st.session_state.age_choice = 64  # sensible default

    cols = st.columns(3)
    if cols[0].button("63", use_container_width=True):
        st.session_state.age_choice = 63
    if cols[1].button("64", use_container_width=True):
        st.session_state.age_choice = 64
    cols[2].button("65 (Referenz)", use_container_width=True, disabled=True)

    st.markdown(
        f"<div class='hint'>Nur 63 oder 64 sind wählbar. 65 ist Referenz (grau).</div>",
        unsafe_allow_html=True
    )

    # Monthly selection within chosen start year (0–11 months)
    st.markdown("#### Monat im Startjahr (Übergangsgeneration)")
    month_in_year = st.select_slider("Monate", options=list(range(0, 12)), value=0, label_visibility="collapsed")
    st.caption(f"Startalter: **{st.session_state.age_choice} Jahre {month_in_year} Monate**")

    # Life expectancy slider
    st.markdown("#### Planungshorizont / Lebenserwartung")
    life_expectancy = st.slider("Alter in Jahren", min_value=75, max_value=100, value=85, step=1)

    # Base monthly pension at 65 (in CHF) – optional, affects absolute values, not break-even
    st.markdown("#### Persönliche AHV-Monatsrente (bei regulär 65)")
    rente_65 = st.number_input("CHF pro Monat (brutto)", min_value=500, max_value=4000, value=2200, step=50)

    # Reduction settings
    st.markdown("#### Reduktionssatz (monatsgenau)")
    col_r1, col_r2 = st.columns([0.6, 0.4])
    with col_r1:
        use_custom_transition = st.checkbox("Übergangsgeneration / individueller Monats‑Satz", value=False)
    with col_r2:
        # default ~6.8%/12 ≈ 0.566̅% pro Monat
        monthly_reduction_pct = st.number_input(
            "Satz % pro Monat",
            value=round(6.8 / 12, 4),
            step=0.01,
            format="%.4f",
            help="Typisch ca. 6.8% pro Jahr ⇒ ~0.5667% pro Monat. Übergangsjahrgänge können abweichen."
        )

    st.markdown("---")
    st.markdown("#### Annahmen (einfach gehalten)")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        inflation_adj = st.checkbox("Inflation ignorieren (Standard)", value=True)
    with col_a2:
        compounding = st.checkbox("Zinseszinseffekt ignorieren (Standard)", value=True)

# -----------------------------
# Core Calculations
# -----------------------------

REGULAR_AGE = 65
base_age_years = int(st.session_state.age_choice)
base_age_months = month_in_year

# months early = (65y0m) - (base_year + base_month) in months
months_early = (REGULAR_AGE - base_age_years) * 12 - base_age_months
months_early = max(0, min(24, months_early))  # clamp to [0, 24]

# reduction factor
monthly_rate = monthly_reduction_pct / 100.0  # convert to decimal
reduction_total = months_early * monthly_rate  # linear monthly interpolation

# Ensure reduction doesn't exceed a reasonable cap (e.g., ~14% for 24 months per current practice)
reduction_total = min(reduction_total, 0.20)  # safety cap at 20%

benefit_regular = rente_65
benefit_early = benefit_regular * (1 - reduction_total)

# Build monthly timeline from min(start, 65) to life_expectancy
start_age_months_total = base_age_years * 12 + base_age_months
regular_start_months_total = REGULAR_AGE * 12

end_age_months_total = life_expectancy * 12

ages_month = np.arange(min(start_age_months_total, regular_start_months_total), end_age_months_total + 1)

# Cashflows per month
cf_early = np.where(ages_month >= start_age_months_total, benefit_early, 0.0)
cf_regular = np.where(ages_month >= regular_start_months_total, benefit_regular, 0.0)

cum_early = np.cumsum(cf_early)
cum_regular = np.cumsum(cf_regular)

# Find break-even (first month where early >= regular), if any
breakeven_idx = None
diff = cum_early - cum_regular
ge_idx = np.where(diff >= 0)[0]
if ge_idx.size > 0:
    breakeven_idx = ge_idx[0]
    breakeven_age_months_total = ages_month[breakeven_idx]
    be_years = breakeven_age_months_total // 12
    be_months = int(breakeven_age_months_total % 12)
else:
    be_years = None
    be_months = None

# Build DataFrame for chart
df = pd.DataFrame({{
    "age_months": ages_month,
    "age_years": ages_month / 12.0,
    "Vorbezug (kumuliert)": cum_early,
    "Regulär (kumuliert)": cum_regular
}})

# -----------------------------
# Visualization
# -----------------------------
with right:
    st.markdown("### Vergleich: Vorbezug vs. regulär")
    base = alt.Chart(df).mark_line(strokeWidth=2).encode(
        x=alt.X("age_years:Q", axis=alt.Axis(title="Alter (Jahre)")),
        y=alt.Y("value:Q", axis=alt.Axis(title="Kumulierte AHV (CHF)")),
        color=alt.Color("variable:N", legend=alt.Legend(title="Variante"))
    ).transform_fold(
        ["Vorbezug (kumuliert)", "Regulär (kumuliert)"],
        as_=["variable", "value"]
    )

    chart = base

    # Add dashed vertical line at breakeven
    if be_years is not None:
        vline = alt.Chart(pd.DataFrame({{"x":[be_years + be_months/12.0]}})).mark_rule(strokeDash=[6,4]).encode(
            x="x:Q"
        )
        chart = chart + vline

    st.altair_chart(chart.interactive(), use_container_width=True)

    # Metrics row
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown("<div class='metric'>Frühbezugsalter</div>", unsafe_allow_html=True)
        st.write(f"**{base_age_years} Jahre {base_age_months} Monate**")
    with m2:
        st.markdown("<div class='metric'>Reduktion gesamt</div>", unsafe_allow_html=True)
        st.write(f"**{reduction_total*100:.2f}%** bei **{months_early}** Monaten Vorbezug")
    with m3:
        if be_years is not None:
            st.markdown("<div class='metric'>Break-even</div>", unsafe_allow_html=True)
            st.write(f"**{be_years} J {be_months} M**")
        else:
            st.markdown("<div class='metric'>Break-even</div>", unsafe_allow_html=True)
            st.write("**nicht erreicht**")

    # Verdict text
    st.markdown("---")
    if be_years is None:
        verdict = "🔵 Vorbezug wirkt vorteilhaft über den gesamten Planungshorizont."
    else:
        if be_years > life_expectancy:
            verdict = f"🔵 Vorbezug **macht Sinn** (Break‑even erst nach {{be_years}}J {{be_months}}M > Lebenserwartung {{life_expectancy}})."
        else:
            verdict = f"🟠 Vorbezug **macht weniger Sinn** (Break‑even bei {{be_years}}J {{be_months}}M < Lebenserwartung {{life_expectancy}})."

    # Add explanation line
    st.write(verdict)
    st.caption("Hinweis: Vereinfachte Modellierung (keine Inflation/Zins). Übergangsjahrgänge: Monats‑Satz ggf. anpassen.")

# Footer mini note
st.markdown("<div class='hint'>© FINAURA · Free Flagship. Für Detailfälle folgt FINAURA Pro.</div>", unsafe_allow_html=True)
