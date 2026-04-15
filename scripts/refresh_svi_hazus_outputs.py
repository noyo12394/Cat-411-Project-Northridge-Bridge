from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from runtime_checks import ensure_packages, ensure_supported_runtime

ensure_supported_runtime()
ensure_packages(["numpy", "pandas", "scipy"])

import pandas as pd

from project_paths import build_paths, require_paths
from svi_methodology import (
    DEFAULT_FRAGILITY_MEDIAN_METHOD,
    clean_kind_series,
    compute_damage_probabilities,
)
from scripts.run_ml_hybrid_analysis import assign_hwb_class


def main() -> None:
    paths = build_paths()
    require_paths(paths, ["PGA_BRIDGE_CSV"])

    bridge_df = pd.read_csv(paths["PGA_BRIDGE_CSV"], low_memory=False)
    bridge_df["kind"] = clean_kind_series(bridge_df["STRUCTURE_KIND_043A"])
    bridge_df["type"] = clean_kind_series(bridge_df["STRUCTURE_TYPE_043B"])
    bridge_df["HWB_CLASS"] = bridge_df.apply(assign_hwb_class, axis=1)

    bridge_df = compute_damage_probabilities(
        bridge_df,
        median_method=DEFAULT_FRAGILITY_MEDIAN_METHOD,
    )

    bridge_df.to_csv(paths["EDR_CSV"], index=False)
    bridge_df.to_csv(paths["SVI_CSV"], index=False)

    summary_cols = [
        "SVI",
        "SVI_RAW",
        "YR_MULTIPLIER",
        "BETA_SVI",
        "P_DS0",
        "P_DS1",
        "P_DS2",
        "P_DS3",
        "P_DS4",
        "EDR",
    ]
    print(bridge_df[summary_cols].describe().to_string())
    print("Saved:", paths["EDR_CSV"])
    print("Saved:", paths["SVI_CSV"])


if __name__ == "__main__":
    main()
