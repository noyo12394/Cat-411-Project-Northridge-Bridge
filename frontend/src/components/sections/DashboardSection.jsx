import { useCallback, useMemo, useState } from 'react'
import DashboardForm from '../dashboard/DashboardForm'
import DashboardResults from '../dashboard/DashboardResults'
import ModeTabs from '../dashboard/ModeTabs'
import PortfolioWorkbench from '../dashboard/PortfolioWorkbench'
import SectionHeading from '../common/SectionHeading'
import { createInitialInputs, DASHBOARD_MODES, runBridgeAssessment } from '../../lib/modelAdapter'

export default function DashboardSection({ researchData, onBridgeStateChange }) {
  const [mode, setMode] = useState('intrinsic')
  const [inputs, setInputs] = useState(() => createInitialInputs(null, researchData))
  const [result, setResult] = useState(() =>
    runBridgeAssessment(createInitialInputs(null, researchData), 'intrinsic', researchData),
  )

  const pushAssessment = useCallback(
    (nextInputs, nextMode) => {
      const next = runBridgeAssessment(nextInputs, nextMode, researchData)
      setResult(next)
      onBridgeStateChange?.({ score: next.vulnerabilityScore, visualState: next.visualState })
      return next
    },
    [onBridgeStateChange, researchData],
  )

  const modeMeta = useMemo(
    () => DASHBOARD_MODES.find((item) => item.id === mode) ?? DASHBOARD_MODES[0],
    [mode],
  )

  const handleChange = (field, value) => {
    setInputs((current) => ({ ...current, [field]: value }))
  }

  const handleModeChange = (nextMode) => {
    setMode(nextMode)
    pushAssessment(inputs, nextMode)
  }

  const handleRun = (event) => {
    event.preventDefault()
    pushAssessment(inputs, mode)
  }

  const handleReset = () => {
    const seeded = createInitialInputs(null, researchData)
    setInputs(seeded)
    pushAssessment(seeded, mode)
  }

  const handleLoadSample = (sample) => {
    if (!sample) return
    const seeded = createInitialInputs(sample, researchData)
    setInputs(seeded)
    pushAssessment(seeded, mode)
  }

  return (
    <section id="dashboard" className="space-y-8">
      <SectionHeading
        eyebrow="Centerpiece interactive dashboard"
        title="One interface, three carefully separated modes"
        description="The dashboard defaults to intrinsic vulnerability screening. Event damage and inspection prioritization are available as connected but separate views so the platform never treats hazard demand or traffic consequence as baseline structural vulnerability."
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
        <DashboardResults result={result} modeMeta={modeMeta} />
      </div>
      <PortfolioWorkbench bridges={researchData.portfolio} onLoadBridge={handleLoadSample} />
    </section>
  )
}
