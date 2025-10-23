"use client";

export default function HomePage() {
  return (
    <main className="home">
      <section className="hero">
        <h1>FINAURA — Schweizer Finanzklarheit</h1>
        <p>
          Klarheit in AHV, BVG, 3a & Budget — anonym, neutral, verständlich.
        </p>
      </section>

      {/* Beispiel-Content – kann beliebig ersetzt werden */}
      <section className="grid">
        <div className="card">Neutralität</div>
        <div className="card">Anonymität</div>
        <div className="card">Swiss Precision</div>
      </section>

      <style jsx>{`
        .home {
          padding: 32px 20px;
          max-width: 1100px;
          margin: 0 auto;
        }
        .hero {
          margin: 24px 0 32px;
        }
        .hero h1 {
          margin: 0 0 8px;
          font-size: 32px;
          line-height: 1.2;
        }
        .hero p {
          margin: 0;
          opacity: 0.75;
        }
        .grid {
          display: grid;
          gap: 16px;
          grid-template-columns: repeat(3, minmax(0, 1fr));
          margin-top: 28px;
        }
        .card {
          border: 1px solid var(--line, #e5e7eb);
          border-radius: 12px;
          padding: 20px;
          background: var(--card, #fff);
        }
        @media (max-width: 900px) {
          .grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </main>
  );
}
