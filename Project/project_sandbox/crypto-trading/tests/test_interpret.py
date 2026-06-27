"""Interpretive layer wiring test — uses a fake LLM client (no API key needed).

Verifies the digest -> LLM -> contract mapping, the elliott_1d fold into
confluence, and that the enriched output still validates against the schema.
"""

import json

import pytest

from crypto_engine.config import load_config
from crypto_engine.contract import Step1Output
from crypto_engine.data import store as S
from crypto_engine.engine import analyze
from crypto_engine.interpret import LLMElliottTF, LLMInterpretation

CFG = load_config("config/engine.yaml")
SYMBOL = "BTCUSDT"
_has_data = not S.read_candles(SYMBOL, CFG.features.ma.anchor_tf).empty
needs_data = pytest.mark.skipif(not _has_data, reason="no backfilled candles")


class _FakeMessages:
    def __init__(self, payload):
        self._payload = payload

    def parse(self, **kwargs):
        # sanity: the engine must send adaptive thinking + structured output schema
        assert kwargs["model"].startswith("claude-")
        assert kwargs["thinking"]["type"] == "adaptive"
        assert kwargs["output_format"] is LLMInterpretation
        return type("R", (), {"parsed_output": self._payload})()


class _FakeClient:
    def __init__(self, payload):
        self.messages = _FakeMessages(payload)


def _payload():
    tf = LLMElliottTF(degree="Primary", current_wave="C", structure="ABC", implied_direction="down", confidence="medium")
    return LLMInterpretation(
        tf_1d=tf, tf_4h=tf, tf_1h=LLMElliottTF(note="noisy", confidence="low"),
        elliott_vote="short", elliott_value="wave 3-of-C",
        summary_daily="d", summary_weekly="w", summary_monthly="m",
        plan_playbook="sell-the-rip (trend-following)", plan_entry_zone=[65000, 68000],
        plan_stop=70000, plan_targets=[60000, 55000], plan_r_r=2.5,
        plan_sizing_note="low leverage", plan_note="watch macro",
    )


@needs_data
def test_interpret_folds_elliott_and_fills_blocks():
    out = analyze(CFG, SYMBOL, interpret=True, llm_client=_FakeClient(_payload()))

    # interpretive blocks now populated
    assert out.plan is not None and out.plan.playbook.startswith("sell-the-rip")
    assert out.summaries is not None and out.summaries.daily == "d"
    assert out.elliott is not None and out.elliott.tf_1d.current_wave == "C"

    # elliott_1d folded into signals at the configured weight
    elliott_sig = next((s for s in out.signals if s.name == "elliott_1d"), None)
    assert elliott_sig is not None
    assert elliott_sig.weight == CFG.elliott.weight
    assert elliott_sig.vote == "short"

    # still a valid contract, confluence still normalized
    reparsed = Step1Output.model_validate(json.loads(out.to_json()))
    cs = reparsed.confluence_score
    assert abs(cs.long + cs.short + cs.neutral - 1.0) < 1e-3


@needs_data
def test_deterministic_path_unchanged_without_interpret():
    out = analyze(CFG, SYMBOL, interpret=False)
    assert out.plan is None and out.summaries is None and out.elliott is None
    assert not any(s.name == "elliott_1d" for s in out.signals)
