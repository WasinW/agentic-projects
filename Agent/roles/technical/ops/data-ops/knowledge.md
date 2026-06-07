# Data Ops — Comprehensive Knowledge

> Deep reference for the data-ops subagent.
> Pipeline reliability + data observability + incident response.

---

## 1. Foundations

### What Data Ops does

Keeps data pipelines + warehouses healthy in production. Applies SRE principles to the data domain.

- SLA / SLO definition + tracking
- Pipeline monitoring + alerting
- Data observability (5 pillars)
- Incident response + postmortem
- Runbooks
- Cost + performance optimization
- Capacity planning

### DataOps vs Data Engineering

- **Data Engineer** — builds + designs
- **Data Ops** — operates + reliably runs
- Significant overlap in small teams; specialize at scale

### DataOps Manifesto (worth knowing)

18 principles, key ideas:
- Continuously satisfy the customer (downstream users)
- Embrace change
- Make analytics value flow
- It's a team sport
- Daily interactions
- Self-organize
- Reduce heroism
- Reflect + adjust

---

## 2. Mental Models / Decision Frameworks

### 5 Pillars of Data Observability (Monte Carlo formulation)

1. **Freshness** — is data up to date?
2. **Volume** — is the row count what we expect?
3. **Schema** — has structure changed?
4. **Distribution** — are values within expected ranges?
5. **Lineage** — where does data come from + go to?

Monitor all 5. Most teams only monitor freshness + volume → catch only obvious issues.

### Pipeline Monitoring vs Data Observability

- **Pipeline Monitoring** — is the job running? Did it succeed?
- **Data Observability** — even if the job succeeded, is the data correct?

A pipeline can succeed AND produce bad data. Both layers needed.

### SLI / SLO / Error Budget (SRE)

- **SLI** (Indicator) — what to measure (freshness, completeness, latency)
- **SLO** (Objective) — target (99% freshness within 1 hour)
- **Error budget** — allowed unreliability (1% can be late = ~7.2h/month)

Use error budget to balance new work vs reliability work.

### Tiered SLA approach

Not all data is equal. Tier datasets:
- **Tier 1** — Critical (customer-facing, real-time): aggressive SLA, on-call
- **Tier 2** — Important (internal dashboards, reports): business-hours
- **Tier 3** — Best effort (research, archive): no SLA

Reliability cost scales steeply. Don't over-protect Tier 3.

### Incident severity classification

- **SEV1** — broad impact, customer-facing, hard outage → all-hands, page
- **SEV2** — significant but contained → page on-call
- **SEV3** — minor, workaround exists → ticket, fix next business day
- **SEV4** — informational → log only

Each tier has different response expectations.

### The 5 Whys

For incident root cause, ask "why" 5 times:
1. Why did data go stale? → Pipeline failed.
2. Why did the pipeline fail? → Source DB connection timeout.
3. Why timeout? → DB CPU at 100%.
4. Why high CPU? → Inefficient query joined unindexed columns.
5. Why no index? → Schema change didn't add the new column to index list.

Stop when you reach actionable root.

---

## 3. Standard Practices

### Monitoring tiers

**Operational**
- Job success/failure
- Pipeline duration
- Resource utilization (CPU, memory, disk)
- Errors + warning counts

**Data quality**
- Freshness (last update timestamp)
- Volume (row counts vs historical)
- Schema (any changes)
- Distribution (column stats vs baseline)
- Custom business rules (e.g., revenue > 0)

**Cost**
- Per-pipeline cost
- Per-table storage
- Query cost (BQ scanned bytes, Snowflake credits)

### Alerting design

- Alert on **symptoms**, not causes (latency, error rate)
- Different severity tiers, different routes
- Runbook link in every alert
- Alert frequency cap (avoid storm)
- Quiet hours for non-critical
- Periodic review: which alerts fire, get acted on, get ignored?

Alert fatigue = primary failure mode for ops teams.

### Runbook anatomy

For each alert / incident type:
1. Title + severity
2. Quick description
3. Likely causes
4. Diagnostic commands / queries
5. Mitigation steps (rollback, scale, redirect)
6. Resolution steps
7. Escalation path
8. Related links

Runbook quality directly correlates with MTTR.

### On-call rotation

- Compensate for off-hours
- Rotate fairly (weekly or biweekly)
- Primary + secondary
- Handoff procedure (shift report)
- Post-rotation retrospective

### Postmortem (blameless)

After every SEV1/SEV2:
- Timeline of events
- Impact (users, duration, dollars)
- Root cause (5 whys)
- Mitigation actions taken
- What worked well
- What didn't work
- Action items (owner + deadline)
- Lessons learned

**Blameless**: focus on systems, not individuals. People will hide info under blame.

### Backfill strategy

When historical data needs reprocessing:
- Idempotent pipelines (safe to re-run)
- Watermark or partition-based replay
- Throttle to not overwhelm downstream
- Monitor for cost spikes
- Validate output before declaring success

### Backfill idempotency + replay validation

The thin version above says "idempotent pipelines + validate output." In production the failure modes are subtle: a backfill that re-runs a window can **double-count** rows, race a live pipeline writing the same partition, or silently produce *fewer* rows than the original and nobody notices.

**Idempotent reprocessing — make re-runs a no-op, not an append**
- **Overwrite by partition** (delete-insert / `INSERT OVERWRITE` / dbt `insert_overwrite` incremental), never blind `INSERT`. Re-running the same window must converge to the same state.
- **MERGE on a natural/business key** when you can't drop a whole partition — dedupes on the key so replays don't duplicate.
- **Deterministic transforms** — no `current_timestamp()`, `rand()`, or non-deterministic UDFs in the write path, or the backfill won't match the original.

**Watermark / partition replay**
- Replay by explicit `[start, end)` partition bounds, not "everything since X." Bounded windows are restartable and auditable.
- Run **newest-first** for user-facing tables (restore freshness fast), **oldest-first** when downstream aggregates need ordered history.
- Quarantine the live writer for the window (pause schedule, or write to a staging partition and atomically swap) so backfill and incrementals don't fight over the same partition.

**Validation before declaring success — don't trust "job succeeded"**
- **Row-count reconciliation** vs source-of-truth or the pre-backfill snapshot (within a tolerance).
- **Data-diff** old vs new partition (DataFold data-diff, dbt-audit-helper) — catch silent value drift, not just counts.
- **Re-run DQ tests** (freshness/volume/distribution) on the backfilled window before unpausing downstream.
- **Idempotency proof**: run the backfill twice in staging — output must be byte-identical. If not, the pipeline isn't idempotent and prod will drift.

**Anti-patterns**: append-mode backfill (silent duplicates); "it ran green so it's done" with no reconciliation; backfilling while the live pipeline writes the same partition; non-deterministic transforms that make old vs new uncomparable.

Refs: [Lydtech — replay safety / idempotency](https://www.lydtechconsulting.com/blog/just-dead-letter-it), [DataFold data-diff](https://github.com/datafold/data-diff).

### DLQ (Dead Letter Queue) handling

For bad records in streaming:
- Route to DLQ topic / table
- Don't block pipeline on bad data
- Alert on DLQ rate exceeding threshold
- Periodic review + replay
- Document common DLQ causes

### DLQ replay decision logic

A DLQ is not an archive — it's a queue of decisions. The hard part isn't routing to the DLQ, it's **deciding what to do with what's in it**. Every DLQ message is one of: transient (retry), poison (never replays clean), or stale (correct to discard).

**Replay vs discard — decide per failure class, not per message**
- **Transient** (broker timeout, downstream 503, lock contention) → replay, ideally auto with bounded retry + backoff before it ever hits the DLQ.
- **Poison pill** (deser failure, schema mismatch, failed validation, NPE in consumer code) → replaying as-is just re-fails. Either fix the consumer/schema and *then* replay, or transform the payload, or discard.
- **Stale** — replaying is meaningless or harmful because the data moved on (a now-deleted user, a closed accounting period, an expired idempotency window). Discard and log; do **not** replay.

**Decision gates before any replay**
1. Is downstream **idempotent**? If not, replay can double-apply (double charge, double inventory move). No idempotency → no bulk replay.
2. Is the data **still valid**? Has the partition/period closed; has too much time elapsed?
3. Is the **root cause fixed**? Replaying into a still-broken consumer just refills the DLQ.

**Poison-pill handling**
- Detect non-transient errors as early as possible (deser/validation at the edge) and route straight to DLQ — don't let one bad message block a partition.
- Cap retries (e.g. 3) before dead-lettering; never infinite-retry a poison pill in place.
- Enrich each DLQ record: original topic/partition/offset, error class, stack, schema version, timestamp — replay is impossible without this metadata.

**Replay ordering + idempotency**
- Preserve original key → partition so per-key ordering survives replay; out-of-order replay can violate downstream invariants.
- Replay through a **rate-limited, filterable tool** with idempotency keys (replay by error class / time window, not "replay all").
- Replay into a *separate* attempt or shadow path when correctness is unproven, then reconcile.

**Thresholds**: alert on DLQ **inflow rate** and **backlog size/age**, not just absolute count — a sudden spike = systemic (bad deploy, schema change upstream); slow steady growth = a tail of genuinely bad data.

**Anti-patterns**: blind "replay everything"; replaying into non-idempotent consumers; infinite in-place retry of poison pills (partition stall); a DLQ no one ever drains (it becomes a data-loss black hole with no owner).

Refs: [Conduktor — dead-letter topics & poison pills](https://www.conduktor.io/blog/dead-letter-topics-handling-poison-pills), [Lydtech — "we'll just dead-letter it"](https://www.lydtechconsulting.com/blog/just-dead-letter-it).

### Hot-fix in production (without full redeploy)

When a pipeline is actively breaking (bad transform, wrong filter, broken UDF) and a full CI/CD redeploy is too slow, you need a controlled fast path — **not** a cowboy edit.

**Decision: hot-fix vs rollback vs pause**
- **Rollback first** if a known-good prior version exists — it's the lowest-risk action. Hot-fix only when rollback isn't possible (e.g. the bug is in already-landed data, or the prior version is also wrong).
- **Pause the pipeline** (stop the schedule / scale to 0 / disable the trigger) if data is being corrupted faster than you can fix — stop the bleeding before patching.

**Controlled hot-fix path (data pipelines)**
- **Config/param hot-fix** — many bugs live in config not code: a wrong date filter, threshold, or feature flag. Change the parameter (Airflow Variable, dbt var, env) — no code deploy. Fastest + most reversible.
- **Object-level redeploy** — re-deploy just the broken unit, not the whole project: a single `dbt run --select my_model+` (model + downstream), one Dataform tag, one Airflow DAG file, one Beam/Spark job — instead of the full pipeline.
- **Break-glass procedure** — emergency change with reduced approval but **full audit**: who, what, why, ticket number, time. Reduced gate ≠ no record. Two-person rule where possible (one applies, one watches).
- **Forward-fix bias** — prefer a new corrective change (roll forward) over editing running state, so the fix flows through the same lineage and is reproducible.

**After any hot-fix**
- Backfill / reprocess the window the bug touched (see Backfill strategy).
- Open a follow-up to land the same fix through normal CI/CD — a hot-fix that never gets "promoted" becomes config drift.
- Add a test that would have caught it. Every hot-fix is a missing test.

**Anti-patterns**: editing data directly in the warehouse with no record; SSHing into a worker to patch code in place; hot-fixing without pausing first so corruption keeps spreading; never backfilling the bad window.

### Capacity planning

- Trend: rows / day, GB / day, $ / day
- Project growth (linear extrapolation as baseline)
- Capacity headroom (target 50-70% utilization)
- Auto-scaling where possible
- Periodic review (quarterly)

### Cost monitoring

- Per-team / per-pipeline attribution (mandatory tagging)
- Daily reports
- Anomaly detection on cost
- Top 10 expensive queries / pipelines
- Optimization backlog

---

## 4. Tools Landscape (2026)

### Pipeline orchestration + monitoring
- **Airflow** — most common, mature
- **Dagster** — modern, asset-based
- **Prefect** — modern
- Operational monitoring built into orchestrator

### Data observability (commercial)
- **Monte Carlo** — pioneer + leader
- **Bigeye**
- **Anomalo**
- **Acceldata**
- **Datafold**

### Data quality (in-pipeline)
- **dbt tests** — minimum
- **Soda** — DQ-as-code
- **Great Expectations**
- **Elementary** — dbt-native

### Catalog + lineage
- **DataHub** — OSS standard
- **OpenMetadata** — alternative
- **Atlan** — commercial UX
- **Unity Catalog** / **Dataplex** / **Lake Formation** — cloud-native

### Logging + metrics + alerting
- **Datadog / New Relic** — APM, full-stack
- **Grafana stack** — OSS
- **Cloud-native** — CloudWatch, Cloud Logging, Azure Monitor
- **Sentry** — error tracking
- **PagerDuty / Opsgenie** — incident management

### Incident response
- **PagerDuty / Opsgenie / Splunk On-Call**
- **Statuspage / Atlassian Statuspage** — customer comms
- **Rootly / FireHydrant** — incident management workflow

### Cost
- **DataFold Data Diff** — pre-prod diff
- **Select.dev** — BQ cost optimization
- **Bluesky** — Snowflake cost optimization
- **Cloud-native cost tools**

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Only pipeline-level monitoring | Pipeline passes, data wrong | Data observability too |
| Alert on every job failure | Alert fatigue | Symptom-based + severity tiers |
| No runbooks | Slow MTTR | Runbook per alert |
| Blameful postmortems | Info hiding | Blameless culture |
| No SLAs | Don't know what good is | SLI/SLO + error budget |
| Ad-hoc backfills | Cost surprises, conflicts | Backfill framework |
| No DLQ | Bad records block pipeline | DLQ + monitoring |
| Manual cost reviews | Bills explode | Automated attribution + alerts |
| Single point of expertise | Bus factor | Documentation + cross-training |
| No capacity planning | Surprise outages | Trend + headroom |

---

## 6. Advanced / Expert Topics

### Data SLOs in practice

```
SLI: % of rows arriving within 1h of source timestamp
Target: 99% over 30 days
Budget: 1% = ~7.2h/month of "stale" data acceptable
```

Track per critical dataset. Burn rate alerts when budget consuming too fast.

### Anomaly detection for data observability

- Statistical (z-score, IQR)
- Time-series (Prophet, ARIMA forecasting + residual)
- ML-based (autoencoders, isolation forest)
- Commercial tools have these built in

### Lineage-aware impact analysis

When a source breaks, what downstream is affected?
- Lineage from OpenLineage events
- Visualize in DataHub / catalog
- Auto-notify owners of affected datasets

### Lineage-aware incident impact analysis (blast radius)

The thin version above says "see what's downstream." The operational discipline is using lineage to **compute blast radius in seconds, prioritize the fix by impact, and notify consumers before they notice** — turning lineage from a documentation artifact into an incident-response weapon.

**Compute blast radius**
- On a broken/corrupt table, traverse the lineage graph **downstream** to enumerate every dependent: dbt models, Spark/Flink jobs, dashboards, ML feature tables, reverse-ETL syncs, reports.
- Use a real lineage backend that ingests **OpenLineage** events (Marquez, DataHub, OpenMetadata, Atlan) — column-level lineage where available, so you can tell whether the broken *column* even feeds a given downstream, not just the table.
- Distinguish **direct** vs **transitive** impact and **dead ends** (downstream that exists but no one reads) — don't page owners of a dashboard nobody opens.

**Prioritize fixes by impact, not by graph distance**
- Rank affected assets by tier (Tier-1 customer-facing first), consumer count, and freshness SLA. A broken staging model that feeds the exec revenue dashboard outranks ten internal scratch tables.
- Fix the **highest-impact reachable node** first; sometimes patching a mid-graph model unblocks 80% of consumers faster than fixing the root.

**Downstream consumer notification**
- Auto-notify owners of affected datasets/dashboards (channel + ticket) with: what's wrong, which assets, expected fix ETA, and whether to stop using the data now.
- Mark affected assets **stale/quarantined** in the catalog so self-serve users see a banner instead of trusting bad numbers.
- Close the loop: notify again on resolution + after backfill validation passes.

**In production**: wire this into the incident workflow — alert fires → query lineage API for blast radius → auto-populate the incident channel with the impacted-asset list + owners. Decube, Monte Carlo, and DataHub ship versions of this; Marquez exposes it via the lineage API.

**Anti-patterns**: hand-maintained lineage diagrams (stale within a sprint); table-level-only lineage causing over-notification; computing blast radius manually mid-incident (too slow); notifying owners but never marking the data stale, so users keep consuming it.

Refs: [OpenLineage as the spine of observability](https://datalakehousehub.com/blog/2026-05-openlineage-observability/), [Atlan — data lineage & impact analysis (2026)](https://atlan.com/know/data-lineage-impact-analysis/).

### Cross-team incident coordination

For multi-team issues:
- Incident commander (single coordinator)
- Comms lead (status updates)
- Tech leads (each team)
- Document via shared doc / channel
- Status updates every 30-60 min

### Chaos engineering for data

Less common than software chaos but emerging:
- Inject schema breaks
- Simulate source outages
- Verify DLQ + replay work
- Test backfill procedures

### Chaos engineering for data systems (fault injection + game days)

Software chaos kills pods and blackholes networks. **Data chaos** injects *data-shaped* faults — late data, schema drift, poison messages, broker loss — and verifies the pipeline degrades gracefully instead of silently corrupting the warehouse. The point isn't to break things; it's to prove your DLQ, replay, alerts, and backfill actually work *before* a real incident relies on them.

**Data-specific faults to inject**
- **Late / out-of-order data** — push events past the watermark; does windowing drop them silently or route to a late-data side output? Do downstream aggregates self-correct?
- **Schema drift** — add/remove/rename a column, change a type, send a bad Avro/Protobuf version. Does the contract check / schema registry reject it, or does it poison the consumer?
- **Poison messages** — inject malformed/unparseable records; verify they hit the DLQ (not a partition stall) and that alerts fire.
- **Broker / source down** — kill a Kafka broker, throttle the source DB, blackhole the warehouse. Does the pipeline retry with backoff, buffer, or fall over? Does consumer-group rebalance behave?
- **Duplicate / replayed events** — re-send a window; confirm idempotency holds (no double-count).
- **Slow consumer / backpressure** — verify lag alerts fire and nothing OOMs.

**Game days**
- Organized, scheduled exercise: a hypothesis ("if the schema registry rejects a bad version, the consumer dead-letters and pages within 5 min"), a blast-radius-limited target (staging first), and a measured outcome.
- Game-day types: validate a past incident never recurs, tune observability (did we even detect it?), train on-call, exploratory.
- Always-on **continuous chaos** in CI/staging > occasional prod heroics; automate experiment + auto-rollback.

**What to actually measure**: was it detected (and how fast), did the right alert fire, did DLQ/replay/backfill work, what was the blast radius, MTTR. A "successful" experiment that surfaces zero gaps usually means the experiment was too timid.

**Tools (2025-2026)**: Gremlin (managed, game-day tooling), AWS FIS, Chaos Mesh / LitmusChaos (k8s, for Flink/Spark on k8s), Steadybit; plus pipeline-native injectors (bad records into a Kafka test topic, schema-registry fault stubs). Start in staging with a kill switch; only graduate to prod with tight blast-radius limits.

**Anti-patterns**: chaos in prod with no abort/rollback; injecting infra faults but never *data* faults (the failure mode unique to pipelines); a game day that produces no action items; running once and never again.

Refs: [Gremlin — fault injection game days](https://www.gremlin.com/docs/fault-injection-gamedays), [awesome-chaos-engineering](https://github.com/dastergon/awesome-chaos-engineering).

### Distributed tracing for data pipelines

Logs tell you a stage failed; tracing tells you *where in a multi-stage flow* a single record (or batch) spent its time and where it died. For pipelines spanning **Kafka → Flink/Spark → warehouse → reverse-ETL**, a trace stitches those hops into one timeline so you can answer "this row is 40 min late — which stage?" without grepping five services.

**Trace context propagation across stages**
- Propagate **W3C Trace Context** (`traceparent`) — or B3 — across boundaries. The hard part in data systems: context must ride **inside the message**, not just an HTTP header.
- **Kafka** — inject `traceparent` into message **headers** at produce; extract at consume. OpenTelemetry's Kafka instrumentation + Kafka Streams `producer-propagation.enabled` carry it through topologies.
- **Flink / Spark** — name the span service after the **job**, not the cluster; propagate context through operators. Batch stages often trace at **batch/partition granularity**, not per-row (per-row tracing on millions of records = unusable cost + cardinality).
- **Warehouse / dbt** — attach the trace/correlation ID as a query tag or run metadata so the load step joins the same trace.

**Span design**
- One span per logical stage (produce, consume, transform, load); parent-child across hops.
- Span attributes that matter in data: topic/partition/offset, batch size, row count, schema version, watermark/lag, dataset name.
- For fan-out (one batch → many records) use **span links** rather than forcing a single parent.

**Correlation IDs**
- When full tracing is too heavy, a propagated **correlation/batch ID** logged at every stage gives 80% of the value — join logs across services to follow one unit of work.

**Tools (2025-2026)**: **OpenTelemetry** is the standard (auto-instrumentation for Airflow, Spark, Flink, Kafka is maturing fast); backends Jaeger / Tempo / Datadog / Honeycomb; eBPF-based tracing emerging for lower-overhead capture. Sample aggressively (head/tail sampling) — tracing every record is neither affordable nor useful.

**Anti-patterns**: per-row spans (cardinality + cost blowup); dropping context at the Kafka boundary so the trace breaks mid-pipeline; tracing only services and never the data hops; no sampling.

Refs: [OpenTelemetry context propagation](https://opentelemetry.io/docs/concepts/context-propagation/), [Distributed observability for data pipelines with OpenTelemetry (2026 playbook)](https://bix-tech.com/distributed-observability-for-data-pipelines-with-opentelemetry-a-practical-endtoend-playbook-for-2026/).

### Continuous testing

- dbt tests run every pipeline
- Production data sampling for ML tests
- Schema drift detection in CI
- Performance regression detection

### Documentation as ops asset

- Architecture docs
- Runbook per alert
- Postmortem archive
- Catalog (data + assets)
- Glossary

Documentation debt = ops debt.

---

## 7. References

### Books
- **Site Reliability Engineering** — Beyer et al. (Google, free)
- **The Practice of Cloud System Administration** — Limoncelli
- **Data Pipelines Pocket Reference** — James Densmore
- **Fundamentals of Data Engineering** — Reis, Housley (has DataOps chapter)

### Frameworks
- **DataOps Manifesto** — dataopsmanifesto.org
- **Five Pillars of Data Observability** — Monte Carlo
- **DAMA DMBOK** — Data Management Body of Knowledge

### Communities
- **DataOps Community** (Slack)
- **DBT Slack** (#data-quality, #observability)
- **MLOps Community** (overlap)

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| Data Engineer | "Pipeline broke — debug + fix" |
| Data Architect | "Long-term reliability + capacity" |
| Platform Ops | "Shared infra cost + capacity" |
| Governance | "Audit trail + lineage gaps" |
| Domain Owner | "SLA + criticality of this dataset" |
| Engineering Leadership | "Reliability investments vs new work" |

---

*Data Ops makes pipelines boring (in the best way). Boring = reliable + predictable + cheap.*
