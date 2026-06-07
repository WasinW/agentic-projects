"""Adapter seams (07 §0.5 tech-extensibility, §4 the 3 hard seams).

Four extensible seams as Protocols + a tiny registry. Adding a platform / source /
generator later = write one class + `register(...)`. No core changes.

  - SourceAdapter     : where product listings come from (TikTok/Shopee/Lazada/...)
  - GeneratorAdapter  : how an asset+caption is produced (FLUX/Kling/Claude/...)
  - PublisherAdapter  : where a post is pushed (TikTok/Reels/IG/...)
  - Scorer            : how combos are ranked (z-score formula now; ML later)

Embedder is selected directly in flow (mock vs bge-m3) — it is an impl detail of
the embed step, not a platform seam, so it is not in this registry.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.core.models import Combo, Decision


# ── Protocols ─────────────────────────────────────────────────────────────
@runtime_checkable
class SourceAdapter(Protocol):
    platform: str
    def scrape(self, brand_id: str) -> list[dict]:
        """Return raw product listings (dicts) for a brand."""
        ...


@runtime_checkable
class GeneratorAdapter(Protocol):
    name: str
    def generate(self, decision: Decision) -> tuple[str, str]:
        """Return (asset_url/path, caption). 🤖 LLM call lives behind this seam."""
        ...


@runtime_checkable
class PublisherAdapter(Protocol):
    platform: str
    def publish(self, decision: Decision) -> str:
        """Push a ready post. Return an external post id/url."""
        ...


@runtime_checkable
class Scorer(Protocol):
    name: str
    def score(self, combo: Combo, ctx: dict) -> "ScoreResult":
        ...


# tiny result carrier to avoid a circular import with models
class ScoreResult:
    def __init__(self, total: float, breakdown: dict):
        self.total = total
        self.breakdown = breakdown


# ── Registry ──────────────────────────────────────────────────────────────
_REGISTRY: dict[str, dict[str, object]] = {
    "source": {}, "generator": {}, "publisher": {}, "scorer": {},
}


def register(kind: str, key: str, impl: object) -> None:
    if kind not in _REGISTRY:
        raise KeyError(f"unknown seam '{kind}'")
    _REGISTRY[kind][key] = impl


def get(kind: str, key: str) -> object:
    try:
        return _REGISTRY[kind][key]
    except KeyError as e:
        raise KeyError(f"no '{key}' registered for seam '{kind}' "
                       f"(have: {list(_REGISTRY[kind])})") from e
