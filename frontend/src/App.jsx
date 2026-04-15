import { Suspense, lazy } from 'react'
import Header from './components/layout/Header'
import Footer from './components/layout/Footer'
import HeroSection from './components/sections/HeroSection'
import ObjectivesSection from './components/sections/ObjectivesSection'
import MotivationSection from './components/sections/MotivationSection'
import FeatureSelectionSection from './components/sections/FeatureSelectionSection'
import ComparativeFrameworkSection from './components/sections/ComparativeFrameworkSection'
import InteractiveDashboardSection from './components/sections/InteractiveDashboardSection'
import SignificanceSection from './components/sections/SignificanceSection'

const AnalyticsSection = lazy(() => import('./components/sections/AnalyticsSection'))

function App() {
  return (
    <div className="min-h-screen">
      {/* Single-page research demo layout with anchored sections for navigation. */}
      <Header />
      <main className="mx-auto flex w-full max-w-[1440px] flex-col gap-8 px-4 pb-12 pt-24 sm:px-6 lg:px-8">
        <HeroSection />
        <ObjectivesSection />
        <MotivationSection />
        <FeatureSelectionSection />
        <ComparativeFrameworkSection />
        <InteractiveDashboardSection />
        <Suspense
          fallback={
            <section className="section-shell">
              <div className="section-grid" />
              <div className="relative z-10 p-8">
                <p className="eyebrow">Analytics</p>
                <p className="mt-5 text-sm leading-7 text-muted">
                  Loading the charting layer for the analytics section.
                </p>
              </div>
            </section>
          }
        >
          <AnalyticsSection />
        </Suspense>
        <SignificanceSection />
      </main>
      <Footer />
    </div>
  )
}

export default App
