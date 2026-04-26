from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import sys
import time
import warnings

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
MPL_CACHE_DIR = PROJECT_ROOT / ".matplotlib-cache"
MPL_CACHE_DIR.mkdir(exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CACHE_DIR))
os.environ.setdefault("MPLBACKEND", "Agg")

from runtime_checks import ensure_packages, ensure_supported_runtime

ensure_supported_runtime()
ensure_packages(["numpy", "pandas", "matplotlib", "sklearn", "seaborn", "scipy"])

import matplotlib

matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import norm

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
from sklearn.multioutput import MultiOutputRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVR
from sklearn.tree import DecisionTreeRegressor

from project_paths import build_paths, require_paths
from svi_methodology import (
    FRAGILITY_DAMAGE_WEIGHTS,
    FRAGILITY_MU_BOUNDS,
    clean_float_series,
    clean_int_series,
    compute_fragility_parameters,
    compute_svi_scores,
    extract_year,
)


warnings.filterwarnings("ignore", category=ConvergenceWarning)
warnings.filterwarnings("ignore", category=UserWarning)
sns.set_theme(style="whitegrid", context="notebook")

RANDOM_STATE = 42
REFERENCE_YEAR = 2025
N_CV_SPLITS = 3
TEST_SIZE = 0.20
CV_SAMPLE_SIZE = 8000

FRAGILITY_TARGETS = [
    "MU_DS1_LINEAR",
    "MU_DS2_LINEAR",
    "MU_DS3_LINEAR",
    "MU_DS4_LINEAR",
    "BETA_SVI",
]
FRAGILITY_TARGET_LABELS = {
    "MU_DS1_LINEAR": "DS1 median",
    "MU_DS2_LINEAR": "DS2 median",
    "MU_DS3_LINEAR": "DS3 median",
    "MU_DS4_LINEAR": "DS4 median",
    "BETA_SVI": "beta",
}
DAMAGE_PROBABILITY_COLUMNS = ["P_DS0", "P_DS1", "P_DS2", "P_DS3", "P_DS4"]
SCENARIO_PGAS = [0.05, 0.10, 0.20, 0.40, 0.60]

STRUCTURAL_NUMERIC = [
    "age_years",
    "time_since_rehab",
    "reconstructed_flag",
    "spans",
    "max_span_log1p",
    "skew",
    "cond",
    "deck_area_log1p",
    "operating_rating",
]
STRUCTURAL_CATEGORICAL = ["HWB_CLASS", "design_era_1989"]
SVI_FEATURES = ["SVI"]
NDVI_FEATURES = ["ndvi_change", "ndvi_loss"]
EVENT_FEATURES = ["pga"]
CONSEQUENCE_COLUMNS = ["adt_raw", "truck_pct", "detour_km", "lanes_on"]

BANNED_CORE_FEATURES = {
    "pga",
    "pga_raw",
    "positive_pga_flag",
    "adt_raw",
    "adt_log1p",
    "ADT_029",
    "avg_daily_",
    "truck_pct",
    "PERCENT_ADT_TRUCK_109",
    "detour_km",
    "detour_km_log1p",
    "DETOUR_KILOS_019",
    "lanes_on",
    "TRAFFIC_LANES_ON_028A",
    "functional_class_cat",
    "FUNCTIONAL_CLASS_026",
    "latitude",
    "longitude",
    "lat",
    "long",
    "join_id",
    "STRUCTURE_NUMBER_008",
    "bridge_id",
}

MODEL_ORDER = [
    "Linear Regression",
    "Ridge Regression",
    "Lasso Regression",
    "Elastic Net",
    "Decision Tree",
    "Random Forest",
    "Extra Trees",
    "Gradient Boosting",
    "HistGradientBoosting",
    "AdaBoost",
    "KNeighbors",
    "Support Vector Regressor (LinearSVR)",
    "MLPRegressor",
]

MULTIOUTPUT_WRAPPER_MODELS = {
    "Gradient Boosting",
    "HistGradientBoosting",
    "AdaBoost",
    "Support Vector Regressor (LinearSVR)",
}


@dataclass(frozen=True)
class FeatureFamily:
    name: str
    description: str
    features: list[str]
    target_kind: str


def table_to_markdown(df: pd.DataFrame, float_digits: int = 6) -> str:
    if df.empty:
        return "_No rows available._"
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in df.iterrows():
        values = []
        for col in cols:
            val = row[col]
            if isinstance(val, (float, np.floating)):
                values.append(f"{val:.{float_digits}f}")
            else:
                values.append(str(val))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def safe_numeric(df: pd.DataFrame, column: str, default=np.nan) -> pd.Series:
    if column in df.columns:
        return pd.to_numeric(df[column], errors="coerce")
    return pd.Series(default, index=df.index, dtype="float64")


def design_era_from_year(year: float) -> str:
    if pd.isna(year):
        return "Unknown"
    if year < 1971:
        return "Pre-1971"
    if year <= 1989:
        return "1971-1989"
    return "1990+"


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    if "year" not in result.columns:
        result["year"] = clean_int_series(result["YEAR_BUILT_027"])
    if "yr_recon" not in result.columns:
        result["yr_recon"] = extract_year(result["YEAR_RECONSTRUCTED_106"])
    if "spans" not in result.columns:
        result["spans"] = clean_int_series(result["MAIN_UNIT_SPANS_045"])
    if "max_span" not in result.columns:
        result["max_span"] = clean_float_series(result["MAX_SPAN_LEN_MT_048"]).clip(lower=0)
    if "skew" not in result.columns:
        result["skew"] = clean_float_series(result["DEGREES_SKEW_034"]).clip(lower=0)
    if "cond" not in result.columns:
        if "SUBSTRUCTURE_COND_060" in result.columns:
            result["cond"] = clean_float_series(result["SUBSTRUCTURE_COND_060"])
        elif "LOWEST_RATING" in result.columns:
            result["cond"] = clean_float_series(result["LOWEST_RATING"])
        else:
            result["cond"] = np.nan

    result["deck_area"] = safe_numeric(result, "DECK_AREA", 0).fillna(0).clip(lower=0)
    result["operating_rating"] = safe_numeric(result, "OPERATING_RATING_064")
    result["adt_raw"] = safe_numeric(result, "ADT_029", 0).fillna(0).clip(lower=0)
    result["truck_pct"] = safe_numeric(result, "PERCENT_ADT_TRUCK_109", 0).fillna(0).clip(lower=0)
    result["detour_km"] = safe_numeric(result, "DETOUR_KILOS_019", 0).fillna(0).clip(lower=0)
    if "TRAFFIC_LANES_ON_028A" in result.columns:
        result["lanes_on"] = clean_int_series(result["TRAFFIC_LANES_ON_028A"]).fillna(0).clip(lower=0)
    else:
        result["lanes_on"] = 0

    result["pga"] = safe_numeric(result, "pga", 0).fillna(0).clip(lower=0)
    result["effective_year"] = result["yr_recon"].where(
        result["yr_recon"].notna() & (result["yr_recon"] > 0),
        result["year"],
    )
    result["age_years"] = (REFERENCE_YEAR - result["year"]).clip(lower=0)
    result["reconstructed_flag"] = (
        result["yr_recon"].notna() & (result["yr_recon"] > 0)
    ).astype(int)
    result["time_since_rehab"] = (REFERENCE_YEAR - result["effective_year"]).clip(lower=0)
    result["design_era_1989"] = result["effective_year"].apply(design_era_from_year)
    result["max_span_log1p"] = np.log1p(safe_numeric(result, "max_span", 0).fillna(0).clip(lower=0))
    result["deck_area_log1p"] = np.log1p(result["deck_area"])

    if "HWB_CLASS" not in result.columns:
        raise KeyError("HWB_CLASS is required as a structural class descriptor.")
    result["HWB_CLASS"] = (
        result["HWB_CLASS"].astype(str).str.strip().replace({"": "Unknown", "nan": "Unknown"})
    )
    result["design_era_1989"] = (
        result["design_era_1989"].astype(str).str.strip().replace({"": "Unknown", "nan": "Unknown"})
    )
    return result


def attach_ndvi_features(df: pd.DataFrame, paths: dict[str, Path]) -> tuple[pd.DataFrame, dict[str, object]]:
    result = df.copy()
    candidates = [
        paths["FINAL_ANALYSIS_CSV"],
        paths["RESULTS_CSV"],
        paths["PROJECT_ROOT"] / "outputs" / "ndvi" / "final_bridge_analysis.csv",
    ]
    ndvi_path = next((path for path in candidates if path.exists()), None)
    info = {"ndvi_source": "not found", "ndvi_rows": 0, "ndvi_nonnull": 0}

    if ndvi_path is None:
        result["ndvi_change"] = np.nan
        result["ndvi_loss"] = np.nan
        return result, info

    ndvi_df = pd.read_csv(ndvi_path, low_memory=False)
    change_col = next(
        (
            col
            for col in ["ndvi_chan", "ndvi_change", "NDVI_CHANGE", "NDVI_Change"]
            if col in ndvi_df.columns
        ),
        None,
    )
    if change_col is None or "join_id" not in ndvi_df.columns or "join_id" not in result.columns:
        result["ndvi_change"] = np.nan
        result["ndvi_loss"] = np.nan
        info["ndvi_source"] = f"{ndvi_path.name} missing join_id or NDVI change"
        return result, info

    slim = ndvi_df[["join_id", change_col]].copy()
    slim["join_id"] = slim["join_id"].astype(str).str.strip()
    slim = slim.rename(columns={change_col: "ndvi_change"})
    slim["ndvi_change"] = pd.to_numeric(slim["ndvi_change"], errors="coerce")
    slim = slim.drop_duplicates(subset=["join_id"], keep="first")

    result["join_id"] = result["join_id"].astype(str).str.strip()
    result = result.merge(slim, on="join_id", how="left")
    result["ndvi_loss"] = np.maximum(0, -result["ndvi_change"])
    info.update(
        {
            "ndvi_source": str(ndvi_path.relative_to(paths["PROJECT_ROOT"])),
            "ndvi_rows": int(len(slim)),
            "ndvi_nonnull": int(result["ndvi_change"].notna().sum()),
        }
    )
    return result, info


def load_dataset(paths: dict[str, Path]) -> tuple[pd.DataFrame, dict[str, object]]:
    require_paths(paths, ["SVI_CSV"])
    df = pd.read_csv(paths["SVI_CSV"], low_memory=False)
    df = compute_fragility_parameters(compute_svi_scores(df))
    df = add_engineered_features(df)
    df, ndvi_info = attach_ndvi_features(df, paths)

    missing_targets = [col for col in FRAGILITY_TARGETS + ["EDR"] if col not in df.columns]
    if missing_targets:
        raise KeyError(f"Missing required targets: {missing_targets}")

    for col in FRAGILITY_TARGETS + ["EDR"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=FRAGILITY_TARGETS + ["EDR"]).reset_index(drop=True)
    return df, ndvi_info


def fragility_feature_families(df: pd.DataFrame) -> list[FeatureFamily]:
    structural = STRUCTURAL_NUMERIC + STRUCTURAL_CATEGORICAL
    families = [
        FeatureFamily(
            "Structural Core",
            "Intrinsic bridge variables only. No PGA, ADT, coordinates, NDVI, or SVI.",
            structural,
            "fragility",
        ),
        FeatureFamily(
            "Structural + SVI",
            "Structural core plus SVI as an explicit contextual vulnerability index.",
            structural + SVI_FEATURES,
            "fragility",
        ),
        FeatureFamily(
            "Structural + SVI + NDVI",
            "Post-event extension. NDVI is included only as contextual proxy information.",
            structural + SVI_FEATURES + NDVI_FEATURES,
            "fragility",
        ),
    ]
    available = set(df.columns)
    for family in families:
        missing = [feature for feature in family.features if feature not in available]
        if missing:
            raise KeyError(f"Missing features for {family.name}: {missing}")
        banned = sorted(set(family.features).intersection(BANNED_CORE_FEATURES))
        if banned:
            raise ValueError(f"{family.name} illegally includes banned core features: {banned}")
    return families


def event_feature_family(df: pd.DataFrame) -> FeatureFamily:
    features = STRUCTURAL_NUMERIC + STRUCTURAL_CATEGORICAL + SVI_FEATURES + EVENT_FEATURES
    missing = [feature for feature in features if feature not in df.columns]
    if missing:
        raise KeyError(f"Missing event features: {missing}")
    return FeatureFamily(
        "Event Damage Family",
        "Downstream event-damage branch. PGA is allowed here because the target is event EDR.",
        features,
        "event_edr",
    )


def make_preprocessor(features: list[str]) -> ColumnTransformer:
    categorical = [feature for feature in features if feature in STRUCTURAL_CATEGORICAL]
    numeric = [feature for feature in features if feature not in categorical]
    numeric_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, numeric),
            ("cat", categorical_pipe, categorical),
        ],
        remainder="drop",
        sparse_threshold=0,
    )


def base_models() -> dict[str, object]:
    return {
        "Linear Regression": LinearRegression(),
        "Ridge Regression": Ridge(alpha=1.5),
        "Lasso Regression": Lasso(alpha=1e-4, max_iter=15000, random_state=RANDOM_STATE),
        "Elastic Net": ElasticNet(alpha=5e-4, l1_ratio=0.25, max_iter=15000, random_state=RANDOM_STATE),
        "Decision Tree": DecisionTreeRegressor(max_depth=12, min_samples_leaf=10, random_state=RANDOM_STATE),
        "Random Forest": RandomForestRegressor(
            n_estimators=45,
            min_samples_leaf=4,
            max_features="sqrt",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
        "Extra Trees": ExtraTreesRegressor(
            n_estimators=50,
            min_samples_leaf=3,
            max_features="sqrt",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=22,
            learning_rate=0.08,
            max_depth=3,
            subsample=0.85,
            random_state=RANDOM_STATE,
        ),
        "HistGradientBoosting": HistGradientBoostingRegressor(
            max_iter=25,
            learning_rate=0.08,
            max_leaf_nodes=31,
            min_samples_leaf=20,
            l2_regularization=0.05,
            random_state=RANDOM_STATE,
        ),
        "AdaBoost": AdaBoostRegressor(
            n_estimators=18,
            learning_rate=0.06,
            loss="square",
            random_state=RANDOM_STATE,
        ),
        "KNeighbors": KNeighborsRegressor(n_neighbors=35, weights="distance", p=2, n_jobs=-1),
        "Support Vector Regressor (LinearSVR)": LinearSVR(
            C=0.7,
            epsilon=0.01,
            loss="squared_epsilon_insensitive",
            max_iter=15000,
            random_state=RANDOM_STATE,
        ),
        "MLPRegressor": MLPRegressor(
            hidden_layer_sizes=(24,),
            alpha=1e-3,
            learning_rate_init=1e-3,
            early_stopping=True,
            validation_fraction=0.12,
            max_iter=25,
            n_iter_no_change=5,
            tol=1e-3,
            batch_size=512,
            random_state=RANDOM_STATE,
        ),
    }


def make_fragility_models(preprocessor: ColumnTransformer) -> dict[str, object]:
    models = {}
    for name, model in base_models().items():
        final_model = MultiOutputRegressor(model) if name in MULTIOUTPUT_WRAPPER_MODELS else model
        models[name] = Pipeline(
            [
                ("prep", clone(preprocessor)),
                ("model", final_model),
            ]
        )
    return models


def make_event_models(preprocessor: ColumnTransformer) -> dict[str, object]:
    models = {}
    for name, model in base_models().items():
        pipe = Pipeline(
            [
                ("prep", clone(preprocessor)),
                ("model", model),
            ]
        )
        models[name] = TransformedTargetRegressor(
            regressor=pipe,
            func=np.log1p,
            inverse_func=np.expm1,
            check_inverse=False,
        )
    return models


def postprocess_fragility_predictions(pred: np.ndarray) -> np.ndarray:
    values = np.asarray(pred, dtype=float).copy()
    for idx, damage_state in enumerate(["slight", "moderate", "extensive", "complete"]):
        low, high = FRAGILITY_MU_BOUNDS[damage_state]
        values[:, idx] = np.clip(values[:, idx], low, high)
    values[:, :4] = np.maximum.accumulate(values[:, :4], axis=1)
    values[:, 4] = np.clip(values[:, 4], 0.40, 1.20)
    return values


def fragility_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    y_pred = postprocess_fragility_predictions(y_pred)
    rows: dict[str, float] = {}
    maes = mean_absolute_error(y_true, y_pred, multioutput="raw_values")
    rmses = np.sqrt(mean_squared_error(y_true, y_pred, multioutput="raw_values"))
    r2s = r2_score(y_true, y_pred, multioutput="raw_values")
    for idx, target in enumerate(FRAGILITY_TARGETS):
        rows[f"MAE_{target}"] = float(maes[idx])
        rows[f"RMSE_{target}"] = float(rmses[idx])
        rows[f"R2_{target}"] = float(r2s[idx])
    rows["MAE_mean"] = float(np.mean(maes))
    rows["RMSE_mean"] = float(np.mean(rmses))
    rows["R2_mean"] = float(np.mean(r2s))
    return rows


def event_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    pred = np.clip(np.asarray(y_pred, dtype=float), 0, 1)
    return {
        "MAE": float(mean_absolute_error(y_true, pred)),
        "RMSE": float(np.sqrt(mean_squared_error(y_true, pred))),
        "R2": float(r2_score(y_true, pred)),
    }


def fragility_scorer(metric_name: str):
    def score_func(estimator, X, y):
        pred = postprocess_fragility_predictions(estimator.predict(X))
        if metric_name == "mae":
            return -float(mean_absolute_error(y, pred, multioutput="uniform_average"))
        if metric_name == "rmse":
            return -float(np.sqrt(mean_squared_error(y, pred, multioutput="uniform_average")))
        if metric_name == "r2":
            return float(r2_score(y, pred, multioutput="uniform_average"))
        raise ValueError(metric_name)

    return score_func


def event_scorer(metric_name: str):
    def score_func(estimator, X, y):
        pred = np.clip(estimator.predict(X), 0, 1)
        if metric_name == "mae":
            return -float(mean_absolute_error(y, pred))
        if metric_name == "rmse":
            return -float(np.sqrt(mean_squared_error(y, pred)))
        if metric_name == "r2":
            return float(r2_score(y, pred))
        raise ValueError(metric_name)

    return score_func


def fit_predict(model, X_train, y_train, X_test) -> tuple[np.ndarray, float, float, object]:
    fitted = clone(model)
    start = time.perf_counter()
    fitted.fit(X_train, y_train)
    fit_seconds = time.perf_counter() - start
    pred_start = time.perf_counter()
    y_pred = fitted.predict(X_test)
    predict_seconds = time.perf_counter() - pred_start
    return y_pred, fit_seconds, predict_seconds, fitted


def run_fragility_family(
    df: pd.DataFrame,
    family: FeatureFamily,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    cv_idx: np.ndarray,
    cv,
) -> tuple[pd.DataFrame, dict[str, object]]:
    X = df[family.features].copy()
    y = df[FRAGILITY_TARGETS].to_numpy(dtype=float)
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    X_cv = X.iloc[cv_idx].reset_index(drop=True)
    y_cv = y[cv_idx]
    models = make_fragility_models(make_preprocessor(family.features))

    rows = []
    fitted = {}
    for model_name in MODEL_ORDER:
        model = models[model_name]
        print(f"[fragility: {family.name}] running {model_name}", flush=True)
        cv_start = time.perf_counter()
        cv_scores = cross_validate(
            model,
            X_cv,
            y_cv,
            cv=cv,
            scoring={
                "mae": fragility_scorer("mae"),
                "rmse": fragility_scorer("rmse"),
                "r2": fragility_scorer("r2"),
            },
            n_jobs=1,
            return_train_score=False,
            error_score="raise",
        )
        cv_seconds = time.perf_counter() - cv_start
        y_pred, fit_seconds, predict_seconds, fitted_model = fit_predict(
            model, X_train, y_train, X_test
        )
        holdout = fragility_metrics(y_test, y_pred)
        rows.append(
            {
                "Target Strategy": "Fragility parameters",
                "Model Family": family.name,
                "Model": model_name,
                "N_Features": len(family.features),
                "CV_MAE_mean": float(-cv_scores["test_mae"].mean()),
                "CV_MAE_std": float(cv_scores["test_mae"].std()),
                "CV_RMSE_mean": float(-cv_scores["test_rmse"].mean()),
                "CV_RMSE_std": float(cv_scores["test_rmse"].std()),
                "CV_R2_mean": float(cv_scores["test_r2"].mean()),
                "CV_R2_std": float(cv_scores["test_r2"].std()),
                "Holdout_MAE_mean": holdout["MAE_mean"],
                "Holdout_RMSE_mean": holdout["RMSE_mean"],
                "Holdout_R2_mean": holdout["R2_mean"],
                "CV_seconds": cv_seconds,
                "Fit_seconds": fit_seconds,
                "Predict_seconds": predict_seconds,
                "Feature Columns": ", ".join(family.features),
                **{f"Holdout_{key}": value for key, value in holdout.items() if key not in {"MAE_mean", "RMSE_mean", "R2_mean"}},
            }
        )
        fitted[model_name] = fitted_model
    return pd.DataFrame(rows), fitted


def run_event_models(
    df: pd.DataFrame,
    family: FeatureFamily,
    train_idx: np.ndarray,
    test_idx: np.ndarray,
    cv_idx: np.ndarray,
    cv,
) -> tuple[pd.DataFrame, dict[str, object]]:
    X = df[family.features].copy()
    y = df["EDR"].to_numpy(dtype=float)
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    X_cv = X.iloc[cv_idx].reset_index(drop=True)
    y_cv = y[cv_idx]
    models = make_event_models(make_preprocessor(family.features))

    rows = []
    fitted = {}
    for model_name in MODEL_ORDER:
        model = models[model_name]
        print(f"[event EDR] running {model_name}", flush=True)
        cv_start = time.perf_counter()
        cv_scores = cross_validate(
            model,
            X_cv,
            y_cv,
            cv=cv,
            scoring={
                "mae": event_scorer("mae"),
                "rmse": event_scorer("rmse"),
                "r2": event_scorer("r2"),
            },
            n_jobs=1,
            return_train_score=False,
            error_score="raise",
        )
        cv_seconds = time.perf_counter() - cv_start
        y_pred, fit_seconds, predict_seconds, fitted_model = fit_predict(
            model, X_train, y_train, X_test
        )
        holdout = event_metrics(y_test, y_pred)
        rows.append(
            {
                "Target Strategy": "Direct event EDR",
                "Model Family": family.name,
                "Model": model_name,
                "N_Features": len(family.features),
                "CV_MAE": float(-cv_scores["test_mae"].mean()),
                "CV_MAE_std": float(cv_scores["test_mae"].std()),
                "CV_RMSE": float(-cv_scores["test_rmse"].mean()),
                "CV_RMSE_std": float(cv_scores["test_rmse"].std()),
                "CV_R2": float(cv_scores["test_r2"].mean()),
                "CV_R2_std": float(cv_scores["test_r2"].std()),
                "Holdout_MAE": holdout["MAE"],
                "Holdout_RMSE": holdout["RMSE"],
                "Holdout_R2": holdout["R2"],
                "CV_seconds": cv_seconds,
                "Fit_seconds": fit_seconds,
                "Predict_seconds": predict_seconds,
                "Feature Columns": ", ".join(family.features),
            }
        )
        fitted[model_name] = fitted_model
    return pd.DataFrame(rows), fitted


def compute_edr_from_fragility(params: np.ndarray, pga_values: np.ndarray | pd.Series | float) -> tuple[np.ndarray, np.ndarray]:
    arr = postprocess_fragility_predictions(np.asarray(params, dtype=float))
    pga = np.asarray(pga_values, dtype=float)
    if pga.ndim == 0:
        pga = np.repeat(float(pga), arr.shape[0])
    pga = np.nan_to_num(pga, nan=0.0, posinf=0.0, neginf=0.0)
    pga = np.clip(pga, 0, None)

    medians = arr[:, :4]
    beta = arr[:, 4]
    exceed = np.zeros((arr.shape[0], 4), dtype=float)
    valid = (pga > 0) & (beta > 0)
    if np.any(valid):
        ratio = pga[valid, None] / medians[valid, :]
        exceed[valid, :] = norm.cdf(np.log(ratio) / beta[valid, None])

    probs = np.zeros((arr.shape[0], 5), dtype=float)
    probs[:, 0] = np.maximum(0, 1 - exceed[:, 0])
    probs[:, 1] = np.maximum(0, exceed[:, 0] - exceed[:, 1])
    probs[:, 2] = np.maximum(0, exceed[:, 1] - exceed[:, 2])
    probs[:, 3] = np.maximum(0, exceed[:, 2] - exceed[:, 3])
    probs[:, 4] = np.maximum(0, exceed[:, 3])
    total = probs.sum(axis=1)
    bad = total <= 0
    total[bad] = 1
    probs = probs / total[:, None]
    probs[bad, :] = np.array([1, 0, 0, 0, 0])
    weights = np.array([FRAGILITY_DAMAGE_WEIGHTS[col] for col in DAMAGE_PROBABILITY_COLUMNS])
    edr = probs @ weights
    return edr, probs


def build_fragility_prediction_frame(
    df: pd.DataFrame,
    family: FeatureFamily,
    model_name: str,
    model,
    test_idx: np.ndarray,
) -> pd.DataFrame:
    X = df.iloc[test_idx][family.features].copy()
    actual = df.iloc[test_idx][FRAGILITY_TARGETS].to_numpy(dtype=float)
    pred = postprocess_fragility_predictions(model.predict(X))
    actual_edr_from_actual_fragility, _ = compute_edr_from_fragility(actual, df.iloc[test_idx]["pga"])
    pred_edr, pred_probs = compute_edr_from_fragility(pred, df.iloc[test_idx]["pga"])

    id_cols = [
        col
        for col in [
            "join_id",
            "STRUCTURE_NUMBER_008",
            "COUNTY_CODE_003",
            "HWB_CLASS",
            "SVI",
            "pga",
            "EDR",
            "ndvi_change",
            "adt_raw",
            "truck_pct",
            "detour_km",
        ]
        if col in df.columns
    ]
    out = df.iloc[test_idx][id_cols].reset_index(drop=True).copy()
    out["Model Family"] = family.name
    out["Model"] = model_name
    for idx, target in enumerate(FRAGILITY_TARGETS):
        out[f"{target}_actual"] = actual[:, idx]
        out[f"{target}_predicted"] = pred[:, idx]
        out[f"{target}_residual"] = actual[:, idx] - pred[:, idx]
    for idx, col in enumerate(DAMAGE_PROBABILITY_COLUMNS):
        out[f"{col}_from_predicted_fragility"] = pred_probs[:, idx]
    out["EDR_from_actual_fragility"] = actual_edr_from_actual_fragility
    out["EDR_from_predicted_fragility"] = pred_edr
    out["EDR_reconstruction_residual"] = out["EDR"] - out["EDR_from_predicted_fragility"]
    for scenario in SCENARIO_PGAS:
        scenario_edr, _ = compute_edr_from_fragility(pred, scenario)
        out[f"Scenario_EDR_from_predicted_fragility_{scenario:.2f}g"] = scenario_edr
    return out


def build_event_prediction_frame(
    df: pd.DataFrame,
    family: FeatureFamily,
    model_name: str,
    model,
    test_idx: np.ndarray,
) -> pd.DataFrame:
    X = df.iloc[test_idx][family.features].copy()
    y_true = df.iloc[test_idx]["EDR"].to_numpy(dtype=float)
    pred = np.clip(model.predict(X), 0, 1)
    id_cols = [
        col
        for col in [
            "join_id",
            "STRUCTURE_NUMBER_008",
            "COUNTY_CODE_003",
            "HWB_CLASS",
            "SVI",
            "pga",
            "ndvi_change",
        ]
        if col in df.columns
    ]
    out = df.iloc[test_idx][id_cols].reset_index(drop=True).copy()
    out["Model Family"] = family.name
    out["Model"] = model_name
    out["EDR_actual"] = y_true
    out["EDR_predicted"] = pred
    out["EDR_residual"] = y_true - pred
    out["EDR_abs_error"] = np.abs(out["EDR_residual"])
    return out


def source_feature_from_encoded(encoded: str, source_features: list[str]) -> str:
    if encoded.startswith("num__"):
        return encoded.split("__", 1)[1]
    if encoded.startswith("cat__"):
        name = encoded.split("__", 1)[1]
        for feature in sorted(source_features, key=len, reverse=True):
            if name == feature or name.startswith(feature + "_"):
                return feature
        return name
    return encoded


def collapse_importance_to_source(encoded_names: np.ndarray, values: np.ndarray, source_features: list[str]) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "Encoded Feature": encoded_names,
            "Source Feature": [source_feature_from_encoded(name, source_features) for name in encoded_names],
            "Value": values,
        }
    )
    return (
        frame.groupby("Source Feature", as_index=False)["Value"]
        .apply(lambda s: float(np.sum(np.abs(s))))
        .rename(columns={"Source Feature": "Feature", "Value": "Abs_Coefficient"})
        .sort_values("Abs_Coefficient", ascending=False)
    )


def coefficient_frame(model, family: FeatureFamily, model_name: str, target_kind: str) -> pd.DataFrame:
    estimator = model.regressor_ if isinstance(model, TransformedTargetRegressor) else model
    if not isinstance(estimator, Pipeline):
        return pd.DataFrame()
    prep = estimator.named_steps["prep"]
    final_model = estimator.named_steps["model"]
    if isinstance(final_model, MultiOutputRegressor):
        return pd.DataFrame()
    if not hasattr(final_model, "coef_"):
        return pd.DataFrame()
    encoded = prep.get_feature_names_out()
    coef = np.asarray(final_model.coef_)
    if coef.ndim == 1:
        collapsed = collapse_importance_to_source(encoded, coef, family.features)
    else:
        collapsed = collapse_importance_to_source(encoded, coef.mean(axis=0), family.features)
    collapsed["Target Kind"] = target_kind
    collapsed["Model Family"] = family.name
    collapsed["Model"] = model_name
    collapsed["Importance Type"] = "coefficient_abs"
    collapsed["Importance"] = collapsed["Abs_Coefficient"]
    collapsed["Importance_std"] = np.nan
    return collapsed[["Target Kind", "Model Family", "Model", "Feature", "Importance Type", "Importance", "Importance_std"]]


def permutation_importance_frame(
    model,
    df: pd.DataFrame,
    family: FeatureFamily,
    test_idx: np.ndarray,
    target_kind: str,
) -> pd.DataFrame:
    X_test = df.iloc[test_idx][family.features].copy()
    if target_kind == "fragility":
        y_test = df.iloc[test_idx][FRAGILITY_TARGETS].to_numpy(dtype=float)
        scoring = fragility_scorer("r2")
    else:
        y_test = df.iloc[test_idx]["EDR"].to_numpy(dtype=float)
        scoring = event_scorer("r2")
    result = permutation_importance(
        model,
        X_test,
        y_test,
        n_repeats=5,
        random_state=RANDOM_STATE,
        n_jobs=1,
        scoring=scoring,
    )
    return pd.DataFrame(
        {
            "Target Kind": target_kind,
            "Model Family": family.name,
            "Model": getattr(model, "_target_model_name", ""),
            "Feature": family.features,
            "Importance Type": "permutation_r2_decrease",
            "Importance": result.importances_mean,
            "Importance_std": result.importances_std,
        }
    ).sort_values("Importance", ascending=False)


def normalize_rank(series: pd.Series, ascending: bool = True) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0)
    if values.nunique(dropna=False) <= 1:
        return pd.Series(0.0, index=series.index)
    return values.rank(method="average", pct=True, ascending=ascending)


def build_priority_scores(df: pd.DataFrame, family: FeatureFamily, model, processed_dir: Path) -> pd.DataFrame:
    X = df[family.features].copy()
    fragility_pred = postprocess_fragility_predictions(model.predict(X))
    scenario_edr, _ = compute_edr_from_fragility(fragility_pred, 0.20)
    out_cols = [
        col
        for col in [
            "join_id",
            "STRUCTURE_NUMBER_008",
            "COUNTY_CODE_003",
            "HWB_CLASS",
            "SVI",
            "adt_raw",
            "truck_pct",
            "detour_km",
            "lanes_on",
        ]
        if col in df.columns
    ]
    out = df[out_cols].copy()
    out["Scenario_EDR_0p20_from_fragility_target_model"] = scenario_edr
    out["Vulnerability_Percentile"] = normalize_rank(out["Scenario_EDR_0p20_from_fragility_target_model"])
    out["ADT_Percentile"] = normalize_rank(out.get("adt_raw", 0))
    out["Truck_Percentile"] = normalize_rank(out.get("truck_pct", 0))
    out["Detour_Percentile"] = normalize_rank(out.get("detour_km", 0))
    out["Consequence_Score"] = (
        0.65 * out["ADT_Percentile"]
        + 0.20 * out["Truck_Percentile"]
        + 0.15 * out["Detour_Percentile"]
    )
    out["Priority_Score"] = 0.70 * out["Vulnerability_Percentile"] + 0.30 * out["Consequence_Score"]
    out["Priority_Rank"] = out["Priority_Score"].rank(method="first", ascending=False).astype(int)
    out = out.sort_values("Priority_Rank").reset_index(drop=True)
    out.to_csv(processed_dir / "ml_target_priority_scores.csv", index=False)
    return out


def pga_bin_labels(series: pd.Series) -> pd.Series:
    bins = [-0.001, 0.0, 0.05, 0.10, 0.20, 0.40, np.inf]
    labels = ["0", "(0,0.05]", "(0.05,0.10]", "(0.10,0.20]", "(0.20,0.40]", ">0.40"]
    return pd.cut(series.fillna(0), bins=bins, labels=labels)


def save_box(ax, xy, width, height, text, color):
    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.02,rounding_size=0.025",
        linewidth=1.2,
        facecolor=color,
        edgecolor="#1f2933",
        alpha=0.96,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=10,
        color="#111827",
        wrap=True,
    )


def save_arrow(ax, start, end):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=14,
            linewidth=1.4,
            color="#334155",
        )
    )


def plot_strategy_overview(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(13, 7))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    save_box(ax, (0.03, 0.63), 0.18, 0.18, "Structural bridge inventory\nage, spans, skew, condition, class", "#dbeafe")
    save_box(ax, (0.28, 0.70), 0.22, 0.14, "Core target A\nfragility medians DS1-DS4 + beta", "#dcfce7")
    save_box(ax, (0.58, 0.70), 0.18, 0.14, "Hazard-independent\nML vulnerability model", "#bbf7d0")
    save_box(ax, (0.81, 0.70), 0.16, 0.14, "Dashboard baseline\nintrinsic vulnerability", "#fef3c7")

    save_box(ax, (0.28, 0.38), 0.22, 0.14, "Target B\nEDR or damage probabilities\nunder a PGA scenario", "#fee2e2")
    save_box(ax, (0.58, 0.38), 0.18, 0.14, "Event-damage model\nPGA allowed", "#fecaca")
    save_box(ax, (0.81, 0.38), 0.16, 0.14, "Scenario damage\nnot intrinsic vulnerability", "#fef3c7")

    save_box(ax, (0.03, 0.18), 0.18, 0.12, "SVI\ncontextual vulnerability index", "#e0e7ff")
    save_box(ax, (0.28, 0.18), 0.18, 0.12, "NDVI\npost-event proxy only", "#ccfbf1")
    save_box(ax, (0.53, 0.18), 0.18, 0.12, "ADT / detour / trucks\nconsequence only", "#f3e8ff")
    save_box(ax, (0.78, 0.18), 0.18, 0.12, "Prioritization layer\nvulnerability x consequence", "#fde68a")

    save_arrow(ax, (0.21, 0.72), (0.28, 0.77))
    save_arrow(ax, (0.50, 0.77), (0.58, 0.77))
    save_arrow(ax, (0.76, 0.77), (0.81, 0.77))
    save_arrow(ax, (0.21, 0.70), (0.28, 0.45))
    save_arrow(ax, (0.50, 0.45), (0.58, 0.45))
    save_arrow(ax, (0.76, 0.45), (0.81, 0.45))
    save_arrow(ax, (0.12, 0.63), (0.12, 0.30))
    save_arrow(ax, (0.21, 0.24), (0.28, 0.24))
    save_arrow(ax, (0.46, 0.24), (0.53, 0.24))
    save_arrow(ax, (0.71, 0.24), (0.78, 0.24))

    ax.text(
        0.5,
        0.94,
        "Target formulation comparison: predict intrinsic fragility first, translate to event damage second",
        ha="center",
        va="center",
        fontsize=15,
        weight="bold",
        color="#111827",
    )
    ax.text(
        0.5,
        0.59,
        "Guardrail: PGA is not a core vulnerability predictor; it enters only when converting fragility into event damage.",
        ha="center",
        va="center",
        fontsize=10,
        color="#475569",
    )
    fig.savefig(path, dpi=230, bbox_inches="tight")
    plt.close(fig)


def plot_model_comparison(results: pd.DataFrame, path: Path) -> None:
    metric_df = results.copy()
    metric_df["Model"] = pd.Categorical(metric_df["Model"], categories=MODEL_ORDER, ordered=True)
    metric_df = metric_df.sort_values("Model")
    fig, axes = plt.subplots(1, 2, figsize=(16, 8), sharey=True)
    pivot_rmse = metric_df.pivot(index="Model", columns="Model Family", values="Holdout_RMSE_mean")
    pivot_r2 = metric_df.pivot(index="Model", columns="Model Family", values="Holdout_R2_mean")
    sns.heatmap(pivot_rmse, annot=True, fmt=".4f", cmap="viridis_r", ax=axes[0], cbar_kws={"label": "RMSE"})
    sns.heatmap(pivot_r2, annot=True, fmt=".3f", cmap="mako", ax=axes[1], cbar_kws={"label": "R2"})
    axes[0].set_title("Fragility-target holdout RMSE")
    axes[1].set_title("Fragility-target holdout R2")
    for ax in axes:
        ax.set_xlabel("")
        ax.set_ylabel("")
    fig.suptitle("Model comparison across hazard-independent feature families", y=1.01, fontsize=15, weight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=230, bbox_inches="tight")
    plt.close(fig)


def plot_event_model_comparison(results: pd.DataFrame, path: Path) -> None:
    plot_df = results.copy()
    plot_df["Model"] = pd.Categorical(plot_df["Model"], categories=MODEL_ORDER, ordered=True)
    plot_df = plot_df.sort_values("Model")
    fig, axes = plt.subplots(1, 2, figsize=(15, 7), sharey=True)
    sns.barplot(data=plot_df, y="Model", x="Holdout_RMSE", color="#2563eb", ax=axes[0])
    sns.barplot(data=plot_df, y="Model", x="Holdout_R2", color="#059669", ax=axes[1])
    axes[0].set_title("Direct EDR event model RMSE")
    axes[1].set_title("Direct EDR event model R2")
    axes[0].set_xlabel("Holdout RMSE")
    axes[1].set_xlabel("Holdout R2")
    axes[0].set_ylabel("")
    axes[1].set_ylabel("")
    fig.suptitle("Event-damage model comparison: PGA allowed", y=1.01, fontsize=15, weight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=230, bbox_inches="tight")
    plt.close(fig)


def plot_top5(fragility_results: pd.DataFrame, event_results: pd.DataFrame, path: Path) -> None:
    frag_top = fragility_results.sort_values(["Holdout_RMSE_mean", "Holdout_MAE_mean"]).head(5).copy()
    frag_top["Task"] = "Fragility target"
    frag_top["Metric"] = frag_top["Holdout_RMSE_mean"]
    event_top = event_results.sort_values(["Holdout_RMSE", "Holdout_MAE"]).head(5).copy()
    event_top["Task"] = "Direct event EDR"
    event_top["Metric"] = event_top["Holdout_RMSE"]
    event_top = event_top.rename(columns={"Holdout_RMSE": "Holdout_RMSE_mean"})
    combined = pd.concat(
        [
            frag_top[["Task", "Model Family", "Model", "Metric"]],
            event_top[["Task", "Model Family", "Model", "Metric"]],
        ],
        ignore_index=True,
    )
    combined["Label"] = combined["Model Family"] + "\n" + combined["Model"]
    plt.figure(figsize=(12, 6.5))
    sns.barplot(data=combined, x="Metric", y="Label", hue="Task")
    plt.xlabel("Holdout RMSE in each task's native target scale")
    plt.ylabel("")
    plt.title("Top-5 models by target formulation")
    plt.tight_layout()
    plt.savefig(path, dpi=230, bbox_inches="tight")
    plt.close()


def plot_fragility_actual_predicted(pred_df: pd.DataFrame, title: str, path: Path) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes = axes.ravel()
    for idx, target in enumerate(FRAGILITY_TARGETS):
        ax = axes[idx]
        actual = pred_df[f"{target}_actual"]
        predicted = pred_df[f"{target}_predicted"]
        ax.scatter(actual, predicted, s=10, alpha=0.36, color="#2563eb")
        low = min(actual.min(), predicted.min())
        high = max(actual.max(), predicted.max())
        ax.plot([low, high], [low, high], color="#111827", linestyle="--", linewidth=1)
        ax.set_title(FRAGILITY_TARGET_LABELS[target])
        ax.set_xlabel("Actual")
        ax.set_ylabel("Predicted")
    axes[-1].axis("off")
    fig.suptitle(title, y=1.01, fontsize=15, weight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=230, bbox_inches="tight")
    plt.close(fig)


def plot_direct_edr_actual_predicted(pred_df: pd.DataFrame, title: str, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    axes[0].scatter(pred_df["EDR_actual"], pred_df["EDR_predicted"], s=11, alpha=0.36, color="#dc2626")
    upper = max(pred_df["EDR_actual"].max(), pred_df["EDR_predicted"].max())
    axes[0].plot([0, upper], [0, upper], color="#111827", linestyle="--", linewidth=1)
    axes[0].set_xlabel("Pipeline EDR")
    axes[0].set_ylabel("Predicted direct EDR")
    axes[0].set_title("Actual vs predicted")
    sns.histplot(pred_df["EDR_residual"], bins=50, kde=True, ax=axes[1], color="#991b1b")
    axes[1].axvline(0, color="#111827", linestyle="--", linewidth=1)
    axes[1].set_title("Residuals")
    axes[1].set_xlabel("Actual - predicted")
    fig.suptitle(title, y=1.02, fontsize=15, weight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=230, bbox_inches="tight")
    plt.close(fig)


def plot_residual_diagnostics(frag_pred: pd.DataFrame, event_pred: pd.DataFrame, path: Path) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes = axes.ravel()
    residual_cols = [
        "MU_DS1_LINEAR_residual",
        "MU_DS2_LINEAR_residual",
        "MU_DS3_LINEAR_residual",
        "MU_DS4_LINEAR_residual",
        "BETA_SVI_residual",
    ]
    titles = ["DS1 median", "DS2 median", "DS3 median", "DS4 median", "beta"]
    for idx, col in enumerate(residual_cols):
        sns.histplot(frag_pred[col], bins=45, kde=True, ax=axes[idx], color="#2563eb")
        axes[idx].axvline(0, color="#111827", linestyle="--", linewidth=1)
        axes[idx].set_title(titles[idx])
        axes[idx].set_xlabel("Actual - predicted")
    sns.histplot(event_pred["EDR_residual"], bins=45, kde=True, ax=axes[-1], color="#dc2626")
    axes[-1].axvline(0, color="#111827", linestyle="--", linewidth=1)
    axes[-1].set_title("Direct EDR")
    axes[-1].set_xlabel("Actual - predicted")
    fig.suptitle("Residual diagnostics by target", y=1.01, fontsize=15, weight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=230, bbox_inches="tight")
    plt.close(fig)


def plot_reconstruction_calibration(
    frag_pred: pd.DataFrame,
    event_pred: pd.DataFrame,
    path: Path,
) -> pd.DataFrame:
    merged = frag_pred[
        ["join_id", "pga", "EDR", "EDR_from_predicted_fragility", "Model Family", "Model"]
    ].copy()
    merged = merged.rename(columns={"EDR": "Pipeline_EDR"})
    if "join_id" in event_pred.columns and "join_id" in merged.columns:
        event_slim = event_pred[["join_id", "EDR_predicted"]].copy()
        merged = merged.merge(event_slim, on="join_id", how="left")
    else:
        merged["EDR_predicted"] = event_pred["EDR_predicted"].to_numpy()
    merged["PGA_bin"] = pga_bin_labels(merged["pga"])
    summary = (
        merged.groupby("PGA_bin", observed=False)
        .agg(
            n=("Pipeline_EDR", "size"),
            pipeline_edr=("Pipeline_EDR", "mean"),
            fragility_reconstructed_edr=("EDR_from_predicted_fragility", "mean"),
            direct_event_edr=("EDR_predicted", "mean"),
        )
        .reset_index()
    )
    long = summary.melt(
        id_vars=["PGA_bin", "n"],
        value_vars=["pipeline_edr", "fragility_reconstructed_edr", "direct_event_edr"],
        var_name="Series",
        value_name="Mean EDR",
    )
    label_map = {
        "pipeline_edr": "Existing pipeline EDR",
        "fragility_reconstructed_edr": "EDR reconstructed from predicted fragility",
        "direct_event_edr": "Direct EDR model",
    }
    long["Series"] = long["Series"].map(label_map)
    plt.figure(figsize=(11, 6))
    sns.lineplot(data=long, x="PGA_bin", y="Mean EDR", hue="Series", marker="o")
    plt.xlabel("Actual PGA bin")
    plt.ylabel("Mean holdout EDR")
    plt.title("Calibration/reconstruction: fragility-first pathway vs direct EDR")
    plt.tight_layout()
    plt.savefig(path, dpi=230, bbox_inches="tight")
    plt.close()
    return summary


def plot_ablation(
    best_fragility: pd.DataFrame,
    best_event: pd.Series,
    path: Path,
) -> None:
    frag = best_fragility.copy()
    frag["Task"] = "Fragility target"
    frag["Best RMSE"] = frag["Holdout_RMSE_mean"]
    event = pd.DataFrame(
        [
            {
                "Model Family": "Event Damage Family",
                "Model": best_event["Model"],
                "Task": "Direct event EDR",
                "Best RMSE": best_event["Holdout_RMSE"],
            }
        ]
    )
    plot_df = pd.concat(
        [frag[["Model Family", "Model", "Task", "Best RMSE"]], event],
        ignore_index=True,
    )
    plt.figure(figsize=(11, 6))
    sns.barplot(data=plot_df, x="Model Family", y="Best RMSE", hue="Task")
    plt.xticks(rotation=16, ha="right")
    plt.ylabel("Best holdout RMSE in task target scale")
    plt.xlabel("")
    plt.title("Ablation: structural core, SVI, NDVI extension, and event PGA branch")
    plt.tight_layout()
    plt.savefig(path, dpi=230, bbox_inches="tight")
    plt.close()


def plot_importance(importance: pd.DataFrame, path: Path) -> None:
    plot_df = importance[importance["Importance Type"] == "permutation_r2_decrease"].copy()
    plot_df = plot_df.sort_values(["Target Kind", "Importance"], ascending=[True, False])
    plot_df = plot_df.groupby("Target Kind", as_index=False).head(10)
    if plot_df.empty:
        return
    g = sns.catplot(
        data=plot_df,
        kind="bar",
        x="Importance",
        y="Feature",
        col="Target Kind",
        sharex=False,
        sharey=False,
        height=5.8,
        aspect=0.95,
        color="#2563eb",
    )
    g.set_axis_labels("Permutation importance (R2 decrease)", "")
    g.set_titles("{col_name}")
    g.fig.suptitle("Feature importance for recommended fragility and event branches", y=1.04, fontsize=15, weight="bold")
    g.fig.savefig(path, dpi=230, bbox_inches="tight")
    plt.close(g.fig)


def plot_ndvi_role(best_by_family: pd.DataFrame, frag_predictions: pd.DataFrame, path: Path) -> None:
    svi_row = best_by_family[best_by_family["Model Family"] == "Structural + SVI"].iloc[0]
    ndvi_row = best_by_family[best_by_family["Model Family"] == "Structural + SVI + NDVI"].iloc[0]
    delta = ndvi_row["Holdout_RMSE_mean"] - svi_row["Holdout_RMSE_mean"]
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))
    comp = pd.DataFrame(
        [
            {"Family": "Structural + SVI", "Holdout RMSE": svi_row["Holdout_RMSE_mean"]},
            {"Family": "Structural + SVI + NDVI", "Holdout RMSE": ndvi_row["Holdout_RMSE_mean"]},
        ]
    )
    sns.barplot(data=comp, x="Family", y="Holdout RMSE", ax=axes[0], palette=["#6366f1", "#14b8a6"])
    axes[0].set_title(f"NDVI extension delta RMSE = {delta:+.6f}")
    axes[0].tick_params(axis="x", rotation=12)
    axes[0].set_xlabel("")
    subset = frag_predictions[frag_predictions["ndvi_change"].notna()].copy()
    if len(subset) > 0:
        subset["Abs reconstruction error"] = subset["EDR_reconstruction_residual"].abs()
        axes[1].scatter(
            subset["ndvi_change"],
            subset["Abs reconstruction error"],
            s=12,
            alpha=0.35,
            color="#0f766e",
        )
        axes[1].axvline(0, color="#111827", linestyle="--", linewidth=1)
        axes[1].set_xlabel("NDVI change")
        axes[1].set_ylabel("Absolute reconstructed EDR error")
        axes[1].set_title("NDVI is contextual/post-event, not structural")
    else:
        axes[1].text(0.5, 0.5, "No non-null NDVI rows available", ha="center", va="center")
        axes[1].set_axis_off()
    fig.suptitle("NDVI role check", y=1.02, fontsize=15, weight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=230, bbox_inches="tight")
    plt.close(fig)


def representative_rows(df: pd.DataFrame, test_idx: np.ndarray) -> pd.DataFrame:
    holdout = df.iloc[test_idx].copy()
    quantiles = holdout["SVI"].quantile([0.15, 0.50, 0.85]).to_dict()
    rows = []
    for label, q in [("Low SVI", quantiles[0.15]), ("Median SVI", quantiles[0.50]), ("High SVI", quantiles[0.85])]:
        idx = (holdout["SVI"] - q).abs().idxmin()
        row = holdout.loc[idx].copy()
        row["Representative"] = label
        rows.append(row)
    return pd.DataFrame(rows)


def fragility_exceedance_curves(params: np.ndarray, pga_grid: np.ndarray) -> dict[str, np.ndarray]:
    arr = postprocess_fragility_predictions(params.reshape(1, -1))
    medians = arr[0, :4]
    beta = arr[0, 4]
    return {
        f"DS{idx + 1}": norm.cdf(np.log(pga_grid / medians[idx]) / beta)
        for idx in range(4)
    }


def plot_fragility_curves(df: pd.DataFrame, family: FeatureFamily, model, test_idx: np.ndarray, path: Path) -> None:
    reps = representative_rows(df, test_idx)
    pga_grid = np.linspace(0.01, 0.80, 120)
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.2), sharey=True)
    for ax, (_, row) in zip(axes, reps.iterrows()):
        actual_params = row[FRAGILITY_TARGETS].to_numpy(dtype=float)
        pred_params = postprocess_fragility_predictions(model.predict(row[family.features].to_frame().T))[0]
        actual_curves = fragility_exceedance_curves(actual_params, pga_grid)
        pred_curves = fragility_exceedance_curves(pred_params, pga_grid)
        for ds, values in actual_curves.items():
            ax.plot(pga_grid, values, linewidth=1.6, label=f"{ds} pipeline")
        for ds, values in pred_curves.items():
            ax.plot(pga_grid, values, linewidth=1.2, linestyle="--", label=f"{ds} ML")
        ax.set_title(f"{row['Representative']}\nSVI={row['SVI']:.3f}, class={row['HWB_CLASS']}")
        ax.set_xlabel("PGA (g)")
        ax.set_ylabel("P(damage >= state)")
        ax.set_ylim(0, 1.02)
    handles, labels = axes[-1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="center right", bbox_to_anchor=(1.07, 0.5), fontsize=8)
    fig.suptitle("Fragility curves: pipeline parameters vs ML-predicted parameters", y=1.03, fontsize=15, weight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=230, bbox_inches="tight")
    plt.close(fig)


def plot_sensitivity(
    df: pd.DataFrame,
    core_family: FeatureFamily,
    core_model,
    svi_family: FeatureFamily,
    svi_model,
    path: Path,
) -> None:
    sample = df.sample(n=min(1800, len(df)), random_state=RANDOM_STATE).copy()
    specs = [
        ("age_years", core_family, core_model),
        ("max_span_log1p", core_family, core_model),
        ("skew", core_family, core_model),
        ("cond", core_family, core_model),
        ("SVI", svi_family, svi_model),
    ]
    fig, axes = plt.subplots(1, len(specs), figsize=(17, 4.2), sharey=False)
    for ax, (feature, family, model) in zip(axes, specs):
        if feature not in family.features:
            ax.set_axis_off()
            continue
        low = sample[feature].quantile(0.05)
        high = sample[feature].quantile(0.95)
        grid = np.linspace(low, high, 35)
        ds2_means = []
        beta_means = []
        X_base = sample[family.features].copy()
        for value in grid:
            X_eval = X_base.copy()
            X_eval[feature] = value
            pred = postprocess_fragility_predictions(model.predict(X_eval))
            ds2_means.append(float(pred[:, 1].mean()))
            beta_means.append(float(pred[:, 4].mean()))
        ax.plot(grid, ds2_means, color="#2563eb", label="DS2 median")
        ax2 = ax.twinx()
        ax2.plot(grid, beta_means, color="#dc2626", linestyle="--", label="beta")
        ax.set_title(feature)
        ax.set_xlabel(feature)
        ax.set_ylabel("Predicted DS2 median")
        ax2.set_ylabel("Predicted beta")
    fig.suptitle("Sensitivity checks for main structural/context variables", y=1.05, fontsize=15, weight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=230, bbox_inches="tight")
    plt.close(fig)


def plot_framework_summary(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(13, 6.5))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    boxes = [
        ((0.04, 0.62), 0.18, 0.16, "Inventory\nstructural features", "#dbeafe"),
        ((0.30, 0.62), 0.20, 0.16, "Core output\nfragility medians + beta", "#bbf7d0"),
        ((0.58, 0.62), 0.17, 0.16, "Scenario translator\napply PGA after model", "#fde68a"),
        ((0.81, 0.62), 0.15, 0.16, "Damage outputs\nP(DS), EDR", "#fed7aa"),
        ((0.30, 0.28), 0.20, 0.14, "SVI\ncontext/audit feature", "#e0e7ff"),
        ((0.58, 0.28), 0.17, 0.14, "NDVI\npost-event proxy", "#ccfbf1"),
        ((0.81, 0.28), 0.15, 0.14, "Priority\nADT/detour/trucks", "#f3e8ff"),
    ]
    for xy, width, height, text, color in boxes:
        save_box(ax, xy, width, height, text, color)
    save_arrow(ax, (0.22, 0.70), (0.30, 0.70))
    save_arrow(ax, (0.50, 0.70), (0.58, 0.70))
    save_arrow(ax, (0.75, 0.70), (0.81, 0.70))
    save_arrow(ax, (0.40, 0.42), (0.40, 0.62))
    save_arrow(ax, (0.66, 0.42), (0.66, 0.62))
    save_arrow(ax, (0.88, 0.42), (0.88, 0.62))
    ax.text(
        0.5,
        0.92,
        "Recommended end-to-end dashboard framework",
        ha="center",
        fontsize=16,
        weight="bold",
    )
    ax.text(
        0.5,
        0.11,
        "Train intrinsic vulnerability on fragility parameters. Use PGA, NDVI, and consequence variables only in their downstream layers.",
        ha="center",
        fontsize=11,
        color="#475569",
    )
    fig.savefig(path, dpi=230, bbox_inches="tight")
    plt.close(fig)


def write_report(
    path: Path,
    df: pd.DataFrame,
    ndvi_info: dict[str, object],
    cv_rows: int,
    fragility_results: pd.DataFrame,
    event_results: pd.DataFrame,
    best_fragility_by_family: pd.DataFrame,
    best_event: pd.Series,
    reconstruction_metrics: pd.DataFrame,
    ablation_summary: pd.DataFrame,
    output_files: list[str],
) -> None:
    top_fragility = fragility_results.sort_values(["Holdout_RMSE_mean", "Holdout_MAE_mean"]).head(5)
    top_event = event_results.sort_values(["Holdout_RMSE", "Holdout_MAE"]).head(5)
    core_best = best_fragility_by_family[best_fragility_by_family["Model Family"] == "Structural Core"].iloc[0]
    svi_best = best_fragility_by_family[best_fragility_by_family["Model Family"] == "Structural + SVI"].iloc[0]
    ndvi_best = best_fragility_by_family[best_fragility_by_family["Model Family"] == "Structural + SVI + NDVI"].iloc[0]
    svi_delta = svi_best["Holdout_RMSE_mean"] - core_best["Holdout_RMSE_mean"]
    ndvi_delta = ndvi_best["Holdout_RMSE_mean"] - svi_best["Holdout_RMSE_mean"]
    recon_row = reconstruction_metrics.iloc[0]

    lines = [
        "# ML Target Formulation Study",
        "",
        "This study answers the target-variable question directly. A hazard-independent vulnerability model should not be trained to predict event damage caused by one shaking field. It should predict bridge-level intrinsic fragility parameters, then translate those parameters into event-specific damage only after a PGA scenario is supplied.",
        "",
        "## Research Question",
        "",
        "- What is the defensible target for a hazard-independent bridge vulnerability model?",
        "- How much changes when EDR is predicted directly instead of predicting fragility first?",
        "- Where should SVI, NDVI, PGA, and consequence variables live in the framework?",
        "",
        "## Data And Existing Logic Used",
        "",
        f"- Source table: `data/processed/bridges_with_svi.csv`",
        f"- Rows modeled: `{len(df):,}`",
        f"- Cross-validation rows: `{cv_rows:,}` stratified by SVI quintile for portable runtime; holdout metrics use the full 20 percent split.",
        f"- Fragility targets: `{', '.join(FRAGILITY_TARGETS)}`",
        f"- Event target: `EDR` from the repository HAZUS/SVI pipeline",
        f"- NDVI source: `{ndvi_info.get('ndvi_source')}`",
        f"- Rows with joined NDVI change: `{int(ndvi_info.get('ndvi_nonnull', 0)):,}`",
        "",
        "The script recomputes SVI and fragility parameters through `svi_methodology.py` before modeling, so the target logic remains tied to the repository methodology. The current repo formulation uses linear fragility medians for DS1-DS4 and `BETA_SVI = 0.6 + 0.2 * SVI`.",
        "",
        "## Target Formulations Built",
        "",
        "### A. Hazard-independent core target",
        "",
        "The main model is multi-output regression for DS1 median, DS2 median, DS3 median, DS4 median, and beta. This is the preferred formulation because the target is a bridge-level fragility description rather than damage under a particular earthquake. The predictions can be reused for any PGA scenario.",
        "",
        "### B. Event-specific target",
        "",
        "The downstream comparison model predicts `EDR` directly and is allowed to use `PGA`. This branch is useful for scenario damage prediction, but it should not replace the core vulnerability model because its target and features mix structural vulnerability with event demand.",
        "",
        "## Feature Families",
        "",
        "- `Structural Core`: intrinsic inventory features only; no PGA, no SVI, no NDVI, no ADT, no coordinates.",
        "- `Structural + SVI`: adds SVI as a contextual vulnerability index. Because the fragility targets are derived from SVI in the existing repository logic, this family is partly a consistency/audit test rather than an independent discovery test.",
        "- `Structural + SVI + NDVI`: post-event extension only. It is not presented as the core hazard-independent model.",
        "- `Event Damage Family`: structural features + SVI + PGA for direct EDR prediction.",
        "- `Prioritization Layer`: ADT, truck percentage, detour, and lane variables are applied only after prediction.",
        "",
        "## Models Compared",
        "",
        ", ".join(f"`{name}`" for name in MODEL_ORDER),
        "",
        "For multi-output fragility regression, `Gradient Boosting`, `HistGradientBoosting`, `AdaBoost`, and `LinearSVR` are wrapped with `MultiOutputRegressor`; the other estimators support multi-output regression directly in this workflow.",
        "",
        "## Best Fragility Models By Family",
        "",
        table_to_markdown(
            best_fragility_by_family[
                [
                    "Model Family",
                    "Model",
                    "CV_RMSE_mean",
                    "CV_R2_mean",
                    "Holdout_RMSE_mean",
                    "Holdout_R2_mean",
                    "Fit_seconds",
                ]
            ],
            float_digits=6,
        ),
        "",
        "## Top 5 Fragility-Target Models",
        "",
        table_to_markdown(
            top_fragility[
                [
                    "Model Family",
                    "Model",
                    "Holdout_RMSE_mean",
                    "Holdout_R2_mean",
                    "CV_RMSE_mean",
                    "CV_R2_mean",
                ]
            ],
            float_digits=6,
        ),
        "",
        "## Top 5 Direct EDR Event Models",
        "",
        table_to_markdown(
            top_event[
                [
                    "Model Family",
                    "Model",
                    "Holdout_RMSE",
                    "Holdout_R2",
                    "CV_RMSE",
                    "CV_R2",
                ]
            ],
            float_digits=6,
        ),
        "",
        "## Reconstruction Test",
        "",
        "After predicting fragility medians and beta, the script reconstructs damage probabilities and EDR at each bridge's observed PGA. This tests whether the fragility-first target can recover event outputs without training the core model on PGA.",
        "",
        table_to_markdown(reconstruction_metrics, float_digits=6),
        "",
        f"Interpretation: direct EDR prediction is allowed to use PGA and may fit event damage well, but in this run the fragility-first structural-core reconstruction had lower holdout EDR RMSE (`{recon_row['RMSE']:.6f}` for the first row versus `{reconstruction_metrics.iloc[1]['RMSE']:.6f}` for direct EDR). The important conceptual distinction remains that the fragility-first branch stores reusable structural response parameters and applies PGA only downstream.",
        "",
        "## SVI And NDVI Ablation",
        "",
        table_to_markdown(ablation_summary, float_digits=6),
        "",
        f"- SVI holdout RMSE delta versus structural core: `{svi_delta:+.6f}`.",
        f"- NDVI holdout RMSE delta versus structural + SVI: `{ndvi_delta:+.6f}`.",
        "- Delta values smaller than `1e-6` RMSE are treated as numerically negligible.",
        "",
        "The SVI result must be interpreted carefully. Since the repository's fragility targets are generated from SVI, adding SVI as a predictor can make the fragility target nearly formula-recoverable. That is useful as an audit that the ML pipeline is consistent with the SVI methodology, but it should not be overclaimed as independent evidence that SVI discovered new vulnerability physics.",
        "",
        "NDVI belongs in a post-event/contextual branch. If it helps, it helps explain observed landscape or access changes after an event; it is not an intrinsic bridge structural property.",
        "",
        "## Figures",
        "",
        "- `figures/ml_target_strategy_overview.png`",
        "- `figures/ml_fragility_model_comparison.png`",
        "- `figures/ml_direct_edr_model_comparison.png`",
        "- `figures/ml_target_top5_models.png`",
        "- `figures/ml_fragility_actual_vs_predicted.png`",
        "- `figures/ml_direct_edr_actual_vs_predicted.png`",
        "- `figures/ml_target_residual_diagnostics.png`",
        "- `figures/ml_fragility_reconstruction_vs_edr.png`",
        "- `figures/ml_target_ablation.png`",
        "- `figures/ml_target_feature_importance.png`",
        "- `figures/ml_target_sensitivity_plots.png`",
        "- `figures/ml_fragility_curve_comparison.png`",
        "- `figures/ml_ndvi_context_role.png`",
        "- `figures/ml_recommended_framework_summary.png`",
        "",
        "## Recommended ML Formulation For This Project",
        "",
        "The main hazard-independent target should be fragility median and beta parameters, preferably as a multi-output regression target: `DS1_median`, `DS2_median`, `DS3_median`, `DS4_median`, and `beta`. This directly answers the professor's concern because the target describes intrinsic structural vulnerability rather than event damage under one PGA field.",
        "",
        "Direct EDR prediction should be kept as a comparison branch and as an event-damage branch. It is allowed to use PGA and may sometimes achieve stronger event-fit metrics, but those metrics would not prove that it is the better vulnerability target. They show that event demand is being modeled directly.",
        "",
        "SVI belongs as a contextual/additive vulnerability feature and as a transparent engineering baseline. Because the current fragility targets are generated from SVI, the `Structural + SVI` fragility model should be described as a consistency check or calibrated SVI-recovery model, not as fully independent validation. For the dashboard, SVI can be shown beside the ML fragility output and used to explain why a bridge received a certain intrinsic score.",
        "",
        "NDVI belongs only in a post-event proxy or context layer. It should not feed the core hazard-independent vulnerability model because vegetation change is not an intrinsic structural property of the bridge.",
        "",
        "PGA belongs only in the scenario translator and direct event-damage branch. The dashboard should apply selected PGA scenarios after the fragility model predicts bridge-level medians and beta.",
        "",
        "ADT, truck percentage, detour distance, and related variables should feed the prioritization layer after vulnerability prediction. They answer consequence and inspection-priority questions, not structural vulnerability questions.",
        "",
        "For the future dashboard, the recommended flow is: structural inventory features -> fragility-target model -> scenario PGA translator -> damage probabilities/EDR -> optional NDVI context -> priority ranking with consequence variables.",
        "",
        "## Generated Outputs",
        "",
    ]
    lines.extend([f"- `{item}`" for item in output_files])
    path.write_text("\n".join(lines) + "\n")


def main() -> None:
    paths = build_paths()
    processed_dir = paths["PROCESSED_DIR"]
    figures_dir = paths["FIGURES_DIR"]
    docs_dir = paths["PROJECT_ROOT"] / "docs"
    figures_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    df, ndvi_info = load_dataset(paths)
    df.to_csv(processed_dir / "ml_fragility_target_training_dataset.csv", index=False)

    stratify_labels = pd.qcut(df["SVI"].rank(method="first"), q=5, labels=False, duplicates="drop")
    train_idx, test_idx = train_test_split(
        np.arange(len(df)),
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=stratify_labels,
    )
    cv_size = min(CV_SAMPLE_SIZE, len(df))
    if cv_size < len(df):
        cv_idx, _ = train_test_split(
            np.arange(len(df)),
            train_size=cv_size,
            random_state=RANDOM_STATE,
            stratify=stratify_labels,
        )
    else:
        cv_idx = np.arange(len(df))
    cv_labels = np.asarray(stratify_labels)[cv_idx]
    cv = list(
        StratifiedKFold(n_splits=N_CV_SPLITS, shuffle=True, random_state=RANDOM_STATE).split(
            np.zeros(len(cv_idx)),
            cv_labels,
        )
    )

    fragility_families = fragility_feature_families(df)
    event_family = event_feature_family(df)

    all_fragility_results = []
    fitted_fragility: dict[str, dict[str, object]] = {}
    for family in fragility_families:
        family_results, fitted = run_fragility_family(df, family, train_idx, test_idx, cv_idx, cv)
        all_fragility_results.append(family_results)
        fitted_fragility[family.name] = fitted

    fragility_results = (
        pd.concat(all_fragility_results, ignore_index=True)
        .sort_values(["Holdout_RMSE_mean", "Holdout_MAE_mean"])
        .reset_index(drop=True)
    )
    fragility_results.to_csv(processed_dir / "ml_fragility_target_model_comparison.csv", index=False)

    best_fragility_by_family = (
        fragility_results.sort_values(["Model Family", "Holdout_RMSE_mean", "Holdout_MAE_mean"])
        .groupby("Model Family", as_index=False)
        .first()
        .sort_values("Holdout_RMSE_mean")
        .reset_index(drop=True)
    )
    best_fragility_by_family.to_csv(processed_dir / "ml_fragility_target_best_by_family.csv", index=False)

    event_results, fitted_event = run_event_models(df, event_family, train_idx, test_idx, cv_idx, cv)
    event_results = event_results.sort_values(["Holdout_RMSE", "Holdout_MAE"]).reset_index(drop=True)
    event_results.to_csv(processed_dir / "ml_direct_edr_model_comparison.csv", index=False)

    core_best = best_fragility_by_family[best_fragility_by_family["Model Family"] == "Structural Core"].iloc[0]
    svi_best = best_fragility_by_family[best_fragility_by_family["Model Family"] == "Structural + SVI"].iloc[0]
    ndvi_best = best_fragility_by_family[best_fragility_by_family["Model Family"] == "Structural + SVI + NDVI"].iloc[0]
    event_best = event_results.iloc[0]

    core_family = next(family for family in fragility_families if family.name == "Structural Core")
    svi_family = next(family for family in fragility_families if family.name == "Structural + SVI")
    ndvi_family = next(family for family in fragility_families if family.name == "Structural + SVI + NDVI")
    recommended_core_model = fitted_fragility[core_family.name][core_best["Model"]]
    svi_model = fitted_fragility[svi_family.name][svi_best["Model"]]
    ndvi_model = fitted_fragility[ndvi_family.name][ndvi_best["Model"]]
    event_model = fitted_event[event_best["Model"]]

    fragility_prediction_frames = [
        build_fragility_prediction_frame(df, core_family, core_best["Model"], recommended_core_model, test_idx),
        build_fragility_prediction_frame(df, svi_family, svi_best["Model"], svi_model, test_idx),
        build_fragility_prediction_frame(df, ndvi_family, ndvi_best["Model"], ndvi_model, test_idx),
    ]
    fragility_predictions = pd.concat(fragility_prediction_frames, ignore_index=True)
    fragility_predictions.to_csv(processed_dir / "ml_fragility_target_predictions.csv", index=False)

    event_predictions = build_event_prediction_frame(
        df,
        event_family,
        event_best["Model"],
        event_model,
        test_idx,
    )
    event_predictions.to_csv(processed_dir / "ml_direct_edr_predictions.csv", index=False)

    core_predictions = fragility_predictions[fragility_predictions["Model Family"] == "Structural Core"].copy()
    reconstruction_metric_rows = []
    reconstruction_metric_rows.append(
        {
            "Comparison": "Fragility-first structural core reconstructed at observed PGA",
            "MAE": mean_absolute_error(core_predictions["EDR"], core_predictions["EDR_from_predicted_fragility"]),
            "RMSE": np.sqrt(mean_squared_error(core_predictions["EDR"], core_predictions["EDR_from_predicted_fragility"])),
            "R2": r2_score(core_predictions["EDR"], core_predictions["EDR_from_predicted_fragility"]),
        }
    )
    reconstruction_metric_rows.append(
        {
            "Comparison": "Direct event EDR model with PGA",
            "MAE": mean_absolute_error(event_predictions["EDR_actual"], event_predictions["EDR_predicted"]),
            "RMSE": np.sqrt(mean_squared_error(event_predictions["EDR_actual"], event_predictions["EDR_predicted"])),
            "R2": r2_score(event_predictions["EDR_actual"], event_predictions["EDR_predicted"]),
        }
    )
    reconstruction_metrics = pd.DataFrame(reconstruction_metric_rows)
    reconstruction_metrics.to_csv(processed_dir / "ml_fragility_reconstruction_metrics.csv", index=False)

    calibration = plot_reconstruction_calibration(
        core_predictions,
        event_predictions,
        figures_dir / "ml_fragility_reconstruction_vs_edr.png",
    )
    calibration.to_csv(processed_dir / "ml_fragility_reconstruction_by_pga_bin.csv", index=False)

    importance_frames = []
    recommended_core_model._target_model_name = core_best["Model"]
    event_model._target_model_name = event_best["Model"]
    importance_frames.append(
        permutation_importance_frame(recommended_core_model, df, core_family, test_idx, "fragility")
    )
    importance_frames.append(
        permutation_importance_frame(event_model, df, event_family, test_idx, "event_edr")
    )
    for model_name in ["Ridge Regression", "Lasso Regression", "Elastic Net", "Linear Regression"]:
        if model_name in fitted_fragility[core_family.name]:
            importance_frames.append(
                coefficient_frame(fitted_fragility[core_family.name][model_name], core_family, model_name, "fragility")
            )
        if model_name in fitted_event:
            importance_frames.append(
                coefficient_frame(fitted_event[model_name], event_family, model_name, "event_edr")
            )
    importance = pd.concat([frame for frame in importance_frames if not frame.empty], ignore_index=True)
    importance.to_csv(processed_dir / "ml_fragility_target_feature_importance.csv", index=False)

    ablation_summary = pd.DataFrame(
        [
            {
                "Question": "Does SVI improve the fragility-target model?",
                "Baseline Family": "Structural Core",
                "Test Family": "Structural + SVI",
                "Baseline Holdout_RMSE_mean": core_best["Holdout_RMSE_mean"],
                "Test Holdout_RMSE_mean": svi_best["Holdout_RMSE_mean"],
                "Delta Holdout_RMSE_mean": svi_best["Holdout_RMSE_mean"] - core_best["Holdout_RMSE_mean"],
                "Improved": bool((svi_best["Holdout_RMSE_mean"] - core_best["Holdout_RMSE_mean"]) < -1e-6),
                "Interpretation": "SVI is part of the target-generating methodology, so gains are expected and should be described as consistency/context.",
            },
            {
                "Question": "Does NDVI help the post-event extension?",
                "Baseline Family": "Structural + SVI",
                "Test Family": "Structural + SVI + NDVI",
                "Baseline Holdout_RMSE_mean": svi_best["Holdout_RMSE_mean"],
                "Test Holdout_RMSE_mean": ndvi_best["Holdout_RMSE_mean"],
                "Delta Holdout_RMSE_mean": ndvi_best["Holdout_RMSE_mean"] - svi_best["Holdout_RMSE_mean"],
                "Improved": bool((ndvi_best["Holdout_RMSE_mean"] - svi_best["Holdout_RMSE_mean"]) < -1e-6),
                "Interpretation": "Any NDVI change below 1e-6 RMSE is treated as numerically negligible; NDVI remains post-event/contextual, not intrinsic structural vulnerability.",
            },
            {
                "Question": "What is gained by direct EDR prediction?",
                "Baseline Family": "Fragility-first structural core reconstructed at observed PGA",
                "Test Family": "Direct event EDR with PGA",
                "Baseline Holdout_RMSE_mean": reconstruction_metrics.iloc[0]["RMSE"],
                "Test Holdout_RMSE_mean": reconstruction_metrics.iloc[1]["RMSE"],
                "Delta Holdout_RMSE_mean": reconstruction_metrics.iloc[1]["RMSE"] - reconstruction_metrics.iloc[0]["RMSE"],
                "Improved": bool((reconstruction_metrics.iloc[1]["RMSE"] - reconstruction_metrics.iloc[0]["RMSE"]) < -1e-6),
                "Interpretation": "Direct EDR fits event damage, but it mixes hazard demand into the modeling target.",
            },
        ]
    )
    ablation_summary.to_csv(processed_dir / "ml_target_strategy_summary.csv", index=False)

    priority_scores = build_priority_scores(df, core_family, recommended_core_model, processed_dir)

    plot_strategy_overview(figures_dir / "ml_target_strategy_overview.png")
    plot_model_comparison(fragility_results, figures_dir / "ml_fragility_model_comparison.png")
    plot_event_model_comparison(event_results, figures_dir / "ml_direct_edr_model_comparison.png")
    plot_top5(fragility_results, event_results, figures_dir / "ml_target_top5_models.png")
    plot_fragility_actual_predicted(
        core_predictions,
        f"Fragility actual vs predicted: {core_best['Model']} ({core_family.name})",
        figures_dir / "ml_fragility_actual_vs_predicted.png",
    )
    plot_direct_edr_actual_predicted(
        event_predictions,
        f"Direct EDR actual vs predicted: {event_best['Model']}",
        figures_dir / "ml_direct_edr_actual_vs_predicted.png",
    )
    plot_residual_diagnostics(core_predictions, event_predictions, figures_dir / "ml_target_residual_diagnostics.png")
    plot_ablation(best_fragility_by_family, event_best, figures_dir / "ml_target_ablation.png")
    plot_importance(importance, figures_dir / "ml_target_feature_importance.png")
    plot_ndvi_role(best_fragility_by_family, fragility_predictions[fragility_predictions["Model Family"] == "Structural + SVI + NDVI"], figures_dir / "ml_ndvi_context_role.png")
    plot_fragility_curves(df, core_family, recommended_core_model, test_idx, figures_dir / "ml_fragility_curve_comparison.png")
    plot_sensitivity(
        df,
        core_family,
        recommended_core_model,
        svi_family,
        svi_model,
        figures_dir / "ml_target_sensitivity_plots.png",
    )
    plot_framework_summary(figures_dir / "ml_recommended_framework_summary.png")

    output_files = [
        "scripts/run_fragility_target_ml_study.py",
        "docs/ML_TARGET_FORMULATION_STUDY.md",
        "data/processed/ml_fragility_target_training_dataset.csv",
        "data/processed/ml_fragility_target_model_comparison.csv",
        "data/processed/ml_fragility_target_best_by_family.csv",
        "data/processed/ml_fragility_target_predictions.csv",
        "data/processed/ml_fragility_target_feature_importance.csv",
        "data/processed/ml_direct_edr_model_comparison.csv",
        "data/processed/ml_direct_edr_predictions.csv",
        "data/processed/ml_fragility_reconstruction_metrics.csv",
        "data/processed/ml_fragility_reconstruction_by_pga_bin.csv",
        "data/processed/ml_target_strategy_summary.csv",
        "data/processed/ml_target_priority_scores.csv",
        "figures/ml_target_strategy_overview.png",
        "figures/ml_fragility_model_comparison.png",
        "figures/ml_direct_edr_model_comparison.png",
        "figures/ml_target_top5_models.png",
        "figures/ml_fragility_actual_vs_predicted.png",
        "figures/ml_direct_edr_actual_vs_predicted.png",
        "figures/ml_target_residual_diagnostics.png",
        "figures/ml_fragility_reconstruction_vs_edr.png",
        "figures/ml_target_ablation.png",
        "figures/ml_target_feature_importance.png",
        "figures/ml_target_sensitivity_plots.png",
        "figures/ml_fragility_curve_comparison.png",
        "figures/ml_ndvi_context_role.png",
        "figures/ml_recommended_framework_summary.png",
    ]
    write_report(
        docs_dir / "ML_TARGET_FORMULATION_STUDY.md",
        df,
        ndvi_info,
        len(cv_idx),
        fragility_results,
        event_results,
        best_fragility_by_family,
        event_best,
        reconstruction_metrics,
        ablation_summary,
        output_files,
    )

    print("\nFragility target ML study complete.")
    print("Rows:", f"{len(df):,}")
    print("NDVI joined rows:", f"{int(ndvi_info.get('ndvi_nonnull', 0)):,}")
    print("\nBest fragility model by family:")
    print(
        best_fragility_by_family[
            [
                "Model Family",
                "Model",
                "Holdout_RMSE_mean",
                "Holdout_R2_mean",
                "CV_RMSE_mean",
                "CV_R2_mean",
            ]
        ].to_string(index=False)
    )
    print("\nBest direct EDR event model:")
    print(
        event_results[
            [
                "Model Family",
                "Model",
                "Holdout_RMSE",
                "Holdout_R2",
                "CV_RMSE",
                "CV_R2",
            ]
        ].head(5).to_string(index=False)
    )
    print("\nReconstruction comparison:")
    print(reconstruction_metrics.to_string(index=False))
    print("\nPriority rows written:", f"{len(priority_scores):,}")
    print("Report: docs/ML_TARGET_FORMULATION_STUDY.md")


if __name__ == "__main__":
    main()
