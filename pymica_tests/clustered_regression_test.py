'''Testing pymica.clustered_regression.py
'''
import json
import unittest

from pymica.methods.clustered_regression import ClusteredRegression


class TestClusteredRegression(unittest.TestCase):
    def test_regression_ideal_data(self):
        f_p = open("pymica_tests/data/sample_data.json")
        data = json.load(f_p)
        f_p.close()
        inst = ClusteredRegression(data,
                                   ["pymica_tests/data/clusters.json"])
        self.assertEqual(len(inst.final_data), 3)
        self.assertAlmostEqual(inst.mse, 2.1828, 3)

        with self.assertRaises(FileNotFoundError) as cm:
            ClusteredRegression(data, ["BadFile"])
        self.assertEqual(
            "File not found, or not ogr compatible BadFile",
            str(cm.exception))

        with self.assertRaises(ValueError) as cm:
            ClusteredRegression(data, 23)
        self.assertEqual(
            "cluster file must be a list",
            str(cm.exception))

    def test_get_residuals(self):
        f_p = open("pymica_tests/data/sample_data.json")
        data = json.load(f_p)
        f_p.close()
        inst = ClusteredRegression(data,
                                   ["pymica_tests/data/clusters.json"])
        result = inst.get_residuals()
        self.assertEqual(len(data), len(result))
        for point in data:
            self.assertTrue(point['id'] in result)

    def test_predict_points(self):
        f_p = open("pymica_tests/data/sample_data.json")
        data = json.load(f_p)
        f_p.close()
        inst = ClusteredRegression(data,
                                   ["pymica_tests/data/clusters.json"])
        sample_data = [{"id": "C6", "temp": 6.4, "altitude": 264,
                        "lon": 0.95172, "lat": 41.6566,
                        "dist": 0.8583929293407604},
                       {"id": "C7", "temp": 5.6, "altitude": 427,
                        "lon": 1.16234, "lat": 41.66695,
                        "dist": 0.8387222708681318},
                       {"id": "UQ", "temp": 10, "altitude": 460,
                        "lon": 2.44532, "lat": 41.61991,
                        "dist": 0.24251682692034138}]
        result = inst.predict_points(sample_data)
        self.assertEqual(len(result), 3)
        # Order is maintained
        self.assertEqual(result[1], inst.predict_points([sample_data[1]])[0])
