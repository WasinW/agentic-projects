"""Backfill orchestration: fetch -> store per (symbol, timeframe).

Incremental: starts from the stored watermark if present, else history_start.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..config import EngineConfig
from . import fetch as F
from . import store as S


@dataclass
class BackfillResult:
    symbol: str
    timeframe: str
    fetched: int
    stored_total: int
    last_ts: int | None


def backfill_timeframe(
    cfg: EngineConfig,
    symbol: str,
    timeframe: str,
    exchange=None,
    root: str = S.DEFAULT_ROOT,
) -> BackfillResult:
    ex = exchange or F.make_exchange(cfg.data.exchange)
    tf_ms = F.tf_to_ms(ex, timeframe)

    watermark = S.last_timestamp(symbol, timeframe, root)
    if watermark is not None:
        since = watermark + tf_ms  # next candle after last stored
    else:
        since = F.date_to_ms(ex, cfg.data.history_start)

    df = F.fetch_ohlcv_range(ex, symbol, timeframe, since_ms=since, limit=cfg.data.fetch_limit)
    total = S.write_candles(
        df, symbol, timeframe, tf_ms, root=root, drop_unclosed=cfg.data.drop_unclosed_candle
    )
    return BackfillResult(
        symbol=symbol,
        timeframe=timeframe,
        fetched=len(df),
        stored_total=total,
        last_ts=S.last_timestamp(symbol, timeframe, root),
    )


def all_timeframes(cfg: EngineConfig) -> list[str]:
    """Analysis TFs + extra fetch-only TFs (e.g. 1w for weekly-close invalidation)."""
    seen, out = set(), []
    for tf in [*cfg.universe.timeframes, *cfg.universe.extra_fetch_timeframes]:
        if tf not in seen:
            seen.add(tf)
            out.append(tf)
    return out


def backfill_symbol(
    cfg: EngineConfig, symbol: str, root: str = S.DEFAULT_ROOT
) -> list[BackfillResult]:
    ex = F.make_exchange(cfg.data.exchange)
    return [backfill_timeframe(cfg, symbol, tf, exchange=ex, root=root) for tf in all_timeframes(cfg)]
