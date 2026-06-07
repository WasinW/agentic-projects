# 0003. Two-layer engine: deterministic code + interpretive LLM

- Status: Accepted
- Date: 2026-06-07
- Deciders: Wasin + solution-architect
- Tags: architecture, llm

## Context
The engine must compute exact TA features AND produce richer interpretation
(Elliott, narrative summaries, plan). Mixing these makes results irreproducible
and burns tokens on raw candles.

## Options
- One LLM call over raw candles — expensive, non-reproducible, hallucination-prone
  on arithmetic.
- All deterministic — can't do Elliott/synthesis/prose.
- **Two layers** — deterministic code does fetch/features/signals/confluence
  (exact); interpretive LLM later reads a *digest* (not raw candles) for Elliott,
  summaries, plan.

## Decision
Engine = deterministic layer (plain code, no LLM) + interpretive layer (calls the
Anthropic API from the engine script itself at runtime — NOT Claude Code, which is
build-time only). **v1 ships deterministic only**; interpretive blocks are emitted
as `null`. The LLM layer consumes the deterministic digest, never raw OHLCV.

## Consequences
- + Reproducible, cheap, fast; numbers always match (code), interpretation optional.
- + Clear provenance per §6 field (see [0004](0004-step1-json-contract-null-shape.md)).
- − Two code paths to maintain once the LLM layer lands.
- Related: build-time (Claude Code/agents/skills) vs runtime (engine) separation.
