import { fallbackResearchData } from '../data/fallbackResearchData'
import type {
  BestModelRow,
  DamageStateModelRow,
  DataHealthPayload,
  FeatureImportanceRow,
  FragilityProfile,
  FutureScenarioRow,
  HazardProfile,
  MethodologyPayload,
  PortfolioBridge,
  ProxyValidationPayload,
  RecommendedModelMetric,
  ResearchData,
  ResearchFigure,
  SiteSummary,
} from '../types/research'

const DATA_PATHS = {
  summary: '/data/site_summary.json',
  portfolio: '/data/bridge_portfolio.json',
  methodology: '/data/methodology_priors.json',
  futureScenarios: '/data/future_scenario_summary.json',
  bestModels: '/data/ml_hybrid_best_by_feature_set.json',
  recommendedMetrics: '/data/ml_recommended_hybrid_metrics.json',
  featureImportance: '/data/ml_recommended_hybrid_feature_importance.json',
  damageStateModels: '/data/damage_state_best_by_feature_set.json',
  proxyValidation: '/data/proxy_validation.json',
  hazardProfile: '/data/hazard_profile.json',
  fragilityProfile: '/data/fragility_profile.json',
  dataHealth: '/data/data_health.json',
  researchManifest: '/research/manifest.json',
} as const

async function fetchJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(path, { cache: 'no-store' })
    if (!response.ok) {
      return null
    }
    return (await response.json()) as T
  } catch {
    return null
  }
}

function toNumber(value: unknown, fallback = 0): number {
  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric : fallback
}

function toNullableNumber(value: unknown): number | null {
  const numeric = Number(value)
  return Number.isFinite(numeric) ? numeric : null
}

function normalizeFutureScenarios(rows: Array<Record<string, unknown>> | null): FutureScenarioRow[] {
  return (rows ?? []).map((row) => ({
    scenario: String(row.Scenario ?? row.scenario ?? 'Scenario'),
    scenarioPga: toNullableNumber(row.Scenario_PGA_g ?? row.scenarioPga),
    meanPredictedEdr: toNumber(row.Mean_Predicted_EDR ?? row.meanPredictedEdr),
    medianPredictedEdr: toNumber(row.Median_Predicted_EDR ?? row.medianPredictedEdr),
    p90PredictedEdr: toNumber(row.P90_Predicted_EDR ?? row.p90PredictedEdr),
    p95PredictedEdr: toNumber(row.P95_Predicted_EDR ?? row.p95PredictedEdr),
    bridgesEdrGe002: toNumber(row.Bridges_EDR_ge_0_02 ?? row.bridgesEdrGe002),
    bridgesEdrGe008: toNumber(row.Bridges_EDR_ge_0_08 ?? row.bridgesEdrGe008),
    bridgesEdrGe025: toNumber(row.Bridges_EDR_ge_0_25 ?? row.bridgesEdrGe025),
  }))
}

function normalizeBestModels(rows: Array<Record<string, unknown>> | null): BestModelRow[] {
  return (rows ?? []).map((row) => ({
    featureSet: String(row['Feature Set'] ?? row.featureSet ?? 'Feature Set'),
    model: String(row.Model ?? row.model ?? 'Model'),
    cvMae: toNumber(row.CV_MAE ?? row.cvMae),
    cvRmse: toNumber(row.CV_RMSE ?? row.cvRmse),
    cvRmsle: toNumber(row.CV_RMSLE ?? row.cvRmsle),
    cvR2: toNumber(row.CV_R2 ?? row.cvR2),
    holdoutMae: toNumber(row.Holdout_MAE ?? row.holdoutMae),
    holdoutRmse: toNumber(row.Holdout_RMSE ?? row.holdoutRmse),
    holdoutRmsle: toNumber(row.Holdout_RMSLE ?? row.holdoutRmsle),
    holdoutR2: toNumber(row.Holdout_R2 ?? row.holdoutR2),
    holdoutRmsePositive: toNullableNumber(row.Holdout_RMSE_Positive ?? row.holdoutRmsePositive),
    holdoutR2Positive: toNullableNumber(row.Holdout_R2_Positive ?? row.holdoutR2Positive),
  }))
}

function normalizeFeatureImportance(rows: Array<Record<string, unknown>> | null): FeatureImportanceRow[] {
  return (rows ?? []).map((row) => ({
    feature: String(row.Feature ?? row.feature ?? 'Feature'),
    importance: toNumber(row.Importance ?? row.importance),
    importanceStd: toNullableNumber(row.Importance_std ?? row.importanceStd),
    label: String(row.Label ?? row.label ?? ''),
  }))
}

function normalizeDamageStateModels(rows: Array<Record<string, unknown>> | null): DamageStateModelRow[] {
  return (rows ?? []).map((row) => ({
    featureGroup: String(row['Feature Group'] ?? row.featureGroup ?? 'Feature Group'),
    model: String(row.Model ?? row.model ?? 'Model'),
    holdoutBalancedAccuracy: toNumber(
      row.Holdout_Balanced_Accuracy ?? row.holdoutBalancedAccuracy,
    ),
    holdoutMacroF1: toNumber(row.Holdout_Macro_F1 ?? row.holdoutMacroF1),
    holdoutWithinOneStateAccuracy: toNumber(
      row.Holdout_Within_One_State_Accuracy ?? row.holdoutWithinOneStateAccuracy,
    ),
    holdoutQuadraticWeightedKappa: toNumber(
      row.Holdout_Quadratic_Weighted_Kappa ?? row.holdoutQuadraticWeightedKappa,
    ),
  }))
}

function normalizeRecommendedMetric(rows: Array<Record<string, unknown>> | null): RecommendedModelMetric | null {
  const row = rows?.[0]
  if (!row) {
    return null
  }
  return {
    featureSet: String(row['Feature Set'] ?? row.featureSet ?? 'Feature Set'),
    model: String(row.Model ?? row.model ?? 'Model'),
    transform: String(row.Transform ?? row.transform ?? 'Transform'),
    mae: toNumber(row.MAE ?? row.mae),
    rmse: toNumber(row.RMSE ?? row.rmse),
    rmsle: toNumber(row.RMSLE ?? row.rmsle),
    medianAe: toNumber(row.MedianAE ?? row.medianAe),
    r2: toNumber(row.R2 ?? row.r2),
    maePositive: toNullableNumber(row.MAE_Positive ?? row.maePositive),
    rmsePositive: toNullableNumber(row.RMSE_Positive ?? row.rmsePositive),
    rmslePositive: toNullableNumber(row.RMSLE_Positive ?? row.rmslePositive),
    r2Positive: toNullableNumber(row.R2_Positive ?? row.r2Positive),
  }
}

function normalizePortfolio(rows: Array<Record<string, unknown>> | null): PortfolioBridge[] {
  return (rows ?? []).map((row) => ({
    structureNumber: String(row.structureNumber ?? row.STRUCTURE_NUMBER_008 ?? ''),
    countyCode: (row.countyCode as number | string | null) ?? null,
    countyLabel: String(row.countyLabel ?? 'County unknown'),
    bridgeClass: String(row.bridgeClass ?? row.HWB_CLASS ?? 'HWB6'),
    yearBuilt: toNumber(row.yearBuilt),
    yearReconstructed: toNullableNumber(row.yearReconstructed),
    spans: toNumber(row.spans),
    maxSpanFt: toNumber(row.maxSpanFt ?? row.maxSpan),
    maxSpanM: toNumber(row.maxSpanM),
    skew: toNumber(row.skew),
    condition: toNumber(row.condition),
    svi: toNumber(row.svi),
    edr: toNumber(row.edr),
    adt: toNumber(row.adt),
    latitude: toNullableNumber(row.latitude),
    longitude: toNullableNumber(row.longitude),
    pga: toNullableNumber(row.pga),
    modalDamageState: row.modalDamageState ? String(row.modalDamageState) : null,
    prototypeVulnerability: toNumber(row.prototypeVulnerability),
    priorityScore: toNumber(row.priorityScore),
    riskBand: String(row.riskBand ?? 'Guarded'),
    inspectionTier: String(row.inspectionTier ?? 'Routine review'),
    componentCondition: toNumber(row.componentCondition),
    componentSVI: toNumber(row.componentSVI),
    componentAge: toNumber(row.componentAge),
    componentRehab: toNumber(row.componentRehab),
    componentSkew: toNumber(row.componentSkew),
    componentMaxSpan: toNumber(row.componentMaxSpan),
    componentBridgeClass: toNumber(row.componentBridgeClass),
    componentSpans: toNumber(row.componentSpans),
  }))
}

function normalizeResearchFigures(rows: Array<Record<string, unknown>> | null): ResearchFigure[] {
  return (rows ?? []).map((row) => ({
    file: String(row.file ?? ''),
    title: String(row.title ?? ''),
    path: String(row.path ?? ''),
  }))
}

function fallbackData(): ResearchData {
  const fallback = fallbackResearchData as unknown as {
    summary?: Record<string, unknown>
    methodology?: MethodologyPayload
    portfolio?: { bridges?: Array<Record<string, unknown>> }
    analytics?: {
      featureImportance?: Array<Record<string, unknown>>
      proxyValidation?: ProxyValidationPayload
    }
  }
  const bridgePortfolio = (fallback.portfolio?.bridges ?? []).map((bridge: Record<string, unknown>) => ({
    structureNumber: String(bridge.structureNumber ?? ''),
    countyCode: bridge.countyCode as number | string | null,
    countyLabel: String(bridge.countyLabel ?? 'County unknown'),
    bridgeClass: String(bridge.bridgeClass ?? 'HWB6'),
    yearBuilt: toNumber(bridge.yearBuilt, 1980),
    yearReconstructed: toNullableNumber(bridge.yearReconstructed),
    spans: toNumber(bridge.spans, 3),
    maxSpanFt: toNumber(bridge.maxSpanFt ?? bridge.maxSpan, 80),
    maxSpanM: toNumber(bridge.maxSpanM),
    skew: toNumber(bridge.skew, 12),
    condition: toNumber(bridge.condition, 6),
    svi: toNumber(bridge.svi, 0.42),
    edr: toNumber(bridge.edr, 0.02),
    adt: toNumber(bridge.adt, 8000),
    latitude: toNullableNumber(bridge.latitude),
    longitude: toNullableNumber(bridge.longitude),
    pga: toNullableNumber(bridge.pga),
    modalDamageState: bridge.modalDamageState ? String(bridge.modalDamageState) : null,
    prototypeVulnerability: toNumber(bridge.prototypeVulnerability, 0.41),
    priorityScore: toNumber(bridge.priorityScore, 0.48),
    riskBand: String(bridge.riskBand ?? 'Guarded'),
    inspectionTier: String(bridge.inspectionTier ?? 'Priority review'),
    componentCondition: toNumber(bridge.componentCondition, 0.2),
    componentSVI: toNumber(bridge.componentSVI, 0.18),
    componentAge: toNumber(bridge.componentAge, 0.14),
    componentRehab: toNumber(bridge.componentRehab, 0.09),
    componentSkew: toNumber(bridge.componentSkew, 0.07),
    componentMaxSpan: toNumber(bridge.componentMaxSpan, 0.06),
    componentBridgeClass: toNumber(bridge.componentBridgeClass, 0.05),
    componentSpans: toNumber(bridge.componentSpans, 0.04),
  }))

  return {
    availability: {
      repoData: false,
      featureImportanceSource: 'fallback',
      recommendedMetricsValid: false,
      notes: ['Using bundled fallback data because repo-exported JSON snapshots were unavailable.'],
    },
    summary: fallback.summary as unknown as SiteSummary,
    portfolio: bridgePortfolio,
    methodology: fallback.methodology as MethodologyPayload,
    futureScenarios: [],
    bestModels: [],
    recommendedModel: null,
    featureImportance: normalizeFeatureImportance(
      (fallback.analytics?.featureImportance ?? []).map((item: Record<string, unknown>) => ({
        Feature: item.feature,
        Importance: item.importance,
      })),
    ),
    damageStateModels: [],
    proxyValidation: fallback.analytics?.proxyValidation as ProxyValidationPayload,
    hazardProfile: null,
    fragilityProfile: null,
    dataHealth: null,
    researchFigures: [],
  }
}

export async function loadResearchData(): Promise<ResearchData> {
  const [
    summary,
    portfolio,
    methodology,
    futureScenarios,
    bestModels,
    recommendedMetrics,
    featureImportance,
    damageStateModels,
    proxyValidation,
    hazardProfile,
    fragilityProfile,
    dataHealth,
    researchManifest,
  ] = await Promise.all([
    fetchJson<SiteSummary>(DATA_PATHS.summary),
    fetchJson<Array<Record<string, unknown>>>(DATA_PATHS.portfolio),
    fetchJson<MethodologyPayload>(DATA_PATHS.methodology),
    fetchJson<Array<Record<string, unknown>>>(DATA_PATHS.futureScenarios),
    fetchJson<Array<Record<string, unknown>>>(DATA_PATHS.bestModels),
    fetchJson<Array<Record<string, unknown>>>(DATA_PATHS.recommendedMetrics),
    fetchJson<Array<Record<string, unknown>>>(DATA_PATHS.featureImportance),
    fetchJson<Array<Record<string, unknown>>>(DATA_PATHS.damageStateModels),
    fetchJson<ProxyValidationPayload>(DATA_PATHS.proxyValidation),
    fetchJson<HazardProfile>(DATA_PATHS.hazardProfile),
    fetchJson<FragilityProfile>(DATA_PATHS.fragilityProfile),
    fetchJson<DataHealthPayload>(DATA_PATHS.dataHealth),
    fetchJson<Array<Record<string, unknown>>>(DATA_PATHS.researchManifest),
  ])

  if (!summary || !portfolio || !methodology || !proxyValidation) {
    return fallbackData()
  }

  const normalizedFeatureImportance = normalizeFeatureImportance(featureImportance)
  const featureImportanceSource =
    dataHealth?.recommendedFeatureImportanceValid && normalizedFeatureImportance.some((row) => row.importance > 0)
      ? 'repo'
      : 'fallback'

  return {
    availability: {
      repoData: true,
      featureImportanceSource,
      recommendedMetricsValid: Boolean(dataHealth?.recommendedMetricsValid),
      notes: [
        'Repo-derived JSON snapshots and figures are feeding the frontend.',
        dataHealth?.notes?.metrics,
        dataHealth?.notes?.importance,
      ].filter(Boolean) as string[],
    },
    summary,
    portfolio: normalizePortfolio(portfolio),
    methodology,
    futureScenarios: normalizeFutureScenarios(futureScenarios),
    bestModels: normalizeBestModels(bestModels),
    recommendedModel: normalizeRecommendedMetric(recommendedMetrics),
    featureImportance:
      featureImportanceSource === 'repo'
        ? normalizedFeatureImportance
        : normalizeFeatureImportance(
            dataHealth?.fallbackFeatureImportance?.map((item) => ({
              Feature: item.feature,
              Importance: item.importance,
              Importance_std: item.importanceStd,
              Label: item.label,
            })) ?? [],
          ),
    damageStateModels: normalizeDamageStateModels(damageStateModels),
    proxyValidation,
    hazardProfile,
    fragilityProfile,
    dataHealth,
    researchFigures: normalizeResearchFigures(researchManifest),
  }
}
