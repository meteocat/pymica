"""Tests for MLR sigma"""

import unittest
from datetime import datetime

import numpy as np

from pymica.methods.multiregression import MultiRegression, MultiRegressionSigma


class TestMultiRegressionSigma(unittest.TestCase):
    """Test MultiRegressionSigma class"""

    def test_regression_ideal_data(self):
        """Test MLR sigma with sample data"""
        data = [
            {"id": "AA", "hr": 0, "value": 0, "dist": 0, "altitude": 0},
            {"id": "BB", "hr": 0.5, "value": 0.5, "dist": 0, "altitude": 0.5},
            {"id": "CC", "hr": 1, "value": 1, "dist": 0, "altitude": 1},
        ]
        inst_regression = MultiRegressionSigma(
            data, ("altitude", "dist"), sigma_limit=1.5
        )

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
                    data.append(
                        {
                            "id": "key_" + str(i),
                            "hr": hr,
                            "dist": dist,
                            "altitude": altitude,
                            "value": 1 + hr + 2 * dist + 3 * altitude,
                        }
                    )

        inst_regression = MultiRegression(data, x_vars=["altitude", "dist", "hr"])

        coefs1 = inst_regression.get_coefs()

        data.append({"id": "BAD", "hr": 0, "value": 0, "dist": 0, "altitude": 0})

        inst_regression = MultiRegressionSigma(
            data, ["altitude", "dist", "hr"], sigma_limit=1.5
        )

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

        inst_regression.predict_points(
            [{"id": "AA", "hr": 0, "value": 0, "dist": 0, "altitude": 0}]
        )
        inst_regression.regr.predict([[0, 0, 0]])

    def test_apply_regression(self):
        """Test apply MLR regression"""
        data = [
            {"id": "AA", "hr": 0, "value": 0, "dist": 0, "altitude": 0},
            {"id": "BB", "hr": 0.5, "value": 0.5, "dist": 0, "altitude": 0.5},
            {"id": "CC", "hr": 1, "value": 1, "dist": 0, "altitude": 1},
        ]
        size = [5, 5]

        alt_data = np.ones(size)
        alt_data[2][2] = 12

        dist_data = np.ones(size)

        inst = MultiRegressionSigma(data, x_vars=["altitude", "dist"])

        in_data = alt_data.reshape([1, 5, 5])

        result = inst.apply_regression(in_data, ["altitude", "dist"])

        self.assertEqual(result.shape[0], size[1])
        self.assertEqual(result.shape[1], size[0])
        self.assertAlmostEqual(result[2][2], 12)

        data = [
            {"id": "AA", "hr": 0, "value": 1, "dist": 0, "altitude": 0},
            {"id": "BB", "hr": 0.5, "value": 4.5, "dist": 1, "altitude": 0.5},
            {"id": "CC", "hr": 1, "value": 6, "dist": 1, "altitude": 1},
            {"id": "DD", "hr": 1, "value": 7.5, "dist": 1, "altitude": 1.5},
            {"id": "EE", "hr": 1, "value": 8, "dist": 2, "altitude": 1},
        ]

        inst = MultiRegressionSigma(data, x_vars=["altitude", "dist"])
        in_data = np.array([alt_data, dist_data])

        result = inst.apply_regression(in_data, ["altitude", "dist"])

        self.assertEqual(result.shape[0], size[1])
        self.assertEqual(result.shape[1], size[0])
        self.assertAlmostEqual(result[2][2], 39)  # t = 1 + 2*dist + 3*alt

        size = [1000, 1000]
        alt_data = np.ones(size)
        alt_data[2][2] = 12

        dist_data = np.ones(size)
        in_data = np.array([alt_data, dist_data])
        now = datetime.utcnow()
        result = inst.apply_regression(in_data, ["altitude", "dist"])

        spent_time = datetime.utcnow() - now
        print("Time for 1000x1000:", spent_time.total_seconds(), "s")

    def test_apply_regression_errors(self):
        """Test error raises from apply regression"""
        data = [
            {"id": "AA", "hr": 0, "value": 0, "dist": 0, "altitude": 0},
            {"id": "BB", "hr": 0.5, "value": 0.5, "dist": 0, "altitude": 0.5},
            {"id": "CC", "hr": 1, "value": 1, "dist": 0, "altitude": 1},
        ]
        inst = MultiRegressionSigma(data, x_vars=["altitude", "dist"])

        in_data = np.ones([5, 5])

        with self.assertRaises(ValueError) as cm:
            inst.apply_regression(in_data, ["altitude", "dist"])
        self.assertEqual(
            "`raster_data` must be a 3 dimensional array", str(cm.exception)
        )

        in_data = [5, 5]

        with self.assertRaises(ValueError) as cm:
            inst.apply_regression(in_data, ["altitude", "dist"])
        self.assertEqual(
            "`raster_data` must be a 3 dimensional array", str(cm.exception)
        )
