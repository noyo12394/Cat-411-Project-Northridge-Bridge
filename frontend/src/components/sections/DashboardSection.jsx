import { useCallback, useMemo, useState } from 'react'
import DashboardForm from '../dashboard/DashboardForm'
import DashboardResults from '../dashboard/DashboardResults'
import ModeTabs from '../dashboard/ModeTabs'
import PortfolioWorkbench from '../dashboard/PortfolioWorkbench'
import SectionHeading from '../common/SectionHeading'
import { createInitialInputs, DASHBOARD_MODES, runBridgeAssessment } from '../../lib/modelAdapter'

export default function DashboardSection({
  researchData,
  onBridgeStateChange,
  onEnsurePortfolioLoaded,
  portfolioLoading = false,
}) {
  const [mode, setMode] = useState('intrinsic')
  const [inputs, setInputs] = useState(() => createInitialInputs(null, researchData))
  const [replayToken, setReplayToken] = useState(0)
  const [showPortfolio, setShowPortfolio] = useState(false)
  const [result, setResult] = useState(() =>
    runBridgeAssessment(createInitialInputs(null, researchData), 'intrinsic', researchData),
  )

  const pushAssessment = useCallback(
    (nextInputs, nextMode, options = {}) => {
      const next = runBridgeAssessment(nextInputs, nextMode, researchData)
      setResult(next)
      onBridgeStateChange?.({
        score: next.vulnerabilityScore,
        visualState: next.visualState,
        replayToken: options.replayToken ?? 0,
      })
      return next
    },
    [onBridgeStateChange, researchData],
  )

  const modeMeta = useMemo(
    () => DASHBOARD_MODES.find((item) => item.id === mode) ?? DASHBOARD_MODES[0],
    [mode],
  )

  const portfolioBridges = useMemo(() => {
    if (Array.isArray(researchData.portfolio)) {
      return researchData.portfolio
    }
    return researchData.portfolio?.bridges ?? []
  }, [researchData.portfolio])

  const handleChange = (field, value) => {
    const nextInputs = { ...inputs, [field]: value }
    setInputs(nextInputs)
    pushAssessment(nextInputs, mode)
  }

  const handleModeChange = (nextMode) => {
    setMode(nextMode)
    const nextReplayToken = Date.now()
    setReplayToken(nextReplayToken)
    pushAssessment(inputs, nextMode, { replayToken: nextReplayToken })
  }

  const handleRun = (event) => {
    event.preventDefault()
    const nextReplayToken = Date.now()
    setReplayToken(nextReplayToken)
    pushAssessment(inputs, mode, { replayToken: nextReplayToken })
  }

  const handleReset = () => {
    const seeded = createInitialInputs(null, researchData)
    setInputs(seeded)
    const nextReplayToken = Date.now()
    setReplayToken(nextReplayToken)
    pushAssessment(seeded, mode, { replayToken: nextReplayToken })
  }

  const handleLoadSample = (sample) => {
    if (!sample) return
    const seeded = createInitialInputs(sample, researchData)
    setInputs(seeded)
    const nextReplayToken = Date.now()
    setReplayToken(nextReplayToken)
    pushAssessment(seeded, mode, { replayToken: nextReplayToken })
  }

  const handleOpenPortfolio = async () => {
    setShowPortfolio(true)
    await onEnsurePortfolioLoaded?.()
  }

  return (
    <section id="dashboard" className="space-y-8">
      <SectionHeading
        eyebrow="Centerpiece interactive dashboard"
        title="One interface, three carefully separated modes"
        description="The dashboard defaults to intrinsic vulnerability screening. Event damage and inspection prioritization are available as connected but separate views so the platform never treats hazard demand or traffic consequence as baseline structural vulnerability. The output panel also exposes a local explainable-AI layer for the currently selected bridge state."
      />
      <ModeTabs modes={DASHBOARD_MODES} activeMode={mode} onChange={handleModeChange} />
      <div className="grid gap-5 xl:grid-cols-[0.92fr_1.08fr]">
        <DashboardForm
          inputs={inputs}
          mode={mode}
          onChange={handleChange}
          onLoadSample={handleLoadSample}
          onReset={handleReset}
          sampleBridges={researchData.summary.sampleBridges}
          onRun={handleRun}
        />
        <DashboardResults result={result} modeMeta={modeMeta} replayToken={replayToken} />
      </div>
      {showPortfolio ? (
        portfolioLoading ? (
          <div className="rounded-[32px] border border-slate-200/70 bg-[linear-gradient(180deg,rgba(255,255,255,0.96)_0%,rgba(243,247,252,0.96)_100%)] p-6 shadow-[0_28px_70px_rgba(15,23,42,0.08)]">
            <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-500">Portfolio explorer</p>
            <h3 className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-950">
              Loading statewide bridge rows
            </h3>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
              We are loading the full statewide portfolio in the background so the rest of the dashboard stays responsive.
            </p>
          </div>
        ) : (
          <PortfolioWorkbench bridges={portfolioBridges} onLoadBridge={handleLoadSample} />
        )
      ) : (
        <div className="rounded-[32px] border border-slate-200/70 bg-[linear-gradient(180deg,rgba(255,255,255,0.96)_0%,rgba(243,247,252,0.96)_100%)] p-6 shadow-[0_28px_70px_rgba(15,23,42,0.08)]">
          <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-slate-500">Portfolio explorer</p>
          <h3 className="mt-2 text-2xl font-semibold tracking-[-0.04em] text-slate-950">
            Load the statewide bridge explorer on demand
          </h3>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600">
            The full bridge portfolio contains {researchData.summary.counts.totalBridges.toLocaleString()} rows.
            We defer that heavy explorer until you open it so the research dashboard paints faster and stays reliable on first load.
          </p>
          <button
            type="button"
            onClick={handleOpenPortfolio}
            className="mt-5 rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white shadow-[0_18px_40px_rgba(15,23,42,0.22)] transition hover:-translate-y-0.5"
          >
            Open statewide explorer
          </button>
        </div>
      )}
    </section>
  )
}
