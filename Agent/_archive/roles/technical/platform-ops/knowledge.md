# Platform Ops — Comprehensive Knowledge

> Deep reference for the platform-ops subagent.
> Cross-pipeline / cross-system operations: cost, capacity, security ops, on-call structure.

---

## 1. Foundations

### What Platform Ops does

Keeps the **shared infrastructure** healthy + economical. Different from Data Ops (specific pipelines) and DevOps (CI/CD): Platform Ops worries about the whole platform's health, cost, capacity, security posture.

Often overlaps with: SRE, FinOps, SecOps.

### Scope

- Infrastructure capacity + health
- Cost attribution + optimization (FinOps)
- Security posture (SecOps)
- Identity + access management
- On-call rotation structure
- Runbook curation
- Incident command for cross-team issues
- Patching + lifecycle of shared services

---

## 2. Mental Models / Decision Frameworks

### Toil reduction (SRE)

Toil = manual, repetitive, automatable, no enduring value.
- Quantify toil per quarter (rough hours)
- Target: <50% of ops time on toil
- Automate the rest

If you're firefighting all the time, you're not improving. Carve out automation time.

### Error budget (SRE)

For shared platform services:
- SLI / SLO defined
- Error budget = 100% - SLO
- Spend on new launches OR reliability work
- Burn rate alerting (consuming budget too fast)

### FinOps maturity model

1. **Inform** — visibility into spend
2. **Optimize** — savings actions
3. **Operate** — continuous optimization

Most orgs stuck at level 1. Real value at level 2-3.

### Capacity planning horizons

- **Tactical** (weeks-months) — handle next month's projected load
- **Strategic** (6-12 months) — multi-quarter trends, commitments
- **Long-term** (1-3 years) — major architecture / vendor decisions

Each requires different data + decision framework.

### Incident scale + escalation

| Scale | Response |
|---|---|
| Single pipeline | Pipeline owner + Data Ops |
| Single service | Service owner + DevOps |
| Cross-team / cross-pipeline | Platform Ops incident commander |
| Region / multi-region | Cloud team + execs notified |

Platform Ops takes IC role on cross-team incidents.

---

## 3. Standard Practices

### Cost attribution (mandatory)

Every resource tagged with:
- `team` / `cost-center`
- `app` / `service`
- `environment` (dev/stg/prod)
- `purpose` (or `data-classification`)

Untagged resources are unmanaged. Periodic audit; auto-shutdown of untagged dev/sandbox.

### Cost dashboards

Weekly / monthly review:
- Total spend by team
- Top 10 expensive resources
- Anomalies (>30% week-over-week)
- Forecast vs actual
- Committed use coverage

### Optimization workflow

Quarterly:
- Identify top expensive resources
- Right-size review
- Committed use / reserved instance opportunities
- Storage tier optimization
- Unused / idle resource cleanup
- Spot/preemptible opportunities

### Capacity health

For each shared platform component:
- Current utilization vs limits
- Forecast against expected growth
- Headroom (target 50-70% utilization)
- Auto-scaling configured
- Alerts on saturation

### Security posture management

- CSPM (Cloud Security Posture Management) tooling
- Periodic IAM access reviews
- Vulnerability scanning + remediation tracking
- Secret rotation policy
- Patching cadence + tracking

### On-call structure

Multi-tier rotation:
- L1: triage + simple runbooks
- L2: specialists (Data, ML, Platform)
- L3: subject experts (called rarely)

Tools: PagerDuty / Opsgenie / Splunk On-Call. Define schedules + escalation policies clearly.

### Cross-team incident command

For SEV1/SEV2 spanning teams:
- Incident Commander (decides + coordinates)
- Comms Lead (status updates internal + external)
- Tech Leads from each affected team
- Scribe (timeline + decisions)
- Status channel + bridge

Train people in IC role before they need it.

### Runbook governance

- Runbook per alert / incident type
- Quarterly review (still relevant? still works?)
- Updated after every postmortem
- Searchable repository
- Linked from alerts

### Postmortem culture

After every SEV1/SEV2:
- Blameless
- Timeline + impact
- Root cause analysis (5 whys, fishbone)
- Action items with owners + due dates
- Track action items to completion

A postmortem without action items completed is worthless.

### Disaster Recovery + Business Continuity

- RTO / RPO defined per service
- DR procedures documented + tested
- Annual DR drills
- Backup retention + validation
- Failover automation where feasible

---

## 4. Tools Landscape (2026)

### FinOps
- **CloudHealth (VMware)** — enterprise
- **Cloudability (Apptio)** — enterprise
- **Vantage** — modern
- **Finout** — multi-cloud
- **OpenCost / KubeCost** — K8s cost
- **Cloud-native** — AWS Cost Explorer, GCP Billing, Azure Cost Management

### Observability (platform-wide)
- **Datadog / New Relic / Dynatrace** — APM
- **Grafana Cloud** — OSS stack managed
- **Honeycomb** — observability-driven
- **Splunk** — logs + SIEM

### Incident management
- **PagerDuty / Opsgenie / Splunk On-Call** — paging
- **Statuspage / Atlassian Statuspage** — customer comms
- **Rootly / FireHydrant / Incident.io** — incident workflow

### Security ops
- **Cloud-native**: GCP Security Command Center, AWS Security Hub, Azure Defender for Cloud
- **CSPM**: Wiz, Lacework, Prisma Cloud
- **SIEM**: Splunk, Sentinel, Chronicle
- **SOAR**: Cortex XSOAR, Splunk SOAR

### Identity
- **Okta / Entra ID / Google Workspace** — IdP
- **Vault / Cyberark** — privileged access
- **AWS Identity Center / GCP IAM / Entra ID** — cloud-native

### Capacity / Performance
- **APM tools** for service-level
- **Cloud-native dashboards** for cloud capacity
- **Capacity planning spreadsheets** (often sufficient)

### Sustainability / Carbon
- **AWS Customer Carbon Footprint Tool**
- **GCP Cloud Sustainability**
- **Azure Emissions Impact Dashboard**
- **Cloud Carbon Footprint** (OSS)

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| No tagging | No cost attribution | Mandatory tagging policy + enforcement |
| Monthly bill review | Surprises | Daily anomaly alerts |
| Manual scaling | Outages or waste | Auto-scaling |
| Untested DR | Untested = doesn't work | Annual drills minimum |
| No on-call coverage off-hours | Slow MTTR | Follow-the-sun or rotation |
| Patching when convenient | Vuln window | Defined cadence + tracking |
| Shared credentials | Audit failure | Identity per person + service |
| Manual access requests | Slow + error-prone | IAM + access workflows |
| No SLO | Don't know what good is | SLI/SLO + error budget |
| Hero culture | Burnout | Toil reduction, automation |
| Runbook in someone's head | Bus factor | Documented, in repo |
| Incident → no postmortem | Repeat | Mandatory postmortem |

---

## 6. Advanced / Expert Topics

### Cost optimization at scale

- **Savings Plans / Committed Use Discounts** for stable base load
- **Spot / Preemptible** for retryable workloads (60-90% savings)
- **Auto-scaling** to match demand
- **Right-sizing automation**
- **Storage lifecycle policies**
- **Idle resource cleanup automation**
- **Reserved capacity pooling** across teams

### Chargeback vs showback

- **Showback** — visibility only (teams see their costs)
- **Chargeback** — actual billing to teams (real $$ flow)

Showback first; chargeback after teams understand their costs.

### Multi-cloud cost management

If genuinely multi-cloud:
- Normalize cost across providers
- Avoid cross-cloud egress
- Centralized FinOps team
- Tools: Finout, Vantage, Cloudability

Most orgs shouldn't be multi-cloud for same workload.

### Carbon accounting + GreenOps

Emerging requirement:
- Track CO2 per service
- Region selection considering carbon
- Workload scheduling for clean energy availability
- Reporting (will become mandatory in some jurisdictions)

### Identity Lifecycle Management

- Joiner / mover / leaver (JML) automation
- Periodic access reviews
- Privileged access (just-in-time)
- Service account hygiene
- Audit trail of access changes

### Vulnerability management

- Automated scanning (CI + runtime)
- SLA per severity (e.g., critical patched in 7 days)
- Exception process for non-fixable
- Compensating controls when patching delayed
- Tracking dashboard

### Cloud reservation strategy

Mix of:
- **On-demand** (~30%) for variability
- **Reserved / Committed** (~50%) for stable base
- **Spot / Preemptible** (~20%) for retryable

Adjust per workload pattern.

### Internal customer support

Platform Ops is a service team:
- Service catalog
- Ticket workflow
- SLA on requests (e.g., new project provisioning in 1 day)
- Office hours / Slack support
- NPS / satisfaction surveys

### Snowflake cost optimization

**What/why.** Snowflake bills credits per warehouse-second of compute plus separate storage and cloud-services lines. Compute dominates the bill, so the levers are about not paying for idle or oversized warehouses while still meeting query SLAs.

**Specific levers.**
- **Warehouse sizing + auto-suspend.** Right-size to the *smallest* warehouse that meets latency; doubling size doubles credits/hour, so only scale up if runtime halves. Set `AUTO_SUSPEND` aggressively (30-60s for interactive, 60-300s for batch); idle warehouses still burn credits. `AUTO_RESUME=TRUE` so suspended warehouses don't block users.
- **Multi-cluster scaling policy.** For concurrency (not bigger queries), use multi-cluster warehouses with `SCALING_POLICY = STANDARD` (spins clusters fast, avoids queueing) vs `ECONOMY` (packs queries, fewer clusters, cheaper but queues). Set `MIN_CLUSTERS=1` to avoid always-on cost.
- **Query Acceleration Service (QAS).** Enterprise+ feature: offloads large-scan/selective-filter portions to shared compute, billed by the second separately. Cap blast radius with `QUERY_ACCELERATION_MAX_SCALE_FACTOR` (e.g., 3) so a Small warehouse bursts only when it pays off.
- **Result + metadata caching.** 24h result cache returns identical queries for free (no compute). Metadata-only queries (`COUNT`, `MIN/MAX`) hit the cloud-services layer, often free.
- **Storage.** Tune `DATA_RETENTION_TIME_IN_DAYS` (Time Travel) down for high-churn tables; Fail-safe adds a non-configurable 7 days for permanent tables. Use **transient/temporary tables** for staging/ETL to skip Fail-safe and reduce retention cost.
- **Micro-partition pruning.** Cluster on high-cardinality filter columns; well-pruned scans read fewer partitions = fewer credits. Check `partitions_scanned / partitions_total`.
- **Resource monitors + budgets.** Circuit breakers on credit quotas — notify at 75%, suspend at 90-100%. Use Snowsight's Cost Management / Account cost views (and `SNOWFLAKE.ACCOUNT_USAGE`) for attribution.

**Anti-patterns.** One giant always-on XL warehouse for everything; `AUTO_SUSPEND` set to hours; no resource monitor (a runaway script can burn thousands overnight); clustering on low-cardinality keys.

**Tools (2025-2026).** Snowsight cost views, `ACCOUNT_USAGE` views, Adaptive Warehouses (auto-sizing, newer), third-party (Capital One Slingshot, Keebo, Select).

Refs: [Query Acceleration Service](https://docs.snowflake.com/en/user-guide/query-acceleration-service) · [Cost & performance optimization guide](https://www.snowflake.com/en/developers/guides/getting-started-cost-performance-optimization/)

### Databricks cost optimization

**What/why.** Databricks bills **DBUs** (a compute-time unit, rate varies by SKU) *plus* the underlying cloud VM cost on classic compute. The bill = DBU rate × DBUs + infra. Optimization targets both the DBU multiplier (engine, SKU) and the infra (instance type, spot, idle).

**Specific levers.**
- **Photon.** Vectorized C++ engine; higher DBU/hour multiplier but often lower *total* cost because jobs finish much faster. Win for SQL/Delta-heavy ETL; verify per-workload — CPU-light/UDF-heavy jobs may not benefit.
- **Serverless vs classic.** Serverless bundles infra into the DBU rate (no VM management, fast startup, no idle-cluster waste) — cheaper for spiky/intermittent and short jobs. Classic (instance pools/fleets) wins for large sustained workloads where you control spot + reserved VMs. Serverless cost is visible in `system.billing.usage` via `billing_origin_product`.
- **Instance fleets + spot.** On classic, use fleets to pull from multiple instance types/AZs; run **spot for workers, on-demand for the driver** (retryable workloads, 60-90% savings). Use **instance pools** to cut cluster startup time.
- **Autoscaling.** Enable min/max workers; prefer **enhanced autoscaling** for jobs. Set short auto-termination on all-purpose clusters.
- **Job vs all-purpose clusters.** Job clusters (ephemeral, lower DBU rate) for scheduled pipelines; all-purpose (higher rate, shared) only for interactive dev. Running production jobs on all-purpose clusters is a classic overspend.
- **Delta layout — OPTIMIZE / Z-order / liquid clustering.** Compaction + data skipping reduce bytes scanned. **Liquid clustering (GA, DBR 15.2+)** replaces both partitioning and Z-ORDER for new tables — incremental, ~7x faster writes than partition+ZORDER, and they can't be combined. Use `CLUSTER BY` (or `CLUSTER BY AUTO`); `OPTIMIZE FULL` forces reclustering.

**Anti-patterns.** Prod jobs on all-purpose clusters; no auto-termination; over-partitioning small tables; spot on the driver; Photon enabled blindly on UDF-heavy jobs.

**Tools (2025-2026).** **Unity Catalog system tables** (`system.billing.usage`, `system.billing.list_prices`) for cost attribution by job/notebook/tag; Predictive Optimization (auto OPTIMIZE/VACUUM); third-party (CloudZero, Flexera, Cloudchipr).

Refs: [Liquid clustering GA](https://www.databricks.com/blog/announcing-general-availability-liquid-clustering) · [Monitor serverless cost (system tables)](https://docs.databricks.com/aws/en/admin/system-tables/serverless-billing)

### Carbon accounting / GreenOps

**What/why.** Sustainability reporting is shifting from voluntary to mandated (EU CSRD, etc.), and cloud carbon is increasingly a board-level metric. GreenOps = FinOps discipline applied to emissions: measure, attribute, reduce. Crucially, **lower cost and lower carbon usually correlate** (less idle compute, fewer bytes scanned, efficient regions), so it piggybacks on existing FinOps work.

**Measuring cloud carbon.**
- **Provider dashboards** — AWS Customer Carbon Footprint Tool, GCP Carbon Footprint, Azure Emissions Impact Dashboard. Easy but coarse, lagging, and methodology differs per vendor (market- vs location-based).
- **Cloud Carbon Footprint (OSS)** — converts billing/usage → energy (PUE-adjusted) → emissions using regional grid carbon intensity; multi-cloud (AWS/Azure/GCP), gives service-level granularity providers don't.

**Patterns / levers.**
- **Region selection by grid intensity.** Same workload in a low-carbon-grid region (e.g., hydro/nuclear-heavy) can be a fraction of the emissions of a coal-heavy region — often a one-line change. Balance against latency/data-residency/egress.
- **Carbon-aware scheduling.** Shift deferrable batch (training, reports, backfills) to times/regions when the grid is cleaner, using live signals from ElectricityMaps / WattTime / Cloud Carbon Footprint. Schedulers (Nomad carbon branch, K8s carbon-aware) score nodes by carbon and steer work.
- **SCI metric.** **Software Carbon Intensity** = `((E × I) + M) / R` — energy × grid intensity, plus embodied hardware emissions, *per functional unit* (user/transaction/API call). It's a **rate, not a total**, so it can't be gamed by scaling down; now **ISO/IEC 21031:2024**. Use it to track efficiency over time and compare designs.

**Anti-patterns.** Treating provider totals as precise; offsets instead of actual reduction; ignoring embodied (M) emissions; chasing carbon while breaking latency SLAs.

**Tools (2025-2026).** Cloud Carbon Footprint (OSS), provider dashboards, ElectricityMaps/WattTime APIs, Green Software Foundation SCI spec + Impact Framework.

Refs: [SCI specification (GSF)](https://sci.greensoftware.foundation/) · [cloudcarbonfootprint.org](https://www.cloudcarbonfootprint.org/)

### SLO burn-rate alerting mechanics

**What/why.** Alerting on raw error rate is noisy (pages on tiny blips) or laggy (misses slow leaks). **Burn rate** = how fast you're consuming the error budget relative to "even" spend over the SLO window. Burn rate **1 = exactly on budget** (exhausts at end of window); **burn rate N = exhausts in window/N**. Page on *budget consumption*, not instantaneous errors.

**Error budget math.** For a 30-day window at 99.9% SLO, budget = 0.1% of requests. Consuming X% of the *total* budget in time T implies burn rate = `X% × window / T`. Examples (Google SRE workbook):
- 2% of budget in 1h → burn rate ≈ `0.02 × 720h / 1h` ≈ **14.4**
- 5% of budget in 6h → burn rate ≈ `0.05 × 720h / 6h` ≈ **6**
- 10% of budget in 3 days → burn rate ≈ **1**

**Multi-window, multi-burn-rate (the recommended pattern).** Combine a **long window** (measures sustained burn) with a **short window** (~1/12 of the long one) that must *also* be burning — the short window stops you paging on an incident that already recovered, and clears the alert fast. Run several tiers:

| Severity | Burn rate | Long window | Short window | Meaning |
|---|---|---|---|---|
| Page (fast) | 14.4 | 1h | 5m | 2% budget in 1h |
| Page (slow) | 6 | 6h | 30m | 5% budget in 6h |
| Ticket | 3 | 24h | 2h | 10% budget in 24h |
| Ticket | 1 | 72h | 6h | slow leak |

Fast burn = page now (a real outage); slow burn = ticket (chronic degradation eroding budget). An alert fires only when **both** windows exceed the threshold.

**Applied to data/platform SLOs.** Same mechanics on data freshness/completeness (e.g., "99% of partitions land < 2h"), pipeline success rate, or API availability of shared platform services. Tie the budget to the on-call policy: fast burn → page, slow burn → backlog.

**Anti-patterns.** Single-window threshold alerts (noisy/laggy); paging on every slow-burn tier (alert fatigue); SLO window mismatched to the budget math; no short-window guard (alerts that never clear).

**Tools (2025-2026).** Sloth / OpenSLO + Prometheus recording rules, Google Cloud SLO monitoring, Datadog/Grafana SLO burn-rate alerts, Nobl9.

Refs: [Google SRE Workbook — Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)

---

## 7. References

### Books
- **Site Reliability Engineering** — Google (free)
- **The Site Reliability Workbook** — Google (free)
- **Cloud FinOps** — O'Reilly
- **Cloud Native Patterns** — Cornelia Davis

### Frameworks
- **FinOps Foundation** — finops.org
- **CIS Benchmarks** — security baselines
- **NIST Cybersecurity Framework**
- **Cloud Security Alliance (CSA) Cloud Controls Matrix**

### Communities
- **FinOps Foundation**
- **CNCF SRE Working Group**
- **DevOps Subreddit / Slack communities**

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| Platform Architect | Capabilities + cost model |
| Solution Architect | Resource planning for new systems |
| DevOps | CI/CD + IaC for platform |
| Data Ops | Pipeline cost + capacity |
| ML Ops | Model serving infra |
| Security | Posture + incident response |
| Finance | Cost reporting, RI strategy |
| Leadership | Reliability vs new work trade-offs |

---

*Platform Ops = SRE applied to the whole platform. Toil reduction is the meta-goal.*
