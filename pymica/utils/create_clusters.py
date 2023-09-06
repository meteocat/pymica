'''Tool for creating and editing clusters with the K-Means method
'''
import http.server
import os
import socketserver
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
    for i, loc_value in enumerate(locations):
        positions[i][0] = loc_value['lon']
        positions[i][1] = loc_value['lat']
        value = utm(loc_value['lon'], loc_value['lat'])
        positions_list.append(value)
    positions_list = np.array(positions_list)
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(positions_list)

    out_geojson = {"type": "FeatureCollection",
                   "features": []}
    for i, labels_value in enumerate(kmeans.labels_):
        locations[i]['cluster'] = labels_value
        out_geojson['features'].append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [locations[i]['lon'], locations[i]['lat']]
            },
            "properties": {
                "cluster": int(labels_value),
                "id": locations[i]['id'],
                "alt": locations[i]['alt']
            }
        })

    web_dir = mkdtemp()
    copytree("./cluster/web", web_dir+"/web")
    f_p = open(web_dir+"/web/points.json", "w")
    f_p.write(dumps(out_geojson))
    f_p.close()

    os.chdir(web_dir + "/web")
    socketserver.socket.setdefaulttimeout(5)
    Handler = http.server.SimpleHTTPRequestHandler
    httpd = socketserver.TCPServer(("", 8000), Handler)
    print("serving at port", 8000)
    webbrowser.get('firefox').open_new_tab("localhost:8000")

    httpd.serve_forever()


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
