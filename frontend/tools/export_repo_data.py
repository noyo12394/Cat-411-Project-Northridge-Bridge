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

PROTOTYPE_PRIORS = [
    {
        'key': 'condition',
        'label': 'Condition rating',
        'weight': 0.22,
        'group': 'condition',
        'rationale': 'Condition remains the clearest bridge-health signal in inspection-led vulnerability screening.',
    },
    {
        'key': 'svi',
        'label': 'SVI',
        'weight': 0.18,
        'group': 'intrinsic index',
        'rationale': 'The revised Seismic Vulnerability Index aggregates multiple structural vulnerability factors into one interpretable score.',
    },
    {
        'key': 'age',
        'label': 'Bridge age / design era',
        'weight': 0.15,
        'group': 'age / detailing',
        'rationale': 'Older bridges are more likely to reflect earlier seismic detailing assumptions and legacy configurations.',
    },
    {
        'key': 'rehab',
        'label': 'Reconstruction timing',
        'weight': 0.10,
        'group': 'maintenance history',
        'rationale': 'More recent reconstruction or rehabilitation generally reduces expected vulnerability relative to peers of similar age.',
    },
    {
        'key': 'skew',
        'label': 'Skew angle',
        'weight': 0.10,
        'group': 'geometry',
        'rationale': 'Skew is consistently treated as a meaningful irregularity driver in bridge seismic vulnerability and fragility studies.',
    },
    {
        'key': 'maxSpan',
        'label': 'Maximum span length',
        'weight': 0.10,
        'group': 'geometry',
        'rationale': 'Longer spans tend to imply greater demand concentration and more consequential structural response when detailing is weak.',
    },
    {
        'key': 'bridgeClass',
        'label': 'Bridge class / HWB class',
        'weight': 0.09,
        'group': 'system type',
        'rationale': 'Bridge class preserves important system-level fragility distinctions without directly importing hazard intensity into the intrinsic score.',
    },
    {
        'key': 'spans',
        'label': 'Number of spans',
        'weight': 0.06,
        'group': 'geometry',
        'rationale': 'More spans increase geometry complexity, support interaction, and the chance of uneven seismic demand distribution.',
    },
]

METHODOLOGY_REFERENCES = [
    {
        'title': 'Mangalathu et al. (2019) - Rapid seismic damage evaluation of bridges using machine learning techniques',
        'url': 'https://www.mainslab.net/_files/ugd/3ad6e3_f43d6856c0a1462db8afbeeb35dfe141.pdf',
        'note': 'Supports the use of bridge-specific structural features and ML for bridge seismic damage evaluation.',
    },
    {
        'title': 'Gorishniy et al. (2021) - Revisiting deep learning models for tabular data',
        'url': 'https://arxiv.org/abs/2106.11959',
        'note': 'Motivates strong tabular baselines and careful comparison across model families instead of assuming deep learning is always best.',
    },
    {
        'title': 'Shwartz-Ziv and Armon (2022) - Tabular data: Deep learning is not all you need',
        'url': 'https://www.sciencedirect.com/science/article/pii/S1566253521002360',
        'note': 'Supports the use of interpretable tree-based and boosted tabular models in engineering-data settings.',
    },
]

FRAGILITY_DAMAGE_WEIGHTS = {
    'P_DS0': 0.0,
    'P_DS1': 0.03,
    'P_DS2': 0.08,
    'P_DS3': 0.25,
    'P_DS4': 1.0,
}


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


def normalize(value, minimum, maximum):
    if value is None or pd.isna(value) or maximum <= minimum:
        return 0.0
    return max(0.0, min(1.0, (float(value) - float(minimum)) / (float(maximum) - float(minimum))))


def current_year():
    return 2026


def max_span_to_feet(series: pd.Series):
    return series.astype(float) * 3.28084


def risk_band_distribution(scores: pd.Series):
    bins = [0.0, 0.28, 0.46, 0.66, 0.82, 1.0]
    labels = ['Low', 'Guarded', 'Elevated', 'High', 'Critical']
    cats = pd.cut(scores.clip(lower=0, upper=1), bins=bins, labels=labels, include_lowest=True)
    return normalize_counts(cats.value_counts().reindex(labels, fill_value=0))


def score_to_band(score: float):
    if score < 0.28:
        return 'Low'
    if score < 0.46:
        return 'Guarded'
    if score < 0.66:
        return 'Elevated'
    if score < 0.82:
        return 'High'
    return 'Critical'


def county_label(code):
    if code is None or pd.isna(code):
        return 'County unknown'
    return f'County {int(code):03d}'


def normal_cdf(value: float):
    return 0.5 * (1 + math.erf(value / math.sqrt(2)))


def exceedance_probability(pga: float, theta: float | None, beta: float | None):
    if pga <= 0 or theta is None or beta is None:
        return 0.0
    if pd.isna(theta) or pd.isna(beta) or theta <= 0 or beta <= 0:
        return 0.0
    z_score = (math.log(pga) - math.log(theta)) / beta
    return max(0.0, min(1.0, normal_cdf(z_score)))


def build_class_profiles(df: pd.DataFrame):
    return (
        df.groupby('HWB_CLASS', dropna=False)
        .agg(count=('HWB_CLASS', 'size'), meanSVI=('SVI', 'mean'), meanEDR=('EDR', 'mean'))
        .reset_index()
        .sort_values('meanSVI', ascending=False)
    )


def compute_intrinsic_scores(df: pd.DataFrame, class_profiles: pd.DataFrame):
    class_mean_lookup = class_profiles.set_index('HWB_CLASS')['meanSVI'].to_dict()
    modal_mapping = {
        'P_DS0': 'None',
        'P_DS1': 'Slight',
        'P_DS2': 'Moderate',
        'P_DS3': 'Extensive',
        'P_DS4': 'Complete',
    }
    ds_cols = [col for col in ['P_DS0', 'P_DS1', 'P_DS2', 'P_DS3', 'P_DS4'] if col in df.columns]

    year_min = float(df['year'].min())
    recon_max = float(df['YEAR_RECONSTRUCTED_106'].dropna().max()) if df['YEAR_RECONSTRUCTED_106'].dropna().any() else current_year()
    spans_max = float(min(df['spans'].max(), 24))
    max_span_ft = max_span_to_feet(df['max_span'])
    max_span_ft_max = float(max_span_ft.quantile(0.98))
    skew_max = float(df['skew'].max())
    cond_min = float(df['cond'].min())
    cond_max = float(df['cond'].max())
    svi_min = float(df['SVI'].min())
    svi_max = float(df['SVI'].max())
    adt_log = df['ADT_029'].fillna(0).clip(lower=0).map(lambda x: math.log1p(float(x)))
    adt_max = float(adt_log.quantile(0.99)) if len(adt_log) else 1.0

    rows = []
    for row in df.itertuples(index=False):
        year_built = float(getattr(row, 'year'))
        year_recon = getattr(row, 'YEAR_RECONSTRUCTED_106')
        bridge_age = current_year() - year_built
        rehab_years = current_year() - float(year_recon) if year_recon and not pd.isna(year_recon) and float(year_recon) > 0 else bridge_age

        class_mean = class_mean_lookup.get(getattr(row, 'HWB_CLASS'), float(df['SVI'].mean()))
        components = {
            'condition': 1 - normalize(getattr(row, 'cond'), cond_min, cond_max),
            'svi': normalize(getattr(row, 'SVI'), svi_min, svi_max),
            'age': normalize(bridge_age, 0, current_year() - year_min),
            'rehab': normalize(rehab_years, 0, current_year() - recon_max if current_year() - recon_max > 0 else current_year() - year_min),
            'skew': normalize(getattr(row, 'skew'), 0, skew_max),
            'maxSpan': normalize(getattr(row, 'max_span') * 3.28084, 0, max_span_ft_max),
            'bridgeClass': normalize(class_mean, 0.25, 0.6),
            'spans': normalize(min(getattr(row, 'spans'), 24), 1, spans_max),
        }
        intrinsic_score = sum(
            prior['weight'] * components[prior['key']] for prior in PROTOTYPE_PRIORS
        )
        intrinsic_score = max(0.0, min(1.0, 0.08 + intrinsic_score))
        traffic_score = normalize(math.log1p(max(float(getattr(row, 'ADT_029') or 0), 0.0)), 0, adt_max)
        priority_score = max(0.0, min(1.0, intrinsic_score * 0.72 + traffic_score * 0.28))
        rows.append(
            {
                'structureNumber': clean_value(getattr(row, 'STRUCTURE_NUMBER_008')),
                'countyCode': clean_value(getattr(row, 'COUNTY_CODE_003')),
                'countyLabel': county_label(getattr(row, 'COUNTY_CODE_003')),
                'bridgeClass': clean_value(getattr(row, 'HWB_CLASS')),
                'yearBuilt': int(clean_value(year_built) or 0),
                'yearReconstructed': clean_value(year_recon),
                'spans': int(clean_value(getattr(row, 'spans')) or 0),
                'maxSpanFt': clean_value(getattr(row, 'max_span') * 3.28084),
                'maxSpanM': clean_value(getattr(row, 'max_span')),
                'skew': clean_value(getattr(row, 'skew')),
                'condition': clean_value(getattr(row, 'cond')),
                'svi': clean_value(getattr(row, 'SVI')),
                'edr': clean_value(getattr(row, 'EDR')),
                'adt': clean_value(getattr(row, 'ADT_029')),
                'latitude': clean_value(getattr(row, 'latitude')),
                'longitude': clean_value(getattr(row, 'longitude')),
                'pga': clean_value(getattr(row, 'pga')) if hasattr(row, 'pga') else None,
                'modalDamageState': (
                    modal_mapping[max(ds_cols, key=lambda col: float(getattr(row, col) or 0.0))]
                    if ds_cols
                    else None
                ),
                'prototypeVulnerability': round(intrinsic_score, 4),
                'priorityScore': round(priority_score, 4),
                'riskBand': score_to_band(intrinsic_score),
                'inspectionTier': 'Immediate review' if priority_score >= 0.78 else 'Priority review' if priority_score >= 0.6 else 'Routine review',
                'componentCondition': round(components['condition'], 4),
                'componentSVI': round(components['svi'], 4),
                'componentAge': round(components['age'], 4),
                'componentRehab': round(components['rehab'], 4),
                'componentSkew': round(components['skew'], 4),
                'componentMaxSpan': round(components['maxSpan'], 4),
                'componentBridgeClass': round(components['bridgeClass'], 4),
                'componentSpans': round(components['spans'], 4),
            }
        )

    return rows, {
        'yearBuilt': {'min': int(year_min), 'max': int(df['year'].max())},
        'yearReconstructed': {'min': int(df['YEAR_RECONSTRUCTED_106'].dropna().min()) if df['YEAR_RECONSTRUCTED_106'].dropna().any() else 0, 'max': int(recon_max)},
        'skew': {'min': 0, 'max': int(skew_max)},
        'spans': {'min': int(df['spans'].min()), 'max': int(df['spans'].max())},
        'maxSpan': {'min': clean_value(max_span_ft.min()), 'max': clean_value(max_span_ft_max)},
        'condition': {'min': int(cond_min), 'max': int(cond_max)},
        'svi': {'min': clean_value(svi_min), 'max': clean_value(svi_max)},
        'adt': {'min': 0, 'max': int(df['ADT_029'].fillna(0).quantile(0.99))},
    }


def build_hazard_profile(df: pd.DataFrame):
    hazard_df = df[df['pga'].notna()].copy()
    if hazard_df.empty:
        return {
            'sampledBridges': 0,
            'positivePgaBridges': 0,
            'quantiles': {'p50': 0.0, 'p75': 0.0, 'p90': 0.0, 'p95': 0.0, 'max': 0.0},
            'histogram': [],
            'countyHotspots': [],
            'samplePoints': [],
        }

    positive_df = hazard_df[hazard_df['pga'].astype(float) > 0].copy()
    pga_series = hazard_df['pga'].astype(float).clip(lower=0)
    upper = max(float(pga_series.max()), 0.35)
    bucket_count = 8
    edges = [round(upper * idx / bucket_count, 4) for idx in range(bucket_count + 1)]
    histogram = []
    for idx in range(bucket_count):
        start = edges[idx]
        end = edges[idx + 1]
        mask = (pga_series >= start) & (pga_series < end if idx < bucket_count - 1 else pga_series <= end)
        histogram.append(
            {
                'label': f'{start:.2f}-{end:.2f} g',
                'start': round(start, 4),
                'end': round(end, 4),
                'count': int(mask.sum()),
            }
        )

    county_hotspots = (
        hazard_df.groupby('COUNTY_CODE_003', dropna=False)
        .agg(
            bridgeCount=('COUNTY_CODE_003', 'size'),
            meanPga=('pga', 'mean'),
            maxPga=('pga', 'max'),
            meanEdr=('EDR', 'mean'),
        )
        .reset_index()
        .sort_values(['maxPga', 'meanEdr', 'bridgeCount'], ascending=[False, False, False])
        .head(12)
    )
    county_hotspots['countyLabel'] = county_hotspots['COUNTY_CODE_003'].map(county_label)

    map_sample = hazard_df.sort_values(['pga', 'EDR'], ascending=[False, False]).head(320)
    sample_points = [
        {
            'structureNumber': clean_value(row.STRUCTURE_NUMBER_008),
            'latitude': clean_value(row.latitude),
            'longitude': clean_value(row.longitude),
            'countyLabel': county_label(row.COUNTY_CODE_003),
            'pga': clean_value(row.pga),
            'edr': clean_value(row.EDR),
            'svi': clean_value(row.SVI),
        }
        for row in map_sample.itertuples(index=False)
        if not pd.isna(row.latitude) and not pd.isna(row.longitude)
    ]

    return {
        'sampledBridges': int(len(hazard_df)),
        'positivePgaBridges': int(len(positive_df)),
        'quantiles': {
            'p50': clean_value(pga_series.quantile(0.5)),
            'p75': clean_value(pga_series.quantile(0.75)),
            'p90': clean_value(pga_series.quantile(0.9)),
            'p95': clean_value(pga_series.quantile(0.95)),
            'max': clean_value(pga_series.max()),
        },
        'histogram': histogram,
        'countyHotspots': to_records(
            county_hotspots[['countyLabel', 'bridgeCount', 'meanPga', 'maxPga', 'meanEdr']]
        ),
        'samplePoints': sample_points,
    }


def build_fragility_profile(df: pd.DataFrame):
    ds_cols = ['P_DS0', 'P_DS1', 'P_DS2', 'P_DS3', 'P_DS4']
    available_ds_cols = [col for col in ds_cols if col in df.columns]
    if not available_ds_cols:
        return {
            'overallDamageProbabilities': [],
            'damageByClass': [],
            'fragilityCurves': [],
        }

    state_labels = {
        'P_DS0': 'None',
        'P_DS1': 'Slight',
        'P_DS2': 'Moderate',
        'P_DS3': 'Extensive',
        'P_DS4': 'Complete',
    }
    overall_damage_probabilities = [
        {
            'state': state_labels[col],
            'probability': clean_value(df[col].astype(float).mean()),
        }
        for col in available_ds_cols
    ]

    damage_by_class = (
        df.groupby('HWB_CLASS', dropna=False)
        .agg(
            count=('HWB_CLASS', 'size'),
            meanPga=('pga', 'mean'),
            meanEdr=('EDR', 'mean'),
            ds0=('P_DS0', 'mean'),
            ds1=('P_DS1', 'mean'),
            ds2=('P_DS2', 'mean'),
            ds3=('P_DS3', 'mean'),
            ds4=('P_DS4', 'mean'),
        )
        .reset_index()
        .rename(columns={'HWB_CLASS': 'bridgeClass'})
        .sort_values(['meanEdr', 'count'], ascending=[False, False])
        .head(12)
    )

    valid_df = df[
        df[['SVI', 'BETA_SVI', 'MU_DS1_LINEAR', 'MU_DS2_LINEAR', 'MU_DS3_LINEAR', 'MU_DS4_LINEAR']]
        .notna()
        .all(axis=1)
    ].copy()
    quantiles = [('Lower vulnerability', 0.2), ('Median vulnerability', 0.5), ('Higher vulnerability', 0.8)]
    pga_values = [round(0.45 * idx / 12, 4) for idx in range(13)]
    fragility_curves = []
    if not valid_df.empty:
        sorted_df = valid_df.sort_values('SVI').reset_index(drop=True)
        for label, quantile in quantiles:
            index = min(len(sorted_df) - 1, max(0, int(quantile * (len(sorted_df) - 1))))
            center_svi = float(sorted_df.iloc[index]['SVI'])
            window = sorted_df[(sorted_df['SVI'] - center_svi).abs() <= 0.03]
            if len(window) < 40:
                start = max(0, index - 80)
                end = min(len(sorted_df), index + 81)
                window = sorted_df.iloc[start:end]
            theta = {
                'ds1': float(window['MU_DS1_LINEAR'].mean()),
                'ds2': float(window['MU_DS2_LINEAR'].mean()),
                'ds3': float(window['MU_DS3_LINEAR'].mean()),
                'ds4': float(window['MU_DS4_LINEAR'].mean()),
            }
            beta = float(window['BETA_SVI'].mean())
            points = []
            for pga in pga_values:
                ex1 = exceedance_probability(pga, theta['ds1'], beta)
                ex2 = exceedance_probability(pga, theta['ds2'], beta)
                ex3 = exceedance_probability(pga, theta['ds3'], beta)
                ex4 = exceedance_probability(pga, theta['ds4'], beta)
                state_probabilities = {
                    'P_DS0': max(0.0, min(1.0, 1 - ex1)),
                    'P_DS1': max(0.0, min(1.0, ex1 - ex2)),
                    'P_DS2': max(0.0, min(1.0, ex2 - ex3)),
                    'P_DS3': max(0.0, min(1.0, ex3 - ex4)),
                    'P_DS4': max(0.0, min(1.0, ex4)),
                }
                edr = sum(
                    FRAGILITY_DAMAGE_WEIGHTS[state] * probability
                    for state, probability in state_probabilities.items()
                )
                points.append(
                    {
                        'pga': round(pga, 4),
                        'ds1': round(ex1, 6),
                        'ds2': round(ex2, 6),
                        'ds3': round(ex3, 6),
                        'ds4': round(ex4, 6),
                        'edr': round(edr, 6),
                    }
                )
            fragility_curves.append(
                {
                    'label': label,
                    'meanSvi': clean_value(window['SVI'].mean()),
                    'beta': clean_value(beta),
                    'points': points,
                }
            )

    return {
        'overallDamageProbabilities': overall_damage_probabilities,
        'damageByClass': to_records(damage_by_class),
        'fragilityCurves': fragility_curves,
    }


def sample_bridge_rows(portfolio_rows):
    picks = []
    labelled_quantiles = [('Portfolio Lower Risk', 0.15), ('Portfolio Mid Risk', 0.5), ('Portfolio Higher Risk', 0.85)]
    ranked = sorted(portfolio_rows, key=lambda row: row['prototypeVulnerability'])
    for label, q in labelled_quantiles:
        idx = min(len(ranked) - 1, max(0, int(q * (len(ranked) - 1))))
        row = ranked[idx]
        picks.append(
            {
                'label': label,
                'structureNumber': row['structureNumber'],
                'countyCode': row['countyCode'],
                'countyLabel': row['countyLabel'],
                'yearBuilt': row['yearBuilt'],
                'yearReconstructed': row['yearReconstructed'],
                'spans': row['spans'],
                'maxSpan': row['maxSpanFt'],
                'skew': row['skew'],
                'condition': row['condition'],
                'svi': row['svi'],
                'bridgeClass': row['bridgeClass'],
                'adt': row['adt'],
                'prototypeVulnerability': row['prototypeVulnerability'],
                'priorityScore': row['priorityScore'],
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

    class_profiles = build_class_profiles(bridges_with_edr)
    county_profiles = (
        bridges_with_edr.groupby('COUNTY_CODE_003', dropna=False)
        .agg(count=('COUNTY_CODE_003', 'size'), meanSVI=('SVI', 'mean'), meanEDR=('EDR', 'mean'))
        .reset_index()
        .sort_values(['count', 'meanSVI'], ascending=[False, False])
        .head(12)
    )

    portfolio_rows, feature_ranges = compute_intrinsic_scores(bridges_with_edr, class_profiles)
    portfolio_df = pd.DataFrame(portfolio_rows)
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
            'meanPrototypeVulnerability': clean_value(portfolio_df['prototypeVulnerability'].mean()),
            'meanPriorityScore': clean_value(portfolio_df['priorityScore'].mean()),
            'sviRiskBands': risk_band_distribution(bridges_with_svi['SVI']),
            'prototypeRiskBands': risk_band_distribution(portfolio_df['prototypeVulnerability']),
            'modalDamageStates': normalize_counts(modal_damage.value_counts()),
        },
        'classProfiles': to_records(class_profiles.rename(columns={'HWB_CLASS': 'bridgeClass'}), limit=12),
        'countyProfiles': to_records(county_profiles.rename(columns={'COUNTY_CODE_003': 'countyCode'}), limit=12),
        'featureRanges': feature_ranges,
        'sampleBridges': sample_bridge_rows(portfolio_rows),
        'pipeline': [
            {'label': 'Bridge inventory', 'file': 'CA25.txt', 'output': 'Raw statewide NBI bridge inventory'},
            {'label': 'ShakeMap sampling', 'file': 'pga_mean.flt', 'output': 'pga_nbi_bridge.csv'},
            {'label': 'Fragility / EDR', 'file': 'bridges_with_edr.csv', 'output': 'Modal damage probabilities + EDR'},
            {'label': 'SVI scoring', 'file': 'bridges_with_svi.csv', 'output': 'Updated intrinsic screening and revised fragility medians'},
            {'label': 'ML comparison', 'file': 'ml_hybrid_best_by_feature_set.csv', 'output': 'Bridge vulnerability vs event-damage framing'},
            {'label': 'Scenario scoring', 'file': 'future_scenario_summary.csv', 'output': 'Uniform PGA stress-test summaries'},
        ],
        'calibrationPoints': to_records(calibration, limit=240),
    }
    return summary, portfolio_rows


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
        {'feature': 'Condition rating', 'importance': 0.22},
        {'feature': 'SVI', 'importance': 0.18},
        {'feature': 'Bridge age / design era', 'importance': 0.15},
        {'feature': 'Reconstruction timing', 'importance': 0.10},
        {'feature': 'Skew angle', 'importance': 0.10},
        {'feature': 'Maximum span length', 'importance': 0.10},
        {'feature': 'Bridge class / HWB class', 'importance': 0.09},
        {'feature': 'Number of spans', 'importance': 0.06},
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
            'importance': 'The exporter falls back to literature-informed prototype priors when the recommended feature-importance file is degenerate or all-zero.',
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


def export_methodology(public_data_root: Path):
    methodology = {
        'status': 'research-prototype',
        'engineLabel': 'Literature-informed prototype vulnerability engine',
        'discipline': {
            'core': 'No PGA in the intrinsic vulnerability score.',
            'event': 'PGA is introduced only in event-damage scenario mode.',
            'priority': 'ADT changes prioritization and consequence, not structural vulnerability.',
            'ndvi': 'NDVI remains an optional contextual modifier rather than a structural core driver.',
        },
        'priors': PROTOTYPE_PRIORS,
        'layers': [
            {'label': 'Structural / age / geometry inputs', 'description': 'Year built, rehab timing, spans, max span, skew, bridge class, condition, and SVI.'},
            {'label': 'Normalized vulnerability indicators', 'description': 'Bridge-specific variables are normalized into interpretable intrinsic vulnerability components.'},
            {'label': 'Prototype vulnerability score', 'description': 'A transparent research prior layer combines those indicators without using PGA.'},
            {'label': 'Consequence and prioritization', 'description': 'ADT and optional NDVI adjustments appear later in inspection prioritization rather than baseline vulnerability.'},
        ],
        'references': METHODOLOGY_REFERENCES,
    }
    (public_data_root / 'methodology_priors.json').write_text(json.dumps(methodology, indent=2), encoding='utf-8')


def export_bridge_portfolio(public_data_root: Path, portfolio_rows):
    (public_data_root / 'bridge_portfolio.json').write_text(json.dumps(portfolio_rows, indent=2), encoding='utf-8')


def export_hazard_and_fragility(repo_root: Path, public_data_root: Path):
    bridges_with_edr = pd.read_csv(
        repo_root / 'data' / 'processed' / 'bridges_with_edr.csv',
        low_memory=False,
    )
    hazard_profile = build_hazard_profile(bridges_with_edr)
    fragility_profile = build_fragility_profile(bridges_with_edr)
    (public_data_root / 'hazard_profile.json').write_text(
        json.dumps(hazard_profile, indent=2),
        encoding='utf-8',
    )
    (public_data_root / 'fragility_profile.json').write_text(
        json.dumps(fragility_profile, indent=2),
        encoding='utf-8',
    )


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

    summary, portfolio_rows = build_summary(repo_root)
    (public_data_root / 'site_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    export_bridge_portfolio(public_data_root, portfolio_rows)
    export_methodology(public_data_root)
    export_csv_jsons(repo_root, public_data_root)
    export_health(repo_root, public_data_root)
    export_proxy_validation(public_data_root)
    export_hazard_and_fragility(repo_root, public_data_root)
    copy_research_figures(repo_root, public_research_root)

    print('Exported frontend data to', public_data_root)
    print('Copied research figures to', public_research_root)


if __name__ == '__main__':
    main()
