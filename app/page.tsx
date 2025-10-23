"use client";
// app/page.tsx
import React from "react";
import Link from "next/link";

export const metadata = {
  title: "FINAURA – Schweizer Finanzklarheit. Anonym. Neutral. Vertrauenswürdig.",
  description:
    "Klarheit in AHV, BVG, 3a & Budget – anonym, neutral und verständlich. Swiss Precision.",
};

export default function HomePage() {
  return (
    <main>
      {/* HERO */}
      <section className="hero">
        <div className="container">
          <p className="eyebrow">Swiss Precision • Anonym • Neutral</p>
          <h1>
            Schweizer Finanzklarheit – <span className="accent">ruhig</span>,
            <span className="accent"> präzise</span>, vertrauenswürdig.
          </h1>
          <p className="sub">
            Verstehen Sie Ihre Situation in wenigen Minuten – ohne Login, ohne
            Verkaufsdruck. FINAURA erklärt, ordnet ein und macht komplexes
            verständlich.
          </p>
          <div className="ctaRow">
            <Link href="/website" className="btnPrimary">Mehr über FINAURA</Link>
            <Link href="/av-vorbezug" className="btnGhost">AV-Vorbezug testen</Link>
          </div>
          <p className="mini">Daten bleiben bei Ihnen • Keine Registrierung • Schweizer Qualität</p>
        </div>
      </section>

      {/* TRUST / WARUM FINAURA */}
      <section className="value">
        <div className="container grid grid-3">
          <div className="card">
            <h3>Neutral & unabhängig</h3>
            <p>Keine Produktverkäufe, keine Provisionen – nur klare Einordnung für gute Entscheidungen.</p>
          </div>
          <div className="card">
            <h3>Anonym & privat</h3>
            <p>Start ohne Login. Sie behalten die Kontrolle über Ihre Angaben – jederzeit.</p>
          </div>
          <div className="card">
            <h3>Schweizer Präzision</h3>
            <p>Komplexes verständlich, korrekt und nachvollziehbar – Schritt für Schritt.</p>
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
              <h4>Bereich wählen</h4>
              <p>AV-Vorbezug, IK-Analyse, Splitting oder Budget – starten Sie dort, wo es für Sie zählt.</p>
            </div>
            <div className="step">
              <div className="nr">2</div>
              <h4>Einordnung erhalten</h4>
              <p>Klare Wirkung, Risiken und Stellschrauben – neutral erklärt, ohne Verkaufen.</p>
            </div>
            <div className="step">
              <div className="nr">3</div>
              <h4>Sicher entscheiden</h4>
              <p>Mit Verständnis statt Bauchgefühl – in Ihrem Tempo, anonym und nachvollziehbar.</p>
            </div>
          </div>
          <div className="ctaCenter">
            <Link href="/av-vorbezug" className="btnPrimary">AV-Vorbezug testen</Link>
          </div>
        </div>
      </section>

      {/* COMING SOON / WARTELISTE */}
      <section className="coming">
        <div className="container comingGrid">
          <div>
            <h2>Premium & Pro – bald verfügbar</h2>
            <p className="muted">
              Erweiterte Analysen, Szenarien, Export & Experten-Feedback. Aktuell im Aufbau –
              tragen Sie sich ein und wir informieren Sie beim Start.
            </p>
          </div>
          <form
            className="waitlist"
            action="https://formspree.io/f/xblddemo"
            method="POST"
          >
            <input
              type="email"
              name="email"
              placeholder="Ihre E-Mail (Warteliste)"
              aria-label="E-Mail für Warteliste"
              required
            />
            <button type="submit">Auf Warteliste</button>
          </form>
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
        main { background: var(--bg); color: var(--ink); }
        .container { max-width: var(--max); margin: 0 auto; padding: 56px 20px; }
        .hero {
          background: radial-gradient(1200px 500px at -20% -20%, #eef4ff, #fff);
          border-bottom: 1px solid var(--line);
        }
        .eyebrow { text-transform: uppercase; letter-spacing: .12em; color: var(--muted); font-size: 12px; margin-bottom: 12px; }
        h1 { font-size: clamp(34px, 4.5vw, 54px); line-height: 1.05; margin: 0 0 14px; }
        h2 { font-size: clamp(26px, 3.2vw, 36px); margin: 0 0 10px; }
        h3 { font-size: 18px; margin: 0 0 6px; }
        h4 { font-size: 16px; margin: 0 0 6px; }
        .accent { color: var(--accent); }
        .sub { color: var(--muted); font-size: 18px; max-width: 760px; margin-bottom: 24px; }
        .mini { color: var(--muted); font-size: 13px; margin-top: 10px; }
        .ctaRow { display: flex; gap: 12px; margin: 18px 0; flex-wrap: wrap; }
        .btnPrimary, .btnGhost {
          display: inline-block; padding: 12px 18px; border-radius: 999px; text-decoration: none; font-weight: 600;
          transition: transform .04s ease, box-shadow .2s ease;
        }
        .btnPrimary { background: var(--accent); color: #fff; box-shadow: var(--shadow); }
        .btnPrimary:active { transform: translateY(1px); }
        .btnGhost { border: 1px solid var(--line); color: var(--ink); background: #fff; }

        .grid { display: grid; gap: 16px; }
        .grid-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
        @media (max-width: 900px) { .grid-3 { grid-template-columns: 1fr; } }

        .value { background: #fff; }
        .card { background: var(--card); border: 1px solid var(--line); border-radius: var(--radius); padding: 22px; }

        .how { background: #fbfcff; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
        .steps { margin-top: 14px; }
        .step { background: #fff; border: 1px solid var(--line); border-radius: var(--radius); padding: 20px; }
        .nr {
          width: 28px; height: 28px; border-radius: 50%;
          display: inline-flex; align-items: center; justify-content: center;
          font-weight: 700; background: var(--accent); color: #fff; margin-bottom: 8px;
        }
        .ctaCenter { display: flex; justify-content: center; margin-top: 22px; }

        .coming { background: #fff; }
        .comingGrid {
          display: grid; gap: 18px; grid-template-columns: 1.2fr .8fr;
          align-items: start; border-top: 1px solid var(--line); padding-top: 24px;
        }
        @media (max-width: 900px) { .comingGrid { grid-template-columns: 1fr; } }
        .waitlist { display: grid; grid-template-columns: 1fr auto; gap: 10px; }
        .waitlist input {
          border: 1px solid var(--line); border-radius: 999px; padding: 12px 14px; outline: none;
        }
        .waitlist button {
          border: 0; border-radius: 999px; padding: 12px 18px; background: var(--accent); color: #fff; font-weight: 600;
        }
        .muted { color: var(--muted); }

        .footer { padding: 22px 0; }
        .footerGrid {
          display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap;
          border-top: 1px solid var(--line); padding-top: 14px;
        }
        .footerNav { display: flex; gap: 14px; }
      `}</style>
    </main>
  );
}

