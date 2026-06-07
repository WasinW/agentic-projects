# 0003. Separate storage/compute on object storage; one unified open engine for batch + streaming

- Status: Accepted
- Date: 2026-06-03
- Deciders: Wasin + data-architect
- Tags: compute, streaming, batch, architecture, irreversible

## Context
The platform must handle both batch (scheduled ETL/ELT) and streaming (real-time, CDC, event-driven) from day one. A Lambda architecture (separate batch and streaming codebases) leads to two sources of truth and constant reconciliation. We also want compute to be swappable across clouds, which requires data to live independently of any compute engine.

## Options considered
- **Storage/compute separation + unified engine (Spark Structured Streaming), Kappa-leaning (chosen)** — data lives as Iceberg tables on object storage; one transformation codebase where "batch = a bounded stream", parameterized by trigger. Both batch and streaming writers MERGE/append into the *same* Iceberg table per layer; Iceberg snapshot isolation makes concurrent writes safe; WAP branch validates a micro-batch against its contract before publish. Con: Spark micro-batch is not the absolute lowest latency for complex event-time windowing.
- **Lambda (separate batch + streaming stacks)** — purpose-built per path, but two codebases, two truths, reconciliation hell, double the maintenance.
- **Flink platform-wide** — best for sub-second stateful streaming, but a second programming model to staff and operate org-wide on day one.

## Decision
Adopt storage/compute separation with data as Iceberg tables on object storage, and a single unified open engine (Spark Structured Streaming) for both batch and streaming, sharing one transformation codebase. Both writers land in the same Iceberg table per medallion layer. Flink is reserved only for specific use cases that prove sub-second stateful streaming is required.

## Consequences
- **Positive:** one codebase for Silver dedup/conform logic (written once), no Lambda fork, no batch-vs-stream reconciliation. Replay/backfill = re-read Landing/Kafka through the same code. Compute is portable ("managed Spark on cloud X" → "cloud Y" is a migration, not a rewrite).
- **Cost / accepted:** Spark micro-batch latency is not the theoretical minimum; complex low-latency event-time joins may later justify adding Flink for those jobs only — accepted as a targeted exception, not a platform default.
- **Constraint introduced:** unification must not happen inside a proprietary, closed streaming service; keep the engine open-source-rooted even when run as a managed service.

## Related
- [[0001-table-format-apache-iceberg]] — both engines write this format.
- [[0004-contract-boundaries-and-openlineage]] — WAP publish gate enforces contracts on streaming writes.
