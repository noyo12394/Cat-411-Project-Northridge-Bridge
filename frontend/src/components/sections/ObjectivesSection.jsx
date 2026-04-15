import InsightCard from '../common/InsightCard'
import SectionHeading from '../common/SectionHeading'

export default function ObjectivesSection() {
  const cards = [
    {
      eyebrow: 'Core objective',
      title: 'Bridge vulnerability prediction from intrinsic structural attributes',
      description:
        'Screen bridges using age, reconstruction timing, skew, span geometry, class, condition, and SVI without letting PGA dominate the baseline vulnerability experience.',
    },
    {
      eyebrow: 'Secondary objective',
      title: 'Interactive bridge-level dashboard for inspection prioritization',
      description:
        'Translate the notebook workflow into a usable interface for bridge-level queries, interpretable scores, damage framing, and emergency inspection triage.',
    },
    {
      eyebrow: 'Integrative goal',
      title: 'Comparative framework linking HAZUS, SVI, NDVI, and ML',
      description:
        'Show how class-based fragility logic, intrinsic index scoring, post-event proxy evidence, and ML-based screening can coexist in one coherent platform.',
    },
  ]

  return (
    <section className="space-y-8">
      <SectionHeading
        eyebrow="What this project does"
        title="A research platform that connects engineering workflow, model discipline, and usable decision support"
        description="The site is meant to read like a serious infrastructure intelligence platform rather than a notebook appendix: one layer for intrinsic vulnerability, one for scenario damage, and one for inspection prioritization."
      />
      <div className="grid gap-5 lg:grid-cols-3">
        {cards.map((card, index) => (
          <InsightCard key={card.title} {...card} tone={index === 1 ? 'accent' : 'default'} />
        ))}
      </div>
    </section>
  )
}
