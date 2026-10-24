"""Request-scoped repository wiring."""
from typing import Annotated
from fastapi import Depends, Request
from .identity import require_workspace
from .repository import Repository


def repository(request: Request, workspace: Annotated[str, Depends(require_workspace)]):
    return Repository(request.app.state.store, workspace)


Repo = Annotated[Repository, Depends(repository)]
