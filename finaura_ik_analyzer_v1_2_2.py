# FINAURA IK Analyzer — v1.2.2 (2025-10-18, Europe/Zurich)
# CHANGE: Fix — `from __future__ import annotations` ganz oben platziert (Python-Anforderung).
# Ablagepfad: ~/Downloads/finaura_app  (verknüpft mit  ~/Documents/Finaura/app)
# Install:    pip install streamlit altair pandas pdfplumber pypdf
# Run:        streamlit run finaura_ik_analyzer_v1_2_2.py
#
# Hinweis: Der Ordner ~/Downloads/finaura_app ist ein Symlink auf ~/Documents/Finaura/app.
#          Dateien, die du dort ablegst/ersetzt, liegen automatisch im echten Projektordner.
from __future__ import annotations

__version__ = "1.2.2"

import io
import re
import typing as t
from dataclasses import dataclass, field

import streamlit as st
import pandas as pd
import altair as alt

# ---------- Styles (Weiß/Blau) ----------
PRIMARY = "#1e88e5"
ACCENT = "#e3f2fd"
st.markdown(
    f"""
    <style>
      .stApp {{
        background: white;
      }}
      .block-container {{
        padding-top: 1.8rem;
      }}
      h1, h2, h3 {{ color: {PRIMARY}; }}
      .finaura-note {{
        background: {ACCENT};
        border: 1px solid #bbdefb;
        padding: .75rem 1rem;
        border-radius: .75rem;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Text-Extraktion ----------
def _extract_text_with_pdfplumber(file_bytes: bytes) -> str:
    try:
        import pdfplumber  # type: ignore
    except Exception:
        return ""
    text_chunks = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            try:
                text_chunks.append(page.extract_text() or "")
            except Exception:
                continue
    return "\n".join(text_chunks).strip()

def _extract_text_with_pypdf(file_bytes: bytes) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        return ""
    text_chunks = []
    reader = PdfReader(io.BytesIO(file_bytes))
    for page in reader.pages:
        try:
            text_chunks.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(text_chunks).strip()

def extract_text(file_bytes: bytes) -> str:
    txt = _extract_text_with_pdfplumber(file_bytes)
    if len(txt) >= 30:
        return txt
    return _extract_text_with_pypdf(file_bytes)

# ---------- Erkennung ----------
YEAR_PATTERNS = [r"(?P<year>19\d{2}|20\d{2})"]
AMOUNT_PATTERNS = [
    r"(?P<amount>[0-9]{1,3}(?:[’'\\s_.,][0-9]{3})*[.,-]?[0-9]{0,2})",
    r"(?P<amount>[0-9]{4,})",
]
LINES_HINT = r"(Einkommen|AHV|ALV|Beitrag|Jahr|Summe|Total|Erwerbseinkommen)"
COMBINED = re.compile(
    rf"(?P<year>19\d{{2}}|20\d{{2}})\D{{0,20}}(?P<amount>[0-9]{{1,3}}(?:[’'\\s_.,][0-9]{{3}})*[.,-]?[0-9]{{0,2}})",
    re.IGNORECASE,
)

def _clean_amount(raw: str) -> t.Optional[float]:
    if not raw:
        return None
    s = raw.strip()
    s = s.replace("CHF", "").replace(".–", "").replace(".-", "").replace("’", "'")
    s = s.replace(" ", "").replace("_", "").replace("\u00a0", "")
    if "," in s and "." not in s:
        s = s.replace(",", ".")
    s = s.rstrip(".,-")
    try:
        return float(s)
    except Exception:
        import re as _re
        try:
            return float(int(_re.sub(r"\\D", "", s)))
        except Exception:
            return None

@dataclass
class ParseResult:
    file_name: str
    ok: bool
    years_found: int = 0
    items: t.List[t.Tuple[int, float]] = field(default_factory=list)
    msg: str = ""
    sample_text: str = ""

def parse_ik_text(file_name: str, text: str) -> ParseResult:
    res = ParseResult(file_name=file_name, ok=False, sample_text=(text or "")[:4000])
    if not text or len(text) < 10:
        res.msg = "Kein Text extrahierbar (evtl. Scan ohne OCR) — bitte PDF mit Text (kein Bild) verwenden."
        return res

    candidates: t.List[t.Tuple[int, float]] = []

    for m in COMBINED.finditer(text):
        y, a = m.group("year"), m.group("amount")
        year = int(y)
        amount = _clean_amount(a)
        if amount is not None and 1900 <= year <= 2100:
            candidates.append((year, amount))

    if not candidates:
        for line in text.splitlines():
            if re.search(LINES_HINT, line, flags=re.IGNORECASE):
                y_m = None
                for ypat in YEAR_PATTERNS:
                    y_m = re.search(ypat, line)
                    if y_m: break
                a_m = None
                for apat in AMOUNT_PATTERNS:
                    a_m = re.search(apat, line)
                    if a_m: break
                if y_m and a_m:
                    year = int(y_m.group("year"))
                    amount = _clean_amount(a_m.group("amount"))
                    if amount is not None and 1900 <= year <= 2100:
                        candidates.append((year, amount))

    if not candidates:
        res.msg = (
            "Keine Jahreswerte erkannt. Möglichkeiten:\n"
            "• PDF ist gescannt → zuerst OCR anwenden (z. B. Vorschau: Text markieren testweise)\n"
            "• Ungewohntes Layout → Debug aktivieren und mir den Textauszug schicken\n"
            "• Beträge als Spalten ohne CHF/.- → ich passe Regex für dein Layout an"
        )
        return res

    df = pd.DataFrame(candidates, columns=["Jahr", "Einkommen"])
    agg = df.groupby("Jahr", as_index=False)["Einkommen"].sum()
    res.items = list(agg.itertuples(index=False, name=None))
    res.years_found = len(agg)
    res.ok = True
    res.msg = f"{res.years_found} Jahr(e) erkannt."
    return res

# ---------- UI ----------
st.set_page_config(page_title=f"FINAURA IK Analyzer v{__version__}", layout="wide")
st.sidebar.markdown(f"**FINAURA** — IK Analyzer v{__version__}")
st.sidebar.caption("Ablage: `~/Downloads/finaura_app` → Projekt: `~/Documents/Finaura/app`")

st.title("FINAURA IK Analyzer")
st.markdown('<div class="finaura-note">IK-PDFs derselben Person hochladen → Jahreswerte werden erkannt und aggregiert.</div>', unsafe_allow_html=True)

left, right = st.columns([1, 1])
with left:
    st.subheader("📨 Upload (mehrere PDFs)")
    files = st.file_uploader("IK-Auszüge als PDF (Mehrfachauswahl möglich)", type=["pdf"], accept_multiple_files=True)
    debug = st.toggle("Debug-Modus (zeigt Textauszug & Treffer)", value=False)
    st.caption("Tipp: Scans ohne sichtbaren Text (OCR) liefern keinen Inhalt.")

results: t.List[ParseResult] = []
all_items: t.List[t.Tuple[int, float, str]] = []

if files:
    for f in files:
        text = extract_text(f.read())
        res = parse_ik_text(f.name, text)
        results.append(res)
        if res.ok:
            for year, amount in res.items:
                all_items.append((year, amount, f.name))

with right:
    st.subheader("🔎 Analyse & Aggregation")
    if not files:
        st.info("Bitte IK-PDF(s) links hochladen.")
    else:
        for res in results:
            if res.ok:
                st.success(f"✅ {res.file_name}: {res.msg}")
                if debug:
                    st.code(res.sample_text or "(kein Textauszug)", language=None)
            else:
                st.error(f"❌ {res.file_name}: {res.msg}")
                if debug:
                    st.code(res.sample_text or "(Kein Text extrahiert)", language=None)

        if all_items:
            df = pd.DataFrame(all_items, columns=["Jahr", "Einkommen", "Quelle"])
            df_agg = df.groupby("Jahr", as_index=False)["Einkommen"].sum().sort_values("Jahr")
            st.markdown("**Erkannte Jahreswerte (aggregiert):**")
            st.dataframe(df_agg, use_container_width=True)

            chart = (
                alt.Chart(df_agg)
                .mark_bar()
                .encode(x="Jahr:O", y="Einkommen:Q", tooltip=["Jahr", "Einkommen"])
                .properties(height=320)
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("Noch keine Werte aggregiert. Falls du PDFs hochgeladen hast und hier nichts erscheint, aktiviere den **Debug-Modus** und sende mir den Textauszug – ich passe die Regex auf dein Layout an.")
