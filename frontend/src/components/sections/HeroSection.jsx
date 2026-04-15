import SectionHeading from '../common/SectionHeading'
import BridgeStateVisual from '../visuals/BridgeStateVisual'

function StatChip({ label, value }) {
  return (
    <div className="rounded-[24px] border border-white/80 bg-white/88 px-4 py-3 shadow-sm backdrop-blur">
      <p className="text-xs uppercase tracking-[0.24em] text-slate-500">{label}</p>
      <p className="mt-2 text-xl font-semibold tracking-[-0.04em] text-slate-950">{value}</p>
    </div>
  )
}

export default function HeroSection({ researchData, bridgeState }) {
  const { counts, portfolio } = researchData.summary

  return (
    <section id="top" className="relative overflow-hidden rounded-[36px] border border-white/80 bg-[radial-gradient(circle_at_top_left,rgba(96,165,250,0.18),transparent_28%),radial-gradient(circle_at_85%_16%,rgba(139,92,246,0.14),transparent_22%),linear-gradient(180deg,#ffffff_0%,#f6f9ff_48%,#eef4ff_100%)] px-6 pb-8 pt-10 shadow-[0_28px_80px_rgba(15,23,42,0.12)] sm:px-8 lg:px-10 lg:pb-10 lg:pt-12">
      <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(90deg,rgba(59,130,246,0.08)_1px,transparent_1px),linear-gradient(rgba(59,130,246,0.08)_1px,transparent_1px)] bg-[size:34px_34px] opacity-35" />
      <div className="relative grid gap-10 xl:grid-cols-[1.06fr_0.94fr] xl:items-center">
        <div className="space-y-8">
          <SectionHeading
            eyebrow="Bridge vulnerability prediction and decision-support dashboard"
            title="Machine-learning-based bridge vulnerability prediction using intrinsic structural attributes, with inspection prioritization and catastrophe-modeling context."
            description="A research/demo platform built from the California National Bridge Inventory, the 1994 Northridge ShakeMap workflow, revised SVI scoring, HAZUS-style fragility logic, NDVI proxy validation, and machine-learning comparisons. The interface deliberately keeps vulnerability, hazard demand, and prioritization separate so the engineering logic remains legible."
            actions={
              <>
                <a href="#dashboard" className="rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-[0_18px_40px_rgba(15,23,42,0.18)] transition hover:-translate-y-0.5">
                  Open Dashboard
                </a>
                <a href="#research-pipeline" className="rounded-full border border-slate-200 bg-white/90 px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-slate-300">
                  View Methodology
                </a>
              </>
            }
          />

          <div className="flex flex-wrap gap-3">
            <span className="rounded-full border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700">Repo pipeline grounded</span>
            <span className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700">No PGA in core vulnerability mode</span>
            <span className="rounded-full border border-violet-200 bg-violet-50 px-4 py-2 text-sm font-medium text-violet-700">NDVI only as optional post-event adjustment</span>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            <StatChip label="Statewide bridges" value={counts.totalBridges.toLocaleString()} />
            <StatChip label="Hazard-sampled bridges" value={counts.hazardSampled.toLocaleString()} />
            <StatChip label="Mean portfolio SVI" value={portfolio.meanSVI.toFixed(3)} />
          </div>
        </div>

        <BridgeStateVisual
          score={bridgeState?.score ?? portfolio.meanSVI}
          visualState={bridgeState?.visualState}
          title="Adaptive bridge state visual"
        />
      </div>
    </section>
  )
}
