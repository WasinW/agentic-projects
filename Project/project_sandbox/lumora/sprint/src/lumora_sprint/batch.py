"""Batch layer — load batch/*.yaml, look posts up, and run the deterministic validity gates.

Everything here is pure and offline: no LLM, no network, no I/O beyond reading the batch yaml.
The two gates it implements are the ones the batch spec calls out (01-batch-30day.md
§"Validity-gate re-check" + §"Cadence + fatigue rules"):

* ``validate_spec``  — gate #1 Legality (+ the oracle-theme and parked-pillar house rules)
* ``fatigue_check``  — gate #3 Diversity / anti-homogenization, windowed per ``engine.yaml``

Outline rows (``full_spec: false``, days 8-30) are deliberately half-empty — empty beats fake.
``expand_outline_hint`` only *prepares the ask*; the ``lumora-content-batch`` skill (Claude Code,
a human in the loop) does the expansion. This module never calls a model to fill a caption.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from .config import AccountConfig, FatigueCfg
from .models import HOOK_TYPES, Batch, PostSpec

__all__ = [
    "expand_outline_hint",
    "fatigue_check",
    "find_post",
    "load_all",
    "load_batch",
    "next_unposted",
    "validate_spec",
]

# (content_pillar, theme, media) of an already-planned post — what fatigue_check compares against.
Combo = tuple[str, str, str]


# ── loading ────────────────────────────────────────────────────────────────


def load_batch(path: str | Path) -> Batch:
    """Load one ``batch/*.yaml`` file into a validated :class:`~lumora_sprint.models.Batch`.

    Raises:
        FileNotFoundError: the path does not exist.
        pydantic.ValidationError: the yaml does not satisfy the Batch contract.
    """
    p = Path(path)
    with open(p, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return Batch.model_validate(raw)


def load_all(batch_dir: str | Path) -> list[Batch]:
    """Load every ``*.yaml`` in ``batch_dir``, sorted by ``batch_id`` (so W1 < W2 < W3 < W4).

    A missing directory yields an empty list — a fresh checkout with no batch is not an error.
    """
    d = Path(batch_dir)
    if not d.is_dir():
        return []
    files = sorted(p for p in d.iterdir() if p.suffix in {".yaml", ".yml"} and not p.name.startswith("_"))
    return sorted((load_batch(p) for p in files), key=lambda b: b.batch_id)


def find_post(batches: list[Batch], key: str | int) -> PostSpec:
    """Find one post by ``post_id`` ('L1-D01') or by day number (1, '1', 'D01').

    Raises:
        KeyError: no post matches ``key``.
    """
    posts = [p for b in batches for p in b.posts]

    day: int | None = None
    if isinstance(key, int):
        day = key
    else:
        k = key.strip()
        for p in posts:
            if p.post_id.casefold() == k.casefold():
                return p
        digits = k.lstrip("dD").lstrip("0") or "0"
        if digits.isdigit():
            day = int(digits)

    if day is not None:
        for p in posts:
            if p.day == day:
                return p

    raise KeyError(f"no post matching {key!r} in {len(posts)} loaded posts")


# ── gate #1: legality / house rules ────────────────────────────────────────


def validate_spec(spec: PostSpec, account: AccountConfig) -> list[str]:
    """Return the deterministic problems with ``spec`` — empty list means it may be produced.

    Checks, in reporting order:

    1. **legality** — pillar active, theme active, media allowed for the pillar and sustainable
       (``AccountConfig.is_legal``; validity gate #1).
    2. **parked pillar** — C4 travelogue stays parked until after the day-90 gate.
    3. **oracle theme** — C2 is the ritual masthead: it holds ``account.oracle_theme`` every day.
       The art engine is what rotates aesthetic, not the oracle.
    4. **hook_type** — must be a fixed tag from ``HOOK_TYPES``, never free text.
    5. **image spec** — a full-spec post with an AI visual cannot be generated without an ImageSpec.
    """
    problems: list[str] = []

    ok, reason = account.is_legal(spec.content_pillar, spec.theme, spec.media)
    if not ok:
        problems.append(f"legality: {reason}")

    if spec.content_pillar in account.parked_pillars:
        problems.append(
            f"parked pillar: {spec.content_pillar} is parked for this sprint "
            f"(parked_pillars={account.parked_pillars}) — unpark only after the gate passes"
        )

    if spec.content_pillar == "C2" and spec.theme != account.oracle_theme:
        problems.append(
            f"oracle theme: C2 must hold the fixed oracle look {account.oracle_theme!r} "
            f"(masthead of the daily ritual), got {spec.theme!r}"
        )

    if spec.hook_type not in HOOK_TYPES:
        problems.append(f"hook_type: {spec.hook_type!r} is not a fixed tag (allowed: {list(HOOK_TYPES)})")

    if spec.full_spec and spec.ai_visual and spec.image is None:
        problems.append("image: full_spec post declares ai_visual but carries no image spec — cannot generate")

    return problems


# ── gate #3: diversity / fatigue ───────────────────────────────────────────


def fatigue_check(spec: PostSpec, recent: list[Combo], fatigue: FatigueCfg) -> list[str]:
    """Return anti-homogenization warnings for ``spec`` given the posts just before it.

    Args:
        spec: the post about to be produced.
        recent: combos of the preceding posts, **most recent first** — ``recent[0]`` is the post
            immediately before ``spec``.
        fatigue: the ``fatigue:`` block of ``engine.yaml``.

    Rules (both skipped when ``spec.content_pillar`` is in ``fatigue.exempt_pillars`` — the oracle
    anchor is exempt on purpose: a daily ritual in a fixed look is the point, not fatigue):

    * ``no_same_c_m_consecutive`` — the same Content+Media two posts in a row.
    * ``same_combo_window_posts`` — the exact same (C, T, M) inside the trailing window.

    Warnings, never blocks — Sin decides. Returns [] when nothing trips.
    """
    if spec.content_pillar in fatigue.exempt_pillars:
        return []

    warnings: list[str] = []
    combo: Combo = (spec.content_pillar, spec.theme, spec.media)

    if fatigue.no_same_c_m_consecutive and recent:
        prev_c, _prev_t, prev_m = recent[0]
        if (prev_c, prev_m) == (spec.content_pillar, spec.media):
            warnings.append(
                f"fatigue: same C+M as the previous post ({spec.content_pillar}+{spec.media}) — "
                f"ห้ามซ้ำ C+M เดิมติดกัน; alternate the media"
            )

    window = fatigue.same_combo_window_posts
    if window > 0 and combo in recent[:window]:
        warnings.append(
            f"fatigue: exact combo {spec.content_pillar} x {spec.theme} x {spec.media} already used "
            f"within the last {window} posts"
        )

    return warnings


# ── queue ──────────────────────────────────────────────────────────────────


def next_unposted(batches: list[Batch], published_ids: set[str]) -> PostSpec | None:
    """The lowest-day post that has not been published yet, or None when the batch is done."""
    posts = sorted((p for b in batches for p in b.posts), key=lambda p: p.day)
    for p in posts:
        if p.post_id not in published_ids:
            return p
    return None


# ── outline expansion (the ask, not the answer) ────────────────────────────


_HINT_TEMPLATE = """\
/lumora-content-batch — expand ONE outline row into a full post spec

Account context: read sprint/config/account.yaml (handle, archetype Explorer x Magician,
persona "GenZ มู สาย aesthetic 22-32 BKK", voice, compliance, affiliate_by_pillar) — do not re-ask.

Fixed axes for this post (DO NOT CHANGE — they came from the 30-day batch plan):
  post_id      : {post_id}   (day {day}, week {week})
  combo        : {pillar} x {theme} x {media}
  funnel / JTBD: {funnel} / {jtbd}
  hook_type    : {hook_type}   (fixed tag — keep it, do not invent a new one)
  concept      : {concept}
  hook         : {hook}
{extra}
Produce, in the account voice (Thai-led, fellow explorer not guru):
  1. caption        — 3-6 บรรทัด, opens with the hook line verbatim, soft CTA at the end
  2. hashtags       — 6-8 tags (broad สายมู + combo-specific + #มูมีแสง + #AIart if AI visual)
  3. affiliate_angle— per account.yaml affiliate_by_pillar[{pillar}]; ไม่ต้องขายทุกโพสต์
  4. image          — via /lumora-art-prompt: prompt, negative, aspect_ratio 9:16, seed, steps,
                      guidance, count ({count_hint}), variation
  5. notes          — format note (production hint for {media}) + AI-label reminder

Hard guardrails: no prediction / no medical / no financial claim / no fear-mongering ·
comedy = self-deprecating only · sacred imagery = respectful homage · PDPA: no personal data ·
avoid banned_phrases_th in account.yaml.

Output: a YAML block for this post_id with full_spec: true, ready to paste over the outline row in
sprint/batch/{batch_file}. Keep every fixed axis above byte-identical.\
"""


def expand_outline_hint(spec: PostSpec) -> str:
    """Build the ready-to-paste ask that turns an outline row into a full post spec.

    The tool does **not** call an LLM to expand a batch row — the ``lumora-content-batch`` skill does,
    with Sin in the loop (ADR-0001: ship by hand; LLM stays surgical). This just prepares the prompt.
    """
    if spec.full_spec:
        return f"{spec.post_id} is already full_spec — nothing to expand."

    extra = ""
    if spec.homage_watch:
        extra = (
            "  homage_watch : true — sacred imagery: สง่างาม ไม่บิดเบือน, เฝ้า reaction 24 ชม.แรก\n"
        )
    if spec.notes:
        indented = "\n".join(f"    {line}" for line in spec.notes.splitlines())
        extra += f"  notes from plan:\n{indented}\n"

    count_hint = "5 for an M2 carousel, else 1"
    if spec.media == "M2":
        count_hint = "5 — carousel, seeds ไล่ต่อกันให้ชุด cohesive"
    elif spec.media in {"M1", "M11"}:
        count_hint = "1"

    return _HINT_TEMPLATE.format(
        post_id=spec.post_id,
        day=spec.day,
        week=spec.week,
        pillar=spec.content_pillar,
        theme=spec.theme,
        media=spec.media,
        funnel=spec.funnel_stage,
        jtbd=spec.jtbd or "(pick from the account persona jobs)",
        hook_type=spec.hook_type,
        concept=spec.concept,
        hook=spec.hook,
        extra=extra,
        count_hint=count_hint,
        batch_file=f"2026-07-w{spec.week}.yaml",
    )
