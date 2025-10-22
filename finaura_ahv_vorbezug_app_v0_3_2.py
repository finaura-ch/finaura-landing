# FINAURA – AHV Vorbezug (Free Flagship)
# Version: 0.3.2    Date: 2025-10-20 (Europe/Zurich)
# Change: Option A umgesetzt – Übergangsfrauen (1961–1963) ohne Vorbezug-UI (nur Hinweis, frühester Beginn 64+3/6/9M).
#         Frauen 1964–1969: Vorbezug nicht vorgesehen (nur 65). Männer & übrige Frauen: 63/64 aktiv.
#         Wheel-Jahrgang, sauberes Chart, Break-even-Label, Apple-kurze Verdicts.
# Project path: ~/Documents/Finaura/app
#
# QUICK START:
#   pip install streamlit altair pandas
#   streamlit run finaura_ahv_vorbezug_app_v0_3_2.py

from __future__ import annotations

__version__ = "0.3.2"

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

# -----------------------------
# Page & Style
# -----------------------------
st.set_page_config(page_title="FINAURA – AHV Vorbezug (Free)", page_icon="🇨🇭", layout="wide")

st.markdown("""
<style>
  .title { font-weight:700; font-size:26px; letter-spacing:.2px; }
  .subtitle { color:#4A5568; font-size:14px; }
  .metric { font-size:18px; font-weight:700; }
  .hint { color:#6B7280; font-size:12px; }
  div.stButton > button { height:44px; border-radius:9999px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>FINAURA · AHV Vorbezug (Free)</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Hyper-simpel · Monatsgenau · Swiss Precision</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ℹ️ Info")
    st.write(f"Version **{__version__}** · Stand **2025-10-20** (Europe/Zurich)")
    with st.expander("Annahmen"):
        st.caption("Reale Darstellung, Diskontsatz 0 %. Inflation 1.2 % nur Info (nicht in Grafik).")
        st.caption("Zuschläge einkommens-/jahrgangsabhängig (nicht in Free). Exakt in **FINAURA Pro** (IK-Upload).")
    with st.expander("Übergangsregeln (kurz)"):
        st.caption("Frau 1961–1963: Frühester Beginn 64J3M / 64J6M / 64J9M (Vorbezug = Zuschlagverlust).")
        st.caption("Frau 1964–1969: Vorbezug nicht vorgesehen → Referenzalter 65J.")

# -----------------------------
# Inputs (left) · Output (right)
# -----------------------------
left, right = st.columns([0.45, 0.55])

with left:
    # Geschlecht
    st.markdown("#### Geschlecht")
    if "sex" not in st.session_state:
        st.session_state.sex = "Frau"
    csex1, csex2 = st.columns(2)
    if csex1.button("Frau", use_container_width=True):
        st.session_state.sex = "Frau"
    if csex2.button("Mann", use_container_width=True):
        st.session_state.sex = "Mann"
    sex = st.session_state.sex

    # Jahrgang "Wheel" via select_slider
    st.markdown("#### Jahrgang")
    years = list(range(1940, 2011))
    default_year = 1963
    jahrgang = st.select_slider("Jahr", options=years, value=default_year if default_year in years else years[len(years)//2], label_visibility="collapsed")

# Übergangsstatus
is_trans_61_63 = (sex == "Frau") and (1961 <= jahrgang <= 1963)
is_trans_64_69 = (sex == "Frau") and (1964 <= jahrgang <= 1969)

# -----------------------------
# Frühbezugs-UI je nach Status
# -----------------------------
with left:
    if is_trans_61_63:
        st.markdown("#### Frühester Rentenbeginn")
        earliest_map = {1961: (64,3), 1962: (64,6), 1963: (64,9)}
        ey, em = earliest_map[jahrgang]
        st.info(f"Übergangsjahrgang: Frühester Beginn **{ey} J {em} M**. Vorbezug führt zu Zuschlagverlust.")
        base_year = 65  # Referenz für Vergleich
        base_month = 0
        early_enabled = False
    elif is_trans_64_69:
        st.markdown("#### Frühester Rentenbeginn")
        st.info("Übergangsjahrgang: Vorbezug nicht vorgesehen. Referenzalter **65 J**.")
        base_year = 65
        base_month = 0
        early_enabled = False
    else:
        st.markdown("#### Frühbezugsalter")
        if "age_choice" not in st.session_state:
            st.session_state.age_choice = 64
        c1, c2, c3 = st.columns(3)
        if c1.button("63", use_container_width=True):
            st.session_state.age_choice = 63
        if c2.button("64", use_container_width=True):
            st.session_state.age_choice = 64
        c3.button("65", use_container_width=True, disabled=True)
        base_year = int(st.session_state.age_choice)

        st.markdown("#### Monat im Startjahr")
        month_in_year = st.select_slider("Monat", options=list(range(0,12)), value=0, label_visibility="collapsed")
        base_month = int(month_in_year)
        early_enabled = True

    st.markdown("#### Lebenserwartung")
    life_expectancy = st.slider("Alter (Jahre)", min_value=75, max_value=100, value=85, step=1)

# -----------------------------
# Berechnung (Investment-Logik, real, Diskont 0 %)
# -----------------------------
REGULAR_AGE = 65
ANNUAL_REDUCTION_PCT = 6.8
MONTHLY_REDUCTION_PCT = ANNUAL_REDUCTION_PCT / 12.0  # ~0.5667 % p.M.
monthly_rate = MONTHLY_REDUCTION_PCT / 100.0

regular_start_months_total = REGULAR_AGE * 12
end_age_months_total = int(life_expectancy * 12)

if early_enabled:
    start_age_months_total = base_year * 12 + base_month
    months_early = max(0, min(24, regular_start_months_total - start_age_months_total))
    reduction_total = min(months_early * monthly_rate, 0.20)
    benefit_early = 1.0 * (1 - reduction_total)
else:
    # Kein Vorbezug: wir rechnen nur die reguläre Linie
    start_age_months_total = regular_start_months_total
    months_early = 0
    reduction_total = 0.0
    benefit_early = None

benefit_regular = 1.0

ages_month = np.arange(min(start_age_months_total, regular_start_months_total), end_age_months_total + 1)
cf_regular = np.where(ages_month >= regular_start_months_total, benefit_regular, 0.0)
cum_regular = np.cumsum(cf_regular)

if early_enabled:
    cf_early = np.where(ages_month >= start_age_months_total, benefit_early, 0.0)
    cum_early = np.cumsum(cf_early)
    # Break-even
    idxs = np.where((cum_early - cum_regular) >= 0)[0]
    if idxs.size > 0:
        be_total_m = int(ages_month[idxs[0]])
        be_y = be_total_m // 12
        be_m = be_total_m % 12
        be_age_float = be_y + be_m/12.0
    else:
        be_y = be_m = None
        be_age_float = None
else:
    cum_early = None
    be_y = be_m = None
    be_age_float = None

# -----------------------------
# Data & Chart
# -----------------------------
if early_enabled:
    df = pd.DataFrame({
        "Alter": ages_month/12.0,
        "Vorbezug (kumuliert)": cum_early,
        "Regulär (kumuliert)": cum_regular
    })
else:
    df = pd.DataFrame({
        "Alter": ages_month/12.0,
        "Regulär (kumuliert)": cum_regular
    })

with right:
    st.markdown("### Vergleich")
    if early_enabled:
        base_chart = alt.Chart(df).transform_fold(
            ["Vorbezug (kumuliert)", "Regulär (kumuliert)"],
            as_=["Variante", "Wert"]
        ).mark_line(strokeWidth=2).encode(
            x=alt.X("Alter:Q", axis=alt.Axis(title="Alter (Jahre)")),
            y=alt.Y("Wert:Q", axis=alt.Axis(title="Kumuliert (Einheiten)")),
            color=alt.Color("Variante:N", legend=alt.Legend(title=""))
        )
        chart = base_chart
        if be_age_float is not None:
            vline = alt.Chart(pd.DataFrame({"x":[be_age_float]})).mark_rule(strokeDash=[6,4]).encode(x="x:Q")
            vtext = alt.Chart(pd.DataFrame({"x":[be_age_float], "y":[float(max(df["Vorbezug (kumuliert)"].max(), df["Regulär (kumuliert)"].max()))*0.06], "t":[f"{be_y}.{str(be_m).zfill(2)}"]}))                .mark_text(align="left", dx=6, dy=-6).encode(x="x:Q", y="y:Q", text="t:N")
            chart = chart + vline + vtext
        st.altair_chart(chart.interactive(), use_container_width=True)
    else:
        chart = alt.Chart(df).mark_line(strokeWidth=2).encode(
            x=alt.X("Alter:Q", axis=alt.Axis(title="Alter (Jahre)")),
            y=alt.Y("Regulär (kumuliert):Q", axis=alt.Axis(title="Kumuliert (Einheiten)"))
        )
        st.altair_chart(chart.interactive(), use_container_width=True)

    # Metrics minimal
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown("<div class='metric'>Startalter</div>", unsafe_allow_html=True)
        sa_y = start_age_months_total // 12
        sa_m = start_age_months_total % 12
        st.write(f"**{sa_y} J {sa_m} M**")
    with m2:
        st.markdown("<div class='metric'>Kürzung</div>", unsafe_allow_html=True)
        st.write(f"**{reduction_total*100:.2f}%**")
    with m3:
        st.markdown("<div class='metric'>Break-even</div>", unsafe_allow_html=True)
        if early_enabled and (be_y is not None):
            st.write(f"**{be_y} J {be_m} M**")
        else:
            st.write("**—**")

    st.markdown("---")
    # Verdicts
    if early_enabled:
        if (be_y is None) or (be_y > life_expectancy):
            verdict = "🔵 Vorbezug: **sinnvoll**"
        else:
            verdict = "🟠 Vorbezug: **weniger sinnvoll**"
        st.write(verdict)
        if be_y is not None:
            st.caption(f"Break-even: {be_y} J {be_m} M")
    else:
        st.write("🔵 Regulärer Bezug: **empfohlen** (Übergangszuschlag sichern)")

st.caption("© FINAURA · Free Flagship. Zusätze (Zuschlag exakt, Zinsen) folgen in FINAURA Pro.")
