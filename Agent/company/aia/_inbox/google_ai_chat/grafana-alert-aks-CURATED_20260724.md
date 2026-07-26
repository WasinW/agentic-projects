# Grafana alert for Strimzi Kafka restart — CURATED (short-term, no kube-state-metrics)

> Reorganized by Claude from the 28-turn Google AI Mode chat (2026-07-24). Companion to the
> full verbatim: `grafana-alert-aks-FULL-verbatim_20260724.md`.
> Provenance markers: **[chat]** = from the Google AI session · **[🧠 Claude]** = my architect
> analysis / correction added on top. Candidate for kb-synth → knowledge/ after review.

## 0. Env facts (extracted) [chat]
- Strimzi Kafka on **AKS**. Grafana + Prometheus present; Grafana connects to **PROD Prometheus only**.
- Namespaces: `nsp-th-u-kafka` (UAT), `nsp-th-p-kafka` (PROD).
- Connect clusters: `thdlcd0-uat-connect-cluster-gen01`, `thdlcd0-prod-connect-cluster-gen01`.
- Dashboard file: `strimzi-operators.json` (existing Strimzi Grafana dashboard).

## 1. The core reality — what metrics actually exist [chat, confirmed by JSON results]
- ❌ **kube-state-metrics is NOT installed** → every `kube_pod_*` query returns **No Data**
  (`kube_pod_container_status_restarts_total`, `kube_pod_status_ready` all empty — Q4, Q17).
- ✅ **Strimzi Operator metrics DO exist** → `strimzi_reconciliations_failed_total`,
  `strimzi_reconciliations_duration_seconds_sum`, etc.
- ⛔ Cross-env (query UAT from the PROD Grafana) = No Data; needs an endpoint from Network/Infra →
  team dropped it, **focus PROD only** (Q25, Q26).

> **[🧠 Claude — correction to my earlier advice]** My previous interim used
> `kube_pod_container_status_restarts_total` assuming Azure Monitor **managed** Prometheus (which
> ships kube-state-metrics by default). **Their Prometheus is a self-managed, Strimzi-focused
> stack WITHOUT kube-state-metrics** — so that path is blocked short-term. The chat's conclusion
> is right: **short-term rides Strimzi operator metrics; kube-state-metrics is the long-term add.**

## 2. Correct metric labels [chat — Q9/Q10, proven from result JSON]
Strimzi emits `namespace`, `exported_namespace`, `kind`, `name` — **NOT** `kubernetes_namespace`.
Working selector:
```promql
strimzi_reconciliations_failed_total{kind="KafkaConnect", namespace="nsp-th-p-kafka"}
```
(Adding a wrong label like `kubernetes_namespace=...` or a non-matching `name=...` → silent No Data.)

## 3. The working queries [chat — final consensus]
```promql
# HISTORY — did it ever fail in the last 30 days?
sum_over_time(strimzi_reconciliations_failed_total{kind="KafkaConnect", namespace="nsp-th-p-kafka"}[30d])

# ALERT — a failure happened in the last 5 min (use in Grafana alert rule)
sum(increase(strimzi_reconciliations_failed_total{kind="KafkaConnect", namespace="nsp-th-p-kafka"}[5m])) > 0

# existing dashboard panel pattern (strimzi-operators.json)
sum(increase(strimzi_reconciliations_failed_total[1h])) by (kind)
```

## 4. PromQL gotchas that caused "No Data / 0" [chat — the debugging trail]
1. **Dashboard time-range was locked to ~2 min** (Step 15s) → `[30d]` computed over 2 min → 0.
   Fix: widen the **top-right time picker** (e.g. 2026-07-01 → 07-31); Grafana then auto-steps to 30m.
2. **Prometheus retention deletes old data** → the July-17 incident window is gone; querying it
   returns the earliest *available* point (~July 24), not the incident (Q7, Q24).
3. **Counter reset on operator pod restart** → `increase()` sees no delta across the reset (Q28).
4. **Series doesn't exist until the first failure** → No Data before the first loop break (Q5).
5. **`sum_over_time([30d])`** sums every 15s scrape of the value "1" → thousands (1449…1453) — that
   is *scrape count*, not failure count (Q10). Use it only as a yes/no "did it fail" signal.

## 5. Incident timeline [chat — the real story]
- **UAT (~2026-07-17):** operator log `Exceeded timeout of 600000ms while waiting for Pods ... to
  be ready` → **Kafka Connect pod took >10 min to boot** → `createOrUpdate failed` (TimeoutException)
  → reconciliation loop hammered/hung. Team did **stop + resume** (~23:30, July 17) → recovered.
  Operator pod `fhgzx` restarted ~15:11 July 17.
- **PROD (2026-07-23 20:56:54):** `ERROR AbstractOperator:285 - Reconciliation #79222(timer)
  KafkaConnect(nsp-th-p-kafka/...): createOrUpdate failed` +
  `io.netty.resolver.dns.DnsResolveContext$SearchDomainUnknownHost...` → **CoreDNS died** (DNS
  resolution failure). During the outage `increase`=0 because the counter jumped 0→1 then froze
  and the operator pod itself restarted (counter reset + data gap before 21:15).
- **Key point:** UAT = *slow-boot timeout*; PROD = *DNS death*. **Different root causes, same
  downstream symptom** (reconciliation failure).

## 6. 🧠 Claude — architect notes (what to do with this)

**(a) The alert is "effect-level", not root-cause** [chat Q20 agrees].
`strimzi_reconciliations_failed_total` fires when *anything* breaks the reconcile loop — it does
NOT specifically detect a restart loop, and it's blind to a pure kube/node problem. Good enough as
an interim tripwire; know its blind spots.

**(b) The alert can MISS an event** — because a hard failure that restarts the operator resets the
counter, and retention can erase the window. So `increase[5m]>0` is best-effort. **Add a companion
signal:** alert also on the operator being **absent/not-updating**, e.g.
`absent(strimzi_reconciliations_periodical_total{namespace="nsp-th-p-kafka"})` or a duration-stall
check — so a dead operator (no metrics at all) still pages you. (Verify exact metric names in-tenant.)

**(c) Alerting ≠ fixing. The two incidents need different real fixes:**
- **UAT slow boot >10 min:** raise the Connect readiness/timeout, or fix the slow startup
  (image size, connector plugin load, JVM, dependency waits). A 10-min boot is the real defect.
- **PROD CoreDNS death:** this is an **AKS platform/infra issue**, not a Kafka one — coordinate
  with the infra/network team on CoreDNS resilience (replicas, node pressure, autoscale, cache).
  This is the more serious risk; the alert only tells you *after* it breaks.

**(d) Long-term (the "ต้นเหตุ" alert Sin wanted):** install **kube-state-metrics** → then
`kube_pod_status_ready{condition="false"}` and `kube_pod_container_status_restarts_total` give
**restart-specific, root-cause-level** alerting (and a real pod-restart counter). That's the
proper monitor; the Strimzi-reconcile alert is the bridge until then. Put both in the SAME Grafana
dashboard (`strimzi-operators.json`, add panels — Q19), single Prometheus datasource.

## 7. Open items → for Sin / relay to Copilot
- Confirm exact Prometheus **retention** (drives how far history queries can go).
- Decide interim alert set: `increase[5m]>0` failure **+** an operator-absence/liveness companion.
- File the two real fixes: (UAT) Connect boot time / timeout; (PROD) CoreDNS resilience with infra.
- Long-term ticket: add kube-state-metrics → restart-specific alerts.
