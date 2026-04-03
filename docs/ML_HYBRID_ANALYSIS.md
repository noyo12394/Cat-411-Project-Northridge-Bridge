# ML Hybrid Analysis

This document summarizes an expanded machine-learning comparison for the bridge project using three views of the same bridge dataset:
- `SVI-only`
- `HAZUS-only`
- `Hybrid HAZUS+SVI`

The goal was not just to fit one more model, but to compare what each information layer contributes:
- can intrinsic bridge vulnerability traits alone reconstruct damage behavior?
- does HAZUS-style hazard plus bridge class dominate the signal?
- does a hybrid model offer the most useful dashboard framing even if it is not the lowest-error reconstruction?

## Why These Models

The model family choices were guided by tabular-ML literature and by what is robust within the current repository stack:
- tree ensembles are consistently strong baselines for structured tabular data
- gradient-boosting trees remain a standard high-performing choice for tabular prediction
- stacked ensembles are useful when combining models that capture different error patterns

Selected model families:
- Elastic Net
- Random Forest
- Extra Trees
- HistGradientBoosting
- Stacked Hybrid Ensemble

## Best Model By Feature Set

| Feature Set | Model | MAE | RMSE | R2 | MAE_std | RMSE_std | R2_std |
| --- | --- | --- | --- | --- | --- | --- | --- |
| HAZUS-only | Extra Trees | 0.000081 | 0.001672 | 0.999079 | 0.000011 | 0.000469 | 0.000523 |
| Hybrid HAZUS+SVI | Extra Trees | 0.000131 | 0.001808 | 0.998942 | 0.000018 | 0.000463 | 0.000516 |
| SVI-only | Random Forest | 0.023365 | 0.053329 | 0.143398 | 0.000509 | 0.001429 | 0.019680 |

## Best Overall Result

- Best overall feature set: `HAZUS-only`
- Best overall model: `Extra Trees`
- Cross-validated MAE: `0.000081`
- Cross-validated RMSE: `0.001672`
- Cross-validated R2: `0.999079`

## Interpretation

### 1. HAZUS-only dominates pure EDR reconstruction
The strongest results come from the `HAZUS-only` feature set, with `Extra Trees` performing best. This is expected because `EDR` is generated from HAZUS-style fragility logic and therefore is closely tied to `PGA` and `HWB_CLASS`.

### 2. SVI-only still captures meaningful signal
The `SVI-only` feature set does not compete with HAZUS-driven reconstruction accuracy, but it still carries predictive value. The best `SVI-only` result comes from `Random Forest`, which suggests non-linear interactions among structural condition, age, span geometry, skew, and SVI are real and useful.

### 3. Hybrid HAZUS+SVI is the most dashboard-relevant framing
The hybrid feature set performs extremely well and remains close to the best HAZUS-only reconstruction. Even when it does not beat the HAZUS-only minimum error, it is the most decision-useful framing because it combines:
- event severity (`PGA`)
- bridge design class (`HWB_CLASS`)
- continuous vulnerability context (`SVI`)
- structural / condition variables that are easier to explain in a dashboard

### 4. Feature importance remains hazard-first
Permutation importance for the best overall model shows that `pga` is the dominant predictor and `HWB_CLASS` is the second most important feature. That reinforces the engineering logic already present in the project.

## Generated Files

Processed tables:
- `data/processed/ml_hybrid_comparison.csv`
- `data/processed/ml_hybrid_best_by_feature_set.csv`
- `data/processed/ml_hybrid_predictions.csv`
- `data/processed/ml_hybrid_feature_importance.csv`

Figures:
- `figures/ml_hybrid_rmse_heatmap.png`
- `figures/ml_hybrid_r2_heatmap.png`
- `figures/ml_hybrid_actual_vs_predicted.png`
- `figures/ml_hybrid_residuals.png`
- `figures/ml_hybrid_feature_importance.png`

## Suggested Project Framing

For a methodological comparison section, the cleanest takeaway is:
- `HAZUS-only` is best for reconstructing HAZUS-derived `EDR`
- `SVI-only` shows that intrinsic bridge vulnerability still carries meaningful predictive information
- `Hybrid HAZUS+SVI` is the most suitable model family for an interpretable dashboard because it combines engineering hazard, bridge classification, and continuous vulnerability in one pipeline

## Literature Notes

- Shwartz-Ziv, R. and Armon, A. (2022): [Tabular data: Deep learning is not all you need](https://www.sciencedirect.com/science/article/pii/S1566253521002360)
- Gorishniy et al. (NeurIPS 2021): [Revisiting Deep Learning Models for Tabular Data](https://research.yandex.com/publications/revisiting-deep-learning-models-for-tabular-data)
- scikit-learn documentation: [HistGradientBoostingRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html)
- scikit-learn documentation: [StackingRegressor](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.StackingRegressor.html)
- Chen and Guestrin (KDD 2016): [XGBoost: A Scalable Tree Boosting System](https://arxiv.org/pdf/1603.02754)
