"""Orchestrator-first pipeline (07 §0 #2, §2). A deterministic Python flow — the
Airflow-DAG analog. The ONLY 🤖 LLM/AI call is inside generation (and it is mocked).

One cycle:
  ⚙️ 1. scrape (SourceAdapter)            -> raw listings
  ⚙️ 2. embed (Embedder, 1024-dim)        -> product vectors + an account vector
  ⚙️ 3. trend z-score (services/trend)    -> trend signal per product
  ⚙️ 4. combo score (services/scorer)     -> weighted formula, rank
  ⚙️ 5. write top-N -> agent_decisions (status=suggested)   [waits for Sin]
  --- approval gate (state machine; Sin approves per combo) ---
  🤖🎨⚙️ 6. produce (GeneratorAdapter = Content Production recipe, 07 §2.5)
            -> multi-step per media_format (M3 reel: script→storyboard→img→clip
               →assemble→caption) -> asset + caption + production trace + cost
               [only on approve — the "gen only approved" cost lever]
  ⚙️ 7. publish (PublisherAdapter)        -> external post id

Steps 1-5 run in run_cycle(). 6 runs in generate_for_decision() (approve trigger).
7 runs in publish_decision().
"""
from __future__ import annotations

import app.adapters  # noqa: F401  -> registers default adapters
from app.core import adapters as seam
from app.core.models import Combo, Decision, ScoreBreakdown, Status
from app.core.repo import get_repo
from app.core.settings import get_settings
from app.adapters.embedder import get_embedder
from app.services import trend as trend_svc
from app.services.scorer import cosine

# Phase 1.A: pillar/theme/media start as config (07 §4 "เริ่มเป็น config file").
PILLARS = ["C1-oracle", "C2-ritual", "C3-product-review"]
THEMES = ["Future-tech", "Historical", "Cozy-home"]
# media tokens map to production recipes (07 §2.5) via recipes.resolve_media_id():
#   M1-image -> M1 single image · M2-carousel -> M2 carousel · M3-reel -> M3 video/reel
MEDIA = ["M1-image", "M2-carousel", "M3-reel"]


def run_cycle(brand_id: str | None = None, trigger: str = "trend") -> list[Decision]:
    """⚙️ deterministic cycle -> writes top-N suggested decisions. $0 token."""
    s = get_settings()
    repo = get_repo()
    brand_id = brand_id or repo.ensure_brand()
    embedder = get_embedder()
    scorer = seam.get("scorer", "zscore")
    source = seam.get("source", s.source if s.source in ("mock",) else "mock")

    # ⚙️ 1. scrape
    listings = source.scrape(brand_id)  # type: ignore[attr-defined]

    # ⚙️ 2. embed (deterministic mock vectors by default; bge-m3 behind flag)
    for l in listings:
        l["embedding"] = embedder.embed(f"{l['canonical_name']} {l.get('category','')}")
    # one synthetic "account vibe" vector to compute fit against
    account_vec = embedder.embed("สายมู mystical cozy oracle aesthetic")

    # ⚙️ 3. trend z-score (use reviews_count as the demand proxy)
    z = trend_svc.z_scores({l["external_id"]: float(l["reviews_count"]) for l in listings})

    # ⚙️ 4. build + score combos (product × pillar × theme × media)
    scored: list[tuple[float, Decision]] = []
    for l in listings:
        ext = l["external_id"]
        ctx = {
            "trend": trend_svc.trend_signal(z[ext]),
            "fit": cosine(l["embedding"], account_vec),
            "lift": min(1.0, (float(l.get("rating", 0)) / 5.0)),  # proxy until perf data
            "recency": 1.0,                                       # freshly scraped
            "season": 0.5,                                        # neutral (no calendar yet)
            "fatigue": 0.0,                                       # nothing posted yet
        }
        # pick a representative combo per product (1 axis-sample; agent could fan out)
        combo = Combo(
            content_pillar=PILLARS[abs(hash(ext)) % len(PILLARS)],
            theme=THEMES[(abs(hash(ext)) // 7) % len(THEMES)],
            media_format=MEDIA[abs(hash(ext)) % len(MEDIA)],
            jtbd="feel-aligned",
            funnel_stage="Hub",
            product_id=ext,
            product_name=l["canonical_name"],
            concept=f"{l['canonical_name']} as today's focus",
        )
        result = scorer.score(combo, ctx)  # type: ignore[attr-defined]
        d = Decision(
            decision_id=__import__("uuid").uuid4().hex,
            brand_id=brand_id, trigger_type=trigger,
            status=Status.SUGGESTED, recommendation=combo,
            score=result.total, score_breakdown=ScoreBreakdown(**result.breakdown),
        )
        scored.append((result.total, d))

    # ⚙️ 5. write top-N -> queue (status=suggested). Waits for Sin (no auto-publish).
    scored.sort(key=lambda t: t[0], reverse=True)
    top = [d for _, d in scored[: s.top_n]]
    for d in top:
        repo.save_decision(d)
    return top


def generate_for_decision(decision_id: str, approved_by: str = "Sin") -> Decision:
    """approve trigger: 🤖 generation (mocked) -> asset_ready. Enforces state machine.

    Moves suggested/reviewing/revised -> approved -> generating -> asset_ready.
    Idempotent on the approve step: if already approved, skip straight to generation.
    """
    repo = get_repo()
    d = repo.get_decision(decision_id)
    if d is None:
        raise KeyError(decision_id)
    if d.status != Status.APPROVED:
        repo.transition(decision_id, Status.APPROVED, approved_by=approved_by)
    repo.transition(decision_id, Status.GENERATING)
    gen = seam.get("generator", get_settings().generator)
    d = repo.get_decision(decision_id)
    # 🤖/🎨/⚙️ production pipeline (07 §2.5). For the default RecipeGenerator this runs
    # the per-media_format recipe (script→storyboard→img→clip→assemble→caption for M3)
    # and exposes the full trace + cost estimate on `.last_result`.
    asset, caption = gen.generate(d)  # type: ignore[attr-defined]
    trace: list[dict] = []
    cost = 0.0
    result = getattr(gen, "last_result", None)
    if result is not None:
        trace = [t.model_dump() for t in result.trace]
        cost = result.production_cost_estimate
    return repo.transition(
        decision_id, Status.ASSET_READY,
        asset_url=asset, caption=caption,
        production_trace=trace, production_cost_estimate=cost,
    )


def publish_decision(decision_id: str) -> Decision:
    """⚙️ publish a ready/scheduled decision."""
    repo = get_repo()
    repo.transition(decision_id, Status.SCHEDULED)
    pub = seam.get("publisher", get_settings().publisher)
    d = repo.get_decision(decision_id)
    pub.publish(d)  # type: ignore[attr-defined]
    return repo.transition(decision_id, Status.PUBLISHED)
