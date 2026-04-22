from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib.pyplot as plt
import pandas as pd

from project_paths import build_paths


plt.style.use('seaborn-v0_8-whitegrid')


def pretty_feature(name: str) -> str:
    return (
        name.replace('_log1p', ' (log1p)')
        .replace('_', ' ')
        .replace('HWB CLASS', 'HWB class')
        .replace('SVI', 'SVI')
        .title()
    )


def save_global_importance_figure(
    disciplined_importance: pd.DataFrame,
    recommended_importance: pd.DataFrame,
    linear_coeffs: pd.DataFrame,
    output_path: Path,
) -> None:
    structural = (
        disciplined_importance.loc[
            disciplined_importance['Model Family'] == 'Structural-only core',
            ['Feature', 'Importance_R2_Decrease'],
        ]
        .sort_values('Importance_R2_Decrease', ascending=True)
        .tail(10)
        .copy()
    )
    structural['Label'] = structural['Feature'].map(pretty_feature)

    recommended = (
        recommended_importance[['Feature', 'Importance']]
        .sort_values('Importance', ascending=True)
        .tail(10)
        .copy()
    )
    recommended['Label'] = recommended['Feature'].map(pretty_feature)

    linear = (
        linear_coeffs.loc[
            (linear_coeffs['Model Family'] == 'Structural-only core')
            & (linear_coeffs['Model'] == 'Elastic Net'),
            ['Source Feature', 'Abs_Coefficient'],
        ]
        .groupby('Source Feature', as_index=False)['Abs_Coefficient']
        .max()
        .sort_values('Abs_Coefficient', ascending=True)
        .tail(10)
        .copy()
    )
    linear['Label'] = linear['Source Feature'].map(pretty_feature)

    fig, axes = plt.subplots(1, 3, figsize=(18, 8))

    axes[0].barh(structural['Label'], structural['Importance_R2_Decrease'], color='#2855c5')
    axes[0].set_title('Structural-only permutation importance')
    axes[0].set_xlabel('R2 decrease after permutation')

    axes[1].barh(recommended['Label'], recommended['Importance'], color='#2d7f5e')
    axes[1].set_title('Recommended statewide model importance')
    axes[1].set_xlabel('Importance')

    axes[2].barh(linear['Label'], linear['Abs_Coefficient'], color='#ad6a1f')
    axes[2].set_title('Linear baseline coefficient magnitude')
    axes[2].set_xlabel('Absolute standardized coefficient')

    fig.suptitle('Explainable AI view of the bridge vulnerability models', fontsize=16, fontweight='bold')
    fig.text(
        0.5,
        0.02,
        'Tree-model panels show global importance. The linear panel shows coefficient magnitude only; none of these plots imply causality.',
        ha='center',
        fontsize=10,
        color='#4b5563',
    )
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    fig.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def save_role_summary_figure(
    ablation_df: pd.DataFrame,
    proxy_df: pd.DataFrame,
    recommended_importance: pd.DataFrame,
    output_path: Path,
) -> None:
    ablation = ablation_df.copy()
    ablation['Label'] = ablation['Question'].replace(
        {
            'Does SVI improve over structural-only?': 'Add SVI to intrinsic model',
            'Does NDVI add value only in post-event setup?': 'Add NDVI to post-event model',
        }
    )

    hybrid = proxy_df.loc[proxy_df['Model'] == 'Hybrid Proxy Model'].iloc[0]
    hazus = proxy_df.loc[proxy_df['Model'] == 'Univariate (HAZUS)'].iloc[0]
    improvement_rows = pd.DataFrame(
        {
            'Metric': ['Exact accuracy', 'Within-1-state', 'Weighted kappa', 'Macro F1'],
            'HAZUS baseline': [
                hazus['Exact_Accuracy'],
                hazus['Within_1_State_Accuracy'],
                hazus['Weighted_Kappa'],
                hazus['Macro_F1'],
            ],
            'Hybrid proxy': [
                hybrid['Exact_Accuracy'],
                hybrid['Within_1_State_Accuracy'],
                hybrid['Weighted_Kappa'],
                hybrid['Macro_F1'],
            ],
        }
    )

    svi_importance = recommended_importance.loc[
        recommended_importance['Feature'] == 'SVI', 'Importance'
    ].iloc[0]

    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    colors = ['#d97706' if delta > 0 else '#059669' for delta in ablation['Delta CV_RMSE']]
    axes[0].barh(ablation['Label'], ablation['Delta CV_RMSE'], color=colors)
    axes[0].axvline(0, color='#111827', linewidth=1)
    axes[0].set_title('Ablation result for SVI and NDVI')
    axes[0].set_xlabel('Change in best cross-validated RMSE')
    for idx, row in ablation.iterrows():
        axes[0].text(
            row['Delta CV_RMSE'] + 0.00001,
            idx,
            f"{row['Delta CV_RMSE']:+.6f}",
            va='center',
            fontsize=9,
            color='#374151',
        )
    axes[0].text(
        0.02,
        0.02,
        f"SVI importance in the recommended statewide model: {svi_importance:.4f}",
        transform=axes[0].transAxes,
        fontsize=10,
        color='#374151',
        bbox=dict(boxstyle='round,pad=0.35', facecolor='#f3f4f6', edgecolor='#d1d5db'),
    )

    x = range(len(improvement_rows))
    width = 0.35
    axes[1].bar(
        [i - width / 2 for i in x],
        improvement_rows['HAZUS baseline'],
        width=width,
        label='HAZUS baseline',
        color='#94a3b8',
    )
    axes[1].bar(
        [i + width / 2 for i in x],
        improvement_rows['Hybrid proxy'],
        width=width,
        label='Hybrid proxy',
        color='#2563eb',
    )
    axes[1].set_xticks(list(x))
    axes[1].set_xticklabels(improvement_rows['Metric'], rotation=15, ha='right')
    axes[1].set_ylim(0, 1.0)
    axes[1].set_title('NDVI-aware proxy validation improves post-event agreement')
    axes[1].set_ylabel('Score')
    axes[1].legend(frameon=True)

    fig.suptitle('Role separation for SVI and NDVI', fontsize=16, fontweight='bold')
    fig.text(
        0.5,
        0.02,
        'SVI is most useful as interpretable structural context. NDVI shows its value most clearly in the post-event proxy-validation branch.',
        ha='center',
        fontsize=10,
        color='#4b5563',
    )
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])
    fig.savefig(output_path, dpi=200, bbox_inches='tight')
    plt.close(fig)


def main() -> None:
    paths = build_paths()
    processed_dir = paths['PROCESSED_DIR']
    figures_dir = paths['FIGURES_DIR']
    figures_dir.mkdir(parents=True, exist_ok=True)

    disciplined_importance = pd.read_csv(processed_dir / 'ml_disciplined_permutation_importance.csv')
    recommended_importance = pd.read_csv(processed_dir / 'ml_recommended_hybrid_feature_importance.csv')
    linear_coeffs = pd.read_csv(processed_dir / 'ml_disciplined_linear_coefficients.csv')
    ablation_df = pd.read_csv(processed_dir / 'ml_disciplined_ablation_summary.csv')
    proxy_df = pd.read_csv(processed_dir / 'proxy_validation_metrics.csv')

    save_global_importance_figure(
        disciplined_importance,
        recommended_importance,
        linear_coeffs,
        figures_dir / 'xai_global_feature_importance.png',
    )
    save_role_summary_figure(
        ablation_df,
        proxy_df,
        recommended_importance,
        figures_dir / 'xai_svi_ndvi_role_summary.png',
    )

    print('Saved:', figures_dir / 'xai_global_feature_importance.png')
    print('Saved:', figures_dir / 'xai_svi_ndvi_role_summary.png')


if __name__ == '__main__':
    main()
