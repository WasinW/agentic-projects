import pandas as pd

from crypto_engine.features import structure as ST
from crypto_engine.features.structure import Pivot


def _df(highs, lows):
    n = len(highs)
    return pd.DataFrame(
        {
            "timestamp": list(range(n)),
            "open": lows,
            "high": highs,
            "low": lows,
            "close": highs,
        }
    )


def test_find_pivots_single_peak():
    df = _df(highs=[1, 2, 3, 5, 3, 2, 1], lows=[0, 1, 2, 4, 2, 1, 0])
    piv = ST.find_pivots(df, lookback=2)
    highs = [p for p in piv if p.kind == "high"]
    assert len(highs) == 1
    assert highs[0].idx == 3 and highs[0].price == 5.0


def test_classify_structure_uptrend():
    piv = [
        Pivot(0, 0, 5.0, "low"),
        Pivot(1, 1, 10.0, "high"),
        Pivot(2, 2, 7.0, "low"),
        Pivot(3, 3, 12.0, "high"),
    ]
    assert ST.classify_structure(piv, swing_count=4) == "HH/HL"


def test_classify_structure_downtrend():
    piv = [
        Pivot(0, 0, 12.0, "high"),
        Pivot(1, 1, 7.0, "low"),
        Pivot(2, 2, 10.0, "high"),
        Pivot(3, 3, 5.0, "low"),
    ]
    assert ST.classify_structure(piv, swing_count=4) == "LH/LL"


def test_classify_structure_mixed_when_insufficient():
    assert ST.classify_structure([Pivot(0, 0, 5.0, "low")]) == "mixed"


def test_support_resistance_split_nearest_first():
    df = _df(highs=[100], lows=[100])  # close = 100
    piv = [
        Pivot(0, 0, 80.0, "low"),
        Pivot(1, 1, 90.0, "low"),
        Pivot(2, 2, 110.0, "high"),
        Pivot(3, 3, 120.0, "high"),
    ]
    sup, res = ST.support_resistance(df, piv, atr_last=1.0, cluster_atr_mult=0.5)
    assert sup == [90.0, 80.0]      # nearest support first (highest below price)
    assert res == [110.0, 120.0]    # nearest resistance first (lowest above price)


def test_vol_regime():
    import pandas as pd
    base = pd.Series([10.0] * 100)
    assert ST.vol_regime(base, lookback=100) == "normal"
    exp = pd.Series([10.0] * 99 + [20.0])
    assert ST.vol_regime(exp, lookback=100, expansion_mult=1.5) == "expansion"
    con = pd.Series([10.0] * 99 + [5.0])
    assert ST.vol_regime(con, lookback=100, contraction_mult=0.7) == "contraction"


def test_price_vs_ma_dist():
    assert ST.price_vs_ma_dist(110.0, 100.0, 4.0) == 2.5
    assert ST.price_vs_ma_dist(110.0, float("nan"), 4.0) == 0.0
