export default function InsightCard({ eyebrow, title, description, children, tone = 'default', className = '' }) {
  const toneClasses = {
    default: 'border-slate-200/90 bg-[linear-gradient(180deg,rgba(255,255,255,0.98)_0%,rgba(247,250,255,0.98)_100%)]',
    accent: 'border-blue-200/90 bg-[linear-gradient(180deg,rgba(239,246,255,0.98)_0%,rgba(232,242,255,0.98)_100%)]',
    dark: 'border-slate-700/50 bg-[linear-gradient(180deg,#111c2c_0%,#0d1624_100%)] text-white',
  }

  return (
    <div
      className={`rounded-[28px] border p-6 shadow-[0_18px_50px_rgba(15,23,42,0.08)] backdrop-blur ${toneClasses[tone]} ${className}`}
    >
      {eyebrow ? (
        <p className={`font-mono text-[11px] uppercase tracking-[0.28em] ${tone === 'dark' ? 'text-blue-100' : 'text-slate-600'}`}>
          {eyebrow}
        </p>
      ) : null}
      <div className="mt-3 space-y-3">
        <h3 className={`text-xl font-semibold tracking-[-0.03em] ${tone === 'dark' ? 'text-white' : 'text-slate-900'}`}>
          {title}
        </h3>
        {description ? (
          <p className={`text-sm leading-6 ${tone === 'dark' ? 'text-slate-200' : 'text-slate-700'}`}>
            {description}
          </p>
        ) : null}
      </div>
      {children ? <div className="mt-5">{children}</div> : null}
    </div>
  )
}
