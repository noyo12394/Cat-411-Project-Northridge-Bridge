# Explainable AI Layer

This note explains how explainable AI is used in the repository without breaking the engineering logic of the project.

The short version is:

- the project does **not** treat explainability as a cosmetic extra
- it uses explainability to check whether the machine-learning models are relying on structurally meaningful variables
- it keeps global intrinsic vulnerability, post-event proxy evidence, and event-damage prediction conceptually separate

## Why Explainable AI Matters Here

The project is not trying to build a mysterious black-box risk score.

Instead, the machine-learning layer is meant to answer questions like:

- Which bridge-intrinsic variables are actually driving the statewide vulnerability-screening model?
- Does `SVI` add signal beyond the raw structural variables it summarizes?
- Where does `NDVI` help, and where should it **not** be used?
- Are the strongest models learning something structurally reasonable, or only memorizing artifacts of the HAZUS-derived target?

That is why the repository includes explicit explainability outputs rather than only reporting accuracy.

## Explainability Methods Currently Implemented

The current repo focuses on **global explainability** rather than local bridge-by-bridge SHAP explanations.

### 1. Permutation feature importance

Used for the strongest tree-based models.

This shows how much performance drops when a feature is randomly shuffled after model training.

Current outputs:

- `data/processed/ml_disciplined_permutation_importance.csv`
- `data/processed/ml_hybrid_feature_importance.csv`
- `data/processed/ml_recommended_hybrid_feature_importance.csv`

Interpretation:

- higher importance means the trained model relied more on that feature
- these are model-based importance measures, not causal effects

### 2. Linear-model coefficients

Used for the disciplined linear baselines.

Current output:

- `data/processed/ml_disciplined_linear_coefficients.csv`

Interpretation:

- coefficients help show direction and relative influence in the standardized linear baseline
- they are useful for transparency, but they do not replace the stronger nonlinear models

### 3. Mutual-information screening

Used in the statewide hybrid workflow as a signal-screening aid.

Current output:

- `data/processed/ml_feature_screen_mutual_info.csv`
- `figures/ml_recommended_hybrid_mutual_information.png`

Interpretation:

- mutual information helps show which variables carry predictive signal, even when the relationship is nonlinear

### 4. Calibration and residual diagnostics

Used as explainability-adjacent checks rather than pure performance plots.

Current outputs include:

- `figures/ml_hybrid_decile_calibration.png`
- `figures/ml_recommended_hybrid_decile_calibration.png`
- `figures/ml_disciplined_residuals.png`
- `figures/ml_hybrid_residuals.png`

These help show whether the model is:

- systematically underpredicting or overpredicting
- only working on low-damage bridges
- behaving sensibly across score ranges

## New XAI Figures Added

The repo now includes two explainability figures generated directly from saved outputs:

- `figures/xai_global_feature_importance.png`
- `figures/xai_svi_ndvi_role_summary.png`

You can regenerate them with:

```bash
python scripts/export_xai_figures.py
```

## What The XAI Outputs Say

### Intrinsic vulnerability models

The strongest structural / no-PGA models rely most heavily on:

- bridge class / structural family
- deck scale / bridge size
- design era
- rehabilitation timing
- span geometry
- age

That is a good sign because those are physically meaningful bridge-intrinsic variables.

### SVI

`SVI` appears as a real contributor in the statewide SVI-inclusive model, but it is not the top driver.

That is logically consistent with the rest of the project:

- `SVI` is built from age, condition, skew, span, and related structural terms
- the raw ML feature set already contains much of that same information
- therefore `SVI` adds interpretability and contextual vulnerability meaning more clearly than it adds a large RMSE improvement

This is why the repo treats `SVI` as a valid contextual vulnerability feature, not as a guaranteed performance booster.

### NDVI

`NDVI` is not part of the core intrinsic vulnerability explanation layer.

The explainability story for `NDVI` is different:

- `NDVI` belongs in the post-event proxy / validation branch
- the proxy-validation metrics show that the hybrid proxy model improves exact accuracy, within-one-state accuracy, weighted kappa, and macro-F1 relative to the HAZUS-only baseline
- so `NDVI` is best explained as a post-event contextual signal rather than a structural vulnerability driver

## Recommended Wording

If you need one short professor-facing explanation, use this:

> The explainable-AI outputs show that the no-PGA statewide vulnerability models are driven primarily by bridge class, scale, design era, rehabilitation timing, age, and span geometry. SVI contributes meaningful structural context, but much of its signal overlaps with the raw bridge variables already included in the model. NDVI shows its strongest value in the post-event proxy-validation branch rather than in the baseline structural vulnerability model.

## Limitations

The current explainability layer is useful, but it has limits:

- it is mostly **global** explainability, not local bridge-by-bridge explanations
- it does not yet include SHAP values or counterfactual analysis
- the target remains HAZUS-derived `EDR`, so the explanations are explanations of the surrogate model behavior, not proof of field-observed causal damage mechanisms

## Good Future Add-Ons

If the project is extended later, the next explainability upgrades would be:

1. local SHAP values for selected bridge case studies
2. bridge-level "why this bridge scored high" cards in the dashboard
3. partial-dependence or ICE plots for variables such as age, skew, span length, and SVI
4. explicit sensitivity checks comparing structural-only and SVI-augmented models on matched bridge subsets
