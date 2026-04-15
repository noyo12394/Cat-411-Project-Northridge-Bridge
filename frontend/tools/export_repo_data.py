from __future__ import annotations

import json
import math
import shutil
from pathlib import Path

import pandas as pd


RESEARCH_FIGURES = [
    'ml_recommended_hybrid_actual_vs_predicted.png',
    'ml_recommended_hybrid_decile_calibration.png',
    'damage_state_confusion_matrices.png',
    'future_scenario_mean_edr.png',
    'future_scenario_risk_bands.png',
    'future_scenario_top_counties.png',
]

CSV_EXPORTS = [
    'ml_recommended_hybrid_metrics.csv',
    'ml_recommended_hybrid_feature_importance.csv',
    'ml_hybrid_best_by_feature_set.csv',
    'damage_state_best_by_feature_set.csv',
    'future_scenario_summary.csv',
]


def clean_value(value):
    if pd.isna(value):
        return None
    if hasattr(value, 'item'):
        value = value.item()
    if isinstance(value, float):
        if math.isinf(value) or math.isnan(value):
            return None
        return round(value, 6)
    return value


def to_records(df: pd.DataFrame, limit: int | None = None):
    if limit is not None:
        df = df.head(limit)
    return [
        {key: clean_value(value) for key, value in row.items()}
        for row in df.to_dict(orient='records')
    ]


def normalize_counts(series: pd.Series):
    return {str(key): int(value) for key, value in series.items()}


def risk_band_distribution(svi: pd.Series):
    bins = [0.0, 0.25, 0.4, 0.55, 0.7, 1.0]
    labels = ['Low', 'Guarded', 'Elevated', 'High', 'Critical']
    cats = pd.cut(svi.clip(lower=0, upper=1), bins=bins, labels=labels, include_lowest=True)
    return normalize_counts(cats.value_counts().reindex(labels, fill_value=0))


def sample_bridge_rows(df: pd.DataFrame):
    picks = []
    labelled_quantiles = [('Portfolio Lower Risk', 0.15), ('Portfolio Mid Risk', 0.5), ('Portfolio Higher Risk', 0.85)]
    ranked = df.sort_values('SVI').reset_index(drop=True)
    for label, q in labelled_quantiles:
        idx = min(len(ranked) - 1, max(0, int(q * (len(ranked) - 1))))
        row = ranked.iloc[idx]
        picks.append(
            {
                'label': label,
                'structureNumber': clean_value(row.get('STRUCTURE_NUMBER_008')),
                'countyCode': clean_value(row.get('COUNTY_CODE_003')),
                'yearBuilt': int(clean_value(row.get('year')) or 0),
                'yearReconstructed': clean_value(row.get('YEAR_RECONSTRUCTED_106')),
                'spans': int(clean_value(row.get('spans')) or 0),
                'maxSpan': clean_value(row.get('max_span')),
                'skew': clean_value(row.get('skew')),
                'condition': clean_value(row.get('cond')),
                'svi': clean_value(row.get('SVI')),
                'bridgeClass': clean_value(row.get('HWB_CLASS')),
                'adt': clean_value(row.get('ADT_029')) if 'ADT_029' in row else None,
            }
        )
    return picks


def build_summary(repo_root: Path):
    processed_root = repo_root / 'data' / 'processed'
    bridges_with_svi = pd.read_csv(processed_root / 'bridges_with_svi.csv', low_memory=False)
    bridges_with_edr = pd.read_csv(processed_root / 'bridges_with_edr.csv', low_memory=False)
    bridge_ml_predictions = pd.read_csv(processed_root / 'bridge_ml_predictions.csv', low_memory=False)
    pga_nbi_bridge = pd.read_csv(processed_root / 'pga_nbi_bridge.csv', low_memory=False)

    ds_cols = [col for col in ['P_DS0', 'P_DS1', 'P_DS2', 'P_DS3', 'P_DS4'] if col in bridges_with_edr.columns]
    mapping = {'P_DS0': 'None', 'P_DS1': 'Slight', 'P_DS2': 'Moderate', 'P_DS3': 'Extensive', 'P_DS4': 'Complete'}
    modal_damage = bridges_with_edr[ds_cols].idxmax(axis=1).map(mapping) if ds_cols else pd.Series(dtype='object')

    class_profiles = (
        bridges_with_svi.groupby('HWB_CLASS', dropna=False)
        .agg(count=('HWB_CLASS', 'size'), meanSVI=('SVI', 'mean'), meanEDR=('EDR', 'mean'))
        .reset_index()
        .sort_values('meanSVI', ascending=False)
    )

    county_profiles = (
        bridges_with_svi.groupby('COUNTY_CODE_003', dropna=False)
        .agg(count=('COUNTY_CODE_003', 'size'), meanSVI=('SVI', 'mean'), meanEDR=('EDR', 'mean'))
        .reset_index()
        .sort_values(['count', 'meanSVI'], ascending=[False, False])
        .head(12)
    )

    feature_ranges = {
        'yearBuilt': {
            'min': int(bridges_with_svi['year'].min()),
            'max': int(bridges_with_svi['year'].max()),
        },
        'yearReconstructed': {
            'min': int(bridges_with_svi['YEAR_RECONSTRUCTED_106'].dropna().min()),
            'max': int(bridges_with_svi['YEAR_RECONSTRUCTED_106'].dropna().max()),
        },
        'skew': {'min': 0, 'max': int(bridges_with_svi['skew'].max())},
        'spans': {'min': int(bridges_with_svi['spans'].min()), 'max': int(bridges_with_svi['spans'].max())},
        'maxSpan': {
            'min': clean_value(bridges_with_svi['max_span'].min()),
            'max': clean_value(bridges_with_svi['max_span'].quantile(0.98)),
        },
        'condition': {'min': int(bridges_with_svi['cond'].min()), 'max': int(bridges_with_svi['cond'].max())},
        'svi': {'min': clean_value(bridges_with_svi['SVI'].min()), 'max': clean_value(bridges_with_svi['SVI'].max())},
        'adt': {'min': 0, 'max': 120000},
    }

    calibration = bridge_ml_predictions[['Actual_EDR', 'Predicted_EDR', 'SVI', 'year', 'cond', 'HWB_CLASS']].copy()
    if len(calibration) > 240:
        calibration = calibration.iloc[:: max(1, len(calibration) // 240)].copy()

    summary = {
        'generatedAt': pd.Timestamp.utcnow().isoformat(),
        'counts': {
            'totalBridges': int(len(bridges_with_svi)),
            'hazardSampled': int(pga_nbi_bridge['pga'].notna().sum()),
            'mlCalibrationRows': int(len(bridge_ml_predictions)),
            'bridgeClasses': int(bridges_with_svi['HWB_CLASS'].nunique()),
        },
        'portfolio': {
            'meanSVI': clean_value(bridges_with_svi['SVI'].mean()),
            'medianSVI': clean_value(bridges_with_svi['SVI'].median()),
            'meanEDR': clean_value(bridges_with_edr['EDR'].mean()),
            'sviRiskBands': risk_band_distribution(bridges_with_svi['SVI']),
            'modalDamageStates': normalize_counts(modal_damage.value_counts()),
        },
        'classProfiles': to_records(class_profiles.rename(columns={'HWB_CLASS': 'bridgeClass'}), limit=12),
        'countyProfiles': to_records(county_profiles.rename(columns={'COUNTY_CODE_003': 'countyCode'}), limit=12),
        'featureRanges': feature_ranges,
        'sampleBridges': sample_bridge_rows(bridges_with_svi),
        'pipeline': [
            {'label': 'Bridge inventory', 'file': 'CA25.txt', 'output': 'Raw statewide NBI bridge inventory'},
            {'label': 'ShakeMap sampling', 'file': 'pga_mean.flt', 'output': 'pga_nbi_bridge.csv'},
            {'label': 'Fragility / EDR', 'file': 'bridges_with_edr.csv', 'output': 'Modal damage probabilities + EDR'},
            {'label': 'SVI scoring', 'file': 'bridges_with_svi.csv', 'output': 'April 2026 weighted intrinsic screening'},
            {'label': 'ML comparison', 'file': 'ml_hybrid_best_by_feature_set.csv', 'output': 'Bridge vulnerability vs event-damage framing'},
            {'label': 'Scenario scoring', 'file': 'future_scenario_summary.csv', 'output': 'Uniform PGA stress-test summaries'},
        ],
        'calibrationPoints': to_records(calibration, limit=240),
    }
    return summary


def compute_bridge_ml_metrics(repo_root: Path):
    df = pd.read_csv(repo_root / 'data' / 'processed' / 'bridge_ml_predictions.csv', low_memory=False)
    actual = df['Actual_EDR'].astype(float)
    pred = df['Predicted_EDR'].astype(float)
    residual = pred - actual
    rmse = float(((residual ** 2).mean()) ** 0.5)
    mae = float(residual.abs().mean())
    r2_num = float(((actual - pred) ** 2).sum())
    r2_den = float(((actual - actual.mean()) ** 2).sum())
    r2 = None if r2_den == 0 else 1 - (r2_num / r2_den)
    return {
        'rows': int(len(df)),
        'modelLabel': str(df['Best_Model'].mode().iloc[0]) if 'Best_Model' in df.columns else 'Bridge ML artifact',
        'mae': clean_value(mae),
        'rmse': clean_value(rmse),
        'r2': clean_value(r2),
    }


def export_csv_jsons(repo_root: Path, public_data_root: Path):
    processed_root = repo_root / 'data' / 'processed'
    for csv_name in CSV_EXPORTS:
        csv_path = processed_root / csv_name
        if not csv_path.exists():
            continue
        df = pd.read_csv(csv_path, low_memory=False)
        json_path = public_data_root / csv_name.replace('.csv', '.json')
        json_path.write_text(json.dumps(to_records(df), indent=2), encoding='utf-8')


def export_health(repo_root: Path, public_data_root: Path):
    metrics_path = repo_root / 'data' / 'processed' / 'ml_recommended_hybrid_metrics.csv'
    feature_path = repo_root / 'data' / 'processed' / 'ml_recommended_hybrid_feature_importance.csv'
    metrics_valid = False
    importance_valid = False
    metrics_rows = []
    importance_rows = []
    if metrics_path.exists():
        metrics_df = pd.read_csv(metrics_path, low_memory=False)
        metrics_rows = to_records(metrics_df)
        if not metrics_df.empty:
            row = metrics_df.iloc[0]
            rmse = float(row.get('RMSE', 0) or 0)
            r2 = float(row.get('R2', 0) or 0)
            metrics_valid = not (abs(rmse) < 1e-12 and abs(r2 - 1.0) < 1e-12)
    if feature_path.exists():
        feature_df = pd.read_csv(feature_path, low_memory=False)
        importance_rows = to_records(feature_df)
        importance_valid = bool((feature_df['Importance'].abs() > 1e-9).any()) if 'Importance' in feature_df.columns else False

    fallback_importance = [
        {'feature': 'Condition rating', 'importance': 0.24},
        {'feature': 'SVI score', 'importance': 0.18},
        {'feature': 'Year built / age', 'importance': 0.14},
        {'feature': 'Maximum span length', 'importance': 0.12},
        {'feature': 'Skew angle', 'importance': 0.10},
        {'feature': 'Bridge class', 'importance': 0.09},
        {'feature': 'Number of spans', 'importance': 0.07},
        {'feature': 'Reconstruction timing', 'importance': 0.06},
    ]

    health = {
        'recommendedMetricsValid': metrics_valid,
        'recommendedFeatureImportanceValid': importance_valid,
        'recommendedMetrics': metrics_rows,
        'recommendedFeatureImportance': importance_rows,
        'fallbackFeatureImportance': fallback_importance,
        'bridgeMlCalibrationMetrics': compute_bridge_ml_metrics(repo_root),
        'notes': {
            'metrics': 'The exporter marks recommended regression metrics as invalid when the current repo snapshot contains perfect zero-error rows, so the frontend can avoid presenting them as credible evidence.',
            'importance': 'The exporter falls back to domain-prior contribution weights when the recommended feature-importance file is degenerate or all-zero.',
        },
    }
    (public_data_root / 'data_health.json').write_text(json.dumps(health, indent=2), encoding='utf-8')


def export_proxy_validation(public_data_root: Path):
    proxy = {
        'subsetSize': 10255,
        'models': [
            {
                'label': 'Univariate (HAZUS)',
                'exactAccuracy': 0.6845,
                'withinOneStateAccuracy': 0.8016,
                'maeOrdinal': 0.7070,
                'weightedKappa': 0.0809,
                'macroF1': 0.2166,
                'underpredictionRate': 0.2599,
            },
            {
                'label': 'Hybrid Proxy Model',
                'exactAccuracy': 0.7426,
                'withinOneStateAccuracy': 0.8415,
                'maeOrdinal': 0.5787,
                'weightedKappa': 0.3548,
                'macroF1': 0.3899,
                'underpredictionRate': 0.2209,
            },
        ],
        'source': 'docs/PROXY_VALIDATION.md',
    }
    (public_data_root / 'proxy_validation.json').write_text(json.dumps(proxy, indent=2), encoding='utf-8')


def copy_research_figures(repo_root: Path, public_research_root: Path):
    figures_root = repo_root / 'figures'
    manifest = []
    for filename in RESEARCH_FIGURES:
        src = figures_root / filename
        if not src.exists():
            continue
        dst = public_research_root / filename
        shutil.copy2(src, dst)
        manifest.append(
            {
                'file': filename,
                'title': filename.replace('.png', '').replace('_', ' ').title(),
                'path': f'/research/{filename}',
            }
        )
    (public_research_root / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')


def main():
    repo_root = Path(__file__).resolve().parents[2]
    frontend_root = repo_root / 'frontend'
    public_data_root = frontend_root / 'public' / 'data'
    public_research_root = frontend_root / 'public' / 'research'
    public_data_root.mkdir(parents=True, exist_ok=True)
    public_research_root.mkdir(parents=True, exist_ok=True)

    summary = build_summary(repo_root)
    (public_data_root / 'site_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    export_csv_jsons(repo_root, public_data_root)
    export_health(repo_root, public_data_root)
    export_proxy_validation(public_data_root)
    copy_research_figures(repo_root, public_research_root)

    print('Exported frontend data to', public_data_root)
    print('Copied research figures to', public_research_root)


if __name__ == '__main__':
    main()
