# Proxy Validation

This report evaluates the optional NDVI branch as a **proxy-validation** workflow.

Important interpretation:
- The observed target here is the NDVI-derived proxy damage state, not an independent bridge inspection label.
- The HAZUS result should therefore be interpreted as a benchmark comparison against the proxy subset, not as full external validation.

- Validation subset size: `10,255` bridges with both proxy damage labels and HAZUS-side features

## Metrics

| Model | Exact_Accuracy | Within_1_State_Accuracy | MAE_Ordinal | Weighted_Kappa | Macro_F1 | Underprediction_Rate | Overprediction_Rate | Severe_Underprediction_Rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Univariate (HAZUS) | 0.6845 | 0.8016 | 0.7070 | 0.0809 | 0.2166 | 0.2599 | 0.0556 | 0.1736 |
| Hybrid Proxy Model | 0.7426 | 0.8415 | 0.5787 | 0.3548 | 0.3899 | 0.2209 | 0.0366 | 0.1390 |

## How To Read These Results

- `Exact_Accuracy` is the strictest metric and often harsh for ordinal damage states.
- `Within_1_State_Accuracy` is useful because predicting `Moderate` instead of `Extensive` is less wrong than predicting `None` instead of `Complete`.
- `Weighted_Kappa` rewards near-miss ordinal predictions more than distant misses.
- `Underprediction_Rate` is especially relevant here because the project concern was that the model may be biased toward lower damage states.

## Recommended Wording

- The current NDVI figure should be described as **limited proxy validation**.
- The HAZUS baseline and hybrid model can be compared on this subset, but this is still not equivalent to validation against a true observed bridge-damage dataset.
- If future observed bridge inspection labels become available, this same evaluation structure can be reused for proper external validation.

