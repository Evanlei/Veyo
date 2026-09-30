"""CPU DeepGaze IIE inference; failures never produce substitute predictions."""
from __future__ import annotations

import argparse
import hashlib
import json
from importlib import metadata
from pathlib import Path
from time import perf_counter

import numpy as np
from PIL import Image
import torch

from .images import load_image


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _prepare_inputs(image: Image.Image) -> tuple[torch.Tensor, torch.Tensor]:
    if image.mode != "RGB":
        raise ValueError("Expected a canonical RGB image from load_image().")
    width, height = image.size
    # Upstream expects RGB values in 0..255 and handles normalization internally.
    pixels = np.array(image, dtype=np.uint8, copy=True)
    tensor = torch.from_numpy(pixels).permute(2, 0, 1).unsqueeze(0).float()
    # Uniform spatial prior: each pixel starts with equal probability.
    centerbias = torch.full((1, height, width), -float(np.log(height * width)))
    return tensor, centerbias


def _probabilities(log_density: torch.Tensor, size: tuple[int, int]) -> np.ndarray:
    width, height = size
    expected = (1, 1, height, width)
    if tuple(log_density.shape) != expected:
        raise ValueError(f"Prediction shape {tuple(log_density.shape)} != {expected}.")
    values = log_density.detach().cpu().double()
    if not torch.isfinite(values).all().item():
        raise ValueError("Prediction contains non-finite values.")
    log_total = torch.logsumexp(values.flatten(), dim=0).item()
    if abs(log_total) > 1e-4:
        raise ValueError(f"Model prediction is not normalized: log total {log_total}.")
    # Correct only small floating-point drift after checking upstream normalization.
    probability = np.exp(values[0, 0].numpy() - log_total)
    probability /= probability.sum()
    return probability


class DeepGazePredictor:
    """Load once and reuse for sequential predictions within one process."""

    def __init__(self, cache_dir: str | Path = PROJECT_ROOT / "model-cache"):
        from deepgaze_pytorch import DeepGazeIIE

        # Torch's cache is process-wide; keep this experiment's downloads local.
        torch.hub.set_dir(str(Path(cache_dir).resolve() / "hub"))
        self.model = DeepGazeIIE(pretrained=True).cpu().eval()

    def predict(self, image: Image.Image) -> np.ndarray:
        tensor, centerbias = _prepare_inputs(image)
        with torch.inference_mode():
            log_density = self.model(tensor, centerbias)
        return _probabilities(log_density, image.size)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--output", required=True, type=Path,
                        help="New directory for the canonical image, probabilities and report.")
    parser.add_argument("--threads", type=int, default=4)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; choose a new directory to preserve the earlier run.")
    if args.threads < 1:
        parser.error("--threads must be positive.")
    torch.set_num_threads(args.threads)
    source_hash = hashlib.sha256(args.image.read_bytes()).hexdigest()
    image = load_image(args.image)
    started = perf_counter()
    predictor = DeepGazePredictor()
    load_seconds = perf_counter() - started
    started = perf_counter()
    probability = predictor.predict(image)
    inference_seconds = perf_counter() - started

    package = metadata.distribution("deepgaze_pytorch")
    source = json.loads(package.read_text("direct_url.json") or "{}")
    report = {
        "status": "completed", "model": "DeepGaze IIE", "pretrained": True,
        "deepgaze_version": package.version,
        "deepgaze_commit": source.get("vcs_info", {}).get("commit_id"),
        "torch_version": torch.__version__, "device": "cpu", "threads": args.threads,
        "centerbias": "uniform", "preprocessing": "exif-white-rgb-v1",
        "input_sha256": source_hash, "width": image.width, "height": image.height,
        "probability_shape": list(probability.shape),
        "probability_sum": float(probability.sum()),
        "probability_min": float(probability.min()), "probability_max": float(probability.max()),
        "load_seconds": load_seconds, "inference_seconds": inference_seconds,
    }
    # Create only after successful inference; never overwrite an existing run.
    args.output.mkdir(parents=True, exist_ok=False)
    image.save(args.output / "input.png")
    np.save(args.output / "probability.npy", probability, allow_pickle=False)
    report["probability_sha256"] = hashlib.sha256(
        (args.output / "probability.npy").read_bytes()
    ).hexdigest()
    # Report is written last; its presence marks a completely saved local run.
    (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
