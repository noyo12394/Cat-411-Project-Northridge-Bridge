# ML Hybrid Analysis

This refreshed analysis rebuilds the machine-learning pipeline on the full California bridge inventory rather than only the ShakeMap-affected subset. The target remains HAZUS-derived Expected Damage Ratio (`EDR`), but bridges outside the PGA footprint are kept in the statewide training set with `pga = 0` and `EDR = 0` so the final model can score every bridge in the inventory.

## What Changed

- The training set now covers the full California inventory (`25,975` bridges).
- Bridges with positive PGA / positive fragility demand: `16,796`.
- The upstream engineering tables now use the revised April 2026 SVI methodology, including updated parameter weights, continuous component scores, and SVI-driven fragility medians / dispersion.
- The professor-requested log-target workflow was tested directly, and the final recommended transform is chosen from the raw-vs-log comparison rather than assumed in advance.
- A new `design_era_1989` categorical feature was added to reflect the professor note about a HAZUS-style design-era split.
- The model comparison now separates pure bridge vulnerability models from event-damage models that also include hazard demand.
- Additional validation outputs were added: log-scale fit plots, decile calibration plots, feature-importance charts, and a mutual-information screen.

## Why These Models

- The comparison now spans 10 models: regularized linear baselines, a max-margin baseline, a distance-based baseline, a single-tree baseline, bagging / forest models, boosting models, and a neural-network baseline.
- Tree ensembles remain the strongest default choice for structured tabular engineering data in both the tabular-ML literature and bridge-seismic applications.
- `LinearSVR` is included because support-vector approaches appear repeatedly in bridge fragility studies and provide a useful non-tree nonlinear benchmark.
- `Random Forest`, `Extra Trees`, `Gradient Boosting`, `HistGradientBoosting`, and `AdaBoost` provide a broad ensemble comparison rather than relying on only one nonlinear family.
- `Ridge` and `Elastic Net` remain as transparent linear baselines, while `MLPRegressor` gives a neural-network comparison without leaving the project runtime.

## Engineering Variable Screen

| Feature | Role | Reason |
| --- | --- | --- |
| pga | Hazard demand | Peak ground acceleration at the bridge site; direct shaking demand. |
| HWB_CLASS | HAZUS classification | Bridge fragility family assigned from structure type and era logic. |
| SVI | Composite vulnerability | Seismic Vulnerability Index from the revised April 2026 weighted methodology. |
| design_era_1989 | Design era | Categorical design-era feature that separates older bridges from post-1989 design practice. |
| age_years | Age | Bridge age in years relative to 2025. |
| time_since_rehab | Rehabilitation timing | Years since the last recorded reconstruction; falls back to bridge age if never reconstructed. |
| reconstructed_flag | Rehabilitation indicator | Binary flag indicating whether a bridge has a recorded reconstruction year. |
| spans | Geometry | Number of main unit spans. |
| max_span_log1p | Geometry | Log-transformed maximum span length to tame the extreme right tail. |
| skew | Geometry | Skew angle in degrees. |
| cond | Condition | Primary condition proxy from NBI Item 60 / substructure condition when available. |
| deck_area_log1p | Scale | Log-transformed deck area as a size / exposure proxy. |
| operating_rating | Capacity / condition | Operating rating from the inventory. |

## Feature-Set Comparison

- `HAZUS Benchmark`: Minimal hazard-only benchmark using PGA and HAZUS bridge class.
- `Structural Core`: Pure no-PGA intrinsic screening using age, rehabilitation, geometry, condition, scale, and rating variables only.
- `Structural + SVI`: Intrinsic structural screening plus the continuous SVI summary, still with no PGA.
- `Structural + HAZUS Class`: Intrinsic structural screening plus HAZUS bridge family, still with no PGA.
- `Structural + SVI + HAZUS Class`: Full intrinsic vulnerability model using structural variables, SVI, and HAZUS class while keeping PGA out.
- `Event Damage Hybrid`: Event-damage model that combines shaking demand with the bridge-intrinsic structural variables.

## Best Model By Feature Set

| Feature Set | Model | CV_MAE | CV_RMSE | CV_RMSLE | CV_R2 | Holdout_RMSE | Holdout_R2 | Holdout_RMSE_Positive | Holdout_R2_Positive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Event Damage Hybrid | MLPRegressor | 0.000205 | 0.000625 | 0.000533 | 0.999772 | 0.000571 | 0.999834 | 0.000703 | 0.999832 |
| HAZUS Benchmark | Gradient Boosting | 0.000807 | 0.004213 | 0.003387 | 0.989992 | 0.004315 | 0.990523 | 0.005341 | 0.990306 |
| Structural + HAZUS Class | Extra Trees | 0.012108 | 0.038232 | 0.033596 | 0.175733 | 0.039341 | 0.212044 | 0.047676 | 0.227622 |
| Structural + SVI | Extra Trees | 0.012475 | 0.038490 | 0.033805 | 0.164816 | 0.039623 | 0.200714 | 0.048262 | 0.208539 |
| Structural + SVI + HAZUS Class | Extra Trees | 0.012255 | 0.038512 | 0.033862 | 0.163664 | 0.039797 | 0.193692 | 0.048204 | 0.210410 |
| Structural Core | Extra Trees | 0.012409 | 0.038518 | 0.033820 | 0.163660 | 0.039286 | 0.214257 | 0.047678 | 0.227569 |

## Top Overall Results

| Feature Set | Model | CV_MAE | CV_RMSE | CV_RMSLE | CV_R2 | Holdout_MAE | Holdout_RMSE | Holdout_RMSLE | Holdout_R2 | Holdout_RMSE_Positive | Holdout_R2_Positive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Event Damage Hybrid | MLPRegressor | 0.000205 | 0.000625 | 0.000533 | 0.999772 | 0.000184 | 0.000571 | 0.000494 | 0.999834 | 0.000703 | 0.999832 |
| Event Damage Hybrid | Gradient Boosting | 0.000215 | 0.000956 | 0.000796 | 0.999470 | 0.000202 | 0.000866 | 0.000709 | 0.999619 | 0.001069 | 0.999612 |
| Event Damage Hybrid | Decision Tree | 0.000364 | 0.002211 | 0.001771 | 0.997239 | 0.000318 | 0.001887 | 0.001514 | 0.998187 | 0.002336 | 0.998146 |
| Event Damage Hybrid | HistGradientBoosting | 0.000479 | 0.002412 | 0.001942 | 0.996709 | 0.000518 | 0.002516 | 0.002018 | 0.996778 | 0.003113 | 0.996706 |
| HAZUS Benchmark | Gradient Boosting | 0.000807 | 0.004213 | 0.003387 | 0.989992 | 0.000848 | 0.004315 | 0.003449 | 0.990523 | 0.005341 | 0.990306 |
| HAZUS Benchmark | Random Forest | 0.000784 | 0.004379 | 0.003524 | 0.989190 | 0.000790 | 0.004195 | 0.003401 | 0.991039 | 0.005194 | 0.990834 |
| HAZUS Benchmark | MLPRegressor | 0.001167 | 0.004391 | 0.003597 | 0.989079 | 0.001103 | 0.004427 | 0.003601 | 0.990022 | 0.005477 | 0.989808 |
| HAZUS Benchmark | KNN Regressor | 0.000758 | 0.004403 | 0.003546 | 0.989086 | 0.000765 | 0.004498 | 0.003632 | 0.989702 | 0.005568 | 0.989467 |
| Event Damage Hybrid | AdaBoost | 0.001430 | 0.004549 | 0.003889 | 0.988272 | 0.001500 | 0.004725 | 0.004036 | 0.988636 | 0.005841 | 0.988407 |
| HAZUS Benchmark | HistGradientBoosting | 0.000861 | 0.004583 | 0.003691 | 0.988157 | 0.000940 | 0.004847 | 0.003887 | 0.988040 | 0.006000 | 0.987768 |

## Target-Transform Check

The professor note about training on the log of the model was implemented directly. The table below compares the same recommended no-PGA vulnerability model trained on the raw target versus `log1p(EDR)` and then mapped back with `expm1(...)`.

| Transform | MAE | RMSE | RMSLE | MedianAE | R2 | MAE_Positive | RMSE_Positive | RMSLE_Positive | R2_Positive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Raw target | 0.012929 | 0.039761 | 0.034852 | 0.002611 | 0.195126 | 0.016676 | 0.048015 | 0.041877 | 0.216613 |
| log1p -> expm1 target | 0.012523 | 0.039797 | 0.034843 | 0.002430 | 0.193692 | 0.016270 | 0.048204 | 0.042015 | 0.210410 |

## Best Overall Benchmark

- Feature set: `Event Damage Hybrid`
- Model: `MLPRegressor`
- Holdout MAE: `0.000184`
- Holdout RMSE: `0.000571`
- Holdout RMSLE: `0.000494`
- Holdout R2: `0.999834`
- Holdout RMSE on positive-damage bridges only: `0.000703`
- Holdout R2 on positive-damage bridges only: `0.999832`

## Recommended Final Model For Presentation

- Feature set: `Structural + HAZUS Class`
- Model: `Extra Trees`
- Target transform used for the final exported model: `Raw target`
- Holdout MAE: `0.012350`
- Holdout RMSE: `0.039341`
- Holdout RMSLE: `0.034440`
- Holdout R2: `0.212044`
- Holdout RMSE on positive-damage bridges only: `0.047676`
- Holdout R2 on positive-damage bridges only: `0.227622`

This is the recommended presentation model because it is the strongest cross-validated no-PGA bridge-intrinsic vulnerability model in the statewide study. It removes PGA and traffic/network consequence variables while retaining a meaningful structural-system descriptor through `HWB_CLASS`. The SVI-inclusive model remains valuable for interpretability, but it is not the strongest RMSE winner.

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
- Vamvatsikos et al. / On the application of machine learning techniques to derive seismic fragility curves (2019): [On the application of machine learning techniques to derive seismic fragility curves](https://www.sciencedirect.com/science/article/pii/S0045794918318650)
- Wang et al. (2022): [Probabilistic seismic analysis of bridges through machine learning approaches](https://www.sciencedirect.com/science/article/pii/S2352012422000972)
- Zhao et al. (2023): [Bridge seismic fragility model based on support vector machine and relevance vector machine](https://www.sciencedirect.com/science/article/pii/S2352012423004666)
- Luo et al. (2025): [Post-earthquake functionality and resilience prediction of bridge networks based on data-driven machine learning method](https://www.sciencedirect.com/science/article/abs/pii/S0267726124006791)
- scikit-learn docs: [TransformedTargetRegressor](https://scikit-learn.org/1.5/modules/generated/sklearn.compose.TransformedTargetRegressor.html)
- scikit-learn docs: [LinearSVR](https://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVR.html)
- scikit-learn docs: [HistGradientBoostingRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html)
- scikit-learn docs: [MLPRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPRegressor.html)
