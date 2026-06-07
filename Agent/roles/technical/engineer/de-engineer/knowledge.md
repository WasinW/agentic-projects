# Data Engineer — Comprehensive Knowledge

> Deep reference for the de-engineer subagent.

---

## 1. Foundations

### What a Data Engineer does

Builds + operates the systems that **move, transform, store, and serve** data reliably at scale.
- Pipelines: batch + streaming
- Storage: lakes, lakehouses, warehouses
- Compute: Spark, Beam, Flink, dbt
- Data quality + observability
- Ops: SLAs, runbooks, on-call

### The Data Engineering Lifecycle (Reis/Housley)

```
Generation → Storage → Ingestion → Transformation → Serving
                          ↓
                   (Undercurrents: security, data management, DataOps, architecture, orchestration, software engineering)
```

A DE works across all these phases.

### Adjacent roles

- **Data Architect** — designs; DE implements
- **Analytics Engineer** — focuses on Silver→Gold transforms with dbt
- **ML Engineer** — uses DE's data for models
- **DBA** — operates databases; DE designs pipelines that touch them
- **Data Analyst** — consumes data; DE makes sure it's reliable + fresh

---

## 2. Mental Models / Decision Frameworks

### ETL vs ELT vs Streaming

| Pattern | When |
|---|---|
| **ETL** (transform before load) | Legacy; controlled output to warehouse |
| **ELT** (transform after load) | Modern default; cheap storage, push transform to warehouse |
| **Streaming** (continuous) | Real-time use cases; willing to pay complexity |
| **CDC + replay** | Sync OLTP → OLAP without dual-writes |

### Batch vs Streaming Decision

```
SLA needed?
  < 1s     → True streaming (Flink, Beam, Kafka Streams)
  < 1 min  → Micro-batch (Spark Structured Streaming, Beam)
  < 1 hr   → Mini-batch / scheduled
  < 1 day  → Standard batch (Airflow + dbt)
  > 1 day  → Should we even build this?
```

90% of "we need real-time" requirements are met with 1-15 min freshness.

### Bronze → Silver → Gold (Medallion)

- **Bronze** — raw, append-only, schema-on-read
- **Silver** — cleaned, deduplicated, normalized, business keys
- **Gold** — modeled for consumption (star schema or wide fact tables)

This is the dominant pattern in modern lakehouses.

### Functional Data Engineering (Maxime Beauchemin)

Treat pipelines as pure functions:
- **Idempotent** — same input → same output, run any number of times
- **Deterministic** — no time-dependence (use event time, not processing time)
- **Reproducible** — pin data + code; can re-run history

This is THE principle that separates good DE from bad DE.

### Storage / Compute Separation

The cloud-era architectural principle:
- Storage: cheap, durable, infinite (S3, GCS, ADLS)
- Compute: ephemeral, billed for use (Spark, BQ, Snowflake compute, Flink)
- Decouple → pick best engine per workload, scale independently

### Schema Evolution Mindset

Schemas change. Plan from day 1:
- Add nullable columns → safe
- Type widening → safe
- Renaming or deletion → breaking; needs migration
- Use column IDs (Iceberg / Avro) not column names internally
- Schema registry for streams

### Decision: vendor warehouse vs open lakehouse

| | Warehouse (Snowflake, BQ, Redshift) | Lakehouse (Iceberg/Delta + Spark/Trino) |
|---|---|---|
| Setup time | Hours | Days-weeks |
| BI ergonomics | ★★★★★ | ★★★★ |
| ML ergonomics | ★★★ | ★★★★★ |
| Cost (small) | Manageable | Lower |
| Cost (large) | Can explode | Predictable |
| Open format | Sometimes | Yes |
| Multi-engine | No | Yes |

Modern default: **Iceberg + BigQuery/Snowflake on top**. Get warehouse ergonomics + open format.

### Idempotency patterns

- **Upsert with unique key** — most common; needs primary key
- **Merge / SCD2** — handles updates over time
- **Overwrite partition** — for daily batches; simple
- **Append + dedupe** — keep raw, dedupe in next layer

### Backpressure / DLQ patterns

Streaming systems need:
- Bounded queues (don't grow forever)
- Dead-letter queues for poison records
- Replay capability for incident recovery
- Backpressure signaling to upstream

---

## 3. Standard Practices

### dbt (analytics engineering bible)

The de facto SQL transformation framework:
- **Models** — SQL files materialized as tables/views
- **Tests** — declarative data quality checks
- **Sources** — declare external dependencies
- **Snapshots** — SCD2 automation
- **Macros** — reusable SQL
- **dbt-utils, dbt-expectations** — community packages
- **dbt contracts** (1.5+) — enforce schema

Best practices:
- Layer: staging → intermediate → marts
- Test sources + key columns (unique, not_null, accepted_values)
- Document models + columns (auto-publishes to docs site)
- Use `ref()` not raw table names
- Materialize strategically: views for cheap, tables for medium, incremental for large

### Apache Spark (workhorse)

When to use Spark:
- Petabyte-scale batch
- Complex transformations
- ML workloads (with Spark ML)
- Stream processing (Structured Streaming for micro-batch)

Key concepts:
- **DataFrame API** > RDD API (almost always)
- **Catalyst optimizer** + **Tungsten** = execution engine
- **AQE (Adaptive Query Execution)** — runtime optimization; enable it
- **Predicate pushdown + column pruning** — happens automatically with Iceberg/Parquet
- **Broadcast joins** — for small × large
- **Skewed joins** — biggest performance footgun

### Apache Beam / Dataflow

When Beam shines:
- Need portable pipelines (run on Dataflow, Flink, Spark)
- Streaming + batch with same code (unified model)
- Heavy stateful streaming (windowing, sessions)

When NOT to use Beam:
- Simple batch (dbt is easier)
- Pure SQL transforms (BigQuery SQL is faster to write)
- Custom code-heavy logic that fits Spark better

### Apache Flink

When Flink wins:
- Lowest-latency streaming
- Complex event processing (CEP)
- Strong exactly-once semantics
- Long-running streaming state

### CDC Patterns

| Tool | Notes |
|---|---|
| **Debezium** | Open source, mature, broad source support |
| **Fivetran / Airbyte** | Managed CDC + initial load |
| **AWS DMS** | AWS-managed, limited |
| **Native** (BigQuery CDC, Snowpipe Streaming) | Vendor lock-in but simple |

CDC patterns:
- **Initial snapshot** + **CDC stream** for ongoing
- **Delete handling** — soft delete vs hard
- **Schema evolution** — schema registry + DDL replication

### Data Quality

Three layers of DQ:
1. **Schema checks** — enforced by format (Parquet types, Avro contracts)
2. **In-pipeline tests** — dbt tests, Great Expectations
3. **Observability** — drift detection, freshness, volume anomalies (Monte Carlo, Soda, Datafold)

Don't skip layer 2 to do layer 3. They serve different purposes.

### Orchestration

| Tool | When |
|---|---|
| **Airflow** | Most popular; mature; older patterns |
| **Dagster** | Modern; assets-based mental model; better local dev |
| **Prefect** | Modern; cloud-first |
| **Argo Workflows** | K8s-native; good for diverse workloads |
| **Cloud-native** (Cloud Composer, MWAA) | Managed Airflow |

Airflow remains the standard, but Dagster's data-asset model is winning hearts.

### Testing pyramid for data

- **Unit tests** — pure functions (parsing, transformation)
- **Integration tests** — pipeline with sample data
- **Data tests** — production data quality (dbt tests, GE)
- **End-to-end tests** — full pipeline against staging

Don't skip unit tests because "data is the test."

### Observability standards

Emit:
- Pipeline metrics: rows in, rows out, duration, error rate
- Data metrics: freshness, volume, schema, distribution
- Lineage events (OpenLineage)
- Logs with correlation IDs

### Reverse ETL / operational analytics

**What it is** — syncing modeled warehouse data (Gold) *back out* to operational SaaS systems: Salesforce, HubSpot, Marketo, Zendesk, ad platforms, Braze. The warehouse becomes the source of truth for business teams ("data activation"). It closes the loop that classic ELT only ran one direction.

**Why it matters in production** — it's the highest-blast-radius pipeline you own. A bug doesn't land in a dashboard nobody reads; it writes a wrong lifecycle stage onto a live customer record, fires a marketing email, or pauses an ad campaign. Treat it as a write path to prod systems, not as analytics.

**Standard patterns**
- **Idempotency is non-negotiable** — destinations are mutable APIs with retries + rate limits. Sync on a stable external ID (e.g. Salesforce `External ID` upsert) so re-runs converge, never duplicate. Diff-based sync (only push changed rows) over full-refresh to respect API quotas.
- **Identity resolution** — match warehouse PK to the SaaS object's unique key; handle the "object doesn't exist yet" (create vs update) split explicitly.
- **Observability** — per-sync row counts, reject/error rows surfaced back (most APIs return partial failures), field-level audit logs, dry-run/approval before prod. Alert on sync failure *and* on suspicious volume (don't silently update 2M records).

**Anti-patterns** — full-refresh syncs that burn API limits; no dead-letter for rejected rows so failures vanish; syncing un-deduped Silver instead of governed Gold; treating it as fire-and-forget with no replay.

**Tools (2025-2026)** — **Hightouch** (broadest destination coverage), **Census** (strongest dbt-native workflows, faster event syncs); both lean on warehouse-native compute. DIY with Airflow/dbt + vendor APIs only when volume is tiny.

- https://hightouch.com/blog/reverse-etl
- https://www.getcensus.com/product/reverse-etl

---

## 4. Tools Landscape (2026)

### Lakehouse storage
- **Apache Iceberg** — leading open format
- **Delta Lake** — strong if on Databricks
- **Apache Hudi** — niche for streaming upserts

### Catalogs
- **Hive Metastore** — legacy
- **AWS Glue Catalog** — AWS-native
- **Unity Catalog** — Databricks; open source 2024+
- **Iceberg REST Catalog** — emerging multi-vendor standard
- **Polaris** (Snowflake-led OSS) — Iceberg REST catalog

### Compute engines
- **Spark** — workhorse
- **Trino / Starburst** — interactive querying over open formats
- **Flink** — streaming
- **Beam (Dataflow)** — unified
- **DuckDB** — local + embedded analytics
- **Polars** — fast DataFrame for single-node

### Transformation
- **dbt** — standard
- **SQLMesh** — newer, semantic
- **Dataform** — GCP-native dbt-like
- **Materialize** — streaming SQL

### Vendor warehouses
- **BigQuery / Snowflake / Databricks SQL / Redshift / Synapse**

### Streaming
- **Kafka** — log standard
- **Pulsar** — multi-tenant alternative
- **Kinesis** — AWS-native
- **Pub/Sub** — GCP-native
- **Redpanda** — Kafka-compatible, simpler ops

### Quality + observability
- **dbt tests** — minimum
- **Soda** — DQ as code, growing
- **Great Expectations** — flexible
- **Monte Carlo** (commercial) — observability + lineage
- **Datafold** — diff + lineage
- **OpenLineage** — open standard

### Format
- **Parquet** — columnar; default for analytics
- **ORC** — columnar; Hive-heritage
- **Avro** — row + schema; default for Kafka
- **JSON** — easy + bloated
- **Iceberg / Delta / Hudi** — table formats over Parquet

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| SELECT * everywhere | Scan more than needed | Project only needed columns |
| No partition column on big tables | Full table scan | Partition by date / tenant |
| Storing JSON blobs in columns | Loses schema, expensive queries | Flatten or use ARRAY/STRUCT |
| Pulling data from prod OLTP in business hours | Hits OLTP performance | CDC + replica + off-peak |
| 100 small files per partition | Small file problem | Compact + bigger partition size |
| Reading wide tables for narrow purposes | Wasted I/O | Layered models — wide silver, narrow gold |
| Mutating Bronze | Breaks audit + replay | Append-only Bronze; mutations in Silver+ |
| Time-of-processing not event-time | Non-deterministic, can't replay | Use event_time consistently |
| No tests | Silent regressions | dbt tests at minimum; GE for rigor |
| One big pipeline | Hard to debug + retry | Decompose into smaller stages |
| Hardcoded credentials | Security nightmare | Secrets manager + IAM |
| Hand-coded incrementals | Bugs in dedup / late data | Use dbt incremental models or framework |

---

## 6. Advanced / Expert Topics

### Iceberg deep

- **Metadata layout** — manifest list → manifests → data files
- **Snapshot isolation** — atomic commits, time travel
- **Hidden partitioning** — `days(ts)`, `bucket(N, col)`
- **Schema evolution** — column IDs
- **Compaction** — rewrite small files; size + sort
- **Branching + tagging** (v3) — WAP, audit branches
- **REST catalog** — emerging standard

### Streaming semantics

- **Watermarks** — declare "no more late data after X"
- **Windowing** — tumbling, sliding, session
- **Exactly-once** — requires idempotent sinks + transactional state
- **State backend** — RocksDB (Flink), Kafka changelog (Kafka Streams)
- **Late arrival handling** — drop, side output, side-table merge

### Backfill at scale

- **Reprocess by partition** — parallel, incremental
- **Replay from CDC log** — for streaming systems
- **Watermark coordination** — for stateful streaming backfills
- Costly + slow; design for minimal backfill needs

### Hot/Cold path (lambda → kappa → unified)

Old lambda: separate batch + streaming pipelines computing same logic. Maintenance nightmare.

Kappa: single streaming pipeline, replay for backfills. Limits depend on engine.

Modern unified: Beam, Flink batch+stream, Spark Structured Streaming with the same code for both modes.

### Data Contracts in DE practice

- Implement as YAML in producer's repo
- CI checks: schema drift, contract test
- Schema registry for runtime enforcement
- Consumer expectations: dbt contracts, GE in downstream

### Cost optimization patterns

- **Partition + cluster** — avoid full scans (biggest lever)
- **Materialize hot queries** — pre-compute frequently asked
- **Right-size compute** — autoscale, spot instances
- **Lifecycle policies** — archive cold data
- **Cluster keys** — physical layout for filter+join
- **Z-ordering / liquid clustering** — multi-dim layout
- **CDC instead of full snapshot** — reduce ingest cost

### Multi-region considerations

- Cross-region egress is expensive (~$0.02-0.20/GB)
- Replicate metadata, not data when possible
- Use CDN / cache for read replicas
- Plan data residency at table level (not just account)

### Debugging slow Spark

Diagnostic order:
1. Skew? (look at task durations in UI)
2. Shuffle volume? (target shuffle partition size ~100MB)
3. AQE enabled?
4. Broadcast applied? (auto for small tables)
5. Predicate pushdown working?
6. Right partition size on source?
7. Memory pressure?

### Real-time architecture (when truly needed)

```
Source → CDC → Kafka → Flink (stateful) → Iceberg (offline) + KV store (online lookup)
```

Add:
- Schema registry
- DLQ for poison records
- Replay tool
- Monitoring per stage

### Late data / out-of-order events (deep)

**What it is** — events arrive after their event-time would suggest: mobile offline buffers, network retries, multi-partition Kafka skew. The watermark is the engine's assertion "no more events ≤ T"; anything behind it is *late*. Out-of-order within the watermark bound is handled transparently; truly late data needs an explicit policy.

**Why it matters** — in production the question is never "if" but "how much, how often, and what do we owe downstream when it's late." A silent drop corrupts revenue/conversion metrics; a too-generous watermark blows up state and delays every window firing.

**Standard patterns + when to use**
- **Bounded-out-of-orderness watermark** — `WatermarkStrategy.forBoundedOutOfOrderness(d)`; size `d` from the observed p99 lateness, not a guess. Bigger `d` = more correctness, more latency + state.
- **Allowed lateness (grace period)** — keep window state past the watermark so late events *re-fire* and correct the window (Flink `allowedLateness`, Spark `withWatermark`). Use when downstream can accept updates/restatements.
- **Side output (side-channel)** — route data later than the grace period to a side stream → DLQ or a late-arrival table merged in a later batch. Use when you must never drop but can't hold state forever. This is the production default.
- **Reprocessing / lambda correction** — a periodic batch job recomputes from the immutable log to absorb stragglers the stream dropped.

**Anti-patterns** — default allowed-lateness of 0 with no side output (silent drop); using processing time then "fixing" it later (non-deterministic, un-replayable); unbounded allowed lateness (state explosion).

- https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/operators/windows/#allowed-lateness
- https://www.decodable.co/blog/understanding-apache-flink-event-time-and-watermarks

### Streaming upsert / dedup semantics (deep)

**What it is** — applying a continuous stream of inserts/updates/deletes into a table format with correct last-writer-wins per key. The two axes: *table type* (read cost vs write cost) and *dedup key + ordering* (which version wins).

**Copy-on-write (CoW) vs merge-on-read (MoR)**
- **CoW** — every update rewrites the whole base Parquet file containing the record. Reads are cheap (plain Parquet); writes amplify. Use for read-heavy, lower-frequency-change tables.
- **MoR** — updates append to delta log files; reads merge base + deltas at query time; async compaction folds them down. Low write latency, higher read cost until compaction. Use for update-heavy / CDC / low-latency streaming sinks. (Iceberg V2 = delete files, Delta = deletion vectors — same idea.)

**Dedup keys** — a **record key** (PK) plus a **precombine / ordering field** (event timestamp or version) so that within a batch and across retries the latest wins. In Hudi this is `recordKey` + `precombine` field; the `UPSERT` op indexes incoming keys to tag insert vs update. Without an ordering field you get nondeterministic "last in microbatch" — a classic CDC bug.

**Flink/Spark upsert** — Flink upsert-kafka / Hudi streaming writer keys on PK; Spark Structured Streaming uses `foreachBatch` + `MERGE INTO`. Exactly-once needs idempotent keyed merge, not just checkpointing.

**Anti-patterns** — no precombine field; MoR with compaction disabled (read cliff); choosing CoW for a high-churn CDC sink (write amplification meltdown).

- https://hudi.apache.org/blog/2025/07/21/mor-comparison/
- https://hudi.apache.org/docs/writing_data.html

### Schema migration of warehouse tables (deep)

**What it is** — propagating upstream OLTP DDL (Postgres/MySQL `ALTER TABLE`) through CDC into lake/warehouse tables without breaking running pipelines or readers. Two distinct problems: (a) safely changing the *source* OLTP under load, (b) absorbing that change downstream.

**Expand-contract (parallel-change)** — the only safe way to do a breaking change online:
1. **Expand** — add the new column/table alongside the old; backfill; dual-write or compute both.
2. **Migrate** — switch all readers/writers to the new shape behind the scenes.
3. **Contract** — once nothing references the old element, drop it.
Never rename-in-place: model a rename as add-new + backfill + cutover + drop-old.

**Online schema change on the source (MySQL)** — when native online DDL can't keep an ALTER online, use **gh-ost** (triggerless, reads the binlog, applies to a ghost table async — lower production impact) or **pt-online-schema-change** (trigger-based, synchronous). For Postgres, **pgroll** implements expand/contract natively with versioned views.

**Propagation to the warehouse** — additive changes are safe: Debezium emits the new field, schema-registry compatibility = `BACKWARD`, sink does `ALTER TABLE ADD COLUMN`. Keep downstream **dbt models / contracts** stable by selecting explicit columns, not `SELECT *`, so a new upstream column never silently reshapes Gold. Iceberg/Delta column-IDs make adds/drops/reorders safe by construction.

**Anti-patterns** — destructive ALTER on a live OLTP table holding a metadata lock; relying on `SELECT *` so schema drift leaks into marts; no schema-registry compatibility mode so a producer breaks every consumer.

- https://github.com/github/gh-ost
- https://www.prisma.io/dataguide/types/relational/expand-and-contract-pattern

---

## 7. References

### Books
- **Fundamentals of Data Engineering** — Reis, Housley
- **Designing Data-Intensive Applications** — Kleppmann
- **The Data Engineering Cookbook** — Andreas Kretz (free)
- **Streaming Systems** — Akidau, Chernyak, Lax

### Blogs / Newsletters
- **Maxime Beauchemin** — Functional Data Engineering
- **Joe Reis** — Data engineering practice
- **Modern Data 101** (Substack)
- **dbt blog**
- **Databricks Engineering blog**

### Communities
- **dbt Slack** — community
- **Locally Optimistic** — Slack, podcast
- **Data Council** — conference
- **Apache mailing lists** (Iceberg, Spark, Flink)

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| Data Architect | "Here's the design — what's the implementation plan?" |
| Solution Architect | "Where does this pipeline fit in the system?" |
| Analytics Engineer / Data Analyst | "Here's the data — what's it shaped like for BI?" |
| ML Engineer | "Here's the feature pipeline — is the schema stable?" |
| Data Ops | "Pipeline reliability + monitoring plan" |
| DBA | "OLTP impact of CDC?" |
| Governance | "PII handling, lineage hooks" |

---

*Data engineering = software engineering applied to data. Be a good software engineer first.*
