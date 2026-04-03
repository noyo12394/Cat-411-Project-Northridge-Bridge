from pathlib import Path
import sys

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

from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, HistGradientBoostingRegressor, RandomForestRegressor, StackingRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import ElasticNetCV, RidgeCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from project_paths import build_paths, require_paths

sns.set_theme(style='whitegrid')

RANDOM_STATE = 42
TARGET = 'EDR'

FEATURE_SETS = {
    'SVI-only': ['year', 'yr_recon', 'spans', 'max_span', 'skew', 'cond', 'SVI'],
    'HAZUS-only': ['pga', 'HWB_CLASS'],
    'Hybrid HAZUS+SVI': ['pga', 'HWB_CLASS', 'SVI', 'year', 'yr_recon', 'spans', 'max_span', 'skew', 'cond'],
}

FEATURE_MANIFEST = [
    ('pga', 'Hazard demand', 'Peak ground acceleration at the bridge site; event-severity input.'),
    ('HWB_CLASS', 'Engineering class', 'HAZUS bridge class used to represent fragility-family behavior.'),
    ('SVI', 'Continuous vulnerability', 'Composite vulnerability score built from bridge attributes.'),
    ('year', 'Design era', 'Construction year proxy for code era and age.'),
    ('yr_recon', 'Rehabilitation history', 'Reconstruction year proxy for retrofit / renewal history.'),
    ('spans', 'Geometry', 'Number of spans; captures system configuration.'),
    ('max_span', 'Geometry', 'Maximum span length; captures structural scale and flexibility.'),
    ('skew', 'Geometry', 'Skew angle; relevant to seismic response and support behavior.'),
    ('cond', 'Condition', 'Condition-rating proxy for deterioration / existing state.'),
]


def make_preprocessor(numeric_features, categorical_features):
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


def make_models(preprocessor):
    return {
        'Elastic Net': Pipeline([
            ('prep', clone(preprocessor)),
            ('model', ElasticNetCV(l1_ratio=[0.1, 0.5, 0.9, 1.0], alphas=np.logspace(-4, 1, 20), cv=5, random_state=RANDOM_STATE, max_iter=20000)),
        ]),
        'Random Forest': Pipeline([
            ('prep', clone(preprocessor)),
            ('model', RandomForestRegressor(n_estimators=160, min_samples_leaf=2, n_jobs=1, random_state=RANDOM_STATE)),
        ]),
        'Extra Trees': Pipeline([
            ('prep', clone(preprocessor)),
            ('model', ExtraTreesRegressor(n_estimators=160, min_samples_leaf=1, n_jobs=1, random_state=RANDOM_STATE)),
        ]),
        'HistGradientBoosting': Pipeline([
            ('prep', clone(preprocessor)),
            ('model', HistGradientBoostingRegressor(max_iter=180, learning_rate=0.05, max_leaf_nodes=31, l2_regularization=0.1, random_state=RANDOM_STATE)),
        ]),
        'Stacked Hybrid Ensemble': Pipeline([
            ('prep', clone(preprocessor)),
            ('model', StackingRegressor(
                estimators=[
                    ('rf', RandomForestRegressor(n_estimators=100, min_samples_leaf=2, n_jobs=1, random_state=RANDOM_STATE)),
                    ('et', ExtraTreesRegressor(n_estimators=100, n_jobs=1, random_state=RANDOM_STATE)),
                    ('hgb', HistGradientBoostingRegressor(max_iter=120, learning_rate=0.05, max_leaf_nodes=31, random_state=RANDOM_STATE)),
                ],
                final_estimator=RidgeCV(alphas=np.logspace(-3, 3, 13)),
                n_jobs=1,
                passthrough=False,
            )),
        ]),
    }


def regression_metrics(y_true, y_pred):
    return {
        'MAE': mean_absolute_error(y_true, y_pred),
        'RMSE': np.sqrt(mean_squared_error(y_true, y_pred)),
        'R2': r2_score(y_true, y_pred),
    }


def fit_holdout_model(df, features, model, label):
    X = df[features].copy()
    y = df[TARGET].copy()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    metrics = regression_metrics(y_test, y_pred)

    pred_df = X_test.copy()
    pred_df['EDR_actual'] = y_test.values
    pred_df['EDR_predicted'] = y_pred
    pred_df['Residual'] = pred_df['EDR_actual'] - pred_df['EDR_predicted']
    pred_df['Absolute_Error'] = pred_df['Residual'].abs()

    perm = permutation_importance(model, X_test, y_test, n_repeats=8, random_state=RANDOM_STATE, n_jobs=1)
    importance_df = pd.DataFrame({
        'Feature': features,
        'Importance': perm.importances_mean,
        'Importance_std': perm.importances_std,
        'Model_Label': label,
    }).sort_values('Importance', ascending=False)

    return metrics, pred_df, importance_df, y_test, y_pred


def save_heatmap(df, value_col, title, path):
    pivot = df.pivot(index='Feature Set', columns='Model', values=value_col)
    plt.figure(figsize=(12, 4.8))
    sns.heatmap(pivot, annot=True, fmt='.4f', cmap='YlGnBu')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(path, dpi=200, bbox_inches='tight')
    plt.close()


def table_to_markdown(df):
    cols = list(df.columns)
    lines = [
        '| ' + ' | '.join(cols) + ' |',
        '| ' + ' | '.join(['---'] * len(cols)) + ' |',
    ]
    for _, row in df.iterrows():
        vals = []
        for col in cols:
            val = row[col]
            if isinstance(val, float):
                vals.append(f'{val:.6f}')
            else:
                vals.append(str(val))
        lines.append('| ' + ' | '.join(vals) + ' |')
    return '\\n'.join(lines)


def main():
    paths = build_paths()
    require_paths(paths, ['SVI_CSV'])

    data_path = paths['SVI_CSV']
    figures_dir = paths['FIGURES_DIR']
    processed_dir = paths['PROCESSED_DIR']
    figures_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(data_path, low_memory=False)
    df = df.dropna(subset=[TARGET]).copy()

    results = []
    best_candidates = []
    cv = KFold(n_splits=3, shuffle=True, random_state=RANDOM_STATE)

    for feature_set_name, features in FEATURE_SETS.items():
        X = df[features].copy()
        y = df[TARGET].copy()
        numeric_features = [c for c in features if c != 'HWB_CLASS']
        categorical_features = [c for c in features if c == 'HWB_CLASS']
        preprocessor = make_preprocessor(numeric_features, categorical_features)
        models = make_models(preprocessor)

        for model_name, model in models.items():
            print(f'Running {feature_set_name} :: {model_name}', flush=True)
            scores = cross_validate(
                model,
                X,
                y,
                cv=cv,
                scoring={
                    'mae': 'neg_mean_absolute_error',
                    'rmse': 'neg_root_mean_squared_error',
                    'r2': 'r2',
                },
                n_jobs=1,
                return_train_score=False,
            )
            row = {
                'Feature Set': feature_set_name,
                'Model': model_name,
                'MAE': -scores['test_mae'].mean(),
                'RMSE': -scores['test_rmse'].mean(),
                'R2': scores['test_r2'].mean(),
                'MAE_std': scores['test_mae'].std(),
                'RMSE_std': scores['test_rmse'].std(),
                'R2_std': scores['test_r2'].std(),
            }
            results.append(row)
            best_candidates.append((row['RMSE'], feature_set_name, model_name, features, model))

    results_df = pd.DataFrame(results).sort_values(['Feature Set', 'RMSE', 'MAE']).reset_index(drop=True)
    results_csv = processed_dir / 'ml_hybrid_comparison.csv'
    results_df.to_csv(results_csv, index=False)

    best_by_feature = results_df.sort_values('RMSE').groupby('Feature Set', as_index=False).first()
    best_summary_csv = processed_dir / 'ml_hybrid_best_by_feature_set.csv'
    best_by_feature.to_csv(best_summary_csv, index=False)

    manifest_df = pd.DataFrame(FEATURE_MANIFEST, columns=['Feature', 'Role', 'Reason'])
    manifest_csv = processed_dir / 'ml_feature_manifest.csv'
    manifest_df.to_csv(manifest_csv, index=False)

    best_rmse, best_feature_set, best_model_name, best_features, best_model = min(best_candidates, key=lambda x: x[0])
    pred_metrics, pred_df, importance_df, y_test, y_pred = fit_holdout_model(
        df,
        best_features,
        best_model,
        f'{best_feature_set} :: {best_model_name}',
    )
    pred_path = processed_dir / 'ml_hybrid_predictions.csv'
    pred_df.to_csv(pred_path, index=False)

    save_heatmap(results_df, 'RMSE', 'RMSE by Feature Set and Model', figures_dir / 'ml_hybrid_rmse_heatmap.png')
    save_heatmap(results_df, 'R2', 'R2 by Feature Set and Model', figures_dir / 'ml_hybrid_r2_heatmap.png')

    plt.figure(figsize=(7, 6))
    plt.scatter(y_test, y_pred, s=14, alpha=0.45)
    lims = [min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())]
    plt.plot(lims, lims, color='black', linestyle='--', linewidth=1)
    plt.xlabel('Actual EDR')
    plt.ylabel('Predicted EDR')
    plt.title(f'Best Model: {best_model_name} on {best_feature_set}')
    plt.tight_layout()
    plt.savefig(figures_dir / 'ml_hybrid_actual_vs_predicted.png', dpi=200, bbox_inches='tight')
    plt.close()

    plt.figure(figsize=(7, 6))
    sns.histplot(pred_df['Residual'], bins=40, kde=True)
    plt.axvline(0, color='black', linestyle='--', linewidth=1)
    plt.xlabel('Residual (Actual - Predicted)')
    plt.title('Residual Distribution for Best Hybrid Model')
    plt.tight_layout()
    plt.savefig(figures_dir / 'ml_hybrid_residuals.png', dpi=200, bbox_inches='tight')
    plt.close()

    importance_path = processed_dir / 'ml_hybrid_feature_importance.csv'
    importance_df.to_csv(importance_path, index=False)

    top_imp = importance_df.head(10).iloc[::-1]
    plt.figure(figsize=(8, 5.5))
    plt.barh(top_imp['Feature'], top_imp['Importance'], xerr=top_imp['Importance_std'])
    plt.xlabel('Permutation Importance')
    plt.title('Top Features for Best Hybrid Model')
    plt.tight_layout()
    plt.savefig(figures_dir / 'ml_hybrid_feature_importance.png', dpi=200, bbox_inches='tight')
    plt.close()

    recommended_row = results_df[
        (results_df['Feature Set'] == 'Hybrid HAZUS+SVI')
    ].sort_values(['RMSE', 'MAE']).iloc[0]
    recommended_model_name = recommended_row['Model']
    recommended_features = FEATURE_SETS['Hybrid HAZUS+SVI']
    recommended_model = make_models(
        make_preprocessor(
            [c for c in recommended_features if c != 'HWB_CLASS'],
            [c for c in recommended_features if c == 'HWB_CLASS'],
        )
    )[recommended_model_name]
    recommended_metrics, recommended_pred_df, recommended_importance_df, recommended_y_test, recommended_y_pred = fit_holdout_model(
        df,
        recommended_features,
        recommended_model,
        f'Hybrid HAZUS+SVI :: {recommended_model_name}',
    )

    recommended_metrics_df = pd.DataFrame([{
        'Feature Set': 'Hybrid HAZUS+SVI',
        'Model': recommended_model_name,
        **recommended_metrics,
    }])
    recommended_metrics_path = processed_dir / 'ml_recommended_hybrid_metrics.csv'
    recommended_metrics_df.to_csv(recommended_metrics_path, index=False)

    recommended_pred_path = processed_dir / 'ml_recommended_hybrid_predictions.csv'
    recommended_pred_df.to_csv(recommended_pred_path, index=False)

    recommended_importance_path = processed_dir / 'ml_recommended_hybrid_feature_importance.csv'
    recommended_importance_df.to_csv(recommended_importance_path, index=False)

    plt.figure(figsize=(7, 6))
    plt.scatter(recommended_y_test, recommended_y_pred, s=14, alpha=0.45)
    recommended_lims = [
        min(recommended_y_test.min(), recommended_y_pred.min()),
        max(recommended_y_test.max(), recommended_y_pred.max()),
    ]
    plt.plot(recommended_lims, recommended_lims, color='black', linestyle='--', linewidth=1)
    plt.xlabel('Actual EDR')
    plt.ylabel('Predicted EDR')
    plt.title(f'Recommended Model: {recommended_model_name} on Hybrid HAZUS+SVI')
    plt.tight_layout()
    plt.savefig(figures_dir / 'ml_recommended_hybrid_actual_vs_predicted.png', dpi=200, bbox_inches='tight')
    plt.close()

    recommended_top_imp = recommended_importance_df.head(10).iloc[::-1]
    plt.figure(figsize=(8, 5.5))
    plt.barh(recommended_top_imp['Feature'], recommended_top_imp['Importance'], xerr=recommended_top_imp['Importance_std'])
    plt.xlabel('Permutation Importance')
    plt.title('Top Features for Recommended Hybrid Model')
    plt.tight_layout()
    plt.savefig(figures_dir / 'ml_recommended_hybrid_feature_importance.png', dpi=200, bbox_inches='tight')
    plt.close()

    literature = [
        ('Shwartz-Ziv and Armon (2022)', 'Tabular data: Deep learning is not all you need', 'https://www.sciencedirect.com/science/article/pii/S1566253521002360'),
        ('Gorishniy et al. (NeurIPS 2021)', 'Revisiting Deep Learning Models for Tabular Data', 'https://research.yandex.com/publications/revisiting-deep-learning-models-for-tabular-data'),
        ('scikit-learn docs', 'HistGradientBoostingRegressor', 'https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.HistGradientBoostingRegressor.html'),
        ('scikit-learn docs', 'StackingRegressor', 'https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.StackingRegressor.html'),
        ('Chen and Guestrin (KDD 2016)', 'XGBoost: A Scalable Tree Boosting System', 'https://arxiv.org/pdf/1603.02754'),
    ]

    summary_path = PROJECT_ROOT / 'docs' / 'ML_HYBRID_ANALYSIS.md'
    lines = [
        '# ML Hybrid Analysis',
        '',
        'This analysis compares structured-data models for predicting Expected Damage Ratio (EDR) from three feature views of the bridge dataset.',
        '',
        '## Why These Models',
        '',
        '- Tree ensembles are strong baselines for tabular data and often outperform more complex deep approaches on structured datasets.',
        '- HistGradientBoosting was included because it is a modern gradient-boosting tree model available in scikit-learn and is optimized for larger tabular datasets.',
        '- A stacked ensemble was included to test whether combining complementary model families improves over any single learner.',
        '',
        '## Feature-Set Comparison',
        '',
        '- `SVI-only`: intrinsic bridge attributes and continuous vulnerability score',
        '- `HAZUS-only`: hazard intensity plus HAZUS bridge class',
        '- `Hybrid HAZUS+SVI`: hazard, HAZUS class, and structural / vulnerability signals together',
        '',
        '## Cross-Validated Results',
        '',
        table_to_markdown(best_by_feature),
        '',
        'Full comparison table saved to:',
        f'- `{results_csv.relative_to(PROJECT_ROOT)}`',
        f'- `{best_summary_csv.relative_to(PROJECT_ROOT)}`',
        f'- `{manifest_csv.relative_to(PROJECT_ROOT)}`',
        '',
        '## Best Overall Model',
        '',
        f'- Feature set: `{best_feature_set}`',
        f'- Model: `{best_model_name}`',
        f'- Holdout MAE: `{pred_metrics["MAE"]:.6f}`',
        f'- Holdout RMSE: `{pred_metrics["RMSE"]:.6f}`',
        f'- Holdout R2: `{pred_metrics["R2"]:.6f}`',
        '',
        '## Recommended Final Model For Presentation',
        '',
        '- Recommended feature set: `Hybrid HAZUS+SVI`',
        f'- Recommended model: `{recommended_model_name}`',
        f'- Holdout MAE: `{recommended_metrics["MAE"]:.6f}`',
        f'- Holdout RMSE: `{recommended_metrics["RMSE"]:.6f}`',
        f'- Holdout R2: `{recommended_metrics["R2"]:.6f}`',
        '',
        'This is the recommended final model because it uses only interpretable hazard, class, geometry, age, and condition variables while still performing very strongly.',
        '',
        '## Generated Artifacts',
        '',
        f'- `{pred_path.relative_to(PROJECT_ROOT)}`: holdout predictions and residuals',
        f'- `{importance_path.relative_to(PROJECT_ROOT)}`: permutation-based feature importance for the best model',
        f'- `{recommended_metrics_path.relative_to(PROJECT_ROOT)}`: metrics for the recommended hybrid model',
        f'- `{recommended_pred_path.relative_to(PROJECT_ROOT)}`: holdout predictions for the recommended hybrid model',
        f'- `{recommended_importance_path.relative_to(PROJECT_ROOT)}`: feature importance for the recommended hybrid model',
        f'- `figures/ml_hybrid_rmse_heatmap.png`',
        f'- `figures/ml_hybrid_r2_heatmap.png`',
        f'- `figures/ml_hybrid_actual_vs_predicted.png`',
        f'- `figures/ml_hybrid_residuals.png`',
        f'- `figures/ml_hybrid_feature_importance.png`',
        f'- `figures/ml_recommended_hybrid_actual_vs_predicted.png`',
        f'- `figures/ml_recommended_hybrid_feature_importance.png`',
        '',
        '## Interpretation',
        '',
        '- `HAZUS-only` is expected to be very strong because EDR is directly tied to hazard intensity and HAZUS fragility logic.',
        '- `SVI-only` tests how much of the damage pattern can be reconstructed from bridge vulnerability traits alone.',
        '- `Hybrid HAZUS+SVI` is the most decision-useful framing for a dashboard because it combines event severity, engineering classification, and continuous vulnerability context.',
        '- For reporting, `HAZUS-only` should be treated as a benchmark ceiling, while `Hybrid HAZUS+SVI` is the more defensible final model.',
        '- All input variables in the hybrid model were restricted to interpretable engineering variables; identifiers and non-causal descriptive fields were intentionally excluded.',
        '',
        '## Recommended Final Variable Set',
        '',
        '- `pga`',
        '- `HWB_CLASS`',
        '- `SVI`',
        '- `year`',
        '- `yr_recon`',
        '- `spans`',
        '- `max_span`',
        '- `skew`',
        '- `cond`',
        '',
        'This is the most defensible final model for presentation because every variable has a clear hazard, classification, geometry, age, or condition interpretation.',
        '',
        '## Literature Notes',
        '',
    ]
    for author, title, url in literature:
        lines.append(f'- {author}: [{title}]({url})')

    summary_path.write_text('\n'.join(lines) + '\n')

    print(results_df.sort_values(['RMSE', 'MAE']).head(12).to_string(index=False))
    print('\nBest by feature set:')
    print(best_by_feature.to_string(index=False))
    print('\nBest overall holdout metrics:')
    for k, v in pred_metrics.items():
        print(f'- {k}: {v:.6f}')
    print(f'\nSaved: {results_csv}')
    print(f'Saved: {best_summary_csv}')
    print(f'Saved: {pred_path}')
    print(f'Saved: {importance_path}')
    print(f'Saved: {summary_path}')


if __name__ == '__main__':
    main()
