# ML Hybrid Analysis

This analysis compares structured-data models for predicting Expected Damage Ratio (EDR) from three views of the bridge dataset:

- `SVI-only`: intrinsic bridge attributes plus the Seismic Vulnerability Index
- `HAZUS-only`: hazard intensity (`pga`) plus HAZUS bridge class
- `Hybrid HAZUS+SVI`: hazard, HAZUS class, and interpretable bridge-vulnerability variables together

## Why These Models

- Tree ensembles are strong baselines for structured tabular data and are widely recommended in the literature for problems of this type.
- `HistGradientBoosting` was included as a modern boosting-tree baseline available directly in scikit-learn.
- A stacked ensemble was included to test whether blending complementary model families improved on single learners.
- `Elastic Net` was kept as a transparent linear baseline to show how much nonlinear structure exists in the dataset.

## Engineering Variable Screen

Only variables with a clear engineering or vulnerability interpretation were retained in the final hybrid model:

| Variable | Why It Was Kept |
| --- | --- |
| `pga` | Event-level seismic demand at the bridge site |
| `HWB_CLASS` | HAZUS bridge fragility family / engineering class |
| `SVI` | Continuous bridge vulnerability score |
| `year` | Design era / age proxy |
| `yr_recon` | Rehabilitation or retrofit history proxy |
| `spans` | Bridge system configuration |
| `max_span` | Structural scale / flexibility proxy |
| `skew` | Geometry feature relevant to seismic response |
| `cond` | Existing condition / deterioration proxy |

The full machine-readable manifest is saved in `data/processed/ml_feature_manifest.csv`.

## Cross-Validated Results

| Feature Set | Best Model | MAE | RMSE | R2 |
| --- | --- | --- | --- | --- |
| `HAZUS-only` | `Extra Trees` | `0.000081` | `0.001672` | `0.999079` |
| `Hybrid HAZUS+SVI` | `Extra Trees` | `0.000131` | `0.001808` | `0.998942` |
| `SVI-only` | `Random Forest` | `0.023365` | `0.053329` | `0.143398` |

Full model-by-model comparison is saved in:

- `data/processed/ml_hybrid_comparison.csv`
- `data/processed/ml_hybrid_best_by_feature_set.csv`

## Best Overall Benchmark

- Feature set: `HAZUS-only`
- Model: `Extra Trees`
- Interpretation: this is the strongest benchmark, but it should be treated as an upper bound because `EDR` is generated from hazard intensity and HAZUS fragility logic.

## Recommended Final Model For Presentation

- Feature set: `Hybrid HAZUS+SVI`
- Model: `Extra Trees`
- Holdout MAE: `0.000122`
- Holdout RMSE: `0.002953`
- Holdout R2: `0.997338`

This is the recommended final model for the report and dashboard framing because it:

- uses only interpretable hazard, class, geometry, age, and condition variables
- remains extremely accurate while being more defensible than the pure `HAZUS-only` benchmark
- supports the project story that vulnerability should be modeled as hazard plus bridge-specific characteristics, not hazard alone

## Recommended Hybrid Artifacts

- `data/processed/ml_recommended_hybrid_metrics.csv`
- `data/processed/ml_recommended_hybrid_predictions.csv`
- `data/processed/ml_recommended_hybrid_feature_importance.csv`

The benchmark artifacts remain available as:

- `data/processed/ml_hybrid_predictions.csv`
- `data/processed/ml_hybrid_feature_importance.csv`

## Interpretation

- `HAZUS-only` performs best because the target `EDR` is tightly tied to `pga` and `HWB_CLASS` by construction.
- `SVI-only` still contains real vulnerability signal, but it is not expected to fully reconstruct a hazard-driven target on its own.
- `Hybrid HAZUS+SVI` is the most useful final framing for a dashboard or decision-support system because it combines seismic demand, engineering class, and continuous vulnerability context.
- The practical takeaway is: use `HAZUS-only` as the benchmark ceiling, and present `Hybrid HAZUS+SVI` as the final model that makes the most engineering sense.

## Literature Notes

- Shwartz-Ziv and Armon (2022): [Tabular data: Deep learning is not all you need](https://www.sciencedirect.com/science/article/pii/S1566253521002360)
- Gorishniy et al. (NeurIPS 2021): [Revisiting Deep Learning Models for Tabular Data](https://research.yandex.com/publications/revisiting-deep-learning-models-for-tabular-data)
- scikit-learn documentation: [HistGradientBoostingRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html)
- scikit-learn documentation: [StackingRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.StackingRegressor.html)
- Chen and Guestrin (KDD 2016): [XGBoost: A Scalable Tree Boosting System](https://arxiv.org/pdf/1603.02754)
