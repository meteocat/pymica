'''Tool for creating and editing clusters with the K-Means method
'''
import webbrowser

from json import dumps, load
from math import floor
from shutil import copytree
from tempfile import mkdtemp

import numpy as np
from pyproj import Proj
from sklearn.cluster import KMeans


def create_clusters(locations, n_clusters):
    """Main function. Creates the clusters and calls the web browser
       to edit the result

    Args:
        locations (list, str): The locations list or the file path with the
                               json data
        n_clusters (int): The number of clusters to create
    """
    if isinstance(locations, str):
        f_p = open(locations)
        locations = load(f_p)

    positions = np.zeros([len(locations), 2])
    utm = calculate_utm_def([locations[0]['lon'], locations[0]['lat']])
    positions_list = []
    for i in range(len(locations)):
        positions[i][0] = locations[i]['lon']
        positions[i][1] = locations[i]['lat']
        value = utm(locations[i]['lon'], locations[i]['lat'])
        positions_list.append(value)
    positions_list = np.array(positions_list)
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(positions_list)

    out_geojson = {"type": "FeatureCollection",
                   "features": []}
    for i in range(len(kmeans.labels_)):
        locations[i]['cluster'] = kmeans.labels_[i]
        out_geojson['features'].append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [locations[i]['lon'], locations[i]['lat']]
            },
            "properties": {
                "cluster": int(kmeans.labels_[i]),
                "id": locations[i]['id'],
                "alt": locations[i]['alt']
            }
        })
    web_dir = mkdtemp()
    copytree("./cluster/web", web_dir+"/web")
    f_p = open(web_dir+"/web/points.json", "w")
    f_p.write(dumps(out_geojson))
    f_p.close()

    webbrowser.get('firefox').open_new_tab(web_dir + "/web/index.html")


def calculate_utm_def(point):
    """Returns the proj4 definition, calculating the utm zone from
    a point definition

    Args:
        point (list): A two element list with the lon and lat values
                      from a point

    Returns:
        object: The pyproj.Proj object to use to convert
    """

    zone = (floor((point[0] + 180)/6) % 60) + 1
    south = " +south " if point[1] < 0 else " "
    desc = ("+proj=utm +zone={}{}+ellps=WGS84 +datum=WGS84 " +
            "+units=m +no_defs").format(zone, south)
    return Proj(desc)
