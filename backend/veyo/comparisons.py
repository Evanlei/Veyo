"""Compare completed runs within one project using explicitly named target roles."""
from .repository import Repository


def compare_runs(repo: Repository, before_id: str, after_id: str) -> dict:
    before, after = repo.get("runs", before_id), repo.get("runs", after_id)
    if before["project_id"] != after["project_id"]:
        raise ValueError("Choose two analyses from the same project.")
    if before["status"] != "completed" or after["status"] != "completed":
        raise ValueError("Both analyses must be complete before comparing.")
    if before["model"] != after["model"]:
        raise ValueError("These analyses used different model settings. Analyze both again.")
    right = {(t["role"], t["label"].casefold()): t for t in after["metrics"]["targets"]}
    pairs = []
    for target in before["metrics"]["targets"]:
        match = right.get((target["role"], target["label"].casefold()))
        if match:
            pairs.append({"label": target["label"], "role": target["role"],
                          "before": target, "after": match,
                          "delta_pp": (match["attention_share"]-target["attention_share"])*100,
                          "relative_delta": match["relative_attention"]-target["relative_attention"]})
    if not pairs:
        raise ValueError("No matching targets. Use the same label and role for corresponding elements.")
    return {"before": before, "after": after, "targets": pairs,
            "same_dimensions": (before["width"], before["height"]) == (after["width"], after["height"]),
            "note": "Compare corresponding elements. Different target areas affect raw attention shares."}
