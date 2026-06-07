"""Signal registry: raw feature readings -> list[Signal] (name, value, vote, weight).

Conforms to doc/03-signal-logic-spec.md §1-§2. A signal whose reading is missing
(NaN / insufficient data) is ABSENT (omitted) so the confluence denominator
self-adjusts. `vol_regime` has weight 0 (context only). Elliott is emitted only
when cfg.elliott.enabled (v2).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from ..config import EngineConfig
from ..contract import Signal


@dataclass
class CandleReading:
    direction: str          # bullish | bearish | neutral
    name: str               # pattern name
    near_support: bool
    near_resistance: bool


@dataclass
class SignalInputs:
    rsi_by_tf: dict[str, float]          # may contain NaN -> absent
    structure_by_tf: dict[str, str]      # HH/HL | LH/LL | mixed
    ma_stack_label: str                  # bullish | bearish | mixed
    vol_regime_label: str                # expansion | contraction | normal
    price_dist: float                    # (close-MA20)/ATR
    candle: CandleReading                # for the candle TF
    candle_tf: str                       # e.g. "1d"


def _vote_rsi(v: float, oversold: float, overbought: float) -> str:
    if v >= overbought:
        return "short"
    return "neutral"  # oversold -> neutral (no knife-catch in v1)


def _vote_structure(label: str) -> str:
    return {"HH/HL": "long", "LH/LL": "short"}.get(label, "neutral")


def _vote_ma_stack(label: str) -> str:
    return {"bullish": "long", "bearish": "short"}.get(label, "neutral")


def _vote_price_dist(dist: float, stretch: float) -> str:
    if dist >= stretch:
        return "short"          # overextended above -> fade
    return "neutral"            # overextended below -> neutral (not long in v1)


def _vote_candle(c: CandleReading) -> str:
    if c.direction == "bullish" and c.near_support:
        return "long"
    if c.direction == "bearish" and c.near_resistance:
        return "short"
    return "neutral"


def build_signals(inp: SignalInputs, cfg: EngineConfig) -> list[Signal]:
    weights = cfg.signals.weights
    rsi_cfg = cfg.features.rsi
    out: list[Signal] = []

    def add(name: str, value, vote: str):
        if name in weights:
            out.append(Signal(name=name, value=value, vote=vote, weight=weights[name]))

    # RSI per TF
    for tf, v in inp.rsi_by_tf.items():
        name = f"rsi_{tf}"
        if name in weights and v is not None and not math.isnan(v):
            add(name, round(float(v), 2), _vote_rsi(v, rsi_cfg.oversold, rsi_cfg.overbought))

    # MA stack (anchor TF)
    add("ma_stack", inp.ma_stack_label, _vote_ma_stack(inp.ma_stack_label))

    # Structure per TF
    for tf, label in inp.structure_by_tf.items():
        add(f"structure_{tf}", label, _vote_structure(label))

    # Price vs MA distance (overextension)
    add("price_vs_ma_dist", round(inp.price_dist, 2), _vote_price_dist(inp.price_dist, cfg.features.price_dist.stretch))

    # Candle pattern (context-filtered)
    add(f"candle_pattern_{inp.candle_tf}", inp.candle.name, _vote_candle(inp.candle))

    # Volatility regime — context only, always neutral, weight 0
    add("vol_regime", inp.vol_regime_label, "neutral")

    # Elliott (v2) — absent unless enabled
    # (intentionally not added in v1; handled by LLM layer later)

    return out
