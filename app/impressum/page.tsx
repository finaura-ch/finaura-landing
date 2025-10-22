import { Container } from '../../components/Container'

export default function Impressum() {
  return (
    <div className="py-16">
      <Container>
        <h1 className="text-3xl font-semibold mb-4">Impressum</h1>
        <p className="text-gray-700">Angaben gemäss schweizerischem Recht. Verantwortlich für den Inhalt: FINAURA.</p>
        <p className="text-gray-700 mt-2">Kontakt: hello@finaura.ch</p>
      </Container>
    </div>
  )
}
