import { useState } from 'react'
import { HeroSection } from './sections/HeroSection'
import { OverviewSection } from './sections/OverviewSection'
import { HazardSection } from './sections/HazardSection'
import { AssetFragilitySection } from './sections/AssetFragilitySection'
import { SviSection } from './sections/SviSection'
import { NdviSection } from './sections/NdviSection'
import { MlVulnerabilitySection } from './sections/MlVulnerabilitySection'
import { ValidationSection } from './sections/ValidationSection'
import { DecisionDashboardSection } from './sections/DecisionDashboardSection'
import { useResearchData } from './hooks/useResearchData'
import {
  applyPortfolioBridge,
  createInitialInputs,
  DASHBOARD_MODES,
  runDashboardAssessment,
} from './lib/dashboardModel'
import type { DashboardInputs, DashboardModeId } from './types/research'

const NAV_ITEMS = [
  ['overview', 'Overview'],
  ['hazard', 'Hazard'],
  ['asset-fragility', 'Asset + Fragility'],
  ['svi', 'SVI'],
  ['ndvi', 'NDVI'],
  ['ml-vulnerability', 'ML Vulnerability'],
  ['validation', 'Validation'],
  ['decision-dashboard', 'Decision Dashboard'],
] as const

function LoadingScreen() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-canvas px-6 text-center">
      <div className="max-w-xl space-y-4">
        <p className="font-mono text-[11px] uppercase tracking-[0.34em] text-seismic/75">
          loading research dashboard
        </p>
        <h1 className="font-display text-4xl font-semibold tracking-[-0.05em] text-ink">
          Preparing the Northridge bridge intelligence layer.
        </h1>
        <p className="text-base leading-8 text-muted">
          Fetching exported JSON snapshots, methodology priors, and research figures from the repo.
        </p>
      </div>
    </div>
  )
}

export default function App() {
  const { data, loading, error } = useResearchData()
  const [mode, setMode] = useState<DashboardModeId>('intrinsic')
  const [inputs, setInputs] = useState<DashboardInputs | null>(null)

  const activeInputs = data ? inputs ?? createInitialInputs(data) : null

  if (loading || !data || !activeInputs) {
    return <LoadingScreen />
  }

  const assessment = runDashboardAssessment(activeInputs, mode, data)

  const updateInput = <K extends keyof DashboardInputs>(field: K, value: DashboardInputs[K]) => {
    setInputs((current) => ({
      ...(current ?? createInitialInputs(data)),
      [field]: value,
    }))
  }

  const loadSample = (structureNumber: string) => {
    if (!structureNumber) {
      return
    }
    const bridge = data.portfolio.find((item) => item.structureNumber === structureNumber)
    if (!bridge) {
      return
    }
    setInputs(applyPortfolioBridge(bridge, data))
  }

  const resetInputs = () => {
    setInputs(createInitialInputs(data))
  }

  const setScenarioPreview = (nextValue: number) => {
    setMode('event')
    updateInput('scenarioPga', nextValue)
  }

  const setNdviPreview = (nextValue: number | '') => {
    updateInput('ndviChange', nextValue)
  }

  return (
    <div className="min-h-screen bg-canvas text-ink">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_20%_0%,rgba(73,182,255,0.08),transparent_28%),radial-gradient(circle_at_80%_16%,rgba(255,156,105,0.06),transparent_26%),linear-gradient(180deg,rgba(255,255,255,0.02),transparent_34%)]" />

      <header className="sticky top-0 z-40 border-b border-line/80 bg-[rgba(7,11,19,0.82)] backdrop-blur-xl">
        <div className="mx-auto flex max-w-[1500px] items-center justify-between gap-6 px-4 py-4 sm:px-6 lg:px-8">
          <a href="#hero" className="shrink-0">
            <p className="font-mono text-[11px] uppercase tracking-[0.34em] text-seismic/75">
              CAT 411
            </p>
            <p className="mt-1 font-display text-xl tracking-[-0.04em] text-ink">
              Northridge Bridge Intelligence Lab
            </p>
          </a>
          <nav className="hidden flex-wrap items-center justify-end gap-2 xl:flex">
            {NAV_ITEMS.map(([href, label]) => (
              <a
                key={href}
                href={`#${href}`}
                className="rounded-full border border-line bg-white/5 px-4 py-2 text-sm text-muted transition hover:border-seismic/20 hover:text-ink"
              >
                {label}
              </a>
            ))}
          </nav>
        </div>
      </header>

      <main className="relative mx-auto flex w-full max-w-[1500px] flex-col gap-24 px-4 pb-24 pt-6 sm:px-6 lg:px-8">
        <HeroSection data={data} assessment={assessment} />
        <OverviewSection data={data} />
        <HazardSection
          data={data}
          scenarioPga={activeInputs.scenarioPga}
          onScenarioChange={setScenarioPreview}
        />
        <AssetFragilitySection data={data} inputs={activeInputs} />
        <SviSection data={data} inputs={activeInputs} />
        <NdviSection data={data} ndviChange={activeInputs.ndviChange} onNdviChange={setNdviPreview} />
        <MlVulnerabilitySection data={data} />
        <ValidationSection data={data} />
        <DecisionDashboardSection
          data={data}
          mode={mode}
          inputs={activeInputs}
          assessment={assessment}
          onModeChange={setMode}
          onInputChange={updateInput}
          onLoadSample={loadSample}
          onReset={resetInputs}
        />
      </main>

      <footer className="border-t border-line bg-[rgba(7,11,19,0.86)]">
        <div className="mx-auto flex max-w-[1500px] flex-col gap-4 px-4 py-8 text-sm text-muted sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
          <p>
            Built from the CAT 411 Northridge bridge repository, exported research artifacts, and a
            synchronized structural bridge twin.
          </p>
          <p>
            {error
              ? 'The site fell back to non-repo data for some layers.'
              : `Using ${data.availability.repoData ? 'repo-backed' : 'fallback'} exports across ${DASHBOARD_MODES.length} dashboard modes.`}
          </p>
        </div>
      </footer>
    </div>
  )
}
