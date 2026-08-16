"""End-to-end smoke tests — the gaps left by the per-module suites, plus the defects found in review.

``tests/test_cli.py`` already drives day 1 through ``main(argv)``. This file adds what nobody pins
yet: the multi-day loop (two independent ``post_log`` rows + the derived ``v_post_scores`` columns),
the packet folder as an actual *artefact* (a decodable 1080x1920 PNG, a paste-ready ``caption.txt``),
and an architectural guard that the only two outbound adapters stay where ADR-0001 put them.

The second half is the defect ledger: one test per bug found in review, each stating the behaviour
the loop must have. They were written as ``xfail(strict=True)`` while the bugs were live; the
markers came off when the fixes landed, and these are now ordinary regression tests.

Sandboxing follows test_cli.py: ``config/`` + ``batch/`` are copied under ``tmp_path`` and
``engine.yaml`` is rewritten to ``generator.provider: stub`` + ``llm.enabled: false``, so no test can
reach Replicate or Anthropic. ``sprint_start`` is pinned per test because the day/week math (and one
of the defects) depends on it.
"""
from __future__ import annotations

import json
import re
import shutil
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import pytest
import yaml
from PIL import Image

from lumora_sprint.cli import EXIT_NEEDS_HUMAN, EXIT_OK, main
from lumora_sprint.events import read_events
from lumora_sprint.models import PacketStatus

SPRINT_ROOT = Path(__file__).resolve().parents[1]
TODAY = date.today()  # noqa: DTZ011 - the sprint counts local calendar days, same as cli.py
URL1 = "https://www.tiktok.com/@mumeesang/video/1"
URL2 = "https://www.tiktok.com/@mumeesang/video/2"

#: 9:16 at the stub's 1080px short edge — what actually gets uploaded.
PORTRAIT = (1080, 1920)


# ── sandbox ────────────────────────────────────────────────────────────────


def make_sandbox(tmp_path: Path, sprint_start: date) -> Path:
    """A self-contained sprint root under ``tmp_path``, offline generator, LLM off.

    Args:
        tmp_path: pytest's per-test directory; becomes ``EngineConfig.root``.
        sprint_start: written into account.yaml so day/week math is deterministic.
    """
    shutil.copytree(SPRINT_ROOT / "config", tmp_path / "config")
    shutil.copytree(SPRINT_ROOT / "batch", tmp_path / "batch")

    engine_path = tmp_path / "config" / "engine.yaml"
    engine = yaml.safe_load(engine_path.read_text(encoding="utf-8"))
    engine["generator"]["provider"] = "stub"
    engine["llm"]["enabled"] = False
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
    account["sprint_start"] = sprint_start.isoformat()
    account_path.write_text(yaml.safe_dump(account, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return tmp_path


@pytest.fixture
def sandbox(tmp_path: Path) -> Path:
    """Sprint root whose day 1 is today — the common case for the loop tests."""
    return make_sandbox(tmp_path, TODAY)


def run(sandbox: Path, *argv: str) -> int:
    """Invoke the CLI exactly as the console script would, against the sandbox config."""
    return main(["--config-dir", str(sandbox / "config"), *argv])


def rows(sandbox: Path, sql: str, params: tuple = ()) -> list[dict]:
    conn = sqlite3.connect(sandbox / "lumora_sprint.db")
    try:
        cur = conn.execute(sql, params)
        cols = [c[0] for c in cur.description]
        return [dict(zip(cols, r, strict=True)) for r in cur.fetchall()]
    finally:
        conn.close()


def meta_path(sandbox: Path, post_id: str) -> Path:
    return sandbox / "out" / post_id / "meta.json"


def meta(sandbox: Path, post_id: str) -> dict:
    return json.loads(meta_path(sandbox, post_id).read_text(encoding="utf-8"))


def publish(sandbox: Path, day: int, post_id: str, url: str) -> None:
    """run -> approve -> log: drive one post all the way to a post_log row."""
    assert run(sandbox, "run", "--day", str(day), "--no-llm") == EXIT_OK
    assert run(sandbox, "approve", post_id) == EXIT_OK
    assert run(sandbox, "log", post_id, "--url", url) == EXIT_OK


# ── artefacts on disk ──────────────────────────────────────────────────────


def test_generated_image_is_a_real_portrait_png(sandbox: Path) -> None:
    """The packet's image must be a decodable PNG at the post's real upload size, not just bytes."""
    assert run(sandbox, "generate", "--day", "1") == EXIT_OK
    img = sandbox / "out" / "L1-D01" / "image_1.png"

    assert img.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
    with Image.open(img) as im:
        im.load()
        assert im.format == "PNG"
        assert im.size == PORTRAIT

    recorded = meta(sandbox, "L1-D01")["images"]
    assert [i["provider"] for i in recorded] == ["stub"]
    assert [i["est_cost_usd"] for i in recorded] == [0.0]     # honest zero, never invented
    assert Path(recorded[0]["path"]) == img                    # provenance points at the real file


def test_caption_txt_is_paste_ready_and_agrees_with_hashtags_txt(sandbox: Path) -> None:
    """One copy of caption.txt = caption + blank line + hashtag line; hashtags.txt is the same line."""
    assert run(sandbox, "run", "--day", "1", "--no-llm") == EXIT_OK
    pdir = sandbox / "out" / "L1-D01"

    caption = (pdir / "caption.txt").read_text(encoding="utf-8")
    hashtags = (pdir / "hashtags.txt").read_text(encoding="utf-8").strip()
    body, _, tail = caption.rpartition("\n\n")

    assert body.startswith("การ์ดใบแรกของช่องนี้")           # Thai caption survives the round trip
    assert tail.strip() == hashtags
    assert hashtags.split() == meta(sandbox, "L1-D01")["spec"]["hashtags"]
    assert "#AIart" in hashtags                                # R-3.7 discoverability, from the batch

    checklist = (pdir / "checklist.md").read_text(encoding="utf-8")
    assert "AI label toggle: ON" in checklist                  # the human gate's whole point
    assert "lumora log L1-D01" in checklist


# ── multi-day loop ─────────────────────────────────────────────────────────


def test_two_day_loop_writes_two_independent_rows_and_derives_scores(sandbox: Path) -> None:
    """Days 1-2 end to end: two post_log rows, metrics on one, NULL (not 0) on the other."""
    publish(sandbox, 1, "L1-D01", URL1)
    publish(sandbox, 2, "L1-D02", URL2)

    assert run(sandbox, "metrics", "L1-D01", "--views-24h", "1200") == EXIT_OK
    assert run(
        sandbox, "metrics", "L1-D01",
        "--views-7d", "4300", "--likes", "300", "--comments", "40",
        "--shares", "12", "--saves", "210", "--follows-delta", "15",
    ) == EXIT_OK

    log = {r["post_id"]: r for r in rows(sandbox, "SELECT * FROM post_log")}
    assert set(log) == {"L1-D01", "L1-D02"}
    for r in log.values():
        assert r["brand_id"] == "own"
        assert r["ai_labeled"] == 1
        assert r["agent"] == "lumora-sprint"
        assert r["prompt_version"] == "2026-07-w1"
        assert r["gen_model"] == "stub"
    assert (log["L1-D01"]["content_pillar"], log["L1-D01"]["media"]) == ("C2", "M11")
    assert (log["L1-D02"]["content_pillar"], log["L1-D02"]["media"]) == ("C1", "M1")

    # empty beats fake: the post nobody measured keeps NULLs, it is not zero-filled
    assert log["L1-D02"]["views_7d"] is None
    assert log["L1-D02"]["saves"] is None

    scores = {r["post_id"]: r for r in rows(sandbox, "SELECT * FROM v_post_scores")}
    assert scores["L1-D01"]["save_rate"] == round(210 / 4300, 4)
    assert scores["L1-D01"]["follow_rate"] == round(15 / 4300, 4)
    assert scores["L1-D01"]["tail_multiple"] == round(4300 / 1200, 2)
    assert scores["L1-D02"]["save_rate"] is None

    # hook_type stayed a fixed tag on both rows (the FK is the enforcement, assert it holds)
    orphans = rows(
        sandbox,
        "SELECT p.post_id FROM post_log p LEFT JOIN hook_types h USING (hook_type) "
        "WHERE h.hook_type IS NULL",
    )
    assert orphans == []

    # one event per step, none silently dropped (`run` logs its 3 sub-steps plus itself)
    steps = [e.step for e in read_events(sandbox / "out" / "agent_events.jsonl")]
    assert steps == [
        "plan", "generate", "packet", "run", "approve", "log",
        "plan", "generate", "packet", "run", "approve", "log",
        "metrics", "metrics",
    ]


def test_weekly_review_renders_four_steps_from_the_live_loop(sandbox: Path) -> None:
    """The ritual file must come out of the same db the loop just filled, with all four steps."""
    publish(sandbox, 1, "L1-D01", URL1)
    assert run(sandbox, "metrics", "L1-D01", "--views-24h", "1200", "--views-7d", "4300",
               "--saves", "210", "--follows-delta", "15") == EXIT_OK

    assert run(sandbox, "review", "--week", "1") == EXIT_OK
    md = (sandbox / "out" / "reviews" / "W1.md").read_text(encoding="utf-8")

    for step in ("## Step 1", "## Step 2", "## Step 3", "## Step 4"):
        assert step in md
    assert "L1-D01" in md
    assert "4,300" in md
    assert "W1: top=L1-D01" in md            # the hand-written decision-trail line is pre-filled


# ── architecture guards ────────────────────────────────────────────────────


def test_outbound_adapters_stay_in_their_two_modules() -> None:
    """ADR-0001: exactly one image adapter + one surgical QA call. Nothing else may reach a network.

    A publisher/scheduler would show up here as a new module importing an HTTP client.
    """
    src = SPRINT_ROOT / "src" / "lumora_sprint"
    offenders: dict[str, set[str]] = {"httpx": set(), "replicate": set(), "anthropic": set()}
    for py in sorted(src.rglob("*.py")):
        for line in py.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped.startswith(("import ", "from ")):
                continue
            for pkg, seen in offenders.items():
                if stripped.startswith((f"import {pkg}", f"from {pkg}")):
                    seen.add(py.relative_to(src).as_posix())

    assert offenders["httpx"] <= {"generate/replicate_flux.py"}
    assert offenders["replicate"] <= {"generate/replicate_flux.py"}
    assert offenders["anthropic"] <= {"compliance.py"}


def test_no_publisher_verbs_anywhere_in_the_package() -> None:
    """Publishing is Sin's thumb — no scheduler, no platform client, not even a helper.

    ``mark_published`` / ``published_ids`` are fine: they *record* what Sin did. What must never
    appear is a callable that would do the posting, or a client for the platform itself.
    """
    src = SPRINT_ROOT / "src" / "lumora_sprint"
    banned = re.compile(
        r"\bdef (?:publish|schedule)(?:_[a-z_]+)?\s*\("     # publish() / publish_post() — never
        r"|\bdef (?:post_to|upload_to)[a-z_]*\s*\("
        r"|TikTokApi|tiktok_api"
    )
    hits = [
        f"{py.relative_to(src).as_posix()}:{m.group(0)}"
        for py in sorted(src.rglob("*.py"))
        for m in banned.finditer(py.read_text(encoding="utf-8"))
    ]
    assert hits == []


# ── defect ledger (regressions for the bugs found in review) ───────────────


def test_packet_must_not_walk_a_published_packet_backwards(sandbox: Path) -> None:
    """Re-running the compliance gate on a live post must not un-publish it.

    post_log still holds the url and the metrics, so a downgrade desyncs the two stores and makes
    `status` demand an `approve` for something already on TikTok.
    """
    publish(sandbox, 1, "L1-D01", URL1)
    assert meta(sandbox, "L1-D01")["status"] == PacketStatus.published.value

    assert run(sandbox, "packet", "--day", "1", "--no-llm") == EXIT_OK

    assert meta(sandbox, "L1-D01")["status"] == PacketStatus.published.value
    assert rows(sandbox, "SELECT status FROM packets WHERE post_id='L1-D01'") == [
        {"status": PacketStatus.published.value}
    ]


def test_force_regenerate_must_not_unpublish_a_live_post(sandbox: Path) -> None:
    """New pixels invalidate an *approval*; they cannot un-happen a post Sin already uploaded."""
    publish(sandbox, 1, "L1-D01", URL1)

    assert run(sandbox, "generate", "--day", "1", "--force") == EXIT_OK

    assert meta(sandbox, "L1-D01")["status"] == PacketStatus.published.value
    assert rows(sandbox, "SELECT status FROM packets WHERE post_id='L1-D01'") == [
        {"status": PacketStatus.published.value}
    ]


def test_packet_preserves_an_accepted_caption_final(sandbox: Path) -> None:
    """checklist.md tells Sin to consider the QA's suggested caption; accepting one must stick."""
    assert run(sandbox, "run", "--day", "2", "--no-llm") == EXIT_OK

    accepted = "แคปชั่นที่รับมาแล้ว — ต้องไม่หาย"
    data = meta(sandbox, "L1-D02")
    data["caption_final"] = accepted
    meta_path(sandbox, "L1-D02").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    assert run(sandbox, "packet", "--post-id", "L1-D02", "--no-llm") == EXIT_OK

    assert meta(sandbox, "L1-D02")["caption_final"] == accepted
    assert (sandbox / "out" / "L1-D02" / "caption.txt").read_text(encoding="utf-8").startswith(accepted)


def test_status_names_the_real_post_id_on_day_29(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Day 29 carries the batch's single Hero post. status must not invent a post id for it."""
    box = make_sandbox(tmp_path, TODAY - timedelta(days=28))
    assert run(box, "init") == EXIT_OK
    capsys.readouterr()

    assert run(box, "status") == EXIT_OK
    out = capsys.readouterr().out

    assert "L5-D29" not in out
    assert "L4-D29" in out


def test_a_failed_step_records_why_it_failed(sandbox: Path) -> None:
    """The append-only log cannot be backfilled — an ok=False line that does not say why is useless."""
    assert run(sandbox, "plan", "--day", "8") == EXIT_NEEDS_HUMAN

    event = read_events(sandbox / "out" / "agent_events.jsonl")[-1]
    assert event.step == "plan"
    assert event.ok is False
    assert "outline" in event.detail
    assert "fatigue" not in event.detail


def test_a_logged_post_is_never_invisible_to_status(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A successful `log` must either be counted or be refused — never accepted and then ignored."""
    box = make_sandbox(tmp_path, TODAY + timedelta(days=1))     # sprint starts tomorrow
    publish(box, 1, "L1-D01", URL1)
    assert rows(box, "SELECT COUNT(*) n FROM post_log") == [{"n": 1}]
    capsys.readouterr()

    assert run(box, "status") == EXIT_OK
    assert "posts logged: 0" not in capsys.readouterr().out


def test_review_also_sees_a_post_dated_before_sprint_start(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The same clamp must hold in Step 4 of the weekly ritual, not just on the status screen."""
    box = make_sandbox(tmp_path, TODAY + timedelta(days=1))
    publish(box, 1, "L1-D01", URL1)
    assert run(box, "metrics", "L1-D01", "--views-7d", "4300") == EXIT_OK
    capsys.readouterr()

    assert run(box, "review", "--week", "1") == EXIT_OK
    md = (box / "out" / "reviews" / "W1.md").read_text(encoding="utf-8")
    assert "**โพสต์ที่ log แล้ว:** 1" in md
    assert "ยังไม่มีโพสต์ให้ตรวจ" not in md              # AI-label check saw the row
    assert "4,300" in md                                  # and so did the gate


def test_packet_reopen_is_the_only_way_back_from_approved(
    sandbox: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The guard is a default, not a wall: `--reopen` is the explicit, auditable way to downgrade."""
    assert run(sandbox, "run", "--day", "1", "--no-llm") == EXIT_OK
    assert run(sandbox, "approve", "L1-D01") == EXIT_OK
    capsys.readouterr()

    assert run(sandbox, "packet", "--day", "1", "--no-llm") == EXIT_OK
    assert meta(sandbox, "L1-D01")["status"] == PacketStatus.approved.value
    assert meta(sandbox, "L1-D01")["approved_at"] is not None   # and the timestamp survived

    assert run(sandbox, "packet", "--day", "1", "--no-llm", "--reopen") == EXIT_OK
    assert meta(sandbox, "L1-D01")["status"] == PacketStatus.draft.value
    assert rows(sandbox, "SELECT status FROM packets WHERE post_id='L1-D01'") == [
        {"status": PacketStatus.draft.value}
    ]


def test_caption_verb_sets_a_final_caption_and_reopens_the_gate(
    sandbox: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`caption` is the sanctioned way to accept a rewording — and new text needs a new approval."""
    assert run(sandbox, "run", "--day", "1", "--no-llm") == EXIT_OK
    assert run(sandbox, "approve", "L1-D01") == EXIT_OK
    capsys.readouterr()

    mine = "แคปชั่นที่ Sin เขียนเอง 🌌"
    assert run(sandbox, "caption", "L1-D01", "--text", mine) == EXIT_OK
    assert meta(sandbox, "L1-D01")["caption_final"] == mine
    assert meta(sandbox, "L1-D01")["status"] == PacketStatus.draft.value
    assert (sandbox / "out" / "L1-D01" / "caption.txt").read_text(encoding="utf-8").startswith(mine)

    # and it survives the next full re-run, which is the whole point
    assert run(sandbox, "run", "--day", "1", "--no-llm") == EXIT_OK
    assert meta(sandbox, "L1-D01")["caption_final"] == mine

    assert run(sandbox, "caption", "L1-D01", "--clear") == EXIT_OK
    assert meta(sandbox, "L1-D01")["caption_final"] == ""


def test_cost_usd_is_total_spend_across_every_generate_run(sandbox: Path) -> None:
    """gen and qa halves must be read the same way, or post_log.cost_usd means two things at once."""
    assert run(sandbox, "run", "--day", "1", "--no-llm") == EXIT_OK
    assert run(sandbox, "generate", "--day", "1", "--force") == EXIT_OK
    assert run(sandbox, "packet", "--day", "1", "--no-llm") == EXIT_OK
    assert run(sandbox, "approve", "L1-D01") == EXIT_OK
    assert run(sandbox, "log", "L1-D01", "--url", URL1) == EXIT_OK

    events = read_events(sandbox / "out" / "agent_events.jsonl")
    total = sum(e.cost_usd for e in events if e.post_id == "L1-D01" and e.step in {"generate", "packet"})
    logged = rows(sandbox, "SELECT cost_usd FROM post_log WHERE post_id='L1-D01'")[0]["cost_usd"]
    assert logged == pytest.approx(total)      # every run counted, not just the last generate
    assert len([e for e in events if e.step == "generate"]) == 2


def test_status_says_the_batch_is_finished_instead_of_inventing_day_31(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The batch is 30 days but the gate is 90 — day 31 must not advise generating a phantom post."""
    box = make_sandbox(tmp_path, TODAY - timedelta(days=30))     # today is sprint day 31
    assert run(box, "init") == EXIT_OK
    capsys.readouterr()

    assert run(box, "status") == EXIT_OK
    out = capsys.readouterr().out
    assert "day 31/90" in out
    assert "L5-D31" not in out
    assert "batch หมดแล้ว" in out
