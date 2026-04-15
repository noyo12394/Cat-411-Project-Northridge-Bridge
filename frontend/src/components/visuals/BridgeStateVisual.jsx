function DeckSegment({ x, y, width, rotation, opacity }) {
  return (
    <rect
      x={x}
      y={y}
      width={width}
      height="22"
      rx="10"
      transform={`rotate(${rotation} ${x + width / 2} ${y + 11})`}
      fill={`rgba(15, 23, 42, ${opacity})`}
    />
  )
}

export default function BridgeStateVisual({ score = 0.4, visualState, title = 'Structural state visual' }) {
  const state = visualState ?? {
    sag: 8,
    crack: score,
    supportShift: score * 10,
    deckFracture: score > 0.65,
  }

  const deckY = 132 + state.sag
  const crackOpacity = Math.min(1, state.crack)
  const shift = state.supportShift

  return (
    <div className="relative overflow-hidden rounded-[30px] border border-white/70 bg-[radial-gradient(circle_at_top,rgba(96,165,250,0.18),transparent_28%),linear-gradient(180deg,#f8fbff_0%,#eef4ff_100%)] p-6 shadow-[0_24px_70px_rgba(15,23,42,0.12)]">
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(90deg,rgba(59,130,246,0.08)_1px,transparent_1px),linear-gradient(rgba(59,130,246,0.08)_1px,transparent_1px)] bg-[size:28px_28px] opacity-30" />
      <div className="relative flex items-start justify-between gap-6">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.32em] text-slate-500">Live structural state</p>
          <h3 className="mt-2 text-xl font-semibold tracking-[-0.03em] text-slate-950">{title}</h3>
          <p className="mt-2 max-w-sm text-sm leading-6 text-slate-600">
            The bridge reacts to the current dashboard score through subtle deck sag, support misalignment, and crack intensity. It is an explanatory visualization, not a finite-element simulation.
          </p>
        </div>
        <div className="rounded-full border border-slate-200/80 bg-white/80 px-4 py-2 text-sm font-medium text-slate-700">
          Score {score.toFixed(2)}
        </div>
      </div>
      <svg viewBox="0 0 760 360" className="relative mt-8 w-full overflow-visible">
        <defs>
          <linearGradient id="deckGradient" x1="0%" x2="100%">
            <stop offset="0%" stopColor="#0f172a" />
            <stop offset="55%" stopColor="#1e3a8a" />
            <stop offset="100%" stopColor="#4338ca" />
          </linearGradient>
          <linearGradient id="supportGradient" x1="0%" x2="0%" y1="0%" y2="100%">
            <stop offset="0%" stopColor="#dbeafe" />
            <stop offset="100%" stopColor="#94a3b8" />
          </linearGradient>
        </defs>

        <path
          d={`M70 ${deckY} C190 ${deckY - 48}, 285 ${deckY - 48}, 380 ${deckY} S570 ${deckY + 48}, 690 ${deckY}`}
          fill="none"
          stroke="rgba(59, 130, 246, 0.22)"
          strokeWidth="8"
          strokeLinecap="round"
        />

        <g>
          <DeckSegment x={90} y={deckY - 14} width={170} rotation={-shift * 0.18} opacity={0.92} />
          <DeckSegment x={245} y={deckY - 18} width={160} rotation={shift * 0.12} opacity={0.96} />
          <DeckSegment x={395} y={deckY - 12} width={170} rotation={-shift * 0.08} opacity={0.9} />
          <DeckSegment x={550} y={deckY - 10} width={120} rotation={shift * 0.16} opacity={0.88} />
          <path
            d={`M88 ${deckY + 2} H668`}
            stroke="url(#deckGradient)"
            strokeWidth="18"
            strokeLinecap="round"
            opacity="0.95"
          />
        </g>

        <g opacity="0.95">
          {[
            { x: 150, y: deckY + 12, w: 26, h: 150, tilt: shift * 0.08 },
            { x: 288, y: deckY + 12, w: 30, h: 180, tilt: -shift * 0.06 },
            { x: 460, y: deckY + 12, w: 28, h: 170, tilt: shift * 0.09 },
            { x: 598, y: deckY + 12, w: 24, h: 145, tilt: -shift * 0.05 },
          ].map((pier, index) => (
            <rect
              key={pier.x}
              x={pier.x}
              y={pier.y}
              width={pier.w}
              height={pier.h}
              rx="12"
              transform={`rotate(${pier.tilt} ${pier.x + pier.w / 2} ${pier.y + pier.h / 2})`}
              fill="url(#supportGradient)"
              stroke="rgba(148, 163, 184, 0.55)"
              strokeWidth="2"
              opacity={0.92 - index * 0.05}
            />
          ))}
        </g>

        <g opacity="0.3">
          <path d={`M150 80 L162 ${deckY - 6}`} stroke="#60a5fa" strokeWidth="3" />
          <path d={`M288 54 L300 ${deckY - 10}`} stroke="#60a5fa" strokeWidth="3" />
          <path d={`M460 48 L474 ${deckY - 4}`} stroke="#60a5fa" strokeWidth="3" />
          <path d={`M598 72 L612 ${deckY - 1}`} stroke="#60a5fa" strokeWidth="3" />
        </g>

        {state.deckFracture ? (
          <g opacity={crackOpacity}>
            <path d={`M373 ${deckY - 24} L364 ${deckY - 2} L378 ${deckY + 9} L369 ${deckY + 30}`} stroke="#f97316" strokeWidth="5" strokeLinecap="round" />
            <path d={`M390 ${deckY - 16} L381 ${deckY + 4} L395 ${deckY + 20}`} stroke="#fb7185" strokeWidth="4" strokeLinecap="round" />
          </g>
        ) : (
          <path d={`M382 ${deckY - 15} L377 ${deckY + 8}`} stroke="#f97316" strokeWidth="3" strokeLinecap="round" opacity={crackOpacity * 0.35} />
        )}

        <ellipse cx="380" cy="318" rx="286" ry="18" fill="rgba(15,23,42,0.08)" />
      </svg>
    </div>
  )
}
