"""
FINAURA Versioning Helper
-------------------------

Install (once):
    pip install streamlit altair pandas

Run app (example):
    streamlit run finaura_ik_analyzer_v1_1_0.py

This module reads the VERSION file from the FINAURA root folder,
exposes a small API to show the version in Streamlit's sidebar,
and appends simple CHANGELOG entries.

Recommended project root: ~/Documents/FINAURA
Files used:
- VERSION            -> current semantic version (e.g., 1.1.0)
- CHANGELOG.md       -> appended with timestamped entries
"""

from __future__ import annotations
import os
from pathlib import Path
from datetime import datetime

ROOT_DEFAULT = Path.home() / "Documents" / "FINAURA"

def _root(root: str | os.PathLike | None) -> Path:
    return Path(root) if root else ROOT_DEFAULT

def read_version(root: str | os.PathLike | None = None) -> str:
    """Return version string from VERSION file (defaults to ROOT_DEFAULT)."""
    r = _root(root)
    vf = r / "VERSION"
    if not vf.exists():
        return "0.0.0"
    return vf.read_text(encoding="utf-8").strip()

def write_version(new_version: str, root: str | os.PathLike | None = None) -> None:
    r = _root(root)
    vf = r / "VERSION"
    vf.write_text(new_version.strip() + "\n", encoding="utf-8")

def bump_version(current: str, bump: str) -> str:
    major, minor, patch = (int(x) for x in current.split("."))
    b = bump.upper().strip()
    if b == "MAJOR":
        major += 1; minor = 0; patch = 0
    elif b == "MINOR":
        minor += 1; patch = 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"

def append_changelog(note: str, new_version: str | None = None, root: str | os.PathLike | None = None) -> None:
    r = _root(root)
    cf = r / "CHANGELOG.md"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = f"\n## {new_version or read_version(r)} — {ts}\n\n"
    entry = f"- {note.strip()}\n" if note else "- (kein Kommentar)\n"
    with cf.open("a", encoding="utf-8") as f:
        f.write(header)
        f.write(entry)

def show_version_in_sidebar(app_name: str = "FINAURA", root: str | os.PathLike | None = None) -> str:
    """Render the current version in Streamlit's sidebar and return it."""
    try:
        import streamlit as st
    except Exception:
        raise RuntimeError("Streamlit not installed. Run: pip install streamlit")
    ver = read_version(root)
    st.sidebar.markdown(f"**{app_name} — Version {ver}**")
    return ver
