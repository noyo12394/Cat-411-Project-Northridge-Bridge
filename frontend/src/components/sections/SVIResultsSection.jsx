import { useCallback, useEffect, useMemo, useState } from 'react'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from 'recharts'
import EnhancedBridgeVisualizer from '../visuals/EnhancedBridgeVisualizer'

const SVI_WEIGHTS = {
  'Year built': 0.20,
  'Condition': 0.20,
  'Skew': 0.15,
  'Continuity': 0.15,
  'Material': 0.10,
  'Max span': 0.10,
  'Number of spans': 0.10,
}

const FRAGILITY_MU_BOUNDS = {
  slight: [0.25, 0.80],
  moderate: [0.35, 1.00],
  extensive: [0.45, 1.20],
  complete: [0.70, 1.70],
}

const HAZUS_HWB6 = {
  slight: { theta: 0.25, beta: 0.60 },
  moderate: { theta: 0.35, beta: 0.60 },
  extensive: { theta: 0.45, beta: 0.60 },
  complete: { theta: 0.70, beta: 0.60 },
}

const DAMAGE_WEIGHTS = { DS0: 0, DS1: 0.03, DS2: 0.08, DS3: 0.25, DS4: 1.0 }

const DEFAULT_INPUTS = {
  yearBuilt: 1970,
  yearReconstructed: null,
  conditionRating: 6,
  skewDegrees: 10,
  continuous: false,
  material: 'concrete',
  maxSpanM: 30,
  numSpans: 3,
  pga: 0.30,
}

const SVI_DISTRIBUTION = [
  { bin: 0.20, count: 2 }, { bin: 0.22, count: 41 }, { bin: 0.24, count: 178 },
  { bin: 0.25, count: 290 }, { bin: 0.27, count: 224 }, { bin: 0.29, count: 236 },
  { bin: 0.30, count: 384 }, { bin: 0.32, count: 373 }, { bin: 0.34, count: 442 },
  { bin: 0.35, count: 485 }, { bin: 0.37, count: 1052 }, { bin: 0.38, count: 823 },
  { bin: 0.40, count: 887 }, { bin: 0.41, count: 835 }, { bin: 0.43, count: 791 },
  { bin: 0.44, count: 894 }, { bin: 0.46, count: 969 }, { bin: 0.48, count: 774 },
  { bin: 0.49, count: 1003 }, { bin: 0.51, count: 1053 }, { bin: 0.52, count: 942 },
  { bin: 0.54, count: 841 }, { bin: 0.55, count: 473 }, { bin: 0.57, count: 485 },
  { bin: 0.58, count: 477 }, { bin: 0.60, count: 373 }, { bin: 0.61, count: 212 },
  { bin: 0.63, count: 446 }, { bin: 0.64, count: 203 }, { bin: 0.66, count: 313 },
  { bin: 0.68, count: 106 }, { bin: 0.69, count: 82 }, { bin: 0.71, count: 49 },
  { bin: 0.72, count: 26 }, { bin: 0.74, count: 20 }, { bin: 0.75, count: 3 },
  { bin: 0.77, count: 6 }, { bin: 0.80, count: 2 }, { bin: 0.82, count: 1 },
]

const BETA_DISTRIBUTION = [
  { bin: 0.641, count: 13 }, { bin: 0.645, count: 72 }, { bin: 0.649, count: 426 },
  { bin: 0.654, count: 310 }, { bin: 0.658, count: 422 }, { bin: 0.662, count: 485 },
  { bin: 0.666, count: 617 }, { bin: 0.670, count: 1016 }, { bin: 0.675, count: 1169 },
  { bin: 0.679, count: 1249 }, { bin: 0.683, count: 1001 }, { bin: 0.687, count: 1157 },
  { bin: 0.692, count: 1264 }, { bin: 0.696, count: 1212 }, { bin: 0.700, count: 1323 },
  { bin: 0.704, count: 1234 }, { bin: 0.708, count: 876 }, { bin: 0.713, count: 631 },
  { bin: 0.717, count: 590 }, { bin: 0.721, count: 405 }, { bin: 0.725, count: 513 },
  { bin: 0.730, count: 434 }, { bin: 0.734, count: 148 }, { bin: 0.738, count: 122 },
  { bin: 0.742, count: 59 }, { bin: 0.747, count: 32 }, { bin: 0.751, count: 7 },
  { bin: 0.755, count: 6 }, { bin: 0.759, count: 2 }, { bin: 0.763, count: 1 },
]

const EDR_COMPARISON = [
  { bin: 0.01, svi: 330, hazus: 619 }, { bin: 0.02, svi: 260, hazus: 318 },
  { bin: 0.03, svi: 171, hazus: 219 }, { bin: 0.04, svi: 121, hazus: 104 },
  { bin: 0.05, svi: 89, hazus: 88 }, { bin: 0.06, svi: 94, hazus: 87 },
  { bin: 0.07, svi: 72, hazus: 57 }, { bin: 0.08, svi: 47, hazus: 70 },
  { bin: 0.09, svi: 34, hazus: 122 }, { bin: 0.10, svi: 41, hazus: 63 },
  { bin: 0.12, svi: 38, hazus: 77 }, { bin: 0.14, svi: 44, hazus: 75 },
  { bin: 0.16, svi: 29, hazus: 29 }, { bin: 0.18, svi: 33, hazus: 33 },
  { bin: 0.20, svi: 35, hazus: 17 }, { bin: 0.22, svi: 28, hazus: 39 },
  { bin: 0.24, svi: 26, hazus: 34 }, { bin: 0.26, svi: 27, hazus: 55 },
  { bin: 0.28, svi: 18, hazus: 41 }, { bin: 0.30, svi: 21, hazus: 40 },
  { bin: 0.32, svi: 13, hazus: 29 }, { bin: 0.34, svi: 19, hazus: 35 },
  { bin: 0.36, svi: 14, hazus: 23 }, { bin: 0.38, svi: 24, hazus: 15 },
  { bin: 0.40, svi: 25, hazus: 16 }, { bin: 0.45, svi: 89, hazus: 51 },
]

const PGA_EDR = [
  { pga: 0.046, svi: 0.00002, hazus: 0.00011 },
  { pga: 0.067, svi: 0.00017, hazus: 0.0009 },
  { pga: 0.096, svi: 0.00068, hazus: 0.0034 },
  { pga: 0.138, svi: 0.00306, hazus: 0.01333 },
  { pga: 0.198, svi: 0.0122, hazus: 0.04381 },
  { pga: 0.285, svi: 0.03674, hazus: 0.11787 },
  { pga: 0.410, svi: 0.09176, hazus: 0.2514 },
  { pga: 0.589, svi: 0.20836, hazus: 0.45685 },
  { pga: 0.848, svi: 0.33914, hazus: 0.63391 },
]

const COMPONENT_MEANS = [
  { name: 'Material', value: 0.828, weight: 0.10 },
  { name: 'Year built', value: 0.800, weight: 0.20 },
  { name: 'Skew', value: 0.468, weight: 0.15 },
  { name: 'Continuity', value: 0.422, weight: 0.15 },
  { name: 'Num spans', value: 0.266, weight: 0.10 },
  { name: 'Condition', value: 0.253, weight: 0.20 },
  { name: 'Max span', value: 0.085, weight: 0.10 },
]

function normCDF(x) {
  const t = 1 / (1 + 0.2316419 * Math.abs(x))
  const d = 0.3989423 * Math.exp(-0.5 * x * x)
  const p = d * t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
  return x > 0 ? 1 - p : p
}

function fragilityProb(pga, theta, beta) {
  if (pga <= 0 || theta <= 0 || beta <= 0) return 0
  return normCDF(Math.log(pga / theta) / beta)
}

function muLinear(svi, ds) {
  const [min, max] = FRAGILITY_MU_BOUNDS[ds]
  return min + svi * (max - min)
}

function muExp(svi, ds) {
  const [min, max] = FRAGILITY_MU_BOUNDS[ds]
  return max * Math.pow(min / max, 1 - svi)
}

function betaFromSVI(svi) {
  return 0.6 + 0.2 * svi
}

function yearBuiltScore(year) {
  if (year < 1971) return 1.0
  if (year <= 1989) return 0.70
  return 0.40
}

function conditionScore(cr) {
  return Math.max(0, Math.min(1, (9 - cr) / 9))
}

function skewScore(deg) {
  return Math.min(1, Math.max(0, deg) / 30)
}

function continuityScore(continuous) {
  return continuous ? 0.0 : 1.0
}

function materialScore(material) {
  if (material === 'wood') return 1.0
  if (material === 'concrete') return 0.85
  if (material === 'steel') return 0.50
  return 0.85
}

function maxSpanScore(lengthM) {
  return Math.min(1, Math.max(0, lengthM) / 250)
}

function numSpansScore(n) {
  if (n === 1) return 0.0
  if (n <= 3) return 0.25
  if (n <= 6) return 0.50
  return 0.85
}

function reconstructionMultiplier(yearRecon) {
  if (!yearRecon) return 1.0
  if (yearRecon > 1989) return 0.90
  if (yearRecon >= 1971) return 0.95
  return 1.0
}

function computeSVI(inputs) {
  const scores = {
    year_built: yearBuiltScore(inputs.yearBuilt),
    condition: conditionScore(inputs.conditionRating),
    skew: skewScore(inputs.skewDegrees),
    continuity: continuityScore(inputs.continuous),
    material: materialScore(inputs.material),
    max_span: maxSpanScore(inputs.maxSpanM),
    num_spans: numSpansScore(inputs.numSpans),
  }
  const raw =
    scores.year_built * 0.20 +
    scores.condition * 0.20 +
    scores.skew * 0.15 +
    scores.continuity * 0.15 +
    scores.material * 0.10 +
    scores.max_span * 0.10 +
    scores.num_spans * 0.10
  const multiplier = reconstructionMultiplier(inputs.yearReconstructed)
  const svi = Math.min(1, Math.max(0, raw * multiplier))
  return { svi, raw, multiplier, scores }
}

function computeDamageStates(svi, pga, method = 'linear') {
  const muFn = method === 'linear' ? muLinear : muExp
  const b = betaFromSVI(svi)
  const pe1 = fragilityProb(pga, muFn(svi, 'slight'), b)
  const pe2 = fragilityProb(pga, muFn(svi, 'moderate'), b)
  const pe3 = fragilityProb(pga, muFn(svi, 'extensive'), b)
  const pe4 = fragilityProb(pga, muFn(svi, 'complete'), b)
  const probs = {
    DS0: Math.max(0, 1 - pe1),
    DS1: Math.max(0, pe1 - pe2),
    DS2: Math.max(0, pe2 - pe3),
    DS3: Math.max(0, pe3 - pe4),
    DS4: Math.max(0, pe4),
  }
  const edr =
    probs.DS1 * DAMAGE_WEIGHTS.DS1 +
    probs.DS2 * DAMAGE_WEIGHTS.DS2 +
    probs.DS3 * DAMAGE_WEIGHTS.DS3 +
    probs.DS4 * DAMAGE_WEIGHTS.DS4
  return { probs, edr, beta: b, mu: { slight: muFn(svi, 'slight'), moderate: muFn(svi, 'moderate'), extensive: muFn(svi, 'extensive'), complete: muFn(svi, 'complete') } }
}

const PGA_CURVE_POINTS = Array.from({ length: 80 }, (_, i) =>
  Math.exp(Math.log(0.01) + (i / 79) * (Math.log(2.0) - Math.log(0.01))),
)

function buildFragilityCurves(method) {
  return PGA_CURVE_POINTS.map((pga) => ({
    pga,
    pgaLabel: pga.toFixed(3),
    minSVI: fragilityProb(
      pga,
      method === 'linear' ? muLinear(0.193, 'slight') : muExp(0.193, 'slight'),
      betaFromSVI(0.193),
    ),
    medSVI: fragilityProb(
      pga,
      method === 'linear' ? muLinear(0.455, 'slight') : muExp(0.455, 'slight'),
      betaFromSVI(0.455),
    ),
    maxSVI: fragilityProb(
      pga,
      method === 'linear' ? muLinear(0.827, 'slight') : muExp(0.827, 'slight'),
      betaFromSVI(0.827),
    ),
  }))
}

function StatCard({ label, value, sub, accent = 'ocean' }) {
  const accentClass = {
    ocean: 'text-ocean',
    ember: 'text-ember',
    signal: 'text-signal',
    moss: 'text-moss',
    hazard: 'text-hazard',
  }[accent]

  return (
    <div className="flex flex-col gap-1 rounded-2xl border border-line bg-panel p-4 shadow-panel">
      <span className="text-xs text-muted">{label}</span>
      <span className={`font-display text-2xl font-semibold ${accentClass}`}>{value}</span>
      {sub && <span className="font-mono text-[10px] text-muted">{sub}</span>}
    </div>
  )
}

function ChartCard({ title, subtitle, children, note }) {
  return (
    <div className="flex flex-col gap-3 rounded-3xl border border-line bg-panel p-5 shadow-panel">
      <div className="flex flex-col">
        <h3 className="font-display text-sm font-semibold text-ink">{title}</h3>
        {subtitle && <p className="font-mono text-[11px] text-muted">{subtitle}</p>}
      </div>
      <div className="min-h-[240px]">{children}</div>
      {note && <p className="font-mono text-[10px] text-muted">{note}</p>}
    </div>
  )
}

function DarkTooltip({ active, payload, label, valueFormatter = (v) => v }) {
  if (!active || !payload || !payload.length) return null
  return (
    <div className="rounded-xl border border-line bg-canvas/95 px-3 py-2 shadow-panel backdrop-blur">
      {label !== undefined && (
        <div className="mb-1 font-mono text-[10px] uppercase tracking-wider text-muted">{label}</div>
      )}
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2 text-xs text-ink">
          <span className="h-2 w-2 rounded-full" style={{ background: p.color }} />
          <span className="text-muted">{p.name}</span>
          <span className="ml-auto font-mono font-medium">{valueFormatter(p.value)}</span>
        </div>
      ))}
    </div>
  )
}

function TabBtn({ active, onClick, children }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-full px-3 py-1 font-mono text-[11px] transition ${
        active
          ? 'bg-ocean/15 text-ocean shadow-[inset_0_0_0_1px_rgba(73,182,255,0.3)]'
          : 'border border-line text-muted hover:border-ocean/40 hover:text-ink'
      }`}
    >
      {children}
    </button>
  )
}

function InputRow({ label, children, hint }) {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-ink">{label}</span>
        {hint && <span className="font-mono text-[10px] text-muted">{hint}</span>}
      </div>
      {children}
    </div>
  )
}

export default function SVIResultsSection({ researchData, onBridgeStateChange }) {
  const [inputs, setInputs] = useState(DEFAULT_INPUTS)
  const [fragMethod, setFragMethod] = useState('linear')
  const [tableMethod, setTableMethod] = useState('linear')

  const { svi, raw, multiplier } = useMemo(() => computeSVI(inputs), [inputs])
  const damage = useMemo(
    () => computeDamageStates(svi, inputs.pga, fragMethod),
    [svi, inputs.pga, fragMethod],
  )

  const vulnerabilityPct = Math.round(svi * 100)
  const visualSeverity = useMemo(() => {
    const severeDamage = (damage.probs.DS3 ?? 0) + (damage.probs.DS4 ?? 0)
    const moderateDamage = damage.probs.DS2 ?? 0
    const edrNormalized = Math.min(1, damage.edr / 0.45)
    const eventStress = Math.min(1, severeDamage * 1.25 + moderateDamage * 0.55 + edrNormalized * 0.7)
    return Math.round(Math.min(100, vulnerabilityPct * 0.65 + eventStress * 45))
  }, [damage.edr, damage.probs.DS2, damage.probs.DS3, damage.probs.DS4, vulnerabilityPct])

  const fragilityCurvesLinear = useMemo(() => buildFragilityCurves('linear'), [])
  const fragilityCurvesExp = useMemo(() => buildFragilityCurves('exponential'), [])
  const currentFragilityCurves = fragMethod === 'linear' ? fragilityCurvesLinear : fragilityCurvesExp

  const handleInput = useCallback(
    (key, value) => {
      setInputs((prev) => ({ ...prev, [key]: value }))
    },
    [],
  )

  const resetInputs = useCallback(() => {
    setInputs(DEFAULT_INPUTS)
  }, [])

  const counts = researchData?.summary?.counts ?? {}
  const hazardSampled = counts.hazardSampled ?? counts.totalBridges ?? 16796
  const sviMean = researchData?.summary?.portfolio?.meanSVI ?? 0.455
  const sviMedian = researchData?.summary?.portfolio?.medianSVI ?? 0.45
  const featureSviRange = researchData?.summary?.featureRanges?.svi
  const sviRange = featureSviRange ? [featureSviRange.min, featureSviRange.max] : [0.193, 0.827]
  const betaRange = [betaFromSVI(sviRange[0]), betaFromSVI(sviRange[1])]
  const sviMeanEdr = researchData?.summary?.portfolio?.meanEDR ?? 0.0132
  const hazusMeanEdr = 0.0314
  const meanReduction = Math.max(0, 1 - sviMeanEdr / hazusMeanEdr)

  useEffect(() => {
    onBridgeStateChange?.({ score: visualSeverity / 100 })
  }, [onBridgeStateChange, visualSeverity])

  const tableData =
    tableMethod === 'linear'
      ? {
          slight: { mean: 0.500, min: 0.356, max: 0.705 },
          moderate: { mean: 0.646, min: 0.476, max: 0.888 },
          extensive: { mean: 0.791, min: 0.595, max: 1.071 },
          complete: { mean: 1.155, min: 0.893, max: 1.527 },
        }
      : {
          slight: { mean: 0.428, min: 0.313, max: 0.654 },
          moderate: { mean: 0.568, min: 0.429, max: 0.834 },
          extensive: { mean: 0.707, min: 0.544, max: 1.013 },
          complete: { mean: 1.053, min: 0.831, max: 1.459 },
        }

  const axisStyle = { fill: '#9db0c8', fontSize: 10, fontFamily: 'IBM Plex Mono' }
  const gridStroke = 'rgba(123,159,197,0.12)'

  return (
    <section id="svi-results" className="flex flex-col gap-10">
      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-3">
          <span className="rounded-full bg-ocean/10 px-3 py-1 font-mono text-xs font-medium text-ocean">
            SVI Results
          </span>
          <span className="rounded-full bg-signal/10 px-3 py-1 font-mono text-xs font-medium text-signal">
            April 2026 Methodology
          </span>
        </div>
        <h2 className="font-display text-3xl font-semibold text-ink sm:text-4xl">
          Seismic Vulnerability Index results
        </h2>
        <p className="max-w-3xl text-base leading-relaxed text-muted">
          Live exploration of the revised SVI framework applied to {hazardSampled.toLocaleString()} hazard-sampled
          California bridges. Tune structural inputs on the left to drive the fragility math end-to-end —
          SVI → μ{' '}→ β → damage states → EDR — and watch the bridge deform in real time.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatCard label="Bridges analyzed" value={hazardSampled.toLocaleString()} sub="SVI computed from hazard-sampled bridge rows" />
        <StatCard label="Mean SVI" value={sviMean.toFixed(3)} sub={`range ${sviRange[0].toFixed(3)} – ${sviRange[1].toFixed(3)}`} accent="ocean" />
        <StatCard label="Median SVI" value={sviMedian.toFixed(3)} sub="Portfolio median intrinsic vulnerability index" accent="signal" />
        <StatCard label="Dispersion β" value={`${betaRange[0].toFixed(2)} – ${betaRange[1].toFixed(2)}`} sub="β = 0.6 + 0.2·SVI" accent="moss" />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_1.1fr]">
        <div className="flex flex-col gap-5 rounded-3xl border border-line bg-panel p-6 shadow-panel">
          <div className="flex items-center justify-between">
            <h3 className="font-display text-lg font-semibold text-ink">Structural inputs</h3>
            <button
              onClick={resetInputs}
              className="rounded-xl border border-line px-3 py-1.5 text-xs text-muted transition hover:border-ocean hover:text-ocean"
            >
              Reset
            </button>
          </div>

          <InputRow label="Year built" hint={inputs.yearBuilt}>
            <input
              type="range"
              min="1900"
              max="2024"
              step="1"
              value={inputs.yearBuilt}
              onChange={(e) => handleInput('yearBuilt', parseInt(e.target.value))}
              className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-line
                [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4
                [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-ocean"
            />
          </InputRow>

          <InputRow label="Condition rating" hint={`${inputs.conditionRating} / 9`}>
            <input
              type="range" min="0" max="9" step="1"
              value={inputs.conditionRating}
              onChange={(e) => handleInput('conditionRating', parseInt(e.target.value))}
              className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-line
                [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4
                [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-ocean"
            />
          </InputRow>

          <InputRow label="Skew (degrees)" hint={`${inputs.skewDegrees}°`}>
            <input
              type="range" min="0" max="60" step="1"
              value={inputs.skewDegrees}
              onChange={(e) => handleInput('skewDegrees', parseInt(e.target.value))}
              className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-line
                [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4
                [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-ocean"
            />
          </InputRow>

          <InputRow label="Max span length" hint={`${inputs.maxSpanM} m`}>
            <input
              type="range" min="5" max="300" step="1"
              value={inputs.maxSpanM}
              onChange={(e) => handleInput('maxSpanM', parseInt(e.target.value))}
              className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-line
                [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4
                [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-ocean"
            />
          </InputRow>

          <InputRow label="Number of spans" hint={inputs.numSpans}>
            <input
              type="range" min="1" max="20" step="1"
              value={inputs.numSpans}
              onChange={(e) => handleInput('numSpans', parseInt(e.target.value))}
              className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-line
                [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4
                [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-ocean"
            />
          </InputRow>

          <InputRow label="PGA (g)" hint={`event layer only · ${inputs.pga.toFixed(2)}`}>
            <input
              type="range" min="0.01" max="1.5" step="0.01"
              value={inputs.pga}
              onChange={(e) => handleInput('pga', parseFloat(e.target.value))}
              className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-line
                [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4
                [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-ember"
            />
          </InputRow>

          <div className="grid grid-cols-2 gap-3">
            <InputRow label="Material">
              <select
                value={inputs.material}
                onChange={(e) => handleInput('material', e.target.value)}
                className="rounded-xl border border-line bg-canvas px-3 py-2 text-sm text-ink focus:border-ocean focus:outline-none"
              >
                <option value="wood">Wood</option>
                <option value="concrete">Concrete</option>
                <option value="steel">Steel</option>
              </select>
            </InputRow>
            <InputRow label="Continuity">
              <select
                value={inputs.continuous ? 'continuous' : 'simple'}
                onChange={(e) => handleInput('continuous', e.target.value === 'continuous')}
                className="rounded-xl border border-line bg-canvas px-3 py-2 text-sm text-ink focus:border-ocean focus:outline-none"
              >
                <option value="simple">Simply supported</option>
                <option value="continuous">Continuous</option>
              </select>
            </InputRow>
          </div>

          <div className="mt-2 grid grid-cols-2 gap-2 rounded-2xl border border-line bg-canvas/60 p-4">
            <div>
              <div className="font-mono text-[10px] uppercase tracking-wider text-muted">Raw SVI</div>
              <div className="font-display text-xl text-ink">{raw.toFixed(3)}</div>
            </div>
            <div>
              <div className="font-mono text-[10px] uppercase tracking-wider text-muted">Multiplier</div>
              <div className="font-display text-xl text-ink">{multiplier.toFixed(2)}</div>
            </div>
            <div>
              <div className="font-mono text-[10px] uppercase tracking-wider text-muted">SVI</div>
              <div className="font-display text-2xl font-semibold text-ocean">{svi.toFixed(3)}</div>
            </div>
            <div>
              <div className="font-mono text-[10px] uppercase tracking-wider text-muted">EDR @ PGA {inputs.pga.toFixed(2)}g</div>
              <div className="font-display text-2xl font-semibold text-ember">{damage.edr.toFixed(4)}</div>
            </div>
          </div>
        </div>

        <div className="flex flex-col gap-4 rounded-3xl border border-line bg-panel p-6 shadow-panel">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-display text-lg font-semibold text-ink">Structural integrity</h3>
              <p className="font-mono text-[11px] text-muted">
                Intrinsic SVI {svi.toFixed(3)} with event-damage response at PGA {inputs.pga.toFixed(2)}g
              </p>
            </div>
            <span className="font-mono text-xs text-ocean">{visualSeverity}%</span>
          </div>
          <EnhancedBridgeVisualizer
            vulnerability={vulnerabilityPct}
            svi={svi}
            edr={damage.edr}
            damageProbs={damage.probs}
            pga={inputs.pga}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <ChartCard
          title="SVI distribution"
          subtitle={`n = ${hazardSampled.toLocaleString()} · bin width ≈ 0.016`}
        >
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={SVI_DISTRIBUTION} margin={{ top: 8, right: 8, bottom: 8, left: 0 }}>
              <CartesianGrid stroke={gridStroke} strokeDasharray="2 4" vertical={false} />
              <XAxis
                dataKey="bin"
                tickFormatter={(v) => v.toFixed(2)}
                tick={axisStyle}
                axisLine={{ stroke: gridStroke }}
                tickLine={false}
              />
              <YAxis tick={axisStyle} axisLine={{ stroke: gridStroke }} tickLine={false} />
              <Tooltip
                content={<DarkTooltip valueFormatter={(v) => `${v} bridges`} />}
                cursor={{ fill: 'rgba(73,182,255,0.06)' }}
              />
              <ReferenceLine x={sviMean} stroke="#ffd166" strokeDasharray="3 3" label={{ value: `μ=${sviMean.toFixed(2)}`, fill: '#ffd166', fontSize: 10, position: 'top' }} />
              <ReferenceLine x={Math.round(svi * 1000) / 1000} stroke="#ff9c69" strokeWidth={2} label={{ value: 'you', fill: '#ff9c69', fontSize: 10, position: 'top' }} />
              <Bar dataKey="count" fill="#49b6ff" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="β dispersion distribution"
          subtitle={`β = 0.6 + 0.2·SVI · all ${hazardSampled.toLocaleString()} hazard-sampled bridges`}
        >
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={BETA_DISTRIBUTION} margin={{ top: 8, right: 8, bottom: 8, left: 0 }}>
              <CartesianGrid stroke={gridStroke} strokeDasharray="2 4" vertical={false} />
              <XAxis
                dataKey="bin"
                tickFormatter={(v) => v.toFixed(2)}
                tick={axisStyle}
                axisLine={{ stroke: gridStroke }}
                tickLine={false}
              />
              <YAxis tick={axisStyle} axisLine={{ stroke: gridStroke }} tickLine={false} />
              <Tooltip
                content={<DarkTooltip valueFormatter={(v) => `${v} bridges`} />}
                cursor={{ fill: 'rgba(102,209,166,0.06)' }}
              />
              <ReferenceLine x={Math.round(betaFromSVI(svi) * 1000) / 1000} stroke="#ff9c69" strokeWidth={2} label={{ value: 'you', fill: '#ff9c69', fontSize: 10, position: 'top' }} />
              <Bar dataKey="count" fill="#66d1a6" radius={[2, 2, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <ChartCard
        title="Fragility curves — P(damage state ≥ slight)"
        subtitle="Min (SVI 0.193) · Median (SVI 0.455) · Max (SVI 0.827) bridge envelopes"
        note="Your bridge's SVI curve is drawn in ember orange for direct comparison."
      >
        <div className="mb-3 flex items-center gap-2">
          <span className="font-mono text-[11px] text-muted">Method</span>
          <TabBtn active={fragMethod === 'linear'} onClick={() => setFragMethod('linear')}>Linear</TabBtn>
          <TabBtn active={fragMethod === 'exponential'} onClick={() => setFragMethod('exponential')}>Exponential</TabBtn>
        </div>
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={currentFragilityCurves} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
            <CartesianGrid stroke={gridStroke} strokeDasharray="2 4" />
            <XAxis
              dataKey="pga"
              type="number"
              scale="log"
              domain={[0.01, 2.0]}
              ticks={[0.01, 0.05, 0.1, 0.5, 1.0, 2.0]}
              tickFormatter={(v) => v < 0.1 ? v.toFixed(2) : v.toFixed(1)}
              tick={axisStyle}
              axisLine={{ stroke: gridStroke }}
              tickLine={false}
              label={{ value: 'PGA (g)', fill: '#9db0c8', fontSize: 11, position: 'insideBottom', offset: -2 }}
            />
            <YAxis
              domain={[0, 1]}
              tickFormatter={(v) => v.toFixed(1)}
              tick={axisStyle}
              axisLine={{ stroke: gridStroke }}
              tickLine={false}
              label={{ value: 'P(exceed)', fill: '#9db0c8', fontSize: 11, angle: -90, position: 'insideLeft' }}
            />
            <Tooltip
              content={<DarkTooltip valueFormatter={(v) => v.toFixed(3)} />}
              labelFormatter={(v) => `PGA ${v.toFixed(3)} g`}
            />
            <ReferenceLine x={inputs.pga} stroke="#ff9c69" strokeDasharray="3 3" label={{ value: `PGA ${inputs.pga.toFixed(2)}g`, fill: '#ff9c69', fontSize: 10, position: 'top' }} />
            <Line type="monotone" dataKey="minSVI" stroke="#49b6ff" strokeWidth={1.5} dot={false} name="Min SVI" />
            <Line type="monotone" dataKey="medSVI" stroke="#ffd166" strokeWidth={1.5} dot={false} name="Median SVI" />
            <Line type="monotone" dataKey="maxSVI" stroke="#f97373" strokeWidth={1.5} dot={false} name="Max SVI" />
            <Legend wrapperStyle={{ fontSize: 11, fontFamily: 'IBM Plex Mono', color: '#9db0c8' }} />
          </LineChart>
        </ResponsiveContainer>
      </ChartCard>

      <div className="rounded-3xl border border-line bg-panel p-6 shadow-panel">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h3 className="font-display text-sm font-semibold text-ink">Fragility median parameters</h3>
            <p className="font-mono text-[11px] text-muted">μ values derived from SVI ∈ [0.193, 0.827]</p>
          </div>
          <div className="flex gap-2">
            <TabBtn active={tableMethod === 'linear'} onClick={() => setTableMethod('linear')}>Linear</TabBtn>
            <TabBtn active={tableMethod === 'exponential'} onClick={() => setTableMethod('exponential')}>Exponential</TabBtn>
          </div>
        </div>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-4">
          {Object.entries(tableData).map(([ds, v]) => (
            <div key={ds} className="rounded-2xl border border-line bg-canvas/40 p-4">
              <div className="font-mono text-[10px] uppercase tracking-wider text-muted">
                DS{['slight', 'moderate', 'extensive', 'complete'].indexOf(ds) + 1} — {ds}
              </div>
              <div className="mt-1 font-display text-xl font-semibold text-ink">{v.mean.toFixed(3)} g</div>
              <div className="mt-1 font-mono text-[10px] text-muted">
                min {v.min.toFixed(3)} · max {v.max.toFixed(3)}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <ChartCard
          title="EDR distribution — SVI vs HAZUS benchmark"
          subtitle="Overlaid histograms (bridges with EDR > 0)"
          note="This comparison card uses a fixed HWB6 HAZUS benchmark curve as the reference fragility family: θ=0.25/0.35/0.45/0.70 g and β=0.60."
        >
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={EDR_COMPARISON} margin={{ top: 8, right: 8, bottom: 8, left: 0 }}>
              <CartesianGrid stroke={gridStroke} strokeDasharray="2 4" vertical={false} />
              <XAxis
                dataKey="bin"
                tickFormatter={(v) => v.toFixed(2)}
                tick={axisStyle}
                axisLine={{ stroke: gridStroke }}
                tickLine={false}
              />
              <YAxis tick={axisStyle} axisLine={{ stroke: gridStroke }} tickLine={false} />
              <Tooltip content={<DarkTooltip valueFormatter={(v) => v} />} cursor={{ fill: 'rgba(73,182,255,0.06)' }} />
              <Legend wrapperStyle={{ fontSize: 11, fontFamily: 'IBM Plex Mono', color: '#9db0c8' }} />
              <Bar dataKey="svi" fill="#49b6ff" name="SVI method" radius={[2, 2, 0, 0]} />
              <Bar dataKey="hazus" fill="#ff9c69" name="HAZUS HWB6" radius={[2, 2, 0, 0]} opacity={0.7} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard
          title="Mean EDR vs PGA"
          subtitle="Log-binned PGA · event-damage comparison"
        >
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={PGA_EDR} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
              <CartesianGrid stroke={gridStroke} strokeDasharray="2 4" />
              <XAxis
                dataKey="pga"
                type="number"
                scale="log"
                domain={[0.04, 1.0]}
                ticks={[0.05, 0.1, 0.2, 0.5, 1.0]}
                tickFormatter={(v) => v.toFixed(2)}
                tick={axisStyle}
                axisLine={{ stroke: gridStroke }}
                tickLine={false}
                label={{ value: 'PGA (g)', fill: '#9db0c8', fontSize: 11, position: 'insideBottom', offset: -2 }}
              />
              <YAxis
                tickFormatter={(v) => v.toFixed(2)}
                tick={axisStyle}
                axisLine={{ stroke: gridStroke }}
                tickLine={false}
                label={{ value: 'Mean EDR', fill: '#9db0c8', fontSize: 11, angle: -90, position: 'insideLeft' }}
              />
              <Tooltip content={<DarkTooltip valueFormatter={(v) => v.toFixed(4)} />} labelFormatter={(v) => `PGA ${v.toFixed(3)} g`} />
              <Legend wrapperStyle={{ fontSize: 11, fontFamily: 'IBM Plex Mono', color: '#9db0c8' }} />
              <Line type="monotone" dataKey="svi" stroke="#49b6ff" strokeWidth={2} dot={{ r: 3, fill: '#49b6ff' }} name="SVI method" />
              <Line type="monotone" dataKey="hazus" stroke="#ff9c69" strokeWidth={2} strokeDasharray="5 3" dot={{ r: 3, fill: '#ff9c69' }} name="HAZUS HWB6" />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <ChartCard
        title="SVI component scores — mean across 16,796 bridges"
        subtitle="Average score each parameter contributes before weighting"
        note="* Higher score = higher vulnerability contribution. Final SVI is the weighted sum × YR multiplier."
      >
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={COMPONENT_MEANS}
            layout="vertical"
            margin={{ top: 8, right: 40, bottom: 8, left: 8 }}
          >
            <CartesianGrid stroke={gridStroke} strokeDasharray="2 4" horizontal={false} />
            <XAxis
              type="number"
              domain={[0, 1]}
              tick={axisStyle}
              axisLine={{ stroke: gridStroke }}
              tickLine={false}
            />
            <YAxis
              type="category"
              dataKey="name"
              tick={{ ...axisStyle, fontSize: 11 }}
              axisLine={{ stroke: gridStroke }}
              tickLine={false}
              width={100}
            />
            <Tooltip
              content={<DarkTooltip valueFormatter={(v) => v.toFixed(3)} />}
              cursor={{ fill: 'rgba(73,182,255,0.06)' }}
            />
            <Bar dataKey="value" fill="#49b6ff" radius={[0, 4, 4, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <div className="rounded-3xl border border-line bg-panel p-6 shadow-panel">
        <h3 className="mb-4 font-display text-sm font-semibold text-ink">Method comparison summary</h3>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <div className="rounded-2xl border border-line bg-canvas/40 p-4">
            <div className="font-mono text-[10px] uppercase tracking-wider text-muted">SVI method EDR</div>
            <div className="mt-1 font-display text-xl font-semibold text-ocean">mean {sviMeanEdr.toFixed(4)}</div>
            <div className="mt-1 font-mono text-[10px] text-muted">median 0.000 · max 0.476</div>
          </div>
          <div className="rounded-2xl border border-line bg-canvas/40 p-4">
            <div className="font-mono text-[10px] uppercase tracking-wider text-muted">HAZUS method EDR</div>
            <div className="mt-1 font-display text-xl font-semibold text-ember">mean 0.0314</div>
            <div className="mt-1 font-mono text-[10px] text-muted">median 0.000 · max 0.702</div>
          </div>
          <div className="rounded-2xl border border-line bg-canvas/40 p-4">
            <div className="font-mono text-[10px] uppercase tracking-wider text-muted">Correlation</div>
            <div className="mt-1 font-display text-xl font-semibold text-signal">ρ = 0.9996</div>
            <div className="mt-1 font-mono text-[10px] text-muted">Pearson r = 0.979</div>
          </div>
        </div>
        <p className="mt-4 font-mono text-[11px] text-muted">
          In this benchmark comparison, the SVI method produces systematically lower damage estimates than the
          fixed HAZUS reference curve (mean EDR about {(meanReduction * 100).toFixed(0)}% lower) because
          SVI-driven medians adjust per bridge rather than applying one fixed HWB6 threshold set. The comparison
          still shows very strong agreement in relative ordering, even when the absolute loss estimates differ.
        </p>
      </div>
    </section>
  )
}
