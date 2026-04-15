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
| Event Damage Hybrid | Ridge | -0.000000 | -0.000000 | -0.000000 | 1.000000 | 0.000000 | 1.000000 | nan | nan |
| HAZUS Benchmark | Ridge | -0.000000 | -0.000000 | -0.000000 | 1.000000 | 0.000000 | 1.000000 | nan | nan |
| Structural + HAZUS Class | Ridge | -0.000000 | -0.000000 | -0.000000 | 1.000000 | 0.000000 | 1.000000 | nan | nan |
| Structural + SVI | Ridge | -0.000000 | -0.000000 | -0.000000 | 1.000000 | 0.000000 | 1.000000 | nan | nan |
| Structural + SVI + HAZUS Class | Ridge | -0.000000 | -0.000000 | -0.000000 | 1.000000 | 0.000000 | 1.000000 | nan | nan |
| Structural Core | Ridge | -0.000000 | -0.000000 | -0.000000 | 1.000000 | 0.000000 | 1.000000 | nan | nan |

## Top Overall Results

| Feature Set | Model | CV_MAE | CV_RMSE | CV_RMSLE | CV_R2 | Holdout_MAE | Holdout_RMSE | Holdout_RMSLE | Holdout_R2 | Holdout_RMSE_Positive | Holdout_R2_Positive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HAZUS Benchmark | Ridge | -0.000000 | -0.000000 | -0.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | nan | nan |
| HAZUS Benchmark | Elastic Net | -0.000000 | -0.000000 | -0.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | nan | nan |
| HAZUS Benchmark | LinearSVR | -0.000000 | -0.000000 | -0.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | nan | nan |
| HAZUS Benchmark | Decision Tree | -0.000000 | -0.000000 | -0.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | nan | nan |
| HAZUS Benchmark | KNN Regressor | -0.000000 | -0.000000 | -0.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | nan | nan |
| HAZUS Benchmark | Random Forest | -0.000000 | -0.000000 | -0.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | nan | nan |
| HAZUS Benchmark | Extra Trees | -0.000000 | -0.000000 | -0.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | nan | nan |
| HAZUS Benchmark | AdaBoost | -0.000000 | -0.000000 | -0.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | nan | nan |
| HAZUS Benchmark | Gradient Boosting | -0.000000 | -0.000000 | -0.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | nan | nan |
| HAZUS Benchmark | HistGradientBoosting | -0.000000 | -0.000000 | -0.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | nan | nan |

## Target-Transform Check

The professor note about training on the log of the model was implemented directly. The table below compares the same recommended no-PGA vulnerability model trained on the raw target versus `log1p(EDR)` and then mapped back with `expm1(...)`.

| Transform | MAE | RMSE | RMSLE | MedianAE | R2 | MAE_Positive | RMSE_Positive | RMSLE_Positive | R2_Positive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Raw target | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | nan | nan | nan | nan |
| log1p -> expm1 target | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 1.000000 | nan | nan | nan | nan |

## Best Overall Benchmark

- Feature set: `HAZUS Benchmark`
- Model: `Ridge`
- Holdout MAE: `0.000000`
- Holdout RMSE: `0.000000`
- Holdout RMSLE: `0.000000`
- Holdout R2: `1.000000`
- Holdout RMSE on positive-damage bridges only: `nan`
- Holdout R2 on positive-damage bridges only: `nan`

## Recommended Final Model For Presentation

- Feature set: `Structural + SVI + HAZUS Class`
- Model: `Ridge`
- Target transform used for the final exported model: `Raw target`
- Holdout MAE: `0.000000`
- Holdout RMSE: `0.000000`
- Holdout RMSLE: `0.000000`
- Holdout R2: `1.000000`
- Holdout RMSE on positive-damage bridges only: `nan`
- Holdout R2 on positive-damage bridges only: `nan`

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
- Vamvatsikos et al. / On the application of machine learning techniques to derive seismic fragility curves (2019): [On the application of machine learning techniques to derive seismic fragility curves](https://www.sciencedirect.com/science/article/pii/S0045794918318650)
- Wang et al. (2022): [Probabilistic seismic analysis of bridges through machine learning approaches](https://www.sciencedirect.com/science/article/pii/S2352012422000972)
- Zhao et al. (2023): [Bridge seismic fragility model based on support vector machine and relevance vector machine](https://www.sciencedirect.com/science/article/pii/S2352012423004666)
- Luo et al. (2025): [Post-earthquake functionality and resilience prediction of bridge networks based on data-driven machine learning method](https://www.sciencedirect.com/science/article/abs/pii/S0267726124006791)
- scikit-learn docs: [TransformedTargetRegressor](https://scikit-learn.org/1.5/modules/generated/sklearn.compose.TransformedTargetRegressor.html)
- scikit-learn docs: [LinearSVR](https://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVR.html)
- scikit-learn docs: [HistGradientBoostingRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html)
- scikit-learn docs: [MLPRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPRegressor.html)
