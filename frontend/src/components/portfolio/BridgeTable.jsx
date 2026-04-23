function formatFixed(value, digits = 3, fallback = 'n/a') {
  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric.toFixed(digits) : fallback
}

export default function BridgeTable({ bridges, selectedBridge, onSelect }) {
  const normalizedBridges = Array.isArray(bridges) ? bridges : bridges?.bridges ?? []
  const rows = normalizedBridges.slice(0, 12)

  return (
    <div className="rounded-[32px] border border-slate-200/90 bg-[linear-gradient(180deg,rgba(255,255,255,0.98)_0%,rgba(247,250,255,0.98)_100%)] p-5 shadow-[0_28px_70px_rgba(15,23,42,0.09)]">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="paper-eyebrow">Searchable bridge table</p>
          <h3 className="mt-2 text-xl font-semibold tracking-[-0.03em] text-slate-900">Filtered portfolio rows</h3>
        </div>
        <div className="text-sm text-slate-600">Showing {rows.length} of {normalizedBridges.length.toLocaleString()}</div>
      </div>

      <div className="mt-5 overflow-x-auto">
        <table className="min-w-full border-separate border-spacing-y-2">
          <thead>
            <tr className="text-left text-[11px] uppercase tracking-[0.22em] text-slate-600">
              <th className="px-3 py-2">Bridge</th>
              <th className="px-3 py-2">County</th>
              <th className="px-3 py-2">Class</th>
              <th className="px-3 py-2">SVI</th>
              <th className="px-3 py-2">Score</th>
              <th className="px-3 py-2">Priority</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((bridge) => {
              const selected = selectedBridge?.structureNumber === bridge.structureNumber
              return (
                <tr
                  key={bridge.structureNumber}
                  onClick={() => onSelect?.(bridge)}
                  className={`cursor-pointer rounded-[20px] text-sm transition ${selected ? 'bg-blue-50 shadow-[0_14px_30px_rgba(59,130,246,0.12)]' : 'bg-slate-50/85 hover:bg-slate-100/80'}`}
                >
                  <td className="rounded-l-[18px] px-3 py-3 font-semibold text-slate-950">{bridge.structureNumber}</td>
                  <td className="px-3 py-3 text-slate-700">{bridge.countyLabel}</td>
                  <td className="px-3 py-3 text-slate-700">{bridge.bridgeClass}</td>
                  <td className="px-3 py-3 text-slate-700">{formatFixed(bridge.svi)}</td>
                  <td className="px-3 py-3 font-medium text-slate-900">{formatFixed(bridge.prototypeVulnerability)}</td>
                  <td className="rounded-r-[18px] px-3 py-3 font-medium text-slate-900">{formatFixed(bridge.priorityScore)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
