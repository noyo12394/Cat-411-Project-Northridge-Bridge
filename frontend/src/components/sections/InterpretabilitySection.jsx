import InsightCard from '../common/InsightCard'
import SectionHeading from '../common/SectionHeading'

export default function InterpretabilitySection() {
  return (
    <section className="space-y-8">
      <SectionHeading
        eyebrow="Interpretability / explainable AI"
        title="Why the score changes, and how the site explains that change without pretending the model is a black box"
        description="The platform separates local bridge-level explanation from global explainable-AI checks. Condition, age, skew, span geometry, bridge class, and SVI influence baseline vulnerability; ADT changes consequence; PGA changes event damage; NDVI changes post-event attention."
      />
      <div className="grid gap-5 lg:grid-cols-2 xl:grid-cols-4">
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
        <InsightCard
          eyebrow="Global XAI"
          title="Feature importance, coefficients, and calibration keep the ML story legible"
          description="The repo-backed explainable-AI layer uses permutation importance for tree models, coefficient magnitude for linear baselines, and calibration / residual diagnostics to check whether the model is leaning on structurally meaningful variables rather than opaque artifacts."
        />
      </div>
    </section>
  )
}
