"""Workspace-scoped records. UUID resources keep analysis history immutable."""
from datetime import datetime, timezone
import re
from uuid import uuid4


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    return uuid4().hex


class Repository:
    def __init__(self, store, workspace: str):
        self.store = store
        self.prefix = f"workspaces/{workspace}"

    def key(self, category: str, identity: str, filename="record.json") -> str:
        if category not in {"projects", "assets", "runs"} or not re.fullmatch(r"[a-f0-9]{32}", identity):
            raise FileNotFoundError("Record not found.")
        return f"{self.prefix}/{category}/{identity}/{filename}"

    def get(self, category: str, identity: str) -> dict:
        return self.store.json(self.key(category, identity))

    def save(self, category: str, record: dict) -> dict:
        self.store.put_json(self.key(category, record["id"]), record)
        return record

    def list(self, category: str, project_id: str | None = None) -> list[dict]:
        records = [self.store.json(k) for k in self.store.keys(f"{self.prefix}/{category}")
                   if k.endswith("/record.json")]
        if project_id is not None:
            records = [r for r in records if r.get("project_id") == project_id]
        return sorted(records, key=lambda r: r["created_at"], reverse=True)

    def project(self, project_id: str) -> dict:
        from .recovery import recover_interrupted_runs
        return {**self.get("projects", project_id),
                "assets": self.list("assets", project_id),
                "runs": recover_interrupted_runs(self, self.list("runs", project_id))}

    def create_project(self, name: str) -> dict:
        return self.save("projects", {"id": new_id(), "name": name[:100],
                                     "created_at": now(), "archived": False})

    def create_asset(self, project_id: str, image_data: bytes, width: int, height: int,
                     label: str, provenance: dict, parent_id=None, targets=None) -> dict:
        import hashlib
        self.get("projects", project_id)
        identity = new_id()
        self.store.put(self.key("assets", identity, "image.png"), image_data, "image/png")
        return self.save("assets", {"id": identity, "project_id": project_id,
            "created_at": now(), "label": label[:100], "width": width, "height": height,
            "sha256": hashlib.sha256(image_data).hexdigest(), "parent_id": parent_id,
            "targets": targets or [], "confirmed": False, "provenance": provenance})
