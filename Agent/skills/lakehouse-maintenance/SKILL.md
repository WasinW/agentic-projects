---
name: lakehouse-maintenance
description: Given a lakehouse table's profile, produce a concrete maintenance plan — compaction, clustering, retention/vacuum, MoR cleanup, schedule + cost note — with format-specific commands. Use when a Delta/Iceberg/Hudi table is slow, accumulating small files, bloated by old snapshots, or just needs a routine upkeep plan.
---

# lakehouse-maintenance

Turns a table profile into a runnable maintenance plan: what to compact, how to cluster, what to expire, and how often — with the actual commands for the table's format.

## When to use

- A lakehouse table is slow to query, has small-file blowup, skew, or storage bloat.
- Setting up routine upkeep for a new or untended table.
- Reviewing whether existing OPTIMIZE / VACUUM / snapshot-expiry cadence is right.

## Inputs

- **Table format** — Delta / Iceberg / Hudi (+ engine/catalog if known).
- **Size & partitioning** — total size, row count, partition columns + cardinality.
- **Write pattern** — append / merge (CDC upsert) / streaming micro-batch.
- **Query pattern** — common filter/join columns, point lookups vs scans, SLA.
- **Symptoms** — small files, skew, slow MERGE, storage growth, stale snapshots.

## Steps

1. **Load knowledge:**
   `mcp__agent-knowledge__search_knowledge(query="lakehouse table maintenance optimize vacuum compaction liquid clustering", role_filter="databricks-expert", top_k=5)` and
   `mcp__agent-knowledge__search_knowledge(query="delta iceberg hudi compaction small files retention snapshot expiry", role_filter="de-engineer", top_k=5)`.
   Fallback: read `roles/technical/consultant/databricks-expert/knowledge.md` + `roles/technical/engineer/de-engineer/knowledge.md`.
2. **Compaction** — fix small files / right-size data files:
   - Delta: `OPTIMIZE tbl [WHERE ...]`; Iceberg: `rewrite_data_files`; Hudi: clustering / inline+async compaction.
3. **Clustering / data layout** — match to query filters:
   - Delta: liquid clustering (`CLUSTER BY`) preferred, else `ZORDER BY`; Iceberg: sort order / partition transforms (bucket, truncate); Hudi: clustering + bucketing.
4. **Retention / reclaim storage** — keep time-travel window but reclaim the rest:
   - Delta: `VACUUM tbl RETAIN n HOURS`; Iceberg: `expire_snapshots` + `remove_orphan_files`; Hudi: cleaner (`hoodie.cleaner.commits.retained`).
5. **MoR / deletion-vector cleanup** — if merge-on-read or deletion vectors are on: schedule compaction of delete files / log files / DVs so read amplification doesn't grow.
6. **Schedule + cost note** — give a cadence (e.g. compaction daily/after-load, clustering weekly, expiry/vacuum daily-to-weekly), tie retention to the time-travel SLA, and note the compute cost vs the query/storage savings. Prefer incremental/`WHERE`-scoped ops to limit cost.

## Guardrails / Notes

- VACUUM / expire_snapshots is irreversible past the retention window — confirm the time-travel SLA before shortening it; never go below in-flight job needs.
- Don't run heavy OPTIMIZE/rewrite concurrently with large writes on the same partitions (conflict/abort risk); schedule in low-traffic windows.
- Tailor commands to the actual format/engine — don't emit Delta syntax for an Iceberg table.
- State assumptions when symptoms or sizes are missing, and recommend measuring file-size distribution before/after.
