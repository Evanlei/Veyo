"""Reversible, bounded image adjustments. No layout changes or generated brand assets."""
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
from .schemas import Adjustment


def adjust_image(image: Image.Image, adjustment: Adjustment, targets: list[dict]):
    result = image.copy()
    box = None
    if adjustment.target_id:
        target = next((t for t in targets if t["id"] == adjustment.target_id), None)
        if target is None:
            raise ValueError("Selected target does not exist on this creative.")
        box = tuple(target["box"])
        result = image.crop(box)
    for enhancer, value in [(ImageEnhance.Brightness, adjustment.brightness),
                            (ImageEnhance.Contrast, adjustment.contrast),
                            (ImageEnhance.Color, adjustment.saturation),
                            (ImageEnhance.Sharpness, adjustment.sharpness)]:
        result = enhancer(result).enhance(value)
    if box:
        full = image.copy()
        # Feather inside the crop; pixels outside the selected rectangle stay exact.
        mask = Image.new("L", result.size, 255)
        if min(result.size) > 12:
            edge = Image.new("L", result.size, 0)
            edge.paste(255, (3, 3, result.width-3, result.height-3))
            mask = edge.filter(ImageFilter.GaussianBlur(2))
        full.paste(result, box[:2], mask)
        result = full
    a, b = np.asarray(image).astype(float), np.asarray(result).astype(float)
    change = {"changed_pixel_share": float((np.abs(a-b).max(axis=2) > 2).mean()),
              "mean_absolute_change": float(np.abs(a-b).mean()),
              "dimensions_preserved": result.size == image.size,
              "kind": "controlled-adjustment", "settings": adjustment.model_dump()}
    if change["changed_pixel_share"] == 0:
        raise ValueError("These settings make no visible change. Adjust a slider and try again.")
    return result, change
