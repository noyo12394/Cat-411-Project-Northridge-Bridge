const DAMAGE_LABELS = ['None', 'Minor', 'Moderate', 'Major', 'Complete']

export const DASHBOARD_MODES = [
  {
    id: 'intrinsic',
    label: 'Intrinsic Vulnerability',
    eyebrow: 'Bridge-intrinsic screening',
    description:
      'Uses structural age, geometry, condition, bridge class, and SVI to screen which bridges appear intrinsically more vulnerable before specifying an earthquake.',
  },
  {
    id: 'event',
    label: 'Event Damage Scenario',
    eyebrow: 'Hazard-inclusive scenario',
    description:
      'Adds scenario PGA only here, after intrinsic screening, to estimate how damage may change under a specific earthquake intensity.',
  },
  {
    id: 'priority',
    label: 'Inspection Prioritization',
    eyebrow: 'Consequence-aware triage',
    description:
      'Combines intrinsic vulnerability with ADT / traffic consequence and optional NDVI post-event evidence to rank emergency attention.',
  },
]

const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value))
const lerp = (start, end, value) => start + (end - start) * value

function normalize(value, min, max) {
  if (value == null || Number.isNaN(Number(value)) || max <= min) {
    return 0
  }
  return clamp((Number(value) - min) / (max - min))
}

function currentYear() {
  return 2026
}

function getClassProfile(bridgeClass, researchData) {
  const profiles = researchData.summary.classProfiles ?? []
  const defaultProfile = {
    meanSVI: researchData.summary.portfolio.meanSVI,
    meanEDR: researchData.summary.portfolio.meanEDR,
  }
  return profiles.find((item) => item.bridgeClass === bridgeClass) ?? defaultProfile
}

function getPriors(researchData) {
  return researchData.methodology?.priors ?? []
}

function getPriorWeight(key, researchData, fallback) {
  return getPriors(researchData).find((item) => item.key === key)?.weight ?? fallback
}

function getPriorNarrative(key, researchData, fallback) {
  return getPriors(researchData).find((item) => item.key === key)?.rationale ?? fallback
}

function makeContribution(label, value, narrative) {
  return {
    label,
    value: Number(value.toFixed(3)),
    narrative,
  }
}

export function createInitialInputs(sampleBridge, researchData) {
  const fallback = researchData.summary.sampleBridges?.[1] ?? {}
  const selected = sampleBridge ?? fallback

  return {
    yearBuilt: selected.yearBuilt ?? 1988,
    yearReconstructed:
      selected.yearReconstructed && Number(selected.yearReconstructed) > 0
        ? selected.yearReconstructed
        : '',
    skew: selected.skew ?? 18,
    spans: selected.spans ?? 3,
    maxSpan: selected.maxSpan ?? selected.maxSpanFt ?? 80,
    condition: selected.condition ?? 6,
    bridgeClass: selected.bridgeClass ?? 'HWB6',
    svi: Number(selected.svi ?? researchData.summary.portfolio.meanSVI ?? 0.45),
    ndviChange: '',
    adt: selected.adt ?? 9000,
    scenarioPga: 0.12,
  }
}

function deriveIntrinsicComponents(inputs, researchData) {
  const ranges = researchData.summary.featureRanges
  const bridgeAge = currentYear() - Number(inputs.yearBuilt)
  const ageNormalized = normalize(bridgeAge, 0, currentYear() - ranges.yearBuilt.min)
  const recentRehabDelta =
    inputs.yearReconstructed && Number(inputs.yearReconstructed) > 0
      ? currentYear() - Number(inputs.yearReconstructed)
      : bridgeAge
  const rehabNormalized = normalize(
    recentRehabDelta,
    0,
    currentYear() - (ranges.yearReconstructed.max || currentYear()),
  )
  const skewNormalized = normalize(Number(inputs.skew), ranges.skew.min, ranges.skew.max)
  const spanCountNormalized = normalize(
    Number(inputs.spans),
    ranges.spans.min,
    Math.min(ranges.spans.max, 24),
  )
  const maxSpanNormalized = normalize(Number(inputs.maxSpan), ranges.maxSpan.min, ranges.maxSpan.max)
  const conditionRisk = 1 - normalize(Number(inputs.condition), ranges.condition.min, ranges.condition.max)
  const sviNormalized = normalize(Number(inputs.svi), ranges.svi.min, ranges.svi.max)
  const classProfile = getClassProfile(inputs.bridgeClass, researchData)
  const classRisk = normalize(
    classProfile.meanSVI ?? researchData.summary.portfolio.meanSVI,
    0.25,
    0.6,
  )

  return {
    bridgeAge,
    classProfile,
    age: ageNormalized,
    rehab: rehabNormalized,
    skew: skewNormalized,
    spans: spanCountNormalized,
    maxSpan: maxSpanNormalized,
    condition: conditionRisk,
    svi: sviNormalized,
    bridgeClass: classRisk,
  }
}

function scoreIntrinsic(inputs, researchData) {
  const components = deriveIntrinsicComponents(inputs, researchData)
  const contributions = [
    makeContribution(
      'Condition rating',
      components.condition * getPriorWeight('condition', researchData, 0.22),
      getPriorNarrative('condition', researchData, 'Condition remains the clearest bridge-health signal in inspection-led vulnerability screening.'),
    ),
    makeContribution(
      'SVI',
      components.svi * getPriorWeight('svi', researchData, 0.18),
      getPriorNarrative('svi', researchData, 'SVI carries the revised multi-factor structural screening signal.'),
    ),
    makeContribution(
      'Bridge age / design era',
      components.age * getPriorWeight('age', researchData, 0.15),
      getPriorNarrative('age', researchData, 'Older bridges generally map to earlier design eras and weaker seismic detailing.'),
    ),
    makeContribution(
      'Reconstruction timing',
      components.rehab * getPriorWeight('rehab', researchData, 0.1),
      getPriorNarrative('rehab', researchData, 'More recent rehabilitation reduces expected vulnerability relative to legacy peers.'),
    ),
    makeContribution(
      'Skew angle',
      components.skew * getPriorWeight('skew', researchData, 0.1),
      getPriorNarrative('skew', researchData, 'Higher skew can amplify irregular seismic response.'),
    ),
    makeContribution(
      'Maximum span length',
      components.maxSpan * getPriorWeight('maxSpan', researchData, 0.1),
      getPriorNarrative('maxSpan', researchData, 'Longer spans increase structural demand concentration and consequence.'),
    ),
    makeContribution(
      'Bridge class / HWB class',
      components.bridgeClass * getPriorWeight('bridgeClass', researchData, 0.09),
      getPriorNarrative('bridgeClass', researchData, 'Bridge class captures system-level fragility family differences without importing PGA into the baseline score.'),
    ),
    makeContribution(
      'Number of spans',
      components.spans * getPriorWeight('spans', researchData, 0.06),
      getPriorNarrative('spans', researchData, 'Additional spans increase geometry complexity and support interaction.'),
    ),
  ]

  const rawScore = contributions.reduce((sum, item) => sum + item.value, 0)
  const intrinsicScore = clamp(0.08 + rawScore)
  return {
    score: intrinsicScore,
    components,
    contributions: contributions.sort((a, b) => b.value - a.value),
  }
}

function deriveRiskLevel(score) {
  if (score < 0.28) return 'Low'
  if (score < 0.46) return 'Guarded'
  if (score < 0.66) return 'Elevated'
  if (score < 0.82) return 'High'
  return 'Critical'
}

function deriveDamageCategory(score) {
  if (score < 0.18) return DAMAGE_LABELS[0]
  if (score < 0.34) return DAMAGE_LABELS[1]
  if (score < 0.52) return DAMAGE_LABELS[2]
  if (score < 0.74) return DAMAGE_LABELS[3]
  return DAMAGE_LABELS[4]
}

function deriveTrafficIndicator(adt) {
  if (adt < 1500) return { label: 'Local corridor', score: 0.18 }
  if (adt < 6000) return { label: 'Regional connector', score: 0.4 }
  if (adt < 18000) return { label: 'High-throughput route', score: 0.66 }
  return { label: 'Network-critical artery', score: 0.88 }
}

function deriveConfidence(inputs, mode) {
  const filledFields = [
    inputs.yearBuilt,
    inputs.skew,
    inputs.spans,
    inputs.maxSpan,
    inputs.condition,
    inputs.bridgeClass,
    inputs.svi,
    mode === 'event' ? inputs.scenarioPga : true,
  ].filter((value) => value !== '' && value != null).length

  const base = mode === 'intrinsic' ? 0.78 : mode === 'event' ? 0.72 : 0.75
  return clamp(base + filledFields * 0.015, 0.55, 0.94)
}

function buildVisualState(score, mode) {
  return {
    vulnerability: score,
    sag: lerp(2, mode === 'event' ? 24 : 16, score),
    crack: lerp(0.04, mode === 'event' ? 0.95 : 0.82, score),
    supportShift: lerp(0, mode === 'event' ? 14 : 8, score),
    deckFracture: score > 0.65,
  }
}

function ndviAdjustmentScore(ndviChange) {
  if (ndviChange === '' || ndviChange == null || Number.isNaN(Number(ndviChange))) {
    return {
      shift: 0,
      narrative: 'No NDVI adjustment applied. This remains a baseline structural screening state.',
      active: false,
    }
  }

  const value = Number(ndviChange)
  const negativeStress = clamp(Math.abs(Math.min(0, value)) / 0.35)
  const positiveRecovery = clamp(Math.max(0, value) / 0.35)
  const shift = negativeStress * 0.08 - positiveRecovery * 0.04
  const narrative =
    value < 0
      ? 'Negative NDVI change suggests post-event degradation and increases inspection attention.'
      : 'Flat or positive NDVI change does not materially elevate structural concern.'

  return { shift, narrative, active: true }
}

export function runBridgeAssessment(inputs, mode, researchData) {
  const intrinsic = scoreIntrinsic(inputs, researchData)
  const baseConfidence = deriveConfidence(inputs, mode)
  const traffic = deriveTrafficIndicator(Number(inputs.adt || 0))
  const ndvi = ndviAdjustmentScore(inputs.ndviChange)

  let headlineScore = intrinsic.score
  let modeNarrative =
    'Intrinsic vulnerability reflects a bridge-intrinsic screening score only. PGA remains outside this baseline score.'
  let scenarioTag = 'No event-specific hazard demand applied'

  if (mode === 'event') {
    const pga = clamp(Number(inputs.scenarioPga || 0), 0, 0.5)
    const pgaNormalized = clamp(Math.sqrt(pga / 0.4))
    headlineScore = clamp(intrinsic.score * 0.6 + pgaNormalized * 0.35 + intrinsic.components.bridgeClass * 0.05)
    modeNarrative =
      'Event damage mode introduces PGA only after the intrinsic vulnerability layer, keeping hazard and vulnerability conceptually separate.'
    scenarioTag = pga > 0 ? `Scenario PGA = ${pga.toFixed(2)} g` : 'Scenario PGA not provided'
  }

  if (mode === 'priority') {
    headlineScore = clamp(intrinsic.score * 0.68 + traffic.score * 0.22 + ndvi.shift + 0.1)
    modeNarrative =
      'Inspection prioritization combines intrinsic vulnerability with traffic consequence and optional post-event NDVI evidence.'
    scenarioTag = 'ADT affects prioritization only; it does not change intrinsic vulnerability.'
  }

  const riskLevel = deriveRiskLevel(headlineScore)
  const damageCategory = deriveDamageCategory(mode === 'intrinsic' ? intrinsic.score : headlineScore)
  const confidence = clamp(baseConfidence - (mode === 'priority' && !ndvi.active ? 0.04 : 0), 0.55, 0.94)
  const priorityPercentile = Math.round(clamp(headlineScore * 100, 5, 99))
  const inspectionPriorityRank =
    mode === 'priority'
      ? `Top ${100 - priorityPercentile}% attention band`
      : headlineScore > 0.66
        ? 'Escalate targeted review'
        : 'Routine-to-targeted review'

  const topContributors = [...intrinsic.contributions.slice(0, 4)]

  if (mode === 'event') {
    topContributors.unshift(
      makeContribution(
        'Scenario PGA',
        clamp(Math.sqrt(Number(inputs.scenarioPga || 0) / 0.4)) * 0.3,
        'Hazard intensity is introduced only in event mode to estimate earthquake-specific damage.',
      ),
    )
  }

  if (mode === 'priority') {
    topContributors.unshift(
      makeContribution(
        'Traffic importance / ADT',
        traffic.score * 0.22,
        'ADT changes inspection urgency and consequence, not baseline structural vulnerability.',
      ),
    )
  }

  return {
    mode,
    vulnerabilityScore: Number((mode === 'intrinsic' ? intrinsic.score : headlineScore).toFixed(3)),
    damageCategory,
    riskLevel,
    inspectionPriorityRank,
    confidence: Number(confidence.toFixed(2)),
    confidenceLabel:
      confidence > 0.86 ? 'High confidence' : confidence > 0.72 ? 'Moderate confidence' : 'Screening confidence',
    trafficIndicator: traffic,
    ndviAdjustment: ndvi,
    topContributors,
    narrative: modeNarrative,
    scenarioTag,
    visualState: buildVisualState(mode === 'intrinsic' ? intrinsic.score : headlineScore, mode),
  }
}
