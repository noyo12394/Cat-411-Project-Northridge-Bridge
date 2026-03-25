"""
Change Detection Module
=======================
Computes NDVI change from raster TIFFs and extracts per-bridge NDVI
statistics using zonal statistics (200m buffer around each bridge).

Inputs:
    - Pre_Event_NDVI.tif, Post_Event_NDVI.tif
    - Bridge shapefile with PGA values

Outputs:
    - DataFrame with pre_ndvi, post_ndvi, ndvi_change per bridge
    - Optional CSV and shapefile exports
"""

import os
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterstats import zonal_stats


def compute_ndvi_change(pre_ndvi_path, post_ndvi_path, output_path=None):
    """
    Compute NDVI change raster (post - pre).

    Parameters
    ----------
    pre_ndvi_path : str
        Path to pre-event NDVI GeoTIFF.
    post_ndvi_path : str
        Path to post-event NDVI GeoTIFF.
    output_path : str, optional
        Path to save the change raster.

    Returns
    -------
    ndvi_change : np.ndarray
    profile : dict
        Rasterio profile for the output.
    """
    with rasterio.open(pre_ndvi_path) as src:
        pre = src.read(1).astype(float)
        pre[pre == src.nodata] = np.nan if src.nodata is not None else np.nan
        profile = src.profile.copy()

    with rasterio.open(post_ndvi_path) as src:
        post = src.read(1).astype(float)
        post[post == src.nodata] = np.nan if src.nodata is not None else np.nan

    ndvi_change = post - pre

    if output_path:
        profile.update(dtype="float32", nodata=np.nan)
        with rasterio.open(output_path, "w", **profile) as dst:
            dst.write(ndvi_change.astype(np.float32), 1)
        print(f"NDVI change raster saved: {output_path}")

    return ndvi_change, profile


def extract_bridge_ndvi(
    bridge_shp_path,
    pre_ndvi_path,
    post_ndvi_path,
    buffer_m=200,
    output_csv=None,
    output_shp=None,
):
    """
    Extract mean NDVI values within a buffer around each bridge.

    Parameters
    ----------
    bridge_shp_path : str
        Path to bridge shapefile (with PGA attribute).
    pre_ndvi_path : str
        Path to pre-event NDVI GeoTIFF.
    post_ndvi_path : str
        Path to post-event NDVI GeoTIFF.
    buffer_m : int
        Buffer radius in meters (default 200m).
    output_csv : str, optional
        Path to save results as CSV.
    output_shp : str, optional
        Path to save results as shapefile.

    Returns
    -------
    bridges : GeoDataFrame
        Bridge data with pre_ndvi, post_ndvi, ndvi_chan columns added.
    """
    print("1. Loading bridge data...")
    bridges = gpd.read_file(bridge_shp_path)

    # Project to metric CRS for accurate buffering (UTM Zone 11N for LA)
    print(f"2. Creating {buffer_m}m buffers around each bridge...")
    bridges_proj = bridges.to_crs(epsg=32611)
    buffers_proj = bridges_proj.copy()
    buffers_proj.geometry = bridges_proj.geometry.buffer(buffer_m)

    # Reproject buffers to match raster CRS
    with rasterio.open(pre_ndvi_path) as src:
        raster_crs = src.crs
    buffers_raster_crs = buffers_proj.to_crs(raster_crs)

    print("3. Extracting mean Pre-Event and Post-Event NDVI...")
    pre_stats = zonal_stats(buffers_raster_crs, pre_ndvi_path, stats="mean")
    post_stats = zonal_stats(buffers_raster_crs, post_ndvi_path, stats="mean")

    bridges["pre_ndvi"] = [
        s["mean"] if s["mean"] is not None else float("nan") for s in pre_stats
    ]
    bridges["post_ndvi"] = [
        s["mean"] if s["mean"] is not None else float("nan") for s in post_stats
    ]

    print("4. Calculating NDVI change (Post - Pre)...")
    bridges["ndvi_chan"] = bridges["post_ndvi"] - bridges["pre_ndvi"]

    # Save outputs
    if output_csv:
        pd.DataFrame(bridges.drop(columns="geometry")).to_csv(output_csv, index=False)
        print(f"Results saved: {output_csv}")

    if output_shp:
        bridges.to_file(output_shp)
        print(f"Results saved: {output_shp}")

    valid = bridges["ndvi_chan"].notna().sum()
    print(f"Done! {valid}/{len(bridges)} bridges have valid NDVI change values.")
    return bridges
