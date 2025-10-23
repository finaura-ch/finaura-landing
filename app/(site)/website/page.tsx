// app/(site)/website/page.tsx
import React from "react";
import Link from "next/link";

export const metadata = {
  title: "FINAURA – Schweizer Finanzklarheit, anonym & neutral",
  description:
    "Klarheit in AHV, BVG, 3a & Budget – anonym, neutral, verständlich. Swiss Precision.",
};

export default function WebsitePage() {
  return (
    <main>
      {/* HERO */}
      <section className="hero">
        <div className="container">
          <p className="eyebrow">Swiss Precision • Privacy • Neutralität</p>
          <h1>
            Finanzklarheit – einfach, anonym,{" "}
            <span className="accent">präzise</span>.
          </h1>
          <p className="sub">
            FINAURA bringt Ordnung in AHV, BVG, 3a & Budget – Schritt für
            Schritt, neutral und auf den Punkt.
          </p>
          <div className="ctaRow">
            <Link href="/" className="btnPrimary">
              Jetzt anonym starten
            </Link>
            <a href="#how" className="btnGhost">
              So funktioniert’s
            </a>
          </div>
          <p className="mini">
            Keine Registrierung • Daten bleiben bei Ihnen • Schweizer Qualität
          </p>
        </div>
      </section>

      {/* TRUST / VALUE */}
      <section className="value">
        <div className="container grid grid-3">
          <div className="card">
            <h3>Neutral & unabhängig</h3>
            <p>
              Keine Produktverkäufe. Keine Provisionen. Nur fundierte
              Einordnung – für gute Entscheidungen.
            </p>
          </div>
          <div className="card">
            <h3>Anonym & privat</h3>
            <p>
              Start ohne Login oder Dateneingabe. Sie bleiben in Kontrolle –
              jederzeit.
            </p>
          </div>
          <div className="card">
            <h3>Schweizer Präzision</h3>
            <p>
              Klar, nachvollziehbar, korrekt. Komplexes verständlich gemacht –
              in wenigen Minuten.
            </p>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section id="how" className="how">
        <div className="container">
          <h2>So funktioniert’s</h2>
          <div className="grid grid-3 steps">
            <div className="step">
              <div className="nr">1</div>
              <h4>Situation wählen</h4>
              <p>
                AHV-Vorbezug, IK-Analyse, Splitting oder Budget. Wählen Sie den
                Bereich, der Sie gerade beschäftigt.
              </p>
            </div>
            <div className="step">
              <div className="nr">2</div>
              <h4>Einordnung erhalten</h4>
              <p>
                Sie erhalten eine klare, neutrale Einordnung – mit Wirkung,
                Risiken und den wichtigsten Stellschrauben.
              </p>
            </div>
            <div className="step">
              <div className="nr">3</div>
              <h4>Sicher entscheiden</h4>
              <p>
                Mit Verständnis statt Bauchgefühl entscheiden – Schritt für
                Schritt, in Ihrem Tempo.
              </p>
            </div>
          </div>
          <div className="ctaCenter">
            <Link href="/" className="btnPrimary">
              Jetzt anonym starten
            </Link>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="footer">
        <div className="container footerGrid">
          <div>© {new Date().getFullYear()} FINAURA</div>
          <nav className="footerNav">
            <Link href="/impressum">Impressum</Link>
            <Link href="/privacy">Datenschutz</Link>
          </nav>
        </div>
      </footer>

      {/* Styles */}
      <style jsx>{`
        :root {
          --bg: #ffffff;
          --ink: #0b1526;
          --muted: #5f6b7a;
          --accent: #1b6bfd;
          --card: #f6f8fb;
          --line: #e8edf5;
          --radius: 14px;
          --max: 1100px;
          --shadow: 0 12px 30px rgba(17, 38, 146, 0.08);
        }
        main {
          background: var(--bg);
          color: var(--ink);
        }
        .container {
          max-width: var(--max);
          margin: 0 auto;
          padding: 56px 20px;
        }
        .hero {
          background: radial-gradient(1200px 500px at -20% -20%, #eef4ff, #fff);
          border-bottom: 1px solid var(--line);
        }
        .eyebrow {
          text-transform: uppercase;
          letter-spacing: 0.12em;
          color: var(--muted);
          font-size: 12px;
          margin-bottom: 12px;
        }
        h1 {
          font-size: clamp(34px, 4.5vw, 54px);
          line-height: 1.05;
          margin: 0 0 14px;
        }
        h2 {
          font-size: clamp(26px, 3.2vw, 36px);
          margin: 0 0 10px;
        }
        h3 {
          font-size: 18px;
          margin: 0 0 6px;
        }
        h4 {
          font-size: 16px;
          margin: 0 0 6px;
        }
        .accent {
          color: var(--accent);
        }
        .sub {
          color: var(--muted);
          font-size: 18px;
          max-width: 760px;
          margin-bottom: 24px;
        }
        .mini {
          color: var(--muted);
          font-size: 13px;
          margin-top: 10px;
        }
        .ctaRow {
          display: flex;
          gap: 12px;
          margin: 18px 0;
          flex-wrap: wrap;
        }
        .btnPrimary,
        .btnGhost {
          display: inline-block;
          padding: 12px 18px;
          border-radius: 999px;
          text-decoration: none;
          font-weight: 600;
          transition: transform 0.04s ease, box-shadow 0.2s ease;
        }
        .btnPrimary {
          background: var(--accent);
          color: #fff;
          box-shadow: var(--shadow);
        }
        .btnPrimary:active {
          transform: translateY(1px);
        }
        .btnGhost {
          border: 1px solid var(--line);
          color: var(--ink);
          background: #fff;
        }

        .grid {
          display: grid;
          gap: 16px;
        }
        .grid-3 {
          grid-template-columns: repeat(3, minmax(0, 1fr));
        }
        @media (max-width: 900px) {
          .grid-3 {
            grid-template-columns: 1fr;
          }
        }

        .value {
          background: #fff;
        }
        .card {
          background: var(--card);
          border: 1px solid var(--line);
          border-radius: var(--radius);
          padding: 22px;
        }

        .how {
          background: #fbfcff;
          border-top: 1px solid var(--line);
          border-bottom: 1px solid var(--line);
        }
        .steps {
          margin-top: 14px;
        }
        .step {
          background: #fff;
          border: 1px solid var(--line);
          border-radius: var(--radius);
          padding: 20px;
        }
        .nr {
          width: 28px;
          height: 28px;
          border-radius: 50%;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          font-weight: 700;
          background: var(--accent);
          color: #fff;
          margin-bottom: 8px;
        }
        .ctaCenter {
          display: flex;
          justify-content: center;
          margin-top: 22px;
        }

        .footer {
          padding: 22px 0;
        }
        .footerGrid {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 16px;
          flex-wrap: wrap;
          border-top: 1px solid var(--line);
          padding-top: 14px;
        }
        .footerNav {
          display: flex;
          gap: 14px;
        }
      `}</style>
    </main>
  );
}

