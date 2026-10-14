"""Part A: read a rollout. TODO 1, 2 and 9 live here; the helpers below them are given."""
from __future__ import annotations

import numpy as np

from avsim import core

G = 9.81
HALF_EGO = core.CAR[0] / 2   # 2.3 m: half the ego's length


def ego_events(R: core.Rollout, k: int) -> list[dict]:
    """Failure events involving the ego in scenario k, earliest first (given).

    event["kind"] is "contact" (the boxes touched) or "block" (the ego's body stopped the pedestrian P1 on the
    crosswalk: pedestrians never walk into a car, so this is how a planner that stops too late fails them)."""
    return [e for e in R.events[k] if e["a"] == "ego" or e["b"] == "ego"]


def min_ttc(R: core.Rollout, cap: float = 10.0) -> np.ndarray:
    """TODO 1. (K,) smallest time-to-collision between the ego and whatever it is following, capped at `cap` s."""
    K, NF = R.F.shape[0], R.F.shape[1]
    EGO = core.IX["ego"]

    x_ego = R.F[:, :, EGO, 0]
    z_ego = R.F[:, :, EGO, 1]
    hx_ego = R.F[:, :, EGO, 2]
    hz_ego = R.F[:, :, EGO, 3]
    v_ego = R.F[:, :, EGO, 4]

    leaders = R.EGO[:, :, 3].astype(int)
    valid = (leaders >= 0) & (leaders < R.F.shape[2])
    safe_leaders = np.where(valid, leaders, 0)

    actor_lens = np.array([a.dims[0] for a in R.actors]) if (hasattr(R, "actors") and R.actors is not None) else core.LEN
    half_len = actor_lens[safe_leaders] / 2.0

    k_idx = np.arange(K)[:, None]
    f_idx = np.arange(NF)[None, :]
    leader_F = R.F[k_idx, f_idx, safe_leaders]

    x_leader = leader_F[..., 0]
    z_leader = leader_F[..., 1]
    v_leader = leader_F[..., 4]

    lon = (x_leader - x_ego) * hx_ego + (z_leader - z_ego) * hz_ego
    gap = np.maximum(lon - 2.3 - half_len, 0.0)

    closing = (v_ego - v_leader) > 0.1
    active = valid & closing

    dv = np.maximum(v_ego - v_leader, 1e-6)
    ttc = np.where(active, gap / dv, np.inf)

    res = np.minimum(cap, np.min(ttc, axis=1))

    for k in range(K):
        if len(ego_events(R, k)) > 0:
            res[k] = 0.0

    return res


def contact_type(R: core.Rollout, k: int, event: dict) -> str:
    """TODO 2. 'front' (the ego ran into it), 'rear' (it ran into the ego) or 'side', at the contact frame."""
    f = event["f"]
    other_id = event["b"] if event["a"] == "ego" else event["a"]
    other_idx = core.IX[other_id] if other_id in core.IX else (R.actor_ix[other_id] if hasattr(R, "actor_ix") else int(other_id))
    ego_idx = core.IX["ego"]

    x_ego, z_ego, hx, hz = R.F[k, f, ego_idx, :4]
    x_other, z_other = R.F[k, f, other_idx, :2]

    rx = x_other - x_ego
    rz = z_other - z_ego

    lon = rx * hx + rz * hz
    lat = -rx * hz + rz * hx

    if lon > 2.3 and abs(lat) < 1.6:
        return "front"
    elif lon < -2.3 and abs(lat) < 1.6:
        return "rear"
    else:
        return "side"


def progress_metrics(R: core.Rollout) -> tuple[np.ndarray, np.ndarray]:
    """TODO 9. Two (K,) arrays: distance covered and count of harsh braking frames."""
    EGO = core.IX["ego"]
    dx = np.diff(R.F[:, :, EGO, 0], axis=1)
    dz = np.diff(R.F[:, :, EGO, 1], axis=1)
    dist = np.sum(np.hypot(dx, dz), axis=1)
    harsh = np.sum(R.F[:, :, EGO, 5] < -3.0, axis=1)
    return dist, harsh


# ---------------------------------------------------------------- given helpers

def pair_min_ttc(R, follower, leader, cap=10.0, lat_max=2.2, leader_vmin=-1.0):
    """(K,) smallest TTC of `follower` running into `leader` while they share a corridor."""
    F = R.F
    a, b = F[:, :, core.IX[follower]], F[:, :, core.IX[leader]]
    rx, rz = b[..., 0] - a[..., 0], b[..., 1] - a[..., 1]
    lon = rx * a[..., 2] + rz * a[..., 3]
    lat = -rx * a[..., 3] + rz * a[..., 2]
    gap = np.maximum(lon - core.LEN[core.IX[follower]] / 2 - core.LEN[core.IX[leader]] / 2, 0.0)
    dv = a[..., 4] - b[..., 4]
    ok = (lon > 0) & (np.abs(lat) < lat_max) & (dv > 0.1) & (b[..., 4] >= leader_vmin)
    ttc = np.where(ok, gap / np.maximum(dv, 1e-6), np.inf)
    return np.minimum(cap, ttc.min(1))


def ped_room(R, cap=30.0):
    """(K,) smallest stopping room [m] left while the crossing pedestrian is in the ego's lane
    (distance to them minus the ego's braking distance at mu*g). Negative = could not have stopped."""
    e, p = R.F[:, :, core.IX["ego"]], R.F[:, :, core.IX["P1"]]
    mu = np.asarray(R.params["mu"])[:, None]
    inlane = np.abs(p[..., 1] - e[..., 1]) < 1.9
    ahead = p[..., 0] - e[..., 0] - HALF_EGO
    room = np.where(inlane & (ahead > -1.0), ahead - e[..., 4] ** 2 / (2 * mu * G), cap)
    return np.clip(room.min(1), -cap, cap)
