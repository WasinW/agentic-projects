"""Command-line entry point — the whole sprint loop, one subcommand per step.

    init -> plan -> generate -> packet -> approve -> [Sin uploads BY HAND] -> log -> metrics -> review

Design rules this file exists to enforce (ADR-0001 / 07 §2):

* **Orchestrator-first.** Every command is deterministic plumbing. The only model calls are the
  image generator (behind the ``generate`` seam, stub by default) and the compliance QA pass
  (``packet``, skippable with ``--no-llm``). Nothing in ``log``/``metrics``/``review``/``status``
  touches an LLM.
* **No publisher.** The loop stops at ``approve``: an approved folder on disk plus the sentence
  "now upload BY HAND". ``log`` records what Sin did afterwards; it never does it.
* **Log from post #1.** Every invocation appends one :class:`~lumora_sprint.models.AgentEvent` to
  ``out/agent_events.jsonl`` (agent, step, model, prompt_version, cost, duration, ok) — success or
  failure, cheap or expensive. That file cannot be backfilled later.

Exit codes: ``0`` ok · ``1`` error · ``2`` needs-human (outline row not expanded yet, packet blocked
by compliance, or a packet that has not been approved).
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from . import db as dbm
from .batch import (
    expand_outline_hint,
    fatigue_check,
    find_post,
    load_all,
    next_unposted,
    validate_spec,
)
from .compliance import run_compliance_with_usage
from .config import DEFAULT_ROOT, AccountConfig, EngineConfig, load_account, load_engine
from .events import append_event, read_events
from .generate import generate_for_spec
from .models import (
    AgentEvent,
    Batch,
    ComplianceReport,
    GeneratedImage,
    LogRow,
    MetricsUpdate,
    Packet,
    PacketStatus,
    PostSpec,
)
from .packet import (
    CAPTION_FILE,
    CHECKLIST_FILE,
    META_FILE,
    PacketRefused,
    approve_packet,
    build_packet,
    load_packet,
    mark_published,
    packet_dir,
    write_packet,
)
from .review import sprint_day, week_of_day, weekly_review, write_review
from .status import read_packets, render_status, status_summary

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_NEEDS_HUMAN = 2

#: Image extensions the packet folder may hold (what the adapters write).
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp")

#: How far along the human gate each status sits. `blocked` deliberately shares `draft`'s rung —
#: it *is* a draft that failed the gate, so draft <-> blocked may be rewritten in both directions,
#: while `approved` / `published` are never walked backwards by a routine re-run (`_write_state`).
_STATUS_RANK: dict[PacketStatus, int] = {
    PacketStatus.planned: 0,
    PacketStatus.generated: 1,
    PacketStatus.draft: 2,
    PacketStatus.blocked: 2,
    PacketStatus.approved: 3,
    PacketStatus.published: 4,
}


class CliError(Exception):
    """A user-facing failure. ``code`` picks the exit status (1 error, 2 needs-human)."""

    def __init__(self, message: str, code: int = EXIT_ERROR) -> None:
        super().__init__(message)
        self.code = code


# ── context ────────────────────────────────────────────────────────────────


@dataclass
class Ctx:
    """Loaded configs plus lazily-opened db / batch files, shared by every subcommand."""

    account: AccountConfig
    engine: EngineConfig
    _conn: sqlite3.Connection | None = None
    _batches: list[Batch] | None = None

    @property
    def db_path(self) -> Path:
        return self.engine.resolve(self.engine.paths.db)

    @property
    def out_dir(self) -> Path:
        return self.engine.resolve(self.engine.paths.out_dir)

    @property
    def events_path(self) -> Path:
        return self.engine.resolve(self.engine.paths.events_log)

    @property
    def batch_dir(self) -> Path:
        return self.engine.resolve(self.engine.paths.batch_dir)

    def conn(self) -> sqlite3.Connection:
        """Open (and create/upgrade) the sprint db on first use. `init_db` is idempotent."""
        if self._conn is None:
            self._conn = dbm.init_db(self.db_path)
        return self._conn

    def batches(self) -> list[Batch]:
        """Every ``batch/*.yaml``, sorted by batch_id. Empty batch dir is an error worth naming."""
        if self._batches is None:
            self._batches = load_all(self.batch_dir)
        return self._batches

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    # -- helpers used by several commands ----------------------------------

    def find(self, key: str | int) -> PostSpec:
        batches = self.batches()
        if not batches:
            raise CliError(f"ไม่พบไฟล์ batch ใน {self.batch_dir} — ใส่ batch/*.yaml ก่อน")
        try:
            return find_post(batches, key)
        except KeyError as exc:
            raise CliError(str(exc)) from exc

    def batch_id_of(self, post_id: str) -> str:
        """Which batch file a post came from — becomes ``post_log.prompt_version``."""
        for b in self.batches():
            if any(p.post_id == post_id for p in b.posts):
                return b.batch_id
        return ""

    def published_ids(self) -> set[str]:
        """Posts already live: logged rows plus packets marked published."""
        conn = self.conn()
        ids = {r["post_id"] for r in dbm.list_posts(conn)}
        packets, _src = read_packets(conn, self.engine)
        ids |= {pid for pid, st in packets.items() if st == PacketStatus.published.value}
        return ids


@dataclass
class Rec:
    """What the command wants recorded in its AgentEvent (filled in as the handler runs)."""

    post_id: str | None = None
    model: str | None = None
    prompt_version: str | None = None
    cost_usd: float = 0.0
    detail: str = ""
    ok: bool = True


Handler = Callable[[Ctx, argparse.Namespace, Rec], int]


# ── small output helpers ───────────────────────────────────────────────────


def _h(title: str) -> None:
    """Section header — keeps a multi-step `run` readable."""
    print(f"\n── {title} " + "─" * max(0, 60 - len(title)))


def _preview(text: str, lines: int = 4, width: int = 96) -> str:
    """First few lines of a caption, indented, with an explicit truncation marker."""
    body = (text or "").splitlines()
    shown = body[:lines]
    out = "\n".join("    " + (ln if len(ln) <= width else ln[: width - 1] + "…") for ln in shown)
    if len(body) > lines:
        out += f"\n    … (+{len(body) - lines} บรรทัด)"
    return out or "    (ว่าง)"


def _combo(spec: PostSpec) -> str:
    return f"{spec.content_pillar} × {spec.theme} × {spec.media}"


def _print_spec(spec: PostSpec) -> None:
    """The whole plan for one post, in the order Sin reads it."""
    kind = "full spec" if spec.full_spec else "OUTLINE (ยังไม่ขยาย)"
    print(f"post      : {spec.post_id}  (day {spec.day}, week {spec.week}) — {kind}")
    print(f"combo     : {_combo(spec)} · funnel {spec.funnel_stage} · hook_type {spec.hook_type}")
    print(f"jtbd      : {spec.jtbd or '—'}")
    print(f"concept   : {spec.concept or '—'}")
    print(f"hook      : {spec.hook or '—'}")
    print(f"affiliate : {spec.affiliate_angle or '—'}")
    print(f"ai_visual : {spec.ai_visual} · homage_watch: {spec.homage_watch}")
    print("caption   :")
    print(_preview(spec.caption))
    print(f"hashtags  : {' '.join(spec.hashtags) or '—'}")
    if spec.image is not None:
        img = spec.image
        print(
            f"image     : count {img.count} · seed {img.seed} · steps {img.steps} · "
            f"guidance {img.guidance} · {img.aspect_ratio}"
        )
        print("prompt    :")
        print(_preview(" ".join(img.prompt.split()), lines=2))
        if img.negative:
            print(f"negative  : {' '.join(img.negative.split())[:96]}")
    else:
        print("image     : — (ไม่มี ImageSpec)")


def _print_findings(report: ComplianceReport | None) -> tuple[int, int]:
    """Print every finding, blocks first. Returns (n_block, n_warn)."""
    findings = list(report.findings) if report else []
    blocks = [f for f in findings if f.severity == "block"]
    warns = [f for f in findings if f.severity == "warn"]
    print(f"compliance: {len(findings)} findings ({len(blocks)} block · {len(warns)} warn)")
    for f in blocks + warns:
        mark = "🚫" if f.severity == "block" else "⚠️ "
        print(f"  {mark} {f.rule} ({f.source}) — {f.detail}")
    if report is not None and report.voice_test_pass is not None:
        print(f"  voice test: {'ผ่าน' if report.voice_test_pass else 'ไม่ผ่าน'}")
    if report is not None and report.suggested_caption:
        print("  suggested caption:")
        print(_preview(report.suggested_caption, lines=6))
    return len(blocks), len(warns)


# ── shared step logic ──────────────────────────────────────────────────────


def _engine_for_run(engine: EngineConfig, *, no_llm: bool) -> EngineConfig:
    """A per-invocation copy of the engine config with LLM QA forced off for ``--no-llm``."""
    if not no_llm:
        return engine
    clone = engine.model_copy(deep=True)
    clone.llm.enabled = False
    clone.root = engine.root
    return clone


def _resolve_key(args: argparse.Namespace) -> str | int:
    """``--post-id`` wins over ``--day``; one of them is required."""
    post_id = getattr(args, "post_id", None)
    if post_id:
        return str(post_id)
    day = getattr(args, "day", None)
    if day is not None:
        return int(day)
    raise CliError("ต้องระบุ --day N หรือ --post-id L1-D01")


def _require_full_spec(spec: PostSpec) -> None:
    """Outline rows stop the loop with exit 2 — expansion is a human + skill job, not an LLM call."""
    if spec.full_spec:
        return
    print(f"\n{spec.post_id} เป็น outline row (full_spec: false) — ต้องขยายก่อน generate.")
    print("คัดลอกคำสั่งข้างล่างนี้ไปรันกับ Claude Code (skill: lumora-content-batch):\n")
    print(expand_outline_hint(spec))
    raise CliError(f"{spec.post_id}: outline ยังไม่ถูกขยาย", code=EXIT_NEEDS_HUMAN)


def _validate(ctx: Ctx, spec: PostSpec) -> None:
    problems = validate_spec(spec, ctx.account)
    if problems:
        print(f"validate  : ❌ {len(problems)} problem(s)")
        for p in problems:
            print(f"  - {p}")
        raise CliError(f"{spec.post_id}: spec ไม่ผ่าน validity gate — แก้ batch yaml ก่อน")
    print("validate  : ✅ legality / oracle-theme / hook_type / image ผ่าน")


def _recent_combos(ctx: Ctx, spec: PostSpec, window: int) -> list[tuple[str, str, str]]:
    """Combos of the ``window`` posts planned immediately before ``spec``, newest first.

    ``fatigue_check`` is positional — ``recent[0]`` must be the post right before ``spec`` — so the
    history has to come from the *plan*, not from post_log. post_log only holds posts already
    published and logged: on a fresh sprint it is empty and every check trivially passes, and
    planning day 5 while only days 1-2 are logged would compare day 5's combo against day 2's,
    which is a wrong verdict rather than a missing one. post_log is used only to top the list up
    with posts that precede this batch entirely (e.g. the previous 30-day plan).
    """
    posts = [p for b in ctx.batches() for p in b.posts]
    planned = sorted((p for p in posts if p.day < spec.day), key=lambda p: p.day, reverse=True)
    combos = [(p.content_pillar, p.theme, p.media) for p in planned[:window]]
    if len(combos) >= window:
        return combos

    in_batch = {p.post_id for p in posts}
    older = [
        (r["content_pillar"], r["theme"], r["media"])
        for r in reversed(dbm.list_posts(ctx.conn()))
        if r["post_id"] not in in_batch
    ]
    return combos + older[: window - len(combos)]


def _fatigue(ctx: Ctx, spec: PostSpec) -> list[str]:
    window = max(int(ctx.engine.fatigue.same_combo_window_posts), 1)
    recent = _recent_combos(ctx, spec, window)
    warnings = fatigue_check(spec, recent, ctx.engine.fatigue)
    if warnings:
        print(f"fatigue   : ⚠️  {len(warnings)} warning(s) (เตือนเฉยๆ — Sin ตัดสินใจ)")
        for w in warnings:
            print(f"  - {w}")
    else:
        print("fatigue   : ✅ ไม่ซ้ำ C+M ติดกัน / ไม่ซ้ำ combo ในหน้าต่าง")
    return warnings


def _image_files(pdir: Path) -> list[Path]:
    """Generated files already sitting in the packet folder, in filename order."""
    if not pdir.is_dir():
        return []
    return sorted(p for p in pdir.glob("image_*.*") if p.suffix.lower() in IMAGE_SUFFIXES)


def _recorded_packet(out_dir: Path, post_id: str) -> Packet | None:
    """The packet already on disk, or None when there is none (or meta.json is unreadable)."""
    try:
        return load_packet(out_dir, post_id)
    except (OSError, ValueError):
        return None


def _recorded_images(out_dir: Path, post_id: str) -> list[GeneratedImage]:
    """Images with provenance, reloaded from ``out/<post_id>/meta.json``. Missing/broken -> []."""
    pkt = _recorded_packet(out_dir, post_id)
    return list(pkt.images) if pkt is not None else []


def _rank(status: PacketStatus | str) -> int:
    """Progress rank of a status; anything unrecognised sorts below `planned`."""
    try:
        return _STATUS_RANK[PacketStatus(str(status))]
    except ValueError:
        return -1


def _tracked_status(ctx: Ctx, post_id: str) -> PacketStatus | None:
    """The furthest-along status on record — the db `packets` row or out/<id>/meta.json.

    Both stores are consulted and the higher rank wins: `_write_state` writes them together, but a
    hand-copied folder or a db restored from a backup can leave one of them behind, and the guard
    must not be defeated by whichever store happens to be stale.
    """
    candidates: list[str] = []
    row = dbm.get_packet_status(ctx.conn(), post_id)
    if row and row.get("status"):
        candidates.append(str(row["status"]))
    on_disk = _recorded_packet(ctx.out_dir, post_id)
    if on_disk is not None:
        candidates.append(on_disk.status.value)

    best: PacketStatus | None = None
    for name in candidates:
        try:
            status = PacketStatus(name)
        except ValueError:
            continue
        if best is None or _rank(status) > _rank(best):
            best = status
    return best


def _step_cost_so_far(ctx: Ctx, post_id: str, steps: set[str]) -> float:
    """Sum the spend already recorded for this post's ``steps`` in the append-only event log."""
    return round(
        sum(
            e.cost_usd
            for e in read_events(ctx.events_path)
            if e.post_id == post_id and e.step in steps
        ),
        6,
    )


def _qa_cost_so_far(ctx: Ctx, post_id: str) -> float:
    """Total compliance-QA spend for this post — every `packet`/`qa` run, not only the last."""
    return _step_cost_so_far(ctx, post_id, {"packet", "qa"})


def _gen_cost_so_far(ctx: Ctx, post_id: str, images: list[GeneratedImage]) -> float:
    """Total generator spend for this post, derived the same way as the QA half.

    ``post_log.cost_usd`` has to mean one thing: total spend. Reading only the images currently on
    the packet would make it "last run" for the generator (a `generate --force` discards the earlier
    Replicate charge) while QA stays "all runs" — two semantics in one column, which corrupts the
    accountability dataset the column exists to seed. The packet's own image rows are the fallback
    for a post generated before the event log had anything for it.
    """
    from_events = _step_cost_so_far(ctx, post_id, {"generate"})
    if from_events:
        return from_events
    return round(sum(i.est_cost_usd for i in images), 6)


def _write_state(
    ctx: Ctx,
    spec: PostSpec,
    status: PacketStatus,
    images: list[GeneratedImage],
    report: ComplianceReport,
    *,
    protect_from: PacketStatus | None = PacketStatus.published,
) -> Path:
    """Build + write ``out/<post_id>/`` and mirror the status into the db. Returns the folder.

    Two guards live here so every writer gets them:

    * **Never walk the state machine backwards.** ``protect_from`` is the lowest tracked status this
      write may not downgrade. The default protects a *published* post from every re-run — post_log
      still holds its url and metrics, so a downgrade desyncs the two stores and makes `status`
      demand an approve for something already on TikTok. ``packet`` passes ``draft`` so an approval
      survives a re-check too; ``None`` turns the guard off (``--reopen``). ``generate --force``
      keeps the default: new pixels legitimately invalidate an *approval*, but cannot un-publish.
    * **Carry Sin's own edits forward.** ``build_packet`` builds from the spec alone, so an accepted
      ``caption_final`` (and ``approved_at``, when the status written is still approved/published)
      would be destroyed on the next run unless reloaded from the packet on disk.
    """
    prior = _recorded_packet(ctx.out_dir, spec.post_id)
    tracked = _tracked_status(ctx, spec.post_id)

    pkt = build_packet(spec, ctx.account, ctx.engine, images, report)
    if pkt.status is not PacketStatus.blocked:
        pkt.status = status
        if (
            protect_from is not None
            and tracked is not None
            and _rank(tracked) >= _rank(protect_from)
            and _rank(tracked) > _rank(pkt.status)
        ):
            print(
                f"note      : {tracked.value} อยู่แล้ว — ไม่ลดกลับเป็น {pkt.status.value} "
                "(ใช้ --reopen ถ้าตั้งใจจะย้อน)"
            )
            pkt.status = tracked

    if prior is not None:
        pkt.caption_final = prior.caption_final
        pkt.created_at = prior.created_at
        if pkt.status in (PacketStatus.approved, PacketStatus.published):
            pkt.approved_at = prior.approved_at

    pdir = write_packet(pkt, ctx.out_dir)
    dbm.upsert_packet_status(
        ctx.conn(), spec.post_id, ctx.account.brand_id, pkt.status, str(pdir / META_FILE)
    )
    print(f"status    : {pkt.status.value}")
    print(f"packet    : {pdir}")
    return pdir


# ── commands ───────────────────────────────────────────────────────────────


def cmd_init(ctx: Ctx, args: argparse.Namespace, rec: Rec) -> int:
    """Create/upgrade the db, re-validate both configs, and print the constraint set."""
    conn = ctx.conn()
    hooks = conn.execute("SELECT COUNT(*) FROM hook_types").fetchone()[0]
    acc, eng = ctx.account, ctx.engine
    today = date.today()  # noqa: DTZ011 - local calendar day is the sprint's unit
    day = sprint_day(acc, today)

    _h("config")
    print(f"account   : {acc.account_handle} · brand_id {acc.brand_id} · catalog {acc.catalog}")
    print(f"archetype : {acc.archetype.primary}" + (f" × {acc.archetype.secondary}" if acc.archetype.secondary else ""))
    print(f"voice     : {acc.voice.one_liner}")
    print("pillars   : " + " · ".join(f"{k} {v.name} ({v.funnel})" for k, v in acc.active_pillars.items()))
    print(f"parked    : {acc.parked_pillars or '—'} · oracle theme: {acc.oracle_theme}")
    print(f"themes    : {', '.join(acc.active_themes)}")
    print(f"media     : {', '.join(acc.sustainable_media) or '—'}")

    _h("gate (day 90)")
    print(f"sprint    : start {acc.sprint_start} · today {today.isoformat()} · day {day}/{acc.gate.days}")
    print(f"target    : 1 post ≥ {acc.gate.best_post_views:,} views  หรือ  {acc.gate.followers:,} followers")

    _h("engine")
    print(f"db        : {ctx.db_path}  (hook_types seeded: {hooks})")
    print(f"batch     : {ctx.batch_dir}")
    print(f"out       : {ctx.out_dir}")
    print(f"events    : {ctx.events_path}")
    print(f"generator : {eng.generator.provider} · {eng.generator.model}")
    print(f"llm       : {eng.llm.model} (enabled: {eng.llm.enabled}) — compliance QA เท่านั้น")

    batches = ctx.batches()
    posts = [p for b in batches for p in b.posts]
    full = sum(1 for p in posts if p.full_spec)
    print(f"batches   : {len(batches)} file · {len(posts)} posts ({full} full spec · {len(posts) - full} outline)")
    if not batches:
        print("⚠️  ไม่พบ batch yaml — plan/generate จะทำงานไม่ได้")
    rec.detail = f"day {day}, {len(posts)} posts"
    return EXIT_OK


def cmd_plan(ctx: Ctx, args: argparse.Namespace, rec: Rec) -> int:
    """Validate one post against the gates and record it as `planned`. No generation, no cost."""
    spec = ctx.find(_resolve_key(args))
    rec.post_id = spec.post_id
    rec.prompt_version = ctx.batch_id_of(spec.post_id)

    _h(f"plan {spec.post_id}")
    _print_spec(spec)
    print()
    _validate(ctx, spec)
    warnings = _fatigue(ctx, spec)
    rec.detail = f"{len(warnings)} fatigue warning(s)"

    current = dbm.get_packet_status(ctx.conn(), spec.post_id)
    if current and current["status"] != PacketStatus.planned.value:
        # never walk a packet backwards: an approved folder must not be reset by a re-plan
        print(f"packet    : {current['status']} อยู่แล้ว — ไม่ลดสถานะกลับเป็น planned")
    else:
        dbm.upsert_packet_status(
            ctx.conn(), spec.post_id, ctx.account.brand_id, PacketStatus.planned,
            str(packet_dir(ctx.out_dir, spec.post_id) / META_FILE),
        )
        print(f"packet    : {PacketStatus.planned.value}")

    _require_full_spec(spec)
    return EXIT_OK


def cmd_generate(ctx: Ctx, args: argparse.Namespace, rec: Rec) -> int:
    """Run the image seam for one post into ``out/<post_id>/`` (stub when there is no API token)."""
    spec = ctx.find(_resolve_key(args))
    rec.post_id = spec.post_id
    rec.prompt_version = ctx.batch_id_of(spec.post_id)
    _require_full_spec(spec)

    _h(f"generate {spec.post_id}")
    pdir = packet_dir(ctx.out_dir, spec.post_id)
    existing = _image_files(pdir)
    if existing and not args.force:
        # nothing changed on disk, so the packet state must not change either: re-running generate
        # over an approved packet is a no-op, while --force below deliberately resets it.
        images = _recorded_images(ctx.out_dir, spec.post_id)
        print(f"skip      : มีรูปอยู่แล้ว {len(existing)} ไฟล์ — ใช้ --force ถ้าจะ generate ใหม่")
        for p in existing:
            print(f"  - {p}")
        if not images:
            print("⚠️  ไม่มี provenance ใน meta.json (ไฟล์รูปมาจากไหนไม่ทราบ) — --force เพื่อบันทึกใหม่")
        tracked = dbm.get_packet_status(ctx.conn(), spec.post_id)
        print(f"status    : {tracked['status'] if tracked else PacketStatus.generated.value} (ไม่เปลี่ยน)")
        print(f"packet    : {pdir}")
        rec.model = "+".join(sorted({i.model for i in images})) or None
        rec.detail = f"skipped, {len(existing)} existing file(s)"
        return EXIT_OK

    try:
        images = generate_for_spec(spec, ctx.engine, pdir)
    except (RuntimeError, ValueError) as exc:
        raise CliError(f"{spec.post_id}: generate ล้มเหลว — {exc}") from exc
    for img in images:
        print(
            f"  + {img.path}  [{img.provider}/{img.model}]"
            + (f" seed {img.seed}" if img.seed is not None else "")
            + f" · {img.duration_s:.2f}s · ${img.est_cost_usd:.4f}"
        )
    rec.detail = f"{len(images)} image(s)"
    rec.cost_usd = round(sum(i.est_cost_usd for i in images), 6)
    rec.model = "+".join(sorted({i.model for i in images})) or None
    print(f"cost      : ${rec.cost_usd:.4f} · model {rec.model or '—'}")

    # deterministic-only report here: the real gate (with optional LLM QA) is the `packet` command.
    # New pixels invalidate any prior *approval*, so the packet drops back to `generated` on purpose
    # — but they cannot un-happen a post Sin already uploaded, so `_write_state`'s default guard
    # keeps a `published` packet published (re-arting a live post is a legit wallpaper workflow).
    report, _usage = run_compliance_with_usage(spec, ctx.account, _engine_for_run(ctx.engine, no_llm=True))
    _write_state(ctx, spec, PacketStatus.generated, images, report)
    return EXIT_OK


def cmd_packet(ctx: Ctx, args: argparse.Namespace, rec: Rec) -> int:
    """Run the compliance gate and assemble the publish packet. Exit 2 when blocked."""
    spec = ctx.find(_resolve_key(args))
    rec.post_id = spec.post_id
    rec.prompt_version = ctx.batch_id_of(spec.post_id)
    _require_full_spec(spec)

    _h(f"packet {spec.post_id}")
    engine = _engine_for_run(ctx.engine, no_llm=args.no_llm)
    if args.no_llm:
        print("llm       : ปิดสำหรับรอบนี้ (--no-llm) — deterministic checks เท่านั้น")

    report, usage = run_compliance_with_usage(spec, ctx.account, engine)
    rec.cost_usd = usage.cost_usd
    rec.model = usage.model or None
    if usage.called:
        print(f"llm qa    : {usage.model} · in {usage.input_tokens} / out {usage.output_tokens} tok · ${usage.cost_usd:.4f}")

    n_block, n_warn = _print_findings(report)
    rec.detail = f"{n_block} block, {n_warn} warn"

    images = _recorded_images(ctx.out_dir, spec.post_id)
    if not images:
        print("⚠️  ยังไม่มีรูปใน packet — รัน `generate` ก่อนถ้าโพสต์นี้ต้องมีภาพ")
    reopen = bool(getattr(args, "reopen", False))
    if reopen:
        print("reopen    : ยอมให้ลดสถานะกลับเป็น draft ได้ (--reopen)")
    _write_state(
        ctx, spec, PacketStatus.draft, images, report,
        protect_from=None if reopen else PacketStatus.draft,
    )

    if n_block:
        print("\n→ packet ถูก block: แก้ caption/hook ใน batch yaml แล้วรัน `packet` ใหม่")
        rec.ok = False
        return EXIT_NEEDS_HUMAN
    print("\n→ ต่อไป: `lumora approve " + spec.post_id + "`")
    return EXIT_OK


def cmd_approve(ctx: Ctx, args: argparse.Namespace, rec: Rec) -> int:
    """The human gate. Records Sin's approval — and says the loop stops here."""
    post_id = args.post_id
    rec.post_id = post_id
    rec.prompt_version = ctx.batch_id_of(post_id)

    _h(f"approve {post_id}")
    try:
        pkt = load_packet(ctx.out_dir, post_id)
    except (OSError, ValueError) as exc:
        raise CliError(f"{post_id}: อ่าน packet ไม่ได้ — รัน `packet` ก่อน ({exc})") from exc

    if pkt.status is PacketStatus.published:
        # same invariant as _write_state: an approve must never walk a live post backwards
        print(f"status    : {pkt.status.value} อยู่แล้ว — approve ซ้ำไม่ทำอะไร")
        rec.detail = "already published"
        return EXIT_OK

    try:
        pkt = approve_packet(pkt, ctx.out_dir, ctx.engine)
    except PacketRefused as exc:
        rec.ok = False
        raise CliError(str(exc), code=EXIT_NEEDS_HUMAN) from exc

    pdir = packet_dir(ctx.out_dir, post_id)
    dbm.upsert_packet_status(
        ctx.conn(), post_id, ctx.account.brand_id, PacketStatus.approved, str(pdir / META_FILE)
    )
    print(f"status    : {pkt.status.value} · approved_at {pkt.approved_at}")
    print(f"checklist : {pdir / CHECKLIST_FILE}")
    print(f"caption   : {pdir / 'caption.txt'}")
    print("\n→ now upload BY HAND (manual publish only — เครื่องมือนี้ไม่โพสต์ให้)")
    print(f"→ โพสต์แล้วรัน: `lumora log {post_id} --url <URL>`")
    rec.detail = "approved"
    return EXIT_OK


def cmd_caption(ctx: Ctx, args: argparse.Namespace, rec: Rec) -> int:
    """Record the caption Sin actually wants to post (``packet.caption_final``). No LLM here.

    checklist.md asks Sin to consider the caption the QA suggested; this is the verb that accepts
    one. Hand-editing meta.json does not survive the next `packet` run — this does, because
    `_write_state` carries ``caption_final`` forward.
    """
    post_id = args.post_id
    rec.post_id = post_id
    rec.prompt_version = ctx.batch_id_of(post_id)

    _h(f"caption {post_id}")
    try:
        pkt = load_packet(ctx.out_dir, post_id)
    except (OSError, ValueError) as exc:
        raise CliError(f"{post_id}: อ่าน packet ไม่ได้ — รัน `packet` ก่อน ({exc})") from exc

    if pkt.status is PacketStatus.published:
        raise CliError(
            f"{post_id}: โพสต์ขึ้นแล้ว — แก้ caption ในแอป ไม่ใช่ใน packet",
            code=EXIT_NEEDS_HUMAN,
        )

    if args.clear:
        pkt.caption_final, action = "", "cleared (กลับไปใช้ caption จาก batch)"
    elif args.text is not None:
        pkt.caption_final, action = args.text, "set จาก --text"
    elif args.accept_suggested:
        suggested = pkt.compliance.suggested_caption if pkt.compliance else None
        if not suggested:
            raise CliError(
                f"{post_id}: QA ไม่ได้เสนอ caption ไว้ (รัน `packet` โดยเปิด LLM ก่อน) — หรือใช้ --text",
                code=EXIT_NEEDS_HUMAN,
            )
        pkt.caption_final, action = suggested, "accepted QA suggestion"
    else:
        raise CliError("ต้องเลือกอย่างใดอย่างหนึ่ง: --accept-suggested / --text '...' / --clear")

    if pkt.status is PacketStatus.approved:
        # new text is new content: the human gate was given the old caption, so it has to run again
        pkt.status, pkt.approved_at = PacketStatus.draft, None
        print("status    : approved → draft (caption เปลี่ยน = ต้อง approve ใหม่)")

    pdir = write_packet(pkt, ctx.out_dir)
    dbm.upsert_packet_status(
        ctx.conn(), post_id, ctx.account.brand_id, pkt.status, str(pdir / META_FILE)
    )
    print(f"caption   : {action}")
    print(_preview(pkt.caption_final or pkt.spec.caption, lines=6))
    print(f"packet    : {pdir / CAPTION_FILE}")
    rec.detail = action
    return EXIT_OK


def cmd_log(ctx: Ctx, args: argparse.Namespace, rec: Rec) -> int:
    """Record a post Sin published by hand: one post_log row + packet -> published."""
    post_id = args.post_id
    rec.post_id = post_id

    _h(f"log {post_id}")
    try:
        pkt = load_packet(ctx.out_dir, post_id)
    except (OSError, ValueError) as exc:
        raise CliError(f"{post_id}: อ่าน packet ไม่ได้ — รัน `packet` + `approve` ก่อน ({exc})") from exc

    if pkt.status not in (PacketStatus.approved, PacketStatus.published):
        raise CliError(
            f"{post_id}: packet สถานะ {pkt.status.value} — ต้อง `approve` ก่อนถึงจะ log ได้",
            code=EXIT_NEEDS_HUMAN,
        )

    try:
        posted_at = date.fromisoformat(args.posted_at) if args.posted_at else date.today()  # noqa: DTZ011
    except ValueError as exc:
        raise CliError(f"--posted-at ต้องเป็น YYYY-MM-DD, ได้ {args.posted_at!r}") from exc

    if posted_at < date.fromisoformat(ctx.account.sprint_start):
        # accepted, not refused — but say so, because every reader filters on sprint_start and would
        # otherwise drop the row. status/review clamp their window back to the earliest logged post.
        print(
            f"⚠️  posted_at {posted_at.isoformat()} มาก่อน sprint_start {ctx.account.sprint_start} "
            "— บันทึกให้ และ status/review จะขยายหน้าต่างย้อนไปถึงโพสต์แรกสุด"
        )

    spec = pkt.spec
    batch_id = ctx.batch_id_of(post_id)
    gen_cost = _gen_cost_so_far(ctx, post_id, pkt.images)
    qa_cost = _qa_cost_so_far(ctx, post_id)
    gen_model = "+".join(sorted({i.model for i in pkt.images}))

    row = LogRow(
        post_id=post_id,
        brand_id=pkt.brand_id,
        account_handle=pkt.account_handle,
        posted_at=posted_at,
        content_pillar=spec.content_pillar,
        theme=spec.theme,
        media=spec.media,
        jtbd=spec.jtbd,
        funnel_stage=spec.funnel_stage,
        hook_type=spec.hook_type,
        ai_labeled=not args.no_ai_label,
        url=args.url,
        notes=args.notes or "",
        agent=ctx.engine.log.agent_id,
        prompt_version=batch_id,
        gen_model=gen_model,
        cost_usd=round(gen_cost + qa_cost, 6),
    )
    dbm.insert_log(ctx.conn(), row)
    mark_published(pkt, ctx.out_dir)
    dbm.upsert_packet_status(
        ctx.conn(), post_id, ctx.account.brand_id, PacketStatus.published,
        str(packet_dir(ctx.out_dir, post_id) / META_FILE),
    )

    print(f"logged    : {post_id} · {row.posted_at.isoformat()} · {_combo(spec)} · {row.funnel_stage}")
    print(f"hook_type : {row.hook_type} · ai_labeled: {row.ai_labeled}")
    print(f"url       : {row.url or '—'}")
    print(f"cost      : ${row.cost_usd:.4f} (gen ${gen_cost:.4f} + qa ${qa_cost:.4f}) · model {gen_model or '—'}")
    print(f"prompt_ver: {batch_id or '—'} · agent {row.agent}")
    print("status    : published")
    print("\n→ metrics ว่างไว้ก่อน (ว่างดีกว่ามั่ว) — กลับมา `lumora metrics` ตอน 24 ชม. และ 7 วัน")
    rec.prompt_version = batch_id
    rec.model = gen_model or None
    rec.cost_usd = row.cost_usd
    rec.detail = "logged"
    return EXIT_OK


_METRIC_FIELDS = (
    "views_24h", "views_7d", "likes", "comments", "shares", "saves", "follows_delta", "gmv", "notes",
)


def cmd_metrics(ctx: Ctx, args: argparse.Namespace, rec: Rec) -> int:
    """Write only what was actually measured — every unsupplied column stays NULL."""
    post_id = args.post_id
    rec.post_id = post_id
    supplied = {f: getattr(args, f) for f in _METRIC_FIELDS if getattr(args, f, None) is not None}
    if not supplied:
        raise CliError(
            "ไม่มีค่าอะไรให้บันทึก — ใส่อย่างน้อยหนึ่งใน "
            "--views-24h/--views-7d/--likes/--comments/--shares/--saves/--follows-delta/--gmv/--notes"
        )

    _h(f"metrics {post_id}")
    n = dbm.update_metrics(ctx.conn(), MetricsUpdate(post_id=post_id, **supplied))
    if n == 0:
        raise CliError(f"{post_id}: ไม่มีแถวใน post_log — `log` ก่อนแล้วค่อยใส่ metrics")
    for k, v in supplied.items():
        print(f"  {k:<14}= {v}")
    print(f"updated   : {n} row · คอลัมน์ที่ไม่ได้ใส่ยังเป็น NULL (ว่างดีกว่ามั่ว)")
    rec.detail = ",".join(supplied)
    return EXIT_OK


def cmd_review(ctx: Ctx, args: argparse.Namespace, rec: Rec) -> int:
    """The 10-minute weekly ritual (§5) — rendered to stdout and to out/reviews/W{n}.md."""
    today = date.today()  # noqa: DTZ011
    week = args.week if args.week is not None else week_of_day(max(sprint_day(ctx.account, today), 1))
    md = weekly_review(ctx.conn(), ctx.account, ctx.engine, week, today)
    print(md)
    path = write_review(md, ctx.engine, week)
    print(f"\nwritten   : {path}")
    rec.detail = f"W{week}"
    return EXIT_OK


def cmd_status(ctx: Ctx, args: argparse.Namespace, rec: Rec) -> int:
    """One screen: where the sprint is and the single next action."""
    today = date.today()  # noqa: DTZ011
    batches = ctx.batches()
    day = sprint_day(ctx.account, today)

    # the batch names today's post; status must never synthesise an id (L{week}-D{day} disagrees
    # with the batch on days 29-30, and names a nonexistent post from day 31 on).
    today_post_id: str | None = None
    if day >= 1 and batches:
        try:
            today_post_id = find_post(batches, day).post_id
        except KeyError:
            today_post_id = None

    summary = status_summary(
        ctx.conn(), ctx.account, ctx.engine, set(), today,
        today_post_id=today_post_id, batch_loaded=bool(batches),
    )
    print(render_status(summary))
    rec.detail = summary["next_action"]
    return EXIT_OK


def cmd_next(ctx: Ctx, args: argparse.Namespace, rec: Rec) -> int:
    """The lowest-day post that has not gone out yet, plus its fatigue warnings."""
    spec = next_unposted(ctx.batches(), ctx.published_ids())
    if spec is None:
        print("all posted — batch หมดแล้ว (เขียน batch ใหม่ด้วย /lumora-content-batch)")
        rec.detail = "all posted"
        return EXIT_OK

    rec.post_id = spec.post_id
    rec.prompt_version = ctx.batch_id_of(spec.post_id)
    kind = "full spec" if spec.full_spec else "OUTLINE — ต้องขยายก่อน"
    print(f"next: {spec.post_id} ({_combo(spec)}) · day {spec.day} · {spec.funnel_stage} · {kind}")
    print(f"hook: {spec.hook or '—'}")
    window = max(int(ctx.engine.fatigue.same_combo_window_posts), 1)
    for w in fatigue_check(spec, _recent_combos(ctx, spec, window), ctx.engine.fatigue):
        print(f"⚠️  {w}")
    if spec.full_spec:
        print(f"→ `lumora run --day {spec.day}`")
    else:
        print(f"→ `lumora plan --day {spec.day}` (จะพิมพ์ prompt ให้ขยาย)")
    rec.detail = spec.post_id
    return EXIT_OK


def cmd_run(ctx: Ctx, args: argparse.Namespace, rec: Rec) -> int:
    """plan + generate + packet in one go. Stops before `approve` — approval is always explicit."""
    key = _resolve_key(args)
    spec = ctx.find(key)
    rec.post_id = spec.post_id
    rec.prompt_version = ctx.batch_id_of(spec.post_id)

    for name in ("plan", "generate", "packet"):
        sub = argparse.Namespace(
            command=name,
            day=getattr(args, "day", None),
            post_id=getattr(args, "post_id", None),
            force=getattr(args, "force", False),
            no_llm=getattr(args, "no_llm", False),
            reopen=getattr(args, "reopen", False),
        )
        code = _run_command(ctx, sub, HANDLERS[name])
        if code != EXIT_OK:
            rec.ok = False
            rec.detail = f"stopped at {name} (exit {code})"
            return code

    print(f"\n→ ตรวจแล้ว approve เอง: `lumora approve {spec.post_id}`  (เครื่องมือไม่ approve ให้)")
    rec.detail = "plan+generate+packet ok"
    return EXIT_OK


HANDLERS: dict[str, Handler] = {
    "init": cmd_init,
    "plan": cmd_plan,
    "generate": cmd_generate,
    "packet": cmd_packet,
    "approve": cmd_approve,
    "caption": cmd_caption,
    "log": cmd_log,
    "metrics": cmd_metrics,
    "review": cmd_review,
    "status": cmd_status,
    "next": cmd_next,
    "run": cmd_run,
}


# ── event wrapper ──────────────────────────────────────────────────────────


def _diagnostic(message: str) -> None:
    """Final line of a failed command, on stderr — flushed after whatever the handler printed."""
    sys.stdout.flush()
    print(message, file=sys.stderr)
    sys.stderr.flush()


def _run_command(ctx: Ctx, args: argparse.Namespace, handler: Handler) -> int:
    """Run one subcommand and append exactly one AgentEvent — on success AND on failure."""
    rec = Rec()
    started = time.monotonic()
    try:
        code = handler(ctx, args, rec)
    except CliError as exc:
        code, rec.ok = exc.code, False
        # unconditional: whatever progress the handler had already recorded ("0 fatigue warning(s)")
        # is not why the step failed, and the event log is append-only — an ok=false line that does
        # not say why is dead weight in the agent-failure dataset it exists to seed.
        rec.detail = str(exc)
        label = "needs-human" if exc.code == EXIT_NEEDS_HUMAN else "error"
        _diagnostic(f"{label}: {exc}")
    except (KeyError, OSError, ValueError, sqlite3.Error) as exc:
        code, rec.ok = EXIT_ERROR, False
        rec.detail = f"{type(exc).__name__}: {exc}"
        _diagnostic(f"error: {rec.detail}")

    append_event(
        ctx.events_path,
        AgentEvent(
            agent=ctx.engine.log.agent_id,
            step=args.command,
            post_id=rec.post_id,
            model=rec.model,
            prompt_version=rec.prompt_version,
            cost_usd=rec.cost_usd,
            duration_s=round(time.monotonic() - started, 3),
            ok=rec.ok and code == EXIT_OK,
            detail=rec.detail,
        ),
    )
    return code


# ── argparse ───────────────────────────────────────────────────────────────


def _add_target(p: argparse.ArgumentParser) -> None:
    """``--day N`` / ``--post-id ID`` — the two ways to name a post."""
    g = p.add_mutually_exclusive_group()
    g.add_argument("--day", type=int, help="วันที่ในสprint (1-30 ตาม batch)")
    g.add_argument("--post-id", help="post id เช่น L1-D01")


def build_parser() -> argparse.ArgumentParser:
    """The whole CLI surface. Every subcommand is deterministic except `packet`'s optional QA call."""
    p = argparse.ArgumentParser(
        prog="lumora",
        description="Lumora sprint loop — plan → generate → packet → approve → (upload by hand) → log → metrics → review",
        epilog="ไม่มีคำสั่ง publish/schedule โดยตั้งใจ: การโพสต์เป็นนิ้วโป้งของ Sin (ADR-0001).",
    )
    p.add_argument("--config-dir", default=str(DEFAULT_ROOT / "config"),
                   help="โฟลเดอร์ที่มี account.yaml + engine.yaml (default: sprint/config)")
    p.add_argument("--db", help="override engine.paths.db")
    sub = p.add_subparsers(dest="command", metavar="<command>")

    sub.add_parser("init", help="สร้าง/อัปเกรด db + ตรวจ config + สรุป account/gate")

    sp = sub.add_parser("plan", help="ตรวจ spec หนึ่งโพสต์ (legality + fatigue) แล้วตั้งเป็น planned")
    _add_target(sp)

    sp = sub.add_parser("generate", help="สร้างรูปเข้า out/<post_id>/ (stub ถ้าไม่มี API token)")
    _add_target(sp)
    sp.add_argument("--force", action="store_true", help="generate ใหม่แม้มีรูปอยู่แล้ว")

    sp = sub.add_parser("packet", help="รัน compliance gate + ประกอบ publish packet")
    _add_target(sp)
    sp.add_argument("--no-llm", action="store_true", help="ข้าม LLM QA รอบนี้ (deterministic เท่านั้น)")
    sp.add_argument("--reopen", action="store_true",
                    help="ยอมให้ลดสถานะ approved/published กลับเป็น draft (ปกติจะไม่ลด)")

    sp = sub.add_parser("approve", help="human gate — Sin อนุมัติเอง")
    sp.add_argument("post_id")

    sp = sub.add_parser("caption", help="รับ caption ที่ QA เสนอ / ใส่เอง (อยู่รอดตอน re-run)")
    sp.add_argument("post_id")
    g = sp.add_mutually_exclusive_group()
    g.add_argument("--accept-suggested", action="store_true", help="ใช้ caption ที่ LLM QA เสนอ")
    g.add_argument("--text", help="ข้อความ caption ที่จะใช้จริง")
    g.add_argument("--clear", action="store_true", help="ล้าง caption_final กลับไปใช้ของ batch")

    sp = sub.add_parser("log", help="บันทึกโพสต์ที่โพสต์ด้วยมือแล้ว")
    sp.add_argument("post_id")
    sp.add_argument("--url", required=True, help="URL ของโพสต์จริง")
    sp.add_argument("--posted-at", help="YYYY-MM-DD (default: วันนี้)")
    sp.add_argument("--notes", help="บันทึกสั้นๆ")
    sp.add_argument("--no-ai-label", action="store_true",
                    help="บันทึกว่า AI-label toggle ไม่ได้เปิด (default: เปิด)")

    sp = sub.add_parser("metrics", help="อัปเดตตัวเลขที่วัดจริง (ที่ไม่ใส่ = ยังว่าง)")
    sp.add_argument("post_id")
    sp.add_argument("--views-24h", dest="views_24h", type=int)
    sp.add_argument("--views-7d", dest="views_7d", type=int)
    sp.add_argument("--likes", type=int)
    sp.add_argument("--comments", type=int)
    sp.add_argument("--shares", type=int)
    sp.add_argument("--saves", type=int)
    sp.add_argument("--follows-delta", dest="follows_delta", type=int)
    sp.add_argument("--gmv", type=float)
    sp.add_argument("--notes", type=str)

    sp = sub.add_parser("review", help="ritual รายสัปดาห์ → out/reviews/W{n}.md")
    sp.add_argument("--week", type=int, help="เลขสัปดาห์ (default: สัปดาห์ปัจจุบันของ sprint)")

    sub.add_parser("status", help="สถานะ sprint หนึ่งหน้าจอ + next action")
    sub.add_parser("next", help="โพสต์ถัดไปที่ยังไม่ได้ลง")

    sp = sub.add_parser("run", help="plan + generate + packet (หยุดก่อน approve เสมอ)")
    _add_target(sp)
    sp.add_argument("--force", action="store_true", help="generate ใหม่แม้มีรูปอยู่แล้ว")
    sp.add_argument("--no-llm", action="store_true", help="ข้าม LLM QA รอบนี้")
    sp.add_argument("--reopen", action="store_true",
                    help="ยอมให้ packet ลดสถานะ approved/published กลับเป็น draft")

    return p


def _load_ctx(args: argparse.Namespace) -> Ctx:
    """Load account.yaml + engine.yaml from ``--config-dir`` and apply the ``--db`` override."""
    cfg_dir = Path(args.config_dir).expanduser()
    account_path = cfg_dir / "account.yaml"
    engine_path = cfg_dir / "engine.yaml"
    for p in (account_path, engine_path):
        if not p.is_file():
            raise CliError(f"ไม่พบ {p} — ชี้ --config-dir ไปที่โฟลเดอร์ที่มี account.yaml + engine.yaml")
    account = load_account(account_path)
    engine = load_engine(engine_path)
    if args.db:
        # a flag is a path the user typed in their shell, so it resolves against cwd — unlike the
        # yaml values, which EngineConfig.resolve deliberately joins onto the sprint root.
        engine.paths.db = str(Path(args.db).expanduser().resolve())
    return Ctx(account=account, engine=engine)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for ``lumora`` and ``python -m lumora_sprint.cli``. Returns the exit code."""
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    if not args.command:
        parser.print_help()
        return EXIT_ERROR

    try:
        ctx = _load_ctx(args)
    except CliError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.code
    except (OSError, ValueError) as exc:
        print(f"error: config โหลดไม่ได้ — {type(exc).__name__}: {exc}", file=sys.stderr)
        return EXIT_ERROR

    try:
        return _run_command(ctx, args, HANDLERS[args.command])
    finally:
        ctx.close()


if __name__ == "__main__":  # pragma: no cover - exercised via subprocess
    sys.exit(main())
