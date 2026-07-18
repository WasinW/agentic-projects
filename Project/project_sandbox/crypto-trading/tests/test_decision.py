"""Deterministic playbook table (doc/03 §4), confidence.floor wiring, position sizing."""

from crypto_engine.config import load_config
from crypto_engine.signals import decision as D

CFG = load_config("config/engine.yaml")   # floor 0.45, risk 1%, equity 10000, lev cap 3


def _pb(trend, direction, conviction, vol, confidence=0.9):
    return D.select_playbook(trend, direction, conviction, vol, confidence, CFG)


def test_playbook_trend_following():
    assert _pb("down", "short", "high", "normal").playbook == "sell-the-rip (trend-following)"
    assert _pb("down", "short", "medium", "expansion").playbook == "sell-the-rip (trend-following)"
    assert _pb("up", "long", "high", "normal").playbook == "buy-the-dip (trend-following)"


def test_playbook_low_conviction_stands_aside():
    assert _pb("down", "short", "low", "normal").playbook == "stand-aside / wait-pullback"
    assert _pb("up", "long", "low", "expansion").playbook == "stand-aside / wait-pullback"


def test_playbook_no_counter_trend():
    # long in a downtrend / short in an uptrend must never trade
    assert _pb("down", "long", "high", "normal").playbook == "stand-aside"
    assert _pb("up", "short", "high", "normal").playbook == "stand-aside"


def test_playbook_range_by_vol():
    assert _pb("sideways", "short", "high", "contraction").playbook == "range-fade"
    assert _pb("sideways", "long", "high", "expansion").playbook == "stand-aside (breakout pending)"
    assert _pb("sideways", "short", "high", "normal").playbook == "stand-aside"


def test_playbook_neutral_stands_aside():
    assert _pb("down", "neutral", "high", "normal").playbook == "stand-aside"


def test_confidence_floor_forces_stand_aside():
    # would be sell-the-rip, but sub-floor confidence overrides (wires the dead knob)
    d = _pb("down", "short", "high", "normal", confidence=0.30)
    assert d.playbook == "stand-aside"
    assert "floor" in d.reason


def test_position_size_basic_and_leverage_cap():
    # risk 1% of 10000 = 100; stop distance 5 -> qty 20; notional 20*100 = 2000 (< 3x cap)
    ps = D.position_size(entry=100.0, stop=95.0, cfg=CFG)
    assert ps is not None
    assert ps.risk_amount == 100.0
    assert ps.qty == 20.0
    assert ps.leverage == 0.2

    # tight stop blows past the 3x leverage cap -> qty clamped to notional = 30000
    ps2 = D.position_size(entry=100.0, stop=99.9, cfg=CFG)
    assert ps2.notional == 30000.0
    assert ps2.leverage == 3.0
    assert "capped" in ps2.note

    # invalid stop distance -> no size
    assert D.position_size(entry=100.0, stop=100.0, cfg=CFG) is None


def test_entry_from_source():
    zone, px = D.entry_from_source("nearest resistance", [90.0], [110.0, 120.0], close=100.0)
    assert zone == [110.0] and px == 110.0
    zone2, px2 = D.entry_from_source("range edges", [90.0], [110.0], close=100.0)
    assert zone2 == [90.0, 110.0]
    assert D.entry_from_source("watch", [90.0], [110.0], close=100.0) == (None, None)
