# Data Layout

This folder contains both committed source inputs and generated outputs.

## Included Source Inputs

These files are already committed and support the core engineering workflow:
- `CA25.txt`: California National Bridge Inventory source table
- `pga_mean.flt` and `pga_mean.hdr`: ShakeMap PGA raster and header
- other ShakeMap raster products in this same folder

## Generated Outputs

The main workflow writes outputs into `processed/`:
- `processed/pga_nbi_bridge.csv`
- `processed/bridges_with_edr.csv`
- `processed/bridges_with_svi.csv`
- `processed/bridge_ml_predictions.csv`
- `processed/final_bridge_analysis.csv` when the full optional pipeline is available

## Optional NDVI Extension Inputs

The optional NDVI-based catastrophe-model workflow uses `change_detection/`:
- `change_detection/Pre_Event_NDVI.tif`
- `change_detection/Post_Event_NDVI.tif`
- `change_detection/NDVI_Change.tif`
- `change_detection/pga_bridge_ndvi_200m.csv`
- `change_detection/pga_bridge_ndvi_200m.shp` plus companion files

If those files are missing, `run_analysis.ipynb` will stop immediately and tell the user exactly which files are required.

## How To Use This Folder

- read raw bridge data and raster inputs from `data/`
- read generated core workflow outputs from `data/processed/`
- place optional NDVI extension files in `data/change_detection/`
