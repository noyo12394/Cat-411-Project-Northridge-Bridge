"""
Prioritization Map
==================
Creates emergency priority maps for post-earthquake bridge inspection.
Bridges are sized by Damage-Weighted TDI (economic impact) and colored
by Damage State (structural severity). This surfaces the highest-priority
inspection targets: bridges that are both badly damaged AND on high-traffic
corridors.
"""

import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

from .damage_classification import DS_ORDER, DS_COLORS


def create_priority_map(gdf, adt_col="avg_daily_", save_path=None):
    """
    Generate a spatial priority map of bridge damage.

    Parameters
    ----------
    gdf : GeoDataFrame
        Bridge data with geometry, damage_state, and TDI_weighted columns.
    adt_col : str
        Average Daily Traffic column name.
    save_path : str, optional
        Path to save the figure.

    Returns
    -------
    fig : matplotlib Figure
    """
    gdf = gdf.copy()
    gdf["damage_state"] = gdf["damage_state"].fillna("DS0 – No Damage")
    gdf["TDI_weighted"] = gdf["TDI_weighted"].fillna(0)

    # Log-scaled marker sizes
    tdi_vals = gdf["TDI_weighted"].clip(lower=1)
    min_size, max_size = 2, 200
    log_tdi = np.log1p(tdi_vals)
    gdf["marker_size"] = min_size + (log_tdi / log_tdi.max()) * (max_size - min_size)
    gdf.loc[gdf["damage_state"] == "DS0 – No Damage", "marker_size"] = min_size

    fig, ax = plt.subplots(figsize=(14, 10))

    # Draw DS0 (undamaged) as background
    ds0 = gdf[gdf["damage_state"] == "DS0 – No Damage"]
    ax.scatter(
        ds0.geometry.x, ds0.geometry.y,
        s=min_size, c="#cccccc", alpha=0.15, zorder=1,
    )

    # Draw damaged bridges DS1 -> DS4 (increasing priority on top)
    for ds in DS_ORDER[1:]:
        sub = gdf[gdf["damage_state"] == ds]
        if len(sub) > 0:
            ax.scatter(
                sub.geometry.x, sub.geometry.y,
                s=sub["marker_size"], c=DS_COLORS[ds],
                alpha=0.7, edgecolors="black", linewidths=0.3, zorder=3,
                label=ds,
            )

    # Annotate top-10 highest TDI bridges
    top10 = gdf[gdf["damage_state"] != "DS0 – No Damage"].nlargest(10, "TDI_weighted")
    for _, row in top10.iterrows():
        ax.annotate(
            f"ADT={int(row[adt_col]):,}\n{row['damage_state'].split('–')[0].strip()}",
            (row.geometry.x, row.geometry.y),
            fontsize=6, fontweight="bold",
            xytext=(8, 8), textcoords="offset points",
            arrowprops=dict(arrowstyle="->", color="black", lw=0.5),
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="gray", alpha=0.8),
        )

    # Color legend
    patches = [mpatches.Patch(color=DS_COLORS[ds], label=ds) for ds in DS_ORDER]
    legend1 = ax.legend(handles=patches, loc="upper left", fontsize=8, title="Damage State")
    ax.add_artist(legend1)

    # Size legend
    tdi_examples = [1000, 10000, 50000, 100000]
    size_handles = []
    for tdi_val in tdi_examples:
        s = min_size + (np.log1p(tdi_val) / log_tdi.max()) * (max_size - min_size)
        size_handles.append(
            mlines.Line2D([], [], marker="o", color="gray", markersize=np.sqrt(s),
                          linestyle="None", label=f"{tdi_val:,.0f}")
        )
    ax.legend(handles=size_handles, loc="lower left", fontsize=7,
              title="TDI Scale (Vehicles/Day)", labelspacing=1.5)
    ax.add_artist(legend1)

    ax.set_xlabel("Longitude", fontsize=11)
    ax.set_ylabel("Latitude", fontsize=11)
    ax.set_title(
        "Phase 4: Emergency Priority Map\n"
        "Northridge 1994 Earthquake  |  Color = DS  |  Size = Damage-Weighted TDI",
        fontsize=13, fontweight="bold",
    )
    ax.grid(True, alpha=0.2)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
        print(f"Figure saved: {save_path}")
    plt.show()
    plt.close(fig)


def get_top_priority_bridges(df, n=20, adt_col="avg_daily_"):
    """
    Return top-N priority bridges ranked by TDI_weighted.

    Parameters
    ----------
    df : DataFrame or GeoDataFrame
        Must contain damage_state, TDI_weighted, pga, ndvi_chan, lat, long columns.
    n : int
        Number of top bridges to return.

    Returns
    -------
    top : DataFrame
    """
    damaged = df[df["damage_state"] != "DS0 – No Damage"]
    top = (
        damaged
        .nlargest(n, "TDI_weighted")[
            ["lat", "long", "damage_state", adt_col, "pga", "ndvi_chan", "TDI_weighted"]
        ]
        .copy()
    )
    top.columns = ["Lat", "Lon", "Damage State", "ADT", "PGA (g)", "NDVI Change", "Wt. TDI"]

    print(f"\nTop {n} Priority Bridges (Highest Damage-Weighted TDI)")
    print("=" * 90)
    print(top.to_string(index=False))
    return top
