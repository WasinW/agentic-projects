"""events.py — the accountability log roundtrips, and never breaks the loop when it can't write."""
from __future__ import annotations

from datetime import datetime

from lumora_sprint.events import append_event, read_events
from lumora_sprint.models import AgentEvent


def _ev(step: str, **kw) -> AgentEvent:
    return AgentEvent(agent="lumora-sprint", step=step, **kw)


def test_roundtrip_preserves_fields(tmp_path):
    p = tmp_path / "out" / "agent_events.jsonl"
    sent = _ev("generate", post_id="L1-D01", model="black-forest-labs/flux-dev",
               prompt_version="2026-07-w1", cost_usd=0.025, duration_s=12.5,
               detail="stub fallback: no REPLICATE_API_TOKEN")

    assert append_event(p, sent) is True
    assert p.parent.is_dir(), "parent directory should be created"

    got = read_events(p)
    assert len(got) == 1
    e = got[0]
    assert (e.agent, e.step, e.post_id) == ("lumora-sprint", "generate", "L1-D01")
    assert e.model == "black-forest-labs/flux-dev" and e.prompt_version == "2026-07-w1"
    assert e.cost_usd == 0.025 and e.duration_s == 12.5 and e.ok is True
    assert e.detail == "stub fallback: no REPLICATE_API_TOKEN"
    assert isinstance(e.ts, datetime)


def test_appends_one_line_per_event_in_order(tmp_path):
    p = tmp_path / "agent_events.jsonl"
    for step in ("plan", "generate", "qa", "packet", "approve"):
        append_event(p, _ev(step, post_id="L1-D01"))

    assert len(p.read_text(encoding="utf-8").strip().splitlines()) == 5   # append-only, 1 line each
    assert [e.step for e in read_events(p)] == ["plan", "generate", "qa", "packet", "approve"]


def test_thai_detail_survives(tmp_path):
    p = tmp_path / "agent_events.jsonl"
    append_event(p, _ev("qa", ok=False, detail="พบวลีต้องห้าม: การันตี"))
    assert read_events(p)[0].detail == "พบวลีต้องห้าม: การันตี"


def test_read_missing_file_returns_empty(tmp_path):
    assert read_events(tmp_path / "nope.jsonl") == []


def test_read_skips_blank_and_malformed_lines(tmp_path, capsys):
    p = tmp_path / "agent_events.jsonl"
    append_event(p, _ev("plan"))
    with open(p, "a", encoding="utf-8") as f:
        f.write("\n")
        f.write("{not json\n")            # crash mid-append
        f.write('{"agent": "x"}\n')       # valid json, invalid AgentEvent (no step)
    append_event(p, _ev("log"))

    events = read_events(p)
    assert [e.step for e in events] == ["plan", "log"], "one bad line must not blind the review"
    assert "malformed" in capsys.readouterr().err


def test_append_never_raises_on_write_failure(tmp_path, capsys):
    p = tmp_path / "blocked"
    p.mkdir()                              # path is a directory -> open() for append fails

    assert append_event(p, _ev("log", post_id="L1-D01")) is False
    assert "could not append" in capsys.readouterr().err
