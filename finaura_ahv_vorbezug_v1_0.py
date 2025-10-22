# FINAURA — AHV Vorbezug (Free) — v1.0
# Option A: Apple-clean UI, Break-even Linie & Label, Übergangsgeneration-Logik
# Requires: pip install streamlit altair pandas numpy

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import date

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
    """Erzeugt kumulierte Kurven & Break-even als Alter in Dezimaljahren."""
    monat_norm = jahresrente / 12.0
    reg_start_m = NORMAL_RENTENALTER * 12

    # Kürzung
    months_early = reg_start_m - start_alter_monate
    kuerzung_total = max(0.0, months_early * MONATLICHER_KUERZUNGSFAKTOR)
    kuerzung_total = min(kuerzung_total, 0.20)  # Sicherheitscap
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

    # Break-even suchen (erster Monat, ab dem Vorbezug >= Normal)
    diff = cum_vor - cum_norm
    idx = np.where(diff >= 0)[0]
    be_age = float(ages_m[idx[0]]/12.0) if idx.size>0 else None

    return df, kuerzung_total, months_early, be_age

def format_be(be_age:float):
    if be_age is None:
        return "—"
    j = int(be_age)
    m = int(round((be_age - j) * 12))
    if m == 12:
        j += 1; m = 0
    return f"{j} Jahre {m} Monate"

# ---------------- Page Config & Styles ----------------
st.set_page_config(page_title="FINAURA — AHV Vorbezug", page_icon="🇨🇭", layout="wide")

# Light look & legibility (works in both Streamlit themes)
st.markdown("""
<style>
html, body, .stApp { background: #FFFFFF; color:#0F172A; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
.title { font-weight:700; font-size:26px; letter-spacing:.2px; }
.subtitle { color:#475569; font-size:14px; margin-bottom:14px; }
.legend { display:flex; gap:18px; align-items:center; margin:6px 0 10px 0;}
.dot { width:10px; height:10px; border-radius:999px; display:inline-block;}
.dot-blue { background:#2563EB; } /* Blue-600 */
.dot-orange { background:#EA580C; } /* Orange-600 */
.pill { background:#F8FAFC; border:1px solid #E2E8F0; padding:12px 14px; border-radius:14px; }
.good { background:#ECFDF5; border:1px solid #A7F3D0; }
.warn { background:#FEF3C7; border:1px solid #FDE68A; }
.kpi { background:#F8FAFC; border:1px solid #E2E8F0; border-radius:12px; padding:12px 14px; }
.kpi h4 { margin:0; font-size:14px; color:#475569; }
.kpi p { margin:4px 0 0 0; font-weight:600; }
.stButton>button { border-radius:12px; height:44px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>FINAURA — AHV Vorbezug</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Monatsgenauer Vergleich · Swiss Precision</div>", unsafe_allow_html=True)

# ---------------- Layout ----------------
colL, colR = st.columns([0.46, 0.54], gap="large")

with colL:
    # Geschlecht
    st.markdown("#### Geschlecht")
    c1, c2 = st.columns(2)
    if "geschlecht" not in st.session_state:
        st.session_state.geschlecht = "Frau"
    if c1.button("Frau", use_container_width=True):
        st.session_state.geschlecht = "Frau"
    if c2.button("Mann", use_container_width=True):
        st.session_state.geschlecht = "Mann"
    geschlecht = "F" if st.session_state.geschlecht == "Frau" else "M"

    # Jahrgang
    st.markdown("#### Jahrgang")
    years = list(range(1940, date.today().year - 17))
    jahrgang = st.select_slider("Jahr", options=years, value=1963, label_visibility="collapsed")

    # Übergangsgeneration Ableitungen
    is_trans_61_63 = (geschlecht == "F") and (jahrgang in UEBERGANG_61_63.keys())
    is_trans_64_69 = (geschlecht == "F") and (1964 <= jahrgang <= 1969)

    # Vorbezugsalter / Buttons
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
        st.markdown("#### Frühbezugsalter")
        if "vorJ" not in st.session_state: st.session_state.vorJ = 64
        b1, b2, b3 = st.columns(3)
        if b1.button("63", use_container_width=True): st.session_state.vorJ = 63
        if b2.button("64", use_container_width=True): st.session_state.vorJ = 64
        b3.button("65", use_container_width=True, disabled=True)
        start_j = int(st.session_state.vorJ)

        st.markdown("#### Monat im Startjahr")
        if "vorM" not in st.session_state: st.session_state.vorM = 0
        st.session_state.vorM = st.select_slider("Monat", options=list(range(0,12)), value=st.session_state.vorM, label_visibility="collapsed")
        start_m = int(st.session_state.vorM)
        early_enabled = True

    st.markdown("#### Planungsdauer (bis Alter)")
    plan_age = st.slider("bis Alter (Jahre)", 65, 100, PLANUNGSDAUER_DEFAULT, 1)

with colR:
    # Legende
    st.markdown(f"""
<div class='legend'>
  <span><span class='dot dot-blue'></span> Normale AHV (65)</span>
  <span><span class='dot dot-orange'></span> Vorbezug</span>
</div>
""", unsafe_allow_html=True)

    # normierte Jahresrente für Vergleich (CHF nicht erforderlich in Free)
    jahresrente = 12_000.0
    reg_start_m = NORMAL_RENTENALTER * 12

    if early_enabled:
        start_total_m = start_j * 12 + start_m
        df, kuerzung_total, months_early, be_age = berechne_kurven(start_total_m, plan_age, jahresrente)

        # Basischart
        chart = alt.Chart(df).transform_fold(
            ["Normale AHV (65)", "Vorbezug"], as_=["Variante", "Wert"]
        ).mark_line(strokeWidth=2).encode(
            x=alt.X("Alter:Q", axis=alt.Axis(title="Alter (Jahre)")),
            y=alt.Y("Wert:Q", axis=alt.Axis(title="Kumuliert (Einheiten)")),
            color=alt.Color(
                "Variante:N",
                scale=alt.Scale(
                    domain=["Normale AHV (65)", "Vorbezug"],
                    range=["#2563EB", "#EA580C"]
                ),
                legend=alt.Legend(orient="top", title=None)
            )
        ).properties(height=360)

        # Break-even Rule + Label
        if be_age is not None:
            be_row = df.iloc[(df["Alter"] - be_age).abs().argsort()[:1]]
            be_y = float(be_row["Normale AHV (65)"])
            be_df = pd.DataFrame({"Alter":[be_age], "Wert":[be_y]})

            be_rule = alt.Chart(be_df).mark_rule(
                color="#0EA5E9", strokeDash=[6,4], strokeWidth=2
            ).encode(x="Alter:Q")

            be_text = alt.Chart(be_df).mark_text(
                dy=-8, align="center", fontSize=12, color="#0F172A"
            ).encode(
                x="Alter:Q",
                y=alt.value(0),
                text=alt.value(f"Break-even • {format_be(be_age)}")
            )

            chart = chart + be_rule + be_text

        st.altair_chart(chart, use_container_width=True)

        # KPIs
        k1, k2, k3 = st.columns(3)
        with k1:
            st.markdown("<div class='kpi'><h4>Break-even</h4><p>"+format_be(be_age)+"</p></div>", unsafe_allow_html=True)
        with k2:
            st.markdown("<div class='kpi'><h4>Kürzung</h4><p>"+f"{kuerzung_total*100:.2f}%"+ "</p></div>", unsafe_allow_html=True)
        with k3:
            years = months_early//12; months = months_early%12
            vor_txt = "0"
            if months_early>0:
                vor_txt = (f"{years} Jahr(e) " if years>0 else "") + (f"{months} Monat(e)" if months>0 or years==0 else "")
            st.markdown("<div class='kpi'><h4>Vorbezug</h4><p>"+vor_txt+"</p></div>", unsafe_allow_html=True)

        st.markdown("---")
        # Urteil
        if be_age is None:
            st.markdown("<div class='pill good'>Bis zum gewählten Planungsalter: Vorbezug lohnt sich.</div>", unsafe_allow_html=True)
        else:
            belowY = max(65, int(np.floor(be_age))-1)
            aboveY = int(np.ceil(be_age))
            st.markdown(f"<div class='pill good'>Bis Alter <b>{belowY}</b>: Vorbezug lohnt sich.</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='pill warn'>Ab Alter <b>{aboveY}</b>: Der normale Bezug ist vorteilhafter.</div>", unsafe_allow_html=True)

    else:
        # Nur Normalkurve (z. B. Übergangsgeneration ohne Vorbezug im Modul 1)
        df = pd.DataFrame({
            "Alter": np.arange(reg_start_m, plan_age*12+1)/12.0,
            "Normale AHV (65)": np.cumsum(np.ones(plan_age*12 - reg_start_m + 1))
        })
        chart = alt.Chart(df).mark_line(strokeWidth=2, color="#2563EB").encode(
            x=alt.X("Alter:Q", axis=alt.Axis(title="Alter (Jahre)")),
            y=alt.Y("Normale AHV (65):Q", axis=alt.Axis(title="Kumuliert (Einheiten)"))
        ).properties(height=360)
        st.altair_chart(chart, use_container_width=True)
        st.markdown("<div class='pill'>Regulärer Bezug: solide Wahl (Zuschlag sichern). Aufschub simulieren in Modul 2.</div>", unsafe_allow_html=True)

st.caption("© FINAURA · Free Flagship · v1.0 · UI polished (Apple-clean).")
