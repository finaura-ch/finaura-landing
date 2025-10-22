# FINAURA UI Module — v0.1.0 (2025-10-18, Europe/Zurich)
# Zweck: Wiederverwendbarer UX‑Baustein für alle FINAURA‑Apps (Header, Styles, Cards).
# Ablagepfad: ~/Downloads/finaura_app  (verknüpft mit  ~/Documents/Finaura/app)
# Install (falls nötig): pip install streamlit altair pandas
# Run (Beispiel-App):     streamlit run <dateiname>.py
#
# Verwendung in deiner App:
#   from finaura_ui import render_header, finaura_card, inject_base_styles
#   st.set_page_config(page_title="FINAURA …", layout="wide")
#   render_header("IK Analyzer", version="1.2.2", subtitle="Präzise Jahreswerte", logo="📈")
#
#   finaura_card("Hinweis", "Lade ein IK‑PDF hoch.", tone="info")
#   finaura_card("Erfolg", "3 Jahre erkannt.", tone="success")
#   finaura_card("Achtung", "Keine Werte erkannt – Debug einschalten.", tone="warning")
#   finaura_card("Fehler", "Kein Text extrahierbar (evtl. Scan ohne OCR).", tone="error")

from __future__ import annotations

from typing import Optional
import streamlit as st
from datetime import datetime

# ---- FINAURA Farben (Weiß/Blau) ----
PRIMARY = "#1e88e5"   # Blau
ACCENT  = "#e3f2fd"   # Helles Blau
SUCCESS = "#1b5e20"
WARNING = "#e65100"
ERROR   = "#b71c1c"

__all__ = [
    "PRIMARY", "ACCENT", "SUCCESS", "WARNING", "ERROR",
    "inject_base_styles", "render_header", "finaura_card"
]

def inject_base_styles() -> None:
    """Injiziert globale Basis-Styles (Hintergrund, Abstände, Buttons, Uploader)."""
    st.markdown(f"""
    <style>
      .stApp {{ background: #fff; }}
      .block-container {{ padding-top: 1.3rem; }}
      h1, h2, h3 {{ color: {PRIMARY}; }}

      /* Buttons einheitlich */
      .stButton>button {{
        border-radius: 12px;
        padding: .55rem 1rem;
      }}

      /* File Uploader */
      [data-testid="stFileUploaderDropzone"] {{
        border-radius: 14px !important;
        border: 1.5px dashed #bcd7fb !important;
        background: {ACCENT}55 !important;
      }}

      /* FINAURA Card */
      .fna-card {{
        border-radius: 14px;
        padding: .9rem 1rem;
        border: 1px solid #e6eef9;
        background: #fafcff;
        margin: .25rem 0 .75rem 0;
      }}
      .fna-card h4 {{
        margin: 0 0 .35rem 0;
        font-size: 1rem;
        color: {PRIMARY};
      }}
      .fna-card--success {{ border-color: #c8e6c9; background:#f1f8e9; }}
      .fna-card--warning {{ border-color: #ffe0b2; background:#fff8e1; }}
      .fna-card--error   {{ border-color: #ffcdd2; background:#ffebee;  }}
    </style>
    """, unsafe_allow_html=True)

def render_header(
    app_name: str,
    version: str,
    subtitle: Optional[str] = None,
    logo: str = "📊",
    info_right: Optional[str] = None,
) -> None:
    """Zeigt den FINAURA-Header mit Logo, App-Namen und Version."""
    inject_base_styles()
    today = datetime.now().strftime("%d.%m.%Y")
    if info_right is None:
        info_right = f"v{version} · {today}"
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                padding:.6rem 0 .8rem 0;border-bottom:1px solid #e9eef7;">
      <div style="display:flex;align-items:center;gap:.6rem;">
        <div style="width:30px;height:30px;border-radius:8px;display:grid;place-items:center;
                    background:{ACCENT};color:{PRIMARY};font-size:18px;">{logo}</div>
        <div>
          <div style="font-weight:700;font-size:1.1rem;color:{PRIMARY};letter-spacing:.2px;">
            FINAURA · {app_name}
          </div>
          {"<div style='opacity:.75;font-size:.85rem;margin-top:2px;'>"+subtitle+"</div>" if subtitle else ""}
        </div>
      </div>
      <div style="font-size:.9rem;opacity:.8;">{info_right}</div>
    </div>
    """, unsafe_allow_html=True)

def finaura_card(title: str, body: Optional[str] = None, *, tone: str = "info") -> None:
    """Kompakte Info-Card. tone: 'info' | 'success' | 'warning' | 'error'."""
    tone_class = {
        "info": "",
        "success": " fna-card--success",
        "warning": " fna-card--warning",
        "error": " fna-card--error",
    }.get(tone, "")
    st.markdown(f"""
    <div class="fna-card{tone_class}">
      <h4>{title}</h4>
      {"<div>"+body+"</div>" if body else ""}
    </div>
    """, unsafe_allow_html=True)
