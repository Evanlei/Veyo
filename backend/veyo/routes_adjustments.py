"""Create an adjustment as a new revision, preserving the original and its evidence."""
from io import BytesIO
from PIL import Image
from fastapi import APIRouter
from .dependencies import Repo
from .schemas import Adjustment
from .adjustments import adjust_image
from .ingest import png_bytes

router = APIRouter(prefix="/api/assets", tags=["adjustments"])


@router.post("/{asset_id}/adjust", status_code=201)
def adjust(asset_id: str, adjustment: Adjustment, repo: Repo):
    asset = repo.get("assets", asset_id)
    if len(repo.list("assets", asset["project_id"])) >= 100:
        raise ValueError("This project has reached its 100-revision limit.")
    image = Image.open(BytesIO(repo.store.get(repo.key("assets", asset_id, "image.png")))).convert("RGB")
    result, evidence = adjust_image(image, adjustment, asset["targets"])
    return repo.create_asset(asset["project_id"], png_bytes(result), *result.size,
                             adjustment.label, evidence, parent_id=asset_id, targets=asset["targets"])
