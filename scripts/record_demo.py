"""Record public sample analyses for a static demo; never read user workspaces.

Requires the backend environment. Published files contain only the repository's
fictional sample ads, controlled revisions, and genuine DeepGaze IIE evidence.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import secrets
import shutil
import sys
import tempfile
from uuid import NAMESPACE_URL, uuid5

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from fastapi.testclient import TestClient
from veyo.analysis import model_identity
from veyo.app import create_app
from veyo.config import Settings
from veyo.exports import project_archive
from veyo.identity import workspace_id
from veyo.repository import Repository, now
from veyo.samples import SAMPLES
from veyo.store import LocalStore

OUT = ROOT / "frontend" / "public" / "demo"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def public_id(name):
    return uuid5(NAMESPACE_URL, f"https://github.com/Evanlei/Veyo/demo/{name}").hex


def normalize(value, ids):
    if isinstance(value, dict):
        return {key: normalize(item, ids) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize(item, ids) for item in value]
    return ids.get(value, value) if isinstance(value, str) else value


def seed_public_cache(repo, asset, cache_name):
    # The README recorder's maps are genuine predictions on these exact images.
    # The production AnalysisService still validates their hashes and contents.
    cache = ROOT / "outputs" / "readme" / cache_name
    if not (cache / "inference.json").is_file() or not (cache / "probability.npy").is_file():
        return
    info = json.loads((cache / "inference.json").read_text())
    data = (cache / "probability.npy").read_bytes()
    if (info.get("input") != {"image_sha256": asset["sha256"], "model": model_identity()}
            or info.get("map_sha256") != digest(data)):
        return
    repo.store.put(repo.key("assets", asset["id"], "probability.npy"), data)
    repo.store.put_json(repo.key("assets", asset["id"], "inference.json"), {
        "input_sha256": asset["sha256"], "model": model_identity(), "sha256": digest(data)})


def main():
    manifest = {"version": 1, "mode": "recorded", "recorded_at": now(),
                "model": model_identity(), "projects": [], "samples": {}, "files": {},
                "notice": "Real DeepGaze IIE results recorded locally on fictional sample ads. No live inference or uploads."}
    with tempfile.TemporaryDirectory(prefix="veyo-public-demo-") as temporary:
        directory = Path(temporary)
        stage = directory / "public"
        stage.mkdir()
        key = secrets.token_hex(32)
        settings = Settings(directory / "recording", None, (), threads=4)
        application = create_app(settings)
        recording = Repository(application.state.store, workspace_id(key))
        published = Repository(LocalStore(directory / "published"), "public-examples")
        with TestClient(application, headers={"X-Workspace-Key": key}) as client:
            def call(method, path, **kwargs):
                response = client.request(method, "/api"+path, **kwargs)
                response.raise_for_status()
                return response

            def publish(route, relative, data):
                path = stage / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                manifest["files"][route] = {"url": "/demo/"+relative,
                                             "sha256": digest(data), "bytes": len(data)}

            for sample_id, sample in SAMPLES.items():
                print(f"Recording {sample_id}: original and localized brightness revision", flush=True)
                project = call("POST", f"/samples/{sample_id}").json()
                original = project["assets"][0]
                seed_public_cache(recording, original, sample_id)
                before = call("POST", f"/assets/{original['id']}/analyze").json()
                primary = sample["targets"][0]
                revision = call("POST", f"/assets/{original['id']}/adjust", json={
                    "label": f"Brighter {primary['label'].lower()}", "brightness": 1.2,
                    "target_id": primary["id"]}).json()
                call("PUT", f"/assets/{revision['id']}/targets", json={
                    "targets": revision["targets"], "confirmed": True})
                if sample_id == "forma":
                    seed_public_cache(recording, revision, "forma-brighter-products")
                after = call("POST", f"/assets/{revision['id']}/analyze").json()
                ids = {project["id"]: public_id(sample_id),
                       original["id"]: public_id(sample_id+"/original"),
                       revision["id"]: public_id(sample_id+"/revision"),
                       before["id"]: public_id(sample_id+"/original-run"),
                       after["id"]: public_id(sample_id+"/revision-run")}
                saved = call("GET", f"/projects/{project['id']}").json()
                public = normalize(saved, ids)
                published.save("projects", {k: v for k, v in public.items() if k not in {"assets", "runs"}})
                for asset in saved["assets"]:
                    data = call("GET", f"/assets/{asset['id']}/image").content
                    asset_id = ids[asset["id"]]
                    published.save("assets", normalize(asset, ids))
                    published.store.put(published.key("assets", asset_id, "image.png"), data, "image/png")
                    publish(f"/assets/{asset_id}/image", f"assets/{asset_id}.png", data)
                for run in saved["runs"]:
                    assert run["status"] == "completed" and run["model"] == manifest["model"]
                    run_id = ids[run["id"]]
                    published.save("runs", normalize(run, ids))
                    for artifact in ("heatmap.png", "overlay.png"):
                        data = call("GET", f"/runs/{run['id']}/{artifact}").content
                        published.store.put(published.key("runs", run_id, artifact), data, "image/png")
                        publish(f"/runs/{run_id}/{artifact}", f"runs/{run_id}/{artifact}", data)
                    publish(f"/runs/{run_id}/report.json", f"runs/{run_id}/report.json",
                            (json.dumps(normalize(run, ids), indent=2)+"\n").encode())
                project_id = ids[project["id"]]
                publish(f"/projects/{project_id}/export", f"projects/{project_id}.zip",
                        project_archive(published, project_id))
                manifest["projects"].append(public)
                manifest["samples"][sample_id] = project_id
                print(f"{sample_id}: {before['metrics']['attention_share']:.6f} -> {after['metrics']['attention_share']:.6f}", flush=True)
        serialized = json.dumps(manifest, indent=2, allow_nan=False)+"\n"
        assert key not in serialized
        (stage / "manifest.json").write_text(serialized)
        # Stable public IDs keep deep links and generated paths consistent.
        shutil.copytree(stage, OUT, dirs_exist_ok=True)
    print(f"Published {len(manifest['projects'])} examples, 6 completed analyses, {len(manifest['files'])} artifacts.", flush=True)


if __name__ == "__main__":
    main()
