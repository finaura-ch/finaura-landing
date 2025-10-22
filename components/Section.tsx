import { clsx } from 'clsx'

export function Section({ children, id, className }: { children: React.ReactNode; id?: string; className?: string }) {
  return (
    <section id={id} className={clsx('py-16 sm:py-20', className)}>
      {children}
    </section>
  )
}
