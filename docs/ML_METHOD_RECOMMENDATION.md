# ML Method Recommendation

This note answers one focused question:

> What is the strongest machine-learning method in this repository once the project is framed correctly?

The answer depends on the question we are asking.

- If the goal is **hazard-independent bridge vulnerability screening**, the best method is a no-PGA tree ensemble.
- If the goal is **event-specific damage prediction**, the best method is the PGA-inclusive event model.

Those are different tasks, so they should not be collapsed into one score.

## Literature-Guided Takeaway

The literature already cited in this repository points in a consistent direction for structured engineering tabular data:

- Shwartz-Ziv and Armon (2022): tree ensembles remain extremely strong default baselines for tabular problems.
- Gorishniy et al. (2021): deep models do not automatically outperform tree ensembles on tabular data.
- Mangalathu et al. (2019), Wang et al. (2022), and Zhao et al. (2023): bridge seismic ML studies repeatedly use tree models, support-vector methods, and related nonlinear tabular methods as competitive baselines.

The saved repository outputs follow that pattern closely:

- `Extra Trees` is the strongest no-PGA model family.
- `Random Forest` is the next-best no-PGA family.
- `HistGradientBoosting` is competitive, but weaker than the best tree-bagging models here.
- `MLPRegressor` becomes dominant only in the separate hazard-inclusive event-damage branch.

## Best Method By Research Question

### 1. Best hazard-independent method

Recommended baseline vulnerability model:

- Feature set: `Structural + HAZUS Class`
- Model: `Extra Trees`
- CV RMSE: `0.038232`
- CV R2: `0.175733`
- Holdout RMSE: `0.039341`
- Holdout R2: `0.212044`
- Holdout RMSE on positive-damage bridges only: `0.047676`
- Holdout R2 on positive-damage bridges only: `0.227622`

Why this is the best overall no-PGA choice:

- it is the best cross-validated no-PGA model in the statewide study
- it keeps `PGA` out of the vulnerability screen
- it uses bridge-intrinsic structural variables only, plus `HWB_CLASS` as a structural-system descriptor
- it is easier to defend than an SVI-heavy model when the question is pure predictive performance

### 2. Best pure structural-only robustness baseline

Nearly tied model:

- Feature set: `Structural Core`
- Model: `Extra Trees`
- CV RMSE: `0.038518`
- Holdout RMSE: `0.039286`
- Holdout R2: `0.214257`

Why it still matters:

- it is the cleanest possible no-PGA, no-SVI, no-class baseline
- it slightly edges the other no-PGA models on one holdout split
- it shows the predictive signal is already present in raw age, rehabilitation, geometry, condition, and size variables

Practical recommendation:

- use `Structural + HAZUS Class + Extra Trees` as the main professor-facing no-PGA method
- keep `Structural Core + Extra Trees` as the robustness baseline that proves the result does not depend on adding SVI

### 3. Best SVI-inclusive method

Best explicit-SVI model:

- Feature set: `Structural + SVI + HAZUS Class`
- Model: `Extra Trees`
- CV RMSE: `0.038512`
- Holdout RMSE: `0.039797`
- Holdout R2: `0.193692`

Interpretation:

- this model is useful when you want `SVI` visible in the feature set
- it is not the strongest pure prediction model
- that is actually a logical result, because SVI overlaps heavily with age, class, geometry, rehabilitation timing, and condition

So the right way to describe SVI is:

- strong for interpretation and engineering communication
- not the main reason the best RMSE is achieved

### 4. Best event-damage method

Best hazard-inclusive downstream model:

- Feature set: `Event Damage Hybrid`
- Model: `MLPRegressor`
- CV RMSE: `0.000625`
- CV R2: `0.999772`
- Holdout RMSE: `0.000571`
- Holdout R2: `0.999834`

Why this is not the main vulnerability model:

- it includes `PGA`
- it answers an event-specific damage question
- it is therefore not directly comparable to the no-PGA vulnerability screening models

This model is excellent for scenario mode in the dashboard, not for the baseline vulnerability score.

## Top 5 No-PGA Models

The saved top-five no-PGA models are:

| Rank | Feature Set | Model | CV RMSE | Holdout RMSE | Holdout R2 |
| --- | --- | --- | ---: | ---: | ---: |
| 1 | Structural + HAZUS Class | Extra Trees | 0.038232 | 0.039341 | 0.212044 |
| 2 | Structural + SVI | Extra Trees | 0.038490 | 0.039623 | 0.200714 |
| 3 | Structural + SVI + HAZUS Class | Extra Trees | 0.038512 | 0.039797 | 0.193692 |
| 4 | Structural Core | Extra Trees | 0.038518 | 0.039286 | 0.214257 |
| 5 | Structural + HAZUS Class | Random Forest | 0.038777 | 0.040333 | 0.171799 |

The pattern is important:

- the top four no-PGA rows are all `Extra Trees`
- `Random Forest` is next, but clearly behind
- that is strong evidence that randomized tree ensembles are the best hazard-independent family in this repo

## What This Means For The Dashboard

If you want one clean end-to-end recommendation:

1. Baseline vulnerability score:
   use `Structural + HAZUS Class + Extra Trees`
2. Interpretability layer:
   surface `SVI` as an explanatory/context variable, not the main accuracy driver
3. Post-event contextual layer:
   use `NDVI` only in the optional post-event / proxy-validation branch
4. Event scenario mode:
   use the PGA-inclusive `Event Damage Hybrid + MLPRegressor`

That gives the dashboard a disciplined architecture:

- baseline vulnerability stays hazard-independent
- event damage stays hazard-specific
- proxy/context layers stay separate

## Final Recommendation

The best machine-learning method in this repository is **not one single model for every purpose**.

The strongest defensible recommendation is:

- **Best hazard-independent bridge vulnerability model:** `Structural + HAZUS Class + Extra Trees`
- **Best pure structural-only baseline:** `Structural Core + Extra Trees`
- **Best explicit-SVI comparison model:** `Structural + SVI + HAZUS Class + Extra Trees`
- **Best event-damage model:** `Event Damage Hybrid + MLPRegressor`

So if the question is:

> What should the project present as its main bridge vulnerability model?

the answer is:

> Present `Extra Trees` with the `Structural + HAZUS Class` no-PGA feature family as the main vulnerability model, keep `Structural Core` as the raw-structural robustness baseline, and treat `SVI`, `NDVI`, and PGA-based event models as separate layers with different roles.
