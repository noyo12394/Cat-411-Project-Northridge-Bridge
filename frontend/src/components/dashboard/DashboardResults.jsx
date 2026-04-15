import SurfaceCard from '../common/SurfaceCard'

function MetricTile({ label, value, supporting, accentClass = 'text-ink' }) {
  return (
    <SurfaceCard className="h-full p-5">
      <p className="text-xs uppercase tracking-[0.18em] text-muted">{label}</p>
      <p className={`mt-3 font-display text-3xl font-semibold tracking-[-0.04em] ${accentClass}`}>{value}</p>
      <p className="mt-2 text-sm leading-6 text-muted">{supporting}</p>
    </SurfaceCard>
  )
}

export default function DashboardResults({ result }) {
  if (!result) {
    return (
      <div className="surface-card p-8">
        <p className="eyebrow">Output panel</p>
        <p className="mt-6 text-sm leading-7 text-muted">Run the dashboard once to generate a vulnerability interpretation.</p>
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <SurfaceCard className="overflow-hidden p-0">
        <div className="border-b border-white/10 bg-gradient-to-br from-ink via-[#173967] to-ocean px-6 py-6 text-white">
          <p className="eyebrow border-white/15 bg-white/10 text-white">Output panel</p>
          <div className="mt-5 flex flex-wrap items-end justify-between gap-4">
            <div>
              <p className="text-sm uppercase tracking-[0.18em] text-white/65">Predicted Vulnerability Score</p>
              <div className="mt-2 flex items-end gap-3">
                <span className="font-display text-6xl font-semibold tracking-[-0.05em]">
                  {result.vulnerabilityScore.toFixed(2)}
                </span>
                <span className={`rounded-full border px-3 py-1 text-sm font-medium ${result.riskLevel.chip}`}>
                  {result.riskLevel.label} risk
                </span>
              </div>
            </div>
            <div className="w-full max-w-[280px] rounded-[24px] border border-white/10 bg-white/8 p-4">
              <div className="flex items-center justify-between text-sm text-white/72">
                <span>Priority score</span>
                <span>{(result.priorityScore * 100).toFixed(0)} / 100</span>
              </div>
              <div className="mt-3 h-3 rounded-full bg-white/15">
                <div
                  className="h-3 rounded-full bg-gradient-to-r from-sky via-signal to-[#ff7b72]"
                  style={{ width: `${result.priorityScore * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        <div className="grid gap-4 p-6 md:grid-cols-2 xl:grid-cols-4">
          <MetricTile
            label="Estimated Damage Category"
            value={`${result.damageCategory.code}`}
            supporting={result.damageCategory.explanation}
            accentClass="text-ocean"
          />
          <MetricTile
            label="Bridge Risk Level"
            value={result.riskLevel.label}
            supporting="Qualitative tier derived from the intrinsic vulnerability score."
            accentClass={result.riskLevel.tone}
          />
          <MetricTile
            label="Inspection Priority Rank"
            value={`#${result.inspectionPriorityRank}`}
            supporting="Lower rank means higher priority once vulnerability and consequence are combined."
            accentClass="text-violet"
          />
          <MetricTile
            label="Confidence Indicator"
            value={`${result.confidence.score}%`}
            supporting={`${result.confidence.label} based on input completeness and model framing.`}
            accentClass="text-teal"
          />
        </div>
      </SurfaceCard>

      <div className="grid gap-5 xl:grid-cols-[1.05fr_0.95fr]">
        <SurfaceCard className="p-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="eyebrow">Interpretability</p>
              <h3 className="mt-4 font-display text-2xl font-semibold tracking-[-0.03em] text-ink">Top contributing features</h3>
            </div>
            <span className="rounded-full border border-slate-200 px-3 py-2 text-sm text-muted">Transparent mock logic</span>
          </div>
          <div className="mt-6 space-y-4">
            {result.topContributingFeatures.map((item) => (
              <div key={item.feature}>
                <div className="mb-2 flex items-center justify-between text-sm font-medium text-ink">
                  <span>{item.feature}</span>
                  <span>{item.contribution}%</span>
                </div>
                <div className="h-2 rounded-full bg-slate-100">
                  <div
                    className="h-2 rounded-full bg-gradient-to-r from-ocean via-sky to-violet"
                    style={{ width: `${Math.min(item.contribution, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </SurfaceCard>

        <div className="grid gap-5">
          <SurfaceCard className="p-6">
            <p className="eyebrow">Consequence layer</p>
            <h3 className="mt-4 font-display text-2xl font-semibold tracking-[-0.03em] text-ink">
              Traffic / Economic Disruption Indicator
            </h3>
            <div className="mt-5 flex items-center justify-between gap-4">
              <div>
                <p className="font-display text-4xl font-semibold tracking-[-0.04em] text-ink">{result.disruption.label}</p>
                <p className="mt-2 text-sm leading-7 text-muted">{result.disruption.detail}</p>
              </div>
              <div className="rounded-[22px] border border-slate-200 bg-slate-50 px-4 py-3 text-center">
                <p className="text-xs uppercase tracking-[0.2em] text-muted">Score</p>
                <p className="mt-2 font-display text-3xl font-semibold tracking-[-0.04em] text-ocean">
                  {result.disruption.score.toFixed(2)}
                </p>
              </div>
            </div>
          </SurfaceCard>

          <SurfaceCard className="p-6">
            <p className="eyebrow">NDVI adjustment card</p>
            <h3 className="mt-4 font-display text-2xl font-semibold tracking-[-0.03em] text-ink">Post-event signal</h3>
            <div className="mt-5 space-y-3 text-sm leading-7 text-muted">
              <p>{result.ndviAdjustment.message}</p>
              <div className="flex items-center justify-between rounded-[22px] border border-slate-200 bg-slate-50 px-4 py-3">
                <span>Adjustment applied</span>
                <span className="font-semibold text-ink">
                  {result.ndviAdjustment.applied ? `${result.ndviAdjustment.adjustment >= 0 ? '+' : ''}${result.ndviAdjustment.adjustment.toFixed(3)}` : 'None'}
                </span>
              </div>
              <div className="flex items-center justify-between rounded-[22px] border border-slate-200 bg-slate-50 px-4 py-3">
                <span>Rehabilitation credit</span>
                <span className="font-semibold text-ink">-{result.rehabCredit.toFixed(3)}</span>
              </div>
            </div>
          </SurfaceCard>
        </div>
      </div>
    </div>
  )
}
