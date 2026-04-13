from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

from project_paths import build_paths
from scripts.run_ml_hybrid_analysis import (
    main as run_full_ml_refresh,
    save_actual_vs_predicted,
    save_feature_importance,
    save_decile_plot,
    save_mutual_information_plot,
)


REQUIRED_ARTIFACTS = [
    'ml_recommended_hybrid_predictions.csv',
    'ml_recommended_hybrid_feature_importance.csv',
    'ml_feature_screen_mutual_info.csv',
]


def main() -> None:
    paths = build_paths()
    processed_dir = paths['PROCESSED_DIR']
    figures_dir = paths['FIGURES_DIR']
    figures_dir.mkdir(parents=True, exist_ok=True)

    missing = [name for name in REQUIRED_ARTIFACTS if not (processed_dir / name).exists()]
    if missing:
        print('Recommended ML artifacts are missing, so the full ML refresh will be run first:')
        for name in missing:
            print('-', name)
        run_full_ml_refresh()
        return

    pred_df = pd.read_csv(processed_dir / 'ml_recommended_hybrid_predictions.csv')
    importance_df = pd.read_csv(processed_dir / 'ml_recommended_hybrid_feature_importance.csv')
    mi_df = pd.read_csv(processed_dir / 'ml_feature_screen_mutual_info.csv')

    y_true = pred_df['EDR_actual'].to_numpy()
    y_pred = pred_df['EDR_predicted'].to_numpy()

    save_actual_vs_predicted(
        y_true,
        y_pred,
        'Recommended statewide model',
        figures_dir / 'ml_recommended_hybrid_actual_vs_predicted.png',
        log_scale=False,
    )
    save_actual_vs_predicted(
        y_true,
        y_pred,
        'Recommended statewide model (log scale)',
        figures_dir / 'ml_recommended_hybrid_log_actual_vs_predicted.png',
        log_scale=True,
    )
    save_feature_importance(
        importance_df,
        'Top features for the recommended statewide model',
        figures_dir / 'ml_recommended_hybrid_feature_importance.png',
    )
    save_decile_plot(
        pred_df,
        'Recommended statewide model decile calibration',
        figures_dir / 'ml_recommended_hybrid_decile_calibration.png',
    )
    save_mutual_information_plot(
        mi_df,
        'Mutual-information screen for recommended statewide features',
        figures_dir / 'ml_recommended_hybrid_mutual_information.png',
    )

    metrics_path = processed_dir / 'ml_recommended_hybrid_metrics.csv'
    if metrics_path.exists():
        metrics_df = pd.read_csv(metrics_path)
        print(metrics_df.to_string(index=False))
    print('Refreshed recommended statewide ML figures.')


if __name__ == '__main__':
    main()
