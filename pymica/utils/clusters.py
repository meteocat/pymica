"""Tool for creating clusters with the K-Means method.
"""
import json
from glob import glob
from os import remove
from os.path import dirname

import numpy as np
import pyproj
import shapefile
from osgeo import gdal, ogr, osr
from scipy.ndimage import gaussian_filter
from scipy.spatial import Voronoi
from shapely.geometry import MultiPolygon, shape
from sklearn.cluster import KMeans

from pymica.utils.geotools import reproject_point


def create_clusters(
    locations: list | str,
    n_clusters: int,
    shp_file: str,
    bounding_box: list,
    epsg_code: int,
) -> None:
    """Group locations into a specified number of clusters and save them as an ESRI
    Shapefile.

    The Shapefile will have the extent of the specified `bounding_box`, and it's
    crucial that the coordinates of the bounding box are in the same projection as the
    locations.

    Args:
        locations (list or str): List of dictionaries containing location data or the
            file path with data in JSON format. Each dictionary should include keys
            'id', 'alt', 'lon', and 'lat' for each location.
        n_clusters (int): The number of clusters to group the locations into.
        shp_file (str): The path to the output ESRI Shapefile.
        bounding_box (list): A list representing the extent of the Shapefile in the
            format [min_x, min_y, max_x, max_y]. The coordinates in this bounding box
            must be in the same projection as the locations.
        epsg_code (int): The EPSG code specifying the coordinate system for the
            provided locations.

    Returns:
        None
    """
    if isinstance(locations, str):
        f_p = open(locations)
        locations = json.load(f_p)

    x_coords, y_coords = [], []
    positions_list = []
    for loc_value in locations:
        x_coord, y_coord = reproject_point(
            (loc_value["lon"], loc_value["lat"]), 4326, epsg_code
        )
        x_coords.append(x_coord)
        y_coords.append(y_coord)

        positions_list.append((x_coord, y_coord))

    positions_list = np.array(positions_list)

    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(positions_list)
    cluster_labels = kmeans.fit_predict(positions_list)

    positions_list = np.append(
        positions_list,
        np.array(
            [
                [0.9 * min(x_coords), 0.9 * min(y_coords)],
                [0.9 * min(x_coords), 1.1 * max(y_coords)],
                [1.1 * max(x_coords), 0.9 * min(y_coords)],
                [1.1 * max(x_coords), 1.1 * max(y_coords)],
            ]
        ),
        axis=0,
    )

    # Calculate Voronoi diagram
    vor = Voronoi(positions_list)

    # Create a dictionary to store Voronoi cells for each cluster
    cluster_cells = {cluster_id: [] for cluster_id in range(n_clusters)}

    # Assign Voronoi cells to clusters
    for station_id, region_id in enumerate(vor.point_region):
        if region_id >= 0:
            try:
                cluster_id = cluster_labels[station_id]
            except Exception:
                cluster_id = 0
            vertices = vor.regions[region_id]

            # Filter out invalid vertices (negative indices)
            vertices = [v for v in vertices if v >= 0]

            if vertices:
                polygon = [vor.vertices[v] for v in vertices]

                # Ensure the polygon is closed by adding the first point to the end
                if np.array_equal(polygon[0], polygon[-1]):
                    polygon.append(polygon[0])

                cluster_cells[cluster_id].append(polygon)

    # Create a shapefile
    auxiliary_shapefile = dirname(shp_file) + "/auxiliary_voronoi.shp"
    sf = shapefile.Writer(auxiliary_shapefile, shapeType=shapefile.POLYGON)

    # Define the fields in the shapefile
    sf.field("ClusterID", "N")

    # Add polygons to the shapefile
    for cluster_id, polygons in cluster_cells.items():
        for polygon in polygons:
            sf.poly([[(x, y) for x, y in polygon]])
            sf.record(cluster_id)

    # Save the shapefile
    sf.close()

    with open(auxiliary_shapefile.replace(".shp", ".prj"), "w") as prj_file:
        prj_file.write(pyproj.CRS.from_epsg(epsg_code).to_wkt(version="WKT1_ESRI"))

    # Re-open the shapefile to merge same cluster ID polygons
    sf = shapefile.Reader(auxiliary_shapefile)

    # Extract the shapes and records (attributes)
    shapes = sf.shapes()
    records = sf.records()

    # Create a dictionary to store merged polygons
    merged_polygons = {}

    # Iterate through the shapes and records
    for shp, record in zip(shapes, records):
        attribute_value = record[sf.fields[1].index("ClusterID")]

        # Convert the shape to a Shapely Polygon
        polygon = shape(shp)

        if attribute_value not in merged_polygons:
            merged_polygons[attribute_value] = polygon
        else:
            merged_polygons[attribute_value] = merged_polygons[attribute_value].union(
                polygon
            )

    auxiliary_merged_shapefile = dirname(shp_file) + "/auxiliary_merged.shp"
    sf_merged = shapefile.Writer(
        auxiliary_merged_shapefile, shapeType=shapefile.POLYGON
    )

    # Copy the fields from the original shapefile to the merged shapefile
    for field in sf.fields[1:]:
        sf_merged.field(*field)

    # Add merged polygons and their attributes to the merged shapefile
    for attribute_value, merged_polygon in merged_polygons.items():
        if isinstance(merged_polygon, MultiPolygon):
            for (
                geom
            ) in merged_polygon.geoms:  # Iterate through the geometries in MultiPolygon
                sf_merged.poly([list(geom.exterior.coords)])
                sf_merged.record(attribute_value)
        else:
            sf_merged.poly([list(merged_polygon.exterior.coords)])
            sf_merged.record(attribute_value)

    with open(auxiliary_merged_shapefile.replace(".shp", ".prj"), "w") as prj_file:
        prj_file.write(pyproj.CRS.from_epsg(epsg_code).to_wkt(version="WKT1_ESRI"))

    # Save the merged shapefile
    sf_merged.close()

    clip_clusters_extent(auxiliary_merged_shapefile, shp_file, bounding_box, epsg_code)

    with open(shp_file.replace(".shp", ".prj"), "w") as prj_file:
        prj_file.write(pyproj.CRS.from_epsg(epsg_code).to_wkt(version="WKT1_ESRI"))

    # Remove auxiliary files
    for cluster_file in glob(auxiliary_merged_shapefile[:-3] + "*"):
        remove(cluster_file)

    for cluster_file in glob(auxiliary_shapefile[:-3] + "*"):
        remove(cluster_file)


def clip_clusters_extent(
    input_shapefile_path: str,
    output_shapefile_path: str,
    bounding_box: list,
    epsg_code: int,
) -> None:
    """Clip a shapefile to a defined extent. Bounding box coordinates must be in the
    same projection as the input shapefile. The clipped shapfile will have the same
    input projection but with a smaller extent.

    Args:
        input_shapefile_path (str): Path to a shapefile to clip.
        output_shapefile_path (str): Path where clipped shapefile is saved.
        bounding_box (list): Coordinates extent following (xmin, ymin, xmax, ymax).
        epsg_code (int): EPSG code.
    """
    # Specify the extent as a bounding box (xmin, ymin, xmax, ymax)
    xmin, ymin, xmax, ymax = bounding_box

    # Open the input Shapefile
    input_ds = ogr.Open(input_shapefile_path)

    # Get the layer from the dataset
    layer = input_ds.GetLayer()

    # Create a geometry representing the clipping extent
    clip_extent_geometry = ogr.Geometry(ogr.wkbPolygon)
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(xmin, ymin)
    ring.AddPoint(xmin, ymax)
    ring.AddPoint(xmax, ymax)
    ring.AddPoint(xmax, ymin)
    ring.AddPoint(xmin, ymin)
    clip_extent_geometry.AddGeometry(ring)

    # Set the spatial reference for the clipping extent
    clip_extent_srs = osr.SpatialReference()
    clip_extent_srs.ImportFromEPSG(epsg_code)
    clip_extent_geometry.AssignSpatialReference(clip_extent_srs)

    # Create an output Shapefile with the same structure as the input
    output_driver = ogr.GetDriverByName("ESRI Shapefile")
    output_ds = output_driver.CreateDataSource(output_shapefile_path)

    # Create a layer in the output dataset
    output_layer = output_ds.CreateLayer("clipped", geom_type=ogr.wkbMultiPolygon)

    # Create a feature definition based on the original layer
    output_layer.CreateFields(layer.schema)

    # Perform the clipping operation
    layer.SetSpatialFilter(clip_extent_geometry)
    for feature in layer:
        clipped_geometry = feature.GetGeometryRef().Intersection(clip_extent_geometry)
        if clipped_geometry:
            new_feature = ogr.Feature(output_layer.GetLayerDefn())
            new_feature.SetGeometry(clipped_geometry)
            for field_index in range(feature.GetFieldCount()):
                field_name = feature.GetFieldDefnRef(field_index).GetName()
                field_value = feature.GetField(field_name)
                new_feature.SetField(field_name, field_value)
            output_layer.CreateFeature(new_feature)
            new_feature = None

    # Clean up and close datasets
    input_ds = None
    output_ds = None


def rasterize_clusters(
    shapefile_path: str, raster_config: dict, sigma: float = 15
) -> None:
    """Rasterize clusters from a GeoJSON file and save the result as a raster image.

    Args:
        shapefile_path (str): The path to the GeoJSON file containing cluster
            information.
        raster_config (dict): A dictionary with the following required keys:
            - 'out_file' (str): Path to save the rasterized clusters.
            - 'size' (tuple): Raster size (x, y) in pixels.
            - 'geotransform' (list): GeoTransform information [ul_x, x_res, x_rot, ul_y, y_rot, y_res].
        sigma (float, optional): Sigma parameter for a Gaussian filter. Defaults to 15.

    Returns:
        None

    Raises:
        ValueError: If `raster_config` does not have all the required keys.
    """
    if raster_config.keys() < {"out_file", "size", "geotransform"}:
        raise KeyError(
            "`out_file`, `size`, `geotransform` must be in the `raster_config` "
            "parameter."
        )

    ds_in = ogr.Open(shapefile_path)

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
        layer.SetAttributeFilter("ClusterID={}".format(float(i)))
        gdal.RasterizeLayer(ds_out, [i + 1], layer, burn_values=[1])

    data = ds_out.ReadAsArray().astype(np.float32)
    for i in range(num_layers):
        blurred = gaussian_filter(data[i], sigma)
        ds_out.GetRasterBand(i + 1).WriteArray(blurred)

    ds_out = None
