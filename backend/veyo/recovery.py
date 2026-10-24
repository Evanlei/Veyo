"""Surface interrupted analyses without pretending they are still executing."""
from datetime import datetime, timezone


def recover_interrupted_runs(repo, runs, max_age_seconds=900, current=None):
    current = current or datetime.now(timezone.utc)
    for run in runs:
        if run["status"] == "running" and (current-datetime.fromisoformat(run["created_at"])).total_seconds() > max_age_seconds:
            run.update(status="failed", completed_at=current.isoformat(),
                       error="This analysis was interrupted. Run it again to generate a prediction.")
            repo.save("runs", run)
    return runs
