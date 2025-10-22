import Link from 'next/link'
import { Container } from './Container'

export function Footer() {
  return (
    <footer className="border-t border-gray-100 mt-16">
      <Container className="py-10 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-gray-600">
        <div>© {new Date().getFullYear()} FINAURA — Schweizer Finanzklarheit</div>
        <div className="flex items-center gap-4">
          <Link className="link" href="/privacy">Datenschutz</Link>
          <Link className="link" href="/impressum">Impressum</Link>
          <span className="text-gray-400">v1.0.0 · 2025-10-22</span>
        </div>
      </Container>
    </footer>
  )
}
