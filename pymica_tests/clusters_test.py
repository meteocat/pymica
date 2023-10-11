"""Tests creation of clusters files (shapefiles and rasters)
"""
import json
import unittest
from glob import glob
from os import remove
from os.path import exists
from tempfile import gettempdir

from osgeo import gdal, ogr

from pymica.utils.clusters import (
    create_clusters,
    rasterize_clusters,
)


class TestClusters(unittest.TestCase):
    """Test creation and rasterization of clusters"""

    with open("pymica_tests/data/sample_station_metadata.json", "r") as f_p:
        sample_data = json.load(f_p)

    clusters_test_file = "pymica_tests/data/test_clusters_3.shp"
    bounding_box = [260000, 4488100, 530000, 4750000]

    def test_rasterize_clusters(self):
        """Test rasterization of clusters"""
        out_file = gettempdir() + "/test.tiff"
        geotransform = (260000, 270, 0, 4750000, 0, -270)
        if exists(out_file):
            remove(out_file)

        rasterize_clusters(
            self.clusters_test_file,
            {"size": [1000, 1000], "geotransform": geotransform, "out_file": out_file},
        )
        d_s = gdal.Open(out_file)
        self.assertIsNotNone(d_s)

        self.assertEqual(d_s.GetGeoTransform(), geotransform)
        self.assertEqual(d_s.RasterCount, 3)

        # Errors
        with self.assertRaises(KeyError) as err:
            rasterize_clusters(
                self.clusters_test_file,
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
                self.clusters_test_file,
                {"out_file": gettempdir() + "/test.tiff", "geotransform": geotransform},
            )
        self.assertEqual(
            "`out_file`, `size`, `geotransform` must be in the `raster_config` "
            "parameter.",
            err.exception.args[0],
        )

        with self.assertRaises(KeyError) as err:
            rasterize_clusters(
                self.clusters_test_file,
                {"out_file": gettempdir() + "/test.tiff", "size": [1000, 1000]},
            )
        self.assertEqual(
            "`out_file`, `size`, `geotransform` must be in the `raster_config` "
            "parameter.",
            err.exception.args[0],
        )

    def test_create_clusters(self):
        """Test creation of clusters with Kmeans"""
        clusters_file_path = "pymica_tests/data/test_clusters_file_3.shp"

        create_clusters(
            self.sample_data, 3, clusters_file_path, self.bounding_box, 25831
        )

        self.assertTrue(exists(clusters_file_path))

        clusters = ogr.Open(clusters_file_path)
        layer = clusters.GetLayer()

        self.assertEqual(layer.GetFeatureCount(), 3)
        self.assertEqual(layer.GetFeature(0).ClusterID, 0.0)
        self.assertEqual(layer.GetFeature(2).ClusterID, 2.0)

    def test_create_clusters_from_file(self):
        """Test creation of clusters with Kmeans from file"""
        clusters_file_path = "pymica_tests/data/test_clusters_file_6.shp"

        create_clusters(
            "pymica_tests/data/sample_station_metadata.json",
            6,
            clusters_file_path,
            self.bounding_box,
            25831,
        )

        self.assertTrue(exists(clusters_file_path))

        clusters = ogr.Open(clusters_file_path)
        layer = clusters.GetLayer()

        self.assertEqual(layer.GetFeatureCount(), 6)
        self.assertEqual(layer.GetFeature(0).ClusterID, 0.0)
        self.assertEqual(layer.GetFeature(2).ClusterID, 2.0)

    def tearDown(self) -> None:
        cluster_files = glob("pymica_tests/data/test_clusters_file_3.*")
        for cluster_file in cluster_files:
            remove(cluster_file)

        cluster_files = glob("pymica_tests/data/test_clusters_file_6.*")
        for cluster_file in cluster_files:
            remove(cluster_file)

        return super().tearDown()
