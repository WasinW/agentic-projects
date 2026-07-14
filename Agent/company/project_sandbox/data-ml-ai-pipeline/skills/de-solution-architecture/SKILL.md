---
name: de-solution-architecture
description: >-
  Use when choosing/comparing a streaming data-platform architecture across the 3 layers —
  (1) PRODUCER/ingest (CDC capture + transport), (2) CONSUMER + data pipeline (ETL: stream compute →
  transform → serving), (3) ML/AI/AGENTIC extension — on Azure/GCP/AWS/OSS, or deciding the lean/low-cost
  option. Also Part 4: SERVING/SHARING a data product across workspaces/tenants you don't control
  (decision tree, compute-affinity trap, data-identity vs compute-identity). Contains the catalogs (producer P1-P25, consumer A1-A16, AI extension), popular + lean picks with
  cost bands, engineering rules (CDC placement, append-then-merge, 24×7-vs-triggered, Debezium deployment
  modes, broker-vs-brokerless), decision guides, and KB-validated real anchors from Wasin's NTT/SCB/AIA work.
  Companion deep docs in ../../knowledge_chat/ (producer-ingestion-survey, de-streaming-architecture-and-ai-survey).
---

# DE Solution Architecture — 3 layers (producer · consumer/ETL · AI)

> Validated 2026-07-02 against Wasin's Agent KB (NTT/The-1 + SCB + AIA + role knowledge) by solution-architect / data-architect / ai-architect. ⚠️ = a correction the KB forced on the first-draft survey. 📌 = a real anchor from his documented work.
> 3 layers: **PRODUCER** (source→capture→transport→topic) · **CONSUMER+ETL** (stream compute→transform→serving) · **AI** (ML/RAG/agentic tapping the stream + gold).

---

# PART 1 — PRODUCER / INGESTION (source → capture → transport → topic)

**Core decision: do you actually need a broker?** Capture (Debezium) and transport (Kafka) are **separable**. Debezium Server / native CDC / SaaS keep CDC while deleting the Connect cluster or the broker. Pick the lightest thing meeting latency + fan-out + replay.

## Catalog (P1-P25, grouped)
- **Debezium + self-Kafka:** P1 Debezium/Strimzi→Kafka (**= AIA**) · P16 Redpanda+Debezium · P17 WarpStream/AutoMQ+Debezium (diskless S3)
- **Debezium without Connect cluster:** P2 Server→Pub/Sub · P4 **Server→Event Hubs** · P3 Server→Kinesis · P6 **Engine (embedded)** — no server/broker
- **Native managed CDC (no Kafka):** P7 GCP Datastream · P8/P9 AWS DMS→Kinesis/MSK/S3 · P10 Azure Synapse Link/ADF
- **Managed Kafka + connector:** P18 Confluent Cloud managed Debezium · P19 MSK+MSK Connect
- **App-emitted (not CDC):** P14 Outbox+Connect · **P15 app→Pub/Sub/Event Hubs domain events (= The-1)**
- **Query/trigger/snapshot:** P11 JDBC-poll · P12 query micro-batch→object store · P13 trigger→shadow · P24 full-snapshot/batch export
- **SaaS:** P20 Fivetran · P21 Airbyte · P22 Estuary · P23 Striim/Qlik/GoldenGate · P25 PeerDB

## Popular (B) + when it's the right practice
| | stack | band/mo | right when (grounded) |
|---|---|---|---|
| B1 | **Debezium/Strimzi → self-Kafka** (AIA) | ~$0.5-1.5k + **0.3-0.5 FTE** | Kafka is a shared multi-consumer high-churn platform. **AIA core — keep it.** |
| B2 | **GCP Datastream native** | $0.3-3k ($2/GiB) | **pure/simple-CDC replication, no deletes-with-logic, no enrichment.** (The-1: only the last-purchases/svoc-interim tier, NOT members/profile) |
| B3 | Confluent+Flink | $3-15k | Kafka-centric, vendor-neutral open storage (principle, not his lived stack) |
| B4 | **Confluent Cloud + managed Debezium** | $1-3k | **regulated insurer valuing SLA + one-throat-to-choke over flex — AIA's plausible exit from Strimzi ops** |
| B5 | MSK + MSK Connect | $0.5-2k | AWS-native only (park for future AWS source) |
| B6 | Fivetran/Airbyte (MAR) | $1-8k | small team, <10 tables, **low-churn — WRONG for AIA** (insurance core = high-churn, MAR punishes it) |
| B7 | **Event Hubs (Debezium Server)** | $25-300 | **peel-off lever for AIA single-sink lanes** (source feeds only Databricks, no fan-out) → deletes that lane's Connect runtime; **cost: loses free SR + DLQ**, peel only where acceptable |

## Lean (C, cheapest first)
C1 query micro-batch→object store ($50-400) · **C2 Debezium Server→Pub/Sub/Event Hubs ($60-500, best lean CDC)** · C3 Datastream serverless · C4 Estuary · C6 **Debezium Engine (~$0)** · C7 diskless Kafka (WarpStream/AutoMQ/Redpanda) · C8 Airbyte OSS.
**Lean rule:** rarely need BOTH a Connect cluster AND a broker. One sink, no replay → Server/Engine. Replay+fan-out but cheap → diskless. Freshness >15 min → query micro-batch.

## Engineering
- **Capture matrix:** log-based (Debezium/DMS/Datastream) = low source load, captures deletes, needs setup (Oracle supplemental logging, SQLServer CDC, PG wal_level=logical) → default. query-based = cheap but no deletes. trigger = write-amp, avoid. snapshot = SCD/backfill only. **app-emitted (outbox/ES) = best semantic events when you own the app.**
- **Debezium modes:** Connect(Strimzi) = buffering+replay+fan-out+DLQ+SMT at cost of a cluster · **Server = 1 source→1 sink container, removes the Connect cluster** · Engine = library, removes server+broker (at-least-once, single consumer, no replay).
- **Broker vs brokerless vs diskless:** broker only for multi-consumer/replay/in-stream processing. Redpanda = no ZK, low latency. WarpStream/AutoMQ = diskless S3, ~77% cheaper at scale but 100s-ms latency (fine for CDC/ETL, not fraud).
- **Snapshot/backfill = biggest surprise-bill + outage risk.** Blocking snapshot can lag redo logs → fail. Use incremental snapshot (signaling); or bulk-export→object store + start CDC from known SCN/LSN. 📌 The-1 does the bulk variant (init-load via BQ staging + DTS, then stream).
- **SR/DLQ/ordering/EOS:** SR (Confluent/Apicurio/Glue) enforces contract; Server loses Connect's SR+DLQ. Order = key by PK. **Debezium = at-least-once → EOS via idempotent upsert on PK+LSN downstream; design consumers idempotent.** 📌 The-1 members-collector: per-bundle dedup, PK member_id+program_code, 3-layer CDC DELETE.
- **Build-vs-buy:** most orgs over-build; <10 tables + pure replication → serverless CDC beats standing up Strimzi. Strimzi wins when Kafka is a platform many teams consume.

## ⚠️ VALIDATED corrections (KB forced these)
1. **The-1 producer = app-emitted domain events (P15), NOT CloudRun→Kafka/Debezium.** Loyalty microservices emit `loyalty.members.upgraded`, `sales.created`, etc. to Kafka; Wasin's team owned the *consumers* (Dataflow). CloudRun at The-1 = API-poll batch collectors → GCS (the C1 pattern), never a Kafka producer. Lesson: **when the source app owns the event, prefer app-emitted events over CDC.**
2. **AIA runs Debezium 1.9.7.Final** → "ROWID incremental-snapshot chunking" and "drop-transaction signal" are **2.x/3.x features AIA cannot use today**. Signalling-based incremental snapshot exists at 1.9; ROWID/drop-tx must be gated on a Debezium upgrade — not presented as available.
3. **AIA transport as-is = self-managed Strimzi Kafka on AKS** (Debezium→Strimzi→Databricks). Event Hubs (B7/C2) is a **proposed** simplification, not the current stack.

## Gaps to remember (the parts that are *actually* Wasin's job)
- **Config-driven / declarative producer onboarding + fail-loud validation** — 📌 AIA connector-as-YAML (edit `table.include.list`, clone-existing, Jenkins→ACR→AKS promote dev→uat→prod→**prod-dr**); 📌 SCB single-active-row (`actv_flag='Y'`) validation before any write. "How do you add source #40 safely" > which capture tool.
- **Topic governance** — 📌 AIA auto-creates topics (no `KafkaTopic` CRs, no git list, broker-default partitions/retention, silent wrong-name-on-typo). Naming discipline + per-topic tuning + declarative source-of-truth = his Goal-#2 refactor angle.
- **Data contract in producer repo + CI** — YAML contract + CI schema-drift/contract test (cheaper first line than runtime SR alone).
- **DR / twin topology** — every prod resource has a `-dr` twin, promoted in lockstep. Table-stakes for a regulated insurer.

---

# PART 2 — CONSUMER + DATA PIPELINE (ETL: stream compute → transform → serving)

**Cross-cutting decision: where does MERGE happen?** Land raw **append-only** (Bronze), collapse in **Silver**. Never MERGE-at-raw.

## Catalog (A1-A16, grouped)
Databricks Lakehouse (A1 Spark-SS+MERGE→Delta =AIA · A2 DLT APPLY CHANGES) · GCP serverless (A3 Datastream→BQ · A5 →GCS→dbt) · **GCP Kafka+Dataflow (A4 =The-1)** · Kafka-open (A6 Confluent+Flink→Iceberg · A13 ksqlDB) · Snowflake (A7 Snowpipe+Dynamic Tables) · AWS (A8 DMS→S3/Redshift · A9 MSK+Flink→Iceberg · A10 Kinesis→Firehose) · Azure (A11 EventHubs→Databricks · A12 Synapse-Link) · ClickHouse (A14) · SaaS (A15 Fivetran→dbt) · batch-CDC (A16→dbt).

## Popular (B) + lean (C) with cost
B1 Databricks Lakehouse $2-12k (driver: always-on DBU+MERGE write-amp) · B2 Datastream→BQ $0.5-4k · B3 Confluent+Flink $3-15k · B4 Snowflake+DT $2-10k · B5 DMS→S3/Redshift $1-6k · B6 SaaS→dbt $1-8k.
Lean: **C1 Batch-CDC→dbt $100-800 (cheapest)** · C2 Datastream serverless · C3 Debezium Server+Spark AvailableNow · C5 ClickHouse · C6 Kinesis Firehose. **Micro-batch every 5-60 min beats 24×7 streaming 3-10× — where the engine bills per-second compute.**

## Engineering + ⚠️ VALIDATED corrections
1. **Append-then-merge, not merge-at-raw.** Bronze = raw append changelog (partition by ingest-date); Silver = incremental collapse on a **bounded event-time window with STATIC partition predicates**. 📌 The-1 sales-collector: `job_type=initial_data` (batch backfill lane) vs `normal` (stream), raw→`raw_sales/` append, current-state derived downstream (`bak_mem/sales/sales_initial_data.md`). ⚠️ The "3B-row scan / 161GB→41GB" figure is **illustrative of the MERGE-scan cost model, not a documented The-1 measurement** (not in KB).
2. **Two valid Silver-collapse idioms** — ⚠️ *partition-overwrite* (batch, business-date-keyed: 📌 SCB `INSERT OVERWRITE PARTITION(bsns_dt)` + dynamic overwrite) vs *row-level MERGE / APPLY CHANGES* (streaming, pk-keyed: 📌 AIA `foreachBatch`+MERGE+`update_date` guard). Don't collapse both into "MERGE".
3. **⚠️ "Kill 24×7" villain is platform-specific.** Databricks/AIA: always-on **DBU** is the driver → `Trigger.AvailableNow` genuinely wins. **The-1/Dataflow: a lone streaming worker is cheap (~$150/mo)** — the cost trap was **Pub/Sub multi-hops + Bigtable IOPS + un-batched Iceberg commits**, NOT the worker. Hunt cost in hops/state-IOPS/commit-frequency; don't dismantle a working 24×7 Dataflow.
4. **⚠️ Heavier stream-compute (Beam/Flink) is justified by more than enrichment** — 📌 The-1 kept Beam for **5** reasons: CDC-with-DELETE (members 3-layer), windowed aggregation (profile V3 FixedWindows+periodic Iceberg MERGE), atomic Iceberg single-committer + commit-batching, exactly-once (Storage Write), portfolio TCO. **6 of 10 collectors stay Beam**; only simple-CDC/batch (last-purchases, svoc-interim) → Datastream. Don't imply "move all of The-1 to Datastream".
5. Storage Write API: exactly-once → at-least-once (cheaper) + dedupe-on-read (`QUALIFY ROW_NUMBER()`). 📌 The-1 `BigQuerySink` = append/cdc/batch modes, PK required for cdc.
6. Config-driven helps homogeneous 80% (📌 SCB FW: pipeline = config rows + parameterized SQL), hurts bespoke 20% (📌 The-1 members 3-layer DELETE, profile V3 windowed = explicit code).
7. Partition by ingest-date (Bronze) / filter col (Silver, static prune); cluster on merge key; compaction + **Iceberg commit-batching** (un-batched = 100× commits); ~256MB-1GB files.

## Gaps to remember
DELETE/tombstone propagation (soft-delete flag→MERGE WHEN MATCHED DELETE / APPLY AS DELETE; multi-source confirm when signal unreliable) · **dup-source-keys-in-MERGE bug** (dedupe within batch via QUALIFY ROW_NUMBER before MERGE, else MERGE errors) · checkpoint namespacing + one-writer-per-target + DLQ table (non-negotiable) · explicit backfill/reprocess lane (first-class mode) · streaming-enrichment KV (📌 The-1 sync-path batch→Redis + stream-path Kafka→Dataflow lookup).

## Decision guide (latency → stack)
<5s: Kafka+Flink / Spark Real-Time / ClickHouse. sec-min: GCP pure-replication→Datastream; GCP+deletes/windowing/multi-sink→keep Beam; Azure→Databricks+DLT+short Trigger; AWS→DMS→Iceberg; Snowflake→Snowpipe+DT. 15min-hours: **Batch-CDC→dbt (cheapest)**. Savings order: (1) triggered-vs-continuous *where compute bills per-second* (2) append-then-merge (3) serverless-vs-self-run.
📌 Real cost anchor: The-1 dataflow-vs-cloudrun @100M events/day = CloudRun **$20.6k/mo** vs Dataflow **$0.7-4.6k**; crossover **<5-10M events/day/collector → CloudRun wins, >10M → Dataflow**.

---

# PART 3 — ML / AI / AGENTIC (extension tapping the same stream + gold)

> **⚠️ GENERIC / aspirational — NOT AIA's actual stack.** This whole Part 3 (and the "reference stack → AIA (Azure-Databricks)" mappings) describes the *possibility space if a platform extended into AI*. **AIA CONFIRMED-real = only the data platform**: Debezium→Kafka (Strimzi/AKS, Sin's job) → ADB (Spark) → outbound *maybe* Azure Synapse / *maybe* one ODS; tooling = ADB + Jenkins + Bitbucket. Feature store / online features / RAG / agents / Vector Search / Mosaic AI / Genie are **NOT confirmed at AIA** — never attribute them to AIA. Keep this survey (research) separate from AIA (Sin's narrow real job).

**Maps onto our extended-medallion vocab** (`knowledge/architecture-modern-data-ai.md`): **EXT-1 ML = Platinum layer** (features, PIT-correct) · **EXT-2 RAG = Diamond layer** (chunk+embed) · **EXT-3 agentic = Agent-State layer** (memory/tool-logs/checkpointer) + feedback-to-Bronze loop.

- **EXT-1 ML / Platinum:** offline features = your gold Delta/BQ (zero copy); online = **tap the CDC stream** → KV; PIT-correct as-of joins (Databricks FS + Online Tables @AIA; **BQML train+score in SQL @The-1**; Feast for anti-lock-in). ⚠️ **Tecton = Databricks now (acq. Aug 2025)** — it IS the Databricks path, not a 3rd option. ⚠️ feature tables live in **Platinum** (not blurred into business-Gold).
- **EXT-2 RAG / Diamond:** **embed from GOLD, trigger from CDC** (Delta CDF / BQ change history → re-embed changed rows on content-hash; delete-then-upsert). NOT parallel-from-bronze/silver (gold already handles quality+governance+PII). **Gap to add: always hybrid retrieve (vector+BM25→RRF) + cross-encoder rerank** (biggest technique gap; "naive chunk+cosine" = named anti-pattern). Embedding model: **Cohere multilingual-v3** for Thai/EN (or Bedrock in-estate); BGE-M3/e5-large self-host lean. Stores: Databricks Vector Search / Vertex Vector Search / **pgvector (lean, <10M — 📌 Lumora pattern)**.
- **EXT-3 agentic / Agent-State:** governed text-to-SQL over **gold + semantic layer** first (Genie/UC @AIA) → LangGraph tool agent (retrieve+predict+query_gold). ⚠️ Agent-State is a **layer** (Redis/Postgres/LangGraph checkpointer for short/long/episodic memory + tool logs) — resumable, not just orchestration. Typed/ACL'd read-only tools, cap iterations, **HITL on every insurance/financial decision** (non-negotiable @AIA).
- **Gaps to add:** LLMOps cost levers — **semantic cache (30-70%) + model routing Haiku/Sonnet/Opus (40-60%) + Batch API (50%) → 80%+ combined**, plus Lumora "orchestrator-first, LLM-surgical" (orchestrator does 95%, LLM only judgment). Eval = golden + LLM-judge + **execution-match + adversarial red-teaming** (insurance = compliance, red-team not optional) + CI gate (fail PR if faithfulness <0.85). Advanced-RAG escape hatches: HyDE/Self-RAG/Corrective-RAG/Graph-RAG when basic underperforms.
- **Principle:** reuse the one CDC stream twice (online features + re-embed) = the DE's unfair advantage; governance = one plane (Unity Catalog / policy-tags+Dataplex) over data+features+vectors+models+agents.
- 📌 **Anchors:** our extended-medallion (Platinum/Diamond/Agent-State) doc; **Lumora** (`company/project_sandbox/lumora/knowledge/07_platform_design.md` — pgvector-in-Postgres, weighted-scorer-before-ML, RLS security-trim, 6-week RAG build ~$70/mo ≥85% acc); `knowledge/ai-rag-agent-reference.md` (tool picks + hybrid/rerank + cost levers). (NeurX/Regent AI not yet in KB.)

---

# PART 4 — SERVING / SHARING A DATA PRODUCT ACROSS WORKSPACES YOU DON'T CONTROL

> Added 2026-07-13. Verified against official Azure Databricks docs (see
> `../../knowledge_chat/aia-cost-dashboard-solution-VERIFIED_20260713.md`).
> **The pattern generalises well beyond Databricks** — read "workspace" as "any tenant/project boundary
> you don't own", and the two traps below are platform-independent.

The pipeline ends at gold. The *product* only exists once someone outside your team can see it — and
that last hop is where architectures quietly fail, because the consumer sits in **a workspace/project
you have no admin rights in**.

## The two traps

**Trap 1 — the compute-affinity trap.** *Whoever hosts the compute pays for the viewers' queries.*
A published dashboard runs on the **publisher's** warehouse. So the team that builds and hosts the
data product funds every consumer's browsing. (On a **chargeback/cost** dashboard this is maximally
ironic and will be noticed by the sponsor before it is noticed by you.)
→ **Separate the two identities explicitly and say which is which:**

| | Who it is | What it controls |
|---|---|---|
| **Data identity** | the **VIEWER** | which rows/columns come back (RLS, masks, GRANTs) |
| **Compute identity** | the **PUBLISHER** | which cluster/warehouse runs it — **and who is billed** |

Because they are separate, the viewer needs **no compute permission and no workspace membership** —
that is the feature. The bill following the *compute* identity is the price.

**Trap 2 — nothing you build appears in their workspace.**
> **The ONLY artifact that ever materialises inside a consumer's workspace is a shared TABLE.**
> **Never a dashboard. Never an app.** Those are **URLs** — a view-only render, outside their nav.

If the requirement is truly *"it must show up in my workspace / my BI tool"*, the answer is a **table
grant**, and nothing else in the catalog satisfies it. Ask which one they actually mean, early — it
changes everything downstream.

## Decision tree

```
Do they need it INSIDE their own workspace / their own BI tool?
├── YES → GRANT the TABLE to their ACCOUNT group (+ hand them a dashboard template file to import)
│         → their compute runs it → THEY pay → real chargeback → $0 marginal cost to you
└── NO — a link is fine
    ├── one curated view, per-viewer row filtering → PUBLISHED DASHBOARD shared to their account group
    │     (publish mode MUST be the viewer-credentials one; the default embeds the publisher's — a leak)
    ├── need a per-team PDF in an inbox, or zero doc-ambiguity → ONE DASHBOARD PER TEAM, pre-filtered
    ├── consumer is in a different METASTORE / a different ORG → DELTA SHARING (and only then)
    └── "share" actually meant "a report" → SCHEDULED PER-TEAM REPORT JOB (cheapest by 10x)
```

| Option | In their WS? | Who pays | Per-viewer security | Use when |
|---|---|---|---|---|
| **Table GRANT (account group)** | ✅ Catalog Explorer | **Consumer** | Row filter / mask (enforced everywhere) | They want self-service, or you want real chargeback |
| **Published dashboard + account-group share** | ❌ URL only | **Publisher** | Viewer-credential publish mode + row filter | Curated view, casual viewers, no admin rights needed anywhere |
| **Dashboard template export/import** (`.lvdash.json`) | ✅ (their copy) | Consumer | via the table's row filter | Hand-off; they own the copy (and the drift) |
| **Delta Sharing** | ✅ (as a share) | Consumer | Coarser (share-level) | **Different metastore / external org ONLY** — same metastore = needless complexity |
| **Scheduled report job** | ❌ (email) | You (tiny) | By construction (query filtered per team) | "Share" means "report". ~10x cheaper than everything above |
| **In-workspace app / NL-query tools** | ❌ | You (24/7 compute) | varies | Usually blocked for non-members anyway. Costs 2-4x a dashboard and does less |

## Rules of thumb

1. **Ask "does it have to appear in your workspace, or is a link enough?" in the first meeting.** That
   single question collapses the option space from 10 to 2.
2. **Ship the link AND the table grant.** The dashboard serves the casual viewer; the grant serves the
   team that wants to build their own thing and pay their own compute. They cost you the same to build.
3. **Governance travels with the TABLE, not with the dashboard.** Define the row filter/mask **once, on
   the table** → it holds in the dashboard, in their notebook, in their Power BI, in their warehouse.
   A filter implemented *in the dashboard query* protects exactly one artifact and nothing else.
4. **Identity must be at the ACCOUNT tier, never workspace-local** — a workspace-local group cannot
   resolve for someone who isn't in your workspace. That is the whole reason cross-workspace grants work.
5. **The default publish mode is usually the insecure one.** Pin it in IaC/bundle config; never trust the UI.
6. **Never blast a single all-teams export to a list of external recipients** — an email destination is
   a static address, not an identity, so it is not per-recipient filtered. Link-only, or one artifact per team.
7. **Name the lock-in out loud:** the gold table is portable (Delta/Iceberg); the *sharing model* is
   vendor-proprietary. If lock-in matters, the exit is "table grant + their own BI tool".

📌 Deep mechanics (grants, `is_account_group_member()`, workspace-catalog binding, publish modes,
subscription gotchas, verification commands): **skill `databricks-uc-governance-sharing`**.
Cost model of each option: **skill `databricks-cost-optimization` §8**.

---

## Related skills
`kafka-strimzi-cdc` (producer internals — HIS job) · `databricks-streaming-pattern` (consumer) · **`databricks-uc-governance-sharing` (serving/sharing — Part 4)** · `databricks-cost-optimization` · `airflow-databricks-orchestration` · global `spark-tune`.

## Validation provenance
Validated 2026-07-02 vs synced Agent KB. Key sources: `company/ntt/the_one/knowledge/discussions/dataflow_vs_cloudrun/*` (cost + 5-reasons), `.../memory/bak_mem/sales/sales_initial_data.md` (append+backfill lane), `.../domains/_mem_clean/loyalty/knowledge_base.md` (3-layer DELETE), `company/scb/datax/knowledge/framework-architecture.md` (config-driven), `company/project_sandbox/data-ml-ai-pipeline/knowledge_chat/aia-kafka-*` (AIA Strimzi/Debezium-1.9.7/auto-create-topics), `knowledge/architecture-modern-data-ai.md` + `ai-rag-agent-reference.md` + `lumora/.../07_platform_design.md` (AI), `roles/technical/{architect,engineer}/*` (best-practice + Tecton→Databricks).
