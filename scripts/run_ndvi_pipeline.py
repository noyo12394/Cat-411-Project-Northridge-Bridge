from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import matplotlib
matplotlib.use("Agg")

import geopandas as gpd
import pandas as pd

from project_paths import build_paths, require_paths
from catastrophe_model.damage_classification import (
    classify_damage_states,
    plot_damage_distribution,
    print_damage_summary,
)
from catastrophe_model.proxy_fragility import (
    compute_fragility_curves,
    plot_fragility_curves,
    print_fragility_summary,
)
from catastrophe_model.economic_disruption import compute_tdi, plot_tdi, summarize_tdi
from catastrophe_model.prioritization_map import create_priority_map, get_top_priority_bridges
from modules.visualization import (
    plot_bridge_ndvi_map,
    plot_ndvi_change_only,
    plot_ndvi_rasters,
    plot_pga_vs_ndvi,
)


def main() -> None:
    paths = build_paths()
    require_paths(
        paths,
        [
            "PRE_NDVI_TIF",
            "POST_NDVI_TIF",
            "NDVI_CHANGE_TIF",
            "RESULTS_CSV",
            "RESULTS_SHP",
        ],
    )

    figures_dir = paths["FIGURES_DIR"]
    final_csv = paths["FINAL_ANALYSIS_CSV"]

    df = pd.read_csv(paths["RESULTS_CSV"])
    gdf = gpd.read_file(paths["RESULTS_SHP"])

    plot_ndvi_rasters(
        paths["PRE_NDVI_TIF"],
        paths["POST_NDVI_TIF"],
        paths["NDVI_CHANGE_TIF"],
        save_path=figures_dir / "NDVI_Raster_Maps.png",
    )
    plot_ndvi_change_only(
        paths["NDVI_CHANGE_TIF"],
        save_path=figures_dir / "NDVI_Change_Only.png",
    )
    plot_pga_vs_ndvi(df, save_path=figures_dir / "PGA_vs_NDVI.png")
    plot_bridge_ndvi_map(gdf, save_path=figures_dir / "Bridge_NDVI_Map.png")

    df = classify_damage_states(df)
    print_damage_summary(df)
    plot_damage_distribution(df, save_path=figures_dir / "Phase1_DamageClassification.png")

    empirical, fitted_params = compute_fragility_curves(df)
    print_fragility_summary(fitted_params)
    plot_fragility_curves(
        empirical,
        fitted_params,
        save_path=figures_dir / "Phase2_FragilityCurves.png",
    )

    df = compute_tdi(df)
    summarize_tdi(df)
    plot_tdi(df, save_path=figures_dir / "Phase3_EconomicDisruption.png")

    gdf = gdf.merge(
        df[["lat", "long", "damage_state", "TDI_weighted", "severity_weight"]],
        on=["lat", "long"],
        how="left",
    )
    gdf["damage_state"] = gdf["damage_state"].fillna("DS0 – No Damage")
    gdf["TDI_weighted"] = gdf["TDI_weighted"].fillna(0)
    create_priority_map(gdf, save_path=figures_dir / "Phase4_PriorityMap.png")
    get_top_priority_bridges(df, n=20)

    df.to_csv(final_csv, index=False)
    print(f"Final analysis saved: {final_csv}")


if __name__ == "__main__":
    main()
