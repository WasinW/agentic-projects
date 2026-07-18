# Insight / Customer-Profile — Production Incidents

> **Platform:** The-1 customer-profile pipeline (`customer-profile-v3-streaming`) on GCP — Apache Beam / Dataflow Runner v2 + Streaming Engine, Pub/Sub source, BigQuery Managed Iceberg (BigLake) sink, cross-cloud Parquet export to AWS S3.
> **Engineer:** Wasin (Senior Data Engineer, NTT DATA on-site at Central The-1).
> **Scope:** Past project. This is a *technical post-mortem KB* capturing root-cause depth and the fixes shipped — not live ops runbooks.

## Why these incidents matter

These three incidents all sit on the same fault line: **a streaming pipeline that does slow, blocking, or schema-fragile I/O on its critical path.** Dataflow's Streaming Engine is unforgiving here — a `DoFn.process()` that blocks too long doesn't just slow down, it gets the SDK harness killed; a watermark held by a blocking sink silently accumulates hours of lag; and a BigQuery table whose *type* is incompatible with the write method orphans production data on disk. Each fix moves slow/fragile work **off the streaming hot path** or **fails it loud at deploy time** — the two reusable principles that run through everything below.

Common stack facts (cited per incident):
- Workers: `n1-standard-2` (2 vCPU, 7.5 GB), autoscale 2–8, Runner v2 + Streaming Engine, `sdk_worker_parallelism=1`, `no_use_multiple_sdk_containers`.
- Source: Pub/Sub (7-day message retention — this number bounds the blast radius of every consumer outage).
- Sinks: BQ Managed Iceberg (`asia-southeast1`) + Parquet to S3 `ap-southeast-1` (cross-cloud from GCP `asia-southeast1`).

---

## Incident 1 — SDK harness crash on the cross-cloud S3 write path (≈7-day PROD data loss)

**Audited:** 2026-03-24 | **Window:** 2026-03-16 → 2026-03-23 | **Env:** PROD

### Symptom
- Pipeline ran clean for ~1–2 weeks after launch (started 2026-03-02), then began crashing around 2026-03-16.
- **790 SDK-harness disconnects over 8 days**; a crash roughly every ~15 minutes. Primary harness `sdk-1-0`: 308 disconnects; secondary `sdk-0-0`: 151. "Expected 2 SDK Harnesses, but only 1 registered": 216.
- Autoscaler stuck in a loop: "Raised to 8. Would have added more but reached maximum" repeated hundreds of times, every 2–3 min — new workers crashed almost immediately after creation.
- Pub/Sub backlog grew with no healthy consumer.

### Impact
- **~7 days of PROD data lost** — Pub/Sub messages expired at the 7-day retention boundary before any consumer recovered.
- Downstream starved: S3 consumers got no new data from crash onset; BQ CDC (driven off the same consume) also stalled.
- Wasted spend on the autoscale → crash → autoscale churn (workers billed but crashing on startup).

### Root cause (deep)
Two factors compounded — a **trigger** and an **amplifier**:

**Amplifier — the S3 write path blocks the worker thread.** `Step 10 / WritePartitionToParquetDoFn` did, per window:
1. `FixedWindows(300s)` → `GroupByKey`, buffering **5 minutes of records in memory** per key/window.
2. `pd.DataFrame(records)` over a `list(records)` — the entire window collected into a Python list (the exact anti-pattern Google's OOM guide warns about: GBK values are *streamed* and need not fit in memory, but the moment you `list()` them into an in-memory object you reintroduce the memory + single-thread cost).
3. Cast **every column of every row to STRING** via `.apply(str)` — CPU-heavy, runs in pandas/PyArrow C extensions.
4. `pq.write_table(compression='snappy')` — serialize + compress the whole batch (PyArrow C extension).
5. `FileSystems.create("s3://…")` — write **cross-cloud** (GCP `asia-southeast1` → AWS `ap-southeast-1`), single-threaded per partition, high-latency with retries on network jitter.

Steps 2–5 hold the **GIL** for the whole batch (pandas + PyArrow + snappy are C/C++ extensions; the blocking S3 socket I/O sits inside the same `process()` call). On a 2-vCPU box with `sdk_worker_parallelism=1`, while that thread is blocked the SDK harness **cannot answer the runner's gRPC keepalive ping**. The ping deadline is **hardcoded in the Dataflow runner infrastructure — there is no pipeline option to raise it.** Missed ping → `StatusCode.UNAVAILABLE: ping timeout` → data-plane disconnect (`data_plane.py:703 _read_inputs`) → "SDK harness disconnected" → worker marked unhealthy → "Failed to UpdateWorkProgress for 5 minutes" → work item retried on a fresh worker → which hits the same slow S3 write → **crash loop**.

**Why it ran fine for a week first:** the batch grew over time. Early on, low volume → small in-memory buffers → fast writes that finished inside the ping window. As backlog accumulated, buffers grew → writes took minutes → crossed the ping deadline. Classic slow-burn: the failure mode is latent until per-element processing time crosses the (invisible, fixed) keepalive threshold.

**Trigger — the stateful-write crash that started the cascade.** The V3 pipeline added `WriteConsentsToBigQuery` *without* `use_at_least_once=True`. Default Storage Write API uses COMMITTED streams, which route through a stateful `GroupIntoBatches`; during an autoscale event the runner reshuffles keys and **invalidates that in-flight state**, producing the first crash. Once the pipeline was knocked into recovery, the already-slow S3 write path made recovery impossible — every retried bundle re-blocked the thread. (V1 didn't crash because it wrote consents to Iceberg instead of via Storage Write API, so it had no stateful-batch failure point.)

Why the obvious knobs don't fix it (validated against Google docs + Beam issue #25273): you can't raise the gRPC ping timeout; Python Beam has no async `DoFn`; `element_processing_timeout_minutes` only *restarts* the harness faster (no cap on streaming restarts → same loop); lowering harness threads or bumping machine type are workarounds, not fixes. Beam team's own position: "SDK harness disconnected is a symptom, not a root cause." The real fix had to remove the blocking I/O from the streaming path.

### Fix
Split Step 10 into a fast same-cloud streaming write + a decoupled hourly compaction to S3:

- **Step 10a (streaming, per-record, no GroupByKey):** Pub/Sub → transform → `FixedWindows(300s)` → `WriteRecordToGCSDoFn` writing small Parquet files to a **GCS buffer in the same region** (ms-latency, non-blocking). No `list(records)` collection; micro-batched flushes (~100 records) keep per-call time well under the ping deadline.
- **Step 10b (hourly batch):** `PeriodicImpulse(3600s)` → `CompactAndCopyToS3DoFn` reads the GCS small files per partition, compacts to ~10 Parquet files, and does the cross-cloud S3 copy **off the streaming critical path** (the slow cross-cloud copy now happens in a once-an-hour batch stage, so its latency can't hold up record consumption).
- Also fixes the small-file problem the buffer would otherwise create (many tiny GCS files → 10 compacted files per partition per hour on S3).

Config (tunable without code changes — `builder.py` reads these):
```python
"s3": {
    "bucket": "s3://t1-analytics/refined/insights/ms_personas_{env}",
    "gcs_buffer_path": "gs://the1-insight-{env}-data-pipeline-data-staging/outbound/ms_personas",
    "compact_interval_sec": 3600,   # tune to 600/300 without rebuild
    "compact_target_files": 10,
}
```
Files: `pipeline/dofns.py` (+`WriteRecordToGCSDoFn`, `CompactAndCopyToS3DoFn`), `pipeline/builder.py` (Step 10 → 10a+10b), `config/settings.py` (new `s3.*` keys). Trigger side: add `use_at_least_once=True` to the consents write to avoid the stateful COMMITTED-stream crash. Residual risk noted: compaction still runs on a Dataflow worker; if it ever blocks, move it to a Cloud Function / separate batch job.

### Reusable lesson
**Never put slow or cross-region/cross-cloud blocking I/O inside a streaming `DoFn.process()`.** The runner's liveness check (gRPC keepalive on Dataflow; analogous heartbeats on Flink/Spark Structured Streaming) has a fixed deadline you usually can't tune — a blocked thread reads as a dead worker and triggers a crash-and-retry loop that is *worse* than the original slowness. Buffer to same-region storage on the hot path, then move slow egress to a decoupled periodic/batch stage. And **never `list()` a GroupByKey iterable** — it converts a streamed value into an in-memory blob and reintroduces both OOM and single-thread-blocking risk.

### CV bullet
Diagnosed and resolved a Dataflow SDK-harness crash loop (790 disconnects in 8 days) that caused ~7 days of production data loss, root-causing a cross-cloud S3 write blocking the gRPC keepalive thread; re-architected the sink into a same-region GCS buffer plus hourly compaction-to-S3, eliminating the crash loop and restoring stable delivery.

---

## Incident 2 — PeriodicImpulse watermark held by a blocking 3 GB S3 copy (14–32 h export lag)

**Window:** observed across sessions, status checked 2026-04-08 | **Env:** PROD

### Symptom
- `ExportPersonasToGCS` lagged real-time by **14–16 h**; `CopyPersonasToS3` lagged **1 day+** (measured up to ~32 h on 2026-04-08: GCS output had `par_day=06` complete, `par_day=07` only to `par_hour=14`, `par_day=08` missing).
- Dataflow UI showed `S3ExportImpulse` **Data Lag: 1 day 10 hr**.
- The parallel `ExportConsentWindow` path — **same building blocks** — had no lag at all. That asymmetry was the diagnostic key.

### Impact
- S3-side consumers of `ms_personas` were served data 14 h to 1.5 days stale — a freshness SLA breach on the customer-profile export, not a data-loss event.

### Root cause (deep)
Both paths use `PeriodicImpulse → FixedWindow → CombineGlobally(signal) → export`. The difference is **what advances the watermark and how long the export blocks**:

- **Consent path (healthy):** its export window is fed by the *output of an upstream `SQLSubmitDoFn`* (the BQ history load), which **emits one element per window when the query completes** — so the watermark is *data-driven* and advances every round. It is also **re-windowed 300s → 3600s**, batching ~12 signals into one export per hour, over a **small** table. Export finishes well within the hour → no backlog.

- **Personas S3 path (lagging):** driven by a **separate `S3ExportImpulse` that is a pure timer** (`PeriodicImpulse`, `fire_interval=300s`), with **no re-window** — every 5-minute fire triggers a full export. Each fire ran `EXPORT DATA` over the whole `ms_personas` table (~3 GB) → wrote Parquet to GCS → `CopyGCSToS3DoFn` did a **boto3 blocking upload of ~3 GB cross-cloud to S3**. That copy takes **minutes**, i.e. longer than the 300 s fire interval. While the `DoFn` blocks, Dataflow **holds the watermark of that window open until `process()` returns** — but the impulse keeps firing every 5 min (288×/day), so windows queue up faster than they drain. Lag = accumulated backlog, growing to 14 h → 32 h.

Crucially this was **not** "EXPORT DATA is slow" (BQ export was fast in the logs) and **not** "interval too fast" in isolation — it was **fire-rate (12×/hour) × blocking-copy-time (minutes) over a large payload**, with no batching to amortize it, while the consent path got all three right by accident of its data-driven, re-windowed design.

### Fix
Match the personas path to the consent pattern — **slow the fire rate so each blocking copy finishes before the next fire**, done at config level (no code rebuild):

```python
# settings.py — customer_profile/config
"s3": { "export_interval_sec": 3600 },   # was 300 (5 min) → 1 hour
```
This drops exports from 12×/hour to 1×/hour, cutting workload 12× and giving the 3 GB copy ample headroom before the next window — watermark advances normally, lag collapses toward ~1 hr. (Equivalent code-level option: re-window `FixedWindows(300s)→FixedWindows(3600s)`. Stronger long-term option, deferred: drop the pure-timer impulse and drive the export off a data-driven trigger like `SyncToIceberg` output, but that needs pipeline rewiring.)

**Deploy-gap caveat (the real-world lesson):** the code fix sat in `settings.py` but the running job kept lagging — **streaming Dataflow jobs read config only at launch and do not hot-reload.** The fix only takes effect after **drain + restart** of the job (and verifying the new image with `export_interval_sec: 3600` is actually built/pushed to GAR before relaunch). "Merged" ≠ "applied" for long-lived streaming jobs.

### Reusable lesson
**On a streaming pipeline, your effective throughput on a blocking sink is `payload_size ÷ fire_interval` — if one invocation can't finish before the next trigger, lag accumulates without bound and the watermark stalls silently** (no error, just growing lag). Right-size the trigger interval to the *actual* blocking time of the slowest sink, batch large exports rather than firing them on a tight timer, and prefer data-driven watermark advancement over pure timers. And operationally: **config changes to streaming jobs require drain + restart**, not just a merge — always confirm the running job picked up the new config.

### CV bullet
Eliminated a 14–32 h freshness lag on a 3 GB cross-cloud S3 export by root-causing a Beam `PeriodicImpulse` watermark stalled behind a blocking sink, then right-sizing the export interval (5 min → 1 h) to amortize copy time — reducing export lag from ~1.5 days to ~1 hour via a config-only change plus a drain/restart deploy.

---

## Incident 3 — `events_consents`: table-type flip + column rename orphans PROD data

**Date:** 2026-01-28 | **Priority:** Critical (production data) | **Env:** PROD

### Symptom
- The V1 pipeline (`WriteToBigLakeIcebergStreamingStep`, Storage Write API) could **no longer write** to `insight.events_consents`.
- Historical data physically present in GCS became **unreadable** through the table.

### Impact
- Production consent table down: writes failing, historical data orphaned (still on disk at `gs://…-data-staging/iceberg/events_consents/`, but no table pointing at it). Consent data is **compliance-relevant** (PDPA), so a silent break here is high-severity.

### Root cause (deep)
Three rapid table redefinitions, each breaking a different invariant of the BigQuery + Storage Write API + Iceberg contract:

- **Original (working):** `table_type: iceberg` (BigQuery *Managed* Iceberg) — Storage Write API **supported**, BQ manages Iceberg metadata, 4-col schema (`personasId` REQUIRED, `memberId`, `consents`, `processDate`).
- **Change #1 → `external_iceberg`:** **Storage Write API does not support `external_iceberg` tables** (external = *you* manage the Iceberg metadata, so BQ won't accept streaming writes into it). The V1 pipeline's write method instantly became invalid; a new empty table was created at a different `dataset_id` (`insight`→`source`) and storage bucket, leaving the original GCS data orphaned.
- **Change #2 → `native`:** `deploy.py` detected breaking changes (type mismatch + partition mismatch), its backup step **failed because the table was already empty** from Change #1, and it then **dropped the old table and created a fresh `native` table** — native tables have **no GCS connection at all**, so the historical Parquet in GCS is now completely orphaned. V1 can write to native, but in a format incompatible with the historical files.
- **Compounding — schema drift:** the redefinitions also renamed the primary key **`personasId` → `personaId`** (dropped the `s`) and replaced `processDate DATE` with `partitionTime STRING` plus new columns. The historical Parquet was written with `personasId`/`processDate`; a table declaring `personaId` **cannot read those files back** even if repointed — the read fails on the column-name mismatch.

So three independent breakages stacked: **(1) write method incompatible with the new table type**, **(2) drop/recreate orphaned the physical data**, **(3) column rename broke read-back of the orphaned data.** The deeper failure was process: breaking changes were applied straight to PROD, and `deploy.py` *detected* the breaking change but **proceeded anyway** (and its backup precondition silently no-op'd on an empty table).

### Fix
Recover by restoring a Managed-Iceberg table pointed at the surviving GCS data, with a schema that matches what's physically on disk:
1. **Pre-flight + backup:** confirm GCS data exists, then `gsutil -m cp -r` it to a timestamped backup; **abort if the data isn't there.**
2. **Verify readability** with a temporary recovery table using the **original** schema (`personasId`/`processDate`) pointed at the existing `storage_uri` — count rows and check the date range before touching anything destructive.
3. **Drop** the broken (empty) `native` table; **recreate** as Managed Iceberg (`WITH CONNECTION … OPTIONS(file_format='PARQUET', table_format='ICEBERG', storage_uri='…/iceberg/events_consents/')`).
4. **Resolve the rename deliberately:** keep `personasId` to read old data immediately, *or* adopt `personaId` going forward and migrate old files — you cannot have both for free, because the physical files carry the old column name. (Documented as an explicit decision, not a silent default.)
5. Update the deploy schema JSON to `table_type: managed` with `managed_config` pointing at the staging bucket so a normal `deploy.py` run **SKIPs** (no further change) instead of re-breaking it.

### Reusable lesson
**Table *type* is part of your write contract, not a cosmetic attribute** — Storage Write API works with native and *managed* Iceberg but **not external Iceberg**; flipping type can orphan physical data and invalidate the writer in one step. Treat any change to table type, storage URI, partition spec, or a `REQUIRED`/primary-key column as a **breaking migration**: stage it first, back up *and verify the backup is non-empty* before any drop, and make deploy tooling **hard-fail (not warn-and-proceed)** on detected breaking changes. Column renames against external/Iceberg-on-GCS tables break read-back because the data files are immutable — rename is a migration, never an in-place edit.

### CV bullet
Recovered a critically broken production consent table (`events_consents`) after a table-type migration (`iceberg`→`external_iceberg`→`native`) orphaned historical GCS data and broke Storage-Write-API ingestion, restoring it to BigQuery Managed Iceberg with verified schema/data continuity and hardening the deploy process to fail-fast on breaking schema changes.

---

## Generalizable lessons → promote to `roles/de-engineer`

These are project-agnostic and worth lifting into the shared de-engineer knowledge base (listed only — do not edit `roles/` here):

1. **No blocking/slow I/O in a streaming `DoFn.process()`.** Runner liveness checks (Dataflow gRPC keepalive, Flink/Spark heartbeats) have fixed, often-untunable deadlines; a blocked thread reads as a dead worker → crash-and-retry loop worse than the original latency. Buffer same-region, egress slowly on a decoupled batch/periodic stage.
2. **Never materialize a `GroupByKey` iterable into an in-memory list.** GBK values are streamed and needn't fit in memory; `list(values)` reintroduces OOM and single-thread blocking. Prefer streaming iteration / `GroupIntoBatches`.
3. **A blocking sink's throughput is `payload ÷ trigger_interval`.** If one invocation can't finish before the next trigger fires, watermark stalls and lag grows unbounded — silently, with no error. Right-size trigger interval to real sink latency; batch large exports.
4. **Prefer data-driven watermark advancement over pure timers.** A `PeriodicImpulse` with no upstream data emission can stall behind a slow downstream `DoFn`; an upstream emit-on-completion keeps the watermark honest.
5. **Streaming jobs don't hot-reload config.** A merged config change isn't applied until drain + restart (and verify the deployed image actually contains it). "Merged ≠ running."
6. **Table type is part of the write contract.** Storage Write API ≠ supported on external Iceberg; type/storage-URI/partition/primary-key changes are breaking migrations that can orphan physical data and invalidate writers.
7. **Deploy tooling must fail-fast on breaking changes, and verify backups are non-empty before any drop.** Warn-and-proceed plus a no-op backup on an already-empty table is how a single bad change cascades into orphaned production data.
8. **Slow-burn failures cross invisible thresholds.** A pipeline that's healthy for a week can be latently broken — per-element time growing until it crosses a fixed keepalive deadline. Watch processing-time-per-element trend, not just success/failure.
