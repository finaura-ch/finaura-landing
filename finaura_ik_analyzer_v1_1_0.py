from finaura_versioner import show_version_in_sidebar
show_version_in_sidebar(app_name="FINAURA IK Analyzer")
# =============================================================
# FINAURA IK Analyzer – v1.1.0
# Datum: 2025-10-18 08:01
# Change-Note: Heuristik verbessert (Jahr/Income/Beiträge), Multi-PDF stabil, 
#              Tabellenparser (pdfplumber) + Regex-Fallback, lokales Export-Verzeichnis
#
# Setup-Hinweise (bitte in Terminal ausführen):
#   pip install streamlit altair pandas pdfplumber pymupdf pytesseract pillow xlsxwriter
#   streamlit run finaura_ik_analyzer_v1_1_0.py
# =============================================================

__version__ = "1.1.0"

import io
import os
import re
import json
import zipfile
from typing import List, Dict, Tuple, Optional

import pandas as pd
import streamlit as st
import altair as alt

# Optionale Backends
_BACKENDS = {
    "pdfplumber": None,
    "fitz": None,  # PyMuPDF
    "pytesseract": None,
    "PIL": None,
}

def _lazy_imports():
    global _BACKENDS
    try:
        import pdfplumber  # type: ignore
        _BACKENDS["pdfplumber"] = pdfplumber
    except Exception:
        _BACKENDS["pdfplumber"] = None

    try:
        import fitz  # type: ignore
        _BACKENDS["fitz"] = fitz
    except Exception:
        _BACKENDS["fitz"] = None

    try:
        import pytesseract  # type: ignore
        _BACKENDS["pytesseract"] = pytesseract
    except Exception:
        _BACKENDS["pytesseract"] = None

    try:
        from PIL import Image  # type: ignore
        _BACKENDS["PIL"] = Image
    except Exception:
        _BACKENDS["PIL"] = None


# ----------------- Utilities & Patterns -----------------
YEAR_RE    = re.compile(r"\b(19\d{2}|20\d{2})\b")
AMT_RE     = re.compile(r"-?\d{1,3}(?:[\.'’]\d{3})*(?:[,\.]\d+)?")
AHV_RE     = re.compile(r"\b756[\.-]?\d{4}[\.-]?\d{4}[\.-]?\d{2}\b")
NAME_HINTS = re.compile(r"(?:Name|Versicherte.?r|Vorname|Nachname)\s*[:\-]\s*(.+)", re.IGNORECASE)
EINKOMMEN_HINTS = re.compile(r"(Einkommen|AHV-?Lohn|Brutto|massgebend(?:er)?\s+Lohn)", re.IGNORECASE)
TOTAL_HINTS     = re.compile(r"\bTotal\b|\bSumme\b|\bGesamt\b", re.IGNORECASE)
JAHR_HINTS      = re.compile(r"(Beitragsjahr|Jahr)", re.IGNORECASE)

def _norm_amount(s: str) -> Optional[float]:
    s = s.strip().replace(" ", "").replace("’", "'")
    s = re.sub(r"[\.'’]", "", s)   # entferne Tausender
    s = s.replace(",", ".")         # Komma zu Punkt
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return None
    try:
        return float(m.group(0))
    except Exception:
        return None

def _ocr_page_with_fitz(page, zoom: float = 2.0) -> Optional[str]:
    if _BACKENDS["pytesseract"] is None or _BACKENDS["PIL"] is None:
        return None
    try:
        mat = _BACKENDS["fitz"].Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        Image = _BACKENDS["PIL"]
        pytesseract = _BACKENDS["pytesseract"]
        img = Image.open(io.BytesIO(img_bytes))
        text = pytesseract.image_to_string(img) or ""
        return text.strip() or None
    except Exception:
        return None

def _extract_all_texts(file_bytes: bytes) -> Tuple[List[str], List[str]]:
    """Liefert eine Liste von Seitentexten + Warnings (mit OCR-Fallback)."""
    warnings: List[str] = []
    pages: List[str] = []

    pdfplumber = _BACKENDS["pdfplumber"]
    fitz_mod   = _BACKENDS["fitz"]
    plumber_pdf = None
    fitz_doc    = None
    total_pages = 0

    try:
        if pdfplumber is not None:
            plumber_pdf = pdfplumber.open(io.BytesIO(file_bytes))
            total_pages = max(total_pages, len(plumber_pdf.pages))
    except Exception as e:
        warnings.append(f"pdfplumber open: {e}")
        plumber_pdf = None

    try:
        if fitz_mod is not None:
            fitz_doc = fitz_mod.open(stream=file_bytes, filetype="pdf")
            total_pages = max(total_pages, len(fitz_doc))
    except Exception as e:
        warnings.append(f"fitz open: {e}")
        fitz_doc = None

    if total_pages == 0:
        warnings.append("Keine Seiten erkannt.")
        return [], warnings

    for i in range(1, total_pages+1):
        txt = ""
        if plumber_pdf is not None and i <= len(plumber_pdf.pages):
            try:
                txt = plumber_pdf.pages[i-1].extract_text() or ""
            except Exception as e:
                warnings.append(f"S{i} pdfplumber text: {e}")
            # Hinweis: Tabellenextraktion separat.
        if not txt and fitz_doc is not None:
            try:
                txt = fitz_doc[i-1].get_text("text") or ""
            except Exception as e:
                warnings.append(f"S{i} fitz text: {e}")
        if not txt and fitz_doc is not None:
            ocr_txt = _ocr_page_with_fitz(fitz_doc[i-1], 2.0)
            if ocr_txt:
                txt = ocr_txt
            else:
                warnings.append(f"S{i} kein Text (OCR nicht verfügbar).")
        pages.append(txt)

    if plumber_pdf is not None:
        try: plumber_pdf.close()
        except Exception: pass
    if fitz_doc is not None:
        try: fitz_doc.close()
        except Exception: pass

    return pages, warnings

def _extract_person_keys(text: str) -> Dict[str, Optional[str]]:
    ahv = None
    m = AHV_RE.search(text)
    if m:
        ahv = m.group(0).replace("-", ".")
    name = None
    for line in text.splitlines():
        nm = NAME_HINTS.search(line)
        if nm:
            name = nm.group(1).strip()
            break
    return {"ahv": ahv, "name": name}

def parse_tables_with_pdfplumber(file_bytes: bytes) -> List[Dict]:
    """Extrahiert Tabellenzeilen (Seite, Zeile, Werte) mit pdfplumber sofern möglich."""
    out = []
    if _BACKENDS["pdfplumber"] is None:
        return out
    try:
        pdfplumber = _BACKENDS["pdfplumber"]
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                try:
                    tables = page.extract_tables() or []
                    for t in tables:
                        for r in t:
                            out.append({"page": i, "values": [c if c is not None else "" for c in r]})
                except Exception:
                    continue
    except Exception:
        pass
    return out

def parse_year_income_from_lines(lines: List[str]) -> List[Tuple[int, float]]:
    """Heuristik: Zeilen mit Jahr + Betrag. Bevorzugt Zeilen, die auch 'Einkommen/AHV-Lohn' o.ä. enthalten."""
    records: List[Tuple[int,float]] = []
    for ln in lines:
        y = YEAR_RE.search(ln)
        if not y:
            continue
        amts = AMT_RE.findall(ln)
        amts = [a for a in amts if not YEAR_RE.fullmatch(a or "")]
        if not amts:
            continue
        vals = [v for v in (_norm_amount(a) for a in amts) if v is not None]
        if not vals:
            continue
        score = 1.0
        if EINKOMMEN_HINTS.search(ln):
            score += 1.0
        if JAHR_HINTS.search(ln):
            score += 0.3
        income = max(vals, key=abs) * score
        records.append((int(y.group(1)), float(income)))
    agg: Dict[int, float] = {}
    for y, inc in records:
        agg[y] = agg.get(y, 0.0) + inc
    return sorted([(y, v) for y, v in agg.items()], key=lambda x: x[0])

def parse_year_income_from_tables(tables: List[Dict]) -> List[Tuple[int, float]]:
    """Heuristik über Tabellen: suche Zeilen, in denen ein Jahr + Betrag vorkommt."""
    rows = tables
    candidates: List[Tuple[int, float]] = []
    for row in rows:
        vals = row.get("values", [])
        if not vals or all((v or "").strip()=="" for v in vals):
            continue
        y = None
        for v in vals:
            m = YEAR_RE.search(str(v))
            if m:
                y = int(m.group(1)); break
        if y is None:
            continue
        amounts = []
        for v in vals:
            for a in AMT_RE.findall(str(v)):
                if not YEAR_RE.fullmatch(a or ""):
                    val = _norm_amount(a)
                    if val is not None:
                        amounts.append(val)
        if not amounts:
            continue
        income = max(amounts, key=abs)
        candidates.append((y, float(income)))
    agg: Dict[int, float] = {}
    for y, inc in candidates:
        agg[y] = agg.get(y, 0.0) + inc
    return sorted([(y, v) for y, v in agg.items()], key=lambda x: x[0])

def aggregate_documents(file_objs: List[Tuple[str, bytes]]) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """Analysiert mehrere PDFs. Erkennt Person (AHV/Name), extrahiert Jahr/Einkommen, aggregiert."""
    warnings: List[str] = []
    rows = []

    for fname, fbytes in file_objs:
        page_texts, warns = _extract_all_texts(fbytes)
        warnings.extend([f"{fname}: " + w for w in warns])
        full_text = "\n".join(page_texts)

        keys = _extract_person_keys(full_text)
        person_key = keys.get("ahv") or (keys.get("name") or "Unbekannt")

        tables = parse_tables_with_pdfplumber(fbytes)
        yr_tbl = parse_year_income_from_tables(tables) if tables else []
        yr_txt = parse_year_income_from_lines(full_text.splitlines())

        combined: Dict[int, float] = {}
        for y, inc in yr_txt:
            combined[y] = combined.get(y, 0.0) + inc
        for y, inc in yr_tbl:
            combined[y] = combined.get(y, 0.0) + inc

        if not combined:
            warnings.append(f"{fname}: Keine Jahreswerte erkannt – Layout evtl. sehr speziell.")

        for y, inc in combined.items():
            rows.append({"person_key": person_key, "year": y, "income": float(inc), "source_file": fname})

    df_year = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["person_key","year","income","source_file"])
    if df_year.empty:
        df_total = pd.DataFrame(columns=["person_key","total_income"])
    else:
        df_total = df_year.groupby("person_key", as_index=False)["income"].sum().rename(columns={"income":"total_income"})
    return df_year, df_total, warnings

def export_excel(df_year: pd.DataFrame, df_total: pd.DataFrame, save_local: bool=True) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_year.sort_values(["person_key","year"]).to_excel(writer, index=False, sheet_name="ByYear")
        df_total.sort_values(["person_key"]).to_excel(writer, index=False, sheet_name="Totals")
    data = output.getvalue()

    if save_local:
        base_dir = os.path.expanduser("~/Documents/Finaura/Exports")
        try:
            os.makedirs(base_dir, exist_ok=True)
            fname = f"IK_aggregation_20251018_060130.xlsx"
            with open(os.path.join(base_dir, fname), "wb") as f:
                f.write(data)
        except Exception:
            pass
    return data


# ============================ Streamlit UI ============================

st.set_page_config(page_title="FINAURA IK Analyzer v1.1.0", page_icon="📈", layout="wide")

# Design
st.markdown(
    """
    <style>
    :root {
        --finaura-blue: #1f7ae0;
    }
    .stApp { background: #ffffff; }
    .finaura-title h1 { color: var(--finaura-blue); letter-spacing: 0.2px; }
    .muted { color:#6b7280; }
    </style>
    """, unsafe_allow_html=True
)

with st.sidebar:
    st.markdown("## ⚙️ Einstellungen")
    st.write(f"Version: **{__version__}**")
    st.caption("Mehrfach-Upload • Gruppierung nach Person • Jahres-Summen • lokaler Export")
    st.markdown("---")
    _lazy_imports()
    st.write({k: ("✅ verfügbar" if v is not None else "⚠️ fehlt") for k, v in _BACKENDS.items()})
    if _BACKENDS["pytesseract"] is None:
        st.info("Für gescannte PDFs bitte 'tesseract' + 'pytesseract' + 'Pillow' installieren.")
    st.markdown("---")
    st.markdown("**Hinweis:** Person wird über AHV-Nummer (756…) oder Namenszeilen erkannt.")

st.markdown('<div class="finaura-title">', unsafe_allow_html=True)
st.title("📈 FINAURA IK Analyzer")
st.markdown("</div>", unsafe_allow_html=True)
st.caption("Mehrere PDFs derselben Person hochladen → Jahre/Einkommen werden zusammengefasst und exportiert.")

left, right = st.columns([1,1])

with left:
    st.markdown("### 📤 Upload (mehrere PDFs)")
    uploads = st.file_uploader("IK-Auszüge als PDF (Mehrfachauswahl möglich)", type=["pdf"], accept_multiple_files=True)
    st.markdown("<div class='muted'>Tipp: Dateien der gleichen Person zusammen auswählen.</div>", unsafe_allow_html=True)

with right:
    st.markdown("### 🔍 Analyse & Aggregation")
    if not uploads:
        st.info("Bitte eine oder mehrere PDF-Dateien auswählen.")
    else:
        file_objs = [ (u.name, u.read()) for u in uploads ]
        with st.spinner("Analysiere Dokumente…"):
            df_year, df_total, warns = aggregate_documents(file_objs)

        for w in warns:
            st.warning(w)

        if df_year.empty:
            st.error("Keine Jahres-Einkommen erkannt. Bitte Beispiel-PDF teilen – wir schärfen die Parser-Regeln gezielt.")
        else:
            st.subheader("Ergebnisse pro Jahr")
            st.dataframe(df_year.sort_values(["person_key","year"]), use_container_width=True)

            st.subheader("Summen pro Person")
            st.dataframe(df_total, use_container_width=True)

            st.subheader("Verlauf je Person")
            persons = df_year["person_key"].unique().tolist()
            sel = st.selectbox("Person wählen", persons, index=0)
            chart_df = df_year[df_year["person_key"]==sel].sort_values("year")
            if not chart_df.empty:
                c = alt.Chart(chart_df).mark_bar().encode(
                    x="year:O", y="income:Q", tooltip=["year","income"]
                ).properties(height=300)
                st.altair_chart(c, use_container_width=True)

            st.markdown("---")
            st.subheader("⬇️ Export")
            xlsx = export_excel(df_year, df_total, save_local=True)
            st.download_button("Excel-Export (ByYear + Totals)", data=xlsx, file_name="finaura_ik_aggregation.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            st.caption("Tipp: Eine Kopie wird zusätzlich lokal gespeichert unter: ~/Documents/Finaura/Exports")

st.markdown("---")
st.caption("© FINAURA • Parser nutzt Tabellen (pdfplumber) + Regex-Fallback. Für 100% Präzision passen wir Regeln an dein IK-Layout an.")
