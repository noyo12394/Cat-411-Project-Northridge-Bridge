"""
Module 5: Emergency Service Accessibility Impact — MCEER Validation

Computes the change in travel time from surrounding Census tract
populations to critical facilities (hospitals, fire stations, police
stations) with vs. without each bridge, restricted to the 37 MCEER
documented Northridge-damaged bridges for validation.

Key optimisations:
- Restricted to MCEER_ALL_37 bridges (~37 vs 4,050)
- Facilities filtered to LA/Ventura bounding box (local only)
- multi_source_dijkstra replaces per-facility inner loop
- Baseline computed once, reused for all 37 bridges

Data sources:
- Facilities: National.gdb / FireStation, PoliceStation (HAZUS CA)
- Hospitals:  Hospitals.shp (HIFLD, CA filter)
- Population: National.gdb / DemographicsByCensusTract + CensusTract
"""
import networkx as nx
import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import config


# ── Data Loaders ───────────────────────────────────────────────────────────────

def load_hospitals(filepath=config.HOSPITALS,
                   state=config.STUDY_STATE):
    """
    Load HIFLD hospital shapefile filtered to California.
    Returns GeoDataFrame with name, facility_type, geometry in EPSG:4326.
    """
    gdf = gpd.read_file(filepath)
    gdf = gdf[gdf["STATE"] == state].copy()
    gdf = gdf.to_crs(epsg=4326)
    gdf["facility_type"] = "hospital"
    gdf = gdf.rename(columns={"NAME": "name"})
    gdf = gdf[["name", "facility_type", "geometry"]].copy()
    print(f"Loaded {len(gdf):,} California hospitals")
    return gdf


def load_fire_stations(gdb_path=config.HAZUS_GDB,
                       state=config.STUDY_STATE):
    """
    Load fire stations from HAZUS National GDB filtered to California.
    Returns GeoDataFrame in EPSG:4326.
    """
    gdf = gpd.read_file(gdb_path, layer="FireStation")
    gdf = gdf[gdf["State"] == state].copy()
    gdf = gdf.to_crs(epsg=4326)
    gdf["facility_type"] = "fire_station"
    gdf = gdf.rename(columns={"Name": "name"})
    gdf = gdf[["name", "facility_type", "geometry"]].copy()
    print(f"Loaded {len(gdf):,} California fire stations")
    return gdf


def load_police_stations(gdb_path=config.HAZUS_GDB,
                         state=config.STUDY_STATE):
    """
    Load police stations from HAZUS National GDB filtered to California.
    Returns GeoDataFrame in EPSG:4326.
    """
    gdf = gpd.read_file(gdb_path, layer="PoliceStation")
    gdf = gdf[gdf["State"] == state].copy()
    gdf = gdf.to_crs(epsg=4326)
    gdf["facility_type"] = "police_station"
    gdf = gdf.rename(columns={"Name": "name"})
    gdf = gdf[["name", "facility_type", "geometry"]].copy()
    print(f"Loaded {len(gdf):,} California police stations")
    return gdf


def load_tract_population(gdb_path=config.HAZUS_GDB,
                          state=config.STUDY_STATE):
    """
    Load Census tract geometry and population from HAZUS National GDB.
    Joins CensusTract geometry with DemographicsByCensusTract.
    Filters to LA + Ventura counties.
    Returns GeoDataFrame with tract_id, Population, geometry.
    """
    print(f"Loading tract population for {state}...")

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

    # Filter to study counties
    tracts = tracts[
        tracts["tract_id"].str.startswith(config.STUDY_TRACT_PREFIXES)
    ].copy()

    # Ensure EPSG:4326
    if tracts.crs is None:
        tracts = tracts.set_crs(epsg=4326)
    else:
        tracts = tracts.to_crs(epsg=4326)

    print(f"  LA + Ventura tracts: {len(tracts):,}, "
          f"population: {tracts['Population'].sum():,.0f}")
    return tracts


# ── Core Analysis ──────────────────────────────────────────────────────────────

def compute_access_impact_validation(G, bridges_gdf, facilities_gdf,
                                     tracts_gdf, facility_type,
                                     bridge_ids=None,
                                     threshold_min=None):
    """
    Optimised emergency access impact for MCEER 37 bridges only.

    For each bridge in bridge_ids, computes population-weighted travel
    time increase to nearest facility when that bridge is removed.

    Uses multi_source_dijkstra — one graph pass from all facility nodes
    simultaneously — instead of looping over facilities per tract.
    Baseline is computed once and reused for all 37 bridges.

    Args:
        G:              NetworkX MultiDiGraph (OSM network)
        bridges_gdf:    GeoDataFrame of matched NBI bridges
        facilities_gdf: Combined GeoDataFrame with facility_type column
        tracts_gdf:     GeoDataFrame with tract_id, Population, geometry
        facility_type:  "hospital", "fire_station", or "police_station"
        bridge_ids:     list of structure numbers to analyse
                        (defaults to config.MCEER_ALL_37)
        threshold_min:  minutes increase that triggers population count

    Returns:
        dict {bridge_id: {
            pop_affected, max_delta_min, mean_delta_min,
            damage_state, pga
        }}
    """
    import osmnx as ox

    if bridge_ids is None:
        bridge_ids = config.MCEER_ALL_37

    if threshold_min is None:
        threshold_map = {
            "hospital":       config.HOSPITAL_THRESHOLD_MIN,
            "fire_station":   config.FIRE_STATION_THRESHOLD_MIN,
            "police_station": config.FIRE_STATION_THRESHOLD_MIN,
        }
        threshold_min = threshold_map.get(
            facility_type, config.HOSPITAL_THRESHOLD_MIN
        )

    print(f"\n{'='*55}")
    print(f"Emergency access — {facility_type.upper()}")
    print(f"Bridges: {len(bridge_ids)} MCEER | "
          f"Threshold: {threshold_min} min")
    print(f"{'='*55}")

    G_simple = nx.DiGraph(G)

    # ── 1. Filter bridges to MCEER set ──────────────────────────────
    id_col = (
        "STRUCTURE_NUMBER_008"
        if "STRUCTURE_NUMBER_008" in bridges_gdf.columns
        else bridges_gdf.columns[0]
    )

    # Strip whitespace from structure numbers for matching
    bridges_gdf = bridges_gdf.copy()
    bridges_gdf[id_col] = bridges_gdf[id_col].astype(str).str.strip()
    bridge_ids_stripped = [b.strip() for b in bridge_ids]

    mceer_bridges = bridges_gdf[
        bridges_gdf[id_col].isin(bridge_ids_stripped)
    ].copy()

    found = len(mceer_bridges)
    print(f"  MCEER bridges found in matched set: "
          f"{found}/{len(bridge_ids)}")

    if found == 0:
        print("  WARNING: No MCEER bridges matched.")
        print("  Sample bridge IDs in GDF:",
              bridges_gdf[id_col].head(5).tolist())
        print("  Sample MCEER IDs:", bridge_ids_stripped[:5])
        return {}

    # Build edge map for MCEER bridges
    mceer_edge_map = {}
    for _, row in mceer_bridges.iterrows():
        bid = row[id_col]
        mceer_edge_map[bid] = (
            row["nearest_u"],
            row["nearest_v"],
            row["nearest_key"],
        )

    # ── 2. Filter facilities to bounding box ────────────────────────
    fac = facilities_gdf[
        facilities_gdf["facility_type"] == facility_type
    ].copy()

    fac = fac.to_crs(epsg=4326)
    b   = config.FACILITY_BOUNDS
    fac = fac.cx[
        b["min_lon"]:b["max_lon"],
        b["min_lat"]:b["max_lat"]
    ].copy()

    if len(fac) == 0:
        print(f"  No {facility_type} facilities in bounding box — "
              f"skipping")
        return {}

    print(f"  Local {facility_type} facilities: {len(fac):,}")

    # Snap facilities to network
    fac_network_nodes = ox.nearest_nodes(
        G,
        X=fac.geometry.x.values,
        Y=fac.geometry.y.values
    )
    facility_node_set = set(fac_network_nodes)

    # ── 3. Filter tracts to bounding box ────────────────────────────
    tracts = tracts_gdf.to_crs(epsg=4326).copy()
    tracts = tracts.cx[
        b["min_lon"]:b["max_lon"],
        b["min_lat"]:b["max_lat"]
    ].copy()

    tract_centroids = tracts.geometry.centroid
    tract_nodes = ox.nearest_nodes(
        G,
        X=tract_centroids.x.values,
        Y=tract_centroids.y.values
    )
    tract_pops = tracts["Population"].values

    print(f"  Local tracts: {len(tracts):,}")

    # ── 4. Baseline — multi_source_dijkstra (computed once) ─────────
    print("  Computing baseline travel times "
          "(multi-source Dijkstra)...")
    baseline_map = dict(
        nx.multi_source_dijkstra_path_length(
            G_simple,
            sources=facility_node_set,
            weight="travel_time"
        )
    )

    # Pre-fetch baseline time for each tract node
    tract_baselines = np.array([
        baseline_map.get(t, np.inf) for t in tract_nodes
    ])

    reachable = int(np.sum(tract_baselines < np.inf))
    print(f"  Tracts reachable from a facility: "
          f"{reachable:,}/{len(tract_nodes):,}")

    # ── 5. Per-bridge impact ─────────────────────────────────────────
    threshold_sec = threshold_min * 60
    result        = {}

    for bridge_id, (u, v, key) in mceer_edge_map.items():

        edge_data = G_simple.edges.get((u, v), None)
        if edge_data is None:
            result[bridge_id] = {
                "pop_affected":   0,
                "max_delta_min":  0.0,
                "mean_delta_min": 0.0,
                "damage_state":   _damage_state(bridge_id),
                "pga":            config.MCEER_PGA.get(bridge_id, 0.0),
            }
            continue

        # Remove bridge edge
        G_simple.remove_edge(u, v)

        # Recompute multi-source from all facilities
        new_map = dict(
            nx.multi_source_dijkstra_path_length(
                G_simple,
                sources=facility_node_set,
                weight="travel_time"
            )
        )

        new_times = np.array([
            new_map.get(t, np.inf) for t in tract_nodes
        ])

        # Compute deltas — only for reachable tracts
        reachable_mask = tract_baselines < np.inf
        deltas = (
            new_times[reachable_mask]
            - tract_baselines[reachable_mask]
        )

        # Population affected = tracts where delta exceeds threshold
        affected_mask = deltas > threshold_sec
        pop_affected  = int(
            tract_pops[reachable_mask][affected_mask].sum()
        )

        positive_deltas = deltas[deltas > 0]
        max_delta_min   = (
            float(positive_deltas.max()) / 60
            if len(positive_deltas) > 0 else 0.0
        )
        mean_delta_min  = (
            float(positive_deltas.mean()) / 60
            if len(positive_deltas) > 0 else 0.0
        )

        # Restore bridge edge
        G_simple.add_edge(u, v, **edge_data)

        result[bridge_id] = {
            "pop_affected":   pop_affected,
            "max_delta_min":  round(max_delta_min,  2),
            "mean_delta_min": round(mean_delta_min, 2),
            "damage_state":   _damage_state(bridge_id),
            "pga":            config.MCEER_PGA.get(bridge_id, 0.0),
        }

    n_impactful = sum(
        1 for v in result.values() if v["pop_affected"] > 0
    )
    print(f"\n  Results:")
    print(f"    Bridges analysed:           {len(result)}")
    print(f"    Bridges with pop affected:  {n_impactful}")
    if result:
        print(f"    Max pop affected (single):  "
              f"{max(v['pop_affected'] for v in result.values()):,}")

    return result


# ── Helper ─────────────────────────────────────────────────────────────────────

def _damage_state(bridge_id):
    """Return MCEER damage state label for a bridge ID."""
    bid = bridge_id.strip()
    if bid in [b.strip() for b in config.MCEER_COLLAPSED]:
        return "Collapse"
    elif bid in [b.strip() for b in config.MCEER_MAJOR_DAMAGE]:
        return "Major"
    elif bid in [b.strip() for b in config.MCEER_MODERATE_DAMAGE]:
        return "Moderate"
    return "Unknown"


# ── Score Compiler ─────────────────────────────────────────────────────────────

def compile_emergency_scores(hospital_impact, fire_impact,
                             police_impact):
    """
    Combine facility-type impacts into a normalised Emergency Access Score.

    Weights:
        hospital:       50%
        fire_station:   30%
        police_station: 20%

    Returns DataFrame sorted by damage state severity then score.
    """
    all_bridges = (
        set(hospital_impact.keys())
        | set(fire_impact.keys())
        | set(police_impact.keys())
    )

    empty = {
        "pop_affected":   0,
        "max_delta_min":  0.0,
        "mean_delta_min": 0.0,
        "damage_state":   "Unknown",
        "pga":            0.0,
    }

    records = []
    for bridge_id in all_bridges:
        h = hospital_impact.get(bridge_id, empty)
        f = fire_impact.get(bridge_id, empty)
        p = police_impact.get(bridge_id, empty)

        records.append({
            "bridge_id":               bridge_id,
            "damage_state":            h.get("damage_state",
                                             _damage_state(bridge_id)),
            "pga":                     h.get("pga",
                                             config.MCEER_PGA.get(
                                                 bridge_id, 0.0)),
            "hospital_pop_affected":   h["pop_affected"],
            "hospital_max_delta_min":  h["max_delta_min"],
            "fire_pop_affected":       f["pop_affected"],
            "fire_max_delta_min":      f["max_delta_min"],
            "police_pop_affected":     p["pop_affected"],
            "police_max_delta_min":    p["max_delta_min"],
            "total_pop_affected": (
                h["pop_affected"]
                + f["pop_affected"]
                + p["pop_affected"]
            ),
        })

    df = pd.DataFrame(records)

    # Normalise each facility type independently
    for col, norm_col in [
        ("hospital_pop_affected",  "hospital_norm"),
        ("fire_pop_affected",      "fire_norm"),
        ("police_pop_affected",    "police_norm"),
    ]:
        max_val = df[col].max()
        df[norm_col] = df[col] / max_val if max_val > 0 else 0.0

    # Weighted composite emergency score
    df["emergency_score"] = (
        df["hospital_norm"] * 0.50
        + df["fire_norm"]   * 0.30
        + df["police_norm"] * 0.20
    ).clip(upper=1.0)

    # Sort by damage state severity then score
    state_order = {"Collapse": 0, "Major": 1, "Moderate": 2, "Unknown": 3}
    df["_sort"] = df["damage_state"].map(state_order)
    df = df.sort_values(
        ["_sort", "emergency_score"],
        ascending=[True, False]
    ).drop(columns="_sort")

    print(f"\nEmergency scores compiled:")
    print(f"  Bridges scored:          {len(df)}")
    print(f"  Collapsed:               "
          f"{(df['damage_state'] == 'Collapse').sum()}")
    print(f"  Major damage:            "
          f"{(df['damage_state'] == 'Major').sum()}")
    print(f"  Moderate damage:         "
          f"{(df['damage_state'] == 'Moderate').sum()}")

    collapse_scores = df[
        df["damage_state"] == "Collapse"
    ]["emergency_score"]
    major_scores = df[
        df["damage_state"] == "Major"
    ]["emergency_score"]
    moderate_scores = df[
        df["damage_state"] == "Moderate"
    ]["emergency_score"]

    if len(collapse_scores):
        print(f"\n  Mean emergency score — Collapse:  "
              f"{collapse_scores.mean():.3f}")
    if len(major_scores):
        print(f"  Mean emergency score — Major:     "
              f"{major_scores.mean():.3f}")
    if len(moderate_scores):
        print(f"  Mean emergency score — Moderate:  "
              f"{moderate_scores.mean():.3f}")

    return df


# ── Main Entry Point ───────────────────────────────────────────────────────────

def run_emergency_access(G, bridge_edges, bridges_gdf):
    """
    Full emergency access validation pipeline.
    Runs on MCEER_ALL_37 bridges only.

    Args:
        G:            NetworkX MultiDiGraph (loaded OSM network)
        bridge_edges: dict {bridge_id: (u, v, key)}
        bridges_gdf:  GeoDataFrame of all matched NBI bridges

    Returns:
        DataFrame with emergency_score per MCEER bridge
    """
    print("\n" + "="*60)
    print("EMERGENCY ACCESS ANALYSIS — NORTHRIDGE VALIDATION")
    print(f"Analysing {len(config.MCEER_ALL_37)} MCEER documented bridges")
    print("="*60)

    # Load all facilities
    print("\nLoading facilities...")
    hospitals = load_hospitals()
    fire      = load_fire_stations()
    police    = load_police_stations()

    # Standardise all to EPSG:4326 before concat
    hospitals = hospitals.to_crs(epsg=4326)
    fire      = fire.to_crs(epsg=4326)
    police    = police.to_crs(epsg=4326)

    all_facilities = pd.concat(
        [hospitals, fire, police], ignore_index=True
    )
    all_facilities = gpd.GeoDataFrame(
        all_facilities, geometry="geometry", crs="EPSG:4326"
    )
    print(f"Total facilities loaded: {len(all_facilities):,}")

    # Load tract population
    tracts = load_tract_population()

    # Run per-facility-type impact on 37 bridges
    hospital_impact = compute_access_impact_validation(
        G, bridges_gdf, all_facilities, tracts,
        facility_type="hospital"
    )
    fire_impact = compute_access_impact_validation(
        G, bridges_gdf, all_facilities, tracts,
        facility_type="fire_station"
    )
    police_impact = compute_access_impact_validation(
        G, bridges_gdf, all_facilities, tracts,
        facility_type="police_station"
    )

    # Compile and save
    scores = compile_emergency_scores(
        hospital_impact, fire_impact, police_impact
    )

    out_path = config.DATA_PROCESSED / "emergency_scores_validation.csv"
    scores.to_csv(out_path, index=False)
    print(f"\nSaved: {out_path}")

    # Validation summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    print("\nMCEER bridges ranked by emergency score:")
    display_cols = [
        "bridge_id", "damage_state", "pga", "emergency_score",
        "hospital_pop_affected", "fire_pop_affected"
    ]
    available = [c for c in display_cols if c in scores.columns]
    print(scores[available].to_string(index=False))

    return scores


if __name__ == "__main__":
    print("Run via run_pipeline.py or import into ncps_scorer.py")