"""Anonymous workspace capability keys; only a one-way digest is persisted."""
import hashlib
import re
from fastapi import Header, HTTPException


def workspace_id(key: str) -> str:
    if not re.fullmatch(r"[a-f0-9]{64}", key):
        raise ValueError("A valid workspace key is required.")
    return hashlib.sha256(key.encode()).hexdigest()


def require_workspace(x_workspace_key: str = Header(default="")) -> str:
    try:
        return workspace_id(x_workspace_key)
    except ValueError as exc:
        raise HTTPException(401, str(exc)) from exc
