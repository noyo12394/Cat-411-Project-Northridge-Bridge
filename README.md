# Cat-411-Project-Northridge-Bridge

This repository analyzes bridge vulnerability during the 1994 Northridge earthquake.

It contains two related workflows:
- a core engineering workflow that starts from the National Bridge Inventory and ShakeMap PGA rasters
- an optional NDVI-based catastrophe-model extension that needs additional change-detection files

The core workflow now runs entirely from repository-relative paths, so another user can clone the repo and reproduce the main results without relying on a personal `Downloads` folder.

## Repository Map

Main notebooks:
- `PGA_bridge.ipynb`: main preprocessing and PGA assignment notebook
- `HAZUS.ipynb`: HAZUS classification and Expected Damage Ratio
- `svi.ipynb`: Seismic Vulnerability Index computation
- `MachineLearning.ipynb`: predictive modeling for bridge vulnerability
- `Bridge_Week1.ipynb`: earlier exploratory preprocessing notebook
- `run_analysis.ipynb`: optional NDVI catastrophe-model pipeline

Main code folders:
- `modules/`: NDVI download, change detection, and visualization helpers
- `catastrophe_model/`: damage classification, fragility, disruption, and prioritization helpers

Project helper:
- `project_paths.py`: central path definitions used by the notebooks

Documentation:
- `README.md`: setup and high-level project explanation
- `docs/WORKFLOW.md`: step-by-step workflow from raw inputs to final outputs
- `data/README.md`: data layout and folder meaning

## Core Data Already Included

The following files needed for the main non-NDVI workflow are already in the repo:
- `data/CA25.txt`
- `data/pga_mean.flt`
- `data/pga_mean.hdr`
- other ShakeMap raster products in `data/`

## Quick Start

1. Clone the repository.
2. Create a Python environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Launch Jupyter from the repository root:

```bash
jupyter notebook
```

Running from the repository root matters because the notebooks discover `data/`, `figures/`, and `data/processed/` relative to the repo.

## Recommended Execution Order

For the main reproducible workflow, run these notebooks in order:

1. `PGA_bridge.ipynb`
2. `HAZUS.ipynb`
3. `svi.ipynb`
4. `MachineLearning.ipynb`

What each step does:
- `PGA_bridge.ipynb`
  Reads the raw bridge inventory and ShakeMap raster, cleans coordinates, samples PGA values, and writes `data/processed/pga_nbi_bridge.csv`.
- `HAZUS.ipynb`
  Assigns HAZUS bridge classes, computes damage-state probabilities, and writes `data/processed/bridges_with_edr.csv`.
- `svi.ipynb`
  Builds a continuous bridge vulnerability score and writes `data/processed/bridges_with_svi.csv`.
- `MachineLearning.ipynb`
  Trains regression models that predict EDR and writes `data/processed/bridge_ml_predictions.csv`.

## Generated Outputs

Core outputs created by the workflow:
- `data/processed/pga_nbi_bridge.csv`
- `data/processed/bridges_with_edr.csv`
- `data/processed/bridges_with_svi.csv`
- `data/processed/bridge_ml_predictions.csv`

These are the best files to inspect if you want the end results without stepping through every notebook cell.

## Optional NDVI Extension

`run_analysis.ipynb` is a separate NDVI-based catastrophe-model pipeline.

It requires additional files that are not currently committed in this repo:
- `data/change_detection/Pre_Event_NDVI.tif`
- `data/change_detection/Post_Event_NDVI.tif`
- `data/change_detection/NDVI_Change.tif`
- `data/change_detection/pga_bridge_ndvi_200m.csv`
- `data/change_detection/pga_bridge_ndvi_200m.shp` and companion files

If those files are missing, the notebook stops early with a clear message.

## How To Read The Project

If you are opening this repository for the first time, this order works well:

1. Read `README.md`
2. Read `docs/WORKFLOW.md`
3. Open `PGA_bridge.ipynb`
4. Open `HAZUS.ipynb`
5. Open `svi.ipynb`
6. Open `MachineLearning.ipynb`
7. Open `run_analysis.ipynb` only if the optional NDVI data is available

## What Was Improved For Portability

- notebook paths no longer depend on `/Users/.../Downloads`
- generated outputs are written inside the repository
- setup instructions are now explicit
- optional NDVI dependencies are separated from the core workflow
- shared paths are defined in one place through `project_paths.py`

## Notes

- `Bridge_Week1.ipynb` is kept for context and exploratory preprocessing, but `PGA_bridge.ipynb` is the cleaner main entry point for the core workflow
- the NDVI extension still depends on data not yet added to the repository
- the core non-NDVI workflow has been tested locally in this repo and generates the expected processed CSV outputs
