// app/av-vorbezug/page.tsx
export const metadata = {
  title: "AV-Vorbezug – FINAURA (Free Tool, Beta)",
  robots: { index: false, follow: true },
};

export default function AvVorbezugPage() {
  return (
    <main style={{ maxWidth: 900, margin: "0 auto", padding: "48px 20px" }}>
      <h1>AV-Vorbezug (Free) – Beta</h1>
      <p style={{ color: "#5f6b7a" }}>
        Hier entsteht Ihr kostenloses Tool zum AV-Vorbezug – verständlich, anonym, neutral.
      </p>
      <hr style={{ margin: "18px 0 24px", border: 0, borderTop: "1px solid #e8edf5" }} />
      <p>In Kürze verfügbar: Eingaben links, Auswertung rechts – wie besprochen.</p>
    </main>
  );
}

