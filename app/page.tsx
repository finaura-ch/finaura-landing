import Image from 'next/image'
import { Container } from '../components/Container'
import { Section } from '../components/Section'
import { Button } from '../components/Button'

export default function Page() {
  return (
    <>
      {/* Hero */}
      <Section className="bg-gradient-to-b from-brand-light/60 to-white">
        <Container>
          <div className="grid gap-10 lg:grid-cols-2 items-center">
            <div className="space-y-6">
              <span className="inline-block rounded-full bg-brand-light px-3 py-1 text-sm font-medium text-brand">Schweizer FinTech</span>
              <h1 className="text-4xl sm:text-5xl font-semibold leading-tight">
                FINAURA — Schweizer Finanzklarheit, anonym und neutral.
              </h1>
              <p className="text-lg text-gray-600">
                Verstehe deine Finanzen wie ein Profi — ohne Datenpreisgabe, ohne Verkaufsdruck. 
                Analyse. Verständnis. Sicherheit — in wenigen Minuten.
              </p>
              <div className="flex gap-3">
                <Button href="#start-anonym" variant="primary">Jetzt anonym starten</Button>
                <Button href="#wie-es-funktioniert" variant="secondary">So funktioniert’s</Button>
              </div>
              <div className="text-xs text-gray-500">100% anonym · Swiss Precision · Keine Werbung</div>
            </div>
            <div className="relative h-[320px] sm:h-[420px] lg:h-[480px]">
              <div className="absolute inset-0 rounded-2xl border border-gray-200 bg-white shadow-soft" />
              <Image src="/hero.png" alt="FINAURA App Vorschau" fill className="object-cover rounded-2xl" />
            </div>
          </div>
        </Container>
      </Section>

      {/* Werte/Trust */}
      <Section>
        <Container>
          <div className="grid sm:grid-cols-3 gap-6">
            {[
              { title: 'Neutralität', text: 'Unabhängig. Keine Produktverkäufe. Dein Vorteil steht im Zentrum.' },
              { title: 'Anonymität', text: 'Starte ohne Login oder Datenpreisgabe. Du behältst die Kontrolle.' },
              { title: 'Swiss Precision', text: 'Klar, fundiert, verständlich. Für Entscheidungen mit gutem Gefühl.' },
            ].map((item) => (
              <div key={item.title} className="card p-6">
                <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
                <p className="text-gray-600">{item.text}</p>
              </div>
            ))}
          </div>
        </Container>
      </Section>

      {/* Problem → Lösung → Nutzen */}
      <Section>
        <Container>
          <div className="grid lg:grid-cols-3 gap-6">
            <div className="card p-6">
              <h3 className="text-xl font-semibold mb-2">Das Problem</h3>
              <p className="text-gray-600">Komplexe Regeln, versteckte Interessen und Zeitmangel machen Finanzentscheidungen schwer.</p>
            </div>
            <div className="card p-6">
              <h3 className="text-xl font-semibold mb-2">Die Lösung</h3>
              <p className="text-gray-600">FINAURA analysiert deine Situation anonym, erklärt sie klar und leitet dich fokussiert durch Entscheidungen.</p>
            </div>
            <div className="card p-6">
              <h3 className="text-xl font-semibold mb-2">Der Nutzen</h3>
              <p className="text-gray-600">Mehr Klarheit, weniger Stress, bessere Resultate — ohne Verkaufsdruck.</p>
            </div>
          </div>
        </Container>
      </Section>

      {/* 3-Step-Flow */}
      <Section id="wie-es-funktioniert">
        <Container>
          <div className="text-center mb-10">
            <h2 className="text-3xl font-semibold">Analysieren → Verstehen → Entscheiden</h2>
            <p className="text-gray-600 mt-2">In drei Schritten zur Finanzklarheit.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { step: '01', title: 'Analysieren', text: 'Gib wenige Eckdaten ein — ganz anonym. FINAURA rechnet im Hintergrund.' },
              { step: '02', title: 'Verstehen', text: 'Erhalte klare, visuelle Auswertungen und Prioritäten statt Fachchinesisch.' },
              { step: '03', title: 'Entscheiden', text: 'Treffe gute Entscheidungen — auf Basis neutraler Fakten.' },
            ].map((s) => (
              <div key={s.step} className="card p-6">
                <div className="text-brand font-semibold">{s.step}</div>
                <h3 className="text-xl font-semibold mb-2">{s.title}</h3>
                <p className="text-gray-600">{s.text}</p>
              </div>
            ))}
          </div>
        </Container>
      </Section>

      {/* Start-CTA */}
      <Section id="start-anonym" className="bg-brand-light/50">
        <Container>
          <div className="card p-8 text-center">
            <h2 className="text-2xl sm:text-3xl font-semibold">Bereit? Starte jetzt anonym.</h2>
            <p className="text-gray-600 mt-2">Keine Registrierung. Keine Werbung. Du behältst die Kontrolle.</p>
            {/* TODO: Wenn Streamlit-URL bekannt, hier ersetzen: href="https://DEIN-STREAMLIT-URL" */}
            <div className="mt-6">
              <Button href="#" variant="primary">Jetzt anonym starten</Button>
            </div>
            <p className="text-xs text-gray-500 mt-3">Hinweis: Der Start-Button kann auf eure bestehende Streamlit-App verlinken.</p>
          </div>
        </Container>
      </Section>
    </>
  )
}
