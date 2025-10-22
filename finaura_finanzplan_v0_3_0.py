"""
FINAURA – Finanzplan (MVP)
Version: 0.3.0
Date: 2025-10-19 (Europe/Zurich)
Change: Neuer Tab/Modul "Finanzplan" (Zwei-Spalten-Layout: links Eingaben, rechts Auswertung). Enthält Altair-Chart,
        Sparquote, freies Budget, einfache Handlungsempfehlung (rule-based) und "Plan freigeben" (read-only, MVP).
Install requirements:
    pip install streamlit altair pandas

Run the app:
    streamlit run finaura_finanzplan_v0_3_0.py

Storage path:
    ~/Downloads/finaura_app (symlink to ~/Documents/Finaura/app)
"""
__version__ = "0.3.0"

import math
from dataclasses import dataclass
import pandas as pd
import altair as alt
import streamlit as st

# -------------------------
# Page & Sidebar
# -------------------------
st.set_page_config(page_title="FINAURA – Finanzplan (MVP)", page_icon="📊", layout="wide")
with st.sidebar:
    st.markdown("### FINAURA")
    st.caption("Swiss Precision – Finanzklarheit")
    st.markdown(f"**Version:** {__version__}")
    st.markdown("*Stand:* 2025-10-19")
    st.markdown("---")
    st.info("MVP: Minimal & pragmatisch. Fokus: Klarheit, Next Steps.")

st.title("📊 Mein Finanzplan – MVP")
st.caption("Zwei‑Spalten‑Layout: Links Eingaben, rechts Auswertung.")

# -------------------------
# Eingaben (links)
# -------------------------
colL, colR = st.columns([1,1], gap="large")

with colL:
    st.subheader("Eingaben")
    income = st.number_input("Monatliches Netto‑Einkommen (CHF)", min_value=0, step=100, value=7500)
    fixed = st.number_input("Fixkosten pro Monat (CHF)", min_value=0, step=50, value=3200, help="Miete, KK, ÖV, Versicherungen, Abos …")
    living = st.number_input("Lebenshaltung/Variabel (CHF)", min_value=0, step=50, value=2500, help="Lebensmittel, Freizeit, Sonstiges")
    reserve = st.number_input("Liquiditäts‑Reserve (CHF)", min_value=0, step=100, value=6000, help="Cash / Tagesgeld – für Notgroschen")
    months_reserve_target = st.slider("Ziel Notgroschen (Monatslöhne)", 0, 12, 3)

    st.markdown("**Vorsorge (optional, grob):**")
    bvg = st.number_input("BVG‑Guthaben (CHF)", min_value=0, step=500, value=0)
    _3a = st.number_input("Säule 3a (CHF)", min_value=0, step=500, value=0)

    st.markdown("---")
    simulate = st.checkbox("12‑Monats‑Projektion anzeigen", value=True)
    st.markdown(" ")
    plan_release = st.toggle("🔓 Finanzplan freigeben (read‑only, MVP)", value=False,
                             help="Ermöglicht verifizierten Finanzplaner:innen Einsicht (MVP‑Simulation, anonym).")

# -------------------------
# Auswertung (rechts)
# -------------------------
def format_chf(x: float) -> str:
    return "CHF {:,.0f}".format(x).replace(",", "'")

with colR:
    st.subheader("Auswertung")
    total_expenses = fixed + living
    savings = max(income - total_expenses, 0)
    savings_rate = (savings / income * 100) if income > 0 else 0.0
    free_budget = savings  # synonym im MVP

    # KPI Cards
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Sparquote", f"{savings_rate:.1f} %")
    kpi2.metric("Freies Budget / Monat", format_chf(free_budget))
    kpi3.metric("Fixkosten‑Quote", f"{(fixed / income * 100):.1f} % " if income>0 else "—")

    # Notgroschen‑Check
    months_reserve_have = (reserve / income) if income > 0 else 0
    need_reserve_chf = max(0, (months_reserve_target - months_reserve_have) * income) if income>0 else 0

    # Handlungsempfehlung (rule‑based, bewusst simpel)
    st.markdown("### Handlungsempfehlung (MVP)")
    bullets = []
    if months_reserve_have < months_reserve_target and need_reserve_chf > 0:
        bullets.append(f"🔹 Zuerst Notgroschen auffüllen auf **{months_reserve_target} Monatslöhne** ({format_chf(need_reserve_chf)} fehlen).")
    if savings_rate < 10:
        bullets.append("🔹 **Sparquote < 10 %** – prüfe Fixkosten & Abos; setze ein Monatsbudget mit Obergrenzen.")
    elif savings_rate < 20:
        bullets.append("🔹 **Sparquote ~10–20 %** – solide. Nächster Schritt: regelmässige 3a‑Einzahlungen prüfen.")
    else:
        bullets.append("🔹 **Sparquote ≥ 20 %** – sehr gut! Reserve stabilisieren und Investitionsplan (3a / ETF) definieren.")
    if bvg + _3a > 0:
        bullets.append("🔹 Vorsorge vorhanden – abgestimmte 3a‑Strategie prüfen (Kosten, Allokation).")
    if not bullets:
        bullets.append("🔹 Lage ist ausgeglichen – behalte dein Budget bei und spare automatisiert.")

    for b in bullets:
        st.write(b)

    # Chart: Einnahmen vs. Ausgaben + kumulative Ersparnis (12 Monate)
    try:
        months = list(range(1, 13))
        df = pd.DataFrame({
            "Monat": months,
            "Einkommen": [income]*12,
            "Ausgaben": [total_expenses]*12,
            "Sparen": [savings]*12,
        })
        df["Kumulierte Ersparnis"] = df["Sparen"].cumsum()

        base = alt.Chart(df).encode(x=alt.X("Monat:O", title="Monat"))
        bars = base.mark_bar().encode(y=alt.Y("Einkommen:Q", title="CHF"), tooltip=["Monat","Einkommen","Ausgaben","Sparen"])
        bars2 = base.mark_bar(opacity=0.65).encode(y="Ausgaben:Q")
        line = base.mark_line(point=True).encode(y=alt.Y("Kumulierte Ersparnis:Q", title="CHF"))

        st.markdown("#### Einnahmen/ Ausgaben & kumulative Ersparnis (12M)")
        st.altair_chart((bars + bars2 + line).resolve_scale(y="independent"), use_container_width=True)
    except Exception as e:
        st.warning(f"Chart konnte nicht erzeugt werden: {{e}}")

# -------------------------
# Hinweise & Status
# -------------------------
st.divider()
if plan_release:
    st.success("Freigabe aktiv (MVP‑Simulation). Verifizierte Finanzplaner:innen können diesen Plan read‑only einsehen.")
else:
    st.info("Freigabe ist aus. Der Plan bleibt privat (anonym).")

st.caption("Hinweis: Dies ist ein MVP. Keine rechtsverbindliche Beratung. Für echte Produktiv‑Freigabe wird ein verknüpftes Kunden/Thread‑System genutzt.")
