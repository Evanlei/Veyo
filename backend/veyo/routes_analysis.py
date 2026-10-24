"""Inference requests hold an HTTP request open so serverless CPU stays allocated."""
from fastapi import APIRouter, Request
from fastapi.responses import Response
import json
from .dependencies import Repo

router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/assets/{asset_id}/analyze", status_code=201)
def analyze(asset_id: str, request: Request, repo: Repo):
    return request.app.state.analysis.run(repo, asset_id)


@router.get("/runs/{run_id}")
def get_run(run_id: str, repo: Repo):
    return repo.get("runs", run_id)


@router.get("/runs/{run_id}/{artifact}")
def get_artifact(run_id: str, artifact: str, repo: Repo):
    run = repo.get("runs", run_id)
    if artifact == "report.json":
        return Response(json.dumps(run, indent=2), media_type="application/json",
                        headers={"Content-Disposition": 'attachment; filename="veyo-report.json"',
                                 "Cache-Control": "private, no-store"})
    if artifact not in {"heatmap.png", "overlay.png"} or run["status"] != "completed":
        raise FileNotFoundError("Artifact not found.")
    return Response(repo.store.get(repo.key("runs", run_id, artifact)), media_type="image/png",
                    headers={"Cache-Control": "private, no-store"})
