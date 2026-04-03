from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib.pyplot as plt
import pandas as pd

from project_paths import build_paths, require_paths
from scripts.run_ml_hybrid_analysis import (
    FEATURE_MANIFEST,
    FEATURE_SETS,
    fit_holdout_model,
    make_models,
    make_preprocessor,
    table_to_markdown,
)


def main():
    paths = build_paths()
    require_paths(paths, ['SVI_CSV'])

    processed_dir = paths['PROCESSED_DIR']
    figures_dir = paths['FIGURES_DIR']
    figures_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(paths['SVI_CSV'], low_memory=False).dropna(subset=['EDR']).copy()
    comparison = pd.read_csv(processed_dir / 'ml_hybrid_comparison.csv')
    best_by_feature = pd.read_csv(processed_dir / 'ml_hybrid_best_by_feature_set.csv')

    manifest_df = pd.DataFrame(FEATURE_MANIFEST, columns=['Feature', 'Role', 'Reason'])
    manifest_df.to_csv(processed_dir / 'ml_feature_manifest.csv', index=False)

    recommended_row = comparison[
        comparison['Feature Set'] == 'Hybrid HAZUS+SVI'
    ].sort_values(['RMSE', 'MAE']).iloc[0]
    recommended_model_name = recommended_row['Model']
    features = FEATURE_SETS['Hybrid HAZUS+SVI']

    preprocessor = make_preprocessor(
        [c for c in features if c != 'HWB_CLASS'],
        [c for c in features if c == 'HWB_CLASS'],
    )
    model = make_models(preprocessor)[recommended_model_name]
    metrics, pred_df, importance_df, y_test, y_pred = fit_holdout_model(
        df,
        features,
        model,
        f'Hybrid HAZUS+SVI :: {recommended_model_name}',
    )

    metrics_df = pd.DataFrame([{
        'Feature Set': 'Hybrid HAZUS+SVI',
        'Model': recommended_model_name,
        **metrics,
    }])
    metrics_df.to_csv(processed_dir / 'ml_recommended_hybrid_metrics.csv', index=False)
    pred_df.to_csv(processed_dir / 'ml_recommended_hybrid_predictions.csv', index=False)
    importance_df.to_csv(processed_dir / 'ml_recommended_hybrid_feature_importance.csv', index=False)

    plt.figure(figsize=(7, 6))
    plt.scatter(y_test, y_pred, s=14, alpha=0.45)
    lims = [min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())]
    plt.plot(lims, lims, color='black', linestyle='--', linewidth=1)
    plt.xlabel('Actual EDR')
    plt.ylabel('Predicted EDR')
    plt.title(f'Recommended Model: {recommended_model_name} on Hybrid HAZUS+SVI')
    plt.tight_layout()
    plt.savefig(figures_dir / 'ml_recommended_hybrid_actual_vs_predicted.png', dpi=200, bbox_inches='tight')
    plt.close()

    top_imp = importance_df.head(10).iloc[::-1]
    plt.figure(figsize=(8, 5.5))
    plt.barh(top_imp['Feature'], top_imp['Importance'], xerr=top_imp['Importance_std'])
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
        '- Tree ensembles are strong baselines for structured tabular data and are widely recommended in the literature for problems like bridge-risk modeling.',
        '- HistGradientBoosting was included as a modern boosting-tree baseline available in scikit-learn.',
        '- A stacked ensemble was included to test whether combining complementary model families improved on single-model learners.',
        '- Elastic Net was kept as a transparent linear baseline to show how much nonlinearity matters in this dataset.',
        '',
        '## Engineering Variable Screen',
        '',
        'Only variables with a clear engineering or vulnerability interpretation were retained in the final hybrid model.',
        '',
        table_to_markdown(manifest_df),
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
        '- `data/processed/ml_hybrid_comparison.csv`',
        '- `data/processed/ml_hybrid_best_by_feature_set.csv`',
        '- `data/processed/ml_feature_manifest.csv`',
        '',
        '## Best Overall Benchmark',
        '',
        '- Feature set: `HAZUS-only`',
        '- Model: `Extra Trees`',
        '- Interpretation: this is the strongest benchmark, but it should be treated as an upper bound because EDR is itself generated from HAZUS fragility logic.',
        '',
        '## Recommended Final Model For Presentation',
        '',
        '- Feature set: `Hybrid HAZUS+SVI`',
        f'- Model: `{recommended_model_name}`',
        f'- Holdout MAE: `{metrics["MAE"]:.6f}`',
        f'- Holdout RMSE: `{metrics["RMSE"]:.6f}`',
        f'- Holdout R2: `{metrics["R2"]:.6f}`',
        '',
        'This is the most defensible final model because it uses only interpretable hazard, class, age, geometry, and condition variables while still performing strongly.',
        '',
        '## Generated Artifacts',
        '',
        '- `data/processed/ml_hybrid_predictions.csv`: holdout predictions and residuals for the overall best benchmark model',
        '- `data/processed/ml_hybrid_feature_importance.csv`: permutation importance for the overall best benchmark model',
        '- `data/processed/ml_recommended_hybrid_metrics.csv`: metrics for the recommended interpretable hybrid model',
        '- `data/processed/ml_recommended_hybrid_predictions.csv`: holdout predictions for the recommended hybrid model',
        '- `data/processed/ml_recommended_hybrid_feature_importance.csv`: feature importance for the recommended hybrid model',
        '- `figures/ml_hybrid_rmse_heatmap.png`',
        '- `figures/ml_hybrid_r2_heatmap.png`',
        '- `figures/ml_hybrid_actual_vs_predicted.png`',
        '- `figures/ml_hybrid_residuals.png`',
        '- `figures/ml_hybrid_feature_importance.png`',
        '- `figures/ml_recommended_hybrid_actual_vs_predicted.png`',
        '- `figures/ml_recommended_hybrid_feature_importance.png`',
        '',
        '## Interpretation',
        '',
        '- `HAZUS-only` wins because the target `EDR` is tightly linked to hazard intensity and HAZUS class by construction.',
        '- `SVI-only` still carries real vulnerability signal, but it is not expected to match a hazard-based target on its own.',
        '- `Hybrid HAZUS+SVI` is the most useful final framing for a dashboard or decision-support tool because it combines seismic demand, bridge class, and continuous vulnerability context.',
        '- The hybrid result is therefore the best presentation model, while the HAZUS-only result serves as a benchmark ceiling.',
        '',
        '## Literature Notes',
        '',
    ]
    for author, title, url in literature:
        lines.append(f'- {author}: [{title}]({url})')
    summary_path.write_text('\n'.join(lines) + '\n')

    print('Recommended model:', recommended_model_name)
    print(metrics_df.to_string(index=False))
    print(importance_df.head(10).to_string(index=False))
    print('Updated:', summary_path)


if __name__ == '__main__':
    main()
