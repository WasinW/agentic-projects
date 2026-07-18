"""Trade journal tests — append-only round-trip, R computation, monthly summary."""

from crypto_engine.journal import (
    JournalEntry,
    append_entry,
    compute_r,
    monthly_summary,
    read_entries,
    summary_markdown,
)


def test_compute_r_long_and_short():
    # long: risk 5, reward 10 -> +2R
    assert compute_r("long", entry=100, exit=110, stop=95) == 2.0
    # short: entry 100, stop 105 (risk 5), exit 90 (reward 10) -> +2R
    assert compute_r("short", entry=100, exit=90, stop=105) == 2.0
    # losing long
    assert compute_r("long", entry=100, exit=97, stop=95) == -0.6
    # zero risk -> None
    assert compute_r("long", entry=100, exit=110, stop=100) is None
    assert compute_r("skip", entry=100, exit=110, stop=95) is None


def test_append_is_appendonly_and_roundtrips(tmp_path):
    path = tmp_path / "journal.jsonl"
    append_entry(JournalEntry(artifact_id="A1", symbol="BTCUSDT", action="short", r=1.5), path)
    append_entry(JournalEntry(artifact_id="A2", symbol="BTCUSDT", action="long", r=-1.0), path)
    entries = read_entries(path)
    assert [e.artifact_id for e in entries] == ["A1", "A2"]      # order preserved
    assert path.read_text().count("\n") == 2                      # exactly two lines, appended
    assert entries[0].action == "short" and entries[0].r == 1.5


def test_monthly_summary_plan_vs_actual():
    entries = [
        JournalEntry(ts="2026-07-01T00:00:00Z", artifact_id="A", symbol="X", action="short", r=2.0, planned_bias="short"),
        JournalEntry(ts="2026-07-05T00:00:00Z", artifact_id="B", symbol="X", action="long", r=-1.0, planned_bias="short"),  # deviated
        JournalEntry(ts="2026-07-09T00:00:00Z", artifact_id="C", symbol="X", action="skip", planned_bias="neutral"),
        JournalEntry(ts="2026-06-30T00:00:00Z", artifact_id="D", symbol="X", action="long", r=3.0, planned_bias="long"),   # other month
    ]
    s = monthly_summary(entries, month="2026-07")
    assert s.n_entries == 3
    assert s.n_trades == 2 and s.n_skips == 1
    assert s.wins == 1 and s.losses == 1
    assert s.total_r == 1.0                     # 2.0 + (-1.0)
    assert s.followed_plan == 1 and s.followed_r == 2.0
    assert s.deviated_plan == 1 and s.deviated_r == -1.0
    assert "2026-07" in summary_markdown(s)

    # all-time rolls in the June trade too
    s_all = monthly_summary(entries, month=None)
    assert s_all.n_entries == 4 and s_all.total_r == 4.0
