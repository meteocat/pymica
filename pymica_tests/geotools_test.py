"""Tests for creation of clusters.
"""
import unittest

import pyproj

from pymica.utils.geotools import get_utm_epsg_from_lonlat


class TestGeotools(unittest.TestCase):
    """Test geotools module"""

    def test_get_utm_epsg_from_lonlat(self):
        """Test get definition of UTM from a point"""
        utm_epsg = get_utm_epsg_from_lonlat(0, 0)
        expected = pyproj.CRS.from_proj4(
            "+proj=utm +zone=31 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
        ).to_epsg()
        self.assertEqual(expected, utm_epsg)

        utm_epsg = get_utm_epsg_from_lonlat(0, -10)
        expected = pyproj.CRS.from_proj4(
            "+proj=utm +zone=31 +south +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
        ).to_epsg()
        self.assertEqual(expected, utm_epsg)

        utm_epsg = get_utm_epsg_from_lonlat(-178, 24)
        expected = pyproj.CRS.from_proj4(
            "+proj=utm +zone=1 +ellps=WGS84 +datum=WGS84 +units=m +no_defs"
        ).to_epsg()
        self.assertEqual(expected, utm_epsg)
