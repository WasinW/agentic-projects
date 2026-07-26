# AIA Observability & Monitoring — Deep Synthesis (big picture + confusion map + target architecture)

> Synthesized by Claude from a 6-agent workflow (4 domain readers → obs-architect → completeness-critic)
> over the full AIA KB. **Working synthesis** — contains unverified items + open questions; promote to
> knowledge/ after the gates resolve. 🔒 private KB. Companion diagram: `aia-observability.drawio`.
> Date: 2026-07-25. Confidence: medium (two deployed-vs-KB contradictions + several make-or-break gates unverified).

---

## 0. THE BIG PICTURE — one platform, TWO panes, ONE spine, ONE seam

Your observability work is **two panes that must stay separate but share one spine and meet at one seam**:
- **Pane 1 — Kafka/AKS producer side** (Strimzi on AKS, Debezium CDC) → instrumented by **Prometheus + Grafana**.
- **Pane 2 — Azure Databricks side** (cost pipeline + Genie/DBU cost + operational health) → instrumented by
  **UC system tables + Lakehouse/Data-Quality Monitoring**.
- **Do NOT merge them into one tool** — different metric stores, latencies, owners.

Unify with **3 things (the spine)** + meet at **1 seam**:
1. **The per-team tag** (`MAP<STRING,STRING>` → projected to a top-level column) = simultaneously the **RLS key +
   chargeback key + budget key + job-pipeline tag**. One key, four jobs. Keeping it (vs บูม who drops it) is what
   makes per-team slicing possible at all.
2. **A central run-metadata/monitoring table** — the framework's `update_workflow_info` → `job_id` = the deploy→run
   join key (extend it, or a Delta twin, to also carry the realtime `mdle_monitor` sink).
3. **One notification fan-out** — Grafana alerts (Kafka) + SQL Alerts/job notifications (ADB) → the **same Teams/webhook**
   → Azure Monitor for paging. **TWO dashboards, ONE alert destination.**
- **The seam** = **bronze-table freshness** ("did the CDC land in bronze?") — the single most valuable end-to-end
  metric, where **Kafka consumer-lag meets Databricks `max(load_ts)` age**.

**Sequencing principle:** build the **already-wired, zero-image-rebuild** signals first; gate the expensive layers on
**ONE unverified question** (is Prometheus scrape config baked into a custom image = rebuild = paused, OR
PodMonitor/ServiceMonitor = light GitOps edit). **That answer, not effort, decides what is actually blocked.**

### ⚠️ There are THREE deploy pipelines — do NOT conflate (this corrupts ownership + obs hooks)
1. **Kafka platform** — 3 repos (build_ci→cluster→connector), Jenkins→ACR→AKS, **MFEC-built, INHERITED**.
2. **Databricks framework `dtp_framework_aiath`** — Jenkins, notebook-deploy THEN workflow-deploy, **INHERITED**.
3. **Your OWN governance/cost/obs delivery** — Terraform L1-L4 + DAB + reconcile jobs (`deploy/`).
→ The obs hooks (`update_workflow_info` job_id, `mdle_monitor`) live in **pipeline 2**, but you build in **pipeline 3**.
You **consume** hooks from #2; MFEC owns #1. **Reconcile your `rls_reconcile` desired-state with #2's
`api_assign_permission`/`wf_policy_config` or two reconcilers fight over the same grants.**

---

## 1. CONFUSION MAP — your tangled points, resolved

| # | The tangle | Why confusing | Resolution |
|---|---|---|---|
| 1 | **TWO "cost gold" tables** — which does the dashboard serve? | Requirement says "share Azure-infra cost via Cost Mgmt Export → cost_wide" (= actual $), but the **deployed `cost_views.sql` builds `v_billing_priced` FROM `system.billing.usage`** = DBU-only, excludes 40-60% classic-VM cost. Artifact ≠ requirement. | Name them distinctly: Dashboard A today = **DBU-list SHOWBACK** (`v_billing_priced_rls`). For "all-service actual" it must **join the Export VM meter** on top of `cost_wide`. Ask Sarunya: do teams need actual-$ or is DBU-attribution OK for showback? |
| 2 | **Genie GROSS vs NET** — subtract the 150 free-tier or not? | Curated master doc says **NET** ("อย่าลบ 150"); synthesis + `dashboard_b_genie.sql` say **GROSS** (AIA data falsified net); deployed view does **no** free-tier math. **3 sources, 3 behaviours.** | **Settle by data before Dashboard B ships:** if users with <150 pooled monthly Genie DBU **have rows → GROSS** → apply `GREATEST(0, dbu-150)` per identified user (SPs excluded). Run that check in-tenant. |
| 3 | **"PROD" is ambiguous** (3 workspaces) | coredata DEV (provider, yours) · coredata PROD (unused, forbidden) · departmental PROD (consumer, client's). "PROD compute → DEV ADLS" = **departmental PROD**. | Always qualify: cost pipeline runs in **coredata DEV** (no network gate); GATE C = **departmental-PROD compute → coredata-DEV ADLS**; entitlement migration is on **departmental PROD (you don't own it)**. |
| 4 | **A UC GRANT = consumer can read** (GATE C) | GRANT is control-plane; bytes flow data-plane — consumer compute reads ADLS **directly**. Closed firewall/PE = **403 despite perfect grant**. | Treat governance (GATE A/B) and network (GATE C) as **independent**. Triage with `dbutils.fs.ls` on the raw abfss path. GATE C = make-or-break of D+. |
| 5 | **The image-rebuild wall blocks ALL long-term Kafka metrics** | kube-state-metrics IS blocked (needs rebuild). But **JMX + Kafka-Exporter are LIGHT CR edits** (JMX agent already in image) — UNLESS Prometheus scrape config is baked into a custom image. | **Packaging, not effort, is the blocker** → resolve ONE question: PodMonitor/ServiceMonitor vs baked scrape config. Kafka-Exporter (lag) is higher-value than KSM and may be **unblocked**. Don't lump them. |
| 6 | **What's in the Monitoring Pool + is Alertmanager deployed?** | Sep-2024 diagram says "Grafana" only; repo-analysis says full **Prometheus+Grafana+Alertmanager**; but the interim builds a Grafana-managed alert with **no** Alertmanager. | Confirm the live stack (repo view is more current). Interim (Grafana-managed → Mail/Teams, **no** Alertmanager) is right regardless — just land rules in the right system. |
| 7 | **The reconcile alert is a "monitor"** | It's **effect-level** (fires on any reconcile break, blind to kube/node) and can **MISS** events (counter reset on operator restart; retention erased the window; series absent until first failure). `sum_over_time[30d]≈1449` = scrape count, not failures. | Keep as a **tripwire** + pair with an **operator-absence/liveness companion** (`absent(strimzi_reconciliations_periodical_total{...})`). Label = `namespace` NOT `kubernetes_namespace`. A real monitor needs Layers 1-2 (JMX + Kafka-Exporter). |
| 8 | **There's one deploy pipeline** | There are **THREE** (§0). Conflating corrupts ownership + obs hooks. | Keep 3 separate in every diagram/RACI. You own #3, consume #2's hooks, MFEC owns #1. |
| 9 | **Silent-RLS-failure cluster** ("everyone sees empty / everyone sees all") | 4 independent slips, all silent: `is_member()` (FALSE for account users), missing `GRANT EXECUTE` on filter fn, `embed_credentials:true` (UI default → leaks), filter checks wrong group. | Ship the 4 fixes as **one unit**: `is_account_group_member()` + all 4 grants (USE CAT/USE SCHEMA/SELECT/EXECUTE) + `embed_credentials:false` (DAB) + verify group names. Test with a **real non-bypass consumer** (admin test = false positive). |

---

## 2. OBSERVABILITY TARGET ARCHITECTURE

### 2A. Kafka pane — from ONE tripwire to a real monitoring set (4 layers)
| Layer | Signal | Status | Source |
|---|---|---|---|
| **L3 operator/reconcile** | `strimzi_reconciliations_failed_total / _duration / _periodical` | ✅ **WIRED** (interim alert) | Strimzi operator, no JMX needed |
| **L2 consumer lag** ⭐ | `kafka_consumergroup_lag` | ❓ likely NOT deployed | **Kafka Exporter** (`spec.kafkaExporter` on Kafka CR) — separate pod, NOT JMX |
| **L1 broker/Connect/Debezium** | offline/under-replicated partitions, ISR, task RUNNING/FAILED, **Debezium `MilliSecondsBehindSource`**, DLQ rate | ❌ not yet | **JMX** `metricsConfig` on Kafka + KafkaConnect CRs (agent already in image) |
| **L4 pod/restart/readiness + node/CoreDNS** | `kube_pod_status_ready`, restarts, node pressure | ❌ **BLOCKED** (no KSM) | kube-state-metrics (needs image rebuild = paused) |

- **Interim (ship now):** Grafana-managed alert `sum(increase(strimzi_reconciliations_failed_total{kind="KafkaConnect",namespace="nsp-th-p-kafka"}[5m]))>0` → Mail+Teams, **no Alertmanager**, + `absent(...)` companion. PROD-only. Add to `strimzi-operators.json`.
- **Long-term (2 independent upgrades):** (A) **Kafka Exporter (lag) + JMX** = the real monitoring set — *light CR edits IF PodMonitor* (resolve packaging first!); (B) kube-state-metrics for root-cause pod layer (paused, needs rebuild).
- **Real per-incident fixes ≠ alerting:** UAT slow-boot = **bake Connect plugins into the image** (`dtp_kafka_build_ci`) + raise the 600000ms pod-ready timeout + right-size; PROD = **CoreDNS resilience** (file with infra — biggest latent risk, no one's ticket).

### 2B. ADB pane — cost pipeline + dashboards + observability core
- **Cost pipeline:** Azure Cost Mgmt **Export → ADLS → 5-layer ETL** (bronze→persist **KEEP custom_tags MAP**→prep→summary→**GOLD `cost_wide`** with team tag projected to top-level `tag_team`; **UC ROW FILTER binds on that column**, never a MAP element). Runs entirely in **coredata DEV** (no network gate). **TWO money sources distinct:** Export = **actual-$** (has classic VM, discount/FX/tax, the ONLY source with VM cost); `system.billing × list_prices` = **DBU-list, GROSS, DBU-only**. **Reconcile DBU-meter↔DBU-meter, actual↔actual — never DBU↔Portal total;** join by the team tag.
- **Dashboards:** A = departmental all-service (7 visuals, DBU-list **showback**, add Export VM for actual-$); B = Genie gross-vs-billed (5 visuals, per-user floor); **C = Observability (Topic 3, deferred — this is its scope).**
- **Observability CORE (3 tracks, UC system tables, no real-time SLA → trend/audit/daily):**
  - **Track 1 INFRA-TAG:** `system.billing.usage.custom_tags` per-team/job/surface.
  - **Track 2 JOB-PIPELINE-TAG:** `system.lakeflow.job_run_timeline` (+ `job_task_run_timeline` — a green job can hide a flaky retried task); **CRITICAL: detect MISSING runs** (last_run older than cadence — "didn't run" is silent); `$` per slow job via `system.billing` + `usage_metadata.job_id`; + `system.compute.*` + `system.query.history`.
  - **Track 3 DATA-QUALITY (2026 naming):** **Anomaly detection** (freshness+completeness → `system.data_quality_monitoring.table_results`) + **Data profiling** (drift, = former Lakehouse Monitoring) + write-time EXPECT rules + **tag-coverage% ≥ 95** (custom metric = chargeback-credibility guard). `system.access.audit` = the RLS-proof/compliance layer.
  - Alerting: SQL Alerts/job notifications → Teams → Azure Monitor. Snapshot to Delta for retention.

### 2C. Access-management on the dashboards (4 layers)
- **L1 Identity** = account users + **ACCOUNT groups** via SCIM/Entra (never TF/UI membership; workspace-local groups don't resolve cross-workspace).
- **L2 Entitlement** = Consumer-access lockdown (`workspace_consume` **SOLE**) via PR-gated Terraform. **Additive trap** + needs the **users-group migration** (⏰ auto-enable **2026-07-27**, enforced **2026-09-14**).
- **L3 Object ACL** = warehouse CAN_USE / dashboard CAN_READ via DAB+TF.
- **L4 Data grant + RLS** = HIGH churn → **control-table reconcile JOB** (`rls_reconcile.py`, dry-run default + max-revoke breaker + audit), NEVER CI. **RLS = secure-view predicate** (`is_account_group_member()` + `team_access_map`), **NOT** `is_member()`, **NOT** `ALTER SET ROW FILTER` on system.billing. Ship the **4 grants together incl. `GRANT EXECUTE`**; `embed_credentials:false` load-bearing. Onboard a team = INSERT one row.
- **GATE C** (network) + **who-pays** (published dashboard runs on publisher's warehouse = showback; real chargeback = also GRANT SELECT so teams query from own warehouse).

---

## 3. PHASED PLAN (build order)

- **Phase 0 — ship what's already wired (this week, zero rebuild):** KAFKA Grafana-managed reconcile alert + `absent()` companion → Mail/Teams. ADB RLS-correct Dashboards A+B (the 4-fix unit). **Run the GATE C network PoC** at coredata UAT. *(Cheapest, highest-trust; de-risks the 2 visible workstreams + validates the make-or-break gate.)*
- **Phase 1 — resolve the blockers that decide everything** (see §6 questions): Prometheus packaging · system tables enabled + `spec.kafkaExporter` deployed? · `update_workflow_info` schema + `mdle_monitor` sink · Prometheus retention · same-metastore. *(Effort isn't the blocker — packaging is.)*
- **Phase 2 — Kafka: tripwire → real monitoring set:** enable Kafka Exporter (lag = the seam) + JMX (broker/Connect/Debezium). *(Highest value per effort once packaging is settled.)*
- **Phase 3 — ADB Observability CORE (Dashboard C, 3 tracks):** gold_ops views on serverless auto-stop warehouse; fold in the cost pipeline's own health. *(Unblocked once Phase 1 confirms system tables + the metadata join key.)*
- **Phase 4 — stitch the seam + root-cause:** bronze-freshness metric (Kafka lag ↔ Databricks `max(load_ts)`); install kube-state-metrics + CoreDNS resilience (carry rebuild/infra cost → last); unify the two access-as-code reconcilers.

---

## 4. Diagram — 9 lanes (see `aia-observability.drawio`)
A Sources&CDC · B Kafka/AKS pane (4 metric layers) · C Kafka obs stack (Prom→Grafana→alert) · **D THE SEAM (bronze
freshness)** · E ADB compute + cost pipeline · F ADB obs plane (system tables + DQ) · G Serving & access (RLS
dashboards, GATE C) · **H Shared spine (tag · metadata table · Teams fan-out)** · I Consumers/alert sinks.

---

## 5. ⏰ TIME-CRITICAL + deployed-vs-KB contradictions (ACT)
1. **⏰ Entitlement migration auto-enables 2026-07-27** (≈2 days), enforced 2026-09-14. Until departmental PROD is
   migrated, **Consumer-access lockdown LEAKS** (users inherit Workspace+SQL authoring) and RLS-for-viewer may misbehave.
   It's on **departmental PROD (you don't own it)** → **coordinate with that workspace's admin NOW**; post-migration
   audit the `users-clone-<TS>` group so `biz-consumers-*` is NOT a member.
2. **Deployed `cost_views.sql` vs reviewed KB disagree on 2 live items → Dashboard B produces a wrong number either way
   until settled:** (a) **Genie GROSS vs NET** (§1 #2); (b) **`usage_unit='DBU'` filter** — deployed SQL still filters it,
   reviewed doc removed it (TOKEN/ANSWER are values of a *different* column `usage_type`; filtering the wrong column risks
   dropping a legitimate Genie meter → understatement). **Decide + re-deploy before shipping B.**

---

## 6. OPEN QUESTIONS — answer before building (grouped; you go find these in-tenant)

**A. Kafka observability (Phase 1 blockers)**
1. **Prometheus packaging** (highest-leverage): PodMonitor/ServiceMonitor **or** static baked scrape config? → decides if Kafka-Exporter/JMX are cheap or blocked.
2. Any **Azure Monitor managed Prometheus / Container Insights** on the AKS cluster already? (Would ship KSM → unblock L4.)
3. Is **`spec.kafkaExporter` deployed** today? (If not, consumer-lag = absent.)
4. Exact **Prometheus retention** window?

**B. ADB cost + access**
5. **Cost target table + exact team tag key?** (`cost_views.sql` leaves `${team_tag_key}`, `${catalog}.${gold_schema}` unset — can't bind RLS without real values.)
6. **Which account groups exist + exact names** — FinOps bypass (`${platform_group}`) + each `consumer-<team>`? Can you mint account groups or is it an Entra/IdP request?
7. **Cost Mgmt Export cadence + owner** (daily drop? month-close? บูม's pipeline or yours)?
8. **Entitlement migration done on departmental PROD?** Path to coordinate before 2026-07-27?
9. **GATE C open?** departmental-PROD compute → coredata-DEV ADLS (firewall/PE)? Same UC metastore?
10. **UC system tables enabled** by account admin + SELECT granted to your warehouse?
11. **Genie GROSS-vs-NET** — do <150-DBU users have rows? (Settle before Dashboard B.)

**C. The shared spine / seam**
12. **`update_workflow_info` central-table schema** (job_id + what else) + **where `mdle_monitor` emits** (Delta/log/Prometheus/Azure Monitor)? = Dashboard C's join key + sink.
13. **Connect gen01/02/03 → source-domain, and topic → bronze-table mapping?** (Required to wire the bronze-freshness seam.)
14. **Teams/webhook destination** exists (admin-created) both panes can fan out to? Azure Monitor for paging?

---

## 7. COVERAGE GAPS (the plan does NOT yet cover — decide scope)
- **Qlik Replicate CDC** = completely uncovered — CDC is DUAL-tool; the Kafka pane only sees the Debezium half. A Qlik-landed source has **no lag/health signal anywhere**.
- **ADF + Integration Runtime health** = blind spot — `system.lakeflow` only sees the Databricks Jobs ADF triggers, not ADF-level failures (IR down, Link Service auth). ADF has native Azure Monitor integration — incorporate it.
- **PowerBI serving** omitted — ~20 tribes consume via PowerBI; the cost dashboard is AI/BI-native only. PowerBI-on-UC RLS/chargeback path not designed.
- **Data360 Analyze / Purview already do DQ + catalog** — overlap with the new Databricks DQ track unreconciled (risk: two DQ systems, divergent verdicts).
- **No DR/HA for the obs stack itself** — single PROD Prometheus/Grafana = unmonitored SPOF on the monitoring plane.
- **No acceptance criteria / SLA targets** — what freshness age pages? what lag = incident? what tag-coverage% acts? (95 asserted, not tied to a testable Given/When/Then.) Without these, "observability done" is undefined.
- **Obs solution cost un-estimated** — Dashboard C + Lakehouse Monitoring scans + system-table snapshots all burn DBU (ironic for a cost workstream).
- **Framework DB (`prd_frmwrk_db`) unexamined** as an existing source of job-run/status metadata — confirm before rebuilding what may exist.
- **Classic-VM allocation modality undecided** (cluster-tag propagation vs pro-rate by DBU) + managed-RG name unverified → the join that makes Dashboard A "actual-$" isn't buildable yet.
- **RLS-fires-for-consumer-identity** doc-CONTESTED — the decisive single-identity test not yet run (GO/NO-GO for the whole RLS pattern; moot only because consumers hold Consumer access).
- **`information_schema.row_filters` column names** not doc-verified — `rls_reconcile.py` guesses; DESCRIBE before hardcoding.
