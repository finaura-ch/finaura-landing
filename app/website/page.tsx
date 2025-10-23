// app/website/page.tsx
import Link from "next/link";

export const metadata = {
  title: "FINAURA — Website",
  description:
    "Schweizer Finanzklarheit – anonym, neutral und verständlich. Starte ohne Login.",
};

export default function WebsitePage() {
  return (
    <main className="min-h-screen">
      {/* HERO */}
      <section className="relative">
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-blue-50/60 to-transparent" />
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-16 sm:py-24 relative">
          <span className="inline-flex items-center rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
            Schweizer FinTech
          </span>

          <h1 className="mt-4 max-w-3xl text-4xl sm:text-5xl font-semibold tracking-tight text-slate-900">
            FINAURA — Schweizer Finanzklarheit, anonym und neutral.
          </h1>

          <p className="mt-5 max-w-2xl text-slate-600 leading-relaxed">
            Verstehe deine Finanzen wie ein Profi — ohne Datenpreisgabe, ohne
            Verkaufsdruck. Analyse. Verständnis. Sicherheit — in wenigen
            Minuten.
          </p>

          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/#start-anonym"
              className="inline-flex items-center justify-center rounded-xl bg-blue-600 px-5 py-3 text-white shadow-sm transition hover:bg-blue-700 active:scale-[0.99]"
            >
              Jetzt anonym starten
            </Link>
            <Link
              href="/so-funktionierts"
              className="inline-flex items-center justify-center rounded-xl border border-slate-200 bg-white px-5 py-3 text-slate-900 shadow-sm transition hover:bg-slate-50"
            >
              So funktioniert’s
            </Link>
          </div>

          <div className="mt-6 flex flex-wrap gap-4 text-xs text-slate-500">
            <span>100% anonym</span>
            <span>•</span>
            <span>Swiss Precision</span>
            <span>•</span>
            <span>Keine Werbung</span>
          </div>
        </div>
      </section>

      {/* VALUE CARDS */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pb-6 sm:pb-10">
        <div className="grid gap-4 sm:gap-6 md:grid-cols-3">
          {[
            {
              t: "Neutralität",
              d: "Unabhängig. Keine Produktverkäufe. Dein Vorteil steht im Zentrum.",
            },
            {
              t: "Anonymität",
              d: "Starte ohne Login oder Datenpreisgabe. Du behältst die Kontrolle.",
            },
            {
              t: "Swiss Precision",
              d: "Klar, fundiert, verständlich – für Entscheidungen mit gutem Gefühl.",
            },
          ].map((c) => (
            <div
              key={c.t}
              className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
            >
              <h3 className="text-slate-900 font-semibold">{c.t}</h3>
              <p className="mt-2 text-slate-600 text-sm leading-relaxed">
                {c.d}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* MODULE OVERVIEW */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8 sm:py-12">
        <div className="flex items-end justify-between gap-4">
          <div>
            <h2 className="text-2xl sm:text-3xl font-semibold text-slate-900">
              Module & Wege zur Klarheit
            </h2>
            <p className="mt-2 text-slate-600">
              Wähle dein Thema – kurz, fokussiert und verständlich.
            </p>
          </div>
        </div>

        <div className="mt-6 grid gap-4 sm:gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[
            {
              href: "/ik",
              t: "IK-Analyse (AHV)",
              d: "Beiträge & Lücken verstehen. Grundlage für Entscheidungen.",
            },
            {
              href: "/bvg",
              t: "BVG / Pensionskasse",
              d: "Einkäufe, Leistungen & Optionen einschätzen.",
            },
            {
              href: "/3a",
              t: "Säule 3a",
              d: "Sinnvoll nutzen – steuerlich und strategisch.",
            },
            {
              href: "/budget",
              t: "Budget & Liquidität",
              d: "Was ist drin? Welche Spielräume hast du wirklich?",
            },
            {
              href: "/zukunft",
              t: "Zukunft & Vorsorge",
              d: "Rente, Kapital oder Mischung: Was passt zu dir?",
            },
            {
              href: "/micro-advice",
              t: "Micro-Advice",
              d: "Kurze, anonyme Expertenantworten – fair bewertet.",
            },
          ].map((m) => (
            <Link
              key={m.t}
              href={m.href}
              className="group rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
            >
              <div className="flex items-start justify-between">
                <h3 className="text-slate-900 font-semibold">{m.t}</h3>
                <span className="rounded-full border border-slate-200 px-2 py-1 text-[10px] text-slate-500">
                  Öffnen
                </span>
              </div>
              <p className="mt-2 text-slate-600 text-sm leading-relaxed">
                {m.d}
              </p>
              <div className="mt-4 inline-flex items-center text-sm font-medium text-blue-700">
                Weiter <span className="ml-1 transition group-hover:translate-x-0.5">→</span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* CTA STRIP */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pb-16 sm:pb-24">
        <div className="rounded-2xl bg-gradient-to-r from-blue-600 to-blue-500 p-6 sm:p-8 text-white shadow-sm">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 className="text-xl sm:text-2xl font-semibold">
                Starte jetzt anonym – und gewinne Klarheit in Minuten.
              </h3>
              <p className="mt-1 text-blue-100">
                Keine Registrierung. Keine Werbung. Nur gute Antworten.
              </p>
            </div>
            <div className="flex gap-3">
              <Link
                href="/#start-anonym"
                className="rounded-xl bg-white px-5 py-3 text-slate-900 shadow-sm transition hover:bg-blue-50"
              >
                Jetzt anonym starten
              </Link>
              <Link
                href="/so-funktionierts"
                className="rounded-xl border border-white/40 px-5 py-3 text-white transition hover:bg-white/10"
              >
                Mehr erfahren
              </Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
