"""
FINAURA – Chat Anon
Version: 0.2.5
Date: 2025-10-19 (Europe/Zurich)
Change: Fix SyntaxError (remove backslashes in f-Strings/line continuations), implement Selectbox Variante B (#id – anon_id – status).

Install requirements:
    pip install streamlit altair pandas

Run the app:
    streamlit run finaura_chat_anon_v0_2_1.py

Storage path:
    ~/Downloads/finaura_app (symlink to ~/Documents/Finaura/app)
"""
__version__ = "0.2.5"

"""
FINAURA – Anonymer Berater-Chat (MVP)
Version: 0.2.0
Datum (Europe/Zurich): 2025-10-19
Change-Note: Neues Feature – Anonymer Chat zwischen Kunde und Finanzplaner inkl. Verifizierungs-Stubs, Ratings und Platin-Status-Logik (MVP Polling, SQLite).
Speicherpfad-Hinweis: ~/Downloads/finaura_app (symlink to ~/Documents/Finaura/app)

Installiere benötigte Pakete (einmalig):
    pip install streamlit altair pandas

Starte die App:
    streamlit run finaura_chat_anon_v0_2_0.py
"""


import streamlit as st
import sqlite3
from datetime import datetime, timezone
import time, os, hashlib, secrets, json
from typing import Optional

__version__ = "0.2.0"

DB_PATH = os.getenv("FINAURA_DB_PATH", "finaura_chat.db")

# ---------- Utilities ----------
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS planners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hashed_member TEXT UNIQUE,
            assoc TEXT,
            handle TEXT UNIQUE,
            score INTEGER DEFAULT 0,
            level TEXT DEFAULT 'Bronze',
            created_at TEXT,
            is_online INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anon_id TEXT UNIQUE,
            created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS threads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            planner_id INTEGER,
            status TEXT DEFAULT 'open', -- open, closed
            created_at TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (planner_id) REFERENCES planners(id)
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id INTEGER,
            sender TEXT, -- 'planner' | 'customer'
            content TEXT,
            ts TEXT,
            FOREIGN KEY (thread_id) REFERENCES threads(id)
        );
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id INTEGER UNIQUE,
            score INTEGER, -- 1..5
            feedback TEXT,
            created_at TEXT,
            FOREIGN KEY (thread_id) REFERENCES threads(id)
        );
        """
    )
    conn.commit()
    conn.close()

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def salted_hash(member_id: str, assoc: str) -> str:
    # Stable salted hash (do not reveal salt). For MVP a static salt; in prod use per-user salt stored server-side.
    salt = "finaura_static_salt_v1"
    return hashlib.sha256((salt + assoc.lower().strip() + ":" + member_id.strip()).encode()).hexdigest()

def level_from_score(score: int) -> str:
    if score >= 200: return "Platin"
    if score >= 120: return "Gold"
    if score >= 60:  return "Silber"
    return "Bronze"

def score_delta_for_rating(r: int) -> int:
    return {1:-10, 2:-5, 3:0, 4:5, 5:10}.get(r, 0)

def upsert_planner(conn, hashed_member: str, assoc: str, desired_handle: str) -> Optional[str]:
    cur = conn.cursor()
    # Ensure unique handle; if taken, append random 3 chars
    handle = desired_handle.strip()
    try:
        cur.execute("INSERT INTO planners(hashed_member, assoc, handle, created_at) VALUES (?,?,?,?)",
                    (hashed_member, assoc, handle, now_iso()))
        conn.commit()
        return handle
    except sqlite3.IntegrityError:
        # handle taken; try suffix
        for _ in range(5):
            candidate = f"{handle}_{secrets.token_hex(2)}"
            try:
                cur.execute("INSERT INTO planners(hashed_member, assoc, handle, created_at) VALUES (?,?,?,?)",
                            (hashed_member, assoc, candidate, now_iso()))
                conn.commit()
                return candidate
            except sqlite3.IntegrityError:
                continue
        return None

def get_planner_by_hash(conn, hashed_member: str):
    cur = conn.cursor()
    cur.execute("SELECT * FROM planners WHERE hashed_member=?", (hashed_member,))
    return cur.fetchone()

def set_planner_online(conn, planner_id: int, online: bool):
    cur = conn.cursor()
    cur.execute("UPDATE planners SET is_online=? WHERE id=?", (1 if online else 0, planner_id))
    conn.commit()

def list_online_planners(conn):
    cur = conn.cursor()
    cur.execute("SELECT id, handle, level, score FROM planners WHERE is_online=1 ORDER BY score DESC, handle ASC")
    return cur.fetchall()

def ensure_customer(conn, anon_id: str):
    cur = conn.cursor()
    cur.execute("SELECT id FROM customers WHERE anon_id=?", (anon_id,))
    row = cur.fetchone()
    if row: return row["id"]
    cur.execute("INSERT INTO customers(anon_id, created_at) VALUES (?,?)", (anon_id, now_iso()))
    conn.commit()
    return cur.lastrowid

def create_thread(conn, customer_id: int, planner_id: int):
    cur = conn.cursor()
    cur.execute("INSERT INTO threads(customer_id, planner_id, status, created_at) VALUES (?,?, 'open', ?)",
                (customer_id, planner_id, now_iso()))
    conn.commit()
    return cur.lastrowid

def get_user_threads(conn, role: str, user_id: int):
    cur = conn.cursor()
    if role == "planner":
        cur.execute("""
            SELECT t.id, t.status, c.anon_id, p.handle
            FROM threads t
            JOIN customers c ON t.customer_id=c.id
            JOIN planners p ON t.planner_id=p.id
            WHERE p.id=?
            ORDER BY t.id DESC
        """, (user_id,))
    else:
        cur.execute("""
            SELECT t.id, t.status, p.handle, c.anon_id
            FROM threads t
            JOIN customers c ON t.customer_id=c.id
            JOIN planners p ON t.planner_id=p.id
            WHERE c.id=?
            ORDER BY t.id DESC
        """, (user_id,))
    return cur.fetchall()

def add_message(conn, thread_id: int, sender: str, content: str):
    cur = conn.cursor()
    cur.execute("INSERT INTO messages(thread_id, sender, content, ts) VALUES (?,?,?,?)",
                (thread_id, sender, content, now_iso()))
    conn.commit()

def get_messages(conn, thread_id: int):
    cur = conn.cursor()
    cur.execute("SELECT sender, content, ts FROM messages WHERE thread_id=? ORDER BY id ASC", (thread_id,))
    return cur.fetchall()

def rate_thread(conn, thread_id: int, rating: int, feedback: str):
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO ratings(thread_id, score, feedback, created_at) VALUES (?,?,?,?)",
                    (thread_id, rating, feedback, now_iso()))
        conn.commit()
        # update planner score & level
        cur.execute("SELECT planner_id FROM threads WHERE id=?", (thread_id,))
        row = cur.fetchone()
        if row:
            planner_id = row["planner_id"]
            delta = score_delta_for_rating(rating)
            cur.execute("UPDATE planners SET score = score + ? WHERE id=?", (delta, planner_id))
            cur.execute("UPDATE planners SET level = ? WHERE id=?", (level_from_score(get_planner_score(conn, planner_id)), planner_id))
            conn.commit()
    except sqlite3.IntegrityError:
        pass

def get_planner_score(conn, planner_id: int) -> int:
    cur = conn.cursor()
    cur.execute("SELECT score FROM planners WHERE id=?", (planner_id,))
    r = cur.fetchone()
    return r["score"] if r else 0

# ---------- UI ----------
st.set_page_config(page_title="FINAURA – Anonymer Berater-Chat", page_icon="💬", layout="wide")
init_db()

with st.sidebar:
    st.markdown("### FINAURA")
    st.caption(f"Anonymer Berater-Chat • Version {__version__}")
    st.markdown("---")
    st.markdown("**Hinweis zur Anonymität**")
    st.write("• Berater bleiben anonym (Handle).")
    st.write("• Keine Klarnamen notwendig. Jahrgang optional.")
    st.write("• Inhalte werden protokolliert, aber pseudonymisiert.")
    st.markdown("---")
    st.markdown("**Platin-Status**")
    st.write("Bronze < Silber < Gold < Platin – basierend auf Bewertungen.")

st.title("💬 Anonymer Berater-Chat (MVP)")
role = st.tabs(["Für Kund:innen", "Für Finanzplaner:innen", "Moderation & Regeln"])

# ---- Kunden-Tab ----
with role[0]:
    st.subheader("Kund:innen")
    st.write("Stelle deine Frage anonym und erhalte Micro‑Advice von verifizierten Finanzplaner:innen.")
    anon_seed = st.text_input("Dein anonymer Bezeichner (frei wählbar, z. B. 'ZRH1990')", value="")
    colK1, colK2 = st.columns([1,1])
    with colK1:
        if st.button("🎭 Anmelden (anonym)"):
            if not anon_seed.strip():
                st.error("Bitte wähle einen anonymen Bezeichner.")
            else:
                conn = get_db()
                cid = ensure_customer(conn, anon_seed.strip())
                st.session_state["customer_id"] = cid
                st.success("Anmeldung erfolgt.")
    with colK2:
        if st.button("🚪 Abmelden"):
            st.session_state.pop("customer_id", None)
            st.experimental_rerun()

    if "customer_id" in st.session_state:
        conn = get_db()
        st.markdown("#### Verfügbare Berater:innen (online)")
        planners = list_online_planners(conn)
        if not planners:
            st.info("Derzeit ist niemand online. Du kannst dennoch eine Unterhaltung starten; sie wird beantwortet, sobald jemand online ist.")
        for p in planners:
            st.write(f"• **{p['handle']}** – Level: {p['level']} | Score: {p['score']}")

        st.markdown("#### Neue Unterhaltung starten")
        planner_handle = st.text_input("Handle der gewünschten Person (optional – leer lassen für Auto-Zuweisung)")
        if st.button("➕ Thread erstellen"):
            cur = conn.cursor()
            # Auto-assign highest score online if no handle chosen
            if not planner_handle.strip():
                cur.execute("SELECT id FROM planners WHERE is_online=1 ORDER BY score DESC LIMIT 1")
            else:
                cur.execute("SELECT id FROM planners WHERE handle=?", (planner_handle.strip(),))
            row = cur.fetchone()
            if not row:
                # fallback: any planner by highest score
                cur.execute("SELECT id FROM planners ORDER BY score DESC LIMIT 1")
                row = cur.fetchone()
            if not row:
                st.error("Noch keine Berater:innen registriert.")
            else:
                thread_id = create_thread(conn, st.session_state["customer_id"], row["id"])
                st.session_state["thread_id"] = thread_id
                st.success(f"Thread #{thread_id} erstellt.")
        # Existing threads
        st.markdown("#### Deine Unterhaltungen")
        threads = get_user_threads(conn, "customer", st.session_state["customer_id"])
        if threads:
            # Format: #<id> – <anon/handle> – <status>
            def _fmt_thread_option(t: dict) -> str:
                who = t.get('anon_id') or t.get('handle') or '—'
                status = t.get('status') or ''
                return f"#{t.get('id')} – {who} – {status}"
            options = [_fmt_thread_option(t) for t in threads]
            selection = st.selectbox("Wähle eine Unterhaltung", options, key="customer_threads")
            sel_id = _extract_ticket_id(selection)
            st.session_state["thread_id"] = sel_id
        else:
            st.info("Noch keine Unterhaltungen.")
        if "thread_id" in st.session_state:
            st.markdown(f"### Unterhaltung #{st.session_state['thread_id']}")
            messages = get_messages(conn, st.session_state["thread_id"])
            for m in messages:
                who = "👤 Kunde" if m["sender"] == "customer" else "🧑‍💼 Berater"
                st.markdown(f"**{who}:** {m['content']}  \n<sub>{m['ts']}</sub>")
            st.divider()
            msg = st.chat_input("Deine Nachricht…")
            if msg:
                add_message(conn, st.session_state["thread_id"], "customer", msg)
                st.experimental_rerun()
            st.markdown("##### Bewertung")
            rating = st.slider("Bewerte diese Beratung", 1, 5, 5)
            fb = st.text_input("Optionales Feedback")
            if st.button("⭐ Bewertung absenden"):
                rate_thread(conn, st.session_state["thread_id"], rating, fb)
                st.success("Danke für deine Bewertung!")

# ---- Planner-Tab ----
with role[1]:
    st.subheader("Finanzplaner:innen")
    st.write("Anonym bleiben, verifiziert beraten und Platin‑Status aufbauen.")

    with st.expander("Verifizierung (MVP-Stub)"):
        st.caption("MVP: Trage Verband & Mitgliedsnummer ein. In Produktion wird dies über eine API des Verbandes geprüft.")
        assoc = st.text_input("Verband (z. B. 'FPSB', 'SFAA')")
        member_no = st.text_input("Mitgliedsnummer")
        desired_handle = st.text_input("Wunsch‑Handle (sichtbar im Chat, anonym)")
        colV1, colV2 = st.columns([1,1])
        if colV1.button("✅ Verifizieren & registrieren"):
            if not assoc.strip() or not member_no.strip() or not desired_handle.strip():
                st.error("Bitte alle Felder ausfüllen.")
            else:
                conn = get_db()
                h = salted_hash(member_no, assoc)
                existing = get_planner_by_hash(conn, h)
                if existing:
                    st.info(f"Bereits registriert als **{existing['handle']}**. Du kannst dich unten anmelden.")
                else:
                    handle = upsert_planner(conn, h, assoc.strip(), desired_handle.strip())
                    if handle:
                        st.success(f"Registrierung erfolgreich. Dein anonymes Handle: **{handle}**")
                    else:
                        st.error("Handle konnte nicht erstellt werden. Versuche einen anderen Namen.")
        if colV2.button("🗑️ Abmelden / Offline gehen"):
            st.session_state.pop("planner_id", None)

    st.markdown("---")
    st.markdown("#### Anmeldung")
    login_assoc = st.text_input("Verband (wie registriert)", key="login_assoc")
    login_member = st.text_input("Mitgliedsnummer (wie registriert)", key="login_member")
    colL1, colL2 = st.columns([1,1])
    if colL1.button("🔐 Anmelden als Berater:in"):
        if not login_assoc.strip() or not login_member.strip():
            st.error("Bitte Verband und Mitgliedsnummer angeben.")
        else:
            conn = get_db()
            h = salted_hash(login_member, login_assoc)
            row = get_planner_by_hash(conn, h)
            if row:
                st.session_state["planner_id"] = row["id"]
                set_planner_online(conn, row["id"], True)
                st.success(f"Angemeldet als **{row['handle']}** (Level {row['level']}, Score {row['score']}).")
            else:
                st.error("Nicht gefunden. Bitte zuerst registrieren.")
    if colL2.button("🚪 Abmelden (offline)"):
        if "planner_id" in st.session_state:
            conn = get_db()
            set_planner_online(conn, st.session_state["planner_id"], False)
            st.session_state.pop("planner_id", None)
            st.success("Abgemeldet.")

    if "planner_id" in st.session_state:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT handle, level, score FROM planners WHERE id=?", (st.session_state["planner_id"],))
        me = cur.fetchone()
        st.info(f"Angemeldet als **{me['handle']}** – Level {me['level']} | Score {me['score']}")
        st.markdown("#### Deine Unterhaltungen")
        threads = get_user_threads(conn, "planner", st.session_state["planner_id"])
        if threads:
            options = [_fmt_ticket_option(t) for t in threads]
            selection = st.selectbox("Wähle eine Unterhaltung", options, key="planner_threads")
            p_sel_id = _extract_ticket_id(selection)
            st.session_state["p_thread_id"] = p_sel_id
        else:
            st.info("Noch keine Unterhaltungen. Warte auf neue Anfragen.")

        if "p_thread_id" in st.session_state:
            st.markdown(f"### Unterhaltung #{st.session_state['p_thread_id']}")
            messages = get_messages(conn, st.session_state["p_thread_id"])
            for m in messages:
                who = "🧑‍💼 Ich" if m["sender"] == "planner" else "👤 Kunde"
                st.markdown(f"**{who}:** {m['content']}  \n<sub>{m['ts']}</sub>")
            st.divider()
            msg = st.chat_input("Deine Antwort…")
            if msg:
                add_message(conn, st.session_state["p_thread_id"], "planner", msg)
                st.experimental_rerun()

# ---- Moderation ----
with role[2]:
    st.subheader("Moderation & Regeln (MVP)")
    st.write("• Keine Klarnamen, keine personenbezogenen Daten.  ")
    st.write("• Keine rechtsverbindliche Beratung; nur Orientierung (Haftungs‑Disclaimer).  ")
    st.write("• Netiquette: respektvoll, keine Werbung, keine Links zu personenbezogenen Profilen.  ")
    st.write("• Verdachtsfälle von Missbrauch bitte melden: moderation@finaura.local (Dummy).")
    st.info("Hinweis: Für Produktivbetrieb sind DSG/DSGVO‑Konformität, Logging, Audit‑Trail, Missbrauchserkennung (ML), sowie echte Verbands‑API‑Verifikation zu implementieren.")