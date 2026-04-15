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
                ? 'border-slate-900 bg-slate-950 text-white shadow-[0_18px_40px_rgba(15,23,42,0.24)]'
                : 'border-slate-200/80 bg-white/85 text-slate-700 hover:border-slate-300 hover:bg-white'
            }`}
          >
            <p className={`font-mono text-[11px] uppercase tracking-[0.28em] ${active ? 'text-blue-200' : 'text-slate-400'}`}>
              {mode.eyebrow}
            </p>
            <h3 className="mt-2 text-base font-semibold tracking-[-0.02em]">{mode.label}</h3>
            <p className={`mt-2 text-sm leading-6 ${active ? 'text-slate-300' : 'text-slate-600'}`}>
              {mode.description}
            </p>
          </button>
        )
      })}
    </div>
  )
}
