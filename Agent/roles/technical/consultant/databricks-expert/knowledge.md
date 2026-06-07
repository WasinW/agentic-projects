# Databricks Expert — Comprehensive Knowledge

> Deep reference for the databricks-expert subagent. Production Databricks Lakehouse for data + AI. This is the vendor-specific counterweight to the Iceberg/open-table-format material elsewhere in the repo.

---

## 1. Foundations

### What Databricks actually is

Databricks = a **lakehouse control plane** layered on top of cloud object storage. The mental model:

```
Control plane (Databricks-managed account)
 ├── Unity Catalog (metastore, governance, lineage)
 ├── Workspace(s)  ← notebooks, jobs, SQL, ML
 └── Job scheduling, cluster orchestration, web UI
Data plane (your cloud account)
 ├── Compute (clusters / serverless / SQL warehouses)
 └── Object storage (ADLS / S3 / GCS) holding Delta/Parquet files
```

The **storage layer is open** (Delta Lake on Parquet, you own the files). The **runtime + control plane are proprietary** (Photon, predictive optimization, the orchestration). Hold this distinction — every lock-in debate hinges on it (§5, §6).

### The open-core lineage

Databricks created and open-sourced the load-bearing primitives: **Apache Spark**, **Delta Lake**, **MLflow**, and now **Unity Catalog (OSS)** and **Spark Declarative Pipelines** (contributed to Apache Spark at DAIS 2025). The commercial product wraps these with proprietary accelerators. This is deliberate: OSS = adoption funnel + storage-layer portability; proprietary = differentiation + performance-based stickiness.

### Positioning vs the field

| | Databricks strength | Weaker |
|---|---|---|
| Spark / ML maturity | Best-in-class, the original | — |
| Lakehouse single-platform | Data eng + BI + ML + GenAI in one | Sprawl risk if undisciplined |
| Multi-cloud | Runs on Azure / AWS / GCP, same UX | Control plane still Databricks-hosted |
| Open formats | Delta OSS + UniForm + Iceberg interop | Runtime perf is proprietary |
| Governance | Unity Catalog is genuinely strong | UC gravity = lock-in vector |
| Cost transparency | DBU model, serverless helps | Easy to overspend without FinOps |

Strong for serious data-engineering + ML/AI shops, regulated enterprise (banking incl. The-1 / BoT / PDPA context), and anyone who outgrew a pure-warehouse story.

---

## 2. Mental Models / Decision Frameworks

### Compute selector

| Need | Choice |
|---|---|
| Interactive notebook dev | All-purpose cluster (or serverless notebooks) |
| Production batch / ETL | Job cluster (ephemeral, cheapest per run) |
| BI / SQL analytics | **Databricks SQL Warehouse** (Serverless > Pro > Classic) |
| Declarative ETL pipeline | **Lakeflow Declarative Pipelines** (ex-DLT) |
| Low-latency, no cold start | **Serverless** compute (DBSQL serverless, serverless jobs) |
| Heavy SQL/aggregation | Anything **Photon**-enabled |
| ML training | ML Runtime cluster (GPU for DL) |
| Model inference | **Mosaic AI Model Serving** |

Default for new ETL in 2026: **Lakeflow Declarative Pipelines on serverless**, governed by Unity Catalog. Default for BI: **Serverless SQL Warehouse**.

### Table-layout decision (this is where people waste money)

| Situation | Do |
|---|---|
| New table, 2026 | **Liquid clustering** — don't partition, don't ZORDER |
| Legacy partitioned table | Migrate to liquid clustering (no full rewrite needed) |
| High-cardinality query predicates | Liquid clustering keys on those columns |
| Frequent point DELETE/UPDATE/MERGE | Ensure **deletion vectors** ON (default on recent runtimes) |
| Need downstream CDC | Enable **Change Data Feed** |
| Maintenance burden | Use **UC managed tables** + **Predictive Optimization** (auto OPTIMIZE/VACUUM/ANALYZE) |

### Delta vs Parquet (the one-liner clients always ask)

Parquet = columnar file format, no transactions, no time travel, no schema enforcement. Delta = Parquet **plus a transaction log** (`_delta_log`) giving ACID, time travel, MERGE, CDF, schema evolution. You never choose "raw Parquet" for a managed table on Databricks — Delta is strictly a superset with negligible overhead.

### Table format strategy (the portability fork)

```
Want max Databricks performance + governance → Delta managed tables in UC
Need Iceberg readers (Snowflake/Trino/Dremio) → Delta + UniForm (read as Iceberg)
Need Iceberg writers / multi-engine writes → UC managed Iceberg + Iceberg REST Catalog
Truly engine-neutral, Databricks optional → external Iceberg, UC as REST catalog
```

This is the single most important architecture conversation for avoiding lock-in (§6).

### Banking / regulated specific (The-1, BoT, PDPA)

- Unity Catalog as the single governance plane: lineage for BCBS-239-style audit, ABAC tags for PII, row/column masking for PDPA.
- Data classification auto-labels PII → ABAC policies enforce masking at scale.
- Audit logs → SIEM. Customer-managed keys on storage. Private networking (Private Link / VNet injection).

---

## 3. Standard Practices

### Delta Lake operations

- **`_delta_log`**: JSON commits + periodic Parquet checkpoints. This is the source of truth — file listing is never trusted directly. Atomicity via optimistic concurrency on the log.
- **OPTIMIZE**: compacts small files. **ZORDER**: multi-dim clustering — *legacy*, superseded by liquid clustering for new tables.
- **Liquid clustering**: `CLUSTER BY` — replaces both partitioning and ZORDER; clustering keys are **redefinable without rewriting data**; incremental on writes. Use it by default.
- **VACUUM**: removes files past retention (default 7 days). Don't set retention too low or you break time travel + concurrent readers.
- **Time travel**: `VERSION AS OF` / `TIMESTAMP AS OF` — for audits, reproducibility, rollback.
- **MERGE**: upsert / SCD. With deletion vectors + Photon predictive I/O it's dramatically faster (no full-file rewrites on small changes).
- **Change Data Feed (CDF)**: `delta.enableChangeDataFeed = true` → read only changed rows between versions via `table_changes()`. Backbone of incremental downstream pipelines + CDC fan-out.
- **Deletion vectors**: soft-delete marker files so DELETE/UPDATE/MERGE mark rows instead of rewriting whole Parquet files (merge-on-read). Default-on for new tables on recent runtimes; Photon reads them natively.

### Unity Catalog

- **Three-level namespace**: `catalog.schema.table`. One metastore per region, shared across workspaces.
- **Governance objects**: catalogs, schemas, tables, views, volumes (for non-tabular files), functions, models, **external locations** + **storage credentials**.
- **Lineage**: automatic table + column-level lineage across notebooks, jobs, pipelines, dashboards.
- **ABAC** (GA 2025): tag-driven **row filter** and **column mask** policies. One policy covers thousands of matching tables — far more scalable than per-table functions. Needs DBR 16.4+ or serverless.
- **Governed tags + data classification** (GA 2025): auto-discovers/labels sensitive columns (GDPR, HIPAA, GLBA, PCI, DPDPA classifiers) → feeds ABAC.
- **RLS/CLS**: row filters + column masks, via ABAC (preferred) or legacy UDF-based functions.
- **Audit**: system tables (`system.access.audit`) + delivery to your SIEM.

### Lakeflow (the ETL stack)

- **Lakeflow Connect**: managed ingestion connectors (DBs, SaaS, files).
- **Lakeflow Declarative Pipelines** (= the renamed **DLT**; backward compatible, zero migration): declare target tables, the engine figures out execution/dependencies/incrementalization. **Expectations** = declarative data-quality constraints (`EXPECT`, drop/fail/quarantine on violation).
- **Lakeflow Jobs** (= Databricks Workflows / Jobs): general orchestration — multi-task DAGs, retries, conditional/if-else, for-each, scheduling, alerting.
- **Structured Streaming**: native Spark streaming; pairs with Delta + CDF + Auto Loader for incremental ingest. Medallion (bronze/silver/gold) is the standard layering.

### Databricks SQL

- **Serverless / Pro / Classic** warehouses. Default to **Serverless** (instant start, auto-scale, lowest idle waste) unless a hard data-residency constraint forces classic.
- Photon under the hood; Photon vectorized shuffle auto-applied to serverless (≈25% gains, no config).
- Surfaces: SQL editor, dashboards, alerts, **AI/BI Genie** (NL-to-SQL).

### Cluster / cost hygiene

- Job clusters for production (ephemeral, no idle cost). All-purpose only for dev.
- Autoscaling + auto-termination on everything interactive.
- Spot/preemptible for fault-tolerant batch; on-demand for drivers.
- Tag clusters/jobs for chargeback; watch **DBU** consumption per workload.

---

## 4. Tools Landscape 2026

### Storage / table format
- **Delta Lake** — default table format (ACID on Parquet, `_delta_log`)
- **Liquid clustering** — GA (DBR 15.2+); replaces partitioning + ZORDER
- **Deletion vectors** — merge-on-read soft deletes, Photon-accelerated
- **Change Data Feed** — row-level change capture
- **Delta UniForm** — auto-generates Iceberg (and Hudi) metadata over one Parquet copy
- **UC managed Iceberg** — native Iceberg tables governed by UC

### Compute / engine
- **Photon** — proprietary C++ vectorized engine; the performance moat
- **Serverless** — DBSQL serverless, serverless jobs/notebooks/pipelines
- **Predictive Optimization** — GA 2025; auto OPTIMIZE/VACUUM/ANALYZE on UC managed tables, default-on for new accounts
- **Spark Declarative Pipelines** — OSS core of Lakeflow (contributed to Apache Spark, DAIS 2025)

### Governance
- **Unity Catalog** — metastore, lineage, ABAC, tags, classification, audit, volumes
- **Iceberg REST Catalog (IRC)** — UC exposes tables to external Iceberg/Delta clients; read for both, write for Iceberg (PrPr→broadening)
- **Delta Sharing** — open protocol for cross-org/cross-platform data sharing
- **Clean Rooms** — privacy-preserving multi-party compute

### Orchestration / ETL
- **Lakeflow Connect** — managed ingestion
- **Lakeflow Declarative Pipelines** — declarative ETL (ex-DLT) + expectations
- **Lakeflow Jobs** — workflow DAGs (ex-Workflows)
- **Auto Loader** — incremental file ingestion

### AI / ML (Mosaic AI)
- **Mosaic AI Vector Search** — GA; rewritten storage-optimized engine, billions of vectors, ~7x lower cost
- **Mosaic AI Model Serving** — GA; 250k+ QPS, in-house inference engine ~1.5x faster than vLLM-v1 on Llama
- **Mosaic AI Gateway** — GA; unified entry point, provider fallback, PII/safety guardrails, rate limits, usage logging
- **Agent Bricks / Agent Framework** — build + eval + deploy agents; UC functions, Genie, Vector Search exposed as **MCP servers**
- **MLflow** — experiments, registry (UC-backed), eval; the ML lifecycle backbone
- **AI Functions** — `ai_query()` etc. — LLM calls from SQL

### BI / consumption
- **AI/BI Dashboards** + **Genie** (NL analytics)
- **Databricks Apps** — host data/AI apps in-platform
- Partner BI: Power BI, Tableau via SQL warehouses

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Partitioning new Delta tables | Small-file skew, rigid, hard to change | **Liquid clustering** (`CLUSTER BY`) |
| ZORDER on new tables | Legacy, manual tuning | Liquid clustering |
| Manual OPTIMIZE/VACUUM cron everywhere | Toil, missed tables | **Predictive Optimization** on UC managed tables |
| All-purpose clusters for production jobs | Idle cost, noisy-neighbor | Ephemeral **job clusters** |
| Hive metastore in 2026 | No lineage/ABAC/fine-grained governance | Migrate to **Unity Catalog** |
| Per-table RLS UDFs at scale | Unmanageable at thousands of tables | **ABAC** tag-driven policies |
| DELETE/MERGE without deletion vectors | Full-file rewrites, slow | Enable deletion vectors |
| Reprocessing whole tables for "incremental" | Cost + latency | **CDF** + Structured Streaming |
| VACUUM retention set very low | Breaks time travel + concurrent reads | Keep ≥7 days unless you understand the risk |
| Classic SQL warehouse left running | Idle DBU burn | **Serverless** auto-stop |
| Treating UniForm as a write path for Iceberg | UniForm is read-as-Iceberg only | Use **UC managed Iceberg** for Iceberg writes |
| Assuming "Delta is open ⇒ no lock-in" | Runtime perf (Photon/PO/DLT) is proprietary | Plan portability explicitly (§6) |
| Notebooks as production code | No tests, no CI | Repos + DABs (Asset Bundles) + CI/CD |
| Secrets in notebooks | Leakage | Databricks secret scopes / cloud KMS |

---

## 6. Advanced / Expert Topics

### The lock-in reality — be honest with clients

Databricks lock-in is **layered**, and the layers detach at very different costs:

- **Storage layer — low lock-in.** Delta is OSS, Parquet is portable, you own the files in your bucket. UniForm + Iceberg REST make the *data* genuinely multi-engine readable.
- **Governance layer — medium-to-high (Unity Catalog gravity).** Lineage, ABAC, classification, audit, Delta Sharing all live in UC. Reproducing this elsewhere is real work; UC becomes the center of organizational gravity.
- **Runtime layer — high.** **Photon**, **Predictive Optimization**, **Lakeflow Declarative Pipelines**, adaptive execution — these only run on Databricks. Your *data* is portable; your *performance and pipeline logic* are not. This is "performance-based lock-in."
- **Control plane — structural.** Orchestration, workspaces, job scheduling are Databricks-hosted across all three clouds. Multi-cloud means "same Databricks on any cloud," not "leave Databricks easily."

**Consultant framing**: portability is a spectrum you design for, not a checkbox. If a client demands a genuine exit path, keep transforms in OSS Spark / Spark Declarative Pipelines (avoid heavy DLT-specific magic), store as Iceberg or Delta+UniForm, and treat UC as a REST catalog rather than the sole governance brain. Accept you forfeit some Photon/PO performance for that optionality.

### UniForm + Iceberg REST Catalog interop (the portability lever)

- **UniForm**: one copy of Parquet; Databricks auto-generates Iceberg (and Hudi) metadata alongside the Delta log. External Iceberg readers (Snowflake, Trino, Dremio, Spark, DuckDB, Daft) read the *same files* — no second copy, no ETL. **Read path only** for Iceberg clients.
- **UC Iceberg REST Catalog (IRC)**: UC speaks the Iceberg REST API + credential vending. External engines get **read** access to Delta (UniForm) tables and **read/write** to UC managed **Iceberg** tables — while UC still runs liquid clustering, predictive optimization, snapshot expiration, compaction underneath.
- **Net**: this is Databricks' answer to the Iceberg-vs-Delta format war — "you don't have to choose, our tables are readable as Iceberg." For the portability debate it genuinely lowers the storage-layer lock-in, but does **not** touch runtime/control-plane lock-in.

### Multi-cloud deployment

| | Azure Databricks | Databricks on AWS | Databricks on GCP |
|---|---|---|---|
| Status | 1st-party Azure service (Microsoft-sold) | Most mature, broadest features | Fully supported, smaller footprint |
| Identity | Entra ID native | IAM + SCIM | Google IAM + SCIM |
| Storage | ADLS Gen2 | S3 | GCS |
| Networking | VNet injection, Private Link | VPC, PrivateLink | VPC, Private Service Connect |
| Net | Best for Microsoft-aligned/regulated (The-1 context) | Default for AWS-native | OK if GCP-committed |

Same Lakehouse UX everywhere; feature parity is close but AWS often leads on new GA. The control plane is Databricks-hosted regardless of cloud — multi-cloud ≠ exit hatch.

### Medallion + streaming pattern (canonical)

```
Source → Auto Loader → Bronze (raw, append) 
       → Silver (cleaned, deduped, CDF/MERGE, expectations) 
       → Gold (business aggregates, served via DBSQL / Genie / BI)
```
Lakeflow Declarative Pipelines expresses all three layers declaratively; CDF carries incremental changes between them; Predictive Optimization keeps file layout healthy.

### Mosaic AI / GenAI stack (deep)

- **RAG**: Vector Search (governed by UC, embeddings synced from Delta) + Model Serving + AI Gateway in front.
- **AI Gateway** as the control point: every LLM call (in-house or external OpenAI/Anthropic) routed through one governed gateway — guardrails, PII redaction, fallback, rate limits, usage logs. For regulated clients this is the compliance choke point for GenAI.
- **Agents**: Agent Framework + Mosaic AI Evaluation; UC functions / Genie / Vector Search exposed as **MCP servers** so agents call governed tools. Lineage + UC permissions apply to AI assets too.

### Predictive Optimization + managed tables

UC **managed tables** (Databricks owns file layout) + Predictive Optimization = the engine auto-runs OPTIMIZE/VACUUM/ANALYZE on serverless, picks clustering, collects stats — no manual maintenance jobs. Default-on for accounts since Nov 2024; existing accounts enabled through 2025. Strong reason to prefer managed over external tables when you don't need external-engine writes.

### Cost optimization

- **Serverless everywhere** it fits — kills idle warehouse/cluster burn.
- **Job clusters** (ephemeral) for production; never all-purpose.
- **Predictive Optimization** instead of hand-rolled maintenance jobs.
- **Liquid clustering** to avoid small-file explosions (cheaper scans).
- **Spot** for fault-tolerant batch; right-size + autoscale.
- **DBU tagging** + system billing tables for chargeback/FinOps.
- Photon raises DBU/hour but usually cuts total runtime — measure $/query, not $/hour.

### Migration plays

- **Hive metastore → Unity Catalog**: the foundational 2026 migration; unlocks lineage/ABAC/sharing.
- **DLT → Lakeflow Declarative Pipelines**: zero migration, code runs as-is (just a rename).
- **Partitioned → liquid clustering**: incremental, no full rewrite required.
- **Snowflake/warehouse → Lakehouse**: usually via Delta + UniForm so Snowflake can still read during transition.

---

## 7. References

### Official
- **docs.databricks.com** (per-cloud: AWS / Azure / GCP)
- **Databricks blog** — feature GA announcements
- **delta.io** — Delta Lake OSS docs
- **Databricks Well-Architected Lakehouse**

### Load-bearing 2025-2026 facts (cited)
- Liquid clustering GA: https://www.databricks.com/blog/announcing-general-availability-liquid-clustering
- Delta UniForm: https://www.databricks.com/blog/delta-uniform-universal-format-lakehouse-interoperability
- UC managed Delta + Iceberg tables: https://docs.databricks.com/aws/en/tables/managed
- Read Delta with Iceberg clients (UniForm / IRC): https://docs.databricks.com/aws/en/delta/uniform
- DLT → Lakeflow Declarative Pipelines: https://docs.databricks.com/aws/en/ldp/where-is-dlt
- Lakeflow July 2025 updates: https://www.databricks.com/blog/whats-new-lakeflow-declarative-pipelines-july-2025
- Mosaic AI @ DAIS 2025 (Vector Search / Model Serving / AI Gateway GA): https://www.databricks.com/blog/mosaic-ai-announcements-data-ai-summit-2025
- Deletion vectors: https://docs.databricks.com/aws/en/delta/deletion-vectors
- ABAC + governed tags + classification GA: https://www.databricks.com/blog/abac-row-filtering-and-column-masking-policies-governed-tags-and-data-classification-are-now
- Predictive Optimization GA: https://www.databricks.com/blog/announcing-general-availability-predictive-optimization
- Photon: https://www.databricks.com/product/photon

### Books / learning
- **Delta Lake: The Definitive Guide** — Bukowski et al.
- **Spark: The Definitive Guide** — Chambers & Zaharia
- **Databricks Certified** paths: Data Engineer Associate/Professional, ML Associate/Professional, Data Analyst, Platform Architect

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| Data Architect | Delta vs Iceberg, UniForm/IRC interop, lock-in spectrum, medallion design |
| Data Engineer | Lakeflow pipelines, CDF/streaming, liquid clustering, MERGE patterns |
| Azure Expert | Azure Databricks vs Fabric/Synapse, OneLake shortcuts, Entra/Private Link |
| Cloud Expert (AWS/GCP) | Multi-cloud deploy, storage/networking, control-plane reality |
| AI Architect | Mosaic AI RAG, Vector Search, Model Serving, AI Gateway governance |
| Platform Architect | Workspace topology, UC metastore strategy, DABs + CI/CD |
| Security | UC ABAC, classification, audit → SIEM, CMK, private networking |
| Compliance | PDPA/BoT/BCBS-239 mapping via UC lineage + masking + audit |
| FinOps | DBU model, serverless, Predictive Optimization, cluster tagging |

---

*Databricks = best-in-class Spark + ML/AI lakehouse on open storage with a proprietary runtime. Data is portable (Delta/UniForm/Iceberg); performance and control plane are not. Govern with Unity Catalog, build ETL with Lakeflow, serve AI through Mosaic AI + the AI Gateway — and be honest about the lock-in spectrum.*
