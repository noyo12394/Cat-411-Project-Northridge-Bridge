from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, cohen_kappa_score, confusion_matrix, f1_score, mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from catastrophe_model.damage_classification import DS_ORDER
from project_paths import build_paths, require_paths


SHORT_LABELS = {
    "DS0 – No Damage": "None",
    "DS1 – Slight": "Slight",
    "DS2 – Moderate": "Moderate",
    "DS3 – Extensive": "Extensive",
    "DS4 – Complete": "Complete",
}

ORDINAL_MAP = {label: idx for idx, label in enumerate(DS_ORDER)}
PROBABILITY_COLUMNS = ["P_DS0", "P_DS1", "P_DS2", "P_DS3", "P_DS4"]
FEATURE_COLUMNS = [
    "pga",
    "HWB_CLASS",
    "SVI",
    "year",
    "yr_recon",
    "spans",
    "max_span",
    "skew",
    "cond",
]
RANDOM_STATE = 42


def build_validation_table() -> pd.DataFrame:
    paths = build_paths()
    require_paths(paths, ["FINAL_ANALYSIS_CSV", "SVI_CSV"])

    proxy_df = pd.read_csv(paths["FINAL_ANALYSIS_CSV"], low_memory=False)
    hazus_df = pd.read_csv(paths["SVI_CSV"], low_memory=False)

    proxy_keep = ["join_id", "damage_state", "ndvi_chan", "avg_daily_", "bridge_id", "lat", "long"]
    proxy_keep = [col for col in proxy_keep if col in proxy_df.columns]
    proxy_df = proxy_df[proxy_keep].dropna(subset=["damage_state"]).copy()
    hazus_keep = ["join_id", *FEATURE_COLUMNS, *PROBABILITY_COLUMNS, "EDR"]
    hazus_df = hazus_df[hazus_keep].copy()

    merged = proxy_df.merge(hazus_df, on="join_id", how="inner", validate="one_to_one")
    merged = merged.dropna(subset=["damage_state"]).copy()
    merged["observed_state"] = merged["damage_state"]
    merged["observed_code"] = merged["observed_state"].map(ORDINAL_MAP)

    hazus_probs = merged[PROBABILITY_COLUMNS].to_numpy()
    merged["hazus_pred_code"] = hazus_probs.argmax(axis=1)
    merged["hazus_pred_state"] = [DS_ORDER[idx] for idx in merged["hazus_pred_code"]]

    return merged


def make_classifier() -> Pipeline:
    numeric_features = [col for col in FEATURE_COLUMNS if col != "HWB_CLASS"]
    categorical_features = ["HWB_CLASS"]

    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, numeric_features),
            ("cat", categorical_pipe, categorical_features),
        ],
        remainder="drop",
        sparse_threshold=0,
    )

    model = ExtraTreesClassifier(
        n_estimators=300,
        min_samples_leaf=1,
        random_state=RANDOM_STATE,
        class_weight="balanced",
        n_jobs=1,
    )

    return Pipeline([
        ("prep", preprocessor),
        ("model", model),
    ])


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    diffs = y_pred - y_true
    return {
        "Exact_Accuracy": accuracy_score(y_true, y_pred),
        "Within_1_State_Accuracy": float(np.mean(np.abs(diffs) <= 1)),
        "MAE_Ordinal": mean_absolute_error(y_true, y_pred),
        "Weighted_Kappa": cohen_kappa_score(y_true, y_pred, weights="quadratic"),
        "Macro_F1": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "Underprediction_Rate": float(np.mean(diffs < 0)),
        "Overprediction_Rate": float(np.mean(diffs > 0)),
        "Severe_Underprediction_Rate": float(np.mean(diffs <= -2)),
    }


def plot_confusions(y_true, hazus_pred, hybrid_pred, save_path: Path) -> None:
    labels = list(range(len(DS_ORDER)))
    label_names = [SHORT_LABELS[ds] for ds in DS_ORDER]
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    matrices = [
        ("Univariate (HAZUS)", hazus_pred),
        ("Hybrid Proxy Model", hybrid_pred),
    ]

    for ax, (title, pred) in zip(axes, matrices):
        cm = confusion_matrix(y_true, pred, labels=labels)
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            cbar=True,
            xticklabels=label_names,
            yticklabels=label_names,
            ax=ax,
        )
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Observed")
        ax.set_title(title)

    plt.suptitle("Proxy Validation Confusion Matrices")
    plt.tight_layout()
    fig.savefig(save_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def write_summary(metrics_df: pd.DataFrame, summary_path: Path, n_rows: int) -> None:
    cols = list(metrics_df.columns)
    table_lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in metrics_df.iterrows():
        vals = []
        for col in cols:
            val = row[col]
            if isinstance(val, float):
                vals.append(f"{val:.4f}")
            else:
                vals.append(str(val))
        table_lines.append("| " + " | ".join(vals) + " |")

    lines = [
        "# Proxy Validation",
        "",
        "This report evaluates the optional NDVI branch as a **proxy-validation** workflow.",
        "",
        "Important interpretation:",
        "- The observed target here is the NDVI-derived proxy damage state, not an independent bridge inspection label.",
        "- The HAZUS result should therefore be interpreted as a benchmark comparison against the proxy subset, not as full external validation.",
        "",
        f"- Validation subset size: `{n_rows:,}` bridges with both proxy damage labels and HAZUS-side features",
        "",
        "## Metrics",
        "",
        *table_lines,
        "",
        "## How To Read These Results",
        "",
        "- `Exact_Accuracy` is the strictest metric and often harsh for ordinal damage states.",
        "- `Within_1_State_Accuracy` is useful because predicting `Moderate` instead of `Extensive` is less wrong than predicting `None` instead of `Complete`.",
        "- `Weighted_Kappa` rewards near-miss ordinal predictions more than distant misses.",
        "- `Underprediction_Rate` is especially relevant here because the project concern was that the model may be biased toward lower damage states.",
        "",
        "## Recommended Wording",
        "",
        "- The current NDVI figure should be described as **limited proxy validation**.",
        "- The HAZUS baseline and hybrid model can be compared on this subset, but this is still not equivalent to validation against a true observed bridge-damage dataset.",
        "- If future observed bridge inspection labels become available, this same evaluation structure can be reused for proper external validation.",
        "",
    ]
    summary_path.write_text("\n".join(lines) + "\n")


def main() -> None:
    sns.set_theme(style="whitegrid")
    paths = build_paths()
    processed_dir = paths["PROCESSED_DIR"]
    figures_dir = paths["FIGURES_DIR"]

    validation_df = build_validation_table()

    X = validation_df[FEATURE_COLUMNS].copy()
    y = validation_df["observed_code"].to_numpy()
    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X,
        y,
        validation_df.index.to_numpy(),
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    hybrid_model = make_classifier()
    hybrid_model.fit(X_train, y_train)
    hybrid_pred = hybrid_model.predict(X_test)

    hazus_pred = validation_df.loc[idx_test, "hazus_pred_code"].to_numpy()

    metrics_rows = []
    for label, pred in [
        ("Univariate (HAZUS)", hazus_pred),
        ("Hybrid Proxy Model", hybrid_pred),
    ]:
        row = {"Model": label, **compute_metrics(y_test, pred)}
        metrics_rows.append(row)

    metrics_df = pd.DataFrame(metrics_rows)
    metrics_path = processed_dir / "proxy_validation_metrics.csv"
    metrics_df.to_csv(metrics_path, index=False)

    predictions = validation_df.loc[idx_test, [
        "join_id",
        "observed_state",
        "hazus_pred_state",
        *FEATURE_COLUMNS,
        "EDR",
    ]].copy()
    predictions["hybrid_pred_state"] = [DS_ORDER[int(x)] for x in hybrid_pred]
    predictions["observed_code"] = y_test
    predictions["hazus_pred_code"] = hazus_pred
    predictions["hybrid_pred_code"] = hybrid_pred
    predictions["hazus_error"] = hazus_pred - y_test
    predictions["hybrid_error"] = hybrid_pred - y_test
    predictions_path = processed_dir / "proxy_validation_predictions.csv"
    predictions.to_csv(predictions_path, index=False)

    confusion_path = figures_dir / "proxy_validation_confusion_matrices.png"
    plot_confusions(y_test, hazus_pred, hybrid_pred, confusion_path)

    summary_path = PROJECT_ROOT / "docs" / "PROXY_VALIDATION.md"
    write_summary(metrics_df, summary_path, len(validation_df))

    print(metrics_df.to_string(index=False))
    print(f"Saved: {metrics_path}")
    print(f"Saved: {predictions_path}")
    print(f"Saved: {confusion_path}")
    print(f"Saved: {summary_path}")


if __name__ == "__main__":
    main()
