"""Aligned, transparent heatmaps from real model probabilities."""
from io import BytesIO
import numpy as np
from PIL import Image

PALETTE = np.array([[36, 32, 111], [44, 92, 207], [29, 179, 178],
                    [179, 220, 86], [255, 199, 62], [248, 85, 45]], dtype=float)


def heatmap_image(probability: np.ndarray) -> Image.Image:
    if probability.ndim != 2 or not np.isfinite(probability).all() or probability.min() < 0:
        raise ValueError("Expected a finite nonnegative probability grid.")
    scale = float(np.percentile(probability, 99.5))
    intensity = np.clip(probability / max(scale, np.finfo(float).tiny), 0, 1)
    levels = intensity * (len(PALETTE)-1)
    low = levels.astype(int)
    high = np.minimum(low+1, len(PALETTE)-1)
    color = PALETTE[low] * (1-(levels-low)[..., None]) + PALETTE[high] * (levels-low)[..., None]
    alpha = np.clip(intensity**0.65 * 235, 0, 235)
    return Image.fromarray(np.dstack([color, alpha]).astype("uint8"), "RGBA")


def overlay_image(image: Image.Image, probability: np.ndarray, opacity=0.6) -> Image.Image:
    heat = heatmap_image(probability)
    heat.putalpha(heat.getchannel("A").point(lambda p: int(p*opacity)))
    return Image.alpha_composite(image.convert("RGBA"), heat).convert("RGB")
