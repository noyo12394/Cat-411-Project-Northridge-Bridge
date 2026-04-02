from pathlib import Path
from typing import Dict, List, Optional


def get_project_root(start: Optional[Path] = None) -> Path:
    """Return the repository root for notebooks or scripts launched inside the repo."""
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / 'data').exists() and (candidate / 'README.md').exists():
            return candidate
    raise FileNotFoundError('Could not locate the project root. Run from inside the repository.')


def build_paths(start: Optional[Path] = None) -> Dict[str, Path]:
    root = get_project_root(start)
    data_dir = root / 'data'
    processed_dir = data_dir / 'processed'
    change_detection_dir = data_dir / 'change_detection'
    figures_dir = root / 'figures'

    processed_dir.mkdir(parents=True, exist_ok=True)
    change_detection_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    return {
        'PROJECT_ROOT': root,
        'DATA_DIR': data_dir,
        'PROCESSED_DIR': processed_dir,
        'CHANGE_DETECTION_DIR': change_detection_dir,
        'FIGURES_DIR': figures_dir,
        'NBI_FILE': data_dir / 'CA25.txt',
        'PGA_RASTER': data_dir / 'pga_mean.flt',
        'PGA_RASTER_HDR': data_dir / 'pga_mean.hdr',
        'PGA_BRIDGE_CSV': processed_dir / 'pga_nbi_bridge.csv',
        'AFFECTED_BRIDGES_CSV': processed_dir / 'bridges_with_pga_affected_only.csv',
        'EDR_CSV': processed_dir / 'bridges_with_edr.csv',
        'SVI_CSV': processed_dir / 'bridges_with_svi.csv',
        'ML_PREDICTIONS_CSV': processed_dir / 'bridge_ml_predictions.csv',
        'FINAL_ANALYSIS_CSV': processed_dir / 'final_bridge_analysis.csv',
        'BRIDGE_SHP': change_detection_dir / 'pga_nbi_bridge.shp',
        'PRE_NDVI_TIF': change_detection_dir / 'Pre_Event_NDVI.tif',
        'POST_NDVI_TIF': change_detection_dir / 'Post_Event_NDVI.tif',
        'NDVI_CHANGE_TIF': change_detection_dir / 'NDVI_Change.tif',
        'RESULTS_CSV': change_detection_dir / 'pga_bridge_ndvi_200m.csv',
        'RESULTS_SHP': change_detection_dir / 'pga_bridge_ndvi_200m.shp',
    }


def require_paths(paths: Dict[str, Path], keys: List[str]) -> None:
    missing = [str(paths[key]) for key in keys if not paths[key].exists()]
    if missing:
        joined = '\n'.join(f'- {path}' for path in missing)
        raise FileNotFoundError(f'Missing required project files:\n{joined}')
