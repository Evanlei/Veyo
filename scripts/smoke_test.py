"""Exercise a running Veyo release with genuine DeepGaze inference, never test doubles."""
import argparse
from io import BytesIO
import json
from pathlib import Path
import secrets
from zipfile import ZipFile
import httpx
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", nargs="?", default="http://127.0.0.1:5173")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    with httpx.Client(base_url=args.base_url.rstrip("/")+"/api/", timeout=120,
                      headers={"X-Workspace-Key": secrets.token_hex(32)}) as client:
        def call(method, path, **kwargs):
            response = client.request(method, path, **kwargs)
            response.raise_for_status()
            return response
        health = call("GET", "health").json()
        assert health["engine"] == "deepgaze-iie" and not health["fallback"]
        sample = call("POST", "samples/forma").json()
        original = sample["assets"][0]
        before = call("POST", f"assets/{original['id']}/analyze").json()
        assert before["status"] == "completed" and before["model"]["source_commit"]
        revision = call("POST", f"assets/{original['id']}/adjust", json={
            "label": "Product brightness study", "brightness": 1.2, "target_id": "products"}).json()
        call("PUT", f"assets/{revision['id']}/targets", json={"targets": revision["targets"], "confirmed": True})
        after = call("POST", f"assets/{revision['id']}/analyze").json()
        comparison = call("POST", "comparisons", json={"before_run_id": before["id"], "after_run_id": after["id"]}).json()
        assert len(comparison["targets"]) == 3
        for run in [before, after]:
            overlay = call("GET", f"runs/{run['id']}/overlay.png")
            assert Image.open(BytesIO(overlay.content)).size == (original["width"], original["height"])
        # Exercise multipart uploads as well as samples and controlled revisions.
        uploaded = call("POST", f"projects/{sample['id']}/assets", data={"label": "Uploaded revision", "parent_id": original["id"]},
                        files={"image": ("forma.png", (root/"frontend/public/samples/forma.png").read_bytes(), "image/png")}).json()
        assert not uploaded["confirmed"]
        exported = call("GET", f"projects/{sample['id']}/export")
        with ZipFile(BytesIO(exported.content)) as archive:
            assert len([n for n in archive.namelist() if n.startswith("creatives/")]) == 3
            assert len([n for n in archive.namelist() if n.endswith("overlay.png")]) == 2
        # The same URL with another key must not expose the creative.
        response = client.get(f"assets/{original['id']}/image", headers={"X-Workspace-Key": secrets.token_hex(32)})
        assert response.status_code == 404
        report = {"status": "passed", "engine": health["engine"], "model_commit": before["model"]["source_commit"],
                  "baseline_attention_share": before["metrics"]["attention_share"],
                  "revision_attention_share": after["metrics"]["attention_share"],
                  "target_deltas_pp": {t["label"]: t["delta_pp"] for t in comparison["targets"]},
                  "baseline_seconds": before["seconds"], "revision_seconds": after["seconds"],
                  "checks": ["real model", "sample intake", "target confirmation", "controlled adjustment", "multipart upload", "comparison", "aligned overlays", "ZIP export", "workspace isolation"]}
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2)+"\n")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
