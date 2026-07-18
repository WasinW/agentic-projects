"""Point-in-time replay: for each anchor-TF close, recompute bias via the live
pipeline on look-ahead-free candle slices, then attach realised forward returns.

`replay` is pure (takes candle DataFrames) so it is fully unit-testable on synthetic
data; `replay_from_store` loads the parquet store and calls it.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ..config import EngineConfig
from ..data import store as S
from ..engine import deterministic


@dataclass
class ReplayRow:
    idx: int
    timestamp: int          # anchor bar open time (ms)
    date: str               # YYYY-MM-DD of the anchor close
    close: float
    bias: str               # long | short | neutral
    conviction: str         # low | medium | high
    confidence: float
    score_long: float
    score_short: float
    score_neutral: float
    forward: dict[str, float | None]   # horizon-label -> forward return (None near series end)


def _tf_ms(df: pd.DataFrame) -> int:
    ts = df["timestamp"].to_numpy()
    if len(ts) < 2:
        return 0
    return int(np.median(np.diff(ts)))


def _ms_to_date(ms: int) -> str:
    from datetime import datetime, timezone

    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d")


def replay(
    cfg: EngineConfig,
    symbol: str,
    candles: dict[str, pd.DataFrame],
    tfs: list[str],
    *,
    horizons: list[int] | None = None,
    min_warmup_bars: int | None = None,
    lookback_cap: int | None = None,
    limit: int = 0,
    stride: int = 1,
) -> tuple[list[ReplayRow], list[str]]:
    """Replay the engine over every anchor-TF close.

    Returns (rows, horizon_labels). Forward return for horizon h (in anchor bars) is
    close[i+h]/close[i] - 1, or None when i+h runs past the series end.
    """
    bt = cfg.backtest
    horizons = horizons if horizons is not None else bt.horizons
    warmup = min_warmup_bars if min_warmup_bars is not None else bt.min_warmup_bars
    cap = lookback_cap if lookback_cap is not None else bt.lookback_cap
    anchor_tf = cfg.features.ma.anchor_tf

    adf = candles[anchor_tf].reset_index(drop=True)
    n = len(adf)
    a_ts = adf["timestamp"].to_numpy()
    a_close = adf["close"].to_numpy(dtype=float)
    a_tf_ms = _tf_ms(adf)

    tf_ms = {tf: _tf_ms(candles[tf]) for tf in tfs}
    full = {tf: candles[tf].reset_index(drop=True) for tf in tfs}
    ts_np = {tf: full[tf]["timestamp"].to_numpy() for tf in tfs}

    unit = anchor_tf[-1] if anchor_tf and anchor_tf[-1].isalpha() else "b"
    horizon_labels = [f"{h}{unit}" for h in horizons]

    # anchor bars we will evaluate (respect warmup, optional most-recent `limit`, stride)
    start = warmup
    if limit and limit > 0:
        start = max(start, n - limit)
    indices = range(start, n, max(1, stride))

    rows: list[ReplayRow] = []
    for i in indices:
        anchor_close_time = int(a_ts[i]) + a_tf_ms

        # look-ahead-free slice per TF: only candles whose close <= anchor close
        sliced: dict[str, pd.DataFrame] = {}
        ok = True
        for tf in tfs:
            closed = int(np.searchsorted(ts_np[tf] + tf_ms[tf], anchor_close_time, side="right"))
            if closed < 2:
                ok = False
                break
            lo = max(0, closed - cap)
            sliced[tf] = full[tf].iloc[lo:closed]
        if not ok:
            continue

        det = deterministic(cfg, symbol, sliced, tfs)
        b = det.out.bias
        cs = det.out.confluence_score

        forward: dict[str, float | None] = {}
        for h, label in zip(horizons, horizon_labels):
            j = i + h
            forward[label] = (float(a_close[j] / a_close[i]) - 1.0) if j < n else None

        rows.append(
            ReplayRow(
                idx=i, timestamp=int(a_ts[i]), date=_ms_to_date(anchor_close_time),
                close=float(a_close[i]), bias=b.direction, conviction=b.conviction,
                confidence=float(det.out.confidence),
                score_long=cs.long, score_short=cs.short, score_neutral=cs.neutral,
                forward=forward,
            )
        )
    return rows, horizon_labels


def replay_from_store(
    cfg: EngineConfig,
    symbol: str,
    root: str = S.DEFAULT_ROOT,
    *,
    limit: int = 0,
    stride: int = 1,
) -> tuple[list[ReplayRow], list[str]]:
    tfs = cfg.universe.timeframes
    candles: dict[str, pd.DataFrame] = {}
    for tf in tfs:
        df = S.read_candles(symbol, tf, root)
        if df.empty:
            raise RuntimeError(f"no stored candles for {symbol} {tf} — run a backfill first")
        candles[tf] = df
    return replay(cfg, symbol, candles, tfs, limit=limit, stride=stride)
