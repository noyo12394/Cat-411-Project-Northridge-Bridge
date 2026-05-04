"""
Module 3: Network Criticality Metrics

Computes three metrics per bridge-carrying edge:
1. Edge betweenness centrality
2. Detour cost ratio
3. Connected component impact
"""
import time
import networkx as nx
import numpy as np
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import src.config as config


def compute_edge_betweenness(G, bridge_edges,
                             k=config.BETWEENNESS_SAMPLE_K):
    """
    Compute approximate edge betweenness centrality.
    Uses k-sample approximation for large graphs.

    Args:
        G:            NetworkX MultiDiGraph (OSMnx)
        bridge_edges: dict {bridge_id: (u, v, key)}
        k:            number of source nodes to sample

    Returns:
        dict {bridge_id: betweenness_score}
    """
    print(f"Computing edge betweenness centrality (k={k} sample)...")
    t0 = time.time()

    # Convert to simple DiGraph — betweenness does not support MultiDiGraph
    G_simple = nx.DiGraph(G)

    eb = nx.edge_betweenness_centrality(
        G_simple,
        k=min(k, G_simple.number_of_nodes()),
        weight="travel_time",
        normalized=True
    )

    result = {}
    for bridge_id, (u, v, key) in bridge_edges.items():
        result[bridge_id] = eb.get((u, v), 0.0)

    vals = list(result.values())
    print(f"  Computed for {len(result):,} bridges in {time.time()-t0:.1f}s")
    print(f"  Median: {np.median(vals):.6f} | Max: {np.max(vals):.6f}")
    return result


def compute_detour_cost(G, bridge_edges,
                        n_samples=config.DETOUR_OD_SAMPLE):
    """
    For each bridge edge, compute the detour cost ratio:
        ratio = travel_time_without_bridge / travel_time_with_bridge

    Uses bridge endpoints (u, v) as the OD proxy.
    Bridges with no feasible detour receive ratio = inf (network severance).

    Args:
        G:            NetworkX MultiDiGraph
        bridge_edges: dict {bridge_id: (u, v, key)}
        n_samples:    OD pairs to sample per bridge (reserved for future use)

    Returns:
        dict {bridge_id: detour_ratio}
    """
    print("Computing detour cost ratios...")
    t0 = time.time()

    G_simple = nx.DiGraph(G)
    result   = {}
    n        = len(bridge_edges)

    for i, (bridge_id, (u, v, key)) in enumerate(bridge_edges.items()):
        if (i + 1) % 500 == 0:
            elapsed  = time.time() - t0
            rate     = (i + 1) / elapsed
            remaining = (n - i - 1) / rate
            print(f"  {i+1:,}/{n:,} "
                  f"({elapsed:.0f}s elapsed, "
                  f"~{remaining:.0f}s remaining)")

        edge_data = G_simple.edges.get((u, v), {})
        if not edge_data:
            result[bridge_id] = 1.0
            continue

        try:
            baseline = nx.shortest_path_length(
                G_simple, u, v, weight="travel_time"
            )
        except nx.NetworkXNoPath:
            result[bridge_id] = 1.0
            continue

        # In-place remove and restore — avoids copying the graph
        G_simple.remove_edge(u, v)
        try:
            detour = nx.shortest_path_length(
                G_simple, u, v, weight="travel_time"
            )
            result[bridge_id] = detour / max(baseline, 0.001)
        except nx.NetworkXNoPath:
            result[bridge_id] = float("inf")
        G_simple.add_edge(u, v, **edge_data)

    elapsed   = time.time() - t0
    severed   = sum(1 for v in result.values() if v == float("inf"))
    finite    = [v for v in result.values() if v != float("inf")]

    print(f"\n  Done in {elapsed:.1f}s")
    print(f"  Severed bridges (no detour): {severed:,}")
    print(f"  Median detour ratio:         {np.median(finite):.2f}")
    print(f"  Max detour ratio (non-inf):  {np.max(finite):.2f}")
    return result


def compute_component_impact(G, bridge_edges, population_gdf=None):
    """
    For each bridge edge, check if removal disconnects the network.
    Uses nx.bridges() to pre-filter — only runs component analysis
    on edges that are actual graph bridges (cut edges).
    Uses in-place remove/restore — no copying the graph per bridge.

    Args:
        G:              NetworkX MultiDiGraph
        bridge_edges:   dict {bridge_id: (u, v, key)}
        population_gdf: optional GeoDataFrame (reserved for future use)

    Returns:
        dict {bridge_id: {
            "disconnects": bool,
            "isolated_nodes": int,
            "isolated_pop": int
        }}
    """
    print("Computing connected component impact...")
    t0 = time.time()

    # Simple undirected graph — faster to work with than MultiDiGraph
    G_undir = nx.Graph(G)

    # Pre-compute graph bridges in one O(V+E) pass
    # Only cut edges can disconnect the network — skip all others
    print("  Finding graph bridges (cut edges)...")
    graph_bridges = set(nx.bridges(G_undir))
    print(f"  Cut edges in full graph: {len(graph_bridges):,}")

    result    = {}
    n_checked = 0

    for bridge_id, (u, v, key) in bridge_edges.items():

        is_cut_edge = (
            (u, v) in graph_bridges or
            (v, u) in graph_bridges
        )

        if not is_cut_edge:
            result[bridge_id] = {
                "disconnects":    False,
                "isolated_nodes": 0,
                "isolated_pop":   0,
            }
            continue

        # Only expensive analysis for confirmed cut edges
        n_checked += 1

        # In-place remove → measure → restore
        G_undir.remove_edge(u, v)
        components = list(nx.connected_components(G_undir))
        G_undir.add_edge(u, v)

        if len(components) > 1:
            comp_sizes     = sorted(
                [len(c) for c in components], reverse=True
            )
            isolated_nodes = sum(comp_sizes[1:])
            result[bridge_id] = {
                "disconnects":    True,
                "isolated_nodes": isolated_nodes,
                "isolated_pop":   0,
            }
        else:
            result[bridge_id] = {
                "disconnects":    False,
                "isolated_nodes": 0,
                "isolated_pop":   0,
            }

    elapsed      = time.time() - t0
    n_disconnect = sum(1 for v in result.values() if v["disconnects"])

    print(f"  Cut edges checked:               {n_checked:,}")
    print(f"  Bridges disconnecting network:   "
          f"{n_disconnect:,}/{len(result):,}")
    print(f"  Done in {elapsed:.1f}s")
    return result


def compile_network_scores(betweenness, detour_cost, component_impact):
    """
    Combine the three network metrics into a single DataFrame
    with a normalised Network Criticality sub-score.

    Composite formula (equal weights across three sub-metrics):
        network_score = betweenness_norm * 0.33
                      + detour_ratio_norm * 0.34
                      + isolated_nodes_norm * 0.33

    Severed bridges (detour_ratio = inf) receive detour_ratio_norm = 1.0.

    Returns:
        DataFrame with bridge_id, raw metrics, normalised metrics,
        and network_score.
    """
    records = []
    for bridge_id in betweenness:
        bc = betweenness.get(bridge_id, 0)
        dc = detour_cost.get(bridge_id, 1.0)
        ci = component_impact.get(
            bridge_id,
            {"disconnects": False, "isolated_nodes": 0}
        )

        records.append({
            "bridge_id":          bridge_id,
            "betweenness":        bc,
            "detour_ratio":       dc if dc != float("inf") else 999.0,
            "detour_severed":     dc == float("inf"),
            "disconnects_network": ci["disconnects"],
            "isolated_nodes":     ci["isolated_nodes"],
        })

    df = pd.DataFrame(records)

    # Normalise each metric to [0, 1]
    for col in ["betweenness", "detour_ratio", "isolated_nodes"]:
        col_max = df[col].replace(999.0, np.nan).max()
        if col_max and col_max > 0:
            df[f"{col}_norm"] = df[col].clip(upper=col_max) / col_max
        else:
            df[f"{col}_norm"] = 0.0

    # Severed bridges get max detour score
    df.loc[df["detour_severed"], "detour_ratio_norm"] = 1.0

    # Composite network score
    df["network_score"] = (
        df["betweenness_norm"]   * 0.33
        + df["detour_ratio_norm"] * 0.34
        + df["isolated_nodes_norm"] * 0.33
    )

    print(f"\nNetwork scores compiled: {len(df):,} bridges")
    print(f"  Mean network score: {df['network_score'].mean():.3f}")
    print(f"  Max network score:  {df['network_score'].max():.3f}")
    print(f"\n  Top 5 by network score:")
    print(df.nlargest(5, "network_score")[
        ["bridge_id", "betweenness", "detour_ratio",
         "disconnects_network", "network_score"]
    ].to_string(index=False))

    return df


if __name__ == "__main__":
    print("Run via run_pipeline.py or import into ncps_scorer.py")