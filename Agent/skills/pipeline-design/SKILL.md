---
name: pipeline-design
description: Design a new data pipeline end-to-end — requirements, data model + storage + table format, components (ETL/ELT/streaming), governance/PDPA hooks, build plan, ops/SLA — and produce a self-contained design doc. Use when standing up a new pipeline, especially one touching regulated data, multiple domains, or a customer-facing SLA.
---

# pipeline-design

The runnable version of the `design_new_pipeline` playbook. Drives a use case through a fixed sequence of design stages and emits one design doc. For depth on any stage, recommend spawning the owning role subagent.

## When to use

- A new pipeline touches regulated data (PDPA/BoT), costs/spans multiple domains, or has a customer-facing SLA → use the full flow.
- For a tiny addition / one-off backfill, a single subagent is enough — say so and stop.
- Read the source playbook for the full DAG + workflow option: `pipelines/playbooks/design_new_pipeline.md`.

## Inputs

- **Use-case description** — what data, from where, to whom, why.
- Anything known about: consumers, latency/freshness target, volume/growth, retention, data sensitivity.

## Steps (each stage consumes the prior stage's output)

1. **Load knowledge:**
   `mcp__agent-knowledge__search_knowledge(query="data pipeline design architecture medallion ingestion serving", role_filter="de-engineer", top_k=5)` and
   `mcp__agent-knowledge__search_knowledge(query="data modeling storage layering data contract pipeline architecture", role_filter="data-architect", top_k=5)`.
   Fallback: read `roles/technical/engineer/de-engineer/knowledge.md` + `roles/technical/architect/data-architect/knowledge.md`.
2. **Clarify requirements** — consumers, latency/freshness, volume + growth, retention, data sensitivity. ASK if unstated; don't invent SLAs.
3. **Data design** — tables/entities, keys, grain, partition/cluster, model (dim/fact, normalized, wide), storage layer (raw/bronze→silver→gold), and **table format** (invoke `table-format-decision` rather than defaulting), plus the data contracts each layer exposes.
4. **Components** — ingest (batch/CDC/stream), transform (ETL vs ELT, engine), orchestration, serve (warehouse/serving/API). Justify each against the requirements; prefer the existing stack.
5. **Governance / PDPA hooks** — PII map, masking/tokenization, retention + consent, access control, lineage. Flag any **blocker** that forces a redesign back to step 3.
6. **Implementation plan** — build steps, dependencies, risks, rough effort, backfill/cutover.
7. **Ops / SLA** — SLA tiers, monitoring (freshness, volume, quality, cost, lineage), alerting, runbook outline.
8. **Synthesize** — assemble one self-contained design doc: use case → requirements → data design → components → governance → build plan → ops/SLA.

## Guardrails / Notes

- Honor the gate: a governance blocker loops back to data design — don't let it flow downstream silently.
- For real depth, recommend the role subagents: `data-architect` (design), `solution-architect` (components), `governance-consultant` (PDPA/BoT), `de-engineer` (build), `data-ops` (SLA). This skill is the orchestrated single-agent pass.
- Don't over-specify domain answers; keep the doc to decisions + reasoning. Offer to record key choices as ADRs (`/adr`).
- For The-1 work, also load `company/ntt/the_one/CLAUDE.md` and pass `company_filter="ntt"`.
