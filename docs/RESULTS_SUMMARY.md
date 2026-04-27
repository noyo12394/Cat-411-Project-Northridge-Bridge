# Results Summary

This file is the recommended high-level results summary for the repository.

It is written to keep the project logic disciplined:
- intrinsic bridge vulnerability is separated from event-specific hazard demand
- `SVI` is treated as an interpretable contextual vulnerability measure, not a magic variable that must improve every metric
- `NDVI` is treated as a post-event proxy / validation layer, not a baseline structural predictor
- `ADT` and related traffic variables belong in consequence / prioritization, not in the core vulnerability model

## Recommended Reading Order

If you want the shortest defensible path through the repo, read these in order:

1. `README.md`
2. `docs/DATA_AND_METHODS.md`
3. `docs/ML_HYBRID_ANALYSIS.md`
4. `docs/ML_DISCIPLINED_STUDY.md`
5. `docs/PROXY_VALIDATION.md`
6. `docs/DAMAGE_STATE_MODELS.md`

## Core Dataset Counts

- Full California bridge inventory used in the statewide ML rebuild: `25,975`
- Bridges with positive PGA / positive fragility demand in the Northridge footprint: `16,796`
- Positive `EDR` rows in the disciplined statewide regression study: `12,879`
- NDVI proxy-validation subset with bridge-level proxy labels and HAZUS-side features: `10,255`

These counts matter because the project now supports both:
- a statewide no-PGA vulnerability-screening workflow
- a Northridge event-damage workflow

## Layer 1. Engineering Workflow Outputs

The repository still starts from the engineering workflow:

1. `PGA_bridge.ipynb`
2. `HAZUS.ipynb`
3. `svi.ipynb`
4. `MachineLearning.ipynb`

Main generated bridge tables:

- `data/processed/pga_nbi_bridge.csv`
- `data/processed/bridges_with_edr.csv`
- `data/processed/bridges_with_svi.csv`

Important methodological updates already reflected in those outputs:

- revised April 2026 SVI parameter weights
- continuous scoring for condition, skew, and span length
- reconstruction-year multiplier on the weighted SVI score
- SVI-driven fragility medians using the revised linear / exponential expressions
- SVI-driven dispersion using `beta = 0.6 + 0.2 * SVI`

## Layer 2. Statewide Intrinsic Vulnerability Screening

When the research question is:

> Which bridges appear more vulnerable based on bridge-intrinsic structural characteristics alone?

the correct comparison is the no-PGA statewide vulnerability study.

### Best performance-first intrinsic model

Best cross-validated no-PGA structural model on the full California inventory:

- Feature set: `Structural + HAZUS Class`
- Model: `Extra Trees`
- Holdout MAE: `0.012350`
- Holdout RMSE: `0.039341`
- Holdout R2: `0.212044`
- Holdout RMSE on positive-damage bridges only: `0.047676`
- Holdout R2 on positive-damage bridges only: `0.227622`

Why this is the strongest professor-facing no-PGA result:

- it is the best cross-validated hazard-independent model
- it keeps `PGA` out of the baseline vulnerability score
- it uses `HWB_CLASS` only as a structural-system descriptor, not as hazard demand

The nearly tied raw-structural robustness baseline is:

- Feature set: `Structural Core`
- Model: `Extra Trees`
- Holdout RMSE: `0.039286`
- Holdout R2: `0.214257`

So the cleanest presentation position is:

- `Structural + HAZUS Class + Extra Trees` as the main no-PGA method
- `Structural Core + Extra Trees` as the pure raw-structural sensitivity check

### SVI-inclusive intrinsic model

Best statewide no-PGA model that explicitly retains `SVI`:

- Feature set: `Structural + SVI + HAZUS Class`
- Model: `Extra Trees`
- Holdout MAE: `0.012929`
- Holdout RMSE: `0.039761`
- Holdout R2: `0.195126`
- Holdout RMSE on positive-damage bridges only: `0.048015`
- Holdout R2 on positive-damage bridges only: `0.216613`

Interpretation:

- This SVI-inclusive model is slightly weaker than the best structural-only model on holdout metrics.
- That does **not** mean `SVI` is useless.
- It means that much of the information carried by `SVI` overlaps with raw structural variables such as age, class, geometry, rehabilitation timing, and deck scale.

### How to describe SVI honestly

The disciplined ablation study showed:

- Structural-only best CV RMSE: `0.039079`
- Structural + SVI best CV RMSE: `0.039219`
- Delta CV RMSE: `+0.000140`

So the correct claim is:

- `SVI` adds interpretable vulnerability context
- `SVI` is a meaningful contributor inside the broader intrinsic model
- but `SVI` does not by itself produce a dramatic RMSE improvement over well-engineered raw structural variables

That is a conceptually sound result, not a failure.

### What mattered most in the SVI-inclusive statewide model

From `data/processed/ml_recommended_hybrid_feature_importance.csv`, the most important variables in the recommended no-PGA SVI-inclusive model were:

1. `HWB_CLASS`
2. `deck_area_log1p`
3. `design_era_1989`
4. `operating_rating`
5. `time_since_rehab`
6. `max_span_log1p`
7. `age_years`
8. `spans`
9. `SVI`

So `SVI` is present as a real contributor, but it is not the dominant driver.

## Layer 3. NDVI As A Post-Event Proxy / Validation Branch

When the question becomes:

> Does remote-sensing-based post-event evidence help damage-state proxy classification?

the correct comparison is the NDVI proxy-validation workflow rather than the intrinsic vulnerability regression.

On the NDVI proxy-validation subset (`10,255` bridges):

| Model | Exact Accuracy | Within-1-State Accuracy | MAE Ordinal | Weighted Kappa | Macro F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Univariate (HAZUS) | 0.6845 | 0.8016 | 0.7070 | 0.0809 | 0.2166 |
| Hybrid Proxy Model | 0.7426 | 0.8415 | 0.5787 | 0.3548 | 0.3899 |

This is the clearest improvement story for `NDVI` in the repository.

Interpretation:

- `NDVI` helps in the post-event proxy-validation layer
- `NDVI` improves agreement with the proxy damage-state labels relative to the simpler HAZUS-only benchmark
- `NDVI` should therefore be described as a useful post-event contextual / validation feature
- `NDVI` should **not** be described as the main baseline structural vulnerability driver

## Layer 4. Event-Specific Damage Prediction

When the question becomes:

> Given event demand, how well can the workflow classify bridge damage state?

the correct comparison is the event-damage model family, which intentionally includes hazard demand.

Best event-damage classifier:

- Feature group: `Event Damage Classifier`
- Model: `Logistic Regression`
- Holdout balanced accuracy: `0.983681`
- Holdout macro-F1: `0.920788`
- Holdout within-one-state accuracy: `0.999230`
- Holdout quadratic weighted kappa: `0.962124`

This is the high-accuracy branch of the project.

Important interpretation:

- these metrics are high because the task is event-specific and includes hazard demand
- these metrics should **not** be used to claim that the hazard-independent intrinsic vulnerability model is equally accurate
- the event-damage model and the intrinsic vulnerability model answer different research questions

## Recommended Presentation Position

If the project needs one clean story, the repository supports this structure:

### Claim 1. The project can produce a defensible hazard-independent bridge vulnerability screen.

Use:
- full California bridge inventory
- no-PGA structural model
- holdout `R2` around `0.20`

Recommended reference:
- `Structural + HAZUS Class + Extra Trees`

### Claim 2. SVI is useful mainly as an interpretable contextual vulnerability measure.

Use:
- the SVI-inclusive model and feature-importance tables
- the disciplined ablation result
- the explainable-AI note in `docs/EXPLAINABLE_AI.md`

Recommended wording:

> SVI contributes meaningful structural context, but the raw structural variables already capture much of the same signal, so SVI improves interpretability more clearly than it improves RMSE.

### Claim 3. NDVI adds value in the post-event proxy-validation layer.

Use:
- `docs/PROXY_VALIDATION.md`
- the improvement in exact accuracy, within-one-state accuracy, weighted kappa, and macro-F1

Recommended wording:

> NDVI is most defensible as a post-event proxy / prioritization feature rather than as a baseline structural vulnerability variable.

### Claim 4. The highest accuracies occur only in the separate event-damage models.

Use:
- `docs/DAMAGE_STATE_MODELS.md`

Recommended wording:

> Event-damage models intentionally include hazard demand and therefore answer a different question from hazard-independent vulnerability screening.

## What Not To Claim

The repository results do **not** support the following statements:

- `SVI dramatically improves the core RMSE`
- `NDVI improves baseline structural vulnerability prediction`
- `ADT is a structural vulnerability predictor`
- `the no-PGA intrinsic vulnerability model is a full observed-damage predictor`
- `event-damage accuracy and intrinsic-screening accuracy are directly comparable`

## Best Files To Cite

For intrinsic vulnerability screening:
- `data/processed/ml_hybrid_best_by_feature_set.csv`
- `data/processed/ml_method_recommendation_summary.csv`
- `data/processed/ml_method_recommendation_top5_no_pga.csv`
- `data/processed/ml_recommended_hybrid_metrics.csv`
- `data/processed/ml_recommended_hybrid_feature_importance.csv`
- `figures/ml_method_recommendation.png`
- `docs/ML_HYBRID_ANALYSIS.md`
- `docs/ML_METHOD_RECOMMENDATION.md`
- `docs/EXPLAINABLE_AI.md`

For the disciplined ablation:
- `data/processed/ml_disciplined_best_by_family.csv`
- `data/processed/ml_disciplined_ablation_summary.csv`
- `data/processed/ml_disciplined_permutation_importance.csv`
- `docs/ML_DISCIPLINED_STUDY.md`

For NDVI:
- `data/processed/proxy_validation_metrics.csv`
- `docs/PROXY_VALIDATION.md`

For event-damage classification:
- `data/processed/damage_state_best_by_feature_set.csv`
- `data/processed/damage_state_model_comparison.csv`
- `docs/DAMAGE_STATE_MODELS.md`

## Bottom-Line Conclusion

The most defensible overall interpretation of the repository is:

- the full California bridge inventory supports a valid hazard-independent vulnerability-screening model
- `SVI` adds interpretable structural context, even when it does not materially outperform the best raw-structural baseline
- `NDVI` shows its strongest value in the post-event proxy-validation branch
- the highest reported accuracies belong to the separate event-damage models that intentionally include hazard demand

The explainable-AI outputs support that interpretation by showing that the strongest intrinsic models are driven mainly by bridge class, scale, design era, age, rehabilitation timing, and span geometry, while `SVI` remains a meaningful but non-dominant contextual feature.

That framing keeps vulnerability, hazard, proxy validation, and consequence from being mixed into one overstated result.
