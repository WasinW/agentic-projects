# AIA Kafka Platform — Repo Navigation & Deployment (confusion-buster)

> Answers Wasin's checklist: the folders are messy, there's no clean "main", versions are everywhere — so *what is live, how does it deploy, how is Kafka actually created, and is AKS infrastructure or code?* Companion to `event-processing-kafka-aks.md`.

## ★ The one concept to unblock everything: AKS = infrastructure, not a program

You are NOT looking at a program that "builds Kafka" step by step. You are looking at **declarative config**. Here is the honest mental model:

| Layer | What it is | Analogy |
|---|---|---|
| **AKS (Azure Kubernetes Service)** | **Managed infrastructure** — a ready-made Kubernetes cluster Azure runs for you (a pool of VMs + the k8s control plane). Closest to **PaaS**, not IaaS-you-configure and NOT your code. | The "electric grid" — you don't build it, you plug into it. |
| **Kubernetes (k8s)** | The **orchestrator** running on AKS. You hand it **YAML describing desired state**; it schedules **containers (pods)** onto nodes and keeps them alive. | A "robot foreman": you give it a blueprint, it builds & maintains. |
| **Strimzi operator** | A **controller program that runs *inside* k8s** and understands Kafka. You give it `Kafka` / `KafkaConnector` YAML; it creates the real broker/connect pods. | A "Kafka specialist robot" the foreman calls in. |
| **The repos (YAML)** | The **blueprints** — desired state in git. No imperative logic. | The blueprint drawings. |

So your instinct is **correct**: *"k8s runs to create the Kafka cluster instances."* Precisely: **YAML (git) → Kubernetes + Strimzi operator (the running 'code') → real Kafka pods on AKS nodes.** The reason you can't find "the program that builds Kafka" is that **there isn't one** — the YAML is the input and the *operator* (which someone else wrote, shipped as an image) is the engine. That's the whole point of the operator pattern: replace deploy scripts with declarative desired-state + a reconciler.

There are only **two kinds of "run" here**:
1. **Install the engine once** — deploy the Strimzi **operator** into the cluster (`dtp_kafka_cluster/install/<ver>/...`). After that it watches for CRDs forever.
2. **Declare what you want** — apply a `Kafka` CR (→ operator builds brokers) or a `KafkaConnector` CR (→ operator starts a CDC connector). Editing a topic/table = editing YAML + re-apply; the operator does the rest.

## How Kafka is actually created (the sequence)
1. **CI builds images** (`dtp_kafka_build_ci`, Jenkins) → push to **ACR**: the custom Connect image, bridge, grafana, and the reference to the Strimzi operator version.
2. **Install the operator** (`dtp_kafka_cluster/install/<ver>/{cluster,topic,user}-operator` + `drain-cleaner`) into the AKS namespace → the operator pod starts and watches for Kafka CRDs.
3. **Apply the `Kafka` cluster CR** (in `dtp_kafka_cluster`) → the **cluster-operator** creates a **StatefulSet of Kafka broker pods** + storage (PVC on Azure Disk) + services + certs. **That** is "Kafka being created" — no VM install, no `kafka-server-start.sh`; the operator does it from the CR.
4. **Apply `KafkaConnect`** (the Connect runtime) + **`KafkaConnector`** CRs (`dtp_kafka_connector`) → Debezium CDC connectors start pulling from the source DBs into topics.
5. **Consumers** (Azure Databricks) read the topics → Delta.

## Where the "deploy scripts" live (there's no monolithic one)
Deployment = **Jenkins pipelines** that run `docker build/push` (to ACR) and `kubectl apply` / `helm` (to AKS). Look here:
- `dtp_kafka_build_ci/` → **Jenkinsfiles** (`Jenkinsfile-0.20.1`, `...-connect_2.60`, etc.) + Dockerfiles per image (`kafka-connect/Dockerfile-connect-strimzi-2.8.0`, `kafka-bridge/`, `grafana/Dockerfile`).
- `dtp_kafka_cluster/jenkins/` → per-env CD pipelines (`jenkins-cd-dev`, `jenkins-cd-dev-0.35.0-datazone`, ...) + `install/*.sh` helpers (`get_crt.sh`, cert scripts).
- `dtp_kafka_connector/.jenkins/` → the connector deploy pipeline.
The pipeline is the "deployment script"; the YAML it applies is the "what". There is no bash that imperatively installs Kafka.

## How to find "what is LIVE / what is main" in the mess

The repos accumulated **env × version folders as a substitute for branches/environments** — that's why it looks chaotic (`connector-prod-main`, `connector-prod-main0.45`, `connector-uat-main0.49.1`, `install/0.38`, `install/0.49.1`, `version/0.35`...). Heuristic to cut through it:

1. **Version = the number suffix.** `0.38 / 0.45 / 0.49.1` = the **Strimzi operator/cluster version**. The **highest number that also appears in recent commits** is the one being migrated TO. (You saw `0.49.1` + "prepare for sf360 migration" 10 hours ago → that's the active target.)
2. **"main" = the `*-main<version>` folder for the target env.** For connectors, **`connector-prod-main<latest>`** is production's live set; `connector-uat-main<latest>` is UAT's. Non-`main` and `_old`/`-del` folders are history/scratch — ignore for "what's live".
3. **The README wins ties.** `dtp_kafka_build_ci/README` "Images Release version" lists the *currently released* image versions (Kafka, Connect, bridge, Debezium). Trust it over folder guesses.
4. **The Jenkins CD job is the tiebreaker of truth.** Whatever folder/branch the prod CD pipeline is *parameterized to apply* is, by definition, what's live. Ask which Jenkins job deploys prod and what it points at.
5. **`-dr` = disaster-recovery mirror**, not a different system — keep it in sync with prod.

If you remember one rule: **live prod ≈ `connector-prod-main<highest-version>` + the versions in the build README + whatever the prod Jenkins CD job applies.** Everything else is history.

## Per-repo: what it is / how it deploys / what the deploy does
| Repo | What it holds | Deploys via | The deploy does |
|---|---|---|---|
| `dtp_kafka_build_ci` | Dockerfiles + Jenkinsfiles + operator versions + release README | Jenkins build jobs | `docker build` custom images → **push ACR** (prod/non-prod) |
| `dtp_kafka_cluster` | Strimzi operator install manifests + `Kafka` CR + certs + Grafana + per-env CD | `jenkins-cd-<env>` | `kubectl/helm apply` operator + `Kafka` CR → operator **creates broker pods** on AKS |
| `dtp_kafka_connector` | `KafkaConnector` CDC YAMLs per source system, per env×version | `.jenkins/` pipeline | `kubectl apply` connector CRs → operator **starts Debezium connectors** |

## Questions to confirm with the team (turns hypothesis → fact fast)
- Which Jenkins jobs are the **real prod CD** for each repo, and which folder/branch do they apply?
- Current live **Strimzi version** in prod? (confirm 0.49.1 is target vs deployed)
- Is deploy **`kubectl apply` or `helm`**? Is there GitOps (ArgoCD/Flux) or is it Jenkins-push only?
- How is the **`Kafka` cluster CR** structured (brokers, KRaft vs ZooKeeper, storage)? — I haven't seen it yet.
- What's the promotion + approval flow dev→uat→prod→dr?
- What's the **`sf360` migration** actually moving (system? cluster version? both)?

---
## 9. How the 3 repos chain together (dependency, not confusion)

```
   dtp_kafka_build_ci  ──builds Docker images──►  ACR (image registry)
        (image factory; deploys nothing)              │  cluster & connector reference image tags from here
                                                       ▼
 ① dtp_kafka_cluster   ──Jenkins deploy──►  Strimzi operator installed  +  Kafka brokers created
                                             (+ likely the KafkaConnect runtime)
                                                       │
                                                       ▼
 ② dtp_kafka_connector ──Jenkins deploy──►  KafkaConnector (Debezium CDC) CRs onto the running Connect runtime
```
- **build_ci is NOT wired directly to the others** — the link is the **image tag in ACR** that the cluster/connector YAML references. build_ci = binaries; cluster/connector = desired-state that consumes those binaries.
- **Order = cluster first, connector second.** Deploy `dtp_kafka_cluster` → operator + brokers exist. Then deploy `dtp_kafka_connector` → connectors attach to the already-running Connect runtime. (Wasin's guessed flow was correct.)
- **Open item:** the `KafkaConnect` *runtime* CR appears to live in the **connector** repo's `connect/` folder ("add create cmic Kafka connect cluster"), not the cluster repo — confirm.

## 10. Strimzi resource kinds (enumerate by `kind:`, don't trace call-flow)

| `kind:` | Creates | Repo |
|---|---|---|
| `Kafka` | the cluster (brokers, ZooKeeper/KRaft, listeners, storage) — the main CR | dtp_kafka_cluster |
| `KafkaTopic` | one topic (partitions, replicas, retention) | dtp_kafka_cluster |
| `KafkaUser` | a user + ACLs + credentials | dtp_kafka_cluster |
| `KafkaConnect` | the Connect runtime (hosts connectors) | connector (`connect/`) |
| `KafkaConnector` | one Debezium CDC connector | dtp_kafka_connector |
| `KafkaBridge` | HTTP↔Kafka bridge | build_ci/cluster |
| `KafkaMirrorMaker2` / `KafkaRebalance` | cross-cluster mirror (DR) / rebalance | if present |
| `ServiceAccount`/`Role`/`ClusterRole`/`RoleBinding`/`CRD`/`Deployment` | the OPERATOR install (not Kafka itself) | dtp_kafka_cluster `install/` |

**Reading strategy:** open files and group by their `kind:` line — you don't trace an imperative flow, you inventory declarative objects.

## 11. Finding the `Kafka` cluster CR (still unseen)
It's a file whose body starts `kind: Kafka` (not KafkaTopic/KafkaConnect), in `dtp_kafka_cluster`. Fastest: **Bitbucket code-search the repo for `kind: Kafka`**. Otherwise open `dev/`, `datazone/`, or `examples/`. Screenshot: (1) that folder's listing, (2) the `kind: Kafka` file contents (brokers/storage/listeners/KRaft-or-ZooKeeper), (3) a `KafkaTopic` file or two. Note: the `install/` manifests you already shared are the *operator install*, not the cluster CR — that's why the cluster CR is still missing.

---
*Confusion-buster — architecture CONFIRMED from git (2026-07-01) except: the `Kafka` cluster CR internals, and whether the `KafkaConnect` runtime lives in the connector repo's `connect/` — both to confirm.*
