"""
Module 1: Road Network Construction

Pulls the OSM driving network for the study area, simplifies it,
and saves as a GeoPackage + NetworkX pickle for downstream use.
"""
import osmnx as ox
import networkx as nx
import geopandas as gpd
import pickle
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
import src.config as config


def fetch_network(place=config.STUDY_AREA, network_type=config.NETWORK_TYPE):
    """
    Download OSM driving network for the study area.
    Returns a MultiDiGraph with speed/travel_time on edges.
    """
    print(f"Fetching OSM network for: {place}")
    G = ox.graph_from_place(place, network_type=network_type, simplify=True)

    # Add travel time (seconds) based on edge length and speed
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)

    print(f"  Nodes: {G.number_of_nodes():,}")
    print(f"  Edges: {G.number_of_edges():,}")
    return G


def save_network(G, name="la_county"):
    """Save network as GeoPackage (for GIS) and pickle (for NetworkX)."""
    out_dir = config.DATA_PROCESSED
    out_dir.mkdir(parents=True, exist_ok=True)

    # GeoPackage for GIS visualization
    gpkg_path = out_dir / f"{name}_network.gpkg"
    ox.save_graph_geopackage(G, filepath=gpkg_path)
    print(f"  Saved GeoPackage: {gpkg_path}")

    # Pickle for fast reload in Python
    pkl_path = out_dir / f"{name}_graph.pkl"
    with open(pkl_path, "wb") as f:
        pickle.dump(G, f)
    print(f"  Saved pickle: {pkl_path}")

    return gpkg_path, pkl_path


def load_network(name="la_county"):
    """Load previously saved network from pickle."""
    pkl_path = config.DATA_PROCESSED / f"{name}_graph.pkl"
    with open(pkl_path, "rb") as f:
        G = pickle.load(f)
    print(f"Loaded network: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")
    return G


if __name__ == "__main__":
    G = fetch_network()
    save_network(G)
    print("Done.")
