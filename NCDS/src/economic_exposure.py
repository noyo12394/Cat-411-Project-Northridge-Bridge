"""
Module 4: Economic Activity Exposure

Scores each bridge by the economic activity that depends on it:
- LEHD LODES job density within network-distance catchment
- AADT (Annual Average Daily Traffic) from NBI
- FHWA NHFN freight corridor designation

Data sources (all verified):
- LODES WAC: ca_wac_S000_JT00_2023_fixed.csv (262,357 CA blocks, 17.8M jobs)
- NHFN: National_Highway_Freight_Network_(NHFN).shp (5,319 CA segments)
- AADT: ADT_029 column from NBI bridges_matched.gpkg
- Demographics: National.gdb / DemographicsByCensusTract (HAZUS, CA filter)
"""
import geopandas as gpd
import pandas as pd
import networkx as nx
import numpy as np
from shapely.geometry import Point
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


# ── Data Loaders ───────────────────────────────────────────────────────────────

def load_lodes_data(filepath=config.LODES_WAC):
    """
    Load LEHD LODES workplace area characteristics.
    Returns DataFrame with w_geocode (15-digit Census block) and C000.
    """
    df = pd.read_csv(filepath, dtype={"w_geocode": str})
    df["w_geocode"] = df["w_geocode"].str.zfill(15)
    df["tract_id"]  = df["w_geocode"].str[:11]
    print(f"Loaded LODES data: {len(df):,} blocks, "
          f"{df['C000'].sum():,.0f} total jobs")
    return df


def load_tract_demographics(gdb_path=config.HAZUS_GDB,
                            state=config.STUDY_STATE):
    """
    Load Census tract geometry and population from HAZUS National GDB.
    Joins CensusTract geometry with DemographicsByCensusTract.
    Returns GeoDataFrame with tract_id, Population, geometry.
    """
    print(f"Loading Census tract demographics for {state}...")

    tracts = gpd.read_file(gdb_path, layer="CensusTract")
    tracts = tracts[tracts["StateAbbr"] == state].copy()
    tracts = tracts.rename(columns={"Tract": "tract_id"})

    demos = gpd.read_file(gdb_path, layer="DemographicsByCensusTract")
    demos = demos[demos["StateAbbr"] == state][
        ["Tract", "Population"]
    ].copy()
    demos = demos.rename(columns={"Tract": "tract_id"})

    tracts = tracts.merge(demos, on="tract_id", how="left")
    tracts["Population"] = tracts["Population"].fillna(0)

    print(f"  Loaded {len(tracts):,} tracts, "
          f"population: {tracts['Population'].sum():,.0f}")
    return tracts


def load_freight_corridors(filepath=config.NHFN_FREIGHT,
                           tier=config.FREIGHT_TIER):
    """
    Load FHWA National Highway Freight Network shapefile.
    Filters to California (STATE_CODE == 6).
    """
    gdf = gpd.read_file(filepath)
    gdf = gdf[gdf["STATE_CODE"] == 6].copy()

    if tier is not None:
        gdf = gdf[gdf["NHFN_CODE"] == tier].copy()

    print(f"Loaded {len(gdf):,} California freight corridor segments"
          f"{f' (tier {tier})' if tier else ' (all tiers)'}")
    return gdf


# ── Spatial Helpers ────────────────────────────────────────────────────────────

def build_tract_job_lookup(lodes_df):
    """Aggregate LODES block-level jobs to tract level."""
    tract_jobs = (
        lodes_df.groupby("tract_id")["C000"]
        .sum()
        .to_dict()
    )
    print(f"Aggregated jobs to {len(tract_jobs):,} tracts")
    return tract_jobs


def snap_tracts_to_network(tracts_gdf, G):
    """Snap tract centroids to nearest OSM network node."""
    import osmnx as ox

    tracts_proj = tracts_gdf.to_crs(epsg=4326)
    centroids   = tracts_proj.geometry.to_crs(epsg=3857).centroid.to_crs(epsg=4326)

    nearest_nodes = ox.nearest_nodes(
        G,
        X=centroids.x.values,
        Y=centroids.y.values
    )

    tracts_gdf = tracts_gdf.copy()
    tracts_gdf["network_node"] = nearest_nodes
    print(f"Snapped {len(tracts_gdf):,} tract centroids to network nodes")
    return tracts_gdf


# ── Core Scoring ───────────────────────────────────────────────────────────────

def compute_job_catchment(G, bridge_edges, tracts_gdf, tract_jobs,
                          catchment_m=config.ECONOMIC_CATCHMENT_M):
    """
    For each bridge, sum employment in Census tracts whose network
    centroid is within catchment_m metres of the bridge node.
    """
    print(f"Computing job catchment (radius={catchment_m:,}m) "
          f"for {len(bridge_edges):,} bridges...")

    G_simple = nx.DiGraph(G)

    # Build node -> jobs lookup
    node_to_jobs = {}
    for _, row in tracts_gdf.iterrows():
        node = row["network_node"]
        jobs = tract_jobs.get(row["tract_id"], 0)
        node_to_jobs[node] = node_to_jobs.get(node, 0) + jobs

    result = {}
    for i, (bridge_id, (u, v, key)) in enumerate(bridge_edges.items()):
        if (i + 1) % 500 == 0:
            print(f"  {i+1:,}/{len(bridge_edges):,}")

        try:
            lengths = nx.single_source_dijkstra_path_length(
                G_simple, u,
                cutoff=catchment_m,
                weight="length"
            )
            nearby_nodes = set(lengths.keys())
        except Exception:
            nearby_nodes = set()

        result[bridge_id] = sum(
            node_to_jobs.get(node, 0) for node in nearby_nodes
        )

    covered = sum(1 for v in result.values() if v > 0)
    print(f"  Bridges with jobs in catchment: {covered:,}/{len(result):,}")
    return result


def flag_freight_corridors(bridges_gdf, freight_gdf, buffer_m=100):
    """
    Flag bridges within buffer_m metres of an NHFN freight corridor.
    Returns dict {bridge_id: bool}.
    """
    print("Flagging freight corridor bridges...")

    bridges_proj = bridges_gdf.to_crs(epsg=3857)
    freight_proj = freight_gdf.to_crs(epsg=3857)

    freight_union = (
        freight_proj.geometry.union_all()
        if hasattr(freight_proj.geometry, "union_all")
        else freight_proj.geometry.unary_union
    )
    freight_buffer = freight_union.buffer(buffer_m)

    id_col = (
        "STRUCTURE_NUMBER_008"
        if "STRUCTURE_NUMBER_008" in bridges_proj.columns
        else bridges_proj.columns[0]
    )

    result = {}
    for _, row in bridges_proj.iterrows():
        result[str(row[id_col]).strip()] = bool(
            row.geometry.intersects(freight_buffer)
        )

    n_freight = sum(result.values())
    print(f"  Bridges on freight corridors: {n_freight:,}/{len(result):,}")
    return result


# ── Score Compiler ─────────────────────────────────────────────────────────────

def compile_economic_scores(job_catchment, freight_flags,
                            aadt_map=None):
    """
    Combine job catchment, AADT, and freight flag into normalised
    Economic Exposure Score.

    Score formula (with AADT):
        economic_score = (jobs_norm * 0.50)
                       + (aadt_norm * 0.20)
                       + (freight_bonus * 0.30)

    Score formula (without AADT):
        economic_score = (jobs_norm * 0.70)
                       + (freight_bonus * 0.30)

    Final score clipped to [0, 1].
    """
    records = []
    for bridge_id in job_catchment:
        bid = str(bridge_id).strip()
        records.append({
            "bridge_id":           bridge_id,
            "bridge_id_clean":     bid,
            "jobs_in_catchment":   job_catchment[bridge_id],
            "on_freight_corridor": freight_flags.get(bid, False),
            "aadt":                aadt_map.get(bid, 0)
                                   if aadt_map else 0,
        })

    df = pd.DataFrame(records)

    # Normalise jobs
    max_jobs = df["jobs_in_catchment"].max()
    df["jobs_norm"] = (
        df["jobs_in_catchment"] / max_jobs if max_jobs > 0 else 0.0
    )

    # Normalise AADT
    if aadt_map and df["aadt"].max() > 0:
        max_aadt = df["aadt"].max()
        df["aadt_norm"] = df["aadt"] / max_aadt
    else:
        df["aadt_norm"] = 0.0

    # Freight corridor bonus
    df["freight_bonus"] = (
        df["on_freight_corridor"].astype(float)
        * config.ECONOMIC_WEIGHTS["freight"]
    )

    # Composite score
    if aadt_map and df["aadt"].max() > 0:
        df["economic_score"] = (
            df["jobs_norm"]   * config.ECONOMIC_WEIGHTS["jobs"]
            + df["aadt_norm"] * config.ECONOMIC_WEIGHTS["aadt"]
            + df["freight_bonus"]
        ).clip(upper=1.0)
    else:
        df["economic_score"] = (
            df["jobs_norm"] * 0.70
            + df["freight_bonus"]
        ).clip(upper=1.0)

    # Drop helper column
    df = df.drop(columns=["bridge_id_clean"])

    print(f"\nEconomic scores compiled:")
    print(f"  Bridges scored:              {len(df):,}")
    print(f"  Max jobs in catchment:       "
          f"{df['jobs_in_catchment'].max():,.0f}")
    print(f"  Max AADT:                    {df['aadt'].max():,.0f}")
    print(f"  Bridges on freight corridor: "
          f"{df['on_freight_corridor'].sum():,}")
    print(f"  Mean economic score:         "
          f"{df['economic_score'].mean():.3f}")
    print(f"  Max economic score:          "
          f"{df['economic_score'].max():.3f}")

    print(f"\n  Top 5 by economic score:")
    print(df.nlargest(5, "economic_score")[
        ["bridge_id", "jobs_in_catchment", "aadt",
         "on_freight_corridor", "economic_score"]
    ].to_string(index=False))

    return df


# ── Main Entry Point ───────────────────────────────────────────────────────────

def run_economic_exposure(G, bridge_edges, bridges_gdf):
    """
    Full economic exposure pipeline.

    Args:
        G:            NetworkX MultiDiGraph (loaded OSM network)
        bridge_edges: dict {bridge_id: (u, v, key)}
        bridges_gdf:  GeoDataFrame of matched bridges

    Returns:
        DataFrame with economic_score per bridge
    """
    print("\n" + "="*60)
    print("ECONOMIC EXPOSURE ANALYSIS")
    print("="*60)

    # Load data
    lodes   = load_lodes_data()
    tracts  = load_tract_demographics()
    freight = load_freight_corridors()

    # Build AADT map from bridges GeoDataFrame
    id_col   = (
        "STRUCTURE_NUMBER_008"
        if "STRUCTURE_NUMBER_008" in bridges_gdf.columns
        else bridges_gdf.columns[0]
    )
    aadt_col = "ADT_029" if "ADT_029" in bridges_gdf.columns else None

    if aadt_col:
        bridges_gdf = bridges_gdf.copy()
        bridges_gdf[aadt_col] = pd.to_numeric(
            bridges_gdf[aadt_col], errors="coerce"
        ).fillna(0)
        aadt_map = {
            str(row[id_col]).strip(): row[aadt_col]
            for _, row in bridges_gdf.iterrows()
        }
        max_aadt    = max(aadt_map.values())
        sorted_aadt = sorted(aadt_map.values())
        median_aadt = sorted_aadt[len(sorted_aadt) // 2]
        print(f"AADT loaded: {len(aadt_map):,} bridges | "
              f"max={max_aadt:,.0f} | median={median_aadt:,.0f}")
    else:
        aadt_map = None
        print("AADT column (ADT_029) not found — skipping AADT component")

    # Build tract job lookup
    tract_jobs = build_tract_job_lookup(lodes)

    # Filter tracts to study counties
    tracts = tracts[
        tracts["tract_id"].str.startswith(config.STUDY_TRACT_PREFIXES)
    ].copy()
    print(f"Filtered to LA + Ventura tracts: {len(tracts):,}")

    # Snap tract centroids to network
    tracts = snap_tracts_to_network(tracts, G)

    # Score bridges
    job_catchment = compute_job_catchment(
        G, bridge_edges, tracts, tract_jobs
    )
    freight_flags = flag_freight_corridors(bridges_gdf, freight)

    # Compile with AADT
    scores = compile_economic_scores(
        job_catchment, freight_flags, aadt_map=aadt_map
    )

    # Save
    out_path = config.DATA_PROCESSED / "economic_scores.csv"
    scores.to_csv(out_path, index=False)
    print(f"\nSaved: {out_path}")

    return scores


if __name__ == "__main__":
    print("Run via run_pipeline.py or import into ncps_scorer.py")