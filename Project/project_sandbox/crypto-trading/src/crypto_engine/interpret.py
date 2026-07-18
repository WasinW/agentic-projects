"""Interpretive LLM layer — Step 1.5.

Takes the deterministic digest (NOT raw candles) and asks Claude to produce the
LLM-owned blocks of the §6 contract: Elliott Wave reads, daily/weekly/monthly
summaries, and a trade plan. Also returns a single `elliott_1d` vote that the
engine folds into confluence at a low weight (ADR 0007).

Runtime layer: this calls the Anthropic API from the engine itself (NOT Claude
Code). Requires ANTHROPIC_API_KEY. Uses adaptive thinking + structured outputs.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal, Optional

from pydantic import BaseModel, Field

from .config import EngineConfig
from .contract import Elliott, ElliottTF, Plan, Step1Output, Summaries

# Model + call params live in config/engine.yaml (cfg.llm); default = claude-sonnet-5
# (ADR 0013 — Opus was overkill for this digest-summarisation task). Never hardcoded.

Dir = Literal["up", "down", "sideways"]
Conf = Literal["low", "medium", "high"]
Vote = Literal["long", "short", "neutral"]


# ---------- LLM output schema (decoupled from the contract) ----------
class LLMElliottTF(BaseModel):
    degree: Optional[str] = None
    current_wave: Optional[str] = None
    structure: Optional[str] = None
    sub_wave: Optional[str] = None
    implied_direction: Optional[Dir] = None
    primary_count: Optional[str] = None
    alt_count: Optional[str] = None
    invalidation: Optional[float] = None
    confidence: Optional[Conf] = None
    note: Optional[str] = None


class LLMInterpretation(BaseModel):
    tf_1d: LLMElliottTF
    tf_4h: LLMElliottTF
    tf_1h: LLMElliottTF
    # single integrated Elliott vote for the confluence signal (supporting view)
    elliott_vote: Vote = Field(description="neutral if primary/alt counts disagree on direction or 1d confidence is low")
    elliott_value: str = Field(description="short label e.g. 'wave 3-of-C'")
    summary_daily: str
    summary_weekly: str
    summary_monthly: str
    plan_playbook: str = Field(description="e.g. sell-the-rip (trend-following), buy-the-dip, range-fade, stand-aside")
    plan_entry_zone: list[float]
    plan_stop: float = Field(description="use the provided deterministic invalidation price")
    plan_targets: list[float]
    plan_r_r: float
    plan_sizing_note: str
    plan_note: str


SYSTEM = """You are a disciplined crypto market technician feeding a deterministic \
decision-support engine. You receive a pre-computed DIGEST (not raw candles): regime, \
bias, weighted signals, support/resistance, invalidation, per-timeframe RSI/structure/ \
swings, MA values, and volatility regime.

Your job is the INTERPRETIVE layer only:
1. Elliott Wave per timeframe (1d most reliable; 1h is noisy -> low confidence). Count \
waves ONLY from the provided `pivot_series_1d` (the full chronological swing high/low \
sequence, ~30-40 pivots) — do NOT invent pivots beyond it. If the series is too short or \
choppy to label a clean impulse/correction, say so and set confidence low. EW is the \
LEAST reliable input and a SUPPORTING view only. Give a primary count + an alternate \
count. Set elliott_vote to neutral if the primary and alternate counts disagree on \
direction, or if 1d confidence is low. Never let EW override structure/MA.
2. daily / weekly / monthly summaries — concise, grounded ONLY in the digest.
3. A trade plan consistent with the deterministic bias and levels: use the provided \
invalidation price as the stop; pick entry_zone and targets from the provided S/R; \
compute r_r = reward/risk. If bias is neutral/low-conviction, playbook = "stand-aside".

Rules: This is decision-support, not advice. Do not invent numbers absent from the \
digest. Respect: no counter-trend trades; oversold != long; macro/ETF flow can override \
technicals. Keep prose tight."""


@dataclass
class InterpretResult:
    elliott: Elliott
    summaries: Summaries
    plan: Plan
    elliott_vote: str
    elliott_value: str


def _to_tf(t: LLMElliottTF) -> ElliottTF:
    return ElliottTF(
        degree=t.degree, current_wave=t.current_wave, structure=t.structure,
        sub_wave=t.sub_wave, implied_direction=t.implied_direction,
        primary_count=t.primary_count, alt_count=t.alt_count,
        invalidation=t.invalidation, confidence=t.confidence, note=t.note,
    )


def interpret(out: Step1Output, digest: dict, cfg: EngineConfig, client=None) -> InterpretResult:
    """Call Claude to produce Elliott / summaries / plan from the digest."""
    import anthropic  # imported lazily so the deterministic path needs no key

    client = client or anthropic.Anthropic()
    user = (
        "DIGEST (deterministic features — interpret, do not recompute):\n"
        + json.dumps(digest, indent=2, default=str)
    )
    resp = client.messages.parse(
        model=cfg.llm.model,
        max_tokens=cfg.llm.max_tokens,
        thinking={"type": "adaptive"},
        output_config={"effort": cfg.llm.effort},
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
        output_format=LLMInterpretation,
    )
    r: LLMInterpretation = resp.parsed_output
    if r is None:
        raise RuntimeError("LLM did not return a parseable interpretation")

    elliott = Elliott(tf_1d=_to_tf(r.tf_1d), tf_4h=_to_tf(r.tf_4h), tf_1h=_to_tf(r.tf_1h))
    summaries = Summaries(daily=r.summary_daily, weekly=r.summary_weekly, monthly=r.summary_monthly)
    plan = Plan(
        playbook=r.plan_playbook, entry_zone=r.plan_entry_zone, stop=r.plan_stop,
        targets=r.plan_targets, r_r=r.plan_r_r, sizing_note=r.plan_sizing_note, note=r.plan_note,
    )
    return InterpretResult(elliott, summaries, plan, r.elliott_vote, r.elliott_value)
