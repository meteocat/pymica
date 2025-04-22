"""Tests for distance to coastline calculations."""

import unittest

from pymica.utils.distance_to_coastline import dist2func, get_dist_array, get_distances


class TestDistSea(unittest.TestCase):
    """Test distance to coastline calculations"""

    def test_dist2func(self):
        """Test distance function"""
        self.assertEqual(dist2func(0), 0)
        self.assertAlmostEqual(dist2func(100000), 1, 1)
        self.assertAlmostEqual(dist2func(200000), dist2func(100000), 1)
        self.assertAlmostEqual(dist2func(200000), dist2func(300000), 2)

    def test_get_distances(self):
        """Test calculating distance from point"""
        result = get_distances([[1, 41]], "pymica_tests/data/coast_line.json")

        self.assertEqual(len(result), 1)
        self.assertTrue(abs(result[0] - 3910) < 1)

        with self.assertRaises(IOError) as c_m:
            get_distances([[1, 41]], "/bad_file.json")
        self.assertEqual("File /bad_file.json doesn't exist", str(c_m.exception))

    def test_get_dist_array(self):
        """Test calculate distance to coastline array"""
        result = get_dist_array(
            25831,
            (420244, 30, 0, 4581058, 0, -30),
            (1000, 10),
            "pymica_tests/data/coast_line.json",
        )
        self.assertEqual(result.shape, (10, 1000))
        self.assertTrue((result <= 1).all() and (result >= 0).all())
