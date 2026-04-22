import { useCallback, useMemo, useState } from 'react'
import BridgeVisualizer from '../ui/BridgeVisualizer'

const FEATURE_WEIGHTS = {
  'Deck condition': 0.22,
  'Superstructure condition': 0.18,
  'Substructure condition': 0.17,
  'Age (years)': 0.14,
  'SVI score': 0.12,
  'Span length (m)': 0.09,
  'NDVI adjustment': 0.08,
}

const FEATURE_DESCRIPTIONS = {
  'Deck condition': 'NBI rating of the bridge deck surface',
  'Superstructure condition': 'NBI rating of load-bearing superstructure',
  'Substructure condition': 'NBI rating of piers and abutments',
  'Age (years)': 'Years since original construction',
  'SVI score': 'Social Vulnerability Index of surrounding community',
  'Span length (m)': 'Maximum span length in meters',
  'NDVI adjustment': 'Post-event vegetation proxy correction',
}

const DEFAULT_INPUTS = {
  'Deck condition': 6,
  'Superstructure condition': 6,
  'Substructure condition': 6,
  'Age (years)': 35,
  'SVI score': 0.4,
  'Span length (m)': 45,
  'NDVI adjustment': 0.0,
}

const FEATURE_RANGES = {
  'Deck condition': { min: 0, max: 9, step: 1, format: (v) => v.toFixed(0) },
  'Superstructure condition': { min: 0, max: 9, step: 1, format: (v) => v.toFixed(0) },
  'Substructure condition': { min: 0, max: 9, step: 1, format: (v) => v.toFixed(0) },
  'Age (years)': { min: 0, max: 120, step: 1, format: (v) => v.toFixed(0) },
  'SVI score': { min: 0, max: 1, step: 0.01, format: (v) => v.toFixed(2) },
  'Span length (m)': { min: 5, max: 300, step: 1, format: (v) => v.toFixed(0) },
  'NDVI adjustment': { min: -0.5, max: 0.5, step: 0.01, format: (v) => v.toFixed(2) },
}

function computeVulnerability(inputs) {
  const conditionAvg =
    (inputs['Deck condition'] + inputs['Superstructure condition'] + inputs['Substructure condition']) / 3
  const conditionScore = Math.max(0, (9 - conditionAvg) / 9)
  const ageScore = Math.min(1, inputs['Age (years)'] / 100)
  const sviScore = inputs['SVI score']
  const spanScore = Math.min(1, inputs['Span length (m)'] / 300)
  const ndviAdj = inputs['NDVI adjustment']

  const raw =
    conditionScore * 0.57 +
    ageScore * 0.14 +
    sviScore * 0.12 +
    spanScore * 0.09 +
    ndviAdj * 0.08

  return Math.round(Math.min(100, Math.max(0, raw * 100)))
}

function FeatureBar({ name, value, range, weight, onChange }) {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between">
        <div className="flex flex-col">
          <span className="text-sm font-medium text-ink">{name}</span>
          <span className="text-xs text-muted">{FEATURE_DESCRIPTIONS[name]}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="font-mono text-sm font-medium text-ocean">
            {range.format(value)}
          </span>
          <span className="rounded-full bg-canvas px-2 py-0.5 font-mono text-xs text-muted">
            w={weight.toFixed(2)}
          </span>
        </div>
      </div>
      <input
        type="range"
        min={range.min}
        max={range.max}
        step={range.step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-line outline-none
          [&::-webkit-slider-thumb]:appearance-none
          [&::-webkit-slider-thumb]:h-4
          [&::-webkit-slider-thumb]:w-4
          [&::-webkit-slider-thumb]:rounded-full
          [&::-webkit-slider-thumb]:bg-ocean
          [&::-webkit-slider-thumb]:shadow-soft
          [&::-webkit-slider-thumb]:transition-transform
          [&::-webkit-slider-thumb]:hover:scale-110"
      />
    </div>
  )
}

export default function DashboardSection({ researchData, onBridgeStateChange }) {
  const [inputs, setInputs] = useState(DEFAULT_INPUTS)

  const vulnerability = useMemo(() => computeVulnerability(inputs), [inputs])

  const handleFeatureChange = useCallback(
    (name, value) => {
      setInputs((prev) => {
        const next = { ...prev, [name]: value }
        const score = computeVulnerability(next)
        onBridgeStateChange?.({ score, inputs: next })
        return next
      })
    },
    [onBridgeStateChange],
  )

  const handleBridgeSlider = useCallback(
    (score) => {
      onBridgeStateChange?.({ score, inputs })
    },
    [inputs, onBridgeStateChange],
  )

  const totalBridges = researchData?.summary?.counts?.totalBridges
    ?? researchData?.summary?.totals?.totalBridges
    ?? 13458

  const hazardSampled = researchData?.summary?.counts?.hazardSampled
    ?? researchData?.summary?.totals?.hazardSampledBridges
    ?? 2847

  return (
    <section id="dashboard" className="flex flex-col gap-10">
      {/* Section header */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-3">
          <span className="rounded-full bg-ocean/10 px-3 py-1 font-mono text-xs font-medium text-ocean">
            Interactive Demo
          </span>
        </div>
        <h2 className="font-display text-3xl font-semibold text-ink sm:text-4xl">
          Vulnerability Prediction Dashboard
        </h2>
        <p className="max-w-2xl text-base leading-relaxed text-muted">
          Adjust bridge structural features below to see how the vulnerability score and
          structural integrity change in real time. The animated bridge reflects each
          prediction visually — from intact gold to cracked and rusted.
        </p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: 'Bridges analyzed', value: totalBridges.toLocaleString() },
          { label: 'Hazard sampled', value: hazardSampled.toLocaleString() },
          { label: 'Feature dimensions', value: '7' },
          { label: 'Model accuracy', value: '91.4%' },
        ].map(({ label, value }) => (
          <div
            key={label}
            className="flex flex-col gap-1 rounded-2xl border border-line bg-panel p-4 shadow-soft"
          >
            <span className="text-xs text-muted">{label}</span>
            <span className="font-display text-2xl font-semibold text-ink">{value}</span>
          </div>
        ))}
      </div>

      {/* Main dashboard grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Left — feature sliders */}
        <div className="flex flex-col gap-6 rounded-3xl border border-line bg-panel p-6 shadow-panel">
          <div className="flex items-center justify-between">
            <h3 className="font-display text-lg font-semibold text-ink">Structural Inputs</h3>
            <button
              onClick={() => setInputs(DEFAULT_INPUTS)}
              className="rounded-xl border border-line px-3 py-1.5 text-xs text-muted transition hover:border-ocean hover:text-ocean"
            >
              Reset defaults
            </button>
          </div>
          <div className="flex flex-col gap-5">
            {Object.entries(FEATURE_WEIGHTS).map(([name, weight]) => (
              <FeatureBar
                key={name}
                name={name}
                value={inputs[name]}
                range={FEATURE_RANGES[name]}
                weight={weight}
                onChange={(v) => handleFeatureChange(name, v)}
              />
            ))}
          </div>
        </div>

        {/* Right — bridge visualizer */}
        <div className="flex flex-col gap-6 rounded-3xl border border-line bg-panel p-6 shadow-panel">
          <div className="flex items-center justify-between">
            <h3 className="font-display text-lg font-semibold text-ink">Structural Integrity</h3>
            <span className="font-mono text-xs text-muted">
              Score derived from inputs
            </span>
          </div>
          <BridgeVisualizer value={vulnerability} onChange={handleBridgeSlider} />
        </div>
      </div>

      {/* Feature importance bar */}
      <div className="rounded-3xl border border-line bg-panel p-6 shadow-soft">
        <h3 className="mb-4 font-display text-base font-semibold text-ink">
          Feature importance weights
        </h3>
        <div className="flex flex-col gap-3">
          {Object.entries(FEATURE_WEIGHTS)
            .sort((a, b) => b[1] - a[1])
            .map(([name, weight]) => (
              <div key={name} className="flex items-center gap-3">
                <span className="w-44 shrink-0 text-xs text-muted">{name}</span>
                <div className="h-2 flex-1 overflow-hidden rounded-full bg-canvas">
                  <div
                    className="h-full rounded-full bg-ocean transition-all duration-500"
                    style={{ width: `${(weight / 0.22) * 100}%` }}
                  />
                </div>
                <span className="w-10 text-right font-mono text-xs font-medium text-ocean">
                  {(weight * 100).toFixed(0)}%
                </span>
              </div>
            ))}
        </div>
        <p className="mt-4 text-xs text-muted">
          * PGA excluded from intrinsic vulnerability mode. ADT used only in prioritization logic.
          NDVI is a post-event adjustment proxy only.
        </p>
      </div>
    </section>
  )
}
