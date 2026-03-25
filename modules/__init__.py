"""
Modules for satellite-based NDVI analysis and change detection.
- ndvi_download: Download NDVI composites from Google Earth Engine
- change_detection: Compute NDVI change and extract per-bridge statistics
- visualization: Plot rasters, scatter plots, and spatial maps
"""

from .ndvi_download import (
    download_ndvi_composites,
    get_aoi_county,
    get_aoi_state,
    get_aoi_multi_county,
    get_aoi_bbox,
    get_aoi_from_raster,
)
from .change_detection import compute_ndvi_change, extract_bridge_ndvi
from .visualization import (
    plot_ndvi_rasters,
    plot_ndvi_change_only,
    plot_pga_vs_ndvi,
    plot_bridge_ndvi_map,
)
