"""One-screen sprint status + the single next action. Deterministic, no LLM (ADR-0001 / 07 §2).

Answers the only question Sin asks the tool between posts: *what do I do right now?* — from the
post_log, the packet states (db `packets` table if present, else out/<post_id>/meta.json) and the
sprint calendar. Publishing is never an action this tool takes; the furthest it goes is telling Sin
to post by hand and log the url.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import date, timedelta
from typing import Any

from .config import AccountConfig, EngineConfig
from .models import PacketStatus
from .review import (
    NOT_MEASURED,
    gate_math,
    load_log,
    measured_gate,
    read_gate_progress,
    review_path,
    sprint_day,
    sprint_window_start,
    week_of_day,
)

DASH = "—"
STATUS_ORDER: tuple[str, ...] = tuple(s.value for s in PacketStatus)

#: What to say once the sprint runs past the last planned post (same wording as `lumora next`).
BATCH_EXHAUSTED = "batch หมดแล้ว — เขียน batch ใหม่ด้วย /lumora-content-batch"


# ── packet states ──────────────────────────────────────────────────────────


def read_packets(conn: sqlite3.Connection, engine: EngineConfig) -> tuple[dict[str, str], str]:
    """Return ({post_id: status}, source) — the db `packets` rows, else out/<post_id>/meta.json.

    db.py creates `packets` on init, so an empty table is not a source of truth: it just means no
    packet was tracked there yet, and the packets on disk are the better answer.
    """
    from_db = _packets_from_db(conn)
    if from_db:
        return from_db, "db"
    from_disk = _packets_from_out(engine)
    return from_disk, "out" if from_disk else "none"


def _packets_from_db(conn: sqlite3.Connection) -> dict[str, str]:
    try:
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='packets'")
        if cur.fetchone() is None:
            return {}
        rows = conn.execute("SELECT post_id, status FROM packets").fetchall()
    except sqlite3.Error:
        return {}
    return {r[0]: str(r[1]) for r in rows if r[0]}


def _packets_from_out(engine: EngineConfig) -> dict[str, str]:
    out_dir = engine.resolve(engine.paths.out_dir)
    packets: dict[str, str] = {}
    if not out_dir.is_dir():
        return packets
    for meta in sorted(out_dir.glob("*/meta.json")):
        try:
            data = json.loads(meta.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue                                  # unreadable packet = not a state we can trust
        if not isinstance(data, dict):
            continue
        post_id = str(data.get("post_id") or meta.parent.name)
        packets[post_id] = str(data.get("status") or PacketStatus.planned.value)
    return packets


# ── review calendar ────────────────────────────────────────────────────────


def next_review_day(day: int, review_days: list[int], done: set[int] | None = None) -> int:
    """Next review day still owed: >= today's day number and not already written.

    Extrapolates weekly past the configured list so a 90-day sprint keeps a review date.
    """
    done = done or set()
    days = sorted(d for d in review_days if d > 0) or [7]
    for d in days:
        if d >= day and d not in done:
            return d
    step = (days[-1] - days[-2]) if len(days) >= 2 else 7
    step = step if step > 0 else 7
    k = max(1, -(-(day - days[-1]) // step))
    return days[-1] + step * k


def due_reviews(day: int, engine: EngineConfig) -> list[int]:
    """Review days already reached whose out/reviews/W{n}.md does not exist yet."""
    return [
        d for d in sorted(engine.review.days)
        if 0 < d <= day and not review_path(engine, week_of_day(d)).exists()
    ]


# ── next action ────────────────────────────────────────────────────────────


def _more(ids: list[str]) -> str:
    """' (+N more)' tail — the action names one post_id, the tail says how many are queued."""
    return f" (+{len(ids) - 1} more)" if len(ids) > 1 else ""


def rank_actions(
    *,
    day: int,
    posts: list[dict[str, Any]],
    packets: dict[str, str],
    published_ids: set[str],
    logged_ids: set[str],
    due: list[int],
    today: date,
    today_post_id: str | None = None,
    batch_loaded: bool = False,
) -> list[str]:
    """All pending actions, most urgent first. Order = finish what is in flight before starting new.

    review (date-bound ritual) > blocked (pipeline stall) > log url (a row must exist before metrics)
    > 24h metrics (the number disappears if not caught) > approve > generate today > 7d metrics.

    ``today_post_id`` is the id the *batch* gives day ``day``; this module never synthesises one.
    ``L{week_of_day(day)}-D{day:02d}`` looks right and is wrong wherever the batch disagrees — the
    30-day plan labels days 29-30 ``L4-*`` while ``week_of_day`` says week 5 — and past the end of
    the batch it names a post that exists nowhere. ``batch_loaded`` says a batch *was* read, so a
    missing id means "batch is finished", not "caller didn't tell us".
    """
    actions: list[str] = []
    by_status: dict[str, list[str]] = {s: [] for s in STATUS_ORDER}
    for pid, st in sorted(packets.items()):
        by_status.setdefault(st, []).append(pid)

    if due:
        actions.append(f"review week {week_of_day(due[0])} due")

    blocked = sorted(by_status.get(PacketStatus.blocked.value, []))
    if blocked:
        actions.append(f"fix caption + re-run packet {blocked[0]} (blocked){_more(blocked)}")

    to_log = sorted((published_ids | set(by_status.get(PacketStatus.approved.value, []))) - logged_ids)
    if to_log:
        actions.append(f"log {to_log[0]} url{_more(to_log)}")

    yesterday = (today - timedelta(days=1)).isoformat()
    need_24h = sorted(
        r["post_id"] for r in posts
        if r.get("views_24h") is None and str(r.get("posted_at", ""))[:10] <= yesterday
    )
    if need_24h:
        actions.append(f"update 24h metrics for {need_24h[0]}{_more(need_24h)}")

    drafts = sorted(by_status.get(PacketStatus.draft.value, []))
    if drafts:
        actions.append(f"approve {drafts[0]}{_more(drafts)}")

    if day >= 1 and today_post_id:
        if packets.get(today_post_id, PacketStatus.planned.value) == PacketStatus.planned.value:
            actions.append(f"generate day {day} ({today_post_id})")
    elif day >= 1 and batch_loaded:
        actions.append(BATCH_EXHAUSTED)

    week_ago = (today - timedelta(days=7)).isoformat()
    need_7d = sorted(
        r["post_id"] for r in posts
        if r.get("views_7d") is None and str(r.get("posted_at", ""))[:10] <= week_ago
    )
    if need_7d:
        actions.append(f"update 7d metrics for {need_7d[0]}{_more(need_7d)}")

    return actions


# ── summary ────────────────────────────────────────────────────────────────


def status_summary(
    conn: sqlite3.Connection,
    account: AccountConfig,
    engine: EngineConfig,
    batches_published_ids: set[str],
    today: date,
    *,
    today_post_id: str | None = None,
    batch_loaded: bool = False,
) -> dict[str, Any]:
    """Everything the CLI shows in one deterministic, JSON-serialisable dict.

    ``batches_published_ids`` = post_ids the caller already knows are live (e.g. from the batch/CLI);
    unioned with packets whose status is ``published``. ``today_post_id`` / ``batch_loaded`` are the
    caller's view of the batch — see :func:`rank_actions`.
    """
    day = sprint_day(account, today)
    since = sprint_window_start(conn, account.sprint_start)
    posts = load_log(conn, since)
    logged_ids = {r["post_id"] for r in posts}
    packets, packets_source = read_packets(conn, engine)
    published_ids = set(batches_published_ids or set()) | {
        pid for pid, st in packets.items() if st == PacketStatus.published.value
    }

    gp = read_gate_progress(conn, since)
    best_views, followers = measured_gate(gp, posts)
    gate = gate_math(account.gate, day, best_views, followers)

    measured7 = [r for r in posts if r.get("views_7d") is not None]
    best_row = max(measured7, key=lambda r: r["views_7d"], default=None)
    measured24 = [r for r in posts if r.get("views_24h") is not None]
    best24 = max((r["views_24h"] for r in measured24), default=None)

    counts = {s: 0 for s in STATUS_ORDER}
    for st in packets.values():
        counts[st] = counts.get(st, 0) + 1

    due = due_reviews(day, engine)
    written = {d for d in engine.review.days if 0 < d <= day and d not in due}
    nxt_day = next_review_day(day, engine.review.days, done=written)
    actions = rank_actions(
        day=day, posts=posts, packets=packets, published_ids=published_ids,
        logged_ids=logged_ids, due=due, today=today,
        today_post_id=today_post_id, batch_loaded=batch_loaded,
    )
    if day < 1:
        actions = [f"sprint starts {account.sprint_start} — เตรียม batch ให้พร้อม"]
    if not actions:
        actions = [f"all caught up — day {day}: ไม่มีอะไรค้าง"]

    return {
        "account_handle": account.account_handle,
        "brand_id": account.brand_id,
        "today": today.isoformat(),
        "sprint_start": account.sprint_start,
        "log_window_start": since,          # == sprint_start unless a post was logged before it
        "today_post_id": today_post_id,
        "day": day,
        "days_total": gate["days"],
        "days_left": gate["days_left"],
        "posts_published": len(posts),
        "best_views": best_row["views_7d"] if best_row else None,
        "best_views_post_id": best_row["post_id"] if best_row else None,
        "best_views_24h": best24,
        "followers_gained": followers,
        "ai_label_ok": gp.get("ai_label_ok", True),
        "gate": gate,
        "next_review_day": nxt_day,
        "next_review_week": week_of_day(nxt_day),
        "next_review_in_days": max(nxt_day - day, 0),
        "reviews_due": due,
        "packets": counts,
        "packets_total": sum(counts.values()),
        "packets_source": packets_source,
        "unlogged_ids": sorted(published_ids - logged_ids),
        "next_action": actions[0],
        "pending_actions": actions,
    }


def render_status(d: dict[str, Any]) -> str:
    """Plain-text one-screen render of ``status_summary`` (CLI default output)."""
    g = d["gate"]
    lines: list[str] = []
    lines.append(f"LUMORA sprint · {d['account_handle']} · day {d['day']}/{d['days_total']} (เหลือ {d['days_left']} วัน)")

    best = DASH if d["best_views"] is None else f"{d['best_views']:,}"
    best_id = f" ({d['best_views_post_id']})" if d["best_views_post_id"] else ""
    foll = DASH if d["followers_gained"] is None else f"{d['followers_gained']:,}"
    lines.append(
        f"posts logged: {d['posts_published']} · best views (7d): {best}{best_id} · followers gained: {foll}"
    )

    if g["on_track"] is None:
        lines.append(f"gate: {NOT_MEASURED} — target {g['best_views_target']:,} views หรือ {g['followers_target']:,} followers")
    else:
        vp = DASH if g["views_pct"] is None else f"{g['views_pct']:.1f}%"
        fp = DASH if g["followers_pct"] is None else f"{g['followers_pct']:.1f}%"
        verdict = "ON TRACK" if g["on_track"] else "BEHIND"
        lines.append(
            f"gate: views {vp} of {g['best_views_target']:,} · followers {fp} of {g['followers_target']:,} "
            f"· elapsed {g['elapsed_pct']:.1f}% → pace {g['pace_pct']}% [{verdict}]"
        )

    counts = " · ".join(f"{k} {v}" for k, v in d["packets"].items())
    lines.append(f"packets: {counts}  [source: {d['packets_source']}]")

    if d["reviews_due"]:
        # never print an extrapolated future date next to "DUE NOW": with four reviews overdue the
        # old line read "next review: day 35 (W5, อีก 6 วัน) — DUE NOW (W1)", which is a contradiction.
        weeks = sorted({week_of_day(x) for x in d["reviews_due"]})
        span = f"W{weeks[0]}" if len(weeks) == 1 else f"W{weeks[0]}..W{weeks[-1]}"
        lines.append(f"next review: DUE NOW — {span} ({len(d['reviews_due'])} ค้าง)")
    else:
        lines.append(
            f"next review: day {d['next_review_day']} (W{d['next_review_week']}, อีก {d['next_review_in_days']} วัน)"
        )
    if not d.get("ai_label_ok", True):
        lines.append("⚠️  AI label ไม่ครบทุกโพสต์ — เปิด toggle ก่อนโดนระบบจับ")

    lines.append(f"→ NEXT: {d['next_action']}")
    rest = d["pending_actions"][1:]
    if rest:
        lines.append("   also pending: " + " · ".join(rest))
    return "\n".join(lines)
