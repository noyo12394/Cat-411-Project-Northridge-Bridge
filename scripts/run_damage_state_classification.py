from pathlib import Path
import sys
import warnings

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from runtime_checks import ensure_packages, ensure_supported_runtime

ensure_supported_runtime()
ensure_packages([
    'numpy', 'pandas', 'matplotlib', 'sklearn', 'seaborn'
])

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
    make_scorer,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from project_paths import build_paths
from scripts.run_ml_hybrid_analysis import (
    CATEGORICAL_FEATURES,
    FEATURE_MANIFEST,
    FEATURE_SETS,
    RANDOM_STATE,
    load_statewide_bridge_dataset,
    table_to_markdown,
)

warnings.filterwarnings('ignore', category=ConvergenceWarning)
sns.set_theme(style='whitegrid')

TARGET = 'Damage_State'
STATE_LABELS = ['None', 'Slight', 'Moderate', 'Extensive', 'Complete']
STATE_TO_INT = {label: idx for idx, label in enumerate(STATE_LABELS)}
FEATURE_GROUPS = {
    'Structural Vulnerability Classifier': FEATURE_SETS['Bridge Vulnerability Structural'],
    'Event Damage Classifier': FEATURE_SETS['Event Damage Hybrid'],
}


def assign_modal_damage_state(df: pd.DataFrame) -> pd.DataFrame:
    damage_cols = ['P_DS0', 'P_DS1', 'P_DS2', 'P_DS3', 'P_DS4']
    modal_idx = df[damage_cols].to_numpy().argmax(axis=1)
    df[TARGET] = [STATE_LABELS[idx] for idx in modal_idx]
    return df


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


def make_models(preprocessor: ColumnTransformer) -> dict:
    return {
        'Logistic Regression': Pipeline([
            ('prep', clone(preprocessor)),
            ('model', LogisticRegression(
                max_iter=4000,
                class_weight='balanced',
                random_state=RANDOM_STATE,
            )),
        ]),
        'Random Forest': Pipeline([
            ('prep', clone(preprocessor)),
            ('model', RandomForestClassifier(
                n_estimators=180,
                min_samples_leaf=2,
                class_weight='balanced_subsample',
                n_jobs=-1,
                random_state=RANDOM_STATE,
            )),
        ]),
        'Extra Trees': Pipeline([
            ('prep', clone(preprocessor)),
            ('model', ExtraTreesClassifier(
                n_estimators=220,
                min_samples_leaf=1,
                class_weight='balanced',
                n_jobs=-1,
                random_state=RANDOM_STATE,
            )),
        ]),
        'HistGradientBoosting': Pipeline([
            ('prep', clone(preprocessor)),
            ('model', HistGradientBoostingClassifier(
                learning_rate=0.05,
                max_iter=180,
                max_leaf_nodes=31,
                min_samples_leaf=20,
                random_state=RANDOM_STATE,
            )),
        ]),
    }


def within_one_state_accuracy(y_true: pd.Series, y_pred: np.ndarray) -> float:
    y_true_int = y_true.map(STATE_TO_INT).to_numpy()
    y_pred_int = pd.Series(y_pred).map(STATE_TO_INT).to_numpy()
    return float(np.mean(np.abs(y_true_int - y_pred_int) <= 1))


def evaluate_holdout(df: pd.DataFrame, features: list[str], model, train_idx: np.ndarray, test_idx: np.ndarray, label: str):
    X = df[features].copy()
    y = df[TARGET].copy()

    X_train = X.iloc[train_idx]
    X_test = X.iloc[test_idx]
    y_train = y.iloc[train_idx]
    y_test = y.iloc[test_idx]

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    metrics = {
        'Accuracy': accuracy_score(y_test, y_pred),
        'Balanced_Accuracy': balanced_accuracy_score(y_test, y_pred),
        'Macro_F1': f1_score(y_test, y_pred, average='macro'),
        'Weighted_F1': f1_score(y_test, y_pred, average='weighted'),
        'Within_One_State_Accuracy': within_one_state_accuracy(y_test, y_pred),
        'Quadratic_Weighted_Kappa': cohen_kappa_score(y_test, y_pred, labels=STATE_LABELS, weights='quadratic'),
    }

    pred_df = df.iloc[test_idx][['join_id', 'STRUCTURE_NUMBER_008', 'pga', 'HWB_CLASS']].reset_index(drop=True)
    x_test_export = X_test.reset_index(drop=True)
    x_test_export = x_test_export.loc[:, ~x_test_export.columns.isin(pred_df.columns)]
    pred_df = pd.concat([pred_df, x_test_export], axis=1)
    pred_df['Observed_State'] = y_test.reset_index(drop=True)
    pred_df['Predicted_State'] = pd.Series(y_pred)
    pred_df['Correct'] = pred_df['Observed_State'] == pred_df['Predicted_State']
    pred_df['Label'] = label

    cm = confusion_matrix(y_test, y_pred, labels=STATE_LABELS)
    report_df = pd.DataFrame(
        classification_report(
            y_test,
            y_pred,
            labels=STATE_LABELS,
            output_dict=True,
            zero_division=0,
        )
    ).T.reset_index().rename(columns={'index': 'Label'})
    return metrics, pred_df, cm, report_df


def plot_confusion_matrix(cm: np.ndarray, title: str, path: Path) -> None:
    plt.figure(figsize=(6.5, 5.5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=STATE_LABELS, yticklabels=STATE_LABELS)
    plt.xlabel('Predicted')
    plt.ylabel('Observed')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()


def main() -> None:
    paths = build_paths()
    processed_dir = paths['PROCESSED_DIR']
    figures_dir = paths['FIGURES_DIR']
    figures_dir.mkdir(parents=True, exist_ok=True)

    df = load_statewide_bridge_dataset(paths)
    df = assign_modal_damage_state(df)

    target_counts = df[TARGET].value_counts().reindex(STATE_LABELS, fill_value=0)
    train_idx, test_idx = train_test_split(
        np.arange(len(df)),
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=df[TARGET],
    )
    cv = list(StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE).split(df, df[TARGET]))
    scorers = {
        'accuracy': make_scorer(accuracy_score),
        'balanced_accuracy': make_scorer(balanced_accuracy_score),
        'macro_f1': make_scorer(f1_score, average='macro'),
        'weighted_f1': make_scorer(f1_score, average='weighted'),
    }

    comparison_rows = []
    best_rows = []
    holdout_payload = {}

    for feature_group, features in FEATURE_GROUPS.items():
        preprocessor = make_preprocessor(features)
        models = make_models(preprocessor)
        X = df[features].copy()
        y = df[TARGET].copy()

        for model_name, model in models.items():
            print(f'Running {feature_group} :: {model_name}', flush=True)
            scores = cross_validate(
                model,
                X,
                y,
                cv=cv,
                scoring=scorers,
                n_jobs=1,
                return_train_score=False,
            )
            metrics, pred_df, cm, report_df = evaluate_holdout(
                df,
                features,
                clone(model),
                train_idx,
                test_idx,
                f'{feature_group} :: {model_name}',
            )
            row = {
                'Feature Group': feature_group,
                'Model': model_name,
                'CV_Accuracy': scores['test_accuracy'].mean(),
                'CV_Balanced_Accuracy': scores['test_balanced_accuracy'].mean(),
                'CV_Macro_F1': scores['test_macro_f1'].mean(),
                'CV_Weighted_F1': scores['test_weighted_f1'].mean(),
                'Holdout_Accuracy': metrics['Accuracy'],
                'Holdout_Balanced_Accuracy': metrics['Balanced_Accuracy'],
                'Holdout_Macro_F1': metrics['Macro_F1'],
                'Holdout_Weighted_F1': metrics['Weighted_F1'],
                'Holdout_Within_One_State_Accuracy': metrics['Within_One_State_Accuracy'],
                'Holdout_Quadratic_Weighted_Kappa': metrics['Quadratic_Weighted_Kappa'],
            }
            comparison_rows.append(row)
            holdout_payload[(feature_group, model_name)] = (pred_df, cm, report_df)

    comparison_df = pd.DataFrame(comparison_rows).sort_values(
        ['CV_Balanced_Accuracy', 'CV_Macro_F1', 'Holdout_Balanced_Accuracy'],
        ascending=False,
    ).reset_index(drop=True)
    comparison_df.to_csv(processed_dir / 'damage_state_model_comparison.csv', index=False)

    best_by_group = (
        comparison_df.groupby('Feature Group', as_index=False)
        .first()
        .sort_values('CV_Balanced_Accuracy', ascending=False)
        .reset_index(drop=True)
    )
    best_by_group.to_csv(processed_dir / 'damage_state_best_by_feature_set.csv', index=False)

    best_prediction_frames = []
    report_frames = []
    fig, axes = plt.subplots(1, len(best_by_group), figsize=(13, 5.5))
    if len(best_by_group) == 1:
        axes = [axes]
    for axis, (_, row) in zip(axes, best_by_group.iterrows()):
        key = (row['Feature Group'], row['Model'])
        pred_df, cm, report_df = holdout_payload[key]
        best_prediction_frames.append(pred_df)
        report_df['Feature Group'] = row['Feature Group']
        report_df['Model'] = row['Model']
        report_frames.append(report_df)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=STATE_LABELS, yticklabels=STATE_LABELS, ax=axis)
        axis.set_title(f"{row['Feature Group']}\n{row['Model']}")
        axis.set_xlabel('Predicted')
        axis.set_ylabel('Observed')
    plt.tight_layout()
    plt.savefig(figures_dir / 'damage_state_confusion_matrices.png', dpi=220, bbox_inches='tight')
    plt.close(fig)

    pd.concat(best_prediction_frames, ignore_index=True).to_csv(processed_dir / 'damage_state_predictions.csv', index=False)
    pd.concat(report_frames, ignore_index=True).to_csv(processed_dir / 'damage_state_classification_report.csv', index=False)

    summary_path = PROJECT_ROOT / 'docs' / 'DAMAGE_STATE_MODELS.md'
    manifest_df = pd.DataFrame(FEATURE_MANIFEST, columns=['Feature', 'Role', 'Reason'])
    summary_lines = [
        '# Damage-State Classification Models',
        '',
        'This exploratory add-on reframes the bridge problem as a modal HAZUS damage-state classification task rather than a continuous EDR regression task.',
        '',
        '## Damage-State Labels',
        '',
        'The target label is the most probable HAZUS damage state for each bridge:',
        '',
    ]
    for state, count in target_counts.items():
        summary_lines.append(f'- `{state}`: `{int(count):,}` bridges')
    summary_lines.extend([
        '',
        '## Feature Groups',
        '',
        '- `Structural Vulnerability Classifier`: no-PGA structural vulnerability variables only',
        '- `Event Damage Classifier`: hazard + bridge variables for event-specific damage-state prediction',
        '',
        '## Results',
        '',
        'The most important metrics here are balanced accuracy, macro-F1, within-one-state accuracy, and quadratic weighted kappa because the damage states are ordinal and highly imbalanced.',
        '',
        table_to_markdown(best_by_group[[
            'Feature Group',
            'Model',
            'CV_Balanced_Accuracy',
            'CV_Macro_F1',
            'Holdout_Balanced_Accuracy',
            'Holdout_Macro_F1',
            'Holdout_Within_One_State_Accuracy',
            'Holdout_Quadratic_Weighted_Kappa',
        ]]),
        '',
        '## Variable Reference',
        '',
        table_to_markdown(manifest_df),
        '',
        '## Generated Artifacts',
        '',
        '- `data/processed/damage_state_model_comparison.csv`',
        '- `data/processed/damage_state_best_by_feature_set.csv`',
        '- `data/processed/damage_state_predictions.csv`',
        '- `data/processed/damage_state_classification_report.csv`',
        '- `figures/damage_state_confusion_matrices.png`',
    ])
    summary_path.write_text('\n'.join(summary_lines) + '\n')

    print(best_by_group.to_string(index=False))
    print('Saved:', summary_path)


if __name__ == '__main__':
    main()
