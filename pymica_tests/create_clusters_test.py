'''Tests for cluster.create_clusters.py
'''
import unittest

from pymica.utils.create_clusters import calculate_utm_def
from pyproj import Proj


class TestCreateClusters(unittest.TestCase):

    # Not possible to open a browser in TravisCI
    '''
    def test_create_clusters(self):
        fp = open("./test/data/sample_station_metadata.json")
        data = json.load(fp)
        create_clusters(data, 6)
        fp.close()
    '''

    def test_calculate_utm_def(self):
        point = [0, 0]
        result = calculate_utm_def(point)
        expected = Proj("+proj=utm +zone=31 +ellps=WGS84 " +
                        "+datum=WGS84 +units=m +no_defs")

        self.assertIsInstance(result, Proj)
        self.assertEqual(set(result(point[0], point[1])),
                         set(expected(point[0], point[1])))

        point = [0, -10]
        result = calculate_utm_def(point)
        expected = Proj("+proj=utm +zone=31 +south +ellps=WGS84 " +
                        "+datum=WGS84 +units=m +no_defs")

        self.assertIsInstance(result, Proj)
        self.assertEqual(set(result(point[0], point[1])),
                         set(expected(point[0], point[1])))

        point = [-178, 24]
        result = calculate_utm_def(point)
        expected = Proj("+proj=utm +zone=1 +ellps=WGS84 " +
                        "+datum=WGS84 +units=m +no_defs")

        self.assertIsInstance(result, Proj)
        self.assertEqual(set(result(point[0], point[1])),
                         set(expected(point[0], point[1])))
