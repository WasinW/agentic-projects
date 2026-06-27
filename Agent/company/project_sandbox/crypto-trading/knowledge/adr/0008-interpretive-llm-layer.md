# 0008. Interpretive LLM layer (Elliott / summaries / plan)

- Status: Accepted
- Date: 2026-06-07
- Deciders: Wasin + software-engineer
- Tags: llm, architecture, interpretation

## Context
v1 emitted the deterministic §6 blocks with `elliott`/`summaries`/`plan = null`
([0004](0004-step1-json-contract-null-shape.md)). The two-layer design
([0003](0003-two-layer-engine-deterministic-interpretive.md)) calls for an
interpretive layer that runs at runtime from the engine itself (not Claude Code)
to fill those blocks and integrate Elliott as a supporting view
([0007](0007-elliott-wave-lowest-weight-supporting-view.md)).

## Options
- Send raw candles to the LLM — expensive, non-reproducible, arithmetic-prone.
- **Send the deterministic digest** (regime, bias, signals, levels, per-TF
  RSI/structure/swings, MA values, ATR, vol regime) — compact, grounded, cheap.

## Decision
`interpret.py` calls the Anthropic API (model **claude-opus-4-8**, adaptive
thinking, `effort: high`, **structured outputs** via `messages.parse` + a pydantic
schema) over the digest only. It returns Elliott (per-TF), daily/weekly/monthly
summaries, and a trade plan (stop = the deterministic invalidation; entry/targets
from the provided S/R; r_r computed). It also returns ONE integrated `elliott_vote`.
- The engine folds a single **`elliott_1d`** signal at `cfg.elliott.weight` (0.05)
  and **recomputes** confluence/bias/confidence — Elliott can nudge, never dominate.
- LLM schema is **decoupled** from the contract (`LLMInterpretation`) then mapped
  into contract models, so prompt/schema changes don't touch the locked contract.
- Enabled via `analyze(..., interpret=True)` / CLI `--interpret`; needs
  `ANTHROPIC_API_KEY`. The deterministic path is unchanged and key-free.

## Consequences
- + Reproducible deterministic core + optional rich interpretation; clear provenance.
- + Digest (not raw candles) keeps tokens low and grounds the model in real numbers.
- + Wiring covered by a fake-client test; deterministic path stays green without a key.
- − Plan/Elliott quality depends on the model and the digest's completeness.
- − Folding Elliott re-runs confluence, so `--interpret` can shift bias vs the pure
  deterministic run (intended, bounded by the 0.05 weight).
