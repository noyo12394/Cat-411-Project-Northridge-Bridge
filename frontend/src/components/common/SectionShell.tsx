import type { PropsWithChildren, ReactNode } from 'react'
import { motion } from 'framer-motion'
import { revealTransition } from '../../animations/motion'

interface SectionShellProps extends PropsWithChildren {
  id: string
  index: string
  eyebrow: string
  title: string
  description: string
  actions?: ReactNode
}

export function SectionShell({
  id,
  index,
  eyebrow,
  title,
  description,
  actions,
  children,
}: SectionShellProps) {
  return (
    <section id={id} className="relative scroll-mt-28 space-y-7">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.25 }}
        transition={revealTransition}
        className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between"
      >
        <div className="max-w-4xl">
          <div className="flex items-center gap-3">
            <span className="rounded-full border border-line bg-white/5 px-3 py-1 font-mono text-[11px] uppercase tracking-[0.3em] text-seismic/75">
              {index}
            </span>
            <span className="font-mono text-[11px] uppercase tracking-[0.34em] text-muted">
              {eyebrow}
            </span>
          </div>
          <h2 className="mt-5 max-w-4xl font-display text-4xl font-semibold tracking-[-0.05em] text-ink sm:text-[3.3rem]">
            {title}
          </h2>
          <p className="mt-5 max-w-3xl text-base leading-8 text-muted">{description}</p>
        </div>
        {actions ? <div className="shrink-0">{actions}</div> : null}
      </motion.div>
      {children}
    </section>
  )
}
