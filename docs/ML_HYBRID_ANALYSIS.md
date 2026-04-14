# ML Hybrid Analysis

This refreshed analysis rebuilds the machine-learning pipeline on the full California bridge inventory rather than only the ShakeMap-affected subset. The target remains HAZUS-derived Expected Damage Ratio (`EDR`), but bridges outside the PGA footprint are kept in the statewide training set with `pga = 0` and `EDR = 0` so the final model can score every bridge in the inventory.

## What Changed

- The training set now covers the full California inventory (`25,975` bridges).
- Bridges with positive PGA / positive fragility demand: `16,796`.
- The professor-requested log-target workflow was tested directly, and the final recommended transform is chosen from the raw-vs-log comparison rather than assumed in advance.
- A new `design_era_1989` categorical feature was added to reflect the professor note about a HAZUS-style design-era split.
- The model comparison now separates pure bridge vulnerability models from event-damage models that also include hazard demand.
- Additional validation outputs were added: log-scale fit plots, decile calibration plots, feature-importance charts, and a mutual-information screen.

## Why These Models

- Tree ensembles remain the strongest default choice for structured tabular engineering data in both the tabular-ML literature and bridge-seismic applications.
- `HistGradientBoosting` and `Extra Trees` cover two strong nonlinear ensemble families available in the project runtime.
- `Random Forest` is kept because bridge-seismic studies often report it as a robust baseline.
- `MLPRegressor` is included as a nonlinear neural-network baseline, but only after the tabular tree baselines.
- `Elastic Net` remains as the transparent linear baseline.

## Engineering Variable Screen

| Feature | Role | Reason |
| --- | --- | --- |
| pga | Hazard demand | Peak ground acceleration at the bridge site; direct shaking demand. |
| HWB_CLASS | HAZUS classification | Bridge fragility family assigned from structure type and era logic. |
| SVI | Composite vulnerability | Seismic Vulnerability Index carried over from the engineering scoring workflow. |
| design_era_1989 | Design era | Categorical design-era feature that separates older bridges from post-1989 design practice. |
| age_years | Age | Bridge age in years relative to 2025. |
| time_since_rehab | Rehabilitation timing | Years since the last recorded reconstruction; falls back to bridge age if never reconstructed. |
| reconstructed_flag | Rehabilitation indicator | Binary flag indicating whether a bridge has a recorded reconstruction year. |
| spans | Geometry | Number of main unit spans. |
| max_span_log1p | Geometry | Log-transformed maximum span length to tame the extreme right tail. |
| skew | Geometry | Skew angle in degrees. |
| cond | Condition | Lowest available bridge condition rating proxy. |
| deck_area_log1p | Scale | Log-transformed deck area as a size / exposure proxy. |
| operating_rating | Capacity / condition | Operating rating from the inventory. |

## Feature-Set Comparison

- `HAZUS Benchmark`: Minimal hazard-only benchmark using PGA and HAZUS bridge class.
- `Bridge Vulnerability Compact`: Compact no-PGA vulnerability framing using SVI and the core age / geometry / condition variables.
- `Bridge Vulnerability Structural`: Pure bridge-intrinsic structural vulnerability model with no PGA and no traffic / network consequence variables.
- `Event Damage Hybrid`: Event-damage model that combines shaking demand with the bridge-intrinsic structural variables.

## Best Model By Feature Set

| Feature Set | Model | CV_MAE | CV_RMSE | CV_RMSLE | CV_R2 | Holdout_RMSE | Holdout_R2 | Holdout_RMSE_Positive | Holdout_R2_Positive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HAZUS Benchmark | MLPRegressor | 0.000226 | 0.000726 | 0.000671 | 0.999755 | 0.000443 | 0.999905 | 0.000545 | 0.999904 |
| Event Damage Hybrid | MLPRegressor | 0.000712 | 0.001514 | 0.001334 | 0.998916 | 0.001438 | 0.998994 | 0.001721 | 0.999044 |
| Bridge Vulnerability Structural | Extra Trees | 0.014493 | 0.042959 | 0.037391 | 0.164772 | 0.041457 | 0.164107 | 0.050829 | 0.166245 |
| Bridge Vulnerability Compact | Random Forest | 0.015600 | 0.044166 | 0.038448 | 0.116852 | 0.042453 | 0.123477 | 0.051900 | 0.130733 |

## Top Overall Results

| Feature Set | Model | CV_MAE | CV_RMSE | CV_RMSLE | CV_R2 | Holdout_MAE | Holdout_RMSE | Holdout_RMSLE | Holdout_R2 | Holdout_RMSE_Positive | Holdout_R2_Positive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HAZUS Benchmark | MLPRegressor | 0.000226 | 0.000726 | 0.000671 | 0.999755 | 0.000183 | 0.000443 | 0.000401 | 0.999905 | 0.000545 | 0.999904 |
| HAZUS Benchmark | Extra Trees | 0.000026 | 0.000939 | 0.000743 | 0.999449 | 0.000008 | 0.000106 | 0.000079 | 0.999994 | 0.000132 | 0.999994 |
| Event Damage Hybrid | MLPRegressor | 0.000712 | 0.001514 | 0.001334 | 0.998916 | 0.000716 | 0.001438 | 0.001282 | 0.998994 | 0.001721 | 0.999044 |
| HAZUS Benchmark | Random Forest | 0.000261 | 0.001904 | 0.001474 | 0.998325 | 0.000236 | 0.001655 | 0.001316 | 0.998668 | 0.002058 | 0.998633 |
| HAZUS Benchmark | HistGradientBoosting | 0.000597 | 0.003503 | 0.002711 | 0.994433 | 0.000558 | 0.002978 | 0.002321 | 0.995685 | 0.003704 | 0.995573 |
| Event Damage Hybrid | HistGradientBoosting | 0.000661 | 0.004099 | 0.003186 | 0.992382 | 0.000488 | 0.002708 | 0.002154 | 0.996433 | 0.003368 | 0.996340 |
| Event Damage Hybrid | Extra Trees | 0.002077 | 0.008748 | 0.006867 | 0.965331 | 0.001882 | 0.008336 | 0.006505 | 0.966206 | 0.010348 | 0.965442 |
| Event Damage Hybrid | Random Forest | 0.003090 | 0.011509 | 0.009024 | 0.940051 | 0.002733 | 0.010639 | 0.008307 | 0.944948 | 0.013163 | 0.944088 |
| Event Damage Hybrid | Elastic Net | 0.006583 | 0.016284 | 0.013884 | 0.879968 | 0.006343 | 0.015959 | 0.013591 | 0.876128 | 0.019843 | 0.872933 |
| HAZUS Benchmark | Elastic Net | 0.006877 | 0.016846 | 0.014399 | 0.871530 | 0.006622 | 0.016529 | 0.014105 | 0.867128 | 0.020556 | 0.863644 |

## Target-Transform Check

The professor note about training on the log of the model was implemented directly. The table below compares the same recommended no-PGA vulnerability model trained on the raw target versus `log1p(EDR)` and then mapped back with `expm1(...)`.

| Transform | MAE | RMSE | RMSLE | MedianAE | R2 | MAE_Positive | RMSE_Positive | RMSLE_Positive | R2_Positive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Raw target | 0.013941 | 0.041542 | 0.036109 | 0.003266 | 0.160687 | 0.018168 | 0.050792 | 0.043949 | 0.167465 |
| log1p -> expm1 target | 0.013475 | 0.041457 | 0.035974 | 0.003054 | 0.164107 | 0.017717 | 0.050829 | 0.043934 | 0.166245 |

## Best Overall Benchmark

- Feature set: `HAZUS Benchmark`
- Model: `MLPRegressor`
- Holdout MAE: `0.000183`
- Holdout RMSE: `0.000443`
- Holdout RMSLE: `0.000401`
- Holdout R2: `0.999905`
- Holdout RMSE on positive-damage bridges only: `0.000545`
- Holdout R2 on positive-damage bridges only: `0.999904`

## Recommended Final Model For Presentation

- Feature set: `Bridge Vulnerability Structural`
- Model: `Extra Trees`
- Target transform used for the final exported model: `log1p -> expm1 target`
- Holdout MAE: `0.013475`
- Holdout RMSE: `0.041457`
- Holdout RMSLE: `0.035974`
- Holdout R2: `0.164107`
- Holdout RMSE on positive-damage bridges only: `0.050829`
- Holdout R2 on positive-damage bridges only: `0.166245`

This is the recommended presentation model because it is a pure bridge-intrinsic vulnerability model: it removes PGA and traffic/network consequence variables and keeps only structural class, age / rehabilitation, geometry, condition, and rating information.

## Important Interpretation Note

- Because the statewide inventory contains many bridges with zero or near-zero damage, overall metrics improve compared with the affected-only subset.
- For that reason, the positive-damage holdout metrics are also reported above so the model is not judged only on easy zero-damage cases.
- The target is still HAZUS-derived `EDR`, so the no-PGA vulnerability model is best interpreted as a bridge-intrinsic surrogate for relative vulnerability, not as a full physics-based damage predictor.
- The `Event Damage Hybrid` rows should be used when the question is event-specific damage prediction, because that framing intentionally includes PGA.

## Generated Artifacts

- `data/processed/ml_statewide_training_dataset.csv`
- `data/processed/ml_hybrid_comparison.csv`
- `data/processed/ml_hybrid_best_by_feature_set.csv`
- `data/processed/ml_hybrid_predictions.csv`
- `data/processed/ml_hybrid_feature_importance.csv`
- `data/processed/ml_recommended_hybrid_metrics.csv`
- `data/processed/ml_recommended_hybrid_predictions.csv`
- `data/processed/ml_recommended_hybrid_feature_importance.csv`
- `data/processed/ml_statewide_bridge_scores.csv`
- `data/processed/ml_feature_screen_mutual_info.csv`
- `data/processed/ml_target_transform_comparison.csv`
- `figures/ml_hybrid_rmse_heatmap.png`
- `figures/ml_hybrid_r2_heatmap.png`
- `figures/ml_hybrid_rmsle_heatmap.png`
- `figures/ml_hybrid_actual_vs_predicted.png`
- `figures/ml_hybrid_log_actual_vs_predicted.png`
- `figures/ml_hybrid_residuals.png`
- `figures/ml_hybrid_decile_calibration.png`
- `figures/ml_hybrid_feature_importance.png`
- `figures/ml_recommended_hybrid_actual_vs_predicted.png`
- `figures/ml_recommended_hybrid_log_actual_vs_predicted.png`
- `figures/ml_recommended_hybrid_feature_importance.png`
- `figures/ml_recommended_hybrid_decile_calibration.png`
- `figures/ml_recommended_hybrid_mutual_information.png`

## Literature Notes

- Shwartz-Ziv and Armon (2022): [Tabular data: Deep learning is not all you need](https://www.sciencedirect.com/science/article/pii/S1566253521002360)
- Gorishniy et al. (2021): [Revisiting Deep Learning Models for Tabular Data](https://research.yandex.com/publications/revisiting-deep-learning-models-for-tabular-data)
- Mangalathu et al. (2019): [Rapid seismic damage evaluation of bridge portfolios using machine learning techniques](https://www.sciencedirect.com/science/article/pii/S0141029619328068)
- Luo et al. (2025): [Post-earthquake functionality and resilience prediction of bridge networks based on data-driven machine learning method](https://www.sciencedirect.com/science/article/abs/pii/S0267726124006791)
- scikit-learn docs: [TransformedTargetRegressor](https://scikit-learn.org/1.5/modules/generated/sklearn.compose.TransformedTargetRegressor.html)
- scikit-learn docs: [HistGradientBoostingRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html)
- scikit-learn docs: [MLPRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPRegressor.html)
