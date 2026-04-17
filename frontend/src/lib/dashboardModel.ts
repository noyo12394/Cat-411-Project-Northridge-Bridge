import type {
  AssessmentDriver,
  AssessmentRecommendation,
  DashboardAssessment,
  DashboardInputs,
  DashboardModeId,
  MethodologyPrior,
  PortfolioBridge,
  ResearchData,
} from '../types/research'

export const DASHBOARD_MODES: Array<{
  id: DashboardModeId
  label: string
  eyebrow: string
  description: string
}> = [
  {
    id: 'intrinsic',
    label: 'Intrinsic Vulnerability',
    eyebrow: 'Bridge-intrinsic screening',
    description:
      'Uses structural condition, age, geometry, bridge class, and SVI only. PGA is intentionally excluded.',
  },
  {
    id: 'event',
    label: 'Event Damage Scenario',
    eyebrow: 'Hazard-inclusive hindcast / scenario',
    description:
      'Adds scenario PGA only here to estimate event-specific damage severity after intrinsic screening.',
  },
  {
    id: 'priority',
    label: 'Operational Prioritization',
    eyebrow: 'Consequence-aware decision mode',
    description:
      'Combines baseline structural vulnerability with traffic criticality and optional NDVI-based post-event evidence.',
  },
]

const DAMAGE_LABELS = ['None', 'Slight', 'Moderate', 'Extensive', 'Complete'] as const

function clamp(value: number, min = 0, max = 1) {
  return Math.min(max, Math.max(min, value))
}

function lerp(start: number, end: number, amount: number) {
  return start + (end - start) * amount
}

function normalize(value: number, min: number, max: number) {
  if (!Number.isFinite(value) || max <= min) {
    return 0
  }
  return clamp((value - min) / (max - min))
}

function currentYear() {
  return 2026
}

function getPriorWeight(priors: MethodologyPrior[], key: string, fallback: number) {
  return priors.find((item) => item.key === key)?.weight ?? fallback
}

function getPriorNarrative(priors: MethodologyPrior[], key: string, fallback: string) {
  return priors.find((item) => item.key === key)?.rationale ?? fallback
}

function getClassRisk(bridgeClass: string, researchData: ResearchData) {
  const classProfile = researchData.summary.classProfiles.find((item) => item.bridgeClass === bridgeClass)
  const meanSvi = classProfile?.meanSVI ?? researchData.summary.portfolio.meanSVI
  return normalize(meanSvi, 0.25, 0.6)
}

function deriveTrafficLabel(adt: number) {
  if (adt < 1500) return 'Local corridor'
  if (adt < 6000) return 'Regional connector'
  if (adt < 18000) return 'High-throughput route'
  return 'Network-critical artery'
}

function severityStage(severity: number) {
  if (severity < 0.18) return 0
  if (severity < 0.34) return 1
  if (severity < 0.52) return 2
  if (severity < 0.72) return 3
  return 4
}

function riskLabel(score: number) {
  if (score < 0.28) return 'Low'
  if (score < 0.46) return 'Guarded'
  if (score < 0.66) return 'Elevated'
  if (score < 0.82) return 'High'
  return 'Critical'
}

function confidenceLabel(value: number) {
  if (value >= 0.9) return 'High confidence'
  if (value >= 0.78) return 'Moderate confidence'
  return 'Screening confidence'
}

function makeDriver(
  key: string,
  label: string,
  value: number,
  description: string,
): AssessmentDriver {
  return {
    key,
    label,
    value: Number(value.toFixed(3)),
    description,
  }
}

function bridgeFromInputs(inputs: DashboardInputs, researchData: ResearchData) {
  return researchData.portfolio.find((bridge) => bridge.structureNumber === inputs.structureNumber) ?? null
}

function deriveIntrinsicDrivers(inputs: DashboardInputs, researchData: ResearchData) {
  const priors = researchData.methodology.priors
  const ranges = researchData.summary.featureRanges
  const bridgeAge = currentYear() - Number(inputs.yearBuilt)
  const reconstructionDelta =
    inputs.yearReconstructed && Number(inputs.yearReconstructed) > 0
      ? currentYear() - Number(inputs.yearReconstructed)
      : bridgeAge

  const components = {
    condition: 1 - normalize(Number(inputs.condition), ranges.condition.min, ranges.condition.max),
    svi: normalize(Number(inputs.svi), ranges.svi.min, ranges.svi.max),
    age: normalize(bridgeAge, 0, currentYear() - ranges.yearBuilt.min),
    rehab: normalize(
      reconstructionDelta,
      0,
      Math.max(1, currentYear() - (ranges.yearReconstructed.max || currentYear())),
    ),
    skew: normalize(Number(inputs.skew), ranges.skew.min, ranges.skew.max),
    maxSpan: normalize(Number(inputs.maxSpan), ranges.maxSpan.min, ranges.maxSpan.max),
    bridgeClass: getClassRisk(inputs.bridgeClass, researchData),
    spans: normalize(Number(inputs.spans), ranges.spans.min, Math.min(ranges.spans.max, 24)),
  }

  const drivers = [
    makeDriver(
      'condition',
      'Condition rating',
      components.condition * getPriorWeight(priors, 'condition', 0.22),
      getPriorNarrative(
        priors,
        'condition',
        'Condition remains the clearest bridge-health signal in inspection-led structural screening.',
      ),
    ),
    makeDriver(
      'svi',
      'Seismic vulnerability index',
      components.svi * getPriorWeight(priors, 'svi', 0.18),
      getPriorNarrative(priors, 'svi', 'SVI concentrates the bridge-intrinsic vulnerability signal.'),
    ),
    makeDriver(
      'age',
      'Bridge age / design era',
      components.age * getPriorWeight(priors, 'age', 0.15),
      getPriorNarrative(priors, 'age', 'Older detailing eras tend to imply weaker seismic behavior.'),
    ),
    makeDriver(
      'rehab',
      'Reconstruction timing',
      components.rehab * getPriorWeight(priors, 'rehab', 0.1),
      getPriorNarrative(priors, 'rehab', 'More recent rehabilitation reduces expected vulnerability relative to legacy peers.'),
    ),
    makeDriver(
      'skew',
      'Skew angle',
      components.skew * getPriorWeight(priors, 'skew', 0.1),
      getPriorNarrative(priors, 'skew', 'Higher skew can amplify irregular support response.'),
    ),
    makeDriver(
      'maxSpan',
      'Maximum span length',
      components.maxSpan * getPriorWeight(priors, 'maxSpan', 0.1),
      getPriorNarrative(priors, 'maxSpan', 'Longer spans increase structural demand concentration.'),
    ),
    makeDriver(
      'bridgeClass',
      'HAZUS bridge class',
      components.bridgeClass * getPriorWeight(priors, 'bridgeClass', 0.09),
      getPriorNarrative(priors, 'bridgeClass', 'Bridge class preserves structural family behavior without importing hazard.'),
    ),
    makeDriver(
      'spans',
      'Number of spans',
      components.spans * getPriorWeight(priors, 'spans', 0.06),
      getPriorNarrative(priors, 'spans', 'Additional spans increase geometry complexity and support interaction.'),
    ),
  ].sort((left, right) => right.value - left.value)

  const intrinsicScore = clamp(0.08 + drivers.reduce((sum, driver) => sum + driver.value, 0))

  return { intrinsicScore, drivers }
}

function ndviStress(value: DashboardInputs['ndviChange']) {
  if (value === '' || value == null) {
    return { stress: 0, relief: 0 }
  }
  const numeric = Number(value)
  return {
    stress: clamp(Math.abs(Math.min(0, numeric)) / 0.35),
    relief: clamp(Math.max(0, numeric) / 0.35),
  }
}

function trafficUrgency(adt: number, researchData: ResearchData) {
  const adtMax = researchData.summary.featureRanges.adt.max
  return clamp(Math.log1p(Math.max(adt, 0)) / Math.log1p(Math.max(adtMax, 1)))
}

function buildRecommendations(
  mode: DashboardModeId,
  headlineScore: number,
  structuralSeverity: number,
  inputs: DashboardInputs,
): AssessmentRecommendation[] {
  const recommendations: AssessmentRecommendation[] = []

  if (mode === 'intrinsic') {
    recommendations.push(
      structuralSeverity > 0.62
        ? {
            title: 'Flag for retrofit screening',
            detail: 'High intrinsic vulnerability suggests this bridge should move into targeted engineering review before any event scenario is specified.',
          }
        : {
            title: 'Keep in network screening set',
            detail: 'This bridge is better suited to portfolio monitoring than urgent structural intervention under the current intrinsic-only framing.',
          },
    )
  }

  if (mode === 'event') {
    recommendations.push(
      headlineScore > 0.72
        ? {
            title: 'Escalate emergency inspection',
            detail: `At ${inputs.scenarioPga.toFixed(2)} g, the event-specific damage estimate is high enough to justify immediate post-event inspection planning.`,
          }
        : {
            title: 'Scenario remains manageable',
            detail: `At ${inputs.scenarioPga.toFixed(2)} g, the bridge shows damage sensitivity but not a full collapse-level signal in this scenario.`,
          },
    )
  }

  if (mode === 'priority') {
    recommendations.push(
      headlineScore > 0.7
        ? {
            title: 'Promote to operational watchlist',
            detail: 'The combination of structural vulnerability, traffic exposure, and optional post-event evidence makes this bridge a high-priority decision target.',
          }
        : {
            title: 'Monitor without front-loading crews',
            detail: 'Consequence is meaningful, but the bridge does not currently need to outrank the top emergency attention tier.',
          },
    )
  }

  recommendations.push({
    title: 'Preserve mode discipline',
    detail:
      mode === 'event'
        ? 'PGA is affecting only the event-specific damage layer here.'
        : mode === 'priority'
          ? 'Traffic is only affecting operational urgency, not intrinsic structural weakness.'
          : 'This score excludes PGA, ADT, and NDVI as core structural drivers.',
  })

  return recommendations
}

export function createInitialInputs(
  researchData: ResearchData,
  sampleBridge?: PortfolioBridge | null,
): DashboardInputs {
  const sample =
    sampleBridge ??
    researchData.portfolio.find((bridge) => bridge.structureNumber === researchData.summary.sampleBridges[1]?.structureNumber) ??
    researchData.portfolio[0]

  return {
    structureNumber: sample?.structureNumber ?? '',
    yearBuilt: sample?.yearBuilt ?? 1988,
    yearReconstructed:
      sample?.yearReconstructed && sample.yearReconstructed > 0 ? sample.yearReconstructed : '',
    skew: sample?.skew ?? 16,
    spans: sample?.spans ?? 3,
    maxSpan: Math.round(sample?.maxSpanFt ?? 82),
    condition: sample?.condition ?? 6,
    bridgeClass: sample?.bridgeClass ?? 'HWB6',
    svi: Number((sample?.svi ?? researchData.summary.portfolio.meanSVI ?? 0.42).toFixed(3)),
    ndviChange: '',
    adt: Math.round(sample?.adt ?? 9000),
    scenarioPga: Number((sample?.pga ?? 0.12).toFixed(2)),
  }
}

export function applyPortfolioBridge(bridge: PortfolioBridge, researchData: ResearchData): DashboardInputs {
  return createInitialInputs(researchData, bridge)
}

export function runDashboardAssessment(
  inputs: DashboardInputs,
  mode: DashboardModeId,
  researchData: ResearchData,
): DashboardAssessment {
  const { intrinsicScore, drivers } = deriveIntrinsicDrivers(inputs, researchData)
  const trafficScore = trafficUrgency(Number(inputs.adt || 0), researchData)
  const hazardScore = clamp(Math.sqrt(Math.max(Number(inputs.scenarioPga || 0), 0) / 0.4))
  const ndvi = ndviStress(inputs.ndviChange)

  const eventScore = clamp(intrinsicScore * 0.55 + hazardScore * 0.4 + ndvi.stress * 0.05 - ndvi.relief * 0.02)
  const priorityScore = clamp(intrinsicScore * 0.62 + trafficScore * 0.26 + ndvi.stress * 0.12 - ndvi.relief * 0.03)
  const structuralSeverity =
    mode === 'event'
      ? eventScore
      : clamp(intrinsicScore + ndvi.stress * 0.1 - ndvi.relief * 0.04)
  const headlineScore = mode === 'intrinsic' ? intrinsicScore : mode === 'event' ? eventScore : priorityScore

  const stage = severityStage(structuralSeverity)
  const collapse = stage === 4 ? clamp((structuralSeverity - 0.72) / 0.28) : 0
  const confidenceBase = mode === 'intrinsic' ? 0.88 : mode === 'event' ? 0.81 : 0.79
  const confidence = clamp(confidenceBase + (inputs.structureNumber ? 0.03 : 0) - (mode === 'priority' && inputs.ndviChange === '' ? 0.04 : 0))

  const assessmentDrivers = [...drivers]
  if (mode === 'event') {
    assessmentDrivers.unshift(
      makeDriver(
        'pga',
        'Scenario PGA',
        hazardScore * 0.4,
        'Hazard intensity is introduced only in event mode after intrinsic vulnerability is established.',
      ),
    )
  }
  if (mode === 'priority') {
    assessmentDrivers.unshift(
      makeDriver(
        'traffic',
        'Traffic / operational criticality',
        trafficScore * 0.26,
        'ADT changes crew urgency and network consequence, not baseline structural weakness.',
      ),
    )
  }
  if (inputs.ndviChange !== '') {
    assessmentDrivers.push(
      makeDriver(
        'ndvi',
        'NDVI / ground-failure adjustment',
        ndvi.stress * 0.12,
        'NDVI is treated as an optional post-event ground-failure signal rather than a default structural driver.',
      ),
    )
  }

  const narrative =
    mode === 'intrinsic'
      ? 'Intrinsic vulnerability mode is screening the bridge using structural age, geometry, condition, bridge class, and SVI only.'
      : mode === 'event'
        ? 'Event damage mode keeps the intrinsic structural baseline intact, then adds PGA as an earthquake-specific stressor.'
        : 'Prioritization mode keeps structural vulnerability separate while layering in ADT consequence and optional NDVI evidence for operational urgency.'

  const scenarioLabel =
    mode === 'event'
      ? `Scenario PGA ${Number(inputs.scenarioPga).toFixed(2)} g`
      : mode === 'priority'
        ? `${deriveTrafficLabel(Number(inputs.adt || 0))} / ADT ${Math.round(Number(inputs.adt || 0)).toLocaleString()}`
        : 'Intrinsic-only structural screen'

  return {
    mode,
    headlineScore,
    intrinsicScore,
    eventScore,
    priorityScore,
    riskLevel: riskLabel(headlineScore),
    damageLabel: DAMAGE_LABELS[stage],
    stageLabel: `Stage ${stage} - ${DAMAGE_LABELS[stage]}`,
    scenarioLabel,
    narrative,
    confidenceLabel: confidenceLabel(confidence),
    confidence,
    trafficLabel: deriveTrafficLabel(Number(inputs.adt || 0)),
    drivers: assessmentDrivers.sort((left, right) => right.value - left.value),
    recommendations: buildRecommendations(mode, headlineScore, structuralSeverity, inputs),
    visual: {
      mode,
      stage,
      structuralSeverity,
      headlineSeverity: headlineScore,
      deckSag: lerp(4, 52, structuralSeverity),
      deckOffset: lerp(0.02, 1, structuralSeverity),
      crackIntensity: lerp(0.05, 1, structuralSeverity),
      columnLean: lerp(0, 1, structuralSeverity),
      fracture: clamp((structuralSeverity - 0.42) / 0.58),
      collapse,
      waveAmp: mode === 'event' ? lerp(0.06, 1, hazardScore) : lerp(0.04, 0.2, structuralSeverity),
      dust: clamp(lerp(0, 1, structuralSeverity) + ndvi.stress * 0.18),
      groundShift: clamp(ndvi.stress * 0.85),
      urgencyPulse: mode === 'priority' ? clamp(priorityScore * 0.8 + trafficScore * 0.2) : 0,
      emergencyTint: mode === 'event' ? clamp(eventScore * 1.1) : structuralSeverity * 0.66,
    },
  }
}

export function findBridgeMatch(
  researchData: ResearchData,
  structureNumber: string,
): PortfolioBridge | null {
  return bridgeFromInputs({ structureNumber } as DashboardInputs, researchData)
}
