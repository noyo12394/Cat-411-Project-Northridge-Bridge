import InsightCard from '../common/InsightCard'
import SectionHeading from '../common/SectionHeading'

export default function InterpretabilitySection() {
  return (
    <section className="space-y-8">
      <SectionHeading
        eyebrow="Interpretability flow"
        title="Why the score changes, and why not every variable belongs in the same layer"
        description="The platform emphasizes interpretable movement: condition, age, skew, span geometry, and SVI influence baseline vulnerability; ADT changes consequence; PGA changes event damage; NDVI changes post-event attention."
      />
      <div className="grid gap-5 lg:grid-cols-3">
        <InsightCard
          eyebrow="Structural drivers"
          title="Condition, age, geometry, and class move the baseline"
          description="Condition rating, age / reconstruction timing, skew, span length, number of spans, HWB class, and SVI are the dominant levers in intrinsic vulnerability mode."
        />
        <InsightCard
          eyebrow="Hazard driver"
          title="PGA changes how much damage may happen in a specific event"
          description="The event mode deliberately introduces PGA only after intrinsic screening, so the UI can answer a different question: what does this bridge look like under a specific earthquake intensity?"
          tone="accent"
        />
        <InsightCard
          eyebrow="Consequence driver"
          title="ADT and NDVI alter urgency, not inherent structure"
          description="Traffic importance and NDVI post-event evidence can make a bridge more urgent to inspect, even when they do not change the underlying structural vulnerability logic."
        />
      </div>
    </section>
  )
}
