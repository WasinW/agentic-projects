"""Compliance gate tests — deterministic pass must stand alone with no API key, no network."""
from __future__ import annotations

import pytest

from lumora_sprint.compliance import (
    RULE_AI_VISUAL_NO_IMAGE,
    RULE_BANNED_PHRASE,
    RULE_EMPTY_CAPTION,
    RULE_LLM_QA_SKIPPED,
    RULE_NO_HASHTAGS,
    deterministic_check,
    estimate_cost_usd,
    llm_qa,
    predictive_markers,
    price_for,
    run_compliance,
    run_compliance_with_usage,
)
from lumora_sprint.config import load_account, load_engine
from lumora_sprint.models import ImageSpec, PostSpec

# Day-1 of the real batch (01-batch-30day.md) — the reference "clean" post.
DAY1_HOOK = "การ์ดใบแรกของช่องนี้ — เลือกใบที่ตาไปหยุดก่อน 🌌"
DAY1_CAPTION = (
    "การ์ดใบแรกของช่องนี้ — เลือกใบที่ตาไปหยุดก่อน 🌌\n"
    "ซ้าย = เริ่มใหม่ · กลาง = อยู่กับปัจจุบัน · ขวา = ปล่อยของเก่า\n"
    "เราไม่ได้มาทำนายว่าพรุ่งนี้จะเป็นไง — แค่ชวนถามตัวเองว่า *วันนี้* อยากถือแสงแบบไหนไป\n"
    "ช่องนี้ชื่อ **มูมีแสง** เพราะเราเชื่อว่าความเชื่อมันสวยได้ โดยไม่ต้องขู่ใคร ✨\n"
    "เซฟใบที่ใช่ไว้ แล้วคอมเมนต์เลขที่เลือกมาให้ดูหน่อย"
)
DAY1_HASHTAGS = ["#การ์ดวันนี้", "#สายมู", "#มูมีแสง", "#ไพ่ออราเคิล", "#cosmic", "#AIart"]


@pytest.fixture
def account():
    return load_account()


@pytest.fixture
def engine():
    """Real engine config with the LLM off — tests never touch the network."""
    cfg = load_engine()
    cfg.llm.enabled = False
    return cfg


def make_spec(**over) -> PostSpec:
    base: dict = {
        "post_id": "L1-D01",
        "day": 1,
        "week": 1,
        "content_pillar": "C2",
        "theme": "Cosmic",
        "media": "M11",
        "funnel_stage": "Hub",
        "jtbd": "ช่วยให้รู้สึกสงบ + ตั้งต้นวันได้",
        "hook_type": "curiosity-choice",
        "concept": "การ์ดเปิดช่อง แสงแรก",
        "hook": DAY1_HOOK,
        "caption": DAY1_CAPTION,
        "hashtags": list(DAY1_HASHTAGS),
        "affiliate_angle": "none",
        "ai_visual": True,
        "homage_watch": False,
        "image": ImageSpec(prompt="Three ethereal oracle cards floating above open palms, cosmic nebula"),
        "full_spec": True,
    }
    base.update(over)
    return PostSpec(**base)


# ── deterministic pass ─────────────────────────────────────────────────────


def test_clean_day1_caption_passes(account, engine):
    findings = deterministic_check(make_spec(), account)
    assert findings == [], f"day-1 spec should be clean, got {[f.rule for f in findings]}"

    report = run_compliance(make_spec(), account, engine)
    assert report.ok is True
    assert not [f for f in report.findings if f.severity == "block"]


def test_banned_phrase_100_percent_blocks(account, engine):
    spec = make_spec(caption=DAY1_CAPTION + "\nบูชาแล้วสมหวัง 100% ทุกคน")
    findings = deterministic_check(spec, account)
    hits = [f for f in findings if f.rule == RULE_BANNED_PHRASE]
    assert len(hits) == 1
    assert hits[0].severity == "block"
    assert "100%" in hits[0].detail
    assert hits[0].source == "deterministic"

    report = run_compliance(spec, account, engine)
    assert report.ok is False


def test_banned_phrase_in_hook_also_blocks(account):
    spec = make_spec(hook="ขอแล้วรวยแน่ ไม่ต้องสงสัย")
    hits = [f for f in deterministic_check(spec, account) if f.rule == RULE_BANNED_PHRASE]
    assert [f.severity for f in hits] == ["block"]


def test_banned_phrase_downgraded_when_engine_flag_off(account, engine):
    engine.compliance.block_on_banned_phrase = False
    spec = make_spec(caption="การันตี 100% ทุกใบ")
    report = run_compliance(spec, account, engine)
    assert report.ok is True
    assert all(f.severity == "warn" for f in report.findings if f.rule == RULE_BANNED_PHRASE)


def test_oracle_predictive_claim_warns_r31(account):
    spec = make_spec(caption="การ์ดวันนี้บอกว่าพรุ่งนี้จะเจอคนที่ใช่")
    findings = deterministic_check(spec, account)
    r31 = [f for f in findings if f.rule == "R-3.1"]
    assert len(r31) == 1
    assert r31[0].severity == "warn"
    assert "จะเจอ" in r31[0].detail


def test_predictive_marker_negation_not_flagged():
    assert predictive_markers("เราไม่ได้มาทำนายว่าพรุ่งนี้จะเป็นไง") == []
    assert predictive_markers("การ์ดนี้ฟันธงว่าเดือนหน้าจะรวย") != []


def test_predictive_check_is_c2_only(account):
    spec = make_spec(content_pillar="C9", media="M6", caption="คนแบบเราจะได้อะไรจากธูปดอกเดียว 😂")
    assert [f for f in deterministic_check(spec, account) if f.rule == "R-3.1"] == []


def test_ai_visual_without_image_spec_warns(account):
    findings = deterministic_check(make_spec(image=None), account)
    hit = [f for f in findings if f.rule == RULE_AI_VISUAL_NO_IMAGE]
    assert len(hit) == 1 and hit[0].severity == "warn"


def test_homage_watch_warns_r36(account):
    findings = deterministic_check(make_spec(homage_watch=True), account)
    hit = [f for f in findings if f.rule == "R-3.6"]
    assert len(hit) == 1 and hit[0].severity == "warn"
    assert "homage-watch" in hit[0].detail


def test_empty_hashtags_warns(account):
    findings = deterministic_check(make_spec(hashtags=[]), account)
    assert [f.rule for f in findings if f.rule == RULE_NO_HASHTAGS] == [RULE_NO_HASHTAGS]


def test_empty_caption_blocks_on_full_spec(account):
    findings = deterministic_check(make_spec(caption="", hook=""), account)
    hit = [f for f in findings if f.rule == RULE_EMPTY_CAPTION]
    assert len(hit) == 1 and hit[0].severity == "block"


def test_empty_caption_on_outline_row_is_not_a_block(account):
    """Days 8-30 are outline rows — they legitimately have no caption yet."""
    findings = deterministic_check(make_spec(caption="", hook="", full_spec=False), account)
    assert [f for f in findings if f.rule == RULE_EMPTY_CAPTION] == []


# ── LLM QA (skipped path — no network) ─────────────────────────────────────


def test_llm_qa_skipped_when_disabled(account, engine):
    report, usage = llm_qa(make_spec(), account, engine)
    assert report.ok is True
    assert report.voice_test_pass is None
    assert [f.rule for f in report.findings] == [RULE_LLM_QA_SKIPPED]
    assert report.findings[0].severity == "warn"
    assert report.findings[0].source == "llm"
    assert usage.called is False
    assert usage.cost_usd == 0.0


def test_llm_qa_skipped_when_no_credentials(account, engine, monkeypatch, tmp_path):
    engine.llm.enabled = True
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    monkeypatch.setenv("ANTHROPIC_CONFIG_DIR", str(tmp_path / "no-such-profile"))
    report, usage = llm_qa(make_spec(), account, engine)
    assert [f.rule for f in report.findings] == [RULE_LLM_QA_SKIPPED]
    assert usage.called is False


# ── LLM QA (fake client — still no network) ────────────────────────────────


class _FakeUsage:
    input_tokens = 1200
    cache_creation_input_tokens = 0
    cache_read_input_tokens = 0
    output_tokens = 300


class _FakeResponse:
    def __init__(self, parsed, stop_reason="end_turn", model="claude-opus-5"):
        self.parsed_output = parsed
        self.stop_reason = stop_reason
        self.model = model
        self.usage = _FakeUsage()


def install_fake_client(monkeypatch, response, recorder=None):
    """Swap anthropic.Anthropic for a stub that records the request and returns `response`."""
    import anthropic

    class _Messages:
        def parse(self, **kwargs):
            if recorder is not None:
                recorder.update(kwargs)
            if isinstance(response, Exception):
                raise response
            return response

    class _FakeAnthropic:
        def __init__(self, *args, **kwargs):
            self.messages = _Messages()

    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test-not-a-real-key")
    monkeypatch.setattr(anthropic, "Anthropic", _FakeAnthropic)


def test_llm_qa_success_maps_findings_and_cost(account, engine, monkeypatch):
    from lumora_sprint.models import ComplianceFinding, ComplianceReport

    engine.llm.enabled = True
    parsed = ComplianceReport(
        ok=True,
        findings=[
            # source deliberately wrong — llm_qa must stamp it back to 'llm'
            ComplianceFinding(rule="R-3.1", severity="warn", detail="เฉียดการทำนาย", source="deterministic")
        ],
        voice_test_pass=True,
        suggested_caption=None,
    )
    sent: dict = {}
    install_fake_client(monkeypatch, _FakeResponse(parsed), recorder=sent)

    report, usage = llm_qa(make_spec(), account, engine)

    assert [f.rule for f in report.findings] == ["R-3.1"]
    assert report.findings[0].source == "llm"
    assert report.voice_test_pass is True
    assert usage.called is True
    assert usage.input_tokens == 1200 and usage.output_tokens == 300
    assert usage.cost_usd == pytest.approx(1200 / 1e6 * 5 + 300 / 1e6 * 25)

    # model + effort come from engine.yaml only — never hardcoded
    assert sent["model"] == engine.llm.model
    assert sent["output_config"] == {"effort": engine.llm.effort}
    assert sent["output_format"] is ComplianceReport
    assert "มูมีแสง" in sent["system"] and "R-3.1" in sent["system"]
    assert "L1-D01" in sent["messages"][0]["content"]


def test_llm_qa_block_finding_makes_report_not_ok(account, engine, monkeypatch):
    from lumora_sprint.models import ComplianceFinding, ComplianceReport

    engine.llm.enabled = True
    parsed = ComplianceReport(
        ok=True,  # model contradicts itself — we recompute ok from the findings
        findings=[ComplianceFinding(rule="R-3.3", severity="block", detail="สัญญาผลตอบแทน")],
    )
    install_fake_client(monkeypatch, _FakeResponse(parsed))
    report, _ = llm_qa(make_spec(), account, engine)
    assert report.ok is False

    merged = run_compliance(make_spec(), account, engine)
    assert merged.ok is False


def test_llm_qa_budget_never_drops_below_the_thinking_floor(account, engine, monkeypatch):
    """max_tokens caps thinking + text together, so a small configured value truncates the JSON."""
    from lumora_sprint.compliance import MIN_QA_MAX_TOKENS
    from lumora_sprint.models import ComplianceReport

    engine.llm.enabled = True
    engine.llm.max_tokens = 2048                      # the shipped engine.yaml value
    sent: dict = {}
    install_fake_client(monkeypatch, _FakeResponse(ComplianceReport(ok=True)), recorder=sent)

    llm_qa(make_spec(), account, engine)
    assert sent["max_tokens"] == MIN_QA_MAX_TOKENS

    engine.llm.max_tokens = MIN_QA_MAX_TOKENS * 2     # config may raise it, never lower it
    llm_qa(make_spec(), account, engine)
    assert sent["max_tokens"] == MIN_QA_MAX_TOKENS * 2


def test_llm_qa_names_truncation_instead_of_blaming_structured_output(account, engine, monkeypatch):
    """A truncated answer must say 'max_tokens', not the generic 'no structured output' finding."""
    engine.llm.enabled = True
    install_fake_client(monkeypatch, _FakeResponse(None, stop_reason="max_tokens"))

    report, usage = llm_qa(make_spec(), account, engine)

    assert [f.rule for f in report.findings] == ["llm_qa_error"]
    assert "max_tokens" in report.findings[0].detail
    assert usage.ok is False and usage.detail == "truncated: max_tokens"
    assert usage.cost_usd > 0                          # the call was still paid for


def test_llm_qa_refusal_degrades_to_warn(account, engine, monkeypatch):
    engine.llm.enabled = True
    install_fake_client(monkeypatch, _FakeResponse(None, stop_reason="refusal"))
    report, usage = llm_qa(make_spec(), account, engine)
    assert report.ok is True
    assert [f.rule for f in report.findings] == ["llm_qa_error"]
    assert usage.ok is False and usage.detail == "refusal"


def test_llm_qa_api_error_never_breaks_the_loop(account, engine, monkeypatch):
    engine.llm.enabled = True
    install_fake_client(monkeypatch, RuntimeError("boom"))
    report, usage = llm_qa(make_spec(), account, engine)
    assert report.ok is True
    assert [f.rule for f in report.findings] == ["llm_qa_error"]
    assert "boom" in report.findings[0].detail
    assert usage.ok is False


def test_run_compliance_merges_both_passes(account, engine):
    spec = make_spec(homage_watch=True, hashtags=[])
    report, usage = run_compliance_with_usage(spec, account, engine)
    rules = [f.rule for f in report.findings]
    assert "R-3.6" in rules and RULE_NO_HASHTAGS in rules and RULE_LLM_QA_SKIPPED in rules
    assert report.ok is True  # warns only
    assert usage.cost_usd == 0.0


# ── cost table ─────────────────────────────────────────────────────────────


def test_price_table_prefix_match_and_default():
    assert price_for("claude-opus-5") == (5.0, 25.0)
    assert price_for("claude-sonnet-5") == (3.0, 15.0)
    assert price_for("claude-haiku-4-5") == (1.0, 5.0)
    assert price_for("some-future-model") == (5.0, 25.0)
    assert price_for("") == (5.0, 25.0)


def test_estimate_cost_usd():
    # 1M in + 1M out on opus-tier = $5 + $25
    assert estimate_cost_usd("claude-opus-5", 1_000_000, 1_000_000) == 30.0
    assert estimate_cost_usd("claude-opus-5", 0, 0) == 0.0
    assert estimate_cost_usd("claude-haiku-4-5", 2000, 500) == pytest.approx(0.0045, abs=1e-6)
