import SectionHeading from '../common/SectionHeading'
import EnhancedBridgeVisualizer from '../visuals/EnhancedBridgeVisualizer'

function StatChip({ label, value, hint }) {
  return (
    <div className="rounded-[24px] border border-slate-200/90 bg-[linear-gradient(180deg,rgba(255,255,255,0.96)_0%,rgba(249,251,255,0.96)_100%)] px-4 py-3 shadow-sm backdrop-blur">
      <p className="text-xs uppercase tracking-[0.24em] text-slate-600">{label}</p>
      <p className="mt-2 text-xl font-semibold tracking-[-0.04em] text-slate-900">{value}</p>
      {hint ? <p className="mt-2 text-sm leading-6 text-slate-700">{hint}</p> : null}
    </div>
  )
}

export default function HeroSection({ researchData, bridgeState }) {
  const { counts, portfolio } = researchData.summary
  const previewScore =
    (bridgeState?.score ?? portfolio.meanPrototypeVulnerability ?? portfolio.meanSVI ?? 0.45) * 100

  return (
    <section id="top" className="relative overflow-hidden rounded-[36px] border border-slate-200/90 bg-[radial-gradient(circle_at_top_left,rgba(96,165,250,0.2),transparent_30%),radial-gradient(circle_at_85%_16%,rgba(139,92,246,0.12),transparent_22%),linear-gradient(180deg,#ffffff_0%,#f7faff_46%,#edf3ff_100%)] px-6 pb-8 pt-10 shadow-[0_28px_80px_rgba(15,23,42,0.14)] sm:px-8 lg:px-10 lg:pb-10 lg:pt-12">
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(90deg,rgba(59,130,246,0.09)_1px,transparent_1px),linear-gradient(rgba(59,130,246,0.09)_1px,transparent_1px)] bg-[size:34px_34px] opacity-40" />
      <div className="relative grid gap-10 xl:grid-cols-[1.02fr_0.98fr] xl:items-center">
        <div className="space-y-8">
          <SectionHeading
            eyebrow="Bridge vulnerability prediction and decision-support dashboard"
            title="A research-grade bridge intelligence platform for intrinsic vulnerability screening, prioritization, and future scenario analysis"
            description="Built from the California bridge inventory, the Northridge ShakeMap workflow, revised SVI scoring, HAZUS-style fragility outputs, NDVI proxy validation, and machine-learning comparisons. The interface is explicit about what is repo-backed today and what remains a transparent prototype layer until the final backend model is wired in."
            theme="paper"
            actions={
              <>
                <a href="#dashboard" className="rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-[0_18px_40px_rgba(15,23,42,0.18)] transition hover:-translate-y-0.5">
                  Explore Dashboard
                </a>
                <a href="#vulnerability-engine" className="rounded-full border border-slate-200/90 bg-white/95 px-5 py-3 text-sm font-semibold text-slate-800 transition hover:border-slate-300 hover:bg-slate-50">
                  See Methodology
                </a>
              </>
            }
          />

          <div className="flex flex-wrap gap-3">
            <span className="rounded-full border border-blue-200/90 bg-blue-50/95 px-4 py-2 text-sm font-medium text-blue-800">Real statewide bridge portfolio loaded from repo exports</span>
            <span className="rounded-full border border-slate-200/90 bg-white/95 px-4 py-2 text-sm font-medium text-slate-800">No PGA in the core vulnerability model</span>
            <span className="rounded-full border border-violet-200/90 bg-violet-50/95 px-4 py-2 text-sm font-medium text-violet-800">ADT only in prioritization / consequence</span>
            <span className="rounded-full border border-cyan-200/90 bg-cyan-50/95 px-4 py-2 text-sm font-medium text-cyan-800">NDVI only as optional contextual adjustment</span>
          </div>

          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatChip label="Statewide bridges" value={counts.totalBridges.toLocaleString()} hint="Bridge rows available in the processed portfolio" />
            <StatChip label="Hazard-sampled bridges" value={counts.hazardSampled.toLocaleString()} hint="Bridges with ShakeMap-derived PGA sampling" />
            <StatChip label="Mean SVI" value={portfolio.meanSVI.toFixed(3)} hint="Repo-derived intrinsic screening index" />
            <StatChip label="Mean prototype score" value={portfolio.meanPrototypeVulnerability.toFixed(3)} hint="Frontend research prototype vulnerability layer" />
          </div>
        </div>

        <div className="paper-panel rounded-[32px] p-5">
          <div className="flex flex-col gap-4 border-b border-slate-200/90 pb-5">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div className="max-w-xl">
                <p className="paper-eyebrow">Live structural preview</p>
                <h3 className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-900">
                  New bridge animation language for the dashboard
                </h3>
                <p className="mt-3 paper-copy">
                  The site now uses the newer bridge animation as the primary structural-state visual, so the
                  dashboard reads more cleanly and the motion language stays consistent.
                </p>
              </div>
              <div className="paper-chip">Preview score {previewScore.toFixed(0)}%</div>
            </div>
          </div>

          <div className="mt-5 overflow-hidden rounded-[28px] bg-[linear-gradient(180deg,#08111d_0%,#0b1625_100%)] p-4 shadow-[inset_0_0_0_1px_rgba(148,163,184,0.08)]">
            <EnhancedBridgeVisualizer
              vulnerability={previewScore}
              showMetrics={false}
              showDamageBreakdown={false}
            />
          </div>
        </div>
      </div>
    </section>
  )
}
