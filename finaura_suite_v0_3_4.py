# coding: utf-8
"""
FINAURA – Suite (Chat + Finanzplan) – Combined App
Version: 0.3.4
Date: dynamic

Install requirements:
    pip install streamlit altair pandas

Run the app:
    streamlit run finaura_suite_v0_3_4.py
"""
__version__ = "0.3.4"

import streamlit as st
import pandas as pd

# Optional: Altair fallback
try:
    import altair as alt
    _HAS_ALTAIR = True
except Exception:
    _HAS_ALTAIR = False

# -------- Page --------
st.set_page_config(page_title="FINAURA – Suite (Chat + Finanzplan)", page_icon="🧭", layout="wide")
with st.sidebar:
    st.markdown("### FINAURA")
    st.caption("Swiss Precision – Pragmatic MVP")
    st.markdown(f"**Version:** {__version__}")
    st.divider()
    st.write("**Module heute:**")
    st.write("• Chat 0.2.7 – bezahlt & Zufriedenheits‑Freigabe")
    st.write("• Finanzplan 0.3.0 – Zwei‑Spalten‑MVP")

st.title("🧭 FINAURA – Suite")
tabs = st.tabs(["Für Kund:innen", "Finanzplan", "Für Finanzplaner:innen", "Moderation & Regeln"])

# -------- Tab: Für Kund:innen --------
with tabs[0]:
    st.subheader("💬 Anonymer Micro‑Advice (kostenpflichtig)")
    st.write("Der Chat läuft als stabiles Modul v0.2.7 mit Zahlung upfront und Zufriedenheits‑Freigabe (No‑Risk).")
    st.info("Aus Gründen der Stabilität läuft das Chat‑Modul separat.")

# -------- Tab: Finanzplan (eingebettet) --------
with tabs[1]:
    st.subheader("📊 Mein Finanzplan – MVP")
    st.caption("Zwei‑Spalten‑Layout: Links Eingaben, rechts Auswertung.")
    colL, colR = st.columns([1,1], gap="large")

    with colL:
        st.markdown("#### Eingaben")
        income = st.number_input("Monatliches Netto‑Einkommen (CHF)", min_value=0, step=100, value=7500)
        fixed = st.number_input("Fixkosten pro Monat (CHF)", min_value=0, step=50, value=3200, help="Miete, Krankenkasse, ÖV, Versicherungen, Abos …")
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

    def format_chf(x: float) -> str:
        return "CHF {:,.0f}".format(x).replace(",", "'")

    with colR:
        st.markdown("#### Auswertung")
        total_expenses = fixed + living
        savings = max(income - total_expenses, 0)
        savings_rate = (savings / income * 100) if income > 0 else 0.0
        free_budget = savings

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Sparquote", f"{savings_rate:.1f} %")
        kpi2.metric("Freies Budget / Monat", format_chf(free_budget))
        kpi3.metric("Fixkosten‑Quote", f"{(fixed / income * 100):.1f} % " if income>0 else "—")

        months_reserve_have = (reserve / income) if income > 0 else 0
        need_reserve_chf = max(0, (months_reserve_target - months_reserve_have) * income) if income>0 else 0

        st.markdown("### Handlungsempfehlung (MVP)")
        bullets = []
        if months_reserve_have < months_reserve_target and need_reserve_chf > 0:
            bullets.append(f"🔹 Zuerst Notgroschen auffüllen auf **{months_reserve_target} Monatslöhne** ({format_chf(need_reserve_chf)} fehlen).")
        if savings_rate < 10:
            bullets.append("🔹 Sparquote < 10 % – prüfe Fixkosten & Abos; setze ein Monatsbudget mit Obergrenzen.")
        elif savings_rate < 20:
            bullets.append("🔹 Sparquote ~10–20 % – solide. Nächster Schritt: regelmässige 3a‑Einzahlungen prüfen.")
        else:
            bullets.append("🔹 Sparquote ≥ 20 % – sehr gut! Reserve stabilisieren und Investitionsplan (3a / ETF) definieren.")
        if bvg + _3a > 0:
            bullets.append("🔹 Vorsorge vorhanden – abgestimmte 3a‑Strategie prüfen (Kosten, Allokation).")
        if not bullets:
            bullets.append("🔹 Lage ist ausgeglichen – behalte dein Budget bei und spare automatisiert.")

        for b in bullets:
            st.write(b)

        # Chart (optional wenn Altair vorhanden)
        if _HAS_ALTAIR:
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
                st.warning(f"Chart konnte nicht erzeugt werden: {e}")
        else:
            st.info("Hinweis: Altair nicht installiert – Chart wird nicht angezeigt. Installiere mit `pip install altair`.")

    st.divider()
    if plan_release:
        st.success("Freigabe aktiv (MVP‑Simulation). Verifizierte Finanzplaner:innen können diesen Plan read‑only einsehen.")
    else:
        st.info("Freigabe ist aus. Der Plan bleibt privat (anonym).")

# -------- Tab: Für Finanzplaner:innen --------
with tabs[2]:
    st.subheader("🧑‍💼 Finanzplaner:innen")
    st.write("Das Berater‑Modul (Chat) läuft als stabiles, separates Modul v0.2.7 mit Payment‑Gate und Zufriedenheits‑Freigabe.")
    st.write(" ")
    if st.button("➡️  Chat‑Modul öffnen (v0.2.7)"):
        st.success("Das Chat‑Modul läuft separat. Öffne es über deinen Shortcut/Launcher. (Bei Bedarf findest du die Startanleitung in der Dokumentation.)")
    st.caption("Grund: Stabilität und saubere Trennung der Verantwortlichkeiten im MVP.")

# -------- Tab: Moderation & Regeln --------
with tabs[3]:
    st.subheader("Moderation, Datenschutz & Regeln")
    st.markdown(\"\"\"
**Datenschutz & Anonymität**  
- Du bleibst anonym. Bitte keine Klarnamen, Adressen oder Kontonummern.  
- Daten werden nur zur Bereitstellung genutzt und nicht an Dritte weitergegeben.  

**Haftungsausschluss**  
- Antworten sind unverbindliche Einschätzungen und ersetzen keine individuelle, rechtsverbindliche Beratung.  
- Entscheidungen triffst du eigenverantwortlich.  

**Verhaltensregeln**  
- Kein Spam, keine Beleidigungen, keine rechtswidrigen Inhalte.  
- Keine sensiblen Personendaten posten.  

**Freigabe deines Finanzplans (optional)**  
- Du kannst deinen Finanzplan für verifizierte Finanzplaner:innen freigeben (anonym, widerrufbar).  
- Nutzung ausschliesslich für Beratungszwecke; keine Weitergabe an Dritte.  

**Bezahltes Micro‑Advice (CHF 15)**  
- Zahlung upfront. Freigabe erst bei Zufriedenheit (No‑Risk).  
- Bei Unzufriedenheit Nachbesserung; erst bei Freigabe ist das Ticket abgeschlossen.  

**Notfall‑Hinweis**  
- Dieser Chat ist kein Notfall‑ oder Krisendienst. Wende dich im Notfall an die zuständigen Stellen.  
\"\"\")
