import InsightCard from '../common/InsightCard'
import SectionHeading from '../common/SectionHeading'

const cards = [
  {
    eyebrow: 'HAZUS',
    title: 'Class-based event damage backbone',
    description: 'Primary role: fragility / expected damage ratio estimation under an earthquake demand. Strength: engineering lineage and class-based fragility mapping. Limitation: class-based and hazard-driven, not a bridge-intrinsic ranking.',
  },
  {
    eyebrow: 'SVI',
    title: 'Intrinsic structural screening layer',
    description: 'Primary role: interpretable bridge vulnerability screening. Strength: transparent weights and bridge-specific factors. Limitation: simplified and still a surrogate, not an event-specific damage solver.',
  },
  {
    eyebrow: 'NDVI',
    title: 'Proxy-based post-event evidence',
    description: 'Primary role: post-event proxy validation and attention adjustment. Strength: useful when inspection labels are sparse. Limitation: not a structural core driver and not equivalent to field-observed damage.',
  },
  {
    eyebrow: 'ML (proposed)',
    title: 'Bridge-specific nonlinear screening',
    description: 'Primary role: bridge-level vulnerability screening and scenario-aware comparison. Strength: captures nonlinear variation and connects outputs into a usable dashboard. Limitation: browser-side demo mode may approximate the trained model when a live backend is absent.',
  },
]

export default function ComparativeFrameworkSection() {
  return (
    <section className="space-y-8">
      <SectionHeading
        eyebrow="Comparative framework"
        title="Four methods, four roles, one coherent platform"
        description="The project is strongest when these methods are shown as complementary rather than interchangeable."
      />
      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {cards.map((card, index) => (
          <InsightCard key={card.title} {...card} tone={index === 3 ? 'accent' : 'default'} />
        ))}
      </div>
    </section>
  )
}
