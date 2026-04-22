function DetailPill({ label, value }) {
  return (
    <div className="rounded-[18px] border border-slate-200/80 bg-slate-50/80 px-3 py-3">
      <p className="text-[11px] uppercase tracking-[0.22em] text-slate-500">{label}</p>
      <p className="mt-2 text-sm font-semibold text-slate-950">{value}</p>
    </div>
  )
}

function ContributionRow({ label, value }) {
  return (
    <div>
      <div className="flex items-center justify-between gap-4 text-sm font-medium text-slate-700">
        <span>{label}</span>
        <span>{value.toFixed(2)}</span>
      </div>
      <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-200">
        <div className="h-full rounded-full bg-gradient-to-r from-blue-500 via-indigo-500 to-violet-500" style={{ width: `${Math.min(100, value * 100)}%` }} />
      </div>
    </div>
  )
}

function safeNumber(value, fallback = 0) {
  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric : fallback
}

function formatFixed(value, digits = 3, fallback = 'n/a') {
  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric.toFixed(digits) : fallback
}

export default function BridgeDetailCard({ bridge, onLoadBridge }) {
  if (!bridge) {
    return null
  }

  const latitude = Number(bridge.latitude)
  const longitude = Number(bridge.longitude)
  const coordinates =
    Number.isFinite(latitude) && Number.isFinite(longitude)
      ? `${latitude.toFixed(2)}, ${longitude.toFixed(2)}`
      : 'Coordinates unavailable'

  return (
    <div className="rounded-[32px] border border-slate-200/70 bg-[linear-gradient(180deg,rgba(255,255,255,0.96)_0%,rgba(247,249,253,0.96)_100%)] p-6 shadow-[0_28px_70px_rgba(15,23,42,0.08)]">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-500">Bridge detail</p>
          <h3 className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-950">{bridge.structureNumber}</h3>
          <p className="mt-2 text-sm leading-6 text-slate-600">{bridge.countyLabel} · {bridge.bridgeClass} · risk band {bridge.riskBand}</p>
        </div>
        <button
          type="button"
          onClick={() => onLoadBridge?.(bridge)}
          className="inline-flex rounded-full bg-slate-950 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-slate-900/20 transition hover:-translate-y-0.5"
        >
          Load into dashboard
        </button>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <DetailPill label="Prototype score" value={formatFixed(bridge.prototypeVulnerability)} />
        <DetailPill label="Priority score" value={formatFixed(bridge.priorityScore)} />
        <DetailPill label="SVI" value={formatFixed(bridge.svi)} />
        <DetailPill label="Repo EDR" value={formatFixed(bridge.edr)} />
        <DetailPill label="Condition" value={bridge.condition ?? 'n/a'} />
        <DetailPill label="ADT" value={bridge.adt ? Number(bridge.adt).toLocaleString() : 'n/a'} />
        <DetailPill label="Spans" value={bridge.spans ?? 'n/a'} />
        <DetailPill label="Max span" value={Number.isFinite(Number(bridge.maxSpanFt)) ? `${Number(bridge.maxSpanFt).toFixed(1)} ft` : 'n/a'} />
      </div>

      <div className="mt-6 grid gap-5 lg:grid-cols-[0.92fr_1.08fr]">
        <div className="rounded-[24px] border border-slate-200 bg-white/85 p-5">
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-500">Why this bridge scores high</p>
          <div className="mt-4 space-y-4">
            <ContributionRow label="Condition component" value={safeNumber(bridge.componentCondition)} />
            <ContributionRow label="SVI component" value={safeNumber(bridge.componentSVI)} />
            <ContributionRow label="Age / design era" value={safeNumber(bridge.componentAge)} />
            <ContributionRow label="Reconstruction timing" value={safeNumber(bridge.componentRehab)} />
            <ContributionRow label="Skew" value={safeNumber(bridge.componentSkew)} />
            <ContributionRow label="Max span" value={safeNumber(bridge.componentMaxSpan)} />
            <ContributionRow label="Bridge class" value={safeNumber(bridge.componentBridgeClass)} />
            <ContributionRow label="Span count" value={safeNumber(bridge.componentSpans)} />
          </div>
        </div>

        <div className="rounded-[24px] border border-slate-900/10 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.14),transparent_28%),linear-gradient(180deg,#0f172a_0%,#111827_100%)] p-5 text-slate-200 shadow-[0_20px_50px_rgba(15,23,42,0.18)]">
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-400">Narrative interpretation</p>
          <h4 className="mt-3 text-xl font-semibold text-white">Bridge-specific story</h4>
          <p className="mt-4 text-sm leading-7 text-slate-300">
            This bridge ranks where it does because the prototype engine combines its condition, SVI, age, geometry, and bridge class into one intrinsic screening score. Traffic appears only in the downstream priority score, which is why a high-ADT bridge can move up in urgency without changing its structural vulnerability logic.
          </p>
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            <DetailPill label="Inspection tier" value={bridge.inspectionTier ?? 'n/a'} />
            <DetailPill label="Coordinates" value={coordinates} />
          </div>
        </div>
      </div>
    </div>
  )
}
