"""Append-only accountability log — one JSON line per agent step (out/agent_events.jsonl).

This is the raw material of the agent-failure dataset (07 §2.5): which agent / prompt version /
model produced what, at what cost, and whether it worked. It cannot be backfilled later, so it is
written from post #1.

Hard rule: **writing an event must never break the loop.** A full disk or an unwritable path costs
us one line of telemetry, not a generated image or an approved packet — so `append_event` swallows
its errors to stderr and reports failure via its return value instead of raising.
"""
from __future__ import annotations

import sys
from pathlib import Path

from .models import AgentEvent


def append_event(path: str | Path, event: AgentEvent) -> bool:
    """Append one AgentEvent as a JSON line, creating the parent directory if needed.

    Returns True on success, False if the write failed (reason goes to stderr). Never raises.
    """
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(event.model_dump_json() + "\n")
        return True
    except Exception as exc:  # noqa: BLE001 — telemetry must not break the hot path
        print(f"[events] could not append to {path}: {exc!r}", file=sys.stderr)
        return False


def read_events(path: str | Path) -> list[AgentEvent]:
    """Read the whole event log back. Missing file -> []. Bad lines are skipped, not fatal.

    A half-written trailing line (crash mid-append) must not blind the weekly review, so malformed
    lines are reported to stderr and dropped.
    """
    p = Path(path)
    if not p.exists():
        return []
    events: list[AgentEvent] = []
    try:
        text = p.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"[events] could not read {path}: {exc!r}", file=sys.stderr)
        return []
    for i, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            events.append(AgentEvent.model_validate_json(line))
        except ValueError as exc:
            print(f"[events] skipping malformed line {i} in {path}: {exc!r}", file=sys.stderr)
    return events
