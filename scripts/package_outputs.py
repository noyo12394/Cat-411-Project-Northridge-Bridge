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
    'ml_statewide_training_dataset.csv': 'Statewide ML training table rebuilt on all California bridges with engineered HAZUS, SVI, and bridge features.',
    'ml_feature_manifest.csv': 'Engineering feature manifest used in the statewide ML comparison.',
    'ml_hybrid_comparison.csv': 'Cross-validated statewide ML model comparison across feature sets and model families.',
    'ml_hybrid_best_by_feature_set.csv': 'Best statewide ML model within each feature-set framing.',
    'ml_hybrid_predictions.csv': 'Holdout predictions for the best overall statewide ML benchmark model.',
    'ml_hybrid_feature_importance.csv': 'Permutation feature importance for the best overall statewide ML benchmark model.',
    'ml_target_transform_comparison.csv': 'Raw-target versus log-target holdout comparison for the recommended statewide model.',
    'ml_recommended_hybrid_metrics.csv': 'Metrics for the recommended statewide hybrid engineering model.',
    'ml_recommended_hybrid_predictions.csv': 'Holdout predictions for the recommended statewide hybrid engineering model.',
    'ml_recommended_hybrid_feature_importance.csv': 'Permutation feature importance for the recommended statewide hybrid engineering model.',
    'ml_feature_screen_mutual_info.csv': 'Mutual-information screen showing which statewide engineered variables carry the most signal.',
    'ml_statewide_bridge_scores.csv': 'Predicted statewide bridge-risk scores from the final recommended ML model.',
}

CORE_FIGURES = {
    'core_bridge_locations.png': 'Scatter map of bridge locations from the core PGA workflow.',
    'core_pga_distribution.png': 'Histogram of sampled bridge PGA values.',
    'core_hazus_class_distribution.png': 'Distribution of HAZUS bridge classes in the processed bridge inventory.',
    'core_edr_distribution.png': 'Distribution of Expected Damage Ratio values.',
    'core_edr_by_hazus_class.png': 'Boxplot of EDR by the most common HAZUS bridge classes.',
    'core_log_edr_distribution.png': 'Log-scaled EDR distribution for positive-damage bridges.',
    'core_damage_state_probabilities.png': 'Average HAZUS damage-state probabilities across the bridge set.',
    'core_damage_state_by_hazus_class.png': 'Stacked average damage-state probabilities by HAZUS class.',
    'core_svi_distribution.png': 'Distribution of Seismic Vulnerability Index values.',
    'core_svi_vs_edr.png': 'Scatter plot comparing SVI against HAZUS EDR.',
    'core_mean_svi_by_hazus_class.png': 'Mean SVI by HAZUS bridge class.',
    'core_pga_vs_svi.png': 'Scatter plot relating PGA and SVI.',
    'core_ml_actual_vs_predicted.png': 'Actual-versus-predicted EDR figure for the notebook ML output.',
    'core_ml_residuals.png': 'Residual distribution for the notebook ML output.',
    'ml_hybrid_rmse_heatmap.png': 'RMSE heatmap for the advanced hybrid ML comparison.',
    'ml_hybrid_r2_heatmap.png': 'R2 heatmap for the advanced hybrid ML comparison.',
    'ml_hybrid_rmsle_heatmap.png': 'RMSLE heatmap for the advanced hybrid ML comparison.',
    'ml_hybrid_actual_vs_predicted.png': 'Actual-versus-predicted EDR for the best advanced hybrid ML model.',
    'ml_hybrid_log_actual_vs_predicted.png': 'Log-scale actual-versus-predicted EDR for the best advanced hybrid ML model.',
    'ml_hybrid_residuals.png': 'Residual distribution for the best advanced hybrid ML model.',
    'ml_hybrid_decile_calibration.png': 'Decile calibration plot for the best advanced hybrid ML model.',
    'ml_hybrid_feature_importance.png': 'Permutation feature importance for the best advanced hybrid ML model.',
    'ml_recommended_hybrid_actual_vs_predicted.png': 'Actual-versus-predicted EDR for the recommended hybrid engineering model.',
    'ml_recommended_hybrid_log_actual_vs_predicted.png': 'Log-scale actual-versus-predicted EDR for the recommended hybrid engineering model.',
    'ml_recommended_hybrid_feature_importance.png': 'Feature importance for the recommended hybrid engineering model.',
    'ml_recommended_hybrid_decile_calibration.png': 'Decile calibration plot for the recommended hybrid engineering model.',
    'ml_recommended_hybrid_mutual_information.png': 'Mutual-information ranking for the recommended statewide feature set.',
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

    for name in CORE_FIGURES:
        src = figures_dir / name
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

    write_inventory(core_dir, 'Core Outputs', {**CORE_OUTPUTS, **CORE_FIGURES})
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
