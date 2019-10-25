'''Testing inverse_distance_3d.py file
'''
import unittest
from datetime import datetime

from numpy import array, zeros

# pylint: disable=E0611
from interpolation.inverse_distance_3d import inverse_distance_3d


class TestInverseDistance3D(unittest.TestCase):

    def test_inverse_distance_3d(self):

        residues = {'AA': {'value': 0, 'z': 1, 'y': 0, 'x': 0},
                    'BB': {'value': 1, 'z': 0, 'y': 1, 'x': 1},
                    'CC': {'value': 2, 'z': 0, 'y': 2, 'x': 2}}
        geotransform = [0, 0.5, 0, 2, 0, -0.5]
        size = [5, 5]

        dem = array([[1, 0, 0, 0, 0],
                     [1, 0, 0, 0, 0],
                     [1, 0, 0, 0, 1],
                     [1, 0, 0, 0, 2],
                     [1, 0, 0, 0, 3]])

        result = inverse_distance_3d(residues, size, geotransform, dem)

        self.assertIsInstance(result, type(array((0, 0))))

        self.assertEqual(result[0][4], 2)
        self.assertEqual(result[4][0], 0)
        self.assertEqual(result[2][2], 1)

        self.assertTrue(abs(result[0][0] - 0.013) < 0.001)
        self.assertTrue(abs(result[4][4] - 0.706) < 0.001)
        self.assertTrue(abs(result[4][1] - 1.165) < 0.001)

        now = datetime.utcnow()
        geotransform = [0, 0.002002, 0, 2, 0, -0.002002]
        size = [1000, 1000]

        dem = zeros((1000, 1000))
        dem[750:, :] = 1
        dem[:, 0:250] = 1

        result = inverse_distance_3d(residues, size, geotransform, dem)
        spent_time = datetime.utcnow() - now
        print("test_inverse_distance:")
        print("Time for 1000x1000:", spent_time.total_seconds(), "s")
        self.assertLess(spent_time.total_seconds(), 50.5)

        self.assertAlmostEqual(result[0][size[1]-1], 2, places=5)
        self.assertAlmostEqual(result[size[0]-1][0], 0, places=5)
        self.assertAlmostEqual(result[int(size[0]/2)][int(size[1]/2)],
                               1, places=5)
        self.assertAlmostEqual(result[0][0], 0.013, places=3)
        self.assertAlmostEqual(result[size[0]-1][size[1]-1], 0.013,
                               places=3)
