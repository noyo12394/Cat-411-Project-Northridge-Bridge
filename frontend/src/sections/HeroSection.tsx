import { motion } from 'framer-motion'
import { MetricCard } from '../components/common/MetricCard'
import { BridgeStateVisual } from '../components/visuals/BridgeStateVisual'
import { revealTransition } from '../animations/motion'
import type { DashboardAssessment, ResearchData } from '../types/research'

interface HeroSectionProps {
  data: ResearchData
  assessment: DashboardAssessment
}

export function HeroSection({ data, assessment }: HeroSectionProps) {
  const counts = data.summary.counts
  const portfolio = data.summary.portfolio

  return (
    <section
      id="hero"
      className="relative overflow-hidden rounded-[2.4rem] border border-line bg-[radial-gradient(circle_at_top_left,rgba(73,182,255,0.12),transparent_28%),radial-gradient(circle_at_80%_14%,rgba(255,156,105,0.12),transparent_22%),linear-gradient(180deg,rgba(16,26,42,0.96),rgba(7,11,19,0.98))] px-6 pb-8 pt-8 shadow-glow sm:px-8 lg:px-10 lg:pb-10 lg:pt-10"
    >
      <div className="pointer-events-none absolute inset-0 bg-grid bg-[size:48px_48px] opacity-40" />
      <motion.div
        aria-hidden="true"
        initial={{ opacity: 0.2 }}
        animate={{ opacity: [0.2, 0.45, 0.2] }}
        transition={{ duration: 8, repeat: Infinity, ease: 'easeInOut' }}
        className="pointer-events-none absolute inset-x-0 top-8 h-56 bg-[radial-gradient(circle_at_center,rgba(125,211,252,0.18),transparent_60%)]"
      />

      <div className="relative grid gap-10 xl:grid-cols-[0.95fr_1.05fr] xl:items-center">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={revealTransition}
          className="space-y-8"
        >
          <div className="flex flex-wrap gap-3">
            <span className="rounded-full border border-seismic/20 bg-seismic/10 px-4 py-2 font-mono text-[11px] uppercase tracking-[0.28em] text-seismic">
              hindcast benchmark / northridge 1994
            </span>
            <span className="rounded-full border border-line bg-white/5 px-4 py-2 font-mono text-[11px] uppercase tracking-[0.28em] text-muted">
              bridge intelligence lab
            </span>
          </div>

          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.34em] text-muted">
              research-grounded vulnerability and damage dashboard
            </p>
            <h1 className="mt-5 max-w-5xl font-display text-5xl font-semibold tracking-[-0.06em] text-ink sm:text-6xl lg:text-[5.5rem]">
              Northridge bridge intelligence for structural vulnerability, event damage, and emergency prioritization.
            </h1>
            <p className="mt-6 max-w-3xl text-lg leading-8 text-muted">
              This site turns the CAT 411 repository into a deployable catastrophe-intelligence interface.
              It keeps intrinsic vulnerability separate from hazard, treats NDVI as an optional augmentation
              layer, and synchronizes the dashboard state with a live structural bridge twin.
            </p>
          </div>

          <div className="flex flex-wrap gap-3">
            <a href="#decision-dashboard" className="lab-button lab-button-primary">
              Enter Decision Dashboard
            </a>
            <a href="#overview" className="lab-button">
              See Research Story
            </a>
          </div>

          <div className="flex flex-wrap gap-3">
            {[
              'Intrinsic mode excludes PGA',
              'PGA lives only in event mode',
              'ADT stays in prioritization',
              'NDVI is optional augmentation',
            ].map((chip) => (
              <span
                key={chip}
                className="rounded-full border border-line bg-white/5 px-4 py-2 text-sm text-muted"
              >
                {chip}
              </span>
            ))}
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <MetricCard
              label="statewide bridges"
              value={counts.totalBridges.toLocaleString()}
              detail="Portfolio rows carried into the dashboard export."
              accent="seismic"
            />
            <MetricCard
              label="hazard sampled"
              value={counts.hazardSampled.toLocaleString()}
              detail="Bridges with ShakeMap-derived PGA in the engineering workflow."
              accent="signal"
            />
            <MetricCard
              label="mean SVI"
              value={portfolio.meanSVI.toFixed(3)}
              detail="Average intrinsic screening score from the revised SVI workflow."
              accent="moss"
            />
            <MetricCard
              label="live dashboard state"
              value={assessment.stageLabel}
              detail={assessment.narrative}
              accent="hazard"
            />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 18 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ ...revealTransition, delay: 0.08 }}
          className="xl:pl-4"
        >
          <BridgeStateVisual
            assessment={assessment}
            title="Live bridge twin"
            caption="The bridge is already tied to the shared dashboard state here. As scenario controls change later in the page, this structure moves with them."
          />
        </motion.div>
      </div>
    </section>
  )
}
