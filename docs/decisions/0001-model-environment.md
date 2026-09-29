# 0001 — Isolate and pin the model experiment environment

Status: Accepted for local feasibility; deployment compatibility remains unverified.
Date: 2026-09-29

Use Python 3.12 and one fresh backend virtual environment. Record direct dependencies separately from the resolved package snapshot, and pin Git dependencies to exact upstream commits resolved during setup.

Why: system Python and globally installed packages are outside project control. Isolation avoids accidental interactions with other projects. A resolved snapshot records what we actually verified; an unpinned install can silently change tomorrow.

Tradeoffs: pip plus venv is sufficient for this increment and adds no separate environment manager. The snapshot is tied to the tested Python/platform combination and lacks wheel hashes. Consider a cross-platform lock workflow when Linux deployment or dependency maintenance requires it. The initial interpreter comes from the bundled runtime, so its continued availability is a local dependency; use a standalone Python 3.12 installation when recreating outside this environment.

DeepGaze's top-level imports include other model families. Install their required import-time dependencies without modifying upstream code. This adds packages we will not directly invoke; choosing an earlier model-specific revision would reduce dependencies but would need its own compatibility review.

No API, database, frontend, pretrained weight download, or inference is part of this change. Successful imports prove packaging compatibility only.
