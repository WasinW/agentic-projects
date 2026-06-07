"""Deterministic decision pieces that ARE emitted in v1: regime.trend +
levels.invalidation (doc/03 §4 trend derivation, §5 invalidation).

The playbook -> plan mapping (§4 table) lives in the LLM/plan layer (plan = null
in v1), so it is intentionally not computed here.
"""

from __future__ import annotations

from ..config import EngineConfig
from ..contract import Invalidation
from ..features.structure import Pivot, recent_swing


def derive_trend(ma_stack_label: str, structure_1d: str) -> str:
    """Trend for regime.trend (contract: up | down | sideways)."""
    if ma_stack_label == "bullish" and structure_1d == "HH/HL":
        return "up"
    if ma_stack_label == "bearish" and structure_1d == "LH/LL":
        return "down"
    return "sideways"


def compute_invalidation(
    direction: str,
    pivots: list[Pivot],
    atr_last: float,
    current_price: float,
    vol_regime: str,
    cfg: EngineConfig,
) -> Invalidation:
    """Invalidation price + rule by bias direction (doc/03 §5)."""
    inv = cfg.invalidation
    buffer = atr_last * inv.atr_mult if atr_last and atr_last > 0 else 0.0
    if vol_regime == "expansion":
        buffer *= inv.expansion_widen
    min_dist = (atr_last * inv.min_atr_dist) if atr_last and atr_last > 0 else 0.0
    confirm = inv.confirm.replace("_", " ")  # "weekly close"

    swing_high = recent_swing(pivots, "high")
    swing_low = recent_swing(pivots, "low")

    if direction == "short":
        base = swing_high.price if swing_high else current_price
        price = base + buffer
        # consistency + ATR floor: must sit ABOVE current price by >= min_dist
        price = max(price, current_price + min_dist)
        rule = f"{confirm} above {round(price, 2)} flips bias"

    elif direction == "long":
        base = swing_low.price if swing_low else current_price
        price = base - buffer
        price = min(price, current_price - min_dist)
        rule = f"{confirm} below {round(price, 2)} flips bias"

    else:  # neutral / range -> opposite range boundary (use nearest swing high)
        base = swing_high.price if swing_high else current_price + min_dist
        price = base + buffer
        price = max(price, current_price + min_dist)
        rule = f"{confirm} beyond range boundary {round(price, 2)} voids range thesis"

    return Invalidation(price=round(price, 2), rule=rule)


def regime_note(
    ma_stack_label: str, ma_values: dict[str, float], rsi_anchor: float, oversold: float, overbought: float
) -> str:
    parts = []
    if ma_stack_label == "bearish":
        parts.append("below MA stack")
    elif ma_stack_label == "bullish":
        parts.append("above MA stack")
    else:
        parts.append("price tangled in MA stack")
    if rsi_anchor is not None:
        if rsi_anchor <= oversold:
            parts.append("oversold")
        elif rsi_anchor >= overbought:
            parts.append("overbought")
        else:
            parts.append(f"RSI {round(rsi_anchor)}")
    return ", ".join(parts)


def structure_text(structure_1d: str) -> str:
    return {
        "HH/HL": "higher-highs / higher-lows",
        "LH/LL": "lower-highs / lower-lows",
    }.get(structure_1d, "mixed / no clear structure")
