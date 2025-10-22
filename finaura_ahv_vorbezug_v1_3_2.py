# FINAURA — AHV Vorbezug (Free · v1.3.2 · UX Flow)
# Focus: Frictionless flow, clear hierarchy, subtle helpers
# Start: streamlit run finaura_ahv_vorbezug_v1_3_2.py

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import date

# ---------------- Page & CSS ----------------
st.set_page_config(page_title="FINAURA — AHV Vorbezug", page_icon="🇨🇭", layout="wide")
st.markdown("""
<style>
:root, html, body, .stApp, [data-testid="stAppViewContainer"] { background:#FFFFFF !important; color:#0F172A !important; }
[data-testid="stSidebar"] { background:#FFFFFF !important; }
.block-container { padding-top: 1.2rem; padding-bottom: 0.8rem; }
.title { font-weight:700; font-size:26px; letter-spacing:.2px; margin-bottom:2px; }
.subtitle { color:#475569; font-size:13px; margin-bottom:14px; }
.legend { display:flex; gap:14px; align-items:center; margin:6px 0 10px 0;}
.dot { width:10px; height:10px; border-radius:999px; display:inline-block;}
.dot-blue { background:#2563EB; }
.dot-orange { background:#EA580C; }
.badge { display:inline-flex; align-items:center; gap:6px; background:#F1F5F9; color:#0F172A; border:1px solid #CBD5E1;
         padding:6px 10px; border-radius:999px; font-size:12px; font-weight:600; }
.badge .dot-ug { width:8px; height:8px; border-radius:999px; background:#9333EA; display:inline-block; }
.pill { background:#FFFFFF; border:1px solid #E2E8F0; padding:12px 14px; border-radius:14px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.good { background:#EAF6FF; border:1px solid #93C5FD; }
.warn { background:#FFFBEB; border:1px solid #FCD34D; }
.info { background:#F8FAFC; border:1px solid #E2E8F0; }
.kpi { background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:14px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.kpi h4 { margin:0; font-size:13px; color:#475569; font-weight:500; display:flex; align-items:center; gap:8px; }
.kpi p { margin:4px 0 0 0; font-weight:700; font-size:22px; }
.info-icon { display:inline-flex; align-items:center; justify-content:center; width:16px; height:16px; font-size:11px;
             border-radius:999px; background:#E5E7EB; color:#374151; cursor:help; }
.stButton>button { border-radius:9px !important; height:42px; font-weight:600 !important; }
.text-btn { background:none; border:none; color:#2563EB; padding:0; font-weight:600; cursor:pointer; }
.divider { height:1px; background:#E2E8F0; margin:10px 0; }
.small { color:#64748B; font-size:12px; }
.strong { font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ---------------- Altair Light Theme ----------------
def theme():
    return {
        "config": {
            "axis": {
                "gridColor": "#E2E8F0",
                "labelFont": "-apple-system, BlinkMacSystemFont, sans-serif",
                "titleFont": "-apple-system, BlinkMacSystemFont, sans-serif",
                "domainColor": "#E2E8F0",
                "domainWidth": 0.5,
            },
            "axisX": {"grid": False},
            "axisY": {"gridDash": [4,4], "grid": True},
            "range": {"category": ["#2563EB", "#EA580C"]},
            "view": {"strokeWidth": 0, "continuousBandSize": 10},
            "background": "#FFFFFF",
        }
    }
alt.themes.register("apple_light", theme)
alt.themes.enable("apple_light")

# ---------------- Constants ----------------
STANDARD_KUERZUNG_PA = 0.068
MONATLICHER_KUERZUNGSFAKTOR = STANDARD_KUERZUNG_PA / 12
NORMAL_RENTENALTER = 65
PLANUNGSDAUER_DEFAULT = 85  # Default 85; range 75–100

REFERENZALTER_FRAUEN = {
    1961:(64,3), 1962:(64,6), 1963:(64,9),
    1964:(65,0), 1965:(65,0), 1966:(65,0), 1967:(65,0), 1968:(65,0), 1969:(65,0),
}
UEBERGANG_61_63 = {1961:(64,3), 1962:(64,6), 1963:(64,9)}

# ---------------- Helpers ----------------
def ug_min_start_for_woman(jahrgang:int):
    if jahrgang in UEBERGANG_61_63: j, m = UEBERGANG_61_63[jahrgang]; return j*12+m
    if 1964 <= jahrgang <= 1969: return 65*12
    return None

def berechne_kurven(start_alter_monate:int, planungsalter_jahre:int, jahresrente:float):
    monat_norm = jahresrente/12.0
    reg_start_m = NORMAL_RENTENALTER*12
    months_early = reg_start_m - start_alter_monate
    kuerzung_total = max(0.0, months_early*MONATLICHER_KUERZUNGSFAKTOR)
    kuerzung_total = min(kuerzung_total, 0.20)
    monat_vor = monat_norm*(1 - kuerzung_total)
    end_m = planungsalter_jahre*12
    ages_m = np.arange(min(reg_start_m, start_alter_monate), end_m+1)
    cf_norm = np.where(ages_m >= reg_start_m, monat_norm, 0.0)
    cf_vor  = np.where(ages_m >= start_alter_monate, monat_vor, 0.0)
    cum_norm = np.cumsum(cf_norm); cum_vor = np.cumsum(cf_vor)
    df = pd.DataFrame({"Alter": ages_m/12.0, "Normale AHV (65)": cum_norm, "Vorbezug": cum_vor})
    diff = cum_norm - cum_vor
    idx = np.where(diff >= 0)[0]
    be_age = float(ages_m[idx[0]]/12.0) if idx.size>0 else None
    return df, kuerzung_total, months_early, be_age

def format_age(age:float):
    if age is None: return "—"
    j = int(age); m = int(round((age - j)*12))
    if m == 12: j += 1; m = 0
    return f"{j} Jahre {m} Monate"

def age_minus_one_month(age:float):
    j = int(age); m = int(round((age - j)*12)); m -= 1
    if m < 0: j -= 1; m = 11
    return max(j,0) + m/12.0

def summary_text(be_age, ug_flag, start_j, start_m, plan_age):
    part1 = f"Start Vorbezug: {start_j} Jahre {start_m} Monate | Plan bis: {plan_age}"
    if be_age is None:
        part2 = "Kein Break-even bis Planungsalter – Vorbezug lohnt sich bis zum Horizont."
    else:
        part2 = f"Break-even: {format_age(be_age)} | Bis {format_age(age_minus_one_month(be_age))} vorteilhaft."
    part3 = "Übergang erkannt" if ug_flag else "Nicht Übergang"
    return f"{part1} · {part2} · {part3}"

# ---------------- Header ----------------
st.markdown("<div class='title'>FINAURA — AHV Vorbezug</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Monatsgenauer Vergleich · Swiss Precision</div>", unsafe_allow_html=True)

# ---------------- Layout ----------------
left, right = st.columns([0.46, 0.54], gap="large")

with left:
    # Init session defaults
    if "geschlecht" not in st.session_state: st.session_state.geschlecht = "Frau"
    if "show_alt" not in st.session_state: st.session_state.show_alt = False
    if "vorM" not in st.session_state: st.session_state.vorM = 0
    if "plan_age" not in st.session_state: st.session_state.plan_age = PLANUNGSDAUER_DEFAULT

    st.markdown("#### Geschlecht")
    g1, g2 = st.columns(2)
    if g1.button("Frau", use_container_width=True): st.session_state.geschlecht = "Frau"
    if g2.button("Mann", use_container_width=True): st.session_state.geschlecht = "Mann"
    is_female = st.session_state.geschlecht == "Frau"
    geschlecht = "F" if is_female else "M"

    st.markdown("#### Jahrgang")
    years = list(range(1940, date.today().year - 17))
    jahrgang = st.select_slider("Jahr", options=years, value=1963, label_visibility="collapsed")

    ug_min_monat = ug_min_start_for_woman(jahrgang) if is_female else None
    is_UG = ug_min_monat is not None

    if is_UG:
        st.markdown("<div class='badge'><span class='dot-ug'></span>Übergangsgeneration erkannt</div>", unsafe_allow_html=True)
        ey = ug_min_monat//12; em = ug_min_monat%12
        st.markdown(f"<div class='pill info'><span class='strong'>Empfohlen:</span> {ey} Jahre {em} Monate (Zuschlag gesichert)</div>", unsafe_allow_html=True)

    st.markdown("#### Frühbezugsalter")
    if is_UG and not st.session_state.show_alt:
        start_j = ug_min_monat//12; start_m = ug_min_monat%12
        st.selectbox("Startjahr (empfohlen)", options=[start_j], index=0, label_visibility="collapsed", disabled=True)
        st.select_slider("Monat (empfohlen)", options=[start_m], value=start_m, label_visibility="collapsed", disabled=True)
        alt_col1, alt_col2 = st.columns([1,1])
        with alt_col1:
            if st.button("Alternative anzeigen (62/63)", use_container_width=True):
                st.session_state.show_alt = True
        with alt_col2:
            if st.button("Zurücksetzen", use_container_width=True):
                st.session_state.show_alt = False; st.session_state.vorM = 0; st.session_state.plan_age = PLANUNGSDAUER_DEFAULT
    else:
        # Freie Auswahl
        if is_UG:
            start_j = st.selectbox("Startjahr", options=[62,63,64], index=1, label_visibility="collapsed")
        else:
            start_j = st.selectbox("Startjahr", options=[63,64], index=1, label_visibility="collapsed")
        st.markdown("#### Monat im Startjahr")
        start_m = st.select_slider("Monat", options=list(range(12)), value=st.session_state.vorM, label_visibility="collapsed")
        st.session_state.vorM = start_m

        if is_UG and (start_j*12 + start_m) < ug_min_monat:
            ey = ug_min_monat//12; em = ug_min_monat%12
            st.markdown(f"<div class='pill warn'>⚠️ Vor dem empfohlenen Start ({ey} Jahre {em} Monate). Zuschlag entfällt. Free rechnet 6.8% p.a. — <i>Exakte reduzierte Kürzung in FINAURA Pro.</i></div>", unsafe_allow_html=True)

    st.markdown("#### Planungsdauer (bis Alter)")
    plan_age = st.slider("bis Alter (Jahre)", 75, 100, st.session_state.plan_age, 1, label_visibility="collapsed")
    st.session_state.plan_age = plan_age
    st.markdown(f"<span class='small'>Geplanter Horizont: bis {plan_age} Jahre</span>", unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    st.markdown("#### Optionen")
    show_be_line = st.checkbox("Break-even-Linie anzeigen", value=False, help="Gestrichelte Linie & Label am Schnittpunkt.")
    st.caption("Free nutzt 6.8% p.a. zur Vergleichbarkeit. ÜG hat reduzierte Sätze → exakte Berechnung in FINAURA Pro.")

with right:
    # Legend with small ⓘ
    legend_tip = "Vorbezugslinie basiert in Free auf Standard-Kürzung 6.8% p.a."
    st.markdown(f"""
<div class='legend'>
  <span><span class='dot dot-blue'></span> Normale AHV (65)</span>
  <span><span class='dot dot-orange'></span> Vorbezug (<span title="{legend_tip}">ⓘ</span> { (ug_min_monat//12 if is_UG and not st.session_state.show_alt else start_j) } J { (ug_min_monat%12 if is_UG and not st.session_state.show_alt else start_m) } M)</span>
</div>
""", unsafe_allow_html=True)

    # Compute
    jahresrente = 12_000.0
    start_total_m = (ug_min_monat if (is_UG and not st.session_state.show_alt) else (start_j*12 + start_m))
    df, kuerzung_total, months_early, be_age = berechne_kurven(start_total_m, plan_age, jahresrente)

    # Chart
    chart = alt.Chart(df).transform_fold(
        ["Normale AHV (65)", "Vorbezug"], as_=["Variante", "Wert"]
    ).mark_line(strokeWidth=2.6).encode(
        x=alt.X("Alter:Q", axis=alt.Axis(title="Alter (Jahre)", grid=False, labelFontSize=13, titleFontSize=14)),
        y=alt.Y("Wert:Q", axis=alt.Axis(title="Kumulierte Rente", grid=True, labelFontSize=13, titleFontSize=14)),
        color=alt.Color("Variante:N", legend=None)
    ).properties(height=360, padding={"left":10, "top":10, "right":10, "bottom":10}).configure_view(strokeWidth=0)

    if show_be_line and (be_age is not None):
        be_row = df.iloc[(df["Alter"] - be_age).abs().argsort()[:1]]
        be_y = float((be_row["Normale AHV (65)"].values[0] + be_row["Vorbezug"].values[0]) / 2)
        be_df = pd.DataFrame({"Alter":[be_age], "Wert":[be_y]})
        be_rule = alt.Chart(be_df).mark_rule(color="#0EA5E9", strokeDash=[5,5], strokeWidth=1.5).encode(x="Alter:Q")
        be_text = alt.Chart(be_df).mark_text(dy=-12, align="center", fontSize=12, fontWeight="bold", color="#0F172A").encode(
            x="Alter:Q", y=alt.Y("Wert:Q", axis=None), text=alt.value(f"Break-even • {format_age(be_age)}")
        )
        chart = chart + be_rule + be_text

    st.altair_chart(chart, use_container_width=True)

    # KPIs
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown("<div class='kpi'><h4>Break-even</h4><p>"+format_age(be_age)+"</p></div>", unsafe_allow_html=True)
    with k2:
        tooltip = "Free nutzt 6.8% p.a. zur Vergleichbarkeit. Für die Übergangsgeneration gelten reduzierte Kürzungssätze – die exakte Berechnung ist in FINAURA Pro verfügbar."
        st.markdown(f"<div class='kpi'><h4>Gesamt-Kürzung Vorbezug <span class='info-icon' title='{tooltip}'>ⓘ</span></h4><p>"+f"{kuerzung_total*100:.2f}%"+ "</p></div>", unsafe_allow_html=True)
    with k3:
        years = months_early//12; months = months_early%12
        vor_txt = "0"
        if months_early>0:
            vor_txt = (f'{years} J ' if years>0 else '') + (f'{months} M' if months>0 or years==0 else '')
        st.markdown("<div class='kpi'><h4>Vorbezugs-Dauer</h4><p>"+vor_txt+"</p></div>", unsafe_allow_html=True)

    st.markdown("---")
    # Verdict
    if be_age is None:
        st.markdown("<div class='pill good'>Bis zum gewählten Planungsalter: Vorbezug lohnt sich.</div>", unsafe_allow_html=True)
    else:
        bis_age = age_minus_one_month(be_age)
        st.markdown(f"<div class='pill good'>✅ <b>Bis Alter {format_age(bis_age)}</b>: Vorbezug lohnt sich.</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='pill warn'>⚠️ <b>Ab Alter {format_age(be_age)}</b>: Der normale Bezug ist vorteilhafter.</div>", unsafe_allow_html=True)

    # Summary box (copy helper)
    st.markdown("#### Zusammenfassung")
    s_text = summary_text(be_age, is_UG, (ug_min_monat//12 if (is_UG and not st.session_state.show_alt) else start_j),
                          (ug_min_monat%12 if (is_UG and not st.session_state.show_alt) else start_m), plan_age)
    st.code(s_text, language="text")

st.caption("© FINAURA · v1.3.2 · UX Flow: Legend-ⓘ, Empfohlen-Hinweis, Alternative auf Klick, Reset, Summary")
