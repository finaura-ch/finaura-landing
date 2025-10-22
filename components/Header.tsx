import Link from 'next/link'
import Image from 'next/image'
import { Container } from './Container'

export function Header() {
  return (
    <header className="sticky top-0 z-40 backdrop-blur bg-white/80 border-b border-gray-100">
      <Container className="flex h-16 items-center justify-between">
        <div className="flex items-center gap-3">
          <Image src="/logo.svg" alt="FINAURA" width={28} height={28} />
          <Link href="/" className="font-semibold">FINAURA</Link>
        </div>
        <nav className="hidden sm:flex items-center gap-6 text-sm text-gray-700">
          <Link href="#wie-es-funktioniert" className="hover:text-gray-900">So funktioniert’s</Link>
          <Link href="/privacy" className="hover:text-gray-900">Datenschutz</Link>
          <Link href="/impressum" className="hover:text-gray-900">Impressum</Link>
          <Link href="#start-anonym" className="btn-primary text-sm">Jetzt anonym starten</Link>
        </nav>
      </Container>
    </header>
  )
}
