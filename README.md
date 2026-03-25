# Cat-411-Project-Northridge-Bridge

This repository contains a bridge-level earthquake vulnerability analysis for the 1994 Northridge earthquake as part of the CAT 411 course project. The workflow combines bridge inventory processing, hazard assignment, HAZUS-based fragility analysis, Seismic Vulnerability Index (SVI) computation, and machine learning-based bridge vulnerability prediction.

The goal of the project is to move from basic bridge exposure analysis toward a more complete bridge risk framework by comparing engineering-based and data-driven methods for estimating damage vulnerability.

---

## Project Overview

This project was developed in multiple stages:

1. *Bridge exposure and hazard assignment*
   - Processed the California National Bridge Inventory (NBI)
   - Converted original bridge coordinates into usable latitude–longitude format
   - Integrated USGS ShakeMap Peak Ground Acceleration (PGA) data
   - Assigned PGA values to bridges within the earthquake footprint
   - Generated validation plots to inspect spatial exposure patterns

2. *HAZUS fragility-based damage estimation*
   - Assigned HAZUS bridge classes using structural attributes
   - Computed fragility-based damage-state probabilities
   - Estimated Expected Damage Ratio (EDR) for each bridge
   - Visualized class distribution and damage patterns

3. *Seismic Vulnerability Index (SVI) computation*
   - Built a continuous bridge vulnerability metric using bridge-specific variables
   - Used factors such as year built, reconstruction year, skew, span characteristics, and condition rating
   - Compared SVI against HAZUS-based damage outputs
   - Mapped spatial variation in structural vulnerability

4. *Machine learning-based vulnerability prediction*
   - Built predictive models for bridge vulnerability using meaningful bridge-specific factors
   - Avoided using PGA in the core ML model so the prediction focuses on intrinsic vulnerability rather than hazard intensity
   - Compared Linear Regression, Gradient Boosting, and Random Forest
   - Identified the best model for predicting EDR from structural and condition-related features

---

## Repository Contents

### Bridge_Week1.ipynb
This notebook contains the initial bridge exposure workflow.

Main tasks:
- Load and clean California NBI bridge data
- Convert raw latitude and longitude fields into decimal degrees
- Check spatial coverage of bridges across California
- Prepare the bridge inventory for hazard assignment

### PGA_bridge.ipynb
This notebook assigns earthquake hazard values to the bridge inventory.

Main tasks:
- Read PGA raster data from the Northridge ShakeMap output
- Sample raster values at bridge coordinates
- Convert raster values from log scale back to PGA values
- Create bridge-level PGA outputs
- Generate spatial and statistical plots for validation

### HAZUS.ipynb
This notebook applies the HAZUS-based bridge fragility framework.

Main tasks:
- Assign HAZUS bridge classes
- Compute exceedance probabilities for bridge damage states
- Convert exceedance probabilities into discrete damage-state probabilities
- Estimate Expected Damage Ratio (EDR)
- Visualize HAZUS class distributions and damage severity

### svi.ipynb
This notebook computes the Seismic Vulnerability Index (SVI).

Main tasks:
- Extract and clean bridge-specific vulnerability variables
- Normalize age, reconstruction history, skew, span geometry, and condition
- Build a weighted SVI score from 0 to 1
- Compare SVI against HAZUS-based EDR
- Generate spatial and class-based SVI plots

---

## Machine Learning Extension

The later phase of the project extends the engineering workflow into a machine learning framework for vulnerability prediction.

The ML setup uses only bridge-specific and structurally meaningful variables:
- year built
- reconstructed year
- number of spans
- maximum span length
- skew
- condition rating
- HAZUS bridge class
- SVI

The target variable is:
- *Expected Damage Ratio (EDR)*

This design is intentional. PGA was not used in the core ML model because PGA represents event intensity rather than intrinsic bridge vulnerability. Excluding PGA allows the model to focus on the bridge itself rather than simply reproducing hazard severity.

The tested models include:
- Linear Regression
- Gradient Boosting
- Random Forest

Among these, *Random Forest* performed best, suggesting that bridge vulnerability is influenced by nonlinear interactions among structural age, condition, geometry, and bridge class.

---

## Key Outputs

The project produces the following main outputs:
- cleaned bridge inventory with converted coordinates
- bridge-level PGA assignments
- HAZUS bridge classification
- damage-state probabilities
- Expected Damage Ratio (EDR)
- Seismic Vulnerability Index (SVI)
- machine learning predictions of bridge vulnerability

---

## Main Variables Used

Important bridge-level variables used across the workflow include:
- YEAR_BUILT_027
- YEAR_RECONSTRUCTED_106
- MAIN_UNIT_SPANS_045
- MAX_SPAN_LEN_MT_048
- DEGREES_SKEW_034
- LOWEST_RATING or SUBSTRUCTURE_COND_060
- STRUCTURE_KIND_043A
- STRUCTURE_TYPE_043B
- LAT_016
- LONG_017

Derived variables include:
- latitude
- longitude
- pga_raw
- pga
- HWB_CLASS
- P_DS0 to P_DS4
- EDR
- SVI

---

## Methods Summary

### HAZUS approach
The HAZUS method uses bridge classification and fragility parameters to estimate damage-state probabilities and Expected Damage Ratio based on hazard exposure.

### SVI approach
The SVI method provides a continuous, interpretable bridge-level vulnerability score derived from bridge attributes rather than predefined fragility classes alone.

### Machine learning approach
The ML method predicts damage-related vulnerability using bridge-specific features only, helping build a more flexible and interpretable data-driven framework.

---

## Interpretation

This repository reflects a progression from:
- bridge exposure analysis,
to
- fragility-based engineering damage estimation,
to
- bridge-specific vulnerability scoring,
to
- machine learning-based vulnerability prediction.

Together, these notebooks create a stronger bridge risk framework that can support future work such as dashboard development, decision-support tools, and comparison between HAZUS, SVI, and machine learning methods.

---

## Satellite NDVI-Based Catastrophe Model (New)

A modular, end-to-end catastrophe modeling pipeline using satellite NDVI change detection as a damage proxy, integrated with USGS ShakeMap ground motion data.

### New Code Structure

```
modules/                            # Satellite & NDVI analysis
    ndvi_download.py                # Download NDVI composites from Google Earth Engine
    change_detection.py             # NDVI change computation & per-bridge extraction
    visualization.py                # Raster maps, PGA-NDVI scatter, spatial plots

catastrophe_model/                  # Cat model pipeline (4 phases)
    damage_classification.py        # Phase 1: DS0-DS4 from NDVI thresholds
    proxy_fragility.py              # Phase 2: Empirical lognormal fragility curves
    economic_disruption.py          # Phase 3: Traffic Disruption Index (TDI)
    prioritization_map.py           # Phase 4: Emergency priority mapping

run_analysis.ipynb                  # Main notebook - runs the full pipeline
data/                               # Output datasets
figures/                            # Output figures from all phases
```

### Pipeline Overview

```
Hazard (PGA) + Exposure (Bridges + ADT) + Vulnerability (NDVI Fragility) = Loss (TDI)
```

- **Phase 1**: Classifies bridges into HAZUS-aligned damage states (DS0-DS4) using NDVI change thresholds
- **Phase 2**: Fits lognormal fragility curves from empirical PGA-damage exceedance data
- **Phase 3**: Computes Traffic Disruption Index (TDI = severity_weight x ADT) as economic loss proxy
- **Phase 4**: Generates emergency priority maps sized by TDI and colored by damage state

### How to Run

1. Open `run_analysis.ipynb` in Jupyter
2. Run all cells sequentially (Phases 0/0b are optional if data is pre-computed)
3. Figures are saved to `figures/`, final data to `data/`

---

## Future Scope

Possible next steps include:
- refining HAZUS class assignment logic
- validating SVI against observed bridge damage
- extending the machine learning workflow
- adding explainability and feature interpretation
- developing an interactive webpage or dashboard for bridge risk prediction and prioritization

---
