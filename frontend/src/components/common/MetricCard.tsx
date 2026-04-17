interface MetricCardProps {
  label: string
  value: string
  detail?: string
  accent?: 'seismic' | 'signal' | 'moss' | 'hazard'
}

const accentMap: Record<NonNullable<MetricCardProps['accent']>, string> = {
  seismic: 'from-seismic/18 to-ocean/6',
  signal: 'from-signal/22 to-transparent',
  moss: 'from-moss/18 to-transparent',
  hazard: 'from-hazard/18 to-transparent',
}

export function MetricCard({
  label,
  value,
  detail,
  accent = 'seismic',
}: MetricCardProps) {
  return (
    <div className="relative overflow-hidden rounded-[1.75rem] border border-line bg-white/5 p-5">
      <div className={`pointer-events-none absolute inset-0 bg-gradient-to-br ${accentMap[accent]} opacity-90`} />
      <div className="relative">
        <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-muted">{label}</p>
        <p className="mt-4 font-display text-3xl font-semibold tracking-[-0.05em] text-ink">
          {value}
        </p>
        {detail ? <p className="mt-3 text-sm leading-6 text-muted">{detail}</p> : null}
      </div>
    </div>
  )
}
