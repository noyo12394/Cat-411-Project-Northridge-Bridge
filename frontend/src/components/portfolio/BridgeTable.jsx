export default function BridgeTable({ bridges, selectedBridge, onSelect }) {
  const rows = bridges.slice(0, 12)

  return (
    <div className="rounded-[32px] border border-slate-200/70 bg-white/95 p-5 shadow-[0_28px_70px_rgba(15,23,42,0.08)]">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-500">Searchable bridge table</p>
          <h3 className="mt-2 text-xl font-semibold tracking-[-0.03em] text-slate-950">Filtered portfolio rows</h3>
        </div>
        <div className="text-sm text-slate-500">Showing {rows.length} of {bridges.length.toLocaleString()}</div>
      </div>

      <div className="mt-5 overflow-x-auto">
        <table className="min-w-full border-separate border-spacing-y-2">
          <thead>
            <tr className="text-left text-[11px] uppercase tracking-[0.22em] text-slate-500">
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
                  <td className="px-3 py-3 text-slate-600">{bridge.countyLabel}</td>
                  <td className="px-3 py-3 text-slate-600">{bridge.bridgeClass}</td>
                  <td className="px-3 py-3 text-slate-600">{bridge.svi.toFixed(3)}</td>
                  <td className="px-3 py-3 font-medium text-slate-900">{bridge.prototypeVulnerability.toFixed(3)}</td>
                  <td className="rounded-r-[18px] px-3 py-3 font-medium text-slate-900">{bridge.priorityScore.toFixed(3)}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
