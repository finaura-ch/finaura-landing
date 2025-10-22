# FINAURA — AHV Vorbezug (Free · v1.3.5 · Apple Story)
# Neu in v1.3.5:
# • Break‑even als DOT (ohne Linie), dezentes Label
# • Ein-Satz-Resultat (R1, neutral-professionell)
# • ÜG-Badge mit Pro‑Verweis (exakte reduzierte Kürzungssätze)
# Start: streamlit run finaura_ahv_vorbezug_v1_3_5.py

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import date

# ---- Page / CSS ----
st.set_page_config(page_title="FINAURA — AHV Vorbezug", page_icon="🇨🇭", layout="wide")
st.markdown("""
<style>
html, body, .stApp { background:#FFFFFF; color:#0F172A; }
.block-container { padding-top: 1.0rem; padding-bottom: .6rem; max-width: 1200px; }
.h1 { font-weight: 700; font-size: 24px; letter-spacing:.2px; margin-bottom:2px; }
.h2 { color:#64748B; font-size: 12px; margin-bottom: 14px; }
.legend { display:flex; gap:16px; align-items:center; margin:0 0 10px 0;}
.dot { width:10px; height:10px; border-radius:999px; display:inline-block;}
.dot-b { background:#2563EB; } .dot-o { background:#EA580C; }
.badge { display:inline-flex; align-items:center; gap:8px; background:#F1F5F9; color:#0F172A; border:1px solid #CBD5E1;
         padding:6px 10px; border-radius:999px; font-size:11.5px; font-weight:600; }
.badge .d { width:8px; height:8px; border-radius:999px; background:#9333EA; display:inline-block; }
.badge a { text-decoration:none; color:#2563EB; font-weight:700; }
.kpi { background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px; padding:12px 14px; }
.kpi h4 { margin:0; font-size:12px; color:#475569; font-weight:500; display:flex; gap:6px; align-items:center;}
.kpi p { margin:3px 0 0 0; font-weight:700; font-size:20px; }
.info-icon { display:inline-flex; align-items:center; justify-content:center; width:16px; height:16px; font-size:11px;
             border-radius:999px; background:#E5E7EB; color:#374151; cursor:help; }
.pill { border:1px solid #E2E8F0; border-radius:12px; padding:10px 12px; }
.good { background:#EAF6FF; border-color:#93C5FD; }
.warn { background:#FFFBEB; border-color:#FCD34D; }
.small { color:#64748B; font-size:12px; }
.result { font-size:16px; font-weight:600; margin-top:4px; }
</style>
""", unsafe_allow_html=True)

# ---- Altair theme ----
def theme():
    return {"config": {
        "axis": {"gridColor":"#E2E8F0","labelFont":"-apple-system,BlinkMacSystemFont,sans-serif",
                 "titleFont":"-apple-system,BlinkMacSystemFont,sans-serif","domainColor":"#E2E8F0","domainWidth":0.5},
        "axisX": {"grid": False}, "axisY": {"gridDash":[4,4], "grid":True},
        "range": {"category": ["#2563EB","#EA580C"]},
        "view":{"strokeWidth":0}, "background":"#FFFFFF"}}
alt.themes.register("apple_story_v135", theme); alt.themes.enable("apple_story_v135")

# ---- Constants ----
NORMAL_RENTENALTER = 65
STANDARD_K = 0.068
K_MONAT = STANDARD_K/12
PLAN_DEFAULT = 85
UEB_61_63 = {1961:(64,3), 1962:(64,6), 1963:(64,9)}

# ---- Helpers ----
def ug_min_start_for_woman(year:int):
    if year in UEB_61_63: j,m = UEB_61_63[year]; return j*12+m
    if 1964 <= year <= 1969: return 65*12
    return None

def curves(start_m:int, end_age:int, jahresrente:float=12000.0):
    m_norm = jahresrente/12.0
    reg_m = NORMAL_RENTENALTER*12
    months_early = reg_m - start_m
    k_total = max(0.0, months_early*K_MONAT); k_total = min(k_total, 0.20)
    m_vor = m_norm*(1-k_total)
    ages_m = np.arange(min(reg_m,start_m), end_age*12+1)
    cf_n = np.where(ages_m>=reg_m, m_norm, 0.0); cf_v = np.where(ages_m>=start_m, m_vor, 0.0)
    cum_n = np.cumsum(cf_n); cum_v = np.cumsum(cf_v)
    df = pd.DataFrame({"Alter":ages_m/12.0,"Normale AHV (65)":cum_n,"Vorbezug":cum_v})
    diff = cum_n - cum_v; idx = np.where(diff>=0)[0]
    be_age = float(ages_m[idx[0]]/12.0) if idx.size>0 else None
    return df, k_total, months_early, be_age

def fmt_age(a:float):
    if a is None: return "—"
    j=int(a); m=int(round((a-j)*12)); 
    if m==12: j+=1; m=0
    return f"{j} Jahre {m} Monate"

def minus1m(a:float):
    j=int(a); m=int(round((a-j)*12))-1
    if m<0: j-=1; m=11
    return max(j,0)+m/12.0

# ---- UI ----
st.markdown("<div class='h1'>FINAURA — AHV Vorbezug</div>", unsafe_allow_html=True)
st.markdown("<div class='h2'>Monatsgenauer Vergleich · Swiss Precision</div>", unsafe_allow_html=True)

left, right = st.columns([0.44, 0.56], gap="large")

with left:
    s = st.session_state
    if "g" not in s: s.g="Frau"
    if "alt" not in s: s.alt=False
    if "m" not in s: s.m=0
    if "plan" not in s: s.plan=PLAN_DEFAULT

    c1,c2 = st.columns(2)
    if c1.button("Frau", use_container_width=True): s.g="Frau"
    if c2.button("Mann", use_container_width=True): s.g="Mann"
    is_f = s.g=="Frau"

    years = list(range(1940, date.today().year-17))
    y = st.select_slider("Jahrgang", options=years, value=1963, label_visibility="collapsed")

    ug_min = ug_min_start_for_woman(y) if is_f else None
    is_ug = ug_min is not None

    if is_ug and not s.alt:
        ey, em = ug_min//12, ug_min%12
        st.markdown(
            f"<span class='badge'><span class='d'></span>"
            f"Übergangsjahr erkannt · empfohlen: {ey} J {em} M · "
            f"<a title='Exakte reduzierte Kürzungssätze & Zuschläge in Pro' href='#'>Pro-Version</a>"
            f"</span>",
            unsafe_allow_html=True
        )
        st.selectbox("Startjahr (empfohlen)", options=[ey], index=0, label_visibility="collapsed", disabled=True)
        st.select_slider("Monat", options=[em], value=em, label_visibility="collapsed", disabled=True)
        b1,b2 = st.columns(2)
        if b1.button("Alternative (62/63) anzeigen", use_container_width=True): s.alt=True
        if b2.button("Zurücksetzen", use_container_width=True): s.alt=False; s.m=0; s.plan=PLAN_DEFAULT
        start_j, start_m = ey, em
    else:
        start_j = st.selectbox("Startjahr", options=([62,63,64] if is_ug else [63,64]), index=(1 if is_ug else 1), label_visibility="collapsed")
        st.select_slider("Monat", options=list(range(12)), value=s.m, label_visibility="collapsed", key="m")
        start_m = s.m
        if is_ug and (start_j*12+start_m) < ug_min:
            ey, em = ug_min//12, ug_min%12
            st.caption(f"⚠️ Vor dem empfohlenen ÜG-Start ({ey} J {em} M) entfällt der Zuschlag. Free rechnet mit 6.8% p.a. (exakte Reduktionen: Pro).")

    plan = st.slider("bis Alter (Jahre)", 75, 100, s.plan, 1, label_visibility="collapsed"); s.plan=plan
    st.markdown(f"<span class='small'>Horizont: bis {plan}</span>", unsafe_allow_html=True)

with right:
    legend_tip = "Vorbezugslinie (Free) nutzt Standard-Kürzung 6.8% p.a."
    eff_j = (ug_min//12 if is_ug and not s.alt else start_j)
    eff_m = (ug_min%12 if is_ug and not s.alt else start_m)
    st.markdown(
        f"<div class='legend'><span><span class='dot dot-b'></span> Normale AHV (65)</span>"
        f"<span><span class='dot dot-o'></span> Vorbezug (<span title='{legend_tip}'>ⓘ</span> {eff_j} J {eff_m} M)</span></div>",
        unsafe_allow_html=True
    )

    start_total = (ug_min if is_ug and not s.alt else (start_j*12+start_m))
    df, k_total, months_early, be_age = curves(start_total, plan)

    # Linien (kräftig) + Break-even DOT
    base = alt.Chart(df).transform_fold(["Normale AHV (65)","Vorbezug"], as_=["Variante","Wert"])
    lines = base.mark_line(strokeWidth=3.0).encode(
        x=alt.X("Alter:Q", axis=alt.Axis(title="Alter (Jahre)", grid=False, labelFontSize=12, titleFontSize=13)),
        y=alt.Y("Wert:Q", axis=alt.Axis(title="Kumuliert", grid=True, labelFontSize=12, titleFontSize=13)),
        color=alt.Color("Variante:N", legend=None)
    )
    chart = lines

    if be_age is not None:
        be_row = df.iloc[(df["Alter"] - be_age).abs().argsort()[:1]]
        # Position des Dots – mittig zwischen den Kurven (wirkt balanciert)
        be_y = float((be_row["Normale AHV (65)"].values[0] + be_row["Vorbezug"].values[0]) / 2)
        be_df = pd.DataFrame({"Alter":[be_age], "Wert":[be_y]})
        dot = alt.Chart(be_df).mark_point(size=80, filled=True, color="#0EA5E9").encode(x="Alter:Q", y="Wert:Q")
        label = alt.Chart(be_df).mark_text(dy=-12, align="center", fontSize=12.5, fontWeight="bold", color="#0F172A").encode(
            x="Alter:Q", y="Wert:Q", text=alt.value(f"Break-even {fmt_age(be_age)}")
        )
        chart = chart + dot + label

    st.altair_chart(chart.properties(height=360), use_container_width=True)

    # KPIs
    K1,K2,K3 = st.columns(3)
    with K1: st.markdown("<div class='kpi'><h4>Break-even</h4><p>"+fmt_age(be_age)+"</p></div>", unsafe_allow_html=True)
    with K2:
        tip="Free nutzt 6.8% p.a. zur Vergleichbarkeit. ÜG hat reduzierte Sätze – exakt in FINAURA Pro."
        st.markdown(f"<div class='kpi'><h4>Kürzung gesamt <span class='info-icon' title='{tip}'>ⓘ</span></h4><p>"+f"{k_total*100:.2f}%"+ "</p></div>", unsafe_allow_html=True)
    with K3:
        yrs = months_early//12; mos = months_early%12
        txt = "0" if months_early<=0 else ((f'{yrs} J ' if yrs>0 else '') + (f'{mos} M' if mos>0 or yrs==0 else ''))
        st.markdown("<div class='kpi'><h4>Vorbezugs‑Dauer</h4><p>"+txt+"</p></div>", unsafe_allow_html=True)

    # EIN-SATZ-RESULTAT (R1)
    if be_age is None:
        st.markdown("<div class='result'>Bei Ihrer Lebenserwartung lohnt sich der Vorbezug.</div>", unsafe_allow_html=True)
    else:
        if plan < be_age:
            st.markdown("<div class='result'>Bei Ihrer Lebenserwartung lohnt sich der Vorbezug.</div>", unsafe_allow_html=True)
        else:
            # Vor-Teil bis BE, danach normal besser
            j = int(be_age); m = int(round((be_age - j)*12)); 
            if m==12: j+=1; m=0
            st.markdown(f"<div class='result'>Bei Ihrer Lebenserwartung lohnt sich der Vorbezug bis Alter {j}. Danach ist der reguläre Bezug vorteilhafter.</div>", unsafe_allow_html=True)

# Details
with st.expander("Details & Hinweise"):
    st.write("• Free vergleicht mit Standard‑Kürzung **6.8 % p.a.** (monatsgenau).")
    st.write("• Übergangsjahrgänge (Frauen 1961–1969) werden erkannt; empfohlenes Startalter wird fixiert.")
    st.write("• **Pro-Version:** exakte reduzierte Kürzungssätze & Zuschläge der ÜG (einkommensabhängig).")
    st.write("• Break‑even = erstes Alter, an dem *Normale AHV (65)* ≥ *Vorbezug*.")
    st.write("• Horizont: Slider **75–100**, Standard **85**.")

st.caption("© FINAURA · v1.3.5 Apple Story · Dot-BE · 1-Satz-Resultat (R1)")
