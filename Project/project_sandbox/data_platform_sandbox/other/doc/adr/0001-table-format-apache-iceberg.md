# 0001. Use Apache Iceberg as the canonical open table format

- Status: Proposed
- Date: 2026-06-03
- Deciders: Wasin + data-architect
- Note (2026-06-04): Reverted Accepted → Proposed. Not yet confirmed — Delta Lake is an equally valid peer. To be re-decided with a neutral data-architect + databricks-expert consult; see the format decision guide `delta_vs_iceberg_vs_hudi.md`.
- Tags: storage, format, lakehouse, irreversible

## Context
Greenfield enterprise data platform, cloud deliberately undecided, with both batch and streaming writers from day one and a GenAI/RAG consumption path to come. The table format is the most irreversible bet on the platform — every byte of historical data is written in it, so changing it later means a full rewrite and a lineage break. Portability across clouds/engines is a primary requirement because no cloud is committed yet. Data is regulated (PDPA Thailand + BoT-style controls), so auditability and time-travel matter.

## Options considered
- **Apache Iceberg (chosen)** — best multi-engine support (Spark, Flink, Trino, Snowflake, BigQuery/BigLake, Dremio, DuckDB read/write the same tables); hidden partitioning + partition transforms; schema evolution by column ID; snapshots, time-travel, and WAP (write-audit-publish) branching for audit + atomic streaming publish. Con: merge-on-read upsert/streaming maturity slightly behind Hudi at extreme scale.
- **Delta Lake** — excellent streaming write story, but path-of-least-resistance only if the org commits to Databricks/Unity Catalog — which is exactly the cloud/vendor decision being deferred. Pre-paying for it now re-couples us.
- **Apache Hudi** — strongest for very high-frequency, high-cardinality continuous upserts (uber-scale CDC); a niche The-1 volume does not require. Weaker multi-engine ecosystem.

## Decision
Apache Iceberg is the single canonical table format for all medallion layers (Landing → Bronze → Silver → Gold → Serving). Warehouses and query engines may *read* these tables, but must not *own* them as proprietary-native tables.

## Consequences
- **Positive:** compute and even cloud can change without rewriting data — the literal embodiment of "cloud undecided". Partition evolution without history rewrite. Snapshots/time-travel give the "query as-of" audit trail PDPA/BoT reviews want.
- **Cost / accepted:** Iceberg's streaming-upsert path is good but not best-in-class; if a future use case needs sub-second high-cardinality continuous upserts at extreme scale, Hudi is the known fallback for that niche only.
- **Constraint introduced:** no layer may be materialized as a warehouse-native table (Snowflake-native, BigQuery-native) — doing so would lock that layer to one engine and defeat this decision.
- **Follow-up:** the real lock-in surface is the catalog, not the format — addressed in [[0002-catalog-iceberg-rest-spec]].

## Related
- [[0002-catalog-iceberg-rest-spec]] — the catalog interface that keeps Iceberg portable.
- [[0003-storage-compute-separation-unified-engine]] — engines writing these tables.
