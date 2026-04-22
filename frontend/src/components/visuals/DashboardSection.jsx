import { useCallback, useMemo, useState } from 'react'
import BridgeVisualizer from '../visuals/BridgeVisualizer'

// Mirrors SVI_WEIGHTS from svi_methodology.py exactly
const SVI_WEIGHTS = {
  'Year built':         0.20,
  'Condition rating':   0.20,
  'Skew angle (°)':     0.15,
  'Span continuity':    0.15,
  'Material type':      0.10,
  'Max span (m)':       0.10,
  'Number of spans':    0.10,
}

const FEATURE_META = {
  'Year built':         { min: 1900, max: 2024, step: 1,    format: v => v.toFixed(0),  desc: 'YEAR_BUILT_027 — pre-1971 bridges score highest' },
  'Condition rating':   { min: 0,    max: 9,    step: 0.1,  format: v => v.toFixed(1),  desc: 'SUBSTRUCTURE_COND_060 — lower rating = higher vulnerability' },
  'Skew angle (°)':     { min: 0,    max: 90,   step: 1,    format: v => v.toFixed(0),  desc: 'DEGREES_SKEW_034 — larger skew increases vulnerability' },
  'Span continuity':    { min: 0,    max: 1,    step: 1,    format: v => v===1?'Simply supported':'Continuous', desc: 'STRUCTURE_KIND_043A — simply supported = more vulnerable' },
  'Material type':      { min: 0,    max: 2,    step: 1,    format: v => ['Steel','Concrete','Wood'][Math.round(v)], desc: 'STRUCTURE_KIND_043A — wood > concrete > steel' },
  'Max span (m)':       { min: 5,    max: 250,  step: 1,    format: v => v.toFixed(0),  desc: 'MAX_SPAN_LEN_MT_048 — longer spans score higher' },
  'Number of spans':    { min: 1,    max: 20,   step: 1,    format: v => v.toFixed(0),  desc: 'MAIN_UNIT_SPANS_045 — more spans = more complex exposure' },
}

const DEFAULTS = {
  'Year built':       1975,
  'Condition rating': 6,
  'Skew angle (°)':   10,
  'Span continuity':  1,
  'Material type':    1,
  'Max span (m)':     45,
  'Number of spans':  3,
}

// Mirrors scoring functions from svi_methodology.py
function yearScore(y)        { if (y < 1971) return 1.0; if (y <= 1989) return 0.7; return 0.4 }
function conditionScore(c)   { return Math.max(0, Math.min(1, (9 - c) / 9)) }
function skewScore(s)        { return Math.min(1, Math.max(0, s) / 30) }
function continuityScore(k)  { return k === 1 ? 1.0 : 0.0 }   // 1=simply supported, 0=continuous
function materialScore(m)    { return [0.5, 0.85, 1.0][Math.round(m)] ?? 0.85 }
function maxSpanScore(sp)    { return Math.min(1, sp / 250) }
function numSpansScore(n)    {
  if (n === 1) return 0.0
  if (n <= 3)  return 0.25
  if (n <= 6)  return 0.5
  return 0.85
}

function computeSVI(inputs) {
  const scores = {
    'Year built':       yearScore(inputs['Year built']),
    'Condition rating': conditionScore(inputs['Condition rating']),
    'Skew angle (°)':   skewScore(inputs['Skew angle (°)']),
    'Span continuity':  continuityScore(inputs['Span continuity']),
    'Material type':    materialScore(inputs['Material type']),
    'Max span (m)':     maxSpanScore(inputs['Max span (m)']),
    'Number of spans':  numSpansScore(inputs['Number of spans']),
  }
  const raw = Object.entries(SVI_WEIGHTS).reduce((sum,[k,w]) => sum + scores[k]*w, 0)
  return { svi: Math.round(Math.min(1, Math.max(0, raw)) * 100), scores }
}

function FeatureSlider({ name, value, onChange }) {
  const meta = FEATURE_META[name]
  const weight = SVI_WEIGHTS[name]
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-start justify-between gap-2">
        <div className="flex flex-col">
          <span className="text-sm font-medium text-ink">{name}</span>
          <span className="text-xs text-muted">{meta.desc}</span>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <span className="font-mono text-sm font-medium text-ocean">
            {meta.format(value)}
          </span>
          <span className="rounded-full bg-canvas px-2 py-0.5 font-mono text-xs text-muted">
            {(weight * 100).toFixed(0)}%
          </span>
        </div>
      </div>
      <input
        type="range" min={meta.min} max={meta.max} step={meta.step} value={value}
        onChange={e => onChange(parseFloat(e.target.value))}
        className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-line outline-none
          [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4
          [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:rounded-full
          [&::-webkit-slider-thumb]:bg-ocean [&::-webkit-slider-thumb]:shadow-soft
          [&::-webkit-slider-thumb]:transition-transform [&::-webkit-slider-thumb]:hover:scale-110"
      />
    </div>
  )
}

export default function DashboardSection({ researchData, onBridgeStateChange }) {
  const [inputs, setInputs] = useState(DEFAULTS)

  const { svi, scores } = useMemo(() => computeSVI(inputs), [inputs])

  const handleChange = useCallback((name, value) => {
    setInputs(prev => {
      const next = { ...prev, [name]: value }
      const { svi: s } = computeSVI(next)
      onBridgeStateChange?.({ score: s, inputs: next })
      return next
    })
  }, [onBridgeStateChange])

  const totalBridges   = researchData?.summary?.counts?.totalBridges ?? researchData?.summary?.totals?.totalBridges ?? 13458
  const hazardSampled  = researchData?.summary?.counts?.hazardSampled ?? researchData?.summary?.totals?.hazardSampledBridges ?? 2847

  return (
    <section id="dashboard" className="flex flex-col gap-10">
      {/* Header */}
      <div className="flex flex-col gap-3">
        <span className="w-fit rounded-full bg-ocean/10 px-3 py-1 font-mono text-xs font-medium text-ocean">
          Interactive SVI Demo
        </span>
        <h2 className="font-display text-3xl font-semibold text-ink sm:text-4xl">
          Vulnerability Prediction Dashboard
        </h2>
        <p className="max-w-2xl text-base leading-relaxed text-muted">
          Adjust bridge structural parameters to compute a real-time Seismic Vulnerability Index
          using the exact weights and scoring functions from the team's April 2026 methodology.
          The bridge animation responds directly to your predicted SVI score.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: 'Bridges in inventory', value: totalBridges.toLocaleString() },
          { label: 'Hazard-sampled',        value: hazardSampled.toLocaleString() },
          { label: 'SVI parameters',         value: '7' },
          { label: 'Current SVI score',      value: `${svi}%` },
        ].map(({ label, value }) => (
          <div key={label} className="flex flex-col gap-1 rounded-2xl border border-line bg-panel p-4 shadow-soft">
            <span className="text-xs text-muted">{label}</span>
            <span className="font-display text-2xl font-semibold text-ink">{value}</span>
          </div>
        ))}
      </div>

      {/* Main grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Sliders */}
        <div className="flex flex-col gap-6 rounded-3xl border border-line bg-panel p-6 shadow-panel">
          <div className="flex items-center justify-between">
            <h3 className="font-display text-lg font-semibold text-ink">SVI Parameters</h3>
            <button
              onClick={() => setInputs(DEFAULTS)}
              className="rounded-xl border border-line px-3 py-1.5 text-xs text-muted transition hover:border-ocean hover:text-ocean"
            >
              Reset
            </button>
          </div>
          <div className="flex flex-col gap-5">
            {Object.keys(SVI_WEIGHTS).map(name => (
              <FeatureSlider key={name} name={name} value={inputs[name]}
                onChange={v => handleChange(name, v)} />
            ))}
          </div>
        </div>

        {/* Bridge */}
        <div className="flex flex-col gap-6 rounded-3xl border border-line bg-panel p-6 shadow-panel">
          <div className="flex items-center justify-between">
            <h3 className="font-display text-lg font-semibold text-ink">Structural Integrity</h3>
            <span className="font-mono text-xs text-muted">SVI = {(svi/100).toFixed(2)}</span>
          </div>
          <BridgeVisualizer value={svi} />
        </div>
      </div>

      {/* Component score bars */}
      <div className="rounded-3xl border border-line bg-panel p-6 shadow-soft">
        <h3 className="mb-5 font-display text-base font-semibold text-ink">
          Component score breakdown
        </h3>
        <div className="flex flex-col gap-3">
          {Object.entries(SVI_WEIGHTS)
            .sort((a,b) => b[1]-a[1])
            .map(([name, weight]) => {
              const score = scores[name] ?? 0
              return (
                <div key={name} className="flex items-center gap-3">
                  <span className="w-40 shrink-0 text-xs text-muted">{name}</span>
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-canvas">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{
                        width: `${score * 100}%`,
                        background: score > 0.7 ? '#e15d50' : score > 0.4 ? '#ffb547' : '#1f5fbf',
                      }}
                    />
                  </div>
                  <span className="w-8 text-right font-mono text-xs text-muted">
                    {(weight * 100).toFixed(0)}%
                  </span>
                  <span className="w-8 text-right font-mono text-xs font-medium text-ink">
                    {score.toFixed(2)}
                  </span>
                </div>
              )
            })}
        </div>
        <p className="mt-4 text-xs text-muted">
          Score bars show each parameter's raw vulnerability score (0–1). Column weights show
          that parameter's share of the final SVI. PGA excluded from intrinsic vulnerability mode.
        </p>
      </div>
    </section>
  )
}
