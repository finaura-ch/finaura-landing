# FINAURA – AHV Vorbezug (Free Flagship)
# Version: 0.3.0    Date: 2025-10-20 (Europe/Zurich)
# Change: Geschlecht+Jahrgang, automatische Übergangslogik (Frau 1961–1969),
#         Mindestalter-Clamp (1961:64J3M / 1962:64J6M / 1963:64J9M / 1964–1969:65J),
#         Apple-clean UI, zwei Linienstile, gestrichelte Break-even-Linie mit Label + Zahl, Urteil kompakt.
# Project path: ~/Documents/Finaura/app
#
# QUICK START:
#   pip install streamlit altair pandas
#   streamlit run finaura_ahv_vorbezug_app_v0_3_0.py

from __future__ import annotations

__version__ = "0.3.0"

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

st.set_page_config(page_title="FINAURA – AHV Vorbezug (Free)", page_icon="🇨🇭", layout="wide")

SWISS_BLUE = "#155E9A"
SWISS_GREY = "#E9EDF2"

st.markdown(f"""
<style>
  .title {{ font-weight: 700; font-size: 26px; letter-spacing: .2px;}}
  .subtitle {{ color:#4A5568; font-size:14px;}}
  .metric {{ font-size:18px; font-weight:700;}}
  .hint {{ color:#6B7280; font-size:12px;}}
  div.stButton > button {{ height:44px; border-radius:9999px; font-weight:600; }}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>FINAURA · AHV Vorbezug (Free)</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Hyper-simpel · Monatsgenau · Swiss Precision</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### ℹ️ Info")
    st.write(f"Version **{__version__}** · Stand **2025-10-20** (Europe/Zurich)")
    st.caption("Reale Darstellung. Diskontsatz 0 %. Inflation 1.2 % als Info, nicht in der Grafik.")
    st.caption("Zuschlag (einkommensabhängig) wird in der Free-Version nicht berechnet. "
               "In **FINAURA Pro** via IK-Upload schätzbar.")
    st.markdown("---")
    st.caption("Übergangslogik: Nur **Frau** mit Jahrgang **1961–1969** → Mindestalter gemäss Übergang.")

left, right = st.columns([0.45, 0.55])

with left:
    st.markdown("#### Geschlecht")
    if "sex" not in st.session_state:
        st.session_state.sex = "Frau"
    csex1, csex2 = st.columns(2)
    if csex1.button("Frau", use_container_width=True):
        st.session_state.sex = "Frau"
    if csex2.button("Mann", use_container_width=True):
        st.session_state.sex = "Mann"
    sex = st.session_state.sex

    st.markdown("#### Jahrgang")
    jahrgang = st.number_input("Jahr (1900–2010)", min_value=1900, max_value=2010, value=1963, step=1)

    is_transition = (sex == "Frau") and (1961 <= jahrgang <= 1969)
    if is_transition:
        st.caption("🟦 Übergangsjahrgang aktiv")
    else:
        st.caption("—")

    st.markdown("#### Frühbezugsalter (Jahre)")
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
    month_in_year = st.select_slider("Monat", options=list(range(0, 12)), value=0, label_visibility="collapsed")

    st.markdown("#### Lebenserwartung")
    life_expectancy = st.slider("Alter (Jahre)", min_value=75, max_value=100, value=85, step=1)

REGULAR_AGE = 65
min_start_age_months_total = None
if is_transition:
    if jahrgang == 1961:
        min_start_age_months_total = 64*12 + 3
    elif jahrgang == 1962:
        min_start_age_months_total = 64*12 + 6
    elif jahrgang == 1963:
        min_start_age_months_total = 64*12 + 9
    else:
        min_start_age_months_total = 65*12 + 0

start_age_months_total = base_year*12 + int(month_in_year)
if min_start_age_months_total is not None:
    start_age_months_total = max(start_age_months_total, min_start_age_months_total)

with left:
    sa_y = start_age_months_total // 12
    sa_m = start_age_months_total % 12
    st.caption(f"Startalter: **{sa_y} Jahre {sa_m} Monate**")

ANNUAL_REDUCTION_PCT = 6.8
MONTHLY_REDUCTION_PCT = ANNUAL_REDUCTION_PCT / 12.0
monthly_rate = MONTHLY_REDUCTION_PCT/100.0

regular_start_months_total = REGULAR_AGE*12
end_age_months_total = int(life_expectancy*12)
months_early = max(0, min(24, regular_start_months_total - start_age_months_total))
reduction_total = min(months_early * monthly_rate, 0.20)

benefit_regular = 1.0
benefit_early = benefit_regular * (1 - reduction_total)

ages_month = np.arange(min(start_age_months_total, regular_start_months_total), end_age_months_total+1)
cf_early = np.where(ages_month >= start_age_months_total, benefit_early, 0.0)
cf_regular = np.where(ages_month >= regular_start_months_total, benefit_regular, 0.0)
cum_early = np.cumsum(cf_early)
cum_regular = np.cumsum(cf_regular)

ge_idx = np.where((cum_early - cum_regular) >= 0)[0]
if ge_idx.size > 0:
    idx = ge_idx[0]
    be_months_total = int(ages_month[idx])
    be_y = be_months_total // 12
    be_m = be_months_total % 12
    be_age_float = be_y + be_m/12.0
else:
    idx = None
    be_y = None
    be_m = None
    be_age_float = None

df = pd.DataFrame({
    "age_years": ages_month/12.0,
    "Vorbezug (kumuliert)": cum_early,
    "Regulär (kumuliert)": cum_regular
})

with right:
    st.markdown("### Vergleich: Vorbezug vs. regulär")
    base = alt.Chart(df).transform_fold(
        ["Vorbezug (kumuliert)", "Regulär (kumuliert)"],
        as_=["Variante", "Wert"]
    ).mark_line(strokeWidth=2).encode(
        x=alt.X("age_years:Q", axis=alt.Axis(title="Alter (Jahre)")),
        y=alt.Y("Wert:Q", axis=alt.Axis(title="Kumuliert (Einheiten)")),
        color=alt.Color("Variante:N", legend=alt.Legend(title="Variante"))
    )
    chart = base
    if be_age_float is not None:
        vline = alt.Chart(pd.DataFrame({"x":[be_age_float]})).mark_rule(strokeDash=[6,4]).encode(x="x:Q")
        vtext = alt.Chart(pd.DataFrame({"x":[be_age_float], "y":[float(max(cum_early.max(), cum_regular.max()))*0.05], "t":[f"{be_y}.{str(be_m).zfill(2)}"]}))            .mark_text(align="left", dx=5, dy=-5).encode(x="x:Q", y="y:Q", text="t:N")
        chart = chart + vline + vtext
    st.altair_chart(chart.interactive(), use_container_width=True)

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown("<div class='metric'>Frühbezugsalter</div>", unsafe_allow_html=True)
        st.write(f"**{sa_y} J {sa_m} M**")
    with m2:
        st.markdown("<div class='metric'>Reduktion gesamt</div>", unsafe_allow_html=True)
        st.write(f"**{reduction_total*100:.2f}%** bei **{months_early}** Monaten")
    with m3:
        st.markdown("<div class='metric'>Break-even</div>", unsafe_allow_html=True)
        if be_y is not None:
            st.write(f"**{be_y} J {be_m} M**")
        else:
            st.write("**nicht erreicht**")

    st.markdown("---")
    if be_y is None or be_y > life_expectancy:
        verdict = "🔵 Vorbezug: **sinnvoll**"
    else:
        verdict = "🟠 Vorbezug: **weniger sinnvoll**"
    st.write(verdict)
    if be_y is not None:
        st.caption(f"Break-even: {be_y} J {be_m} M")
    else:
        st.caption("Break-even im Planungshorizont nicht erreicht.")

st.markdown("<div class='hint'>© FINAURA · Free Flagship. Zuschläge & exakte Tabellen in FINAURA Pro (via IK-Upload).</div>", unsafe_allow_html=True)
