# Streaming-CDC ETL Architectures + AI/ML/Agentic Extension — Survey (2026-07-02)

> Reference for สิน (Senior DE, AIA). Two layers: **Part 1 = data architecture** (provider→consumer→pipeline→warehouse; possible / popular / lean-low-cost) · **Part 2 = ML/AI/agentic extension** of each. Baselines: **AIA** (Azure: Kafka/Debezium→Databricks Structured Streaming→Delta) and **The-1** (GCP: app-emitted events→Kafka→Dataflow/Beam→BigQuery/Iceberg). Domain synthesis + web anchors (cited at bottom).
>
> **⚠️ KB-VALIDATED CORRECTIONS (2026-07-02) — canonical version = `skills/de-solution-architecture/SKILL.md`:**
> 1. **"Kill 24×7 streaming" villain is platform-specific.** Databricks/AIA: always-on **DBU** is the driver → `Trigger.AvailableNow` wins. **The-1/Dataflow: a lone streaming worker is cheap (~$150/mo)** — the real cost was Pub/Sub multi-hops + Bigtable IOPS + un-batched Iceberg commits. Don't dismantle a working 24×7 Dataflow.
> 2. **Heavier stream-compute (Beam) is justified by 5 things, not just enrichment**: CDC-with-DELETE, windowing, atomic Iceberg single-committer, exactly-once, portfolio TCO. **6/10 The-1 collectors keep Beam**; only simple-CDC (last-purchases/svoc-interim) → Datastream. Don't imply "move all of The-1 to Datastream".
> 3. **The "3B-row scan / 161GB→41GB" figure is illustrative of the MERGE-scan cost model, not a documented The-1 measurement.**
> 4. **Two Silver-collapse idioms:** partition-overwrite (SCB, business-date) vs row-level MERGE/APPLY CHANGES (AIA, pk). Don't conflate.
> 5. AI: **Tecton = Databricks now (Aug 2025)**; feature tables = **Platinum** layer (not gold); Agent-State is a **layer**. Add hybrid-retrieve+rerank, Cohere-multilingual embeddings, LLMOps cost levers (cache+routing+batch=80%), adversarial red-team eval (insurance).
> 6. **⚠️ THIS SURVEY IS GENERIC RESEARCH — NOT AIA's actual stack.** The "Reference stack per platform → AIA (Azure-Databricks)" column = the *generic Azure-Databricks path IF you extended into AI*, it is **aspirational, not what exists at AIA**. **AIA CONFIRMED-real = only**: Debezium→Kafka (Strimzi/AKS, Sin's job) → ADB (Spark) → outbound *maybe* Azure Synapse / *maybe* one ODS; tooling = ADB + Jenkins + Bitbucket. Online features / feature store / RAG / agents / Vector Search / Mosaic AI / Genie are **NOT confirmed at AIA**. Do not present the AI extension as AIA's stack.

---

# PART 1 — DATA ARCHITECTURE

## The canonical 4-stage pipeline
```
SOURCE DB ──CDC──► [1 PROVIDER/INGEST] ──► [2 CONSUMER/STREAM COMPUTE] ──► [3 PIPELINE/TRANSFORM] ──► [4 SERVING/STORAGE]
 (PG/Oracle/       Debezium/native CDC       Spark SS / Flink / Beam /       dbt / DLT / Dataform /     Delta/Iceberg/Hudi,
  SQLServer)       → Kafka/PubSub/            Snowpipe Streaming             Spark / MV                 BQ / Snowflake /
                     EventHubs/Kinesis                                                                  Synapse-Fabric / ClickHouse
        └── LANDING/BRONZE ──── SILVER (apply MERGE HERE, not at raw) ──── GOLD/serve ──┘
```
**The decision that cuts across everything:** *where does the MERGE happen?* Land raw as **append-only**, collapse to current-state in **Silver** → almost always cheaper + replayable than MERGE-at-raw.

## A. All plausible architectures (shipped-in-prod combos)
| # | Name | One-liner |
|---|---|---|
| A1 | **Databricks Lakehouse CDC** (AIA) | Debezium/Strimzi→Kafka→Spark SS→MERGE/`APPLY CHANGES`→Delta medallion |
| A2 | **DLT Declarative CDC** | Same, but DLT `APPLY CHANGES INTO` replaces hand MERGE + orchestration |
| A3 | **GCP Datastream→BigQuery** (native serverless) | Managed CDC straight to BQ via Storage Write API + BQ CDC; no Kafka/Dataflow |
| A4 | **GCP Kafka→Dataflow/Beam→BQ/Iceberg** (The-1) | CloudRun/Kafka→Dataflow→BQ or BigLake Iceberg; MERGE in-pipeline/downstream |
| A5 | **Datastream→GCS→Dataflow/dbt→BQ** | Datastream lands changelog to GCS; batch/micro-batch MERGE downstream |
| A6 | **Confluent + Flink→Iceberg/Delta** (Tableflow) | Managed Flink materializes topics to open Iceberg/Delta |
| A7 | **Confluent/MSK + Flink→Snowflake** (Snowpipe Streaming) | Kafka→Snowpipe Streaming→raw→Dynamic Tables collapse CDC |
| A8 | **AWS DMS→S3/Redshift/Iceberg** | DMS native CDC→S3/Redshift; Glue/EMR/dbt MERGE |
| A9 | **AWS MSK + Managed Flink→S3 Iceberg** | Debezium/MSK Connect→Flink→Iceberg; Athena/EMR serve |
| A10 | **Kinesis→Firehose→S3/Redshift** | Serverless auto-batch |
| A11 | **Azure Event Hubs→Databricks→Delta/Fabric** | Event Hubs (Kafka API)→Spark SS→Delta→Fabric/Synapse |
| A12 | **ADF/Synapse Link CDC** | Azure-native no-code CDC→Synapse/Fabric |
| A13 | **ksqlDB / Kafka Streams in-broker** | Lightweight stateful transform in Kafka, sink connector — no Spark/Flink |
| A14 | **ClickHouse CDC (PeerDB/ClickPipes)** | PG CDC→ClickHouse (ReplacingMergeTree collapses versions) real-time analytics |
| A15 | **SaaS-managed CDC** (Fivetran/Airbyte/Estuary) | Managed connector = capture+load; dbt transforms; zero streaming infra |
| A16 | **Batch-CDC / "poor-man's CDC"** | Watermark/`updated_at` extract→object store→dbt incremental MERGE; no CDC log |

## B. Commonly-adopted / industry-standard (+ cost band, driver)
- **B1 Databricks Lakehouse (A1/A2)** — one engine stream+batch+ML, medallion, Delta CDF keeps Silver→Gold incremental. **~$2k–12k/mo**; driver = always-on streaming DBU + MERGE write-amp. Lever = `Trigger.AvailableNow` + append-landing.
- **B2 Datastream→BQ (A3)** — lowest-ops GCP CDC, serverless, no Kafka/Dataflow. **~$500–4k/mo**; driver = Datastream GiB + BQ storage/query. *The-1 chose the heavier A4 only because it needed mid-stream enrichment + multi-sink; pure replication should use B2.*
- **B3 Confluent + Flink→Iceberg (A6)** — Kafka-centric, vendor-neutral open storage. **~$3k–15k/mo**; driver = CKU + Flink CFU.
- **B4 Snowflake + Snowpipe Streaming + Dynamic Tables (A7)** — flat ingest price; DT collapses CDC (managed MERGE). **~$2k–10k/mo**; driver = DT refresh warehouse (not ingest).
- **B5 AWS DMS→S3/Redshift (A8)** — AWS-native default. **~$1k–6k/mo**; driver = DMS instance + Redshift/EMR.
- **B6 SaaS (Fivetran/Airbyte)→dbt (A15)** — zero-infra, mid-market. **~$1k–8k/mo**; driver = connector MAR (bites on high-churn tables).

## C. Lean / low-cost (cheapest first) — theme: kill 24×7, append-land, MERGE on schedule
| # | Stack | Cost | Driver |
|---|---|---|---|
| C1 | **Batch-CDC → dbt incremental** (A16) | **$100–800/mo** | warehouse query only |
| C2 | **Datastream→BQ serverless** (B2) | $300–1.5k | Datastream GiB (free tier) |
| C3 | **OSS Debezium+Kafka on 1 VM → Spark `Trigger.AvailableNow`** | $400–2k | VM + intermittent Spark |
| C4 | **Snowpipe Streaming + Dynamic Tables, XS warehouse** | $800–3k | DT refresh (raise lag target) |
| C5 | **PeerDB/ClickPipes → ClickHouse** | $500–2.5k | CH nodes (no MERGE job) |
| C6 | **Kinesis Firehose → S3 Iceberg + Athena** | $300–1.5k | Firehose GB + Athena scan |

**Lean golden rule:** if you don't truly need sub-minute freshness, **micro-batch MERGE every 5–60 min beats 24×7 streaming by 3–10×** (streaming bills idle wall-clock). Most "real-time" needs are actually "within 15 min".

## Engineering points (สิน's issues addressed)
1. **CDC placement — append-then-merge, NOT merge-at-raw** (fixes The-1 sales-collector 3B-row scan):
   - MERGE cost ≈ bytes scanned in target's matched partitions. Keys spread across the table OR a *dynamic* partition filter → engine can't prune → full scan. (BQ: MERGE w/o static partition filter scans full table; with it prunes — 161GB→41GB example.)
   - Pattern: **Bronze = raw append changelog (partition by ingest date)**; **Silver = incremental MERGE/MV on a bounded event-time window with STATIC predicates**, or a MV/Dynamic Table/DLT `APPLY CHANGES` the platform maintains.
   - Snapshot source → don't MERGE snapshot-into-current; diff snapshots or `ROW_NUMBER() OVER (PARTITION BY pk ORDER BY ts DESC)` in a view.
   - Set event-time **watermark** (Spark/Flink) so MERGE key-space is bounded.
2. **24×7 vs triggered:** Spark `Trigger.AvailableNow` = process backlog as bounded batch then release cluster (no idle bill); Dataflow streaming bills per-second always-on → scheduled batch / Datastream serverless avoids it. Always-on justified only < ~1–2 min SLA + steady high volume.
3. **Storage Write API / exactly-once:** Datastream + Dataflow BQ template use Storage Write API (offsets+commit, no dup). Knob: exactly-once → at-least-once (cheaper) + dedupe-on-read (`QUALIFY ROW_NUMBER()`). Watch committed vs pending streams + quotas.
4. **Config-driven — when it helps vs hurts:** HELPS when pipelines are homogeneous (differ only by table/keys/partition/watermark) → generic template × N tables. HURTS when each has bespoke enrichment/joins → config becomes an untyped, untestable second language (the 3B-scan is often a generic "MERGE everything" template on a table that needed a custom bounded strategy). **Standardize the interface (Bronze append contract, Silver collapse contract) for the 80%; let the bespoke 20% be explicit code. Metadata describes data, not control flow.**
5. **Partition/cluster/compaction:** Bronze partition by ingest-date; Silver partition by merge/query filter col (static pruning); cluster (Z-order/Liquid/BQ clustering) on join/merge key; schedule `OPTIMIZE`/compaction (streaming = small-file hell); target ~256MB–1GB files; avoid over-partitioning (BQ 4000-partition cap).

## Decision guide (latency → stack)
- **< 5 sec** (fraud/trading/ops): Kafka+Flink (B3) or Spark Real-Time Mode → Iceberg/Delta; ClickHouse (C5) for real-time dashboards.
- **seconds–minutes**: GCP pure replication → **Datastream→BQ (B2)**; GCP + enrichment → Kafka→Dataflow→BQ/Iceberg (A4) *but append-land + Silver MERGE*; Azure/Databricks → B1 move to DLT + short Trigger; AWS → DMS→Iceberg (B5); Snowflake → Snowpipe+DT (B4).
- **15 min–hours** (most analytics — be honest): lowest cost → **Batch-CDC→dbt (C1)**; have a CDC log → Debezium→append→Spark `AvailableNow` (C3); small team → Fivetran/Airbyte→dbt.
- **Budget-dominant savings order:** (1) triggered vs continuous (2) append-then-merge vs merge-at-raw (3) managed serverless vs self-run cluster.
- **Lock-in worry:** land in open Iceberg/Delta on object storage; keep compute swappable; don't make warehouse-native CDC the only copy.

**AIA (B1):** wins = DLT `APPLY CHANGES` over hand-MERGE + `Trigger.AvailableNow` scheduled + append-Bronze/bounded-Silver → same arch, 2–5× cheaper.
**The-1 (A4):** interrogate 24×7 Dataflow vs triggered; move sales-collector CDC off raw (append by ingest-date → partition-pruned Silver MERGE/MV) → kills the 3B-scan; pure-replication tables → Datastream-native (B2) removes the Beam burden.

---

# PART 2 — ML / AI / AGENTIC EXTENSION

**Core idea:** your CDC medallion is already 80% of an AI platform. Extensions are **modules that tap the existing stream + gold marts**, not a 2nd platform. Two taps:
1. **Gold tap** (batch, curated, governed) — offline features, RAG over trusted entities, agent tools.
2. **Stream tap** (the SAME Kafka CDC topic) — online/streaming features + near-real-time re-embedding. *Reusing the one stream twice = the DE's unfair advantage.*

## EXT-1 — ML (feature store → training → registry → serving → drift)
- **Attaches to medallion:** bronze=source for online features; silver=offline features engineered/materialized; gold=entity-keyed **feature tables** + training sets; stream-tap=online features → low-latency KV.
- **Offline store = your gold Delta/BQ (no duplication); online store = KV** (Cosmos/Bigtable/Redis/Dynamo) fed by CDC stream.
- **Point-in-time correctness** = non-negotiable (as-of joins; don't leak the future). Use FS native as-of joins, don't hand-roll.
- Paths: **AIA** = Databricks Feature Engineering in UC + Online Tables + MLflow/UC Models + Model Serving + Lakehouse Monitoring. **The-1** = Vertex Feature Store (BQ-backed) / **BQML (train+score in SQL, zero MLOps infra — stealth win)** + Vertex Registry/Endpoints/Monitoring. **Lean** = Feast + Redis + MLflow + vLLM/BentoML + Evidently.
- **Rec:** start with the native FS (offline = already your gold); Feast only for multi-cloud/anti-lock-in. The-1: BQML lets a DE ship models in SQL.

## EXT-2 — GenAI / RAG (the vector-DB question สิน asked)
**Recommendation: embed from GOLD primarily; use CDC only as the TRIGGER for incremental re-embed. NOT parallel-from-bronze/silver (except a narrow real-time slice).**

| Dimension | Embed from GOLD | Parallel from bronze/silver |
|---|---|---|
| Freshness | mins–hours (usually fine) | seconds (only for live ops) |
| Data quality/trust | high (dedup, PII-handled, business logic) → RAG matches dashboard | low (raw dupes/tombstones) → hallucination |
| Governance/lineage | inherits UC/BQ policy tags, masking, ACLs | must re-implement all governance (PII-leak risk) |
| Cost | embed once, smaller curated set | embed high-volume raw churn (every CDC flicker) |
| Reprocessing | clean/idempotent on gold change | wasted re-embed of rows gold would discard |
| Consistency w/ analytics | one source of truth | "chatbot said X, dashboard said Y" |

- **Close the freshness gap** by making gold **CDC-triggered incremental** (Delta CDF / BQ change history) → "gold-quality + near-fresh", no 2nd governance surface.
- **Pattern:** Kafka CDC → gold updated → change feed (Delta CDF / BQ change history) → only CHANGED rows → chunk → embed (batch) → **upsert into vector index; delete-then-insert by pk on content-hash change**. Managed sync (Databricks **Vector Search Delta Sync**, Vertex **Vector Search streaming**) does the diff for you.
- **Parallel-silver only for:** real-time operational knowledge (live agent-assist, incident notes), or unstructured sources (PDF/tickets/transcripts) that bypass the structured medallion → own ingestion lane but still land in a governed "gold-for-text" zone before embedding.
- **Chunking/metadata:** structure-aware 256–512 tok + overlap; store `entity_id, source_table, gold_load_ts, acl_tags` as **filterable metadata** (enables security-trimmed retrieval).
- **Vector stores:** Databricks Vector Search (AIA, Delta-native) · Vertex Vector Search (The-1, BQ-native) · **pgvector** (<~10M vectors, simplest, prod-grade — best cheap POC) · Qdrant/Milvus (>10M) · Azure AI Search/OpenSearch (hybrid keyword+vector).

## EXT-3 — Agentic (text-to-SQL / tool-use / prediction)
- **3 agent classes:** (1) text-to-SQL over **gold marts** (highest value, lowest risk) (2) tool-use agent composing `query_gold()`+`retrieve()`+`predict()`+`get_online_feature()` (DE+ML+GenAI converge) (3) prediction/decision agent (highest risk → strongest guardrails + HITL).
- **Foundation = gold + data contracts:** agents fail by compounding errors → never touch ungoverned data. Text-to-SQL needs a **semantic layer/metric definitions** (a contract, not raw schemas). Every tool = typed, validated, ACL'd; read-only default; writes need approval.
- **Orchestration/guardrails/eval:** LangGraph (cap iterations); input (jailbreak/PII) + output (SQL parse+cost+row-limit+read-only, grounding check, PII egress) validation at EVERY step; eval = golden set + LLM-judge + **execution-match** for SQL; **HITL for insurance/financial decisions**; trace tokens/latency/cost.
- Paths: **AIA** = Mosaic AI Agent Framework + **Genie** (governed text-to-SQL over UC) + AI Gateway + UC (one policy plane). **The-1** = Vertex Agent Builder/Gemini + BQML-in-SQL tools + Model Armor. **Lean** = LangGraph + vLLM + Guardrails-AI/NeMo + Ragas/DeepEval.
- **Rec:** ship governed **text-to-SQL over gold** first, then graduate to a LangGraph tool agent composing retrieve+predict+query. Agents touch **gold only**.

## Reference stack per platform
| Layer | AIA (Azure-Databricks) | The-1 (GCP) | Lean/OSS |
|---|---|---|---|
| CDC | Debezium→Kafka | Kafka | Debezium→Kafka/Redpanda |
| Medallion | DLT/Spark SS→Delta+UC | Dataflow→BQ+Iceberg | Spark/Flink→Delta/Iceberg |
| Offline feat | Databricks FS (Delta) | Vertex FS / BQML | Feast |
| Online feat | stream tap→Online Tables/Cosmos | Dataflow→Bigtable | Flink→Redis |
| Model reg/serve | UC Models + Serving + Lakehouse Monitoring | Vertex Registry/Endpoints/Monitoring | MLflow + vLLM + Evidently |
| Embeddings | gold+CDF→Vector Search Delta Sync | gold+BQ change history→Vertex Vector Search | gold change-hash→pgvector |
| RAG | Mosaic AI + FMAPI | RAG Engine + Gemini | LangChain + vLLM |
| Agents | Mosaic Agent FW/Genie + AI Gateway | Agent Builder/Gemini | LangGraph + Guardrails-AI |
| Governance | **Unity Catalog (one plane)** | IAM + policy tags + Dataplex | OPA + app ACL |

## Load-bearing principles
1. **Embed from GOLD, trigger from CDC** (quality+governance + freshness, no 2nd governance surface).
2. **Reuse the one CDC stream twice** — online features + incremental re-embed. Don't build parallel ingestion.
3. **Feature store offline = your gold** (native stores read Delta/BQ directly, no copy).
4. **Governance is one plane** (UC / policy tags+Dataplex) over data+features+vectors+models+agent-tools.
5. **Agents touch gold only, via typed tools + contracts**; cap iterations; validate every step; HITL for insurance/financial; eval before deploy.
6. **สิน's skill path:** BQML/Databricks FS (SQL-native ML) → gold-sourced RAG (Vector Search Delta Sync) → governed text-to-SQL agent → composed LangGraph tool agent. Each step reuses the platform you own; **pgvector + Feast + vLLM = lock-in-free sandbox** to learn the same patterns cheaply.

## Risks → mitigations
| Risk | Mitigation |
|---|---|
| RAG diverges from BI ("two truths") | embed from gold only; share metric defs w/ agents |
| PII→LLM via parallel embed path | default gold (PII-handled); parallel path replicates masking + governance review |
| Train/serve skew, PIT leakage | FS as-of joins; never hand-roll time-travel |
| Vector staleness | CDC-triggered incremental re-embed on content-hash; delete-then-upsert |
| Agent compounding failures | iteration caps, per-step validation, read-only tools, HITL, execution-match eval |
| Cost blowout (continuous sync / frontier models) | batch-incremental unless seconds needed; multi-model routing; index only curated gold |

---

## Sources (web anchors)
Databricks: DLT CDC, Real-Time Mode, Trigger.AvailableNow, Vector Search Delta Sync, Feature Store, CDC guide · Google Cloud: Datastream→BQ, Datastream pricing, Datastream→BQ Dataflow template, BQ incremental ingestion cost, BQ MERGE partition pruning, Vertex Feature Store / Vector Search / pricing · Snowflake: Snowpipe Streaming + Dynamic Tables · Confluent vs MSK cost · Kafka cost comparison 2026 · "Embedding pipelines are the new ETL" · Production RAG w/ pgvector+vLLM · Lakehouse 2025/2026 guide.
