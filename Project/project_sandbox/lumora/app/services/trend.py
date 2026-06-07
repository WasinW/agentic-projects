"""⚙️ DETERMINISTIC trend detection — z-score per product (07 §3, $0 token).

z = (value - mean) / std across the product population for a metric.
Normalized to 0..1 via a logistic squash for use as the `trend` term in the scorer.
"""
from __future__ import annotations

import math
import statistics


def z_scores(values: dict[str, float]) -> dict[str, float]:
    """product_id -> z-score for one metric."""
    vals = list(values.values())
    if len(vals) < 2:
        return {k: 0.0 for k in values}
    mean = statistics.fmean(vals)
    std = statistics.pstdev(vals) or 1.0
    return {k: (v - mean) / std for k, v in values.items()}


def trend_signal(z: float) -> float:
    """Squash a z-score to 0..1 (logistic). z=0 -> 0.5, z=2 -> ~0.88."""
    return 1.0 / (1.0 + math.exp(-z))
