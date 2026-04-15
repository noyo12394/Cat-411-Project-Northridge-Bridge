import { Map, Target, Workflow } from 'lucide-react'
import SectionHeader from '../common/SectionHeader'
import SurfaceCard from '../common/SurfaceCard'
import SectionShell from '../layout/SectionShell'
import { significancePoints } from '../../data/content'

const icons = [Target, Workflow, Map]

export default function SignificanceSection() {
  return (
    <SectionShell id="significance">
      <SectionHeader
        eyebrow="Expected significance"
        title="Why this platform matters beyond a single model score"
        description="The strongest value of the project is not only that it predicts a vulnerability score. It gives a structured way to move from static bridge analysis to an interpretable, comparative, and interactive decision-support environment."
      />
      <div className="mt-8 grid gap-5 xl:grid-cols-3">
        {significancePoints.map((point, index) => {
          const Icon = icons[index]
          return (
            <SurfaceCard key={point.title} className="h-full p-7">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-violet/10 text-violet">
                <Icon className="h-5 w-5" />
              </div>
              <h3 className="mt-5 font-display text-2xl font-semibold tracking-[-0.03em] text-ink">{point.title}</h3>
              <p className="mt-4 text-sm leading-7 text-muted">{point.body}</p>
            </SurfaceCard>
          )
        })}
      </div>
      <SurfaceCard className="mt-8 bg-gradient-to-r from-ink via-[#16365f] to-ocean p-7 text-white">
        <div className="grid gap-5 lg:grid-cols-[0.8fr_1fr] lg:items-center">
          <div>
            <p className="font-mono text-xs uppercase tracking-[0.24em] text-white/65">Professor-facing takeaway</p>
            <h3 className="mt-4 font-display text-3xl font-semibold tracking-[-0.04em] text-white">
              A clean bridge vulnerability story, presented as a serious application
            </h3>
          </div>
          <p className="text-sm leading-8 text-white/78">
            The website is structured so you can present the conceptual framework, the variable logic, the dashboard outputs, and the
            charts in one place. It should feel like a research platform ready for live model integration, not a toy interface.
          </p>
        </div>
      </SurfaceCard>
    </SectionShell>
  )
}
