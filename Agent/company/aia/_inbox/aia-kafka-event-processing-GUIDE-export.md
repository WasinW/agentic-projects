# AIA Kafka Event-Processing — Onboarding Guide (portable export)

> **Purpose of this file:** a self-contained brain-dump so that (a) I can re-read it on my phone, and (b) a fresh AI chat with NO prior context can understand my situation and keep helping me. Everything below was reverse-engineered from git screenshots + guidance in a previous session (2026-07-01). Where something is confirmed vs guessed is marked.

---

## 0. Who I am / my situation (context primer for a fresh chat)

- I'm **Wasin, Senior Data Engineer, newly started at AIA** (life insurance, Thailand), 2026-07-01.
- Background: strong in **Spark / Azure Databricks + config-driven ETL frameworks** (ex-SCB, built the RDT regulatory ETL framework on Azure Databricks + ADF; ex-The-1/Central, GCP Dataflow streaming). **I am NEW to Kafka-on-Kubernetes** — explain that layer from first principles.
- My scope at AIA = the **event-processing / Kafka layer**, an internal platform branded **"Kafka MFEC" / DTP** (Data Platform; MFEC = the system-integrator that built it).
- **Stack = Azure** (NOT AWS): Azure Databricks (ADB), Azure Data Factory, ADLS, Azure SQL/Synapse, **AKS** (Azure Kubernetes Service), Azure Container Registry (ACR), PowerBI. CI = **Jenkins**. Git = **Bitbucket** (org `aia-th`).
- **STRICT policy: I cannot export code or data.** Any helper must reason from architecture + screenshots I describe, and give me self-check checklists rather than asking me to paste code.

---

## 1. THE key concept: AKS is infrastructure, not a program

I was confused whether "AKS" is IaaS or code I write. Answer:

| Layer | What it really is | Analogy |
|---|---|---|
| **AKS (Azure Kubernetes Service)** | **Managed infrastructure** — a ready-made Kubernetes cluster Azure runs (VM pool + control plane). Closest to **PaaS**. NOT IaaS-you-configure, NOT my code. | the electric grid — you plug in, you don't build it |
| **Kubernetes (k8s)** | the **orchestrator** on AKS. You give it **YAML describing desired state**; it schedules **containers (pods)** and keeps them alive. | a robot foreman: give it a blueprint, it builds & maintains |
| **Strimzi operator** | a **controller program that runs INSIDE k8s** and understands Kafka. Give it `Kafka`/`KafkaConnector` YAML → it creates the real broker/connector pods. | a Kafka-specialist robot the foreman calls in |
| **The 3 repos (YAML)** | just the **blueprints** (desired state in git). No imperative logic. | the drawings |

**Why I couldn't find "the program that builds Kafka": there isn't one.** The YAML is the input; the *operator* (written by the Strimzi project, shipped as a container image) is the engine. That's the whole "operator pattern" — replace deploy scripts with *declarative desired-state + a reconciler*.

Only **two kinds of "run"** exist here:
1. **Install the engine once** — deploy the Strimzi **operator** into the cluster. It then watches for Kafka CRDs forever.
2. **Declare what you want** — apply a `Kafka` CR (→ operator builds brokers) or a `KafkaConnector` CR (→ operator starts a CDC connector). Editing a topic/table = edit YAML + re-apply; the operator reconciles.

---

## 2. End-to-end architecture (CONFIRMED from git)

```
AIA source databases  (Oracle e.g. "cmic";  SQL Server e.g. "bbl360sql"; also autopay, ams,
                        appsub/smartclaim, aiaone*, aa, cmac ...)
        │
        │  Debezium CDC  (change-data-capture: streams every insert/update/delete)
        ▼
  Kafka Connect runtime  ──►  Kafka topic  ──►  Azure Databricks (Structured Streaming)  ──►  Delta table
   (on AKS, Strimzi-managed)        │                                                          (raw → ... zones)
                                    └──►  Kafka Bridge (HTTP↔Kafka, for REST consumers)

  Built & shipped by:  Jenkins  ──build images──►  ACR  ──pulled by──►  AKS
  Monitoring: Grafana + Strimzi Kafka Exporter.   DR: every prod resource has a "-dr" mirror.
  Namespaces like:  651563-kbdev-cluster   (pattern: <project-code>-<env>-cluster)
```

- **Producers** = Debezium CDC connectors (Oracle/SQL Server/Postgres source connectors, Debezium 1.9.7.Final).
- **Consumers** = Azure Databricks Structured Streaming → Delta (this side is already my strength).
- **My job ≈ own the CDC connectors** (details in §5).

---

## 3. The 3 repos (Bitbucket org `aia-th`) and how they chain

```
   dtp_kafka_build_ci  ──builds Docker images──►  ACR (image registry)
        (image factory; deploys NOTHING)             │  cluster & connector reference image tags from ACR
                                                      ▼
 ① dtp_kafka_cluster   ──Jenkins deploy──►  Strimzi operator installed + Kafka brokers created
                                            (+ likely the KafkaConnect runtime)
                                                      │
                                                      ▼
 ② dtp_kafka_connector ──Jenkins deploy──►  KafkaConnector (Debezium CDC) CRs onto the running Connect runtime
```

**Per-repo detail:**

| Repo | Holds | Deploys via | The deploy actually does |
|---|---|---|---|
| **dtp_kafka_build_ci** | Dockerfiles + Jenkinsfiles + Strimzi operator versions + "Images Release version" README | Jenkins build jobs | `docker build` custom images (Connect image = base Strimzi + Debezium + a custom `TimestampConsumer` jar; bridge; grafana) → **push to ACR** (prod/non-prod) |
| **dtp_kafka_cluster** | Strimzi operator install manifests (`install/<ver>/{cluster,topic,user}-operator`, `drain-cleaner`) + the `Kafka` cluster CR + certs (`cert/`, `get_crt.sh`) + Grafana dashboards + per-env `jenkins-cd-*` | `jenkins-cd-<env>` | `kubectl/helm apply` the operator + the `Kafka` CR → operator **creates the broker pods** (StatefulSet) on AKS |
| **dtp_kafka_connector** | `KafkaConnector` (Debezium) YAMLs — one per source system, organized by **env × Strimzi-version** (`connector-{dev,uat,prod,dr}-main{,0.38,0.45,0.49.1}`); a `connect/` folder likely holds the `KafkaConnect` runtime CR | `.jenkins/` pipeline | `kubectl apply` the connector CRs → operator **starts the Debezium connectors** on the Connect runtime |

**Key point:** build_ci is NOT wired directly to the others — the link is the **image tag in ACR** that the cluster/connector YAML references. Order = **cluster first (brokers + Connect runtime), connector second (attach connectors)**.

**Jenkins scripts live in 2 places:** the **pipeline definition (Jenkinsfile / `jenkins/` / `.jenkins/`)** is IN each repo; the **job that runs** is on the **Jenkins server** (need Jenkins UI access to see which job deploys what).

---

## 4. How the Kafka cluster is actually CREATED (the sequence)

1. `dtp_kafka_build_ci` (Jenkins) builds images → **ACR**.
2. `dtp_kafka_cluster/install/<ver>/...` deploys the **Strimzi operator** into the AKS namespace → operator pod starts, watches for Kafka CRDs.
3. Apply the **`Kafka` cluster CR** (in `dtp_kafka_cluster`) → the cluster-operator **creates a StatefulSet of broker pods** + storage (PVC on Azure Disk) + services + certs. *This* is "Kafka being created" — no VM install, no `kafka-server-start.sh`.
4. Apply **`KafkaConnect`** (runtime) + **`KafkaConnector`** CRs → Debezium connectors pull from source DBs into topics.
5. **Azure Databricks** reads the topics → Delta.

There is **no monolithic deploy script**. "Deployment" = Jenkins pipelines running `docker build/push` (→ ACR) and `kubectl apply`/`helm` (→ AKS). The YAML is the "what"; the pipeline is the "how"; the operator does the actual building.

---

## 5. The connector layer = my likely day-to-day (CONFIRMED)

**One YAML = one `KafkaConnector` = one source system**, via Debezium CDC. Anatomy:

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaConnector
metadata:
  name: cmic-connector
  labels:
    strimzi.io/cluster: <the KafkaConnect runtime name>   # binds connector to a Connect cluster
spec:
  class: io.debezium.connector.oracle.OracleConnector      # cmic=Oracle; bbl360sql=SqlServer; etc.
  tasksMax: N
  config:
    database.hostname / port / user / password: ...        # the source DB
    database.dbname / database.names: ...
    topic.prefix (or database.server.name): ...            # → topic naming
    table.include.list: SCHEMA.TBL_A, SCHEMA.TBL_B, ...    # ← WHICH TABLES are captured  (most-edited field)
    snapshot.mode: ...                                      # initial-load behaviour
    key.converter / value.converter: ...                   # Avro/JSON (+ schema registry)
    transforms: ...                                         # SMTs (routing/unwrap/etc.)
```

**My day-to-day (read from the commit history "add new tbl ..."):**
1. **Onboard a new table into CDC** → add it to `table.include.list` (in the correct env file, start `connector-uat-main<latest>`).
2. **Rebuild/redeploy** via the connector Jenkins pipeline → applies the `KafkaConnector` CR → Strimzi reconciles it into the running Connect cluster.
3. **Promote across envs**: dev → uat → **prod AND prod-dr** (keep the DR twin in sync).
4. **Version migrations** — e.g. "prepare for sf360 migration", moving connectors onto a newer Strimzi/cluster version (0.45 → 0.49.1). This is the migrate/re-platform work.
5. **Operational fixes** — "restart strimzi operator", "delete all connector on cluster 1.24", "update message.max.bytes".

---

## 6. Strimzi resource kinds — read by `kind:`, don't trace call-flow

| `kind:` | Creates | Repo |
|---|---|---|
| `Kafka` | the cluster (brokers, ZooKeeper/KRaft, listeners, storage) — main CR | dtp_kafka_cluster |
| `KafkaTopic` | one topic (partitions, replicas, retention) | dtp_kafka_cluster |
| `KafkaUser` | a user + ACLs + credentials | dtp_kafka_cluster |
| `KafkaConnect` | the Connect runtime (hosts connectors) | connector (`connect/`) |
| `KafkaConnector` | one Debezium CDC connector | dtp_kafka_connector |
| `KafkaBridge` | HTTP↔Kafka bridge | build_ci/cluster |
| `KafkaMirrorMaker2` / `KafkaRebalance` | cross-cluster mirror (DR) / rebalance | if present |
| `ServiceAccount`/`Role`/`ClusterRole`/`RoleBinding`/`CRD`/`Deployment` | the OPERATOR install (not Kafka itself) | dtp_kafka_cluster `install/` |

**Strategy:** open each file, look at its `kind:` line, group by kind. You inventory declarative objects; you do NOT follow an imperative program.

---

## 7. How to find "what is LIVE / what is main" in the messy repos

The repos use **env × version folders as a substitute for branches** — that's why they look chaotic (`connector-prod-main`, `connector-prod-main0.45`, `install/0.49.1`, `version/0.35`, `_old`, `-del`...). Heuristic:

1. **Version = the number suffix** (`0.38/0.45/0.49.1` = Strimzi version). The highest number in **recent commits** is the migration target (`0.49.1` + "sf360 migration" 10 hours ago = active).
2. **"main" = `*-main<latest-version>` for the target env.** Prod-live ≈ `connector-prod-main<latest>`. `_old`/`-del` = history — ignore.
3. **README wins ties** — `dtp_kafka_build_ci` "Images Release version" lists currently-released versions.
4. **The Jenkins CD job is the final truth** — whatever folder/branch the prod CD pipeline applies IS live.
5. **`-dr` = disaster-recovery mirror**, keep in sync with prod.

One rule: **live prod ≈ `connector-prod-main<highest-version>` + the README versions + whatever the prod Jenkins CD job applies.** Everything else is history.

---

## 8. What I still need to see (screenshots to grab next)

Still unseen: the **`Kafka` cluster CR internals** (brokers/storage/KRaft) and whether the **`KafkaConnect` runtime** lives in the connector repo's `connect/`.

In repo `dtp_kafka_cluster`, **Bitbucket code-search `kind: Kafka`** (or open `dev/`, `datazone/`, `examples/`). Grab:
1. the folder listing where `kind: Kafka` lives,
2. the `kind: Kafka` file contents (broker count, storage, listeners, KRaft-or-ZooKeeper),
3. one or two `KafkaTopic` files.
(The `install/` manifests already seen are the *operator install*, not the cluster CR.)

---

## 9. What to brush up (small, targeted)
- **Kubernetes basics:** pod, StatefulSet, Service, PVC, namespace, `kubectl get/describe/logs`.
- **Strimzi CRDs:** `Kafka`, `KafkaTopic`, `KafkaUser`, `KafkaConnect`, `KafkaConnector` + the cluster/topic/user operators.
- **Kafka core:** broker, topic, partition, consumer-group, offset, replication.
- **Debezium:** what CDC is, snapshot vs streaming mode, connector config, `table.include.list`.
- **Debugging here = `kubectl get/describe` the CRs + operator logs**, not reading program flow.

## 10. Questions to confirm with the team (hypothesis → fact)
- Which Jenkins jobs are the **real prod CD** per repo, and which folder/branch do they apply?
- Current **live Strimzi version** in prod (is 0.49.1 target vs deployed)?
- Deploy via **`kubectl apply` or `helm`**? Any GitOps (ArgoCD/Flux) or Jenkins-push only?
- **`Kafka` cluster CR** structure — brokers, KRaft vs ZooKeeper, storage?
- Promotion + approval flow dev→uat→prod→dr?
- What is the **`sf360` migration** moving — a system, a cluster version, or both?
- Is Databricks the only consumer, or do sink connectors also land data?
- Schema Registry in use (Avro/JSON, compatibility policy)?
- What's *my* first concrete task — maintain a connector, add a table, or build/CI work?

---
*Reverse-engineered 2026-07-01 from git screenshots. CONFIRMED: Strimzi-on-AKS + Debezium CDC + Jenkins→ACR→AKS + Azure Databricks consumers. NOT yet seen: the `Kafka` cluster CR internals. Nothing here is copied AIA code — it's architecture-level notes only.*
