'''Tool for creating and editing clusters with the K-Means method
'''
import asyncio
import http.server
import socketserver
import webbrowser
import sys
from json import dumps
from math import floor
from os import chdir
from shutil import copytree, rmtree
from tempfile import mkdtemp

import numpy as np
from pyproj import Proj
from sklearn.cluster import KMeans


def create_clusters(locations, n_clusters):
    """Main function. Creates the clusters and calls the web browser
       to edit the result

    Args:
        locations (list): The locations list
        n_clusters (int): The number of clusters to create
    """

    positions = np.zeros([len(locations), 2])
    calculate_utm_def([locations[0]['lon'], locations[0]['lat']])
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

    chdir(web_dir+"/web")
    port = 8087

    Handler = http.server.SimpleHTTPRequestHandler

    httpd = socketserver.TCPServer(("", port), Handler)
    print("serving at port", port)
    webbrowser.open("http://127.0.0.1:" + str(port), new=2)
    #asyncio.run(open_browser(2, port))
    asyncio.run(close_after(100, httpd, web_dir))
    
    httpd.serve_forever()
    print("ENCARA")


async def open_browser(delay, port):
    """Opens browser after some seconds, so the server is running
    
    Args:
        delay (int): Seconds to wait before opening
        port (int): Port to open at the localhost
    """

    await asyncio.sleep(delay)
    webbrowser.open("http://127.0.0.1:" + str(port), new=2)


async def close_after(delay, httpd, web_dir):
    """Closes the script after a delay, so the serve_forever is stopped
    
    Args:
        delay (int): Seconds to wait before closing
        httpd (obj): The web server instance
        web_dir (str): The web dir path to be deleted before leaving
    """

    await asyncio.sleep(delay)
    print("Closing the server")
    rmtree(web_dir)
    httpd.shutdown()
    sys.exit()  # httpd.shutdown() doesn't work...


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
