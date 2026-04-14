from pathlib import Path
import sys

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

from project_paths import build_paths
from scripts.run_ml_hybrid_analysis import (
    FEATURE_SETS,
    RANDOM_STATE,
    make_models,
    make_preprocessor,
    load_statewide_bridge_dataset,
    table_to_markdown,
)

sns.set_theme(style='whitegrid')

FEATURE_SET_NAME = 'Event Damage Hybrid'
DEFAULT_MODEL_NAME = 'MLPRegressor'
SCENARIOS = [
    ('Observed PGA', None),
    ('Scenario 0.05g', 0.05),
    ('Scenario 0.10g', 0.10),
    ('Scenario 0.20g', 0.20),
    ('Scenario 0.40g', 0.40),
]
RISK_BANDS = [
    ('Low', 0.00, 0.02),
    ('Moderate', 0.02, 0.08),
    ('High', 0.08, 0.25),
    ('Very High', 0.25, np.inf),
]


def choose_event_model_name(processed_dir: Path) -> str:
    comparison_path = processed_dir / 'ml_hybrid_best_by_feature_set.csv'
    if comparison_path.exists():
        comparison_df = pd.read_csv(comparison_path)
        match = comparison_df.loc[comparison_df['Feature Set'] == FEATURE_SET_NAME, 'Model']
        if not match.empty:
            return str(match.iloc[0])
    return DEFAULT_MODEL_NAME


def assign_risk_band(edr: float) -> str:
    for label, lower, upper in RISK_BANDS:
        if lower <= edr < upper:
            return label
    return 'Unknown'


def fit_event_model(df: pd.DataFrame, model_name: str):
    features = FEATURE_SETS[FEATURE_SET_NAME]
    preprocessor = make_preprocessor(features)
    model = make_models(preprocessor, log_target=True)[model_name]
    model.fit(df[features], df['EDR'])
    return model, features


def score_scenarios(df: pd.DataFrame, model, features: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    bridge_frames = []
    summary_rows = []

    for scenario_name, scenario_pga in SCENARIOS:
        scenario_df = df.copy()
        if scenario_pga is not None:
            scenario_df['pga'] = scenario_pga

        preds = np.clip(model.predict(scenario_df[features]), 0, None)
        scored = scenario_df[
            ['join_id', 'STRUCTURE_NUMBER_008', 'COUNTY_CODE_003', 'HWB_CLASS', 'design_era_1989']
        ].copy()
        scored['Scenario'] = scenario_name
        scored['Scenario_PGA_g'] = scenario_pga if scenario_pga is not None else scored.get('pga', np.nan)
        scored['Predicted_EDR'] = preds
        scored['Risk_Band'] = [assign_risk_band(val) for val in preds]
        scored['Statewide_Rank'] = scored['Predicted_EDR'].rank(method='dense', ascending=False).astype(int)
        bridge_frames.append(scored)

        summary_rows.append({
            'Scenario': scenario_name,
            'Scenario_PGA_g': np.nan if scenario_pga is None else scenario_pga,
            'Mean_Predicted_EDR': float(np.mean(preds)),
            'Median_Predicted_EDR': float(np.median(preds)),
            'P90_Predicted_EDR': float(np.quantile(preds, 0.90)),
            'P95_Predicted_EDR': float(np.quantile(preds, 0.95)),
            'Bridges_EDR_ge_0_02': int(np.sum(preds >= 0.02)),
            'Bridges_EDR_ge_0_08': int(np.sum(preds >= 0.08)),
            'Bridges_EDR_ge_0_25': int(np.sum(preds >= 0.25)),
        })

    return pd.concat(bridge_frames, ignore_index=True), pd.DataFrame(summary_rows)


def save_summary_plot(summary_df: pd.DataFrame, path: Path) -> None:
    plot_df = summary_df[summary_df['Scenario'] != 'Observed PGA'].copy()
    plt.figure(figsize=(7.5, 5.5))
    plt.plot(plot_df['Scenario_PGA_g'], plot_df['Mean_Predicted_EDR'], marker='o', linewidth=2, label='Mean EDR')
    plt.plot(plot_df['Scenario_PGA_g'], plot_df['P95_Predicted_EDR'], marker='s', linewidth=2, label='95th percentile EDR')
    plt.xlabel('Uniform scenario PGA (g)')
    plt.ylabel('Predicted EDR')
    plt.title('Future earthquake scenario sensitivity')
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()


def save_risk_band_plot(bridge_df: pd.DataFrame, path: Path) -> None:
    plot_df = (
        bridge_df.groupby(['Scenario', 'Risk_Band'], as_index=False)
        .size()
        .rename(columns={'size': 'Bridge_Count'})
    )
    plot_df['Risk_Band'] = pd.Categorical(
        plot_df['Risk_Band'],
        categories=[label for label, _, _ in RISK_BANDS],
        ordered=True,
    )
    plot_df = plot_df.sort_values(['Scenario', 'Risk_Band'])

    plt.figure(figsize=(9.5, 5.5))
    sns.barplot(data=plot_df, x='Scenario', y='Bridge_Count', hue='Risk_Band', palette='YlOrRd')
    plt.xlabel('')
    plt.ylabel('Number of bridges')
    plt.title('Predicted bridge risk bands across future PGA scenarios')
    plt.xticks(rotation=20, ha='right')
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()


def save_top_counties_plot(bridge_df: pd.DataFrame, path: Path) -> None:
    scenario_df = bridge_df[bridge_df['Scenario'] == 'Scenario 0.20g'].copy()
    county_summary = (
        scenario_df.groupby('COUNTY_CODE_003', as_index=False)
        .agg(
            Mean_Predicted_EDR=('Predicted_EDR', 'mean'),
            P95_Predicted_EDR=('Predicted_EDR', lambda s: float(np.quantile(s, 0.95))),
        )
        .sort_values('Mean_Predicted_EDR', ascending=False)
        .head(12)
    )

    plt.figure(figsize=(9.5, 5.8))
    sns.barplot(
        data=county_summary,
        y='COUNTY_CODE_003',
        x='Mean_Predicted_EDR',
        hue='COUNTY_CODE_003',
        dodge=False,
        palette='crest',
        legend=False,
    )
    plt.xlabel('Mean predicted EDR at 0.20g')
    plt.ylabel('County code')
    plt.title('Top county-level bridge vulnerability under a 0.20g scenario')
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches='tight')
    plt.close()


def write_doc(path: Path, model_name: str, summary_df: pd.DataFrame) -> None:
    doc_summary_df = summary_df.copy()
    doc_summary_df['Scenario_PGA_g'] = doc_summary_df['Scenario_PGA_g'].apply(
        lambda value: 'Observed pattern' if pd.isna(value) else value
    )
    lines = [
        '# Future Scenario Scoring',
        '',
        'This exploratory add-on fits the event-damage model on the statewide bridge inventory and then rescores the full inventory under uniform hypothetical PGA scenarios. It is intended for future-earthquake scenario planning rather than intrinsic vulnerability ranking.',
        '',
        '## Model Choice',
        '',
        f'- Feature set: `{FEATURE_SET_NAME}`',
        f'- Model: `{model_name}`',
        '- Target: HAZUS-derived `EDR`',
        '- Target transform: `log1p -> expm1`',
        '',
        '## Scenario Summary',
        '',
        table_to_markdown(doc_summary_df),
        '',
        '## Interpretation',
        '',
        '- `Observed PGA` keeps the original Northridge-like shaking pattern already stored in the dataset.',
        '- The uniform scenarios are stress tests: every bridge is rescored as if it experienced the same PGA level.',
        '- These outputs are useful for prioritizing bridge screening before a future event, but they are still surrogate estimates because the target is HAZUS-derived `EDR` rather than observed bridge damage.',
        '',
        '## Generated Artifacts',
        '',
        '- `data/processed/future_scenario_summary.csv`',
        '- `data/processed/future_scenario_bridge_scores.csv`',
        '- `figures/future_scenario_mean_edr.png`',
        '- `figures/future_scenario_risk_bands.png`',
        '- `figures/future_scenario_top_counties.png`',
    ]
    path.write_text('\n'.join(lines) + '\n')


def main() -> None:
    paths = build_paths()
    processed_dir = paths['PROCESSED_DIR']
    figures_dir = paths['FIGURES_DIR']
    figures_dir.mkdir(parents=True, exist_ok=True)

    model_name = choose_event_model_name(processed_dir)
    df = load_statewide_bridge_dataset(paths)
    model, features = fit_event_model(df, model_name)
    bridge_scores_df, summary_df = score_scenarios(df, model, features)

    bridge_scores_df.to_csv(processed_dir / 'future_scenario_bridge_scores.csv', index=False)
    summary_df.to_csv(processed_dir / 'future_scenario_summary.csv', index=False)

    save_summary_plot(summary_df, figures_dir / 'future_scenario_mean_edr.png')
    save_risk_band_plot(bridge_scores_df, figures_dir / 'future_scenario_risk_bands.png')
    save_top_counties_plot(bridge_scores_df, figures_dir / 'future_scenario_top_counties.png')

    write_doc(PROJECT_ROOT / 'docs' / 'FUTURE_SCENARIO_SCORING.md', model_name, summary_df)

    print(summary_df.to_string(index=False))
    print('Saved: docs/FUTURE_SCENARIO_SCORING.md')


if __name__ == '__main__':
    main()
