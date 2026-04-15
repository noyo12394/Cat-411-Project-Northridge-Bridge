import InsightCard from '../common/InsightCard'
import SectionHeading from '../common/SectionHeading'

export default function SignificanceSection() {
  const cards = [
    {
      eyebrow: 'Research value',
      title: 'From class-based estimation to bridge-level screening',
      description:
        'The platform translates class-based fragility thinking into a bridge-level screening workflow that still respects the difference between structural vulnerability and event hazard demand.',
    },
    {
      eyebrow: 'Product value',
      title: 'From static notebooks to interactive decision support',
      description:
        'Instead of leaving the workflow in disconnected notebooks, the site turns it into a dashboard experience that makes inspection triage and scenario communication legible to a user.',
    },
    {
      eyebrow: 'Systems value',
      title: 'One platform for HAZUS, SVI, NDVI, and ML',
      description:
        'The final value is not any one model in isolation. It is the ability to keep those layers coherent while moving between intrinsic screening, event damage, and consequence-aware prioritization.',
    },
  ]

  return (
    <section className="space-y-8">
      <SectionHeading
        eyebrow="Significance / research value"
        title="A bridge-intelligence interface that stays faithful to the repo's engineering logic"
        description="The point of the website is not just polish. It is to make the project more rigorous to read, easier to demonstrate, and easier to evolve into a fuller decision-support product."
      />
      <div className="grid gap-5 lg:grid-cols-3">
        {cards.map((card, index) => (
          <InsightCard key={card.title} {...card} tone={index === 1 ? 'accent' : 'default'} />
        ))}
      </div>
    </section>
  )
}
