"""MOCK sub-adapters (default, $0, no keys, no model downloads) + real STUBS.

Every mock emits a fake-but-STRUCTURED output and, where it "produces" a file,
writes a small JSON/manifest stub under `assets/`. This lets Sin see the whole
multi-step pipeline run end-to-end without spending a cent.

`est_cost()` returns the 07 §2.5 figures:
    image ~$0.025 · video clip ~$0.07 · LLM step ~$0.01 · assemble $0.

Real stubs (ClaudeScript, ReplicateImage, KlingVideo, ...) live behind env keys and
raise NotImplementedError — same pattern as `app/adapters/mock_generator.py`.
"""
from __future__ import annotations

import json
import os

from app.core.models import Combo
from app.core.settings import get_settings
from app.production.protocols import CaptionResult, Script, Shot

# 07 §2.5 cost figures (USD)
COST_LLM = 0.01
COST_IMAGE = 0.025
COST_VIDEO = 0.07
COST_ASSEMBLE = 0.0


def _assets_dir() -> str:
    d = os.path.abspath(get_settings().assets_dir)
    os.makedirs(d, exist_ok=True)
    return d


def _slug(combo: Combo) -> str:
    base = combo.product_id or combo.product_name or combo.content_pillar or "asset"
    return "".join(c if c.isalnum() else "-" for c in str(base)).strip("-").lower()[:40]


def _write_stub(name: str, payload: dict) -> str:
    """Write a JSON stub describing a 'generated' artifact; return its path."""
    path = os.path.join(_assets_dir(), name)
    with open(path, "w") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


# ── 🤖 LLM sub-adapters ────────────────────────────────────────────────────
class MockScriptGen:
    """🤖 LLM (mocked): combo -> {hook, beats, cta}. Real = Claude Sonnet (cached)."""
    name = "mock-script"

    def script(self, combo: Combo) -> Script:
        subject = combo.product_name or combo.concept or combo.theme
        return Script(
            hook=f"หยุดก่อน… {subject} กำลังจะเปลี่ยนวันของคุณ ✨",
            beats=[
                f"เปิดด้วยมู้ด {combo.theme} ที่เข้ากับ {combo.content_pillar}",
                f"โชว์ {subject} ใกล้ๆ ให้เห็นรายละเอียด",
                f"เชื่อมกับ JTBD: {combo.jtbd or 'feel-aligned'}",
            ],
            cta="กดติดตามไว้ แล้วเซฟโพสต์นี้สำหรับวันที่ต้องการพลังบวก 🌙",
        )

    def est_cost(self) -> float:
        return COST_LLM


class MockStoryboardGen:
    """🤖 LLM (mocked): script -> shot list (camera/mood/seconds + per-shot prompts)."""
    name = "mock-storyboard"

    def storyboard(self, combo: Combo, script: Script, n_shots: int = 5) -> list[Shot]:
        subject = combo.product_name or combo.theme
        cameras = ["slow push-in", "static close-up", "orbit", "tilt-up", "pull-back"]
        moods = ["dreamy", "cozy", "ethereal", "warm", "mystical"]
        shots: list[Shot] = []
        # first shot mirrors the hook; remaining follow the beats
        lines = [script.hook] + script.beats
        for i in range(n_shots):
            line = lines[i % len(lines)]
            shots.append(
                Shot(
                    description=line,
                    camera=cameras[i % len(cameras)],
                    mood=moods[i % len(moods)],
                    seconds=2.0,
                    # per-shot 🤖 prompts (07 §2.5 steps 3 & 5)
                    image_prompt=(
                        f"{subject}, {combo.theme} aesthetic, {moods[i % len(moods)]} mood, "
                        f"{cameras[i % len(cameras)]} framing, สายมู spiritual vibe, photoreal"
                    ),
                    motion_prompt=f"{cameras[i % len(cameras)]}, subtle particle drift, 2s loop",
                )
            )
        return shots

    def est_cost(self) -> float:
        return COST_LLM


class MockCaptionGen:
    """🤖 LLM (mocked): combo -> {caption, hashtags}. Real = Claude Sonnet brand-voice."""
    name = "mock-caption"

    def caption(self, combo: Combo) -> CaptionResult:
        subject = combo.product_name or "this piece"
        return CaptionResult(
            caption=(
                f"✨ {subject} — {combo.concept or combo.theme}. "
                f"พลังที่ใช่สำหรับวันนี้ 🌙"
            ),
            hashtags=["#สายมู", f"#{combo.content_pillar}", f"#{combo.theme}"],
        )

    def est_cost(self) -> float:
        return COST_LLM


# ── 🎨 gen-API sub-adapters ────────────────────────────────────────────────
class MockImageGen:
    """🎨 gen-API (mocked): prompt -> image stub path. Real = FLUX/MJ/Ideogram."""
    name = "mock-image-flux"

    def image(self, prompt: str, combo: Combo, idx: int) -> str:
        return _write_stub(
            f"{_slug(combo)}-img{idx}.image.json",
            {"_stub": "image", "engine": self.name, "idx": idx, "prompt": prompt},
        )

    def est_cost(self) -> float:
        return COST_IMAGE


class MockVideoGen:
    """🎨 gen-API (mocked): image+motion -> clip stub path. Real = Kling/Runway/Luma."""
    name = "mock-video-kling"

    def clip(self, image_path: str, motion_prompt: str, combo: Combo, idx: int) -> str:
        return _write_stub(
            f"{_slug(combo)}-clip{idx}.clip.json",
            {"_stub": "clip", "engine": self.name, "idx": idx,
             "from_image": os.path.basename(image_path), "motion": motion_prompt},
        )

    def est_cost(self) -> float:
        return COST_VIDEO


# ── ⚙️ deterministic sub-adapter ───────────────────────────────────────────
class MockAssembler:
    """⚙️ deterministic (mocked): clips+audio+subs -> final asset manifest.

    Real impl = ffmpeg concat + subtitle burn + 9:16 encode -> mp4.
    """
    name = "mock-ffmpeg"

    def assemble(self, combo: Combo, shots: list[Shot], audio: str | None = None) -> str:
        manifest = {
            "_stub": "assembled-asset",
            "assembler": self.name,
            "format": "9:16 mp4 (manifest stub — real = ffmpeg encode)",
            "audio": audio or "none",
            "clips": [os.path.basename(s.clip_path) for s in shots if s.clip_path],
            "images": [os.path.basename(s.image_path) for s in shots if s.image_path],
            "subtitles": [s.description for s in shots],
            "duration_s": sum(s.seconds for s in shots),
        }
        return _write_stub(f"{_slug(combo)}.final.json", manifest)

    def est_cost(self) -> float:
        return COST_ASSEMBLE


# ── REAL STUBS (behind env keys; raise NotImplementedError) ────────────────
class ClaudeScript:
    """STUB — 🤖 real script via Claude Sonnet (cached brand voice). Needs ANTHROPIC_API_KEY."""
    name = "claude-script"

    def script(self, combo: Combo) -> Script:
        if not get_settings().anthropic_api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set; use GENERATOR=mock")
        raise NotImplementedError("ClaudeScript stub — wire Claude here (07 §2.5 step 1 🤖).")

    def est_cost(self) -> float:
        return COST_LLM


class ReplicateImage:
    """STUB — 🎨 real image via Replicate FLUX. Needs REPLICATE_API_TOKEN."""
    name = "replicate-image"

    def image(self, prompt: str, combo: Combo, idx: int) -> str:
        if not get_settings().replicate_api_token:
            raise RuntimeError("REPLICATE_API_TOKEN not set; use GENERATOR=mock")
        raise NotImplementedError("ReplicateImage stub — wire FLUX.1 here (07 §2.5 step 4 🎨).")

    def est_cost(self) -> float:
        return COST_IMAGE


class KlingVideo:
    """STUB — 🎨 real image->video via Kling/Runway. Needs a gen-API key."""
    name = "kling-video"

    def clip(self, image_path: str, motion_prompt: str, combo: Combo, idx: int) -> str:
        raise NotImplementedError("KlingVideo stub — wire Kling/Runway here (07 §2.5 step 6 🎨).")

    def est_cost(self) -> float:
        return COST_VIDEO
