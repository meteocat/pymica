"""Tool for creating clusters with the K-Means method.
"""
import json
import math
from os.path import dirname

import numpy as np
from pyproj import Proj
from sklearn.cluster import KMeans


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
    utm = calculate_utm_def([locations[0]["lon"], locations[0]["lat"]])
    positions_list = []
    for i, loc_value in enumerate(locations):
        positions[i][0] = loc_value["lon"]
        positions[i][1] = loc_value["lat"]
        value = utm(loc_value["lon"], loc_value["lat"])
        positions_list.append(value)
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
        with open(geojson_file, 'w') as f_p:
            json.dump(out_geojson, f_p)
    except FileNotFoundError:
        raise FileNotFoundError(dirname(geojson_file) + ' directory does not exist.')


def calculate_utm_def(point: list) -> Proj:
    """Determine proj4 definition calculation the UTM zone from a point (two-element
    list).

    Args:
        point (list): A two element list with the longitude and latitude values of a
                      point.

    Returns:
        Proj: The pyproj.Proj object used to transform data.
    """
    zone = (math.floor((point[0] + 180) / 6) % 60) + 1
    south = " +south " if point[1] < 0 else " "
    desc = (
        "+proj=utm +zone={}{}+ellps=WGS84 +datum=WGS84 +units=m +no_defs"
    ).format(zone, south)

    return Proj(desc)
