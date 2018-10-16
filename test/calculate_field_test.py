'''Testing calculate_field.py file
'''

import unittest
from pymica.calculate_field import calculate_field


class TestCalculateField(unittest.TestCase):
    def test_calculate_field(self):
        data = [{'id': 'AA', 'hr': 0, 'temp': 9, 'dist': 4, 'altitude': 0},
                {'id': 'BB', 'hr': 0.5, 'temp': 7.5, 'dist': 3,
                 'altitude': 0.5},
                {'id': 'CC', 'hr': 1, 'temp': 6, 'dist': 2, 'altitude': 1},
                {'id': 'DD', 'hr': 1, 'temp': 5, 'dist': 1, 'altitude': 2},
                {'id': 'EE', 'hr': 1, 'temp': 5, 'dist': 0.5, 'altitude': 3},
                {'id': 'FF', 'hr': 1, 'temp': 5, 'dist': 0, 'altitude': 4}
                ]
        
        # Simplest input
        calculate_field(data)

        # Passing sigma
        # calculate_field(data, sigma=1.2)
