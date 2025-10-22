
# FINAURA – AHV Vorbezug (Free Flagship)
# Version: 0.3.4    Date: 2025-10-20 (Europe/Zurich)
# – Übergangsjahrgänge implementiert (Frau 1961–1963 & 1964–1969)
# – Legende über der Grafik (Blau = Normale AHV 65, Orange = Vorbezug)
# – Break-even als Zahl unten (keine gestrichelte Linie)
# – Urteil mit Karten + ★-Rating-Texten
# – (i)-Info mit Vergleichstabelle (Ja/Nein + Sterne), jahrgangsgenau
# – Planungsdauer-Slider 65–100 (Default 85)
# Start: pip install streamlit altair pandas ; streamlit run finaura_ahv_vorbezug_app_v0_3_4.py

from __future__ import annotations

__version__ = "0.3.4"

import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

st.set_page_config(page_title="FINAURA — AHV Vorbezug", page_icon="🇨🇭", layout="wide")

# ---------- Styles ----------
st.markdown("""
<style>
  .title { font-weight:700; font-size:26px; letter-spacing:.2px; }
  .subtitle { color:#4A5568; font-size:14px; }
  .legend { display:flex; gap:18px; align-items:center; margin:8px 0 6px 0;}
  .dot { width:10px; height:10px; border-radius:999px; display:inline-block;}
  .dot-blue { background:#2563EB; }
  .dot-orange { background:#EA580C; }
  .pill { background:#EEF2FF; border:1px solid #C7D2FE; padding:12px 14px; border-radius:14px; margin-top:8px; }
  .good { background:#ECFDF5; border:1px solid #A7F3D0; }
  .warn { background:#FEF3C7; border:1px solid #FDE68A; }
  .hint { color:#6B7280; font-size:12px; }
  .label { font-size:12px; color:#4B5563; }
  div.stButton > button { height:44px; border-radius:9999px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>FINAURA — AHV Vorbezug</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Monatsgenauer Vergleich · Swiss Precision</div>", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### ℹ️ Info")
    st.write(f"Version **{__version__}** · Stand **2025-10-20** (Europe/Zurich)")
    with st.expander("Annahmen"):
        st.caption("Reale Darstellung, Diskontsatz 0 %. Inflation 1.2 % nur Info.")
        st.caption("Zuschläge einkommens-/jahrgangsabhängig (nicht in Free). Exakt in **FINAURA Pro** (IK-Upload).")
    with st.expander("Übergangsregeln (kurz)"):
        st.caption("Frau 1961–1963: Idealer Rentenbeginn 64J3M / 64J6M / 64J9M. Vorbezug entzieht den Zuschlag.")
        st.caption("Frau 1964–1969: Vorbezug im Modul 1 nicht vorgesehen → Referenzalter 65J. Aufschub in Modul 2.")

# ---------- Layout ----------
left, right = st.columns([0.45, 0.55])

# ---------- Inputs ----------
with left:
    st.markdown("#### Geschlecht")
    sex = st.session_state.get("sex", "Frau")
    c1, c2 = st.columns(2)
    if c1.button("Frau", use_container_width=True):
        sex = "Frau"
    if c2.button("Mann", use_container_width=True):
        sex = "Mann"
    st.session_state["sex"] = sex

    st.markdown("#### Jahrgang")
    years = list(range(1940, 2011))
    jahrgang = st.select_slider("Jahr", options=years, value=1963, label_visibility="collapsed")

# Übergang bestimmen
is_trans_61_63 = (sex == "Frau") and (1961 <= jahrgang <= 1963)
is_trans_64_69 = (sex == "Frau") and (1964 <= jahrgang <= 1969)

with left:
    if is_trans_61_63:
        st.markdown("#### Übergangsjahrgang")
        mapping = {1961:(64,3), 1962:(64,6), 1963:(64,9)}
        ey, em = mapping[jahrgang]
        st.info(f"Idealer Rentenbeginn: **{ey} Jahre {em} Monate**\n(Vorbezug nicht empfohlen – Zuschlag entfällt)")
        # Info (i)
        with st.expander("Warum? (Vergleich)"):
            st.markdown(f"""
| Bezug | Zuschlag | Kürzung | Ergebnis | Bewertung |
|---|---:|---:|---|:--:|
| Vorbezug | Nein | Ja | schlechteste Wahl | ★☆☆☆☆ |
| Referenzalter (**{ey}+{str(em).zfill(2)}M**) | Ja | Nein | solide Wahl | ★★★☆☆ |
| Bezug bis **65** | Ja | Nein | beste Wahl | ★★★★★ |
""")
        early_enabled = False
        start_year, start_month = 65, 0
    elif is_trans_64_69:
        st.markdown("#### Übergangsjahrgang")
        st.info("Vorbezug im Modul 1 nicht vorgesehen. Referenzalter **65 Jahre**.")
        early_enabled = False
        start_year, start_month = 65, 0
    else:
        st.markdown("#### Frühbezugsalter")
        choice = st.session_state.get("age_choice", 64)
        b1, b2, b3 = st.columns(3)
        if b1.button("63", use_container_width=True):
            choice = 63
        if b2.button("64", use_container_width=True):
            choice = 64
        b3.button("65", use_container_width=True, disabled=True)
        st.session_state["age_choice"] = choice
        start_year = int(choice)

        st.markdown("#### Monat im Startjahr")
        start_month = st.select_slider("Monat", options=list(range(0,12)), value=0, label_visibility="collapsed")
        early_enabled = True

    st.markdown("#### Planungsdauer (bis Alter)")
    plan_age = st.slider("bis Alter (Jahre)", 65, 100, 85, 1)

# ---------- Calculation ----------
REGULAR_AGE = 65
ANNUAL_REDUCTION_PCT = 6.8
MONTHLY_REDUCTION_PCT = ANNUAL_REDUCTION_PCT / 12.0
monthly_rate = MONTHLY_REDUCTION_PCT / 100.0

regular_start_m = REGULAR_AGE * 12
end_m = int(plan_age * 12)

if early_enabled:
    start_m = start_year * 12 + int(start_month)
    months_early = max(0, min(24, regular_start_m - start_m))
    reduction_total = min(months_early * monthly_rate, 0.20)
    benefit_early = 1.0 * (1 - reduction_total)
else:
    start_m = regular_start_m
    months_early = 0
    reduction_total = 0.0
    benefit_early = None

benefit_regular = 1.0

ages_m = np.arange(min(start_m, regular_start_m), end_m + 1)
cf_regular = np.where(ages_m >= regular_start_m, benefit_regular, 0.0)
cum_regular = np.cumsum(cf_regular)

if early_enabled:
    cf_early = np.where(ages_m >= start_m, benefit_early, 0.0)
    cum_early = np.cumsum(cf_early)
    diff = cum_early - cum_regular
    idxs = np.where(diff >= 0)[0]
    be_age = float(ages_m[idxs[0]]/12.0) if idxs.size>0 else None
else:
    cum_early = None
    be_age = None

# ---------- Chart ----------
with right:
    # Legende (oben)
    if early_enabled:
        if months_early >= 12:
            label = f"{months_early//12} Jahr(e)"
        elif months_early > 0:
            label = f"{months_early} Monate"
        else:
            label = "0 Monate"
    else:
        label = "—"

    st.markdown(f"""
<div class='legend'>
  <span><span class='dot dot-blue'></span> Normale AHV (65)</span>
  <span><span class='dot dot-orange'></span> Vorbezug {label}</span>
</div>
""", unsafe_allow_html=True)

    if early_enabled:
        df = pd.DataFrame({{
            "Alter": ages_m/12.0,
            "Normale AHV (65)": cum_regular,
            "Vorbezug": cum_early
        }})
        chart = alt.Chart(df).transform_fold(
            ["Normale AHV (65)", "Vorbezug"], as_=["Variante", "Wert"]
        ).mark_line(strokeWidth=2).encode(
            x=alt.X("Alter:Q", axis=alt.Axis(title="Alter (Jahre)")),
            y=alt.Y("Wert:Q", axis=alt.Axis(title="Kumuliert (Einheiten)")),
            color=alt.Color("Variante:N",
                scale=alt.Scale(domain=["Normale AHV (65)", "Vorbezug"],
                                range=["#2563EB", "#EA580C"]),
                legend=None)
        )
        st.altair_chart(chart.properties(height=320).interactive(), use_container_width=True)
    else:
        df = pd.DataFrame({{
            "Alter": ages_m/12.0,
            "Normale AHV (65)": cum_regular
        }})
        chart = alt.Chart(df).mark_line(strokeWidth=2, color="#2563EB").encode(
            x=alt.X("Alter:Q", axis=alt.Axis(title="Alter (Jahre)")),
            y=alt.Y("Normale AHV (65):Q", axis=alt.Axis(title="Kumuliert (Einheiten)"))
        )
        st.altair_chart(chart.properties(height=320).interactive(), use_container_width=True)

    # Break-even & verdicts
    cA, cB, cC = st.columns(3)
    with cA:
        st.markdown("**Break-even**")
        st.write(f"{be_age:.1f} Jahre" if be_age is not None else "—")
    with cB:
        st.markdown("**Kürzung**")
        st.write(f"{reduction_total*100:.2f}%")
    with cC:
        st.markdown("**Vorbezug**")
        st.write(f"{months_early} Monate" if early_enabled else "—")

    st.markdown("---")
    if early_enabled:
        if be_age is None:
            st.markdown("<div class='pill good'>Bis zum gewählten Planungsalter: Vorbezug lohnt sich.</div>", unsafe_allow_html=True)
        else:
            below = max(65, int(np.floor(be_age))-1)
            above = int(np.ceil(be_age))
            st.markdown(f"<div class='pill good'>Bis Alter <b>{below}</b>: Vorbezug lohnt sich.</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='pill warn'>Ab Alter <b>{above}</b>: Der normale Bezug ist vorteilhafter.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='pill'>Regulärer Bezug: solide Wahl (Zuschlag sichern). Aufschub simulieren in Modul 2.</div>", unsafe_allow_html=True)

st.caption("© FINAURA · Free Flagship. Modul 2 (Aufschub) folgt separat.")
