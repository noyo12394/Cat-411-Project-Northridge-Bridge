import { ArrowRight, BrainCircuit, Database, ShieldCheck } from 'lucide-react'
import Button from '../common/Button'
import SurfaceCard from '../common/SurfaceCard'
import SectionShell from '../layout/SectionShell'
import { heroMetrics } from '../../data/content'

export default function HeroSection() {
  return (
    <SectionShell id="top" className="overflow-hidden">
      <div className="grid gap-8 lg:grid-cols-[1.15fr_0.85fr] lg:items-end">
        <div className="relative z-10 space-y-8">
          <div className="space-y-5">
            <span className="eyebrow">Bridge risk intelligence platform</span>
            <div className="space-y-4">
              <h1 className="max-w-4xl font-display text-4xl font-semibold leading-[1.02] tracking-[-0.05em] text-ink sm:text-5xl lg:text-[4.4rem]">
                Bridge Vulnerability Prediction and Decision-Support Dashboard
              </h1>
              <p className="max-w-3xl text-lg leading-8 text-muted sm:text-xl">
                ML-based bridge vulnerability prediction using intrinsic structural features, with hazard intensity separated from
                the core model and consequence layers reserved for prioritization.
              </p>
            </div>
            <p className="max-w-3xl text-base leading-8 text-muted">
              This research demo translates the project into a polished web platform: a comparative framework linking HAZUS, SVI,
              NDVI, and machine learning, plus an interactive dashboard for bridge-level queries, interpretable scores, and
              inspection-oriented outputs.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <Button href="#dashboard" icon={<ArrowRight className="h-4 w-4" />}>
              Open Dashboard
            </Button>
            <Button href="#methodology" variant="secondary">
              View Methodology
            </Button>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            {heroMetrics.map((metric) => (
              <SurfaceCard key={metric.label} className="p-5">
                <p className="text-xs uppercase tracking-[0.2em] text-muted">{metric.label}</p>
                <p className="mt-3 font-display text-3xl font-semibold tracking-[-0.04em] text-ink">{metric.value}</p>
                <p className="mt-2 text-sm leading-6 text-muted">{metric.detail}</p>
              </SurfaceCard>
            ))}
          </div>
        </div>

        <SurfaceCard className="overflow-hidden p-0">
          <div className="bg-gradient-to-br from-ink via-[#16365f] to-ocean p-7 text-white">
            <div className="flex items-center justify-between">
              <p className="font-mono text-[11px] uppercase tracking-[0.24em] text-white/70">Model architecture</p>
              <span className="rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-medium text-white/80">
                Demo-ready
              </span>
            </div>
            <div className="mt-8 space-y-5">
              {[
                {
                  icon: Database,
                  title: 'Intrinsic bridge features',
                  body: 'Age, geometry, condition, bridge class, and SVI define the core vulnerability signal.',
                },
                {
                  icon: BrainCircuit,
                  title: 'Interpretable mock ML engine',
                  body: 'Weighted nonlinear logic estimates a vulnerability score while preserving a clean path to model replacement.',
                },
                {
                  icon: ShieldCheck,
                  title: 'Decision-support outputs',
                  body: 'Risk level, damage state, consequence screening, and inspection rank are all surfaced together.',
                },
              ].map((item) => {
                const Icon = item.icon
                return (
                  <div key={item.title} className="rounded-[24px] border border-white/10 bg-white/5 p-5 backdrop-blur-sm">
                    <div className="flex items-start gap-4">
                      <div className="mt-1 flex h-11 w-11 items-center justify-center rounded-2xl bg-white/10">
                        <Icon className="h-5 w-5" />
                      </div>
                      <div className="space-y-2">
                        <p className="font-display text-xl font-medium tracking-[-0.03em] text-white">{item.title}</p>
                        <p className="text-sm leading-7 text-white/72">{item.body}</p>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </SurfaceCard>
      </div>
    </SectionShell>
  )
}
