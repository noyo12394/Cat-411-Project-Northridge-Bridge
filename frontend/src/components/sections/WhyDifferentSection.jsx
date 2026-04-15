import InsightCard from '../common/InsightCard'
import SectionHeading from '../common/SectionHeading'

export default function WhyDifferentSection() {
  return (
    <section className="grid gap-6 xl:grid-cols-[0.92fr_1.08fr]">
      <InsightCard
        eyebrow="Why this is different"
        title="The platform is opinionated about what belongs in vulnerability, damage, and prioritization"
        description="That separation is the point. HAZUS is useful but class-based. SVI is interpretable but simplified. NDVI is useful only after an event and only as proxy evidence. ML can capture nonlinear bridge-specific variation, but only if the interface refuses to blur hazard demand into intrinsic vulnerability."
        tone="dark"
      />
      <div className="grid gap-5 md:grid-cols-2">
        <InsightCard
          eyebrow="HAZUS"
          title="Good fragility backbone, limited intrinsic nuance"
          description="Useful for translating bridge class and hazard intensity into damage probabilities, but it is not the same as a bridge-intrinsic vulnerability ranking."
        />
        <InsightCard
          eyebrow="SVI"
          title="Transparent structural screening"
          description="The revised SVI carries interpretable structural weights and continuous ranges, making it a strong bridge-intrinsic screening layer."
        />
        <InsightCard
          eyebrow="NDVI"
          title="Post-event proxy, not a baseline driver"
          description="NDVI helps after an earthquake when inspection labels are sparse. It should inform post-event attention, not define baseline structure."
        />
        <InsightCard
          eyebrow="ML"
          title="Captures nonlinear variation bridge by bridge"
          description="Used carefully, ML can turn the statewide pipeline into a screening instrument that adapts to bridge-specific geometry, condition, and age instead of only class-level assumptions."
        />
      </div>
    </section>
  )
}
