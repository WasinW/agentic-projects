# AIA Kafka — Deploy Mechanics & Topics (session notes, 2026-07-02)

> **For:** สิน (วศิน) — Senior DE @ AIA. Portable notes to paste into the web chat. Companion to `context_20260702.md`, `strimzi_config_20260702.md`, `strimzi_ex_20260702.md`.
> **Policy:** ❌ never ask him to paste AIA code / never generate "AIA code". ✅ reason from architecture + screenshots + public Strimzi/Debezium docs. Company machine is air-gapped (he photographs summarized field lists — that's expected).

## 1. Making a config change (real example: `startupProbe` on Kafka)
An issue asked to add a **`startupProbe`** with `failureThreshold: 30`, `periodSeconds: 60` (= up to 30 min startup window before k8s kills the broker; useful for slow log recovery).

- **Where to edit:** the **`kind: Kafka` instance** (the actual cluster CR, short file with real values) in the **`dtp_kafka_cluster`** repo — under the relevant component (`spec.kafka` for brokers). NOT the CRD (`*-Crd-*.yaml`).
  ```yaml
  spec:
    kafka:
      startupProbe:
        failureThreshold: 30
        periodSeconds: 60
  ```
- **⚠️ Verify first:** the Kafka CRD screenshot showed only `livenessProbe` + `readinessProbe` under `spec.kafka` — **not** `startupProbe`. Before editing, **search the Kafka CRD for `startupProbe`** to confirm the running Strimzi version exposes it. If it's not there, ask the senior how they inject it (Strimzi may not natively support a broker `startupProbe` in that version) — don't apply a field the operator will reject.
- **Deploy path:** edit the CR YAML → PR → run the **cluster repo's Jenkins CD** (correct env: dev → uat → prod, plus prod-dr) → Strimzi operator sees the changed `Kafka` CR → **rolling-restarts the broker pods one at a time** with the new probe.
- Confirmed with the senior: config changes to the Kafka cluster live in the cluster repo and go out via the cluster's Jenkins deploy. ✅

## 2. What the "Jenkins deploy of the cluster" actually does
It takes the YAML in `dtp_kafka_cluster` and `kubectl`/`helm apply`s it to AKS:
1. operator install + CRDs (`install/<ver>/`) — when needed
2. the **`kind: Kafka`** cluster CR (the file you edit)
3. `KafkaUser` CRs (and `KafkaTopic` CRs *if they existed* — but see §3)

After apply, the **Strimzi operator reconciles**: for a probe change it rolls the brokers. So "Jenkins deploy of cluster" = **push desired-state YAML → operator makes it real**. There is no imperative "install Kafka" script.

## 3. Jenkinsfile (in git) ≠ Jenkins server (UI) — important unblock
- The **Jenkinsfile / pipeline script** (`jenkins/jenkins-cd-*`, `Jenkinsfile-*`) is a **file IN the Bitbucket repo** → **readable now**, no Jenkins access needed. Open it to see exactly what the deploy runs (`kubectl apply ...`, any topic handling).
- The **Jenkins server UI** (job runs, which branch is wired to prod, credentials) needs access สิน doesn't have yet.
- Lesson: to understand *how* deploy works, **read the Jenkinsfile in git** — don't wait for Jenkins UI.

## 4. Kafka topics = AUTO-CREATE (confirmed 2026-07-02)
The cluster repo has only `04-Crd-kafkatopic.yaml` (the **CRD** = schema) and **no `kind: KafkaTopic` instance files**. So:
- **Topics are auto-created at runtime** — when a Debezium connector first writes a change event for a table, the broker creates the topic. **Not at deploy time.**
- **Topic name** = `<database.server.name>.<schema>.<table>` (from the connector YAML in `dtp_kafka_connector`).
- **Topic settings** = the **broker defaults** (`num.partitions`, `default.replication.factor`, retention in the `kind: Kafka` `config`), because there's no per-topic `KafkaTopic` CR. Requires `auto.create.topics.enable=true` on the broker.

### What this means for สิน's work
- **Adding a table (Checklist A) needs NO topic creation** — edit `table.include.list` in the connector; the topic appears automatically on first CDC event. (This is why they chose auto-create: Debezium makes one topic per table — too many to hand-write `KafkaTopic` CRs.)

### Gotchas of auto-create
- Every topic gets the **same default** partitions/replication/retention — per-topic tuning needs an explicit `KafkaTopic` CR (they don't use them).
- A typo in the connector config **silently creates a wrongly-named topic** (no error) — verify topic names after deploy.
- **No declarative list of topics in git** → weaker governance/audit (a possible angle for สิน's Goal #2 refactor — but auto-create is simpler, that's the trade-off).

## 5. Full data flow (recap)
```
source DB (Oracle/SQL Server)
   └─ Debezium CDC  (dtp_kafka_connector: KafkaConnect runtime + KafkaConnector)
        └─► Kafka topic  (AUTO-CREATED at runtime; settings = broker defaults; broker in dtp_kafka_cluster)
              └─► Azure Databricks Structured Streaming ─► Delta
Repos:  build = image→ACR   |   connect = Debezium (producer)   |   cluster = broker + config + operator (+ auto-created topics live here)
```

## Still open / next
- Verify `startupProbe` exists in the Kafka CRD (else ask senior).
- Read the cluster Jenkinsfile to confirm the exact apply steps.
- Still unseen: the real `kind: Kafka` instance (replicas/storage/KRaft-vs-ZooKeeper/listeners) and a `KafkaConnect` runtime CR.
