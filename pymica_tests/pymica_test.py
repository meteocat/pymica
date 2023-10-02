'''Tests for pymica.pymica.py
'''
from genericpath import exists
import io
import json
from os import remove, makedirs, rmdir
import unittest
import unittest.mock

import numpy as np
from osgeo import gdal, osr
from pymica.pymica import PyMica


class TestPyMica(unittest.TestCase):

    data = [{'id': 'A', 'lon': 0.3990722, 'lat': 40.6215578,
                 'altitude': 10, 'value': 50.0},
                {'id': 'B', 'lon': 1.5613071, 'lat': 41.5426639,
                 'altitude': 100, 'value': 20.0},
                {'id': 'C', 'lon': 2.7567764, 'lat': 42.4520729,
                 'altitude': 1000, 'value': 10.0}]

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

        makedirs('pymica_tests/data/tifs/')

        driver = gdal.GetDriverByName('GTiff')

        # Create fake altitude field
        d_s = driver.Create('pymica_tests/data/tifs/altitude.tif',
                            size[1], size[0], 1, gdal.GDT_Float32)
        d_s.GetRasterBand(1).WriteArray(alt_data)
        d_s.SetGeoTransform((260000, 270, 0, 4750000, 0, -270))
        d_s.SetProjection(proj.ExportToWkt())
        d_s = None

        # Create fake distance to coast field
        d_s = driver.Create('pymica_tests/data/tifs/d_coast.tif',
                            size[1], size[0], 1, gdal.GDT_Float32)
        d_s.GetRasterBand(1).WriteArray(dist_data)
        d_s.SetGeoTransform((260000, 270, 0, 4750000, 0, -270))
        d_s.SetProjection(proj.ExportToWkt())
        d_s = None

        # Create wrong fake distance to coast field
        d_s = driver.Create('pymica_tests/data/tifs/d_coast_2.tif',
                            3, 3, 1, gdal.GDT_Float32)
        d_s.GetRasterBand(1).WriteArray(dist_data[:3, :3])
        d_s.SetGeoTransform((260000, 270, 0, 4750000, 0, -270))
        d_s.SetProjection(proj.ExportToWkt())
        d_s = None

        config = {'id3d': {'id_smoothing': 0.0,
                           'id_penalization': 30,
                           'resolution': 270,
                           'id_power': 2.5,
                           'interpolation_bounds': [260000, 4480000,
                                                    530000, 4750000],
                           'EPSG': 25831,
                           'variables_files': {'altitude':
                                               'pymica_tests/data/tifs/altitude.tif'}},
                  'mlr': {'clusters': None,
                          'resolution': 270,
                          'interpolation_bounds': [260000, 4480000,
                                                   530000, 4750000],
                          'EPSG': 25831,
                          'variables_files': {'altitude':
                                              'pymica_tests/data/tifs/altitude.tif',
                                              'd_coast':
                                              'pymica_tests/data/tifs/d_coast.tif'}}}

        with open('pymica_tests/data/config_interpolate.json', 'w') as f:
            json.dump(config, f)
            f.close()

    def test_init_wrong_variables_files(cls):
        config = {'mlr': {'resolution': 270,
                          'interpolation_bounds': [260000, 4480000,
                                                   530000, 4750000],
                          'clusters': 'None',
                          'variables_files': {'altitude': 'pymica_tests/data/tifs/'
                                                          'altitude.tif',
                                              'd_coast': 'pymica_tests/data/tifs/'
                                                         'd_coast_2.tif'},
                          'EPSG': 25831}}

        with open('pymica_tests/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with cls.assertRaises(ValueError) as cm:
            PyMica('mlr', 'pymica_tests/data/config_test.json')
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
            PyMica('id3d', 'pymica_tests/data/config_error.json')
        self.assertEqual('Expecting property name enclosed in double quotes: '
                         'line 2 column 5 (char 6)',
                         str(cm.exception))

    def test_init_wrong_methodology(self):
        with self.assertRaises(ValueError) as cm:
            PyMica('id3', 'pymica_tests/data/config_interpolate.json')
        self.assertEqual('Methodology must be \"id2d\", \"id3d\", '
                         '\"mlr+id2d\", \"mlr+id3d\" or \"mlr\"',
                         str(cm.exception))

    def test_init_methodology_not_in_config(self):

        config = {'id3d': {'resolution': 270,
                           'interpolation_bounds': [260000, 4480000,
                                                    530000, 4750000],
                           'EPSG': 25831,
                           'variables_files': {'altitude':
                                               'pymica_tests/data/tifs/altitude.tif'}}}

        with open('pymica_tests/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(KeyError) as cm:
            PyMica('id2d', 'pymica_tests/data/config_test.json')
        self.assertEqual('id2d not defined in the configuration file.',
                         cm.exception.args[0])

    def test_init_default_values_config(self):

        config = {'id3d': {'resolution': 270,
                           'interpolation_bounds': [260000, 4480000,
                                                    530000, 4750000],
                           'EPSG': 25831,
                           'variables_files': {'altitude':
                                               'pymica_tests/data/tifs/altitude.tif'}}}

        with open('pymica_tests/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with unittest.mock.patch('sys.stdout',
                                 new_callable=io.StringIO) as mock_stdout:
            inst = PyMica('id3d',
                          'pymica_tests/data/config_test.json')
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

        with open('pymica_tests/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(KeyError) as cm:
            PyMica('id2d', 'pymica_tests/data/config_test.json')
        self.assertEqual('interpolation_bounds must be defined in the '
                         'configuration dictionary.', cm.exception.args[0])

    def test_init_wrong_type_interpolation_bounds(self):

        config = {'id2d': {'id_power': 2.5,
                           'id_smoothing': 0.0,
                           'interpolation_bounds': 0,
                           'resolution': 1000,
                           'EPSG': 25831}}

        with open('pymica_tests/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(TypeError) as cm:
            PyMica('id2d', 'pymica_tests/data/config_test.json')
        self.assertEqual('interpolation_bounds must be a List as '
                         '[x_min, y_min, x_max, y_max]', cm.exception.args[0])

    def test_init_wrong_length_interpolation_bounds(self):

        config = {'id2d': {'id_power': 2.5,
                           'id_smoothing': 0.0,
                           'interpolation_bounds': [0, 100],
                           'resolution': 1000,
                           'EPSG': 25831}}

        with open('pymica_tests/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(ValueError) as cm:
            PyMica('id2d', 'pymica_tests/data/config_test.json')
        self.assertEqual('interpolation_bounds must be a List as '
                         '[x_min, y_min, x_max, y_max]', cm.exception.args[0])

    def test_init_missing_resolution(self):

        config = {'id2d': {'id_power': 2.5,
                           'id_smoothing': 0.0,
                           'interpolation_bounds': [0, 0, 1000, 1000],
                           'EPSG': 25831}}

        with open('pymica_tests/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(KeyError) as cm:
            PyMica('id2d', 'pymica_tests/data/config_test.json')
        self.assertEqual('resolution must be defined in the configuration '
                         'dictionary.', cm.exception.args[0])

    def test_init_wrong_type_resolution(self):

        config = {'id2d': {'id_power': 2.5,
                           'id_smoothing': 0.0,
                           'interpolation_bounds': [0, 0, 1000, 1000],
                           'resolution': '1000',
                           'EPSG': 25831}}

        with open('pymica_tests/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(TypeError) as cm:
            PyMica('id2d', 'pymica_tests/data/config_test.json')
        self.assertEqual('resolution must have a valid value in meters.',
                         cm.exception.args[0])

    def test_init_missing_epsg(self):

        config = {'id2d': {'id_power': 2.5,
                           'id_smoothing': 0.0,
                           'interpolation_bounds': [0, 0, 1000, 1000],
                           'resolution': 1000}}

        with open('pymica_tests/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(KeyError) as cm:
            PyMica('id2d', 'pymica_tests/data/config_test.json')
        self.assertEqual('EPSG must be defined in the configuration '
                         'dictionary.', cm.exception.args[0])

    def test_init_wrong_type_epsg(self):

        config = {'id2d': {'id_power': 2.5,
                           'id_smoothing': 0.0,
                           'interpolation_bounds': [0, 0, 1000, 1000],
                           'resolution': 1000,
                           'EPSG': '25831'}}

        with open('pymica_tests/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(TypeError) as cm:
            PyMica('id2d', 'pymica_tests/data/config_test.json')
        self.assertEqual('EPSG must have a valid int value.',
                         cm.exception.args[0])

    def test_init_missing_variables_files(self):

        config = {'mlr+id2d': {'id_power': 2.5,
                               'id_smoothing': 0.0,
                               'interpolation_bounds': [0, 0, 1000, 1000],
                               'resolution': 1000,
                               'EPSG': 25831}}

        with open('pymica_tests/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(KeyError) as cm:
            PyMica('mlr+id2d', 'pymica_tests/data/config_test.json')
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

        with open('pymica_tests/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(ValueError) as cm:
            PyMica('mlr+id2d', 'pymica_tests/data/config_test.json')
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

        with open('pymica_tests/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        with self.assertRaises(FileNotFoundError) as cm:
            PyMica('mlr+id2d', 'pymica_tests/data/config_test.json')
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
                                   'altitude': 'pymica_tests/data/tifs/altitude.tif',
                                   'd_coast': 'pymica_tests/data/tifs/d_coast.tif'}}}

        with open('pymica_tests/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        mlr_id2d = PyMica('mlr+id2d', 'pymica_tests/data/config_test.json')

        self.assertEqual(mlr_id2d.variables.shape, (2, 1000, 1000))

    def test_init_interpolate_id2d(self):

        config = {'id2d': {'id_power': 2.5,
                           'id_smoothing': 0.0,
                           'interpolation_bounds': [260000, 4480000,
                                                    530000, 4750000],
                           'resolution': 270,
                           'EPSG': 25831,
                           'variables_files': {
                               'altitude': 'pymica_tests/data/tifs/altitude.tif',
                               'd_coast': 'pymica_tests/data/tifs/d_coast.tif'}}}
        
        with open('pymica_tests/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()          
        
        id2d = PyMica('id2d', 'pymica_tests/data/config_test.json')
        field = id2d.interpolate(self.data)

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
                               'altitude': 'pymica_tests/data/tifs/altitude.tif',
                               'd_coast': 'pymica_tests/data/tifs/d_coast.tif'}}}

        with open('pymica_tests/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        id3d = PyMica('id3d', 'pymica_tests/data/config_test.json')
        field = id3d.interpolate(self.data)

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
                              'altitude': 'pymica_tests/data/tifs/altitude.tif'}}}

        with open('pymica_tests/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        mlr = PyMica('mlr', 'pymica_tests/data/config_test.json')
        field = mlr.interpolate(self.data)

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
                                   'altitude': 'pymica_tests/data/tifs/altitude.tif'}}}

        with open('pymica_tests/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()


        mlr_id2d = PyMica('mlr+id2d', 'pymica_tests/data/config_test.json')
        field = mlr_id2d.interpolate(self.data)

        self.assertEqual(field.shape, (1000, 1000))
        self.assertAlmostEqual(field[925, 74], 50.000, 2)
        self.assertAlmostEqual(field[555, 444], 20.000, 2)
        self.assertAlmostEqual(field[185, 814], 9.999, 2)

    def test_init_interpolate_mlr_id3d(self):

        config = {'mlr+id3d': {'id_power': 2.5,
                               'id_smoothing': 0.0,
                               'interpolation_bounds': [260000, 4480000,
                                                        530000, 4750000],
                               'resolution': 270,
                               'EPSG': 25831,
                               'variables_files': {
                                   'altitude': 'pymica_tests/data/tifs/altitude.tif'}}}

        with open('pymica_tests/data/config_test.json', 'w') as f:
            json.dump(config, f)
            f.close()

        mlr_id2d = PyMica('mlr+id3d', 'pymica_tests/data/config_test.json')
        field = mlr_id2d.interpolate(self.data)

        self.assertEqual(field.shape, (1000, 1000))
        self.assertAlmostEqual(field[925, 74], 50.000, 2)
        self.assertAlmostEqual(field[555, 444], 20.000, 2)
        self.assertAlmostEqual(field[185, 814], 9.999, 2)


    def test_interpolate_input_bad_keys(self):
        # Fem test per les lat
        data_dict = [{'id': 'C6', 'value': 6.4, 'altitude': 264,
                      'lon': 0.95172, 'lati': 41.6566,
                      'dist': 0.8583929293407604},
                     {'id': 'C7', 'value': 5.6, 'altitude': 427,
                      'lon': 1.16234, 'lat': 41.66695,
                      'dist': 0.8387222708681318}]

        with self.assertRaises(KeyError) as cm:
            inst = PyMica('id3d', 'pymica_tests/data/config_interpolate.json')
            inst.interpolate(data_dict)
        self.assertEqual('id, lat, lon, value keys must be included in the imput data',
                         cm.exception.args[0])


    def test_interpolate_input_altitude_missing(self):
        data_dict = [{'id': 'C6', 'value': 6.4, 'alti': 264, 'lon': 0.95172,
                      'lat': 41.6566, 'dist': 0.8583929293407604},
                     {'id': 'C7', 'value': 5.6, 'altitude': 427,
                      'lon': 1.16234, 'lat': 41.66695,
                      'dist': 0.8387222708681318}]
        
        with self.assertRaises(KeyError) as cm:
            inst = PyMica('id3d', 'pymica_tests/data/config_interpolate.json')
            inst.interpolate(data_dict)
        self.assertEqual('altitude must be included in the data file',
                         cm.exception.args[0])


    def test_interpolate_input_data_variable_missing(self):
        data_dict = [{'id': 'C6', 'value': 6.4, 'altitude': 264,
                      'lon': 0.95172, 'lat': 41.6566},
                     {'id': 'C7', 'value': 5.6, 'altitude': 427,
                      'lon': 1.16234, 'lat': 41.66695,
                      'd_coast': 0.8387222708681318}]


        with self.assertRaises(KeyError) as cm:
            inst = PyMica('mlr', 'pymica_tests/data/config_interpolate.json')
            inst.interpolate(data_dict)
        self.assertEqual('Some of the variables provided in the '
                         'variables_files dictionary missing in C6.',
                         cm.exception.args[0])

    @classmethod
    def tearDownClass(self):
        if exists('pymica_tests/data/config_test.json'):
            remove('pymica_tests/data/config_test.json')
        if exists('pymica_tests/data/config_interpolate.json'):
            remove('pymica_tests/data/config_interpolate.json')
        if exists('pymica_tests/data/tifs/altitude.tif'):
            remove('pymica_tests/data/tifs/altitude.tif')
        if exists('pymica_tests/data/tifs/d_coast.tif'):
            remove('pymica_tests/data/tifs/d_coast.tif')
        if exists('pymica_tests/data/tifs/d_coast_2.tif'):
            remove('pymica_tests/data/tifs/d_coast_2.tif')
        if exists('pymica_tests/data/init_data.json'):
            remove('pymica_tests/data/init_data.json')
        if exists('pymica_tests/data/sample_data_test_keys.json'):
            remove('pymica_tests/data/sample_data_test_keys.json')
        if exists('pymica_tests/data/tifs'):
            rmdir('pymica_tests/data/tifs')
