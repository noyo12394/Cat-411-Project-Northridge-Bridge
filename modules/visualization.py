"""
Visualization Module
====================
Plotting functions for NDVI rasters, scatter analysis, and spatial maps.
All figures can be saved to the figures/ directory.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import seaborn as sns
import rasterio
import geopandas as gpd
from scipy import stats

sns.set_style("whitegrid")


def plot_ndvi_rasters(pre_path, post_path, change_path, save_path=None):
    """
    Three-panel map: Pre-Event NDVI, Post-Event NDVI, NDVI Change.
    """
    with rasterio.open(pre_path) as src:
        pre = src.read(1).astype(float)
        pre[pre == src.nodata] = np.nan if src.nodata else np.nan
        extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]

    with rasterio.open(post_path) as src:
        post = src.read(1).astype(float)
        post[post == src.nodata] = np.nan if src.nodata else np.nan

    with rasterio.open(change_path) as src:
        change = src.read(1).astype(float)
        change[change == src.nodata] = np.nan if src.nodata else np.nan

    ndvi_colors = [
        (0.6, 0.3, 0.1), (0.8, 0.6, 0.2), (0.95, 0.95, 0.7),
        (0.6, 0.8, 0.4), (0.2, 0.6, 0.2), (0.0, 0.4, 0.0),
    ]
    ndvi_cmap = mcolors.LinearSegmentedColormap.from_list("ndvi", ndvi_colors)
    change_cmap = plt.cm.RdYlGn

    fig, axes = plt.subplots(1, 3, figsize=(20, 6))

    axes[0].imshow(pre, extent=extent, cmap=ndvi_cmap, vmin=-0.2, vmax=0.6, aspect="auto")
    axes[0].set_title("Pre-Event NDVI", fontweight="bold")

    axes[1].imshow(post, extent=extent, cmap=ndvi_cmap, vmin=-0.2, vmax=0.6, aspect="auto")
    axes[1].set_title("Post-Event NDVI", fontweight="bold")

    im = axes[2].imshow(change, extent=extent, cmap=change_cmap, vmin=-0.2, vmax=0.2, aspect="auto")
    axes[2].set_title("NDVI Change (Post - Pre)", fontweight="bold")

    for ax in axes:
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")

    fig.colorbar(im, ax=axes, orientation="horizontal", fraction=0.05, pad=0.08, label="NDVI Change")
    plt.suptitle("Northridge 1994 Earthquake - NDVI Change Detection", fontsize=14, fontweight="bold")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
        print(f"Figure saved: {save_path}")
    plt.show()
    plt.close(fig)


def plot_ndvi_change_only(change_path, save_path=None):
    """Single-panel NDVI change map."""
    with rasterio.open(change_path) as src:
        change = src.read(1).astype(float)
        change[change == src.nodata] = np.nan if src.nodata else np.nan
        extent = [src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top]

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(change, extent=extent, cmap="RdYlGn", vmin=-0.2, vmax=0.2, aspect="auto")
    ax.set_title("NDVI Change Detection - Northridge 1994", fontsize=14, fontweight="bold")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    fig.colorbar(im, ax=ax, label="NDVI Change", shrink=0.7)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
        print(f"Figure saved: {save_path}")
    plt.show()
    plt.close(fig)


def plot_pga_vs_ndvi(df, save_path=None):
    """
    Scatter plot of PGA vs NDVI change with linear regression.

    Parameters
    ----------
    df : DataFrame
        Must contain 'pga' and 'ndvi_chan' columns.
    """
    df_clean = df.dropna(subset=["pga", "ndvi_chan"])

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(data=df_clean, x="pga", y="ndvi_chan", alpha=0.3, edgecolor=None, ax=ax)

    slope, intercept, r, p, _ = stats.linregress(df_clean["pga"], df_clean["ndvi_chan"])
    x_line = np.linspace(df_clean["pga"].min(), df_clean["pga"].max(), 100)
    ax.plot(x_line, slope * x_line + intercept, "r-", linewidth=2,
            label=f"y = {slope:.4f}x + {intercept:.4f}\nR² = {r**2:.4f}, p = {p:.2e}")

    ax.set_xlabel("Peak Ground Acceleration (g)", fontsize=12)
    ax.set_ylabel("NDVI Change", fontsize=12)
    ax.set_title("PGA vs NDVI Change at Bridge Locations", fontsize=14, fontweight="bold")
    ax.legend(fontsize=10)
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
        print(f"Figure saved: {save_path}")
    plt.show()
    plt.close(fig)


def plot_bridge_ndvi_map(gdf, column="ndvi_chan", save_path=None):
    """
    Choropleth map of bridges colored by NDVI change.

    Parameters
    ----------
    gdf : GeoDataFrame
        Bridge data with geometry and ndvi_chan column.
    """
    gdf_clean = gdf.dropna(subset=[column])

    fig, ax = plt.subplots(figsize=(12, 8))
    gdf_clean.plot(
        column=column,
        cmap="RdYlGn",
        markersize=5,
        legend=True,
        legend_kwds={"label": "NDVI Change", "shrink": 0.6},
        ax=ax,
    )
    ax.set_title("Bridge NDVI Change - Northridge 1994", fontsize=14, fontweight="bold")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    plt.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=200, bbox_inches="tight")
        print(f"Figure saved: {save_path}")
    plt.show()
    plt.close(fig)
