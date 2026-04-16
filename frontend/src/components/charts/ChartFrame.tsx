import type { PropsWithChildren, ReactNode } from 'react'

interface ChartFrameProps extends PropsWithChildren {
  title: string
  description: string
  aside?: ReactNode
  className?: string
}

export function ChartFrame({
  title,
  description,
  aside,
  className = '',
  children,
}: ChartFrameProps) {
  return (
    <div className={`rounded-[2rem] border border-line bg-white/5 p-5 ${className}`}>
      <div className="mb-5 flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
        <div className="max-w-2xl">
          <h3 className="font-display text-xl font-semibold tracking-[-0.04em] text-ink">{title}</h3>
          <p className="mt-2 text-sm leading-6 text-muted">{description}</p>
        </div>
        {aside ? <div className="shrink-0">{aside}</div> : null}
      </div>
      {children}
    </div>
  )
}
