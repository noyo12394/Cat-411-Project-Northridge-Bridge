import EnhancedBridgeVisualizer from '../visuals/EnhancedBridgeVisualizer'

function MetricCard({ label, value, hint, accent = 'slate' }) {
  const accentClasses = {
    slate: 'border-slate-200/90 bg-white/96 text-slate-900',
    blue: 'border-blue-200/90 bg-blue-50/95 text-blue-950',
    violet: 'border-violet-200/90 bg-violet-50/95 text-violet-950',
    amber: 'border-amber-200/90 bg-amber-50/95 text-amber-950',
  }

  return (
    <div className={`rounded-[22px] border p-4 shadow-sm ${accentClasses[accent]}`}>
      <p className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-600">{label}</p>
      <div className="mt-2 text-2xl font-semibold tracking-[-0.04em]">{value}</div>
      {hint ? <p className="mt-2 text-sm leading-6 text-slate-700">{hint}</p> : null}
    </div>
  )
}

function ContributorRow({ item }) {
  return (
    <div className="rounded-[20px] border border-slate-200/90 bg-white/90 p-4 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h4 className="text-base font-semibold text-slate-900">{item.label}</h4>
          <p className="mt-1 text-sm leading-6 text-slate-700">{item.narrative}</p>
        </div>
        <div className="rounded-full bg-slate-950 px-3 py-1 text-sm font-semibold text-white shadow-sm">
          {item.value.toFixed(3)}
        </div>
      </div>
    </div>
  )
}

function LogicChip({ children }) {
  return (
    <div className="rounded-full border border-slate-200/90 bg-white/95 px-4 py-2 text-sm font-medium text-slate-700 shadow-sm">
      {children}
    </div>
  )
}

export default function DashboardResults({ result, modeMeta, inputs }) {
  const eventPga = modeMeta.id === 'event' ? Number(inputs?.scenarioPga || 0) : undefined
  const svi = Number(inputs?.svi)

  return (
    <div className="space-y-5">
      <div className="paper-panel rounded-[30px] p-6">
        <div className="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
          <div className="max-w-3xl">
            <p className="paper-eyebrow">Output panel</p>
            <h3 className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-900">
              {modeMeta.label}
            </h3>
            <p className="mt-3 paper-copy">{result.narrative}</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <LogicChip>{result.scenarioTag}</LogicChip>
            <LogicChip>{result.visualState?.stageHeading ?? 'Live structural state'}</LogicChip>
          </div>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          <MetricCard
            label="Predicted Vulnerability Score"
            value={result.vulnerabilityScore.toFixed(3)}
            hint="0 to 1 screening scale"
            accent="blue"
          />
          <MetricCard
            label="Damage Category"
            value={result.damageCategory}
            hint="Displayed as a screening-tier interpretation"
            accent="violet"
          />
          <MetricCard
            label="Risk Level"
            value={result.riskLevel}
            hint="Portfolio band used for dashboard communication"
            accent="amber"
          />
          <MetricCard
            label="Inspection Priority Rank"
            value={result.inspectionPriorityRank}
            hint="Consequence-aware ranking output"
          />
          <MetricCard
            label="Confidence Indicator"
            value={result.confidenceLabel}
            hint={`Confidence score ${result.confidence.toFixed(2)}`}
          />
          <MetricCard
            label="Traffic / Economic Disruption"
            value={result.trafficIndicator.label}
            hint="ADT changes this layer without changing baseline vulnerability"
          />
        </div>
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.05fr_0.95fr]">
        <div className="paper-panel rounded-[30px] p-6">
          <div className="flex flex-col gap-4 border-b border-slate-200/90 pb-5 sm:flex-row sm:items-start sm:justify-between">
            <div className="max-w-2xl">
              <p className="paper-eyebrow">Live structural state</p>
              <h3 className="mt-2 text-xl font-semibold tracking-[-0.03em] text-slate-900">
                New bridge animation tied directly to the current dashboard state
              </h3>
              <p className="mt-3 paper-copy">
                This visual settles into a structural condition rather than wiggling in place. It reflects the current
                screening score and, in event mode, the added scenario demand layer.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <LogicChip>{modeMeta.label}</LogicChip>
              <LogicChip>{result.visualState?.stageLabel ?? result.riskLevel}</LogicChip>
            </div>
          </div>

          <div className="mt-5 overflow-hidden rounded-[28px] bg-[linear-gradient(180deg,#08111d_0%,#0b1625_100%)] p-4 shadow-[inset_0_0_0_1px_rgba(148,163,184,0.08)]">
            <EnhancedBridgeVisualizer
              vulnerability={result.vulnerabilityScore * 100}
              svi={Number.isFinite(svi) ? svi : undefined}
              pga={eventPga}
              showMetrics={false}
              showDamageBreakdown={false}
            />
          </div>

          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            <div className="rounded-[22px] border border-slate-200/90 bg-slate-50/92 p-4">
              <p className="paper-eyebrow">Structural reading</p>
              <p className="mt-2 text-lg font-semibold tracking-[-0.03em] text-slate-900">
                {result.visualState?.stageHeading ?? 'Stable structural state'}
              </p>
            </div>
            <div className="rounded-[22px] border border-slate-200/90 bg-slate-50/92 p-4">
              <p className="paper-eyebrow">SVI input</p>
              <p className="mt-2 text-lg font-semibold tracking-[-0.03em] text-slate-900">
                {Number.isFinite(svi) ? svi.toFixed(3) : 'Not set'}
              </p>
            </div>
            <div className="rounded-[22px] border border-slate-200/90 bg-slate-50/92 p-4">
              <p className="paper-eyebrow">Scenario PGA</p>
              <p className="mt-2 text-lg font-semibold tracking-[-0.03em] text-slate-900">
                {typeof eventPga === 'number' ? `${eventPga.toFixed(2)} g` : 'Intrinsic mode'}
              </p>
            </div>
          </div>
        </div>

        <div className="space-y-5">
          <div className="paper-panel rounded-[30px] p-6">
            <p className="paper-eyebrow">Interpretability / explainable AI</p>
            <h3 className="mt-2 text-xl font-semibold tracking-[-0.03em] text-slate-900">
              Top contributing features for this bridge state
            </h3>
            <p className="mt-3 paper-copy">
              This is the local explanation layer of the dashboard. It summarizes why the current bridge state moved
              the way it did, while the analytics section carries the repo-backed global XAI figures.
            </p>
            <div className="mt-5 space-y-3">
              {result.topContributors.map((item) => (
                <ContributorRow key={item.label} item={item} />
              ))}
            </div>
          </div>

          <div className="paper-panel rounded-[30px] p-6">
            <p className="paper-eyebrow">Decision logic</p>
            <h3 className="mt-2 text-xl font-semibold tracking-[-0.03em] text-slate-900">
              What changed the score, and what did not
            </h3>
            <div className="mt-4 space-y-4">
              <div className="rounded-[22px] border border-slate-200/90 bg-slate-50/92 p-4">
                <h4 className="font-semibold text-slate-900">NDVI adjustment card</h4>
                <p className="mt-2 text-sm leading-6 text-slate-700">{result.ndviAdjustment.narrative}</p>
                <p className="mt-3 text-sm font-semibold text-slate-900">
                  Adjustment shift: {result.ndviAdjustment.shift.toFixed(3)}
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <LogicChip>Intrinsic mode excludes PGA from the core vulnerability score.</LogicChip>
                <LogicChip>ADT changes prioritization and disruption, not intrinsic vulnerability.</LogicChip>
                <LogicChip>NDVI acts only as an optional post-event adjustment.</LogicChip>
                <LogicChip>Contribution chips are local explanations, not causal proof.</LogicChip>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
