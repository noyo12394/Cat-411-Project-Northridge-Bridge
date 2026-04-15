import { Activity, BrainCircuit, LineChart } from 'lucide-react'
import SectionHeader from '../common/SectionHeader'
import SurfaceCard from '../common/SurfaceCard'
import SectionShell from '../layout/SectionShell'
import { motivationPoints } from '../../data/content'

const icons = [BrainCircuit, Activity, LineChart]

export default function MotivationSection() {
  return (
    <SectionShell id="motivation">
      <div className="grid gap-8 xl:grid-cols-[0.9fr_1.1fr]">
        <div className="space-y-5">
          <SectionHeader
            eyebrow="Why ML"
            title="Why machine learning belongs in this bridge vulnerability workflow"
            description="The case for ML is not that it should replace engineering judgment. It is that it can augment structured fragility logic by learning nonlinear bridge-specific variation, while remaining interpretable enough for academic presentation and decision-support use."
          />
          <SurfaceCard className="p-6">
            <p className="text-sm leading-7 text-muted">
              This framing keeps the project defensible: HAZUS remains a fragility anchor, SVI remains an interpretable vulnerability layer,
              NDVI remains an optional post-event signal, and ML becomes the bridge-specific prediction engine that ties them together.
            </p>
          </SurfaceCard>
        </div>
        <div className="grid gap-5">
          {motivationPoints.map((point, index) => {
            const Icon = icons[index]
            return (
              <SurfaceCard key={point.title} className="flex gap-4 p-6 sm:items-start">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-violet/10 text-violet">
                  <Icon className="h-5 w-5" />
                </div>
                <div className="space-y-2">
                  <h3 className="font-display text-xl font-semibold tracking-[-0.03em] text-ink">{point.title}</h3>
                  <p className="text-sm leading-7 text-muted">{point.body}</p>
                </div>
              </SurfaceCard>
            )
          })}
        </div>
      </div>
    </SectionShell>
  )
}
