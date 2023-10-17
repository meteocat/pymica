"""Module with geographic tools.
"""
import math

import numpy as np
import numpy as np
import pyproj
from osgeo import gdal, osr
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


def save_array_as_geotiff(
    output_path: str, data: np.array, geotransform: list, epsg_code: int
) -> None:
    """Save a numpy array into a GeoTIFF file.

    Args:
        output_path (str): Path of the GeoTIFF file to be saved.
        data (np.array): Data to be saved as GeoTIFF.
        geotransform (list): Geotransform as [x_min, x_res, x_rot, y_max, y_rot, y_res]
        EPSG_code (int): ESPG coordinate system code.
    """    
    driver = gdal.GetDriverByName("GTiff")
    ds_out = driver.Create(
        output_path, data.shape[1], data.shape[0], 1, gdal.GDT_Float32
    )
    ds_out.GetRasterBand(1).WriteArray(data)
    ds_out.GetRasterBand(1).SetNoDataValue(0)
    ds_out.SetGeoTransform(geotransform)
    spatialRef = osr.SpatialReference()
    spatialRef.ImportFromEPSG(epsg_code)
    ds_out.SetProjection(str(spatialRef))

    ds_out = None
