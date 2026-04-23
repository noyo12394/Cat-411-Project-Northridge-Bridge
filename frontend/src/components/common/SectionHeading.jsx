export default function SectionHeading({
  eyebrow,
  title,
  description,
  align = 'left',
  actions,
  theme = 'canvas',
}) {
  const isPaper = theme === 'paper'

  return (
    <div className={`flex flex-col gap-5 ${align === 'center' ? 'items-center text-center' : ''}`}>
      {eyebrow ? (
        <span
          className={`inline-flex w-fit max-w-full items-center rounded-full px-4 py-2 font-mono text-[11px] uppercase tracking-[0.28em] shadow-sm backdrop-blur ${
            isPaper
              ? 'border border-slate-200/90 bg-white/88 text-slate-600'
              : 'border border-white/12 bg-white/5 text-slate-300'
          }`}
        >
          {eyebrow}
        </span>
      ) : null}
      <div className="space-y-4">
        <h2
          className={`max-w-4xl font-display text-[clamp(2.15rem,4vw,3.2rem)] font-semibold leading-[1.02] tracking-[-0.05em] ${
            isPaper ? 'text-slate-900' : 'text-slate-50'
          }`}
        >
          {title}
        </h2>
        {description ? (
          <p
            className={`max-w-3xl text-[clamp(1rem,1.35vw,1.12rem)] leading-8 ${
              isPaper ? 'text-slate-700' : 'text-slate-300'
            }`}
          >
            {description}
          </p>
        ) : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-3">{actions}</div> : null}
    </div>
  )
}
