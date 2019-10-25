'''Tests for inverse_distance.py
'''
import unittest
from datetime import datetime

from numpy import array

from interpolation.inverse_distance import \
    inverse_distance  # pylint: disable=E0611


class TestInverseDistance(unittest.TestCase):
    def test_inverse_distance(self):

        residues = {'AA': {'value': 0, 'y': 0, 'x': 0},
                    'BB': {'value': 1, 'y': 1, 'x': 1},
                    'CC': {'value': 2, 'y': 2, 'x': 2}}
        geotransform = [0, 0.5, 0, 2, 0, -0.5]
        size = [5, 5]

        result = inverse_distance(residues, size, geotransform)

        self.assertIsInstance(result, type(array((0, 0))))

        self.assertEqual(result[0][4], 2)
        self.assertEqual(result[4][0], 0)
        self.assertEqual(result[2][2], 1)

        now = datetime.utcnow()
        geotransform = [0, 0.002002, 0, 2, 0, -0.002002]
        size = [1000, 1000]

        result = inverse_distance(residues, size, geotransform)

        spent_time = datetime.utcnow() - now
        print("test_inverse_distance:")
        print("Time for 1000x1000:", spent_time.total_seconds(), "s")
        self.assertLess(spent_time.total_seconds(), 2.0)

        self.assertAlmostEqual(result[0][size[1]-1], 2)
        self.assertAlmostEqual(result[size[0]-1][0], 0)
        self.assertAlmostEqual(result[500][500], 1)
