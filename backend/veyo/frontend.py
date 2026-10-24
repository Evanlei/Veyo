"""Serve the production interface alongside the API on one origin."""
import re
from pathlib import Path
from starlette.exceptions import HTTPException
from starlette.staticfiles import StaticFiles


class FrontendFiles(StaticFiles):
    async def get_response(self, path, scope):
        # Reserve the API namespace even if a build accidentally contains it.
        if path == "api" or path.startswith("api/"):
            raise HTTPException(404)
        try:
            response = await super().get_response(path, scope)
        except HTTPException as exc:
            # Only application routes receive the SPA shell. Missing scripts,
            # arbitrary files and traversal attempts must remain real 404s.
            is_view = path in (".", "", "guide", "settings") or re.fullmatch(
                r"(?:creative|compare)/[A-Za-z0-9_-]+", path
            )
            if exc.status_code != 404 or not is_view or scope["method"] not in ("GET", "HEAD"):
                raise
            response = await super().get_response("index.html", scope)
        if response.status_code == 200:
            response.headers["Cache-Control"] = (
                "public, max-age=31536000, immutable" if path.startswith("assets/") else "no-cache"
            )
        return response


def mount_frontend(app, directory: Path | None):
    if directory is not None and (directory / "index.html").is_file():
        # Register last so /api routes and their authentication always win.
        app.mount("/", FrontendFiles(directory=directory, html=True), name="frontend")
