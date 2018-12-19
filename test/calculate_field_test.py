'''Testing calculate_field.py file
'''

import unittest

import numpy as np
from pymica.calculate_field import calculate_field


class TestCalculateField(unittest.TestCase):
    def test_calculate_field(self):
        data = [{'id': 'AA', 'hr': 0, 'temp': 9, 'dist': 4, 'altitude': 0,
                 'x': 0, 'y': 0, 'z': 1},
                {'id': 'BB', 'hr': 0.5, 'temp': 7.5, 'dist': 3,
                 'altitude': 0.5, 'x': 0, 'y': 1, 'z': 0},
                {'id': 'CC', 'hr': 1, 'temp': 6, 'dist': 2, 'altitude': 1,
                 'x': 0, 'y': 2, 'z': 0},
                {'id': 'DD', 'hr': 1, 'temp': 5, 'dist': 1, 'altitude': 2,
                 'x': 1, 'y': 0, 'z': 0},
                {'id': 'EE', 'hr': 1, 'temp': 5, 'dist': 0.5, 'altitude': 3,
                 'x': 1, 'y': 2, 'z': 0},
                {'id': 'FF', 'hr': 1, 'temp': 5, 'dist': 0, 'altitude': 4,
                 'x': 2, 'y': 2, 'z': 0}
                ]

        size = [1000, 1000]
        alt_data = np.ones(size)
        alt_data[2][2] = 12

        dist_data = np.ones(size)
        geotransform = [0, 0.002002, 0, 2, 0, -0.002002]
        # Simplest input
        calculate_field(data, [alt_data, dist_data], geotransform)

        # Passing sigma
        # calculate_field(data, sigma=1.2)
