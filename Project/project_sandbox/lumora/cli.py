#!/usr/bin/env python3
"""LUMORA CLI — drive the FULL agentic loop locally without a UI.

Runs against the in-memory repo by default (no docker needed). Set DATABASE_URL
to drive Postgres instead.

  python cli.py seed                 # ensure brand + show it
  python cli.py cycle                # run one deterministic pipeline cycle
  python cli.py queue                # list suggested combos (ranked)
  python cli.py approve <id>         # approve -> production recipe -> asset_ready
  python cli.py publish <id>         # asset_ready -> published (mock)
  python cli.py produce [media]      # run the FULL production trace for a media
                                     #   (default M3-reel): script -> shots ->
                                     #   per-shot image/clip -> assemble -> caption -> $
  python cli.py demo                 # seed -> cycle -> queue -> approve top -> publish
"""
from __future__ import annotations

import sys

import app.adapters  # noqa: F401  -> register adapters
from app.core.models import Combo, Status
from app.core.repo import get_repo
from app.flow import pipeline
from app.production.recipes import get_recipe
from app.production.runner import RecipeGenerator, estimate_cost


def _print_decision(d):
    c = d.recommendation
    print(f"  [{d.score:.3f}] {d.decision_id[:8]}  "
          f"{c.content_pillar} × {c.theme} × {c.media_format}  ->  {c.product_name}")


def cmd_seed():
    bid = get_repo().ensure_brand()
    print(f"brand_id = {bid}")


def cmd_cycle():
    decisions = pipeline.run_cycle()
    print(f"⚙️  cycle done — {len(decisions)} combos suggested:")
    for d in decisions:
        _print_decision(d)


def cmd_queue():
    repo = get_repo()
    items = repo.list_queue(repo.ensure_brand(), Status.SUGGESTED)
    if not items:
        print("queue empty — run `python cli.py cycle` first")
        return
    print(f"queue ({len(items)} suggested):")
    for d in items:
        _print_decision(d)


def _print_trace(trace: list[dict], cost: float):
    """Pretty-print a production trace (list of StepTrace dicts) + total cost."""
    print("    production trace (07 §2.5):")
    for t in trace:
        fan = f" ×{t['count']}" if t.get("count", 1) > 1 else ""
        print(f"      {t['boundary']:<18} {t['step']}{fan:<4} "
              f"[{t['adapter']}]  ~${t['est_cost']:.3f}")
        if t.get("detail"):
            print(f"          └─ {t['detail']}")
    print(f"    production_cost_estimate: ~${cost:.3f}")


def cmd_approve(decision_id: str):
    out = pipeline.generate_for_decision(_resolve(decision_id))
    print(f"🤖🎨⚙️  approved+produced -> status={out.status.value}")
    print(f"    media:   {out.recommendation.media_format}")
    print(f"    asset:   {out.asset_url}")
    print(f"    caption: {out.caption}")
    if out.production_trace:
        _print_trace(out.production_trace, out.production_cost_estimate)


def cmd_produce(media: str = "M3-reel"):
    """Run the FULL production recipe for a media_format with MOCK sub-adapters and
    print the entire trace end-to-end (script -> shots -> img/clip -> assemble -> $)."""
    recipe = get_recipe(media)
    combo = Combo(
        content_pillar="C1-oracle", theme="Future-tech", media_format=media,
        jtbd="feel-aligned", funnel_stage="Hub",
        product_id="demo-moonstone", product_name="Moonstone bracelet (มูนสโตน)",
        concept="Moonstone bracelet as today's focus",
    )
    print(f"=== Content Production pipeline — {media} "
          f"(recipe {recipe.media_id}: {recipe.label}) ===")
    if recipe.todo:
        print(f"  (simplified/stub — TODO: {recipe.todo})")
    print(f"  pre-run est cost: ~${estimate_cost(media):.3f}  "
          f"(steps: {' -> '.join(s.value for s in recipe.steps)})\n")

    result = RecipeGenerator().produce(combo)

    if result.script:
        print("🤖 SCRIPT")
        print(f"   hook: {result.script.hook}")
        for b in result.script.beats:
            print(f"   beat: {b}")
        print(f"   cta:  {result.script.cta}\n")
    if result.shots:
        print(f"🤖 STORYBOARD — {len(result.shots)} shots")
        for i, sh in enumerate(result.shots):
            print(f"   shot {i}: [{sh.camera} / {sh.mood} / {sh.seconds}s] {sh.description}")
            if sh.image_path:
                print(f"            🎨 image: {sh.image_path}")
            if sh.clip_path:
                print(f"            🎨 clip:  {sh.clip_path}")
        print()
    if not result.shots and result.images:
        print(f"🎨 IMAGES — {len(result.images)}")
        for p in result.images:
            print(f"   {p}")
        print()
    asset_label = "⚙️ ASSEMBLED ASSET" if result.clips else "🎨 FINAL ASSET (image)"
    print(f"{asset_label}\n   {result.asset_path}\n")
    print(f"🤖 CAPTION\n   {result.caption}\n   {' '.join(result.hashtags)}\n")
    _print_trace([t.model_dump() for t in result.trace], result.production_cost_estimate)


def cmd_publish(decision_id: str):
    out = pipeline.publish_decision(_resolve(decision_id))
    print(f"⚙️  published -> status={out.status.value}")


def _resolve(prefix: str) -> str:
    """Allow short id prefixes for convenience."""
    repo = get_repo()
    if repo.get_decision(prefix):
        return prefix
    for st in Status:
        for d in repo.list_queue(repo.ensure_brand(), st):
            if d.decision_id.startswith(prefix):
                return d.decision_id
    raise SystemExit(f"no decision matching '{prefix}'")


def cmd_demo():
    print("=== LUMORA mock loop (end-to-end, $0) ===\n")
    cmd_seed(); print()
    cmd_cycle(); print()
    repo = get_repo()
    queue = repo.list_queue(repo.ensure_brand(), Status.SUGGESTED)
    # prefer an M3 reel so the demo shows the full multi-step production trace.
    from app.production.recipes import resolve_media_id
    top = next((d for d in queue if resolve_media_id(d.recommendation.media_format) == "M3"),
               queue[0])
    print(f"approving combo {top.decision_id[:8]} "
          f"({top.recommendation.media_format}) ...")
    cmd_approve(top.decision_id); print()
    cmd_publish(top.decision_id); print()
    print("=== loop complete: suggested -> approved -> asset_ready -> published ===")


COMMANDS = {
    "seed": cmd_seed, "cycle": cmd_cycle, "queue": cmd_queue,
    "approve": cmd_approve, "publish": cmd_publish, "produce": cmd_produce,
    "demo": cmd_demo,
}


def main(argv: list[str]) -> int:
    if not argv or argv[0] not in COMMANDS:
        print(__doc__)
        return 1
    cmd, rest = argv[0], argv[1:]
    COMMANDS[cmd](*rest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
