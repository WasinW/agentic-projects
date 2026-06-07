# 0007. Elliott Wave = lowest weight, supporting view only

- Status: Accepted
- Date: 2026-06-07
- Deciders: Wasin + investment-consultant
- Tags: signals, elliott, scoping

## Context
doc/02 §5/§7: Elliott Wave is the least reliable and hardest to auto-compute
signal, and is inherently ambiguous (primary + alternate counts). It must inform,
never dominate.

## Decision
- v1 deterministic: Elliott is **absent** (`elliott = null`, not in `signals[]`),
  produced later by the interpretive LLM layer.
- v2 integration: add **one** signal `elliott_1d` (not per-TF — 1h is noise and
  stays descriptive only), preventing multiplicity from swamping deterministic
  signals.
- Weight default **0.05**, hard-capped ≤ the smallest directional deterministic
  weight. At that weight it can only break ties / nudge conviction (~5% max swing),
  never flip a primary-decided argmax.
- Vote = `implied_direction`; if confidence low OR primary/alt counts disagree on
  direction → neutral. If it contradicts `structure_1d`, don't suppress — let it
  lower the margin (possible conviction downgrade). It is caution, not a veto.

## Consequences
- + EW adds nuance without hijacking the bias; honors §5 reliability ordering.
- + Config flag `elliott.enabled` gates it; off in v1.
- − Requires the LLM layer before it contributes at all.
- Source: doc/03-signal-logic-spec.md §6.
