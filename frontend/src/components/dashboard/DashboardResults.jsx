import BridgeStateVisual from '../visuals/BridgeStateVisual'

function StatCard({ label, value, hint, accent = 'slate' }) {
  const accentClasses = {
    slate: 'border-slate-200/80 bg-white',
    blue: 'border-blue-200/80 bg-blue-50/70',
    violet: 'border-violet-200/80 bg-violet-50/70',
    amber: 'border-amber-200/80 bg-amber-50/70',
  }

  return (
    <div className={`rounded-[24px] border p-4 shadow-sm ${accentClasses[accent]}`}>
      <p className="text-xs uppercase tracking-[0.24em] text-slate-500">{label}</p>
      <div className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-950">{value}</div>
      {hint ? <p className="mt-2 text-sm leading-6 text-slate-600">{hint}</p> : null}
    </div>
  )
}

export default function DashboardResults({ result, modeMeta, replayToken = 0 }) {
  return (
    <div className="space-y-5">
      <div className="rounded-[30px] border border-white/80 bg-white/92 p-6 shadow-[0_18px_50px_rgba(15,23,42,0.08)] backdrop-blur">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-500">Output panel</p>
            <h3 className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-950">{modeMeta.label}</h3>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">{result.narrative}</p>
          </div>
          <div className="rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm font-medium text-slate-600">{result.scenarioTag}</div>
        </div>
        <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          <StatCard label="Predicted Vulnerability Score" value={result.vulnerabilityScore.toFixed(3)} hint="0 to 1 screening scale" accent="blue" />
          <StatCard label="Damage Category" value={result.damageCategory} hint="Displayed as a screening-tier interpretation" accent="violet" />
          <StatCard label="Risk Level" value={result.riskLevel} hint="Portfolio band used for dashboard communication" accent="amber" />
          <StatCard label="Inspection Priority Rank" value={result.inspectionPriorityRank} hint="Consequence-aware ranking output" />
          <StatCard label="Confidence Indicator" value={result.confidenceLabel} hint={`Confidence score ${result.confidence.toFixed(2)}`} />
          <StatCard label="Traffic / Economic Disruption" value={result.trafficIndicator.label} hint="ADT changes this layer without changing baseline vulnerability" />
        </div>
      </div>

      <BridgeStateVisual
        score={result.vulnerabilityScore}
        visualState={result.visualState}
        replayToken={replayToken}
        title={`${modeMeta.label} structural signal`}
        caption={result.visualState?.summary}
      />

      <div className="grid gap-5 xl:grid-cols-[1.25fr_0.75fr]">
        <div className="rounded-[30px] border border-white/80 bg-white/92 p-6 shadow-[0_18px_50px_rgba(15,23,42,0.08)] backdrop-blur">
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-500">Interpretability</p>
          <h3 className="mt-2 text-xl font-semibold tracking-[-0.03em] text-slate-950">Top contributing features</h3>
          <div className="mt-5 space-y-3">
            {result.topContributors.map((item) => (
              <div key={item.label} className="rounded-[22px] border border-slate-200/80 bg-slate-50/80 p-4">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <h4 className="font-semibold text-slate-900">{item.label}</h4>
                    <p className="mt-1 text-sm leading-6 text-slate-600">{item.narrative}</p>
                  </div>
                  <div className="rounded-full bg-white px-3 py-1 text-sm font-semibold text-slate-700 shadow-sm">{item.value.toFixed(3)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-5">
          <div className="rounded-[30px] border border-white/80 bg-white/92 p-6 shadow-[0_18px_50px_rgba(15,23,42,0.08)] backdrop-blur">
            <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-500">NDVI adjustment card</p>
            <h3 className="mt-2 text-xl font-semibold tracking-[-0.03em] text-slate-950">Post-event evidence status</h3>
            <p className="mt-3 text-sm leading-6 text-slate-600">{result.ndviAdjustment.narrative}</p>
            <div className="mt-4 rounded-[22px] border border-slate-200/80 bg-slate-50 p-4 text-sm text-slate-700">
              Adjustment shift: <span className="font-semibold">{result.ndviAdjustment.shift.toFixed(3)}</span>
            </div>
          </div>
          <div className="rounded-[30px] border border-white/80 bg-white/92 p-6 shadow-[0_18px_50px_rgba(15,23,42,0.08)] backdrop-blur">
            <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-500">Rule discipline</p>
            <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-600">
              <li>• Intrinsic mode excludes PGA from the core vulnerability score.</li>
              <li>• Event mode introduces PGA only as a scenario layer after screening.</li>
              <li>• ADT changes prioritization and disruption, not intrinsic vulnerability.</li>
              <li>• NDVI acts only as an optional post-event adjustment.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
