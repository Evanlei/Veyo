"""Curated, first-party example ads with known target annotations."""
from pathlib import Path
from fastapi import APIRouter
from .dependencies import Repo
from .ingest import decode_upload, png_bytes
from .config import Settings

SAMPLE_DIR = Path(__file__).resolve().parents[2] / "frontend" / "public" / "samples"
SAMPLES = {
    "forma": {"name": "Forma — Everyday essentials", "targets": [
        {"id": "products", "label": "Products", "role": "product", "box": [175, 345, 735, 930], "priority": 3},
        {"id": "headline", "label": "Headline", "role": "headline", "box": [50, 170, 825, 310], "priority": 2},
        {"id": "brand", "label": "Brand", "role": "logo", "box": [48, 40, 300, 135], "priority": 1}]},
    "fieldwork": {"name": "Fieldwork — A better morning", "targets": [
        {"id": "product", "label": "Coffee bag", "role": "product", "box": [240, 375, 660, 955], "priority": 3},
        {"id": "headline", "label": "Headline", "role": "headline", "box": [50, 170, 845, 320], "priority": 2},
        {"id": "brand", "label": "Brand", "role": "logo", "box": [48, 45, 425, 115], "priority": 1}]},
    "pace": {"name": "Pace — Find your own rhythm", "targets": [
        {"id": "headline", "label": "Headline", "role": "headline", "box": [45, 178, 760, 537], "priority": 3},
        {"id": "cta", "label": "Call to action", "role": "cta", "box": [50, 992, 395, 1084], "priority": 2},
        {"id": "brand", "label": "Brand", "role": "logo", "box": [48, 45, 295, 135], "priority": 1}]},
}
router = APIRouter(prefix="/api/samples", tags=["examples"])


@router.post("/{sample_id}", status_code=201)
def create_sample(sample_id: str, repo: Repo):
    if sample_id not in SAMPLES:
        raise FileNotFoundError("Sample not found.")
    if len(repo.list("projects")) >= 50:
        raise ValueError("This workspace has reached its 50-project limit.")
    sample = SAMPLES[sample_id]
    image, source = decode_upload((SAMPLE_DIR / f"{sample_id}.png").read_bytes(), Settings.from_env())
    project = repo.create_project(sample["name"])
    asset = repo.create_asset(project["id"], png_bytes(image), *image.size,
                             "Original", {"kind": "sample", "sample": sample_id, **source}, targets=sample["targets"])
    asset["confirmed"] = True
    repo.save("assets", asset)
    return {**project, "assets": [asset], "runs": []}
