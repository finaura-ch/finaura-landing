import Link from 'next/link'
import { clsx } from 'clsx'

export function Button({ href = '#', children, variant = 'primary' }: { href?: string; children: React.ReactNode; variant?: 'primary' | 'secondary' }) {
  return (
    <Link href={href} className={clsx(variant === 'primary' ? 'btn-primary' : 'btn-secondary')}>
      {children}
    </Link>
  )
}
