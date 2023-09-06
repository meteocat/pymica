import math
import pyproj


def calculate_utm_def(point):
    """Returns the proj4 definition, calculating the utm zone from
    a point definition

    Args:
        point (list): A two element list with the lon and lat values
                      from a point

    Returns:
        object: The pyproj.Proj object to use to convert
    """

    zone = (math.floor((point[0] + 180)/6) % 60) + 1
    south = " +south " if point[1] < 0 else " "
    desc = ("+proj=utm +zone={}{}+ellps=WGS84 +datum=WGS84 " +
            "+units=m +no_defs").format(zone, south)
    return pyproj.Proj(desc)