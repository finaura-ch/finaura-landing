import { Container } from '../../components/Container'

export default function Privacy() {
  return (
    <div className="py-16">
      <Container>
        <h1 className="text-3xl font-semibold mb-4">Datenschutz</h1>
        <p className="text-gray-700 mb-4">
          FINAURA legt größten Wert auf Datenschutz und Anonymität. Die Nutzung unserer Analysefunktionen ist ohne Registrierung möglich. 
          Erhobene Eingaben dienen ausschließlich der Bereitstellung der Dienstleistung und werden nicht zu Werbezwecken verwendet.
        </p>
        <p className="text-gray-700 mb-2">Kontakt für Datenschutzanfragen: privacy@finaura.ch</p>
      </Container>
    </div>
  )
}
