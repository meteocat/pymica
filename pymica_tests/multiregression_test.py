'''Tests for pymica.multiregression.py
'''
import unittest

from pymica.methods.multiregression import MultiRegression


class TestMultiRegression(unittest.TestCase):
    def test_regression_ideal_data(self):

        # Correlation with altitude and coef = 1
        data = [{'id': 'AA', 'hr': 0, 'temp': 0, 'dist': 0, 'altitude': 0},
                {'id': 'BB', 'hr': 0.5, 'temp': 0.5, 'dist': 0,
                 'altitude': 0.5},
                {'id': 'CC', 'hr': 1, 'temp': 1, 'dist': 0, 'altitude': 1}
                ]
        inst_regression = MultiRegression(data)

        coefs = inst_regression.get_coefs()

        self.assertEqual(len(coefs), 2)
        self.assertEqual(len(coefs[0]), 1)
        self.assertAlmostEqual(coefs[0][0], 1)
        self.assertAlmostEqual(coefs[1], 0)
        self.assertAlmostEqual(inst_regression.get_score(), 1)

        # Correlation with two variables & score 1 y = 1 + a + 2b
        data = [{'id': 'AA', 'hr': 0, 'temp': 9, 'dist': 4, 'altitude': 0},
                {'id': 'BB', 'hr': 0.5, 'temp': 7.5, 'dist': 3,
                 'altitude': 0.5},
                {'id': 'CC', 'hr': 1, 'temp': 6, 'dist': 2, 'altitude': 1},
                {'id': 'DD', 'hr': 1, 'temp': 5, 'dist': 1, 'altitude': 2},
                {'id': 'EE', 'hr': 1, 'temp': 5, 'dist': 0.5, 'altitude': 3},
                {'id': 'FF', 'hr': 1, 'temp': 5, 'dist': 0, 'altitude': 4}
                ]

        inst_regression = MultiRegression(data)

        coefs = inst_regression.get_coefs()
        self.assertEqual(len(coefs), 2)
        self.assertEqual(len(coefs[0]), 2)
        self.assertAlmostEqual(coefs[0][0], 2)
        self.assertAlmostEqual(coefs[0][1], 1)
        self.assertAlmostEqual(coefs[1], 1)
        self.assertAlmostEqual(inst_regression.get_score(), 1)

        # Correlation with three variables & score 1 y = 1 + a + 2b + 3c
        data = [{'id': 'AA', 'hr': 0, 'temp': 9, 'dist': 4, 'altitude': 0},
                {'id': 'BB', 'hr': 0.5, 'temp': 9, 'dist': 3, 'altitude': 0.5},
                {'id': 'CC', 'hr': 1, 'temp': 9, 'dist': 2, 'altitude': 1},
                {'id': 'DD', 'hr': 1, 'temp': 8, 'dist': 1, 'altitude': 2},
                {'id': 'EE', 'hr': 4, 'temp': 17, 'dist': 0.5, 'altitude': 3},
                {'id': 'FF', 'hr': 2, 'temp': 11, 'dist': 0, 'altitude': 4},
                {'id': 'GG', 'hr': 2, 'temp': 12, 'dist': 0, 'altitude': 5},
                {'id': 'HH', 'hr': 2, 'temp': 14, 'dist': 1, 'altitude': 5}
                ]
        inst_regression = MultiRegression(data, y_var='temp',
                                          x_vars=['altitude', 'dist', 'hr'])

        coefs = inst_regression.get_coefs()

        self.assertEqual(len(coefs), 2)
        self.assertEqual(len(coefs[0]), 3)
        self.assertAlmostEqual(coefs[0][0], 3)
        self.assertAlmostEqual(coefs[0][1], 2)
        self.assertAlmostEqual(coefs[0][2], 1)
        self.assertAlmostEqual(coefs[1], 1)
        self.assertAlmostEqual(inst_regression.get_score(), 1)

        # Let's worsen the correlation
        data[0]['temp'] = 0
        inst_regression = MultiRegression(data, y_var='temp',
                                          x_vars=['altitude', 'dist', 'hr'])

        self.assertTrue(inst_regression.get_score() < 1)

    def test_threshold(self):
        data = [{'id': 'AA', 'hr': 0, 'temp': 0.3, 'dist': 0, 'altitude': 0},
                {'id': 'BB', 'hr': 0.5, 'temp': 0.4, 'dist': 0.1,
                 'altitude': 0.5},
                {'id': 'CC', 'hr': 1, 'temp': 1, 'dist': 0.4, 'altitude': 1}
                ]
        inst_regression = MultiRegression(data, score_threshold=0.000000001)
        self.assertEqual(len(set(inst_regression.used_vars)
                         .intersection(['dist', 'altitude'])), 2)
        inst_regression = MultiRegression(data, score_threshold=0.5)
        self.assertEqual(len(set(inst_regression.used_vars)
                         .intersection(['dist', 'altitude'])), 1)

    def test_change_input_values(self):
        data = [{'name': 'AA', 'hr': 0, 'temp': 0, 'dist': 0, 'altitude': 0},
                {'name': 'BB', 'hr': 0.5, 'temp': 0.5, 'dist': 0,
                 'altitude': 0.5},
                {'name': 'CC', 'hr': 1, 'temp': 1, 'dist': 0, 'altitude': 1}
                ]
        inst_regression = MultiRegression(data, id_key='name')

        residuals = inst_regression.get_residuals()
        self.assertTrue('BB' in residuals)

        data = [{'id': 'AA', 'hr': 0, 'temp': 0, 'dist': 0, 'altitude': 0},
                {'id': 'BB', 'hr': 0.5, 'temp': 0.5, 'dist': 0,
                 'altitude': 0.5},
                {'id': 'CC', 'hr': 1, 'temp': 1, 'dist': 0, 'altitude': 1}
                ]
        inst_regression = MultiRegression(data, y_var='hr')

        coefs = inst_regression.get_coefs()

        self.assertEqual(len(coefs), 2)
        self.assertEqual(len(coefs[0]), 1)
        self.assertAlmostEqual(coefs[0][0], 1)

        data = [{'id': 'AA', 'hr': 0, 'temp': 0, 'dist': 0, 'hhh': 0},
                {'id': 'BB', 'hr': 0.5, 'temp': 0.5, 'dist': 0,
                 'hhh': 0.5},
                {'id': 'CC', 'hr': 1, 'temp': 1, 'dist': 0, 'hhh': 1}
                ]
        inst_regression = MultiRegression(data, x_vars=['dist', 'hhh'])

        coefs = inst_regression.get_coefs()

        self.assertEqual(len(coefs), 2)
        self.assertEqual(len(coefs[0]), 1)
        self.assertAlmostEqual(coefs[0][0], 1)

    def test_get_residuals(self):
        data = [{'id': 'AA', 'hr': 1, 'temp': 0, 'dist': 0, 'altitude': 0},
                {'id': 'BB', 'hr': 2, 'temp': 0.5, 'dist': 0, 'altitude': 0.5},
                {'id': 'CC', 'hr': 3, 'temp': 1, 'dist': 0, 'altitude': 1}
                ]

        inst_regression = MultiRegression(data)
        residuals = inst_regression.get_residuals()

        self.assertTrue(isinstance(residuals, dict))
        for key in residuals.keys():
            self.assertAlmostEqual(residuals[key], 0)

        data = [{'id': 'AA', 'hr': 0, 'temp': 9, 'dist': 4, 'altitude': 0},
                {'id': 'BB', 'hr': 0.5, 'temp': 7.5, 'dist': 3,
                 'altitude': 0.5},
                {'id': 'CC', 'hr': 1, 'temp': 6, 'dist': 2, 'altitude': 1},
                {'id': 'DD', 'hr': 1, 'temp': 5, 'dist': 1, 'altitude': 2},
                {'id': 'EE', 'hr': 1, 'temp': 5, 'dist': 0.5, 'altitude': 3},
                {'id': 'FF', 'hr': 1, 'temp': 5, 'dist': 0, 'altitude': 4}
                ]
        inst_regression = MultiRegression(data)
        residuals = inst_regression.get_residuals()

        self.assertTrue(isinstance(residuals, dict))
        for key in residuals.keys():
            self.assertAlmostEqual(residuals[key], 0)

        # Make the correlation not be perfect so some residuals exist
        data = [{'id': 'AA', 'hr': 0, 'temp': 0, 'dist': 4, 'altitude': 0},
                {'id': 'BB', 'hr': 0.5, 'temp': 9, 'dist': 3, 'altitude': 0.5},
                {'id': 'CC', 'hr': 1, 'temp': 9, 'dist': 2, 'altitude': 1},
                {'id': 'DD', 'hr': 1, 'temp': 8, 'dist': 1, 'altitude': 2},
                {'id': 'EE', 'hr': 4, 'temp': 17, 'dist': 0.5, 'altitude': 3},
                {'id': 'FF', 'hr': 2, 'temp': 11, 'dist': 0, 'altitude': 4},
                {'id': 'GG', 'hr': 2, 'temp': 12, 'dist': 0, 'altitude': 5},
                {'id': 'HH', 'hr': 2, 'temp': 14, 'dist': 1, 'altitude': 5}
                ]
        inst_regression = MultiRegression(data)
        residuals = inst_regression.get_residuals()

        self.assertTrue(isinstance(residuals, dict))
        for key in residuals.keys():
            self.assertTrue(abs(residuals[key]) > 0)

    def test_predict_point(self):
        data = [{'id': 'AA', 'hr': 1, 'temp': 0, 'dist': 0, 'altitude': 0},
                {'id': 'BB', 'hr': 2, 'temp': 0.5, 'dist': 0, 'altitude': 0.5},
                {'id': 'CC', 'hr': 3, 'temp': 1, 'dist': 0, 'altitude': 1}
                ]

        inst_regression = MultiRegression(data)

        self.assertAlmostEqual(inst_regression.predict_point(
                                {'dist': 11, 'altitude': 22}), 22)

        # Three variable correlation & score 1 y = 1 + a + 2b + 3c
        data = [{'id': 'AA', 'hr': 0, 'temp': 9, 'dist': 4, 'altitude': 0},
                {'id': 'BB', 'hr': 0.5, 'temp': 9, 'dist': 3, 'altitude': 0.5},
                {'id': 'CC', 'hr': 1, 'temp': 9, 'dist': 2, 'altitude': 1},
                {'id': 'DD', 'hr': 1, 'temp': 8, 'dist': 1, 'altitude': 2},
                {'id': 'EE', 'hr': 4, 'temp': 17, 'dist': 0.5, 'altitude': 3},
                {'id': 'FF', 'hr': 2, 'temp': 11, 'dist': 0, 'altitude': 4},
                {'id': 'GG', 'hr': 2, 'temp': 12, 'dist': 0, 'altitude': 5},
                {'id': 'HH', 'hr': 2, 'temp': 14, 'dist': 1, 'altitude': 5}
                ]

        inst_regression = MultiRegression(data, y_var='temp',
                                          x_vars=['altitude', 'dist', 'hr'])
        self.assertAlmostEqual(
            inst_regression.predict_point(
                {'dist': 11, 'altitude': 22, 'hr': 1}), 48)

    def test_predict_points(self):
        data = [{'id': 'AA', 'hr': 1, 'temp': 0, 'dist': 0, 'altitude': 0},
                {'id': 'BB', 'hr': 2, 'temp': 0.5, 'dist': 0, 'altitude': 0.5},
                {'id': 'CC', 'hr': 3, 'temp': 1, 'dist': 0, 'altitude': 1}
                ]

        inst_regression = MultiRegression(data)
        results = inst_regression.predict_points(
            [{'dist': 11, 'altitude': 22}, {'dist': 11, 'altitude': 23}])

        self.assertAlmostEqual(results[0], 22)
        self.assertAlmostEqual(results[1], 23)

    def test_mae_mse(self):
        data = [{'id': 'AA', 'hr': 1, 'temp': 0, 'dist': 0, 'altitude': 0},
                {'id': 'BB', 'hr': 2, 'temp': 0.5, 'dist': 0, 'altitude': 0.5},
                {'id': 'CC', 'hr': 3, 'temp': 1, 'dist': 0, 'altitude': 1}
                ]

        inst_regression = MultiRegression(data)
        self.assertAlmostEqual(inst_regression.get_mae(), 0)
        self.assertAlmostEqual(inst_regression.get_mse(), 0)


if __name__ == '__main__':
    unittest.main()
