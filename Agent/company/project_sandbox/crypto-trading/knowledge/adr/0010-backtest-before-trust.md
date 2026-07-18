# 0010. Backtest harness before trusting the weights

- Status: Accepted
- Date: 2026-07-18
- Deciders: Wasin (+ portfolio-review 2026-07-18 §3.3)
- Tags: backtest, validation, signals

## Context
The signal weights (`structure_1d 0.22`, `ma_stack 0.20`, conviction bands 0.15/0.35…)
and the "confidence 0.493" number were opinions from one design session, never tested
against the 2.5 years of BTC candles already on disk. An unvalidated tool that *looks*
rigorous is more dangerous to real money than no tool — false precision launders gut
feel through decimals ([0005](0005-confluence-formula-bias-derivation.md) flagged the
weights as "judgment calls, revisit with backtests later").

## Options
- Ship automation/journal first, validate later — risks trading unvalidated weights.
- Predictive ML / walk-forward optimisation — out of scope, over-engineered for a
  personal decision-support tool.
- **A forward-return probe** that replays the EXISTING deterministic pipeline at every
  historical close and bins realised returns by the bias/conviction it produced.

## Decision
Build `src/crypto_engine/backtest/` (replay + report). It replays over every anchor-TF
close with **look-ahead-free** point-in-time candle slices and calls
`engine.deterministic(...)` — the identical signal/confluence/bias code the live
`analyze` uses (imported, never re-implemented). It then bins the realised 1d/3d/7d
forward returns by bias and conviction and answers the honest question: **do short-bias
signals actually show negative forward returns (and long-bias positive)?** CLI:
`crypto-engine backtest` → `output/backtest_report.{json,md}`. Config lives under
`backtest:` in engine.yaml (horizons, warmup, lookback_cap). This is a signal-quality
probe, not a P&L backtest (no fees/slippage/leverage).

## Consequences
- + First real evidence about the weights. Full-history BTC run (768 closes) returned
  **"EDGE NOT CONSISTENT"** — short-bias negative in only 2/3 horizons, barely above
  the unconditional baseline. The harness earns its keep by contradicting the design.
- + Reuses the live pipeline, so a signal-logic change is automatically re-validated.
- + Causal-indicator caveat handled via `lookback_cap` (Wilder RMA/EMA converge well
  within the window) — a pure perf lever, not a change in the values.
- − Correlated overlapping windows inflate apparent significance; treat directional
  hit-rate as a sanity signal, not a p-value.
- Action: retune or distrust the weights; do not size real trades off them yet.
