import unittest
from pymica.apply_regression import apply_regression
from pymica.multiregression import MultiRegressionSigma
import numpy as np
from datetime import datetime


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

        inst = MultiRegressionSigma(data, y_var='temp', x_vars=['altitude', 'dist'])
        coefs = inst.get_coefs()

        in_data = alt_data.reshape([1, 5, 5])

        result = apply_regression(coefs, in_data)

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
        coefs = inst.get_coefs()
        in_data = np.array([alt_data, dist_data])

        result = apply_regression(coefs, in_data)

        self.assertEqual(result.shape[0], size[1])
        self.assertEqual(result.shape[1], size[0])
        self.assertAlmostEqual(result[2][2], 39) # t = 1 + 2*dist + 3*alt

        size = [1000, 1000]
        alt_data = np.ones(size)
        alt_data[2][2] = 12

        dist_data = np.ones(size)
        in_data = np.array([alt_data, dist_data])
        now = datetime.utcnow()
        result = apply_regression(coefs, in_data)

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
        coefs = inst.get_coefs()

        in_data = np.ones([5, 5])

        with self.assertRaises(ValueError) as cm:
            apply_regression(coefs, in_data)
        self.assertEqual(
            "raster_data must be a 3 dimensional array",
            str(cm.exception))

        in_data = [5, 5]

        with self.assertRaises(ValueError) as cm:
            apply_regression(coefs, in_data)
        self.assertEqual(
            "raster_data must be a 3 dimensional array",
            str(cm.exception))
