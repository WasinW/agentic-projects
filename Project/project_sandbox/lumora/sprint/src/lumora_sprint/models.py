"""Locked pydantic contracts for the Lumora sprint loop.

Deterministic core, LLM surgical (07 §2). Every module imports these; nobody redefines them.
Naming maps 1:1 onto sprint-2026-07/02-post-log-template.md (post_log) and the batch spec
(01-batch-30day.md) so Phase-2 ingest into Supabase posts+performance is a column map.
"""
from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, field_validator

# ── enums / fixed tags ─────────────────────────────────────────────────────

Funnel = Literal["Hero", "Hub", "Hygiene"]

HOOK_TYPES: tuple[str, ...] = (
    "curiosity-choice",  # ชวนเลือก/ทายก่อนเฉลย
    "statement",         # ประโยคยืนยัน/ทัศนะ
    "relatable-callout", # ประเภทคนที่... (self-deprecating)
    "question",          # ตั้งคำถามตรงกับผู้ชม
    "list-promise",      # สัญญาว่ามีของให้เลือก N อย่าง
    "milestone",         # หมุด/โอกาส/ครบรอบ
    "other",             # fixed bucket, not free text
)


class PacketStatus(StrEnum):
    """Publish-packet state machine (human-gated, no auto-publish — ADR-0001 rule 5)."""
    planned = "planned"        # spec loaded from batch, nothing generated
    generated = "generated"    # image(s) on disk
    draft = "draft"            # packet assembled + compliance QA run
    blocked = "blocked"        # deterministic compliance hit — edit caption then re-run packet
    approved = "approved"      # Sin approved (human gate) — ready to upload BY HAND
    published = "published"    # Sin posted manually and logged the URL (post_log row exists)


# ── batch spec (input) ─────────────────────────────────────────────────────

class ImageSpec(BaseModel):
    prompt: str
    negative: str = ""
    aspect_ratio: str = "9:16"
    seed: int | None = None
    steps: int | None = None
    guidance: float | None = None
    count: int = 1                       # M2 carousel = 5..10; M1/M11 = 1
    variation: str = ""                  # free note from lumora-art-prompt (e.g. "vary palette per card")


class PostSpec(BaseModel):
    """One planned post = one labelled point in the C x T x M space (Framework v3)."""
    post_id: str = Field(pattern=r"^L\d+-D\d{2}$")   # 'L1-D01' — week + 2-digit day
    day: int = Field(ge=1, le=90)
    week: int = Field(ge=1)
    content_pillar: str = Field(pattern=r"^C(10|[1-9])$")
    theme: str
    media: str = Field(pattern=r"^M(1[0-2]|[1-9])$")
    funnel_stage: Funnel = "Hub"
    jtbd: str = ""
    hook_type: str = "other"
    concept: str = ""
    hook: str = ""                        # บรรทัดแรก
    caption: str = ""                     # full caption in the account voice (Thai)
    hashtags: list[str] = Field(default_factory=list)
    affiliate_angle: str = ""             # what to ปักตะกร้า (or "none" / "own product")
    ai_visual: bool = True                # -> AI label required
    homage_watch: bool = False            # sacred imagery — watch reaction, be ready to pull
    image: ImageSpec | None = None
    notes: str = ""
    full_spec: bool = True                # False = outline row (days 8-30) — needs expansion before generate

    @field_validator("hook_type")
    @classmethod
    def _hook_type_fixed(cls, v: str) -> str:
        if v not in HOOK_TYPES:
            raise ValueError(f"hook_type must be one of {HOOK_TYPES}, got {v!r}")
        return v


class Batch(BaseModel):
    batch_id: str                         # e.g. '2026-07-w1'
    account_handle: str
    posts: list[PostSpec]


# ── generation / packet (working state) ────────────────────────────────────

class GeneratedImage(BaseModel):
    path: str
    provider: str                         # replicate | stub
    model: str
    seed: int | None = None
    prompt: str
    est_cost_usd: float = 0.0
    duration_s: float = 0.0


class ComplianceFinding(BaseModel):
    rule: str                             # R-3.1 .. R-3.9 or 'banned_phrase'
    severity: Literal["block", "warn"]
    detail: str
    source: Literal["deterministic", "llm"] = "deterministic"


class ComplianceReport(BaseModel):
    """Structured output contract for the LLM QA pass (messages.parse) + deterministic findings."""
    ok: bool
    findings: list[ComplianceFinding] = Field(default_factory=list)
    voice_test_pass: bool | None = None   # can you tell it's this channel without the image?
    suggested_caption: str | None = None  # only if a block/warn needs rewording; else None


class Packet(BaseModel):
    """What ends up in out/<post_id>/meta.json — the publish packet Sin uploads by hand."""
    post_id: str
    brand_id: str
    account_handle: str
    status: PacketStatus = PacketStatus.planned
    spec: PostSpec
    images: list[GeneratedImage] = Field(default_factory=list)
    compliance: ComplianceReport | None = None
    caption_final: str = ""               # after any suggested rewording accepted by Sin
    ai_labeled_reminder: bool = True
    approved_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# ── log / metrics (output) ─────────────────────────────────────────────────

class LogRow(BaseModel):
    """post_log insert (02-post-log-template §4) + accountability columns (log from post #1)."""
    post_id: str
    brand_id: str = "own"
    account_handle: str
    posted_at: date
    content_pillar: str
    theme: str
    media: str
    jtbd: str = ""
    funnel_stage: Funnel = "Hub"
    hook_type: str = "other"
    ai_labeled: bool = True
    url: str = ""
    notes: str = ""
    # accountability byproduct (agent-failure dataset seed): which agent/prompt/model produced it, at what cost
    agent: str = "lumora-sprint"
    prompt_version: str = ""              # batch_id or spec hash
    gen_model: str = ""
    cost_usd: float = 0.0


class MetricsUpdate(BaseModel):
    """Empty beats fake — only set what was actually measured."""
    post_id: str
    views_24h: int | None = None
    views_7d: int | None = None
    likes: int | None = None
    comments: int | None = None
    shares: int | None = None
    saves: int | None = None
    follows_delta: int | None = None
    gmv: float | None = None
    notes: str | None = None


class AgentEvent(BaseModel):
    """One line in out/agent_events.jsonl — the accountability layer's raw material (cannot be backfilled)."""
    ts: datetime = Field(default_factory=datetime.now)
    agent: str
    step: str                             # plan | generate | qa | packet | approve | log | metrics | review
    post_id: str | None = None
    model: str | None = None
    prompt_version: str | None = None
    cost_usd: float = 0.0
    duration_s: float = 0.0
    ok: bool = True
    detail: str = ""
