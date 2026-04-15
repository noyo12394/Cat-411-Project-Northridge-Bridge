export default function InsightCard({ eyebrow, title, description, children, tone = 'default', className = '' }) {
  const toneClasses = {
    default: 'border-white/80 bg-white/90',
    accent: 'border-blue-200/80 bg-blue-50/80',
    dark: 'border-slate-800/60 bg-slate-950 text-white',
  }

  return (
    <div
      className={`rounded-[28px] border p-6 shadow-[0_18px_50px_rgba(15,23,42,0.08)] backdrop-blur ${toneClasses[tone]} ${className}`}
    >
      {eyebrow ? (
        <p className={`font-mono text-[11px] uppercase tracking-[0.28em] ${tone === 'dark' ? 'text-blue-200' : 'text-slate-500'}`}>
          {eyebrow}
        </p>
      ) : null}
      <div className="mt-3 space-y-3">
        <h3 className={`text-xl font-semibold tracking-[-0.03em] ${tone === 'dark' ? 'text-white' : 'text-slate-950'}`}>
          {title}
        </h3>
        {description ? (
          <p className={`text-sm leading-6 ${tone === 'dark' ? 'text-slate-300' : 'text-slate-600'}`}>
            {description}
          </p>
        ) : null}
      </div>
      {children ? <div className="mt-5">{children}</div> : null}
    </div>
  )
}
