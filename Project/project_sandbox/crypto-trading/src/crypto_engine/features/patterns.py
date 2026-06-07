"""Single-bar / two-bar candle patterns on the last closed bar.

Detection returns the pattern name + its inherent direction. The *context
filter* (must sit at a relevant swing level) is applied in the signal layer,
where support/resistance is available — a pattern mid-range is noise (spec §1.4).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class PatternHit:
    name: str           # "bullish_engulfing" | "hammer" | ... | "none"
    direction: str      # "bullish" | "bearish" | "neutral"


def _body(o: float, c: float) -> float:
    return abs(c - o)


def detect_last(df: pd.DataFrame, enabled: list[str] | None = None) -> PatternHit:
    """Detect the highest-information pattern on the last closed bar."""
    if len(df) < 2:
        return PatternHit("none", "neutral")
    enabled = enabled or ["engulfing", "hammer", "shooting_star", "doji"]

    o, h, lo, c = (float(df[k].iloc[-1]) for k in ("open", "high", "low", "close"))
    po, pc = float(df["open"].iloc[-2]), float(df["close"].iloc[-2])

    rng = max(h - lo, 1e-12)
    body = _body(o, c)
    upper = h - max(o, c)
    lower = min(o, c) - lo

    # --- engulfing (two-bar) ---
    if "engulfing" in enabled:
        prev_red, prev_green = pc < po, pc > po
        if prev_red and c > o and c >= po and o <= pc:
            return PatternHit("bullish_engulfing", "bullish")
        if prev_green and c < o and c <= po and o >= pc:
            return PatternHit("bearish_engulfing", "bearish")

    # --- hammer (long lower wick, small body near top) ---
    if "hammer" in enabled and body > 0:
        if lower >= 2 * body and upper <= body and body <= 0.4 * rng:
            return PatternHit("hammer", "bullish")

    # --- shooting star (long upper wick, small body near bottom) ---
    if "shooting_star" in enabled and body > 0:
        if upper >= 2 * body and lower <= body and body <= 0.4 * rng:
            return PatternHit("shooting_star", "bearish")

    # --- doji (very small body) ---
    if "doji" in enabled and body <= 0.1 * rng:
        return PatternHit("doji", "neutral")

    return PatternHit("none", "neutral")
