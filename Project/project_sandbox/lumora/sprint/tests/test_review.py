"""Tests for review.py (weekly ritual) and status.py (next action).

The fixture db is the real schema (db.py `init_db`, itself a verbatim mirror of
sprint-2026-07/02-post-log-template.md §4: post_log + packets + v_post_scores); one test forces the
standalone SQL fallback in review.py so both read paths stay honest. All dates are relative to the
real ``date.today()`` so the assertions hold for either path (db.py windows on SQLite's
``date('now')``, the fallback windows on the ``today`` argument).
"""
from __future__ import annotations

import json
import sqlite3
from datetime import date, timedelta

import pytest

from lumora_sprint import db, review
from lumora_sprint.config import EngineConfig, load_account
from lumora_sprint.review import (
    NOT_MEASURED,
    diagnose,
    gate_math,
    review_path,
    reweight,
    sprint_day,
    week_of_day,
    weekly_review,
    write_review,
)
from lumora_sprint.status import (
    next_review_day,
    render_status,
    status_summary,
)

INSERT = """
INSERT INTO post_log (post_id, posted_at, content_pillar, theme, media, funnel_stage, hook_type,
                      ai_labeled, url, views_24h, views_7d, likes, comments, shares, saves,
                      follows_delta, gmv, notes)
VALUES (:post_id, :posted_at, :content_pillar, :theme, :media, :funnel_stage, :hook_type,
        :ai_labeled, :url, :views_24h, :views_7d, :likes, :comments, :shares, :saves,
        :follows_delta, :gmv, :notes)
"""

# local calendar day on purpose: the sprint is a human ritual counted in Sin's own days
TODAY = date.today()  # noqa: DTZ011


def _row(**kw):
    """A post_log row with every metric NULL — override only what the test actually measures."""
    base = {
        "post_id": "X", "posted_at": TODAY.isoformat(), "content_pillar": "C2", "theme": "Cosmic",
        "media": "M11", "funnel_stage": "Hub", "hook_type": "other", "ai_labeled": 1, "url": "",
        "views_24h": None, "views_7d": None, "likes": None, "comments": None, "shares": None,
        "saves": None, "follows_delta": None, "gmv": 0, "notes": "",
    }
    base.update(kw)
    return base


@pytest.fixture()
def conn() -> sqlite3.Connection:
    """Empty log on the real §4 schema (post_log + packets + v_post_scores)."""
    c = db.init_db(":memory:")
    yield c
    c.close()


@pytest.fixture()
def conn3(conn) -> sqlite3.Connection:
    """3 posts: full metrics / 24h only / unmeasured."""
    rows = [
        _row(post_id="L1-D01", posted_at=(TODAY - timedelta(days=6)).isoformat(), content_pillar="C2",
             theme="Cosmic", media="M11", hook_type="curiosity-choice", url="https://t/1",
             views_24h=8200, views_7d=15400, likes=1120, comments=240, shares=95, saves=980,
             follows_delta=63, gmv=0, notes="launch card 3-choice"),
        _row(post_id="L1-D02", posted_at=(TODAY - timedelta(days=4)).isoformat(), content_pillar="C1",
             theme="Future-tech", media="M1", funnel_stage="Hygiene", hook_type="statement",
             url="https://t/2", views_24h=1200, notes="ท่านท้าวเวสฯ cyber; homage-watch 24h"),
        _row(post_id="L1-D03", posted_at=(TODAY - timedelta(days=1)).isoformat(), content_pillar="C9",
             theme="Contemporary", media="M6", hook_type="question", url="https://t/3",
             notes="voice test"),
    ]
    conn.executemany(INSERT, rows)
    conn.commit()
    return conn


@pytest.fixture()
def account():
    """Real config/account.yaml, sprint_start pinned so today == day 7."""
    acc = load_account()
    return acc.model_copy(update={"sprint_start": (TODAY - timedelta(days=6)).isoformat()})


@pytest.fixture()
def engine(tmp_path):
    cfg = EngineConfig()
    cfg.root = tmp_path
    return cfg


def _mark_reviewed(engine, *weeks: int) -> None:
    for w in weeks:
        p = review_path(engine, w)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"W{w} done", encoding="utf-8")


# ── TASK A — weekly_review ─────────────────────────────────────────────────


def test_weekly_review_renders_all_four_steps(conn3, account, engine):
    md = weekly_review(conn3, account, engine, week=1, today=TODAY)

    assert "## Step 1 — Top performer" in md
    assert "## Step 2 — Bottom performer" in md
    assert "## Step 3 — Pillar × hook rollup" in md
    assert "## Step 4 — Gate progress + compliance" in md
    # top performer is the only fully measured post
    assert "L1-D01" in md
    assert "15,400" in md


def test_weekly_review_says_not_measured_never_fakes(conn3, account, engine):
    md = weekly_review(conn3, account, engine, week=1, today=TODAY)

    assert NOT_MEASURED in md                       # NULL metrics are named, not imputed
    assert "วัดแล้ว 1" in md                          # 1 of 3 posts has views_7d
    assert "0.00%" not in md and "| 0 | 0 |" not in md   # never imputed as a measured zero
    # the unmeasured posts are excluded from the bottom ranking, not ranked as the worst
    assert "ไม่เอามาจัดอันดับเพราะยังไม่ได้วัด (not measured yet): `L1-D02`, `L1-D03`" in md


def test_weekly_review_gate_and_compliance_lines(conn3, account, engine):
    md = weekly_review(conn3, account, engine, week=1, today=TODAY)

    assert "day 7 / 90" in md
    assert "50,000" in md and "1,000" in md          # gate targets
    assert "AI label" in md and "ครบทุกโพสต์ (3)" in md
    assert "Homage-watch:** C1 ใน 7 วัน = 1 · มี note แล้ว 1 ✓" in md   # L1-D02 carries the note


def test_weekly_review_note_line_prefilled(conn3, account, engine):
    md = weekly_review(conn3, account, engine, week=1, today=TODAY)
    assert "W1: top=L1-D01, bottom=L1-D01, changing ____________ next week" in md


def test_weekly_review_reweight_suggestion(conn3, account, engine):
    md = weekly_review(conn3, account, engine, week=1, today=TODAY)
    assert "เพิ่มสัดส่วนสัปดาห์หน้า" in md
    assert "C2×curiosity-choice" in md
    assert "W2 = Historical" in md                   # feeds back into the aesthetic-week map


def test_weekly_review_empty_db_is_graceful(conn, account, engine):
    md = weekly_review(conn, account, engine, week=1, today=TODAY)

    assert "## Step 4" in md
    assert "ยังไม่มีโพสต์ในหน้าต่าง 7 วัน" in md
    assert "ยังไม่มีข้อมูลใน 28 วัน" in md
    assert NOT_MEASURED in md
    assert "W1: top=—, bottom=—" in md               # no fake ids


def test_weekly_review_matches_on_the_standalone_sql_fallback(conn3, account, engine, monkeypatch):
    """review.py must render the same report without db.py (the §5 SQL fallback)."""
    with_db = weekly_review(conn3, account, engine, week=1, today=TODAY)
    monkeypatch.setattr(review, "_db_fn", lambda name: None)
    without_db = weekly_review(conn3, account, engine, week=1, today=TODAY)

    for marker in ("L1-D01", "15,400", "W1: top=L1-D01", "day 7 / 90", NOT_MEASURED):
        assert marker in without_db
    assert without_db.splitlines()[:6] == with_db.splitlines()[:6]


def test_write_review_lands_in_out_reviews(conn3, account, engine):
    md = weekly_review(conn3, account, engine, week=2, today=TODAY)
    p = write_review(md, engine, 2)

    assert p == engine.resolve("./out/reviews") / "W2.md"
    assert p.read_text(encoding="utf-8") == md


# ── heuristics (pure functions) ────────────────────────────────────────────


def test_diagnose_low_views_24h_is_weak_hook():
    row = {"views_24h": 500, "views_7d": 900, "saves": 5}
    med = {"views_24h": 5000.0, "tail_multiple": 3.0, "save_rate": 0.05}
    out = " ".join(diagnose(row, med))
    assert "hook อ่อน" in out
    assert "algo ไม่รับต่อ" in out                     # tail 1.8 < 3.0
    assert "aesthetic/คุณค่าไม่พอ" in out              # save_rate 0.0056 < 0.05


def test_diagnose_unmeasured_row_gets_no_fake_diagnosis():
    out = diagnose({"views_24h": None, "views_7d": None}, {"views_24h": 1.0})
    assert len(out) == 1 and NOT_MEASURED in out[0]


def test_diagnose_above_median_says_nothing_is_low():
    row = {"views_24h": 9000, "views_7d": 30000, "saves": 3000}
    med = {"views_24h": 5000.0, "tail_multiple": 2.0, "save_rate": 0.05}
    assert "ไม่มีตัวชี้วัดไหนต่ำกว่า median" in " ".join(diagnose(row, med))


def test_reweight_splits_around_the_median():
    rollup = [
        {"content_pillar": "C2", "hook_type": "curiosity-choice", "n": 5, "avg_views": 12000, "avg_save_rate": 0.060},
        {"content_pillar": "C1", "hook_type": "statement", "n": 3, "avg_views": 9000, "avg_save_rate": 0.005},
        {"content_pillar": "C6", "hook_type": "list-promise", "n": 4, "avg_views": 400, "avg_save_rate": 0.080},
        {"content_pillar": "C9", "hook_type": "question", "n": 2, "avg_views": 300, "avg_save_rate": 0.001},
    ]
    b = reweight(rollup)                                            # medians: 4700 views · 0.0325 save
    assert [r["content_pillar"] for r in b["increase"]] == ["C2"]   # above both
    assert [r["content_pillar"] for r in b["rest"]] == ["C9"]       # below both
    assert [r["content_pillar"] for r in b["keep"]] == ["C1", "C6"]  # mixed signal, leave the weight alone


def test_reweight_keeps_pairs_with_no_numbers():
    b = reweight([{"content_pillar": "C1", "hook_type": "statement", "n": 1, "avg_views": None,
                   "avg_save_rate": None}])
    assert len(b["keep"]) == 1 and not b["increase"] and not b["rest"]


# ── gate math ──────────────────────────────────────────────────────────────


def test_gate_math_progress_and_pace(account):
    g = gate_math(account.gate, day=7, best_views=15400, followers_gained=63)
    assert g["views_pct"] == 30.8 and g["best_views_gap"] == 34600
    assert g["followers_pct"] == 6.3 and g["followers_gap"] == 937
    assert g["elapsed_pct"] == 7.8 and g["days_left"] == 83
    assert g["progress_pct"] == 30.8                # gate is OR -> the better arm counts
    assert g["pace_pct"] == 395 and g["on_track"] is True


def test_gate_math_behind_schedule(account):
    g = gate_math(account.gate, day=45, best_views=1000, followers_gained=50)
    assert g["progress_pct"] == 5.0 and g["elapsed_pct"] == 50.0
    assert g["on_track"] is False


def test_gate_math_unmeasured_is_none_not_zero(account):
    g = gate_math(account.gate, day=7, best_views=None, followers_gained=None)
    assert g["views_pct"] is None and g["followers_pct"] is None
    assert g["progress_pct"] is None and g["on_track"] is None and g["pace_pct"] is None


def test_sprint_day_and_week_of_day(account):
    assert sprint_day(account, TODAY) == 7
    assert sprint_day(account, TODAY + timedelta(days=1)) == 8
    assert [week_of_day(d) for d in (1, 7, 8, 14, 28)] == [1, 1, 2, 2, 4]


# ── TASK B — status ────────────────────────────────────────────────────────


def test_status_summary_core_numbers(conn3, account, engine):
    _mark_reviewed(engine, 1)
    d = status_summary(conn3, account, engine, set(), TODAY)

    assert d["day"] == 7 and d["days_left"] == 83
    assert d["posts_published"] == 3
    assert d["best_views"] == 15400 and d["best_views_post_id"] == "L1-D01"
    assert d["best_views_24h"] == 8200
    assert d["followers_gained"] == 63
    assert d["gate"]["on_track"] is True
    assert d["next_review_day"] == 14 and d["next_review_week"] == 2
    assert d["packets_source"] == "none" and d["packets_total"] == 0
    assert d["ai_label_ok"] is True


def test_status_next_action_review_due(conn3, account, engine):
    d = status_summary(conn3, account, engine, set(), TODAY)      # no W1.md written
    assert d["next_action"] == "review week 1 due"
    assert d["reviews_due"] == [7]


def test_status_next_action_blocked_beats_the_rest(conn3, account, engine):
    _mark_reviewed(engine, 1)
    _write_packet(engine, "L1-D05", "blocked")
    d = status_summary(conn3, account, engine, set(), TODAY)
    assert d["next_action"] == "fix caption + re-run packet L1-D05 (blocked)"
    assert d["packets_source"] == "out" and d["packets"]["blocked"] == 1


def test_status_next_action_log_url(conn3, account, engine):
    _mark_reviewed(engine, 1)
    _write_packet(engine, "L1-D07", "approved")
    d = status_summary(conn3, account, engine, set(), TODAY)
    assert d["next_action"] == "log L1-D07 url"
    assert d["unlogged_ids"] == []                                # approved is not yet 'published'


def test_status_next_action_log_url_from_published_ids(conn, account, engine):
    _mark_reviewed(engine, 1)
    d = status_summary(conn, account, engine, {"L1-D06", "L1-D07"}, TODAY)
    assert d["next_action"] == "log L1-D06 url (+1 more)"
    assert d["unlogged_ids"] == ["L1-D06", "L1-D07"]


def test_status_next_action_update_24h_metrics(conn3, account, engine):
    _mark_reviewed(engine, 1)
    d = status_summary(conn3, account, engine, set(), TODAY)
    assert d["next_action"] == "update 24h metrics for L1-D03"    # posted yesterday, still NULL


def test_status_next_action_approve_then_generate(conn, account, engine):
    _mark_reviewed(engine, 1)
    _write_packet(engine, "L1-D07", "draft")
    d = status_summary(conn, account, engine, set(), TODAY)
    assert d["next_action"] == "approve L1-D07"
    assert "generate day 7" not in " ".join(d["pending_actions"])  # today's packet already exists


def test_status_next_action_generate_today(conn, account, engine):
    _mark_reviewed(engine, 1)
    d = status_summary(conn, account, engine, set(), TODAY)
    assert d["next_action"] == "generate day 7 (L1-D07)"


def test_status_next_action_7d_metrics(conn, account, engine):
    acc = load_account().model_copy(update={"sprint_start": (TODAY - timedelta(days=13)).isoformat()})
    conn.execute(INSERT, _row(post_id="L2-D08", posted_at=(TODAY - timedelta(days=8)).isoformat(),
                              views_24h=900, notes="old"))
    conn.commit()
    _mark_reviewed(engine, 1, 2)
    _write_packet(engine, "L2-D14", "generated")
    d = status_summary(conn, acc, engine, set(), TODAY)
    assert d["day"] == 14
    assert d["next_action"] == "update 7d metrics for L2-D08"


def test_status_next_action_all_caught_up(conn, account, engine):
    _mark_reviewed(engine, 1)
    conn.execute(INSERT, _row(post_id="L1-D07", posted_at=TODAY.isoformat(), views_24h=10,
                              views_7d=20, saves=1, follows_delta=1))
    conn.commit()
    _write_packet(engine, "L1-D07", "published")
    d = status_summary(conn, account, engine, set(), TODAY)
    assert d["next_action"] == "all caught up — day 7: ไม่มีอะไรค้าง"


def test_status_before_sprint_start(conn, account, engine):
    acc = account.model_copy(update={"sprint_start": (TODAY + timedelta(days=3)).isoformat()})
    d = status_summary(conn, acc, engine, set(), TODAY)
    assert d["day"] == -2
    assert d["next_action"].startswith("sprint starts")


def test_status_reads_packets_table_when_present(conn3, account, engine):
    db.upsert_packet_status(conn3, "L1-D01", "own", "published")
    db.upsert_packet_status(conn3, "L1-D07", "own", "draft")
    _write_packet(engine, "L1-D09", "blocked")            # disk is ignored once the db has rows
    _mark_reviewed(engine, 1)
    d = status_summary(conn3, account, engine, set(), TODAY)
    assert d["packets_source"] == "db"
    assert d["packets"]["published"] == 1 and d["packets"]["draft"] == 1
    assert d["packets"]["blocked"] == 0


def test_status_skips_unreadable_meta_json(conn, account, engine):
    _mark_reviewed(engine, 1)
    bad = engine.resolve("./out") / "L1-D09"
    bad.mkdir(parents=True, exist_ok=True)
    (bad / "meta.json").write_text("{not json", encoding="utf-8")
    _write_packet(engine, "L1-D07", "generated")
    d = status_summary(conn, account, engine, set(), TODAY)
    assert d["packets_total"] == 1 and d["packets"]["generated"] == 1


def test_next_review_day_extrapolates_past_the_configured_list():
    days = [7, 14, 21, 28]
    assert next_review_day(1, days) == 7
    assert next_review_day(7, days) == 7
    assert next_review_day(8, days) == 14
    assert next_review_day(30, days) == 35
    assert next_review_day(90, days) == 91


def test_render_status_is_one_screen(conn3, account, engine):
    _mark_reviewed(engine, 1)
    d = status_summary(conn3, account, engine, set(), TODAY)
    txt = render_status(d)

    assert "day 7/90" in txt
    assert "best views (7d): 15,400 (L1-D01)" in txt
    assert "ON TRACK" in txt
    assert "→ NEXT: update 24h metrics for L1-D03" in txt
    assert txt.count("\n") <= 8


def test_render_status_empty_db_shows_not_measured(conn, account, engine):
    d = status_summary(conn, account, engine, set(), TODAY)
    txt = render_status(d)
    assert NOT_MEASURED in txt
    assert "posts logged: 0" in txt
    assert "→ NEXT: review week 1 due" in txt


def _write_packet(engine, post_id: str, status: str) -> None:
    d = engine.resolve("./out") / post_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "meta.json").write_text(json.dumps({"post_id": post_id, "status": status}), encoding="utf-8")
