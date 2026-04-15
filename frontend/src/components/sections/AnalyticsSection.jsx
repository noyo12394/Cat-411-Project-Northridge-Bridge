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
  const riskBands = mapCounts(researchData.summary.portfolio.sviRiskBands)
  const damageStates = mapCounts(researchData.summary.portfolio.modalDamageStates)
  const calibrationPoints = researchData.summary.calibrationPoints
  const featureImportance = researchData.analytics.featureImportance
  const scenarioData = researchData.analytics.futureScenarios
  const classifierMetrics = researchData.analytics.classifierMetrics

  return (
    <section id="analytics" className="space-y-8">
      <SectionHeading
        eyebrow="Charts / analytics"
        title="Repo-driven visuals for screening, calibration, and future scenario context"
        description="The charts below are wired to exported JSON snapshots from the repo when available. Where the adapter detects degenerate or placeholder-like outputs, it falls back with explicit labeling rather than silently fabricating certainty."
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
