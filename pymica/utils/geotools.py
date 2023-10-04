"""Module with geographic tools.
"""
import math

import numpy as np
import pyproj
from osgeo import gdal, osr


def get_utm_epsg_from_lonlat(longitude: float, latitude: float) -> str:
    """Get UTM EPSG from longitude and latitude coordinates.

    Args:
        longitude (float): Longitude of a location.
        latitude (float): Latitude of a location.

    Returns:
        str: UTM EPSG coordinates reference system.
    """
    zone = (math.floor((longitude + 180) / 6) % 60) + 1
    south = " +south " if latitude < 0 else " "
    desc = ("+proj=utm +zone={}{}+ellps=WGS84 +datum=WGS84 +units=m +no_defs").format(
        zone, south
    )

    utm_epsg = pyproj.CRS.from_proj4(desc).to_epsg()

    return utm_epsg


def reproject_point(point: tuple, in_proj: int | str, out_proj: int | str) -> tuple:
    """Reproject a location from `in_proj` to `out_proj`.

    Args:
        point (tuple): Coordinates of a location.
        in_proj (int | str): Input projection as EPSG code or proj4.
        out_proj (int | str): Output projection as EPSG code or proj4.

    Returns:
        tuple: Reprojected point coordinates.
    """
    reproject = pyproj.Transformer.from_crs(in_proj, out_proj, always_xy=True)

    point_x, point_y = reproject.transform(point[0], point[1])

    return (point_x, point_y)


def get_tif_from_array(
    file_path: str, data: np.array, geotransform: np.array, projection: int
) -> None:
    """Save an array into a raster TIF file.

    Args:
        file_path (str): Output file path.
        data (np.array): Array to be saved as a raster file.
        geotransform (np.array): GDAL Geotransform.
        projection (int): EPSG projection.
    """
    driver = gdal.GetDriverByName("GTiff")
    ds_out = driver.Create(file_path, data.shape[1], data.shape[0], 1, gdal.GDT_Float32)
    ds_out.GetRasterBand(1).WriteArray(data)
    ds_out.GetRasterBand(1).SetNoDataValue(0)
    ds_out.SetGeoTransform(geotransform)
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromEPSG(projection)
    ds_out.SetProjection(str(spatialRef))

    ds_out = None
