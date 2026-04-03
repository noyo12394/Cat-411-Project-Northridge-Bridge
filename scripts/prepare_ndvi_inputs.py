from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
MODULES_DIR = PROJECT_ROOT / "modules"
if str(MODULES_DIR) not in sys.path:
    sys.path.insert(0, str(MODULES_DIR))

from project_paths import build_paths
from change_detection import build_bridge_shapefile, extract_bridge_ndvi


def main() -> None:
    paths = build_paths()

    bridge_csv = paths['PGA_BRIDGE_CSV']
    bridge_shp = paths['BRIDGE_SHP']
    pre_ndvi = paths['PRE_NDVI_TIF']
    post_ndvi = paths['POST_NDVI_TIF']
    results_csv = paths['RESULTS_CSV']
    results_shp = paths['RESULTS_SHP']

    print('Preparing NDVI inputs...')
    print(f'- bridge CSV: {bridge_csv}')
    print(f'- bridge shapefile: {bridge_shp}')

    if not bridge_shp.exists():
        build_bridge_shapefile(bridge_csv, bridge_shp)
    else:
        print('Bridge shapefile already exists; skipping rebuild.')

    if pre_ndvi.exists() and post_ndvi.exists():
        print('NDVI rasters found. Extracting bridge-level NDVI summaries...')
        extract_bridge_ndvi(
            bridge_shp_path=bridge_shp,
            pre_ndvi_path=pre_ndvi,
            post_ndvi_path=post_ndvi,
            output_csv=results_csv,
            output_shp=results_shp,
        )
    else:
        print('NDVI rasters are still missing, so bridge-level NDVI extraction was skipped.')
        print('Expected files:')
        print(f'  - {pre_ndvi}')
        print(f'  - {post_ndvi}')
        print('Once those files exist, rerun this script to create:')
        print(f'  - {results_csv}')
        print(f'  - {results_shp}')


if __name__ == '__main__':
    main()
