# Kafka Streaming Expert — Comprehensive Knowledge

> Deep reference for the kafka-streaming-expert subagent. The **event-ingestion / streaming-transport layer**: sources → CDC/producers → **Kafka** (run on Kubernetes via the **Strimzi** operator) → topics → a downstream consumer (typically Spark Structured Streaming, which is the databricks-expert's territory). This doc is version-aware but evergreen; engagement-specific detail (repos, exact versions) lives in the `kafka-strimzi-cdc` skill.

---

## 1. Foundations

### Kafka in one paragraph
Kafka is a distributed, partitioned, replicated **commit log**. Producers append records to **topics**; each topic is split into **partitions** (the unit of parallelism + ordering — order is guaranteed *within* a partition only). Records are retained by time/size, not deleted on read, so many independent **consumer groups** can read the same topic at their own pace. Each consumer group tracks its position via **offsets** (stored in the internal `__consumer_offsets` topic). Brokers replicate each partition `replication.factor` times; `min.insync.replicas` + `acks=all` define the durability contract.

### The core objects and their knobs
| Object | What it is | Key knobs |
|---|---|---|
| **Topic** | Named log | `partitions` (↑ only, never ↓), `replication.factor`, `retention.ms/bytes`, `cleanup.policy` (`delete` vs `compact`) |
| **Partition** | Ordered shard of a topic | Assigned to one broker as leader + N followers; the unit of consumer parallelism |
| **Producer** | Writes records | `acks` (0/1/all), `enable.idempotence`, partitioner (key → partition), batching/linger |
| **Consumer group** | Set of consumers sharing a topic's partitions | `group.id`, one partition → one consumer in the group; rebalance on membership change |
| **Offset** | A consumer's position in a partition | Committed to `__consumer_offsets`; earliest/latest reset policy |
| **Broker / controller** | The server process | In **KRaft** the controllers own metadata (no ZooKeeper); in legacy mode ZooKeeper does |

### Delivery semantics
- **At-most-once** — commit offset before processing; a crash loses records.
- **At-least-once** (the default you design around) — process then commit; a crash re-delivers → **consumers must be idempotent**.
- **Exactly-once (EOS)** — Kafka's transactional producer + `read_committed` consumer + `transaction.state.log.*` gives EOS *within Kafka*. Requires idempotent producer + transactions; costs latency. For a Spark→Delta sink, EOS is achieved on the consumer side (checkpoint + idempotent MERGE) — that's the databricks-expert's layer, not Kafka's transaction API.

### Consumer lag — the health metric that matters
Lag = latest offset − committed offset per partition, per group. Rising lag = the consumer can't keep up (or is down). This is the single most important operational signal for a streaming platform; expose it via **Kafka Exporter → Prometheus → Grafana** and alert on it.

---

## 2. Kafka-on-Kubernetes: the Strimzi model

### The one idea
Kafka here does **not** run on VMs you SSH into. It runs on Kubernetes, managed **declaratively by an operator**. You don't write code that "starts Kafka" — you write **YAML that DESCRIBES the Kafka you want** (how many brokers, which topics, which connectors), and the **Strimzi operator** running inside the cluster continuously reconciles reality to that description and re-heals drift.

> Mental model: **YAML (git) → CI applies it → operator reconciles → running Kafka.** There is no imperative `main()`. This is GitOps / declarative infrastructure. Debugging = `kubectl get/describe` the CRs + operator logs, *not* tracing a program's control flow.

Strimzi registers **Custom Resource Definitions (CRDs)** — new Kubernetes kinds — so you manage Kafka with `kubectl apply` like any Deployment. The CRD apiVersion in current Strimzi is **`kafka.strimzi.io/v1beta2`**.

### The custom resources (kinds you'll touch)
| Kind | Declares | Runs as |
|---|---|---|
| `Kafka` | The broker cluster: replicas, storage (PVC), listeners (TLS/auth), config, KRaft-vs-ZooKeeper | StatefulSet / StrimziPodSet of broker pods |
| `KafkaNodePool` | (KRaft) a group of nodes with `roles: [broker]`/`[controller]`/both + replicas + storage | part of the broker workload |
| `KafkaConnect` | The Connect **runtime** — a cluster of stateless worker pods that host connectors; which image/plugins | Deployment |
| `KafkaConnector` | **One connector** (a Debezium source, or a sink) — `class`, `tasksMax`, `config` | a task inside the Connect runtime |
| `KafkaTopic` | A topic — partitions, replicas, retention, cleanup policy | reconciled by the Topic Operator |
| `KafkaUser` | A principal + ACLs — materialized into a Kafka user **and a K8s Secret** (cert or password) | reconciled by the User Operator |
| `KafkaBridge` | HTTP ↔ Kafka REST proxy | Deployment |

### Typical topology on one cluster
- **Strimzi Cluster Operator** (1 deployment) — watches all the CRs above, reconciles them.
- **Kafka broker cluster** (`kind: Kafka`) — StatefulSet + PVCs.
- **Entity Operator** — bundles the Topic Operator + User Operator (only present if you want `KafkaTopic`/`KafkaUser`).
- **Kafka Connect cluster** (`kind: KafkaConnect`) — Deployment of worker pods; **Debezium ships as JAR plugins baked into the Connect image**, not as its own pod.

### Two annotations that trip people up
- `strimzi.io/use-connector-resources: "true"` on the `KafkaConnect` CR — **without it, your `KafkaConnector` CRs are ignored** (the runtime would expect the REST API instead).
- `strimzi.io/node-pools: enabled` / `strimzi.io/kraft: enabled` on the `Kafka` CR — switch on KafkaNodePool + KRaft mode.

---

## 3. Debezium CDC — the producer side

### What Debezium is
Debezium is a set of **Kafka Connect source connectors** that tail a database's transaction log (Oracle redo/LogMiner, SQL Server CDC change tables, Postgres WAL, MySQL binlog) and emit each row change as a Kafka record. It runs **inside the Connect runtime** as a plugin — it is not a separate service. One `KafkaConnector` CR = one source system.

### Snapshot modes (know this before you deploy — it's a cost decision)
| `snapshot.mode` | Behaviour |
|---|---|
| `initial` | Snapshot the whole table set once, then stream changes. **Re-reads entire tables on first run — heavy on large Oracle tables.** |
| `schema_only` | Capture schema only, stream from now — no historical data. |
| `initial_only` | Snapshot then stop (no streaming). |
| `never` | Stream from the current log position, assume schema known. |

### State that persists (and that you can destroy)
- **Connector offsets** live in the Connect **`offset.storage.topic`** (internal). Reusing the **same connector name** resumes from the stored offset; deploying under a **new name re-snapshots** from scratch.
- **Schema-history topic** (per connector) records source DDL so Debezium can decode old log entries. It **must exist and persist** — lose it and the connector breaks.
- These internal topics (`config.storage.topic`, `offset.storage.topic`, `status.storage.topic`) belong to the **Connect runtime**, replicated `*.storage.replication.factor` times.

### Source-DB prerequisites (CDC captures nothing without these)
- **Oracle:** archivelog mode ON; `ALTER DATABASE ADD SUPPLEMENTAL LOG DATA;` (+ per captured table); LogMiner privileges for the CDC user. `logminer` is the 1.9 default adapter (XStream is the licensed alternative).
- **SQL Server:** SQL Server **Agent running**; `sys.sp_cdc_enable_db` at the DB; `sys.sp_cdc_enable_table` per table. Debezium reads the SQL Server CDC change tables.
- **Postgres:** logical replication (`wal_level=logical`) + a replication slot + publication.

### Debezium 1.9.x vs 2.x — the renames that bite
Several config keys were renamed in Debezium 2.x. On a **1.9.x** platform use the **left column**:

| Concept | 1.9.x (use on 1.9) | 2.x |
|---|---|---|
| Topic prefix / logical name | `database.server.name` | `topic.prefix` |
| Schema-history brokers | `database.history.kafka.bootstrap.servers` | `schema.history.internal.kafka.bootstrap.servers` |
| Schema-history topic | `database.history.kafka.topic` | `schema.history.internal.kafka.topic` |

Also **2.x/3.x-only** features you can't use on 1.9: ROWID incremental-snapshot chunking, the drop-transaction signal. Always confirm the running Debezium version before reaching for a feature.

### Single Message Transforms (SMT)
Applied per record inside Connect. The most common with Debezium:
- **`io.debezium.transforms.ExtractNewRecordState`** ("unwrap") — flatten the CDC envelope (`before`/`after`/`op`/`source`) down to just the new row state. Decide deliberately: unwrapping loses the operation type + tombstones unless configured to keep them.
- **`RegexRouter`** — rewrite topic names (`transforms.route.regex` + `.replacement`).

---

## 4. Connector & CR YAML anatomy

> Version-correct templates (Strimzi `v1beta2`, Debezium 1.9.x). Placeholders throughout — **confirm against the live cluster before applying.**

### `KafkaConnector` — Debezium Oracle
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaConnector
metadata:
  name: <system>-connector
  labels:
    strimzi.io/cluster: <the KafkaConnect runtime name>   # MUST match the KafkaConnect CR
spec:
  class: io.debezium.connector.oracle.OracleConnector
  tasksMax: 1                                             # Oracle Debezium = 1 task (single log reader)
  config:
    database.hostname: <host>
    database.port: "1521"
    database.user: <cdc_user>
    database.password: "${secrets:...}"                  # via K8s Secret / KafkaUser, never inline
    database.dbname: <CDB_or_SID>
    database.pdb.name: <PDB>                              # only for CDB/PDB (multitenant)
    database.connection.adapter: logminer                # 1.9 default; XStream is the alt
    database.server.name: <server>                       # 1.9 key → topics become <server>.<schema>.<table>
    database.history.kafka.bootstrap.servers: <kafka-bootstrap>:9092   # 1.9 key
    database.history.kafka.topic: schema-history.<server>              # 1.9 key; must persist
    table.include.list: SCHEMA.TABLE_A,SCHEMA.TABLE_B    # the most-edited field
    snapshot.mode: initial
    key.converter: io.confluent.connect.avro.AvroConverter    # or JsonConverter
    value.converter: io.confluent.connect.avro.AvroConverter
    transforms: unwrap
    transforms.unwrap.type: io.debezium.transforms.ExtractNewRecordState
```
SQL Server is the same shape with `class: io.debezium.connector.sqlserver.SqlServerConnector`, port `1433`, and `database.names: <DB1>,<DB2>` (1.9 supports multi-DB; older single-DB used `database.dbname`).

### `KafkaConnect` — the runtime that HOSTS connectors
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaConnect
metadata:
  name: <connect-cluster>
  annotations:
    strimzi.io/use-connector-resources: "true"           # REQUIRED — lets KafkaConnector CRs drive it
spec:
  version: 3.7.0                                          # Kafka version (matches image)
  replicas: 2                                             # worker pods (stateless Deployment)
  bootstrapServers: <kafka-bootstrap>:9093
  image: <registry>/strimzi-kafka-connect:<ver>-debezium<dbz>  # custom image w/ Debezium plugins baked in
  config:
    group.id: <connect-group>
    config.storage.topic: connect-configs                # Connect's internal state topics
    offset.storage.topic: connect-offsets                # ← connector offsets live here
    status.storage.topic: connect-status
    config.storage.replication.factor: 3
    offset.storage.replication.factor: 3
    status.storage.replication.factor: 3
  tls: { trustedCertificates: [...] }                    # talk to brokers over TLS
```
One Connect cluster hosts many connectors. If Strimzi should build the image itself, use `spec.build` (`output` + `plugins[].artifacts[]`) instead of a prebuilt `image`.

### `Kafka` — the broker cluster (abridged)
```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata: { name: <cluster> }
spec:
  kafka:
    replicas: 3
    listeners:
      - { name: tls, port: 9093, type: internal, tls: true, authentication: { type: tls } }
    storage: { type: persistent-claim, size: 100Gi, class: managed-premium }   # cloud disk PVC
    config: { offsets.topic.replication.factor: 3, default.replication.factor: 3, min.insync.replicas: 2 }
  # zookeeper: { replicas: 3, ... }    # legacy ZK mode; OR use KafkaNodePool + strimzi.io/kraft: enabled
  entityOperator: { topicOperator: {}, userOperator: {} }
```

### `KafkaTopic` + `KafkaUser`
```yaml
kind: KafkaTopic
spec: { partitions: 12, replicas: 3, config: { retention.ms: "604800000", cleanup.policy: delete } }
---
kind: KafkaUser
spec:
  authentication: { type: scram-sha-512 }                # or tls (mTLS)
  authorization:
    type: simple
    acls:
      - { resource: { type: topic, name: "<prefix>.", patternType: prefix }, operations: [Read, Describe] }
      - { resource: { type: group, name: <consumer-group> }, operations: [Read] }
```
The User Operator turns a `KafkaUser` into a Kafka principal **and a K8s Secret** holding the cert (mTLS) or password (SCRAM) that the consumer (e.g. a Databricks reader) mounts to authenticate.

### Field cheat-sheet — what changes when
| You want to… | Change |
|---|---|
| capture more tables | `table.include.list` (schema-qualified, exact case) |
| rename topics | `transforms` / RegexRouter, or the `database.server.name` prefix |
| avoid a full re-snapshot | `snapshot.mode: schema_only` (only if losing history is acceptable) |
| point at a different DB | `database.hostname/port/dbname/names` |
| change parallelism | `tasksMax` (**Oracle stays 1**) |
| flatten the CDC envelope | `transforms.unwrap` (ExtractNewRecordState) |
| move to a new cluster version | rebuild in the new version's folder, match the Connect `image` tag |

---

## 5. kubectl — the commands a streaming DE actually uses

> Read-only inspection first. `NS=<namespace>`. Rule: **`get` → `describe` → logs**; change via repo + CI, not ad-hoc `apply`, unless firefighting.

```bash
# Orient
kubectl config get-contexts                        # which cluster am I on
kubectl get ns
kubectl get crds | grep strimzi                    # proves Strimzi + which kinds exist
kubectl api-resources | grep strimzi               # short names: kafka, kt, ku, kc, kctr

# The custom resources (READY status = the first thing to check)
kubectl get kafka,kafkaconnect -n $NS
kubectl get kafkatopic,kafkauser -n $NS
kubectl get kafkaconnector -n $NS                  # Debezium connectors + READY / TASKS
kubectl describe kafkaconnector <name> -n $NS      # desired vs actual + last error (the reconcile story)
kubectl get kafkaconnector <name> -n $NS -o yaml   # read a live spec (read-only)

# Pods / storage / secrets
kubectl get pods -n $NS -o wide                    # brokers, connect workers, operators
kubectl get statefulset,pvc -n $NS                 # broker workload + storage
kubectl get secret -n $NS | grep -Ei 'kafka|user'  # creds the User Operator generated

# Logs (where reconcile + connector errors surface)
kubectl logs deploy/strimzi-cluster-operator -n $NS --tail=300      # operator: reconcile errors for ANY CR
kubectl logs deploy/<cluster>-entity-operator -c topic-operator -n $NS
kubectl logs <connect-pod> -n $NS | grep -iE 'debezium|snapshot|ERROR'
kubectl get events -n $NS --sort-by=.lastTimestamp | tail -30

# Connector state via the Connect REST API (from inside a Connect pod)
kubectl exec -it <connect-pod> -n $NS -- bash
curl -s localhost:8083/connectors | jq
curl -s localhost:8083/connectors/<name>/status | jq          # state + per-task state + stack traces
curl -s localhost:8083/connector-plugins | jq                 # which plugins are baked in
curl -s -X POST localhost:8083/connectors/<name>/restart?includeTasks=true

# Topics / lag (from inside a broker pod)
kubectl exec -it <cluster>-kafka-0 -n $NS -- bash
bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic <topic>
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group <group>   # LAG

# Write ops (only when authorized; normally CI does this)
kubectl annotate kafkaconnector <name> strimzi.io/restart="true" -n $NS       # operator-safe restart
kubectl rollout restart statefulset/<cluster>-kafka -n $NS                     # rolling broker restart (careful)
```
Prefer the **operator restart annotation** over deleting pods — it respects Strimzi's safe-rolling logic (leadership migration, drain-cleaner). Real listeners use TLS/SCRAM, so console tools need a `--command-config` properties file built from the `KafkaUser` Secret.

---

## 6. Operational playbooks

### Add a new table to an existing connector (the most common task)
1. Find the connector file in the **correct env + Strimzi-version** folder (start with UAT/latest).
2. Add the table to **`table.include.list`** (schema-qualified, exact case). **Confirm the source DB side is CDC-ready** for that table (SQL Server: `sp_cdc_enable_table`; Oracle: supplemental logging) — else nothing is captured.
3. Decide topic naming — usually auto `<server-name>.<schema>.<table>`; check any RegexRouter and whether a `KafkaTopic` CR must be pre-created (partitions/retention).
4. Commit → run the CI pipeline for UAT → it `kubectl apply`s the `KafkaConnector` CR.
5. Verify: `describe` = READY, no failed tasks; topic exists; messages flow; the downstream consumer picks it up.
6. **Promote:** dev → uat → prod **and** prod-dr — keep the `-dr` twin identical.

### Onboard a brand-new source system
1. Confirm source DB type + CDC prerequisites met.
2. Confirm the Connect **image** already bundles that Debezium plugin. New plugin needed → that's an image rebuild (CI/ACR) first.
3. Clone an existing connector of the same DB type; change name, `database.*`, `database.server.name` (→ topic prefix), `table.include.list`, schema-history topic, credentials (Secret/`KafkaUser`).
4. Pre-create supporting `KafkaTopic`s if the platform requires explicit topic CRs.
5. Deploy dev → uat → prod → prod-dr; verify each hop.

### Stand up a new Kafka cluster from zero
1. **Images:** ensure operator + Connect images for the target version exist in the registry.
2. **Operator:** apply cluster-operator (registers CRDs), then topic-operator, user-operator, drain-cleaner.
3. **Broker cluster:** apply `kind: Kafka` — replicas, storage, listeners (TLS+auth), KRaft-vs-ZooKeeper, resources.
4. **Topics/Users:** apply `KafkaTopic` + `KafkaUser` (incl. a consumer user with Read ACLs).
5. **Connect runtime:** apply `kind: KafkaConnect` (image with Debezium plugins).
6. **Connectors:** apply `KafkaConnector` CRs.
7. **Consumers/monitoring:** point the consumer at the topics; confirm Grafana/Kafka-Exporter dashboards.
8. Do it in dev/sandbox first, then uat/prod/dr; verify every step with `get`/`describe`.

### Strimzi version migration
1. Read the target release notes for **breaking CRD/API changes** (v1beta2 fields, KRaft defaults, **topic-operator mode**).
2. Build/push new operator + Connect images.
3. Upgrade the **operator first**, let it reconcile the `Kafka` CR; watch operator logs.
4. Rebuild connectors against the new version folder; apply per env.
5. Migrate uat → prod → prod-dr, verifying connector READY + no data gap at each hop. **Keep the old version deployable for rollback.**

### DLQ + replay
- Connect can route un-deserializable/failed records to a **dead-letter-queue topic** (`errors.tolerance: all` + `errors.deadletterqueue.topic.name`). Replay = re-consume the DLQ after fixing the schema/mapping, or reset the consumer group's offsets.
- Because Kafka retains records, "replay" a downstream consumer by resetting its group offsets (`kafka-consumer-groups.sh --reset-offsets`) rather than re-snapshotting the source.

### KRaft migration states (read from `status.kafkaMetadataState`)
`ZooKeeper → KRaftMigration → KRaftDualWriting → KRaftPostMigration` (**last rollback-safe state**) `→ PreKRaft → KRaft`. Driven by the `strimzi.io/kraft` annotation (`migration` advances to the rollback point; `enabled` finalizes — no rollback after).

---

## 7. Common failure modes
| Symptom | Likely cause |
|---|---|
| `KafkaConnector` CR applied but nothing happens | `strimzi.io/use-connector-resources: "true"` missing on the `KafkaConnect` CR |
| Connector READY but no records for a table | table not CDC-enabled at the source DB, or wrong case/schema in `table.include.list` |
| Connector fails on restart with schema-decode errors | schema-history topic lost/deleted |
| A redeploy re-snapshots a huge table unexpectedly | connector **name changed** → offsets not found → fresh snapshot |
| `database.server.name`/history keys rejected | you used 2.x keys on a 1.9 platform (or vice-versa) |
| Rising consumer lag | consumer down or under-provisioned; too few partitions to parallelize; a slow downstream sink |
| Duplicate rows downstream | at-least-once redelivery on restart — the consumer isn't idempotent (fix on the consumer side) |
| Wrong-named topic silently created | `auto.create.topics.enable=true` + a typo in the prefix/route — no `KafkaTopic` source-of-truth |
| Prod fine, DR broken | DR twin drift — a prod connector change never landed in `-dr` |
| Topic partition count won't decrease | partitions are increase-only by design; plan capacity up front |

---

## 8. Boundaries & handoffs
- **Consumer / lakehouse side → databricks-expert.** Spark Structured Streaming reading a topic → Delta, checkpoint namespacing, trigger modes (availableNow vs processingTime), watermark/stateful ops, and idempotent/exactly-once Delta writes via `foreachBatch` + MERGE all belong to the **databricks-streaming-pattern** skill under databricks-expert. You own up to and including the topic.
- **Cloud + CI plumbing → devops / cloud expert.** AKS/ACR/networking/IAM, the Jenkins pipelines that build images and `kubectl apply`, and TLS/cert management are infra concerns; you own the Kafka/Connect logic they carry.
- **Schema-contract policy across teams → governance-consultant.** You own the *mechanics* — schema registry, converters (Avro/JSON), compatibility modes, evolution — they own the *policy* of who may break a contract.

---

## 9. Engagement caveats (verify before apply)
This role is currently exercised on an **Azure Databricks + Strimzi-on-AKS + Debezium CDC** platform where Kafka feeds Databricks Structured Streaming. Carry these disciplines, but **treat every specific as HYPOTHESIS until confirmed against the live cluster / official docs for the pinned version**:
- **Never assume a config key, CRD field, UI label, or capability** — Debezium and Strimzi rename things across versions; check the docs for the exact running version first. Separate **CONFIRMED (seen in git / docs / by the engagement owner)** from **HYPOTHESIS** in every answer.
- **No code/data export in regulated engagements.** Reason from architecture + screenshots; give the engineer self-check checklists and commands to run themselves, not "paste me your YAML".
- **Debezium 1.9.x is common in the field** and lacks 2.x/3.x features (ROWID incremental snapshot chunking, drop-transaction signal, the renamed keys). Confirm the version before recommending any of those.
- **Auto-created topics are a real anti-pattern to watch for:** no `KafkaTopic` CRs means no git source-of-truth, broker-default partitions/retention, and a typo silently creates a wrong-named topic. Raise it; don't assume topics are declaratively managed.
- **DR is first-class** in enterprise setups — every prod resource may have a `-dr` twin that must stay in sync.

The hands-on, engagement-specific playbook (repo layout, exact versions, dated checklists, connector-YAML reference tables) lives in the **`kafka-strimzi-cdc`** skill. Load it for real work.
