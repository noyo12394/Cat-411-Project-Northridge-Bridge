import { BarChart3, BrainCircuit, Database, Layers3 } from 'lucide-react'
import SectionHeader from '../common/SectionHeader'
import SurfaceCard from '../common/SurfaceCard'
import SectionShell from '../layout/SectionShell'
import { frameworkCards } from '../../data/content'

const iconMap = {
  HAZUS: Database,
  SVI: Layers3,
  NDVI: BarChart3,
  'ML (Proposed)': BrainCircuit,
}

export default function ComparativeFrameworkSection() {
  return (
    <SectionShell id="framework">
      <SectionHeader
        eyebrow="Comparative framework"
        title="Where HAZUS, SVI, NDVI, and ML each belong"
        description="A strong demo should make the methods legible. The framework below shows each tool’s role, what it does well, where it is limited, and how it connects back to the proposed ML-driven dashboard."
      />

      <div className="mt-8 grid gap-5 xl:grid-cols-4">
        {frameworkCards.map((card) => {
          const Icon = iconMap[card.name]
          return (
            <SurfaceCard key={card.name} className="flex h-full flex-col gap-5 p-6">
              <div className="flex items-center gap-4">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-ocean/8 text-ocean">
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <p className="font-display text-xl font-semibold tracking-[-0.03em] text-ink">{card.name}</p>
                  <p className="text-xs uppercase tracking-[0.2em] text-muted">{card.role}</p>
                </div>
              </div>
              <div className="space-y-4 text-sm leading-7 text-muted">
                <div>
                  <p className="font-semibold text-ink">Strength</p>
                  <p>{card.strength}</p>
                </div>
                <div>
                  <p className="font-semibold text-ink">Limitation</p>
                  <p>{card.limitation}</p>
                </div>
                <div>
                  <p className="font-semibold text-ink">ML connection</p>
                  <p>{card.connection}</p>
                </div>
              </div>
            </SurfaceCard>
          )
        })}
      </div>
    </SectionShell>
  )
}
