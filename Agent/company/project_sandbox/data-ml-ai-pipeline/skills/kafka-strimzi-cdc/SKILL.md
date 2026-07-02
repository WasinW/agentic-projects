---
name: kafka-strimzi-cdc
description: >-
  Use when สิน works on AIA's Kafka event-processing platform — Strimzi on AKS, Debezium CDC
  connectors, the dtp_kafka_{build_ci,cluster,connector} repos, adding a source/table, promoting
  across dev/uat/prod/dr, a Strimzi version migration, or standing up a new Kafka cluster. Gives the
  mental model, kubectl commands, connector-YAML anatomy (reference/), and step-by-step checklists.
  STARTER — verify keys/versions against AIA's live setup before applying.
---

# Kafka + Strimzi + Debezium CDC on AKS (AIA)

> **STARTER — verify against AIA's live version.** Debezium at AIA = **1.9.7.Final** (1.9.x config keys — 2.x renamed several; noted below). Strimzi versions in play: 0.38 / 0.45 / **0.49.1** (migration target).
> **POLICY:** never paste AIA code into a chat, never generate code claiming to be AIA's. These are generic templates สิน adapts locally. Reason from architecture + screenshots.

## Mental model (10-second recap)
- **AKS** = managed Kubernetes (infrastructure). **Kubernetes** = orchestrator (declarative YAML → pods). **Strimzi operator** = a controller in the cluster that turns `Kafka`/`KafkaConnect`/`KafkaConnector` CRs into real pods and keeps them matching (reconciliation loop). **Debezium** = JAR *plugins* inside the Kafka Connect image (not a pod).
- **3 clusters on one AKS:** Strimzi operator (1 pod) · Kafka **broker** cluster (`kind: Kafka`, StatefulSet+PVC) · Kafka **Connect** cluster (`kind: KafkaConnect`, Deployment, hosts Debezium).
- **Flow:** source DB → Debezium CDC (in Connect) → Kafka topic → Azure Databricks Structured Streaming → Delta.
- Full narrative: `../../knowledge_chat/aia-kafka-event-processing-GUIDE-export.md` + `../../aia/repo-navigation-and-deployment.md`.

## Deep references (read when you need field-level detail)
- **`reference/connector-yaml-anatomy.md`** — `KafkaConnector` (Debezium Oracle + SQL Server, 1.9.x keys), `KafkaConnect` runtime, `KafkaTopic`, `KafkaUser`, converters, transforms — field by field.
- **`reference/kubectl-cheatsheet.md`** — the ~30 kubectl commands a DE needs to inspect/debug this platform.

---

## kubectl — the 12 you'll actually use first (full set in reference/)
```bash
kubectl config get-contexts                       # which cluster am I on
kubectl get ns                                     # namespaces (e.g. 651563-kbdev-cluster)
NS=<namespace>
kubectl get crds | grep strimzi                    # what CRDs exist (proves Strimzi + version)
kubectl get kafka,kafkaconnect -n $NS              # broker + connect clusters
kubectl get kafkatopic,kafkauser -n $NS            # topics + users
kubectl get kafkaconnector -n $NS                  # the Debezium connectors + READY status
kubectl get pods -n $NS                            # brokers, connect workers, operators
kubectl describe kafkaconnector <name> -n $NS      # desired vs actual + last error
kubectl logs deploy/strimzi-cluster-operator -n $NS --tail=200      # operator log (reconcile errors)
kubectl logs <connect-pod> -n $NS | grep -i debezium               # plugins loaded / connector state
kubectl get kafkaconnector <name> -n $NS -o yaml   # read a live connector spec (read-only)
```
Rule: **debug by describing CRs + reading operator/connect logs**, not by tracing code.

---

## Checklist A — add a new TABLE to an existing connector (most common task)
1. Identify the connector file for that source system in the **correct env+version** folder — start `dtp_kafka_connector/connector-uat-main<latest>/<system>-connector.yaml`.
2. Add the table to **`table.include.list`** (schema-qualified, exact case). Confirm the **source DB side is CDC-ready** (SQL Server: table enabled via `sys.sp_cdc_enable_table`; Oracle: supplemental logging on the table) — otherwise Debezium won't capture it.
3. Decide topic naming — usually auto `<server-name>.<schema>.<table>`; check any `transforms`/RegexRouter that rewrites it, and whether a matching `KafkaTopic` CR must be pre-created (partitions/retention).
4. Commit → run the connector **Jenkins** pipeline for UAT → it `kubectl apply`s the `KafkaConnector` CR.
5. Verify: `kubectl describe kafkaconnector <name>` = READY, no failed tasks; confirm the topic exists and messages flow; check the Databricks consumer picks it up.
6. **Promote:** repeat for **prod** AND **prod-dr** (keep the dr twin identical). Follow the exact promotion/approval flow the team uses.

## Checklist B — onboard a brand-NEW source system (new connector)
1. Confirm the source DB type + that **CDC prerequisites** are met (see reference §prereqs): Oracle (archivelog + supplemental logging + LogMiner privs) / SQL Server (SQL Agent + `sp_cdc_enable_db` + per-table).
2. Confirm the **Connect image** already bundles that Debezium plugin (it does for Oracle/SQLServer/Postgres). If a new plugin is needed → that's a `dtp_kafka_build_ci` image change → ACR rebuild first.
3. Create `<system>-connector.yaml` by **cloning an existing connector of the same DB type** and changing: name, `database.*` connection, `database.server.name` (logical name → topic prefix), `table.include.list`, schema-history topic, credentials (via secret/`KafkaUser`).
4. Pre-create supporting `KafkaTopic`s if the platform requires explicit topic CRs (schema-history topic, per-table topics).
5. Deploy dev → uat → prod → prod-dr via Jenkins; verify at each step (Checklist A step 5).

## Checklist C — stand up a NEW Kafka cluster from zero (Goal #1)
1. **Images** (`dtp_kafka_build_ci`): ensure operator + Connect images for the target version exist in ACR (build/push if not).
2. **Operator** (`dtp_kafka_cluster/install/<ver>/`): apply `cluster-operator/` (registers CRDs, starts the operator), then `topic-operator/`, `user-operator/`, `drain-cleaner/`.
3. **Broker cluster:** apply the `kind: Kafka` CR — set replicas, storage (PVC size/class), listeners (TLS + auth), KRaft-vs-ZooKeeper, resources. Operator builds the StatefulSet.
4. **Topics/Users:** apply `KafkaTopic` + `KafkaUser` CRs (incl. a `KafkaUser` for the Databricks consumer with Read ACLs).
5. **Connect runtime:** apply the `kind: KafkaConnect` CR (image from ACR with Debezium plugins) — `dtp_kafka_connector/connect/`.
6. **Connectors:** apply `KafkaConnector` CRs (Checklist B).
7. **Consumers/monitoring:** point Databricks at the topics; confirm Grafana/Kafka-Exporter dashboards.
8. Do it in **dev/sandbox first**; then uat/prod/dr. Verify every step with `kubectl get/describe`.

## Checklist D — Strimzi version migration (e.g. 0.45 → 0.49.1, the "sf360 migration")
1. Read the target Strimzi release notes for **breaking CRD/API changes** (e.g. `v1beta2` fields, KRaft defaults, topic-operator mode) between the two versions.
2. Build/push the new operator + Connect images to ACR (`build_ci`).
3. Upgrade the **operator first** (`install/<newver>/`), then let it reconcile the `Kafka` CR; watch operator logs.
4. Rebuild connectors against the new version folder (`connector-*-main<newver>`); apply per env.
5. Migrate **uat → prod → prod-dr**, verifying connector READY + no data gap at each hop. Keep the old version deployable for rollback.

---

## Gotchas to remember
- **Debezium 1.9.x keys ≠ 2.x** — 1.9 uses `database.server.name` (not `topic.prefix`) and `database.history.kafka.*` (not `schema.history.internal.*`). AIA is on 1.9.7 → use 1.9 keys. (Details in reference.)
- **Snapshot cost:** `snapshot.mode: initial` re-reads the whole table on first run of a new connector — heavy on big Oracle tables. Know the mode before deploying.
- **Schema-history topic** must exist/persist per connector — losing it breaks the connector's schema tracking.
- **Offsets live in Kafka** (Connect's internal topics) — deleting/recreating a connector with the same name resumes from stored offset; a new name re-snapshots.
- **DR twin drift** is the classic incident — every prod connector change must land in `-dr` too.
- **Topic-operator mode** (unidirectional vs bidirectional) changed across Strimzi versions — verify which mode AIA runs before hand-editing topics vs CRs.
