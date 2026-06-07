import pandas as pd

from crypto_engine.features import patterns as P


def _df(rows):
    return pd.DataFrame(rows, columns=["open", "high", "low", "close"]).assign(
        timestamp=range(len(rows))
    )


def test_bullish_engulfing():
    df = _df([[10.5, 10.6, 10.3, 10.4], [7.0, 11.5, 6.9, 11.0]])  # prev red, curr engulfs up
    hit = P.detect_last(df)
    assert hit.name == "bullish_engulfing" and hit.direction == "bullish"


def test_bearish_engulfing():
    df = _df([[10.0, 11.0, 9.9, 10.9], [11.5, 11.6, 9.0, 9.5]])  # prev green, curr engulfs down
    hit = P.detect_last(df)
    assert hit.name == "bearish_engulfing" and hit.direction == "bearish"


def test_hammer():
    df = _df([[10.5, 10.6, 10.4, 10.45], [10.0, 10.3, 9.0, 10.2]])
    hit = P.detect_last(df)
    assert hit.name == "hammer" and hit.direction == "bullish"


def test_doji():
    df = _df([[10.0, 10.1, 9.9, 10.05], [10.0, 11.0, 9.0, 10.005]])
    hit = P.detect_last(df)
    assert hit.name == "doji" and hit.direction == "neutral"


def test_none():
    df = _df([[10.0, 10.5, 9.5, 10.2], [10.2, 10.6, 10.0, 10.4]])
    hit = P.detect_last(df)
    assert hit.name == "none"
