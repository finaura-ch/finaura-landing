import type { Metadata } from 'next'
import './globals.css'
import { Header } from '../components/Header'
import { Footer } from '../components/Footer'

export const metadata: Metadata = {
  title: 'FINAURA — Schweizer Finanzklarheit',
  description: 'FINAURA: Schweizer Finanzklarheit, anonym und neutral. Verstehe deine Finanzen ohne Datenpreisgabe, ohne Verkaufsdruck.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="de">
      <body className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  )
}
