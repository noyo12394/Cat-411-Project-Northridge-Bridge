const METRICS = [
  { key: 'prototypeVulnerability', label: 'Intrinsic vulnerability' },
  { key: 'priorityScore', label: 'Priority score' },
  { key: 'edr', label: 'Repo EDR' },
]

export default function BridgeRankingList({ bridges, metric, onMetricChange, selectedBridge, onSelect }) {
  const topRows = [...bridges]
    .sort((a, b) => Number(b[metric] ?? 0) - Number(a[metric] ?? 0))
    .slice(0, 8)

  return (
    <div className="rounded-[32px] border border-slate-200/70 bg-white/95 p-5 shadow-[0_28px_70px_rgba(15,23,42,0.08)]">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-500">Ranked bridge list</p>
          <h3 className="mt-2 text-xl font-semibold tracking-[-0.03em] text-slate-950">Top bridges under the current filter</h3>
        </div>
        <div className="inline-flex rounded-full border border-slate-200 bg-slate-50 p-1">
          {METRICS.map((item) => (
            <button
              key={item.key}
              type="button"
              onClick={() => onMetricChange(item.key)}
              className={`rounded-full px-3 py-2 text-sm font-medium transition ${metric === item.key ? 'bg-slate-950 text-white shadow-lg shadow-slate-900/15' : 'text-slate-600 hover:text-slate-950'}`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-5 space-y-3">
        {topRows.map((bridge, index) => {
          const selected = selectedBridge?.structureNumber === bridge.structureNumber
          return (
            <button
              key={bridge.structureNumber}
              type="button"
              onClick={() => onSelect?.(bridge)}
              className={`flex w-full items-center justify-between rounded-[22px] border px-4 py-4 text-left transition ${selected ? 'border-blue-300 bg-blue-50/80 shadow-[0_14px_30px_rgba(59,130,246,0.12)]' : 'border-slate-200 bg-slate-50/80 hover:border-slate-300 hover:bg-white'}`}
            >
              <div className="flex items-start gap-4">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-slate-950 text-sm font-semibold text-white">{index + 1}</div>
                <div>
                  <h4 className="font-semibold text-slate-950">{bridge.structureNumber}</h4>
                  <p className="mt-1 text-sm text-slate-600">{bridge.countyLabel} · {bridge.bridgeClass} · Built {bridge.yearBuilt}</p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-xl font-semibold tracking-[-0.03em] text-slate-950">{Number(bridge[metric] ?? 0).toFixed(3)}</div>
                <p className="mt-1 text-xs uppercase tracking-[0.22em] text-slate-500">{metric}</p>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
