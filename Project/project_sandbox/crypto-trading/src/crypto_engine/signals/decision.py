"""Deterministic decision pieces that ARE emitted in v1: regime.trend +
levels.invalidation (doc/03 §4 trend derivation, §5 invalidation).

The playbook -> plan mapping (§4 table) lives in the LLM/plan layer (plan = null
in v1), so it is intentionally not computed here.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..config import EngineConfig
from ..contract import Invalidation
from ..features.structure import Pivot, recent_swing

STAND_ASIDE = "stand-aside"


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


# ---------- playbook decision table (doc/03 §4) — deterministic, not LLM prose ----------
@dataclass
class PlaybookDecision:
    playbook: str
    entry_source: str   # "nearest resistance" | "nearest support" | "range edges" | "watch" | "none"
    reason: str


def select_playbook(
    trend: str,          # up | down | sideways  (regime.trend)
    direction: str,      # long | short | neutral (bias.direction)
    conviction: str,     # low | medium | high
    vol: str,            # expansion | contraction | normal
    confidence: float,
    cfg: EngineConfig,
) -> PlaybookDecision:
    """Map (trend, direction, conviction, vol) -> playbook per the doc/03 §4 table.

    Caveat surface #3: confidence < confidence.floor forces stand-aside (wires the
    previously-dead `confidence.floor` knob). Baked-in discipline: no counter-trend,
    low conviction -> stand-aside, range+expansion -> stand-aside.
    """
    floor = cfg.confidence.floor
    if confidence < floor:
        return PlaybookDecision(STAND_ASIDE, "none", f"confidence {round(confidence, 4)} < floor {floor}")

    if direction == "neutral":
        return PlaybookDecision(STAND_ASIDE, "none", "neutral bias")

    strong = conviction in ("medium", "high")

    if trend == "up":
        if direction == "long":
            if strong:
                return PlaybookDecision("buy-the-dip (trend-following)", "nearest support", "uptrend + conviction")
            return PlaybookDecision("stand-aside / wait-pullback", "none", "uptrend but low conviction")
        return PlaybookDecision(STAND_ASIDE, "none", "no counter-trend (short in uptrend)")

    if trend == "down":
        if direction == "short":
            if strong:
                return PlaybookDecision("sell-the-rip (trend-following)", "nearest resistance", "downtrend + conviction")
            return PlaybookDecision("stand-aside / wait-pullback", "watch", "downtrend but low conviction")
        return PlaybookDecision(STAND_ASIDE, "none", "no counter-trend (long in downtrend)")

    # trend == sideways (range)
    if vol == "contraction":
        return PlaybookDecision("range-fade", "range edges", "range + contraction")
    if vol == "expansion":
        return PlaybookDecision("stand-aside (breakout pending)", "await break", "range + expansion")
    return PlaybookDecision(STAND_ASIDE, "none", "range, normal vol — no edge")


# ---------- position sizing (deterministic risk-based) ----------
@dataclass
class PositionSize:
    qty: float
    notional: float
    leverage: float
    risk_amount: float
    stop_distance: float
    note: str


def position_size(entry: float | None, stop: float | None, cfg: EngineConfig) -> PositionSize | None:
    """qty = (risk_pct × equity) / stop_distance, capped at max_leverage × equity notional."""
    sc = cfg.sizing
    if not sc.enabled or entry is None or stop is None:
        return None
    stop_distance = abs(float(entry) - float(stop))
    if stop_distance <= 0 or entry <= 0:
        return None
    risk_amount = sc.risk_pct * sc.equity
    qty = risk_amount / stop_distance
    notional = qty * entry
    cap = sc.max_leverage * sc.equity
    capped = notional > cap
    if capped:
        qty = cap / entry
        notional = cap
    leverage = notional / sc.equity if sc.equity else 0.0
    qty = round(qty, sc.round_qty)
    note = (
        f"risk {sc.risk_pct * 100:.1f}% (~{risk_amount:.0f}) / stop dist {stop_distance:.2f} "
        f"-> {qty} @ {entry:.2f} (notional {notional:.0f}, {leverage:.2f}x{' capped' if capped else ''})"
    )
    return PositionSize(qty=qty, notional=round(notional, 2), leverage=round(leverage, 4),
                        risk_amount=round(risk_amount, 2), stop_distance=round(stop_distance, 2), note=note)


def entry_from_source(entry_source: str, support: list[float], resistance: list[float],
                      close: float) -> tuple[list[float] | None, float | None]:
    """Derive an entry zone + a representative entry price from the playbook's source."""
    if entry_source == "nearest support":
        px = support[0] if support else close
        return [px], px
    if entry_source == "nearest resistance":
        px = resistance[0] if resistance else close
        return [px], px
    if entry_source == "range edges":
        edges = [x for x in (support[0] if support else None, resistance[0] if resistance else None) if x is not None]
        if not edges:
            return [close], close
        return sorted(edges), edges[0]
    return None, None  # watch / await break / none -> no position
