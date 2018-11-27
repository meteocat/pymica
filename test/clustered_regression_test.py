'''Testing pymica.clustered_regression.py
'''

import unittest
import json
from pymica.clustered_regression import ClusteredRegression


class TestClusteredRegression(unittest.TestCase):
    def test_regression_ideal_data(self):
        f_p = open("./test/data/sample_data.json")
        data = json.load(f_p)
        f_p.close()
        inst = ClusteredRegression(data,
                                   ["./test/data/clusters.json"])
        self.assertEqual(len(inst.final_data), 3)
        self.assertAlmostEqual(inst.get_mse(), 2.1828, 3)

    def test_predict_points(self):
        f_p = open("./test/data/sample_data.json")
        data = json.load(f_p)
        f_p.close()
        inst = ClusteredRegression(data,
                                   ["./test/data/clusters.json"])
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
