# AIA Event Processing — Kafka on AKS (learning notes)

> Wasin's actual scope at AIA = the **event-processing / Kafka layer**: sources → producers → **Kafka on AKS** → topics → **Azure Databricks** Structured Streaming consumes → tables. Stack is **Azure** (ADB, ADF, ADLS, AKS, ACR). The 3 repos (`dtp_kafka_build_ci`, `dtp_kafka_cluster`, `dtp_kafka_connector`) are "all YAML" — this doc explains why, and what builds/runs/deploys.
>
> **Confidence note:** ✅ **CONFIRMED Strimzi** from git screenshots (2026-07-01) — see §0. "dtp" = Data Platform; the platform is branded "Kafka MFEC" (MFEC = the SI that built/maintains it).

## 0. CONFIRMED from git screenshots (2026-07-01)

Hard evidence seen in Bitbucket — the architecture is **Strimzi (Kafka-on-Kubernetes operator) on AKS, CI'd by Jenkins, images in ACR**:

| Evidence seen | Confirms |
|---|---|
| `dtp_kafka_build_ci/version/{0.20,0.27,0.35,0.38}/strimzi-kafka-operator` | Strimzi operator, multiple versions (they upgrade over time) |
| `dtp_kafka_cluster/install/<ver>/{cluster-operator, topic-operator, user-operator, drain-cleaner}` + manifests `01-ServiceAccount-…`, `04-Crd-kafkatopic.yaml`, `Crd-kafkauser` | Strimzi operator install (standard component split) |
| `kafka-bridge/…/strimzi-kafka-bridge` (0.21/0.23/0.25) | Strimzi **Kafka Bridge** (HTTP↔Kafka REST) is deployed |
| README "Kafka MFEC" → `strimzi-kafka-connect:0.35-kafka-2.8.0` + **`debezium-connector-oracle/sqlserver/postgres 1.9.7.Final`** | Connect image + **Debezium CDC** source connectors (Oracle/SQL Server/Postgres) |
| `kafka-connect/{my-plugins, kafka-kubernetes-config-provider, Dockerfile-connect-strimzi-2.8.0, TimestampConsumer-1.2.4.jar}` | Custom Connect image = base + plugins + a bespoke `TimestampConsumer` jar |
| `Jenkinsfile-0.20.1-connect_2.60`, `jenkins-cd-dev-0.35.0-datazone`, per-env `jenkins-cd-*` | **CI/CD = Jenkins** (not Azure DevOps), per-version + per-env pipelines |
| `grafana/{config,dashboard,Dockerfile}` + dashboards `Strimzi Kafka Exporter/Connect`, `MONITOR_DATALAKE`, `Azure SQL/Storage Insights` | Monitoring = **Grafana + Strimzi Kafka Exporter** + Azure dashboards |
| `dtp_kafka_cluster/cert/{get_crt.sh, manual_gen_cert.md, WORLDCert, ca-password}` | Custom **TLS/DNS certs** managed for the cluster listeners |
| namespace `651563-kbdev-cluster` in a ServiceAccount manifest | AKS namespace = `<project-code>-<env>-cluster` (env `kbdev`) |
| "pull kafka image from acr prod to none-prod" | promotion path across ACR prod ↔ non-prod |

So the earlier guesses are now facts, with two corrections: **CI is Jenkins** (not Azure DevOps), and **producers are Debezium CDC connectors** pulling from Oracle/SQL Server/Postgres into topics.

## 1. The one idea that makes "all YAML" make sense

Kafka here does **not** run on VMs you SSH into. It runs on **Kubernetes (AKS)**, managed **declaratively by an operator**. You don't write code that "starts Kafka" — you write **YAML that DESCRIBES the Kafka you want** (how many brokers, which topics, which connectors), and an **operator** running inside the cluster continuously makes reality match that description (and re-heals it if something drifts). 

That's the whole reason the repos are nothing but YAML: **the YAML *is* the system.** There is no imperative "main()". This pattern is called **GitOps / declarative infrastructure**, and for Kafka-on-Kubernetes the dominant operator is **Strimzi** (alt: Confluent-for-Kubernetes). Strimzi defines **Custom Resources (CRDs)** — new Kubernetes object types like `Kafka`, `KafkaTopic`, `KafkaConnector` — so you manage Kafka with `kubectl apply` just like Deployments.

Mental model: **YAML (git) → CI applies it → operator reconciles → running Kafka.**

## 2. The end-to-end architecture (where your repos sit)

```
                 (event-processing producers, on AKS)
  sources  ─────────────►  publish  ─────────►  ┌──────────────────────────┐
 (apps/CDC/                                       │  KAFKA CLUSTER (on AKS)   │
  services)                                       │  brokers + topics        │  ◄── dtp_kafka_cluster
                                                   │  (Strimzi-managed)       │
                          ┌────────────────────────┤                          │
                          │                        └───────────┬──────────────┘
                          │                                    │
                 ┌────────▼─────────┐                 ┌────────▼───────────┐
                 │  Kafka Connect   │ ◄── dtp_kafka_  │  Azure Databricks  │
                 │  source/sink     │     connector   │  Structured        │
                 │  connectors      │                 │  Streaming consumer│
                 └────────┬─────────┘                 └────────┬───────────┘
                          │                                    │
                     (to/from ADLS,                      writes to Delta
                      Azure SQL, etc.)                   raw → persist → ...

  dtp_kafka_build_ci  = the CI/CD that builds the images + deploys the two repos above to AKS
```

- **Producers** publish events to **topics**. (Sometimes producers are their own services; sometimes ingestion is done by **Kafka Connect source connectors** — e.g. Debezium CDC from a database into a topic.)
- **Consumers** read topics. Here the main consumer is **Azure Databricks Structured Streaming** (your existing `streaming-batch-patterns` / `databricks-streaming-pattern` skill covers this side). **Kafka Connect sink connectors** may also land data into ADLS/Azure SQL without Spark.

## 3. Repo-by-repo (what each builds / runs / deploys)

### `dtp_kafka_cluster` — the Kafka cluster itself
- **What it is:** the declarative definition of the broker cluster. Under Strimzi, the key files are a `kind: Kafka` resource (+ likely `KafkaNodePool` for broker/controller pools in newer KRaft mode), plus `KafkaTopic` and `KafkaUser` resources, and listener/TLS/auth config.
- **What it declares:** number of brokers (`replicas`), storage (PVC size/class on Azure Disk), listeners (internal TLS, SCRAM-SHA/mTLS auth), topic definitions (partitions, replication-factor, retention), users + ACLs.
- **How it "runs":** the Strimzi **Cluster Operator** watches these resources and creates the actual **StatefulSet** of broker pods, services, config, certs. You never start a broker by hand — you edit YAML and the operator rolls it.
- **Deploy:** `kubectl apply`/Helm/Kustomize of these manifests into the Kafka namespace on AKS (done by the CI repo).

### `dtp_kafka_connector` — Kafka Connect + connectors
- **What it is:** two layers of YAML —
  1. a **`kind: KafkaConnect`** resource = the Connect *runtime* (a cluster of worker pods that host connectors), including which **plugins/images** it uses and how it talks to the brokers.
  2. one **`kind: KafkaConnector`** per pipeline = a specific **source** (external system → topic) or **sink** (topic → external system) connector, with its `class`, `tasksMax`, `topics`, converters (Avro/JSON + Schema Registry), and transforms (SMTs).
- **What it declares:** e.g. a Debezium source connector doing CDC from Azure SQL into a topic, or a sink connector writing a topic to ADLS/Blob. The connector `class` tells you exactly what it does.
- **How it "runs":** the Connect worker pods run the connector tasks continuously; the operator reconciles the `KafkaConnector` spec into the running Connect cluster via its REST API.
- **Deploy:** same — manifests applied to AKS; the custom Connect **image** (with the connector JARs baked in) comes from the CI repo → ACR.

### `dtp_kafka_build_ci` — the build + deploy pipeline
- **What it is:** the CI/CD glue (almost certainly **Azure DevOps `azure-pipelines.yml`**, maybe Helm charts / Kustomize overlays / a Makefile).
- **Build stage:** builds **container images** — most importantly a **custom Kafka Connect image** = base Strimzi/Connect image + the connector plugin JARs your pipelines need — then **pushes to Azure Container Registry (ACR)**. May also lint/validate the YAML.
- **Deploy stage:** authenticates to AKS and **applies the manifests** from `dtp_kafka_cluster` and `dtp_kafka_connector` (kubectl/helm), usually per environment (dev/uat/prod) via overlays/variable groups. This is the repo that ties the other two together and actually pushes changes to the cluster.

## 4. Build → run → deploy, as one lifecycle

1. **Change YAML** in `dtp_kafka_cluster` or `dtp_kafka_connector` (e.g. add a topic, add a connector), commit, open MR.
2. **CI (`dtp_kafka_build_ci`)** runs: builds/pushes any needed image to **ACR**, validates manifests.
3. **CD** applies the manifests to the **AKS** namespace for the target env.
4. **Strimzi operator** on AKS sees the new/changed CRs and **reconciles** — creates the topic, rolls the brokers, or updates the connector — with no downtime for unrelated resources.
5. **Runtime:** brokers serve topics; producers publish; **ADB Structured Streaming** consumes → Delta tables; Connect sink/source connectors move data in/out.

The key insight for you: **there is nothing to "run" locally.** The pipeline's job is to get YAML + images onto the cluster; the operator does the rest. Debugging = `kubectl get/describe` the CRs + operator logs, not reading a program's control flow.

## 5. What maps from your past experience (you know more than it feels)

- **Consumer side = already yours:** ADB Structured Streaming reading a topic → Delta is exactly your `databricks-streaming-pattern` / SCB Spark work. Only the *producer/broker infra* is new.
- **Config-driven mindset = yours:** SCB was config-table-driven; this is CRD-YAML-driven. Same philosophy — declare intent, a runtime enforces it. You already think this way.
- **New muscle to build:** Kubernetes basics (pods, StatefulSet, Service, PVC, namespace, `kubectl`), the Strimzi CRD model, and Kafka broker/topic/partition/consumer-group fundamentals.

## 6. Self-check checklist — read the YAML you *can* see and confirm

Ask/look for these to lock down the architecture (you don't need to share anything):
- **Operator?** `apiVersion: kafka.strimzi.io/v1beta2` + `kind: Kafka` → **Strimzi**. `apiVersion: platform.confluent.io/...` → **Confluent for Kubernetes** instead.
- **KRaft or ZooKeeper?** presence of `KafkaNodePool` + `strimzi.io/kraft: enabled` → KRaft (no ZooKeeper).
- **Topics:** `kind: KafkaTopic` — note `partitions`, `replicas`, `retention.ms`.
- **Auth/security:** listeners with `tls` + `authentication` type (`scram-sha-512` / `tls`/mTLS); `KafkaUser` + ACLs.
- **Connectors:** `kind: KafkaConnector` → the `spec.class` (Debezium? JDBC sink? ADLS/Blob sink?) and `spec.config.topics` tell you each pipeline's job.
- **CI:** `azure-pipelines.yml` stages → look for `docker build`/`push` to ACR, and `kubectl apply`/`helm upgrade` to AKS; environment overlays (kustomize `overlays/dev|uat|prod` or Helm `values-*.yaml`).
- **Schema:** any Schema Registry reference (Confluent/Apicurio) + converters (`AvroConverter`) → events are schema'd, not raw JSON.

## 7. Open questions to ask the team (fill the gaps)
- Which operator + version (Strimzi vs Confluent)? KRaft or ZooKeeper?
- Who produces to the topics — app services, or Connect source/CDC connectors?
- Is Databricks the only consumer, or do sink connectors also land data?
- Schema Registry in use? Avro/JSON? compatibility policy?
- Env promotion: how does a change go dev → uat → prod? Who approves?
- What's *my* first task — maintain a connector, add a topic, or something on the build/CI side?

---
## 8. Connector layer — CONFIRMED detail + your likely day-to-day

From `dtp_kafka_connector` screenshots (Bitbucket org `aia-th`):

**Organization = env × Strimzi-version:** folders `connector-{dev,uat,prod,dr}-main{,0.38,0.45,0.49.1}`. The trailing `0.38/0.45/0.49.1` = the Strimzi/cluster version the connectors are built against (must match the operator version deployed). `-dr` = a **Disaster-Recovery** mirror of prod (DR is first-class — every prod connector has a dr twin; commits like "create bbl360sql on prod dr").

**One YAML = one `KafkaConnector` = one source system.** Inside e.g. `connector-prod-main0.45/` there is `<system>-connector.yaml` (+ a `-n.yaml` variant) per source: `cmic` (Oracle, the biggest ~5.7KB), `bbl360`/`bbl360sql` (SQL Server), `autopay`, `ams`, `appsub` (smartclaim), `aiaone`/`aiaonedp`/`aiaonelmsdp`, `aa`, `cmac`. These are AIA source systems captured via **Debezium CDC** into topics.

**Anatomy of a connector YAML** (Strimzi `KafkaConnector` wrapping Debezium):
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaConnector
metadata:
  name: <system>-connector
  labels:
    strimzi.io/cluster: <the KafkaConnect cluster name>   # binds it to a Connect runtime
spec:
  class: io.debezium.connector.{oracle|sqlserver|postgres}.…Connector
  tasksMax: N
  config:
    database.hostname / port / user / password: …          # source DB
    database.dbname / database.names: …
    topic.prefix (or database.server.name): …              # → topic naming
    table.include.list: SCHEMA.TBL_A, SCHEMA.TBL_B, …      # ← WHICH TABLES are captured
    snapshot.mode: …                                        # initial load behaviour
    key.converter / value.converter: …                     # Avro/JSON (+ schema registry)
    transforms: …                                           # SMTs (routing, unwrap, etc.)
```
The single most-edited field is **`table.include.list`** — that's what most commits ("add new tbl efhc / prs / aamn ams") change.

**Your likely day-to-day (from the commit history):**
1. **Onboard a new table into CDC** — add it to `table.include.list` (+ any topic/transform), in the right env file (`connector-uat-main0.49.1` first).
2. **Rebuild/redeploy the connector** via the Jenkins pipeline (`.jenkins/` in the repo) → applies the `KafkaConnector` CR to AKS → Strimzi reconciles it into the running Connect cluster.
3. **Promote across envs**: dev → uat → prod **and** prod-dr (keep the dr twin in sync).
4. **Version migrations** — e.g. "prepare for sf360 migration", moving connectors onto a new cluster version (0.45 → 0.49.1); this is the migrate/re-platform work.
5. **Operational fixes** — "restart strimzi operator", "delete all connector on cluster 1.24", "update admin message.max.bytes".

So your real job ≈ **own the CDC connectors**: onboard tables, keep dev/uat/prod/dr in sync, and carry connectors through Strimzi version migrations — all as YAML through Jenkins onto AKS.

---
*Learning doc — Strimzi + Debezium-CDC + Jenkins/ACR/AKS all CONFIRMED from git (2026-07-01). Refine connector-config specifics once a full YAML is readable.*
