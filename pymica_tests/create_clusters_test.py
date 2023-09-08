"""Tests for creation of clusters.
"""
import json
import unittest
from os.path import exists

from pyproj import Proj

from pymica.utils.create_clusters import calculate_utm_def, create_clusters


class TestCreateClusters(unittest.TestCase):
    """Test creation of clusters"""

    with open("pymica_tests/data/sample_station_metadata.json", "r") as f_p:
        sample_data = json.load(f_p)

    def test_create_clusters(self):
        """Test create_clusters"""
        create_clusters(self.sample_data, 6, "pymica_tests/datatest_clusters_6.json")

        self.assertTrue(exists("pymica_tests/data/test_clusters_6.json"))

        with open("pymica_tests/data/test_clusters_6.json", "r") as f_p:
            clusters = json.load(f_p)

        self.assertEqual(
            clusters["features"][0]["geometry"]["coordinates"], [2.18091, 41.39004]
        )
        self.assertEqual(
            clusters["features"][0]["properties"],
            {"cluster": 1, "id": "AN", "alt": 7.5},
        )

        self.assertEqual(
            clusters["features"][-1]["geometry"]["coordinates"], [1.89716, 42.32211]
        )
        self.assertEqual(
            clusters["features"][-1]["properties"],
            {"cluster": 2, "id": "ZD", "alt": 2478},
        )

    def test_create_clusters_not_found(self):
        """Test directory not found in create_clusters"""
        with self.assertRaises(FileNotFoundError) as err:
            create_clusters(self.sample_data, 6, "dir_not_found/sample.json")

        self.assertEqual(
            err.exception.args[0], "dir_not_found directory does not exist."
        )

    def test_calculate_utm_def(self):
        """Test calculate definition of UTM from a point"""
        point = [0, 0]
        result = calculate_utm_def(point)
        expected = Proj(
            "+proj=utm +zone=31 +ellps=WGS84 " + "+datum=WGS84 +units=m +no_defs"
        )

        self.assertIsInstance(result, Proj)
        self.assertEqual(
            set(result(point[0], point[1])), set(expected(point[0], point[1]))
        )

        point = [0, -10]
        result = calculate_utm_def(point)
        expected = Proj(
            "+proj=utm +zone=31 +south +ellps=WGS84 " + "+datum=WGS84 +units=m +no_defs"
        )

        self.assertIsInstance(result, Proj)
        self.assertEqual(
            set(result(point[0], point[1])), set(expected(point[0], point[1]))
        )

        point = [-178, 24]
        result = calculate_utm_def(point)
        expected = Proj(
            "+proj=utm +zone=1 +ellps=WGS84 " + "+datum=WGS84 +units=m +no_defs"
        )

        self.assertIsInstance(result, Proj)
        self.assertEqual(
            set(result(point[0], point[1])), set(expected(point[0], point[1]))
        )
