"""Typed loaders for config/account.yaml (constraint set) and config/engine.yaml (tunables).

Both files are the single source of truth for the skills AND this tool (file-06 GAP-1 closed here).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, model_validator

from .models import Funnel

# ── account.yaml ───────────────────────────────────────────────────────────


class Gate(BaseModel):
    days: int = 90
    best_post_views: int = 50000
    followers: int = 1000


class Archetype(BaseModel):
    primary: str
    secondary: str | None = None
    shading: dict[str, list[str]] = Field(default_factory=dict)   # {"Jester": ["C9"]}


class Persona(BaseModel):
    name: str
    age: str = ""
    where: str = ""
    belief: str = ""
    jobs: list[str] = Field(default_factory=list)


class Voice(BaseModel):
    one_liner: str
    registers: list[str] = Field(default_factory=list)
    test: str = ""


class PillarCfg(BaseModel):
    name: str
    role: str = ""
    funnel: Funnel = "Hub"
    cadence: str = ""
    media: list[str] = Field(default_factory=list)


class ThemeCfg(BaseModel):
    parent: str
    note: str = ""


class Compliance(BaseModel):
    no_prediction: bool = True
    no_medical: bool = True
    no_financial: bool = True
    no_fear_mongering: bool = True
    comedy_self_deprecating_only: bool = True
    sacred_imagery: str = "respectful_homage"
    ai_label_every_ai_visual: bool = True
    pdpa_no_personal_data: bool = True
    manual_publish_only: bool = True
    banned_phrases_th: list[str] = Field(default_factory=list)


class AccountConfig(BaseModel):
    brand_id: str = "own"
    account_handle: str
    catalog: str = "saymu"
    sprint_start: str                                   # ISO date 'YYYY-MM-DD'
    gate: Gate = Field(default_factory=Gate)
    archetype: Archetype
    appearance: str = "faceless_voice_led"
    persona: Persona
    voice: Voice
    active_pillars: dict[str, PillarCfg]                # {"C2": PillarCfg, ...}
    parked_pillars: list[str] = Field(default_factory=list)
    active_themes: dict[str, ThemeCfg]                  # {"Cosmic": ThemeCfg, ...}
    oracle_theme: str = "Cosmic"
    sustainable_media: list[str] = Field(default_factory=list)
    funnel_target: dict[str, float] = Field(default_factory=dict)
    channels: int = 1
    aesthetic_weeks: dict[int, str] = Field(default_factory=dict)
    compliance: Compliance = Field(default_factory=Compliance)
    affiliate_by_pillar: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _sanity(self) -> AccountConfig:
        if not (2 <= len(self.active_pillars) <= 4):
            raise ValueError("active_pillars must have 2-4 entries (framework: pick 2-4 pillars per account)")
        if self.oracle_theme not in self.active_themes:
            raise ValueError("oracle_theme must be one of active_themes")
        if self.channels != 1:
            raise ValueError("sprint runs N=1 channel — do not split (1 <= N <= SxA; gates decide)")
        return self

    # convenience — the legality gate (validity gate #1)
    def is_legal(self, pillar: str, theme: str, media: str) -> tuple[bool, str]:
        if pillar not in self.active_pillars:
            return False, f"pillar {pillar} not active (active: {sorted(self.active_pillars)})"
        if theme not in self.active_themes:
            return False, f"theme {theme!r} not in active_themes"
        allowed = self.active_pillars[pillar].media
        if allowed and media not in allowed:
            return False, f"media {media} not allowed for {pillar} (allowed: {allowed})"
        if self.sustainable_media and media not in self.sustainable_media:
            return False, f"media {media} not in sustainable_media {self.sustainable_media}"
        return True, "ok"


# ── engine.yaml ────────────────────────────────────────────────────────────


class Paths(BaseModel):
    db: str = "./lumora_sprint.db"
    batch_dir: str = "./batch"
    out_dir: str = "./out"
    events_log: str = "./out/agent_events.jsonl"
    reviews_dir: str = "./out/reviews"


class GeneratorCfg(BaseModel):
    provider: str = "auto"                              # auto | replicate | stub
    model: str = "black-forest-labs/flux-dev"
    defaults: dict[str, Any] = Field(default_factory=dict)
    est_cost_usd_per_image: float = 0.025
    timeout_s: int = 180


class LlmCfg(BaseModel):
    model: str = "claude-opus-5"
    effort: str = "low"
    max_tokens: int = 2048
    enabled: bool = True


class ComplianceCfg(BaseModel):
    require_llm_qa_before_approve: bool = False
    block_on_banned_phrase: bool = True


class FatigueCfg(BaseModel):
    no_same_c_m_consecutive: bool = True
    same_combo_window_posts: int = 3
    exempt_pillars: list[str] = Field(default_factory=list)


class MetricsCfg(BaseModel):
    snapshot_hours: list[int] = Field(default_factory=lambda: [24, 168])


class ReviewCfg(BaseModel):
    days: list[int] = Field(default_factory=lambda: [7, 14, 21, 28])
    lookback_days: int = 28


class LogCfg(BaseModel):
    agent_id: str = "lumora-sprint"


class EngineConfig(BaseModel):
    paths: Paths = Field(default_factory=Paths)
    generator: GeneratorCfg = Field(default_factory=GeneratorCfg)
    llm: LlmCfg = Field(default_factory=LlmCfg)
    compliance: ComplianceCfg = Field(default_factory=ComplianceCfg)
    fatigue: FatigueCfg = Field(default_factory=FatigueCfg)
    metrics: MetricsCfg = Field(default_factory=MetricsCfg)
    review: ReviewCfg = Field(default_factory=ReviewCfg)
    log: LogCfg = Field(default_factory=LogCfg)

    root: Path = Field(default=Path("."), exclude=True)   # directory the yaml was loaded from; paths resolve relative to it

    def resolve(self, p: str) -> Path:
        q = Path(p)
        return q if q.is_absolute() else (self.root / q).resolve()


# ── loaders ────────────────────────────────────────────────────────────────

DEFAULT_ROOT = Path(__file__).resolve().parents[2]      # .../sprint/


def _read_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_account(path: str | Path | None = None) -> AccountConfig:
    p = Path(path) if path else DEFAULT_ROOT / "config" / "account.yaml"
    return AccountConfig.model_validate(_read_yaml(p))


def load_engine(path: str | Path | None = None) -> EngineConfig:
    p = Path(path) if path else DEFAULT_ROOT / "config" / "engine.yaml"
    cfg = EngineConfig.model_validate(_read_yaml(p))
    cfg.root = p.parent.parent                          # sprint/ (config/ is one level down)
    return cfg
