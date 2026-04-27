from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from runtime_checks import ensure_packages, ensure_supported_runtime

ensure_supported_runtime()
ensure_packages(['pandas', 'matplotlib', 'numpy'])

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from project_paths import build_paths


def main() -> None:
    paths = build_paths()
    comparison_csv = paths['PROCESSED_DIR'] / 'ml_hybrid_comparison.csv'
    if not comparison_csv.exists():
        raise FileNotFoundError(f'Missing required comparison file: {comparison_csv}')

    df = pd.read_csv(comparison_csv)
    structural = df[df['Feature Set'].str.startswith('Structural')].copy()
    structural = structural.sort_values(['CV_RMSE', 'Holdout_RMSE', 'Holdout_R2'], ascending=[True, True, False])

    top5_no_pga = structural.head(5).copy()
    top5_no_pga.insert(0, 'Rank', range(1, len(top5_no_pga) + 1))

    summary_rows = [
        {
            'Question': 'Best hazard-independent model',
            'Feature Set': 'Structural + HAZUS Class',
            'Model': 'Extra Trees',
            'CV_RMSE': 0.038232,
            'CV_R2': 0.175733,
            'Holdout_RMSE': 0.039341,
            'Holdout_R2': 0.212044,
            'Holdout_RMSE_Positive': 0.047676,
            'Holdout_R2_Positive': 0.227622,
            'Reason': 'Best cross-validated no-PGA model while retaining an interpretable structural-system descriptor.',
        },
        {
            'Question': 'Best pure structural-only baseline',
            'Feature Set': 'Structural Core',
            'Model': 'Extra Trees',
            'CV_RMSE': 0.038518,
            'CV_R2': 0.163660,
            'Holdout_RMSE': 0.039286,
            'Holdout_R2': 0.214257,
            'Holdout_RMSE_Positive': 0.047678,
            'Holdout_R2_Positive': 0.227569,
            'Reason': 'Nearly tied with the best no-PGA model and slightly better on one holdout split, using only raw structural variables.',
        },
        {
            'Question': 'Best SVI-inclusive model',
            'Feature Set': 'Structural + SVI + HAZUS Class',
            'Model': 'Extra Trees',
            'CV_RMSE': 0.038512,
            'CV_R2': 0.163664,
            'Holdout_RMSE': 0.039797,
            'Holdout_R2': 0.193692,
            'Holdout_RMSE_Positive': 0.048204,
            'Holdout_R2_Positive': 0.210410,
            'Reason': 'Best model that keeps SVI explicit, useful for interpretability even though it is not the top RMSE winner.',
        },
        {
            'Question': 'Best event-damage model',
            'Feature Set': 'Event Damage Hybrid',
            'Model': 'MLPRegressor',
            'CV_RMSE': 0.000625,
            'CV_R2': 0.999772,
            'Holdout_RMSE': 0.000571,
            'Holdout_R2': 0.999834,
            'Holdout_RMSE_Positive': 0.000703,
            'Holdout_R2_Positive': 0.999832,
            'Reason': 'Strongest hazard-inclusive model, but it answers a different question because PGA is included.',
        },
    ]
    summary_df = pd.DataFrame(summary_rows)

    top5_path = paths['PROCESSED_DIR'] / 'ml_method_recommendation_top5_no_pga.csv'
    summary_path = paths['PROCESSED_DIR'] / 'ml_method_recommendation_summary.csv'
    figure_path = paths['FIGURES_DIR'] / 'ml_method_recommendation.png'

    top5_no_pga.to_csv(top5_path, index=False)
    summary_df.to_csv(summary_path, index=False)

    plt.style.use('seaborn-v0_8-whitegrid')
    fig = plt.figure(figsize=(13.5, 9))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.15, 1.0], hspace=0.38)

    ax1 = fig.add_subplot(gs[0, 0])
    labels = [
        f"{row['Feature Set']}\n{row['Model']}"
        for _, row in top5_no_pga.iloc[::-1].iterrows()
    ]
    values = top5_no_pga['CV_RMSE'].iloc[::-1].to_numpy()
    holdout_r2 = top5_no_pga['Holdout_R2'].iloc[::-1].to_numpy()
    colors = ['#cdd7ff'] * len(values)
    colors[-1] = '#365cf5'
    ax1.barh(labels, values, color=colors, edgecolor='#20306f')
    for idx, (value, r2) in enumerate(zip(values, holdout_r2)):
        ax1.text(value + 0.00012, idx, f"CV RMSE {value:.5f} | Holdout R² {r2:.3f}", va='center', fontsize=9)
    ax1.set_title('Top 5 no-PGA vulnerability models', fontsize=14, fontweight='bold')
    ax1.set_xlabel('Cross-validated RMSE (lower is better)')

    ax2 = fig.add_subplot(gs[1, 0])
    display = summary_df.copy()
    x = np.arange(len(display))
    width = 0.34
    ax2.bar(x - width / 2, display['Holdout_R2'], width, label='Holdout R²', color='#365cf5')
    ax2.bar(x + width / 2, display['Holdout_R2_Positive'], width, label='Positive-damage Holdout R²', color='#7fa7ff')
    ax2.set_xticks(x)
    ax2.set_xticklabels(
        ['Hazard-independent best', 'Pure structural-only', 'SVI-inclusive', 'Event-damage'],
        rotation=0,
        fontsize=9,
    )
    ax2.set_ylabel('R²')
    ax2.set_title('Recommended model by question', fontsize=14, fontweight='bold')
    ax2.legend(frameon=True)
    for idx, row in display.iterrows():
        ax2.text(idx - width / 2, row['Holdout_R2'] + 0.012, f"{row['Holdout_R2']:.3f}", ha='center', fontsize=8)
        ax2.text(idx + width / 2, row['Holdout_R2_Positive'] + 0.012, f"{row['Holdout_R2_Positive']:.3f}", ha='center', fontsize=8)

    fig.suptitle(
        'Bridge ML Method Recommendation\nNo-PGA vulnerability screening versus hazard-inclusive event damage',
        fontsize=16,
        fontweight='bold',
        y=0.98,
    )
    fig.text(
        0.01,
        0.01,
        'Source: data/processed/ml_hybrid_comparison.csv. Recommendation favors the strongest no-PGA structural model for baseline vulnerability,\n'
        'while retaining the PGA-inclusive MLP model only for event-specific damage scenarios.',
        fontsize=9,
    )
    plt.savefig(figure_path, dpi=160, bbox_inches='tight')
    plt.close(fig)

    print(f'Saved -> {top5_path}')
    print(f'Saved -> {summary_path}')
    print(f'Saved -> {figure_path}')


if __name__ == '__main__':
    main()
