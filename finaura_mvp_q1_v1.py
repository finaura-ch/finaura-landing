# coding: utf-8
"""
FINAURA – MVP Q1 (Micro · Finanzplan · Premium‑Chat · Legal)
Version: 0.1.0
Run: streamlit run finaura_mvp_q1_v1.py
"""
__version__ = "0.1.0"

import streamlit as st
import pandas as pd

# Altair optional (charts)
try:
    import altair as alt
    HAS_ALTAIR = True
except Exception:
    HAS_ALTAIR = False

# ---------- Page ----------
st.set_page_config(page_title="FINAURA – MVP Q1", page_icon="🧭", layout="wide")

# Brand (UI‑B: clean + slight emotion)
with st.sidebar:
    st.markdown("### 🧭 FINAURA")
    st.caption("Swiss Precision · Neutral · Anonym")
    st.write("**Version:** " + __version__)
    st.divider()
    st.markdown("**Heute im MVP:**")
    st.write("• Micro‑Impuls (CHF 15)")
    st.write("• Finanzplan (MVP)")
    st.write("• Premium‑Chat (Basic)")
    st.write("• Legal & Onboarding")

st.title("🧭 FINAURA – MVP Q1")
tabs = st.tabs(["Für Kund:innen", "Finanzplan", "Premium‑Chat", "Onboarding & Legal"])

# ---------- Helpers ----------
def chf(x: float) -> str:
    try:
        return "CHF {:,.0f}".format(float(x)).replace(",", "'")
    except Exception:
        return "CHF —"

# ---------- Tab: Micro‑Impuls (Customer Landing) ----------
with tabs[0]:
    st.subheader("💬 Micro‑Impuls – Sofort Orientierung (CHF 15)")
    st.write("Eine Frage. Eine klare, produktneutrale Antwort – anonym, schriftlich, nachvollziehbar.")
    st.info("Hinweis: FIN AURA verkauft keine Produkte und ersetzt keine persönliche Beratung.")

    # Anonyme Frage
    q = st.text_area("Deine Frage (anonym, keine Klarnamen, keine Kontonummern)", placeholder="z. B. Reicht meine Sparquote? Soll ich 3a priorisieren? Wie setze ich ein Budget?")

    # Simulierter Bezahl‑Flow (MVP): Auswahl + Button + Quittung
    st.markdown("#### Zahlung (MVP‑Simulation)")
    pay_method = st.selectbox("Methode", ["Kreditkarte (Sim)", "TWINT (Sim)", "Rechnung (Sim)"])
    agree = st.checkbox("Ich bestätige Anonymität, produktfreie Einschätzung und AGB‑Light.")
    paid = st.button("CHF 15 bezahlen & Anfrage senden", disabled=not (q and agree))

    if "micro_tickets" not in st.session_state:
        st.session_state.micro_tickets = []

    if paid:
        ticket = {"frage": q, "status": "eingegangen"}
        st.session_state.micro_tickets.append(ticket)
        st.success("Danke! Dein Micro‑Ticket wurde anonym eingereicht. Du erhältst eine schriftliche Antwort im Tool (MVP) innerhalb von 24–72h.")
        st.caption("MVP‑Hinweis: Zahlung ist simuliert. In der Pro‑Version wird ein echtes Gateway angebunden.")

    # Liste eigener Tickets (anonym, nur lokal sichtbar)
    if st.session_state.micro_tickets:
        st.markdown("#### Deine Tickets (MVP‑Demo)")
        for i, t in enumerate(st.session_state.micro_tickets, start=1):
            st.write(f"{i}. Status: **{t['status']}** – Frage: {t['frage'][:120]}{'…' if len(t['frage'])>120 else ''}")

# ---------- Tab: Finanzplan (MVP) ----------
with tabs[1]:
    st.subheader("📊 Finanzplan – MVP")
    st.caption("Zwei‑Spalten‑Layout: Links Eingaben, rechts Auswertung & (optional) Chart.")

    colL, colR = st.columns([1,1], gap="large")
    with colL:
        st.markdown("#### Eingaben")
        income = st.number_input("Monatliches Netto‑Einkommen (CHF)", min_value=0, step=100, value=7500)
        fixed = st.number_input("Fixkosten/Monat (CHF)", min_value=0, step=50, value=3200, help="Miete, Krankenkasse, ÖV, Versicherungen, Abos …")
        living = st.number_input("Lebenshaltung/Variabel (CHF)", min_value=0, step=50, value=2500, help="Lebensmittel, Freizeit, Sonstiges")
        reserve = st.number_input("Liquiditäts‑Reserve (CHF)", min_value=0, step=100, value=6000, help="Cash / Tagesgeld – Notgroschen")
        months_reserve_target = st.slider("Ziel Notgroschen (Monatslöhne)", 0, 12, 3)

        st.markdown("**Vorsorge (optional, grob):**")
        bvg = st.number_input("BVG‑Guthaben (CHF)", min_value=0, step=500, value=0)
        _3a = st.number_input("Säule 3a (CHF)", min_value=0, step=500, value=0)

        st.markdown("---")
        show_projection = st.checkbox("12‑Monats‑Projektion anzeigen", value=True)
        plan_release = st.toggle("🔓 Finanzplan freigeben (read‑only, MVP)", value=False,
                                 help="Ermöglicht verifizierten Finanzplaner:innen Einsicht (anonym, MVP‑Simulation).")

    with colR:
        st.markdown("#### Auswertung")
        total_expenses = fixed + living
        savings = max(income - total_expenses, 0)
        savings_rate = (savings / income * 100) if income > 0 else 0.0
        k1, k2, k3 = st.columns(3)
        k1.metric("Sparquote", f"{savings_rate:.1f} %")
        k2.metric("Freies Budget/Monat", chf(savings))
        k3.metric("Fixkosten‑Quote", f"{(fixed / income * 100):.1f} %" if income>0 else "—")

        months_reserve_have = (reserve / income) if income>0 else 0
        need_reserve_chf = max(0, (months_reserve_target - months_reserve_have) * income) if income>0 else 0

        st.markdown("### Handlungsempfehlung (neutral, kurz)")
        recs = []
        if months_reserve_have < months_reserve_target and need_reserve_chf > 0:
            recs.append(f"Notgroschen auf **{months_reserve_target} Monatslöhne** erhöhen (ca. {chf(need_reserve_chf)} fehlen).")
        if savings_rate < 10:
            recs.append("Sparquote < 10 %: Fixkosten & Abos prüfen, Budget‑Obergrenzen setzen.")
        elif savings_rate < 20:
            recs.append("Sparquote 10–20 %: solide. Nächster Schritt: regelmässige 3a‑Einzahlung prüfen (kosten/Allokation).")
        else:
            recs.append("Sparquote ≥ 20 %: sehr gut. Reserve stabilisieren und Investitionsplan definieren (neutral, produktfrei).")
        if bvg + _3a > 0:
            recs.append("Vorsorge vorhanden: 3a‑Strategie & Kostenstruktur prüfen (neutral, keine Produktempfehlung).")
        if not recs:
            recs.append("Lage ausgeglichen – Budget beibehalten und automatisiert sparen.")

        for r in recs:
            st.write("• " + r)

        if HAS_ALTAIR and show_projection:
            try:
                months = list(range(1,13))
                df = pd.DataFrame({
                    "Monat": months,
                    "Einkommen": [income]*12,
                    "Ausgaben": [total_expenses]*12,
                    "Sparen": [savings]*12
                })
                df["Kumulierte Ersparnis"] = df["Sparen"].cumsum()
                base = alt.Chart(df).encode(x=alt.X("Monat:O", title="Monat"))
                bars = base.mark_bar().encode(y=alt.Y("Einkommen:Q", title="CHF"),
                                              tooltip=["Monat","Einkommen","Ausgaben","Sparen"])
                bars2 = base.mark_bar(opacity=0.65).encode(y="Ausgaben:Q")
                line = base.mark_line(point=True).encode(y=alt.Y("Kumulierte Ersparnis:Q", title="CHF"))
                st.markdown("#### Einnahmen/Ausgaben & kumulative Ersparnis (12M)")
                st.altair_chart((bars + bars2 + line).resolve_scale(y="independent"), use_container_width=True)
            except Exception as e:
                st.warning(f"Chart konnte nicht erzeugt werden: {e}")
        elif show_projection and not HAS_ALTAIR:
            st.info("Altair nicht installiert – Chart optional mit `pip install altair`.")

    st.divider()
    if plan_release:
        st.success("Freigabe aktiv (MVP‑Simulation). Verifizierte Finanzplaner:innen können diesen Plan read‑only einsehen.")
    else:
        st.info("Freigabe ist aus. Der Plan bleibt privat (anonym).")

# ---------- Tab: Premium‑Chat (Basic) ----------
with tabs[2]:
    st.subheader("🧑‍💼 Premium‑Chat (Basic) – Begleitete Entscheidungen, produktfrei")
    st.caption("Kein Produktverkauf. Klare Handlungsschritte. 24–72h Antwortzeit (MVP‑Simulation).")

    if "chat" not in st.session_state:
        st.session_state.chat = []  # list of dicts: {"role": "user"/"planner", "text": str}

    # Input
    user_msg = st.text_input("Deine Nachricht (anonym):", placeholder="Beschreibe dein Thema in 1–2 Sätzen.")
    submit = st.button("Senden")
    if submit and user_msg:
        st.session_state.chat.append({"role":"user", "text": user_msg})
        # MVP Planner‑Antwort (Fake): automatische generische Struktur, keine Produkte
        plan = []
        plan.append("1) Ziel & Zeithorizont definieren.")
        plan.append("2) Budget prüfen: Fix/Variabel begrenzen, Sparquote sichern.")
        plan.append("3) Reserve auffüllen: 3–6 Monatslöhne als Notgroschen.")
        plan.append("4) Nächster Schritt: eine konkrete Aktion in 7 Tagen festlegen.")
        st.session_state.chat.append({"role":"planner", "text": "Handlungsvorschlag:\n" + "\n".join(plan)})

    # Thread anzeigen
    if st.session_state.chat:
        st.markdown("#### Verlauf")
        for m in st.session_state.chat:
            if m["role"] == "user":
                st.write(f"**Du:** {m['text']}")
            else:
                st.write(f"**Planner:** {m['text']}")

    # Abschluss‑Summary erzeugen
    if st.session_state.chat:
        if st.button("🔖 Abschluss‑Summary (MVP) erzeugen"):
            # simple text export in session (MVP)
            summary = "Premium‑Chat Summary (MVP)\n\n"
            for m in st.session_state.chat:
                who = "Kunde" if m["role"]=="user" else "Planner"
                summary += f"{who}: {m['text']}\n"
            st.download_button("Summary herunterladen (TXT)", summary, file_name="finaura_premium_chat_summary.txt")
        st.caption("MVP‑Hinweis: In der Pro‑Version wird eine schöne PDF‑Zusammenfassung generiert.")

# ---------- Tab: Onboarding & Legal ----------
with tabs[3]:
    st.subheader("Onboarding & Legal")
    st.markdown("""
**So startest du (Kund:in):** Micro‑Impuls einreichen (CHF 15), Finanzplan ausfüllen, bei Bedarf Premium‑Chat aktivieren.  
**So startest du (Finanzplaner:in):** Zugang anfragen, produktneutral beraten, Qualität sichern (klare Handlungsschritte).
""")
    st.markdown("""
**Haftung:** FINAURA ist ein neutrales Analyse‑ und Klarheitstool und ersetzt keine persönliche Finanz‑, Vorsorge‑, Steuer‑ oder Anlageberatung. Entscheidungen liegen bei Nutzer:innen bzw. beratenden Fachpersonen.  
**Datenschutz:** Nutzung anonym, keine Klarnamen/Kontonummern erforderlich, keine Weitergabe an Dritte.  
**Compliance:** Keine Produktempfehlung, keine Vermittlung, keine Vertriebssignale. Banken‑/Versicherungsberater können freiwillig nutzen, sofern produktneutral beraten wird.
""")
