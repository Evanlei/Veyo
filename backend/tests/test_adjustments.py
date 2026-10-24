import unittest
import numpy as np
from PIL import Image
from veyo.adjustments import adjust_image
from veyo.schemas import Adjustment


class AdjustmentTests(unittest.TestCase):
    def test_local_adjustment_preserves_unselected_pixels_and_original(self):
        source = np.arange(30*30*3, dtype=np.uint8).reshape(30, 30, 3)
        image = Image.fromarray(source)
        result, evidence = adjust_image(image, Adjustment(brightness=1.3, target_id="product"),
                                        [{"id": "product", "box": [5, 5, 25, 25]}])
        actual = np.asarray(result)
        self.assertTrue(np.array_equal(actual[:5], source[:5]))
        self.assertTrue(np.array_equal(actual[:, :5], source[:, :5]))
        self.assertTrue(np.array_equal(np.asarray(image), source))
        self.assertGreater(evidence["changed_pixel_share"], 0)
        self.assertTrue(evidence["dimensions_preserved"])

    def test_noop_and_unknown_target_are_rejected(self):
        image = Image.new("RGB", (20, 20), "gray")
        with self.assertRaises(ValueError):
            adjust_image(image, Adjustment(), [])
        with self.assertRaises(ValueError):
            adjust_image(image, Adjustment(brightness=1.2, target_id="absent"), [])
