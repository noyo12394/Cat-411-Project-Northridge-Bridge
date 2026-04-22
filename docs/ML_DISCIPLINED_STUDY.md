# Disciplined ML Vulnerability Study

This analysis is the conceptually disciplined ML study for the bridge vulnerability project. The target is continuous HAZUS-derived `EDR`, so the task is regression. The study deliberately separates intrinsic structural vulnerability, SVI context, post-event NDVI proxy information, and downstream consequence / prioritization variables.

## Guardrails

- `PGA` is not used in the core vulnerability feature families.
- `ADT`, truck percentage, detour distance, lanes, and functional class are not used as vulnerability predictors.
- `NDVI` appears only in the extended post-event model family.
- `SVI` is tested as an additive covariate rather than forced into every model.
- Consequence variables are used only after prediction to create an inspection-priority layer.

## Dataset And Target

- Rows used: `25,975`
- Positive `EDR` rows: `12,879`
- Target: continuous `EDR` regression
- NDVI source: `data/change_detection/pga_bridge_ndvi_200m.csv`
- Rows with non-null NDVI change joined into ML table: `16,156`

## Feature Role Manifest

| Feature | Role | Use |
| --- | --- | --- |
| age_years | intrinsic structural | Bridge age derived from year built. |
| time_since_rehab | intrinsic structural | Years since reconstruction, falling back to bridge age. |
| reconstructed_flag | intrinsic structural | Whether a reconstruction year is recorded. |
| spans | intrinsic structural | Number of main spans. |
| max_span_log1p | intrinsic structural | Log transformed maximum span length. |
| skew | intrinsic structural | Skew angle in degrees. |
| cond | intrinsic structural | Condition rating proxy. |
| deck_area_log1p | intrinsic structural | Log transformed bridge deck area / structural scale. |
| operating_rating | intrinsic structural | Operating rating from inventory. |
| HWB_CLASS | intrinsic structural class | HAZUS bridge class used as structural-system descriptor, not hazard demand. |
| design_era_1989 | intrinsic design context | Design-era category derived from effective construction / reconstruction year. |
| SVI | contextual vulnerability covariate | Added only in Structural + SVI family to test incremental value. |
| ndvi_change | post-event proxy | Added only in extended post-event family. |
| ndvi_loss | post-event proxy | Negative NDVI change recoded as nonnegative post-event loss proxy. |
| adt_raw | consequence / prioritization only | Used only after vulnerability prediction for ranking, never in core regression. |
| truck_pct | consequence / prioritization only | Used only after vulnerability prediction for ranking. |
| detour_km | consequence / prioritization only | Used only after vulnerability prediction for ranking. |

## Model Families

- `Structural-only core`: `age_years, time_since_rehab, reconstructed_flag, spans, max_span_log1p, skew, cond, deck_area_log1p, operating_rating, HWB_CLASS, design_era_1989`
- `Structural + SVI`: `age_years, time_since_rehab, reconstructed_flag, spans, max_span_log1p, skew, cond, deck_area_log1p, operating_rating, HWB_CLASS, design_era_1989, SVI`
- `Structural + SVI + NDVI`: `age_years, time_since_rehab, reconstructed_flag, spans, max_span_log1p, skew, cond, deck_area_log1p, operating_rating, HWB_CLASS, design_era_1989, SVI, ndvi_change, ndvi_loss`

## Methods Compared

- `Linear Regression`: Transparent ordinary least-squares baseline.
- `Ridge Regression`: Linear baseline with L2 regularization for collinearity control.
- `Lasso Regression`: Sparse linear baseline with L1 feature selection pressure.
- `Elastic Net`: Hybrid L1/L2 linear baseline.
- `Decision Tree`: Single nonlinear tree baseline for interpretability.
- `Random Forest`: Bagged tree ensemble for robust tabular nonlinearities.
- `Extra Trees`: Randomized tree ensemble, often strong on tabular data.
- `Gradient Boosting`: Sequential boosting baseline for nonlinear structured data.
- `HistGradientBoosting`: Fast histogram-based boosting for larger tabular datasets.
- `AdaBoost`: Boosting baseline that reweights difficult examples.
- `KNeighbors`: Distance-based nonparametric baseline.
- `Support Vector Regressor (LinearSVR)`: Portable support-vector regressor baseline; avoids RBF SVR cost on 25k rows.
- `MLPRegressor`: Small neural-network baseline for tabular comparison.

## Best Model By Family

| Model Family | Model | CV_MAE | CV_RMSE | CV_R2 | Holdout_MAE | Holdout_RMSE | Holdout_R2 | Fit_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Structural-only core | Random Forest | 0.012853 | 0.039079 | 0.139127 | 0.013198 | 0.040833 | 0.151138 | 1.287722 |
| Structural + SVI | Random Forest | 0.012983 | 0.039219 | 0.133038 | 0.013359 | 0.041003 | 0.144071 | 1.711808 |
| Structural + SVI + NDVI | Random Forest | 0.012811 | 0.039398 | 0.125000 | 0.013035 | 0.040927 | 0.147247 | 1.452906 |

## Ablation Answer

| Question | Baseline Family | Test Family | Baseline Best CV_RMSE | Test Best CV_RMSE | Delta CV_RMSE | Improved? |
| --- | --- | --- | --- | --- | --- | --- |
| Does SVI improve over structural-only? | Structural-only core | Structural + SVI | 0.039079 | 0.039219 | 0.000140 | False |
| Does NDVI add value only in post-event setup? | Structural + SVI | Structural + SVI + NDVI | 0.039219 | 0.039398 | 0.000179 | False |

## Top Overall Rows

| Model Family | Model | CV_MAE | CV_RMSE | CV_R2 | Holdout_RMSE | Holdout_R2 | Fit_seconds |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Structural-only core | Random Forest | 0.012853 | 0.039079 | 0.139127 | 0.040833 | 0.151138 | 1.287722 |
| Structural + SVI | Random Forest | 0.012983 | 0.039219 | 0.133038 | 0.041003 | 0.144071 | 1.711808 |
| Structural + SVI + NDVI | Random Forest | 0.012811 | 0.039398 | 0.125000 | 0.040927 | 0.147247 | 1.452906 |
| Structural + SVI + NDVI | HistGradientBoosting | 0.012789 | 0.039407 | 0.124434 | 0.040568 | 0.162131 | 4.272198 |
| Structural-only core | HistGradientBoosting | 0.012977 | 0.039414 | 0.124396 | 0.040991 | 0.144566 | 2.799291 |
| Structural + SVI + NDVI | Extra Trees | 0.012890 | 0.039445 | 0.122985 | 0.041101 | 0.139996 | 0.829924 |
| Structural + SVI | HistGradientBoosting | 0.013042 | 0.039548 | 0.118489 | 0.041035 | 0.142755 | 3.431921 |
| Structural-only core | Extra Trees | 0.013094 | 0.039581 | 0.116926 | 0.041197 | 0.135949 | 0.802571 |
| Structural + SVI | Extra Trees | 0.013125 | 0.039639 | 0.114369 | 0.041352 | 0.129446 | 1.121371 |
| Structural-only core | KNeighbors | 0.012983 | 0.040206 | 0.088533 | 0.041792 | 0.110827 | 0.033031 |
| Structural + SVI | KNeighbors | 0.013096 | 0.040381 | 0.080753 | 0.041929 | 0.104996 | 0.036087 |
| Structural + SVI + NDVI | KNeighbors | 0.012850 | 0.040413 | 0.079318 | 0.042356 | 0.086651 | 0.063139 |
| Structural + SVI + NDVI | Gradient Boosting | 0.013392 | 0.040511 | 0.074983 | 0.042584 | 0.076799 | 8.174404 |
| Structural-only core | Gradient Boosting | 0.013679 | 0.040861 | 0.058957 | 0.043076 | 0.055343 | 5.367025 |
| Structural + SVI | Gradient Boosting | 0.013693 | 0.040863 | 0.058847 | 0.042984 | 0.059376 | 6.717793 |

## Interpretation Notes

- The structural-only family answers which bridge-intrinsic variables can approximate relative vulnerability without hazard demand.
- The structural + SVI family tests whether the SVI summary adds information beyond the raw structural variables.
- The NDVI family is a post-event extension, not the baseline vulnerability model.
- The priority output demonstrates where ADT belongs: ranking / consequence, not structural vulnerability prediction.
- Because `EDR` is derived from the HAZUS-style workflow, these models are surrogate vulnerability screens, not independent validation against observed bridge damage.

## Generated Outputs

- `data/processed/ml_disciplined_training_dataset.csv`
- `data/processed/ml_structural_only_core_results.csv`
- `data/processed/ml_structural_svi_results.csv`
- `data/processed/ml_structural_svi_ndvi_results.csv`
- `data/processed/ml_disciplined_model_comparison.csv`
- `data/processed/ml_disciplined_best_by_family.csv`
- `data/processed/ml_disciplined_best_predictions.csv`
- `data/processed/ml_disciplined_linear_coefficients.csv`
- `data/processed/ml_disciplined_permutation_importance.csv`
- `data/processed/ml_disciplined_ablation_summary.csv`
- `data/processed/ml_consequence_priority_scores.csv`
- `figures/ml_disciplined_model_comparison.png`
- `figures/ml_disciplined_ablation_rmse.png`
- `figures/ml_disciplined_actual_vs_predicted.png`
- `figures/ml_disciplined_residuals.png`
- `figures/ml_disciplined_feature_importance.png`
- `figures/ml_disciplined_priority_layer.png`
- `docs/ML_DISCIPLINED_STUDY.md`
