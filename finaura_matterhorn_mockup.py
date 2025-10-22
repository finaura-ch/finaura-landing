# coding: utf-8
"""
FINAURA – Matterhorn Visual (S2)
Desktop-Mockup + UI-Visual in Streamlit
Run: streamlit run finaura_matterhorn_mockup.py
"""
import io
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

st.set_page_config(page_title="FINAURA – Matterhorn Visual", page_icon="🧭", layout="wide")
st.title("🧭 FINAURA – Matterhorn Visual (S2)")

st.caption("Swiss Minimal · zentrierte Route (P2) · Icons dezent · Claim: 'Klarheit. Kontrolle. Freiheit.'")

# ---------- Parameters ----------
claim = "Klarheit. Kontrolle. Freiheit."
labels = {
    "summit": "🚩 Finanzielle Freiheit",
    "camp3": "Camp 3:\nEinkommen steigern",
    "camp2": "Camp 2:\nSteuern optimieren",
    "base": "Basecamp:\nBudget steuern",
}

# ---------- Draw function ----------
def render_matterhorn(figsize=(12,7), dpi=160, show_axes=False):
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # Simple, clean mountain silhouette (smooth curve, centered)
    x = np.array([0, 2, 4, 5, 6, 8, 10])
    y = np.array([0, 3, 5.5, 8, 5.5, 3, 0])
    ax.plot(x, y, linewidth=1.2)  # keep colors default for a neutral Swiss look

    # Positions (centered along the ridge)
    ax.text(5, 8.25, labels["summit"], ha="center", va="bottom", fontsize=16, fontweight="bold")
    ax.text(5, 5.8, labels["camp3"], ha="center", va="bottom", fontsize=13)
    ax.text(5, 3.8, labels["camp2"], ha="center", va="bottom", fontsize=13)
    ax.text(5, 1.55, labels["base"], ha="center", va="bottom", fontsize=13)

    # Title + Claim
    ax.set_title("FINAURA – Matterhorn Finanzplan Reise", pad=18, fontsize=18, fontweight="bold")
    ax.text(5, -0.9, claim, ha="center", fontsize=14)

    # Clean look
    if not show_axes:
        ax.axis("off")

    fig.tight_layout()
    return fig

# ---------- UI ----------
col1, col2 = st.columns([3,2], gap="large")

with col1:
    st.subheader("Desktop-Mockup (Preview)")
    fig = render_matterhorn(figsize=(12,7), dpi=160)
    st.pyplot(fig, use_container_width=True)

with col2:
    st.subheader("Onboarding (für Budget-Tab)")
    st.write(
        "Ein guter Finanzplan beginnt im **Basecamp**: Budget steuern, Sparquote sichern, Sicherheit schaffen. "
        "Dann folgt **Camp 2**: Steuern optimieren – mehr Netto ohne mehr Arbeit. "
        "In **Camp 3** erhöhst du dein **Einkommen** über Skills und Karriere. "
        "Am **Gipfel** lässt du dein **Kapital investieren** und erreichst echte **finanzielle Freiheit**."
    )
    st.markdown("---")
    st.subheader("Gamification-Levels")
    st.write("**Basecamp** – Budget & Kontrolle | **Camp 2** – Steuern | **Camp 3** – Einkommen | **Gipfel** – Investieren & Freiheit")

st.markdown("---")

# ---------- Exports ----------
st.subheader("Export")
fmt = st.selectbox("Format wählen", ["PNG 1920x1080", "PNG 1600x900 (UI)"], index=0)

if st.button("Bild erzeugen & herunterladen"):
    if fmt.startswith("PNG 1920"):
        fig2 = render_matterhorn(figsize=(19.2,10.8), dpi=100)  # ~1920x1080
        fname = "finaura_matterhorn_desktop.png"
    else:
        fig2 = render_matterhorn(figsize=(16,9), dpi=100)       # 1600x900
        fname = "finaura_matterhorn_ui.png"

    buf = io.BytesIO()
    fig2.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig2)
    st.download_button("Download", buf.getvalue(), file_name=fname, mime="image/png")
    st.success(f"Export fertig: {fname}")
