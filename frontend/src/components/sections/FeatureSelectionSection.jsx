import { FlaskConical, Gauge, ShieldCheck } from 'lucide-react'
import SectionHeader from '../common/SectionHeader'
import SurfaceCard from '../common/SurfaceCard'
import SectionShell from '../layout/SectionShell'
import { featureSelectionCards } from '../../data/content'

const icons = [ShieldCheck, FlaskConical, Gauge]

export default function FeatureSelectionSection() {
  return (
    <SectionShell id="methodology">
      <SectionHeader
        eyebrow="Feature selection logic"
        title="Keep vulnerability, hazard, and consequence logically separate"
        description="The core model is designed around intrinsic structural vulnerability. PGA is deliberately excluded from the primary input panel because hazard intensity belongs to event-specific damage estimation, not to the bridge-intrinsic vulnerability definition."
      />

      <div className="mt-8 rounded-[28px] border border-ocean/10 bg-gradient-to-r from-ocean/7 via-white to-violet/6 p-6">
        <div className="grid gap-3 lg:grid-cols-[0.55fr_1fr] lg:items-center">
          <div>
            <p className="font-mono text-xs uppercase tracking-[0.24em] text-ocean">Design discipline</p>
            <h3 className="mt-3 font-display text-2xl font-semibold tracking-[-0.03em] text-ink">
              PGA is excluded from the core vulnerability model on purpose
            </h3>
          </div>
          <p className="text-sm leading-7 text-muted">
            Hazard demand answers “what happens in this earthquake?” Vulnerability answers “which bridges are intrinsically weaker?”
            The dashboard keeps those questions separate so the project stays academically coherent and easier to defend.
          </p>
        </div>
      </div>

      <div className="mt-8 grid gap-5 xl:grid-cols-3">
        {featureSelectionCards.map((card, index) => {
          const Icon = icons[index]
          return (
            <SurfaceCard key={card.title} className="h-full p-7">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-ink text-white shadow-soft">
                <Icon className="h-5 w-5" />
              </div>
              <h3 className="mt-5 font-display text-2xl font-semibold tracking-[-0.03em] text-ink">{card.title}</h3>
              <ul className="mt-5 space-y-3 text-sm leading-7 text-muted">
                {card.bullets.map((bullet) => (
                  <li key={bullet} className="flex gap-3">
                    <span className="mt-2 h-2 w-2 rounded-full bg-ocean" />
                    <span>{bullet}</span>
                  </li>
                ))}
              </ul>
              <p className="mt-5 border-t border-slate-100 pt-5 text-sm leading-7 text-muted">{card.note}</p>
            </SurfaceCard>
          )
        })}
      </div>
    </SectionShell>
  )
}
