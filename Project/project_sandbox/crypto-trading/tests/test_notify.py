"""Notification routing tests — no network, no tokens, pure channel selection."""

from crypto_engine import notify as N
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


def _out() -> Step1Output:
    return Step1Output(
        meta=Meta(symbol="BTCUSDT", asset_class="crypto", timeframes=["1h", "4h", "1d"],
                  generated_at="2026-07-18T09:00:00Z",
                  data_window=DataWindow(**{"from": "2024-01-01", "to": "2026-06-07"}),
                  engine_version="0.1.0"),
        regime={"trend": "down", "structure": "lower-highs / lower-lows", "note": "x"},
        bias=Bias(direction="short", conviction="medium",
                  timeframe_alignment={"1h": "neutral", "4h": "short", "1d": "short"}),
        levels=Levels(support=[60000], resistance=[70000],
                      invalidation=Invalidation(price=72000, rule="weekly close above 72000 flips bias")),
        signals=[Signal(name="structure_1d", value="LH/LL", vote="short", weight=0.22)],
        confluence_score=ConfluenceScore(long=0.0, short=0.58, neutral=0.42),
        confidence=0.49, caveats=["x"],
        plan=Plan(playbook="sell-the-rip (trend-following)"),
    )


def test_build_message_is_one_line_summary():
    msg = N.build_message(_out())
    assert "BTCUSDT" in msg and "SHORT" in msg and "sell-the-rip" in msg
    assert "\n" not in msg


def test_choose_channel_prefers_telegram_when_env_set():
    env = {"TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "c"}
    assert N.choose_channel(env) == "telegram"


def test_choose_channel_none_without_telegram_or_desktop():
    # partial telegram config does not qualify; desktop suppressed -> none
    env = {"TELEGRAM_BOT_TOKEN": "t", "CE_NO_DESKTOP_NOTIFY": "1"}
    assert N.choose_channel(env) == "none"


def test_send_none_channel_is_noop():
    # empty env + desktop suppressed -> 'none', never touches the network
    assert N.send("hi", env={"CE_NO_DESKTOP_NOTIFY": "1"}) == "none"
