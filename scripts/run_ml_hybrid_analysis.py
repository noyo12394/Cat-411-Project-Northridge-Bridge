from pathlib import Path
import sys
import warnings

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from runtime_checks import ensure_packages, ensure_supported_runtime

ensure_supported_runtime()
ensure_packages([
    'numpy', 'pandas', 'matplotlib', 'scipy', 'sklearn', 'seaborn'
])

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from scipy.stats import norm
from sklearn.base import clone
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.feature_selection import mutual_info_regression
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import ElasticNet
from sklearn.metrics import (
    make_scorer,
    mean_absolute_error,
    mean_squared_error,
    median_absolute_error,
    r2_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.exceptions import ConvergenceWarning

from project_paths import build_paths, require_paths

sns.set_theme(style='whitegrid')
warnings.filterwarnings('ignore', category=ConvergenceWarning)

RANDOM_STATE = 42
REFERENCE_YEAR = 2025
TARGET = 'EDR'
RECOMMENDED_FEATURE_SET = 'Bridge Vulnerability Structural'
BENCHMARK_FEATURE_SET = 'HAZUS Benchmark'
CATEGORICAL_FEATURES = {'HWB_CLASS', 'design_era_1989', 'functional_class_cat', 'kind', 'type'}

FEATURE_SETS = {
    'HAZUS Benchmark': ['pga', 'HWB_CLASS'],
    'Bridge Vulnerability Compact': [
        'SVI', 'design_era_1989', 'age_years', 'time_since_rehab', 'reconstructed_flag',
        'spans', 'max_span_log1p', 'skew', 'cond',
    ],
    'Bridge Vulnerability Structural': [
        'HWB_CLASS', 'design_era_1989', 'age_years', 'time_since_rehab', 'reconstructed_flag',
        'spans', 'max_span_log1p', 'skew', 'cond', 'deck_area_log1p',
        'operating_rating',
    ],
    'Event Damage Hybrid': [
        'pga', 'HWB_CLASS', 'design_era_1989', 'age_years', 'time_since_rehab',
        'reconstructed_flag', 'spans', 'max_span_log1p', 'skew', 'cond',
        'deck_area_log1p', 'operating_rating',
    ],
}

FEATURE_SET_DESCRIPTIONS = {
    'HAZUS Benchmark': 'Minimal hazard-only benchmark using PGA and HAZUS bridge class.',
    'Bridge Vulnerability Compact': 'Compact no-PGA vulnerability framing using SVI and the core age / geometry / condition variables.',
    'Bridge Vulnerability Structural': 'Pure bridge-intrinsic structural vulnerability model with no PGA and no traffic / network consequence variables.',
    'Event Damage Hybrid': 'Event-damage model that combines shaking demand with the bridge-intrinsic structural variables.',
}

FEATURE_MANIFEST = [
    ('pga', 'Hazard demand', 'Peak ground acceleration at the bridge site; direct shaking demand.'),
    ('HWB_CLASS', 'HAZUS classification', 'Bridge fragility family assigned from structure type and era logic.'),
    ('SVI', 'Composite vulnerability', 'Seismic Vulnerability Index carried over from the engineering scoring workflow.'),
    ('design_era_1989', 'Design era', 'Categorical design-era feature that separates older bridges from post-1989 design practice.'),
    ('age_years', 'Age', 'Bridge age in years relative to 2025.'),
    ('time_since_rehab', 'Rehabilitation timing', 'Years since the last recorded reconstruction; falls back to bridge age if never reconstructed.'),
    ('reconstructed_flag', 'Rehabilitation indicator', 'Binary flag indicating whether a bridge has a recorded reconstruction year.'),
    ('spans', 'Geometry', 'Number of main unit spans.'),
    ('max_span_log1p', 'Geometry', 'Log-transformed maximum span length to tame the extreme right tail.'),
    ('skew', 'Geometry', 'Skew angle in degrees.'),
    ('cond', 'Condition', 'Lowest available bridge condition rating proxy.'),
    ('deck_area_log1p', 'Scale', 'Log-transformed deck area as a size / exposure proxy.'),
    ('operating_rating', 'Capacity / condition', 'Operating rating from the inventory.'),
]

LITERATURE = [
    (
        'Shwartz-Ziv and Armon (2022)',
        'Tabular data: Deep learning is not all you need',
        'https://www.sciencedirect.com/science/article/pii/S1566253521002360',
    ),
    (
        'Gorishniy et al. (2021)',
        'Revisiting Deep Learning Models for Tabular Data',
        'https://research.yandex.com/publications/revisiting-deep-learning-models-for-tabular-data',
    ),
    (
        'Mangalathu et al. (2019)',
        'Rapid seismic damage evaluation of bridge portfolios using machine learning techniques',
        'https://www.sciencedirect.com/science/article/pii/S0141029619328068',
    ),
    (
        'Luo et al. (2025)',
        'Post-earthquake functionality and resilience prediction of bridge networks based on data-driven machine learning method',
        'https://www.sciencedirect.com/science/article/abs/pii/S0267726124006791',
    ),
    (
        'scikit-learn docs',
        'TransformedTargetRegressor',
        'https://scikit-learn.org/1.5/modules/generated/sklearn.compose.TransformedTargetRegressor.html',
    ),
    (
        'scikit-learn docs',
        'HistGradientBoostingRegressor',
        'https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html',
    ),
    (
        'scikit-learn docs',
        'MLPRegressor',
        'https://scikit-learn.org/stable/modules/generated/sklearn.neural_network.MLPRegressor.html',
    ),
]

FRAG = {
    'HWB1': {'slight': (0.25, 0.6), 'moderate': (0.50, 0.6), 'extensive': (0.90, 0.6), 'complete': (1.20, 0.6)},
    'HWB2': {'slight': (0.20, 0.6), 'moderate': (0.40, 0.6), 'extensive': (0.80, 0.6), 'complete': (1.10, 0.6)},
    'HWB3': {'slight': (0.18, 0.6), 'moderate': (0.35, 0.6), 'extensive': (0.70, 0.6), 'complete': (1.00, 0.6)},
    'HWB4': {'slight': (0.15, 0.6), 'moderate': (0.30, 0.6), 'extensive': (0.60, 0.6), 'complete': (0.90, 0.6)},
    'HWB5': {'slight': (0.22, 0.6), 'moderate': (0.45, 0.6), 'extensive': (0.85, 0.6), 'complete': (1.15, 0.6)},
    'HWB6': {'slight': (0.18, 0.6), 'moderate': (0.36, 0.6), 'extensive': (0.72, 0.6), 'complete': (1.00, 0.6)},
    'HWB7': {'slight': (0.30, 0.6), 'moderate': (0.60, 0.6), 'extensive': (1.00, 0.6), 'complete': (1.30, 0.6)},
    'HWB8': {'slight': (0.24, 0.6), 'moderate': (0.48, 0.6), 'extensive': (0.90, 0.6), 'complete': (1.20, 0.6)},
    'HWB9': {'slight': (0.20, 0.6), 'moderate': (0.40, 0.6), 'extensive': (0.80, 0.6), 'complete': (1.10, 0.6)},
    'HWB10': {'slight': (0.16, 0.6), 'moderate': (0.32, 0.6), 'extensive': (0.64, 0.6), 'complete': (0.95, 0.6)},
    'HWB11': {'slight': (0.21, 0.6), 'moderate': (0.42, 0.6), 'extensive': (0.82, 0.6), 'complete': (1.12, 0.6)},
    'HWB12': {'slight': (0.19, 0.6), 'moderate': (0.38, 0.6), 'extensive': (0.76, 0.6), 'complete': (1.05, 0.6)},
    'HWB13': {'slight': (0.23, 0.6), 'moderate': (0.46, 0.6), 'extensive': (0.88, 0.6), 'complete': (1.18, 0.6)},
    'HWB14': {'slight': (0.18, 0.6), 'moderate': (0.36, 0.6), 'extensive': (0.70, 0.6), 'complete': (1.00, 0.6)},
    'HWB15': {'slight': (0.14, 0.6), 'moderate': (0.28, 0.6), 'extensive': (0.56, 0.6), 'complete': (0.85, 0.6)},
    'HWB16': {'slight': (0.17, 0.6), 'moderate': (0.34, 0.6), 'extensive': (0.68, 0.6), 'complete': (0.98, 0.6)},
    'HWB17': {'slight': (0.20, 0.6), 'moderate': (0.40, 0.6), 'extensive': (0.80, 0.6), 'complete': (1.10, 0.6)},
    'HWB18': {'slight': (0.22, 0.6), 'moderate': (0.44, 0.6), 'extensive': (0.84, 0.6), 'complete': (1.14, 0.6)},
    'HWB19': {'slight': (0.18, 0.6), 'moderate': (0.36, 0.6), 'extensive': (0.72, 0.6), 'complete': (1.02, 0.6)},
    'HWB20': {'slight': (0.16, 0.6), 'moderate': (0.32, 0.6), 'extensive': (0.64, 0.6), 'complete': (0.94, 0.6)},
    'HWB21': {'slight': (0.24, 0.6), 'moderate': (0.48, 0.6), 'extensive': (0.90, 0.6), 'complete': (1.20, 0.6)},
    'HWB22': {'slight': (0.20, 0.6), 'moderate': (0.40, 0.6), 'extensive': (0.80, 0.6), 'complete': (1.10, 0.6)},
    'HWB23': {'slight': (0.15, 0.6), 'moderate': (0.30, 0.6), 'extensive': (0.60, 0.6), 'complete': (0.90, 0.6)},
    'HWB24': {'slight': (0.19, 0.6), 'moderate': (0.38, 0.6), 'extensive': (0.76, 0.6), 'complete': (1.06, 0.6)},
    'HWB25': {'slight': (0.22, 0.6), 'moderate': (0.44, 0.6), 'extensive': (0.86, 0.6), 'complete': (1.16, 0.6)},
    'HWB26': {'slight': (0.17, 0.6), 'moderate': (0.34, 0.6), 'extensive': (0.68, 0.6), 'complete': (0.98, 0.6)},
    'HWB27': {'slight': (0.21, 0.6), 'moderate': (0.42, 0.6), 'extensive': (0.82, 0.6), 'complete': (1.12, 0.6)},
    'HWB28': {'slight': (0.20, 0.6), 'moderate': (0.40, 0.6), 'extensive': (0.80, 0.6), 'complete': (1.10, 0.6)},
}

DAMAGE_WEIGHTS = {
    'P_DS0': 0.00,
    'P_DS1': 0.03,
    'P_DS2': 0.08,
    'P_DS3': 0.25,
    'P_DS4': 1.00,
}


def clean_int_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors='coerce')


def clean_float_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors='coerce')


def extract_year(series: pd.Series) -> pd.Series:
    return (
        series.astype(str)
        .str.extract(r'(\d{4})')[0]
        .pipe(pd.to_numeric, errors='coerce')
    )


def minmax_scale(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors='coerce')
    valid = numeric.dropna()
    if valid.empty:
        return pd.Series(np.nan, index=series.index)
    lo = valid.min()
    hi = valid.max()
    if hi == lo:
        return pd.Series(0.0, index=series.index)
    return (numeric - lo) / (hi - lo)


def design_era_from_year(year: float) -> str:
    if pd.isna(year):
        return 'Unknown'
    if year < 1975:
        return 'Pre-1975'
    if year <= 1989:
        return '1975-1989'
    return '1990+'


def assign_hwb_class(row: pd.Series) -> str:
    year = row['year']
    kind = row['kind']
    spans = row['spans']
    max_span = row['max_span']

    if pd.isna(year):
        return 'HWB28'
    if kind == '1':
        return 'HWB1' if year >= 1975 else 'HWB2'
    if kind in ['2', '3']:
        if spans == 1:
            return 'HWB3' if pd.notna(max_span) and max_span >= 45 else 'HWB4'
        return 'HWB5' if year >= 1975 else 'HWB6'
    if kind in ['4', '5']:
        return 'HWB7' if year >= 1975 else 'HWB8'
    if kind in ['6', '7']:
        return 'HWB9' if pd.notna(max_span) and max_span >= 45 else 'HWB10'
    if kind == '8':
        return 'HWB11'
    if kind == '9':
        return 'HWB12'
    if kind == '10':
        return 'HWB13'
    if kind == '11':
        return 'HWB14'
    if kind == '12':
        return 'HWB15'
    if kind == '13':
        return 'HWB16'
    if kind == '14':
        return 'HWB17'
    if kind == '15':
        return 'HWB18'
    if kind == '16':
        return 'HWB19'
    if kind == '17':
        return 'HWB20'
    if kind == '18':
        return 'HWB21'
    if kind == '19':
        return 'HWB22'
    if kind == '20':
        return 'HWB23'
    if kind == '21':
        return 'HWB24'
    if kind == '22':
        return 'HWB25'
    if kind == '23':
        return 'HWB26'
    if kind == '24':
        return 'HWB27'
    return 'HWB28'


def exceed_prob(pga: float, median: float, beta: float) -> float:
    if pd.isna(pga) or pga <= 0 or pd.isna(median) or pd.isna(beta):
        return 0.0
    z = (np.log(pga) - np.log(median)) / beta
    return float(norm.cdf(z))


def compute_damage_probs(row: pd.Series) -> pd.Series:
    hwb = row['HWB_CLASS']
    pga = row['pga']
    if hwb not in FRAG or pd.isna(pga) or pga <= 0:
        return pd.Series([1.0, 0.0, 0.0, 0.0, 0.0])

    frag = FRAG[hwb]
    pe_slight = exceed_prob(pga, frag['slight'][0], frag['slight'][1])
    pe_moderate = exceed_prob(pga, frag['moderate'][0], frag['moderate'][1])
    pe_extensive = exceed_prob(pga, frag['extensive'][0], frag['extensive'][1])
    pe_complete = exceed_prob(pga, frag['complete'][0], frag['complete'][1])

    p_ds0 = max(0.0, 1.0 - pe_slight)
    p_ds1 = max(0.0, pe_slight - pe_moderate)
    p_ds2 = max(0.0, pe_moderate - pe_extensive)
    p_ds3 = max(0.0, pe_extensive - pe_complete)
    p_ds4 = max(0.0, pe_complete)

    total = p_ds0 + p_ds1 + p_ds2 + p_ds3 + p_ds4
    if total <= 0:
        return pd.Series([1.0, 0.0, 0.0, 0.0, 0.0])
    return pd.Series([p_ds0 / total, p_ds1 / total, p_ds2 / total, p_ds3 / total, p_ds4 / total])


def compute_svi(df: pd.DataFrame) -> pd.DataFrame:
    score_year = minmax_scale(REFERENCE_YEAR - df['year'])
    recon_base = (REFERENCE_YEAR - df['yr_recon']).fillna(REFERENCE_YEAR - df['year'])
    score_recon = minmax_scale(recon_base)
    score_skew = minmax_scale(df['skew'])
    score_spans = minmax_scale(df['spans'])
    score_max_span = minmax_scale(df['max_span'])
    score_cond = minmax_scale(9 - df['cond'])

    svi_raw = (
        0.20 * score_year.fillna(score_year.median()) +
        0.10 * score_recon.fillna(score_recon.median()) +
        0.15 * score_skew.fillna(score_skew.median()) +
        0.10 * score_spans.fillna(score_spans.median()) +
        0.15 * score_max_span.fillna(score_max_span.median()) +
        0.30 * score_cond.fillna(score_cond.median())
    )

    df['score_year'] = score_year
    df['score_recon'] = score_recon
    df['score_skew'] = score_skew
    df['score_spans'] = score_spans
    df['score_max_span'] = score_max_span
    df['score_cond'] = score_cond
    df['SVI_RAW'] = svi_raw
    df['SVI'] = minmax_scale(svi_raw)
    return df


def table_to_markdown(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = [
        '| ' + ' | '.join(cols) + ' |',
        '| ' + ' | '.join(['---'] * len(cols)) + ' |',
    ]
    for _, row in df.iterrows():
        values = []
        for col in cols:
            val = row[col]
            if isinstance(val, float):
                values.append(f'{val:.6f}')
            else:
                values.append(str(val))
        lines.append('| ' + ' | '.join(values) + ' |')
    return '\n'.join(lines)


def rmse_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_pred = np.clip(y_pred, 0, None)
    return float(np.sqrt(mean_squared_error(y_true, y_pred)))


def rmsle_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    y_true = np.clip(y_true, 0, None)
    y_pred = np.clip(y_pred, 0, None)
    return float(np.sqrt(np.mean((np.log1p(y_true) - np.log1p(y_pred)) ** 2)))


def mae_score(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(mean_absolute_error(y_true, np.clip(y_pred, 0, None)))


def r2_nonnegative(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(r2_score(y_true, np.clip(y_pred, 0, None)))


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    y_pred = np.clip(y_pred, 0, None)
    metrics = {
        'MAE': mean_absolute_error(y_true, y_pred),
        'RMSE': rmse_score(y_true, y_pred),
        'RMSLE': rmsle_score(y_true, y_pred),
        'MedianAE': median_absolute_error(y_true, y_pred),
        'R2': r2_score(y_true, y_pred),
    }
    positive_mask = y_true > 0
    if positive_mask.any():
        yp = y_pred[positive_mask]
        yt = y_true[positive_mask]
        metrics.update({
            'MAE_Positive': mean_absolute_error(yt, yp),
            'RMSE_Positive': rmse_score(yt, yp),
            'RMSLE_Positive': rmsle_score(yt, yp),
            'R2_Positive': r2_score(yt, yp) if positive_mask.sum() > 1 else np.nan,
        })
    else:
        metrics.update({
            'MAE_Positive': np.nan,
            'RMSE_Positive': np.nan,
            'RMSLE_Positive': np.nan,
            'R2_Positive': np.nan,
        })
    return metrics


def make_preprocessor(features: list[str]) -> ColumnTransformer:
    numeric_features = [feature for feature in features if feature not in CATEGORICAL_FEATURES]
    categorical_features = [feature for feature in features if feature in CATEGORICAL_FEATURES]

    numeric_pipe = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
    ])
    categorical_pipe = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
    ])
    return ColumnTransformer(
        transformers=[
            ('num', numeric_pipe, numeric_features),
            ('cat', categorical_pipe, categorical_features),
        ],
        remainder='drop',
        sparse_threshold=0,
    )


def wrap_target_transform(pipeline: Pipeline, log_target: bool = True):
    if not log_target:
        return pipeline
    return TransformedTargetRegressor(
        regressor=pipeline,
        func=np.log1p,
        inverse_func=np.expm1,
        check_inverse=False,
    )


def make_models(preprocessor: ColumnTransformer, log_target: bool = True) -> dict:
    models = {
        'Elastic Net': Pipeline([
            ('prep', clone(preprocessor)),
            ('model', ElasticNet(
                alpha=5e-4,
                l1_ratio=0.25,
                random_state=RANDOM_STATE,
                max_iter=12000,
            )),
        ]),
        'Random Forest': Pipeline([
            ('prep', clone(preprocessor)),
            ('model', RandomForestRegressor(
                n_estimators=150,
                min_samples_leaf=2,
                max_features='sqrt',
                n_jobs=-1,
                random_state=RANDOM_STATE,
            )),
        ]),
        'Extra Trees': Pipeline([
            ('prep', clone(preprocessor)),
            ('model', ExtraTreesRegressor(
                n_estimators=180,
                min_samples_leaf=1,
                max_features='sqrt',
                n_jobs=-1,
                random_state=RANDOM_STATE,
            )),
        ]),
        'HistGradientBoosting': Pipeline([
            ('prep', clone(preprocessor)),
            ('model', HistGradientBoostingRegressor(
                learning_rate=0.04,
                max_iter=180,
                max_leaf_nodes=31,
                min_samples_leaf=20,
                l2_regularization=0.05,
                random_state=RANDOM_STATE,
            )),
        ]),
        'MLPRegressor': Pipeline([
            ('prep', clone(preprocessor)),
            ('model', MLPRegressor(
                hidden_layer_sizes=(64, 32),
                alpha=1e-4,
                learning_rate_init=0.001,
                early_stopping=True,
                validation_fraction=0.1,
                max_iter=250,
                random_state=RANDOM_STATE,
            )),
        ]),
    }
    return {name: wrap_target_transform(model, log_target=log_target) for name, model in models.items()}


def load_statewide_bridge_dataset(paths: dict) -> pd.DataFrame:
    require_paths(paths, ['PGA_BRIDGE_CSV'])
    df = pd.read_csv(paths['PGA_BRIDGE_CSV'], low_memory=False)

    df['year'] = clean_int_series(df['YEAR_BUILT_027'])
    df['yr_recon'] = extract_year(df['YEAR_RECONSTRUCTED_106'])
    df['spans'] = clean_int_series(df['MAIN_UNIT_SPANS_045'])
    df['max_span'] = clean_float_series(df['MAX_SPAN_LEN_MT_048']).clip(lower=0)
    df['skew'] = clean_float_series(df['DEGREES_SKEW_034']).clip(lower=0)
    df['cond'] = clean_float_series(df['LOWEST_RATING'])
    df['pga'] = clean_float_series(df['pga']).fillna(0.0).clip(lower=0)
    df['adt_raw'] = clean_float_series(df['ADT_029']).fillna(0)
    df['truck_pct'] = clean_float_series(df['PERCENT_ADT_TRUCK_109']).fillna(0).clip(lower=0)
    df['deck_area'] = clean_float_series(df['DECK_AREA']).fillna(0).clip(lower=0)
    df['operating_rating'] = clean_float_series(df['OPERATING_RATING_064'])
    df['detour_km'] = clean_float_series(df['DETOUR_KILOS_019']).fillna(0).clip(lower=0)
    df['lanes_on'] = clean_int_series(df['TRAFFIC_LANES_ON_028A']).fillna(0)
    df['kind'] = df['STRUCTURE_KIND_043A'].astype(str).str.strip().replace({'': 'Unknown', 'nan': 'Unknown'})
    df['type'] = df['STRUCTURE_TYPE_043B'].astype(str).str.strip().replace({'': 'Unknown', 'nan': 'Unknown'})
    df['functional_class_cat'] = df['FUNCTIONAL_CLASS_026'].astype(str).str.strip().replace({'': 'Unknown', 'nan': 'Unknown'})

    df['effective_year'] = df['yr_recon'].fillna(df['year'])
    df['age_years'] = (REFERENCE_YEAR - df['year']).clip(lower=0)
    df['reconstructed_flag'] = df['yr_recon'].notna().astype(int)
    df['time_since_rehab'] = (REFERENCE_YEAR - df['effective_year']).clip(lower=0)
    df['design_era_1989'] = df['effective_year'].apply(design_era_from_year)

    df['max_span_log1p'] = np.log1p(df['max_span'].fillna(0).clip(lower=0))
    df['deck_area_log1p'] = np.log1p(df['deck_area'])
    df['adt_log1p'] = np.log1p(df['adt_raw'])
    df['detour_km_log1p'] = np.log1p(df['detour_km'])

    df['HWB_CLASS'] = df.apply(assign_hwb_class, axis=1)
    df[['P_DS0', 'P_DS1', 'P_DS2', 'P_DS3', 'P_DS4']] = df.apply(compute_damage_probs, axis=1)
    df['P_SUM'] = df[['P_DS0', 'P_DS1', 'P_DS2', 'P_DS3', 'P_DS4']].sum(axis=1)
    df[TARGET] = sum(df[col] * DAMAGE_WEIGHTS[col] for col in DAMAGE_WEIGHTS)
    df['EDR_LOG1P'] = np.log1p(df[TARGET])
    df['positive_pga_flag'] = (df['pga'] > 0).astype(int)

    df = compute_svi(df)
    return df


def evaluate_model_on_holdout(
    df: pd.DataFrame,
    features: list[str],
    model,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    label: str,
):
    X = df[features].copy()
    y = df[TARGET].to_numpy()

    X_train = X.iloc[train_idx].copy()
    X_test = X.iloc[test_idx].copy()
    y_train = y[train_idx]
    y_test = y[test_idx]

    model.fit(X_train, y_train)
    y_pred = np.clip(model.predict(X_test), 0, None)
    metrics = regression_metrics(y_test, y_pred)

    meta_cols = [
        'join_id', 'STRUCTURE_NUMBER_008', 'COUNTY_CODE_003', 'pga', 'HWB_CLASS',
        'SVI', 'design_era_1989', 'positive_pga_flag',
    ]
    pred_df = df.iloc[test_idx][meta_cols].reset_index(drop=True)
    pred_df = pd.concat([pred_df, X_test.reset_index(drop=True)], axis=1)
    pred_df['EDR_actual'] = y_test
    pred_df['EDR_predicted'] = y_pred
    pred_df['EDR_actual_log1p'] = np.log1p(y_test)
    pred_df['EDR_predicted_log1p'] = np.log1p(np.clip(y_pred, 0, None))
    pred_df['Residual'] = pred_df['EDR_actual'] - pred_df['EDR_predicted']
    pred_df['Absolute_Error'] = pred_df['Residual'].abs()
    pred_df['Label'] = label

    perm = permutation_importance(model, X_test, y_test, n_repeats=6, random_state=RANDOM_STATE, n_jobs=1)
    importance_df = pd.DataFrame({
        'Feature': features,
        'Importance': perm.importances_mean,
        'Importance_std': perm.importances_std,
        'Label': label,
    }).sort_values('Importance', ascending=False)

    return metrics, pred_df, importance_df, y_test, y_pred, model


def save_heatmap(results_df: pd.DataFrame, value_col: str, title: str, path: Path) -> None:
    pivot = results_df.pivot(index='Feature Set', columns='Model', values=value_col)
    plt.figure(figsize=(12, 5.5))
    sns.heatmap(pivot, annot=True, fmt='.4f', cmap='YlGnBu')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()


def save_actual_vs_predicted(y_true: np.ndarray, y_pred: np.ndarray, title: str, path: Path, log_scale: bool = False) -> None:
    if log_scale:
        x_vals = np.log1p(np.clip(y_true, 0, None))
        y_vals = np.log1p(np.clip(y_pred, 0, None))
        xlabel = 'log1p(Actual EDR)'
        ylabel = 'log1p(Predicted EDR)'
    else:
        x_vals = np.clip(y_true, 0, None)
        y_vals = np.clip(y_pred, 0, None)
        xlabel = 'Actual EDR'
        ylabel = 'Predicted EDR'

    plt.figure(figsize=(7, 6))
    plt.scatter(x_vals, y_vals, s=14, alpha=0.45)
    lims = [min(float(np.min(x_vals)), float(np.min(y_vals))), max(float(np.max(x_vals)), float(np.max(y_vals)))]
    plt.plot(lims, lims, color='black', linestyle='--', linewidth=1)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()


def save_residual_hist(pred_df: pd.DataFrame, title: str, path: Path) -> None:
    plt.figure(figsize=(7, 5.5))
    sns.histplot(pred_df['Residual'], bins=45, kde=True)
    plt.axvline(0, color='black', linestyle='--', linewidth=1)
    plt.xlabel('Residual (Actual - Predicted)')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()


def save_feature_importance(importance_df: pd.DataFrame, title: str, path: Path) -> None:
    top_imp = importance_df.head(12).iloc[::-1]
    plt.figure(figsize=(8.5, 6.0))
    plt.barh(top_imp['Feature'], top_imp['Importance'], xerr=top_imp['Importance_std'])
    plt.xlabel('Permutation Importance')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()


def save_decile_plot(pred_df: pd.DataFrame, title: str, path: Path) -> None:
    plot_df = pred_df[['EDR_actual', 'EDR_predicted']].copy()
    plot_df['Predicted_Bin'] = pd.qcut(plot_df['EDR_predicted'].rank(method='first'), q=10, labels=False)
    grouped = plot_df.groupby('Predicted_Bin', as_index=False).agg(
        Predicted_EDR=('EDR_predicted', 'mean'),
        Actual_EDR=('EDR_actual', 'mean'),
    )

    plt.figure(figsize=(7, 5.5))
    plt.plot(grouped['Predicted_EDR'], grouped['Actual_EDR'], marker='o', linewidth=2)
    lims = [
        min(grouped['Predicted_EDR'].min(), grouped['Actual_EDR'].min()),
        max(grouped['Predicted_EDR'].max(), grouped['Actual_EDR'].max()),
    ]
    plt.plot(lims, lims, color='black', linestyle='--', linewidth=1)
    plt.xlabel('Mean predicted EDR by prediction decile')
    plt.ylabel('Mean actual EDR by prediction decile')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()


def source_feature_from_encoded(name: str, categorical_features: list[str]) -> str:
    if name.startswith('num__'):
        return name.split('__', 1)[1]
    if name.startswith('cat__'):
        remainder = name.split('__', 1)[1]
        for feature in sorted(categorical_features, key=len, reverse=True):
            prefix = feature + '_'
            if remainder == feature or remainder.startswith(prefix):
                return feature
        return remainder
    return name


def compute_mutual_information(df: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    preprocessor = make_preprocessor(features)
    X = df[features].copy()
    y = np.log1p(df[TARGET].to_numpy())
    transformed = preprocessor.fit_transform(X)
    encoded_names = list(preprocessor.get_feature_names_out())
    categorical_features = [feature for feature in features if feature in CATEGORICAL_FEATURES]
    discrete_mask = np.array([name.startswith('cat__') for name in encoded_names], dtype=bool)

    scores = mutual_info_regression(transformed, y, discrete_features=discrete_mask, random_state=RANDOM_STATE)
    mi_df = pd.DataFrame({
        'Encoded Feature': encoded_names,
        'Source Feature': [source_feature_from_encoded(name, categorical_features) for name in encoded_names],
        'Mutual Information': scores,
    })
    mi_df = (
        mi_df.groupby('Source Feature', as_index=False)['Mutual Information']
        .sum()
        .sort_values('Mutual Information', ascending=False)
        .reset_index(drop=True)
    )
    return mi_df


def save_mutual_information_plot(mi_df: pd.DataFrame, title: str, path: Path) -> None:
    top_df = mi_df.head(12).iloc[::-1]
    plt.figure(figsize=(8.5, 6.0))
    plt.barh(top_df['Source Feature'], top_df['Mutual Information'])
    plt.xlabel('Aggregated mutual information with log1p(EDR)')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()


def compare_target_transforms(df: pd.DataFrame, features: list[str], model_name: str, train_idx: np.ndarray, test_idx: np.ndarray) -> pd.DataFrame:
    preprocessor = make_preprocessor(features)
    raw_model = make_models(preprocessor, log_target=False)[model_name]
    log_model = make_models(preprocessor, log_target=True)[model_name]

    rows = []
    for transform_label, model in [('Raw target', raw_model), ('log1p -> expm1 target', log_model)]:
        metrics, _, _, _, _, _ = evaluate_model_on_holdout(
            df,
            features,
            model,
            train_idx,
            test_idx,
            f'{RECOMMENDED_FEATURE_SET} :: {model_name} :: {transform_label}',
        )
        rows.append({'Transform': transform_label, **metrics})
    return pd.DataFrame(rows)


def write_ml_doc(
    summary_path: Path,
    dataset_df: pd.DataFrame,
    best_by_feature: pd.DataFrame,
    results_df: pd.DataFrame,
    transform_df: pd.DataFrame,
    benchmark_label: tuple[str, str],
    recommended_label: tuple[str, str],
    recommended_transform_label: str,
    benchmark_metrics: dict,
    recommended_metrics: dict,
) -> None:
    feature_manifest_df = pd.DataFrame(FEATURE_MANIFEST, columns=['Feature', 'Role', 'Reason'])
    top_results = results_df.sort_values(['CV_RMSE', 'CV_MAE']).head(10).copy()
    top_results = top_results[[
        'Feature Set', 'Model', 'CV_MAE', 'CV_RMSE', 'CV_RMSLE', 'CV_R2',
        'Holdout_MAE', 'Holdout_RMSE', 'Holdout_RMSLE', 'Holdout_R2',
        'Holdout_RMSE_Positive', 'Holdout_R2_Positive',
    ]]

    lines = [
        '# ML Hybrid Analysis',
        '',
        'This refreshed analysis rebuilds the machine-learning pipeline on the full California bridge inventory rather than only the ShakeMap-affected subset. The target remains HAZUS-derived Expected Damage Ratio (`EDR`), but bridges outside the PGA footprint are kept in the statewide training set with `pga = 0` and `EDR = 0` so the final model can score every bridge in the inventory.',
        '',
        '## What Changed',
        '',
        '- The training set now covers the full California inventory (`25,975` bridges).',
        f'- Bridges with positive PGA / positive fragility demand: `{int(dataset_df["positive_pga_flag"].sum()):,}`.',
        '- The professor-requested log-target workflow was tested directly, and the final recommended transform is chosen from the raw-vs-log comparison rather than assumed in advance.',
        '- A new `design_era_1989` categorical feature was added to reflect the professor note about a HAZUS-style design-era split.',
        '- The model comparison now separates pure bridge vulnerability models from event-damage models that also include hazard demand.',
        '- Additional validation outputs were added: log-scale fit plots, decile calibration plots, feature-importance charts, and a mutual-information screen.',
        '',
        '## Why These Models',
        '',
        '- Tree ensembles remain the strongest default choice for structured tabular engineering data in both the tabular-ML literature and bridge-seismic applications.',
        '- `HistGradientBoosting` and `Extra Trees` cover two strong nonlinear ensemble families available in the project runtime.',
        '- `Random Forest` is kept because bridge-seismic studies often report it as a robust baseline.',
        '- `MLPRegressor` is included as a nonlinear neural-network baseline, but only after the tabular tree baselines.',
        '- `Elastic Net` remains as the transparent linear baseline.',
        '',
        '## Engineering Variable Screen',
        '',
        table_to_markdown(feature_manifest_df),
        '',
        '## Feature-Set Comparison',
        '',
    ]
    for name, desc in FEATURE_SET_DESCRIPTIONS.items():
        lines.append(f'- `{name}`: {desc}')
    lines.extend([
        '',
        '## Best Model By Feature Set',
        '',
        table_to_markdown(best_by_feature[[
            'Feature Set', 'Model', 'CV_MAE', 'CV_RMSE', 'CV_RMSLE', 'CV_R2',
            'Holdout_RMSE', 'Holdout_R2', 'Holdout_RMSE_Positive', 'Holdout_R2_Positive',
        ]]),
        '',
        '## Top Overall Results',
        '',
        table_to_markdown(top_results),
        '',
        '## Target-Transform Check',
        '',
        'The professor note about training on the log of the model was implemented directly. The table below compares the same recommended no-PGA vulnerability model trained on the raw target versus `log1p(EDR)` and then mapped back with `expm1(...)`.',
        '',
        table_to_markdown(transform_df),
        '',
        '## Best Overall Benchmark',
        '',
        f'- Feature set: `{benchmark_label[0]}`',
        f'- Model: `{benchmark_label[1]}`',
        f'- Holdout MAE: `{benchmark_metrics["MAE"]:.6f}`',
        f'- Holdout RMSE: `{benchmark_metrics["RMSE"]:.6f}`',
        f'- Holdout RMSLE: `{benchmark_metrics["RMSLE"]:.6f}`',
        f'- Holdout R2: `{benchmark_metrics["R2"]:.6f}`',
        f'- Holdout RMSE on positive-damage bridges only: `{benchmark_metrics["RMSE_Positive"]:.6f}`',
        f'- Holdout R2 on positive-damage bridges only: `{benchmark_metrics["R2_Positive"]:.6f}`',
        '',
        '## Recommended Final Model For Presentation',
        '',
        f'- Feature set: `{recommended_label[0]}`',
        f'- Model: `{recommended_label[1]}`',
        f'- Target transform used for the final exported model: `{recommended_transform_label}`',
        f'- Holdout MAE: `{recommended_metrics["MAE"]:.6f}`',
        f'- Holdout RMSE: `{recommended_metrics["RMSE"]:.6f}`',
        f'- Holdout RMSLE: `{recommended_metrics["RMSLE"]:.6f}`',
        f'- Holdout R2: `{recommended_metrics["R2"]:.6f}`',
        f'- Holdout RMSE on positive-damage bridges only: `{recommended_metrics["RMSE_Positive"]:.6f}`',
        f'- Holdout R2 on positive-damage bridges only: `{recommended_metrics["R2_Positive"]:.6f}`',
        '',
        'This is the recommended presentation model because it is a pure bridge-intrinsic vulnerability model: it removes PGA and traffic/network consequence variables and keeps only structural class, age / rehabilitation, geometry, condition, and rating information.',
        '',
        '## Important Interpretation Note',
        '',
        '- Because the statewide inventory contains many bridges with zero or near-zero damage, overall metrics improve compared with the affected-only subset.',
        '- For that reason, the positive-damage holdout metrics are also reported above so the model is not judged only on easy zero-damage cases.',
        '- The target is still HAZUS-derived `EDR`, so the no-PGA vulnerability model is best interpreted as a bridge-intrinsic surrogate for relative vulnerability, not as a full physics-based damage predictor.',
        '- The `Event Damage Hybrid` rows should be used when the question is event-specific damage prediction, because that framing intentionally includes PGA.',
        '',
        '## Generated Artifacts',
        '',
        '- `data/processed/ml_statewide_training_dataset.csv`',
        '- `data/processed/ml_hybrid_comparison.csv`',
        '- `data/processed/ml_hybrid_best_by_feature_set.csv`',
        '- `data/processed/ml_hybrid_predictions.csv`',
        '- `data/processed/ml_hybrid_feature_importance.csv`',
        '- `data/processed/ml_recommended_hybrid_metrics.csv`',
        '- `data/processed/ml_recommended_hybrid_predictions.csv`',
        '- `data/processed/ml_recommended_hybrid_feature_importance.csv`',
        '- `data/processed/ml_statewide_bridge_scores.csv`',
        '- `data/processed/ml_feature_screen_mutual_info.csv`',
        '- `data/processed/ml_target_transform_comparison.csv`',
        '- `figures/ml_hybrid_rmse_heatmap.png`',
        '- `figures/ml_hybrid_r2_heatmap.png`',
        '- `figures/ml_hybrid_rmsle_heatmap.png`',
        '- `figures/ml_hybrid_actual_vs_predicted.png`',
        '- `figures/ml_hybrid_log_actual_vs_predicted.png`',
        '- `figures/ml_hybrid_residuals.png`',
        '- `figures/ml_hybrid_decile_calibration.png`',
        '- `figures/ml_hybrid_feature_importance.png`',
        '- `figures/ml_recommended_hybrid_actual_vs_predicted.png`',
        '- `figures/ml_recommended_hybrid_log_actual_vs_predicted.png`',
        '- `figures/ml_recommended_hybrid_feature_importance.png`',
        '- `figures/ml_recommended_hybrid_decile_calibration.png`',
        '- `figures/ml_recommended_hybrid_mutual_information.png`',
        '',
        '## Literature Notes',
        '',
    ])
    for author, title, url in LITERATURE:
        lines.append(f'- {author}: [{title}]({url})')

    summary_path.write_text('\n'.join(lines) + '\n')


def main() -> None:
    paths = build_paths()
    require_paths(paths, ['PGA_BRIDGE_CSV'])

    processed_dir = paths['PROCESSED_DIR']
    figures_dir = paths['FIGURES_DIR']
    figures_dir.mkdir(parents=True, exist_ok=True)

    dataset_df = load_statewide_bridge_dataset(paths)
    dataset_path = processed_dir / 'ml_statewide_training_dataset.csv'
    dataset_df.to_csv(dataset_path, index=False)

    y = dataset_df[TARGET].to_numpy()
    positive_indicator = dataset_df['positive_pga_flag'].to_numpy()
    cv = list(StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE).split(dataset_df, positive_indicator))
    train_idx, test_idx = train_test_split(
        np.arange(len(dataset_df)),
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=positive_indicator,
    )

    scorers = {
        'mae': make_scorer(mae_score, greater_is_better=False),
        'rmse': make_scorer(rmse_score, greater_is_better=False),
        'rmsle': make_scorer(rmsle_score, greater_is_better=False),
        'r2': make_scorer(r2_nonnegative),
    }

    results = []
    best_candidates = []

    for feature_set_name, features in FEATURE_SETS.items():
        X = dataset_df[features].copy()
        preprocessor = make_preprocessor(features)
        models = make_models(preprocessor, log_target=True)

        for model_name, model in models.items():
            print(f'Running {feature_set_name} :: {model_name}', flush=True)
            scores = cross_validate(
                model,
                X,
                y,
                cv=cv,
                scoring=scorers,
                n_jobs=1,
                return_train_score=False,
            )

            holdout_metrics, _, _, _, _, _ = evaluate_model_on_holdout(
                dataset_df,
                features,
                clone(model),
                train_idx,
                test_idx,
                f'{feature_set_name} :: {model_name}',
            )

            row = {
                'Feature Set': feature_set_name,
                'Model': model_name,
                'CV_MAE': -scores['test_mae'].mean(),
                'CV_RMSE': -scores['test_rmse'].mean(),
                'CV_RMSLE': -scores['test_rmsle'].mean(),
                'CV_R2': scores['test_r2'].mean(),
                'CV_MAE_std': scores['test_mae'].std(),
                'CV_RMSE_std': scores['test_rmse'].std(),
                'CV_RMSLE_std': scores['test_rmsle'].std(),
                'CV_R2_std': scores['test_r2'].std(),
                'Holdout_MAE': holdout_metrics['MAE'],
                'Holdout_RMSE': holdout_metrics['RMSE'],
                'Holdout_RMSLE': holdout_metrics['RMSLE'],
                'Holdout_R2': holdout_metrics['R2'],
                'Holdout_MAE_Positive': holdout_metrics['MAE_Positive'],
                'Holdout_RMSE_Positive': holdout_metrics['RMSE_Positive'],
                'Holdout_RMSLE_Positive': holdout_metrics['RMSLE_Positive'],
                'Holdout_R2_Positive': holdout_metrics['R2_Positive'],
            }
            results.append(row)
            best_candidates.append((row['CV_RMSE'], feature_set_name, model_name, features))

    results_df = pd.DataFrame(results).sort_values(['CV_RMSE', 'CV_MAE', 'Holdout_RMSE']).reset_index(drop=True)
    results_csv = processed_dir / 'ml_hybrid_comparison.csv'
    results_df.to_csv(results_csv, index=False)

    best_by_feature = (
        results_df.sort_values(['Feature Set', 'CV_RMSE', 'CV_MAE'])
        .groupby('Feature Set', as_index=False)
        .first()
        .sort_values('CV_RMSE')
        .reset_index(drop=True)
    )
    best_summary_csv = processed_dir / 'ml_hybrid_best_by_feature_set.csv'
    best_by_feature.to_csv(best_summary_csv, index=False)

    manifest_df = pd.DataFrame(FEATURE_MANIFEST, columns=['Feature', 'Role', 'Reason'])
    manifest_csv = processed_dir / 'ml_feature_manifest.csv'
    manifest_df.to_csv(manifest_csv, index=False)

    best_rmse, best_feature_set, best_model_name, best_features = min(best_candidates, key=lambda item: item[0])
    best_model = make_models(make_preprocessor(best_features), log_target=True)[best_model_name]
    best_metrics, best_pred_df, best_importance_df, best_y_test, best_y_pred, _ = evaluate_model_on_holdout(
        dataset_df,
        best_features,
        best_model,
        train_idx,
        test_idx,
        f'{best_feature_set} :: {best_model_name}',
    )
    best_pred_df.to_csv(processed_dir / 'ml_hybrid_predictions.csv', index=False)
    best_importance_df.to_csv(processed_dir / 'ml_hybrid_feature_importance.csv', index=False)

    recommended_row = (
        results_df[results_df['Feature Set'] == RECOMMENDED_FEATURE_SET]
        .sort_values(['CV_RMSE', 'CV_MAE', 'Holdout_RMSE'])
        .iloc[0]
    )
    recommended_model_name = recommended_row['Model']
    recommended_features = FEATURE_SETS[RECOMMENDED_FEATURE_SET]
    recommended_log_model = make_models(make_preprocessor(recommended_features), log_target=True)[recommended_model_name]
    log_metrics, log_pred_df, log_importance_df, log_y_test, log_y_pred, _ = evaluate_model_on_holdout(
        dataset_df,
        recommended_features,
        recommended_log_model,
        train_idx,
        test_idx,
        f'{RECOMMENDED_FEATURE_SET} :: {recommended_model_name} :: log1p -> expm1 target',
    )

    recommended_raw_model = make_models(make_preprocessor(recommended_features), log_target=False)[recommended_model_name]
    raw_metrics, raw_pred_df, raw_importance_df, raw_y_test, raw_y_pred, _ = evaluate_model_on_holdout(
        dataset_df,
        recommended_features,
        recommended_raw_model,
        train_idx,
        test_idx,
        f'{RECOMMENDED_FEATURE_SET} :: {recommended_model_name} :: raw target',
    )

    transform_df = pd.DataFrame([
        {'Transform': 'Raw target', **raw_metrics},
        {'Transform': 'log1p -> expm1 target', **log_metrics},
    ])
    transform_df.to_csv(processed_dir / 'ml_target_transform_comparison.csv', index=False)

    if raw_metrics['RMSE'] <= log_metrics['RMSE']:
        recommended_transform_label = 'Raw target'
        recommended_metrics = raw_metrics
        recommended_pred_df = raw_pred_df
        recommended_importance_df = raw_importance_df
        recommended_y_test = raw_y_test
        recommended_y_pred = raw_y_pred
        recommended_full_model = make_models(make_preprocessor(recommended_features), log_target=False)[recommended_model_name]
    else:
        recommended_transform_label = 'log1p -> expm1 target'
        recommended_metrics = log_metrics
        recommended_pred_df = log_pred_df
        recommended_importance_df = log_importance_df
        recommended_y_test = log_y_test
        recommended_y_pred = log_y_pred
        recommended_full_model = make_models(make_preprocessor(recommended_features), log_target=True)[recommended_model_name]

    recommended_metrics_df = pd.DataFrame([{
        'Feature Set': RECOMMENDED_FEATURE_SET,
        'Model': recommended_model_name,
        'Transform': recommended_transform_label,
        **recommended_metrics,
    }])
    recommended_metrics_df.to_csv(processed_dir / 'ml_recommended_hybrid_metrics.csv', index=False)
    recommended_pred_df.to_csv(processed_dir / 'ml_recommended_hybrid_predictions.csv', index=False)
    recommended_importance_df.to_csv(processed_dir / 'ml_recommended_hybrid_feature_importance.csv', index=False)

    mi_df = compute_mutual_information(dataset_df, recommended_features)
    mi_df.to_csv(processed_dir / 'ml_feature_screen_mutual_info.csv', index=False)

    save_heatmap(results_df, 'CV_RMSE', 'Cross-validated RMSE by feature set and model', figures_dir / 'ml_hybrid_rmse_heatmap.png')
    save_heatmap(results_df, 'CV_R2', 'Cross-validated R2 by feature set and model', figures_dir / 'ml_hybrid_r2_heatmap.png')
    save_heatmap(results_df, 'CV_RMSLE', 'Cross-validated RMSLE by feature set and model', figures_dir / 'ml_hybrid_rmsle_heatmap.png')

    save_actual_vs_predicted(best_y_test, best_y_pred, f'Best overall model: {best_model_name} on {best_feature_set}', figures_dir / 'ml_hybrid_actual_vs_predicted.png', log_scale=False)
    save_actual_vs_predicted(best_y_test, best_y_pred, f'Best overall model: {best_model_name} on {best_feature_set} (log scale)', figures_dir / 'ml_hybrid_log_actual_vs_predicted.png', log_scale=True)
    save_residual_hist(best_pred_df, 'Residual distribution for best overall ML model', figures_dir / 'ml_hybrid_residuals.png')
    save_feature_importance(best_importance_df, 'Top features for the best overall ML model', figures_dir / 'ml_hybrid_feature_importance.png')
    save_decile_plot(best_pred_df, 'Best overall model decile calibration', figures_dir / 'ml_hybrid_decile_calibration.png')

    save_actual_vs_predicted(recommended_y_test, recommended_y_pred, f'Recommended statewide model: {recommended_model_name}', figures_dir / 'ml_recommended_hybrid_actual_vs_predicted.png', log_scale=False)
    save_actual_vs_predicted(recommended_y_test, recommended_y_pred, f'Recommended statewide model: {recommended_model_name} (log scale)', figures_dir / 'ml_recommended_hybrid_log_actual_vs_predicted.png', log_scale=True)
    save_feature_importance(recommended_importance_df, 'Top features for the recommended statewide model', figures_dir / 'ml_recommended_hybrid_feature_importance.png')
    save_decile_plot(recommended_pred_df, 'Recommended statewide model decile calibration', figures_dir / 'ml_recommended_hybrid_decile_calibration.png')
    save_mutual_information_plot(mi_df, 'Mutual-information screen for recommended statewide features', figures_dir / 'ml_recommended_hybrid_mutual_information.png')

    # Fit the recommended model on the full statewide dataset for scoring / ranking outputs.
    X_full = dataset_df[recommended_features].copy()
    recommended_full_model.fit(X_full, y)
    statewide_pred = np.clip(recommended_full_model.predict(X_full), 0, None)

    statewide_scores = dataset_df[[
        'join_id', 'STRUCTURE_NUMBER_008', 'COUNTY_CODE_003', 'latitude', 'longitude',
        'pga', 'HWB_CLASS', 'SVI', 'design_era_1989', 'adt_raw', 'truck_pct', 'kind', 'type',
    ]].copy()
    statewide_scores['Observed_EDR'] = dataset_df[TARGET]
    statewide_scores['Predicted_EDR'] = statewide_pred
    statewide_scores['Predicted_EDR_log1p'] = np.log1p(statewide_pred)
    statewide_scores['Risk_Percentile'] = pd.Series(statewide_pred).rank(method='average', pct=True)
    statewide_scores['Risk_Decile'] = pd.qcut(
        statewide_scores['Risk_Percentile'].rank(method='first'),
        q=10,
        labels=[f'D{i}' for i in range(1, 11)],
    )
    statewide_scores = statewide_scores.sort_values('Predicted_EDR', ascending=False).reset_index(drop=True)
    statewide_scores.to_csv(processed_dir / 'ml_statewide_bridge_scores.csv', index=False)

    summary_path = PROJECT_ROOT / 'docs' / 'ML_HYBRID_ANALYSIS.md'
    write_ml_doc(
        summary_path,
        dataset_df,
        best_by_feature,
        results_df,
        transform_df,
        (best_feature_set, best_model_name),
        (RECOMMENDED_FEATURE_SET, recommended_model_name),
        recommended_transform_label,
        best_metrics,
        recommended_metrics,
    )

    print('Statewide bridges used for ML:', f'{len(dataset_df):,}')
    print('Bridges with positive PGA:', f'{int(dataset_df["positive_pga_flag"].sum()):,}')
    print('\nTop 12 model rows:')
    print(results_df.head(12).to_string(index=False))
    print('\nBest by feature set:')
    print(best_by_feature[['Feature Set', 'Model', 'CV_RMSE', 'CV_R2', 'Holdout_RMSE', 'Holdout_R2', 'Holdout_RMSE_Positive', 'Holdout_R2_Positive']].to_string(index=False))
    print('\nRecommended target transform comparison:')
    print(transform_df.to_string(index=False))
    print(f'\nSaved: {results_csv}')
    print(f'Saved: {best_summary_csv}')
    print(f'Saved: {summary_path}')


if __name__ == '__main__':
    main()
