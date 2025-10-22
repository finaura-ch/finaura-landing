# FINAURA — AHV Vorbezug (Free) — v1.1 (LIGHT MODE FORCED)
# Apple-Style UI · Break-even korrekt · Übergangsjahrgänge
# Start: streamlit run finaura_ahv_vorbezug_v1_1_light.py

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import date

# ---------------- Force LIGHT Mode (works regardless of OS/Streamlit theme) ----------------
st.set_page_config(page_title="FINAURA — AHV Vorbezug", page_icon="🇨🇭", layout="wide")
st.markdown("""
    <style>
    :root, html, body, .stApp, [data-testid="stAppViewContainer"] {
        background: #FFFFFF !important;
        color: #0F172A !important;
    }
    [data-testid="stSidebar"] {
        background: #FFFFFF !important;
    }
    /* General typography */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .title { font-weight:700; font-size:26px; letter-spacing:.2px; }
    .subtitle { color:#475569; font-size:14px; margin-bottom:14px; }
    .legend { display:flex; gap:18px; align-items:center; margin:6px 0 10px 0;}
    .dot { width:10px; height:10px; border-radius:999px; display:inline-block;}
    .dot-blue { background:#2563EB; }
    .dot-orange { background:#EA580C; }
    .pill { background:#FFFFFF; border:1px solid #E2E8F0; padding:12px 14px; border-radius:14px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .good { background:#EAF6FF; border:1px solid #93C5FD; }
    .warn { background:#FFFBEB; border:1px solid #FCD34D; }
    .kpi { background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .kpi h4 { margin:0; font-size:14px; color:#475569; font-weight:500; }
    .kpi p { margin:4px 0 0 0; font-weight:700; font-size:22px; }
    .stButton>button { border-radius:8px !important; height:44px; font-weight:500 !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------- Altair Light Theme ----------------
def get_apple_theme():
    return {
        "config": {
            "title": {"anchor": "start", "fontSize": 16, "font": "Inter", "color": "#0F172A"},
            "axis": {
                "gridColor": "#E2E8F0",
                "labelFont": "-apple-system, BlinkMacSystemFont, sans-serif",
                "titleFont": "-apple-system, BlinkMacSystemFont, sans-serif",
                "domainColor": "#E2E8F0",
                "domainWidth": 0.5,
            },
            "axisX": {"grid": False},
            "axisY": {"gridDash": [4, 4], "grid": True},
            "range": {"category": ["#2563EB", "#EA580C"]},
            "view": {"strokeWidth": 0, "continuousBandSize": 10},
            "background": "#FFFFFF",
        }
    }
alt.themes.register("apple_light", get_apple_theme)
alt.themes.enable("apple_light")

# ---------------- Constants ----------------
STANDARD_KUERZUNG_PA = 0.068   # 6.8 % p.a.
MONATLICHER_KUERZUNGSFAKTOR = STANDARD_KUERZUNG_PA / 12
NORMAL_RENTENALTER = 65
PLANUNGSDAUER_DEFAULT = 85

REFERENZALTER_FRAUEN = {
    1961: (64, 3),
    1962: (64, 6),
    1963: (64, 9),
    1964: (65, 0),
    1965: (65, 0),
    1966: (65, 0),
    1967: (65, 0),
    1968: (65, 0),
    1969: (65, 0),
}
UEBERGANG_61_63 = {1961:(64,3), 1962:(64,6), 1963:(64,9)}

# ---------------- Helpers ----------------
def berechne_kurven(start_alter_monate:int, planungsalter_jahre:int, jahresrente:float):
    """Kumulierter Vergleich & Break-even: erstes Alter mit (Normal >= Vorbezug)."""
    monat_norm = jahresrente / 12.0
    reg_start_m = NORMAL_RENTENALTER * 12

    months_early = reg_start_m - start_alter_monate
    kuerzung_total = max(0.0, months_early * MONATLICHER_KUERZUNGSFAKTOR)
    kuerzung_total = min(kuerzung_total, 0.20)  # Sicherheitscap (20%)
    monat_vor = monat_norm * (1 - kuerzung_total)

    end_m = planungsalter_jahre * 12
    ages_m = np.arange(min(reg_start_m, start_alter_monate), end_m + 1)

    cf_norm = np.where(ages_m >= reg_start_m, monat_norm, 0.0)
    cf_vor  = np.where(ages_m >= start_alter_monate, monat_vor, 0.0)

    cum_norm = np.cumsum(cf_norm)
    cum_vor  = np.cumsum(cf_vor)

    df = pd.DataFrame({
        "Alter": ages_m/12.0,
        "Normale AHV (65)": cum_norm,
        "Vorbezug": cum_vor
    })

    diff = cum_norm - cum_vor
    idx = np.where(diff >= 0)[0]
    be_age = float(ages_m[idx[0]]/12.0) if idx.size>0 else None

    return df, kuerzung_total, months_early, be_age

def format_age(age:float):
    if age is None:
        return "—"
    j = int(age)
    m = int(round((age - j) * 12))
    if m == 12:
        j += 1; m = 0
    return f"{j} Jahre {m} Monate"

def age_minus_one_month(age:float):
    j = int(age); m = int(round((age - j)*12))
    m -= 1
    if m < 0:
        j -= 1; m = 11
    return max(j,0) + m/12.0

# ---------------- Header ----------------
st.markdown("<div class='title'>FINAURA — AHV Vorbezug</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Monatsgenauer Vergleich · Swiss Precision</div>", unsafe_allow_html=True)

# ---------------- Layout ----------------
colL, colR = st.columns([0.46, 0.54], gap="large")

with colL:
    st.markdown("#### Geschlecht")
    if "geschlecht" not in st.session_state:
        st.session_state.geschlecht = "Frau"
    g1, g2 = st.columns(2)
    if g1.button("Frau", use_container_width=True):
        st.session_state.geschlecht = "Frau"
    if g2.button("Mann", use_container_width=True):
        st.session_state.geschlecht = "Mann"
    geschlecht = "F" if st.session_state.geschlecht == "Frau" else "M"

    st.markdown("#### Jahrgang")
    years = list(range(1940, date.today().year - 17))
    jahrgang = st.select_slider("Jahr", options=years, value=1963, label_visibility="collapsed")

    is_trans_61_63 = (geschlecht == "F") and (jahrgang in UEBERGANG_61_63)
    is_trans_64_69 = (geschlecht == "F") and (1964 <= jahrgang <= 1969)

    if is_trans_61_63:
        ey, em = UEBERGANG_61_63[jahrgang]
        st.markdown("#### Übergangsjahrgang")
        st.info(f"Idealer Rentenbeginn für Ihren Jahrgang: **{ey} Jahre {em} Monate**. "
                "Vorbezug entzieht den Übergangszuschlag (nicht empfohlen).")
        with st.expander("Kurzer Vergleich"):
            st.markdown(f"""
| Bezug | Zuschlag | Kürzung | Ergebnis | Bewertung |
|---|---:|---:|---|:--:|
| Vorbezug (vor {ey}+{str(em).zfill(2)}M) | Nein | Ja | schlechteste Wahl | ★☆☆☆☆ |
| Bezug im Referenzalter (**{ey}+{str(em).zfill(2)}M**) | Ja | Nein | solide Wahl | ★★★☆☆ |
| Bezug bis **65** | Ja | Nein | beste Wahl | ★★★★★ |
""")
        early_enabled = False
        start_j, start_m = 65, 0

    elif is_trans_64_69:
        st.markdown("#### Übergangsjahrgang")
        st.info("Vorbezug im Free-Modul nicht vorgesehen. Referenzalter **65 Jahre** (Zuschlag sichern).")
        early_enabled = False
        start_j, start_m = 65, 0

    else:
        st.markdown("#### Frühbezugsalter (Jahre)")
        start_j = st.selectbox("Wählen Sie das Startjahr", options=[63, 64], index=1, label_visibility="collapsed")
        st.markdown("#### Monat im Startjahr")
        start_m = st.select_slider("Monat", options=list(range(12)), value=0, label_visibility="collapsed")
        early_enabled = True

    st.markdown("#### Planungsdauer (bis Alter)")
    plan_age = st.slider("bis Alter (Jahre)", 65, 100, PLANUNGSDAUER_DEFAULT, 1, label_visibility="collapsed")
    st.markdown(f"**Geplanter Horizont:** bis {plan_age} Jahre")

with colR:
    st.markdown(f"""
<div class='legend'>
  <span><span class='dot dot-blue'></span> Normale AHV (65)</span>
  <span><span class='dot dot-orange'></span> Vorbezug ({start_j} J {start_m} M)</span>
</div>
""", unsafe_allow_html=True)

    jahresrente = 12_000.0
    reg_start_m = NORMAL_RENTENALTER * 12

    if early_enabled:
        start_total_m = start_j * 12 + start_m
        df, kuerzung_total, months_early, be_age = berechne_kurven(start_total_m, plan_age, jahresrente)

        chart = alt.Chart(df).transform_fold(
            ["Normale AHV (65)", "Vorbezug"], as_=["Variante", "Wert"]
        ).mark_line(strokeWidth=2.5).encode(
            x=alt.X("Alter:Q", axis=alt.Axis(title="Alter (Jahre)", grid=False, labelFontSize=12, titleFontSize=14)),
            y=alt.Y("Wert:Q", axis=alt.Axis(title="Kumulierte Rente (Einheiten)", grid=True, labelFontSize=12, titleFontSize=14)),
            color=alt.Color("Variante:N", legend=None)
        ).properties(height=360, padding={"left":10,"top":10,"right":10,"bottom":10}).configure_view(strokeWidth=0)

        if be_age is not None:
            be_row = df.iloc[(df["Alter"] - be_age).abs().argsort()[:1]]
            be_y = float((be_row["Normale AHV (65)"].values[0] + be_row["Vorbezug"].values[0]) / 2)
            be_df = pd.DataFrame({"Alter":[be_age], "Wert":[be_y]})
            be_rule = alt.Chart(be_df).mark_rule(color="#0EA5E9", strokeDash=[4,4], strokeWidth=1.5).encode(x="Alter:Q")
            be_text = alt.Chart(be_df).mark_text(dy=-12, align="center", fontSize=13, fontWeight="bold", color="#0F172A").encode(
                x="Alter:Q", y=alt.Y("Wert:Q", axis=None), text=alt.value(f"Break-even • {format_age(be_age)}")
            )
            chart = chart + be_rule + be_text

        st.altair_chart(chart, use_container_width=True)

        k1, k2, k3 = st.columns(3)
        with k1:
            st.markdown("<div class='kpi'><h4>Break-even</h4><p>"+format_age(be_age)+"</p></div>", unsafe_allow_html=True)
        with k2:
            st.markdown("<div class='kpi'><h4>Kürzung (gesamt)</h4><p>"+f"{kuerzung_total*100:.2f}%"+ "</p></div>", unsafe_allow_html=True)
        with k3:
            years = months_early//12; months = months_early%12
            vor_txt = "0"
            if months_early>0:
                vor_txt = (f"{years} J " if years>0 else "") + (f"{months} M" if months>0 or years==0 else "")
            st.markdown("<div class='kpi'><h4>Dauer des Vorbezugs</h4><p>"+vor_txt+"</p></div>", unsafe_allow_html=True)

        st.markdown("---")
        if be_age is None:
            st.markdown("<div class='pill good'>Bis zum gewählten Planungsalter: Vorbezug lohnt sich.</div>", unsafe_allow_html=True)
        else:
            bis_age = age_minus_one_month(be_age)
            st.markdown(f"<div class='pill good'>✅ <b>Bis Alter {format_age(bis_age)}</b>: Vorbezug lohnt sich.</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='pill warn'>⚠️ <b>Ab Alter {format_age(be_age)}</b>: Der normale Bezug ist vorteilhafter.</div>", unsafe_allow_html=True)

    else:
        df = pd.DataFrame({"Alter": np.arange(reg_start_m, plan_age*12+1)/12.0, "Normale AHV (65)": np.cumsum(np.ones(plan_age*12 - reg_start_m + 1))})
        chart = alt.Chart(df).mark_line(strokeWidth=2.5, color="#2563EB").encode(
            x=alt.X("Alter:Q", axis=alt.Axis(title="Alter (Jahre)", grid=False, labelFontSize=12, titleFontSize=14)),
            y=alt.Y("Normale AHV (65):Q", axis=alt.Axis(title="Kumulierte Rente (Einheiten)", grid=True, labelFontSize=12, titleFontSize=14))
        ).properties(height=360, padding={"left":10,"top":10,"right":10,"bottom":10}).configure_view(strokeWidth=0)
        st.altair_chart(chart, use_container_width=True)
        st.markdown("<div class='pill'>Regulärer Bezug: solide Wahl (Zuschlag sichern). Aufschub simulieren in Modul 2.</div>", unsafe_allow_html=True)

st.caption("© FINAURA · Free Flagship · v1.1 · Light Mode forced")
