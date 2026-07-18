# 0014. Deterministic playbook + position sizing + confidence.floor wired; Elliott digest fixed

- Status: Accepted
- Date: 2026-07-18
- Deciders: Wasin (+ portfolio-review 2026-07-18 §3.3)
- Tags: signals, plan, sizing, contract, elliott

## Context
Three deterministic gaps and one LLM soundness bug surfaced in the review:
1. The doc/03 §4 playbook decision table was fully specified but **delegated to LLM prose**
   — `plan.playbook` was null in v1 even though spec §6 calls it a "code-owned field".
2. `confidence.floor: 0.45` existed in config + spec but **no code ever read it**
   (dead knob, verified by grep).
3. No deterministic position sizing (~20 lines, more valuable than the whole Elliott block).
4. The LLM digest fed only **3 swing highs/lows** — you cannot count Elliott waves from 3
   points, so the model confabulated an authoritative-looking count.

## Options (playbook placement)
- Keep `plan = null` deterministically (as [0004](0004-step1-json-contract-null-shape.md)
  froze) and leave the playbook to the LLM — perpetuates gap #1 and the false precision.
- Add a new top-level contract field — churns the locked schema.
- **Populate the existing `plan` block deterministically** (playbook/entry/stop/sizing),
  leaving `targets`/`r_r`/prose LLM-owned. Spec §6 always intended `plan.playbook` to be
  code-owned; v1 simply hadn't implemented it.

## Decision
- `decision.select_playbook(trend, direction, conviction, vol, confidence, cfg)` implements
  the §4 table in code, including the caveat-#3 rule: `confidence < confidence.floor` forces
  **stand-aside** (wiring the dead knob) and appends a caveat. Baked-in discipline preserved:
  no counter-trend, low-conviction → stand-aside, range+expansion → stand-aside.
- `decision.position_size(entry, stop, cfg)` = `(risk_pct × equity) / stop_distance`, capped
  at `max_leverage × equity` notional. Params in a new `sizing:` config block.
- `engine._build_output` now always emits a deterministic `plan` (playbook + entry_zone from
  the S/R source + stop = invalidation + sizing_note). Under `--interpret`, the LLM only
  enriches `targets`/`r_r`/prose; the deterministic **playbook/stop win**.
- Elliott: the digest now carries the full `pivot_series_1d` (~40 pivots) and the prompt
  instructs the model to count ONLY from it (else confidence low). Straightforward feed-the-
  full-series fix chosen over removing the Elliott block.

## Consequences
- + `plan.playbook` is now reproducible and transparent, not laundered through an LLM.
- + Partially supersedes [0004](0004-step1-json-contract-null-shape.md) for the `plan` block
  (elliott/summaries stay null deterministically; `plan.targets`/`r_r` stay null too).
  Schema (`Plan` pydantic) is unchanged — this is a fill-a-null-field behavior change, not a
  breaking schema change, so `engine_version` stays 0.1.0.
- + Elliott is now grounded in real pivot structure or explicitly low-confidence.
- − Consumers that assumed `plan is None` in the deterministic path must read `plan.playbook`
  (tests updated). − Sizing uses config equity/risk, not live account state (by design, v1).
