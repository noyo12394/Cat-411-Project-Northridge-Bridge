"""
NDVI Download Module
====================
Downloads pre-event and post-event NDVI composites from Google Earth Engine
for a given area of interest and disaster date. Automatically selects the
appropriate satellite (Landsat 5/7/8/9 or Sentinel-2) based on the event date.

Supports multiple AOI options:
    - Single county (e.g., "Los Angeles")
    - Entire state (e.g., "California")
    - Custom bounding box
    - Match ShakeMap raster extent

Outputs:
    - Pre_Event_NDVI.tif
    - Post_Event_NDVI.tif
    - NDVI_Change.tif
"""

import ee
import os


def _get_collection(event_year, aoi, start, end):
    """Select satellite collection based on event year and apply cloud masking."""

    if event_year >= 2019:
        # Sentinel-2
        col = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(aoi)
            .filterDate(start, end)
        )

        def mask_clouds(img):
            qa = img.select("SCL")
            mask = qa.neq(3).And(qa.neq(8)).And(qa.neq(9)).And(qa.neq(10))
            nir = img.select("B8").multiply(0.0001)
            red = img.select("B4").multiply(0.0001)
            return (
                nir.subtract(red).divide(nir.add(red)).rename("NDVI").updateMask(mask)
            )

        return col.map(mask_clouds)

    elif event_year >= 2013:
        # Landsat 8/9
        col = (
            ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
            .filterBounds(aoi)
            .filterDate(start, end)
        )

        def mask_clouds(img):
            qa = img.select("QA_PIXEL")
            mask = qa.bitwiseAnd(1 << 3).eq(0).And(qa.bitwiseAnd(1 << 4).eq(0))
            nir = img.select("SR_B5").multiply(0.0000275).add(-0.2)
            red = img.select("SR_B4").multiply(0.0000275).add(-0.2)
            return (
                nir.subtract(red).divide(nir.add(red)).rename("NDVI").updateMask(mask)
            )

        return col.map(mask_clouds)

    else:
        # Landsat 5 (pre-2013, including 1994 Northridge)
        col = (
            ee.ImageCollection("LANDSAT/LT05/C02/T1_L2")
            .filterBounds(aoi)
            .filterDate(start, end)
        )

        def mask_clouds(img):
            qa = img.select("QA_PIXEL")
            mask = qa.bitwiseAnd(1 << 3).eq(0).And(qa.bitwiseAnd(1 << 4).eq(0))
            nir = img.select("SR_B4").multiply(0.0000275).add(-0.2)
            red = img.select("SR_B3").multiply(0.0000275).add(-0.2)
            return (
                nir.subtract(red).divide(nir.add(red)).rename("NDVI").updateMask(mask)
            )

        return col.map(mask_clouds)


def get_ndvi_composites(aoi, disaster_date, window_days=60):
    """
    Compute pre-event and post-event NDVI median composites.

    Parameters
    ----------
    aoi : ee.Geometry
        Area of interest.
    disaster_date : str
        Event date in 'YYYY-MM-DD' format.
    window_days : int
        Number of days before/after event to composite.

    Returns
    -------
    pre_ndvi, post_ndvi, ndvi_change : ee.Image
    """
    event = ee.Date(disaster_date)
    event_year = int(disaster_date[:4])

    pre_start = event.advance(-window_days, "day")
    pre_end = event.advance(-2, "day")
    post_start = event.advance(2, "day")
    post_end = event.advance(window_days, "day")

    pre_col = _get_collection(event_year, aoi, pre_start, pre_end)
    post_col = _get_collection(event_year, aoi, post_start, post_end)

    pre_ndvi = pre_col.median().clip(aoi)
    post_ndvi = post_col.median().clip(aoi)
    ndvi_change = post_ndvi.subtract(pre_ndvi)

    return pre_ndvi, post_ndvi, ndvi_change


# ── AOI Helper Functions ─────────────────────────────────────────────────


def get_aoi_county(county_name="Los Angeles"):
    """
    Get AOI geometry for a single US county.

    Parameters
    ----------
    county_name : str
        County name (e.g., "Los Angeles", "Ventura").

    Returns
    -------
    aoi : ee.Geometry
    """
    counties = ee.FeatureCollection("TIGER/2018/Counties")
    county = counties.filter(ee.Filter.eq("NAME", county_name))
    return county.geometry()


def get_aoi_state(state_name="California"):
    """
    Get AOI geometry for an entire US state.

    Parameters
    ----------
    state_name : str
        State name (e.g., "California", "Nevada").

    Returns
    -------
    aoi : ee.Geometry
    """
    states = ee.FeatureCollection("TIGER/2018/States")
    state = states.filter(ee.Filter.eq("NAME", state_name))
    return state.geometry()


def get_aoi_multi_county(county_names):
    """
    Get AOI geometry for multiple counties merged together.

    Parameters
    ----------
    county_names : list of str
        List of county names (e.g., ["Los Angeles", "Ventura", "Orange"]).

    Returns
    -------
    aoi : ee.Geometry
    """
    counties = ee.FeatureCollection("TIGER/2018/Counties")
    filters = [ee.Filter.eq("NAME", name) for name in county_names]
    combined_filter = ee.Filter.Or(*filters)
    selected = counties.filter(combined_filter)
    return selected.geometry().dissolve()


def get_aoi_bbox(west, south, east, north):
    """
    Get AOI geometry from a bounding box.

    Parameters
    ----------
    west, south, east, north : float
        Bounding box coordinates in WGS84 (longitude/latitude).
        Example for Southern California: west=-121, south=33, east=-116, north=36

    Returns
    -------
    aoi : ee.Geometry
    """
    return ee.Geometry.Rectangle([west, south, east, north])


def get_aoi_from_raster(raster_path):
    """
    Get AOI geometry matching the extent of a local raster file (e.g., ShakeMap).
    This ensures your NDVI download covers the exact same area as your hazard data.

    NOTE: ee.Initialize() must be called BEFORE this function, since it
    creates an ee.Geometry object that requires an active EE session.

    Parameters
    ----------
    raster_path : str
        Path to a local raster file (e.g., pga_mean.flt).

    Returns
    -------
    aoi : ee.Geometry
    """
    import rasterio

    with rasterio.open(raster_path) as src:
        bounds = src.bounds  # (left, bottom, right, top)
        print(
            f"Raster extent: W={bounds.left:.3f}, S={bounds.bottom:.3f}, "
            f"E={bounds.right:.3f}, N={bounds.top:.3f}"
        )

    # Verify EE is initialized before creating geometry
    try:
        return ee.Geometry.Rectangle([bounds.left, bounds.bottom, bounds.right, bounds.top])
    except Exception:
        raise RuntimeError(
            "Earth Engine is not initialized. Call ee.Authenticate() and "
            "ee.Initialize(project='ee-mat724') BEFORE get_aoi_from_raster()."
        )


def download_ndvi_composites(
    aoi,
    disaster_date,
    output_dir,
    window_days=60,
    scale=30,
    ee_project="ee-mat724",
):
    """
    Authenticate with GEE, compute NDVI composites, and export as GeoTIFFs.

    Parameters
    ----------
    aoi : ee.Geometry or ee.FeatureCollection
        Area of interest.
    disaster_date : str
        Event date in 'YYYY-MM-DD' format.
    output_dir : str
        Directory to save output TIFFs.
    window_days : int
        Temporal window for compositing.
    scale : int
        Output resolution in meters.
    ee_project : str
        Google Earth Engine project ID.

    Returns
    -------
    dict : Paths to the three output TIFFs.

    Note
    ----
    You must call ee.Authenticate() and ee.Initialize() BEFORE calling
    this function. This avoids double-authentication and ensures the
    AOI helpers (get_aoi_from_raster, etc.) work correctly.
    """
    # Ensure EE is initialized (don't re-authenticate if already done)
    try:
        ee.data.getAsset("projects/earthengine-public/assets/COPERNICUS")
    except ee.ee_exception.EEException:
        ee.Initialize(project=ee_project)

    os.makedirs(output_dir, exist_ok=True)

    pre_ndvi, post_ndvi, ndvi_change = get_ndvi_composites(
        aoi, disaster_date, window_days
    )

    import geemap

    paths = {
        "pre_ndvi": os.path.join(output_dir, "Pre_Event_NDVI.tif"),
        "post_ndvi": os.path.join(output_dir, "Post_Event_NDVI.tif"),
        "ndvi_change": os.path.join(output_dir, "NDVI_Change.tif"),
    }

    geemap.ee_export_image(
        pre_ndvi,
        filename=paths["pre_ndvi"],
        scale=scale,
        region=aoi,
        file_per_band=False,
    )
    geemap.ee_export_image(
        post_ndvi,
        filename=paths["post_ndvi"],
        scale=scale,
        region=aoi,
        file_per_band=False,
    )
    geemap.ee_export_image(
        ndvi_change,
        filename=paths["ndvi_change"],
        scale=scale,
        region=aoi,
        file_per_band=False,
    )

    print(f"NDVI composites saved to: {output_dir}")
    return paths
