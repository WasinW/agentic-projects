"""Deterministic indicators — MA stack, Wilder RSI, Wilder ATR.

Wilder smoothing (RMA) is used for RSI/ATR so values match TradingView's
`ta.rsi` / `ta.atr` — the whole point is the engine's numbers line up with what
the user sees on the chart (doc/02 §3).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period, min_periods=period).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False, min_periods=period).mean()


def wilder_rma(series: pd.Series, period: int) -> pd.Series:
    """Wilder's running moving average (RMA), seeded with an SMA of `period`.

    rma[period-1] = mean(x[0:period]); rma[i] = (rma[i-1]*(period-1) + x[i]) / period
    """
    arr = series.to_numpy(dtype=float)
    out = np.full(arr.shape, np.nan)
    n = len(arr)
    if n < period:
        return pd.Series(out, index=series.index)
    out[period - 1] = arr[:period].mean()
    for i in range(period, n):
        out[i] = (out[i - 1] * (period - 1) + arr[i]) / period
    return pd.Series(out, index=series.index)


def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff().fillna(0.0)  # first row has no prior close -> zero change
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_gain = wilder_rma(gain, period)
    avg_loss = wilder_rma(loss, period)
    rs = avg_gain / avg_loss
    out = 100.0 - (100.0 / (1.0 + rs))
    # avg_loss == 0 -> RSI 100 (all gains); both 0 handled by NaN propagation
    out = out.where(avg_loss != 0, 100.0)
    out = out.where(~((avg_gain == 0) & (avg_loss == 0)), 50.0)
    return out


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)
    tr = pd.concat(
        [(high - low), (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    return tr


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    return wilder_rma(true_range(high, low, close), period)


def ma_stack(
    close: pd.Series, periods: list[int], ma_type: str = "ema"
) -> tuple[str, dict[str, float]]:
    """Classify the MA stack at the last bar.

    Returns (label, values) where label in {bullish, bearish, mixed}:
      bullish = close > MA[0] > MA[1] > ... (strictly ascending shorter->longer)
      bearish = close < MA[0] < MA[1] < ...
      else    = mixed
    """
    fn = ema if ma_type == "ema" else sma
    mas = {f"ma{p}": fn(close, p) for p in sorted(periods)}
    last_close = float(close.iloc[-1])
    vals = {k: float(v.iloc[-1]) for k, v in mas.items()}
    if any(np.isnan(x) for x in vals.values()):
        return "mixed", vals  # not enough data
    ordered = [vals[f"ma{p}"] for p in sorted(periods)]
    seq = [last_close, *ordered]
    if all(seq[i] > seq[i + 1] for i in range(len(seq) - 1)):
        return "bullish", vals
    if all(seq[i] < seq[i + 1] for i in range(len(seq) - 1)):
        return "bearish", vals
    return "mixed", vals
