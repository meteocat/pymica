'''Testing inverse_distance_3d.py file
'''
import unittest
from datetime import datetime

from numpy import array, zeros

# pylint: disable=E0611
from pymica.methods.inverse_distance_3d import inverse_distance_3d


class TestInverseDistance3D(unittest.TestCase):

    residues = [{'id': 'AA', 'value': 0, 'altitude': 1, 'y': 0, 'x': 0},
                {'id': 'BB', 'value': 1, 'altitude': 0, 'y': 1, 'x': 1},
                {'id': 'CC', 'value': 2, 'altitude': 0, 'y': 2, 'x': 2}]

    geotransform = [0, 0.5, 0, 2, 0, -0.5]
    size = [5, 5]

    dem = array([[1, 0, 0, 0, 0],
                 [1, 0, 0, 0, 0],
                 [1, 0, 0, 0, 1],
                 [1, 0, 0, 0, 2],
                 [1, 0, 0, 0, 3]])

    def test_inverse_distance_3d(self):
        result = inverse_distance_3d(self.residues, self.size,
                                     self.geotransform, self.dem)

        self.assertIsInstance(result, type(array((0, 0))))

        self.assertEqual(result[0][4], 2)
        self.assertEqual(result[4][0], 0)
        self.assertEqual(result[2][2], 1)

        self.assertAlmostEqual(result[0][0], 0.013, 2)
        self.assertAlmostEqual(result[4][4], 0.706, 2)
        self.assertAlmostEqual(result[4][1], 1.165, 2)

    def test_inverse_distance_3d_power(self):
        result = inverse_distance_3d(self.residues, self.size,
                                     self.geotransform, self.dem,
                                     power=3)

        self.assertIsInstance(result, type(array((0, 0))))

        self.assertEqual(result[0][4], 2)
        self.assertEqual(result[4][0], 0)
        self.assertEqual(result[2][2], 1)

        self.assertAlmostEqual(result[0][0], 0.0008, 3)
        self.assertAlmostEqual(result[4][4], 0.5584, 3)
        self.assertAlmostEqual(result[4][1], 1.0820, 3)

    def test_inverse_distance_3d_smoothing(self):
        result = inverse_distance_3d(self.residues, self.size,
                                     self.geotransform, self.dem,
                                     smoothing=2)

        self.assertIsInstance(result, type(array((0, 0))))

        self.assertEqual(result[0][4], 2)
        self.assertEqual(result[4][0], 0)
        self.assertEqual(result[2][2], 1)

        self.assertAlmostEqual(result[0][0], 0.0259, 3)
        self.assertAlmostEqual(result[4][4], 0.7063, 3)
        self.assertAlmostEqual(result[4][1], 1.3335, 3)

    def test_inverse_distance_3d_penalization(self):
        result = inverse_distance_3d(self.residues, self.size,
                                     self.geotransform, self.dem,
                                     smoothing=2, penalization=100)

        self.assertIsInstance(result, type(array((0, 0))))

        self.assertEqual(result[0][4], 2)
        self.assertEqual(result[4][0], 0)
        self.assertEqual(result[2][2], 1)

        self.assertAlmostEqual(result[0][0], 0.0023, 3)
        self.assertAlmostEqual(result[4][4], 0.7063, 3)
        self.assertAlmostEqual(result[4][1], 1.3382, 3)

    def test_inverse_distance_3d_1000(self):

        now = datetime.utcnow()
        geotransform = [0, 0.002002, 0, 2, 0, -0.002002]
        size = [1000, 1000]

        dem = zeros((1000, 1000))
        dem[750:, :] = 1
        dem[:, 0:250] = 1

        result = inverse_distance_3d(self.residues, size, geotransform, dem)
        spent_time = datetime.utcnow() - now
        print("test_inverse_distance:")
        print("Time for 1000x1000:", spent_time.total_seconds(), "s")
        self.assertLess(spent_time.total_seconds(), 50.5)

        self.assertAlmostEqual(result[0][size[1]-1], 2, 5)
        self.assertAlmostEqual(result[size[0]-1][0], 0, 5)
        self.assertAlmostEqual(result[int(size[0]/2)][int(size[1]/2)], 1, 5)
        self.assertAlmostEqual(result[0][0], 0.013, 3)
        self.assertAlmostEqual(result[size[0]-1][size[1]-1], 0.013, 3)
