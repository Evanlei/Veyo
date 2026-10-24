"""Reproducible analysis records with cached real predictions and immutable target snapshots."""
from io import BytesIO
import hashlib
from importlib import metadata
import json
from time import perf_counter
import numpy as np
from PIL import Image
from .repository import Repository, new_id, now
from .metrics import measure_targets
from .distractors import competing_regions
from .heatmaps import heatmap_image, overlay_image
from .ingest import png_bytes

MODEL_CONFIG = {"model": "DeepGaze IIE", "centerbias": "uniform", "device": "cpu",
                "preprocessing": "exif-white-rgb-max1600-v1", "version": 1}


def model_identity() -> dict:
    package = metadata.distribution("deepgaze_pytorch")
    source = json.loads(package.read_text("direct_url.json") or "{}")
    return {**MODEL_CONFIG, "package_version": package.version,
            "source_commit": source.get("vcs_info", {}).get("commit_id")}


class AnalysisService:
    def __init__(self, engine):
        self.engine = engine

    def probability(self, repo: Repository, asset: dict):
        key = repo.key("assets", asset["id"], "probability.npy")
        info_key = repo.key("assets", asset["id"], "inference.json")
        identity = model_identity()
        try:
            info = repo.store.json(info_key)
            data = repo.store.get(key)
            if (info["input_sha256"] == asset["sha256"] and info["model"] == identity
                    and info["sha256"] == hashlib.sha256(data).hexdigest()):
                values = np.load(BytesIO(data), allow_pickle=False)
                if (values.shape == (asset["height"], asset["width"])
                        and np.isfinite(values).all() and (values >= 0).all()
                        and np.isclose(values.sum(), 1, atol=1e-6, rtol=0)):
                    return values, True, identity
        except (FileNotFoundError, KeyError, ValueError):
            pass
        image = Image.open(BytesIO(repo.store.get(repo.key("assets", asset["id"], "image.png")))).convert("RGB")
        values = self.engine.predict(image)
        out = BytesIO()
        np.save(out, values, allow_pickle=False)
        data = out.getvalue()
        repo.store.put(key, data)
        repo.store.put_json(info_key, {"input_sha256": asset["sha256"], "model": identity,
                                      "sha256": hashlib.sha256(data).hexdigest()})
        return values, False, identity

    def run(self, repo: Repository, asset_id: str):
        asset = repo.get("assets", asset_id)
        if not asset["confirmed"] or not asset["targets"]:
            raise ValueError("Mark and confirm at least one target before running analysis.")
        run = {"id": new_id(), "project_id": asset["project_id"], "asset_id": asset_id,
               "created_at": now(), "status": "running", "input_sha256": asset["sha256"],
               "width": asset["width"], "height": asset["height"], "targets": asset["targets"]}
        repo.save("runs", run)
        started = perf_counter()
        try:
            values, cached, identity = self.probability(repo, asset)
            metrics = measure_targets(values, asset["targets"])
            image = Image.open(BytesIO(repo.store.get(repo.key("assets", asset_id, "image.png")))).convert("RGB")
            for filename, rendered in [("heatmap.png", heatmap_image(values)),
                                       ("overlay.png", overlay_image(image, values))]:
                repo.store.put(repo.key("runs", run["id"], filename), png_bytes(rendered), "image/png")
            run.update(status="completed", completed_at=now(), metrics=metrics, model=identity,
                       cached=cached, seconds=round(perf_counter()-started, 3),
                       competing_regions=competing_regions(values, asset["targets"]),
                       interpretation="Model-predicted fixation probabilities, not measured attention, clicks, or sales.")
            return repo.save("runs", run)
        except Exception as exc:
            run.update(status="failed", error="Analysis failed. No substitute prediction was generated.",
                       completed_at=now())
            repo.save("runs", run)
            raise exc
