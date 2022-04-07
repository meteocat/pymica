'''Tests for pymica.pymica.py
'''
import unittest
import unittest.mock
from tempfile import gettempdir

import numpy as np
from osgeo import gdal, osr
from pymica.pymica2 import PyMica
import io

import json


class TestPyMica(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = {"id2d": {"id_power": 2.5,
                               "id_smoothing": 0.0},
                      
                      "id3d": {"id_power":2.5,
                              "id_smoothing":0.0,
                              "id_penalization":30.0},
                  
                      "mlr": {"clusters": "None",
                              "variables_files": {"altitude": "",
                                              "d_coast": ""}},
  
                      "mlr+id2d": {"id_power":2.5,
                                  "id_smoothing":0.0,
                                  "clusters":"None",
                                  "variables_files": {"altitud": "",
                                                      "d_coast": ""}},
                      "mlr+id3d": {"variables_files": {"altitud": "",
                                                      "d_coast": ""}}}

    def test_init_config_not_found(self):
        with self.assertRaises(FileNotFoundError) as cm:
            PyMica(methodology='id3d', conf='aaaa.json')
        self.assertEqual('Wrong configuration file path.', str(cm.exception))

    def test_init_config_json_error(self):
        with self.assertRaises(json.decoder.JSONDecodeError) as cm:
            PyMica(methodology='id3d', conf='./test/data/config_error.json')
        self.assertEqual('Expecting property name enclosed in double quotes: '
                         'line 2 column 5 (char 6)',
                         str(cm.exception))

    def test_config_return(self):
        ins=PyMica(methodology='id3d', conf='./test/data/config_init.json')
        self.assertEqual(len(ins.config.keys()), 5) 

    
    def test_init_methodology(self):
        with self.assertRaises(ValueError) as cm:
            PyMica(methodology='id3', conf='./test/data/config_init.json')
        self.assertEqual('Methodology must be \"id2d\", \"id3d\", '
                             '\"mlr+id2d\", \"mlr+id3d\" or \"mlr\"', str(cm.exception))


    def test_values_config(self):
        ins=PyMica(methodology='id3d', conf='./test/data/config_init.json')
        self.assertEqual(ins.power,2.5)
        self.assertEqual(ins.penalization,30)
        self.assertEqual(ins.smoothing,0)

        with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            PyMica(methodology='id3d', conf='./test/data/config_init_error_parameters.json')
        self.assertEqual(mock_stdout.getvalue().strip(), 'id_power not in the configuration dictionary. ' +
                                                 'id_power set to default value of 2.5.')

        with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            PyMica(methodology='id2d', conf='./test/data/config_init_error_parameters.json')
        self.assertEqual(mock_stdout.getvalue().strip(), 'id_smoothing not in the configuration dictionary. ' +
                      'id_smoothing set to default value of 0.0.')

        with unittest.mock.patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            PyMica(methodology='mlr+id3d', conf='./test/data/config_init_error_parameters.json')
        self.assertEqual(mock_stdout.getvalue().strip(), 'id_penalization not in the configuration dictionary. ' +
                          'id_penalization set to default value of 30.')
        
        with self.assertRaises(KeyError) as cm:
            method='mlr+id2d'
            PyMica(methodology=method, conf='./test/data/config_init_error_parameters.json')
        self.assertEqual('\'variables_files must be included in the configuration file if ' + method + ' is selected.\'', str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            method='mlr'
            PyMica(methodology=method, conf='./test/data/config_init_error_parameters.json')
        self.assertEqual('variables_files dictionary must have at ' +
                        'least one key including a variable file ' +
                        'path containing a 2D predictor field.', str(cm.exception))
        


    '''
    def test_init(self):
        inst = PyMica("./test/data/sample_data.json", self.variables_file,
                      self.clusters)
        self.assertEqual(inst.result.shape, (1000, 1000))

        inst.save_file(gettempdir() + "/out.tiff")

        # Test passing multiple variable files instead
        # of one with all the layers
        PyMica("./test/data/sample_data.json", [self.variables_file],
               self.clusters)

        # No clusters
        PyMica("./test/data/sample_data.json", [self.variables_file])

        # Multiple clusters
        clusters2 = {'clusters_files': ["./test/data/clusters.json",
                                        "./test/data/clusters5.json"],
                     'mask_files': [self.mask_file, self.mask5_file]}
        PyMica("./test/data/sample_data.json", [self.variables_file],
               clusters2)

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
    '''