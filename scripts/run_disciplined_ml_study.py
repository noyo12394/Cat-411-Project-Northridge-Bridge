from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
import time
import warnings

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from runtime_checks import ensure_packages, ensure_supported_runtime

ensure_supported_runtime()
ensure_packages(['numpy', 'pandas', 'matplotlib', 'sklearn', 'seaborn'])

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from sklearn.base import clone
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import (
    AdaBoostRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import ElasticNet, Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVR
from sklearn.tree import DecisionTreeRegressor

from project_paths import build_paths, require_paths
from svi_methodology import clean_float_series, clean_int_series, extract_year

warnings.filterwarnings('ignore', category=ConvergenceWarning)
sns.set_theme(style='whitegrid')

RANDOM_STATE = 42
REFERENCE_YEAR = 2025
TARGET = 'EDR'
N_CV_SPLITS = 3
TEST_SIZE = 0.2

STRUCTURAL_NUMERIC = [
    'age_years',
    'time_since_rehab',
    'reconstructed_flag',
    'spans',
    'max_span_log1p',
    'skew',
    'cond',
    'deck_area_log1p',
    'operating_rating',
]
STRUCTURAL_CATEGORICAL = ['HWB_CLASS', 'design_era_1989']
SVI_FEATURES = ['SVI']
NDVI_FEATURES = ['ndvi_change', 'ndvi_loss']
CONSEQUENCE_COLUMNS = ['adt_raw', 'truck_pct', 'detour_km', 'lanes_on']

BANNED_CORE_FEATURES = {
    'pga', 'pga_raw', 'positive_pga_flag', 'adt_raw', 'adt_log1p', 'ADT_029',
    'avg_daily_', 'truck_pct', 'PERCENT_ADT_TRUCK_109', 'detour_km',
    'detour_km_log1p', 'DETOUR_KILOS_019', 'lanes_on', 'TRAFFIC_LANES_ON_028A',
    'functional_class_cat', 'FUNCTIONAL_CLASS_026', 'latitude', 'longitude',
    'lat', 'long', 'join_id', 'STRUCTURE_NUMBER_008', 'bridge_id',
}

MODEL_FAMILY_ORDER = [
    'Structural-only core',
    'Structural + SVI',
    'Structural + SVI + NDVI',
]

LINEAR_COEFFICIENT_MODELS = {
    'Linear Regression',
    'Ridge Regression',
    'Lasso Regression',
    'Elastic Net',
    'Support Vector Regressor (LinearSVR)',
}

MODEL_NOTES = {
    'Linear Regression': 'Transparent ordinary least-squares baseline.',
    'Ridge Regression': 'Linear baseline with L2 regularization for collinearity control.',
    'Lasso Regression': 'Sparse linear baseline with L1 feature selection pressure.',
    'Elastic Net': 'Hybrid L1/L2 linear baseline.',
    'Decision Tree': 'Single nonlinear tree baseline for interpretability.',
    'Random Forest': 'Bagged tree ensemble for robust tabular nonlinearities.',
    'Extra Trees': 'Randomized tree ensemble, often strong on tabular data.',
    'Gradient Boosting': 'Sequential boosting baseline for nonlinear structured data.',
    'HistGradientBoosting': 'Fast histogram-based boosting for larger tabular datasets.',
    'AdaBoost': 'Boosting baseline that reweights difficult examples.',
    'KNeighbors': 'Distance-based nonparametric baseline.',
    'Support Vector Regressor (LinearSVR)': 'Portable support-vector regressor baseline; avoids RBF SVR cost on 25k rows.',
    'MLPRegressor': 'Small neural-network baseline for tabular comparison.',
}

FEATURE_ROLE_ROWS = [
    ('age_years', 'intrinsic structural', 'Bridge age derived from year built.'),
    ('time_since_rehab', 'intrinsic structural', 'Years since reconstruction, falling back to bridge age.'),
    ('reconstructed_flag', 'intrinsic structural', 'Whether a reconstruction year is recorded.'),
    ('spans', 'intrinsic structural', 'Number of main spans.'),
    ('max_span_log1p', 'intrinsic structural', 'Log transformed maximum span length.'),
    ('skew', 'intrinsic structural', 'Skew angle in degrees.'),
    ('cond', 'intrinsic structural', 'Condition rating proxy.'),
    ('deck_area_log1p', 'intrinsic structural', 'Log transformed bridge deck area / structural scale.'),
    ('operating_rating', 'intrinsic structural', 'Operating rating from inventory.'),
    ('HWB_CLASS', 'intrinsic structural class', 'HAZUS bridge class used as structural-system descriptor, not hazard demand.'),
    ('design_era_1989', 'intrinsic design context', 'Design-era category derived from effective construction / reconstruction year.'),
    ('SVI', 'contextual vulnerability covariate', 'Added only in Structural + SVI family to test incremental value.'),
    ('ndvi_change', 'post-event proxy', 'Added only in extended post-event family.'),
    ('ndvi_loss', 'post-event proxy', 'Negative NDVI change recoded as nonnegative post-event loss proxy.'),
    ('adt_raw', 'consequence / prioritization only', 'Used only after vulnerability prediction for ranking, never in core regression.'),
    ('truck_pct', 'consequence / prioritization only', 'Used only after vulnerability prediction for ranking.'),
    ('detour_km', 'consequence / prioritization only', 'Used only after vulnerability prediction for ranking.'),
]


@dataclass(frozen=True)
class FeatureFamily:
    name: str
    description: str
    features: list[str]


def table_to_markdown(df: pd.DataFrame, float_digits: int = 6) -> str:
    if df.empty:
        return '_No rows available._'
    cols = list(df.columns)
    lines = [
        '| ' + ' | '.join(cols) + ' |',
        '| ' + ' | '.join(['---'] * len(cols)) + ' |',
    ]
    for _, row in df.iterrows():
        values = []
        for col in cols:
            val = row[col]
            if isinstance(val, (float, np.floating)):
                values.append(f'{val:.{float_digits}f}')
            else:
                values.append(str(val))
        lines.append('| ' + ' | '.join(values) + ' |')
    return '\n'.join(lines)


def design_era_from_year(year: float) -> str:
    if pd.isna(year):
        return 'Unknown'
    if year < 1975:
        return 'Pre-1975'
    if year <= 1989:
        return '1975-1989'
    return '1990+'


def safe_numeric(df: pd.DataFrame, column: str, default=np.nan) -> pd.Series:
    if column in df.columns:
        return pd.to_numeric(df[column], errors='coerce')
    return pd.Series(default, index=df.index, dtype='float64')


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if 'year' not in df.columns:
        df['year'] = clean_int_series(df['YEAR_BUILT_027'])
    if 'yr_recon' not in df.columns:
        df['yr_recon'] = extract_year(df['YEAR_RECONSTRUCTED_106'])
    if 'spans' not in df.columns:
        df['spans'] = clean_int_series(df['MAIN_UNIT_SPANS_045'])
    if 'max_span' not in df.columns:
        df['max_span'] = clean_float_series(df['MAX_SPAN_LEN_MT_048']).clip(lower=0)
    if 'skew' not in df.columns:
        df['skew'] = clean_float_series(df['DEGREES_SKEW_034']).clip(lower=0)
    if 'cond' not in df.columns:
        df['cond'] = clean_float_series(df.get('LOWEST_RATING', df.get('SUBSTRUCTURE_COND_060')))

    df['deck_area'] = safe_numeric(df, 'DECK_AREA', 0).fillna(0).clip(lower=0)
    df['operating_rating'] = safe_numeric(df, 'OPERATING_RATING_064')
    df['adt_raw'] = safe_numeric(df, 'ADT_029', 0).fillna(0).clip(lower=0)
    df['truck_pct'] = safe_numeric(df, 'PERCENT_ADT_TRUCK_109', 0).fillna(0).clip(lower=0)
    df['detour_km'] = safe_numeric(df, 'DETOUR_KILOS_019', 0).fillna(0).clip(lower=0)
    df['lanes_on'] = clean_int_series(df['TRAFFIC_LANES_ON_028A']) if 'TRAFFIC_LANES_ON_028A' in df.columns else 0

    df['effective_year'] = df['yr_recon'].where(df['yr_recon'].notna() & (df['yr_recon'] > 0), df['year'])
    df['age_years'] = (REFERENCE_YEAR - df['year']).clip(lower=0)
    df['reconstructed_flag'] = (df['yr_recon'].notna() & (df['yr_recon'] > 0)).astype(int)
    df['time_since_rehab'] = (REFERENCE_YEAR - df['effective_year']).clip(lower=0)
    df['design_era_1989'] = df['effective_year'].apply(design_era_from_year)
    df['max_span_log1p'] = np.log1p(safe_numeric(df, 'max_span', 0).fillna(0).clip(lower=0))
    df['deck_area_log1p'] = np.log1p(df['deck_area'])

    if 'HWB_CLASS' not in df.columns:
        raise KeyError('HWB_CLASS is required as the structural bridge-class descriptor.')
    df['HWB_CLASS'] = df['HWB_CLASS'].astype(str).str.strip().replace({'': 'Unknown', 'nan': 'Unknown'})
    df['design_era_1989'] = df['design_era_1989'].astype(str).str.strip().replace({'': 'Unknown', 'nan': 'Unknown'})

    if TARGET not in df.columns:
        raise KeyError(f'{TARGET} target column is required for this continuous regression study.')
    df[TARGET] = safe_numeric(df, TARGET, np.nan)
    df = df.dropna(subset=[TARGET]).reset_index(drop=True)
    return df


def attach_ndvi_features(df: pd.DataFrame, paths: dict) -> tuple[pd.DataFrame, dict]:
    df = df.copy()
    ndvi_path_candidates = [
        paths['RESULTS_CSV'],
        paths['PROCESSED_DIR'] / 'final_bridge_analysis.csv',
        paths['PROJECT_ROOT'] / 'outputs' / 'ndvi' / 'final_bridge_analysis.csv',
    ]
    ndvi_path = next((path for path in ndvi_path_candidates if path.exists()), None)
    info = {'ndvi_source': 'not found', 'ndvi_rows': 0, 'ndvi_nonnull': 0}

    if ndvi_path is None:
        df['ndvi_change'] = np.nan
        df['ndvi_loss'] = np.nan
        return df, info

    ndvi_df = pd.read_csv(ndvi_path, low_memory=False)
    change_col = next((col for col in ['ndvi_chan', 'ndvi_change', 'NDVI_CHANGE', 'NDVI_Change'] if col in ndvi_df.columns), None)
    if change_col is None or 'join_id' not in ndvi_df.columns:
        df['ndvi_change'] = np.nan
        df['ndvi_loss'] = np.nan
        info['ndvi_source'] = f'{ndvi_path.name} missing join_id or NDVI change column'
        return df, info

    slim = ndvi_df[['join_id', change_col]].copy()
    slim['join_id'] = slim['join_id'].astype(str).str.strip()
    slim = slim.rename(columns={change_col: 'ndvi_change'})
    slim['ndvi_change'] = pd.to_numeric(slim['ndvi_change'], errors='coerce')
    slim = slim.drop_duplicates(subset=['join_id'], keep='first')

    df['join_id'] = df['join_id'].astype(str).str.strip() if 'join_id' in df.columns else df.index.astype(str)
    df = df.merge(slim, on='join_id', how='left')
    df['ndvi_loss'] = np.maximum(0, -df['ndvi_change'])
    info.update({
        'ndvi_source': str(ndvi_path.relative_to(paths['PROJECT_ROOT'])),
        'ndvi_rows': len(slim),
        'ndvi_nonnull': int(df['ndvi_change'].notna().sum()),
    })
    return df, info


def load_dataset(paths: dict) -> tuple[pd.DataFrame, dict]:
    require_paths(paths, ['SVI_CSV'])
    df = pd.read_csv(paths['SVI_CSV'], low_memory=False)
    df = add_engineered_features(df)
    df, ndvi_info = attach_ndvi_features(df, paths)
    return df, ndvi_info


def feature_families(df: pd.DataFrame) -> list[FeatureFamily]:
    structural = STRUCTURAL_NUMERIC + STRUCTURAL_CATEGORICAL
    structural_svi = structural + SVI_FEATURES
    extended_ndvi = structural_svi + NDVI_FEATURES
    families = [
        FeatureFamily(
            'Structural-only core',
            'Intrinsic bridge variables only: age, reconstruction timing, geometry, condition, deck scale, rating, design era, and HWB class. No PGA, ADT, traffic, NDVI, or coordinates.',
            structural,
        ),
        FeatureFamily(
            'Structural + SVI',
            'Adds SVI as a contextual vulnerability covariate to test whether the index improves over structural variables alone.',
            structural_svi,
        ),
        FeatureFamily(
            'Structural + SVI + NDVI',
            'Extended post-event proxy model. Adds NDVI change and NDVI loss only after the structural + SVI model.',
            extended_ndvi,
        ),
    ]
    available = set(df.columns)
    for family in families:
        missing = [feature for feature in family.features if feature not in available]
        if missing:
            raise KeyError(f'Missing features for {family.name}: {missing}')
        banned = sorted(set(family.features).intersection(BANNED_CORE_FEATURES))
        if banned:
            raise ValueError(f'{family.name} illegally includes banned core features: {banned}')
    return families


def make_preprocessor(features: list[str]) -> ColumnTransformer:
    categorical = [feature for feature in features if feature in STRUCTURAL_CATEGORICAL]
    numeric = [feature for feature in features if feature not in categorical]
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
            ('num', numeric_pipe, numeric),
            ('cat', categorical_pipe, categorical),
        ],
        remainder='drop',
        sparse_threshold=0,
    )


def transformed(pipe: Pipeline, use_log_target: bool = True):
    if not use_log_target:
        return pipe
    return TransformedTargetRegressor(
        regressor=pipe,
        func=np.log1p,
        inverse_func=np.expm1,
        check_inverse=False,
    )


def make_models(preprocessor: ColumnTransformer) -> dict[str, object]:
    return {
        'Linear Regression': transformed(Pipeline([
            ('prep', clone(preprocessor)),
            ('model', LinearRegression()),
        ])),
        'Ridge Regression': transformed(Pipeline([
            ('prep', clone(preprocessor)),
            ('model', Ridge(alpha=1.5)),
        ])),
        'Lasso Regression': transformed(Pipeline([
            ('prep', clone(preprocessor)),
            ('model', Lasso(alpha=1e-4, max_iter=15000, random_state=RANDOM_STATE)),
        ])),
        'Elastic Net': transformed(Pipeline([
            ('prep', clone(preprocessor)),
            ('model', ElasticNet(alpha=5e-4, l1_ratio=0.25, max_iter=15000, random_state=RANDOM_STATE)),
        ])),
        'Decision Tree': transformed(Pipeline([
            ('prep', clone(preprocessor)),
            ('model', DecisionTreeRegressor(max_depth=14, min_samples_leaf=8, random_state=RANDOM_STATE)),
        ])),
        'Random Forest': transformed(Pipeline([
            ('prep', clone(preprocessor)),
            ('model', RandomForestRegressor(n_estimators=160, min_samples_leaf=3, max_features='sqrt', n_jobs=-1, random_state=RANDOM_STATE)),
        ])),
        'Extra Trees': transformed(Pipeline([
            ('prep', clone(preprocessor)),
            ('model', ExtraTreesRegressor(n_estimators=180, min_samples_leaf=2, max_features='sqrt', n_jobs=-1, random_state=RANDOM_STATE)),
        ])),
        'Gradient Boosting': transformed(Pipeline([
            ('prep', clone(preprocessor)),
            ('model', GradientBoostingRegressor(n_estimators=180, learning_rate=0.045, max_depth=3, subsample=0.85, random_state=RANDOM_STATE)),
        ])),
        'HistGradientBoosting': transformed(Pipeline([
            ('prep', clone(preprocessor)),
            ('model', HistGradientBoostingRegressor(max_iter=180, learning_rate=0.045, max_leaf_nodes=31, min_samples_leaf=20, l2_regularization=0.05, random_state=RANDOM_STATE)),
        ])),
        'AdaBoost': transformed(Pipeline([
            ('prep', clone(preprocessor)),
            ('model', AdaBoostRegressor(n_estimators=160, learning_rate=0.035, loss='square', random_state=RANDOM_STATE)),
        ])),
        'KNeighbors': transformed(Pipeline([
            ('prep', clone(preprocessor)),
            ('model', KNeighborsRegressor(n_neighbors=35, weights='distance', p=2, n_jobs=-1)),
        ])),
        'Support Vector Regressor (LinearSVR)': transformed(Pipeline([
            ('prep', clone(preprocessor)),
            ('model', LinearSVR(C=0.7, epsilon=0.01, loss='squared_epsilon_insensitive', max_iter=15000, random_state=RANDOM_STATE)),
        ])),
        'MLPRegressor': transformed(Pipeline([
            ('prep', clone(preprocessor)),
            ('model', MLPRegressor(hidden_layer_sizes=(32,), alpha=1e-3, learning_rate_init=1e-3, early_stopping=True, validation_fraction=0.12, max_iter=45, n_iter_no_change=4, tol=1e-3, batch_size=512, random_state=RANDOM_STATE)),
        ])),
    }


def rmse(y_true, y_pred) -> float:
    return float(np.sqrt(mean_squared_error(y_true, np.clip(y_pred, 0, None))))


def regression_metrics(y_true, y_pred) -> dict[str, float]:
    y_pred = np.clip(y_pred, 0, None)
    return {
        'MAE': float(mean_absolute_error(y_true, y_pred)),
        'RMSE': rmse(y_true, y_pred),
        'R2': float(r2_score(y_true, y_pred)),
    }


def scorer_from_metric(metric_name: str):
    def score_func(estimator, X, y):
        pred = np.clip(estimator.predict(X), 0, None)
        if metric_name == 'mae':
            return -mean_absolute_error(y, pred)
        if metric_name == 'rmse':
            return -np.sqrt(mean_squared_error(y, pred))
        if metric_name == 'r2':
            return r2_score(y, pred)
        raise ValueError(metric_name)
    return score_func


def positive_target_bins(y: np.ndarray) -> np.ndarray:
    return (np.asarray(y) > 1e-12).astype(int)


def fit_predict(model, X_train, y_train, X_test) -> tuple[np.ndarray, float, float, object]:
    start = time.perf_counter()
    fitted = clone(model)
    fitted.fit(X_train, y_train)
    fit_seconds = time.perf_counter() - start
    pred_start = time.perf_counter()
    y_pred = np.clip(fitted.predict(X_test), 0, None)
    predict_seconds = time.perf_counter() - pred_start
    return y_pred, fit_seconds, predict_seconds, fitted


def run_family_models(df: pd.DataFrame, family: FeatureFamily, train_idx, test_idx, cv) -> tuple[pd.DataFrame, dict[str, object]]:
    features = family.features
    X = df[features].copy()
    y = df[TARGET].to_numpy()
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    preprocessor = make_preprocessor(features)
    models = make_models(preprocessor)
    rows = []
    fitted = {}

    for model_name, model in models.items():
        print(f'[{family.name}] running {model_name}', flush=True)
        cv_start = time.perf_counter()
        cv_scores = cross_validate(
            model,
            X,
            y,
            cv=cv,
            scoring={
                'mae': scorer_from_metric('mae'),
                'rmse': scorer_from_metric('rmse'),
                'r2': scorer_from_metric('r2'),
            },
            n_jobs=1,
            return_train_score=False,
            error_score='raise',
        )
        cv_seconds = time.perf_counter() - cv_start
        y_pred, fit_seconds, predict_seconds, fitted_model = fit_predict(model, X_train, y_train, X_test)
        holdout = regression_metrics(y_test, y_pred)
        rows.append({
            'Model Family': family.name,
            'Model': model_name,
            'N_Features': len(features),
            'CV_MAE': float(-cv_scores['test_mae'].mean()),
            'CV_MAE_std': float(cv_scores['test_mae'].std()),
            'CV_RMSE': float(-cv_scores['test_rmse'].mean()),
            'CV_RMSE_std': float(cv_scores['test_rmse'].std()),
            'CV_R2': float(cv_scores['test_r2'].mean()),
            'CV_R2_std': float(cv_scores['test_r2'].std()),
            'Holdout_MAE': holdout['MAE'],
            'Holdout_RMSE': holdout['RMSE'],
            'Holdout_R2': holdout['R2'],
            'CV_seconds': cv_seconds,
            'Fit_seconds': fit_seconds,
            'Predict_seconds': predict_seconds,
            'Feature Columns': ', '.join(features),
        })
        fitted[model_name] = fitted_model
    return pd.DataFrame(rows), fitted


def prediction_frame(df: pd.DataFrame, family: FeatureFamily, model_name: str, model, test_idx) -> pd.DataFrame:
    X_test = df.iloc[test_idx][family.features].copy()
    y_test = df.iloc[test_idx][TARGET].to_numpy()
    y_pred = np.clip(model.predict(X_test), 0, None)
    cols = [col for col in ['join_id', 'STRUCTURE_NUMBER_008', 'COUNTY_CODE_003', 'HWB_CLASS', 'SVI', 'ndvi_change', 'adt_raw', 'truck_pct', 'detour_km'] if col in df.columns]
    out = df.iloc[test_idx][cols].reset_index(drop=True)
    out['Model Family'] = family.name
    out['Model'] = model_name
    out['EDR_actual'] = y_test
    out['EDR_predicted'] = y_pred
    out['Residual'] = out['EDR_actual'] - out['EDR_predicted']
    out['Absolute_Error'] = out['Residual'].abs()
    return out


def source_feature_from_encoded(encoded: str, source_features: list[str]) -> str:
    if encoded.startswith('num__'):
        return encoded.split('__', 1)[1]
    if encoded.startswith('cat__'):
        name = encoded.split('__', 1)[1]
        for feature in sorted(source_features, key=len, reverse=True):
            if name == feature or name.startswith(feature + '_'):
                return feature
        return name
    return encoded


def model_coefficients(model, family: FeatureFamily) -> pd.DataFrame:
    regressor = model.regressor_ if isinstance(model, TransformedTargetRegressor) else model
    final_model = regressor.named_steps.get('model') if isinstance(regressor, Pipeline) else None
    if final_model is None or not hasattr(final_model, 'coef_'):
        return pd.DataFrame()
    prep = regressor.named_steps['prep']
    encoded = prep.get_feature_names_out()
    coef = np.asarray(final_model.coef_).ravel()
    if len(coef) != len(encoded):
        return pd.DataFrame()
    result = pd.DataFrame({
        'Model Family': family.name,
        'Encoded Feature': encoded,
        'Source Feature': [source_feature_from_encoded(name, family.features) for name in encoded],
        'Coefficient': coef,
        'Abs_Coefficient': np.abs(coef),
    })
    return result.sort_values('Abs_Coefficient', ascending=False)


def permutation_importance_frame(model, df: pd.DataFrame, family: FeatureFamily, test_idx) -> pd.DataFrame:
    X_test = df.iloc[test_idx][family.features].copy()
    y_test = df.iloc[test_idx][TARGET].to_numpy()
    result = permutation_importance(
        model,
        X_test,
        y_test,
        n_repeats=5,
        random_state=RANDOM_STATE,
        n_jobs=1,
        scoring=scorer_from_metric('r2'),
    )
    return pd.DataFrame({
        'Model Family': family.name,
        'Feature': family.features,
        'Importance_R2_Decrease': result.importances_mean,
        'Importance_std': result.importances_std,
    }).sort_values('Importance_R2_Decrease', ascending=False)


def normalize_rank(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors='coerce').fillna(0)
    if values.nunique(dropna=False) <= 1:
        return pd.Series(0.0, index=series.index)
    return values.rank(method='average', pct=True)


def create_priority_scores(df: pd.DataFrame, family: FeatureFamily, model, processed_dir: Path) -> pd.DataFrame:
    X = df[family.features].copy()
    vulnerability = np.clip(model.predict(X), 0, None)
    out_cols = [col for col in ['join_id', 'STRUCTURE_NUMBER_008', 'COUNTY_CODE_003', 'latitude', 'longitude', 'HWB_CLASS', 'SVI', 'adt_raw', 'truck_pct', 'detour_km'] if col in df.columns]
    out = df[out_cols].copy()
    out['Observed_EDR'] = df[TARGET]
    out['Predicted_Vulnerability_EDR'] = vulnerability
    out['Vulnerability_Percentile'] = normalize_rank(out['Predicted_Vulnerability_EDR'])
    out['ADT_Percentile'] = normalize_rank(out.get('adt_raw', 0))
    out['Truck_Percentile'] = normalize_rank(out.get('truck_pct', 0))
    out['Detour_Percentile'] = normalize_rank(out.get('detour_km', 0))
    out['Consequence_Score'] = 0.65 * out['ADT_Percentile'] + 0.2 * out['Truck_Percentile'] + 0.15 * out['Detour_Percentile']
    out['Inspection_Priority_Score'] = 0.7 * out['Vulnerability_Percentile'] + 0.3 * out['Consequence_Score']
    out['Priority_Rank'] = out['Inspection_Priority_Score'].rank(method='first', ascending=False).astype(int)
    out = out.sort_values('Priority_Rank').reset_index(drop=True)
    path = processed_dir / 'ml_consequence_priority_scores.csv'
    out.to_csv(path, index=False)
    return out


def save_barplot(df: pd.DataFrame, x: str, y: str, hue: str | None, title: str, path: Path, top_n: int | None = None) -> None:
    plot_df = df.copy()
    if top_n:
        plot_df = plot_df.head(top_n)
    plt.figure(figsize=(11, 6))
    sns.barplot(data=plot_df, x=x, y=y, hue=hue)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()


def save_model_comparison_plot(results: pd.DataFrame, path: Path) -> None:
    best = results.sort_values(['Model Family', 'CV_RMSE']).groupby('Model Family', as_index=False).head(6)
    plt.figure(figsize=(12, 6))
    sns.barplot(data=best, x='CV_RMSE', y='Model', hue='Model Family')
    plt.title('Top model comparison by feature family (lower CV RMSE is better)')
    plt.xlabel('Cross-validated RMSE')
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()


def save_ablation_plot(best_by_family: pd.DataFrame, path: Path) -> None:
    order = [name for name in MODEL_FAMILY_ORDER if name in set(best_by_family['Model Family'])]
    plot_df = best_by_family.set_index('Model Family').loc[order].reset_index()
    plt.figure(figsize=(9, 5.5))
    sns.barplot(data=plot_df, x='Model Family', y='CV_RMSE', color='#4f7cac')
    plt.xticks(rotation=16, ha='right')
    plt.ylabel('Best cross-validated RMSE')
    plt.title('Ablation: structural-only vs SVI vs NDVI extension')
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()


def save_actual_predicted(pred_df: pd.DataFrame, title: str, path: Path) -> None:
    plt.figure(figsize=(7, 6))
    plt.scatter(pred_df['EDR_actual'], pred_df['EDR_predicted'], s=14, alpha=0.42)
    upper = max(pred_df['EDR_actual'].max(), pred_df['EDR_predicted'].max())
    plt.plot([0, upper], [0, upper], linestyle='--', color='black', linewidth=1)
    plt.xlabel('Actual EDR')
    plt.ylabel('Predicted EDR')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()


def save_residuals(pred_df: pd.DataFrame, title: str, path: Path) -> None:
    plt.figure(figsize=(8, 5.5))
    sns.histplot(pred_df['Residual'], bins=45, kde=True)
    plt.axvline(0, linestyle='--', color='black')
    plt.xlabel('Residual (actual - predicted)')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()


def save_importance_plot(importance_df: pd.DataFrame, title: str, path: Path) -> None:
    plot_df = importance_df.head(12).iloc[::-1]
    plt.figure(figsize=(8.5, 6))
    plt.barh(plot_df['Feature'], plot_df['Importance_R2_Decrease'], xerr=plot_df['Importance_std'], color='#345995')
    plt.xlabel('Permutation importance (R2 decrease)')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()


def save_priority_plot(priority_df: pd.DataFrame, path: Path) -> None:
    sample = priority_df.head(1500).copy()
    plt.figure(figsize=(8, 6))
    plt.scatter(sample['Vulnerability_Percentile'], sample['Consequence_Score'], c=sample['Inspection_Priority_Score'], cmap='viridis', s=16, alpha=0.65)
    plt.colorbar(label='Inspection priority score')
    plt.xlabel('Vulnerability percentile')
    plt.ylabel('Consequence score (ADT/trucks/detour only)')
    plt.title('Consequence layer: ADT affects priority, not vulnerability prediction')
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()


def write_doc(path: Path, df: pd.DataFrame, ndvi_info: dict, family_rows: pd.DataFrame, best_by_family: pd.DataFrame, ablation: pd.DataFrame, outputs: list[str]) -> None:
    manifest = pd.DataFrame(FEATURE_ROLE_ROWS, columns=['Feature', 'Role', 'Use'])
    top = family_rows.sort_values(['CV_RMSE', 'CV_MAE']).head(15)
    lines = [
        '# Disciplined ML Vulnerability Study',
        '',
        'This analysis is the conceptually disciplined ML study for the bridge vulnerability project. The target is continuous HAZUS-derived `EDR`, so the task is regression. The study deliberately separates intrinsic structural vulnerability, SVI context, post-event NDVI proxy information, and downstream consequence / prioritization variables.',
        '',
        '## Guardrails',
        '',
        '- `PGA` is not used in the core vulnerability feature families.',
        '- `ADT`, truck percentage, detour distance, lanes, and functional class are not used as vulnerability predictors.',
        '- `NDVI` appears only in the extended post-event model family.',
        '- `SVI` is tested as an additive covariate rather than forced into every model.',
        '- Consequence variables are used only after prediction to create an inspection-priority layer.',
        '',
        '## Dataset And Target',
        '',
        f'- Rows used: `{len(df):,}`',
        f'- Positive `EDR` rows: `{int((df[TARGET] > 1e-12).sum()):,}`',
        f'- Target: continuous `EDR` regression',
        f'- NDVI source: `{ndvi_info.get("ndvi_source")}`',
        f'- Rows with non-null NDVI change joined into ML table: `{int(ndvi_info.get("ndvi_nonnull", 0)):,}`',
        '',
        '## Feature Role Manifest',
        '',
        table_to_markdown(manifest),
        '',
        '## Model Families',
        '',
    ]
    for _, row in family_rows[['Model Family', 'Feature Columns']].drop_duplicates().iterrows():
        lines.append(f'- `{row["Model Family"]}`: `{row["Feature Columns"]}`')
    lines.extend([
        '',
        '## Methods Compared',
        '',
    ])
    for model_name, note in MODEL_NOTES.items():
        lines.append(f'- `{model_name}`: {note}')
    lines.extend([
        '',
        '## Best Model By Family',
        '',
        table_to_markdown(best_by_family[['Model Family', 'Model', 'CV_MAE', 'CV_RMSE', 'CV_R2', 'Holdout_MAE', 'Holdout_RMSE', 'Holdout_R2', 'Fit_seconds']]),
        '',
        '## Ablation Answer',
        '',
        table_to_markdown(ablation),
        '',
        '## Top Overall Rows',
        '',
        table_to_markdown(top[['Model Family', 'Model', 'CV_MAE', 'CV_RMSE', 'CV_R2', 'Holdout_RMSE', 'Holdout_R2', 'Fit_seconds']]),
        '',
        '## Interpretation Notes',
        '',
        '- The structural-only family answers which bridge-intrinsic variables can approximate relative vulnerability without hazard demand.',
        '- The structural + SVI family tests whether the SVI summary adds information beyond the raw structural variables.',
        '- The NDVI family is a post-event extension, not the baseline vulnerability model.',
        '- The priority output demonstrates where ADT belongs: ranking / consequence, not structural vulnerability prediction.',
        '- Because `EDR` is derived from the HAZUS-style workflow, these models are surrogate vulnerability screens, not independent validation against observed bridge damage.',
        '',
        '## Generated Outputs',
        '',
    ])
    lines.extend([f'- `{item}`' for item in outputs])
    path.write_text('\n'.join(lines) + '\n')


def main() -> None:
    paths = build_paths()
    processed_dir = paths['PROCESSED_DIR']
    figures_dir = paths['FIGURES_DIR']
    figures_dir.mkdir(parents=True, exist_ok=True)

    df, ndvi_info = load_dataset(paths)
    families = feature_families(df)
    dataset_path = processed_dir / 'ml_disciplined_training_dataset.csv'
    df.to_csv(dataset_path, index=False)

    y = df[TARGET].to_numpy()
    stratify = positive_target_bins(y)
    train_idx, test_idx = train_test_split(
        np.arange(len(df)),
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=stratify,
    )
    cv = list(StratifiedKFold(n_splits=N_CV_SPLITS, shuffle=True, random_state=RANDOM_STATE).split(df, stratify))

    all_rows = []
    fitted_models_by_family = {}
    for family in families:
        result_df, fitted = run_family_models(df, family, train_idx, test_idx, cv)
        all_rows.append(result_df)
        fitted_models_by_family[family.name] = fitted
        slug_map = {
            'Structural-only core': 'structural_only_core',
            'Structural + SVI': 'structural_svi',
            'Structural + SVI + NDVI': 'structural_svi_ndvi',
        }
        slug = slug_map[family.name]
        result_df.to_csv(processed_dir / f'ml_{slug}_results.csv', index=False)

    results = pd.concat(all_rows, ignore_index=True).sort_values(['CV_RMSE', 'CV_MAE']).reset_index(drop=True)
    results_path = processed_dir / 'ml_disciplined_model_comparison.csv'
    results.to_csv(results_path, index=False)

    best_by_family = (
        results.sort_values(['Model Family', 'CV_RMSE', 'CV_MAE'])
        .groupby('Model Family', as_index=False)
        .first()
        .sort_values('CV_RMSE')
        .reset_index(drop=True)
    )
    best_by_family_path = processed_dir / 'ml_disciplined_best_by_family.csv'
    best_by_family.to_csv(best_by_family_path, index=False)

    family_lookup = {family.name: family for family in families}
    prediction_frames = []
    importance_frames = []
    for _, best_row in best_by_family.iterrows():
        family = family_lookup[best_row['Model Family']]
        model_name = best_row['Model']
        model = fitted_models_by_family[family.name][model_name]
        prediction_frames.append(prediction_frame(df, family, model_name, model, test_idx))
        imp_df = permutation_importance_frame(model, df, family, test_idx)
        imp_df['Model'] = model_name
        importance_frames.append(imp_df)

    coefficient_frames = []
    for family in families:
        for model_name, model in fitted_models_by_family[family.name].items():
            if model_name not in LINEAR_COEFFICIENT_MODELS:
                continue
            coeff_df = model_coefficients(model, family)
            if not coeff_df.empty:
                coeff_df['Model'] = model_name
                coefficient_frames.append(coeff_df)

    predictions = pd.concat(prediction_frames, ignore_index=True)
    predictions_path = processed_dir / 'ml_disciplined_best_predictions.csv'
    predictions.to_csv(predictions_path, index=False)

    coefficients = pd.concat(coefficient_frames, ignore_index=True) if coefficient_frames else pd.DataFrame()
    coefficients_path = processed_dir / 'ml_disciplined_linear_coefficients.csv'
    coefficients.to_csv(coefficients_path, index=False)

    importances = pd.concat(importance_frames, ignore_index=True)
    importances_path = processed_dir / 'ml_disciplined_permutation_importance.csv'
    importances.to_csv(importances_path, index=False)

    manifest_path = processed_dir / 'ml_disciplined_feature_manifest.csv'
    pd.DataFrame(FEATURE_ROLE_ROWS, columns=['Feature', 'Role', 'Use']).to_csv(manifest_path, index=False)

    best_structural = best_by_family[best_by_family['Model Family'] == 'Structural-only core'].iloc[0]
    best_svi = best_by_family[best_by_family['Model Family'] == 'Structural + SVI'].iloc[0]
    best_ndvi = best_by_family[best_by_family['Model Family'] == 'Structural + SVI + NDVI'].iloc[0]
    ablation = pd.DataFrame([
        {
            'Question': 'Does SVI improve over structural-only?',
            'Baseline Family': 'Structural-only core',
            'Test Family': 'Structural + SVI',
            'Baseline Best CV_RMSE': best_structural['CV_RMSE'],
            'Test Best CV_RMSE': best_svi['CV_RMSE'],
            'Delta CV_RMSE': best_svi['CV_RMSE'] - best_structural['CV_RMSE'],
            'Improved?': bool(best_svi['CV_RMSE'] < best_structural['CV_RMSE']),
        },
        {
            'Question': 'Does NDVI add value only in post-event setup?',
            'Baseline Family': 'Structural + SVI',
            'Test Family': 'Structural + SVI + NDVI',
            'Baseline Best CV_RMSE': best_svi['CV_RMSE'],
            'Test Best CV_RMSE': best_ndvi['CV_RMSE'],
            'Delta CV_RMSE': best_ndvi['CV_RMSE'] - best_svi['CV_RMSE'],
            'Improved?': bool(best_ndvi['CV_RMSE'] < best_svi['CV_RMSE']),
        },
    ])
    ablation_path = processed_dir / 'ml_disciplined_ablation_summary.csv'
    ablation.to_csv(ablation_path, index=False)

    structural_svi_family = family_lookup['Structural + SVI']
    structural_svi_model = fitted_models_by_family['Structural + SVI'][best_svi['Model']]
    priority_df = create_priority_scores(df, structural_svi_family, structural_svi_model, processed_dir)

    save_model_comparison_plot(results, figures_dir / 'ml_disciplined_model_comparison.png')
    save_ablation_plot(best_by_family, figures_dir / 'ml_disciplined_ablation_rmse.png')
    save_actual_predicted(
        predictions[predictions['Model Family'] == best_svi['Model Family']],
        f'Best core vulnerability model: {best_svi["Model"]} ({best_svi["Model Family"]})',
        figures_dir / 'ml_disciplined_actual_vs_predicted.png',
    )
    save_residuals(
        predictions[predictions['Model Family'] == best_svi['Model Family']],
        f'Residuals for {best_svi["Model"]} ({best_svi["Model Family"]})',
        figures_dir / 'ml_disciplined_residuals.png',
    )
    save_importance_plot(
        importances[importances['Model Family'] == 'Structural + SVI'],
        'Permutation importance for best Structural + SVI model',
        figures_dir / 'ml_disciplined_feature_importance.png',
    )
    save_priority_plot(priority_df, figures_dir / 'ml_disciplined_priority_layer.png')

    outputs = [
        'data/processed/ml_disciplined_training_dataset.csv',
        'data/processed/ml_structural_only_core_results.csv',
        'data/processed/ml_structural_svi_results.csv',
        'data/processed/ml_structural_svi_ndvi_results.csv',
        'data/processed/ml_disciplined_model_comparison.csv',
        'data/processed/ml_disciplined_best_by_family.csv',
        'data/processed/ml_disciplined_best_predictions.csv',
        'data/processed/ml_disciplined_linear_coefficients.csv',
        'data/processed/ml_disciplined_permutation_importance.csv',
        'data/processed/ml_disciplined_ablation_summary.csv',
        'data/processed/ml_consequence_priority_scores.csv',
        'figures/ml_disciplined_model_comparison.png',
        'figures/ml_disciplined_ablation_rmse.png',
        'figures/ml_disciplined_actual_vs_predicted.png',
        'figures/ml_disciplined_residuals.png',
        'figures/ml_disciplined_feature_importance.png',
        'figures/ml_disciplined_priority_layer.png',
        'docs/ML_DISCIPLINED_STUDY.md',
    ]
    write_doc(PROJECT_ROOT / 'docs' / 'ML_DISCIPLINED_STUDY.md', df, ndvi_info, results, best_by_family, ablation, outputs)

    print('\nDisciplined ML study complete.')
    print('Rows:', f'{len(df):,}')
    print('Target:', TARGET, '(continuous regression)')
    print('NDVI joined rows:', f'{ndvi_info["ndvi_nonnull"]:,}', 'from', ndvi_info['ndvi_source'])
    print('\nBest by family:')
    print(best_by_family[['Model Family', 'Model', 'CV_MAE', 'CV_RMSE', 'CV_R2', 'Holdout_RMSE', 'Holdout_R2', 'Fit_seconds']].to_string(index=False))
    print('\nAblation:')
    print(ablation.to_string(index=False))
    print('\nSaved outputs listed in docs/ML_DISCIPLINED_STUDY.md')


if __name__ == '__main__':
    main()
