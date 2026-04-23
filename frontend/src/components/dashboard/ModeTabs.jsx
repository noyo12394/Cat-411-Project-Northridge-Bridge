export default function ModeTabs({ modes, activeMode, onChange }) {
  return (
    <div className="grid gap-3 md:grid-cols-3">
      {modes.map((mode) => {
        const active = mode.id === activeMode
        return (
          <button
            key={mode.id}
            type="button"
            onClick={() => onChange(mode.id)}
            className={`rounded-[24px] border px-5 py-4 text-left transition ${
              active
                ? 'border-slate-900 bg-[linear-gradient(180deg,#0f172a_0%,#111827_100%)] text-white shadow-[0_18px_40px_rgba(15,23,42,0.24)]'
                : 'border-slate-200/90 bg-[linear-gradient(180deg,rgba(255,255,255,0.96)_0%,rgba(247,250,255,0.96)_100%)] text-slate-800 shadow-[0_12px_30px_rgba(15,23,42,0.06)] hover:border-slate-300'
            }`}
          >
            <p className={`font-mono text-[11px] uppercase tracking-[0.28em] ${active ? 'text-blue-100' : 'text-slate-600'}`}>
              {mode.eyebrow}
            </p>
            <h3 className="mt-2 text-base font-semibold tracking-[-0.02em]">{mode.label}</h3>
            <p className={`mt-2 text-sm leading-6 ${active ? 'text-slate-200' : 'text-slate-700'}`}>
              {mode.description}
            </p>
          </button>
        )
      })}
    </div>
  )
}
