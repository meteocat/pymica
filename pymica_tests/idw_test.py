"""Tests for inverse distance weighting method."""

import unittest
from datetime import datetime

from numpy import array

from pymica.methods.idw import idw


class TestInverseDistanceWeighting(unittest.TestCase):
    """Test for inverse distance weighting"""

    def test_inverse_distance_weighting(self):
        """Test inverse distance weighting"""
        residues = {
            "AA": {"value": 0, "y": 0, "x": 0},
            "BB": {"value": 1, "y": 1, "x": 1},
            "CC": {"value": 2, "y": 2, "x": 2},
        }
        geotransform = [0, 0.5, 0, 2, 0, -0.5]
        size = [5, 5]
        result = idw(residues, size, geotransform, 2)

        self.assertIsInstance(result, type(array((0, 0))))

        self.assertAlmostEqual(result[0][4], 2, places=2)
        self.assertAlmostEqual(result[4][0], 0, places=2)
        self.assertAlmostEqual(result[2][2], 1, places=2)

        now = datetime.utcnow()
        geotransform = [0, 0.002002, 0, 2, 0, -0.002002]
        size = [1000, 1000]

        result = idw(residues, size, geotransform, 2)

        spent_time = datetime.utcnow() - now

        print("test_inverse_distance:")
        print("Time for 1000x1000:", spent_time.total_seconds(), "s")
        self.assertLess(spent_time.total_seconds(), 2.0)

        self.assertAlmostEqual(result[0][size[1] - 1], 2, places=2)
        self.assertAlmostEqual(result[size[0] - 1][0], 0, places=2)
        self.assertAlmostEqual(result[500][500], 1, places=2)
