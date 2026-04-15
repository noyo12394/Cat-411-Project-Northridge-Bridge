# Results Summary

This file summarizes the core non-NDVI workflow results that were generated directly from the repository data.

Important methodology note:
- the engineering workflow now uses the revised April 2026 SVI methodology, including updated parameter weights, continuous scoring for selected variables, an SVI-based fragility-median mapping, and the SVI-based dispersion expression

## What Was Run

The following notebooks were run successfully as the main reproducible workflow:
- `PGA_bridge.ipynb`
- `HAZUS.ipynb`
- `svi.ipynb`
- `MachineLearning.ipynb`

The optional NDVI workflow in `run_analysis.ipynb` was not executed because its additional change-detection files are not yet committed to the repository.

## Main Output Files

The core workflow produced these outputs:
- `data/processed/pga_nbi_bridge.csv`
- `data/processed/bridges_with_edr.csv`
- `data/processed/bridges_with_svi.csv`
- `data/processed/bridge_ml_predictions.csv`

## Key Dataset Counts

### PGA assignment
- total bridge rows processed: `25,975`
- bridges with non-null PGA values: `16,796`

### HAZUS and SVI stages
- bridges carried through HAZUS damage analysis: `16,796`
- bridges carried through SVI scoring: `16,796`

### Machine-learning stage
- prediction rows written: `3,361`

## Model Performance

The machine-learning notebook compared three regressors for predicting `EDR`:

| Model | MAE | RMSE | R2 |
| --- | ---: | ---: | ---: |
| Random Forest | 0.022871 | 0.052651 | 0.153384 |
| Gradient Boosting | 0.024467 | 0.054899 | 0.079534 |
| Linear Regression | 0.025208 | 0.056212 | 0.034983 |

Best-performing model in this run:
- `Random Forest`

## Interpretation

What these results suggest:
- the preprocessing pipeline successfully matched a large subset of bridges to the ShakeMap hazard footprint
- the HAZUS workflow produced bridge-level probabilistic damage outputs for all bridges that received usable PGA values
- the SVI workflow adds a continuous vulnerability measure that can be compared against damage estimates
- the machine-learning extension can reproduce part of the HAZUS-based damage pattern, but the modest `R2` values show that this remains a noisy and challenging prediction problem

## How To Use These Results

For a quick understanding of the finished project, review the outputs in this order:
1. `data/processed/pga_nbi_bridge.csv`
2. `data/processed/bridges_with_edr.csv`
3. `data/processed/bridges_with_svi.csv`
4. `data/processed/bridge_ml_predictions.csv`

For the full project story, read these docs in order:
1. `README.md`
2. `docs/DATA_AND_METHODS.md`
3. `docs/WORKFLOW.md`
4. `docs/RESULTS_SUMMARY.md`
