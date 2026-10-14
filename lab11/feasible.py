"""Part B: physics check. TODO 3."""
from __future__ import annotations

G = 9.81


import math


def is_feasible(p: dict) -> bool:
    """TODO 3. False for scenarios no real road user could produce."""
    mu = p["mu"]
    cut_dur = p["cutDur"]
    a_lat = (math.pi / cut_dur) ** 2 * 3.5 / 2.0
    if a_lat > mu * G:
        return False
    if p["cutBrake"] > mu * G:
        return False
    if p["pedV"] > 2.5:
        return False
    if not (0 < p["cutV"] <= 22):
        return False
    return True
