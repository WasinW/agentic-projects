"""Trade journal — append-only JSONL of *taken* trades + a monthly plan-vs-actual
review. A discipline tool with no journal is just a signal printer (portfolio review
2026-07-18 §3.3), so this closes the loop: link each action back to the analyze
artifact that informed it, record the outcome in R, and grade adherence to the plan.

Append-only: entries are never mutated; a close/adjust is a NEW entry. One JSON object
per line so the file is greppable, diffable, and cheap to append.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

Action = str  # "long" | "short" | "close" | "skip"


class JournalEntry(BaseModel):
    ts: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    artifact_id: str                       # links to output/<symbol>_<stamp>.json (the signal)
    symbol: str
    action: Action                         # what the trader actually did
    entry: Optional[float] = None
    exit: Optional[float] = None
    stop: Optional[float] = None
    size: Optional[float] = None
    r: Optional[float] = None              # realised R multiple (win/loss in risk units)
    planned_bias: Optional[str] = None     # what the engine's bias was (plan-vs-actual)
    planned_playbook: Optional[str] = None
    note: Optional[str] = None


def compute_r(action: str, entry: float, exit: float, stop: float) -> Optional[float]:
    """Realised R = reward / initial risk, signed by trade direction."""
    if entry is None or exit is None or stop is None:
        return None
    risk = abs(entry - stop)
    if risk <= 0:
        return None
    if action == "long":
        return round((exit - entry) / risk, 4)
    if action == "short":
        return round((entry - exit) / risk, 4)
    return None


def default_path(output_dir: str = "output") -> Path:
    return Path(output_dir) / "journal.jsonl"


def append_entry(entry: JournalEntry, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(entry.model_dump_json() + "\n")
    return path


def read_entries(path: str | Path) -> list[JournalEntry]:
    path = Path(path)
    if not path.exists():
        return []
    out: list[JournalEntry] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(JournalEntry.model_validate_json(line))
    return out


# ---------- monthly plan-vs-actual summary ----------
class MonthlySummary(BaseModel):
    month: str                  # "YYYY-MM" or "all"
    n_entries: int
    n_trades: int               # long/short/close actions (exclude skips)
    n_skips: int
    wins: int
    losses: int
    win_rate: Optional[float]
    total_r: float
    avg_r: Optional[float]
    expectancy_r: Optional[float]   # avg R across closed trades (with an r value)
    followed_plan: int              # action direction matched engine bias
    deviated_plan: int
    followed_r: float               # summed R when following the plan
    deviated_r: float               # summed R when deviating


def _month_of(ts: str) -> str:
    return ts[:7]  # "YYYY-MM"


def monthly_summary(entries: list[JournalEntry], month: Optional[str] = None) -> MonthlySummary:
    rows = entries if month is None else [e for e in entries if _month_of(e.ts) == month]
    trades = [e for e in rows if e.action in ("long", "short", "close")]
    skips = [e for e in rows if e.action == "skip"]
    closed = [e for e in rows if e.r is not None]

    wins = sum(1 for e in closed if e.r > 0)
    losses = sum(1 for e in closed if e.r < 0)
    total_r = round(sum(e.r for e in closed), 4)
    win_rate = round(wins / len(closed), 4) if closed else None
    avg_r = round(total_r / len(closed), 4) if closed else None

    followed = [e for e in rows if e.planned_bias and e.action == e.planned_bias]
    deviated = [e for e in rows if e.planned_bias and e.action in ("long", "short") and e.action != e.planned_bias]

    return MonthlySummary(
        month=month or "all",
        n_entries=len(rows), n_trades=len(trades), n_skips=len(skips),
        wins=wins, losses=losses, win_rate=win_rate,
        total_r=total_r, avg_r=avg_r, expectancy_r=avg_r,
        followed_plan=len(followed), deviated_plan=len(deviated),
        followed_r=round(sum(e.r for e in followed if e.r is not None), 4),
        deviated_r=round(sum(e.r for e in deviated if e.r is not None), 4),
    )


def summary_markdown(s: MonthlySummary) -> str:
    wr = f"{s.win_rate * 100:.0f}%" if s.win_rate is not None else "—"
    avg = f"{s.avg_r:+.2f}R" if s.avg_r is not None else "—"
    return "\n".join([
        f"# Trade journal — {s.month}",
        f"- entries: {s.n_entries} · trades: {s.n_trades} · skips: {s.n_skips}",
        f"- wins/losses: {s.wins}/{s.losses} · win-rate: {wr}",
        f"- total R: {s.total_r:+.2f} · avg R/trade: {avg}",
        "",
        "## Plan vs actual",
        f"- followed engine bias: {s.followed_plan} trades ({s.followed_r:+.2f}R)",
        f"- deviated from bias: {s.deviated_plan} trades ({s.deviated_r:+.2f}R)",
        "",
        "_Discipline check: deviating from the plan should not out-earn following it. "
        "Not investment advice._",
    ]) + "\n"
