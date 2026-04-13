# ML Hybrid Analysis

This refreshed analysis rebuilds the machine-learning pipeline on the full California bridge inventory rather than only the ShakeMap-affected subset. The target remains HAZUS-derived Expected Damage Ratio (`EDR`), but bridges outside the PGA footprint are kept in the statewide training set with `pga = 0` and `EDR = 0` so the final model can score every bridge in the inventory.

## What Changed

- The training set now covers the full California inventory (`25,975` bridges).
- Bridges with positive PGA / positive fragility demand: `16,796`.
- The professor-requested log-target workflow was tested directly, and the final recommended transform is chosen from the raw-vs-log comparison rather than assumed in advance.
- A new `design_era_1989` categorical feature was added to reflect the professor note about a HAZUS-style design-era split.
- The model comparison now tests generic statewide bridge features, HAZUS variables, and a combined statewide hybrid model.
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
| adt_log1p | Traffic importance | Log-transformed average daily traffic. |
| truck_pct | Traffic importance | Truck share of ADT. |
| detour_km_log1p | Network disruption | Log-transformed detour length in kilometers. |
| lanes_on | Capacity | Traffic lanes carried by the bridge. |
| operating_rating | Capacity / condition | Operating rating from the inventory. |
| functional_class_cat | Network role | Functional class category from the bridge inventory. |
| kind | Structural system | Structure kind code from the NBI inventory. |
| type | Structural system | Structure type code from the NBI inventory. |

## Feature-Set Comparison

- `HAZUS Benchmark`: Minimal hazard-only benchmark using PGA and HAZUS bridge class.
- `Intrinsic Vulnerability`: Bridge age, geometry, condition, and SVI without direct hazard demand.
- `Statewide Bridge`: Generic statewide bridge descriptors that remain meaningful across California.
- `Statewide HAZUS + Bridge`: Hazard, HAZUS class, and statewide bridge descriptors combined into the final presentation model.

## Best Model By Feature Set

| Feature Set | Model | CV_MAE | CV_RMSE | CV_RMSLE | CV_R2 | Holdout_RMSE | Holdout_R2 | Holdout_RMSE_Positive | Holdout_R2_Positive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HAZUS Benchmark | MLPRegressor | 0.000226 | 0.000726 | 0.000671 | 0.999755 | 0.000443 | 0.999905 | 0.000545 | 0.999904 |
| Statewide HAZUS + Bridge | MLPRegressor | 0.000665 | 0.001476 | 0.001263 | 0.998993 | 0.001217 | 0.999280 | 0.001503 | 0.999271 |
| Statewide Bridge | Extra Trees | 0.012796 | 0.039416 | 0.034096 | 0.297143 | 0.038945 | 0.262355 | 0.048011 | 0.256139 |
| Intrinsic Vulnerability | Random Forest | 0.015209 | 0.043409 | 0.037694 | 0.147169 | 0.042214 | 0.133301 | 0.051780 | 0.134738 |

## Top Overall Results

| Feature Set | Model | CV_MAE | CV_RMSE | CV_RMSLE | CV_R2 | Holdout_MAE | Holdout_RMSE | Holdout_RMSLE | Holdout_R2 | Holdout_RMSE_Positive | Holdout_R2_Positive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HAZUS Benchmark | MLPRegressor | 0.000226 | 0.000726 | 0.000671 | 0.999755 | 0.000183 | 0.000443 | 0.000401 | 0.999905 | 0.000545 | 0.999904 |
| HAZUS Benchmark | Extra Trees | 0.000026 | 0.000939 | 0.000743 | 0.999449 | 0.000008 | 0.000106 | 0.000079 | 0.999994 | 0.000132 | 0.999994 |
| Statewide HAZUS + Bridge | MLPRegressor | 0.000665 | 0.001476 | 0.001263 | 0.998993 | 0.000468 | 0.001217 | 0.001019 | 0.999280 | 0.001503 | 0.999271 |
| HAZUS Benchmark | Random Forest | 0.000261 | 0.001904 | 0.001474 | 0.998325 | 0.000236 | 0.001655 | 0.001316 | 0.998668 | 0.002058 | 0.998633 |
| HAZUS Benchmark | HistGradientBoosting | 0.000597 | 0.003503 | 0.002711 | 0.994433 | 0.000558 | 0.002978 | 0.002321 | 0.995685 | 0.003704 | 0.995573 |
| Statewide HAZUS + Bridge | HistGradientBoosting | 0.000670 | 0.003684 | 0.002878 | 0.993857 | 0.000539 | 0.002626 | 0.002095 | 0.996645 | 0.003266 | 0.996558 |
| Statewide HAZUS + Bridge | Elastic Net | 0.006397 | 0.015798 | 0.013448 | 0.887019 | 0.006160 | 0.015380 | 0.013093 | 0.884958 | 0.019121 | 0.882007 |
| Statewide HAZUS + Bridge | Extra Trees | 0.004560 | 0.016362 | 0.013254 | 0.878897 | 0.004217 | 0.016113 | 0.013020 | 0.873731 | 0.019964 | 0.871385 |
| HAZUS Benchmark | Elastic Net | 0.006877 | 0.016846 | 0.014399 | 0.871530 | 0.006622 | 0.016529 | 0.014105 | 0.867128 | 0.020556 | 0.863644 |
| Statewide HAZUS + Bridge | Random Forest | 0.005357 | 0.018008 | 0.014427 | 0.853247 | 0.005097 | 0.017690 | 0.014144 | 0.847799 | 0.021870 | 0.845651 |

## Target-Transform Check

The professor note about training on the log of the model was implemented directly. The table below compares the same recommended model trained on the raw target versus `log1p(EDR)` and then mapped back with `expm1(...)`.

| Transform | MAE | RMSE | RMSLE | MedianAE | R2 | MAE_Positive | RMSE_Positive | RMSLE_Positive | R2_Positive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Raw target | 0.000352 | 0.001056 | 0.000914 | 0.000068 | 0.999458 | 0.000497 | 0.001246 | 0.001061 | 0.999499 |
| log1p -> expm1 target | 0.000468 | 0.001217 | 0.001019 | 0.000164 | 0.999280 | 0.000667 | 0.001503 | 0.001254 | 0.999271 |

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

- Feature set: `Statewide HAZUS + Bridge`
- Model: `MLPRegressor`
- Target transform used for the final exported model: `Raw target`
- Holdout MAE: `0.000352`
- Holdout RMSE: `0.001056`
- Holdout RMSLE: `0.000914`
- Holdout R2: `0.999458`
- Holdout RMSE on positive-damage bridges only: `0.001246`
- Holdout R2 on positive-damage bridges only: `0.999499`

This is the recommended presentation model because it is the most generic statewide framing while still using variables that make engineering sense: hazard demand, HAZUS class, design era, bridge geometry, traffic importance, and continuous vulnerability context.

## Important Interpretation Note

- Because the statewide inventory contains many bridges with zero or near-zero damage, overall metrics improve compared with the affected-only subset.
- For that reason, the positive-damage holdout metrics are also reported above so the model is not judged only on easy zero-damage cases.
- The target is still HAZUS-derived `EDR`, so this is a statewide surrogate / reconstruction model rather than external field-damage validation.

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
