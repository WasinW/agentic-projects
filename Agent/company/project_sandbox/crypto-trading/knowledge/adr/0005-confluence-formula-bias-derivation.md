# 0005. Confluence formula + bias / conviction / confidence derivation

- Status: Accepted
- Date: 2026-06-07
- Deciders: Wasin + investment-consultant + software-engineer
- Tags: signals, scoring

## Context
`confluence_score` was underspecified in §6 (weights summed to 0.90 but scores to
1.0 — implicit normalization). Needed a locked, transparent rule, plus how `bias`
and `confidence` derive deterministically.

## Decision
```
score[vote] = Σ(weight where signal.vote == vote) / Σ(weights of PRESENT signals)
```
- `neutral` is its own bucket. Absent signals (insufficient data, and `elliott` in
  v1) drop from the denominator. `vol_regime` carries weight 0 (context only).
- `bias.direction = argmax(score)`; `margin = top − second`.
- `conviction`: margin < 0.15 → low; 0.15–0.35 → medium; > 0.35 → high.
- `confidence = max_score × macro_factor` (see
  [0006](0006-macro-haircut-no-counter-trend.md)).
- `timeframe_alignment` read from per-TF `structure_<tf>` votes.
- All weights/thresholds live in `config/engine.yaml` — never hardcoded.

## Consequences
- + Transparent and reproducible; verified by a golden test reproducing the spec's
  worked example (short 0.58 / neutral 0.42, medium, confidence 0.493).
- + Adding/removing a signal just changes config; denominator self-adjusts.
- − Weights are judgment calls; treat as tunable, revisit with backtests later.
- Source: doc/03-signal-logic-spec.md §2–§3.
