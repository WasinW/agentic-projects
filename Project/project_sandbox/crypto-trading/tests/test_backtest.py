"""Backtest harness tests.

Aggregation is tested on hand-built rows (pure, deterministic). The replay is tested
on a small synthetic uptrend (anchor-only) so it stays fast and offline — it exercises
the SAME `engine.deterministic` pipeline the live analyze uses, no re-implementation.
"""

import math

import numpy as np
import pandas as pd

from crypto_engine.backtest.replay import ReplayRow, replay
from crypto_engine.backtest.report import aggregate, to_markdown
from crypto_engine.config import load_config

LABELS = ["1d", "3d", "7d"]
BARS = [1, 3, 7]


def _row(bias, conviction, fwd):
    return ReplayRow(
        idx=0, timestamp=0, date="2024-01-01", close=100.0, bias=bias, conviction=conviction,
        confidence=0.5, score_long=0.0, score_short=0.0, score_neutral=1.0, forward=fwd,
    )


def test_aggregate_directional_hit_rate_and_verdict():
    rows = [
        # short signals that all fell -> should read as negative mean, 100% hit
        _row("short", "high", {"1d": -0.05, "3d": -0.10, "7d": -0.02}),
        _row("short", "high", {"1d": -0.01, "3d": -0.03, "7d": -0.04}),
        # long signals that rose
        _row("long", "medium", {"1d": 0.02, "3d": 0.05, "7d": 0.08}),
        _row("long", "medium", {"1d": 0.01, "3d": -0.01, "7d": 0.03}),
        _row("neutral", "low", {"1d": 0.00, "3d": 0.00, "7d": 0.00}),
    ]
    rep = aggregate(rows, LABELS, BARS, "BTCUSDT", "1d")

    short = next(b for b in rep.buckets if b.label == "short")
    s1 = next(s for s in short.stats if s.horizon == "1d")
    assert s1.n == 2
    assert s1.mean_return < 0
    assert s1.directional_hit_rate == 1.0     # both short signals fell

    long = next(b for b in rep.buckets if b.label == "long")
    l1 = next(s for s in long.stats if s.horizon == "1d")
    assert l1.directional_hit_rate == 1.0     # both long signals rose on 1d

    # neutral bucket has no directional alignment
    neutral = next(b for b in rep.buckets if b.label == "neutral")
    assert all(s.directional_hit_rate is None for s in neutral.stats)

    # verdict: short negative in all horizons, long positive in all -> consistent
    v = rep.verdict
    assert all(v.short_bias_negative_by_horizon[lab] for lab in LABELS)
    assert "EDGE CONSISTENT" in v.verdict
    assert to_markdown(rep).startswith("# BTCUSDT")


def test_aggregate_flags_inconsistent_edge():
    rows = [
        _row("short", "high", {"1d": 0.05, "3d": 0.04, "7d": 0.03}),   # shorts that RALLIED
    ]
    rep = aggregate(rows, LABELS, BARS, "BTCUSDT", "1d")
    assert not any(rep.verdict.short_bias_negative_by_horizon[lab] for lab in LABELS)
    assert "NOT CONSISTENT" in rep.verdict.verdict


def _synthetic_1d(n: int = 160) -> pd.DataFrame:
    # rising trend with a zigzag so fractal pivots (HH/HL) form
    i = np.arange(n)
    close = 100.0 + 0.6 * i + 3.0 * np.sin(i / 3.0)
    openp = np.concatenate([[close[0]], close[:-1]])
    high = np.maximum(openp, close) + 1.0
    low = np.minimum(openp, close) - 1.0
    ts = 1_600_000_000_000 + i * 86_400_000  # 1d spacing in ms
    return pd.DataFrame(
        {"timestamp": ts, "open": openp, "high": high, "low": low, "close": close, "volume": 1.0}
    )


def test_replay_forward_returns_and_pipeline_reuse():
    cfg = load_config("config/engine.yaml")
    cfg.universe.timeframes = ["1d"]           # anchor-only replay -> fast + offline
    df = _synthetic_1d()
    rows, labels = replay(cfg, "BTCUSDT", {"1d": df}, ["1d"],
                          horizons=[1, 3, 7], min_warmup_bars=120, lookback_cap=800, stride=3)
    assert labels == ["1d", "3d", "7d"]
    assert rows, "replay produced no rows"

    close = df["close"].to_numpy()
    # forward return must be exact close-to-close and look-ahead-free
    r = rows[0]
    expected = close[r.idx + 1] / close[r.idx] - 1.0
    assert math.isclose(r.forward["1d"], expected, rel_tol=1e-9)
    # last-few rows have None where the horizon runs past the series end
    assert any(row.forward["7d"] is None for row in rows[-3:])

    # a persistent uptrend should yield at least some long-bias closes
    assert any(row.bias == "long" for row in rows)
