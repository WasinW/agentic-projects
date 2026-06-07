---
name: data-contract-review
description: Review a proposed schema / data-contract change for breaking-ness and compatibility, then output a verdict + required actions — versioning, expand-contract migration, CI enforcement, rollback. Use when someone changes a table/event/API schema that downstream consumers depend on.
---

# data-contract-review

Classifies a schema/contract change as safe or breaking, names who it breaks, and prescribes the migration + enforcement so it ships without surprising a consumer.

## When to use

- A table, event (Avro/Protobuf/JSON), or API payload schema is changing and others consume it.
- Reviewing a PR that alters a published data contract.
- Deciding whether a change needs a new version or can ship in place.

## Inputs

- **The change** — before/after schema (fields added/removed/renamed/retyped, nullability, enum/default changes, semantic meaning changes).
- **Consumers** — known downstream jobs/services/dashboards/models; how they read (positional vs by-name, strict vs lenient).
- **Enforcement point** — schema registry, contract tests, CI, or none yet.

## Steps

1. **Load knowledge:**
   `mcp__agent-knowledge__search_knowledge(query="data contract schema evolution backward forward compatibility breaking change", role_filter="data-architect", top_k=5)` and
   `mcp__agent-knowledge__search_knowledge(query="schema registry contract test CI enforcement migration expand contract", role_filter="de-engineer", top_k=5)`.
   Fallback: read `roles/technical/architect/data-architect/knowledge.md` + `roles/technical/engineer/de-engineer/knowledge.md`.
2. **Classify the change** field by field:
   - **Safe / backward-compatible** — add optional/nullable field with default, widen a type, add enum value (for readers that tolerate unknowns).
   - **Breaking** — drop/rename a field, narrow/retype, make a field required, remove enum value, change units/semantics, reorder positional fields.
   - Note forward- vs backward-compat per the registry's compatibility mode.
3. **List affected consumers** — map each breaking item to the jobs/services it breaks and how (read failure, silent wrong value, type error).
4. **Recommend versioning + migration** — use **expand-contract**: add new alongside old → dual-write/backfill → migrate consumers → contract (remove old). Bump version (semantic) for breaking changes; keep old contract during transition.
5. **Recommend CI enforcement** — register schema with a compatibility check (e.g. BACKWARD), add a contract test that fails the build on incompatible changes, and require it before merge.
6. **Recommend rollback** — how to revert safely (keep old version readable, dual-write window, feature-flag the new shape).
7. **Output a verdict** — `SAFE` / `BREAKING` (+ which fields) and a checklist of **required actions** before merge.

## Guardrails / Notes

- "It compiles" is not "it's compatible" — semantic changes (units, meaning, nullability behavior) break consumers silently; call those out explicitly.
- Default to treating rename/drop/retype as breaking unless proven otherwise by consumer read mode.
- Never recommend a hard cutover when consumers are unknown — expand-contract + a migration window is the safe path.
- If the change has no enforcement point, flag that as a gap and recommend adding a registry/contract test.
