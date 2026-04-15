import SectionHeader from '../common/SectionHeader'
import SectionShell from '../layout/SectionShell'
import FeatureImportanceChart from '../charts/FeatureImportanceChart'
import VulnerabilityDistributionChart from '../charts/VulnerabilityDistributionChart'
import RiskDistributionChart from '../charts/RiskDistributionChart'
import ReliabilityChart from '../charts/ReliabilityChart'
import {
  featureImportanceData,
  vulnerabilityDistributionData,
  riskDistributionData,
  reliabilityScatterData,
} from '../../data/mockAnalytics'

export default function AnalyticsSection() {
  return (
    <SectionShell id="analytics">
      <SectionHeader
        eyebrow="Analytics"
        title="Portfolio analytics for a polished professor-facing demo"
        description="These charts are seeded with mock research-ready data so the site already behaves like a real decision-support platform. They can later be pointed to live model outputs or exported summary tables with minimal UI changes."
      />
      <div className="mt-8 grid gap-5 xl:grid-cols-2">
        <FeatureImportanceChart data={featureImportanceData} />
        <VulnerabilityDistributionChart data={vulnerabilityDistributionData} />
        <RiskDistributionChart data={riskDistributionData} />
        <ReliabilityChart data={reliabilityScatterData} />
      </div>
    </SectionShell>
  )
}
