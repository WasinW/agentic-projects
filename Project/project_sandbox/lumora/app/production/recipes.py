"""ProductionRecipe — `media_format -> ordered steps` (07 §2.5 recipe table).

The recipe is the ⚙️ deterministic orchestrator: it declares WHICH sub-adapters run,
in what order, for a given media. The runner (`runner.py`) executes it and CALLS the
🤖/🎨 sub-adapters at the marked steps.

07 §2.5 table:
    M1 single image : ImageGen(1) -> CaptionGen
    M2 carousel     : ImageGen(N) -> CaptionGen
    M3 video/reel   : ScriptGen -> StoryboardGen -> per-shot[ImageGen -> VideoGen]
                      -> Assembler -> CaptionGen
    M5/M6 vlog/talking-head : (simplified stub — TODO real b-roll recipe)
    M7 fiction              : (simplified stub — TODO real heavy recipe)

Steps are declared as `Step` enum tokens; the runner interprets them. `n_images` /
`n_shots` parameterize fan-out (carousel slides, reel shots).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Step(str, Enum):
    SCRIPT = "ScriptGen"            # 🤖
    STORYBOARD = "StoryboardGen"   # 🤖
    IMAGE = "ImageGen"             # 🎨  (one per shot/slide; runner fans out)
    VIDEO = "VideoGen"             # 🎨  (one per shot; runner fans out)
    ASSEMBLE = "Assembler"        # ⚙️
    CAPTION = "CaptionGen"        # 🤖


@dataclass(frozen=True)
class Recipe:
    media_id: str                  # canonical M1/M2/M3/...
    label: str
    steps: tuple[Step, ...]
    n_images: int = 1              # IMAGE fan-out (carousel slides) when no storyboard
    n_shots: int = 5              # storyboard shot count (reel)
    todo: str | None = None        # set => simplified/stubbed recipe


# ── the recipe table (07 §2.5) ─────────────────────────────────────────────
RECIPES: dict[str, Recipe] = {
    # M1 single image: ImageGen(1) -> CaptionGen
    "M1": Recipe("M1", "single image", (Step.IMAGE, Step.CAPTION), n_images=1),
    # M2 carousel: ImageGen(N) -> CaptionGen
    "M2": Recipe("M2", "carousel", (Step.IMAGE, Step.CAPTION), n_images=5),
    # M3 video/reel: full pipeline
    "M3": Recipe(
        "M3", "video/reel",
        (Step.SCRIPT, Step.STORYBOARD, Step.IMAGE, Step.VIDEO, Step.ASSEMBLE, Step.CAPTION),
        n_shots=5,
    ),
    # M5/M6 vlog/talking-head — simplified: script + 1 b-roll image + caption (TODO real).
    "M5": Recipe(
        "M5", "vlog/talking-head",
        (Step.SCRIPT, Step.IMAGE, Step.CAPTION), n_images=1,
        todo="b-roll prompts + Sin-shot footage + edit/encode (07 §2.5 M5/M6)",
    ),
    "M6": Recipe(
        "M6", "talking-head",
        (Step.SCRIPT, Step.IMAGE, Step.CAPTION), n_images=1,
        todo="b-roll prompts + Sin-shot footage + edit/encode (07 §2.5 M5/M6)",
    ),
    # M7 fiction — simplified: reuse the reel recipe shape (TODO heavy multi-scene).
    "M7": Recipe(
        "M7", "fiction",
        (Step.SCRIPT, Step.STORYBOARD, Step.IMAGE, Step.VIDEO, Step.ASSEMBLE, Step.CAPTION),
        n_shots=5,
        todo="multi-scene story + heavy video gen (07 §2.5 M7)",
    ),
}

_DEFAULT = "M1"  # safest/cheapest fallback for unknown media


def resolve_media_id(media_format: str | None) -> str:
    """Normalize any media_format string to a canonical recipe id (M1/M2/M3/...).

    Tolerant of the scaffold's tokens (`M1-carousel`, `M2-short-video`) AND the 07
    §2.5 labels (`M3 video/reel`). Falls back to keyword matching, then M1.
    """
    if not media_format:
        return _DEFAULT
    m = media_format.strip().lower()

    # explicit Mn prefix wins (e.g. "m3-video", "M2 carousel")
    for mid in RECIPES:
        if m.startswith(mid.lower()):
            # scaffold quirk: "M1-carousel" historically means a carousel -> route to M2;
            # "M2-short-video" historically means a reel -> route to M3.
            if m.startswith("m1") and "carousel" in m:
                return "M2"
            if m.startswith("m2") and ("video" in m or "reel" in m or "short" in m):
                return "M3"
            return mid

    # keyword fallback (no Mn prefix)
    if any(k in m for k in ("reel", "video", "vdo", "clip")):
        return "M3"
    if "carousel" in m or "slide" in m:
        return "M2"
    if "image" in m or "single" in m or "photo" in m:
        return "M1"
    if any(k in m for k in ("vlog", "talking")):
        return "M5"
    if any(k in m for k in ("fiction", "story", "เรื่อง")):
        return "M7"
    return _DEFAULT


def get_recipe(media_format: str | None) -> Recipe:
    return RECIPES[resolve_media_id(media_format)]
