from fastapi import APIRouter
from .dependencies import Repo
from .comparisons import compare_runs
from .schemas import ComparisonRequest

router = APIRouter(prefix="/api/comparisons", tags=["comparisons"])


@router.post("")
def compare(comparison: ComparisonRequest, repo: Repo):
    return compare_runs(repo, comparison.before_run_id, comparison.after_run_id)
