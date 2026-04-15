import InsightCard from '../common/InsightCard'
import SectionHeading from '../common/SectionHeading'

export default function FeatureDisciplineSection() {
  const cards = [
    {
      eyebrow: 'Core vulnerability model',
      title: 'Intrinsic bridge screening only',
      description:
        'Year built, reconstruction timing, skew, number of spans, maximum span length, condition, bridge class / HWB class, and SVI belong here. These tell us which bridges are structurally more vulnerable in general.',
    },
    {
      eyebrow: 'Event damage layer',
      title: 'Hazard enters only for scenario damage',
      description:
        'PGA belongs in event-specific damage estimation after intrinsic vulnerability has already been established. It changes how much damage may happen in a specific earthquake, not which bridge is inherently weaker.',
    },
    {
      eyebrow: 'Prioritization / consequence',
      title: 'ADT, disruption, and NDVI belong later',
      description:
        'Traffic importance, economic disruption logic, and optional NDVI adjustment belong in emergency inspection ranking and consequence framing. They should not contaminate the baseline vulnerability score.',
    },
  ]

  return (
    <section id="feature-discipline" className="space-y-8">
      <SectionHeading
        eyebrow="Feature discipline / model logic"
        title="A strict interface that keeps vulnerability, hazard, and consequence from collapsing into one score"
        description="The website follows the engineering rules in the repo rather than flattening everything into one generic ML form."
      />
      <div className="grid gap-5 lg:grid-cols-3">
        {cards.map((card) => (
          <InsightCard key={card.title} {...card} />
        ))}
      </div>
    </section>
  )
}
