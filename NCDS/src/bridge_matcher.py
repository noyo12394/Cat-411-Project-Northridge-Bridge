"""
Module 2: Bridge-to-Network Spatial Matching

Takes NBI bridge inventory (with lat/lon) and snaps each bridge
to its nearest OSM network edge. Produces a mapping of
bridge_id -> (u, v, key) edge tuple.
"""
import osmnx as ox
import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import src.config as config


def load_nbi_bridges(filepath):
    """
    Load NBI bridge data. Expects a CSV or GeoDataFrame with at minimum:
    - STRUCTURE_NUMBER (bridge ID)
    - LATITUDE, LONGITUDE (decimal degrees)
    - YEAR_BUILT
    - DEGREES_SKEW
    - MAX_SPAN_LENGTH
    - NUM_SPANS
    - CONDITION_RATING (deck, superstructure, or substructure)

    Adapt column names to match your team's codebase output.
    """
    if str(filepath).endswith(".csv"):
        df = pd.read_csv(filepath)
    elif str(filepath).endswith(".gpkg") or str(filepath).endswith(".shp"):
        df = gpd.read_file(filepath)
    else:
        df = pd.read_csv(filepath)

    # Basic validation
    required = ["LATITUDE", "LONGITUDE"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Convert to GeoDataFrame if not already
    if not isinstance(df, gpd.GeoDataFrame):
        geometry = [Point(lon, lat) for lon, lat in zip(df["LONGITUDE"], df["LATITUDE"])]
        df = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

    print(f"Loaded {len(df)} bridges")
    return df


def snap_bridges_to_network(bridges_gdf, G, tolerance_m=config.BRIDGE_SNAP_TOLERANCE_M):
    """
    For each bridge, find the nearest edge in the network graph.

    Returns the bridges GeoDataFrame with added columns:
    - nearest_u, nearest_v, nearest_key: the matched edge
    - snap_distance_m: distance from bridge to nearest edge
    - matched: boolean, True if within tolerance
    """
    # Project to a metre-based CRS for distance calculation
    bridges_proj = bridges_gdf.to_crs(epsg=3857)

    # Get nearest edges using osmnx
    nearest_edges = ox.nearest_edges(
        G,
        X=bridges_gdf["LONGITUDE"].values,
        Y=bridges_gdf["LATITUDE"].values,
        return_dist=True
    )

    # nearest_edges returns (u, v, key, dist) arrays
    edges, dists = nearest_edges

    bridges_gdf = bridges_gdf.copy()
    bridges_gdf["nearest_u"] = [e[0] for e in edges]
    bridges_gdf["nearest_v"] = [e[1] for e in edges]
    bridges_gdf["nearest_key"] = [e[2] for e in edges]
    bridges_gdf["snap_distance_m"] = dists
    bridges_gdf["matched"] = bridges_gdf["snap_distance_m"] <= tolerance_m

    n_matched = bridges_gdf["matched"].sum()
    n_total = len(bridges_gdf)
    print(f"Matched {n_matched}/{n_total} bridges within {tolerance_m}m tolerance")
    print(f"  Median snap distance: {bridges_gdf['snap_distance_m'].median():.1f}m")
    print(f"  Max snap distance (matched): {bridges_gdf.loc[bridges_gdf['matched'], 'snap_distance_m'].max():.1f}m")

    return bridges_gdf


def get_bridge_edge_map(bridges_gdf):
    """
    Returns a dict mapping bridge ID to edge tuple for matched bridges only.
    {structure_number: (u, v, key)}
    """
    matched = bridges_gdf[bridges_gdf["matched"]].copy()
    id_col = "STRUCTURE_NUMBER" if "STRUCTURE_NUMBER" in matched.columns else matched.columns[0]

    bridge_edge_map = {}
    for _, row in matched.iterrows():
        bridge_edge_map[row[id_col]] = (
            row["nearest_u"],
            row["nearest_v"],
            row["nearest_key"]
        )

    return bridge_edge_map


if __name__ == "__main__":
    # Example usage
    from network_builder import load_network

    G = load_network()
    bridges = load_nbi_bridges(config.DATA_RAW / "nbi_bridges.csv")
    bridges = snap_bridges_to_network(bridges, G)

    matched_bridges = bridges[bridges["matched"]]
    out_path = config.DATA_PROCESSED / "bridges_matched.gpkg"
    matched_bridges.to_file(out_path, driver="GPKG")
    print(f"Saved matched bridges: {out_path}")
