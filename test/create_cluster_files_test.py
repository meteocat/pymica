import unittest
from osgeo import gdal, ogr
from os.path import exists
from os import remove
from cluster.create_cluster_files import (create_reprojected_geoms,
                                          rasterize_clusters)


class TestCalculateField(unittest.TestCase):
    def test_create_reprojected_geoms(self):
        d_s = create_reprojected_geoms("./test/data/clusters.json", 25831)

        self.assertIsInstance(d_s, ogr.DataSource)
        layer = d_s.GetLayer()

        self.assertEqual(layer.GetFeatureCount(), 3)
        self.assertTrue(layer.GetSpatialRef() is not None)

    def test_rasterize_clusters(self):
        out_file = "/tmp/test.tiff"
        geotransform = (260000, 270, 0, 4750000, 0, -270)
        if exists(out_file):
            remove(out_file)

        layer = create_reprojected_geoms("./test/data/clusters.json", 25831)
        rasterize_clusters(layer,
                           {'size': [1000, 1000],
                            'geotransform':geotransform,
                            'out_file': out_file})
        d_s = gdal.Open(out_file)
        self.assertIsNotNone(d_s)

        self.assertEqual(d_s.GetGeoTransform(), geotransform)
        self.assertEqual(d_s.RasterCount, 3)

        # Errors
        with self.assertRaises(ValueError) as cm:
            rasterize_clusters(layer,
                               {'size': [1000, 1000],
                                'geotransform': geotransform,
                                })
        self.assertEqual(
            "The out_conf parameter doesn't have allthe needed elements",
            str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            rasterize_clusters(layer,
                               {'out_file': '/tmp/test.tiff',
                                'geotransform': geotransform
                                })
        self.assertEqual(
            "The out_conf parameter doesn't have allthe needed elements",
            str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            rasterize_clusters(layer,
                               {'out_file': '/tmp/test.tiff',
                                'size': [1000, 1000]
                                })
        self.assertEqual(
            "The out_conf parameter doesn't have allthe needed elements",
            str(cm.exception))
