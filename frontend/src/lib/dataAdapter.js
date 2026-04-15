import { fallbackResearchData } from '../data/fallbackResearchData'

const DATA_PATHS = {
  summary: '/data/site_summary.json',
  damageState: '/data/damage_state_best_by_feature_set.json',
  futureScenario: '/data/future_scenario_summary.json',
  hybridBest: '/data/ml_hybrid_best_by_feature_set.json',
  recommendedMetrics: '/data/ml_recommended_hybrid_metrics.json',
  recommendedImportance: '/data/ml_recommended_hybrid_feature_importance.json',
  health: '/data/data_health.json',
  proxyValidation: '/data/proxy_validation.json',
  researchManifest: '/research/manifest.json',
}

async function fetchJson(path) {
  try {
    const response = await fetch(path, { cache: 'no-store' })
    if (!response.ok) {
      return null
    }
    return await response.json()
  } catch {
    return null
  }
}

function formatClassifierMetrics(rows = []) {
  return rows.map((row) => ({
    featureGroup: row['Feature Group'] ?? row.featureGroup,
    model: row.Model ?? row.model,
    holdoutBalancedAccuracy: row.Holdout_Balanced_Accuracy ?? row.holdoutBalancedAccuracy,
    holdoutMacroF1: row.Holdout_Macro_F1 ?? row.holdoutMacroF1,
    holdoutWithinOneStateAccuracy: row.Holdout_Within_One_State_Accuracy ?? row.holdoutWithinOneStateAccuracy,
    holdoutQuadraticWeightedKappa:
      row.Holdout_Quadratic_Weighted_Kappa ?? row.holdoutQuadraticWeightedKappa,
  }))
}

function formatFutureScenario(rows = []) {
  return rows.map((row) => ({
    scenario: row.Scenario ?? row.scenario,
    scenarioPga: row.Scenario_PGA_g ?? row.scenarioPga ?? null,
    meanPredictedEdr: row.Mean_Predicted_EDR ?? row.meanPredictedEdr,
    medianPredictedEdr: row.Median_Predicted_EDR ?? row.medianPredictedEdr,
    p90PredictedEdr: row.P90_Predicted_EDR ?? row.p90PredictedEdr,
    p95PredictedEdr: row.P95_Predicted_EDR ?? row.p95PredictedEdr,
    bridgesEdrGe002: row.Bridges_EDR_ge_0_02 ?? row.bridgesEdrGe002,
    bridgesEdrGe008: row.Bridges_EDR_ge_0_08 ?? row.bridgesEdrGe008,
    bridgesEdrGe025: row.Bridges_EDR_ge_0_25 ?? row.bridgesEdrGe025,
  }))
}

function formatFeatureImportance(rows = []) {
  return rows.map((row) => ({
    feature: row.Feature ?? row.feature,
    importance: row.Importance ?? row.importance,
  }))
}

function isUsableFeatureImportance(rows = []) {
  return rows.some((row) => Number(row.importance ?? row.Importance ?? 0) > 0)
}

export async function loadResearchData() {
  const [summary, damageState, futureScenario, hybridBest, recommendedMetrics, recommendedImportance, health, proxyValidation, researchManifest] =
    await Promise.all([
      fetchJson(DATA_PATHS.summary),
      fetchJson(DATA_PATHS.damageState),
      fetchJson(DATA_PATHS.futureScenario),
      fetchJson(DATA_PATHS.hybridBest),
      fetchJson(DATA_PATHS.recommendedMetrics),
      fetchJson(DATA_PATHS.recommendedImportance),
      fetchJson(DATA_PATHS.health),
      fetchJson(DATA_PATHS.proxyValidation),
      fetchJson(DATA_PATHS.researchManifest),
    ])

  if (!summary) {
    return fallbackResearchData
  }

  const healthPayload = health ?? {}
  const repoImportance = formatFeatureImportance(recommendedImportance)
  const featureImportanceSource =
    healthPayload.recommendedFeatureImportanceValid && isUsableFeatureImportance(repoImportance)
      ? 'repo'
      : 'fallback'

  return {
    availability: {
      repoData: true,
      figures: Array.isArray(researchManifest) && researchManifest.length > 0,
      featureImportanceSource,
      recommendedMetricsValid: Boolean(healthPayload.recommendedMetricsValid),
      notes: [
        'Repo-derived JSON snapshots were exported from the Python / notebook workflow into the frontend public data layer.',
        healthPayload.notes?.metrics,
        healthPayload.notes?.importance,
      ].filter(Boolean),
    },
    summary,
    analytics: {
      classifierMetrics: formatClassifierMetrics(damageState),
      futureScenarios: formatFutureScenario(futureScenario),
      proxyValidation: proxyValidation ?? fallbackResearchData.analytics.proxyValidation,
      hybridBest: hybridBest ?? [],
      recommendedMetrics:
        healthPayload.recommendedMetricsValid && Array.isArray(recommendedMetrics)
          ? recommendedMetrics
          : [],
      bridgeMlMetrics:
        healthPayload.bridgeMlCalibrationMetrics ?? fallbackResearchData.analytics.bridgeMlMetrics,
      featureImportance:
        featureImportanceSource === 'repo'
          ? repoImportance
          : healthPayload.fallbackFeatureImportance ?? fallbackResearchData.analytics.featureImportance,
    },
    evidence: Array.isArray(researchManifest) ? researchManifest : fallbackResearchData.evidence,
  }
}
