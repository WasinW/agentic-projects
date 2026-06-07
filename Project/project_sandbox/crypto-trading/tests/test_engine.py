"""Integration: run analyze on stored candles, round-trip validate the contract.

Skips cleanly if no data has been backfilled yet (keeps CI green offline).
"""

import json

import pytest

from crypto_engine.config import load_config
from crypto_engine.contract import Step1Output
from crypto_engine.data import store as S
from crypto_engine.engine import analyze

CFG = load_config("config/engine.yaml")
SYMBOL = "BTCUSDT"

_has_data = not S.read_candles(SYMBOL, CFG.features.ma.anchor_tf).empty
needs_data = pytest.mark.skipif(not _has_data, reason="no backfilled candles — run `crypto-engine backfill`")


@needs_data
def test_analyze_produces_valid_contract():
    out = analyze(CFG, SYMBOL)
    # round-trip through JSON and re-validate against the schema
    reparsed = Step1Output.model_validate(json.loads(out.to_json()))
    assert reparsed.meta.symbol == SYMBOL
    assert set(reparsed.bias.timeframe_alignment) == set(CFG.universe.timeframes)
    # v1: interpretive blocks null
    assert reparsed.elliott is None and reparsed.summaries is None and reparsed.plan is None
    # confluence sums to ~1
    cs = reparsed.confluence_score
    assert abs(cs.long + cs.short + cs.neutral - 1.0) < 1e-3
    assert 0.0 <= reparsed.confidence <= 1.0


@needs_data
def test_levels_invalidation_consistent_with_bias():
    out = analyze(CFG, SYMBOL)
    close = float(S.read_candles(SYMBOL, CFG.features.ma.anchor_tf)["close"].iloc[-1])
    if out.bias.direction == "short":
        assert out.levels.invalidation.price > close
    elif out.bias.direction == "long":
        assert out.levels.invalidation.price < close
