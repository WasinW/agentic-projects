"""Weekly review ritual (sprint-2026-07/02-post-log-template.md §5) rendered as markdown.

Deterministic end-to-end — there is no LLM in this path (ADR-0001 / 07_platform_design §2: the LLM
is surgical, compliance QA only). The log is read through ``db.py`` when that module exposes the
helper, and through the canonical SQL of §5 otherwise, so the review runs standalone.

Empty beats fake: NULL metrics render as ``—`` and are named "not measured yet" in prose. Nothing
is imputed, averaged-in or back-filled — an unmeasured post is never ranked as a bad post.
"""
from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from .config import AccountConfig, EngineConfig, Gate

NOT_MEASURED = "not measured yet"
UNMEASURED_TH = f"ยังไม่ได้วัด ({NOT_MEASURED})"
DASH = "—"

# ── db access ──────────────────────────────────────────────────────────────
# db.py owns the schema; this module only reads. Every accessor prefers the db.py function of the
# same name and falls back to the §5 query, which keeps review.py importable before db.py lands.

# NOTE: v_post_scores (§4) does not project views_24h even though the §5 bottom query selects it —
# join back to post_log for that column instead of patching the template's view.
_SELECT_SCORES = """
SELECT s.post_id, s.posted_at, s.content_pillar, s.theme, s.media, s.hook_type, s.funnel_stage,
       p.views_24h, s.views_7d, p.saves, s.save_rate, s.follow_rate, s.tail_multiple, s.gmv
FROM v_post_scores s JOIN post_log p USING (post_id)
"""

_SQL_TOP = _SELECT_SCORES + """
WHERE s.posted_at >= ?
ORDER BY s.views_7d DESC, s.save_rate DESC
LIMIT ?
"""

_SQL_BOTTOM = _SELECT_SCORES + """
WHERE s.posted_at >= ? AND s.views_7d IS NOT NULL
ORDER BY s.views_7d ASC
LIMIT ?
"""

_SQL_ROLLUP = """
SELECT content_pillar, hook_type,
       COUNT(*) n, ROUND(AVG(views_7d)) avg_views,
       ROUND(AVG(save_rate), 4) avg_save_rate, ROUND(SUM(gmv)) total_gmv
FROM v_post_scores
WHERE posted_at >= ?
GROUP BY content_pillar, hook_type
ORDER BY avg_views DESC
"""

_SQL_GATE = """
SELECT MAX(views_7d) AS best_post_views,
       SUM(follows_delta) AS followers_gained,
       COUNT(*) AS posts_count,
       SUM(CASE WHEN ai_labeled = 0 THEN 1 ELSE 0 END) AS not_labeled
FROM post_log
WHERE posted_at >= ?
"""


def _db_fn(name: str):
    """Return ``db.<name>`` if db.py exposes it, else None so the local SQL fallback runs."""
    try:
        from . import db  # lazy: db.py is authored independently of this module
    except ImportError:
        return None
    return getattr(db, name, None)


def _rows(conn: sqlite3.Connection, sql: str, params: tuple) -> list[dict[str, Any]]:
    """Run a query and return plain dicts (never mutates the caller's row_factory)."""
    cur = conn.execute(sql, params)
    cols = [c[0] for c in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def _norm(rows: Any) -> list[dict[str, Any]]:
    """Normalise whatever db.py returns (dict / sqlite3.Row / namedtuple / pydantic) to dicts."""
    out: list[dict[str, Any]] = []
    for r in rows or []:
        if isinstance(r, dict):
            out.append(dict(r))
        elif hasattr(r, "keys"):            # sqlite3.Row
            out.append({k: r[k] for k in r.keys()})  # noqa: SIM118 - Row iterates values, not keys
        elif hasattr(r, "model_dump"):      # pydantic model
            out.append(r.model_dump())
        elif hasattr(r, "_asdict"):         # namedtuple
            out.append(r._asdict())
        else:
            raise TypeError(f"cannot read row of type {type(r)!r} — expected a mapping")
    return out


def read_top(conn: sqlite3.Connection, days: int, limit: int, since: str) -> list[dict[str, Any]]:
    """§5 Step 1 rows: best posts of the window, views_7d desc then save_rate desc."""
    fn = _db_fn("top_performers")
    if fn is not None:
        return _norm(fn(conn, days, limit))
    return _rows(conn, _SQL_TOP, (since, limit))


def read_bottom(conn: sqlite3.Connection, days: int, limit: int, since: str) -> list[dict[str, Any]]:
    """§5 Step 2 rows: worst *measured* posts (unmeasured ones are excluded, not ranked last)."""
    fn = _db_fn("bottom_performers")
    if fn is not None:
        rows = _norm(fn(conn, days, max(limit, 5)))
    else:
        rows = _rows(conn, _SQL_BOTTOM, (since, max(limit, 5)))
    measured = [r for r in rows if r.get("views_7d") is not None]
    return measured[:limit]


def read_rollup(conn: sqlite3.Connection, days: int, since: str) -> list[dict[str, Any]]:
    """§5 Step 3 rows: pillar x hook_type rollup over the lookback window."""
    fn = _db_fn("pillar_hook_rollup")
    if fn is not None:
        return _norm(fn(conn, days))
    return _rows(conn, _SQL_ROLLUP, (since,))


def read_gate_progress(conn: sqlite3.Connection, since_date: str) -> dict[str, Any]:
    """§5 Step 4 aggregate: best_post_views, followers_gained, posts_count, ai_label_ok."""
    fn = _db_fn("gate_progress")
    if fn is not None:
        return dict(fn(conn, since_date))
    row = _rows(conn, _SQL_GATE, (since_date,))[0]
    return {
        "best_post_views": row["best_post_views"],
        "followers_gained": row["followers_gained"],
        "posts_count": row["posts_count"] or 0,
        "ai_label_ok": (row["not_labeled"] or 0) == 0,
    }


def measured_gate(gp: dict[str, Any], posts: list[dict[str, Any]]) -> tuple[int | None, int | None]:
    """(best_views, followers_gained) with 'never measured' collapsed back to None.

    db.gate_progress reports unmeasured totals as 0 so they compare against the thresholds; for a
    *report* that reads as "measured, and it was zero". The log rows say which it really is.
    """
    best = gp.get("best_post_views")
    if not any(r.get("views_7d") is not None for r in posts):
        best = None
    followers = gp.get("followers_gained")
    if not any(r.get("follows_delta") is not None for r in posts):
        followers = None
    return best, followers


def load_log(conn: sqlite3.Connection, since: str | None = None) -> list[dict[str, Any]]:
    """Raw post_log rows (optionally from ``since`` ISO date). Shared with status.py."""
    fn = _db_fn("list_posts")
    if fn is not None:
        return _norm(fn(conn, since))
    if since:
        return _rows(conn, "SELECT * FROM post_log WHERE posted_at >= ? ORDER BY posted_at", (since,))
    return _rows(conn, "SELECT * FROM post_log ORDER BY posted_at", ())


# ── sprint calendar + gate math (Step 4; reused by status.py) ──────────────


def sprint_day(account: AccountConfig, today: date) -> int:
    """Day number of the sprint, 1-based. <= 0 means the sprint has not started yet."""
    return (today - date.fromisoformat(account.sprint_start)).days + 1


def week_of_day(day: int) -> int:
    """Sprint week for a day number (1-7 -> W1, 8-14 -> W2 ...); matches the L{week}-D{day} ids."""
    return max(1, (day + 6) // 7)


def gate_math(gate: Gate, day: int, best_views: int | None, followers_gained: int | None) -> dict[str, Any]:
    """Distance to the day-90 gate (1 post >= 50K views OR 1,000 followers) + a linear pace check.

    Percentages are None when the underlying number was never measured — never 0, which would read
    as "measured and bad".
    """
    total = max(gate.days, 1)
    elapsed_pct = round(100.0 * max(day, 0) / total, 1)
    views_pct = None if best_views is None else round(100.0 * best_views / gate.best_post_views, 1)
    foll_pct = None if followers_gained is None else round(100.0 * followers_gained / gate.followers, 1)
    measured = [p for p in (views_pct, foll_pct) if p is not None]
    progress_pct = max(measured) if measured else None
    pace_pct = None
    if progress_pct is not None and elapsed_pct > 0:
        pace_pct = round(100.0 * progress_pct / elapsed_pct)
    return {
        "day": day,
        "days": total,
        "days_left": max(total - day, 0),
        "best_views": best_views,
        "best_views_target": gate.best_post_views,
        "best_views_gap": None if best_views is None else max(gate.best_post_views - best_views, 0),
        "views_pct": views_pct,
        "followers_gained": followers_gained,
        "followers_target": gate.followers,
        "followers_gap": None if followers_gained is None else max(gate.followers - followers_gained, 0),
        "followers_pct": foll_pct,
        "progress_pct": progress_pct,
        "elapsed_pct": elapsed_pct,
        "pace_pct": pace_pct,
        "on_track": None if progress_pct is None else progress_pct >= elapsed_pct,
    }


# ── formatting helpers ─────────────────────────────────────────────────────


def _i(v: Any) -> str:
    """Thousands-separated integer, or the em dash when the metric was never measured."""
    if v is None:
        return DASH
    try:
        return f"{round(float(v)):,}"
    except (TypeError, ValueError):
        return str(v)


def _rate(v: Any) -> str:
    return DASH if v is None else f"{float(v) * 100:.2f}%"


def _mult(v: Any) -> str:
    return DASH if v is None else f"{float(v):.2f}x"


def _pct(v: Any) -> str:
    return DASH if v is None else f"{float(v):.1f}%"


def _combo(r: dict[str, Any]) -> str:
    return f"{r.get('content_pillar', '?')}×{r.get('theme', '?')}×{r.get('media', '?')}"


def _table(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "|" + "|".join("---" for _ in headers) + "|"
    body = ["| " + " | ".join(c for c in r) + " |" for r in rows]
    return "\n".join([head, sep, *body])


def derived_rates(row: dict[str, Any]) -> tuple[float | None, float | None]:
    """(save_rate, tail_multiple) — taken from the view, or derived when the source lacks them."""
    v24, v7 = row.get("views_24h"), row.get("views_7d")
    save_rate = row.get("save_rate")
    if save_rate is None and row.get("saves") is not None and v7:
        save_rate = round(row["saves"] / v7, 4)
    tail = row.get("tail_multiple")
    if tail is None and v24 and v7:
        tail = round(v7 / v24, 2)
    return save_rate, tail


def _median(values: list[float]) -> float | None:
    vals = sorted(v for v in values if v is not None)
    if not vals:
        return None
    mid = len(vals) // 2
    return vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2


# ── Step 2 diagnosis ───────────────────────────────────────────────────────


def diagnose(row: dict[str, Any], medians: dict[str, float | None]) -> list[str]:
    """Fixed heuristics from §5 Step 2 — 'low' means below the median of the same 7-day window."""
    save_rate, tail = derived_rates(row)
    v24 = row.get("views_24h")
    if v24 is None and row.get("views_7d") is None and save_rate is None:
        return [f"ยังไม่มีตัวเลข ({NOT_MEASURED}) — วินิจฉัยไม่ได้"]

    out: list[str] = []
    m24, mtail, msr = medians.get("views_24h"), medians.get("tail_multiple"), medians.get("save_rate")
    if v24 is not None and m24 is not None and v24 < m24:
        out.append(f"hook อ่อน — views_24h {_i(v24)} ต่ำกว่า median {_i(m24)} (เปลี่ยน hook_type / บรรทัดแรก)")
    if tail is not None and mtail is not None and tail < mtail:
        out.append(
            f"algo ไม่รับต่อ — tail_multiple {_mult(tail)} ต่ำกว่า median {_mult(mtail)} "
            "(combo ล้า / เวลาโพสต์ / ยาวไม่พอให้ re-watch)"
        )
    if save_rate is not None and msr is not None and save_rate < msr:
        out.append(
            f"aesthetic/คุณค่าไม่พอ — save_rate {_rate(save_rate)} ต่ำกว่า median {_rate(msr)} "
            "(ปรับ art direction หรือใส่ value ที่คนอยากเก็บ)"
        )
    if v24 is None:
        out.append(f"views_24h {NOT_MEASURED} — วินิจฉัย hook ไม่ได้")
    if not out:
        out.append("ไม่มีตัวชี้วัดไหนต่ำกว่า median — ยังไม่ต้องพักคอมโบนี้ (ข้อมูลน้อย)")
    return out


# ── Step 3 reweight ────────────────────────────────────────────────────────


def reweight(rollup: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Split pillar x hook pairs into increase / keep / rest around the medians of the rollup."""
    med_views = _median([r.get("avg_views") for r in rollup])
    use_sr = any(r.get("avg_save_rate") is not None for r in rollup)
    med_sr = _median([r.get("avg_save_rate") for r in rollup]) if use_sr else None
    buckets: dict[str, list[dict[str, Any]]] = {"increase": [], "keep": [], "rest": []}
    for r in rollup:
        av, sr = r.get("avg_views"), r.get("avg_save_rate")
        if av is None or med_views is None or (use_sr and (sr is None or med_sr is None)):
            buckets["keep"].append(r)
            continue
        hi_v, hi_s = av >= med_views, (True if not use_sr else sr >= med_sr)
        if hi_v and hi_s:
            buckets["increase"].append(r)
        elif not hi_v and not hi_s:
            buckets["rest"].append(r)
        else:
            buckets["keep"].append(r)
    return buckets


def _pair_label(r: dict[str, Any]) -> str:
    return (
        f"`{r.get('content_pillar')}×{r.get('hook_type')}` "
        f"(n={r.get('n')} · avg {_i(r.get('avg_views'))} views · save {_rate(r.get('avg_save_rate'))})"
    )


# ── the report ─────────────────────────────────────────────────────────────


def weekly_review(
    conn: sqlite3.Connection,
    account: AccountConfig,
    engine: EngineConfig,
    week: int,
    today: date,
) -> str:
    """Render the 10-minute weekly ritual (§5 steps 1-4 + the 1-line note) as markdown."""
    win_days = 7
    look_days = engine.review.lookback_days
    since_7d = (today - timedelta(days=win_days)).isoformat()
    since_look = (today - timedelta(days=look_days)).isoformat()
    day = sprint_day(account, today)

    window = load_log(conn, since_7d)
    top = read_top(conn, win_days, 3, since_7d)
    bottom = read_bottom(conn, win_days, 2, since_7d)
    rollup = read_rollup(conn, look_days, since_look)
    gp = read_gate_progress(conn, account.sprint_start)
    all_posts = load_log(conn, account.sprint_start)

    medians = _medians_of(window)
    unmeasured = [r["post_id"] for r in window if r.get("views_7d") is None]

    out: list[str] = []
    out.append(f"# W{week} — weekly review · {account.account_handle}")
    out.append("")
    out.append(f"- **วันที่รีวิว:** {today.isoformat()} · sprint **day {day} / {account.gate.days}**")
    out.append(f"- **หน้าต่างข้อมูล:** Step 1-2 = {win_days} วัน (ตั้งแต่ {since_7d}) · Step 3 = {look_days} วัน")
    out.append(f"- **โพสต์ใน 7 วัน:** {len(window)} (วัดแล้ว {len(window) - len(unmeasured)} · {NOT_MEASURED} {len(unmeasured)})")
    out.append(f"- **brand_id:** `{account.brand_id}` · legend: `{DASH}` = {NOT_MEASURED} (ว่างดีกว่ามั่ว)")
    out.append("")

    out.append(_step1(top))
    out.append(_step2(bottom, medians, unmeasured))
    out.append(_step3(rollup, account, week, look_days))
    out.append(_step4(gp, account, day, all_posts, window))

    top_id = top[0]["post_id"] if top else DASH
    bottom_id = bottom[0]["post_id"] if bottom else DASH
    out.append("## บันทึก 1 บรรทัด (เขียนเอง — decision trail)")
    out.append("")
    out.append("```")
    out.append(f"W{week}: top={top_id}, bottom={bottom_id}, changing ____________ next week")
    out.append("```")
    out.append("")
    return "\n".join(out)


def _medians_of(window: list[dict[str, Any]]) -> dict[str, float | None]:
    """Medians of the 7-day window — the yardstick every Step-2 heuristic compares against."""
    v24, tails, srs = [], [], []
    for r in window:
        sr, tail = derived_rates(r)
        if r.get("views_24h") is not None:
            v24.append(float(r["views_24h"]))
        if tail is not None:
            tails.append(float(tail))
        if sr is not None:
            srs.append(float(sr))
    return {"views_24h": _median(v24), "tail_multiple": _median(tails), "save_rate": _median(srs)}


def _step1(top: list[dict[str, Any]]) -> str:
    lines = ["## Step 1 — Top performer (double down)", ""]
    if not top:
        lines += ["ยังไม่มีโพสต์ในหน้าต่าง 7 วัน — ไม่มีอะไรให้ double down (log โพสต์ก่อน).", ""]
        return "\n".join(lines)
    rows = [
        [
            f"`{r['post_id']}`", _combo(r), f"`{r.get('hook_type', 'other')}`",
            _i(r.get("views_7d")), _rate(derived_rates(r)[0]), _rate(r.get("follow_rate")), _i(r.get("gmv")),
        ]
        for r in top
    ]
    lines.append(_table(["post_id", "combo (C×T×M)", "hook", "views_7d", "save_rate", "follow_rate", "gmv"], rows))
    lines.append("")
    best = top[0]
    if best.get("views_7d") is None:
        lines.append(f"→ **double down:** ยังตัดสินไม่ได้ — โพสต์ในหน้าต่างนี้{UNMEASURED_TH} (อัปเดต metrics ก่อน).")
    else:
        lines.append(
            f"→ **double down:** ทำซ้ำ {_combo(best)} + hook `{best.get('hook_type', 'other')}` "
            f"สัปดาห์หน้าแบบ *variation* (ไม่ใช่ copy) — `{best['post_id']}` นำอยู่ที่ {_i(best.get('views_7d'))} views."
        )
    lines.append("")
    return "\n".join(lines)


def _step2(bottom: list[dict[str, Any]], medians: dict[str, float | None], unmeasured: list[str]) -> str:
    lines = ["## Step 2 — Bottom performer (diagnose)", ""]
    if not bottom:
        lines.append(
            f"ยังไม่มีโพสต์ที่วัดแล้วในหน้าต่าง 7 วัน — จัดอันดับล่างไม่ได้ ({NOT_MEASURED})."
        )
        if unmeasured:
            lines.append(f"รอตัวเลข: {', '.join('`' + p + '`' for p in unmeasured)}")
        lines.append("")
        return "\n".join(lines)

    rows = []
    for r in bottom:
        sr, tail = derived_rates(r)
        rows.append([
            f"`{r['post_id']}`", _combo(r), f"`{r.get('hook_type', 'other')}`",
            _i(r.get("views_24h")), _i(r.get("views_7d")), _mult(tail), _rate(sr),
        ])
    lines.append(_table(["post_id", "combo (C×T×M)", "hook", "views_24h", "views_7d", "tail", "save_rate"], rows))
    lines.append("")
    lines.append(
        f"เกณฑ์เทียบ = median ของ 7 วันนี้: views_24h {_i(medians['views_24h'])} · "
        f"tail {_mult(medians['tail_multiple'])} · save_rate {_rate(medians['save_rate'])}"
    )
    lines.append("")
    for r in bottom:
        lines.append(f"- **`{r['post_id']}`** — {_combo(r)}")
        for d in diagnose(r, medians):
            lines.append(f"  - {d}")
    lines.append("")
    lines.append("→ **ทำอะไรต่อ:** ปรับ hook/aesthetic แล้วลองซ้ำ 1 ครั้ง; ถ้ายังแป้ก → พักคอมโบ (mark `notes='fatigued'`).")
    if unmeasured:
        lines.append(
            f"→ ไม่เอามาจัดอันดับเพราะ{UNMEASURED_TH}: {', '.join('`' + p + '`' for p in unmeasured)}"
        )
    lines.append("")
    return "\n".join(lines)


def _step3(rollup: list[dict[str, Any]], account: AccountConfig, week: int, look_days: int) -> str:
    lines = [f"## Step 3 — Pillar × hook rollup ({look_days} วัน)", ""]
    if not rollup:
        lines += [f"ยังไม่มีข้อมูลใน {look_days} วัน — ยัง reweight ไม่ได้.", ""]
        return "\n".join(lines)

    rows = [
        [
            f"`{r.get('content_pillar')}`", f"`{r.get('hook_type')}`", str(r.get("n", DASH)),
            _i(r.get("avg_views")), _rate(r.get("avg_save_rate")), _i(r.get("total_gmv")),
        ]
        for r in rollup
    ]
    lines.append(_table(["pillar", "hook", "n", "avg_views", "avg_save_rate", "total_gmv"], rows))
    lines.append("")

    if len(rollup) < 2:
        lines.append("→ **reweight:** มีแค่ 1 คู่ pillar×hook — ข้อมูลน้อยเกินจะปรับสัดส่วน, คงแผนเดิมไว้ก่อน.")
    else:
        b = reweight(rollup)
        if b["increase"]:
            lines.append("→ **เพิ่มสัดส่วนสัปดาห์หน้า** (avg_views + save_rate เหนือ median): "
                         + ", ".join(_pair_label(r) for r in b["increase"]))
        if b["rest"]:
            lines.append("→ **พัก / ปรับก่อนใช้ซ้ำ** (ต่ำกว่า median ทั้งสองตัว): "
                         + ", ".join(_pair_label(r) for r in b["rest"]))
        if b["keep"]:
            lines.append("→ **คงสัดส่วนเดิม** (สัญญาณผสม หรือข้อมูลยังไม่พอ): "
                         + ", ".join(_pair_label(r) for r in b["keep"]))
    nxt = account.aesthetic_weeks.get(week + 1)
    if nxt:
        lines.append(f"→ ป้อนกลับเข้า batch: aesthetic ของ **W{week + 1} = {nxt}** (art engine เท่านั้น; oracle คง Cosmic).")
    lines.append("")
    return "\n".join(lines)


def _step4(
    gp: dict[str, Any],
    account: AccountConfig,
    day: int,
    all_posts: list[dict[str, Any]],
    window: list[dict[str, Any]],
) -> str:
    best, followers = measured_gate(gp, all_posts)
    g = gate_math(account.gate, day, best, followers)
    lines = ["## Step 4 — Gate progress + compliance", ""]
    lines.append(f"- **day {g['day']} / {g['days']}** (เหลือ {g['days_left']} วัน · เวลาเดินไปแล้ว {_pct(g['elapsed_pct'])})")
    lines.append(f"- **โพสต์ที่ log แล้ว:** {gp.get('posts_count', 0)}")
    if g["best_views"] is None:
        lines.append(f"- **best post views:** {NOT_MEASURED} → ยังวัดระยะถึง {_i(g['best_views_target'])} ไม่ได้")
    else:
        lines.append(
            f"- **best post views:** {_i(g['best_views'])} / {_i(g['best_views_target'])} "
            f"({_pct(g['views_pct'])}) · ขาดอีก {_i(g['best_views_gap'])}"
        )
    if g["followers_gained"] is None:
        lines.append(f"- **followers gained:** {NOT_MEASURED} → ยังวัดระยะถึง {_i(g['followers_target'])} ไม่ได้")
    else:
        lines.append(
            f"- **followers gained:** {_i(g['followers_gained'])} / {_i(g['followers_target'])} "
            f"({_pct(g['followers_pct'])}) · ขาดอีก {_i(g['followers_gap'])}"
        )
    if g["on_track"] is None:
        lines.append(f"- **on-track:** ยังบอกไม่ได้ — ตัวเลข gate {UNMEASURED_TH}")
    else:
        verdict = "ON TRACK" if g["on_track"] else "BEHIND"
        lines.append(
            f"- **on-track:** {_pct(g['progress_pct'])} ของ gate เทียบเวลา {_pct(g['elapsed_pct'])} "
            f"→ pace **{g['pace_pct']}%** → **{verdict}** "
            "*(ไม้บรรทัดเชิงเส้น; growth ไม่ linear — ใช้เป็น sanity check)*"
        )
    lines.append("")

    # compliance — ai label + homage watch
    not_labeled = [r["post_id"] for r in all_posts if not _truthy(r.get("ai_labeled"), default=True)]
    ai_ok = gp.get("ai_label_ok", not not_labeled)
    if not all_posts:
        lines.append("- **AI label:** ยังไม่มีโพสต์ให้ตรวจ")
    elif ai_ok and not not_labeled:
        lines.append(f"- **AI label:** ครบทุกโพสต์ ({len(all_posts)}) ✓")
    else:
        ids = ", ".join(f"`{p}`" for p in not_labeled) or "(db รายงานว่าไม่ครบ)"
        lines.append(f"- **AI label:** ⚠️ ไม่ครบ — {ids} (เปิด toggle ก่อนโดนระบบจับ)")

    homage = [r["post_id"] for r in window if "homage" in str(r.get("notes") or "").lower()]
    sacred = [r["post_id"] for r in window if r.get("content_pillar") == "C1"]
    missing = [p for p in sacred if p not in homage]
    if not sacred:
        lines.append("- **Homage-watch:** ไม่มีโพสต์ C1 (sacred imagery) ใน 7 วันนี้")
    else:
        lines.append(
            f"- **Homage-watch:** C1 ใน 7 วัน = {len(sacred)} · มี note แล้ว {len(homage)}"
            + (f" · ยังไม่มี note: {', '.join('`' + p + '`' for p in missing)}" if missing else " ✓")
        )
    lines.append("- **AI-suppression watch:** ถ้า labeled posts reach ตกผิดปกติ → เพิ่มสัดส่วน C9 voice/comedy (human layer).")
    lines.append("")
    return "\n".join(lines)


def _truthy(v: Any, default: bool = True) -> bool:
    if v is None:
        return default
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v != 0
    return str(v).strip().lower() in {"1", "true", "yes", "y"}


# ── output ─────────────────────────────────────────────────────────────────


def review_path(engine: EngineConfig, week: int) -> Path:
    """out/reviews/W{n}.md for this engine config."""
    return engine.resolve(engine.paths.reviews_dir) / f"W{week}.md"


def write_review(md: str, engine: EngineConfig, week: int) -> Path:
    """Write the rendered review to out/reviews/W{n}.md and return the path."""
    p = review_path(engine, week)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(md, encoding="utf-8")
    return p
