"""Generator seam. 🤖 The ONLY LLM/AI surface in the loop lives here.

MockGenerator (default): writes a fake asset file to local fs + returns a fake
caption. No keys, no Replicate, no Claude. ClaudeCaption / ReplicateImage are stubs
behind GENERATOR=real (need ANTHROPIC_API_KEY / REPLICATE_API_TOKEN).
"""
from __future__ import annotations

import os

from app.core.models import Decision
from app.core.settings import get_settings


class MockGenerator:
    name = "mock"

    def generate(self, decision: Decision) -> tuple[str, str]:
        s = get_settings()
        assets = os.path.abspath(s.assets_dir)
        os.makedirs(assets, exist_ok=True)
        path = os.path.join(assets, f"{decision.decision_id}.txt")
        combo = decision.recommendation
        # 🤖 (mocked) — in real impl this is an image-model call (FLUX/Kling).
        with open(path, "w") as f:
            f.write(f"[MOCK ASSET] {combo.content_pillar} × {combo.theme} × {combo.media_format}\n")
            f.write(f"product: {combo.product_name}\n")
        # 🤖 (mocked) — real impl = Claude Sonnet caption with cached brand-voice prompt.
        caption = (
            f"✨ {combo.product_name or 'this piece'} — "
            f"{combo.concept or combo.theme}. #สายมู #{combo.content_pillar}"
        )
        return path, caption


class ReplicateImage:
    """STUB — real image gen via Replicate FLUX. Needs REPLICATE_API_TOKEN."""
    name = "replicate-image"

    def generate(self, decision: Decision) -> tuple[str, str]:
        s = get_settings()
        if not s.replicate_api_token:
            raise RuntimeError("REPLICATE_API_TOKEN not set; use GENERATOR=mock")
        raise NotImplementedError("ReplicateImage stub — wire FLUX.1 here (07 §3 🎨).")


class ClaudeCaption:
    """STUB — real caption via Claude (cached brand-voice system prompt)."""
    name = "claude-caption"

    def caption(self, decision: Decision) -> str:
        s = get_settings()
        if not s.anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set; use GENERATOR=mock")
        raise NotImplementedError("ClaudeCaption stub — wire Claude here (07 §3 🤖).")


class RealGenerator:
    """Composes the real stubs. Behind GENERATOR=real."""
    name = "real"

    def __init__(self):
        self.image = ReplicateImage()
        self.caption = ClaudeCaption()

    def generate(self, decision: Decision) -> tuple[str, str]:
        asset, _ = self.image.generate(decision)
        return asset, self.caption.caption(decision)


def get_generator():
    if get_settings().generator == "real":
        return RealGenerator()
    return MockGenerator()
