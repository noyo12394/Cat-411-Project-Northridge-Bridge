const STAGES = [
  {
    key: 'stable',
    label: 'Stable',
    heading: 'Stable structural state',
    range: [0.0, 0.25],
    summary: 'Bridge remains visually stable under the current vulnerability state.',
  },
  {
    key: 'moderate',
    label: 'Moderate',
    heading: 'Moderate structural stress',
    range: [0.25, 0.5],
    summary: 'Bridge exhibits moderate sagging and localized stress indicators.',
  },
  {
    key: 'elevated',
    label: 'Elevated',
    heading: 'Elevated vulnerability',
    range: [0.5, 0.7],
    summary: 'Bridge shows visible cracking, joint strain, and growing support misalignment.',
  },
  {
    key: 'severe',
    label: 'Severe',
    heading: 'Severe structural instability',
    range: [0.7, 0.85],
    summary: 'Bridge shows severe instability, progressive cracking, and support distress.',
  },
  {
    key: 'critical',
    label: 'Critical',
    heading: 'Critical failure state',
    range: [0.85, 1.0],
    summary: 'Bridge shows partial failure behavior with major separation and collapse risk.',
  },
]

const clamp = (value, min = 0, max = 1) => Math.min(max, Math.max(min, value))
const lerp = (start, end, value) => start + (end - start) * value

function smoothstep(min, max, value) {
  const x = clamp((value - min) / (max - min || 1))
  return x * x * (3 - 2 * x)
}

function stageFor(score) {
  if (score < 0.25) return STAGES[0]
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
  const contextualStress = clamp(Math.max(0, ndviShift) * 1.4, 0, 0.08)
  const base = clamp(structuralScore ?? vulnerabilityScore)
  const stateScore = clamp(base + eventAmplifier * 0.12 + contextualStress)
  const stage = stageFor(stateScore)

  const deckSag = lerp(1.5, 34, Math.pow(stateScore, 1.28))
  const crackOpacity = clamp(0.03 + smoothstep(0.18, 0.96, stateScore) * 0.94)
  const crackCount = Math.max(0, Math.round(lerp(0, 10, smoothstep(0.24, 0.96, stateScore))))
  const pierTilt = lerp(0, 13.5, Math.pow(smoothstep(0.18, 1, stateScore), 1.12))
  const jointGap = lerp(0, 28, smoothstep(0.42, 0.98, stateScore + eventAmplifier * 0.05))
  const debrisOpacity = lerp(0, 0.55, smoothstep(0.82, 1.0, stateScore + eventAmplifier * 0.06))
  const collapseOffset = lerp(0, 70, smoothstep(0.86, 1.0, stateScore + eventAmplifier * 0.12))
  const supportFailure = smoothstep(0.72, 1.0, stateScore + eventAmplifier * 0.08)
  const stressGlow = lerp(0.08, 0.62, smoothstep(0.14, 0.98, stateScore))
  const waveAmplitude = lerp(1.4, 6.5, smoothstep(0.12, 1.0, stateScore + eventAmplifier * 0.06))
  const segmentRotation = lerp(0.3, 7.6, smoothstep(0.22, 1.0, stateScore))
  const dustCount = Math.max(2, Math.round(lerp(2, 10, smoothstep(0.82, 1.0, stateScore + eventAmplifier * 0.08))))
  const deckBreak = stateScore >= 0.86
  const tint = clamp(0.14 + stateScore * 0.42 + eventAmplifier * 0.08)

  return {
    score: Number(stateScore.toFixed(3)),
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
