# Future Scenario Scoring

This exploratory add-on fits the event-damage model on the statewide bridge inventory and then rescores the full inventory under uniform hypothetical PGA scenarios. It is intended for future-earthquake scenario planning rather than intrinsic vulnerability ranking.

## Model Choice

- Feature set: `Event Damage Hybrid`
- Model: `MLPRegressor`
- Target: HAZUS-derived `EDR`
- Target transform: `log1p -> expm1`

## Scenario Summary

| Scenario | Scenario_PGA_g | Mean_Predicted_EDR | Median_Predicted_EDR | P90_Predicted_EDR | P95_Predicted_EDR | Bridges_EDR_ge_0_02 | Bridges_EDR_ge_0_08 | Bridges_EDR_ge_0_25 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Observed PGA | Observed pattern | 0.010988 | 0.000377 | 0.011580 | 0.049385 | 2052 | 961 | 332 |
| Scenario 0.05g | 0.050000 | 0.001248 | 0.001241 | 0.001831 | 0.002067 | 0 | 0 | 0 |
| Scenario 0.10g | 0.100000 | 0.004818 | 0.004129 | 0.008894 | 0.009900 | 0 | 0 | 0 |
| Scenario 0.20g | 0.200000 | 0.027061 | 0.030867 | 0.036017 | 0.037672 | 20817 | 0 | 0 |
| Scenario 0.40g | 0.400000 | 0.114803 | 0.126824 | 0.155431 | 0.160674 | 25975 | 20959 | 0 |

## Interpretation

- `Observed PGA` keeps the original Northridge-like shaking pattern already stored in the dataset.
- The uniform scenarios are stress tests: every bridge is rescored as if it experienced the same PGA level.
- These outputs are useful for prioritizing bridge screening before a future event, but they are still surrogate estimates because the target is HAZUS-derived `EDR` rather than observed bridge damage.

## Generated Artifacts

- `data/processed/future_scenario_summary.csv`
- `data/processed/future_scenario_bridge_scores.csv`
- `figures/future_scenario_mean_edr.png`
- `figures/future_scenario_risk_bands.png`
- `figures/future_scenario_top_counties.png`
