"""Testing pymica.clustered_regression.py
"""
import json
import unittest
import numpy as np

from pymica.methods.clustered_regression import ClusteredRegression


class TestClusteredRegression(unittest.TestCase):
    with open("pymica_tests/data/sample_data_value.json", "rb") as f_p:
        data = json.load(f_p)

    def test_regression_ideal_data(self):
        """Test clustered regression with ideal data"""

        inst = ClusteredRegression(
            self.data, ["pymica_tests/data/test_clusters_3.shp"], ("altitude", "dist")
        )
        self.assertEqual(len(inst.final_data), 3)
        self.assertAlmostEqual(inst.mse, 2.1853, 3)

        with self.assertRaises(FileNotFoundError) as cm:
            ClusteredRegression(self.data, ["BadFile"], ("altitude", "dist"))
        self.assertEqual(
            "File not found, or not ogr compatible BadFile", str(cm.exception)
        )

        with self.assertRaises(ValueError) as cm:
            ClusteredRegression(self.data, 23, ("altitude", "dist"))
        self.assertEqual("cluster file must be a list", str(cm.exception))

    def test_get_residuals(self):
        inst = ClusteredRegression(
            self.data, ["pymica_tests/data/test_clusters_3.shp"], ("altitude", "dist")
        )
        result = inst.get_residuals()
        self.assertEqual(len(self.data), len(result))
        for point in self.data:
            self.assertTrue(point["id"] in result)

    def test_predict_points(self):
        inst = ClusteredRegression(
            self.data, ["pymica_tests/data/test_clusters_3.shp"], ("altitude", "dist")
        )
        sample_data = [
            {
                "id": "C6",
                "temp": 6.4,
                "altitude": 264,
                "lon": 0.95172,
                "lat": 41.6566,
                "dist": 0.8583929293407604,
            },
            {
                "id": "C7",
                "temp": 5.6,
                "altitude": 427,
                "lon": 1.16234,
                "lat": 41.66695,
                "dist": 0.8387222708681318,
            },
            {
                "id": "UQ",
                "temp": 10,
                "altitude": 460,
                "lon": 2.44532,
                "lat": 41.61991,
                "dist": 0.24251682692034138,
            },
        ]
        result = inst.predict_points(sample_data)
        self.assertEqual(len(result), 3)
        # Order is maintained
        self.assertAlmostEqual(result[1], inst.predict_points([sample_data[1]])[0], 3)

    def test_apply_clustered_regression(self):
        """Test application of clustered regression"""
        inst = ClusteredRegression(
            self.data,
            ["pymica_tests/data/test_clusters_3.shp"],
            x_vars=("altitude", "dist"),
        )

        size = [1000, 1000]
        alt_data = np.ones(size)
        alt_data[2][2] = 12

        dist_data = np.ones(size)

        in_data = np.array([alt_data, dist_data])

        # An arbitrary mask to check the effect
        mask = np.zeros([3, 1000, 1000])
        for i in range(3):
            for j in range(500):
                mask[i][i * 250 + j][:] = 1 - j / 550

        result = inst.apply_clustered_regression(in_data, ["altitude", "dist"], mask)
        self.assertEqual(list(result.shape), size)
