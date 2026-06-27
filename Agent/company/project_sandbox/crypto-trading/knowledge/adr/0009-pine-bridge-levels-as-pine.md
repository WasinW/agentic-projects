# 0009. Pine bridge — levels-as-Pine (generated snippet)

- Status: Accepted
- Date: 2026-06-07
- Deciders: Wasin + software-engineer
- Tags: pine, tradingview, bridge

## Context
doc/02 §3 lists three engine→TradingView bridges, easy→hard: (1) manual review,
(2) **levels-as-Pine** — generate a Pine snippet hard-coding the latest
levels/zones/bias and paste it into TV, (3) webhook action leg (outbound alerts).
Pine cannot fetch an external API or receive external series (§5), so only the
*result* can cross to TV, never the engine.

## Options
- Manual review only — no code, but nothing visualized on the chart.
- **Levels-as-Pine (option 2)** — `pine.py` emits a self-contained Pine v6 overlay
  with hard-coded values from a `Step1Output`.
- Webhook action leg (option 3) — TV alert → service round-trip; higher complexity,
  needs a hosted endpoint.

## Decision
Implement option 2 now. `pine.py::to_pine(Step1Output)` generates `//@version=6`
`indicator(overlay=true)` with: support/resistance as dashed `hline`s (nearest-first),
the invalidation as a solid orange line + rule comment, and (when the LLM `plan` is
present) the entry zone as a filled band, stop, and targets, plus a bias label on the
last bar. CLI: `analyze --pine` writes `output/<symbol>_<ts>.pine`. All strings are
literal-safe (quotes/newlines/backslashes stripped). Deterministic; no LLM/network.

Defer option 3 (webhook leg) — it needs a hosted service and is only worth it after
the dashboard exists.

## Consequences
- + One paste puts the engine's levels + bias on the real chart next to price/RSI.
- + Snapshot is hard-coded and reproducible; re-run + re-paste to refresh (acceptable
  for the manual-review workflow that starts the bridge).
- − Values are static — they don't update as new candles print (by design; Pine can't
  call back to the engine).
- − Plan band/stop/targets only appear with `--interpret` (plan is LLM-owned, ADR 0008).
