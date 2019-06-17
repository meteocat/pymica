import unittest

from distance.distance_to_sea import dist2func, get_distances, get_dist_array


class TestDistSea(unittest.TestCase):
    def test_dist2func(self):
        self.assertEqual(dist2func(0), 0)
        self.assertAlmostEqual(dist2func(100000), 1, 1)
        self.assertAlmostEqual(dist2func(200000), dist2func(100000), 1)
        self.assertAlmostEqual(dist2func(200000), dist2func(300000), 2)

    def test_get_distances(self):
        result = get_distances([[1, 41]], "./test/data/coast_line.json")

        self.assertEqual(len(result), 1)
        self.assertTrue(abs(result[0] - 3910) < 1)

        with self.assertRaises(IOError) as c_m:
            get_distances([[1, 41]], "/bad_file.json")
        self.assertEqual(
            "File /bad_file.json doesn't exist",
            str(c_m.exception))

    def test_get_dist_array(self):
        result = get_dist_array(25831, (420244, 30, 0, 4581058, 0, -30),
                                (1000, 10),
                                "./test/data/coast_line.json")
        self.assertEqual(result.shape, (10, 1000))
        self.assertTrue((result <= 1).all() and (result >= 0).all())
