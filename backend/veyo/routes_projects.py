"""Creative library and project lifecycle endpoints."""
from fastapi import APIRouter, File, Form, Request, UploadFile
from .dependencies import Repo
from .ingest import decode_upload, png_bytes
from .schemas import ProjectPatch
from .exports import project_archive
from fastapi.responses import Response

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("")
def list_projects(repo: Repo):
    projects = repo.list("projects")
    assets = repo.list("assets")
    runs = repo.list("runs")
    for project in projects:
        project_assets = [a for a in assets if a["project_id"] == project["id"]]
        project_runs = [r for r in runs if r["project_id"] == project["id"] and r["status"] == "completed"]
        project.update(cover_asset=project_assets[-1] if project_assets else None,
                       asset_count=len(project_assets), analysis_count=len(project_runs),
                       latest_run=project_runs[0] if project_runs else None)
    return projects


@router.post("", status_code=201)
def create_project(request: Request, repo: Repo, image: UploadFile = File(...),
                   name: str = Form("Untitled creative", min_length=1, max_length=100)):
    settings = request.app.state.settings
    if len(repo.list("projects")) >= 50:
        raise ValueError("This workspace has reached its 50-project limit.")
    data = image.file.read(settings.max_upload_bytes+1)
    canonical, source = decode_upload(data, settings)
    project = repo.create_project(name)
    asset = repo.create_asset(project["id"], png_bytes(canonical), *canonical.size,
                              "Original", {"kind": "upload", **source})
    return {**project, "assets": [asset], "runs": []}


@router.get("/{project_id}")
def get_project(project_id: str, repo: Repo):
    return repo.project(project_id)


@router.patch("/{project_id}")
def update_project(project_id: str, patch: ProjectPatch, repo: Repo):
    project = repo.get("projects", project_id)
    project.update(patch.model_dump(exclude_none=True))
    return repo.save("projects", project)


@router.get("/{project_id}/export")
def export_project(project_id: str, repo: Repo):
    return Response(project_archive(repo, project_id), media_type="application/zip",
                    headers={"Content-Disposition": 'attachment; filename="veyo-project.zip"',
                             "Cache-Control": "private, no-store"})
