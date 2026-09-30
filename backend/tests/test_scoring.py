import unittest

import numpy as np

from veyo.scoring import score_region


class RegionScoringTests(unittest.TestCase):
    def setUp(self):
        self.probability = np.array([[0.05, 0.10, 0.15], [0.20, 0.25, 0.25]])

    def test_asymmetric_region_uses_y_then_x_and_excludes_endpoints(self):
        self.assertAlmostEqual(score_region(self.probability, (1, 0, 3, 1)), 0.25)
        self.assertAlmostEqual(score_region(self.probability, (0, 1, 1, 2)), 0.20)

    def test_full_image_and_disjoint_partition(self):
        self.assertEqual(score_region(self.probability, (0, 0, 3, 2)), 1.0)
        upper = score_region(self.probability, (0, 0, 3, 1))
        lower = score_region(self.probability, (0, 1, 3, 2))
        self.assertAlmostEqual(upper + lower, 1.0)

    def test_zero_probability_region(self):
        self.assertEqual(score_region(np.array([[0.0, 1.0]]), (0, 0, 1, 1)), 0.0)

    def test_rejects_invalid_boxes(self):
        for box in [(-1, 0, 1, 1), (0, 0, 4, 2), (0, 0, 3, 3),
                    (1, 0, 1, 1), (2, 0, 1, 1), (0, 1, 1, 0),
                    (0.5, 0, 1, 1), (False, 0, 1, 1), (0, 0, 1)]:
            with self.subTest(box=box), self.assertRaises(ValueError):
                score_region(self.probability, box)

    def test_rejects_invalid_probability_maps(self):
        for probability in [np.array([]), np.zeros((0, 2)), np.ones((1, 1, 1)),
                            np.array([[np.nan]]), np.array([[np.inf]]),
                            np.array([[-0.1, 1.1]]), np.array([[0.5]]),
                            np.array([[0.0]]), np.array([[1 + 0j]]),
                            np.array([["1"]])]:
            with self.subTest(probability=probability), self.assertRaises(ValueError):
                score_region(probability, (0, 0, 1, 1))

    def test_small_float_drift_is_corrected_without_mutating_input(self):
        probability = self.probability * (1 + 1e-7)
        before = probability.copy()
        self.assertAlmostEqual(score_region(probability, (1, 0, 3, 1)), 0.25)
        np.testing.assert_array_equal(probability, before)


if __name__ == "__main__":
    unittest.main()
