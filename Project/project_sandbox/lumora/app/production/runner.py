"""Recipe runner — ⚙️ deterministic orchestrator of the production pipeline (07 §2.5).

It reads `ProductionRecipe[media_format]`, executes the ordered steps, and CALLS the
🤖/🎨 sub-adapters at the marked steps. It records a per-step **production trace**
(which step ran, boundary, adapter, fan-out count, est cost) and sums a
`production_cost_estimate`.

`RecipeGenerator` adapts the whole pipeline back to the existing `GeneratorAdapter`
seam: `generate(decision) -> (asset_path, caption)`, so the registry and the
approve->generate flow keep working unchanged. The full `ProductionResult` (with the
trace) is also stashed on the runner for callers that want it (CLI / flow).
"""
from __future__ import annotations

from app.core.models import Combo, Decision
from app.production import mock_subadapters as mock
from app.production.protocols import (
    CaptionResult,
    ProductionResult,
    Script,
    Shot,
    StepTrace,
)
from app.production.recipes import Recipe, Step, get_recipe

# boundary labels per step (07 §2.5)
_BOUNDARY = {
    Step.SCRIPT: "🤖 LLM",
    Step.STORYBOARD: "🤖 LLM",
    Step.IMAGE: "🎨 gen-API",
    Step.VIDEO: "🎨 gen-API",
    Step.ASSEMBLE: "⚙️ deterministic",
    Step.CAPTION: "🤖 LLM",
}


def _default_subadapters() -> dict:
    """The MOCK sub-adapter set (default, $0). Swap individual entries to go real."""
    return {
        Step.SCRIPT: mock.MockScriptGen(),
        Step.STORYBOARD: mock.MockStoryboardGen(),
        Step.IMAGE: mock.MockImageGen(),
        Step.VIDEO: mock.MockVideoGen(),
        Step.ASSEMBLE: mock.MockAssembler(),
        Step.CAPTION: mock.MockCaptionGen(),
    }


def estimate_cost(media_format: str | None, subadapters: dict | None = None) -> float:
    """Sum est_cost() across the recipe's steps WITHOUT running them (07 §6 cost lever).

    Lets Sin see ~$ per asset BEFORE generating. Fan-out (N images / N shots) counted.
    """
    sa = subadapters or _default_subadapters()
    recipe = get_recipe(media_format)
    total = 0.0
    for step, count in _planned_steps(recipe):
        total += sa[step].est_cost() * count
    return round(total, 4)


def _planned_steps(recipe: Recipe) -> list[tuple[Step, int]]:
    """Expand the recipe into (step, fan_out_count) pairs for costing/tracing."""
    has_storyboard = Step.STORYBOARD in recipe.steps
    n = recipe.n_shots if has_storyboard else recipe.n_images
    out: list[tuple[Step, int]] = []
    for step in recipe.steps:
        if step in (Step.IMAGE, Step.VIDEO):
            out.append((step, n))
        else:
            out.append((step, 1))
    return out


def run_recipe(combo: Combo, subadapters: dict | None = None) -> ProductionResult:
    """⚙️ Execute the per-media recipe for `combo`. Returns the full ProductionResult.

    The orchestration is deterministic; it invokes 🤖/🎨 sub-adapters at marked steps.
    """
    sa = subadapters or _default_subadapters()
    recipe = get_recipe(combo.media_format)

    script: Script | None = None
    shots: list[Shot] = []
    caption: CaptionResult | None = None
    asset_path: str | None = None
    trace: list[StepTrace] = []

    # fan-out count: storyboard recipes use n_shots; flat image recipes use n_images.
    n = recipe.n_shots if Step.STORYBOARD in recipe.steps else recipe.n_images

    for step in recipe.steps:
        if step is Step.SCRIPT:
            script = sa[Step.SCRIPT].script(combo)
            trace.append(StepTrace(step=step.value, boundary=_BOUNDARY[step],
                                   adapter=sa[step].name, est_cost=sa[step].est_cost(),
                                   detail=f"hook: {script.hook[:48]}…"))

        elif step is Step.STORYBOARD:
            shots = sa[Step.STORYBOARD].storyboard(combo, script or Script(hook=""), n_shots=n)
            trace.append(StepTrace(step=step.value, boundary=_BOUNDARY[step],
                                   adapter=sa[step].name, est_cost=sa[step].est_cost(),
                                   detail=f"{len(shots)} shots"))

        elif step is Step.IMAGE:
            if not shots:
                # flat recipe (M1/M2): synthesize `n` slide-shots from the combo
                shots = [
                    Shot(description=f"{combo.product_name or combo.theme} — slide {i+1}",
                         image_prompt=(combo.concept or combo.theme or "สายมู aesthetic"))
                    for i in range(n)
                ]
            for i, sh in enumerate(shots):
                sh.image_path = sa[Step.IMAGE].image(
                    sh.image_prompt or (combo.concept or combo.theme or ""), combo, i)
            trace.append(StepTrace(step=step.value, boundary=_BOUNDARY[step],
                                   adapter=sa[step].name, count=len(shots),
                                   est_cost=round(sa[step].est_cost() * len(shots), 4),
                                   detail=f"{len(shots)} image(s)"))

        elif step is Step.VIDEO:
            for i, sh in enumerate(shots):
                sh.clip_path = sa[Step.VIDEO].clip(
                    sh.image_path or "", sh.motion_prompt, combo, i)
            trace.append(StepTrace(step=step.value, boundary=_BOUNDARY[step],
                                   adapter=sa[step].name, count=len(shots),
                                   est_cost=round(sa[step].est_cost() * len(shots), 4),
                                   detail=f"{len(shots)} clip(s)"))

        elif step is Step.ASSEMBLE:
            asset_path = sa[Step.ASSEMBLE].assemble(combo, shots)
            trace.append(StepTrace(step=step.value, boundary=_BOUNDARY[step],
                                   adapter=sa[step].name, est_cost=sa[step].est_cost(),
                                   detail="stitch+sub+encode (manifest stub)"))

        elif step is Step.CAPTION:
            caption = sa[Step.CAPTION].caption(combo)
            trace.append(StepTrace(step=step.value, boundary=_BOUNDARY[step],
                                   adapter=sa[step].name, est_cost=sa[step].est_cost(),
                                   detail=caption.caption[:48] + "…"))

    # no Assembler in the recipe (M1/M2) -> the (first) image IS the asset
    if asset_path is None:
        asset_path = next((s.image_path for s in shots if s.image_path), "")
    if caption is None:  # defensive — every recipe ends in CAPTION
        caption = sa[Step.CAPTION].caption(combo)

    total = round(sum(t.est_cost for t in trace), 4)
    return ProductionResult(
        media_format=combo.media_format,
        asset_path=asset_path or "",
        caption=caption.caption,
        hashtags=caption.hashtags,
        script=script,
        shots=shots,
        images=[s.image_path for s in shots if s.image_path],
        clips=[s.clip_path for s in shots if s.clip_path],
        trace=trace,
        production_cost_estimate=total,
    )


# ── GeneratorAdapter bridge ────────────────────────────────────────────────
class RecipeGenerator:
    """Registered as the `generator` seam. BE the generator: run the production
    recipe for the decision's media_format, return (asset_path, caption).

    The full ProductionResult (script/shots/clips/trace/cost) of the LAST run is kept
    on `.last_result` so the flow/CLI can record + print the production trace.
    """
    name = "recipe"

    def __init__(self, subadapters: dict | None = None):
        self._subadapters = subadapters
        self.last_result: ProductionResult | None = None

    def generate(self, decision: Decision) -> tuple[str, str]:
        result = run_recipe(decision.recommendation, self._subadapters)
        self.last_result = result
        return result.asset_path, result.caption

    def produce(self, combo: Combo) -> ProductionResult:
        """Full-fidelity run (for the CLI trace)."""
        self.last_result = run_recipe(combo, self._subadapters)
        return self.last_result
