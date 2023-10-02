'''Testing pymica.apply_regression.py
'''
import json
import unittest
from datetime import datetime

import numpy as np


from pymica.methods.clustered_regression import ClusteredRegression
from pymica.methods.multiregression import MultiRegressionSigma


class ApplyRegressionTest(unittest.TestCase):
    def test_apply_regression(self):
        data = [{'id': 'AA', 'hr': 0, 'temp': 0, 'dist': 0, 'altitude': 0},
                {'id': 'BB', 'hr': 0.5, 'temp': 0.5, 'dist': 0,
                 'altitude': 0.5},
                {'id': 'CC', 'hr': 1, 'temp': 1, 'dist': 0, 'altitude': 1}
                ]
        size = [5, 5]

        alt_data = np.ones(size)
        alt_data[2][2] = 12

        dist_data = np.ones(size)

        inst = MultiRegressionSigma(
            data, y_var='temp', x_vars=['altitude', 'dist'])

        in_data = alt_data.reshape([1, 5, 5])

        result = inst.apply_regression(in_data, ['altitude', 'dist'])

        self.assertEqual(result.shape[0], size[1])
        self.assertEqual(result.shape[1], size[0])
        self.assertAlmostEqual(result[2][2], 12)

        data = [{'id': 'AA', 'hr': 0, 'temp': 1, 'dist': 0, 'altitude': 0},
                {'id': 'BB', 'hr': 0.5, 'temp': 4.5, 'dist': 1,
                 'altitude': 0.5},
                {'id': 'CC', 'hr': 1, 'temp': 6, 'dist': 1, 'altitude': 1},
                {'id': 'DD', 'hr': 1, 'temp': 7.5, 'dist': 1, 'altitude': 1.5},
                {'id': 'EE', 'hr': 1, 'temp': 8, 'dist': 2, 'altitude': 1}
                ]

        inst = MultiRegressionSigma(data, y_var='temp',
                                    x_vars=['altitude', 'dist'])
        in_data = np.array([alt_data, dist_data])

        result = inst.apply_regression(in_data, ['altitude', 'dist'])

        self.assertEqual(result.shape[0], size[1])
        self.assertEqual(result.shape[1], size[0])
        self.assertAlmostEqual(result[2][2], 39)  # t = 1 + 2*dist + 3*alt

        size = [1000, 1000]
        alt_data = np.ones(size)
        alt_data[2][2] = 12

        dist_data = np.ones(size)
        in_data = np.array([alt_data, dist_data])
        now = datetime.utcnow()
        result = inst.apply_regression(in_data, ['altitude', 'dist'])

        spent_time = datetime.utcnow() - now
        print("Time for 1000x1000:", spent_time.total_seconds(), "s")

    def test_apply_regression_errors(self):
        data = [{'id': 'AA', 'hr': 0, 'temp': 0, 'dist': 0, 'altitude': 0},
                {'id': 'BB', 'hr': 0.5, 'temp': 0.5, 'dist': 0,
                 'altitude': 0.5},
                {'id': 'CC', 'hr': 1, 'temp': 1, 'dist': 0, 'altitude': 1}
                ]
        inst = MultiRegressionSigma(data, y_var='temp',
                                    x_vars=['altitude', 'dist'])

        in_data = np.ones([5, 5])

        with self.assertRaises(ValueError) as cm:
            inst.apply_regression(in_data, ['altitude', 'dist'])
        self.assertEqual(
            "raster_data must be a 3 dimensional array",
            str(cm.exception))

        in_data = [5, 5]

        with self.assertRaises(ValueError) as cm:
            inst.apply_regression(in_data, ['altitude', 'dist'])
        self.assertEqual(
            "raster_data must be a 3 dimensional array",
            str(cm.exception))

    def test_apply_clustered_regression(self):
        f_p = open("pymica_tests/data/sample_data.json")
        data = json.load(f_p)
        f_p.close()
        inst = ClusteredRegression(data,
                                   ["pymica_tests/data/clusters.json"])

        size = [1000, 1000]
        alt_data = np.ones(size)
        alt_data[2][2] = 12

        dist_data = np.ones(size)

        in_data = np.array([alt_data, dist_data])

        # An arbitrary mask to check the effect
        mask = np.zeros([3, 1000, 1000])
        for i in range(3):
            for j in range(500):
                mask[i][i*250 + j][:] = 1 - j/550

        result = inst.apply_clustered_regression(
                      in_data, ['altitude', 'dist'], mask)
        self.assertEqual(list(result.shape), size)
