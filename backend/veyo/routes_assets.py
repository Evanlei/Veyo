"""Revision uploads, target annotations, and private image delivery."""
from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import Response
from .dependencies import Repo
from .ingest import decode_upload, png_bytes
from .schemas import Annotation

router = APIRouter(prefix="/api", tags=["creatives"])


@router.post("/projects/{project_id}/assets", status_code=201)
def upload_revision(project_id: str, request: Request, repo: Repo,
                    image: UploadFile = File(...), label: str = Form("Revision", min_length=1, max_length=100),
                    parent_id: str | None = Form(None)):
    repo.get("projects", project_id)
    if len(repo.list("assets", project_id)) >= 100:
        raise ValueError("This project has reached its 100-revision limit.")
    if parent_id and repo.get("assets", parent_id)["project_id"] != project_id:
        raise ValueError("Parent creative belongs to another project.")
    data = image.file.read(request.app.state.settings.max_upload_bytes+1)
    image, source = decode_upload(data, request.app.state.settings)
    return repo.create_asset(project_id, png_bytes(image), *image.size, label,
                             {"kind": "upload", **source}, parent_id=parent_id)


@router.put("/assets/{asset_id}/targets")
def annotate(asset_id: str, annotation: Annotation, repo: Repo):
    asset = repo.get("assets", asset_id)
    for target in annotation.targets:
        if target.box[2] > asset["width"] or target.box[3] > asset["height"]:
            raise ValueError("Target extends outside this creative.")
    names = [(t.role, t.label.casefold()) for t in annotation.targets]
    if len(set(names)) != len(names):
        raise ValueError("Use a distinct label for each target with the same role.")
    asset.update(targets=[t.model_dump(mode="json") for t in annotation.targets], confirmed=annotation.confirmed)
    return repo.save("assets", asset)


@router.get("/assets/{asset_id}/image")
def asset_image(asset_id: str, repo: Repo):
    repo.get("assets", asset_id)
    return Response(repo.store.get(repo.key("assets", asset_id, "image.png")), media_type="image/png",
                    headers={"Cache-Control": "private, no-store", "X-Content-Type-Options": "nosniff"})
