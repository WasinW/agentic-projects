"""SQLite store for the sprint loop — the per-post log + packet status + review queries.

Schema mirrors `sprint-2026-07/02-post-log-template.md` §4 verbatim (so a Phase-2 ingest into
Supabase `posts` + `performance` is a plain column map) plus four additive accountability columns
(`agent`, `prompt_version`, `gen_model`, `cost_usd`) — log from post #1, per ADR-0001.

Rules honoured here:
  * stdlib `sqlite3` only, no ORM (thin loop, not the parked backend);
  * `brand_id` on every row;
  * `hook_type` is a fixed tag enforced by a lookup table + FK, never free text;
  * empty beats fake — metric columns stay NULL until actually measured, and `update_metrics`
    only writes the fields that were supplied.
"""
from __future__ import annotations

import sqlite3
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from .models import HOOK_TYPES, LogRow, MetricsUpdate, PacketStatus

# ── schema ─────────────────────────────────────────────────────────────────

#: Thai descriptions for the fixed hook tags (02-post-log-template.md §3).
HOOK_TYPE_DESCRIPTIONS: dict[str, str] = {
    "curiosity-choice": "ชวนเลือก/ทายก่อนเฉลย",
    "statement": "ประโยคยืนยัน/ทัศนะ",
    "relatable-callout": "ประเภทคนที่... (self-deprecating)",
    "question": "ตั้งคำถามตรงกับผู้ชม",
    "list-promise": "สัญญาว่ามีของให้เลือก N อย่าง",
    "milestone": "หมุด/โอกาส/ครบรอบ",
    "other": "อื่นๆ (fixed bucket, not free text)",
}

SCHEMA_SQL = """
-- ── fixed-tag lookup (hook types) — pattern from reject_reasons in 001_init.sql ──
CREATE TABLE IF NOT EXISTS hook_types (
  hook_type    TEXT PRIMARY KEY,
  description  TEXT
);

-- ── the log (one row per PUBLISHED post) ────────────────────────────────
CREATE TABLE IF NOT EXISTS post_log (
  post_id         TEXT PRIMARY KEY,               -- 'L1-D01' (stable, hand-entered)
  brand_id        TEXT NOT NULL DEFAULT 'own',    -- brand_id discipline (Phase1 own -> Phase2 client)
  account_handle  TEXT NOT NULL DEFAULT '@มูมีแสง',
  posted_at       TEXT NOT NULL,                  -- ISO-8601 'YYYY-MM-DD' or full datetime

  -- 3-axis tagging (-> posts.content_pillar/theme/media_format)
  content_pillar  TEXT NOT NULL,                  -- C1..C10
  theme           TEXT NOT NULL,                  -- Cosmic / Future-tech / Historical / Pastoral / Contemporary
  media           TEXT NOT NULL,                  -- M1..M12
  jtbd            TEXT,
  funnel_stage    TEXT DEFAULT 'Hub',             -- Hero | Hub | Hygiene
  hook_type       TEXT REFERENCES hook_types(hook_type),  -- fixed tag only
  ai_labeled      INTEGER NOT NULL DEFAULT 1,     -- 0/1: AI-label toggle flipped (default yes)
  url             TEXT,

  -- performance snapshots (-> performance.*) — NULL until measured
  views_24h       INTEGER,
  views_7d        INTEGER,
  likes           INTEGER,
  comments        INTEGER,
  shares          INTEGER,
  saves           INTEGER,
  follows_delta   INTEGER,
  gmv             REAL DEFAULT 0,                 -- บาท (-> performance.revenue)

  notes           TEXT,
  created_at      TEXT DEFAULT (datetime('now')),
  updated_at      TEXT DEFAULT (datetime('now')),

  -- accountability byproduct (agent-failure dataset seed) — additive to template §4
  agent           TEXT,
  prompt_version  TEXT,
  gen_model       TEXT,
  cost_usd        REAL DEFAULT 0,

  CHECK (funnel_stage IN ('Hero','Hub','Hygiene')),
  CHECK (ai_labeled IN (0,1))
);

CREATE INDEX IF NOT EXISTS idx_postlog_pillar ON post_log(brand_id, content_pillar);
CREATE INDEX IF NOT EXISTS idx_postlog_date   ON post_log(brand_id, posted_at);
CREATE INDEX IF NOT EXISTS idx_postlog_combo  ON post_log(content_pillar, theme, media);

-- ── publish-packet state (human-gated; nothing here ever publishes) ─────
CREATE TABLE IF NOT EXISTS packets (
  post_id     TEXT PRIMARY KEY,
  brand_id    TEXT NOT NULL DEFAULT 'own',
  status      TEXT NOT NULL,
  meta_path   TEXT,
  updated_at  TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_packets_status ON packets(brand_id, status);

-- derived engagement view (save-rate = strongest signal for oracle/wallpaper).
-- Dropped first: CREATE VIEW IF NOT EXISTS never *replaces*, so an older db would keep a stale
-- definition forever and fail at review time with a column error instead of upgrading. The view is
-- derived from post_log, so dropping it costs nothing.
DROP VIEW IF EXISTS v_post_scores;
CREATE VIEW v_post_scores AS
SELECT
  post_id, posted_at, content_pillar, theme, media, hook_type, funnel_stage,
  views_7d, saves, follows_delta, gmv,
  CASE WHEN views_7d > 0 THEN ROUND(1.0*saves        /views_7d, 4) END AS save_rate,
  CASE WHEN views_7d > 0 THEN ROUND(1.0*follows_delta/views_7d, 4) END AS follow_rate,
  CASE WHEN views_24h > 0 THEN ROUND(1.0*views_7d    /views_24h, 2) END AS tail_multiple
FROM post_log;
"""

#: Additive columns, kept as (name, ddl) so an older db file can be upgraded in place.
_ADDITIVE_COLUMNS: tuple[tuple[str, str], ...] = (
    ("agent", "TEXT"),
    ("prompt_version", "TEXT"),
    ("gen_model", "TEXT"),
    ("cost_usd", "REAL DEFAULT 0"),
)


# ── connection / init ──────────────────────────────────────────────────────


def connect(path: str | Path) -> sqlite3.Connection:
    """Open the sprint db with FK enforcement and dict-like rows."""
    p = Path(path)
    if p.name != ":memory:":
        p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(path: str | Path) -> sqlite3.Connection:
    """Create (or upgrade) the schema and seed the hook_types lookup. Idempotent.

    Returns an open connection so callers can chain straight into inserts.
    """
    conn = connect(path)
    conn.executescript(SCHEMA_SQL)
    _ensure_columns(conn)
    conn.executemany(
        "INSERT OR IGNORE INTO hook_types (hook_type, description) VALUES (?, ?)",
        [(h, HOOK_TYPE_DESCRIPTIONS.get(h, "")) for h in HOOK_TYPES],
    )
    conn.commit()
    return conn


def _ensure_columns(conn: sqlite3.Connection) -> None:
    """Add accountability columns to a post_log created by an older version."""
    existing = {r["name"] for r in conn.execute("PRAGMA table_info(post_log)")}
    for name, ddl in _ADDITIVE_COLUMNS:
        if name not in existing:
            conn.execute(f"ALTER TABLE post_log ADD COLUMN {name} {ddl}")


# ── helpers ────────────────────────────────────────────────────────────────


def _rows(cursor: sqlite3.Cursor) -> list[dict[str, Any]]:
    """All rows as dicts.

    Built from cursor.description rather than dict(sqlite3.Row) so every read works whatever
    row_factory the caller's connection uses — callers must not have to know about `connect()`.
    """
    cols = [d[0] for d in cursor.description]
    return [dict(zip(cols, r, strict=True)) for r in cursor.fetchall()]


def _one(cursor: sqlite3.Cursor) -> dict[str, Any] | None:
    """First row as a dict, or None. Same row_factory independence as `_rows`."""
    r = cursor.fetchone()
    if r is None:
        return None
    return dict(zip([d[0] for d in cursor.description], r, strict=True))


def _iso(d: str | date) -> str:
    """Normalise a date/ISO string to 'YYYY-MM-DD' (or pass a full datetime string through)."""
    return d.isoformat() if isinstance(d, date) else str(d)


def _since(days: int, since: str | date | None = None) -> str:
    """Window start as an ISO date: the caller's explicit ``since``, else ``days`` back from today.

    Deliberately *not* SQLite's ``date('now', '-N day')``: that is UTC, while ``posted_at`` is
    written from Python's local calendar day (cli.py). In a positive-offset zone the SQLite date
    lags by a day for part of the morning and the window silently widens; in a negative-offset zone
    it leads and genuinely drops the oldest day's posts. Compute the cutoff in the same clock the
    rows were written in.
    """
    if since is not None:
        return _iso(since)
    return (date.today() - timedelta(days=max(int(days), 0))).isoformat()  # noqa: DTZ011


# ── writes ─────────────────────────────────────────────────────────────────


def insert_log(conn: sqlite3.Connection, row: LogRow) -> int:
    """Insert one published post into post_log.

    Re-logging the same post_id refreshes the descriptive + accountability fields (e.g. the URL
    was pasted wrong) and deliberately leaves every measured metric column untouched.
    """
    params = {
        "post_id": row.post_id,
        "brand_id": row.brand_id,
        "account_handle": row.account_handle,
        "posted_at": _iso(row.posted_at),
        "content_pillar": row.content_pillar,
        "theme": row.theme,
        "media": row.media,
        "jtbd": row.jtbd,
        "funnel_stage": row.funnel_stage,
        "hook_type": row.hook_type,
        "ai_labeled": int(row.ai_labeled),
        "url": row.url,
        "notes": row.notes,
        "agent": row.agent,
        "prompt_version": row.prompt_version,
        "gen_model": row.gen_model,
        "cost_usd": row.cost_usd,
    }
    cols = ", ".join(params)
    binds = ", ".join(f":{k}" for k in params)
    updates = ", ".join(f"{k} = excluded.{k}" for k in params if k != "post_id")
    cur = conn.execute(
        f"INSERT INTO post_log ({cols}) VALUES ({binds}) "
        f"ON CONFLICT(post_id) DO UPDATE SET {updates}, updated_at = datetime('now')",
        params,
    )
    conn.commit()
    return cur.rowcount


def update_metrics(conn: sqlite3.Connection, update: MetricsUpdate) -> int:
    """Write only the metrics that were actually measured (None = leave NULL/unchanged).

    Returns the number of rows updated (0 if nothing was supplied or post_id is unknown).
    """
    fields = update.model_dump(exclude_none=True, exclude={"post_id"})
    if not fields:
        return 0
    sets = ", ".join(f"{k} = :{k}" for k in fields)
    cur = conn.execute(
        f"UPDATE post_log SET {sets}, updated_at = datetime('now') WHERE post_id = :post_id",
        {**fields, "post_id": update.post_id},
    )
    conn.commit()
    return cur.rowcount


def upsert_packet_status(
    conn: sqlite3.Connection,
    post_id: str,
    brand_id: str,
    status: PacketStatus | str,
    meta_path: str = "",
) -> int:
    """Track where a publish packet sits in the human-gated state machine."""
    cur = conn.execute(
        "INSERT INTO packets (post_id, brand_id, status, meta_path, updated_at) "
        "VALUES (?, ?, ?, ?, datetime('now')) "
        "ON CONFLICT(post_id) DO UPDATE SET brand_id = excluded.brand_id, "
        "status = excluded.status, meta_path = excluded.meta_path, updated_at = datetime('now')",
        (post_id, brand_id, str(status), meta_path),
    )
    conn.commit()
    return cur.rowcount


# ── reads ──────────────────────────────────────────────────────────────────


def get_post(conn: sqlite3.Connection, post_id: str) -> dict[str, Any] | None:
    """One post_log row as a dict, or None if it was never logged."""
    return _one(conn.execute("SELECT * FROM post_log WHERE post_id = ?", (post_id,)))


def list_posts(conn: sqlite3.Connection, since: str | date | None = None) -> list[dict[str, Any]]:
    """All logged posts (chronological). `since` filters on posted_at >= that ISO date."""
    if since is None:
        return _rows(conn.execute("SELECT * FROM post_log ORDER BY posted_at, rowid"))
    return _rows(
        conn.execute(
            "SELECT * FROM post_log WHERE posted_at >= ? ORDER BY posted_at, rowid", (_iso(since),)
        )
    )


def get_packet_status(conn: sqlite3.Connection, post_id: str) -> dict[str, Any] | None:
    """Packet-status row as a dict, or None if the packet was never tracked."""
    return _one(conn.execute("SELECT * FROM packets WHERE post_id = ?", (post_id,)))


def earliest_posted_at(conn: sqlite3.Connection) -> str | None:
    """The oldest ``posted_at`` in post_log as 'YYYY-MM-DD', or None when nothing is logged.

    Lets the readers open their window early enough to see a post dated before ``sprint_start`` —
    a row the tool accepted must never be invisible to ``status``/``review``.
    """
    row = _one(conn.execute("SELECT MIN(posted_at) AS first_posted FROM post_log"))
    first = row["first_posted"] if row else None
    return str(first)[:10] if first else None


def recent_combos(conn: sqlite3.Connection, n: int) -> list[tuple[str, str, str]]:
    """The (content_pillar, theme, media) of the last `n` published posts, newest first.

    Feeds the fatigue gate (engine.yaml `fatigue.*`). Ties on posted_at break by insertion order.
    """
    if n <= 0:
        return []
    cur = conn.execute(
        "SELECT content_pillar, theme, media FROM post_log ORDER BY posted_at DESC, rowid DESC LIMIT ?",
        (int(n),),
    )
    return [(r["content_pillar"], r["theme"], r["media"]) for r in _rows(cur)]


# ── weekly review ritual (02-post-log-template §5) ─────────────────────────


def top_performers(
    conn: sqlite3.Connection, days: int = 7, limit: int = 3, since: str | date | None = None
) -> list[dict[str, Any]]:
    """Step 1 — what to double down on next week. ``since`` overrides the ``days`` lookback."""
    return _rows(
        conn.execute(
            "SELECT post_id, content_pillar, theme, media, hook_type, views_7d, save_rate, "
            "follow_rate, gmv FROM v_post_scores WHERE posted_at >= ? "
            "ORDER BY views_7d DESC, save_rate DESC LIMIT ?",
            (_since(days, since), int(limit)),
        )
    )


def bottom_performers(
    conn: sqlite3.Connection, days: int = 7, limit: int = 2, since: str | date | None = None
) -> list[dict[str, Any]]:
    """Step 2 — what to diagnose (weak hook? aesthetic? fatigued combo?).

    Two deliberate deviations from the template SQL: `views_24h` is joined in from post_log (the
    view does not expose it, though §5 selects it), and unmeasured posts (views_7d NULL) sort to
    the end instead of the front, so a not-yet-measured post is never reported as the worst.
    """
    return _rows(
        conn.execute(
            "SELECT s.post_id, s.content_pillar, s.theme, s.media, s.hook_type, "
            "p.views_24h, s.views_7d, s.save_rate "
            "FROM v_post_scores s JOIN post_log p ON p.post_id = s.post_id "
            "WHERE s.posted_at >= ? "
            "ORDER BY (s.views_7d IS NULL), s.views_7d ASC LIMIT ?",
            (_since(days, since), int(limit)),
        )
    )


def pillar_hook_rollup(
    conn: sqlite3.Connection, days: int = 28, since: str | date | None = None
) -> list[dict[str, Any]]:
    """Step 3 — which pillar x hook pays, over the review lookback window."""
    return _rows(
        conn.execute(
            "SELECT content_pillar, hook_type, COUNT(*) n, ROUND(AVG(views_7d)) avg_views, "
            "ROUND(AVG(save_rate), 4) avg_save_rate, ROUND(SUM(gmv)) total_gmv "
            "FROM v_post_scores WHERE posted_at >= ? "
            "GROUP BY content_pillar, hook_type ORDER BY avg_views DESC",
            (_since(days, since),),
        )
    )


def gate_progress(conn: sqlite3.Connection, since_date: str | date) -> dict[str, Any]:
    """Step 4 — distance to the day-90 gate (1 post >= 50K views OR 1,000 followers).

    Unmeasured totals report as 0 (nothing measured yet), which compares correctly against the
    gate thresholds. `ai_label_ok` is True when every logged post has ai_labeled = 1 (vacuously
    true when nothing is logged yet).
    """
    r = _one(
        conn.execute(
            "SELECT MAX(views_7d) best_post_views, SUM(follows_delta) followers_gained, "
            "COUNT(*) posts_count, COALESCE(MIN(ai_labeled), 1) min_ai_labeled "
            "FROM post_log WHERE posted_at >= ?",
            (_iso(since_date),),
        )
    )
    assert r is not None  # aggregate query always returns exactly one row
    return {
        "best_post_views": int(r["best_post_views"] or 0),
        "followers_gained": int(r["followers_gained"] or 0),
        "posts_count": int(r["posts_count"] or 0),
        "ai_label_ok": bool(r["min_ai_labeled"] == 1),
    }
