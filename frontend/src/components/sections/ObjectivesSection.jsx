import { Layers3, Target, Workflow } from 'lucide-react'
import SectionHeader from '../common/SectionHeader'
import SurfaceCard from '../common/SurfaceCard'
import SectionShell from '../layout/SectionShell'
import { objectives } from '../../data/content'

const icons = [Target, Workflow, Layers3]

export default function ObjectivesSection() {
  return (
    <SectionShell id="objectives">
      <SectionHeader
        eyebrow="Objectives"
        title="A bridge-risk website with a serious research posture"
        description="The site is intentionally framed as more than a visualization exercise. It is meant to communicate the modeling logic, the decision-support goal, and the comparative value of HAZUS, SVI, NDVI, and ML in one coherent demo."
      />
      <div className="mt-8 grid gap-5 xl:grid-cols-3">
        {objectives.map((item, index) => {
          const Icon = icons[index]
          return (
            <SurfaceCard key={item.title} className="flex h-full flex-col gap-5 p-7">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-ocean/8 text-ocean">
                <Icon className="h-5 w-5" />
              </div>
              <div className="space-y-3">
                <h3 className="font-display text-2xl font-semibold tracking-[-0.03em] text-ink">{item.title}</h3>
                <p className="text-sm leading-7 text-muted">{item.body}</p>
              </div>
            </SurfaceCard>
          )
        })}
      </div>
    </SectionShell>
  )
}
