# AIA Data Platform — Master Architecture & Relationships

> The single "read-this-first" document that ties together runtime, the three deploy pipelines,
> observability, and governance. Diagrams are inline (Mermaid, renders in VSCode/GitHub) + the
> detailed drawio files. 🔒 private KB. Date: 2026-07-26.

## 0. Document map (what to read for what)
| Concern | Detailed doc | Diagram (.drawio) |
|---|---|---|
| **Runtime** (data flow) | `raw_architect.md` | `aia-data-platform.drawio` |
| **Deploy / code** (Kafka 3 repos + Databricks framework) | `deploy-framework_raw.md` | `aia-deploy-framework.drawio` |
| **Observability & monitoring** (the current work) | `observability-synthesis.md` | `aia-observability.drawio` |
| **Governance / access** (4 layers) | `../../knowledge/governance-management-deployment-options.md` | (in obs drawio, LANE G) |
| **Confirmed platform facts** | `../../knowledge/data-platform-architecture.md` | — |
| **This master (relationships)** | *(this file)* | (Mermaid inline below) |

---

## 1. The platform in one narrative (RUNTIME spine)

~30 insurance source systems → **dual CDC** (Qlik Replicate log-based + Debezium Kafka-native) →
**Kafka/Strimzi on AKS** (Sin's producer domain) → **Azure Databricks** (real-time Structured Streaming +
batch, config-driven by an Azure SQL MI "Framework DB") → **ADLS Gen2 medallion** (RAW→Persist→Staging) →
serving (**Azure SQL MI ODS** + **Synapse EDW/marts**) → **ESB / PowerBI / apps**. Orchestrated by **ADF+IR**,
governed by **Purview + Data360**.

```mermaid
flowchart LR
  SRC["~30 sources<br/>(Ingenium, AA Admin, CRM,<br/>Magnum, SF360…)"]
  QLIK["Qlik Replicate<br/>(log CDC)"]
  DEBZ["Debezium<br/>(Kafka-native CDC)<br/>= Sin's domain"]
  KAFKA["Kafka / Strimzi on AKS<br/>brokers + Connect gen01/02/03<br/>+ Bridge + Prometheus/Grafana"]
  RT["ADB Real-time<br/>Structured Streaming<br/>(dp-rlt/fw)"]
  BT["ADB Batch<br/>(dp-bt/fw)"]
  LAKE["ADLS Gen2 medallion<br/>RAW → Persist → Staging"]
  ODS["Azure SQL MI — ODS"]
  EDW["Synapse EDW / Departmental marts"]
  SERVE["ESB / PowerBI / apps<br/>~20 business tribes"]
  FWDB["SQL MI — Framework DB<br/>(config-driven)"]
  ADF["ADF + Integration Runtime<br/>(batch orchestrator)"]

  SRC --> QLIK & DEBZ
  DEBZ --> KAFKA --> RT
  QLIK --> BT
  ADF --> BT
  FWDB -.config.-> BT
  FWDB -.config.-> RT
  RT --> LAKE
  BT --> LAKE
  LAKE --> ODS & EDW
  ODS --> SERVE
  EDW --> SERVE
```

---

## 2. The THREE deploy pipelines (never conflate — different owners, different obs hooks)

```mermaid
flowchart TB
  subgraph P1["Pipeline 1 — KAFKA PLATFORM  (MFEC, INHERITED)"]
    B1["dtp_kafka_build_ci<br/>build Strimzi images → ACR"] --> B2["dtp-kafka_cluster<br/>kubectl -f → operator+brokers+Connect+monitoring"] --> B3["dtp-kafka_connector<br/>Debezium KafkaConnector CRs"]
  end
  subgraph P2["Pipeline 2 — DATABRICKS FRAMEWORK dtp_framework_aiath  (INHERITED)"]
    N["Notebook deploy (main.py, git-diff) — FIRST"] --> W["Workflow deploy (workflow_main.py) — SECOND<br/>job_policy → wf_policy_config → workflow_job → permission"]
    W --> MD["update_workflow_info → central metadata table (job_id)"]
  end
  subgraph P3["Pipeline 3 — SIN'S OWN GOVERNANCE/COST/OBS  (deploy/)"]
    T["Terraform L1-L4<br/>entitlement/permission/grant"] 
    DAB["DAB<br/>dashboards + jobs"]
    RJ["rls_reconcile.py<br/>control-table RLS job"]
  end
  P1 -. Kafka topics .-> P2
  P2 -. obs hooks<br/>(job_id, mdle_monitor) .-> P3
  P3 -. ⚠ reconcile grants with<br/>P2 api_assign_permission .-> P2
```
**Rule:** you (Sin) **own P3**, **consume P2's hooks**, **MFEC owns P1**. The obs hooks live in P2 but you build
in P3 → **reconcile your `rls_reconcile` desired-state with P2's `api_assign_permission`/`wf_policy_config`** or
two reconcilers fight over the same grants.

---

## 3. Observability model — 2 panes · 1 spine · 1 seam (the current work)

```mermaid
flowchart TB
  subgraph K["PANE 1 — KAFKA / AKS  (Prometheus + Grafana)"]
    KM["4 metric layers:<br/>L1 JMX (broker/Connect/Debezium)<br/>L2 Kafka-Exporter lag ⭐<br/>L3 operator reconcile ✅ WIRED<br/>L4 kube_pod_* ❌ no KSM"]
    KG["Grafana-managed alert → Mail/Teams<br/>(no Alertmanager)"]
    KM --> KG
  end
  subgraph A["PANE 2 — DATABRICKS  (UC system tables + DQ)"]
    AC["Cost pipeline: Cost Mgmt Export → ADLS<br/>→ 5-layer ETL → cost_wide GOLD"]
    AO["system.lakeflow (job/task/SLA/missing-run)<br/>+ compute + query.history + access.audit<br/>+ DQ (anomaly freshness / profiling drift)"]
    AD["Dashboards A (dept cost) · B (Genie) · C (obs)"]
    AC --> AD
    AO --> AD
  end
  SEAM{{"THE SEAM — bronze freshness<br/>'did the CDC land in bronze?'<br/>Kafka lag ⇔ Databricks max(load_ts) age"}}
  K --- SEAM --- A
  SPINE["SHARED SPINE (cuts both panes):<br/>1) per-team TAG (RLS+chargeback+budget+job key)<br/>2) central metadata table (job_id + mdle_monitor sink)<br/>3) ONE Teams/webhook → Azure Monitor"]
  SPINE -.-> K
  SPINE -.-> A
```
**Sequencing = packaging not effort:** the one question that decides everything — is Prometheus scrape config
**PodMonitor/ServiceMonitor** (light edit → Kafka-Exporter+JMX are quick wins) or **baked image** (rebuild →
paused, same wall as kube-state-metrics). Full phased plan P0–P4 in `observability-synthesis.md §3`.

---

## 4. Governance / access — 4 layers (applies to the cost dashboard)

```mermaid
flowchart LR
  L1["L1 Identity<br/>account groups via SCIM/Entra"] --> L2["L2 Entitlement<br/>Consumer-access (workspace_consume SOLE)<br/>Terraform, PR-gated"]
  L2 --> L3["L3 Object ACL<br/>warehouse CAN_USE / dashboard CAN_READ<br/>DAB + TF"]
  L3 --> L4["L4 Data grant + RLS<br/>control-table reconcile JOB<br/>is_account_group_member + embed_credentials:false"]
  L4 --> GATEC{{"GATE C — NETWORK<br/>GRANT ≠ network path<br/>403 if firewall/PE closed"}}
```
Churn-based modality: **SCIM** (identity) · **Terraform** (entitlement, structural grant) · **DAB** (dashboard,
object ACL) · **reconcile-job** (high-churn RLS). Detail: `governance-management-deployment-options.md`.

---

## 5. Master relationship map (how a single team's cost view is produced end-to-end)

```mermaid
flowchart LR
  DBZ["Debezium CDC"] --> TOPIC["Kafka topic"] --> RTC["ADB Real-time<br/>dp-rlt/fw"] --> BRONZE["Delta bronze"]
  BRONZE --> SILVER["silver/gold"] 
  COST["Azure Cost Mgmt Export"] --> ETL["5-layer cost ETL<br/>(keep custom_tags MAP)"] --> CW["cost_wide GOLD<br/>tag_team top-level col"]
  CW --> RLSV["v_billing_priced_rls<br/>is_account_group_member + team_access_map"]
  RLSV --> DASH["Dashboard A (per-team)<br/>embed_credentials:false"]
  GRP["Entra account group<br/>consumer-team"] --> RLSV
  RJOB["rls_reconcile.py<br/>(control table)"] --> RLSV
  DASH --> TEAM["Team sees ONLY its rows"]
  TOPIC -. consumer-lag .-> SEAM["bronze-freshness seam"]
  BRONZE -. max(load_ts) age .-> SEAM
```

---

## 6. Status & gates (what's done / pending / blocked)
| Item | Status |
|---|---|
| Runtime + deploy architecture captured | ✅ done (4 drawio + 4 md) |
| Kafka interim reconcile alert | ✅ wired (Sin has email working) |
| Grafana alert enrichment (issue detail + deep-link) | 📄 manual written (`grafana-alert-user-manual.md`) |
| RLS-correct cost Dashboards A+B | ⚠️ deployed SQL has 2 bugs to fix (Genie GROSS/NET, usage_unit) |
| Genie cost SQL | 🔎 verifying (GROSS+floor, usage_unit) |
| Entitlement migration (2026-07-27) | 🔎 verifying necessity/impact |
| GATE C network path (D+) | ⏳ PoC pending at coredata UAT |
| Kafka Exporter (lag) + JMX | ❓ blocked-or-not depends on Prometheus packaging (Q1) |
| kube-state-metrics (L4) | ⛔ paused (needs image rebuild) |
| Observability Dashboard C (Topic 3) | ⏸️ deferred (needs metadata-table schema + system tables) |
| Open questions to Sin | 📋 14 in `observability-synthesis.md §6` |

---

## 7. The 5 hard truths to keep front-of-mind
1. **A UC GRANT is not a network path** — GATE C (firewall/PE) is independent and make-or-break for D+.
2. **Packaging, not effort, blocks Kafka metrics** — resolve PodMonitor-vs-baked before assuming lag/JMX are stuck.
3. **RLS fails silently in 4 ways** — ship `is_account_group_member()` + 4 grants (incl EXECUTE) + `embed_credentials:false` + right group, as one unit; test as a real consumer.
4. **Three deploy pipelines, three owners** — you consume P2's hooks, own P3; reconcile the two grant-appliers.
5. **The tag is the spine** — one `MAP→column` team tag = RLS + chargeback + budget + job-pipeline key; keeping it (vs บูม dropping it) is what makes everything per-team possible.
