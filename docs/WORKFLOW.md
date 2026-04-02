# Workflow Guide

This file explains the project from raw inputs to final outputs.

For the data-collection rationale and variable-selection logic behind this workflow, also read `docs/DATA_AND_METHODS.md`.

## Goal

The project studies bridge vulnerability during the 1994 Northridge earthquake using two connected ideas:
- an engineering workflow based on ShakeMap PGA and HAZUS fragility logic
- an optional NDVI-based catastrophe-model extension

The engineering workflow is the core reproducible path that runs from the data already committed in the repository.

## Core Inputs

These files are already in the repository:
- `data/CA25.txt`: California National Bridge Inventory source table
- `data/pga_mean.flt`: ShakeMap raster with log-scale PGA values
- `data/pga_mean.hdr`: raster header file required to read `pga_mean.flt`
- additional ShakeMap products in `data/` such as MMI, PGV, and PSA rasters
- `data/Data Collection.xlsx` and `data/Data Collection.docx`: bridge-parameter planning notes used during project development

## Core Notebook Sequence

### 1. `PGA_bridge.ipynb`
Purpose:
Convert NBI coordinates to decimal degrees and sample PGA from the ShakeMap raster.

Reads:
- `data/CA25.txt`
- `data/pga_mean.flt`

Writes:
- `data/processed/pga_nbi_bridge.csv`

Main columns created:
- `latitude`
- `longitude`
- `pga_raw`
- `pga`
- `join_id`

### 2. `HAZUS.ipynb`
Purpose:
Assign HAZUS bridge classes and compute damage-state probabilities and Expected Damage Ratio.

Reads:
- `data/processed/pga_nbi_bridge.csv`

Writes:
- `data/processed/bridges_with_edr.csv`

Main columns created:
- `HWB_CLASS`
- `P_DS0` to `P_DS4`
- `P_SUM`
- `EDR`

### 3. `svi.ipynb`
Purpose:
Build a continuous Seismic Vulnerability Index from bridge attributes.

Reads:
- `data/processed/bridges_with_edr.csv`

Writes:
- `data/processed/bridges_with_svi.csv`

Main columns created:
- `score_year`
- `score_recon`
- `score_skew`
- `score_spans`
- `score_max_span`
- `score_cond`
- `SVI_RAW`
- `SVI`

### 4. `MachineLearning.ipynb`
Purpose:
Train regression models that predict Expected Damage Ratio from bridge-specific features.

Reads:
- `data/processed/bridges_with_svi.csv`

Writes:
- `data/processed/bridge_ml_predictions.csv`

Models tested:
- Linear Regression
- Gradient Boosting
- Random Forest

## Exploratory Notebook

### `Bridge_Week1.ipynb`
Purpose:
Early exploratory preprocessing notebook that inspects coordinate cleaning and writes an affected-bridge subset.

Writes:
- `data/processed/bridges_with_pga_affected_only.csv`

Use this notebook for understanding the original preprocessing logic. Use `PGA_bridge.ipynb` for the cleaner main workflow.

## Optional NDVI Catastrophe-Model Extension

### `run_analysis.ipynb`
Purpose:
Run the NDVI-based damage proxy workflow and catastrophe-model extension.

Additional files required:
- `data/change_detection/Pre_Event_NDVI.tif`
- `data/change_detection/Post_Event_NDVI.tif`
- `data/change_detection/NDVI_Change.tif`
- `data/change_detection/pga_bridge_ndvi_200m.csv`
- `data/change_detection/pga_bridge_ndvi_200m.shp` and companion shapefile files

This notebook is intentionally separated from the core workflow because these files are not currently committed in the repository.

The shapefile and CSV in `data/change_detection/` represent the spatial bridge-layer outputs needed to connect the remote-sensing rasters back to bridge-level analysis.

## Recommended Reading Order For A New User

1. `README.md`
2. `docs/DATA_AND_METHODS.md`
3. `docs/WORKFLOW.md`
4. `PGA_bridge.ipynb`
5. `HAZUS.ipynb`
6. `svi.ipynb`
7. `MachineLearning.ipynb`
8. `run_analysis.ipynb` if the optional NDVI data is available

## Final Outputs A Reader Should Look At

If you want the clearest summary of the reproducible core workflow, start with:
- `data/processed/pga_nbi_bridge.csv`
- `data/processed/bridges_with_edr.csv`
- `data/processed/bridges_with_svi.csv`
- `data/processed/bridge_ml_predictions.csv`
