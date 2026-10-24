"""Verify the published static recording, assets, deep links and downloads over HTTP."""
import argparse
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
from pathlib import Path
import re
from zipfile import ZipFile

import httpx
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", nargs="?", default="https://veyo-attention-studio.web.app")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with httpx.Client(base_url=args.base_url, timeout=30, follow_redirects=True) as client:
        def get(path):
            response = client.get(path)
            response.raise_for_status()
            return response
        home = get("/")
        assert "Veyo — Recorded Attention Demo" in home.text
        assert "frame-ancestors 'none'" in home.headers["content-security-policy"]
        script = re.search(r'src="([^"]+\.js)"', home.text).group(1)
        assert "immutable" in get(script).headers["cache-control"]
        response = get("/demo/manifest.json")
        assert "no-store" in response.headers["cache-control"]
        recording = response.json()
        assert recording["mode"] == "recorded" and recording["version"] == 1
        assert len(recording["projects"]) == 3
        assert recording["model"]["source_commit"] == "c7db17e2d1d7ea6468ffdee2cfaddf141095dcff"
        artifacts = {}
        for route, file in recording["files"].items():
            assert file["url"].startswith("/demo/")
            data = get(file["url"]).content
            assert hashlib.sha256(data).hexdigest() == file["sha256"], route
            assert len(data) == file["bytes"]
            artifacts[route] = data
        totals = []
        for project in recording["projects"]:
            for route in (f"/creative/{project['id']}", f"/compare/{project['id']}"):
                assert "Veyo — Recorded Attention Demo" in get(route).text
            assert len(project["assets"]) == 2 and len(project["runs"]) == 2
            for asset in project["assets"]:
                assert Image.open(BytesIO(artifacts[f"/assets/{asset['id']}/image"])).size == (asset["width"], asset["height"])
            for run in project["runs"]:
                assert run["status"] == "completed" and run["model"] == recording["model"]
                assert json.loads(artifacts[f"/runs/{run['id']}/report.json"])["id"] == run["id"]
                for artifact in ("heatmap.png", "overlay.png"):
                    assert Image.open(BytesIO(artifacts[f"/runs/{run['id']}/{artifact}"])).size == (run["width"], run["height"])
            with ZipFile(BytesIO(artifacts[f"/projects/{project['id']}/export"])) as archive:
                assert json.loads(archive.read("project.json"))["id"] == project["id"]
                assert len([name for name in archive.namelist() if name.startswith("creatives/")]) == 2
                assert len([name for name in archive.namelist() if name.endswith("/overlay.png")]) == 2
            original = next(asset for asset in project["assets"] if not asset["parent_id"])
            before = next(run for run in project["runs"] if run["asset_id"] == original["id"])
            after = next(run for run in project["runs"] if run["asset_id"] != original["id"])
            totals.append({"name": project["name"], "before": before["metrics"]["attention_share"], "after": after["metrics"]["attention_share"]})
        assert any(total["after"] < total["before"] for total in totals)
        for route in ("/guide", "/settings"):
            assert "Veyo — Recorded Attention Demo" in get(route).text
        for route in ("/api/health", "/api/projects", "/assets/missing.js", "/demo/missing.png"):
            assert client.get(route).status_code == 404, route
        report = {"status": "passed", "url": args.base_url, "checked_at": datetime.now(timezone.utc).isoformat(),
                  "projects": 3, "analyses": 6, "verified_artifacts": len(artifacts), "totals": totals,
                  "checks": ["recorded page metadata", "security headers", "static asset cache", "recording revalidation", "all artifact hashes", "canonical image dimensions", "three ZIP downloads", "direct creative and comparison links", "guide and demo details", "unknown resources return 404", "losing revision retained"]}
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(report, indent=2)+"\n")
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
