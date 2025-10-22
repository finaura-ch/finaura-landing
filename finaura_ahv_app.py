
# FINAURA · AHV-Vorbezug – Entscheidungsmodul
# Version: 0.1.0
# Date (Europe/Zurich): 2025-10-19 19:46
# Change: Initial functional screen (UI-WHITE, 2 columns, LINE-SOFT chart, CTA Outline)
# Path Hint: ~/Downloads/finaura_app (symlink to ~/Documents/Finaura/app)
#
# Install & Run (auto-included as requested):
#   pip install streamlit altair pandas
#   streamlit run finaura_ahv_app.py

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

__version__ = "0.1.0"

st.set_page_config(page_title="FINAURA · AHV vorziehen oder regulär beziehen?", page_icon="💡", layout="wide")

# --- Sidebar meta ---
st.sidebar.markdown("### FINAURA")
st.sidebar.caption("Swiss Precision · Simplicity · Apple-like")
st.sidebar.write(f"Version: **{__version__}**")
st.sidebar.write("Frage: **AHV vorziehen oder regulär beziehen?**")

# --- Title ---
st.markdown("## AHV vorziehen oder regulär beziehen?")
st.caption("Klarheit in 60 Sekunden · Swiss Precision")

col_left, col_right = st.columns([1.05, 1])

with col_left:
    st.markdown("### Eingaben")

    age = st.selectbox("Ich plane den AHV‑Bezug mit", [63, 64], index=0)
    annual = st.number_input("Jährliche volle AHV‑Rente (CHF)", min_value=0, step=100, value=28680, format="%i")

    st.markdown("**Referenz**")
    ref_col1, ref_col2 = st.columns(2)
    with ref_col1:
        st.metric("Regulärer Bezug", "65")
    with ref_col2:
        st.metric("Lebenslange Kürzung bei Vorbezug*", "≈ 6–14 %")
    st.caption("*Richtwert abhängig von Vorbezugsjahren / Gesetzesstand.")

    st.write("")
    st.button("Weiter zur Finanzwirkung", type="secondary")

with col_right:
    st.markdown("### Ergebnis & Break‑Even")

    # --- Simplified reduction assumptions (illustrative) ---
    reduction_lookup = {64: 6.8, 63: 13.6}
    reduction_pct = reduction_lookup.get(age, 6.8)

    base_age = 65
    horizon_years = list(range(0, 40))

    early_annual = annual * (1 - reduction_pct/100.0)
    regular_annual = annual

    head_years = 65 - age
    cum_early = []
    cum_regular = []
    e_total = early_annual * head_years  # early payments before 65
    r_total = 0.0
    for t in horizon_years:
        e_total += early_annual
        r_total += regular_annual
        cum_early.append(e_total)
        cum_regular.append(r_total)

    # Break-even
    breakeven_idx = next((i for i, (e, r) in enumerate(zip(cum_early, cum_regular)) if r >= e), None)
    breakeven_age = 65 + (breakeven_idx if breakeven_idx is not None else 0)

    # KPIs
    kpi1, kpi2 = st.columns(2)
    with kpi1:
        choice = "Regulär (65)" if (breakeven_idx is not None and breakeven_idx < 15) else f"Vorbezug ({age})"
        st.metric("Empfehlung", choice)
    with kpi2:
        st.metric("Break‑Even (ca.)", f"{breakeven_age if breakeven_age else '—'} Jahre")

    # Recommendation (T2 tone)
    if choice.startswith("Regulär"):
        st.info("**Mein Rat:** Regulär mit 65 beziehen – langfristig kommt voraussichtlich mehr bei dir an. "
                "Wenn kurzfristige Liquidität wichtiger ist, kann ein Vorbezug dennoch sinnvoll sein.")
    else:
        st.info("**Mein Rat:** Vorbezug kann für dich sinnvoll sein – insbesondere wenn du die zusätzliche Liquidität "
                "frühzeitig brauchst. Prüfe dennoch die langfristigen Auswirkungen.")

    # Chart (LINE-SOFT, FIN-blue)
    import pandas as pd
    df = pd.DataFrame({
        "Jahre_nach_65": horizon_years,
        "Kumuliert_Early": cum_early,
        "Kumuliert_Regular": cum_regular
    })
    base = alt.Chart(df).encode(x=alt.X("Jahre_nach_65:Q", axis=alt.Axis(title="Jahre nach 65", labelColor="#6B7280", titleColor="#6B7280")))

    line_early = base.mark_line(stroke="#0A3A82", strokeWidth=2, opacity=0.35).encode(y=alt.Y("Kumuliert_Early:Q", axis=alt.Axis(title="Kumulierte Rente (CHF)", labelColor="#6B7280", titleColor="#6B7280")), tooltip=["Jahre_nach_65","Kumuliert_Early"])
    line_regular = base.mark_line(stroke="#0A3A82", strokeWidth=2).encode(y="Kumuliert_Regular:Q", tooltip=["Jahre_nach_65","Kumuliert_Regular"])

    chart = (line_regular + line_early).properties(height=220).configure_view(stroke="#E5E7EB")
    st.altair_chart(chart, use_container_width=True)

    st.caption("Visualisierung: kumulierte Rente über Zeit – Break‑Even markiert, ab wann der reguläre Bezug den Vorbezug überholt.")
