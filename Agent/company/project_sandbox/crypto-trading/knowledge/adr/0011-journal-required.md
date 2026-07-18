# 0011. Trade journal required — a discipline tool without a journal is a signal printer

- Status: Accepted
- Date: 2026-07-18
- Deciders: Wasin (+ portfolio-review 2026-07-18 §3.3)
- Tags: journal, discipline, feedback-loop

## Context
The engine's stated value (a) is *discipline* — systematising decisions and removing
emotion. But value (a) is exactly 0 while the tool is never used, and there was no way
to record what was actually traded or to compare intent vs outcome. Without a feedback
loop the engine emits signals into the void.

## Options
- Spreadsheet by hand — no link back to the artifact that informed the trade; drifts.
- A shared outcome-ledger unifying Lumora + crypto + framework (architect's proposal) —
  the review explicitly de-scoped this: designing a shared schema before either consumer
  has >1 month of real data is the same trap Lumora's backend fell into.
- **A tiny append-only `output/journal.jsonl`** scoped to crypto only.

## Decision
`journal.py` + `crypto-engine journal log` / `journal summary`. Append-only JSONL, one
record per line (greppable, diffable). Each taken trade links to the analyze
`artifact_id`, records action / entry / exit / stop / size / R and the engine's
`planned_bias`. R is computed from entry/exit/stop when not supplied. `journal summary
[--month]` gives a monthly plan-vs-actual review: win-rate, total R, and **followed-plan
vs deviated-plan R** — the discipline check (deviating from the engine should not
out-earn following it).

## Consequences
- + Closes the loop: signal → action → outcome, all reconstructable from artifact IDs.
- + Append-only means no destructive edits; a close/adjust is a new row.
- + Deliberately un-unified — becomes a shared component only once real data justifies it.
- − Manual `journal log` after each trade; if that habit doesn't stick, the tool is
  still just a signal printer (this is the real test of the whole project — see
  [0012](0012-kill-date-2026-08-31.md)).
