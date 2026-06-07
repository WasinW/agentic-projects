# Technical Clarification — Answers

> Based on real experience from NTT DATA (The 1 Central Group) and SCB Data-X projects.
> Written to be honest — areas where experience is indirect are noted.

---

## 1. Most Complex Lakehouse Project — End-to-End Architecture

**Project:** Loyalty Data Platform — The 1 Central Group (NTT DATA, 2025–Present)

**Context:** The 1 is Thailand's largest retail loyalty program. The platform needed to ingest real-time member activity from Confluent Kafka and daily batch data from PostgreSQL and REST APIs into a queryable analytics layer for downstream teams.

**End-to-End Architecture:**

```
[Sources]                    [Processing]              [Storage - Two-Layer Lakehouse]
Confluent Kafka ──────┐
  (Avro/JSON)         ├──→ Apache Beam ──→ Dataflow ──→ Apache Iceberg (GCS)  ← Source of truth
PostgreSQL ───────────┤      (Python)                    │
REST APIs ────────────┘                                  ↓ (refined transforms)
                                                       BigQuery (CDC)  ← Analytics/refined layer
```

- **Storage:** Google Cloud Storage (GCS) as Iceberg warehouse, BigQuery as the refined analytics layer.
- **Compute:** Apache Beam pipelines running on Google Cloud Dataflow (both streaming and batch runners).
- **Table Format:** Apache Iceberg for the source layer — chosen for schema evolution support, time-travel, and decoupling storage from compute.
- **Catalog:** Migrated from Hadoop Catalog to BigLake Managed Storage (BLMS) REST Catalog with Google-managed vended credentials. This was a significant migration — the Hadoop Catalog required manual metadata management and lacked native GCP integration, while BLMS REST provides automatic catalog registration, IAM-based access control, and seamless BigQuery interop.
- **Partitioning:** Iceberg tables partitioned by ingestion date (integer YYYYMMDD) for the source layer. BigQuery refined tables partitioned by DATE (DAY granularity) with clustering on high-cardinality lookup fields (e.g., member ID, tier code).
- **Write Pattern:** Apache Beam's `managed.Write` transform with IcebergIO — the pipeline writes directly to Iceberg via BLMS REST, and the table is auto-created on first write if it doesn't exist. This eliminated the need for manual table bootstrapping scripts.

**Small-File and Read-Performance:**

Iceberg's small-file problem is inherent to streaming writes — each Dataflow worker produces small Parquet files per commit. In our case:
- **Managed.Write handles file sizing** — Beam's managed Iceberg writer batches records before committing, reducing file count compared to per-record writes.
- **Partition strategy** — By partitioning on DAY (not HOUR), we reduced the number of partitions and concentrated files into fewer directories.
- **Read performance** — The primary read path is BigQuery (refined layer), not Iceberg directly. BigQuery reads from Iceberg via BigLake external tables, and BigQuery's query engine handles file scanning efficiently. For the Iceberg source layer, read access is primarily for reconciliation and debugging, not production analytics queries.

> **Honest note:** We haven't needed to implement explicit compaction jobs yet — the current data volume doesn't create severe small-file issues. If it scales, Iceberg's `rewrite_data_files` or a scheduled compaction pipeline would be the next step.

---

## 2. CDC, Schema Evolution, and Deterministic Replay

**CDC Implementation (The 1 — NTT DATA):**

We implemented CDC at the BigQuery refined layer using BigQuery's Storage Write API with primary keys:

- **UPSERT pattern:** Each refined BigQuery table has a defined primary key (e.g., composite key of member_id + tier_code for member_tier, or tierMaintenanceId for maintenance records). Incoming records are written with CDC semantics — BigQuery deduplicates by primary key automatically.

- **DELETE pattern:** For the member_tier table, we needed to handle tier removal events. When a member loses a tier, the Kafka event carries the tier code, but the upstream API no longer returns that tier. We implemented a verification flow:
  - The pipeline receives a Kafka event with a tier code.
  - It calls the upstream Loyalty API — if the tier is not found in the API response, it's a potential DELETE.
  - Before issuing the DELETE, the pipeline queries BigQuery to confirm the record actually exists (preventing phantom deletes).
  - Only if all three checks pass does the pipeline emit a CDC DELETE mutation.

  This was a real design challenge — a naive approach would delete records incorrectly during API outages or race conditions. The three-layer check ensures we only delete what we're confident has been removed.

- **CDC table setup:** Primary keys declared as `NOT ENFORCED` in BigQuery (BigQuery doesn't enforce uniqueness, but Storage Write API uses them for CDC semantics). Write mode set to CDC in pipeline configuration.

**Schema Evolution:**

- **Iceberg layer:** Schema evolution is handled by `managed.Write` — if new fields appear in the data, Iceberg's schema evolution adds them automatically. We also explicitly control schema through PyArrow schema definitions in the pipeline code to prevent unintended drift.
- **BigQuery layer:** Schema changes are managed through deployment tooling — `deploy.py` compares the live BigQuery schema against the JSON schema definitions in the repo, and issues `ALTER TABLE ADD COLUMN` for new fields. Existing columns are never dropped or modified in-place to preserve backward compatibility.
- **Real example:** We renamed the partition field from `etlLoadTime` (INT, YYYYMMDDHH, HOUR partition) to `ingestedTHDate` (INT, YYYYMMDD / DATE, DAY partition) across 14 files. This required coordinated changes across Iceberg writer configs, BigQuery schemas, SQL initialization scripts, and pipeline transforms — with 220 tests validating correctness.

**Deterministic Replay:**

- **Streaming pipelines:** Dataflow provides exactly-once processing guarantees with checkpointing. If a pipeline fails and restarts, it resumes from the last Kafka offset committed. Combined with CDC UPSERT semantics in BigQuery, replayed records overwrite themselves — making the output idempotent.
- **Batch pipelines:** Parameterized by date — re-running with the same date produces the same output. The batch pipeline queries PostgreSQL with `WHERE date BETWEEN start AND end`, making it deterministic given the same input window.

> **Honest note:** We don't use Talend. Our CDC and replay approach is built natively on Apache Beam + Dataflow + BigQuery Storage Write API.

---

## 3. Data-Freshness SLAs — Ingestion Cadence, Streaming vs Batch

**SLA Design (The 1 — NTT DATA):**

We have two freshness tiers:

| Pipeline | Type | Cadence | Target Freshness |
|----------|------|---------|-----------------|
| Members (tier events) | Streaming | Continuous | Near real-time (seconds to minutes) |
| Tiers (master data) | Batch | Daily 1AM BKK (UTC+7) | D-1 |
| Members-Tiers-History | Batch | Daily 1AM BKK (UTC+7) | D-1 |

**Streaming (Members Collector):**
- Confluent Kafka consumer running on Dataflow streaming runner.
- Dataflow manages checkpointing automatically — Kafka offsets are committed after successful processing.
- Watermarking is handled by Beam's windowing — we use GlobalWindows for the Iceberg write (append-only), while the BigQuery refined write uses the event timestamp for partition assignment.
- The pipeline runs continuously — no micro-batch scheduling. Data is available in BigQuery within minutes of the Kafka event being produced.

**Batch (Tiers + Members-Tiers-History):**
- Triggered by Cloud Scheduler at 1AM Bangkok time daily.
- The pipeline reads from the upstream source (REST API for tiers, PostgreSQL for history), processes, and writes to Iceberg + BigQuery.
- "D-1" means data from yesterday is available by early morning — downstream analysts have fresh data when they start their day.

**Streaming vs Batch Decision:**
- Member tier events are streaming because they're business-critical for real-time personalization — when a member upgrades/downgrades, the loyalty platform needs to reflect this quickly.
- Tiers master data and history are batch because they change infrequently (tiers structure changes rarely, history is append-only) — a daily load is sufficient and simpler to operate.

**Checkpointing:**
- Streaming: Dataflow's built-in checkpointing with Kafka offset tracking. If the pipeline crashes, it resumes from the last committed offset.
- Batch: No checkpointing needed — the pipeline is idempotent. Re-run = same result.

---

## 4. Data Quality and Observability Stack

**Pipeline-Level Quality (The 1 — NTT DATA):**

- **Schema validation at ingestion:** Each pipeline validates incoming messages against expected schemas. Multi-format auto-detection (flat JSON, nested payload, stringified wrapper) ensures we handle all Kafka message variants without silent data loss.
- **Transform validation:** Transformers include explicit checks — null handling, type coercion, timezone conversion (UTC → Bangkok UTC+7). Invalid records are logged rather than silently dropped.
- **CDC consistency checks:** The 3-layer CDC DELETE validation (Kafka event → API verification → BigQuery existence check) is itself a data quality measure — preventing false deletes.

**Testing as Quality Gate:**
- 600+ unit tests (pytest) across all pipeline projects — covering message parsing, API integration, CDC logic, schema validation, timestamp handling, and edge cases.
- Static typing (mypy) catches type mismatches at development time.
- Linting (ruff) and SonarQube enforce code quality standards.
- Pre-commit hooks + GitLab CI ensure no untested code reaches production.

**Monitoring and Observability:**
- Dataflow provides built-in metrics: throughput, latency, backlog size, error counts — visible in GCP Console.
- Pipeline failures trigger Dataflow alerts.
- For batch pipelines, Cloud Scheduler + Dataflow job status provides basic freshness monitoring — if the daily job doesn't complete by expected time, it's visible.

**Data Platform Level (SCB Data-X):**
- At SCB, data validation was a core deliverable — validation processes on Azure Databricks checked row counts, null ratios, schema consistency between source databases and data warehouse.
- Schema synchronization processes (PySpark on Databricks) ensured data consistency across databases and data warehouses — detecting and reconciling schema drift.

> **Honest note:** We don't have a dedicated observability platform (like Monte Carlo or Great Expectations) at The 1 project. Observability relies on Dataflow built-in metrics + manual monitoring. This is an area for improvement — I'd recommend adding structured DQ metrics (row counts, null rates, freshness timestamps) and alerting via Cloud Monitoring.

---

## 5. Performance Tuning on a Terabyte-Scale Spark Job

**Context (SCB Data-X — RDT Project):**

The Regulatory Data Transformation (RDT) project at SCB processed banking regulatory data on Azure Databricks using PySpark. The datasets were large (multi-TB scale from transaction and account data across SCB's banking systems).

**Bottlenecks encountered:**
- **Shuffle-heavy joins:** Regulatory models required joining multiple source tables (accounts, transactions, customers). Naive joins caused excessive shuffle, with Spark stages spending most time on network I/O.
- **Skewed keys:** Certain account types (e.g., corporate accounts) had disproportionately more transactions, causing task skew in joins.
- **Schema sync overhead:** The schema synchronization process compared schemas across databases and data warehouse, which on large datasets involved full-table scans.

**Fixes applied:**
- **Broadcast joins:** For smaller dimension tables (reference/lookup tables), used broadcast hints to eliminate shuffle entirely — the driver broadcasts the small table to all executors.
- **Partition pruning:** Ensured partition columns were used in filter predicates so Spark could skip irrelevant partitions during reads.
- **Repartitioning before joins:** For large-to-large joins, repartitioned both sides on the join key before the join to reduce shuffle volume — co-locating matching keys on the same partitions.
- **Caching intermediate results:** For models that reuse the same transformed dataset multiple times, cached the intermediate DataFrame to avoid recomputation.

**Apache Beam / Dataflow context (The 1 — NTT DATA):**

On Dataflow (not Spark, but similar performance principles):
- **Fan-out optimization:** Instead of processing each output table in a separate pipeline (4x Kafka reads), designed a fan-out pattern — one Kafka consumer, branching to multiple writers. This reduced Kafka read load and Dataflow worker count.
- **Cross-bundle deduplication:** Replaced per-bundle in-memory dedup (which missed duplicates across bundles) with `beam.Distinct()` (GroupByKey-based) for reliable cross-bundle deduplication — eliminating duplicate API calls and writes.
- **Partition field optimization:** Switched from HOUR to DAY partition granularity to reduce the number of Iceberg file commits and BigQuery partition maintenance.

> **Honest note:** My deepest Spark tuning experience is from SCB Data-X on Databricks. At The 1, the compute engine is Apache Beam on Dataflow, where performance tuning is more about pipeline topology (fan-out, dedup strategy, worker scaling) than Spark-specific knobs (shuffle partitions, join strategies).

---

## 6. Data Governance — PII Masking and Access Control

**SCB Data-X (Banking — High Sensitivity):**

Banking data at SCB has strict regulatory requirements (Bank of Thailand regulations).

- **RBAC implementation:** Developed Role-Based Access Control processes on Azure Databricks. Different teams (risk, compliance, analytics) had different access levels to the same datasets. Implemented through Databricks workspace permissions and Unity Catalog access policies.
- **Data classification:** Part of the RDT CardX project — profiled data sources to classify fields by sensitivity level before migrating to the new platform.

**The 1 — NTT DATA (Retail Loyalty):**

- **Secret management:** All credentials (Kafka, API, database) stored in GCP Secret Manager, referenced by service account — no secrets in code or config files.
- **IAM per-collector:** Each pipeline (collector) has its own GCP service account with least-privilege access. IAM bindings are defined in Terraform (`biglake-metastore.tf` per collector) — a collector can only access its own datasets in BigLake and BigQuery.
- **Network isolation:** Dataflow jobs run in specific VPC subnets with controlled network access.

> **Honest note:** I haven't implemented column-level PII masking (e.g., dynamic masking, tokenization) at production scale. My governance experience is primarily at the access control and infrastructure level (RBAC, IAM, secret management). For PII masking specifically, I understand the patterns (BigQuery column-level security, policy tags, Data Catalog) but haven't implemented them end-to-end in production.

---

## 7. Production Incident — Impact on Data Freshness

**Incident: Schema C — Stringified Kafka Messages in STG (The 1, 2025)**

**What happened:**
After deploying the members-collector to STG for the first time, the pipeline started successfully but produced empty/null fields in the BigQuery refined tables. The Iceberg source layer showed double-nested payload structures that didn't match the expected schema.

**Triage:**
1. Checked Dataflow logs — no errors, pipeline running normally.
2. Inspected Iceberg source data — found `payload.payload.{actual_fields}` instead of `payload.{actual_fields}`.
3. Inspected raw Kafka messages — discovered messages arrived in an unexpected format: `{"message": "<stringified JSON>"}` where the inner value was a **string**, not a parsed JSON object.
4. Root cause: The Kafka producer (not our team) was wrapping messages in an outer `message` key with the original JSON serialized as a string. Our pipeline only handled two formats (flat JSON and nested `payload` dict) — this third format was undocumented.

**Fix:**
Added a three-schema detection flow in the message transformer:
1. **Schema C** (new): detect `message` key with string value → parse the string → extract inner payload.
2. **Schema B**: detect `payload` key as dict → unwrap inner payload.
3. **Schema A**: flat message → wrap as payload.

The fix was deployed the same day. Added 3 regression tests specifically for Schema C.

**Prevention:**
- Added explicit schema detection tests for all known message formats.
- Coordinated with the Kafka platform team to document all message envelope formats.
- The multi-format auto-detection pattern is now the standard for all Kafka consumers — it handles unknown wrappers gracefully rather than silently corrupting data.

**Incident: Kafka Config Migration — Silent Timeout (The 1, 2025)**

**What happened:**
After migrating Kafka credential structure in Secret Manager (key renamed from `kafka_connection` to `kafkaCredentials`), the pipeline deployed successfully but Kafka consumer silently timed out — no events were being read.

**Triage:**
1. Pipeline showed no errors — Dataflow job was "running" but processing zero records.
2. Checked Kafka consumer lag — growing, meaning the consumer wasn't reading.
3. Found that the pipeline code was still reading the old secret key name — the secret existed but contained no value under the new structure, so the Kafka client initialized with empty credentials and timed out.

**Fix:**
Updated the secret key references in the pipeline configuration. Added validation in the pipeline startup to fail-fast if credential fields are empty or missing.

**Prevention:**
- Added configuration validation at pipeline initialization — if required secret fields are empty, the pipeline fails immediately with a clear error instead of silently degrading.
- Documented the secret key structure and included it in the deployment checklist.
