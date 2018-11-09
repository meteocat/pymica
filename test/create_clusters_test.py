import json
import unittest

from cluster.create_clusters import create_clusters
from cluster.create_clusters import calculate_utm_def

from pyproj import Proj


class TestInverseDistance(unittest.TestCase):
    def test_inverse_distance(self):
        fp = open("./test/data/sample_station_metadata.json")
        data = json.load(fp)
        create_clusters(data, 3)
        fp.close()

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

