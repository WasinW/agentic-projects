---
name: table-format-decision
description: Given a workload's conditions, output a BALANCED Delta Lake vs Apache Iceberg vs Hudi recommendation with trade-offs — never a fixed default. Use when choosing (or revisiting) the open table format for a lakehouse table/pipeline, or when someone asks "Delta or Iceberg or Hudi?".
---

# table-format-decision

Picks an open table format by scoring the three peers against the *workload's actual conditions*, not by habit. The output is a recommendation **plus the reasoning that would flip it** — so the reader can sanity-check the fit.

## When to use

- Standing up a new lakehouse table/pipeline and the storage format is open.
- Revisiting a format because the engine, catalog, or compliance needs changed.
- Someone asks "should we use Delta / Iceberg / Hudi?" — answer with a comparison, not a default.

## Inputs (ASK for any that are missing BEFORE recommending)

- **Primary compute engine(s)** — Databricks/Spark, Flink, Trino/Presto, Snowflake, BigQuery, DuckDB, etc.
- **Cloud** — AWS / Azure / GCP / on-prem / undecided.
- **Catalog** — Unity Catalog, AWS Glue, Hive Metastore, Iceberg REST, Polaris/Nessie, none yet.
- **Streaming / upsert needs** — append-only? CDC merge? record-level upserts? low-latency ingest?
- **Governance needs** — fine-grained access, lineage, time-travel/audit, multi-engine governance.
- **Team skills & existing stack** — what they already run and operate well.

## Steps

1. **Load the neutral guide + cloud depth:**
   `mcp__agent-knowledge__search_knowledge(query="delta vs iceberg vs hudi table format trade-offs", role_filter="data-architect", top_k=5)` (should surface `delta_vs_iceberg_vs_hudi.md`) and
   `mcp__agent-knowledge__search_knowledge(query="delta lake unity catalog liquid clustering uniform", role_filter="databricks-expert", top_k=5)`.
   Fallback if MCP is down: read `roles/technical/architect/data-architect/delta_vs_iceberg_vs_hudi.md` + that role's `knowledge.md`, and `roles/technical/consultant/databricks-expert/knowledge.md`.
2. **Confirm conditions** — if any input above is unknown, ASK first. Do not recommend on guesses.
3. **Score each format** against the conditions (engine fit, catalog/interop, upsert/streaming model, governance, ops burden, team fit). Show a short table: Delta | Iceberg | Hudi × the conditions.
4. **Recommend** the best fit for *these* conditions, and name the **2-3 deciding factors** that drove it.
5. **State when you'd switch** — e.g. "if you add Flink CDC → Iceberg/Hudi look stronger", "if you standardize on Databricks + UC → Delta", "record-level upsert at low latency → Hudi".
6. **Note interop reduces lock-in** — Delta UniForm and Iceberg REST catalog let engines read across formats, so the choice is reversible; don't over-weight a 10-year bet.
7. **Offer to capture as an ADR** (`/adr`) so the "why X over Y" survives.

## Guardrails / Notes

- Do **NOT** default to Iceberg or Delta (or Hudi). Present all three as peers; let the conditions decide.
- Ask conditions BEFORE recommending — a format chosen against wrong assumptions is the real risk.
- Be explicit about confidence; flag where a condition is assumed vs confirmed.
- One table, one workload — different tables in the same platform can justify different formats; say so if relevant.
