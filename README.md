# Cat-411-Project-Northridge-Bridge

Bridge-level earthquake vulnerability analysis for the 1994 Northridge earthquake. The repository combines four related workflows:

- bridge inventory cleaning and PGA assignment from USGS ShakeMap rasters
- HAZUS fragility-based bridge damage estimation
- Seismic Vulnerability Index (SVI) scoring
- machine-learning prediction of bridge vulnerability

The repo has been reorganized so the notebooks use paths inside the repository instead of machine-specific `Downloads` folders.

## What Is In The Repo

Core source files:
- `Bridge_Week1.ipynb`
- `PGA_bridge.ipynb`
- `HAZUS.ipynb`
- `svi.ipynb`
- `MachineLearning.ipynb`
- `run_analysis.ipynb`
- `modules/`
- `catastrophe_model/`
- `project_paths.py`

Core data already included:
- `data/CA25.txt`
- `data/pga_mean.flt`
- `data/pga_mean.hdr`
- additional ShakeMap raster layers in `data/`

Generated outputs go to:
- `data/processed/`
- `figures/`

Optional change-detection inputs for `run_analysis.ipynb` go to:
- `data/change_detection/`

## Setup

1. Clone the repository.
2. Create and activate a Python environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Launch Jupyter from the repository root:

```bash
jupyter notebook
```

Running from the repository root matters because the notebooks now discover paths relative to the repo.

## Recommended Notebook Order

If you want the main bridge vulnerability workflow, run these notebooks in order:

1. `PGA_bridge.ipynb`
2. `HAZUS.ipynb`
3. `svi.ipynb`
4. `MachineLearning.ipynb`

What each one produces:
- `PGA_bridge.ipynb` writes `data/processed/pga_nbi_bridge.csv`
- `HAZUS.ipynb` writes `data/processed/bridges_with_edr.csv`
- `svi.ipynb` writes `data/processed/bridges_with_svi.csv`
- `MachineLearning.ipynb` writes `data/processed/bridge_ml_predictions.csv`

`Bridge_Week1.ipynb` is an earlier exploratory notebook. It now also writes the affected-only bridge subset to `data/processed/bridges_with_pga_affected_only.csv`.

## About `run_analysis.ipynb`

`run_analysis.ipynb` drives the NDVI-based catastrophe-model extension. It needs additional change-detection files that are not currently committed in this repository:

- `data/change_detection/Pre_Event_NDVI.tif`
- `data/change_detection/Post_Event_NDVI.tif`
- `data/change_detection/NDVI_Change.tif`
- `data/change_detection/pga_bridge_ndvi_200m.csv`
- `data/change_detection/pga_bridge_ndvi_200m.shp` and companion files

If those files are missing, the notebook now stops immediately with a clear error instead of failing later with broken paths.

If you also want to re-download NDVI data from Google Earth Engine, you will need:
- an authenticated Earth Engine account
- a valid GEE project for `ee.Initialize(...)`
- the optional packages in `requirements.txt`

## Main Methods

### HAZUS-based damage estimation
The HAZUS workflow assigns bridge classes and computes damage-state probabilities from PGA, then combines them into Expected Damage Ratio (EDR).

### SVI computation
The SVI workflow creates a continuous vulnerability score from bridge age, reconstruction year, skew, span characteristics, and condition measures.

### Machine learning
The ML workflow predicts EDR from bridge-specific features such as age, span geometry, condition, SVI, and HAZUS bridge class.

## Repo Notes

- Paths no longer depend on `/Users/.../Downloads`.
- Generated outputs stay inside the repository.
- The included ShakeMap raster lets the core PGA-to-HAZUS-to-SVI-to-ML workflow be reproduced once dependencies are installed.
- The NDVI catastrophe-model extension still needs the optional `data/change_detection/` bundle before it can run end-to-end.
