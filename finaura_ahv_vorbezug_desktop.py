
# ==============================================
# FINAURA – AHV Vorbezug Simulator (Desktop)
# Version: 0.1.0   |   Datum: 2025-10-19 (Europe/Zurich)
# CHANGELOG kurz: Erste Desktop-Variante mit Auswahl 63/64, 65 gesperrt, Planhorizont + Grafik.
# Speicherpfad-Empfehlung: ~/Downloads/finaura_app (symlink to ~/Documents/Finaura/app)
#
# Installiere Abhängigkeiten (Terminal):
#   pip install streamlit altair pandas
#
# Starte die App (Terminal):
#   streamlit run finaura_ahv_vorbezug_desktop.py
# ==============================================

from __future__ import annotations
import math
import pandas as pd
import altair as alt
import streamlit as st

__version__ = "0.1.0"

st.set_page_config(
    page_title="FINAURA – AHV Vorbezug (Desktop)",
    page_icon="🇨🇭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Minimalistisches Swiss-Precision Styling ----------
st.markdown(
    """
    <style>
    :root {
      --finaura-blue: #0B61A4;
      --finaura-blue-50: #E6F0FA;
      --finaura-grey: #E9ECEF;
      --finaura-grey-strong: #C9CED3;
      --finaura-green: #0B9A6D;
      --finaura-red: #C43B3B;
      --radius: 1rem;
    }
    .block-title {
      font-weight: 700;
      font-size: 1.1rem;
      margin-bottom: .25rem;
    }
    .muted {
      color: #6c757d;
      font-size: 0.9rem;
    }
    div[data-testid="stHorizontalBlock"] > div {
      border: 1px solid var(--finaura-grey);
      background: white;
      border-radius: var(--radius);
      padding: 1rem;
    }
    /* 65 Button disabled look */
    .locked {
      background: var(--finaura-grey);
      color: #6c757d;
      border: 1px solid var(--finaura-grey-strong);
      padding: .6rem 1rem;
      border-radius: .75rem;
      cursor: not-allowed;
      user-select: none;
      font-weight: 600;
      text-align: center;
    }
    .age-btn {
      display: inline-block;
      padding: .6rem 1rem;
      border-radius: .75rem;
      border: 1px solid var(--finaura-blue);
      color: var(--finaura-blue);
      font-weight: 700;
      background: white;
      transition: all .15s ease;
      text-align: center;
      width: 100%;
    }
    .age-btn.active {
      background: var(--finaura-blue);
      color: white;
    }
    .hint {
      background: var(--finaura-blue-50);
      border-left: 4px solid var(--finaura-blue);
      padding: .75rem 1rem;
      border-radius: .5rem;
      font-size: .9rem;
    }
    .legend-dot {
      display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:.25rem; background:#1f77b4;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### FINAURA")
    st.write("AHV Vorbezug – Desktop-Modul")
    st.caption(f"Version **{__version__}**")
    st.divider()
    st.markdown("**Modus**")
    st.write("• Unterjährige Renten (monatsgenau) aktiv")
    st.write("• Übergangsgenerationen-Hinweis integriert (vereinfachte Darstellung)")
    st.divider()
    st.markdown("**Hinweis**")
    st.caption("Die Rentenhöhe ist hier sekundär. In einer Pro-Version kann die individuelle Rentenhöhe und die Regeln der AHV-Übergangsgenerationen präzise parametriert werden.")

# ---------- Core: Parameter & Logik ----------

# Breakeven-Vorgaben (vom Nutzer)
BREAKEVEN_63 = 77.7
BREAKEVEN_64 = 78.7

# Wir normieren die jährliche Rente im regulären Bezug (65) auf 1.0.
# Daraus leiten wir die Reduktionsfaktoren so ab, dass die vorgegebenen Breakeven-Punkte exakt getroffen werden.
def reduction_factor(early_age: float, x_breakeven: float) -> float:
    # f = (x_b - 65) / (x_b - early_age)
    return (x_breakeven - 65.0) / (x_breakeven - early_age)

F63 = reduction_factor(63.0, BREAKEVEN_63)
F64 = reduction_factor(64.0, BREAKEVEN_64)

def cumulative_benefit(age_grid: pd.Series, start_age: float, annual_amount: float) -> pd.Series:
    # Monatsgenaue Integration: anteilige Rente ab Startalter
    # age_grid ist in Jahren (mit Dezimalstellen). Wir rechnen monatsweise linear.
    benefit = []
    for a in age_grid:
        if a <= start_age:
            benefit.append(0.0)
        else:
            # Monate seit Start
            months = (a - start_age) * 12.0
            benefit.append(annual_amount * (months / 12.0))
    return pd.Series(benefit, index=age_grid.index)

def make_dataframe(selected_early: int, horizon_max: float) -> pd.DataFrame:
    # Monatsfeinheit
    ages = pd.Series([63.0 + i/12.0 for i in range(int((horizon_max - 63.0) * 12) + 1)], name="Alter")
    # Early plan
    if selected_early == 63:
        f = F63
        be = BREAKEVEN_63
        early_age = 63.0
    else:
        f = F64
        be = BREAKEVEN_64
        early_age = 64.0

    cum_early = cumulative_benefit(ages, early_age, f * 1.0)
    cum_regular = cumulative_benefit(ages, 65.0, 1.0)

    df = pd.DataFrame({
        "Alter": ages,
        "Kumuliert – Vorbezug": cum_early,
        "Kumuliert – Regulär (65)": cum_regular,
    })
    df.attrs["breakeven"] = be
    df.attrs["early_age"] = early_age
    return df

# ---------- Header ----------
colA, colB = st.columns([1, 2], gap="large")
with colA:
    st.markdown('<div class="block-title">AHV Vorbezug – Auswahl</div>', unsafe_allow_html=True)
    st.caption("Desktop-Variante · Swiss Precision")

with colB:
    st.markdown(
        """
        <div class="hint">
        Dieser Simulator zeigt monatsgenau die kumulierten Leistungen beim <b>Vorbezug</b> (63/64) im Vergleich zum <b>regulären Bezug mit 65</b>.
        Der <i>Break-even</i> ist der Schnittpunkt beider Linien.
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

# ---------- Auswahlleiste (63/64 aktiv, 65 gesperrt) ----------
c1, c2, c3 = st.columns([1,1,1])

# Verwenden wir einen Radio-Switch für 63/64 und zeigen daneben einen gesperrten 65-Button
with c1:
    st.markdown('<div class="block-title">Vorbezug</div>', unsafe_allow_html=True)
    selected = st.radio("Startalter (Vorbezug):", options=[63, 64], horizontal=True, label_visibility="collapsed", index=0,
                        captions=["", ""], format_func=lambda x: f"{x} Jahre")

with c2:
    # Button-Look für aktive Auswahl-Buttons
    # Visual feedback: highlight the chosen age
    b63 = f'<div class="age-btn {"active" if selected==63 else ""}">63</div>'
    b64 = f'<div class="age-btn {"active" if selected==64 else ""}">64</div>'
    st.markdown(b63, unsafe_allow_html=True)
    st.markdown(b64, unsafe_allow_html=True)

with c3:
    st.markdown('<div class="block-title">Regulär</div>', unsafe_allow_html=True)
    st.markdown('<div class="locked">65 (fix)</div>', unsafe_allow_html=True)
    st.caption("Nicht wählbar – Referenzlinie")

st.divider()

# ---------- Planhorizont ----------
st.markdown('<div class="block-title">Planhorizont</div>', unsafe_allow_html=True)
horizon = st.slider("bis Alter", min_value=70, max_value=100, value=100, step=1)

# ---------- Daten & Grafik ----------
df = make_dataframe(selected, float(horizon))

# Altair-Chart
base = alt.Chart(df).transform_fold(
    ["Kumuliert – Vorbezug", "Kumuliert – Regulär (65)"],
    as_=["Kategorie", "Wert"]
).mark_line().encode(
    x=alt.X("Alter:Q", title="Alter (Jahre)", scale=alt.Scale(domain=[63, horizon])),
    y=alt.Y("Wert:Q", title="Kumulierte Rente (normiert)"),
    strokeDash=alt.StrokeDash("Kategorie", sort=["Kumuliert – Vorbezug", "Kumuliert – Regulär (65)"],
                              scale=alt.Scale(domain=["Kumuliert – Vorbezug", "Kumuliert – Regulär (65)"],
                                              range=[[], [4,4]])),
    tooltip=["Alter:Q", "Kategorie:N", "Wert:Q"]
).properties(
    height=420
)

# Breakeven-Punkt als Marker
be_age = df.attrs["breakeven"]
# Werte an BE ablesen (identisch)
be_value = df.loc[df["Alter"].sub(be_age).abs().idxmin(), "Kumuliert – Vorbezug"]

be_points = alt.Chart(pd.DataFrame({"Alter":[be_age], "Wert":[be_value]})).mark_point(size=100).encode(
    x="Alter:Q",
    y="Wert:Q",
    tooltip=[alt.Tooltip("Alter:Q", title="Break-even Alter"), alt.Tooltip("Wert:Q", title="Kumuliert")]
)

be_rule = alt.Chart(pd.DataFrame({"Alter":[be_age]})).mark_rule(strokeDash=[2,4]).encode(x="Alter:Q")

chart = base + be_points + be_rule

st.markdown("#### Kumulierte Leistungen (monatsgenau)")
st.altair_chart(chart, use_container_width=True)

# ---------- Kennzahlen ----------
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Vorbezug-Start", f"{int(df.attrs['early_age'])} Jahre")
with col2:
    st.metric("Break-even", f"{be_age:.1f} Jahre")
with col3:
    lead = "Vorbezug" if df.attrs['early_age'] in (63.0, 64.0) else "—"
    st.metric("Bis Break-even führt", lead)

st.caption("Hinweis: Übergangsgenerationen der AHV sind in dieser Basis-Version nur implizit berücksichtigt (monatsgenaue Summierung). Präzisere Zuschläge/Abzüge folgen in der Pro-Version.")

# ---------- Footer ----------
st.divider()
st.markdown(
    '<span class="muted">© FINAURA · Eleganz & Swiss Precision · Diese Version dient der Visualisierung der Vor-/Nachteile eines Vorbezugs.</span>',
    unsafe_allow_html=True
)
