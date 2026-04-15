# Data And Methods Guide

This file explains what data was collected, why it was collected, and how it flows through the project.

## Project Goal

The project studies bridge risk in the 1994 Northridge earthquake by combining:
- bridge inventory data
- earthquake hazard rasters
- HAZUS-style fragility logic
- a custom Seismic Vulnerability Index
- an optional NDVI-based catastrophe-model extension
- a machine-learning comparison layer

The result is a bridge-by-bridge workflow that starts from raw inventory and hazard data, then produces interpretable damage and vulnerability outputs.

## Core Source Data

### 1. Bridge Inventory

Primary file:
- `data/CA25.txt`

Collection method:
- downloaded as the California state extract from the Federal Highway Administration National Bridge Inventory ASCII files
- saved into the repository as `CA25.txt`
- loaded into Python with `pandas.read_csv()` for cleaning and analysis

Purpose:
- provides the California bridge inventory used throughout the project
- contains bridge attributes such as location, year built, reconstruction information, geometry, and condition-related fields
- serves as the asset base for hazard assignment, HAZUS classification, SVI computation, and ML modeling

What is in the local file:
- `25,975` bridge records
- `123` tabular fields
- key fields used in this project include structure identifiers, packed latitude and longitude values, bridge age / reconstruction variables, span-related fields, and condition-related attributes

### 2. ShakeMap Hazard Data

Primary files:
- `data/pga_mean.flt`
- `data/pga_mean.hdr`

Collection method:
- downloaded from the USGS ShakeMap product set for the 1994 Northridge earthquake
- stored in the repository as raster grid files, with `pga_mean.flt` used as the main hazard surface in the core workflow
- accompanied by related hazard layers and source metadata packaged with the ShakeMap download

Additional ShakeMap products included in the repository:
- `data/pga_std.flt`
- `data/pga_std.hdr`
- `data/mmi_mean.flt`
- `data/mmi_mean.hdr`
- `data/mmi_std.flt`
- `data/mmi_std.hdr`
- `data/pgv_mean.flt`
- `data/pgv_mean.hdr`
- `data/pgv_std.flt`
- `data/pgv_std.hdr`
- `data/psa0p3_mean.flt`
- `data/psa0p3_mean.hdr`
- `data/psa0p3_std.flt`
- `data/psa0p3_std.hdr`
- `data/psa1p0_mean.flt`
- `data/psa1p0_mean.hdr`
- `data/psa1p0_std.flt`
- `data/psa1p0_std.hdr`
- `data/psa3p0_mean.flt`
- `data/psa3p0_mean.hdr`
- `data/psa3p0_std.flt`
- `data/psa3p0_std.hdr`
- `data/metadata.xml`

Purpose:
- `pga_mean` is the main hazard surface used in the core workflow
- the other raster products show that the repository preserves the broader ShakeMap download, not just a single derived file
- `psa0p3` and `psa1p0` are especially relevant to HAZUS-style fragility adjustment concepts discussed during project development

Source note:
- USGS describes the 1994 Northridge ShakeMap as a retroactively generated ShakeMap product
- the broader ShakeMap program provides mapped ground-motion products such as PGA, PGV, MMI, and spectral acceleration layers

## Data Collection Strategy

The weekly project updates show that the team separated bridge variables into three groups.

### Critical parameters

These were treated as the most important variables for structural response:
- structure height
- span length
- span continuity
- skew angle
- location

Why they matter:
- they influence unseating risk, substructure response, and how a bridge experiences seismic demand

### Supplementary parameters

These were useful additions for improving interpretation and vulnerability scoring:
- year built
- retrofit status
- material type
- number of spans
- total bridge length

Why they matter:
- they help approximate bridge age, design era, geometry, and likely condition when a more detailed mechanics model is unavailable

### Parameters intentionally left out

These were acknowledged as important, but treated as out of scope for the simplified workflow:
- bearing type
- foundation type

Why they were left out:
- they are harder to collect consistently
- they are more useful in detailed finite-element-style modeling than in a broad inventory-scale screening workflow

## How Raw Data Becomes Analysis Data

### Step 1. Coordinate preprocessing

The bridge inventory stores location values in packed DMS-style fields. The preprocessing notebooks:
- unpack those values
- convert them to decimal latitude and longitude
- create bridge point locations

This is the key bridge between the asset dataset and the hazard rasters.

### Step 2. Spatial hazard assignment

The workflow overlays bridge points on the USGS ShakeMap raster:
- bridges inside the ShakeMap footprint are identified
- each bridge is assigned a PGA value
- the log-scale raster values are converted back into PGA units of `g`

This produces the first major derived table:
- `data/processed/pga_nbi_bridge.csv`

### Step 3. HAZUS bridge fragility workflow

The HAZUS portion of the project:
- assigns a HAZUS bridge class to each bridge
- rebuilds the updated SVI methodology on the bridge table
- computes damage-state fragility medians from SVI using either the revised linear or exponential expressions
- computes fragility dispersion from SVI using `beta = 0.6 + 0.2 * SVI`
- computes damage-state exceedance probabilities using lognormal fragility functions
- converts those into discrete damage-state probabilities
- computes Expected Damage Ratio (`EDR`)

This produces:
- `data/processed/bridges_with_edr.csv`

### Step 4. Seismic Vulnerability Index

The project then adds a continuous vulnerability measure that now follows the revised April 2026 methodology note.

The updated SVI uses these bridge attributes:
- year built
- condition rating
- skew
- structural continuity
- material family
- maximum span length
- number of spans
- year reconstructed as a multiplier

Updated method:
- `Year Built` uses era buckets:
  - pre-1971 -> `1.00`
  - `1971-1989` -> `0.70`
  - post-1989 -> `0.40`
- `Condition Rating` uses the continuous expression `(9 - CR) / 9`
- `Skew` uses the continuous expression `Skew / 30`, capped at `1.0`
- `Continuity` is scored as `1.0` for simply supported bridges and `0.0` for continuous bridges
- `Material` is scored by material family:
  - wood -> `1.00`
  - concrete -> `0.85`
  - steel -> `0.50`
- `Maximum Span Length` uses the continuous expression `Span Length / 250`, capped at `1.0`
- `Number of Spans` uses span-count buckets:
  - `1` -> `0.00`
  - `2-3` -> `0.25`
  - `4-6` -> `0.50`
  - `> 6` -> `0.85`
- the weighted raw score is multiplied by the `Year Reconstructed` factor:
  - pre-1971 -> `1.00`
  - `1971-1989` -> `0.95`
  - post-1989 -> `0.90`

Updated weights:
- Year Built -> `0.20`
- Condition Rating -> `0.20`
- Skew -> `0.15`
- Continuity -> `0.15`
- Material -> `0.10`
- Maximum Span Length -> `0.10`
- Number of Spans -> `0.10`

In code, the final score is:
- `SVI = (w_YB*YB + w_CR*CR + w_SK*SK + w_CT*CT + w_MA*MA + w_SL*SL + w_NS*NS) * YR`

Interpretation:
- lower `SVI` means lower relative bridge vulnerability
- higher `SVI` means higher relative bridge vulnerability

This produces:
- `data/processed/bridges_with_svi.csv`

### Step 4b. SVI-driven fragility parameters

The revised methodology also connects SVI directly to fragility parameters.

Median options implemented in the repo:
- linear:
  - `mu_DS(SVI) = mu_min,DS + SVI * (mu_max,DS - mu_min,DS)`
- exponential:
  - `mu_DS(SVI) = mu_max,DS * (mu_min,DS / mu_max,DS) ** (1 - SVI)`

The current default in the repo is the `linear` option.

Damage-state bounds used:
- slight: `0.25` to `0.80`
- moderate: `0.35` to `1.00`
- extensive: `0.45` to `1.20`
- complete: `0.70` to `1.70`

Dispersion expression:
- `beta = 0.6 + 0.2 * SVI`

This means the fragility curves are no longer a fixed lookup by bridge class alone. They now vary continuously with bridge-level vulnerability.

### Step 5. Machine-learning extension

The ML notebook compares simple predictive models for reproducing the HAZUS-style damage pattern from bridge and hazard features.

Models tested:
- Linear Regression
- Random Forest
- Gradient Boosting

Inputs include combinations of:
- PGA
- bridge attributes
- HAZUS class
- SVI

Output:
- predicted `EDR`
- model comparison metrics
- `data/processed/bridge_ml_predictions.csv`

## Damage Validation Logic Discussed During The Project

The slide materials also show the validation framing used in the project:
- most Northridge-exposed bridges had no damage
- moderate and major damage were much less common
- collapses were rare and concentrated in older structures
- damage increased with stronger shaking, but even high-PGA zones still contained many surviving bridges

That context matters because it explains why:
- the project keeps a probabilistic fragility framework
- the damage distribution is highly imbalanced
- comparing multiple methods is useful instead of trusting a single output blindly

## Optional NDVI And Catastrophe-Model Extension

The project later explored a remote-sensing-based extension.

Main idea:
- earthquake-driven ground disturbance can produce negative NDVI change
- bridges in higher shaking zones may also show stronger NDVI change nearby
- NDVI can be used as a proxy signal for disruption and post-event prioritization

Expected additional inputs:
- `data/change_detection/pga_nbi_bridge.shp` and companion shapefile files
- `data/change_detection/Pre_Event_NDVI.tif`
- `data/change_detection/Post_Event_NDVI.tif`
- `data/change_detection/NDVI_Change.tif`
- `data/change_detection/pga_bridge_ndvi_200m.csv`
- `data/change_detection/pga_bridge_ndvi_200m.shp` and companion shapefile files

Why the shapefile matters:
- it stores bridge-centered spatial features tied to the NDVI analysis
- it acts as the geometry layer connecting bridge locations with raster-based NDVI change summaries

The NDVI workflow was also used to discuss:
- HAZUS-aligned damage-state thresholds based on NDVI change
- Traffic Disruption Index ideas using damage probability and ADT
- prioritization mapping for emergency inspection

## What A New Reader Should Focus On

If someone wants to understand the project quickly, the most important files are:
- `README.md`
- `docs/DATA_AND_METHODS.md`
- `docs/WORKFLOW.md`
- `data/README.md`

Then they should inspect these outputs in order:
- `data/processed/pga_nbi_bridge.csv`
- `data/processed/bridges_with_edr.csv`
- `data/processed/bridges_with_svi.csv`
- `data/processed/bridge_ml_predictions.csv`

## What This Repository Now Documents Clearly

The repository now makes clear:
- which raw files were collected
- which bridge parameters were considered important
- which variables were intentionally excluded from the simplified workflow
- how bridge data is transformed into hazard, damage, vulnerability, and ML outputs
- where optional shapefiles and NDVI products fit into the broader project
