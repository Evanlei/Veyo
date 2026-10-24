"""Portable exports include evidence and files, never workspace credentials."""
from io import BytesIO
import json
from zipfile import ZipFile, ZIP_DEFLATED
from .repository import Repository


def project_archive(repo: Repository, project_id: str) -> bytes:
    project = repo.project(project_id)
    out = BytesIO()
    with ZipFile(out, "w", ZIP_DEFLATED) as archive:
        archive.writestr("project.json", json.dumps({"format": "veyo-project-v1", **project}, indent=2))
        for asset in project["assets"]:
            archive.writestr(f"creatives/{asset['id']}.png",
                             repo.store.get(repo.key("assets", asset["id"], "image.png")))
        for run in project["runs"]:
            if run["status"] == "completed":
                for name in ("heatmap.png", "overlay.png"):
                    archive.writestr(f"analyses/{run['id']}/{name}", repo.store.get(repo.key("runs", run["id"], name)))
        archive.writestr("README.txt", "Veyo predictions are spatial model probabilities, not CTR, sales, or measured human attention.\n")
    return out.getvalue()
