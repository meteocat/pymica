'''Tests for pymica.pymica.py
'''
from operator import methodcaller
import unittest
from tempfile import gettempdir

import numpy as np
from osgeo import gdal, osr
from pymica.pymica2 import PyMica


class TestPyMica2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.variables_file = gettempdir() + '/variables.tiff'
        cls.config = {'variables_files':
                      {'altitude': gettempdir() + '/altitude.tif',
                       'd_coast': gettempdir() + '/d_coast.tif'}}
        cls.config_wrong = {'variables_files':
                            {'altitude': gettempdir() + '/altitude.tif',
                             'd_coast': gettempdir() + '/d_coast_2.tif'}}

        size = [1000, 1000]
        alt_data = np.ones(size)
        alt_data[2][2] = 12

        dist_data = np.ones(size)

        proj = osr.SpatialReference()
        proj.ImportFromEPSG(25831)

        driver = gdal.GetDriverByName('GTiff')

        # Create fake altitude field
        d_s = driver.Create(cls.config['variables_files']['altitude'],
                            size[1], size[0], 1, gdal.GDT_Float32)
        d_s.GetRasterBand(1).WriteArray(alt_data)
        d_s.SetGeoTransform((260000, 270, 0, 4750000, 0, -270))
        d_s.SetProjection(proj.ExportToWkt())
        d_s = None

        # Create fake distance to coast field
        d_s = driver.Create(cls.config['variables_files']['d_coast'],
                            size[1], size[0], 1, gdal.GDT_Float32)
        d_s.GetRasterBand(1).WriteArray(dist_data)
        d_s.SetGeoTransform((260000, 270, 0, 4750000, 0, -270))
        d_s.SetProjection(proj.ExportToWkt())
        d_s = None

        # Create wrong fake distance to coast field
        d_s = driver.Create(cls.config_wrong['variables_files']['d_coast'],
                            3, 3, 1, gdal.GDT_Float32)
        d_s.GetRasterBand(1).WriteArray(dist_data[:3, :3])
        d_s.SetGeoTransform((260000, 270, 0, 4750000, 0, -270))
        d_s.SetProjection(proj.ExportToWkt())
        d_s = None

    def test_init(cls):
        mlr_id2d = PyMica(methodology='mlr+id2d', config=cls.config)
        cls.assertEqual(mlr_id2d.smoothing, 0.0)
        cls.assertEqual(mlr_id2d.power, 2.5)

        mlr_id3d = PyMica(methodology='mlr+id3d', config=cls.config)
        cls.assertEqual(mlr_id3d.smoothing, 0.0)
        cls.assertEqual(mlr_id3d.power, 2.5)
        cls.assertEqual(mlr_id3d.penalization, 30)

    def test_init_wrong_variables_files(cls):
        with cls.assertRaises(ValueError) as cm:
            PyMica(methodology='mlr+id2d', config=cls.config_wrong)
        cls.assertEqual('Variables properties are not the same. '
                        'Variables fields must have the same '
                        'GeoTransform, Projection, XSize and YSize.',
                        str(cm.exception))

    def test_init_different_vars(self):
        with open("./test/data/sample_data.json") as d_s:
            data = d_s.read()
        with open(gettempdir() + "/sample_data.json", "w") as d_s:
            d_s.write(data.replace('id', 'other_id')
                          .replace('temp', 'other_var')
                          .replace('dist', 'other_x_var'))

        data_format = {'loc_vars': ('lon', 'lat'),
                       'id_key': 'other_id',
                       'y_var': 'other_var',
                       'x_vars': ('altitude', 'other_x_var')}
        inst = PyMica(gettempdir() + "/sample_data.json", self.variables_file,
                      self.clusters, data_format)
        self.assertEqual(inst.result.shape, (1000, 1000))

    @unittest.skip
    def test_errors(self):

        with self.assertRaises(FileNotFoundError) as cm:
            PyMica("BadFile", self.variables_file,
                   self.clusters)
        self.assertEqual(
            "[Errno 2] No such file or directory: 'BadFile'",
            str(cm.exception))

        with self.assertRaises(FileNotFoundError) as cm:
            PyMica("./test/data/sample_data.json", ["BadFile"])
        self.assertEqual(
            "[Errno 2] No such file or directory: 'BadFile'",
            str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            PyMica("./test/data/sample_data.json", self.variables_file,
                   residuals_int='BadMethdology')
        self.assertEqual(
            "[Errno 2]residuals_int must be \"id2d\"," +
            " \"id3d\" or \"idw\"",
            str(cm.exception)
            )
        # TODO : mask doesn't exist or clusters bad formatted
        # TODO : Bad variable names passed
