"""Step 1 output contract (§6 of doc/02-project-context.md) — LOCKED schema.

These pydantic models ARE the contract. The engine emits JSON that validates
against `Step1Output`. Symbol-agnostic: swap symbol/asset_class to reuse for
stocks/options.

v1 (deterministic) sets the interpretive blocks to null with a STABLE shape:
    elliott   = None
    summaries = None
    plan      = None
so downstream consumers (dashboard / Pine generator) can rely on fixed keys.
"""

from __future__ import annotations

from typing import Literal, Optional, Union

from pydantic import BaseModel, Field, model_validator

Vote = Literal["long", "short", "neutral"]
Direction = Literal["long", "short", "neutral"]
Trend = Literal["up", "down", "sideways"]
Conviction = Literal["low", "medium", "high"]
ConfidenceCat = Literal["low", "medium", "high"]


# ---------- meta ----------
class DataWindow(BaseModel):
    from_: str = Field(alias="from")  # date-only "YYYY-MM-DD"
    to: str

    model_config = {"populate_by_name": True}


class Meta(BaseModel):
    symbol: str
    asset_class: str
    timeframes: list[str]
    generated_at: str  # full ISO-8601 Z
    data_window: DataWindow
    engine_version: str


# ---------- deterministic blocks ----------
class Regime(BaseModel):
    trend: Trend
    structure: str
    note: str


class Bias(BaseModel):
    direction: Direction
    conviction: Conviction
    # keys MUST match meta.timeframes exactly (enforced in Step1Output)
    timeframe_alignment: dict[str, Direction]


class Invalidation(BaseModel):
    price: float
    rule: str


class Levels(BaseModel):
    # nearest-first relative to current price
    support: list[float]
    resistance: list[float]
    invalidation: Invalidation


class Signal(BaseModel):
    name: str
    value: Union[float, str]  # polymorphic: 28 | "bearish" | "none"
    vote: Vote
    weight: float


class ConfluenceScore(BaseModel):
    long: float
    short: float
    neutral: float


# ---------- interpretive blocks (LLM-owned; None in v1) ----------
class ElliottTF(BaseModel):
    degree: Optional[str] = None
    current_wave: Optional[str] = None
    structure: Optional[str] = None
    sub_wave: Optional[str] = None
    implied_direction: Optional[str] = None
    primary_count: Optional[str] = None
    alt_count: Optional[str] = None
    invalidation: Optional[float] = None
    note: Optional[str] = None
    confidence: Optional[ConfidenceCat] = None


class Elliott(BaseModel):
    tf_1d: Optional[ElliottTF] = None
    tf_4h: Optional[ElliottTF] = None
    tf_1h: Optional[ElliottTF] = None


class Summaries(BaseModel):
    daily: Optional[str] = None
    weekly: Optional[str] = None
    monthly: Optional[str] = None


class Plan(BaseModel):
    playbook: Optional[str] = None
    entry_zone: Optional[list[float]] = None
    stop: Optional[float] = None
    targets: Optional[list[float]] = None
    r_r: Optional[float] = None
    sizing_note: Optional[str] = None
    note: Optional[str] = None


# ---------- root ----------
class Step1Output(BaseModel):
    meta: Meta
    regime: Regime
    bias: Bias
    levels: Levels
    signals: list[Signal]
    confluence_score: ConfluenceScore
    confidence: float = Field(ge=0.0, le=1.0)  # top-level float 0..1
    caveats: list[str]

    # interpretive — null in v1, stable shape
    elliott: Optional[Elliott] = None
    summaries: Optional[Summaries] = None
    plan: Optional[Plan] = None

    @model_validator(mode="after")
    def _check_alignment_keys(self) -> "Step1Output":
        tfs = set(self.meta.timeframes)
        align = set(self.bias.timeframe_alignment)
        if align != tfs:
            raise ValueError(
                f"bias.timeframe_alignment keys {sorted(align)} "
                f"must match meta.timeframes {sorted(tfs)}"
            )
        return self

    def to_json(self, **kwargs) -> str:
        # by_alias so data_window emits "from" not "from_"
        return self.model_dump_json(by_alias=True, **kwargs)
