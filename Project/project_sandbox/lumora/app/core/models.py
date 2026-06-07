"""Domain types + the decision STATE MACHINE (07 §4 "state machine กัน auto-publish").

The state machine is the safety seam: nothing auto-publishes. Sin approves at the
combo step (decision #2: per-combo first, with revise). Stale/rejected combos go
to `archived` (decision #4), never hard-deleted.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Status(str, Enum):
    SUGGESTED = "suggested"
    REVIEWING = "reviewing"
    REVISED = "revised"
    APPROVED = "approved"
    REJECTED = "rejected"
    GENERATING = "generating"
    ASSET_READY = "asset_ready"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"


# Allowed transitions. Enforced by `assert_transition`.
# decision #4: anything (except terminal published) can be archived (idea bank).
TRANSITIONS: dict[Status, set[Status]] = {
    Status.SUGGESTED:   {Status.REVIEWING, Status.REVISED, Status.APPROVED,
                         Status.REJECTED, Status.ARCHIVED},
    Status.REVIEWING:   {Status.REVISED, Status.APPROVED, Status.REJECTED, Status.ARCHIVED},
    Status.REVISED:     {Status.APPROVED, Status.REJECTED, Status.ARCHIVED},
    Status.APPROVED:    {Status.GENERATING, Status.ARCHIVED},
    Status.GENERATING:  {Status.ASSET_READY, Status.FAILED},
    Status.ASSET_READY: {Status.SCHEDULED, Status.ARCHIVED},
    Status.SCHEDULED:   {Status.PUBLISHED, Status.FAILED, Status.ARCHIVED},
    Status.PUBLISHED:   set(),                          # terminal
    Status.REJECTED:    {Status.ARCHIVED},
    Status.FAILED:      {Status.GENERATING, Status.ARCHIVED},
    Status.ARCHIVED:    set(),                          # terminal (idea bank)
}

# decision #5: reject reasons are FIXED TAGS (mirror of reject_reasons table).
REJECT_TAGS = {
    "off_brand", "off_trend", "low_fit", "fatigued",
    "seasonal_miss", "compliance", "duplicate", "other",
}


class InvalidTransition(Exception):
    pass


def assert_transition(current: Status, target: Status) -> None:
    if target not in TRANSITIONS[current]:
        raise InvalidTransition(f"{current.value} -> {target.value} not allowed")


class Combo(BaseModel):
    """A Content × Theme × Media recommendation (+ jtbd, funnel)."""
    content_pillar: str
    theme: str
    media_format: str
    jtbd: str | None = None
    funnel_stage: str | None = None
    product_id: str | None = None
    product_name: str | None = None
    concept: str | None = None


class ScoreBreakdown(BaseModel):
    """07 §3 weighted formula components (each normalized 0..1, fatigue subtracts)."""
    trend: float = 0.0
    fit: float = 0.0
    lift: float = 0.0
    recency: float = 0.0
    season: float = 0.0
    fatigue: float = 0.0
    total: float = 0.0


class Decision(BaseModel):
    decision_id: str
    brand_id: str
    account_id: str | None = None
    trigger_type: str = "trend"
    status: Status = Status.SUGGESTED
    recommendation: Combo
    score: float = 0.0
    score_breakdown: ScoreBreakdown = Field(default_factory=ScoreBreakdown)
    reject_reason: str | None = None
    approved_by: str | None = None
    asset_url: str | None = None
    caption: str | None = None
    # production pipeline (07 §2.5): which steps ran + the summed cost estimate.
    # `production_trace` is a list of dicts (StepTrace.model_dump) to keep models.py
    # free of an import cycle with app.production.
    production_trace: list[dict] = Field(default_factory=list)
    production_cost_estimate: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
