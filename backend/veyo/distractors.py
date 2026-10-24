"""Find competing probability peaks outside marked targets, without inventing labels."""
import numpy as np
from scipy.ndimage import uniform_filter


def competing_regions(probability: np.ndarray, targets: list[dict], count=3) -> list[dict]:
    h, w = probability.shape
    size = max(5, round(min(h, w)*0.13)) | 1
    available = np.ones((h, w), bool)
    for target in targets:
        l, t, r, b = target["box"]
        available[t:b, l:r] = False
    local_mass = uniform_filter(np.where(available, probability, 0), size=size, mode="constant")
    # Report whole regions outside every target, not boxes whose center alone is outside.
    clear_window = uniform_filter(available.astype(float), size=size, mode="constant") > .999999
    local_mass[~clear_window] = 0
    regions = []
    for _ in range(count):
        y, x = np.unravel_index(local_mass.argmax(), local_mass.shape)
        if local_mass[y, x] <= 0:
            break
        l, r = max(0, x-size//2), min(w, x+(size+1)//2)
        t, b = max(0, y-size//2), min(h, y+(size+1)//2)
        share = float(np.where(available[t:b, l:r], probability[t:b, l:r], 0).sum())
        if share < 0.005:
            break
        regions.append({"box": [int(l), int(t), int(r), int(b)],
                        "attention_share": share, "label": f"Competing region {len(regions)+1}"})
        local_mass[max(0,y-size):min(h,y+size), max(0,x-size):min(w,x+size)] = 0
    return regions
