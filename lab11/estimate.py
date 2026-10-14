"""Part C: estimate a rare probability honestly. TODO 4, 6 and 7."""
from __future__ import annotations

import math

import numpy as np

from avsim import space
from .search import proposal_logpdf


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """TODO 4. Wilson score interval for k successes in n trials."""
    if n == 0:
        return 0.0, 1.0
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half_width = (z / denom) * math.sqrt(p * (1.0 - p) / n + (z * z) / (4.0 * n * n))
    lo = max(0.0, center - half_width)
    hi = min(1.0, center + half_width)
    return lo, hi


def log_weights(Z, Bn, nat: space.Natural, prop: dict, beta: float = 0.2) -> np.ndarray:
    """TODO 6. log p(u) - log q(u) for each row, where q is the DEFENSIVE MIXTURE
    q = (1 - beta) * proposal + beta * natural."""
    log_p = nat.logpdf(Z, Bn)
    log_prop = proposal_logpdf(prop, Z, Bn)
    log_q = np.logaddexp(math.log(1.0 - beta) + log_prop, math.log(beta) + log_p)
    return log_p - log_q


def is_estimate(logw: np.ndarray, y: np.ndarray, z: float = 1.96) -> dict:
    """TODO 7. Importance-sampling estimate of P(y = 1) under the natural distribution."""
    n = len(logw)
    w = np.exp(logw)
    wy = w * y
    p = float(np.mean(wy))
    se = float(np.std(wy, ddof=1) / math.sqrt(n)) if n > 1 else 0.0
    lo = float(max(0.0, p - z * se))
    hi = float(p + z * se)
    sum_w = float(np.sum(w))
    sum_w2 = float(np.sum(w ** 2))
    ess = float((sum_w ** 2) / sum_w2) if sum_w2 > 0 else 0.0
    return dict(p=p, lo=lo, hi=hi, se=se, ess=ess, n=n)


def rule_of_three(n_eff: float) -> float:
    """Given: 95% upper bound on a probability when 0 events were seen in n_eff independent tries."""
    return 3.0 / max(n_eff, 1.0)
