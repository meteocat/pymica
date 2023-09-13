"""Tests creation of clusters files (shapefiles and rasters)
"""
import unittest
from os import remove
from os.path import exists
from tempfile import gettempdir

from osgeo import gdal, ogr
import json

from pymica.utils.clusters import (
    create_reprojected_geometries,
    rasterize_clusters,
    create_clusters,
)


class TestClusters(unittest.TestCase):
    """Test creation and rasterization of clusters"""

    with open("pymica_tests/data/sample_station_metadata.json", "r") as f_p:
        sample_data = json.load(f_p)

    def test_create_reprojected_geometries(self):
        """Test creation of reprojected geometries"""
        d_s = create_reprojected_geometries("pymica_tests/data/clusters.json", 25831)

        self.assertIsInstance(d_s, ogr.DataSource)
        layer = d_s.GetLayer()

        self.assertEqual(layer.GetFeatureCount(), 3)
        self.assertTrue(layer.GetSpatialRef() is not None)

        with self.assertRaises(IOError) as err:
            create_reprojected_geometries("/bad_file.json", 25831)
        self.assertEqual("File /bad_file.json doesn't exist", str(err.exception))

        with self.assertRaises(ValueError) as err:
            create_reprojected_geometries("pymica_tests/data/clusters.json", -999)
        self.assertEqual("Wrong EPSG code: -999", str(err.exception))

    def test_rasterize_clusters(self):
        """Test rasterization of clusters"""
        out_file = gettempdir() + "/test.tiff"
        geotransform = (260000, 270, 0, 4750000, 0, -270)
        if exists(out_file):
            remove(out_file)

        layer = create_reprojected_geometries("pymica_tests/data/clusters.json", 25831)
        rasterize_clusters(
            layer,
            {"size": [1000, 1000], "geotransform": geotransform, "out_file": out_file},
        )
        d_s = gdal.Open(out_file)
        self.assertIsNotNone(d_s)

        self.assertEqual(d_s.GetGeoTransform(), geotransform)
        self.assertEqual(d_s.RasterCount, 3)

        # Errors
        with self.assertRaises(KeyError) as err:
            rasterize_clusters(
                layer,
                {
                    "size": [1000, 1000],
                    "geotransform": geotransform,
                },
            )
        self.assertEqual(
            "`out_file`, `size`, `geotransform` must be in the `raster_config` "
            "parameter.",
            err.exception.args[0],
        )

        with self.assertRaises(KeyError) as err:
            rasterize_clusters(
                layer,
                {"out_file": gettempdir() + "/test.tiff", "geotransform": geotransform},
            )
        self.assertEqual(
            "`out_file`, `size`, `geotransform` must be in the `raster_config` "
            "parameter.",
            err.exception.args[0],
        )

        with self.assertRaises(KeyError) as err:
            rasterize_clusters(
                layer, {"out_file": gettempdir() + "/test.tiff", "size": [1000, 1000]}
            )
        self.assertEqual(
            "`out_file`, `size`, `geotransform` must be in the `raster_config` "
            "parameter.",
            err.exception.args[0],
        )

    def test_create_clusters(self):
        """Test creation of clusters with Kmeans"""
        create_clusters(self.sample_data, 6, "pymica_tests/data/test_clusters_6.json")

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

        if exists("pymica_tests/data/test_clusters_6.json"):
            remove("pymica_tests/data/test_clusters_6.json")

    def test_create_clusters_from_file(self):
        """Test creation of clusters with Kmeans from file"""
        create_clusters(
            "pymica_tests/data/sample_station_metadata.json",
            6,
            "pymica_tests/data/test_clusters_6.json",
        )

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

        if exists("pymica_tests/data/test_clusters_6.json"):
            remove("pymica_tests/data/test_clusters_6.json")

    def test_create_clusters_wrong_dir(self):
        """Test error raise from creation of clusters"""
        with self.assertRaises(FileNotFoundError) as err:
            create_clusters(
                "pymica_tests/data/sample_station_metadata.json",
                6,
                "not/found/test_clusters_6.json",
            )

        self.assertEqual(err.exception.args[0], "not/found directory does not exist.")
