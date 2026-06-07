"""⚙️ DETERMINISTIC combo scorer (07 §3 weighted formula, $0 token).

    score = 0.30·trend + 0.25·fit + 0.20·lift + 0.10·recency + 0.10·season − fatigue

Every term normalized to 0..1; fatigue subtracts. This is a Scorer seam impl — swap
for an ML ranker later by registering another class (defer until data is rich, 07 §4).
"""
from __future__ import annotations

from app.core.adapters import ScoreResult
from app.core.models import Combo

WEIGHTS = {"trend": 0.30, "fit": 0.25, "lift": 0.20, "recency": 0.10, "season": 0.10}


class ComboScorer:
    name = "zscore"

    def score(self, combo: Combo, ctx: dict) -> ScoreResult:
        # ctx terms are precomputed deterministic signals (all 0..1):
        trend = float(ctx.get("trend", 0.0))      # from trend.trend_signal(z)
        fit = float(ctx.get("fit", 0.0))          # cosine(product_emb, account_emb)
        lift = float(ctx.get("lift", 0.0))        # historical perf lift of this combo
        recency = float(ctx.get("recency", 0.0))  # data freshness
        season = float(ctx.get("season", 0.0))    # seasonal/calendar relevance
        fatigue = float(ctx.get("fatigue", 0.0))  # posted-recently penalty

        total = (
            WEIGHTS["trend"] * trend
            + WEIGHTS["fit"] * fit
            + WEIGHTS["lift"] * lift
            + WEIGHTS["recency"] * recency
            + WEIGHTS["season"] * season
            - fatigue
        )
        total = max(0.0, min(1.0, total))
        return ScoreResult(
            total=round(total, 4),
            breakdown={
                "trend": round(trend, 4), "fit": round(fit, 4), "lift": round(lift, 4),
                "recency": round(recency, 4), "season": round(season, 4),
                "fatigue": round(fatigue, 4), "total": round(total, 4),
            },
        )


def cosine(a: list[float], b: list[float]) -> float:
    """0..1 cosine similarity (vectors are unit-norm from the embedder)."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    return max(0.0, min(1.0, (dot + 1) / 2))   # map [-1,1] -> [0,1]
