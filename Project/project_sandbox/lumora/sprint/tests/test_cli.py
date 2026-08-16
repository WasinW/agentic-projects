"""CLI tests — the full sprint loop end-to-end in a tmp dir, stub generator, no API keys.

Everything runs in-process through ``main(argv)`` so the tests exercise the real argparse surface
and the real exit codes without paying for a subprocess per step (and without depending on the
venv's editable install, which macOS's UF_HIDDEN flag keeps breaking).

The sandbox is a full copy of ``config/`` + ``batch/`` under ``tmp_path``: because
``load_engine`` sets ``EngineConfig.root`` to the config dir's parent, every relative path in
``engine.yaml`` (db, out, events, reviews) lands inside ``tmp_path`` automatically. The copied
``engine.yaml`` is rewritten to force ``generator.provider: stub`` and ``llm.enabled: false`` so no
test can ever reach Replicate or Anthropic, and ``account.yaml``'s ``sprint_start`` is pinned to
today so day/week math is deterministic.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
from datetime import date
from pathlib import Path

import pytest
import yaml

from lumora_sprint.cli import EXIT_ERROR, EXIT_NEEDS_HUMAN, EXIT_OK, HANDLERS, main
from lumora_sprint.events import read_events
from lumora_sprint.models import PacketStatus

SPRINT_ROOT = Path(__file__).resolve().parents[1]
TODAY = date.today()  # noqa: DTZ011 - the sprint counts local calendar days, same as cli.py
POST_URL = "https://tiktok.com/x"


# ── sandbox fixture ────────────────────────────────────────────────────────


@pytest.fixture
def sandbox(tmp_path: Path) -> Path:
    """A self-contained sprint root under tmp_path: config/ + batch/, offline generator + no LLM."""
    shutil.copytree(SPRINT_ROOT / "config", tmp_path / "config")
    shutil.copytree(SPRINT_ROOT / "batch", tmp_path / "batch")

    engine_path = tmp_path / "config" / "engine.yaml"
    engine = yaml.safe_load(engine_path.read_text(encoding="utf-8"))
    engine["generator"]["provider"] = "stub"          # never call Replicate from a test
    engine["llm"]["enabled"] = False                  # never call Anthropic from a test
    engine["paths"] = {
        "db": "./lumora_sprint.db",
        "batch_dir": "./batch",
        "out_dir": "./out",
        "events_log": "./out/agent_events.jsonl",
        "reviews_dir": "./out/reviews",
    }
    engine_path.write_text(yaml.safe_dump(engine, allow_unicode=True, sort_keys=False), encoding="utf-8")

    account_path = tmp_path / "config" / "account.yaml"
    account = yaml.safe_load(account_path.read_text(encoding="utf-8"))
    account["sprint_start"] = TODAY.isoformat()        # day 1 = today, so review/status are meaningful
    account_path.write_text(yaml.safe_dump(account, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return tmp_path


def run(sandbox: Path, *argv: str) -> int:
    """Invoke the CLI exactly as the console script would, against the sandbox config."""
    return main(["--config-dir", str(sandbox / "config"), *argv])


def db_rows(sandbox: Path, sql: str, params: tuple = ()) -> list[dict]:
    conn = sqlite3.connect(sandbox / "lumora_sprint.db")
    try:
        cur = conn.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r, strict=True)) for r in cur.fetchall()]
    finally:
        conn.close()


def meta(sandbox: Path, post_id: str) -> dict:
    return json.loads((sandbox / "out" / post_id / "meta.json").read_text(encoding="utf-8"))


# ── the full loop ──────────────────────────────────────────────────────────


def test_full_loop_day1(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """init → plan → generate → packet → approve → log → metrics ×2 → review → status → next."""
    assert run(sandbox, "init") == EXIT_OK
    out = capsys.readouterr().out
    assert "@มูมีแสง" in out
    assert "30 posts" in out
    assert (sandbox / "lumora_sprint.db").is_file()

    # plan --------------------------------------------------------------
    assert run(sandbox, "plan", "--day", "1") == EXIT_OK
    out = capsys.readouterr().out
    assert "L1-D01" in out
    assert "C2 × Cosmic × M11" in out                      # combo
    assert "curiosity-choice" in out                        # hook_type is a fixed tag
    assert "การ์ดใบแรกของช่องนี้" in out                      # caption preview
    assert "oracle cards floating" in out                   # image prompt
    assert db_rows(sandbox, "SELECT status FROM packets WHERE post_id='L1-D01'") == [
        {"status": PacketStatus.planned.value}
    ]

    # generate ----------------------------------------------------------
    assert run(sandbox, "generate", "--day", "1") == EXIT_OK
    out = capsys.readouterr().out
    assert "[stub/stub]" in out
    image = sandbox / "out" / "L1-D01" / "image_1.png"
    assert image.is_file() and image.stat().st_size > 0
    assert meta(sandbox, "L1-D01")["status"] == PacketStatus.generated.value

    # packet ------------------------------------------------------------
    assert run(sandbox, "packet", "--day", "1", "--no-llm") == EXIT_OK
    out = capsys.readouterr().out
    assert "0 block" in out
    assert "llm_qa_skipped" in out                          # honest: QA did not run
    pdir = sandbox / "out" / "L1-D01"
    for name in ("meta.json", "caption.txt", "hashtags.txt", "checklist.md"):
        assert (pdir / name).is_file()
    assert meta(sandbox, "L1-D01")["status"] == PacketStatus.draft.value

    # approve (human gate) ----------------------------------------------
    assert run(sandbox, "approve", "L1-D01") == EXIT_OK
    out = capsys.readouterr().out
    assert "checklist.md" in out
    assert "upload BY HAND" in out
    assert meta(sandbox, "L1-D01")["status"] == PacketStatus.approved.value

    # log ---------------------------------------------------------------
    assert run(sandbox, "log", "L1-D01", "--url", POST_URL) == EXIT_OK
    out = capsys.readouterr().out
    assert POST_URL in out
    row = db_rows(sandbox, "SELECT * FROM post_log WHERE post_id='L1-D01'")[0]
    assert row["brand_id"] == "own"
    assert (row["content_pillar"], row["theme"], row["media"]) == ("C2", "Cosmic", "M11")
    assert row["funnel_stage"] == "Hub"
    assert row["hook_type"] == "curiosity-choice"
    assert row["ai_labeled"] == 1
    assert row["url"] == POST_URL
    assert row["posted_at"] == TODAY.isoformat()
    assert row["agent"] == "lumora-sprint"
    assert row["prompt_version"] == "2026-07-w1"            # batch_id
    assert row["gen_model"] == "stub"
    assert row["cost_usd"] == 0.0
    assert row["views_24h"] is None                          # empty beats fake
    assert meta(sandbox, "L1-D01")["status"] == PacketStatus.published.value

    # metrics (partial, twice) -------------------------------------------
    assert run(sandbox, "metrics", "L1-D01", "--views-24h", "100") == EXIT_OK
    row = db_rows(sandbox, "SELECT * FROM post_log WHERE post_id='L1-D01'")[0]
    assert row["views_24h"] == 100
    assert row["views_7d"] is None and row["saves"] is None  # untouched columns stay NULL

    assert run(
        sandbox, "metrics", "L1-D01",
        "--views-7d", "500", "--saves", "30", "--follows-delta", "3",
    ) == EXIT_OK
    row = db_rows(sandbox, "SELECT * FROM post_log WHERE post_id='L1-D01'")[0]
    assert (row["views_24h"], row["views_7d"], row["saves"], row["follows_delta"]) == (100, 500, 30, 3)
    assert row["likes"] is None and row["comments"] is None

    # review -------------------------------------------------------------
    capsys.readouterr()
    assert run(sandbox, "review", "--week", "1") == EXIT_OK
    out = capsys.readouterr().out
    review_md = sandbox / "out" / "reviews" / "W1.md"
    assert review_md.is_file()
    assert "# W1" in out
    assert "L1-D01" in review_md.read_text(encoding="utf-8")

    # status -------------------------------------------------------------
    assert run(sandbox, "status") == EXIT_OK
    out = capsys.readouterr().out
    assert "day 1/90" in out
    assert "posts logged: 1" in out
    assert "published 1" in out
    assert "NEXT:" in out

    # next ---------------------------------------------------------------
    assert run(sandbox, "next") == EXIT_OK
    out = capsys.readouterr().out
    assert out.startswith("next: L1-D02")
    assert "C1 × Future-tech × M1" in out

    # accountability log --------------------------------------------------
    events = read_events(sandbox / "out" / "agent_events.jsonl")
    steps = [e.step for e in events]
    assert steps == [
        "init", "plan", "generate", "packet", "approve", "log",
        "metrics", "metrics", "review", "status", "next",
    ]
    assert all(e.ok for e in events)
    assert all(e.agent == "lumora-sprint" for e in events)
    assert {e.post_id for e in events if e.step in {"plan", "generate", "packet", "approve", "log"}} == {
        "L1-D01"
    }
    gen = next(e for e in events if e.step == "generate")
    assert gen.model == "stub" and gen.prompt_version == "2026-07-w1" and gen.duration_s >= 0


# ── individual commands / edge cases ───────────────────────────────────────


def test_no_command_prints_help(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(sandbox) == EXIT_ERROR
    assert "usage: lumora" in capsys.readouterr().out


def test_there_is_no_publish_command() -> None:
    """ADR-0001 rule 5 as a test: the CLI must never grow a publisher or a scheduler."""
    commands = set(HANDLERS)
    assert commands == {
        "init", "plan", "generate", "packet", "approve", "caption",
        "log", "metrics", "review", "status", "next", "run",
    }
    assert not commands & {"publish", "post", "schedule", "upload", "cron"}


def test_unknown_subcommand_exits_via_argparse(sandbox: Path) -> None:
    with pytest.raises(SystemExit):
        run(sandbox, "publish", "L1-D01")


def test_missing_config_dir_errors(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--config-dir", str(tmp_path / "nope"), "init"]) == EXIT_ERROR
    assert "account.yaml" in capsys.readouterr().err


def test_db_override(sandbox: Path) -> None:
    alt = sandbox / "alt" / "other.db"
    assert main(["--config-dir", str(sandbox / "config"), "--db", str(alt), "init"]) == EXIT_OK
    assert alt.is_file()
    assert not (sandbox / "lumora_sprint.db").exists()


def test_db_override_with_a_relative_path_resolves_against_cwd(
    sandbox: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A flag is a path the user typed in their shell — not one of engine.yaml's sprint-root paths."""
    here = tmp_path / "elsewhere"
    here.mkdir()
    monkeypatch.chdir(here)

    assert main(["--config-dir", str(sandbox / "config"), "--db", "./scratch.db", "init"]) == EXIT_OK
    assert (here / "scratch.db").is_file()
    assert not (sandbox / "scratch.db").exists()


def test_plan_requires_a_target(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(sandbox, "plan") == EXIT_ERROR
    assert "--day" in capsys.readouterr().err


def test_unknown_post_id_is_an_error(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(sandbox, "plan", "--post-id", "L9-D99") == EXIT_ERROR
    assert "no post matching" in capsys.readouterr().err


def test_plan_outline_row_prints_hint_and_exits_2(
    sandbox: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Day 8 is an outline row: the tool prepares the ask for the skill, it never fills it in."""
    assert run(sandbox, "plan", "--day", "8") == EXIT_NEEDS_HUMAN
    out = capsys.readouterr().out
    assert "/lumora-content-batch" in out
    assert "L2-D08" in out
    assert "full_spec: true" in out


def test_generate_outline_row_exits_2_without_calling_the_generator(sandbox: Path) -> None:
    assert run(sandbox, "generate", "--day", "8") == EXIT_NEEDS_HUMAN
    assert not (sandbox / "out" / "L2-D08").exists()


def test_plan_rejects_a_spec_that_fails_the_validity_gate(
    sandbox: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """L4-D29 (Hero) is C2 × Historical × M2 — illegal media and the wrong oracle theme."""
    assert run(sandbox, "plan", "--day", "29") == EXIT_ERROR
    out = capsys.readouterr().out
    assert "media M2 not allowed for C2" in out
    assert "oracle theme" in out


def test_generate_is_idempotent_and_force_regenerates(
    sandbox: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(sandbox, "generate", "--day", "1") == EXIT_OK
    image = sandbox / "out" / "L1-D01" / "image_1.png"
    first = image.read_bytes()
    capsys.readouterr()

    assert run(sandbox, "generate", "--day", "1") == EXIT_OK
    assert "skip" in capsys.readouterr().out
    assert image.read_bytes() == first

    assert run(sandbox, "generate", "--day", "1", "--force") == EXIT_OK
    assert "[stub/stub]" in capsys.readouterr().out
    assert image.is_file()


def test_generate_skip_keeps_approval_but_force_invalidates_it(
    sandbox: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Re-generating changes the pixels, so it must reset the human gate; skipping must not."""
    run(sandbox, "run", "--day", "1", "--no-llm")
    run(sandbox, "approve", "L1-D01")
    capsys.readouterr()

    assert run(sandbox, "generate", "--day", "1") == EXIT_OK
    assert "ไม่เปลี่ยน" in capsys.readouterr().out
    assert meta(sandbox, "L1-D01")["status"] == PacketStatus.approved.value

    assert run(sandbox, "generate", "--day", "1", "--force") == EXIT_OK
    capsys.readouterr()
    assert meta(sandbox, "L1-D01")["status"] == PacketStatus.generated.value
    assert db_rows(sandbox, "SELECT status FROM packets WHERE post_id='L1-D01'") == [
        {"status": PacketStatus.generated.value}
    ]


def test_fatigue_history_comes_from_the_plan_not_post_log(sandbox: Path) -> None:
    """`fatigue_check` is positional: recent[0] must be the post right before spec, published or not.

    Feeding it post_log (published posts only) made the gate a no-op on a fresh sprint and, once a
    few posts were logged, a *wrong* comparison — planning day 5 while only days 1-2 were logged
    compared day 5's combo against day 2's.
    """
    from lumora_sprint.batch import find_post
    from lumora_sprint.cli import _load_ctx, _recent_combos

    args = argparse.Namespace(config_dir=str(sandbox / "config"), db=None)
    ctx = _load_ctx(args)
    try:
        spec5 = find_post(ctx.batches(), 5)
        assert _recent_combos(ctx, spec5, 3) == [                # days 4, 3, 2 — newest first
            ("C9", "Contemporary", "M1"),
            ("C2", "Cosmic", "M1"),
            ("C1", "Future-tech", "M1"),
        ]
        assert _recent_combos(ctx, find_post(ctx.batches(), 1), 3) == []   # nothing precedes day 1
    finally:
        ctx.close()


def test_fatigue_warns_on_a_repeat_before_anything_is_published(
    sandbox: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """End to end: a batch that repeats a non-exempt C+M must trip the gate with an empty post_log."""
    (sandbox / "batch" / "2026-07-w5.yaml").write_text(
        yaml.safe_dump(
            {
                "batch_id": "2026-07-w5",
                "account_handle": "@มูมีแสง",
                "posts": [
                    {"post_id": f"L5-D{d}", "day": d, "week": 5, "content_pillar": "C1",
                     "theme": "Future-tech", "media": "M1", "hook_type": "statement",
                     "caption": "x", "hashtags": ["#x"], "ai_visual": False, "full_spec": True}
                    for d in (31, 32)
                ],
            },
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    assert run(sandbox, "init") == EXIT_OK
    capsys.readouterr()
    assert db_rows(sandbox, "SELECT * FROM post_log") == []       # the old blind spot

    assert run(sandbox, "plan", "--day", "32") == EXIT_OK
    out = capsys.readouterr().out
    assert "⚠️" in out
    assert "same C+M as the previous post (C1+M1)" in out
    assert "C1 x Future-tech x M1 already used" in out


def test_fatigue_gate_is_exempt_for_the_oracle_anchor(
    sandbox: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """C2 is in engine.yaml's exempt_pillars — a daily ritual in a fixed look is the point.

    Day 5 repeats day 1's C2×Cosmic×M11 exactly and must still pass.
    """
    assert run(sandbox, "plan", "--day", "5") == EXIT_OK
    assert "✅ ไม่ซ้ำ" in capsys.readouterr().out


def test_packet_blocked_by_banned_phrase_exits_2(
    sandbox: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """L1-D04's verbatim caption contains 'หายป่วย' — the gate blocks it until Sin rewords."""
    assert run(sandbox, "packet", "--day", "4", "--no-llm") == EXIT_NEEDS_HUMAN
    out = capsys.readouterr().out
    assert "banned_phrase" in out
    assert "1 block" in out
    assert meta(sandbox, "L1-D04")["status"] == PacketStatus.blocked.value
    assert db_rows(sandbox, "SELECT status FROM packets WHERE post_id='L1-D04'") == [
        {"status": PacketStatus.blocked.value}
    ]


def test_approve_refuses_a_blocked_packet(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run(sandbox, "packet", "--day", "4", "--no-llm")
    capsys.readouterr()
    assert run(sandbox, "approve", "L1-D04") == EXIT_NEEDS_HUMAN
    assert "block" in capsys.readouterr().err
    assert meta(sandbox, "L1-D04")["status"] == PacketStatus.blocked.value


def test_approve_without_a_packet_errors(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(sandbox, "approve", "L1-D01") == EXIT_ERROR
    assert "packet" in capsys.readouterr().err


def test_log_requires_an_approved_packet(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run(sandbox, "run", "--day", "1", "--no-llm")
    capsys.readouterr()
    assert run(sandbox, "log", "L1-D01", "--url", POST_URL) == EXIT_NEEDS_HUMAN
    assert "approve" in capsys.readouterr().err
    assert db_rows(sandbox, "SELECT * FROM post_log") == []


def test_log_accepts_posted_at_and_notes(sandbox: Path) -> None:
    run(sandbox, "run", "--day", "1", "--no-llm")
    run(sandbox, "approve", "L1-D01")
    assert run(
        sandbox, "log", "L1-D01", "--url", POST_URL,
        "--posted-at", "2026-08-01", "--notes", "launch post",
    ) == EXIT_OK
    row = db_rows(sandbox, "SELECT * FROM post_log WHERE post_id='L1-D01'")[0]
    assert row["posted_at"] == "2026-08-01"
    assert row["notes"] == "launch post"


def test_log_rejects_a_bad_date(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run(sandbox, "run", "--day", "1", "--no-llm")
    run(sandbox, "approve", "L1-D01")
    capsys.readouterr()
    assert run(sandbox, "log", "L1-D01", "--url", POST_URL, "--posted-at", "01/08/2026") == EXIT_ERROR
    assert "YYYY-MM-DD" in capsys.readouterr().err


def test_metrics_needs_at_least_one_value(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(sandbox, "metrics", "L1-D01") == EXIT_ERROR
    assert "ไม่มีค่าอะไรให้บันทึก" in capsys.readouterr().err


def test_metrics_on_an_unlogged_post_errors(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(sandbox, "metrics", "L1-D01", "--views-24h", "10") == EXIT_ERROR
    assert "post_log" in capsys.readouterr().err


def test_run_does_plan_generate_packet_and_stops_before_approve(
    sandbox: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(sandbox, "run", "--day", "1", "--no-llm") == EXIT_OK
    out = capsys.readouterr().out
    assert "plan L1-D01" in out
    assert "generate L1-D01" in out
    assert "packet L1-D01" in out
    assert "approve L1-D01" in out                       # as an instruction, not an action
    assert meta(sandbox, "L1-D01")["status"] == PacketStatus.draft.value
    steps = [e.step for e in read_events(sandbox / "out" / "agent_events.jsonl")]
    assert steps == ["plan", "generate", "packet", "run"]


def test_run_stops_at_a_blocked_packet(sandbox: Path) -> None:
    assert run(sandbox, "run", "--day", "4", "--no-llm") == EXIT_NEEDS_HUMAN
    assert meta(sandbox, "L1-D04")["status"] == PacketStatus.blocked.value


def test_run_stops_on_an_outline_row_before_generating(sandbox: Path) -> None:
    assert run(sandbox, "run", "--day", "8") == EXIT_NEEDS_HUMAN
    steps = [e.step for e in read_events(sandbox / "out" / "agent_events.jsonl")]
    assert steps == ["plan", "run"]                       # generate never ran


def test_replan_does_not_walk_an_approved_packet_backwards(
    sandbox: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    run(sandbox, "run", "--day", "1", "--no-llm")
    run(sandbox, "approve", "L1-D01")
    capsys.readouterr()
    assert run(sandbox, "plan", "--day", "1") == EXIT_OK
    assert "approved" in capsys.readouterr().out
    assert db_rows(sandbox, "SELECT status FROM packets WHERE post_id='L1-D01'") == [
        {"status": PacketStatus.approved.value}
    ]


def test_next_and_status_on_an_empty_sprint(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(sandbox, "next") == EXIT_OK
    assert capsys.readouterr().out.startswith("next: L1-D01")
    assert run(sandbox, "status") == EXIT_OK
    out = capsys.readouterr().out
    assert "posts logged: 0" in out
    assert "—" in out                                     # never measured, never faked


def test_next_reports_all_posted_when_the_batch_is_done(sandbox: Path, capsys: pytest.CaptureFixture[str]) -> None:
    run(sandbox, "init")
    every_id = [
        (p["post_id"],)
        for f in sorted((sandbox / "batch").glob("*.yaml"))
        for p in yaml.safe_load(f.read_text(encoding="utf-8"))["posts"]
    ]
    assert len(every_id) == 30
    conn = sqlite3.connect(sandbox / "lumora_sprint.db")
    with conn:
        conn.executemany(
            "INSERT INTO packets (post_id, brand_id, status) VALUES (?, 'own', 'published')",
            every_id,
        )
    conn.close()
    capsys.readouterr()
    assert run(sandbox, "next") == EXIT_OK
    assert "all posted" in capsys.readouterr().out


def test_review_defaults_to_the_current_sprint_week(sandbox: Path) -> None:
    assert run(sandbox, "review") == EXIT_OK
    assert (sandbox / "out" / "reviews" / "W1.md").is_file()


def test_failures_are_recorded_in_the_event_log(sandbox: Path) -> None:
    """The accountability log records what went wrong too — that is the point of it."""
    assert run(sandbox, "plan", "--post-id", "L9-D99") == EXIT_ERROR
    events = read_events(sandbox / "out" / "agent_events.jsonl")
    assert len(events) == 1
    assert events[0].step == "plan"
    assert events[0].ok is False
    assert "no post matching" in events[0].detail


def test_no_network_adapters_are_touched_with_the_stub_provider(sandbox: Path) -> None:
    """The offline loop must not import replicate or construct an Anthropic client."""
    import sys as _sys

    for mod in ("replicate", "anthropic"):
        _sys.modules.pop(mod, None)
    assert run(sandbox, "run", "--day", "1", "--no-llm") == EXIT_OK
    assert "replicate" not in _sys.modules
