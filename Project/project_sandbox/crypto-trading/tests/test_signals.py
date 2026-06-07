from crypto_engine.config import load_config
from crypto_engine.contract import Signal
from crypto_engine.signals import confluence as C
from crypto_engine.signals.registry import CandleReading, SignalInputs, build_signals

CFG = load_config("config/engine.yaml")


def test_confluence_worked_example_from_spec():
    """doc/03 §3.3: short=0.58, neutral=0.42, long=0, medium conviction."""
    sigs = [
        Signal(name="structure_1d", value="LH/LL", vote="short", weight=0.22),
        Signal(name="structure_4h", value="LH/LL", vote="short", weight=0.16),
        Signal(name="structure_1h", value="mixed", vote="neutral", weight=0.06),
        Signal(name="ma_stack", value="bearish", vote="short", weight=0.20),
        Signal(name="price_vs_ma_dist", value=-3.9, vote="neutral", weight=0.08),
        Signal(name="rsi_1d", value=15, vote="neutral", weight=0.09),
        Signal(name="rsi_4h", value=42, vote="neutral", weight=0.06),
        Signal(name="rsi_1h", value=64, vote="neutral", weight=0.03),
        Signal(name="candle_pattern_1d", value="doji", vote="neutral", weight=0.10),
        Signal(name="vol_regime", value="normal", vote="neutral", weight=0.0),
    ]
    score = C.confluence_score(sigs)
    assert score.short == 0.58
    assert score.neutral == 0.42
    assert score.long == 0.0

    res = C.derive(sigs, {"1h": "mixed", "4h": "LH/LL", "1d": "LH/LL"}, ["1h", "4h", "1d"], CFG)
    assert res.bias.direction == "short"
    assert res.bias.conviction == "medium"          # margin 0.16
    assert res.bias.timeframe_alignment == {"1h": "neutral", "4h": "short", "1d": "short"}
    assert res.confidence == round(0.58 * 0.85, 4)  # macro haircut


def test_rsi_oversold_is_neutral_not_long():
    inp = SignalInputs(
        rsi_by_tf={"1d": 20.0}, structure_by_tf={"1d": "mixed"}, ma_stack_label="mixed",
        vol_regime_label="normal", price_dist=0.0,
        candle=CandleReading("neutral", "none", False, False), candle_tf="1d",
    )
    sigs = {s.name: s for s in build_signals(inp, CFG)}
    assert sigs["rsi_1d"].vote == "neutral"


def test_absent_signal_when_rsi_nan():
    inp = SignalInputs(
        rsi_by_tf={"1d": float("nan")}, structure_by_tf={"1d": "LH/LL"}, ma_stack_label="bearish",
        vol_regime_label="normal", price_dist=0.0,
        candle=CandleReading("neutral", "none", False, False), candle_tf="1d",
    )
    names = {s.name for s in build_signals(inp, CFG)}
    assert "rsi_1d" not in names         # NaN reading -> absent
    assert "structure_1d" in names


def test_candle_context_filter():
    base = dict(rsi_by_tf={}, structure_by_tf={}, ma_stack_label="mixed",
                vol_regime_label="normal", price_dist=0.0, candle_tf="1d")
    at_support = SignalInputs(candle=CandleReading("bullish", "hammer", True, False), **base)
    mid_range = SignalInputs(candle=CandleReading("bullish", "hammer", False, False), **base)
    assert {s.name: s.vote for s in build_signals(at_support, CFG)}["candle_pattern_1d"] == "long"
    assert {s.name: s.vote for s in build_signals(mid_range, CFG)}["candle_pattern_1d"] == "neutral"
