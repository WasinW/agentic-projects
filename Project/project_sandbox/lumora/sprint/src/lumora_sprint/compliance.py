"""Compliance gate — the one place the taboo lines are enforced (07 §2, ADR-0001 guardrails).

Two passes, in this order:

1. :func:`deterministic_check` — pure functions, zero I/O. Substring hits on
   ``account.compliance.banned_phrases_th`` plus flag checks on the spec. This pass is what makes
   the loop runnable with no API key at all.
2. :func:`llm_qa` — ONE structured-output call (``messages.parse`` -> :class:`ComplianceReport`)
   that catches the paraphrases a substring pass cannot see. Surgical by design: if the LLM is
   disabled, has no credentials, refuses, or errors, we degrade to a ``warn`` finding and the loop
   keeps running. Compliance QA never raises into the hot path.

:func:`run_compliance` merges both; ``ok`` is False iff any finding has severity ``block``.

Rule ids: ``R-3.1``..``R-3.9`` are the hard taboo lines (mirrors ``account.compliance``);
``banned_phrase`` is the deterministic substring hit; the remaining lowercase ids are
spec-completeness / plumbing findings.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, replace
from pathlib import Path

from .config import AccountConfig, EngineConfig
from .models import ComplianceFinding, ComplianceReport, PostSpec

# ── rule catalogue ─────────────────────────────────────────────────────────

TABOO_RULES: dict[str, str] = {
    "R-3.1": "no prediction / guaranteed outcome — frame as belief, meaning, reflection",
    "R-3.2": "no medical claim (หายป่วย / รักษาโรค / เลิกยา)",
    "R-3.3": "no financial claim (รวยแน่ / กำไรแน่ / เลขเด็ด)",
    "R-3.4": "no fear-mongering (ถ้าไม่ทำ...จะซวย / มีอันเป็นไป)",
    "R-3.5": "comedy = self-deprecating only — never mock believers, beliefs or deities",
    "R-3.6": "sacred imagery = respectful homage; homage-watch 24h and be ready to pull",
    "R-3.7": "AI label ON for every AI visual, from post #1",
    "R-3.8": "PDPA — collect no personal data (no birthdates, no DM harvesting) during the sprint",
    "R-3.9": "manual publish only — never an unofficial auto-publisher",
}

# which account.compliance flag switches each taboo line on
_RULE_FLAGS: dict[str, str] = {
    "R-3.1": "no_prediction",
    "R-3.2": "no_medical",
    "R-3.3": "no_financial",
    "R-3.4": "no_fear_mongering",
    "R-3.5": "comedy_self_deprecating_only",
    "R-3.7": "ai_label_every_ai_visual",
    "R-3.8": "pdpa_no_personal_data",
    "R-3.9": "manual_publish_only",
}

# non-taboo rule ids (plumbing / spec completeness) — kept fixed so the log can group on them
RULE_BANNED_PHRASE = "banned_phrase"
RULE_EMPTY_CAPTION = "empty_caption"
RULE_NO_HASHTAGS = "no_hashtags"
RULE_AI_VISUAL_NO_IMAGE = "ai_visual_no_image"
RULE_LLM_QA_SKIPPED = "llm_qa_skipped"
RULE_LLM_QA_ERROR = "llm_qa_error"

#: Floor applied to ``engine.llm.max_tokens`` for the QA call (engine.yaml may set it higher).
#: On the configured Claude models adaptive thinking is ON whenever no ``thinking`` field is sent,
#: and ``max_tokens`` caps thinking + response text *together*. A long Thai caption plus the ~1.5KB
#: system brief can burn a small budget on thinking and return truncated JSON — a failure that is
#: only discovered after the call has already been paid for.
MIN_QA_MAX_TOKENS = 8000

# Predictive markers for R-3.1. Deliberately specific: the channel's own voice says
# "เราไม่ได้มาทำนาย..." constantly, so a bare 'แน่' would fire on 'ไม่แน่ใจ'. Combined forms
# ('ได้แน่', 'ปังแน่') carry the guarantee; a negation guard drops "ไม่...ทำนาย" style phrasing.
PREDICTIVE_MARKERS_TH: tuple[str, ...] = (
    "จะได้",
    "จะรวย",
    "จะเจอ",
    "จะปัง",
    "จะสมหวัง",
    "จะดีขึ้น",
    "ได้แน่",
    "รวยแน่",
    "ปังแน่",
    "ดีแน่",
    "สมหวังแน่",
    "ทำนาย",
    "ฟันธง",
    "รับรองว่า",
    "ดวงบอกว่า",
    "เลขเด็ด",
)

_NEGATION_MARKERS: tuple[str, ...] = ("ไม่", "มิได้", "ห้าม")
_NEGATION_WINDOW = 16  # chars to look back before a marker for a negation


# ── pass 1: deterministic ──────────────────────────────────────────────────


def _is_negated(text: str, idx: int, window: int = _NEGATION_WINDOW) -> bool:
    """True if a negation word sits just before ``idx`` (e.g. 'เราไม่ได้มาทำนาย')."""
    start = max(0, idx - window)
    return any(n in text[start:idx] for n in _NEGATION_MARKERS)


def predictive_markers(text: str) -> list[str]:
    """Return the predictive/guarantee markers present in ``text``, negations excluded (R-3.1)."""
    hits: list[str] = []
    for marker in PREDICTIVE_MARKERS_TH:
        idx = text.find(marker)
        while idx != -1:
            if not _is_negated(text, idx):
                hits.append(marker)
                break
            idx = text.find(marker, idx + 1)
    return hits


def banned_phrase_hits(text: str, banned: list[str]) -> list[str]:
    """Case-insensitive substring hits from the account's banned-phrase list."""
    hay = text.lower()
    return [p for p in (b.strip() for b in banned) if p and p.lower() in hay]


def deterministic_check(spec: PostSpec, account: AccountConfig) -> list[ComplianceFinding]:
    """Pure taboo + completeness checks on one spec. No I/O, no network, no LLM.

    Findings, in order:
      * ``banned_phrase``  block — a phrase from ``banned_phrases_th`` appears in hook/caption
      * ``R-3.1``          warn  — a C2 oracle caption makes a predictive/guarantee claim
      * ``empty_caption``  block — a full-spec post has no caption to publish
      * ``ai_visual_no_image`` warn — AI visual declared but no ImageSpec to generate from
      * ``R-3.6``          warn  — sacred-imagery homage-watch: note it in the log
      * ``no_hashtags``    warn  — nothing to paste into the hashtag field
    """
    findings: list[ComplianceFinding] = []
    hook = spec.hook or ""
    caption = spec.caption or ""
    text = f"{hook}\n{caption}"

    for phrase in banned_phrase_hits(text, account.compliance.banned_phrases_th):
        findings.append(
            ComplianceFinding(
                rule=RULE_BANNED_PHRASE,
                severity="block",
                detail=f"พบวลีต้องห้าม {phrase!r} ใน hook/caption — แก้ข้อความก่อนโพสต์",
            )
        )

    if spec.content_pillar == "C2" and account.compliance.no_prediction:
        hits = predictive_markers(text)
        if hits:
            findings.append(
                ComplianceFinding(
                    rule="R-3.1",
                    severity="warn",
                    detail=(
                        f"oracle caption มีคำเชิงทำนาย/การันตี {hits} — "
                        f"{TABOO_RULES['R-3.1']}"
                    ),
                )
            )

    if spec.full_spec and not caption.strip():
        findings.append(
            ComplianceFinding(
                rule=RULE_EMPTY_CAPTION,
                severity="block",
                detail="full_spec=True แต่ caption ว่าง — ขยาย outline ให้เป็น full spec ก่อน",
            )
        )

    if spec.ai_visual and spec.image is None:
        findings.append(
            ComplianceFinding(
                rule=RULE_AI_VISUAL_NO_IMAGE,
                severity="warn",
                detail="ai_visual=True แต่ไม่มี ImageSpec — generate ไม่ได้ (และยังต้องเปิด AI label, R-3.7)",
            )
        )

    if spec.homage_watch:
        findings.append(
            ComplianceFinding(
                rule="R-3.6",
                severity="warn",
                detail=f"homage-watch: note in log — {TABOO_RULES['R-3.6']}",
            )
        )

    if not spec.hashtags:
        findings.append(
            ComplianceFinding(
                rule=RULE_NO_HASHTAGS,
                severity="warn",
                detail="ไม่มี hashtags — อย่างน้อย 1 tag ต่อ dimension (niche / theme / format / brand)",
            )
        )

    return findings


# ── cost estimate ──────────────────────────────────────────────────────────

# USD per 1M tokens (input, output), keyed by model-id prefix. Config-driven model ids mean this
# table must degrade gracefully: unknown prefix -> DEFAULT (opus-tier) so cost is never under-reported.
PRICE_PER_MTOK_USD: dict[str, tuple[float, float]] = {
    "claude-fable": (10.0, 50.0),
    "claude-mythos": (10.0, 50.0),
    "claude-opus": (5.0, 25.0),
    "claude-sonnet": (3.0, 15.0),
    "claude-haiku": (1.0, 5.0),
}
DEFAULT_PRICE_PER_MTOK_USD: tuple[float, float] = (5.0, 25.0)


def price_for(model: str) -> tuple[float, float]:
    """(input, output) USD per 1M tokens for a model id, by longest matching prefix."""
    m = (model or "").lower()
    for prefix in sorted(PRICE_PER_MTOK_USD, key=len, reverse=True):
        if m.startswith(prefix):
            return PRICE_PER_MTOK_USD[prefix]
    return DEFAULT_PRICE_PER_MTOK_USD


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    """Approximate list-price cost of one QA call (no cache discount applied — empty beats fake)."""
    p_in, p_out = price_for(model)
    return round(input_tokens / 1_000_000 * p_in + output_tokens / 1_000_000 * p_out, 6)


@dataclass(frozen=True)
class LlmUsage:
    """What one QA call actually cost — packet.py / log.py write this into post_log.cost_usd."""

    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    ok: bool = True
    detail: str = ""

    @property
    def called(self) -> bool:
        """True if a request actually went out (a skipped pass has no model and no tokens)."""
        return bool(self.model) and (self.input_tokens > 0 or self.output_tokens > 0)


# ── pass 2: LLM QA (surgical) ──────────────────────────────────────────────


def credentials_available() -> bool:
    """True if the anthropic SDK can authenticate: env key/token, or an `ant auth login` profile.

    An unset ANTHROPIC_API_KEY does not mean 'no credentials' — the SDK also reads the OAuth
    profile written by `ant auth login`, so check that directory too.
    """
    if os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        return True
    cfg_dir = os.environ.get("ANTHROPIC_CONFIG_DIR")
    root = Path(cfg_dir) if cfg_dir else Path.home() / ".config" / "anthropic"
    creds = root / "credentials"
    try:
        return creds.is_dir() and any(creds.glob("*.json"))
    except OSError:
        return False


def build_qa_system_prompt(account: AccountConfig) -> str:
    """Compact auditor brief built from the account constraint set — no post content in here.

    Kept stable across posts on purpose: only the user turn varies, so the prefix stays cacheable
    if we ever turn caching on.
    """
    arch = account.archetype
    shading = ", ".join(f"{k}->{v}" for k, v in arch.shading.items()) or "none"
    active_rules = [
        f"- {rid}: {TABOO_RULES[rid]}"
        for rid, flag in _RULE_FLAGS.items()
        if getattr(account.compliance, flag, False)
    ]
    active_rules.append(f"- R-3.6: {TABOO_RULES['R-3.6']} (policy: {account.compliance.sacred_imagery})")
    banned = ", ".join(account.compliance.banned_phrases_th) or "(none)"
    return (
        "You are the compliance + voice auditor for one Thai creator channel. "
        "Audit ONE draft post and return a structured ComplianceReport. Be strict but not precious: "
        "this is art and reflection content, not advice.\n\n"
        f"CHANNEL: {account.account_handle} (catalog: {account.catalog}, {account.appearance})\n"
        f"ARCHETYPE: {arch.primary}"
        + (f" x {arch.secondary}" if arch.secondary else "")
        + f" (shading: {shading}) — fellow explorer, never a guru\n"
        f"VOICE: {account.voice.one_liner}\n"
        f"REGISTERS: {', '.join(account.voice.registers) or '(unspecified)'}\n"
        f"VOICE TEST: {account.voice.test}\n\n"
        "HARD TABOO LINES (rule id -> rule):\n"
        + "\n".join(sorted(set(active_rules)))
        + "\n\nBANNED PHRASES (already checked by substring — flag paraphrases of these):\n"
        f"{banned}\n\n"
        "HOW TO REPORT:\n"
        "- One finding per violated rule. `rule` MUST be one of R-3.1..R-3.9 (never free text).\n"
        "- `severity`: 'block' only for a real taboo violation that must not be published; "
        "'warn' for anything that is merely risky, off-voice, or worth noting in the log.\n"
        "- `source` MUST be 'llm'. `detail` in Thai, one sentence, actionable.\n"
        "- `voice_test_pass`: true if you could tell this is THIS channel from the caption alone.\n"
        "- `suggested_caption`: only when a block/warn needs rewording — otherwise null. "
        "Keep the author's voice; never turn it into marketing copy.\n"
        "- `ok`: true iff there is no 'block' finding.\n"
        "- No violations found is a normal, expected outcome — return an empty findings list."
    )


def build_qa_user_message(spec: PostSpec) -> str:
    """The draft post, flattened. Only fields an auditor needs to judge hook/caption/tags/affiliate."""
    lines = [
        f"post_id: {spec.post_id} (day {spec.day}, week {spec.week})",
        f"combo: {spec.content_pillar} x {spec.theme} x {spec.media} | funnel: {spec.funnel_stage}",
        f"jtbd: {spec.jtbd or '(none)'}",
        f"hook_type: {spec.hook_type}",
        f"ai_visual: {spec.ai_visual} | homage_watch: {spec.homage_watch}",
        "",
        f"HOOK (first line):\n{spec.hook or '(empty)'}",
        "",
        f"CAPTION:\n{spec.caption or '(empty)'}",
        "",
        f"HASHTAGS: {' '.join(spec.hashtags) or '(none)'}",
        f"AFFILIATE ANGLE: {spec.affiliate_angle or '(none)'}",
    ]
    if spec.image is not None:
        lines += ["", f"IMAGE PROMPT: {spec.image.prompt}"]
    return "\n".join(lines)


def _skipped(reason: str) -> tuple[ComplianceReport, LlmUsage]:
    return (
        ComplianceReport(
            ok=True,
            findings=[
                ComplianceFinding(rule=RULE_LLM_QA_SKIPPED, severity="warn", detail=reason, source="llm")
            ],
            voice_test_pass=None,
        ),
        LlmUsage(ok=True, detail=reason),
    )


def _errored(model: str, reason: str) -> tuple[ComplianceReport, LlmUsage]:
    return (
        ComplianceReport(
            ok=True,
            findings=[
                ComplianceFinding(rule=RULE_LLM_QA_ERROR, severity="warn", detail=reason, source="llm")
            ],
            voice_test_pass=None,
        ),
        LlmUsage(model=model, ok=False, detail=reason),
    )


def llm_qa(
    spec: PostSpec, account: AccountConfig, engine: EngineConfig
) -> tuple[ComplianceReport, LlmUsage]:
    """One structured-output QA call. Never raises — every failure becomes a `warn` finding.

    Returns ``(report, usage)``; ``usage`` carries the token counts + approximate cost so the
    caller can write ``post_log.cost_usd`` and an ``AgentEvent`` without a second call.
    """
    if not engine.llm.enabled:
        return _skipped("engine.llm.enabled=false — deterministic checks only")
    if not credentials_available():
        return _skipped("ไม่พบ ANTHROPIC credentials — ข้าม LLM QA (deterministic checks ยังทำงาน)")

    model = engine.llm.model
    try:
        import anthropic
    except ImportError:  # pragma: no cover - anthropic is a hard dep, guard is belt-and-braces
        return _errored(model, "anthropic SDK ไม่ได้ติดตั้ง — ข้าม LLM QA")

    try:
        client = anthropic.Anthropic()
        response = client.messages.parse(
            model=model,
            max_tokens=max(int(engine.llm.max_tokens), MIN_QA_MAX_TOKENS),
            system=build_qa_system_prompt(account),
            messages=[{"role": "user", "content": build_qa_user_message(spec)}],
            output_format=ComplianceReport,
            output_config={"effort": engine.llm.effort},
        )
    except anthropic.NotFoundError as exc:
        return _errored(model, f"model {model!r} ไม่พบ ({exc}) — ตรวจ engine.llm.model")
    except anthropic.RateLimitError as exc:
        return _errored(model, f"rate limited ({exc}) — ลอง qa ใหม่ภายหลัง")
    except anthropic.APIStatusError as exc:
        return _errored(model, f"API error {exc.status_code} ({exc}) — ข้าม LLM QA")
    except anthropic.APIConnectionError as exc:
        return _errored(model, f"เชื่อมต่อ API ไม่ได้ ({exc}) — ข้าม LLM QA")
    except Exception as exc:  # noqa: BLE001 - QA must never break the loop
        return _errored(model, f"LLM QA ล้มเหลว ({type(exc).__name__}: {exc}) — ข้าม")

    usage_obj = getattr(response, "usage", None)
    in_tok = sum(
        int(getattr(usage_obj, field, 0) or 0)
        for field in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
    )
    out_tok = int(getattr(usage_obj, "output_tokens", 0) or 0)
    used_model = getattr(response, "model", model) or model
    usage = LlmUsage(
        model=used_model,
        input_tokens=in_tok,
        output_tokens=out_tok,
        cost_usd=estimate_cost_usd(used_model, in_tok, out_tok),
    )

    stop_reason = getattr(response, "stop_reason", None)
    if stop_reason == "refusal":
        report, _ = _errored(used_model, "LLM ปฏิเสธคำขอ (stop_reason=refusal) — ตรวจด้วยตาแทน")
        return report, replace(usage, ok=False, detail="refusal")

    if stop_reason == "max_tokens":
        # named explicitly: truncation would otherwise surface as the generic "no structured
        # output" finding below, which points at the wrong fix (the budget, not the model).
        report, _ = _errored(
            used_model,
            f"คำตอบถูกตัดกลางคัน (stop_reason=max_tokens ที่ {out_tok} output tokens) — "
            "ขึ้น engine.llm.max_tokens แล้วรัน packet ใหม่",
        )
        return report, replace(usage, ok=False, detail="truncated: max_tokens")

    parsed = getattr(response, "parsed_output", None)
    if parsed is None:
        report, _ = _errored(used_model, "LLM ไม่คืน structured output — ข้าม LLM QA")
        return report, replace(usage, ok=False, detail="no parsed_output")

    findings = [f.model_copy(update={"source": "llm"}) for f in parsed.findings]
    report = ComplianceReport(
        ok=not any(f.severity == "block" for f in findings),
        findings=findings,
        voice_test_pass=parsed.voice_test_pass,
        suggested_caption=parsed.suggested_caption,
    )
    return report, usage


# ── merge ──────────────────────────────────────────────────────────────────


def has_rule(report: ComplianceReport | None, rule: str) -> bool:
    """True if ``report`` carries a finding with this rule id."""
    return bool(report) and any(f.rule == rule for f in report.findings)


def blocking_findings(report: ComplianceReport | None) -> list[ComplianceFinding]:
    """The findings that stop a packet from being approved."""
    return [f for f in report.findings if f.severity == "block"] if report else []


def run_compliance_with_usage(
    spec: PostSpec, account: AccountConfig, engine: EngineConfig
) -> tuple[ComplianceReport, LlmUsage]:
    """:func:`run_compliance` plus the token/cost record for the accountability log."""
    findings = deterministic_check(spec, account)
    if not engine.compliance.block_on_banned_phrase:
        findings = [
            f.model_copy(update={"severity": "warn"})
            if f.rule == RULE_BANNED_PHRASE and f.severity == "block"
            else f
            for f in findings
        ]

    llm_report, usage = llm_qa(spec, account, engine)
    merged = findings + list(llm_report.findings)
    report = ComplianceReport(
        ok=not any(f.severity == "block" for f in merged),
        findings=merged,
        voice_test_pass=llm_report.voice_test_pass,
        suggested_caption=llm_report.suggested_caption,
    )
    return report, usage


def run_compliance(spec: PostSpec, account: AccountConfig, engine: EngineConfig) -> ComplianceReport:
    """Full gate: deterministic findings + LLM QA findings, merged. ok = no 'block' finding."""
    report, _usage = run_compliance_with_usage(spec, account, engine)
    return report
