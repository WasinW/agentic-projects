"""Sub-adapter Protocols + structured I/O types for the production pipeline (07 §2.5).

Each sub-adapter is one seam: swap the model = swap the class (e.g. ImageGen FLUX ->
Ideogram), no recipe/core changes. Every sub-adapter exposes `est_cost()` so the
recipe can sum a `production_cost_estimate` BEFORE/after a run (the "gen only
approved" cost lever, 07 §6).

Boundary tags per sub-adapter:
    ScriptGen     🤖 LLM
    StoryboardGen 🤖 LLM
    ImageGen      🎨 gen-API
    VideoGen      🎨 gen-API
    CaptionGen    🤖 LLM
    Assembler     ⚙️ deterministic
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field

from app.core.models import Combo


# ── structured I/O (mock sub-adapters emit these; not free text) ──────────
class Script(BaseModel):
    """🤖 ScriptGen output — a reel/video script."""
    hook: str                       # 1-2s opener
    beats: list[str] = Field(default_factory=list)
    cta: str = ""


class Shot(BaseModel):
    """🤖 StoryboardGen output — one shot in the storyboard."""
    description: str
    camera: str = "static"
    mood: str = "neutral"
    seconds: float = 2.0
    image_prompt: str = ""          # filled by StoryboardGen (the per-shot 🤖 prompt)
    motion_prompt: str = ""         # filled by StoryboardGen (the per-shot 🤖 prompt)
    image_path: str | None = None   # filled by ImageGen 🎨
    clip_path: str | None = None    # filled by VideoGen 🎨


class CaptionResult(BaseModel):
    """🤖 CaptionGen output."""
    caption: str
    hashtags: list[str] = Field(default_factory=list)


class StepTrace(BaseModel):
    """One recorded step of a production run (for the trace Sin sees)."""
    step: str                       # e.g. "ImageGen", "VideoGen", "Assembler"
    boundary: str                   # "🤖 LLM" | "🎨 gen-API" | "⚙️ deterministic"
    adapter: str                    # adapter `name` that ran
    detail: str = ""                # human-readable one-liner
    est_cost: float = 0.0           # USD estimate for this step
    count: int = 1                  # fan-out (e.g. N images / N clips)


class ProductionResult(BaseModel):
    """Full output of a recipe run — the final asset + caption + trace + cost."""
    media_format: str
    asset_path: str                 # final assembled asset (manifest in mock)
    caption: str
    hashtags: list[str] = Field(default_factory=list)
    script: Script | None = None
    shots: list[Shot] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)
    clips: list[str] = Field(default_factory=list)
    trace: list[StepTrace] = Field(default_factory=list)
    production_cost_estimate: float = 0.0


# ── Sub-adapter Protocols ─────────────────────────────────────────────────
@runtime_checkable
class ScriptGen(Protocol):
    """🤖 LLM: combo -> {hook, beats, cta}."""
    name: str
    def script(self, combo: Combo) -> Script: ...
    def est_cost(self) -> float: ...


@runtime_checkable
class StoryboardGen(Protocol):
    """🤖 LLM: script -> ordered shot list (each with image + motion prompt)."""
    name: str
    def storyboard(self, combo: Combo, script: Script) -> list[Shot]: ...
    def est_cost(self) -> float: ...


@runtime_checkable
class ImageGen(Protocol):
    """🎨 gen-API: shot/prompt -> image path (FLUX/MJ/Ideogram swappable)."""
    name: str
    def image(self, prompt: str, combo: Combo, idx: int) -> str: ...
    def est_cost(self) -> float: ...


@runtime_checkable
class VideoGen(Protocol):
    """🎨 gen-API: image + motion prompt -> clip path (Kling/Runway/Luma swappable)."""
    name: str
    def clip(self, image_path: str, motion_prompt: str, combo: Combo, idx: int) -> str: ...
    def est_cost(self) -> float: ...


@runtime_checkable
class CaptionGen(Protocol):
    """🤖 LLM: combo -> {caption, hashtags}."""
    name: str
    def caption(self, combo: Combo) -> CaptionResult: ...
    def est_cost(self) -> float: ...


@runtime_checkable
class Assembler(Protocol):
    """⚙️ deterministic: clips + audio + subtitles -> final asset.

    mock = write a manifest describing the assembly; real = ffmpeg stitch+sub+encode.
    """
    name: str
    def assemble(self, combo: Combo, shots: list[Shot], audio: str | None = None) -> str: ...
    def est_cost(self) -> float: ...
