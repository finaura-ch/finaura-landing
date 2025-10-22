# ============================================================
# FINAURA – PDF Ingest (Upload-Guard + Silent OCR)
# Version: 1.2.0
# Datum: 2025-10-18 15:57 (Europe/Zurich)
# Change-Note: PDF-only Upload-Guard integriert + Silent OCR Fallback (ocrmypdf).
# Pfad-Empfehlung: ~/Documents/Finaura/app/
# ------------------------------------------------------------
# Setup (im Terminal ausführen, falls nötig):
#   pip install streamlit altair pandas pdfplumber ocrmypdf
#   streamlit run finaura_pdf_ingest_v1_2_0.py
# ============================================================

from __future__ import annotations
import io
import os
import tempfile
import subprocess
from typing import List

def _maybe_show_version():
    try:
        from finaura_versioner import show_version_in_sidebar
        show_version_in_sidebar(app_name="FINAURA PDF Ingest")
    except Exception:
        pass

PDF_MAGIC = b"%PDF-"

def _is_pdf_file(upload) -> bool:
    try:
        name = (upload.name or "").lower()
    except Exception:
        name = ""
    if not name.endswith(".pdf"):
        return False
    mime = getattr(upload, "type", "") or getattr(upload, "mime", "")
    if mime and ("pdf" not in mime.lower()):
        return False
    pos = upload.tell() if hasattr(upload, "tell") else None
    try:
        upload.seek(0)
        header = upload.read(5)
        return header == PDF_MAGIC
    finally:
        try:
            if pos is not None:
                upload.seek(pos)
        except Exception:
            pass

def _has_text(pdf_fileobj) -> bool:
    try:
        import pdfplumber
    except Exception as e:
        raise RuntimeError("pdfplumber nicht installiert. Bitte 'pip install pdfplumber' ausführen.") from e
    pdf_fileobj.seek(0)
    with pdfplumber.open(pdf_fileobj) as pdf:
        for page in pdf.pages:
            if (page.extract_text() or "").strip():
                return True
    return False

def ensure_ocr(uploaded_file):
    uploaded_file.seek(0)
    if _has_text(uploaded_file):
        uploaded_file.seek(0)
        return uploaded_file
    uploaded_file.seek(0)
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, "in.pdf")
        dst = os.path.join(td, "out.pdf")
        with open(src, "wb") as f:
            f.write(uploaded_file.read())
        try:
            subprocess.run(
                ["ocrmypdf", "--deskew", "--skip-text", "--force-ocr", src, dst],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except FileNotFoundError as e:
            raise RuntimeError("ocrmypdf nicht gefunden. Installiere es mit 'pip install ocrmypdf' und 'brew install tesseract'.") from e
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"OCR fehlgeschlagen: {e.stderr.decode('utf-8', 'ignore')[:400]}") from e
        return open(dst, "rb")

def upload_pdfs_streamlit(label: str = "📥 Upload (nur PDF)", key: str = "pdf_ingest",
                          max_total_mb: int = 500):
    import streamlit as st
    _maybe_show_version()
    uploads = st.file_uploader(
        label, type=["pdf"], accept_multiple_files=True, key=key,
        help="IK-Auszüge als PDF (Mehrfachauswahl möglich) – Nicht-PDFs werden blockiert."
    )
    if not uploads:
        return []
    valid, invalid = [], []
    total_bytes = 0
    for up in uploads:
        if _is_pdf_file(up):
            size = getattr(up, "size", None) or 0
            total_bytes += int(size)
            valid.append(up)
        else:
            invalid.append(up.name)
    if invalid:
        st.error("❌ Nicht-PDF erkannt und verworfen: " + ", ".join(invalid))
    total_mb = total_bytes / (1024 * 1024)
    if total_mb > max_total_mb:
        st.error(f"❌ Upload zu groß: {total_mb:.1f} MB > erlaubt {max_total_mb} MB.")
        return []
    result = []
    for up in valid:
        try:
            fixed = ensure_ocr(up)
            result.append(fixed)
        except Exception as e:
            st.error(f"❌ OCR-Problem bei '{getattr(up, 'name', 'Datei')}': {e}")
    if result:
        st.success(f"✅ {len(result)} PDF(s) akzeptiert und vorbereitet.")
    else:
        st.warning("⚠️ Keine verwendbaren PDFs erkannt.")
    return result

def _demo():
    import streamlit as st
    st.set_page_config(page_title="FINAURA PDF Ingest", layout="wide")
    _maybe_show_version()
    st.title("FINAURA PDF Ingest — Demo")
    st.caption("Akzeptiert nur echte PDFs, ergänzt bei Bedarf automatisch OCR.")
    files = upload_pdfs_streamlit()
    if files:
        st.subheader("Vorbereitete PDFs")
        for i, f in enumerate(files, 1):
            st.write(f"• PDF #{i} — bereit (Bytes-Stream)")

if __name__ == "__main__":
    _demo()
