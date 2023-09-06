'''Tests fot create_cluster_files.py
'''
import unittest
from os import remove
from os.path import exists
from tempfile import gettempdir

from osgeo import gdal, ogr

from pymica.utils.create_cluster_files import (create_reprojected_geoms,
                                          rasterize_clusters)


class TestCreateClustersFiles(unittest.TestCase):
    def test_create_reprojected_geoms(self):
        d_s = create_reprojected_geoms("./pymica_tests/data/clusters.json", 25831)

        self.assertIsInstance(d_s, ogr.DataSource)
        layer = d_s.GetLayer()

        self.assertEqual(layer.GetFeatureCount(), 3)
        self.assertTrue(layer.GetSpatialRef() is not None)

        with self.assertRaises(IOError) as c_m:
            create_reprojected_geoms("/bad_file.json", 25831)
        self.assertEqual(
            "File /bad_file.json doesn't exist",
            str(c_m.exception))

        with self.assertRaises(ValueError) as c_m:
            create_reprojected_geoms("./pymica_tests/data/clusters.json", -999)
        self.assertEqual(
            "Wrong EPSG code: -999",
            str(c_m.exception))

    def test_rasterize_clusters(self):
        out_file = gettempdir() + "/test.tiff"
        geotransform = (260000, 270, 0, 4750000, 0, -270)
        if exists(out_file):
            remove(out_file)

        layer = create_reprojected_geoms("./pymica_tests/data/clusters.json", 25831)
        rasterize_clusters(layer,
                           {'size': [1000, 1000],
                            'geotransform': geotransform,
                            'out_file': out_file})
        d_s = gdal.Open(out_file)
        self.assertIsNotNone(d_s)

        self.assertEqual(d_s.GetGeoTransform(), geotransform)
        self.assertEqual(d_s.RasterCount, 3)

        # Errors
        with self.assertRaises(ValueError) as c_m:
            rasterize_clusters(layer,
                               {'size': [1000, 1000],
                                'geotransform': geotransform,
                                })
        self.assertEqual(
            "The out_conf parameter doesn't have allthe needed elements",
            str(c_m.exception))

        with self.assertRaises(ValueError) as c_m:
            rasterize_clusters(layer,
                               {'out_file': gettempdir() + '/test.tiff',
                                'geotransform': geotransform
                                })
        self.assertEqual(
            "The out_conf parameter doesn't have allthe needed elements",
            str(c_m.exception))

        with self.assertRaises(ValueError) as c_m:
            rasterize_clusters(layer,
                               {'out_file': gettempdir() + '/test.tiff',
                                'size': [1000, 1000]
                                })
        self.assertEqual(
            "The out_conf parameter doesn't have allthe needed elements",
            str(c_m.exception))
