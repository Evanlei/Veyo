"""Contract tests use explicit test doubles; the real-model run is separate."""
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image
import torch

from veyo.inference import DeepGazePredictor, _prepare_inputs, _probabilities


class InferenceContractTests(unittest.TestCase):
    def test_input_layout_channels_and_scale(self):
        image = Image.new("RGB", (3, 2), (11, 22, 233))
        image.putpixel((2, 1), (255, 0, 99))
        tensor, prior = _prepare_inputs(image)
        self.assertEqual(tuple(tensor.shape), (1, 3, 2, 3))
        self.assertEqual(tensor.dtype, torch.float32)
        self.assertEqual(tensor[0, :, 1, 2].tolist(), [255, 0, 99])
        self.assertEqual(tensor[0, :, 0, 0].tolist(), [11, 22, 233])
        self.assertEqual(tuple(prior.shape), (1, 2, 3))
        self.assertAlmostEqual(prior.exp().sum().item(), 1, places=6)

    def test_noncanonical_input_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "canonical RGB"):
            _prepare_inputs(Image.new("RGBA", (3, 2)))

    def test_asymmetric_probability_grid_preserves_coordinates(self):
        expected = np.array([[.05, .10, .15], [.20, .10, .40]])
        result = _probabilities(torch.tensor(np.log(expected))[None, None], (3, 2))
        np.testing.assert_allclose(result, expected, atol=1e-12)
        self.assertEqual(np.unravel_index(result.argmax(), result.shape), (1, 2))
        self.assertAlmostEqual(float(result.sum()), 1)

    def test_wrong_shape_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "shape"):
            _probabilities(torch.zeros((1, 1, 3, 2)), (3, 2))

    def test_nonfinite_values_are_rejected(self):
        for bad in [float('nan'), float('inf'), -float('inf')]:
            with self.subTest(value=bad), self.assertRaisesRegex(ValueError, "non-finite"):
                _probabilities(torch.tensor([[[[bad]]]]), (1, 1))

    def test_unnormalized_model_output_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "not normalized"):
            _probabilities(torch.zeros((1, 1, 2, 3)), (3, 2))

    def test_small_numerical_drift_is_corrected(self):
        values = torch.full((1, 1, 2, 3), -float(np.log(6)) + 1e-6)
        result = _probabilities(values, (3, 2))
        self.assertAlmostEqual(float(result.sum()), 1)
        np.testing.assert_allclose(result, 1/6)

    def test_prediction_uses_inference_mode_and_propagates_failure(self):
        class FailingModel:
            def __call__(self, tensor, prior):
                if not torch.is_inference_mode_enabled():
                    raise AssertionError("Gradients were not disabled")
                raise RuntimeError("Intentional model failure")
        predictor = DeepGazePredictor.__new__(DeepGazePredictor)
        predictor.model = FailingModel()
        with self.assertRaisesRegex(RuntimeError, "Intentional model failure"):
            predictor.predict(Image.new("RGB", (3, 2)))

    def test_model_load_failure_is_not_replaced(self):
        with patch('deepgaze_pytorch.DeepGazeIIE', side_effect=RuntimeError('weights unavailable')):
            with patch('torch.hub.set_dir'):
                with self.assertRaisesRegex(RuntimeError, 'weights unavailable'):
                    DeepGazePredictor()


if __name__ == '__main__':
    unittest.main()
