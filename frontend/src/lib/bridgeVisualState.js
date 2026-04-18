const STAGES = [
  {
    key: 'stable',
    label: 'Stable',
    heading: 'Stable structural state',
    range: [0.0, 0.29],
    summary: 'Bridge remains visually stable under the current vulnerability state.',
  },
  {
    key: 'moderate',
    label: 'Moderate',
    heading: 'Moderate structural stress',
    range: [0.3, 0.49],
    summary: 'Bridge exhibits slight deck sag with mild support strain, while remaining largely intact.',
  },
  {
    key: 'elevated',
    label: 'Elevated',
    heading: 'Elevated vulnerability',
    range: [0.5, 0.69],
    summary: 'Bridge shows visible cracking near the joints, moderate sagging, and controlled support misalignment.',
  },
  {
    key: 'severe',
    label: 'Severe',
    heading: 'Severe structural instability',
    range: [0.7, 0.84],
    summary: 'Bridge shows clear cracking, stronger deck deformation, and localized support distress.',
  },
  {
    key: 'critical',
    label: 'Critical',
    heading: 'Critical failure state',
    range: [0.85, 1.0],
    summary: 'Bridge shows severe cracking, partial deck separation, and near-failure behavior.',
  },
]

const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value))
const lerp = (start, end, value) => start + (end - start) * value

function smoothstep(min, max, value) {
  const x = clamp((value - min) / (max - min || 1))
  return x * x * (3 - 2 * x)
}

function stageFor(score) {
  if (score < 0.3) return STAGES[0]
  if (score < 0.5) return STAGES[1]
  if (score < 0.7) return STAGES[2]
  if (score < 0.85) return STAGES[3]
  return STAGES[4]
}

function defaultSummary(stage, mode, eventIntensity) {
  if (mode === 'event' && eventIntensity > 0.04) {
    return `${stage.summary} Event-demand effects are shown as an added scenario layer rather than baseline structural weakness.`
  }
  if (mode === 'priority') {
    return `${stage.summary} Traffic consequence changes urgency elsewhere, but does not directly drive this structural deformation.`
  }
  return stage.summary
}

export function getBridgeStructuralState({
  vulnerabilityScore = 0.4,
  mode = 'intrinsic',
  eventIntensity = 0,
  ndviShift = 0,
  structuralScore,
} = {}) {
  const eventAmplifier = mode === 'event' ? clamp(eventIntensity, 0, 1) : 0
  const contextualStress = clamp(Math.max(0, ndviShift) * 0.6, 0, 0.03)
  const base = clamp(structuralScore ?? vulnerabilityScore)
  const stateScore = clamp(base + eventAmplifier * 0.06 + contextualStress)
  const visualScore = clamp(stateScore)
  const stage = stageFor(visualScore)

  const mild = smoothstep(0.3, 0.49, visualScore)
  const elevated = smoothstep(0.5, 0.69, visualScore)
  const severe = smoothstep(0.7, 0.84, visualScore + eventAmplifier * 0.03)
  const critical = smoothstep(0.85, 1.0, visualScore + eventAmplifier * 0.04)
  const hairline = smoothstep(0.42, 0.55, visualScore)

  const deckSag = 1.2 + mild * 5.5 + elevated * 10 + severe * 12 + critical * 16 + eventAmplifier * 3
  const crackOpacity = clamp(hairline * 0.18 + elevated * 0.32 + severe * 0.32 + critical * 0.18, 0, 0.92)
  const crackCount = visualScore < 0.42 ? 0 : Math.round(1 + elevated * 2 + severe * 3 + critical * 3)
  const pierTilt = mild * 1.8 + elevated * 4 + severe * 6 + critical * 8
  const jointGap = elevated * 4 + severe * 10 + critical * 20 + eventAmplifier * 4
  const debrisOpacity = critical * 0.28
  const collapseOffset = critical * 42 + Math.max(0, eventAmplifier - 0.65) * 14
  const supportFailure = smoothstep(0.76, 0.98, visualScore + eventAmplifier * 0.08)
  const stressGlow = 0.08 + mild * 0.05 + elevated * 0.08 + severe * 0.11 + critical * 0.14
  const waveAmplitude = 1 + visualScore * 0.6
  const segmentRotation = severe * 2.4 + critical * 7.4
  const dustCount = critical > 0.04 ? Math.max(2, Math.round(2 + critical * 4)) : 0
  const deckBreak = visualScore >= 0.9
  const tint = clamp(0.12 + elevated * 0.18 + severe * 0.18 + critical * 0.2 + eventAmplifier * 0.08)

  return {
    score: Number(stateScore.toFixed(3)),
    visualScore: Number(visualScore.toFixed(3)),
    baseScore: Number(base.toFixed(3)),
    mode,
    stageKey: stage.key,
    stageLabel: stage.label,
    stageHeading: stage.heading,
    summary: defaultSummary(stage, mode, eventIntensity),
    deckSag,
    crackOpacity,
    crackCount,
    pierTilt,
    jointGap,
    debrisOpacity,
    collapseOffset,
    supportFailure,
    stressGlow,
    waveAmplitude,
    segmentRotation,
    dustCount,
    deckBreak,
    eventAmplifier,
    ndviAccent: contextualStress,
    emergencyTint: tint,
  }
}

export function getBridgeStageLegend() {
  return STAGES.map((stage) => ({
    key: stage.key,
    label: stage.label,
    heading: stage.heading,
  }))
}
