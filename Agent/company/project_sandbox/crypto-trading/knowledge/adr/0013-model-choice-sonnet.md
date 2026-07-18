# 0013. LLM model = claude-sonnet-5 (config-driven, was hardcoded Opus)

- Status: Accepted
- Date: 2026-07-18
- Deciders: Wasin (+ portfolio-review 2026-07-18 §3.3)
- Tags: llm, config, cost

## Context
`interpret.py` hardcoded `MODEL = "claude-opus-4-8"` — which broke the project's own rule
that all tuning lives in `config/engine.yaml`, never inline
([0008](0008-interpretive-llm-layer.md), CLAUDE.md). The interpretive layer's job is
narrow: summarise a small pre-computed digest into Elliott / summaries / plan prose. That
is not a frontier-reasoning task; Opus-tier was overkill and the higher per-token cost
bought nothing here.

## Options
- Keep Opus 4.8 hardcoded — violates the config rule; overpays for digest summarisation.
- Keep Opus but move to config — still overpays by default.
- **Default to `claude-sonnet-5`, model name + call params in config.**

## Decision
Add an `llm:` block to engine.yaml (`model: claude-sonnet-5`, `max_tokens: 16000`,
`effort: high`) and a `LLMCfg` model. `interpret.py` reads `cfg.llm.*` — no hardcoded
model string. The `messages.parse(..., thinking={"type":"adaptive"},
output_config={"effort": ...}, output_format=…)` call is unchanged and is compatible with
Sonnet 5 (adaptive thinking + effort + structured outputs all supported). Swapping the
model or effort is now a one-line config edit; Opus/Fable remain available by changing
`cfg.llm.model`.

## Consequences
- + Restores the config-driven invariant; model is diffable and per-run overridable.
- + Sonnet 5 is enough for digest summarisation at materially lower cost than Opus.
- + Verified by the fake-client test asserting `model == cfg.llm.model` (no live key).
- − If Elliott/plan quality ever needs more, bump `cfg.llm.model` back to Opus/Fable —
  the deterministic core is unaffected either way.
- Model IDs verified against the claude-api skill catalog (2026-07-18): `claude-sonnet-5`
  is an active model.
