'''Tests for pymica.pymica.py
'''
import io
import json
import unittest
import unittest.mock

import numpy as np
from osgeo import gdal, osr
from pymica.pymica2 import PyMica


class TestPyMica(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        size = [1000, 1000]
        alt_data = np.ones(size)
        alt_data[2][2] = 12
        alt_data[185, 814] = 1000
        alt_data[555, 444] = 100
        alt_data[925, 74] = 10

        dist_data = np.ones(size)

        proj = osr.SpatialReference()
        proj.ImportFromEPSG(25831)

        driver = gdal.GetDriverByName('GTiff')

        # Create fake altitude field
        d_s = driver.Create('test/data/tifs/altitude.tif',
                            size[1], size[0], 1, gdal.GDT_Float32)
        d_s.GetRasterBand(1).WriteArray(alt_data)
        d_s.SetGeoTransform((260000, 270, 0, 4750000, 0, -270))
        d_s.SetProjection(proj.ExportToWkt())
        d_s = None

        # Create fake distance to coast field
        d_s = driver.Create('test/data/tifs/d_coast.tif',
                            size[1], size[0], 1, gdal.GDT_Float32)
        d_s.GetRasterBand(1).WriteArray(dist_data)
        d_s.SetGeoTransform((260000, 270, 0, 4750000, 0, -270))
        d_s.SetProjection(proj.ExportToWkt())
        d_s = None

        # Create wrong fake distance to coast field
        d_s = driver.Create('test/data/tifs/d_coast_2.tif',
                            3, 3, 1, gdal.GDT_Float32)
        d_s.GetRasterBand(1).WriteArray(dist_data[:3, :3])
        d_s.SetGeoTransform((260000, 270, 0, 4750000, 0, -270))
        d_s.SetProjection(proj.ExportToWkt())
        d_s = None

    def test_init_wrong_variables_files(cls):
        with cls.assertRaises(ValueError) as cm:
            PyMica('mlr', './test/data/config_init.json')
        cls.assertEqual('Variables properties are not the same. '
                        'Variables fields must have the same '
                        'GeoTransform, Projection, XSize and YSize.',
                        str(cm.exception))

    def test_init_config_not_found(self):
        with self.assertRaises(FileNotFoundError) as cm:
            PyMica('id3d', 'aaaa.json')
        self.assertEqual('Wrong configuration file path.', str(cm.exception))

    def test_init_config_json_error(self):
        with self.assertRaises(json.decoder.JSONDecodeError) as cm:
            PyMica('id3d', './test/data/config_error.json')
        self.assertEqual('Expecting property name enclosed in double quotes: '
                         'line 2 column 5 (char 6)',
                         str(cm.exception))

    def test_init_wrong_methodology(self):
        with self.assertRaises(ValueError) as cm:
            PyMica('id3', './test/data/config_init.json')
        self.assertEqual('Methodology must be \"id2d\", \"id3d\", '
                         '\"mlr+id2d\", \"mlr+id3d\" or \"mlr\"',
                         str(cm.exception))

    def test_init_default_values_config(self):

        config = {'id3d': {'resolution': 270,
                           'interpolation_bounds': [260000, 4480000,
                                                    530000, 4750000],
                           'EPSG': 25831,
                           'variables_files': {'altitude':
                                               'test/data/tifs/altitude.tif'}}}

        with open('test/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with unittest.mock.patch('sys.stdout',
                                 new_callable=io.StringIO) as mock_stdout:
            inst = PyMica('id3d',
                          './test/data/config_test.json')
        self.assertEqual(mock_stdout.getvalue().strip(),
                         'id_power not in the configuration dictionary.'
                         ' id_power set to default value of 2.5.\n'
                         'id_smoothing not in the configuration dictionary.'
                         ' id_smoothing set to default value of 0.0.\n'
                         'id_penalization not in the configuration dictionary.'
                         ' id_penalization set to default value of 30.')
        self.assertEqual(inst.power, 2.5)
        self.assertEqual(inst.penalization, 30)
        self.assertEqual(inst.smoothing, 0)

    def test_init_missing_interpolation_bounds(self):

        config = {'id2d': {'id_power': 2.5,
                           'id_smoothing': 0.0,
                           'resolution': 1000,
                           'EPSG': 25831}}

        with open('test/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(KeyError) as cm:
            PyMica('id2d', './test/data/config_test.json')
        self.assertEqual('interpolation_bounds must be defined in the '
                         'configuration dictionary.', cm.exception.args[0])

    def test_init_wrong_type_interpolation_bounds(self):

        config = {'id2d': {'id_power': 2.5,
                           'id_smoothing': 0.0,
                           'interpolation_bounds': 0,
                           'resolution': 1000,
                           'EPSG': 25831}}

        with open('test/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(TypeError) as cm:
            PyMica('id2d', './test/data/config_test.json')
        self.assertEqual('interpolation_bounds must be a List as '
                         '[x_min, y_min, x_max, y_max]', cm.exception.args[0])

    def test_init_wrong_length_interpolation_bounds(self):

        config = {'id2d': {'id_power': 2.5,
                           'id_smoothing': 0.0,
                           'interpolation_bounds': [0, 100],
                           'resolution': 1000,
                           'EPSG': 25831}}

        with open('test/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(ValueError) as cm:
            PyMica('id2d', './test/data/config_test.json')
        self.assertEqual('interpolation_bounds must be a List as '
                         '[x_min, y_min, x_max, y_max]', cm.exception.args[0])

    def test_init_missing_resolution(self):

        config = {'id2d': {'id_power': 2.5,
                           'id_smoothing': 0.0,
                           'interpolation_bounds': [0, 0, 1000, 1000],
                           'EPSG': 25831}}

        with open('test/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(KeyError) as cm:
            PyMica('id2d', './test/data/config_test.json')
        self.assertEqual('resolution must be defined in the configuration '
                         'dictionary.', cm.exception.args[0])

    def test_init_wrong_type_resolution(self):

        config = {'id2d': {'id_power': 2.5,
                           'id_smoothing': 0.0,
                           'interpolation_bounds': [0, 0, 1000, 1000],
                           'resolution': "1000",
                           'EPSG': 25831}}

        with open('test/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(TypeError) as cm:
            PyMica('id2d', './test/data/config_test.json')
        self.assertEqual('resolution must have a valid value in meters.',
                         cm.exception.args[0])

    def test_init_missing_epsg(self):

        config = {'id2d': {'id_power': 2.5,
                           'id_smoothing': 0.0,
                           'interpolation_bounds': [0, 0, 1000, 1000],
                           'resolution': 1000}}

        with open('test/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(KeyError) as cm:
            PyMica('id2d', './test/data/config_test.json')
        self.assertEqual('EPSG must be defined in the configuration '
                         'dictionary.', cm.exception.args[0])

    def test_init_wrong_type_epsg(self):

        config = {'id2d': {'id_power': 2.5,
                           'id_smoothing': 0.0,
                           'interpolation_bounds': [0, 0, 1000, 1000],
                           'resolution': 1000,
                           'EPSG': "25831"}}

        with open('test/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(TypeError) as cm:
            PyMica('id2d', './test/data/config_test.json')
        self.assertEqual('EPSG must have a valid int value.',
                         cm.exception.args[0])

    def test_init_missing_variables_files(self):

        config = {'mlr+id2d': {'id_power': 2.5,
                               'id_smoothing': 0.0,
                               'interpolation_bounds': [0, 0, 1000, 1000],
                               'resolution': 1000,
                               'EPSG': 25831}}

        with open('test/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(KeyError) as cm:
            PyMica('mlr+id2d', './test/data/config_test.json')
        self.assertEqual('variables_files must be included in the ' +
                         'configuration file if mlr+id2d is selected.',
                         cm.exception.args[0])

    def test_init_empty_variables_files(self):

        config = {'mlr+id2d': {'id_power': 2.5,
                               'id_smoothing': 0.0,
                               'interpolation_bounds': [0, 0, 1000, 1000],
                               'resolution': 1000,
                               'EPSG': 25831,
                               'variables_files': {}}}

        with open('test/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(ValueError) as cm:
            PyMica('mlr+id2d', './test/data/config_test.json')
        self.assertEqual('variables_files dictionary must have at ' +
                         'least one key including a variable file ' +
                         'path containing a 2D predictor field.',
                         cm.exception.args[0])

    def test_init_not_found_variables_files(self):

        config = {'mlr+id2d': {'id_power': 2.5,
                               'id_smoothing': 0.0,
                               'interpolation_bounds': [0, 0, 1000, 1000],
                               'resolution': 1000,
                               'EPSG': 25831,
                               'variables_files': {'altitude':
                                                   'notfound.tif'}}}

        with open('test/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(FileNotFoundError) as cm:
            PyMica('mlr+id2d', './test/data/config_test.json')
        self.assertEqual('No such file or directory: notfound.tif',
                         str(cm.exception))

    def test_init_two_variables_files(self):

        config = {'mlr+id2d': {'id_power': 2.5,
                               'id_smoothing': 0.0,
                               'interpolation_bounds': [260000, 4480000,
                                                        530000, 4750000],
                               'resolution': 270,
                               'EPSG': 25831,
                               'variables_files': {
                                   'altitude': 'test/data/tifs/altitude.tif',
                                   'd_coast': 'test/data/tifs/d_coast.tif'}}}

        with open('test/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        mlr_id2d = PyMica('mlr+id2d', './test/data/config_test.json')

        self.assertEqual(mlr_id2d.variables.shape, (2, 1000, 1000))

    def test_init_interpolate_id2d(self):

        config = {'id2d': {'id_power': 2.5,
                           'id_smoothing': 0.0,
                           'interpolation_bounds': [260000, 4480000,
                                                    530000, 4750000],
                           'resolution': 270,
                           'EPSG': 25831,
                           'variables_files': {
                               'altitude': 'test/data/tifs/altitude.tif',
                               'd_coast': 'test/data/tifs/d_coast.tif'}}}

        with open('test/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        id2d = PyMica('id2d', './test/data/config_test.json')

        data = [{'id': 'A', 'x': 280000.0, 'y': 4500000.0, 'value': 50.0},
                {'id': 'B', 'x': 380000.0, 'y': 4600000.0, 'value': 20.0},
                {'id': 'C', 'x': 480000.0, 'y': 4700000.0, 'value': 10.0}]

        field = id2d.interpolate(data)

        self.assertEqual(field.shape, (1000, 1000))
        self.assertAlmostEqual(field[0, 0], 23.992, 2)
        self.assertAlmostEqual(field[500, 500], 20.052, 2)
        self.assertAlmostEqual(field[750, 750], 21.693, 2)

    def test_init_interpolate_id3d(self):

        config = {'id3d': {'id_power': 2.5,
                           'id_smoothing': 0.0,
                           'interpolation_bounds': [260000, 4480000,
                                                    530000, 4750000],
                           'resolution': 270,
                           'EPSG': 25831,
                           'variables_files': {
                               'altitude': 'test/data/tifs/altitude.tif',
                               'd_coast': 'test/data/tifs/d_coast.tif'}}}

        with open('test/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        id3d = PyMica('id3d', './test/data/config_test.json')

        data = {'A': {'x': 280000.0, 'y': 4500000.0, 'z': 10, 'value': 50.0},
                'B': {'x': 380000.0, 'y': 4600000.0, 'z': 100,  'value': 20.0},
                'C': {'x': 480000.0, 'y': 4700000.0, 'z': 1000, 'value': 10.0}}

        field = id3d.interpolate(data)

        self.assertEqual(field.shape, (1000, 1000))
        self.assertAlmostEqual(field[0, 0], 24.086, 2)
        self.assertAlmostEqual(field[500, 500], 20.063, 2)
        self.assertAlmostEqual(field[750, 750], 21.809, 2)

    def test_init_interpolate_mlr(self):

        config = {'mlr': {'id_power': 2.5,
                          'id_smoothing': 0.0,
                          'interpolation_bounds': [260000, 4480000,
                                                   530000, 4750000],
                          'resolution': 270,
                          'EPSG': 25831,
                          'variables_files': {
                              'altitude': 'test/data/tifs/altitude.tif'}}}

        with open('test/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        mlr = PyMica('mlr', './test/data/config_test.json')

        data = [{'id': 'A', 'x': 280000.0, 'y': 4500000.0,
                 'altitude': 10, 'value': 50.0},
                {'id': 'B', 'x': 380000.0, 'y': 4600000.0,
                 'altitude': 100,  'value': 20.0},
                {'id': 'C', 'x': 480000.0, 'y': 4700000.0,
                 'altitude': 1000, 'value': 10.0}]

        field = mlr.interpolate(data)

        self.assertEqual(field.shape, (1000, 1000))
        self.assertAlmostEqual(field[0, 0], 37.193, 2)
        self.assertAlmostEqual(field[2, 2], 36.879, 2)
        self.assertAlmostEqual(field[3, 3], 37.193, 2)

    def test_init_interpolate_mlr_id2d(self):

        config = {'mlr+id2d': {'id_power': 2.5,
                               'id_smoothing': 0.0,
                               'interpolation_bounds': [260000, 4480000,
                                                        530000, 4750000],
                               'resolution': 270,
                               'EPSG': 25831,
                               'variables_files': {
                                   'altitude': 'test/data/tifs/altitude.tif'}}}

        with open('test/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        mlr_id2d = PyMica('mlr+id2d', './test/data/config_test.json')

        data = [{'id': 'A', 'x': 280000.0, 'y': 4500000.0,
                 'altitude': 10, 'value': 50.0},
                {'id': 'B', 'x': 380000.0, 'y': 4600000.0,
                 'altitude': 100,  'value': 20.0},
                {'id': 'C', 'x': 480000.0, 'y': 4700000.0,
                 'altitude': 1000, 'value': 10.0}]

        field = mlr_id2d.interpolate(data)

        self.assertEqual(field.shape, (1000, 1000))
        self.assertAlmostEqual(field[925, 74], 50.000, 2)
        self.assertAlmostEqual(field[555, 444], 20.000, 2)
        self.assertAlmostEqual(field[185, 814], 9.999, 2)
