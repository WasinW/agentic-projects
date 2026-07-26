# AKS CLI + FIRST Kafka restart investigation — CURATED

> Reorganized by Claude from the 6-turn Google AI Mode chat. Raw: `aks-cli-kafka-investigate-FULL_20260724.md`.
> **This is the ORIGIN chat** — where the UAT Kafka restart was first traced. It precedes the
> Grafana-alert chat (`grafana-alert-aks-*`). Provenance: **[chat]** / **[🧠 Claude]**.

## 0. az aks vs kubectl [chat]
- `az aks` = manages the **infrastructure** ("the house"): create/delete cluster, scale nodes, upgrade
  K8s version. Works from outside the cluster (Azure control plane).
- `kubectl` = manages the **applications** inside ("the people"): deploy pods, view logs, check
  services. Needs `az aks get-credentials` first.
- Core flow: `az login` → `az aks get-credentials -g <rg> -n <cluster>` → `kubectl ...`.

## 1. Triage commands to find a failing Kafka cluster [chat]
```bash
# find any pod NOT running (incl CrashLoopBackOff) across all namespaces
kubectl get pods --all-namespaces --field-selector status.phase!=Running
# Strimzi custom resources
kubectl get kafka --all-namespaces
kubectl get kafkaconnect --all-namespaces
# operator log (the reconcile errors live here)
kubectl logs <strimzi-cluster-operator-pod> -n <ns>
```

## 2. THE ROOT FINDING (2026-07-17) [chat — proven from kubectl output]
- The thing that failed was **NOT a Kafka broker** — it was **Kafka Connect
  `thdlcd0-uat-connect-cluster-gen01`** in namespace **`nsp-th-u-kafka`** (UAT).
- Operator log: `Exceeded timeout of 600000ms while waiting for Pods resource
  thdlcd0-uat-connect-cluster-gen01-connect-2 in namespace nsp-th-u-kafka to be ready`
  → the **3rd Connect node (`connect-2`)** did not reach Ready within **10 min** → Timeout →
  reconcile loop failed and hammered.
- **Why it looks "Running" now:** a previous admin did **Pause & Resume** (cleared the stuck
  reconcile) → status green again, but the failure history stayed in the operator counter (this is
  why the Grafana `strimzi_reconciliations_failed_total` shows the scar — see the Grafana chat).
- ~20 Kafka resources were Running; only this one Connect cluster was stuck (Init:0/1 / pending).

## 3. Why the Connect pod hung [chat — root causes]
1. **Container image / plugin loads too slow** — Connect with many plugins (Debezium, JDBC, S3),
   or **hot-loading JAR files at every start**, makes boot exceed the **Readiness Probe** window.
2. Network / external resource wait during boot.
3. **Helm Chart default config too low** — default `timeoutSeconds` / readiness / resources from a
   stock chart, never tuned → the 10-min timeout is a chart default that's too tight for this Connect.

## 4. 🧠 Claude — architect notes
- **This = the UAT incident** (slow Connect boot / timeout). The **PROD** incident (2026-07-23) was a
  **different root cause — CoreDNS death** (see `grafana-alert-aks-CURATED`). Same symptom
  (reconcile failed), different cause. Don't conflate them.
- **The real fix is NOT "pause & resume"** (that's masking). Fix the boot time:
  - **Bake connector plugins into the image** (the `dtp_kafka_build_ci` / build-image repo) instead
    of hot-loading JARs at startup → faster, deterministic boot. This is the highest-leverage fix.
  - **Raise the readiness/timeout** in the Connect config if boot legitimately needs longer
    (`spec.template` readiness probe, or the operator's pod-ready timeout) — a stopgap, not a cure.
  - Right-size Connect resources (CPU/mem) so the JVM + plugin load isn't starved.
- **Monitoring tie-in:** because kube-state-metrics isn't installed, you can't alert on the pod
  Readiness directly yet — interim alert rides `strimzi_reconciliations_failed_total` (Grafana chat).
- **Helm/GitOps note:** since the timeout is a chart/config default, the durable fix lives in the
  Kafka Connect CR / values in the cluster repo, deployed via Jenkins → ACR → AKS → operator reconcile.

## 5. Open items
- Confirm whether Connect plugins are hot-loaded vs baked-in (drives the boot-time fix).
- Decide readiness/timeout values; file the build-image change to bake plugins.
- Long-term: kube-state-metrics → readiness-level alerting (see the Grafana chat's long-term).
