"""Backtest harness — replay stored candles through the SAME deterministic pipeline.

The honest question this answers: do short-bias signals actually show *negative*
forward returns (and long-bias positive)? If not, the weights are opinion, not edge.

Pipeline reuse: at every anchor-TF close we slice each timeframe to only the candles
that had closed by that moment (no look-ahead) and call `engine.deterministic(...)` —
the identical signal/confluence/bias code the live `analyze` uses. We then measure the
realised forward return and bucket it by the bias/conviction the engine produced.
"""

from __future__ import annotations

from .replay import ReplayRow, replay, replay_from_store
from .report import BacktestReport, aggregate, run_backtest, to_markdown

__all__ = [
    "ReplayRow",
    "replay",
    "replay_from_store",
    "BacktestReport",
    "aggregate",
    "run_backtest",
    "to_markdown",
]
