# 0004. Step 1 JSON contract + null-shape for interpretive blocks

- Status: Accepted
- Date: 2026-06-07
- Deciders: Wasin + solution-architect
- Tags: data-contract, schema

## Context
doc/02 §6 locks the Step 1 output JSON (symbol-agnostic, transparent — every
signal shows its vote + weight). The architect sanity-check (GO-WITH-NOTES) found
provenance/null-handling gaps to close before scaffolding: which fields come from
code vs LLM, and null-vs-omit policy.

## Decision
`contract.py` pydantic models ARE the contract; the engine validates on emit.
- **Provenance:** code-owned = `regime`, `levels` (incl. invalidation), `signals`,
  `confluence_score`, `bias`, `confidence`. LLM-owned = `elliott`, `summaries`,
  `plan` (and `plan.note`).
- **Null policy (stable shape):** v1 sets `elliott = null`, `summaries = null`,
  `plan = null` — fixed keys so consumers (dashboard / Pine generator) rely on a
  stable shape rather than missing keys.
- `signals[].value` is `number | string` (polymorphic, intentional).
- Top-level `confidence` is float 0–1; elliott block `confidence` is categorical.
- `levels.support/resistance` ordered **nearest-first** to current price.
- `bias.timeframe_alignment` keys MUST equal `meta.timeframes` (validator enforces).

## Consequences
- + Downstream code never branches on key-presence; schema-validated output.
- + Swapping `symbol`/`asset_class` reuses the contract for stocks/options.
- − Adding a new top-level interpretive block is a contract change (version + ADR).
- Related: [0003](0003-two-layer-engine-deterministic-interpretive.md),
  [0005](0005-confluence-formula-bias-derivation.md).
