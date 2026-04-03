from pathlib import Path
import shutil
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from project_paths import build_paths


CORE_OUTPUTS = {
    'pga_nbi_bridge.csv': 'Bridge inventory with cleaned coordinates and sampled PGA values.',
    'bridges_with_edr.csv': 'HAZUS-based bridge damage probabilities and Expected Damage Ratio.',
    'bridges_with_svi.csv': 'Bridge-level Seismic Vulnerability Index scores merged onto the damage table.',
    'bridge_ml_predictions.csv': 'Machine-learning predictions and evaluation outputs for bridge damage modeling.',
    'bridges_with_pga_affected_only.csv': 'Exploratory subset of bridges with usable PGA values from the week-1 workflow.',
}

NDVI_EXPECTED = {
    'final_bridge_analysis.csv': 'Final catastrophe-model dataset after NDVI damage classification, fragility, and disruption analysis.',
    'proxy_validation_metrics.csv': 'Proxy-validation metrics comparing the HAZUS baseline against the hybrid validation model.',
    'proxy_validation_predictions.csv': 'Held-out bridge-level proxy-validation predictions for HAZUS and the hybrid validation model.',
    'NDVI_Raster_Maps.png': 'Three-panel raster comparison of pre-event NDVI, post-event NDVI, and NDVI change.',
    'NDVI_Change_Only.png': 'Standalone map of NDVI change.',
    'PGA_vs_NDVI.png': 'Scatter plot comparing bridge PGA values to bridge-level NDVI change.',
    'Bridge_NDVI_Map.png': 'Spatial bridge map colored by NDVI change.',
    'Phase1_DamageClassification.png': 'Damage-state distribution figure based on NDVI thresholds.',
    'Phase2_FragilityCurves.png': 'Empirical proxy fragility curves derived from NDVI-based damage states.',
    'Phase3_EconomicDisruption.png': 'Traffic disruption summary figure.',
    'Phase4_PriorityMap.png': 'Emergency bridge prioritization map.',
    'proxy_validation_confusion_matrices.png': 'Side-by-side confusion matrices for the HAZUS baseline and the hybrid proxy-validation model.',
}


def write_inventory(path: Path, title: str, items: dict) -> None:
    lines = [f'# {title}', '', 'This folder contains packaged outputs for easier review.', '']
    for name, desc in items.items():
        exists = (path / name).exists()
        status = 'present' if exists else 'not present yet'
        lines.append(f'- `{name}`: {desc} Currently {status}.')
    path.mkdir(parents=True, exist_ok=True)
    (path / 'README.md').write_text('\n'.join(lines) + '\n')


def main() -> None:
    paths = build_paths()
    project_root = paths['PROJECT_ROOT']
    processed_dir = paths['PROCESSED_DIR']
    figures_dir = paths['FIGURES_DIR']
    outputs_dir = project_root / 'outputs'
    core_dir = outputs_dir / 'core'
    ndvi_dir = outputs_dir / 'ndvi'

    core_dir.mkdir(parents=True, exist_ok=True)
    ndvi_dir.mkdir(parents=True, exist_ok=True)

    for name in CORE_OUTPUTS:
        src = processed_dir / name
        if src.exists():
            shutil.copy2(src, core_dir / name)

    if paths['FINAL_ANALYSIS_CSV'].exists():
        shutil.copy2(paths['FINAL_ANALYSIS_CSV'], ndvi_dir / paths['FINAL_ANALYSIS_CSV'].name)
    for name in ['proxy_validation_metrics.csv', 'proxy_validation_predictions.csv']:
        src = processed_dir / name
        if src.exists():
            shutil.copy2(src, ndvi_dir / name)

    for name in NDVI_EXPECTED:
        src = figures_dir / name
        if src.exists():
            shutil.copy2(src, ndvi_dir / name)

    write_inventory(core_dir, 'Core Outputs', CORE_OUTPUTS)
    write_inventory(ndvi_dir, 'NDVI Outputs', NDVI_EXPECTED)

    overview = outputs_dir / 'README.md'
    overview.write_text(
        '# Outputs\n\n'
        'This folder collects review-friendly copies of generated project outputs.\n\n'
        '- `core/`: outputs from the main reproducible bridge workflow\n'
        '- `ndvi/`: outputs from the optional NDVI catastrophe-model workflow\n\n'
        'Run `python scripts/package_outputs.py` after generating results to refresh these folders.\n'
    )


if __name__ == '__main__':
    main()
