'''Tests for pymica.multiregression.py
'''
import unittest

from pymica.methods.multiregression import MultiRegression, MultiRegressionSigma


class TestMultiRegressionSigma(unittest.TestCase):
    def test_regression_ideal_data(self):

        data = [{'id': 'AA', 'hr': 0, 'temp': 0, 'dist': 0, 'altitude': 0},
                {'id': 'BB', 'hr': 0.5, 'temp': 0.5, 'dist': 0,
                 'altitude': 0.5},
                {'id': 'CC', 'hr': 1, 'temp': 1, 'dist': 0, 'altitude': 1}
                ]
        inst_regression = MultiRegressionSigma(data, sigma_limit=1.5)
        # print(vars(inst_regression))
        coefs = inst_regression.get_coefs()

        self.assertEqual(len(coefs), 2)
        self.assertEqual(len(coefs[0]), 1)
        self.assertAlmostEqual(coefs[0][0], 1)
        self.assertAlmostEqual(coefs[1], 0)
        self.assertAlmostEqual(inst_regression.get_score(), 1)

        data = []
        i = 0
        for altitude in range(0, 2):
            for hr in range(0, 2):
                for dist in range(0, 2):
                    i += 1
                    data.append({'id': 'key_' + str(i),
                                 'hr': hr, 'dist': dist,
                                 'altitude': altitude,
                                 'temp': 1 + hr + 2 * dist + 3 * altitude
                                 })

        inst_regression = MultiRegression(data,
                                          x_vars=['altitude', 'dist', 'hr'])
        # print(vars(inst_regression))
        coefs1 = inst_regression.get_coefs()

        data.append({'id': 'BAD', 'hr': 0, 'temp': 0, 'dist': 0,
                     'altitude': 0})

        inst_regression = MultiRegressionSigma(data, sigma_limit=1.5,
                                               x_vars=['altitude',
                                                       'dist', 'hr'])
        # print(vars(inst_regression))
        coefs2 = inst_regression.get_coefs()
        # The MultiRegressionSigma class must have filtered the bad data
        self.assertEqual(len(coefs2[0]), len(coefs1[0]))
        self.assertAlmostEqual(coefs2[0][0], coefs1[0][0])
        self.assertAlmostEqual(coefs2[1], coefs1[1])
        # The MultiRegressionSigma must have the result as if the bad element
        # didn't exist.
        self.assertEqual(len(coefs2), 2)
        self.assertEqual(len(coefs2[0]), 3)
        self.assertAlmostEqual(coefs2[0][0], 3)
        self.assertAlmostEqual(coefs2[1], 1)
        self.assertAlmostEqual(inst_regression.get_score(), 1)
        # The Multiregression sigma must return the residuals for all the data,
        # not only the one inside the sigma values
        self.assertAlmostEqual(len(data), len(inst_regression.get_residuals()))

        inst_regression.predict_points([{'id': 'AA', 'hr': 0, 'temp': 0,
                                         'dist': 0, 'altitude': 0}])
        inst_regression.regr.predict([[0, 0, 0]])
