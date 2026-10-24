"""Atomic local object persistence. Object keys never contain user filenames."""
from __future__ import annotations
import json
import os
from pathlib import Path, PurePosixPath
import tempfile


def safe_key(key: str) -> str:
    p = PurePosixPath(key)
    if not key or p.is_absolute() or ".." in p.parts or "\\" in key:
        raise ValueError("Invalid storage key.")
    return str(p)


class LocalStore:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, key: str, data: bytes, content_type="application/octet-stream"):
        path = self.root / safe_key(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp = tempfile.mkstemp(dir=path.parent, prefix=".write-")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp, path)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)

    def get(self, key: str) -> bytes:
        return (self.root / safe_key(key)).read_bytes()

    def keys(self, prefix: str) -> list[str]:
        base = self.root / safe_key(prefix)
        if not base.exists():
            return []
        return sorted(str(p.relative_to(self.root).as_posix()) for p in base.rglob("*")
                      if p.is_file() and not p.name.startswith(".write-"))

    def delete(self, key: str):
        (self.root / safe_key(key)).unlink(missing_ok=True)

    def json(self, key: str) -> dict:
        return json.loads(self.get(key))

    def put_json(self, key: str, value: dict):
        self.put(key, (json.dumps(value, allow_nan=False) + "\n").encode(), "application/json")
