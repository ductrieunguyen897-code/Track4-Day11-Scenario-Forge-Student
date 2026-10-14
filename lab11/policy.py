"""Part E: choose a policy honestly. TODO 10."""
from __future__ import annotations


def choose_policy(table: list[dict], baseline_progress: float, max_loss: float = 0.05):
    """TODO 10. Return row with lowest fail_hi among rows keeping >= (1 - max_loss) * baseline_progress."""
    min_prog = (1.0 - max_loss) * baseline_progress
    candidates = [r for r in table if r.get("progress", 0.0) >= min_prog]
    if not candidates:
        return None
    return min(candidates, key=lambda r: (r["fail_hi"], -r["progress"]))
