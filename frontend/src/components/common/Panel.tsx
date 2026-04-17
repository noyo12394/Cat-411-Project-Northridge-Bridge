import type { PropsWithChildren, ReactNode } from 'react'
import { motion } from 'framer-motion'
import { revealTransition } from '../../animations/motion'

interface PanelProps extends PropsWithChildren {
  className?: string
  eyebrow?: string
  title?: string
  description?: string
  aside?: ReactNode
}

export function Panel({
  children,
  className = '',
  eyebrow,
  title,
  description,
  aside,
}: PanelProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={revealTransition}
      className={`relative overflow-hidden rounded-5xl border border-line bg-[linear-gradient(180deg,rgba(18,28,43,0.94),rgba(12,19,31,0.94))] shadow-float ${className}`}
    >
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(73,182,255,0.12),transparent_38%)] opacity-70" />
      {(eyebrow || title || description || aside) && (
        <div className="relative flex flex-col gap-4 border-b border-line/80 px-6 py-5 sm:px-8">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="max-w-3xl">
              {eyebrow ? (
                <p className="font-mono text-[11px] uppercase tracking-[0.34em] text-seismic/80">
                  {eyebrow}
                </p>
              ) : null}
              {title ? (
                <h3 className="mt-3 font-display text-2xl font-semibold tracking-[-0.04em] text-ink">
                  {title}
                </h3>
              ) : null}
              {description ? (
                <p className="mt-3 max-w-3xl text-sm leading-7 text-muted">{description}</p>
              ) : null}
            </div>
            {aside ? <div className="shrink-0">{aside}</div> : null}
          </div>
        </div>
      )}
      <div className="relative px-6 py-6 sm:px-8">{children}</div>
    </motion.div>
  )
}
