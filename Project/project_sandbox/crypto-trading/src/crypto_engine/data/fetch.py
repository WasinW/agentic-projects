"""Fetch OHLCV history from an exchange via ccxt (Binance public, no API keys).

Ingest-once-store-local: pull a wide window, then incremental top-ups from the
stored watermark. Rate limiting is handled by ccxt (`enableRateLimit`).
"""

from __future__ import annotations

import time

import ccxt
import pandas as pd

OHLCV_COLS = ["timestamp", "open", "high", "low", "close", "volume"]


def make_exchange(exchange_id: str = "binance") -> ccxt.Exchange:
    klass = getattr(ccxt, exchange_id)
    return klass({"enableRateLimit": True})


def tf_to_ms(exchange: ccxt.Exchange, timeframe: str) -> int:
    """Timeframe duration in milliseconds (e.g. '1h' -> 3_600_000)."""
    return int(exchange.parse_timeframe(timeframe)) * 1000


def date_to_ms(exchange: ccxt.Exchange, date_str: str) -> int:
    """'2024-01-01' -> epoch ms (UTC)."""
    return exchange.parse8601(f"{date_str}T00:00:00Z")


def fetch_ohlcv_range(
    exchange: ccxt.Exchange,
    symbol: str,
    timeframe: str,
    since_ms: int,
    until_ms: int | None = None,
    limit: int = 1000,
) -> pd.DataFrame:
    """Page through fetch_ohlcv from since_ms to until_ms (or now).

    Returns a DataFrame [timestamp(ms,int), open, high, low, close, volume],
    de-duplicated and sorted ascending. The last row may be an unclosed candle —
    the store layer drops it.
    """
    tf_ms = tf_to_ms(exchange, timeframe)
    if until_ms is None:
        until_ms = exchange.milliseconds()

    rows: list[list] = []
    since = since_ms
    while since < until_ms:
        batch = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
        if not batch:
            break
        rows.extend(batch)
        last_ts = batch[-1][0]
        next_since = last_ts + tf_ms
        if next_since <= since:  # no forward progress -> stop (safety)
            break
        since = next_since
        if len(batch) < limit:  # reached the end of available data
            break

    if not rows:
        return pd.DataFrame(columns=OHLCV_COLS).astype({"timestamp": "int64"})

    df = pd.DataFrame(rows, columns=OHLCV_COLS)
    df["timestamp"] = df["timestamp"].astype("int64")
    df = (
        df.drop_duplicates(subset="timestamp")
        .sort_values("timestamp")
        .reset_index(drop=True)
    )
    df = df[df["timestamp"] < until_ms]
    return df


def now_ms() -> int:
    return int(time.time() * 1000)
