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
        description="The charts below use exported repo JSON wherever those files are trustworthy. For the intrinsic vulnerability layer, the dashboard now prioritizes the prototype portfolio score and transparent priors rather than conflating the frontend with a finalized backend model."
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
