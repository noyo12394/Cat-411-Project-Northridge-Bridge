const CURRENT_YEAR = 2026

const bridgeClassFactor = {
  HWB1: 0.34,
  HWB2: 0.28,
  HWB3: 0.38,
  HWB4: 0.46,
  HWB5: 0.57,
  HWB6: 0.48,
  HWB7: 0.69,
  HWB8: 0.63,
  HWB9: 0.51,
  HWB10: 0.44,
  HWB11: 0.58,
  HWB12: 0.61,
}

const weights = {
  condition: 0.28,
  svi: 0.22,
  age: 0.16,
  skew: 0.12,
  spanLength: 0.1,
  spanCount: 0.07,
  bridgeClass: 0.05,
}

const clamp = (value, min, max) => Math.min(max, Math.max(min, value))

const parseMaybeNumber = (value) => {
  if (value === '' || value === null || value === undefined) return null
  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric : null
}

const normalizeAgeScore = (yearBuilt) => {
  if (!yearBuilt) return 0.5
  if (yearBuilt <= 1970) return 0.95
  if (yearBuilt <= 1989) return 0.78
  if (yearBuilt <= 2000) return 0.56
  return 0.32
}

const normalizeConditionScore = (conditionRating) => {
  if (conditionRating === null) return 0.5
  return clamp((9 - clamp(conditionRating, 0, 9)) / 9, 0, 1)
}

const normalizeSkewScore = (skewAngle) => {
  if (skewAngle === null) return 0.35
  return clamp(skewAngle / 60, 0, 1)
}

const normalizeSpanLengthScore = (maxSpan) => {
  if (maxSpan === null) return 0.45
  return clamp(maxSpan / 250, 0, 1)
}

const normalizeSpanCountScore = (spans) => {
  if (spans === null) return 0.35
  if (spans <= 1) return 0.08
  if (spans <= 3) return 0.3
  if (spans <= 6) return 0.58
  return 0.8
}

const normalizeSviScore = (sviScore) => {
  if (sviScore === null) return 0.5
  return clamp(sviScore, 0, 1)
}

const calculateRehabCredit = (yearReconstructed, yearBuilt) => {
  if (!yearReconstructed || yearReconstructed <= 0 || (yearBuilt && yearReconstructed <= yearBuilt)) {
    return 0
  }

  const yearsSinceRehab = clamp(CURRENT_YEAR - yearReconstructed, 0, 80)
  if (yearsSinceRehab <= 15) return 0.1
  if (yearsSinceRehab <= 30) return 0.065
  if (yearsSinceRehab <= 45) return 0.035
  return 0.015
}

const calculateNdviAdjustment = (ndviChange) => {
  if (ndviChange === null) {
    return {
      applied: false,
      adjustment: 0,
      message: 'No NDVI adjustment applied. The score reflects pre-event intrinsic vulnerability only.',
    }
  }

  if (ndviChange < 0) {
    const adjustment = clamp(Math.abs(ndviChange) * 0.22, 0, 0.07)
    return {
      applied: true,
      adjustment,
      message: 'Negative NDVI change was treated as a modest post-event stress adjustment.',
    }
  }

  const adjustment = -clamp(ndviChange * 0.08, 0, 0.02)
  return {
    applied: true,
    adjustment,
    message: 'Positive or neutral NDVI change slightly reduced the post-event adjustment term.',
  }
}

const calculateConsequenceScore = (trafficImportance) => {
  if (trafficImportance === null) return 0.25
  const normalized = Math.log1p(Math.max(trafficImportance, 0)) / Math.log1p(100000)
  return clamp(normalized, 0, 1)
}

const determineDamageCategory = (score) => {
  if (score < 0.18) return { code: 'DS-0', label: 'None', explanation: 'Minimal expected bridge distress under a moderate event scenario.' }
  if (score < 0.34) return { code: 'DS-1', label: 'Minor', explanation: 'Localized damage may be visible, but global structural integrity remains stable.' }
  if (score < 0.52) return { code: 'DS-2', label: 'Moderate', explanation: 'Bridge likely requires follow-up inspection and limited intervention planning.' }
  if (score < 0.72) return { code: 'DS-3', label: 'Major', explanation: 'Serious functional impairment is plausible and inspection urgency increases.' }
  return { code: 'DS-4', label: 'Complete', explanation: 'Severe instability or closure conditions should be treated as credible.' }
}

const determineRiskLevel = (score) => {
  if (score < 0.28) return { label: 'Low', tone: 'text-teal', chip: 'bg-teal/10 text-teal border-teal/15' }
  if (score < 0.48) return { label: 'Medium', tone: 'text-ocean', chip: 'bg-ocean/10 text-ocean border-ocean/15' }
  if (score < 0.68) return { label: 'High', tone: 'text-signal', chip: 'bg-signal/12 text-[#8f5a00] border-signal/20' }
  return { label: 'Critical', tone: 'text-danger', chip: 'bg-danger/10 text-danger border-danger/15' }
}

const determineDisruptionLevel = (score) => {
  if (score < 0.24) return 'Limited'
  if (score < 0.42) return 'Localized'
  if (score < 0.64) return 'Elevated'
  return 'Severe'
}

const toContributionRow = (label, value) => ({
  feature: label,
  contribution: Number((value * 100).toFixed(1)),
})

// This function is intentionally isolated so a future trained model can replace
// the weighted heuristic without changing the dashboard components.
export function runBridgePrediction(rawInput) {
  const input = {
    yearBuilt: parseMaybeNumber(rawInput.yearBuilt),
    yearReconstructed: parseMaybeNumber(rawInput.yearReconstructed),
    skewAngle: parseMaybeNumber(rawInput.skewAngle),
    numberOfSpans: parseMaybeNumber(rawInput.numberOfSpans),
    maximumSpanLength: parseMaybeNumber(rawInput.maximumSpanLength),
    conditionRating: parseMaybeNumber(rawInput.conditionRating),
    bridgeClass: rawInput.bridgeClass || 'HWB3',
    sviScore: parseMaybeNumber(rawInput.sviScore),
    ndviChange: parseMaybeNumber(rawInput.ndviChange),
    trafficImportance: parseMaybeNumber(rawInput.trafficImportance),
  }

  const componentScores = {
    condition: normalizeConditionScore(input.conditionRating),
    svi: normalizeSviScore(input.sviScore),
    age: normalizeAgeScore(input.yearBuilt),
    skew: normalizeSkewScore(input.skewAngle),
    spanLength: normalizeSpanLengthScore(input.maximumSpanLength),
    spanCount: normalizeSpanCountScore(input.numberOfSpans),
    bridgeClass: bridgeClassFactor[input.bridgeClass] ?? 0.46,
  }

  const contributions = {
    condition: componentScores.condition * weights.condition,
    svi: componentScores.svi * weights.svi,
    age: componentScores.age * weights.age,
    skew: componentScores.skew * weights.skew,
    spanLength: componentScores.spanLength * weights.spanLength,
    spanCount: componentScores.spanCount * weights.spanCount,
    bridgeClass: componentScores.bridgeClass * weights.bridgeClass,
  }

  const baseScore = Object.values(contributions).reduce((sum, value) => sum + value, 0)
  const rehabCredit = calculateRehabCredit(input.yearReconstructed, input.yearBuilt)
  const ndvi = calculateNdviAdjustment(input.ndviChange)
  const vulnerabilityScore = clamp(baseScore - rehabCredit + ndvi.adjustment, 0.02, 0.97)

  const consequenceScore = calculateConsequenceScore(input.trafficImportance)
  const priorityScore = clamp(vulnerabilityScore * 0.72 + consequenceScore * 0.28, 0, 1)
  const inspectionPriorityRank = Math.max(1, 101 - Math.round(priorityScore * 100))

  const providedInputs = Object.values(input).filter((value) => value !== null && value !== '').length
  const completeness = providedInputs / 10
  const confidenceScore = clamp(64 + completeness * 26 + (input.sviScore !== null ? 4 : 0), 60, 97)

  const topContributingFeatures = [
    toContributionRow('Condition rating', contributions.condition),
    toContributionRow('SVI score', contributions.svi),
    toContributionRow('Year built / age', contributions.age),
    toContributionRow('Skew angle', contributions.skew),
    toContributionRow('Maximum span length', contributions.spanLength),
    toContributionRow('Number of spans', contributions.spanCount),
    toContributionRow('Bridge class', contributions.bridgeClass),
  ]
    .sort((a, b) => b.contribution - a.contribution)
    .slice(0, 5)

  const damageCategory = determineDamageCategory(vulnerabilityScore)
  const riskLevel = determineRiskLevel(vulnerabilityScore)
  const disruptionScore = clamp(vulnerabilityScore * 0.4 + consequenceScore * 0.6, 0, 1)

  return {
    normalizedInput: input,
    vulnerabilityScore: Number(vulnerabilityScore.toFixed(3)),
    damageCategory,
    riskLevel,
    inspectionPriorityRank,
    confidence: {
      score: Math.round(confidenceScore),
      label: confidenceScore >= 88 ? 'High confidence' : confidenceScore >= 76 ? 'Moderate confidence' : 'Screening confidence',
    },
    disruption: {
      score: Number(disruptionScore.toFixed(3)),
      label: determineDisruptionLevel(disruptionScore),
      detail: 'Traffic / economic disruption uses ADT only as a consequence layer, not as a core vulnerability input.',
    },
    ndviAdjustment: {
      ...ndvi,
      adjustment: Number(ndvi.adjustment.toFixed(3)),
    },
    topContributingFeatures,
    priorityScore: Number(priorityScore.toFixed(3)),
    consequenceScore: Number(consequenceScore.toFixed(3)),
    rehabCredit: Number(rehabCredit.toFixed(3)),
  }
}
