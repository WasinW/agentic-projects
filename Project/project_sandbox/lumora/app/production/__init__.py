"""Content Production pipeline (07 §2.5).

The single-step `GeneratorAdapter.generate()` is decomposed here into a pipeline of
swappable **sub-adapters**, orchestrated by a per-`media_format` **recipe**:

    ScriptGen(🤖) · StoryboardGen(🤖) · ImageGen(🎨) · VideoGen(🎨)
    CaptionGen(🤖) · Assembler(⚙️)
        └── ProductionRecipe[media_format] picks which sub-adapters run, in order.

Legend (07 §2.5 / §3):
    🤖 LLM        — script / storyboard / caption (Claude). ~$0.01/step (cached).
    🎨 gen-API    — image (FLUX/MJ/Ideogram) / video (Kling/Runway/Luma).
    ⚙️ deterministic — recipe orchestrator + ffmpeg assemble. $0 token.

MOCK by default ($0, no keys, no model downloads). Real impls are stubs behind env
keys that raise NotImplementedError — same pattern as `app/adapters/mock_generator.py`.
"""
from app.production.protocols import (
    Assembler,
    CaptionGen,
    CaptionResult,
    ImageGen,
    ProductionResult,
    ScriptGen,
    Script,
    Shot,
    StoryboardGen,
    StepTrace,
    VideoGen,
)
from app.production.runner import RecipeGenerator, run_recipe

__all__ = [
    "ScriptGen",
    "StoryboardGen",
    "ImageGen",
    "VideoGen",
    "CaptionGen",
    "Assembler",
    "Script",
    "Shot",
    "CaptionResult",
    "StepTrace",
    "ProductionResult",
    "RecipeGenerator",
    "run_recipe",
]
