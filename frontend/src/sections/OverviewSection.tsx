import { Panel } from '../components/common/Panel'
import { SectionShell } from '../components/common/SectionShell'
import type { ResearchData } from '../types/research'

interface OverviewSectionProps {
  data: ResearchData
}

export function OverviewSection({ data }: OverviewSectionProps) {
  return (
    <SectionShell
      id="overview"
      index="01"
      eyebrow="overview"
      title="A historical earthquake becomes a decision-support pipeline."
      description="The project is framed as a hindcast benchmark: start from the Northridge 1994 event, connect hazard to statewide bridge assets, apply fragility logic and SVI screening, compare ML formulations, then surface the work as an operational interface."
    >
      <div className="grid gap-5 xl:grid-cols-[0.95fr_1.05fr]">
        <Panel
          eyebrow="pipeline"
          title="Historical event to decision support"
          description="This is the core story the site tells. The interface is designed to keep those layers legible instead of collapsing them into one synthetic score."
        >
          <div className="grid gap-4 md:grid-cols-2">
            {data.summary.pipeline.map((step, index) => (
              <div
                key={step.label}
                className="relative rounded-[1.8rem] border border-line bg-white/5 p-5"
              >
                <div className="absolute right-4 top-4 rounded-full border border-line bg-white/6 px-3 py-1 font-mono text-[10px] uppercase tracking-[0.24em] text-muted">
                  step {index + 1}
                </div>
                <p className="font-mono text-[11px] uppercase tracking-[0.3em] text-seismic/70">
                  {step.file}
                </p>
                <h3 className="mt-4 font-display text-2xl font-semibold tracking-[-0.04em] text-ink">
                  {step.label}
                </h3>
                <p className="mt-3 text-sm leading-6 text-muted">{step.output}</p>
              </div>
            ))}
          </div>
        </Panel>

        <div className="grid gap-5">
          <Panel
            eyebrow="framing"
            title="What the dashboard is solving"
            description="The site is not just a report viewer. It is meant to help explain which bridges are structurally vulnerable, how a specific hazard scenario changes the picture, and which assets deserve scarce post-event attention first."
          >
            <div className="grid gap-4 md:grid-cols-3">
              {[
                {
                  title: 'Intrinsic vulnerability',
                  detail: 'Structural screening based on age, condition, geometry, HAZUS class, and SVI. No PGA here.',
                },
                {
                  title: 'Event damage under hazard',
                  detail: 'Scenario PGA is introduced only in the hazard-specific damage layer.',
                },
                {
                  title: 'Operational prioritization',
                  detail: 'Consequence, traffic, and optional NDVI evidence affect urgency after structural logic is established.',
                },
              ].map((card) => (
                <div key={card.title} className="rounded-[1.6rem] border border-line bg-white/5 p-5">
                  <h3 className="font-display text-xl font-semibold tracking-[-0.04em] text-ink">
                    {card.title}
                  </h3>
                  <p className="mt-3 text-sm leading-6 text-muted">{card.detail}</p>
                </div>
              ))}
            </div>
          </Panel>

          <Panel
            eyebrow="methodology"
            title="Repository-backed layers already available"
            description="The frontend is not inventing structure from scratch. These layers are already exported from the repository and are being elevated into a stronger interface."
          >
            <div className="flex flex-wrap gap-3 text-sm text-muted">
              {[
                'statewide bridge portfolio',
                'scenario summaries',
                'hybrid ML model comparison',
                'recommended model metrics',
                'feature importance',
                'proxy validation',
                'research figures',
              ].map((item) => (
                <span key={item} className="rounded-full border border-line bg-white/6 px-4 py-2">
                  {item}
                </span>
              ))}
            </div>
          </Panel>
        </div>
      </div>
    </SectionShell>
  )
}
