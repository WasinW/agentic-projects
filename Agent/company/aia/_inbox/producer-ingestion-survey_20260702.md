# Streaming Producer / Ingestion Architectures — Survey (Part 1 of 3)

> **Scope: source → CHANGE CAPTURE → TRANSPORT → topic/stream ready for a consumer.** Part 2 = consumer+ETL, Part 3 = ML/AI (in `de-streaming-architecture-and-ai-survey_20260702.md`). Audience: สิน (Senior DE @ AIA — the producer side IS the job: Strimzi/Debezium/Kafka on AKS).
>
> **⚠️ KB-VALIDATED CORRECTIONS (2026-07-02) — read these before trusting the body below; canonical version = `skills/de-solution-architecture/SKILL.md`:**
> 1. **The-1 was mis-stated as "CloudRun→Kafka→Dataflow" — WRONG.** The-1's producer = **app-emitted domain events (P15)**: loyalty microservices emit events to Kafka; Wasin's team owned the *consumers* (Dataflow). CloudRun at The-1 = API-poll batch → GCS (the C1 pattern), never a Kafka producer.
> 2. **AIA runs Debezium 1.9.7.Final** → the "Debezium 3.4+ ROWID incremental snapshot / drop-transaction" advice is a **2.x/3.x feature AIA cannot use today**; gate it on an upgrade.
> 3. **AIA transport as-is = self-managed Strimzi Kafka on AKS.** Event Hubs (B7/C2) is a *proposed* peel-off lever, not the current stack.
> 4. Add (his actual job): **config-driven producer onboarding + fail-loud validation** (SCB single-active-row; AIA connector-YAML), **topic governance** (AIA auto-create topics = weak governance), **data-contract-in-repo+CI**, **DR/twin topology**.

```
 SOURCE ──► [1 CHANGE CAPTURE] ──► [2 TRANSPORT] ──► topic/stream (→ Part 2 consumer)
 Oracle/    log-CDC · query-poll     self-Kafka(Strimzi) · managed(Confluent/MSK)
 SQLServer/ trigger · snapshot       Redpanda/WarpStream · PubSub/Kinesis/EventHubs
 PG/App     app-emitted(outbox/ES)   or KAFKA-LESS → object store
```
**The decision that cuts across everything:** *do you actually need a broker?* Capture (Debezium) and transport (Kafka) are **separable** — Debezium Server / native CDC / SaaS keep CDC while deleting the Connect cluster or the broker entirely. Pick the lightest thing meeting latency + fan-out + replay needs.

## A. All plausible producer architectures (P1–P25)
| # | Name | capture | transport |
|---|---|---|---|
| P1 | **Debezium/Strimzi → Kafka** (AIA) | log-CDC | self-Kafka |
| P2 | **Debezium Server → Pub/Sub** (no Connect cluster) | log-CDC | Pub/Sub |
| P3 | Debezium Server → Kinesis | log-CDC | Kinesis |
| P4 | **Debezium Server → Event Hubs** | log-CDC | Event Hubs |
| P5 | Debezium Server → Pulsar/Redis/RabbitMQ | log-CDC | other bus |
| P6 | **Debezium Engine (embedded lib)** — no server/broker | log-CDC | in-process |
| P7 | **GCP Datastream (native serverless)** | log-CDC | managed/Kafka-less |
| P8 | AWS DMS → Kinesis | log-CDC | Kinesis |
| P9 | AWS DMS → MSK / S3 | log-CDC | MSK/S3 |
| P10 | Azure Synapse Link / ADF CDC | native CDC | managed/Kafka-less |
| P11 | JDBC-poll / Kafka Connect | query-based | Kafka |
| P12 | Query-based micro-batch → object store | query-based | Kafka-less |
| P13 | Trigger-based → shadow table → CDC | trigger | any |
| P14 | **Outbox pattern + Connect** (domain events) | app-emitted | Kafka/any |
| P15 | App → Pub/Sub/Kinesis/Event Hubs direct | app-emitted | native bus |
| P16 | **Redpanda + Debezium** (Kafka-API, no ZK) | log-CDC | Redpanda |
| P17 | **WarpStream/AutoMQ + Debezium** (diskless, S3) | log-CDC | diskless Kafka |
| P18 | Confluent Cloud fully-managed connector | log-CDC | managed Kafka |
| P19 | MSK + MSK Connect (Debezium) | log-CDC | managed Kafka |
| P20 | Fivetran managed CDC | log-CDC (SaaS) | Kafka-less→warehouse |
| P21 | Airbyte CDC (cloud/OSS self-host) | log-CDC | Kafka-less |
| P22 | Estuary Flow (exactly-once) | log-CDC (SaaS) | either |
| P23 | Striim/Streamkap/Qlik/GoldenGate (enterprise, Oracle-heavy) | log-CDC (commercial) | any |
| P24 | Full-snapshot / batch export | snapshot | Kafka-less |
| P25 | PeerDB → Kafka/warehouse (PG-specialized) | log-CDC | either |

## B. Commonly-adopted (cost band = infra+license; headcount called out)
- **B1 Debezium/Strimzi → self-Kafka (P1, AIA)** — max control/flex, no per-GB tax, no lock-in. ~$500–1.5k/mo infra + **~0.3–0.5 FTE ops**. Justified when Kafka is a shared platform.
- **B2 GCP Datastream native (P7)** — lowest-ops, serverless, idle=$0. ~$300–3k/mo; driver = **$2/GiB CDC** (bites on high-churn). Pure replication.
- **B3 AWS DMS Serverless → Kinesis/MSK/S3 (P8/P9)** — ~$120–2k/mo; **~$0.08/DCU-hr**. Oracle LogMiner finicky at scale.
- **B4 Confluent Cloud + managed Debezium (P18)** — buy the whole producer (Kafka+connector+SR+Flink). ~$1–3k/mo + egress. Lowest-ops all-in.
- **B5 MSK + MSK Connect (P19)** — ~$500–2k/mo (billed on broker infra); middle ground.
- **B6 Fivetran/Airbyte (P20/P21)** — zero-infra; driver = **row-change volume (MAR)** — punishes high-churn CDC.
- **B7 Event Hubs (Kafka API) transport (P4/P15)** — Azure-native bus; ~$25–300/mo (Standard TU ~$22/mo). Natural managed transport for Azure + Debezium Server.

## C. Lean / low-cost (cheapest first) — delete the broker, delete 24×7
| # | stack | cost | why cheap |
|---|---|---|---|
| C1 | **Query micro-batch → object store** (P12/P24) | $50–400 | no CDC engine, no broker; loses deletes |
| C2 | **Debezium Server (1 container) → Pub/Sub / Event Hubs** (P2/P4) | $60–500 | full log-CDC, **no Connect cluster, no broker fleet** — best lean CDC |
| C3 | Datastream → BQ/GCS serverless (P7) | $150–1.5k | idle=$0, free tier |
| C4 | Estuary Flow (P22) | $100–800 | $0.50/GB + $100/connector; exactly-once |
| C5 | DMS Serverless → S3 (P9) | $120–600 | scales to min DCU idle |
| C6 | **Debezium Engine embedded** (P6) | ~$0 extra | in-process; no server/broker; at-least-once, single consumer, no replay |
| C7 | **WarpStream/AutoMQ/Redpanda + Debezium** (P16/P17) | $300–1k | diskless S3, no ZK, no cross-AZ tax; keep Kafka API + replay |
| C8 | Airbyte OSS self-host (P21) | $100–400 | free software + compute |

**Lean golden rule (producer):** you rarely need BOTH a Connect cluster AND a broker for a first pipeline. One sink, no replay → **Debezium Server (C2) or Engine (C6)**. Need replay/fan-out but cheap → **diskless Kafka (C7)**. Freshness >5–15 min → **query micro-batch (C1)** beats any streaming CDC.

## Engineering points
**1. Capture technique matrix**
| technique | latency | deletes? | intermediate states? | source load | verdict |
|---|---|---|---|---|---|
| **log-based** (Debezium/DMS/GoldenGate/Datastream) | sub-sec–sec | ✅ | ✅ | **low** (reads redo/WAL/binlog) | default; tax = setup (Oracle supplemental logging, SQLServer CDC, PG wal_level=logical) |
| **query-based** (JDBC poll/watermark) | min+ | ❌ | ❌ | **high** (repeated SELECT) | cheap/simple; fails on deletes; needs monotonic column |
| **trigger** | sub-sec | ✅ | ✅ | **highest** (write-amp) | avoid unless no log access |
| **snapshot/batch** | hours | ✅(diff) | ❌ | spiky | good for SCD + backfill only |
| **app-emitted (outbox/ES)** | sub-sec | n/a | ✅ | none | best semantic events; needs app ownership |

Oracle gotcha (AIA): supplemental logging + LogMiner has real source overhead; Debezium 3.4+ ROWID incremental snapshot + drop-transaction signal help; huge/hot Oracle → weigh XStream(GoldenGate license)/commercial engines.

**2. Debezium deployment modes**
- **Kafka Connect (Strimzi)** = buffering + replay + fan-out + DLQ + SMT + scaling, at cost of a cluster.
- **Debezium Server** = 1 source→1 sink container, **removes the Connect cluster (and optionally Kafka)** → sinks straight to Pub/Sub/Kinesis/Event Hubs. Right call when target is one native bus + no in-Kafka processing.
- **Embedded Engine** = library in your app/Flink; removes server+broker; at-least-once, single consumer, no replay.

**3. Kafka vs Kafka-less vs diskless** — need a broker only for multi-consumer / replay / in-stream processing / backpressure. Redpanda = Kafka API, no ZK, lower latency. WarpStream/AutoMQ = diskless S3-backed, ~77% cheaper at scale but 100s-ms latency (fine for CDC/ETL, not fraud/trading).

**4. Initial snapshot/backfill** — biggest surprise-bill + outage risk. Blocking snapshot can lag redo logs → fail. Use **incremental snapshot (signaling)**: concurrent with CDC, resumable, per-table on demand; ROWID chunking for big Oracle. Or bulk export → object store + start CDC from known SCN/LSN.

**5. Schema registry / DLQ / ordering / exactly-once** — SR (Confluent/Apicurio/Glue) enforces the contract on the producer; Debezium Server loses Connect's SR+DLQ → handle out-of-band. Order = key by PK (per-partition). Debezium = **at-least-once**; achieve EOS via idempotent upsert on PK+LSN downstream — design consumers idempotent.

**6. Build vs buy** — self-managed Strimzi (~0.3–0.5 FTE, max flex, no lock-in) vs managed Kafka (Confluent/MSK, ~0.1–0.2 FTE) vs serverless CDC (Datastream/DMS/Fivetran, ~0 FTE, per-GB/MAR, high lock-in). Most orgs over-build: <10 tables + pure replication → serverless CDC beats standing up Strimzi. Strimzi wins when Kafka is a platform many teams consume.

**7. Outbox vs raw CDC** — outbox = app writes semantic domain event in same txn, Debezium CDCs only the outbox table (clean events, no dual-write). Raw CDC = faithful replication (analytics). AIA = mostly raw (replicating vendor/core DBs); outbox where AIA owns the producing service.

## Decision guide (source/latency/ops/cloud → stack)
- Azure, few sinks, minimal infra → **Debezium Server → Event Hubs** (P4)
- Azure, Kafka shared platform, many consumers → **Strimzi + Debezium** (P1, keep)
- GCP pure replication → **Datastream native** (P7)
- GCP + enrichment/multi-sink/replay → Kafka(Redpanda)+Debezium / CloudRun→Kafka
- AWS-native → **DMS Serverless → Kinesis/MSK/S3**
- High-volume, 200ms+ OK, cost-sensitive → **WarpStream/AutoMQ + Debezium**
- Sub-100ms self-managed → **Redpanda + Debezium**
- Small team, few sources → **Fivetran/Airbyte/Estuary**
- Freshness >15 min → **query micro-batch** (skip CDC)
- Own the app, want domain events → **Outbox + Debezium**
- Huge/hot Oracle, LogMiner hurts → **GoldenGate/Qlik/Striim** or XStream
- No replay/fan-out, durable sink → **Debezium Server / Engine** (no broker)

**Savings order:** (1) need a broker at all? (2) serverless CDC vs self-run Connect (3) diskless/S3 vs disk Kafka (4) log-CDC only where deletes/freshness demand.

## AIA-specific
**Keep Strimzi as the platform, but it's likely over-provisioned per-source; Debezium Server is the simplification lever.**
1. **Peel single-sink lanes to Debezium Server → Event Hubs** — if a source only feeds Databricks + needs no in-Kafka processing/fan-out, a Debezium Server container removes the `dtp_kafka_connector` Connect runtime for that lane (Event Hubs speaks Kafka API → Databricks reads unchanged). Highest-leverage simplification.
2. **One KafkaConnect runtime hosting many KafkaConnector CRs** — don't sprawl a Connect cluster per source.
3. **Incremental snapshot (signaling) + ROWID chunking** for onboarding big Oracle tables (avoid blocking snapshot / redo-log aging).
4. **Add Apicurio Schema Registry** (Strimzi-native) for producer-side DDL governance; keep Connect DLQ — moving a lane to Debezium Server loses free SR+DLQ, so only move lanes where acceptable.
5. Weigh **Confluent Cloud managed connectors** if ops burden isn't buying enough flex (regulated insurer may value SLA + "one throat to choke").
**Net:** keep Strimzi for the shared multi-consumer high-churn core; peel single-sink lanes to Debezium Server → Event Hubs. Same CDC guarantees, less to operate.

## The-1-specific
- CloudRun→Kafka→Dataflow justified only for mid-stream enrichment / multi-consumer / replay. Pure replication → **Datastream native** (kills CloudRun + Kafka + Dataflow; idle=$0; land changelog to BQ/GCS, collapse in Part-2 view/MERGE).
- Keep Kafka only for lanes that fan out/enrich; if kept, use **Redpanda/WarpStream** over self-managed (no first-party managed Kafka on GCP).
- 24×7 CloudRun polling low-volume changes = same anti-pattern as 24×7 Dataflow; Datastream idle=$0 fixes it.

*Sources: Debezium Server/Oracle/incremental-snapshot docs · Datastream/DMS/Confluent/MSK/Event Hubs pricing · WarpStream/AutoMQ/Redpanda TCO · Fivetran/Airbyte/Estuary pricing. DRAFT — validate vs Agent KB then finalize.*
