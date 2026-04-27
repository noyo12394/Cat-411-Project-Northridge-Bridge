# Interpretation Of Results

This note explains what the saved machine-learning outputs in the repository mean, which results are logically consistent, and how they should be presented in a defensible way.

It is based on the current saved outputs in:

- `docs/RESULTS_SUMMARY.md`
- `docs/ML_HYBRID_ANALYSIS.md`
- `docs/ML_DISCIPLINED_STUDY.md`
- `docs/PROXY_VALIDATION.md`
- `docs/DAMAGE_STATE_MODELS.md`

## Short Takeaway

The machine-learning results mostly make sense, but only if the project is interpreted as a layered framework with separate roles:

1. `Intrinsic vulnerability screening`: no PGA, bridge-intrinsic variables only.
2. `SVI context`: an interpretable structural summary that may overlap with raw bridge variables.
3. `NDVI post-event proxy branch`: useful after an event, not as a baseline structural driver.
4. `Event-damage prediction`: hazard-inclusive models that answer a different question and therefore achieve much higher accuracy.

The strongest conclusion is not that one model solves everything. The strongest conclusion is that the repository supports a disciplined separation between vulnerability, proxy validation, and event-specific damage.

## Data Context

From `data/processed/bridges_with_svi.csv`:

- Total bridges: `25,975`
- Bridges with positive EDR: `12,879`
- Bridges with zero or near-zero EDR: `13,096`
- Positive EDR share: `0.4958`
- Mean EDR: `0.00854`
- Median EDR: approximately `0`
- 95th percentile EDR: `0.03198`
- Maximum EDR: `0.47581`

This means the target distribution is highly skewed, with many very small values and a relatively small high-damage tail. That matters because:

- low RMSE values can still correspond to only moderate explanatory power
- models may look numerically strong on absolute error while still missing meaningful variation in the upper tail
- hazard-independent models should not be expected to reproduce event-specific damage perfectly

## Layer 1. Intrinsic Vulnerability Screening

The strongest no-PGA statewide model in the current repository is:

- Feature set: `Structural + HAZUS Class`
- Model: `Extra Trees`
- CV RMSE: `0.038232`
- Holdout MAE: `0.012350`
- Holdout RMSE: `0.039341`
- Holdout R2: `0.212044`
- Holdout RMSE on positive-damage bridges only: `0.047676`
- Holdout R2 on positive-damage bridges only: `0.227622`

The nearly tied pure raw-structural baseline is:

- Feature set: `Structural Core`
- Model: `Extra Trees`
- Holdout RMSE: `0.039286`
- Holdout R2: `0.214257`

### Interpretation

These values are believable.

Why they make sense:

- the target is HAZUS-derived `EDR`, which is fundamentally tied to hazard demand
- the intrinsic model deliberately excludes `PGA`
- without hazard intensity, the model can only learn bridge-intrinsic susceptibility, not exact earthquake damage

So the correct interpretation is:

- this is a `screening / ranking` model
- it captures a real structural signal
- it is not a full event-damage predictor

The no-PGA model is therefore strongest when described as a bridge-intrinsic vulnerability surrogate or screening tool. In practice, the best professor-facing choice is `Structural + HAZUS Class + Extra Trees`, while `Structural Core + Extra Trees` serves as a strong robustness check showing that the result does not depend on SVI.

## Layer 2. SVI As An Interpretable Context Variable

The best SVI-inclusive no-PGA statewide model in the repository is:

- Feature set: `Structural + SVI + HAZUS Class`
- Model: `Extra Trees`
- Holdout MAE: `0.012929`
- Holdout RMSE: `0.039761`
- Holdout R2: `0.195126`
- Holdout RMSE on positive-damage bridges only: `0.048015`
- Holdout R2 on positive-damage bridges only: `0.216613`

From the disciplined ablation study:

- Structural-only best CV RMSE: `0.039079`
- Structural + SVI best CV RMSE: `0.039219`
- Delta CV RMSE: `+0.000140`

### Interpretation

This also makes sense.

The results do **not** support the claim that SVI dramatically improves predictive accuracy. But they also do **not** imply that SVI is useless.

The most defensible reading is:

- `SVI` adds interpretable vulnerability context
- much of the information in `SVI` overlaps with raw structural variables already present in the model
- therefore SVI improves interpretation more clearly than it improves RMSE

This is exactly what we would expect if `SVI` summarizes things like age, geometry, class, rehabilitation timing, and condition.

### Why this is still a valid result

If a summary index is built from variables already included individually, then a small incremental gain is normal. That does not weaken the project. It shows that:

- the raw bridge variables are already informative
- the SVI framework is broadly aligned with those structural signals
- SVI can still serve as a transparent engineering summary for communication and comparison

### Feature-importance evidence

In `data/processed/ml_recommended_hybrid_feature_importance.csv`, the strongest variables in the recommended SVI-inclusive model are:

1. `HWB_CLASS`
2. `deck_area_log1p`
3. `design_era_1989`
4. `operating_rating`
5. `time_since_rehab`
6. `max_span_log1p`
7. `age_years`
8. `spans`
9. `SVI`

So `SVI` is a real contributor, but not the dominant one.

## Layer 3. NDVI As A Post-Event Proxy / Validation Branch

The cleanest NDVI result in the repository comes from the proxy-validation workflow on the subset with proxy labels (`10,255` bridges).

Saved comparison:

| Model | Exact Accuracy | Within-1-State Accuracy | MAE Ordinal | Weighted Kappa | Macro F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Univariate (HAZUS) | 0.6845 | 0.8016 | 0.7070 | 0.0809 | 0.2166 |
| Hybrid Proxy Model | 0.7426 | 0.8415 | 0.5787 | 0.3548 | 0.3899 |

### Interpretation

This improvement is logically consistent and should be presented as the main NDVI result.

Why it makes sense:

- NDVI reflects post-event surface/environmental response, not inherent bridge structure
- NDVI should therefore help in a post-event proxy-validation or prioritization layer
- NDVI should not be expected to improve the baseline intrinsic vulnerability model in the same way

The most defensible claim is:

- `NDVI` improves agreement with the proxy damage-state labels in the post-event branch
- `NDVI` is useful as contextual validation evidence or prioritization support
- `NDVI` should not be described as a core structural vulnerability predictor

## Layer 4. Event-Specific Damage Prediction

The highest-accuracy results in the repository come from the hazard-inclusive event-damage branch.

Best event-damage regression result:

- Feature set: `Event Damage Hybrid`
- Model: `MLPRegressor`
- Holdout RMSE: `0.000571`
- Holdout R2: `0.999834`

Best event-damage classification result:

- Feature group: `Event Damage Classifier`
- Model: `Logistic Regression`
- Holdout balanced accuracy: `0.983681`
- Holdout macro-F1: `0.920788`
- Holdout within-one-state accuracy: `0.999230`
- Holdout quadratic weighted kappa: `0.962124`

### Interpretation

These values are understandable, but they need careful framing.

Why they are so high:

- the event-damage branch includes `PGA`
- the target is HAZUS-derived `EDR` / damage state
- even the simple `HAZUS Benchmark` using `PGA + HWB_CLASS` already achieves very high performance

So this branch is best understood as:

- strong reproduction of the hazard-inclusive HAZUS-style target
- event-specific damage modeling
- not proof of near-perfect prediction of independent observed earthquake damage

That distinction matters. The event-damage model and the intrinsic vulnerability model answer different questions.

## What Makes The Overall Story Logical

Taken together, the repository outputs support a coherent interpretation:

### 1. Structural variables alone do contain useful vulnerability information.

That is why the no-PGA statewide model reaches holdout `R2` around `0.20`.

### 2. SVI overlaps with structural features by design.

That is why SVI contributes meaningfully but does not produce a dramatic accuracy jump.

### 3. NDVI belongs after the event, not before it.

That is why the NDVI improvement appears in proxy-validation metrics rather than in the baseline structural regression.

### 4. Hazard-inclusive models should outperform hazard-independent models.

That is why the event-damage branch is much more accurate than the intrinsic screening branch.

## Most Defensible Presentation Language

If the project needs a clean professor-facing interpretation, the following wording is appropriate:

> The no-PGA structural models support a defensible bridge-intrinsic vulnerability screening workflow, with moderate but real predictive power against the HAZUS-derived EDR target. SVI contributes interpretable structural context, but the raw structural variables already capture much of the same signal, so SVI improves interpretability more clearly than it improves RMSE. NDVI shows its strongest value in the post-event proxy-validation branch, where it improves agreement with proxy damage-state labels. The highest accuracies occur only in the separate hazard-inclusive event-damage models, which intentionally include PGA and are therefore answering a different research question.

## What Should Not Be Claimed

The current outputs do **not** justify saying:

- `SVI dramatically improves the core model`
- `NDVI improves baseline structural vulnerability prediction`
- `the event-damage model proves near-perfect prediction of observed bridge damage`
- `all branches of the project answer the same question`

## Bottom Line

The values in the repository make sense when interpreted as a layered framework:

- `Intrinsic vulnerability`: moderate, real, no-PGA structural screening
- `SVI`: interpretable contextual vulnerability signal
- `NDVI`: useful post-event proxy / validation feature
- `Event damage`: high-accuracy hazard-inclusive branch tied closely to the HAZUS-derived target

That is a coherent and defensible project story.
