"""Exact attention math, overlay alignment, and competing-region behavior."""
import unittest
import numpy as np
from PIL import Image
from veyo.metrics import measure_targets
from veyo.heatmaps import heatmap_image, overlay_image
from veyo.distractors import competing_regions


def target(identity, box):
    return {"id": identity, "label": identity, "role": "product", "priority": 1, "box": box}


class MetricTests(unittest.TestCase):
    def test_overlap_is_counted_once_and_area_adjustment_is_explicit(self):
        p = np.full((10, 10), .01)
        result = measure_targets(p, [target("one", [0, 0, 8, 10]), target("two", [2, 0, 10, 10])])
        self.assertAlmostEqual(result["attention_share"], 1)
        self.assertAlmostEqual(result["area_share"], 1)
        self.assertAlmostEqual(result["targets"][0]["relative_attention"], 1)
        self.assertAlmostEqual(sum(t["attention_share"] for t in result["targets"]), 1.6)

    def test_heatmap_and_overlay_keep_the_canonical_grid(self):
        p = np.arange(1, 121, dtype=float).reshape(10, 12)
        p /= p.sum()
        heat = heatmap_image(p)
        self.assertEqual(heat.size, (12, 10))
        self.assertEqual(heat.mode, "RGBA")
        self.assertGreater(heat.getpixel((11, 9))[3], heat.getpixel((0, 0))[3])
        original = Image.new("RGB", (12, 10), "white")
        self.assertEqual(overlay_image(original, p).size, original.size)
        self.assertEqual(overlay_image(original, p, 0).tobytes(), original.tobytes())

    def test_competing_peaks_are_outside_targets(self):
        p = np.zeros((100, 100)); p[20:30, 20:30] = .004; p[70:80, 70:80] = .006
        regions = competing_regions(p, [target("primary", [10, 10, 40, 40])])
        self.assertTrue(regions)
        self.assertGreater(regions[0]["box"][0], 40)

    def test_competing_boxes_do_not_overlap_any_target(self):
        p = np.full((100, 100), .0001)
        targets = [target("primary", [30, 30, 70, 70])]
        for region in competing_regions(p, targets):
            l, t, r, b = region["box"]
            self.assertTrue(r <= 30 or l >= 70 or b <= 30 or t >= 70)
