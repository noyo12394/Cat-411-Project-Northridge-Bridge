import { useState } from 'react'
import { BarChart3 } from 'lucide-react'
import SectionHeader from '../common/SectionHeader'
import SurfaceCard from '../common/SurfaceCard'
import SectionShell from '../layout/SectionShell'
import DashboardForm from '../dashboard/DashboardForm'
import DashboardResults from '../dashboard/DashboardResults'
import { emptyBridgeInput, sampleBridges } from '../../data/sampleBridges'
import { runBridgePrediction } from '../../lib/predictionEngine'

export default function InteractiveDashboardSection() {
  const [sampleIndex, setSampleIndex] = useState(0)
  const [formValues, setFormValues] = useState(sampleBridges[0].values)
  const [result, setResult] = useState(() => runBridgePrediction(sampleBridges[0].values))

  const handleFieldChange = (event) => {
    const { name, value } = event.target
    setFormValues((current) => ({
      ...current,
      [name]: value,
    }))
  }

  const handlePredict = () => {
    setResult(runBridgePrediction(formValues))
  }

  const handleReset = () => {
    setFormValues(emptyBridgeInput)
    setResult(runBridgePrediction(emptyBridgeInput))
  }

  const handleLoadSample = () => {
    const nextIndex = (sampleIndex + 1) % sampleBridges.length
    const nextSample = sampleBridges[nextIndex]
    setSampleIndex(nextIndex)
    setFormValues(nextSample.values)
    setResult(runBridgePrediction(nextSample.values))
  }

  return (
    <SectionShell id="dashboard" className="overflow-hidden">
      <SectionHeader
        eyebrow="Interactive dashboard"
        title="A dashboard built like an infrastructure risk platform"
        description="This centerpiece demonstrates the decision-support idea directly. The input panel focuses on intrinsic bridge features, the output panel keeps the predictions interpretable, and the consequence layer is separated from the core vulnerability estimate."
      />

      <SurfaceCard className="mt-8 flex items-start gap-4 bg-gradient-to-r from-ocean/7 via-white to-violet/6 p-6">
        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-ink text-white shadow-soft">
          <BarChart3 className="h-5 w-5" />
        </div>
        <div className="space-y-2">
          <h3 className="font-display text-xl font-semibold tracking-[-0.03em] text-ink">Mock prediction engine, real interface logic</h3>
          <p className="text-sm leading-7 text-muted">
            The current dashboard uses weighted, interpretable logic based on condition, age, skew, SVI, span length, span count,
            and bridge class. NDVI is optional and post-event only. ADT is used only for prioritization and disruption screening.
          </p>
        </div>
      </SurfaceCard>

      <div className="mt-8 grid gap-5 xl:grid-cols-[0.98fr_1.02fr]">
        <DashboardForm
          values={formValues}
          onFieldChange={handleFieldChange}
          onPredict={handlePredict}
          onReset={handleReset}
          onLoadSample={handleLoadSample}
          activeSampleName={sampleBridges[sampleIndex].name}
        />
        <DashboardResults result={result} />
      </div>
    </SectionShell>
  )
}
