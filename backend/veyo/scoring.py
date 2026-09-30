"""Score rectangular targets using normalized spatial probabilities."""
from numbers import Integral

import numpy as np


def score_region(
    probability: np.ndarray, box: tuple[int, int, int, int]
) -> float:
    """Return fixation probability mass inside a half-open (left, top, right, bottom) box.

    Coordinates must refer to the canonical image that produced this H x W map.
    The result is a fraction in [0, 1], not measured attention or click probability.
    """
    values = np.asarray(probability)
    if values.ndim != 2 or values.size == 0:
        raise ValueError("Expected a nonempty H x W probability map.")
    if values.dtype.kind not in "fiu":
        raise ValueError("Probability values must be real numbers.")
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("Probabilities must be finite and nonnegative.")
    total = float(values.sum(dtype=np.float64))
    if not np.isclose(total, 1.0, rtol=0, atol=1e-6):
        raise ValueError("Probability map must sum to 1.")
    if len(box) != 4 or any(
        isinstance(coordinate, (bool, np.bool_)) or not isinstance(coordinate, Integral)
        for coordinate in box
    ):
        raise ValueError("Box must contain four integer pixel coordinates.")
    left, top, right, bottom = box
    height, width = values.shape
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise ValueError("Box must have positive area and lie inside the probability map.")
    # Arrays index rows (y) first, then columns (x). Correct only accepted float drift.
    return float(values[top:bottom, left:right].sum(dtype=np.float64) / total)
