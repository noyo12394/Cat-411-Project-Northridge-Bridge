import DamageStateChart from '../charts/DamageStateChart'
import FeatureImportanceChart from '../charts/FeatureImportanceChart'
import FutureScenarioChart from '../charts/FutureScenarioChart'
import { RiskDistributionDonut, VulnerabilityDistributionChart } from '../charts/RiskDistributionChart'
import CalibrationScatterChart from '../charts/CalibrationScatterChart'
import InsightCard from '../common/InsightCard'
import SectionHeading from '../common/SectionHeading'

function mapCounts(record = {}) {
  return Object.entries(record).map(([label, count]) => ({ label, count }))
}

export default function AnalyticsSection({ researchData }) {
  const riskBands = mapCounts(researchData.summary.portfolio.prototypeRiskBands ?? researchData.summary.portfolio.sviRiskBands)
  const damageStates = mapCounts(researchData.summary.portfolio.modalDamageStates)
  const calibrationPoints = researchData.summary.calibrationPoints
  const featureImportance = researchData.analytics.featureImportance
  const scenarioData = researchData.analytics.futureScenarios
  const classifierMetrics = researchData.analytics.classifierMetrics

  return (
    <section id="analytics" className="space-y-8">
      <SectionHeading
        eyebrow="Charts / analytics"
        title="Repo-backed visuals for portfolio screening, calibration, and future scenario context"
        description="The charts below use exported repo JSON wherever those files are trustworthy. For the intrinsic vulnerability layer, the dashboard now prioritizes the prototype portfolio score and transparent priors rather than conflating the frontend with a finalized backend model. This section also functions as the site’s global explainable-AI layer."
      />
      <div className="grid gap-5 xl:grid-cols-2">
        <FeatureImportanceChart data={featureImportance} source={researchData.availability.featureImportanceSource} />
        <CalibrationScatterChart data={calibrationPoints} metrics={researchData.analytics.bridgeMlMetrics} />
        <VulnerabilityDistributionChart data={riskBands} />
        <RiskDistributionDonut data={riskBands} />
        <DamageStateChart data={damageStates} />
        <FutureScenarioChart data={scenarioData} />
      </div>
      <div className="grid gap-5 lg:grid-cols-2">
        <InsightCard
          eyebrow="Explainable AI"
          title="Global explanation sits here; local explanation stays in the dashboard"
          description="The feature-importance and calibration panels are global XAI views drawn from repo exports. The dashboard’s contributor cards are local bridge-level explanation cards for the currently selected input state. Keeping those two views separate makes the site more defensible."
          tone="accent"
        />
        <InsightCard
          eyebrow="Model discipline"
          title="SVI and NDVI are explained in different places for a reason"
          description="SVI appears here as a structural-context variable inside the intrinsic screening story, while NDVI earns its value in the post-event proxy-validation branch. That separation is part of the model design, not a presentation trick."
        />
      </div>
      <div className="grid gap-5 lg:grid-cols-2">
        {classifierMetrics.map((metric) => (
          <InsightCard
            key={metric.featureGroup}
            eyebrow={metric.featureGroup}
            title={`${metric.model} performance snapshot`}
            description={`Balanced accuracy ${metric.holdoutBalancedAccuracy.toFixed(3)}, macro-F1 ${metric.holdoutMacroF1.toFixed(3)}, within-one-state accuracy ${metric.holdoutWithinOneStateAccuracy.toFixed(3)}, and weighted kappa ${metric.holdoutQuadraticWeightedKappa.toFixed(3)}.`}
          />
        ))}
      </div>
    </section>
  )
}
