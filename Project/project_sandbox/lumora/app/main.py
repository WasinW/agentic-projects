"""LUMORA Phase 1.A — FastAPI app.

Approval workflow (decision #2: per-combo first + revise) + service-based metrics
ingestion (decision #1). The state machine (app/core/models.py) is enforced in the
repo, so invalid transitions return 409.
"""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import app.adapters  # noqa: F401  -> register default adapters
from app.core.models import (Combo, InvalidTransition, REJECT_TAGS, Status)
from app.core.repo import get_repo
from app.flow import pipeline

app = FastAPI(title="LUMORA Phase 1.A", version="0.1.0")


# ── request bodies ────────────────────────────────────────────────────────
class ReviseBody(BaseModel):
    content_pillar: str | None = None
    theme: str | None = None
    media_format: str | None = None
    jtbd: str | None = None
    funnel_stage: str | None = None
    concept: str | None = None


class RejectBody(BaseModel):
    reason_tag: str   # decision #5: must be one of REJECT_TAGS


class MetricsBody(BaseModel):
    post_id: str
    views: int = 0
    likes: int = 0
    shares: int = 0
    saves: int = 0
    clicks: int = 0
    conversions: int = 0
    revenue: float = 0.0


# ── health / cycle ────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"ok": True}


@app.post("/cycle")
def run_cycle():
    """⚙️ run one deterministic pipeline cycle -> writes suggested combos."""
    decisions = pipeline.run_cycle()
    return {"suggested": [d.decision_id for d in decisions], "count": len(decisions)}


# ── approval queue ────────────────────────────────────────────────────────
@app.get("/queue")
def queue(status: str = "suggested"):
    repo = get_repo()
    brand_id = repo.ensure_brand()
    items = repo.list_queue(brand_id, Status(status))
    return [
        {"decision_id": d.decision_id, "status": d.status.value, "score": d.score,
         "combo": d.recommendation.model_dump(), "breakdown": d.score_breakdown.model_dump()}
        for d in items
    ]


def _transition(decision_id: str, target: Status, **fields):
    try:
        d = get_repo().transition(decision_id, target, **fields)
    except KeyError:
        raise HTTPException(404, "decision not found")
    except InvalidTransition as e:
        raise HTTPException(409, str(e))
    return {"decision_id": d.decision_id, "status": d.status.value}


@app.post("/decisions/{decision_id}/approve")
def approve(decision_id: str):
    """approve -> triggers (mock) generation -> asset_ready."""
    try:
        out = pipeline.generate_for_decision(decision_id)
    except KeyError:
        raise HTTPException(404, "decision not found")
    except InvalidTransition as e:
        raise HTTPException(409, str(e))
    return {"decision_id": out.decision_id, "status": out.status.value,
            "asset_url": out.asset_url, "caption": out.caption}


@app.post("/decisions/{decision_id}/revise")
def revise(decision_id: str, body: ReviseBody):
    """edit the combo, then mark revised (decision #2 revise step)."""
    repo = get_repo()
    d = repo.get_decision(decision_id)
    if d is None:
        raise HTTPException(404, "decision not found")
    patch = {k: v for k, v in body.model_dump().items() if v is not None}
    combo = Combo(**{**d.recommendation.model_dump(), **patch})
    try:
        out = repo.transition(decision_id, Status.REVISED, recommendation=combo)
    except InvalidTransition as e:
        raise HTTPException(409, str(e))
    return {"decision_id": out.decision_id, "status": out.status.value,
            "combo": out.recommendation.model_dump()}


@app.post("/decisions/{decision_id}/reject")
def reject(decision_id: str, body: RejectBody):
    """reject with a FIXED tag (decision #5)."""
    if body.reason_tag not in REJECT_TAGS:
        raise HTTPException(422, f"reason_tag must be one of {sorted(REJECT_TAGS)}")
    return _transition(decision_id, Status.REJECTED, reject_reason=body.reason_tag)


@app.post("/decisions/{decision_id}/archive")
def archive(decision_id: str):
    """archive -> idea bank (decision #4: no hard delete)."""
    return _transition(decision_id, Status.ARCHIVED)


@app.post("/decisions/{decision_id}/publish")
def publish(decision_id: str):
    """asset_ready -> scheduled -> published (mock publisher)."""
    try:
        out = pipeline.publish_decision(decision_id)
    except KeyError:
        raise HTTPException(404, "decision not found")
    except InvalidTransition as e:
        raise HTTPException(409, str(e))
    return {"decision_id": out.decision_id, "status": out.status.value}


# ── metrics ingestion (decision #1: service/API, not manual paste) ────────
@app.post("/metrics")
def ingest_metrics(body: MetricsBody):
    """Service-based performance ingestion. Reusable for dealer/platform services
    later (07 §0.5). In-memory mode acks; PgRepo mode would INSERT into performance."""
    return {"ingested": True, "post_id": body.post_id,
            "note": "wire INSERT into performance when DATABASE_URL is set"}
