import numpy as np
import pandas as pd
import pytest

from crypto_engine.features import indicators as I


def test_sma_ema_basic():
    s = pd.Series([1, 2, 3, 4, 5], dtype=float)
    assert I.sma(s, 3).iloc[-1] == pytest.approx(4.0)        # mean(3,4,5)
    assert np.isnan(I.sma(s, 3).iloc[0])
    # EMA(period=3) seeded, last value finite and within data range
    assert 3.0 < I.ema(s, 3).iloc[-1] <= 5.0


def test_wilder_rma_hand_computed():
    s = pd.Series([1, 2, 3, 4, 5, 6], dtype=float)
    rma = I.wilder_rma(s, 3)
    # seed = mean(1,2,3) = 2.0 at idx2, then Wilder recursion
    assert rma.iloc[2] == pytest.approx(2.0)
    assert rma.iloc[3] == pytest.approx(8 / 3)
    assert rma.iloc[4] == pytest.approx(3.4444444, abs=1e-6)
    assert rma.iloc[5] == pytest.approx(4.2962963, abs=1e-6)
    assert np.isnan(rma.iloc[1])


def test_rsi_hand_computed_period2():
    close = pd.Series([10, 11, 10, 11], dtype=float)
    r = I.rsi(close, period=2)
    assert r.iloc[2] == pytest.approx(33.33333, abs=1e-4)
    assert r.iloc[3] == pytest.approx(71.42857, abs=1e-4)


def test_rsi_bounds_extremes():
    up = pd.Series(range(1, 30), dtype=float)
    down = pd.Series(range(30, 1, -1), dtype=float)
    assert I.rsi(up, 14).iloc[-1] == pytest.approx(100.0)
    assert I.rsi(down, 14).iloc[-1] == pytest.approx(0.0)


def test_atr_constant_true_range():
    df = pd.DataFrame(
        {"high": [10, 11, 12], "low": [8, 9, 10], "close": [9, 10, 11]}, dtype=float
    )
    a = I.atr(df["high"], df["low"], df["close"], period=2)
    assert a.iloc[-1] == pytest.approx(2.0)


def test_ma_stack_labels():
    n = 120
    up = pd.Series(np.linspace(100, 200, n))      # rising -> bullish stack
    down = pd.Series(np.linspace(200, 100, n))    # falling -> bearish stack
    assert I.ma_stack(up, [20, 50, 100], "ema")[0] == "bullish"
    assert I.ma_stack(down, [20, 50, 100], "ema")[0] == "bearish"
    short = pd.Series(np.linspace(100, 110, 30))  # not enough for ma100
    assert I.ma_stack(short, [20, 50, 100], "ema")[0] == "mixed"
