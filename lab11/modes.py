"""Part D: name the failure. TODO 8."""
from __future__ import annotations

from avsim import core


def label_mode(R: core.Rollout, k: int, event: dict, contact_type) -> str:
    """TODO 8. Name the kind of failure behind one ego failure event."""
    other = event["b"] if event["a"] == "ego" else event["a"]
    if other == "P1" or event.get("kind") == "block":
        return "crosswalk_block"
    if contact_type(R, k, event) == "rear":
        return "rear_ended"
    if other == "C2":
        f = event["f"]
        c2_state = R.F[k, f, core.IX["C2"]]
        x_c2 = c2_state[0]
        v_c2 = c2_state[4]
        if x_c2 < 112.0 and v_c2 < 6.0:
            return "bus_bypass"
        return "cut_in"
    return "other"
