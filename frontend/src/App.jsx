import { useMemo, useState } from 'react'
import Header from './components/layout/Header'
import Footer from './components/layout/Footer'
import AnalyticsSection from './components/sections/AnalyticsSection'
import ComparativeFrameworkSection from './components/sections/ComparativeFrameworkSection'
import DashboardSection from './components/sections/DashboardSection'
import FeatureDisciplineSection from './components/sections/FeatureDisciplineSection'
import HeroSection from './components/sections/HeroSection'
import InterpretabilitySection from './components/sections/InterpretabilitySection'
import ObjectivesSection from './components/sections/ObjectivesSection'
import PipelineSection from './components/sections/PipelineSection'
import SignificanceSection from './components/sections/SignificanceSection'
import TransparencySection from './components/sections/TransparencySection'
import VulnerabilityEngineSection from './components/sections/VulnerabilityEngineSection'
import WhyDifferentSection from './components/sections/WhyDifferentSection'
import { useResearchData } from './hooks/useResearchData'
import SectionErrorBoundary from './components/common/SectionErrorBoundary'

function App() {
  const { data: researchData, loading, diagnostics, ensurePortfolioLoaded, portfolioLoading } =
    useResearchData()
  const [bridgeState, setBridgeState] = useState(null)

  const heroBridgeState = useMemo(() => bridgeState, [bridgeState])
  const summaryCounts = useMemo(
    () =>
      researchData.summary.counts ??
      researchData.summary.totals ?? {
        totalBridges: 0,
        hazardSampled: 0,
        hazardSampledBridges: 0,
      },
    [researchData],
  )
  const dashboardKey = useMemo(
    () =>
      [
        researchData.availability.repoData ? 'repo' : 'fallback',
        summaryCounts.totalBridges,
        summaryCounts.hazardSampled ?? summaryCounts.hazardSampledBridges,
      ].join('-'),
    [researchData.availability.repoData, summaryCounts],
  )

  return (
    <div className="min-h-screen bg-transparent text-slate-950">
      <Header />
      <main className="mx-auto flex w-full max-w-[1440px] flex-col gap-20 px-4 pb-16 pt-28 sm:px-6 lg:px-8">
        <SectionErrorBoundary sectionLabel="Hero section">
          <HeroSection researchData={researchData} bridgeState={heroBridgeState} />
        </SectionErrorBoundary>
        <ObjectivesSection />
        <WhyDifferentSection />
        <FeatureDisciplineSection />
        <VulnerabilityEngineSection methodology={researchData.methodology} />
        <PipelineSection pipeline={researchData.summary.pipeline} />
        <ComparativeFrameworkSection />
        <SectionErrorBoundary sectionLabel="Dashboard section">
          <DashboardSection
            key={dashboardKey}
            researchData={researchData}
            onBridgeStateChange={setBridgeState}
            onEnsurePortfolioLoaded={ensurePortfolioLoaded}
            portfolioLoading={portfolioLoading}
          />
        </SectionErrorBoundary>
        <SectionErrorBoundary sectionLabel="Analytics section">
          <AnalyticsSection researchData={researchData} />
        </SectionErrorBoundary>
        <TransparencySection
          researchData={researchData}
          diagnostics={loading ? 'Loading exported research snapshots...' : diagnostics}
        />
        <InterpretabilitySection />
        <SignificanceSection />
      </main>
      <Footer />
    </div>
  )
}

export default App
