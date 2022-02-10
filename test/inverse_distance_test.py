'''Tests for inverse_distance.py
'''
import unittest
from datetime import datetime

from numpy import array

from interpolation.inverse_distance import \
    inverse_distance  # pylint: disable=E0611


class TestInverseDistance(unittest.TestCase):

    residues = {'AA': {'value': 0, 'y': 0, 'x': 0},
                'BB': {'value': 1, 'y': 1, 'x': 1},
                'CC': {'value': 2, 'y': 2, 'x': 2}}
    geotransform = [0, 0.5, 0, 2, 0, -0.5]
    size = [5, 5]

    def test_inverse_distance(self):
        result = inverse_distance(self.residues, self.size, self.geotransform)

        self.assertIsInstance(result, type(array((0, 0))))

        self.assertEqual(result[0][4], 2)
        self.assertEqual(result[4][0], 0)
        self.assertEqual(result[2][2], 1)

    def test_inverse_distance_power(self):
        result = inverse_distance(self.residues, self.size, self.geotransform,
                                  power=4)
        self.assertIsInstance(result, type(array((0, 0))))

        self.assertAlmostEqual(result[1][0], 0.8407, 3)
        self.assertAlmostEqual(result[3][4], 1.1592, 3)
        self.assertEqual(result[4][0], 0)
        self.assertEqual(result[2][2], 1)

    def test_inverse_distance_smoothing(self):
        result = inverse_distance(self.residues, self.size, self.geotransform,
                                  smoothing=0.5)
        self.assertIsInstance(result, type(array((0, 0))))

        self.assertAlmostEqual(result[0][4], 1.9169, 3)
        self.assertAlmostEqual(result[4][0], 0.0830, 3)
        self.assertAlmostEqual(result[2][2], 1)

    def test_inverse_distance_100(self):
        now = datetime.utcnow()
        geotransform = [0, 0.002002, 0, 2, 0, -0.002002]
        size = [1000, 1000]

        result = inverse_distance(self.residues, size, geotransform)

        spent_time = datetime.utcnow() - now
        print("test_inverse_distance:")
        print("Time for 1000x1000:", spent_time.total_seconds(), "s")
        self.assertLess(spent_time.total_seconds(), 2.0)

        self.assertAlmostEqual(result[0][size[1]-1], 2)
        self.assertAlmostEqual(result[size[0]-1][0], 0)
        self.assertAlmostEqual(result[500][500], 1)
