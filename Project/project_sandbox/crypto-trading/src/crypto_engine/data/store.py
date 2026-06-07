"""Local candle store: Parquet = store-of-record, DuckDB = query layer.

Layout (partitioned by symbol/timeframe):
    data/candles/symbol=BTCUSDT/timeframe=1h/data.parquet

Rules (locked):
- Ingest-once-store-local; never call the API in a tight loop.
- Only CLOSED candles are stored — the in-progress candle is dropped on write.
- Upsert by timestamp (idempotent): re-running a backfill never duplicates rows.
"""

from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from .fetch import OHLCV_COLS, now_ms

DEFAULT_ROOT = "data/candles"


def partition_path(symbol: str, timeframe: str, root: str = DEFAULT_ROOT) -> Path:
    return Path(root) / f"symbol={symbol}" / f"timeframe={timeframe}" / "data.parquet"


def is_closed(open_ms: int, tf_ms: int, ref_ms: int | None = None) -> bool:
    """A candle that opened at open_ms is closed once open_ms + tf_ms <= now."""
    ref = ref_ms if ref_ms is not None else now_ms()
    return open_ms + tf_ms <= ref


def read_candles(
    symbol: str, timeframe: str, root: str = DEFAULT_ROOT
) -> pd.DataFrame:
    """Read stored candles via DuckDB (query layer over parquet)."""
    path = partition_path(symbol, timeframe, root)
    if not path.exists():
        return pd.DataFrame(columns=OHLCV_COLS).astype({"timestamp": "int64"})
    con = duckdb.connect()
    try:
        df = con.execute(
            "SELECT timestamp, open, high, low, close, volume "
            "FROM read_parquet(?) ORDER BY timestamp",
            [str(path)],
        ).df()
    finally:
        con.close()
    df["timestamp"] = df["timestamp"].astype("int64")
    return df


def last_timestamp(
    symbol: str, timeframe: str, root: str = DEFAULT_ROOT
) -> int | None:
    """Watermark: max stored (closed) candle open-time in ms, or None."""
    path = partition_path(symbol, timeframe, root)
    if not path.exists():
        return None
    con = duckdb.connect()
    try:
        val = con.execute(
            "SELECT max(timestamp) FROM read_parquet(?)", [str(path)]
        ).fetchone()[0]
    finally:
        con.close()
    return int(val) if val is not None else None


def write_candles(
    df: pd.DataFrame,
    symbol: str,
    timeframe: str,
    tf_ms: int,
    root: str = DEFAULT_ROOT,
    drop_unclosed: bool = True,
    ref_ms: int | None = None,
) -> int:
    """Upsert candles into the partition. Returns final row count.

    - drops the in-progress (unclosed) candle when drop_unclosed=True
    - merges with existing rows, de-dupes by timestamp (new data wins), sorts
    """
    if df.empty:
        return len(read_candles(symbol, timeframe, root))

    df = df.copy()
    df["timestamp"] = df["timestamp"].astype("int64")
    if drop_unclosed:
        ref = ref_ms if ref_ms is not None else now_ms()
        df = df[df["timestamp"] + tf_ms <= ref]

    existing = read_candles(symbol, timeframe, root)
    merged = (
        pd.concat([existing, df], ignore_index=True)
        .drop_duplicates(subset="timestamp", keep="last")
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    path = partition_path(symbol, timeframe, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(path, index=False)
    return len(merged)
