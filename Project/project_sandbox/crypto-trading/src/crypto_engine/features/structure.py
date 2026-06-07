"""Swing structure, pivots, support/resistance, volatility regime.

Pivots use a symmetric fractal: a bar is a pivot high if its high is the strict
max over `lookback` bars on each side (so the last `lookback` bars are not yet
confirmed). Swing label compares the two most recent confirmed highs and lows.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class Pivot:
    idx: int
    timestamp: int
    price: float
    kind: str  # "high" | "low"


def find_pivots(df: pd.DataFrame, lookback: int = 3) -> list[Pivot]:
    """Confirmed fractal pivots. Needs `lookback` bars each side."""
    highs = df["high"].to_numpy(dtype=float)
    lows = df["low"].to_numpy(dtype=float)
    ts = df["timestamp"].to_numpy()
    n = len(df)
    out: list[Pivot] = []
    for i in range(lookback, n - lookback):
        win_h = highs[i - lookback : i + lookback + 1]
        win_l = lows[i - lookback : i + lookback + 1]
        if highs[i] == win_h.max() and (win_h.argmax() == lookback):
            out.append(Pivot(i, int(ts[i]), float(highs[i]), "high"))
        elif lows[i] == win_l.min() and (win_l.argmin() == lookback):
            out.append(Pivot(i, int(ts[i]), float(lows[i]), "low"))
    return out


def classify_structure(pivots: list[Pivot], swing_count: int = 4) -> str:
    """Return 'HH/HL' (long), 'LH/LL' (short), or 'mixed'."""
    if len(pivots) < 2:
        return "mixed"
    recent = pivots[-swing_count:] if swing_count > 0 else pivots
    highs = [p for p in recent if p.kind == "high"]
    lows = [p for p in recent if p.kind == "low"]
    if len(highs) < 2 or len(lows) < 2:
        # widen to all pivots if the recent window lacks a pair
        highs = [p for p in pivots if p.kind == "high"][-2:]
        lows = [p for p in pivots if p.kind == "low"][-2:]
    if len(highs) < 2 or len(lows) < 2:
        return "mixed"
    hh = highs[-1].price > highs[-2].price
    hl = lows[-1].price > lows[-2].price
    lh = highs[-1].price < highs[-2].price
    ll = lows[-1].price < lows[-2].price
    if hh and hl:
        return "HH/HL"
    if lh and ll:
        return "LH/LL"
    return "mixed"


def _cluster(levels: list[float], tol: float) -> list[float]:
    """Merge levels within `tol` (absolute price) into their mean."""
    if not levels:
        return []
    levels = sorted(levels)
    clusters: list[list[float]] = [[levels[0]]]
    for x in levels[1:]:
        if abs(x - clusters[-1][-1]) <= tol:
            clusters[-1].append(x)
        else:
            clusters.append([x])
    return [float(np.mean(c)) for c in clusters]


def support_resistance(
    df: pd.DataFrame,
    pivots: list[Pivot],
    atr_last: float,
    ma_levels: list[float] | None = None,
    cluster_atr_mult: float = 0.5,
    max_support: int = 3,
    max_resistance: int = 3,
) -> tuple[list[float], list[float]]:
    """Support/resistance nearest-first relative to the last close.

    Pool = confirmed pivots + (optional) MA levels. Clustered by ATR distance,
    split around current price, returned nearest-first.
    """
    close = float(df["close"].iloc[-1])
    tol = max(atr_last * cluster_atr_mult, 1e-9) if not np.isnan(atr_last) else 0.0
    pool = [p.price for p in pivots] + list(ma_levels or [])
    merged = _cluster(pool, tol)

    support = sorted([x for x in merged if x < close], reverse=True)[:max_support]
    resistance = sorted([x for x in merged if x > close])[:max_resistance]
    return [round(x, 2) for x in support], [round(x, 2) for x in resistance]


def vol_regime(
    atr_series: pd.Series, lookback: int = 100, expansion_mult: float = 1.5, contraction_mult: float = 0.7
) -> str:
    """'expansion' | 'contraction' | 'normal' from ATR vs its rolling median."""
    s = atr_series.dropna()
    if len(s) < 2:
        return "normal"
    window = min(lookback, len(s))
    median = float(s.tail(window).median())
    last = float(s.iloc[-1])
    if median <= 0:
        return "normal"
    if last >= expansion_mult * median:
        return "expansion"
    if last <= contraction_mult * median:
        return "contraction"
    return "normal"


def price_vs_ma_dist(close_last: float, ma20_last: float, atr_last: float) -> float:
    """(close - MA20) / ATR — overextension in ATR units. NaN-safe -> 0.0."""
    if np.isnan(ma20_last) or np.isnan(atr_last) or atr_last == 0:
        return 0.0
    return float((close_last - ma20_last) / atr_last)


def recent_swing(pivots: list[Pivot], kind: str) -> Pivot | None:
    for p in reversed(pivots):
        if p.kind == kind:
            return p
    return None
