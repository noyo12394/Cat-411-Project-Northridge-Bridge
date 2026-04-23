const CALIFORNIA_PATH = 'M88 26 L134 18 L168 38 L186 86 L205 134 L238 187 L245 242 L263 289 L273 342 L300 385 L322 434 L334 475 L319 506 L285 515 L257 502 L235 476 L214 452 L186 430 L167 404 L149 366 L130 334 L112 296 L98 262 L86 228 L73 196 L56 160 L50 122 L58 88 L74 60 Z'

function riskColor(band) {
  const colors = {
    Low: '#cbd5f5',
    Guarded: '#7dd3fc',
    Elevated: '#60a5fa',
    High: '#6366f1',
    Critical: '#a855f7',
  }
  return colors[band] ?? '#94a3b8'
}

function projectPoint(bridge) {
  const longitude = Number(bridge.longitude)
  const latitude = Number(bridge.latitude)
  const x = 52 + ((longitude + 124.7) / 10.8) * 290
  const y = 518 - ((latitude - 32.3) / 9.9) * 470
  return { x, y }
}

export default function PortfolioMap({ bridges, selectedBridge, onSelect }) {
  const plotted = bridges.slice(0, 900)

  return (
    <div className="rounded-[32px] border border-slate-200/90 bg-[linear-gradient(180deg,rgba(255,255,255,0.98)_0%,rgba(242,247,255,0.96)_100%)] p-5 shadow-[0_28px_70px_rgba(15,23,42,0.09)]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="paper-eyebrow">Map view</p>
          <h3 className="mt-2 text-xl font-semibold tracking-[-0.03em] text-slate-900">California bridge portfolio</h3>
          <p className="mt-2 max-w-xl text-sm leading-6 text-slate-700">
            Real bridge locations from the processed statewide bridge file. Point color follows the prototype intrinsic vulnerability band, not PGA.
          </p>
        </div>
        <div className="paper-chip">
          {bridges.length.toLocaleString()} filtered bridges
        </div>
      </div>

      <div className="mt-5 overflow-hidden rounded-[28px] border border-slate-200/80 bg-[radial-gradient(circle_at_top_left,rgba(56,189,248,0.18),transparent_26%),linear-gradient(180deg,#f8fbff_0%,#eef4ff_100%)] p-4">
        <svg viewBox="0 0 380 540" className="h-[420px] w-full">
          <defs>
            <linearGradient id="caGlow" x1="0%" x2="100%" y1="0%" y2="100%">
              <stop offset="0%" stopColor="rgba(59,130,246,0.22)" />
              <stop offset="100%" stopColor="rgba(99,102,241,0.08)" />
            </linearGradient>
          </defs>
          <rect x="0" y="0" width="380" height="540" rx="22" fill="transparent" />
          {[0, 1, 2, 3, 4, 5].map((line) => (
            <line key={`h-${line}`} x1="24" y1={60 + line * 76} x2="356" y2={60 + line * 76} stroke="rgba(148,163,184,0.18)" strokeDasharray="4 8" />
          ))}
          {[0, 1, 2, 3].map((line) => (
            <line key={`v-${line}`} x1={88 + line * 72} y1="30" x2={88 + line * 72} y2="510" stroke="rgba(148,163,184,0.12)" strokeDasharray="4 8" />
          ))}
          <path d={CALIFORNIA_PATH} fill="url(#caGlow)" stroke="rgba(30,41,59,0.4)" strokeWidth="2.5" />

          {plotted.map((bridge) => {
            const point = projectPoint(bridge)
            const selected = selectedBridge?.structureNumber === bridge.structureNumber
            return (
              <g key={bridge.structureNumber} onClick={() => onSelect?.(bridge)} className="cursor-pointer">
                {selected ? <circle cx={point.x} cy={point.y} r="7" fill="rgba(99,102,241,0.16)" /> : null}
                <circle cx={point.x} cy={point.y} r={selected ? 4.5 : 2.5} fill={riskColor(bridge.riskBand)} opacity={selected ? 1 : 0.72} />
              </g>
            )
          })}
        </svg>
      </div>

      <div className="mt-4 flex flex-wrap gap-3 text-xs font-medium text-slate-700">
        {['Low', 'Guarded', 'Elevated', 'High', 'Critical'].map((band) => (
          <div key={band} className="inline-flex items-center gap-2 rounded-full border border-slate-200/90 bg-white/95 px-3 py-1.5">
            <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: riskColor(band) }} />
            {band}
          </div>
        ))}
      </div>
    </div>
  )
}
