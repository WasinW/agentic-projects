"""Confluence scoring + bias + confidence (doc/03 §3 — LOCKED formula).

    score[v] = Σ(weight where vote==v) / Σ(weights of PRESENT signals)

`neutral` is its own bucket. bias.direction = argmax; conviction from the winning
margin. confidence = max_score × macro factor (technical subordinate to macro/ETF
flow). timeframe_alignment is read from the per-TF structure votes.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..config import EngineConfig
from ..contract import Bias, ConfluenceScore, Signal

MACRO_CAVEAT = "technical subordinate to macro/ETF flow — confidence haircut applied"
NOT_ADVICE = "decision-support only — not investment advice"


@dataclass
class ConfluenceResult:
    score: ConfluenceScore
    bias: Bias
    confidence: float
    margin: float
    caveats: list[str]


def confluence_score(signals: list[Signal]) -> ConfluenceScore:
    total = sum(s.weight for s in signals)
    if total <= 0:
        return ConfluenceScore(long=0.0, short=0.0, neutral=1.0)
    buckets = {"long": 0.0, "short": 0.0, "neutral": 0.0}
    for s in signals:
        buckets[s.vote] += s.weight
    return ConfluenceScore(
        long=round(buckets["long"] / total, 4),
        short=round(buckets["short"] / total, 4),
        neutral=round(buckets["neutral"] / total, 4),
    )


def _conviction(margin: float, cfg: EngineConfig) -> str:
    c = cfg.signals.conviction
    if margin > c.high_margin:
        return "high"
    if margin >= c.medium_margin:
        return "medium"
    return "low"


def derive(
    signals: list[Signal],
    structure_by_tf: dict[str, str],
    analysis_tfs: list[str],
    cfg: EngineConfig,
) -> ConfluenceResult:
    score = confluence_score(signals)
    ranked = sorted(
        [("long", score.long), ("short", score.short), ("neutral", score.neutral)],
        key=lambda kv: kv[1],
        reverse=True,
    )
    direction = ranked[0][0]
    margin = round(ranked[0][1] - ranked[1][1], 4)
    conviction = _conviction(margin, cfg)

    # per-TF alignment from structure votes
    vote_map = {"HH/HL": "long", "LH/LL": "short"}
    alignment = {tf: vote_map.get(structure_by_tf.get(tf, "mixed"), "neutral") for tf in analysis_tfs}

    bias = Bias(direction=direction, conviction=conviction, timeframe_alignment=alignment)

    confidence = round(ranked[0][1] * cfg.macro_regime.factor, 4)
    caveats = [NOT_ADVICE]
    if cfg.macro_regime.active != "aligned":
        caveats.insert(0, MACRO_CAVEAT)

    return ConfluenceResult(
        score=score, bias=bias, confidence=confidence, margin=margin, caveats=caveats
    )
