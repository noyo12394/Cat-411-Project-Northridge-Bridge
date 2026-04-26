# ML Target Formulation Study

This study answers the target-variable question directly. A hazard-independent vulnerability model should not be trained to predict event damage caused by one shaking field. It should predict bridge-level intrinsic fragility parameters, then translate those parameters into event-specific damage only after a PGA scenario is supplied.

## Research Question

- What is the defensible target for a hazard-independent bridge vulnerability model?
- How much changes when EDR is predicted directly instead of predicting fragility first?
- Where should SVI, NDVI, PGA, and consequence variables live in the framework?

## Data And Existing Logic Used

- Source table: `data/processed/bridges_with_svi.csv`
- Rows modeled: `25,975`
- Cross-validation rows: `8,000` stratified by SVI quintile for portable runtime; holdout metrics use the full 20 percent split.
- Fragility targets: `MU_DS1_LINEAR, MU_DS2_LINEAR, MU_DS3_LINEAR, MU_DS4_LINEAR, BETA_SVI`
- Event target: `EDR` from the repository HAZUS/SVI pipeline
- NDVI source: `data/processed/final_bridge_analysis.csv`
- Rows with joined NDVI change: `16,156`

The script recomputes SVI and fragility parameters through `svi_methodology.py` before modeling, so the target logic remains tied to the repository methodology. The current repo formulation uses linear fragility medians for DS1-DS4 and `BETA_SVI = 0.6 + 0.2 * SVI`.

## Target Formulations Built

### A. Hazard-independent core target

The main model is multi-output regression for DS1 median, DS2 median, DS3 median, DS4 median, and beta. This is the preferred formulation because the target is a bridge-level fragility description rather than damage under a particular earthquake. The predictions can be reused for any PGA scenario.

### B. Event-specific target

The downstream comparison model predicts `EDR` directly and is allowed to use `PGA`. This branch is useful for scenario damage prediction, but it should not replace the core vulnerability model because its target and features mix structural vulnerability with event demand.

## Feature Families

- `Structural Core`: intrinsic inventory features only; no PGA, no SVI, no NDVI, no ADT, no coordinates.
- `Structural + SVI`: adds SVI as a contextual vulnerability index. Because the fragility targets are derived from SVI in the existing repository logic, this family is partly a consistency/audit test rather than an independent discovery test.
- `Structural + SVI + NDVI`: post-event extension only. It is not presented as the core hazard-independent model.
- `Event Damage Family`: structural features + SVI + PGA for direct EDR prediction.
- `Prioritization Layer`: ADT, truck percentage, detour, and lane variables are applied only after prediction.

## Models Compared

`Linear Regression`, `Ridge Regression`, `Lasso Regression`, `Elastic Net`, `Decision Tree`, `Random Forest`, `Extra Trees`, `Gradient Boosting`, `HistGradientBoosting`, `AdaBoost`, `KNeighbors`, `Support Vector Regressor (LinearSVR)`, `MLPRegressor`

For multi-output fragility regression, `Gradient Boosting`, `HistGradientBoosting`, `AdaBoost`, and `LinearSVR` are wrapped with `MultiOutputRegressor`; the other estimators support multi-output regression directly in this workflow.

## Best Fragility Models By Family

| Model Family | Model | CV_RMSE_mean | CV_R2_mean | Holdout_RMSE_mean | Holdout_R2_mean | Fit_seconds |
| --- | --- | --- | --- | --- | --- | --- |
| Structural + SVI + NDVI | Linear Regression | 0.000000 | 1.000000 | 0.000000 | 1.000000 | 0.061251 |
| Structural + SVI | Linear Regression | 0.000000 | 1.000000 | 0.000000 | 1.000000 | 0.047509 |
| Structural Core | Random Forest | 0.023450 | 0.887358 | 0.018226 | 0.920268 | 0.792420 |

## Top 5 Fragility-Target Models

| Model Family | Model | Holdout_RMSE_mean | Holdout_R2_mean | CV_RMSE_mean | CV_R2_mean |
| --- | --- | --- | --- | --- | --- |
| Structural + SVI + NDVI | Linear Regression | 0.000000 | 1.000000 | 0.000000 | 1.000000 |
| Structural + SVI | Linear Regression | 0.000000 | 1.000000 | 0.000000 | 1.000000 |
| Structural + SVI | Ridge Regression | 0.000009 | 1.000000 | 0.000039 | 1.000000 |
| Structural + SVI + NDVI | Ridge Regression | 0.000009 | 1.000000 | 0.000039 | 1.000000 |
| Structural + SVI | Lasso Regression | 0.000100 | 0.999994 | 0.000100 | 0.999994 |

## Top 5 Direct EDR Event Models

| Model Family | Model | Holdout_RMSE | Holdout_R2 | CV_RMSE | CV_R2 |
| --- | --- | --- | --- | --- | --- |
| Event Damage Family | Decision Tree | 0.002307 | 0.996793 | 0.004464 | 0.988291 |
| Event Damage Family | AdaBoost | 0.005217 | 0.983607 | 0.005399 | 0.982526 |
| Event Damage Family | HistGradientBoosting | 0.006118 | 0.977456 | 0.007060 | 0.970700 |
| Event Damage Family | KNeighbors | 0.006669 | 0.973208 | 0.010285 | 0.938006 |
| Event Damage Family | Gradient Boosting | 0.008249 | 0.959013 | 0.008265 | 0.959864 |

## Reconstruction Test

After predicting fragility medians and beta, the script reconstructs damage probabilities and EDR at each bridge's observed PGA. This tests whether the fragility-first target can recover event outputs without training the core model on PGA.

| Comparison | MAE | RMSE | R2 |
| --- | --- | --- | --- |
| Fragility-first structural core reconstructed at observed PGA | 0.000162 | 0.001081 | 0.999296 |
| Direct event EDR model with PGA | 0.000360 | 0.002307 | 0.996793 |

Interpretation: direct EDR prediction is allowed to use PGA and may fit event damage well, but in this run the fragility-first structural-core reconstruction had lower holdout EDR RMSE (`0.001081` for the first row versus `0.002307` for direct EDR). The important conceptual distinction remains that the fragility-first branch stores reusable structural response parameters and applies PGA only downstream.

## SVI And NDVI Ablation

| Question | Baseline Family | Test Family | Baseline Holdout_RMSE_mean | Test Holdout_RMSE_mean | Delta Holdout_RMSE_mean | Improved | Interpretation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Does SVI improve the fragility-target model? | Structural Core | Structural + SVI | 0.018226 | 0.000000 | -0.018226 | True | SVI is part of the target-generating methodology, so gains are expected and should be described as consistency/context. |
| Does NDVI help the post-event extension? | Structural + SVI | Structural + SVI + NDVI | 0.000000 | 0.000000 | -0.000000 | False | Any NDVI change below 1e-6 RMSE is treated as numerically negligible; NDVI remains post-event/contextual, not intrinsic structural vulnerability. |
| What is gained by direct EDR prediction? | Fragility-first structural core reconstructed at observed PGA | Direct event EDR with PGA | 0.001081 | 0.002307 | 0.001226 | False | Direct EDR fits event damage, but it mixes hazard demand into the modeling target. |

- SVI holdout RMSE delta versus structural core: `-0.018226`.
- NDVI holdout RMSE delta versus structural + SVI: `-0.000000`.
- Delta values smaller than `1e-6` RMSE are treated as numerically negligible.

The SVI result must be interpreted carefully. Since the repository's fragility targets are generated from SVI, adding SVI as a predictor can make the fragility target nearly formula-recoverable. That is useful as an audit that the ML pipeline is consistent with the SVI methodology, but it should not be overclaimed as independent evidence that SVI discovered new vulnerability physics.

NDVI belongs in a post-event/contextual branch. If it helps, it helps explain observed landscape or access changes after an event; it is not an intrinsic bridge structural property.

## Figures

- `figures/ml_target_strategy_overview.png`
- `figures/ml_fragility_model_comparison.png`
- `figures/ml_direct_edr_model_comparison.png`
- `figures/ml_target_top5_models.png`
- `figures/ml_fragility_actual_vs_predicted.png`
- `figures/ml_direct_edr_actual_vs_predicted.png`
- `figures/ml_target_residual_diagnostics.png`
- `figures/ml_fragility_reconstruction_vs_edr.png`
- `figures/ml_target_ablation.png`
- `figures/ml_target_feature_importance.png`
- `figures/ml_target_sensitivity_plots.png`
- `figures/ml_fragility_curve_comparison.png`
- `figures/ml_ndvi_context_role.png`
- `figures/ml_recommended_framework_summary.png`

## Recommended ML Formulation For This Project

The main hazard-independent target should be fragility median and beta parameters, preferably as a multi-output regression target: `DS1_median`, `DS2_median`, `DS3_median`, `DS4_median`, and `beta`. This directly answers the professor's concern because the target describes intrinsic structural vulnerability rather than event damage under one PGA field.

Direct EDR prediction should be kept as a comparison branch and as an event-damage branch. It is allowed to use PGA and may sometimes achieve stronger event-fit metrics, but those metrics would not prove that it is the better vulnerability target. They show that event demand is being modeled directly.

SVI belongs as a contextual/additive vulnerability feature and as a transparent engineering baseline. Because the current fragility targets are generated from SVI, the `Structural + SVI` fragility model should be described as a consistency check or calibrated SVI-recovery model, not as fully independent validation. For the dashboard, SVI can be shown beside the ML fragility output and used to explain why a bridge received a certain intrinsic score.

NDVI belongs only in a post-event proxy or context layer. It should not feed the core hazard-independent vulnerability model because vegetation change is not an intrinsic structural property of the bridge.

PGA belongs only in the scenario translator and direct event-damage branch. The dashboard should apply selected PGA scenarios after the fragility model predicts bridge-level medians and beta.

ADT, truck percentage, detour distance, and related variables should feed the prioritization layer after vulnerability prediction. They answer consequence and inspection-priority questions, not structural vulnerability questions.

For the future dashboard, the recommended flow is: structural inventory features -> fragility-target model -> scenario PGA translator -> damage probabilities/EDR -> optional NDVI context -> priority ranking with consequence variables.

## Generated Outputs

- `scripts/run_fragility_target_ml_study.py`
- `docs/ML_TARGET_FORMULATION_STUDY.md`
- `data/processed/ml_fragility_target_training_dataset.csv`
- `data/processed/ml_fragility_target_model_comparison.csv`
- `data/processed/ml_fragility_target_best_by_family.csv`
- `data/processed/ml_fragility_target_predictions.csv`
- `data/processed/ml_fragility_target_feature_importance.csv`
- `data/processed/ml_direct_edr_model_comparison.csv`
- `data/processed/ml_direct_edr_predictions.csv`
- `data/processed/ml_fragility_reconstruction_metrics.csv`
- `data/processed/ml_fragility_reconstruction_by_pga_bin.csv`
- `data/processed/ml_target_strategy_summary.csv`
- `data/processed/ml_target_priority_scores.csv`
- `figures/ml_target_strategy_overview.png`
- `figures/ml_fragility_model_comparison.png`
- `figures/ml_direct_edr_model_comparison.png`
- `figures/ml_target_top5_models.png`
- `figures/ml_fragility_actual_vs_predicted.png`
- `figures/ml_direct_edr_actual_vs_predicted.png`
- `figures/ml_target_residual_diagnostics.png`
- `figures/ml_fragility_reconstruction_vs_edr.png`
- `figures/ml_target_ablation.png`
- `figures/ml_target_feature_importance.png`
- `figures/ml_target_sensitivity_plots.png`
- `figures/ml_fragility_curve_comparison.png`
- `figures/ml_ndvi_context_role.png`
- `figures/ml_recommended_framework_summary.png`
