"""db.py — schema fidelity to 02-post-log-template §4/§5 + the empty-beats-fake metric rules."""
from __future__ import annotations

import sqlite3
from datetime import date, timedelta

import pytest

from lumora_sprint import db
from lumora_sprint.models import HOOK_TYPES, LogRow, MetricsUpdate, PacketStatus

# Local calendar day: posted_at is written from Python's date.today() (cli.py) and the review-window
# queries now cut on the same clock, instead of SQLite's UTC date('now').
TODAY = date.today()  # noqa: DTZ011


@pytest.fixture()
def conn(tmp_path):
    c = db.init_db(tmp_path / "lumora_sprint.db")
    yield c
    c.close()


def _row(post_id: str, day_offset: int = 0, **kw) -> LogRow:
    """A minimal valid LogRow, posted `day_offset` days ago."""
    base = {
        "post_id": post_id,
        "account_handle": "@มูมีแสง",
        "posted_at": TODAY - timedelta(days=day_offset),
        "content_pillar": "C2",
        "theme": "Cosmic",
        "media": "M11",
        "hook_type": "curiosity-choice",
    }
    return LogRow(**(base | kw))


# ── schema ─────────────────────────────────────────────────────────────────


def test_init_db_is_idempotent_and_seeds_hook_types(tmp_path):
    p = tmp_path / "nested" / "dir" / "sprint.db"
    c = db.init_db(p)
    c.close()
    c = db.init_db(p)  # second run must not raise or duplicate seed rows

    assert p.exists(), "init_db should create the file (and its parent dirs)"
    seeded = {r["hook_type"]: r["description"] for r in c.execute("SELECT * FROM hook_types")}
    assert set(seeded) == set(HOOK_TYPES)
    assert seeded["curiosity-choice"] == "ชวนเลือก/ทายก่อนเฉลย"  # Thai description, from the template
    c.close()


def test_post_log_has_template_columns_plus_accountability(conn):
    cols = {r["name"] for r in conn.execute("PRAGMA table_info(post_log)")}
    template = {
        "post_id", "brand_id", "account_handle", "posted_at", "content_pillar", "theme", "media",
        "jtbd", "funnel_stage", "hook_type", "ai_labeled", "url", "views_24h", "views_7d", "likes",
        "comments", "shares", "saves", "follows_delta", "gmv", "notes", "created_at", "updated_at",
    }
    assert template <= cols
    assert {"agent", "prompt_version", "gen_model", "cost_usd"} <= cols


def test_init_db_upgrades_a_pre_accountability_db(tmp_path):
    """A db created before the accountability columns existed gets them added, data intact."""
    p = tmp_path / "old.db"
    old = db.connect(p)
    old.executescript(
        "CREATE TABLE post_log (post_id TEXT PRIMARY KEY, brand_id TEXT NOT NULL DEFAULT 'own', "
        "account_handle TEXT, posted_at TEXT NOT NULL, content_pillar TEXT, theme TEXT, "
        "media TEXT, ai_labeled INTEGER NOT NULL DEFAULT 1, views_7d INTEGER, gmv REAL DEFAULT 0);"
        "INSERT INTO post_log (post_id, posted_at, content_pillar, theme, media, views_7d) "
        "VALUES ('L1-D01', '2026-08-01', 'C2', 'Cosmic', 'M11', 15400);"
    )
    old.commit()
    old.close()

    c = db.init_db(p)
    cols = {r["name"] for r in c.execute("PRAGMA table_info(post_log)")}
    assert {"agent", "prompt_version", "gen_model", "cost_usd"} <= cols
    assert db.get_post(c, "L1-D01")["views_7d"] == 15400, "upgrade must not drop existing rows"
    c.close()


def test_checks_and_hook_type_fk_are_enforced(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO post_log (post_id, posted_at, content_pillar, theme, media, hook_type) "
            "VALUES ('L1-D99', '2026-08-01', 'C2', 'Cosmic', 'M11', 'made-up-hook')"
        )  # FK to hook_types rejects free-text tags

    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO post_log (post_id, posted_at, content_pillar, theme, media, funnel_stage) "
            "VALUES ('L1-D98', '2026-08-01', 'C2', 'Cosmic', 'M11', 'Viral')"
        )  # CHECK funnel_stage IN (Hero, Hub, Hygiene)


def test_reads_work_on_a_plain_connection(tmp_path):
    """Callers must not have to use db.connect(): reads work whatever row_factory is set.

    Regression — every read used to assume sqlite3.Row and blew up on a plain sqlite3.connect().
    """
    p = tmp_path / "sprint.db"
    db.init_db(p).close()
    plain = sqlite3.connect(p)                     # no row_factory, no FK pragma
    assert plain.row_factory is None

    db.insert_log(plain, _row("L1-D01"))
    db.update_metrics(plain, MetricsUpdate(post_id="L1-D01", views_24h=8200, views_7d=15400,
                                           saves=980, follows_delta=63))
    db.upsert_packet_status(plain, "L1-D01", "own", PacketStatus.published, "out/L1-D01/meta.json")

    assert db.get_post(plain, "L1-D01")["views_7d"] == 15400
    assert db.get_packet_status(plain, "L1-D01")["status"] == "published"
    assert db.list_posts(plain)[0]["post_id"] == "L1-D01"
    assert db.recent_combos(plain, 1) == [("C2", "Cosmic", "M11")]
    assert db.top_performers(plain, days=7)[0]["post_id"] == "L1-D01"
    assert db.bottom_performers(plain, days=7)[0]["views_24h"] == 8200
    assert db.pillar_hook_rollup(plain, days=28)[0]["n"] == 1
    assert db.gate_progress(plain, TODAY)["best_post_views"] == 15400
    plain.close()


# ── insert / update / read ─────────────────────────────────────────────────


def test_insert_log_then_get_post(conn):
    db.insert_log(conn, _row("L1-D01", url="https://tiktok.com/x", notes="launch card",
                             agent="lumora-sprint", prompt_version="2026-07-w1",
                             gen_model="black-forest-labs/flux-dev", cost_usd=0.025))
    got = db.get_post(conn, "L1-D01")

    assert got is not None
    assert got["brand_id"] == "own"                       # brand_id on every row
    assert got["posted_at"] == TODAY.isoformat()
    assert (got["content_pillar"], got["theme"], got["media"]) == ("C2", "Cosmic", "M11")
    assert got["ai_labeled"] == 1
    assert got["gen_model"] == "black-forest-labs/flux-dev" and got["cost_usd"] == 0.025
    assert got["views_24h"] is None and got["views_7d"] is None  # empty beats fake
    assert db.get_post(conn, "nope") is None


def test_insert_log_twice_keeps_measured_metrics(conn):
    db.insert_log(conn, _row("L1-D01", url="typo"))
    db.update_metrics(conn, MetricsUpdate(post_id="L1-D01", views_7d=15400))
    db.insert_log(conn, _row("L1-D01", url="https://tiktok.com/fixed"))

    got = db.get_post(conn, "L1-D01")
    assert got["url"] == "https://tiktok.com/fixed"
    assert got["views_7d"] == 15400, "re-logging must not wipe measured metrics"


def test_update_metrics_is_partial(conn):
    db.insert_log(conn, _row("L1-D01"))

    assert db.update_metrics(conn, MetricsUpdate(post_id="L1-D01", views_24h=8200)) == 1
    after_24h = db.get_post(conn, "L1-D01")
    assert after_24h["views_24h"] == 8200
    assert after_24h["views_7d"] is None and after_24h["saves"] is None  # untouched stays NULL

    db.update_metrics(conn, MetricsUpdate(post_id="L1-D01", views_7d=15400, likes=1120,
                                          comments=240, shares=95, saves=980, follows_delta=63))
    after_7d = db.get_post(conn, "L1-D01")
    assert after_7d["views_24h"] == 8200                  # earlier snapshot preserved
    assert (after_7d["views_7d"], after_7d["saves"], after_7d["follows_delta"]) == (15400, 980, 63)
    assert after_7d["gmv"] == 0                            # never supplied -> default, not invented


def test_update_metrics_noop_and_unknown_post(conn):
    db.insert_log(conn, _row("L1-D01"))
    assert db.update_metrics(conn, MetricsUpdate(post_id="L1-D01")) == 0   # nothing measured
    assert db.update_metrics(conn, MetricsUpdate(post_id="ghost", views_7d=1)) == 0


def test_list_posts_and_since_filter(conn):
    db.insert_log(conn, _row("L1-D01", day_offset=10))
    db.insert_log(conn, _row("L1-D02", day_offset=2))

    assert [p["post_id"] for p in db.list_posts(conn)] == ["L1-D01", "L1-D02"]  # chronological
    recent = db.list_posts(conn, since=TODAY - timedelta(days=5))
    assert [p["post_id"] for p in recent] == ["L1-D02"]


# ── v_post_scores ──────────────────────────────────────────────────────────


def test_v_post_scores_derives_rates(conn):
    db.insert_log(conn, _row("L1-D01"))
    db.update_metrics(conn, MetricsUpdate(post_id="L1-D01", views_24h=8200, views_7d=15400,
                                          saves=980, follows_delta=63, gmv=250.0))

    s = dict(conn.execute("SELECT * FROM v_post_scores WHERE post_id = 'L1-D01'").fetchone())
    assert s["save_rate"] == pytest.approx(980 / 15400, abs=1e-4)      # 0.0636
    assert s["follow_rate"] == pytest.approx(63 / 15400, abs=1e-4)     # 0.0041
    assert s["tail_multiple"] == pytest.approx(15400 / 8200, abs=1e-2)  # 1.88
    assert s["gmv"] == 250.0


def test_v_post_scores_null_until_measured(conn):
    db.insert_log(conn, _row("L1-D01"))
    s = dict(conn.execute("SELECT * FROM v_post_scores WHERE post_id = 'L1-D01'").fetchone())
    assert s["save_rate"] is None and s["follow_rate"] is None and s["tail_multiple"] is None


# ── fatigue gate input ─────────────────────────────────────────────────────


def test_recent_combos_newest_first(conn):
    db.insert_log(conn, _row("L1-D01", day_offset=3, content_pillar="C1", theme="Future-tech", media="M1"))
    db.insert_log(conn, _row("L1-D02", day_offset=2, content_pillar="C2", theme="Cosmic", media="M11"))
    db.insert_log(conn, _row("L1-D03", day_offset=1, content_pillar="C6", theme="Historical", media="M2"))

    assert db.recent_combos(conn, 2) == [("C6", "Historical", "M2"), ("C2", "Cosmic", "M11")]
    assert len(db.recent_combos(conn, 10)) == 3       # asking for more than exists is fine
    assert db.recent_combos(conn, 0) == []


def test_recent_combos_breaks_same_day_ties_by_insertion(conn):
    db.insert_log(conn, _row("L1-D01", day_offset=1, media="M11"))
    db.insert_log(conn, _row("L1-D02", day_offset=1, media="M1"))
    assert db.recent_combos(conn, 1) == [("C2", "Cosmic", "M1")]


# ── packet status ──────────────────────────────────────────────────────────


def test_packet_status_upsert(conn):
    assert db.get_packet_status(conn, "L1-D01") is None

    db.upsert_packet_status(conn, "L1-D01", "own", PacketStatus.draft, "out/L1-D01/meta.json")
    first = db.get_packet_status(conn, "L1-D01")
    assert first["status"] == "draft" and first["brand_id"] == "own"
    assert first["meta_path"] == "out/L1-D01/meta.json"

    db.upsert_packet_status(conn, "L1-D01", "own", PacketStatus.approved, "out/L1-D01/meta.json")
    assert db.get_packet_status(conn, "L1-D01")["status"] == "approved"
    assert conn.execute("SELECT COUNT(*) c FROM packets").fetchone()["c"] == 1


# ── weekly review ritual ───────────────────────────────────────────────────


@pytest.fixture()
def week(conn):
    """Three posts inside the 7-day window + one old post outside it."""
    db.insert_log(conn, _row("L1-D01", day_offset=1, hook_type="curiosity-choice"))
    db.insert_log(conn, _row("L1-D02", day_offset=2, content_pillar="C1", theme="Future-tech",
                             media="M1", hook_type="statement"))
    db.insert_log(conn, _row("L1-D03", day_offset=3, content_pillar="C1", theme="Future-tech",
                             media="M1", hook_type="statement"))
    db.insert_log(conn, _row("L0-D00", day_offset=30, hook_type="milestone"))
    db.update_metrics(conn, MetricsUpdate(post_id="L1-D01", views_24h=8200, views_7d=15400,
                                          saves=980, follows_delta=63, gmv=250.0))
    db.update_metrics(conn, MetricsUpdate(post_id="L1-D02", views_24h=900, views_7d=1200,
                                          saves=20, follows_delta=2, gmv=0.0))
    db.update_metrics(conn, MetricsUpdate(post_id="L1-D03", views_24h=3000, views_7d=5000,
                                          saves=100, follows_delta=10, gmv=50.0))
    db.update_metrics(conn, MetricsUpdate(post_id="L0-D00", views_7d=99999, follows_delta=500))
    return conn


def test_top_performers(week):
    top = db.top_performers(week, days=7, limit=3)
    assert [p["post_id"] for p in top] == ["L1-D01", "L1-D03", "L1-D02"]  # old post excluded
    assert top[0]["save_rate"] == pytest.approx(0.0636, abs=1e-4)
    assert db.top_performers(week, days=7, limit=1)[0]["post_id"] == "L1-D01"


def test_bottom_performers_ranks_measured_worst_first(week):
    bottom = db.bottom_performers(week, days=7, limit=2)
    assert [p["post_id"] for p in bottom] == ["L1-D02", "L1-D03"]
    assert bottom[0]["views_24h"] == 900          # joined in from post_log (view lacks it)

    db.insert_log(week, _row("L1-D04", day_offset=1))   # unmeasured -> must not rank as worst
    assert db.bottom_performers(week, days=7, limit=2)[0]["post_id"] == "L1-D02"
    assert db.bottom_performers(week, days=7, limit=4)[-1]["post_id"] == "L1-D04"


def test_pillar_hook_rollup(week):
    rollup = db.pillar_hook_rollup(week, days=28)
    by_key = {(r["content_pillar"], r["hook_type"]): r for r in rollup}

    assert ("C2", "milestone") not in by_key                      # 30d old post is outside 28d
    assert by_key[("C2", "curiosity-choice")]["n"] == 1
    c1 = by_key[("C1", "statement")]
    assert c1["n"] == 2 and c1["avg_views"] == pytest.approx(3100)  # (1200 + 5000) / 2
    assert c1["total_gmv"] == pytest.approx(50)
    assert [r["content_pillar"] for r in rollup] == ["C2", "C1"]    # ordered by avg_views DESC


def test_review_windows_cut_on_the_local_day_not_utc(week):
    """The oldest day in a 7-day window must survive whatever the machine's UTC offset is.

    `posted_at` is a local calendar day; SQLite's date('now') is UTC. With a UTC cutoff the window
    silently widens or — in a negative-offset zone — genuinely drops the oldest day's posts.
    """
    edge = TODAY - timedelta(days=7)
    db.insert_log(week, _row("L1-D07", day_offset=7))          # exactly on the boundary
    db.update_metrics(week, MetricsUpdate(post_id="L1-D07", views_7d=10))

    ids = {r["post_id"] for r in db.top_performers(week, days=7, limit=10)}
    assert "L1-D07" in ids, "a post dated exactly `days` ago is inside the window"
    assert "L0-D00" not in ids                                  # 30 days old, still outside

    # an explicit `since` wins over `days`, so review.py's printed window and the SQL agree
    only_recent = db.top_performers(week, days=7, limit=10, since=TODAY - timedelta(days=2))
    assert {r["post_id"] for r in only_recent} == {"L1-D01", "L1-D02"}
    assert edge.isoformat() < TODAY.isoformat()


def test_earliest_posted_at(conn):
    assert db.earliest_posted_at(conn) is None
    db.insert_log(conn, _row("L1-D02", day_offset=2))
    db.insert_log(conn, _row("L1-D09", day_offset=9))
    assert db.earliest_posted_at(conn) == (TODAY - timedelta(days=9)).isoformat()


def test_init_db_refreshes_a_stale_v_post_scores_view(tmp_path):
    """CREATE VIEW IF NOT EXISTS never replaces — a stale view must be dropped, not kept forever.

    `_ensure_columns` upgrades an older post_log in place, but a view left over from an earlier
    schema would survive untouched and feed top_performers / pillar_hook_rollup columns that no
    longer exist — an OperationalError at review time instead of an upgrade.
    """
    p = tmp_path / "stale.db"
    c = db.init_db(p)
    c.executescript(
        "DROP VIEW v_post_scores;"
        "CREATE VIEW v_post_scores AS SELECT post_id, posted_at FROM post_log;"   # a past schema
    )
    c.commit()
    c.close()

    c = db.init_db(p)                                   # re-init must rebuild it
    cols = {d[0] for d in c.execute("SELECT * FROM v_post_scores").description}
    assert {"save_rate", "follow_rate", "tail_multiple", "hook_type"} <= cols
    c.close()


def test_gate_progress(week):
    since = (TODAY - timedelta(days=7)).isoformat()
    g = db.gate_progress(week, since)
    assert g == {"best_post_views": 15400, "followers_gained": 75, "posts_count": 3,
                 "ai_label_ok": True}

    assert db.gate_progress(week, "1900-01-01")["best_post_views"] == 99999  # whole sprint


def test_gate_progress_empty_and_ai_label_flag(conn):
    assert db.gate_progress(conn, TODAY) == {"best_post_views": 0, "followers_gained": 0,
                                             "posts_count": 0, "ai_label_ok": True}

    db.insert_log(conn, _row("L1-D01"))
    assert db.gate_progress(conn, TODAY)["ai_label_ok"] is True
    db.insert_log(conn, _row("L1-D02", ai_labeled=False))
    g = db.gate_progress(conn, TODAY)
    assert g["ai_label_ok"] is False and g["posts_count"] == 2
    assert g["best_post_views"] == 0, "no metrics measured yet -> 0, not a made-up number"
