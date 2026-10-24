"""Build README figures from public sample ads and genuine DeepGaze predictions.

Run with backend/.venv/bin/python scripts/make_readme.py. Validated predictions
are cached under outputs/readme; --refresh recomputes every prediction. No user
workspace data, browser credentials, cloud services, or generated heatmaps are used.
"""
from __future__ import annotations

import argparse
from io import BytesIO
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from veyo.adjustments import adjust_image
from veyo.analysis import model_identity
from veyo.config import Settings
from veyo.distractors import competing_regions
from veyo.heatmaps import overlay_image
from veyo.ingest import decode_upload, png_bytes
from veyo.inference import DeepGazePredictor
from veyo.metrics import measure_targets
from veyo.samples import SAMPLES, SAMPLE_DIR
from veyo.schemas import Adjustment

OUT = ROOT / "docs" / "media"
CACHE = ROOT / "outputs" / "readme"
INK, MUTED, BG, LINE, BLUE = "#242720", "#65705e", "#f7f7f2", "#dfe2d8", "#3b4ee8"
COLORS = {"product": "#3b4ee8", "headline": "#ad4c23", "logo": "#357357", "cta": "#884fa1"}


def font(size, bold=False):
    for path in (
        f"/System/Library/Fonts/Supplemental/Arial{' Bold' if bold else ''}.ttf",
        f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf",
    ):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def label(draw, xy, text, size=22, color=INK, bold=False):
    draw.text(xy, text, font=font(size, bold), fill=color)


def canvas(width, height):
    image = Image.new("RGB", (width, height), BG)
    return image, ImageDraw.Draw(image)


def image_panel(canvas_image, image, x, y, width, height, targets=()):
    thumb = image.resize((width, height), Image.Resampling.LANCZOS)
    canvas_image.paste(thumb, (x, y))
    draw = ImageDraw.Draw(canvas_image)
    sx, sy = width / image.width, height / image.height
    for target in targets:
        l, t, r, b = target["box"]
        draw.rectangle((x+l*sx, y+t*sy, x+r*sx, y+b*sy), outline=COLORS.get(target["role"], BLUE), width=2)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def prediction(name, image, identity, predictor, refresh):
    directory = CACHE / name
    directory.mkdir(parents=True, exist_ok=True)
    meta_path, map_path = directory / "inference.json", directory / "probability.npy"
    fingerprint = {"image_sha256": sha(png_bytes(image)), "model": identity}
    if not refresh and meta_path.exists() and map_path.exists():
        meta, data = json.loads(meta_path.read_text()), map_path.read_bytes()
        if meta.get("input") == fingerprint and meta.get("map_sha256") == sha(data):
            values = np.load(BytesIO(data), allow_pickle=False)
            if (values.shape == (image.height, image.width) and np.isfinite(values).all()
                    and (values >= 0).all() and np.isclose(values.sum(), 1, atol=1e-6, rtol=0)):
                print(f"{name}: validated real-model cache", flush=True)
                return values
    if not predictor:
        predictor.append(DeepGazePredictor())
    print(f"{name}: running DeepGaze IIE", flush=True)
    values = predictor[0].predict(image)
    np.save(map_path, values, allow_pickle=False)
    meta_path.write_text(json.dumps({"input": fingerprint, "map_sha256": sha(map_path.read_bytes())}, indent=2)+"\n")
    return values


def gallery(examples):
    image, draw = canvas(1536, 882)
    label(draw, (42, 30), "THREE CREATIVES. THREE ATTENTION MAPS.", 22, MUTED, True)
    label(draw, (42, 68), "What stands out in each design?", 40, bold=True)
    for index, example in enumerate(examples):
        x = 42 + index * 504
        label(draw, (x, 147), example["short_name"], 28, bold=True)
        label(draw, (x, 190), "CREATIVE + TARGETS", 15, MUTED, True)
        label(draw, (x+240, 190), "PREDICTED ATTENTION", 15, MUTED, True)
        image_panel(image, example["image"], x, 222, 222, 278, example["targets"])
        image_panel(image, example["overlay"], x+240, 222, 222, 278)
        draw.line((x, 524, x+462, 524), fill=LINE, width=2)
        for row, target in enumerate(example["metrics"]["targets"]):
            y = 550 + row * 65
            draw.ellipse((x, y+8, x+11, y+19), fill=COLORS[target["role"]])
            label(draw, (x+22, y), target["label"], 22, bold=True)
            label(draw, (x+22, y+28), f"{target['area_share']*100:.1f}% of image", 17, MUTED)
            value = f"{target['attention_share']*100:.1f}%  /  {target['relative_attention']:.2f}x"
            value_width = draw.textlength(value, font=font(22))
            label(draw, (x+462-value_width, y), value, 22)
    label(draw, (42, 789), "Values: attention share / attention per pixel relative to the image average.", 22, MUTED)
    label(draw, (42, 826), "Actual DeepGaze IIE outputs on original fictional ads. Colors show intensity; no gaze sequence is inferred.", 21, MUTED)
    image.save(OUT / "examples.png", optimize=True)


def hero(examples):
    frames = []
    for example in examples:
        image, draw = canvas(1080, 792)
        label(draw, (36, 24), "VEYO / ATTENTION STUDIO", 19, MUTED, True)
        label(draw, (36, 60), example["short_name"], 37, bold=True)
        label(draw, (36, 125), "MARK WHAT MATTERS", 17, MUTED, True)
        label(draw, (558, 125), "SEE THE PREDICTION", 17, MUTED, True)
        image_panel(image, example["image"], 36, 164, 486, 608, example["targets"])
        image_panel(image, example["overlay"], 558, 164, 486, 608)
        frames.append(image)
    frames[0].save(OUT / "attention.gif", save_all=True, append_images=frames[1:],
                   duration=2800, loop=0, optimize=False, disposal=2)


def comparison(before, after):
    image, draw = canvas(1536, 1120)
    label(draw, (42, 28), "ONE CONTROLLED EDIT", 22, MUTED, True)
    label(draw, (42, 69), "A brighter product. A small, mixed result.", 40, bold=True)
    images = [before["image"], after["image"], before["overlay"], after["overlay"]]
    titles = ["Original", "Product brightness 1.20x", "Original attention", "Revised attention"]
    for index, (panel, title) in enumerate(zip(images, titles)):
        x = 42 + index * 378
        label(draw, (x, 148), title, 21, bold=True)
        image_panel(image, panel, x, 196, 318, 398)
    draw.line((42, 625, 1494, 625), fill=LINE, width=2)
    columns = [42, 580, 820, 1060, 1280]
    for x, title in zip(columns, ("TARGET", "BEFORE", "AFTER", "CHANGE", "AREA")):
        label(draw, (x, 656), title, 18, MUTED, True)
    left = before["metrics"]["targets"]
    right = {target["id"]: target for target in after["metrics"]["targets"]}
    for row, target in enumerate(left):
        match, y = right[target["id"]], 708+row*62
        delta = 100 * (match["attention_share"]-target["attention_share"])
        values = (target["label"], f"{target['attention_share']*100:.2f}%",
                  f"{match['attention_share']*100:.2f}%", f"{delta:+.2f} pp", f"{target['area_share']*100:.2f}%")
        for col, (x, value) in enumerate(zip(columns, values)):
            label(draw, (x, y), value, 25, "#ad4c23" if col == 3 and delta < 0 else INK, col == 0)
    draw.line((42, 917, 1494, 917), fill=LINE, width=2)
    label(draw, (42, 951), "Same target bounds. Same model. Pixels outside the Products target are unchanged.", 26, bold=True)
    label(draw, (42, 999), "Product and headline shares increase; brand share decreases. A model gain is not proof of a better ad.", 23, MUTED)
    label(draw, (42, 1044), "Metrics are recomputed from saved probability maps whenever this figure is built. pp = percentage points.", 22, MUTED)
    image.save(OUT / "before-after.png", optimize=True)


def main():
    import torch
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    torch.set_num_threads(4)
    OUT.mkdir(parents=True, exist_ok=True)
    identity, predictor, examples = model_identity(), [], []
    for name, sample in SAMPLES.items():
        image, provenance = decode_upload((SAMPLE_DIR / f"{name}.png").read_bytes(), Settings.from_env())
        values = prediction(name, image, identity, predictor, args.refresh)
        examples.append({"name": name, "short_name": sample["name"].split(" — ")[0], "image": image,
                         "overlay": overlay_image(image, values), "targets": sample["targets"],
                         "metrics": measure_targets(values, sample["targets"]), "provenance": provenance,
                         "competing_regions": competing_regions(values, sample["targets"]),
                         "image_sha256": sha(png_bytes(image)), "probability_sha256": sha((CACHE/name/"probability.npy").read_bytes())})
    before = examples[0]
    adjustment = Adjustment(label="Brighter products", brightness=1.2, target_id="products")
    revised, change = adjust_image(before["image"], adjustment, before["targets"])
    values = prediction("forma-brighter-products", revised, identity, predictor, args.refresh)
    after = {"image": revised, "overlay": overlay_image(revised, values), "targets": before["targets"],
             "metrics": measure_targets(values, before["targets"])}
    revised.save(OUT / "forma-brighter-products.png", optimize=True)
    # Assert the figure's claim against the actual pixels, not a visual approximation.
    a, b = np.asarray(before["image"]), np.asarray(revised)
    l, t, r, bottom = before["targets"][0]["box"]
    outside = np.ones(a.shape[:2], dtype=bool)
    outside[t:bottom, l:r] = False
    assert np.array_equal(a[outside], b[outside])
    deltas = [{"label": left["label"], "before": left["attention_share"], "after": right["attention_share"],
               "delta_pp": (right["attention_share"]-left["attention_share"])*100}
              for left, right in zip(before["metrics"]["targets"], after["metrics"]["targets"])]
    measurements = {"model": identity, "heatmap": {"percentile": 99.5, "opacity": 0.6},
                    "examples": [{k: v for k, v in example.items() if k not in {"image", "overlay"}} for example in examples],
                    "comparison": {"settings": adjustment.model_dump(), "change": change, "targets": deltas,
                                   "before_total": before["metrics"]["attention_share"], "after_total": after["metrics"]["attention_share"],
                                   "image_sha256": sha(png_bytes(revised)),
                                   "probability_sha256": sha((CACHE/"forma-brighter-products"/"probability.npy").read_bytes()),
                                   "outside_target_pixels_unchanged": True}}
    (OUT / "measurements.json").write_text(json.dumps(measurements, indent=2, allow_nan=False)+"\n")
    gallery(examples)
    hero(examples)
    comparison(before, after)
    print(json.dumps({"examples": {e["name"]: e["metrics"] for e in examples}, "comparison": deltas}, indent=2), flush=True)


if __name__ == "__main__":
    main()
