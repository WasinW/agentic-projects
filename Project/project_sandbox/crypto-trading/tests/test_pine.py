import json

import pytest

from crypto_engine.config import load_config
from crypto_engine.contract import (
    Bias,
    ConfluenceScore,
    DataWindow,
    Invalidation,
    Levels,
    Meta,
    Plan,
    Signal,
    Step1Output,
)
from crypto_engine.data import store as S
from crypto_engine.engine import analyze
from crypto_engine.pine import to_pine

CFG = load_config("config/engine.yaml")
SYMBOL = "BTCUSDT"
_has_data = not S.read_candles(SYMBOL, CFG.features.ma.anchor_tf).empty
needs_data = pytest.mark.skipif(not _has_data, reason="no backfilled candles")


def _out(plan: Plan | None = None) -> Step1Output:
    return Step1Output(
        meta=Meta(symbol="BTCUSDT", asset_class="crypto", timeframes=["1h", "4h", "1d"],
                  generated_at="2026-06-07T12:00:00Z",
                  data_window=DataWindow(**{"from": "2024-01-01", "to": "2026-06-07"}),
                  engine_version="0.1.0"),
        regime={"trend": "down", "structure": "lower-highs / lower-lows", "note": "x"},
        bias=Bias(direction="short", conviction="medium",
                  timeframe_alignment={"1h": "neutral", "4h": "short", "1d": "short"}),
        levels=Levels(support=[60000, 55000], resistance=[65000, 68000],
                      invalidation=Invalidation(price=70000, rule='weekly close above 70000 flips bias')),
        signals=[Signal(name="structure_1d", value="LH/LL", vote="short", weight=0.22)],
        confluence_score=ConfluenceScore(long=0.0, short=0.58, neutral=0.42),
        confidence=0.49, caveats=["x"], plan=plan,
    )


def test_pine_header_and_levels():
    src = to_pine(_out())
    assert src.startswith("//@version=6")
    assert 'indicator("CE BTCUSDT | SHORT", overlay = true)' in src
    assert 'hline(60000.00, "S1"' in src and 'hline(55000.00, "S2"' in src
    assert 'hline(65000.00, "R1"' in src
    assert 'hline(70000.00, "Invalidation"' in src
    assert "if barstate.islast" in src and "label.new(" in src
    assert "color.red" in src  # short bias color


def test_pine_plan_section():
    plan = Plan(playbook="sell-the-rip", entry_zone=[65000, 68000], stop=70000,
                targets=[60000, 55000], r_r=2.5, sizing_note="x", note="y")
    src = to_pine(_out(plan))
    assert "fill(e_lo, e_hi" in src
    assert 'hline(70000.00, "Stop"' in src
    assert 'hline(60000.00, "T1"' in src and 'hline(55000.00, "T2"' in src
    assert "// playbook: sell-the-rip" in src


def test_pine_string_safety():
    out = _out()
    out.levels.invalidation.rule = 'weekly "close"\nabove \\ 70000'
    src = to_pine(out)
    # no raw quote/newline/backslash leaked from the rule into a comment line
    assert '"close"' not in src and "\\ 70000" not in src


@needs_data
def test_pine_from_real_analysis_is_wellformed():
    out = analyze(CFG, SYMBOL)
    src = to_pine(out)
    assert src.count("//@version=6") == 1
    # every hline call has a closing paren on its line
    for line in src.splitlines():
        if line.strip().startswith("hline(") or line.strip().endswith('= hline('):
            assert line.rstrip().endswith(")")
    # round-trips with the JSON artifact unaffected
    json.loads(out.to_json())
