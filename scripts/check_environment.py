from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from runtime_checks import ensure_packages, ensure_supported_runtime


def main() -> None:
    ensure_supported_runtime()
    ensure_packages(
        [
            "numpy",
            "pandas",
            "matplotlib",
            "scipy",
            "sklearn",
            "rasterio",
            "geopandas",
            "shapely",
            "seaborn",
            "rasterstats",
        ]
    )
    print("Environment check passed.")
    print("You are using a supported local Python runtime with the required packages installed.")


if __name__ == "__main__":
    main()
