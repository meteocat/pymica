import unittest

import gdal
import numpy as np
import osr
from pymica.pymica import PyMica


class TestPyMica(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.variables_file = '/tmp/variables.tiff'
        cls.mask_file = '/tmp/mask.tiff'
        size = [1000, 1000]
        alt_data = np.ones(size)
        alt_data[2][2] = 12

        dist_data = np.ones(size)

        driver = gdal.GetDriverByName('GTiff')
        d_s = driver.Create(cls.variables_file, size[1], size[0], 2,
                            gdal.GDT_Float32)

        d_s.GetRasterBand(1).WriteArray(alt_data)
        d_s.GetRasterBand(2).WriteArray(dist_data)

        d_s.SetGeoTransform((260000, 270, 0, 4750000, 0, -270))

        proj = osr.SpatialReference()
        proj.ImportFromEPSG(25831)

        d_s.SetProjection(proj.ExportToWkt())

        d_s = None

        mask = np.zeros([3, 1000, 1000])
        for i in range(3):
            for j in range(500):
                mask[i][i*250 + j][:] = 1 - j/550
        d_s = driver.Create(cls.mask_file, size[1], size[0], 3,
                            gdal.GDT_Float32)

        for i in range(mask.shape[0]):
            d_s.GetRasterBand(i + 1).WriteArray(mask[i])
        d_s = None

    def test_init(self):
        inst = PyMica("./test/data/sample_data.json", self.variables_file,
                      ["./test/data/clusters.json"], self.mask_file)
        self.assertEqual(inst.result.shape, (1000, 1000))

        inst.save_file("/tmp/out.tiff")

        # Test passing multiple variable files instead
        # of one with all the layers
        inst = PyMica("./test/data/sample_data.json", [self.variables_file],
                      ["./test/data/clusters.json"], self.mask_file)

    def test_errors(self):

        with self.assertRaises(FileNotFoundError) as cm:
            PyMica("BadFile", self.variables_file,
                   ["./test/data/clusters.json"], self.mask_file)
        self.assertEqual(
            "[Errno 2] No such file or directory: 'BadFile'",
            str(cm.exception))

        with self.assertRaises(FileNotFoundError) as cm:
            PyMica("./test/data/sample_data.json", ["BadFile"])
        self.assertEqual(
            "[Errno 2] No such file or directory: 'BadFile'",
            str(cm.exception))
        # TODO : mask doesn't exist
    
