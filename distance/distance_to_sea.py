'''Calculations to get the distance to the coast values
'''
from math import exp, floor

from osgeo import ogr
from osgeo import osr
from numpy import ones


def dist2func(dist):
    '''A basic distance function that makes it not linear and
    with a maximum value of 1

    Args:
        dist (float): The real distance in meters

    Returns:
        float: A value from 0 to 1 to be used in the regression
    '''

    return 1 - exp(-3*dist/100000)


def get_distances(points, dist_file):
    '''Get the distances from a shore line (or any line) to a set
    of points. The function reprojects the points and file to the
    best fitting UTM projection so the distances are in meters

    Args:
        points (list): a list of (lon, lat) points
        dist_file (str): The path to an ogr compatible file with a line
                         containing the shore geometry.

    Raises:
        IOError: The dist_file doesn't exist

    Returns:
        list: The list of distances, one for each point, in meters
    '''

    d_s = ogr.Open(dist_file)

    if d_s is None:
        raise IOError("File {} doesn't exist".format(dist_file))
    lyr = d_s.GetLayer()
    lyr.ResetReading()

    feat = next(iter(lyr))
    geom = feat.GetGeometryRef()
    file_proj = geom.GetSpatialReference()
    points_proj = osr.SpatialReference()
    points_proj.ImportFromEPSG(4326)

    target_proj = calculate_utm_def(points[0])

    transform_file = osr.CoordinateTransformation(file_proj, target_proj)
    geom.Transform(transform_file)

    transform_point = osr.CoordinateTransformation(points_proj, target_proj)

    out = []
    for point in points:
        point = ogr.CreateGeometryFromWkt("POINT ({} {})".format(point[0],
                                                                 point[1]))
        point.Transform(transform_point)

        out.append(point.Distance(geom))
    return out


def calculate_utm_def(point):
    '''Calculates the utm zone from a point in lon - lat

    Args:
        point (list): A two element list with the longitude and latitude values

    Returns:
       osr.SpatialReference : The osr projection object
    '''

    proj = osr.SpatialReference()
    zone = (floor((point[0] + 180)/6) % 60) + 1
    south = " +south " if point[1] < 0 else " "
    desc = ("+proj=utm +zone={}{}+ellps=WGS84 +datum=WGS84 " +
            "+units=m +no_defs").format(zone, south)
    proj.ImportFromProj4(desc)
    return proj


def get_dist_array(proj, geotransform, size, dist_file, verbose=True):
    '''Creates a numpy array with the distance to the coast values applying
    the dist2func to all the actual distances so the values go from 0 to 1

    Args:
        proj (int): The EPSG code for the output matrix values projection
        geotransform (list): The geotransform as defined in the gdal data model
        size (list): A two element list with the longitude and latitude values
        dist_file (str): The path to an ogr compatible file with a line
                         containing the shore geometry.

    Raises:
        IOError: The dist_file doesn't exist

    Returns:
        numpy.ndarray: The matrix with the function values
    '''

    d_s = ogr.Open(dist_file)

    if d_s is None:
        raise IOError("File {} doesn't exist".format(dist_file))
    lyr = d_s.GetLayer()
    lyr.ResetReading()

    feat = next(iter(lyr))
    geom = feat.GetGeometryRef()
    file_proj = geom.GetSpatialReference()

    target_proj = osr.SpatialReference()
    target_proj.ImportFromEPSG(proj)

    transform_file = osr.CoordinateTransformation(file_proj, target_proj)
    geom.Transform(transform_file)

    out_array = ones([size[1], size[0]])

    for i in range(size[0]):
        if verbose:
            print("\rProgress: {:.1f}%".format(100*(i/size[0])), end='',
                  flush=True)
        for j in range(size[1]):
            x_coord = i * geotransform[1] + geotransform[0]
            y_coord = j * geotransform[5] + geotransform[3]

            point = ogr.Geometry(ogr.wkbPoint)
            point.SetPoint_2D(0, x_coord, y_coord)

            dist = point.Distance(geom)

            out_array[j, i] = dist2func(dist)
    if verbose:
        print("\rProgress: 100%  ")
    return out_array
