# Data Layout

This folder contains both committed source inputs and generated outputs.

## Included Source Inputs

These files are already committed and support the core engineering workflow:
- `CA25.txt`: California National Bridge Inventory source table downloaded as the California state ASCII extract from the FHWA National Bridge Inventory dataset
- `pga_mean.flt` and `pga_mean.hdr`: ShakeMap PGA raster and header downloaded from the USGS ShakeMap product set for the 1994 Northridge earthquake
- other ShakeMap raster products in this same folder
- `Data Collection.xlsx` and `Data Collection.docx`: project data-planning notes describing which bridge parameters were considered critical, supplementary, or out of scope
- `metadata.xml`: metadata that came with the raster download

Notable additional raster products in this folder:
- `mmi_mean` and `mmi_std`
- `pgv_mean` and `pgv_std`
- `psa0p3_mean` and `psa0p3_std`
- `psa1p0_mean` and `psa1p0_std`
- `psa3p0_mean` and `psa3p0_std`

These are not all used in the current core notebooks, but they document the broader hazard dataset collected for the project.

## How The Bridge Inventory Was Collected

The bridge inventory in `CA25.txt` was not created manually. It was collected by downloading the California state bridge-inventory extract from the Federal Highway Administration National Bridge Inventory ASCII files and then bringing that file into the repository for preprocessing.

In this repository, that file is then:
- read into pandas as the raw bridge table
- cleaned to unpack the stored coordinate fields
- converted into usable latitude / longitude values
- joined with the ShakeMap hazard raster during PGA assignment

## How The Hazard Rasters Were Collected

The hazard rasters in this folder were collected from the USGS ShakeMap product set for the 1994 Northridge earthquake. The repository keeps the main PGA raster used by the workflow, along with other related hazard layers and metadata that came with the download.

In this repository, those files are then:
- read as raster grids during preprocessing
- converted from stored ShakeMap values into usable ground-motion measures where needed
- sampled at bridge locations to assign bridge-level hazard intensity

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

The shapefile component is important because shapefiles are multi-file datasets. If this layer is added later, keep all companion files together, such as:
- `.shp`
- `.shx`
- `.dbf`
- `.prj`
- `.cpg` when available

If those files are missing, `run_analysis.ipynb` will stop immediately and tell the user exactly which files are required.

## How To Use This Folder

- read raw bridge data and raster inputs from `data/`
- read generated core workflow outputs from `data/processed/`
- place optional NDVI extension files in `data/change_detection/`
