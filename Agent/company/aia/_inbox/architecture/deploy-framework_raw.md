# AIA Data Platform — Deployment & Framework (raw transcription)

> Transcribed by Claude from Sin's 5 screen-photos of an in-env agent (Claude Sonnet) analysis of the
> actual repos, + Sin's typed folder-structure/Jenkins notes. **Raw dump**, faithful to the captures.
> `[?]` = best-effort read. 🔒 AIA-internal — private KB only.
> Companions: runtime = `raw_architect.md` / `aia-data-platform.drawio`; this = `aia-deploy-framework.drawio`.

## 0. Wide overview (Sin's mental model — the 3-part framework)

```
Data Platform Framework
├── Job Pipeline            ├── Batch
│                           └── Streaming
└── Framework              ├── Config Table
                           ├── Databricks Workflow
                           ├── Transformation Scripts
                           └── custom scripts (optional): custom dependency-check (w/ config dependency),
                                pre-process (before real transform), custom audit for special jobs
                                — NOT standard; config-driven "do you want to customize?"

Deployment
├── Jenkins
└── Core Data Platform     ├── Kafka   — 3 repos (§1)
                           └── Databricks — repo dtp_framework_aiath (§2)
```

---

## 1. KAFKA platform — 3 repos (build → cluster → connector)

```
dtp_kafka_build_ci ──push images──► ACR ──► dtp-kafka_cluster ──deploy──► Strimzi Operator + Kafka Cluster
                                                                                   ▲
dtp-kafka_connector ──deploy CR──► KafkaConnector resources ····runs inside········┘
```

### 1.1 `dtp_kafka_build_ci` — build image ("โรงงานผลิตชิ้นส่วน")
- **Output:** Docker images pushed to **ACR** — `acrth01seanshared01.azurecr.io/...`
- Builds the WHOLE Strimzi image set (not one image): `strimzi-base`, `strimzi-operator`,
  `strimzi-kafka`, `strimzi-kafka-connect`, `strimzi-kafka-bridge`, `strimzi-jmxtrans`,
  `strimzi-kaniko-executor` (+ prometheus / grafana / alertmanager images — surfaced in the notification work).
- Knows NOTHING about AKS/cluster: just **compile (Maven) → `docker build` → push** artifact. Deploys nothing.

### 1.2 `dtp-kafka_cluster` — deploy the Kafka platform itself ("ประกอบรถ + มาตรวัด")
- **Output:** real resources on **AKS** (`aks-th01-sea-u-kfka01-gemblz4` = UAT) via
  **`kubectl create/delete -f`** (raw manifest, **NOT Helm**).
- Creates:
  - **Strimzi Cluster Operator** (main controller, deployed first)
  - **Kafka cluster** (broker/controller pods)
  - **KafkaConnect clusters** — **gen01 / gen02 / gen03** ← the one with the restart-loop incident
  - **Kafka Bridge** (REST proxy)
  - **Monitoring stack: Prometheus + Grafana** (+ Alertmanager, newly added)
- = the **infrastructure layer** (pulls repo #1's images and assembles the running cluster).

### 1.3 `dtp-kafka_connector` — deploy connectors ("เติมของเข้ารถ")
- **Output:** `KafkaConnector` custom resources (CR) applied into the same namespace as the cluster from #2.
- These are **Debezium CDC connectors** → connect to source DB (Oracle/SQL Server) → pull change events
  (insert/update/delete) → Kafka topics.
- Creates NO new infra — just "plugs in" the connector job onto the existing Kafka Connect cluster.
  = the **application/job layer** running ON the cluster.

### 1.4 Summary
| Repo | Analogy | Layer |
|---|---|---|
| `dtp_kafka_build_ci` | parts factory (image) | build/CI |
| `dtp-kafka_cluster` | assemble the car + gauges (cluster + Connect + monitoring) | infrastructure |
| `dtp-kafka_connector` | load cargo into the finished car (connector job) | application/job |

→ Sequence **build → cluster → connector**; the real data endpoint (Kafka topics) is then **consumed by
Databricks** (`dtp_framework_aiath`, the **DP_RLT** realtime path — §2, separate `adb` repo).

---

## 2. DATABRICKS framework — repo `dtp_framework_aiath`

Structure = **3 parts: Deployment / Framework / Workflow.** Deploy flow:

```
Git Repo (dtp_framework_aiath)
        ▼
Jenkins (deployments/)
        ├──────────────► Notebook Deploy Engine   (main.py, git-diff incremental import)
        └──────────────► Workflow Deploy Engine    (workflow_main.py → workflow_dpy.py)
                                 ▼
                         workflow_bt/, workflow_rlt/   (Jobs/Policy created via API)
        ▼ (both converge into the workspace)
dp-bt/fw, dp-rlt/fw   (framework code imported to workspace)
        ▼
DP_DDL/ + dsl/   (DDL — SEPARATE execution path)
```

### 2.1 Deploy part (`deployments/`) — TWO engines, different pipelines
> This is the "why deploy twice?" confusion — they're two distinct pipelines.

| Engine | Jenkinsfile | Does what |
|---|---|---|
| **Notebook deploy** | `JenkinsFile.dtp_adb_dev/uat/prd/dr` | imports code/notebooks (`dp-bt/fw`, `dp-rlt/fw`, DDL) into the Databricks **workspace** — `main.py` compares **CURRENT_VERSION vs NEW_VERSION** (git diff) → imports **only changed files** (no full overwrite) |
| **Workflow deploy** | `JenkinsFile_workflow.dev/uat/prd` | creates/resets Databricks **Jobs** via Jobs API — `workflow_main.py → workflow_dpy.py` (job policy → workflow policy config → workflow job → permission) |

**⚠️ Order matters:** **Notebook deploy runs FIRST** (code into workspace), **then Workflow deploy**
(creates jobs that call that code). Reversed → jobs point to notebook paths that don't exist yet.

**Jenkins workflow_main.py invocation (from Sin's note):**
```
python -u deployments/python/workflow_main.py ${host} ${token} ${WORKFLOW_DIR} \
       ${CURRENT_VERSION} ${NEW_VERSION} ${WORKFLOW_ENV} ${WORKFLOW_RUN_AS}
```

### 2.2 Framework part (`dp-bt/fw`, `dp-rlt/fw`) — answers "fw เยอะ ไม่รู้อันไหนหลัก"
Two frameworks, separate engines, don't mix:

**Batch (`dp-bt/fw`)** — 5+ engines by function (NOT one scattered script):
```
fw/ingt/bin/fw_ingt_main.py       <- MAIN: ingestion (pull files/data in)
fw/tnfm/bin/fw_tnfm_wrapper.py    <- MAIN: transform
fw/svc/bin/fw_svc_main.py         <- MAIN: service layer
fw/outbnd/bin/fw_outbnd_main.py   <- MAIN: outbound (send to downstream)
fw/hskp/bin/*.py                  <- housekeeping (cleanup/retention)
fw/init/run_init_config*.py       <- bootstrap config (first-time setup)
```
**Rule:** files ending `_main.py` / `_wrapper.py` in a folder's `bin/` = that engine's **entry point**;
everything else in `fw/` = modules those entry points call (not invoked directly by a job).

**Realtime (`dp-rlt/fw`)** — single job, fewer engines than batch:
- `fw_rlt_wrapper.py` = main entry point (read config → connect Kafka source → stream → persist)
- Sub-modules the wrapper calls: `mdle_conn*.py`, `mdle_prrc_write_strg*.py`, `mdle_monitor*.py`,
  `mdle_offset.py` — pattern: **read config → connect kafka → stream+preprocess → write delta →
  monitor/offset tracking**

### 2.3 Workflow part (`workflow_bt/`, `workflow_rlt/`) — 3-layer config
```
job_policy/<env>/*.json      -> cluster spec (spark config, node type, autoscale) per env
wf_policy_config/*.json      -> mapping "this workflow uses which policy"
workflow_job/*.json          -> the real job definition (task, notebook path, schedule, dependency)
```
**Deploy flow (matches Sin's note):**
1. **job policy** → `api_policy_apply` (create cluster policy on Databricks, `policies/clusters/create`)
   + `api_assign_pc_permission` (which group may use it, `permissions/cluster-policies`)
2. **workflow policy config** → bind the workflow to the policy from step 1
3. **workflow job** → create the real job from `workflow_job/*.json`, then `api_assign_permission`
   (which group / service principal may run/view, `permissions/jobs`) + write `job_deploy_info.txt`
- After deploy: extra step runs notebook **`update_workflow_info`** to update a central **metadata table**
  with the latest `job_id` (for tracking/monitoring). Example workflow: `pl_all_dm_agent`.

### 2.4 DDL/DML deploy — answers "งง DDL/DML deploy ยังไง" (SEPARATE path)
`DP_DDL/` does **NOT** go through the workflow deploy engine — it's a different path:
- `DP_DDL/<ZONE>/*.sql` = DDL scripts by zone (RAW / STAGING / ODS / EDW / DM / SYNAPSE / UNITY_CATALOG…)
- `dsl/run_ddl.py` + `dsl/util_config.py` = runs DDL directly into Databricks / SQL warehouse
  (**NOT** via Jobs API like workflows)
- To add a new table → run `dsl/run_ddl.py` yourself (or a separate pipeline calling it) —
  **not** via `main.py` / `workflow_main.py`.

---

## 3. 🧠 Claude — how this connects (architect notes)
- **This is the DEPLOY/CODE view**; `raw_architect.md` is the RUNTIME view. Kafka §1 = the EVENT
  PROCESSING zone; Databricks §2 (`dp-rlt/fw`) = the Real-time cluster consuming Kafka (the
  stream-join-stream work); `dp-bt/fw` = the Batch cluster; DDL zones = the medallion + Synapse/UC tables.
- **Corrected read** vs the runtime capture: ACR = `acrth01seanshared01` (earlier `[?]`), AKS UAT =
  `aks-th01-sea-u-kfka01-gemblz4`.
- **Ties to Sin's 4 focus areas:**
  1. **Access Mgmt** — the `api_assign_permission` / `api_assign_pc_permission` steps (§2.3) ARE the
     entitlement/permission layer in code; group/service-principal grants live in `wf_policy_config` +
     `job_policy`. This is where Access-Mgmt-as-code already partially exists.
  2. **Monitoring/Observability** — `update_workflow_info` → central metadata table (`job_id`) is the
     hook for **job-pipeline tracking**; realtime `mdle_monitor*.py` + Kafka Prometheus/Grafana (§1.2) =
     the observability spine; DDL zones + DQ = data-quality layer.
  3. **Streaming provider** — Kafka §1 + the restart/alert work (Monitoring stack in §1.2).
  4. **Consumer stream-join** — `dp-rlt/fw` (`fw_rlt_wrapper.py`) is exactly where the stream-static-join
     pattern would live (see `../google_ai_chat/adb-consume-stream-join-CURATED`).
- **Sin's noted pains** (for later deep-dive): "fw เยอะ ไม่รู้อันไหนหลัก" → answered by the `_main.py`/
  `_wrapper.py` entry-point rule (§2.2); "DDL/DML deploy งง" → answered by the separate `dsl/run_ddl.py`
  path (§2.4).

## 4. Uncertain reads to verify
- Exact suffixes on `workflow_dpy.py` / list names (`incre_policy_list`, `workflow_flow1_list`,
  `workflow_flow2_list`) — from Sin's typed note, confirm against repo.
- `NOTEBOOK_DIR_COMMON`, `executenotebook_ods.py` args.
- Whether gen01/02/03 map to specific source domains.
