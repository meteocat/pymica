"""Tool for creating clusters with the K-Means method.
"""
import json
from os.path import dirname

import numpy as np
from osgeo import gdal, ogr, osr
from scipy.ndimage import gaussian_filter
from sklearn.cluster import KMeans

from pymica.utils.geotools import get_utm_epsg_from_lonlat, reproject_point


def create_clusters(locations: list | str, n_clusters: int, geojson_file: str) -> None:
    """Group locations in a specified number of clusters using K-Means algorithm.

    Args:
        locations (list | str): List of dictionaries including location data or the
                                file path with data as json format. Data for each
                                location is a dictionary with 'id', 'alt', 'lon' and
                                'lat' as keys.
        n_clusters (int): Number of clusters to create.
        geojson_file (str): File path where clusters are saved.
    """
    if isinstance(locations, str):
        f_p = open(locations)
        locations = json.load(f_p)

    positions = np.zeros([len(locations), 2])
    utm_proj4 = get_utm_epsg_from_lonlat(locations[0]["lon"], locations[0]["lat"])

    positions_list = []
    for i, loc_value in enumerate(locations):
        positions[i][0] = loc_value["lon"]
        positions[i][1] = loc_value["lat"]

        utm_coordinates = reproject_point(
            (loc_value["lon"], loc_value["lat"]), "EPSG:4326", utm_proj4
        )
        positions_list.append(utm_coordinates)
    positions_list = np.array(positions_list)

    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(positions_list)

    out_geojson = {"type": "FeatureCollection", "features": []}
    for i, labels_value in enumerate(kmeans.labels_):
        locations[i]["cluster"] = labels_value
        out_geojson["features"].append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [locations[i]["lon"], locations[i]["lat"]],
                },
                "properties": {
                    "cluster": int(labels_value),
                    "id": locations[i]["id"],
                    "alt": locations[i]["alt"],
                },
            }
        )

    try:
        with open(geojson_file, "w") as f_p:
            json.dump(out_geojson, f_p)
    except FileNotFoundError:
        raise FileNotFoundError(dirname(geojson_file) + " directory does not exist.")


def create_reprojected_geometries(geojson_file: str, epsg: int) -> ogr.DataSource:
    """Reprojection of an ogr file to specified projection.
    Taken from: https://pcjericks.github.io/py-gdalogr-cookbook/projection.html

    Args:
        geojson_file (str): Path to a GeoJSON file with geometries.
        epsg (int): EPSG code of the new projection

    Raises:
        ValueError: If EPSG code is wrong.
        IOError: If `geojson_file` does not exist.

    Returns:
        ogr.DataSource: Reprojected geometries.
    """
    out_proj = osr.SpatialReference()
    out_proj.ImportFromEPSG(epsg)
    if len(out_proj.ExportToPrettyWkt()) <= 1:
        raise ValueError("Wrong EPSG code: {}".format(epsg))

    in_proj = osr.SpatialReference()
    in_proj.ImportFromEPSG(4326)

    transf = osr.CoordinateTransformation(in_proj, out_proj)

    in_ds = ogr.Open(geojson_file)
    if in_ds is None:
        raise IOError("File {} doesn't exist".format(geojson_file))
    in_layer = in_ds.GetLayer()

    mem_driver = ogr.GetDriverByName("MEMORY")
    proj_ds = mem_driver.CreateDataSource("memData")
    proj_layer = proj_ds.CreateLayer(
        "clusters", out_proj, geom_type=ogr.wkbMultiPolygon
    )

    in_layer_def = in_layer.GetLayerDefn()
    for i in range(0, in_layer_def.GetFieldCount()):
        field_def = in_layer_def.GetFieldDefn(i)
        proj_layer.CreateField(field_def)

    out_layer_def = proj_layer.GetLayerDefn()

    feature = in_layer.GetNextFeature()
    while feature:
        geom = feature.GetGeometryRef()
        geom.Transform(transf)
        proj_feat = ogr.Feature(out_layer_def)
        proj_feat.SetGeometry(geom)
        for i in range(0, out_layer_def.GetFieldCount()):
            proj_feat.SetField(
                out_layer_def.GetFieldDefn(i).GetNameRef(), feature.GetField(i)
            )
        proj_layer.CreateFeature(proj_feat)
        proj_feat = None
        feature = in_layer.GetNextFeature()

    return proj_ds


def rasterize_clusters(
    ds_in: ogr.DataSource, raster_config: dict, sigma: float = 15
) -> None:
    """Rasterize clusters from the GeoJSON file generated by

    Args:
        ds_in (ogr.DataSource): Input layer.
        raster_config (dict): The output raster characteristics. Must include
            'out_file' (path to save the rasterized clusters), 'size'
            (raster size (x, y)) and 'geotransform' ([ul_x, x_res, x_rot,
            ul_y, y_rot, y_res]) keys.
        sigma (float, optional): Sigma parameter for a Gaussian filter. Defaults to 15.

    Raises:
        ValueError: If `raster_config` does not have all required keys.
    """
    if raster_config.keys() < {"out_file", "size", "geotransform"}:
        raise KeyError(
            "`out_file`, `size`, `geotransform` must be in the `raster_config` "
            "parameter."
        )

    layer = ds_in.GetLayer()
    num_layers = layer.GetFeatureCount()
    proj = layer.GetSpatialRef()

    driver = gdal.GetDriverByName("GTIFF")
    ds_out = driver.Create(
        raster_config["out_file"],
        raster_config["size"][0],
        raster_config["size"][1],
        num_layers,
        gdal.GDT_Float32,
    )
    ds_out.SetGeoTransform(raster_config["geotransform"])
    ds_out.SetProjection(proj.ExportToWkt())

    for i in range(num_layers):
        layer.SetAttributeFilter("cluster={}".format(i))
        gdal.RasterizeLayer(ds_out, [i + 1], layer, burn_values=[1])

    data = ds_out.ReadAsArray().astype(np.float32)
    for i in range(num_layers):
        blurred = gaussian_filter(data[i], sigma)
        ds_out.GetRasterBand(i + 1).WriteArray(blurred)

    ds_out = None