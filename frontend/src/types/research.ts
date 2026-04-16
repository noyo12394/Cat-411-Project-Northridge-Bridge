export type DashboardModeId = 'intrinsic' | 'event' | 'priority'

export interface RangeMetric {
  min: number
  max: number
}

export interface SummaryCounts {
  totalBridges: number
  hazardSampled: number
  mlCalibrationRows: number
  bridgeClasses: number
}

export interface PortfolioSummary {
  meanSVI: number
  medianSVI: number
  meanEDR: number
  meanPrototypeVulnerability: number
  meanPriorityScore: number
  sviRiskBands: Record<string, number>
  prototypeRiskBands: Record<string, number>
  modalDamageStates: Record<string, number>
}

export interface ClassProfile {
  bridgeClass: string
  count: number
  meanSVI: number
  meanEDR: number
}

export interface CountyProfile {
  countyCode: number | string | null
  count: number
  meanSVI: number
  meanEDR: number
}

export interface SampleBridge {
  label: string
  structureNumber: string
  countyCode: number | string | null
  countyLabel: string
  yearBuilt: number
  yearReconstructed: number | null
  spans: number
  maxSpan: number
  skew: number
  condition: number
  svi: number
  bridgeClass: string
  adt: number
  prototypeVulnerability: number
  priorityScore: number
}

export interface PipelineStep {
  label: string
  file: string
  output: string
}

export interface CalibrationPoint {
  Actual_EDR: number
  Predicted_EDR: number
  SVI: number
  year: number
  cond: number
  HWB_CLASS: string
}

export interface SiteSummary {
  generatedAt: string
  counts: SummaryCounts
  portfolio: PortfolioSummary
  classProfiles: ClassProfile[]
  countyProfiles: CountyProfile[]
  featureRanges: Record<string, RangeMetric>
  sampleBridges: SampleBridge[]
  pipeline: PipelineStep[]
  calibrationPoints: CalibrationPoint[]
}

export interface PortfolioBridge {
  structureNumber: string
  countyCode: number | string | null
  countyLabel: string
  bridgeClass: string
  yearBuilt: number
  yearReconstructed: number | null
  spans: number
  maxSpanFt: number
  maxSpanM: number
  skew: number
  condition: number
  svi: number
  edr: number
  adt: number
  latitude: number | null
  longitude: number | null
  pga: number | null
  modalDamageState: string | null
  prototypeVulnerability: number
  priorityScore: number
  riskBand: string
  inspectionTier: string
  componentCondition: number
  componentSVI: number
  componentAge: number
  componentRehab: number
  componentSkew: number
  componentMaxSpan: number
  componentBridgeClass: number
  componentSpans: number
}

export interface MethodologyPrior {
  key: string
  label: string
  weight: number
  group: string
  rationale: string
}

export interface MethodologyLayer {
  label: string
  description: string
}

export interface MethodologyReference {
  title: string
  url: string
  note: string
}

export interface MethodologyDiscipline {
  core: string
  event: string
  priority: string
  ndvi: string
}

export interface MethodologyPayload {
  status: string
  engineLabel: string
  discipline: MethodologyDiscipline
  priors: MethodologyPrior[]
  layers: MethodologyLayer[]
  references: MethodologyReference[]
}

export interface FutureScenarioRow {
  scenario: string
  scenarioPga: number | null
  meanPredictedEdr: number
  medianPredictedEdr: number
  p90PredictedEdr: number
  p95PredictedEdr: number
  bridgesEdrGe002: number
  bridgesEdrGe008: number
  bridgesEdrGe025: number
}

export interface BestModelRow {
  featureSet: string
  model: string
  cvMae: number
  cvRmse: number
  cvRmsle: number
  cvR2: number
  holdoutMae: number
  holdoutRmse: number
  holdoutRmsle: number
  holdoutR2: number
  holdoutRmsePositive: number | null
  holdoutR2Positive: number | null
}

export interface RecommendedModelMetric {
  featureSet: string
  model: string
  transform: string
  mae: number
  rmse: number
  rmsle: number
  medianAe: number
  r2: number
  maePositive: number | null
  rmsePositive: number | null
  rmslePositive: number | null
  r2Positive: number | null
}

export interface FeatureImportanceRow {
  feature: string
  importance: number
  importanceStd: number | null
  label: string
}

export interface DamageStateModelRow {
  featureGroup: string
  model: string
  holdoutBalancedAccuracy: number
  holdoutMacroF1: number
  holdoutWithinOneStateAccuracy: number
  holdoutQuadraticWeightedKappa: number
}

export interface ProxyValidationModel {
  label: string
  exactAccuracy: number
  withinOneStateAccuracy: number
  maeOrdinal: number
  weightedKappa: number
  macroF1: number
  underpredictionRate: number
}

export interface ProxyValidationPayload {
  subsetSize: number
  source: string
  models: ProxyValidationModel[]
}

export interface HazardHistogramBin {
  label: string
  start: number
  end: number
  count: number
}

export interface HazardCountyHotspot {
  countyLabel: string
  bridgeCount: number
  meanPga: number
  maxPga: number
  meanEdr: number
}

export interface HazardPoint {
  structureNumber: string
  latitude: number
  longitude: number
  countyLabel: string
  pga: number
  edr: number
  svi: number
}

export interface HazardProfile {
  sampledBridges: number
  positivePgaBridges: number
  quantiles: Record<string, number>
  histogram: HazardHistogramBin[]
  countyHotspots: HazardCountyHotspot[]
  samplePoints: HazardPoint[]
}

export interface DamageProbabilityRow {
  state: string
  probability: number
}

export interface DamageByClassRow {
  bridgeClass: string
  count: number
  meanPga: number
  meanEdr: number
  ds0: number
  ds1: number
  ds2: number
  ds3: number
  ds4: number
}

export interface FragilityCurvePoint {
  pga: number
  ds1: number
  ds2: number
  ds3: number
  ds4: number
  edr: number
}

export interface FragilityCurveBand {
  label: string
  meanSvi: number
  beta: number
  points: FragilityCurvePoint[]
}

export interface FragilityProfile {
  overallDamageProbabilities: DamageProbabilityRow[]
  damageByClass: DamageByClassRow[]
  fragilityCurves: FragilityCurveBand[]
}

export interface ResearchFigure {
  file: string
  title: string
  path: string
}

export interface AvailabilityNotes {
  repoData: boolean
  featureImportanceSource: 'repo' | 'fallback'
  recommendedMetricsValid: boolean
  notes: string[]
}

export interface DataHealthPayload {
  bridgeMlCalibrationMetrics?: {
    rows: number
    modelLabel: string
    mae: number
    rmse: number
    r2: number
  }
  fallbackFeatureImportance?: FeatureImportanceRow[]
  recommendedFeatureImportanceValid?: boolean
  recommendedMetricsValid?: boolean
  notes?: Record<string, string>
}

export interface ResearchData {
  availability: AvailabilityNotes
  summary: SiteSummary
  portfolio: PortfolioBridge[]
  methodology: MethodologyPayload
  futureScenarios: FutureScenarioRow[]
  bestModels: BestModelRow[]
  recommendedModel: RecommendedModelMetric | null
  featureImportance: FeatureImportanceRow[]
  damageStateModels: DamageStateModelRow[]
  proxyValidation: ProxyValidationPayload
  hazardProfile: HazardProfile | null
  fragilityProfile: FragilityProfile | null
  dataHealth: DataHealthPayload | null
  researchFigures: ResearchFigure[]
}

export interface DashboardInputs {
  structureNumber: string
  yearBuilt: number
  yearReconstructed: number | ''
  skew: number
  spans: number
  maxSpan: number
  condition: number
  bridgeClass: string
  svi: number
  ndviChange: number | ''
  adt: number
  scenarioPga: number
}

export interface AssessmentDriver {
  key: string
  label: string
  value: number
  description: string
}

export interface AssessmentRecommendation {
  title: string
  detail: string
}

export interface BridgeVisualState {
  mode: DashboardModeId
  stage: number
  structuralSeverity: number
  headlineSeverity: number
  deckSag: number
  deckOffset: number
  crackIntensity: number
  columnLean: number
  fracture: number
  collapse: number
  waveAmp: number
  dust: number
  groundShift: number
  urgencyPulse: number
  emergencyTint: number
}

export interface DashboardAssessment {
  mode: DashboardModeId
  headlineScore: number
  intrinsicScore: number
  eventScore: number
  priorityScore: number
  riskLevel: string
  damageLabel: string
  stageLabel: string
  scenarioLabel: string
  narrative: string
  confidenceLabel: string
  confidence: number
  trafficLabel: string
  drivers: AssessmentDriver[]
  recommendations: AssessmentRecommendation[]
  visual: BridgeVisualState
}
