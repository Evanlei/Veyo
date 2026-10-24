"""Transparent attention metrics; overlapping targets are unioned for totals."""
import numpy as np
from .scoring import score_region


def measure_targets(probability: np.ndarray, targets: list[dict]) -> dict:
    height, width = probability.shape
    union = np.zeros((height, width), dtype=bool)
    scores = []
    for target in targets:
        l, t, r, b = target["box"]
        share = score_region(probability, (l, t, r, b))
        area = (r-l) * (b-t) / (height*width)
        union[t:b, l:r] = True
        scores.append({**target, "attention_share": share, "area_share": area,
                       "relative_attention": share / area})
    return {"targets": scores, "attention_share": float(probability[union].sum()),
            "area_share": float(union.mean()), "overlap_note": "Totals count overlapping pixels once."}
