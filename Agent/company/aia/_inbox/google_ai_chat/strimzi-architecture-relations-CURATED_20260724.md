# Strimzi/Kafka component architecture + relations — CURATED

> Reorganized by Claude from the 3-turn Google AI Mode chat. Raw: `strimzi-architecture-relations-FULL_20260724.md`.
> Overlaps the component map I gave in-session; this consolidates + adds the Grafana-alert part.
> Provenance: **[chat]** / **[🧠 Claude]**.

## 1. Component roles [chat — matches my earlier answer]
3 planes on top of Kubernetes:
- **Control:** **Strimzi** (the operator project) + its **Cluster Operator** (= "Cluster Operation")
  — reconciles CRs, deploys/manages everything, rolling-restart, cert, scale.
- **Data:** **Kafka Cluster** (brokers) · **Kafka Connect** (connectors, no-code integration) ·
  **Debezium** (CDC source connectors ON Connect) · **Kafka Bridge** (HTTP/REST ↔ Kafka gateway).
- **Ops/observability:** **Kafka Rebalance** (`KafkaRebalance` CR → **Cruise Control** rebalances
  partitions) · **Prometheus** (scrapes JMX metrics) · **Grafana** (dashboards + alerts).

## 2. Architecture (from chat's ASCII, condensed) [chat]
```
[ K8s / AKS ]
  STRIMZI Cluster Operator ── controls/manages ──> Kafka Cluster, Kafka Connect(+Debezium), Kafka Bridge, Cruise Control
  MONITORING:  Grafana <-- pulls -- Prometheus <-- scrapes JMX metrics -- (Kafka/Connect/Operator)
DATA FLOW:  Source DB --Debezium--> Kafka topics --> consumers (ADB) / Kafka Bridge (HTTP)
```

## 3. Alert to Mail / MS Teams [chat — Q3, aligns with the Grafana chat]
- **Grafana Alerting (built-in, v8+) can send Mail + MS Teams WITHOUT Prometheus Alertmanager.**
- Why Prometheus-side is heavier: Prometheus stores only metrics; alerting there needs a separate
  **Alertmanager** deployment (rules + deploy = more resource) → for interim, Grafana-managed alert
  is the right choice (UI-only, no image build, no new code).
- Concept: Grafana already pulls the metric to draw the graph → "check the graph every X min, if it
  crosses Y, send Mail/Teams."

## 4. 🧠 Claude — notes
- This confirms the interim direction in the Grafana chat: **Grafana-managed alert** on an existing
  Strimzi metric, no Alertmanager, no rebuild. Consistent across both chats. ✅
- One correction the chat did NOT need but worth stating: the user earlier assumed "the operator of
  the Kafka cluster is Prometheus" — **no**, the operator is **Strimzi Cluster Operator**; Prometheus
  only *scrapes/stores metrics*, it doesn't operate Kafka.
- Full detail of each component + repo mapping is in memory [[aia-data-platform-streaming]] and my
  in-session component map. Nothing here contradicts it.
