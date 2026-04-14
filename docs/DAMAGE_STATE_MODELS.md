# Damage-State Classification Models

This exploratory add-on reframes the bridge problem as a modal HAZUS damage-state classification task rather than a continuous EDR regression task.

## Damage-State Labels

The target label is the most probable HAZUS damage state for each bridge:

- `None`: `24,315` bridges
- `Slight`: `901` bridges
- `Moderate`: `706` bridges
- `Extensive`: `0` bridges
- `Complete`: `53` bridges

## Feature Groups

- `Structural Vulnerability Classifier`: no-PGA structural vulnerability variables only
- `Event Damage Classifier`: hazard + bridge variables for event-specific damage-state prediction

## Results

The most important metrics here are balanced accuracy, macro-F1, within-one-state accuracy, and quadratic weighted kappa because the damage states are ordinal and highly imbalanced.

| Feature Group | Model | CV_Balanced_Accuracy | CV_Macro_F1 | Holdout_Balanced_Accuracy | Holdout_Macro_F1 | Holdout_Within_One_State_Accuracy | Holdout_Quadratic_Weighted_Kappa |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Event Damage Classifier | Logistic Regression | 0.985661 | 0.931205 | 0.983681 | 0.920788 | 0.999230 | 0.962124 |
| Structural Vulnerability Classifier | Logistic Regression | 0.538226 | 0.262409 | 0.558036 | 0.263839 | 0.711453 | 0.046746 |

## Variable Reference

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

## Generated Artifacts

- `data/processed/damage_state_model_comparison.csv`
- `data/processed/damage_state_best_by_feature_set.csv`
- `data/processed/damage_state_predictions.csv`
- `data/processed/damage_state_classification_report.csv`
- `figures/damage_state_confusion_matrices.png`
