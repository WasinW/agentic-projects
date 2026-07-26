# ADB consume Kafka + stream-to-stream join — CURATED (with verified corrections)

> Reorganized by Claude from the 9-turn Google AI Mode chat. Raw: `adb-consume-stream-join-FULL_20260724.md`.
> **This is a teammate's use case** (Sin consulting on their behalf), not Sin's own workstream.
> Provenance: **[chat]** = Google AI · **[🧠 Claude ✅verified]** = corrected + verified by databricks-expert.
> ⚠️ **The chat's headline "Solution 1" is architecturally WRONG — see §2.** Read the corrections.

## 0. Use case [chat]
Consume **2 Kafka streams (Orders + Payments)** → **stream-to-stream JOIN** → write to **SQL Server**.
Volume ~**10M rec/min (~166k rec/s)**, join context ~40M-row table, latency SLA **1–5 min**, and the
hard requirement: **the Payments stream can be LATE by up to a DAY** (payment system may be down a day),
yet the join must still match and totals must be accurate. No intermediate bronze "buffer" desired
(transform-on-the-fly from Kafka → SQL Server).

## 1. What the chat got RIGHT [chat, verified]
- Databricks consumes via **Spark Structured Streaming** (`spark.readStream.format("kafka")`), micro-batch
  by default (Continuous mode exists but niche). ✅
- **Stream-stream join needs watermark on both sides + a time-bound**, and state is held to wait for the
  match. ✅ (Q5, Q6)
- **`withWatermark` works ACROSS micro-batches** (not within one batch): Spark tracks max event-time seen,
  minus the allowed lateness, = the watermark line; data older than it is dropped and its state evicted. ✅ (Q6)
- **The core problem is real** (Q7): a **multi-day watermark = unbounded state → OOM**. Correct diagnosis.

## 2. 🚩 What the chat got WRONG — "Azure Databricks PyFlink" [🧠 Claude ✅verified: REFUTED]
- Google AI's **"Solution 1 = PyFlink on Databricks"** (Flink JobManager/TaskManager running on a Databricks
  cluster, Flink RocksDB State Backend + State TTL for multi-day state) is a **fabrication**.
- **Databricks does NOT run Apache Flink/PyFlink as a cluster engine.** A Databricks cluster runs **Spark**;
  the streaming engine is **Spark Structured Streaming**. There is no Flink JobManager/TaskManager on
  Databricks compute — that topology + "State Backend" + "State TTL" is **Flink vocabulary** mis-mapped onto
  Databricks.
- Flink + Databricks only legitimately co-occur as **separate compute**: *DeltaStream for Databricks* (3rd-party,
  Flink is DeltaStream's engine surfaced in the DBX UI) or *HDInsight-on-AKS Flink* (separate Azure service that
  can write into Delta). Neither is "Flink on a Databricks cluster."

## 3. RocksDB — correct attribution [🧠 Claude ✅verified: CONFIRMED, but it's SPARK's]
- The **RocksDB on-disk state store** the chat praised is a **real Spark/Databricks feature** — NOT Flink's.
  State lives **off-heap on local disk (spills)** → avoids JVM-heap OOM.
- Enable: **DBR 17.3+** → RocksDB + changelog checkpointing **default**. Below 17.3 (DBR 13.3 LTS+): set
  `spark.sql.streaming.stateStore.providerClass=...RocksDBStateStoreProvider` + changelog checkpointing.
- ⚠️ RocksDB lets big state **spill to disk** — it does **NOT** make an *unbounded multi-day-watermark join*
  cheap. At 166k/s a 1-day window ≈ ~14B records buffered — huge/slow-to-checkpoint on **any** engine
  (Flink included). So "just use Flink State TTL for a day" moves the same enormous state elsewhere; it
  doesn't solve it. **Get the state out of the streaming join entirely.**

## 4. ✅ The corrected architecture [🧠 Claude ✅verified — recommended]
Key insight: **Payments are late, Orders are on-time** → the match completes **when the payment arrives**, and
the order has been sitting durably for up to a day. So make the durable side a **Delta table**, not hot join state.

```
Orders  (Kafka) ──readStream──► foreachBatch MERGE ──►  orders_ref  (Delta, liquid-clustered on join key, durable)
                                                              │
Payments(Kafka) ──readStream──►  stream-STATIC join  ◄────────┘   (stateless, NO watermark; day-late payment still matches)
                                        │
                                        ├─ matched   ──► enriched ──► foreachBatch: staging bulk-insert + set-based MERGE ──► SQL Server
                                        └─ unmatched ──► pending_payments (Delta)
                                                              │
                    scheduled batch reconciliation (CDF over orders_ref + pending_payments) ──► re-emit late / out-of-order matches
```

**Why this beats a stream-stream join:**
- **stream-static join is stateless, needs NO watermark**, and re-reads the **latest Delta version every
  micro-batch** → a payment arriving a full day late still finds its order (order persisted in `orders_ref`
  since yesterday). The multi-day "state" lives in **Delta on cheap ADLS** (columnar, data-skipped, Photon),
  not a hot state store. **No unbounded state, no multi-day-watermark OOM.**
- **Don't silently drop unmatched** (payment whose order isn't present yet) → route to `pending_payments`,
  let the **batch reconciliation** re-attempt. This is the completeness backstop.

**Alternatives (only if needed):**
- **(b) bounded-watermark stream-stream join (1–2h) + batch reconciliation** — if the immediate emit before
  payment has business value. More moving parts.
- **(c) real Flink OFF Databricks** (AKS/Confluent/HDInsight) — only if true per-message multi-day-TTL
  stream-stream is non-negotiable AND you can't restructure to (a). Rarely worth it in an Azure+Databricks shop.

## 5. DLT vs raw Structured Streaming [🧠 Claude ✅verified: PARTLY]
- DLT/Lakeflow **CAN** do the stream-stream join (watermark both sides). BUT there is **no native, first-class
  DLT sink for SQL Server via JDBC upsert**, and DLT doesn't expose `foreachBatch` like raw SS.
- → For **Kafka → join → SQL Server upsert**, use **raw Spark Structured Streaming + `foreachBatch`** (the
  control + imperative JDBC sink you need). Optional hybrid: DLT for the Delta medallion landing +
  a Structured Streaming job for the enrich-join + JDBC push.
- ⚠️ Verify the current DLT external-sink surface on the target DBR before relying on it (strong prior: no
  native SQL Server sink).

## 6. Feasibility 166k rec/s [🧠 Claude ✅verified: PARTLY — the JOIN is fine; the SQL Server SINK is the risk]
- **Join feasible** with Photon + parallelism: Kafka partitions ≥ target parallelism; bound each batch with
  `maxOffsetsPerTrigger`. **40M rows (~8 GB) is NOT broadcastable** → shuffle/sort-merge → **liquid-cluster
  `orders_ref` on the join key**, keep files compacted, lean on data-skipping.
- **SQL Server sink is the real bottleneck.** **166k upserts/s into Azure SQL MI is extremely demanding.**
  Mitigate: `foreachBatch` → **bulk-insert to staging → one set-based `MERGE`** (never row-by-row); partitioned
  parallel JDBC; batched writes; index the merge key. **Strongly consider decoupling:** write enriched result
  to **Delta first** (absorbs 166k/s easily) → separate, controlled push to SQL Server (replay + backpressure).
- Latency: a `processingTime` trigger of ~30–60s meets the 1–5 min SLA comfortably (don't run tighter — cost lever).

## 7. Open items / uncertainties [🧠 Claude]
- **Load-test the SQL Server sink** (staging+MERGE and the Delta-decoupled variant) — feasibility depends on the
  SQL MI tier + indexing, not a paper answer. This is the #1 risk.
- Verify DLT SQL-Server sink surface on their DBR.
- Confirm `orders_ref` row width (the ~8 GB / broadcast reasoning assumes ~200 B/row).
- Code templates for Kafka read / checkpoint / empty-batch guard / dedupe-MERGE / DLQ split are in skill
  `databricks-streaming-pattern` (§1,2,5,6) — reusable, generic.
- Since it's a teammate's system: Sin can offer the corrected pattern (stream-static + Delta upsert) — the
  main message is **"don't build on 'Databricks PyFlink' — it doesn't exist; use stream-static join on Delta."**
