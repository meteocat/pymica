from math import exp
from math import floor
import ogr
import osr


def dist2func(dist):
    return 1 - exp(-3*dist/100000)


def get_dists(points, dist_file):
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

    proj = osr.SpatialReference()
    zone = (floor((point[0] + 180)/6) % 60) + 1
    south = " +south " if point[1] < 0 else " "
    desc = ("+proj=utm +zone={}{}+ellps=WGS84 +datum=WGS84 " +
            "+units=m +no_defs").format(zone, south)
    proj.ImportFromProj4(desc)
    return proj