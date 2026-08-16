---
title: Strimzi Alerts — Grafana UI Setup Manual
version: 1.0
date: 2026-08-15
author: For สิน (วศิน) — Senior DE @ AIA
purpose: Step-by-step UI walkthrough for creating 9 alert rules without code deploy
target_grafana: 10.x or later (Grafana Alerting, not legacy)
prerequisite_file: strimzi_alerts.yaml
---

# 📖 Strimzi Alerts — Grafana UI Setup Manual

## เกี่ยวกับ Manual นี้

ทำเพราะ Sin ระบุว่า **code deploy กระทบทีมอื่น** เลย setup ผ่าน UI ทีละ rule แทน

**สิ่งที่จะได้:**
- 1 Heartbeat rule (multi-query cluster status)
- 8 Alert rules (event-driven)
- ทั้งหมด follow pattern เดียวกับ 2 rules ที่ Sin มีอยู่แล้ว

**เวลาที่ใช้:** ประมาณ 1-1.5 ชม. (rule ละ 5-10 นาที)

---

## 🗺️ Table of Contents

- [Prerequisites](#-prerequisites)
- [Section 1: Prep Work](#-section-1-prep-work-15-min)
- [Section 2: Create Heartbeat Rule (H1)](#-section-2-create-heartbeat-rule-h1)
- [Section 3: Create Alert Rules (A1-A8)](#-section-3-create-alert-rules-a1-a8)
  - [Rule A1: Reconciliation Failed (Any Kind)](#rule-a1-reconciliation-failed-any-kind)
  - [Rule A2: Operator Down](#rule-a2-operator-down)
  - [Rule A3: Resource Count Dropped](#rule-a3-resource-count-dropped)
  - [Rule A4: Reconciliation Slow](#rule-a4-reconciliation-slow)
  - [Rule A5: Resource Paused](#rule-a5-resource-paused)
  - [Rule A6: Lock Storm](#rule-a6-lock-storm)
  - [Rule A7: No Reconciliation Happening](#rule-a7-no-reconciliation-happening)
  - [Rule A8: KafkaConnector Not Ready](#rule-a8-kafkaconnector-not-ready)
- [Section 4: Verification & Testing](#-section-4-verification--testing)
- [Section 5: Troubleshooting](#-section-5-troubleshooting)

---

## 📋 Prerequisites

**สิ่งที่ต้องมี:**

```
✓ Grafana access (Editor role หรือสูงกว่า)
✓ Prometheus datasource ที่มี Strimzi metrics
✓ Folder "kafka-clsuter-alert-rule" (Sin's existing folder)
✓ Contact point "test_wasin" (Sin's existing receiver)
```

**สิ่งที่ต้อง verify ก่อนเริ่ม:**

1. เข้า **Explore** ใน Grafana
2. เลือก Prometheus datasource
3. Query แต่ละ metric เพื่อยืนยันว่ามีอยู่:

```promql
strimzi_reconciliations_failed_total{namespace="nsp-th-u-kafka"}
strimzi_reconciliations_successful_total{namespace="nsp-th-u-kafka"}
strimzi_reconciliations_total{namespace="nsp-th-u-kafka"}
strimzi_reconciliations_duration_seconds_bucket{namespace="nsp-th-u-kafka"}
strimzi_reconciliations_locked_total{namespace="nsp-th-u-kafka"}
strimzi_resources{namespace="nsp-th-u-kafka"}
strimzi_resources_paused{namespace="nsp-th-u-kafka"}
strimzi_resource_state{namespace="nsp-th-u-kafka"}
up{namespace="nsp-th-u-kafka"}
```

**ถ้า metric ไหนไม่มีค่า** → note ไว้ แล้ว skip rule ที่ต้องใช้ metric นั้น  
**ถ้า `strimzi_resource_state` ไม่มี** → skip Rule A8

---

## 🔧 Section 1: Prep Work (15 min)

### Step 1.1: Note Datasource UID ของ Prometheus

**สำคัญ:** ต้องรู้ UID ของ Prometheus datasource ก่อน — ทุก rule ใช้ค่านี้

**วิธีหา:**

1. เข้า **Home** → **Connections** → **Data sources**
2. คลิก Prometheus datasource ของ Sin
3. ดู URL ใน browser: `.../datasources/edit/<UID>`
4. **UID ตัวนี้แหละ** — จด/copy ไว้

**หรือ:**
- Grafana → **Alerting** → **Alert rules** → เปิด rule เดิม (Sin's existing rules) → ดู datasource ที่ query ใช้อยู่

**ในตัวอย่างของ Sin:**
```
datasourceUid: PBFA97CFB590B2093
```

---

### Step 1.2: Verify Contact Point "test_wasin"

1. Grafana → **Alerting** → **Contact points**
2. หา "test_wasin"
3. ถ้ามี → ✓ พร้อมใช้
4. ถ้าไม่มี → ต้อง create (Sin น่าจะมีอยู่แล้ว)

**แนะนำสำหรับ future:** เปลี่ยนเป็น DL email แทน personal เพราะ:
- Rotation ง่ายกว่า
- Handoff ให้ทีมได้
- ไม่ตายเมื่อคนออก

---

### Step 1.3: Verify Folder

1. Grafana → **Alerting** → **Alert rules**
2. หา folder "kafka-clsuter-alert-rule"
3. ถ้ามี → ✓ ใช้ folder เดิม
4. ถ้าไม่มี → คลิก **New folder** → ตั้งชื่อตามที่ Sin ใช้

**หมายเหตุ:** ชื่อ folder ที่ Sin ใช้มี typo `clsuter` (ควรเป็น `cluster`) — เก็บไว้ตามเดิมเพื่อให้ compat กับ 2 rules ที่ Sin มีแล้ว หรือจะย้ายไป folder ใหม่ก็ได้

---

## 🩺 Section 2: Create Heartbeat Rule (H1)

### Overview

- **Name:** `strimzi-cluster-heartbeat-uat`
- **Group:** `kafka-cluster-alert-heartbeat`
- **Interval:** 1 hour
- **Pending (for):** 4 hours
- **Purpose:** Comprehensive cluster status every 4h
- **Queries:** 9 (A through I) + threshold (J)

### Step 2.1: Create New Rule

1. **Alerting** → **Alert rules** → **New alert rule**
2. เลือก **Grafana managed alert rule**

### Step 2.2: Section "1. Enter alert rule name"

```
Alert rule name: strimzi-cluster-heartbeat-uat
```

### Step 2.3: Section "2. Define query and alert condition"

**Add Query A (Operator up):**

- คลิก **Add query** (ถ้ายังไม่มี query)
- ที่ query A:
  - **Data source:** Prometheus (UID `PBFA97CFB590B2093`)
  - **Query type:** Instant (สำคัญ — เปลี่ยนจาก Range เป็น Instant)
  - **Time range:** 5m (from 300 to 0)
  - Toggle **Code editor** (จาก Builder → Code)
  - **Expression:**
    ```
    sum(up{namespace="nsp-th-u-kafka", job=~".*strimzi.*"})
    ```

**Add Query B (Kafka CR count):**

- คลิก **+ Add query**
- Query B:
  - **Data source:** Prometheus
  - **Instant** query, Time range 5m
  - **Expression:**
    ```
    sum(strimzi_resources{kind="Kafka", namespace="nsp-th-u-kafka"}) or vector(0)
    ```

**Add Query C (KafkaConnect count):**

- **+ Add query** → C
- Expression:
  ```
  sum(strimzi_resources{kind="KafkaConnect", namespace="nsp-th-u-kafka"}) or vector(0)
  ```

**Add Query D (KafkaConnector count):**

- **+ Add query** → D
- Expression:
  ```
  sum(strimzi_resources{kind="KafkaConnector", namespace="nsp-th-u-kafka"}) or vector(0)
  ```

**Add Query E (KafkaTopic count):**

- **+ Add query** → E
- Expression:
  ```
  sum(strimzi_resources{kind="KafkaTopic", namespace="nsp-th-u-kafka"}) or vector(0)
  ```

**Add Query F (Reconciliations succeeded 24h):**

- **+ Add query** → F
- Time range: **24h** (from 86400 to 0)
- Expression:
  ```
  sum(increase(strimzi_reconciliations_successful_total{namespace="nsp-th-u-kafka"}[24h])) or vector(0)
  ```

**Add Query G (Reconciliations failed 24h):**

- **+ Add query** → G
- Time range: **24h**
- Expression:
  ```
  sum(increase(strimzi_reconciliations_failed_total{namespace="nsp-th-u-kafka"}[24h])) or vector(0)
  ```

**Add Query H (Paused resources):**

- **+ Add query** → H
- Time range: 5m
- Expression:
  ```
  sum(strimzi_resources_paused{namespace="nsp-th-u-kafka"}) or vector(0)
  ```

**Add Query I (Reconciliation P95 duration 24h):**

- **+ Add query** → I
- Time range: **24h**
- Expression:
  ```
  histogram_quantile(0.95, sum(rate(strimzi_reconciliations_duration_seconds_bucket{namespace="nsp-th-u-kafka"}[24h])) by (le)) or vector(0)
  ```

**Add Expression J (Threshold — always fire):**

- คลิก **+ Add expression**
- เลือก **Threshold**
- **Input:** A (จะใช้แค่ A เป็นตัว trigger)
- **When:** IS ABOVE OR EQUAL TO
- **Threshold value:** `0`
- **Alert condition:** ✓ (checkbox — เลือก J เป็น alert condition)

**Verify:** Preview button → ควรเห็นค่าทั้ง A-I แสดง

### Step 2.4: Section "3. Set evaluation behavior"

```
Folder:            kafka-clsuter-alert-rule
Evaluation group:  kafka-cluster-alert-heartbeat
Evaluation interval: 1h
Pending period:    4h
```

**Advanced options** (คลิกขยาย):

```
No data and error handling:
├── Alert state if no data or all values are null: Alerting  ⭐
└── Alert state if execution error or timeout:    Error
```

**⭐ สำคัญ:** `noData = Alerting` ทำให้ heartbeat กลายเป็น deadman's switch — ถ้า Prometheus/Operator ตาย → alert ยิงเข้ามาแทน

### Step 2.5: Section "4. Configure labels and notifications"

**Labels:**

คลิก **+ Add label** ทีละอัน:

```
component  =  strimzi-cluster
env        =  uat
severity   =  info
team       =  data-platform
type       =  heartbeat
```

**Notifications:**

เลือก **Use notification policy** (ตามที่ Sin ใช้อยู่)

หรือถ้าอยากใช้ specific contact point:
- เลือก **Use contact point**
- Contact point: `test_wasin`
- Group interval: 4h (repeat interval)

### Step 2.6: Section "5. Annotations"

**Summary:**

```
[Heartbeat] Strimzi UAT — Op={{ $values.A }} | Kafka={{ $values.B }} | Connect={{ $values.C }} | Connectors={{ $values.D }} | Topics={{ $values.E }} | Failed(24h)={{ $values.G }}
```

**Description:** (copy ทั้งบล็อก)

```
🩺 รายงานสถานะ Strimzi cluster (UAT) ประจำ 4 ชั่วโมง

📡 Operator Health
├─ Cluster Operator up: {{ $values.A }} (expected: 1)

📦 Resources ที่ operator เห็น
├─ Kafka clusters:      {{ $values.B }}
├─ KafkaConnect:        {{ $values.C }}
├─ KafkaConnector:      {{ $values.D }}
└─ KafkaTopic:          {{ $values.E }}

🔄 Reconciliation (24 ชม.)
├─ Successful:          {{ $values.F }}
├─ Failed:              {{ $values.G }}
└─ P95 duration:        {{ printf "%.2f" $values.I.Value }} วินาที

⏸️  Paused resources:    {{ $values.H }}

🎯 Interpret:
{{ if eq ($values.A).Value 0.0 }}⚠️ OPERATOR DOWN — ต้องแก้ด่วน!{{ else }}✓ Operator ทำงานปกติ{{ end }}
{{ if gt ($values.G).Value 0.0 }}⚠️ พบ failed reconciliation {{ $values.G }} ครั้งใน 24 ชม.{{ else }}✓ ไม่พบ reconciliation failure{{ end }}
{{ if gt ($values.H).Value 0.0 }}⚠️ มี resources ถูก pause อยู่ {{ $values.H }} ตัว — ตรวจสอบด้วย{{ else }}✓ ไม่มี resource ถูก pause{{ end }}
{{ if gt ($values.I).Value 60.0 }}⚠️ Reconciliation p95 > 60s — operator อาจ overloaded{{ else }}✓ Reconciliation performance ปกติ{{ end }}
```

### Step 2.7: Save

- คลิก **Save rule and exit** (top-right)
- ✓ Rule H1 เสร็จ

---

## 🚨 Section 3: Create Alert Rules (A1-A8)

**Pattern ทั่วไปสำหรับทุก alert rule:**

```
1. Alerting → Alert rules → New alert rule
2. Enter alert rule name
3. Define query (A, sometimes B/C) + threshold expression
4. Set evaluation behavior:
   - Folder: kafka-clsuter-alert-rule
   - Group: kafka-cluster-alert-instant
   - Interval: 5m
   - Pending (for): varies per rule
5. Labels (component/env/severity/team)
6. Notifications (test_wasin, repeat_interval)
7. Annotations (summary + description)
8. Save
```

Skip step ที่ตรงกันทุก rule เพื่อไม่ต้องเขียนซ้ำ

---

### Rule A1: Reconciliation Failed (Any Kind)

**Name:** `strimzi-reconcile-fail-any-kind-uat`

**Query A (Failed reconciliations by kind):**
- Instant, Time range **10m**
```promql
sum by (kind) (
  increase(strimzi_reconciliations_failed_total{namespace="nsp-th-u-kafka"}[10m])
)
```

**Query B (Reference - resource count by kind):**
- Instant, Time range 5m
```promql
sum by (kind) (strimzi_resources{namespace="nsp-th-u-kafka"})
```

**Expression C (Threshold):**
- Input: A
- IS ABOVE `0`
- ✓ Alert condition

**Evaluation:**
```
Group:    kafka-cluster-alert-instant
Interval: 5m
Pending:  5m
No data:  OK
Error:    Error
```

**Labels:**
```
component  = strimzi
env        = uat
severity   = critical
team       = data-platform
```

**Notifications:**
- Contact: `test_wasin`
- Repeat interval: `15m`

**Summary:**
```
[CRITICAL] Strimzi reconciliation failed — kind={{ $labels.kind }}, count={{ $values.A }}
```

**Description:**
```
🚨 Strimzi พบ reconciliation failure

Resource kind:      {{ $labels.kind }}
Namespace:          nsp-th-u-kafka
Failed count (10m): {{ $values.A }}
Env:                UAT

⚡ Action:
1. kubectl get {{ $labels.kind | toLower }} -n nsp-th-u-kafka
2. kubectl describe {{ $labels.kind | toLower }} <name> -n nsp-th-u-kafka
3. kubectl logs -n nsp-th-u-kafka -l strimzi.io/kind=cluster-operator --tail=200
```

**Runbook URL:** `https://strimzi.io/docs/operators/latest/deploying`

---

### Rule A2: Operator Down

**Name:** `strimzi-cluster-operator-down-uat`

**Query A:**
- Instant, Time range 5m
```promql
sum(up{namespace="nsp-th-u-kafka", job=~".*strimzi.*"})
```

**Expression C (Threshold):**
- Input: A
- IS BELOW `1`
- ✓ Alert condition

**Evaluation:**
```
Group:    kafka-cluster-alert-instant
Interval: 5m
Pending:  2m
No data:  Alerting    ⭐ สำคัญ — no data = also down
Error:    Alerting    ⭐
```

**Labels:**
```
component  = strimzi-operator
env        = uat
severity   = critical
team       = data-platform
```

**Notifications:**
- Contact: `test_wasin`, Repeat: `15m`

**Summary:**
```
[CRITICAL] Strimzi Cluster Operator DOWN — UAT
```

**Description:**
```
🔴 Strimzi Cluster Operator ไม่ทำงาน

Namespace: nsp-th-u-kafka
Env: UAT
Up count: {{ $values.A }} (expected: 1)

⚠️ Impact:
- ไม่มีใคร reconcile Kafka/Connect/Topics ใหม่
- Changes ที่ apply ไปจะไม่ถูกดำเนินการ
- Existing brokers ยัง run แต่ไม่มี management layer

⚡ Action:
1. kubectl get pods -n nsp-th-u-kafka -l strimzi.io/kind=cluster-operator
2. kubectl describe pod -n nsp-th-u-kafka <operator-pod>
3. kubectl logs -n nsp-th-u-kafka <operator-pod> --tail=200
4. Check node health / resource quota
```

---

### Rule A3: Resource Count Dropped

**Name:** `strimzi-resource-count-dropped-uat`

**Query A (Current count):**
- Instant, Time range 5m
```promql
sum by (kind) (strimzi_resources{namespace="nsp-th-u-kafka"})
```

**Query B (Count 1h ago):**
- Instant, Time range 5m
```promql
sum by (kind) (strimzi_resources{namespace="nsp-th-u-kafka"} offset 1h)
```

**Expression C (Math — difference):**
- Type: **Math**
- Expression: `$B - $A`

**Expression D (Threshold):**
- Input: C
- IS ABOVE `0`
- ✓ Alert condition

**Evaluation:**
```
Group:    kafka-cluster-alert-instant
Interval: 5m
Pending:  10m
No data:  OK
Error:    Error
```

**Labels:**
```
component  = strimzi
env        = uat
severity   = warning
team       = data-platform
```

**Notifications:**
- Contact: `test_wasin`, Repeat: `1h`

**Summary:**
```
[WARNING] Strimzi resource count dropped — {{ $labels.kind }} lost {{ $values.C }}
```

**Description:**
```
⚠️ จำนวน {{ $labels.kind }} resources ลดลง

Kind:        {{ $labels.kind }}
Current:     {{ $values.A }}
1h ago:      {{ $values.B }}
Lost:        {{ $values.C }}

Possible causes:
- มีคน kubectl delete
- CI/CD deployment error
- Namespace ถูก reconfigure

⚡ Action:
1. kubectl get events -n nsp-th-u-kafka --sort-by='.lastTimestamp' | head -50
2. kubectl get {{ $labels.kind | toLower }} -n nsp-th-u-kafka
3. Check git history for recent CR changes
```

---

### Rule A4: Reconciliation Slow

**Name:** `strimzi-reconcile-duration-p99-slow-uat`

**Query A:**
- Instant, Time range **15m**
```promql
histogram_quantile(0.99,
  sum by (kind, le) (
    rate(strimzi_reconciliations_duration_seconds_bucket{namespace="nsp-th-u-kafka"}[15m])
  )
)
```

**Expression C (Threshold):**
- Input: A
- IS ABOVE `120`
- ✓ Alert condition

**Evaluation:**
```
Group:    kafka-cluster-alert-instant
Interval: 5m
Pending:  15m
No data:  OK
Error:    Error
```

**Labels:**
```
component  = strimzi-operator
env        = uat
severity   = warning
team       = data-platform
```

**Notifications:**
- Contact: `test_wasin`, Repeat: `1h`

**Summary:**
```
[WARNING] Strimzi reconcile P99 slow — kind={{ $labels.kind }}, p99={{ printf "%.2f" $values.A.Value }}s
```

**Description:**
```
⚠️ Reconciliation ช้าผิดปกติ

Kind:      {{ $labels.kind }}
P99:       {{ printf "%.2f" $values.A.Value }} seconds
Threshold: 120s

Possible causes:
- Operator overloaded (มี CR เยอะเกินไป)
- Kubernetes API slow
- Network issue between operator and API server
- Kafka cluster unresponsive during rolling update

⚡ Action:
1. kubectl top pod -n nsp-th-u-kafka -l strimzi.io/kind=cluster-operator
2. kubectl logs -n nsp-th-u-kafka <operator-pod> | grep -i "reconcil\|slow\|timeout"
3. Check kube-apiserver latency
```

---

### Rule A5: Resource Paused

**Name:** `strimzi-resource-paused-uat`

**Query A:**
- Instant, Time range 5m
```promql
sum by (kind) (strimzi_resources_paused{namespace="nsp-th-u-kafka"})
```

**Expression C (Threshold):**
- Input: A
- IS ABOVE `0`
- ✓ Alert condition

**Evaluation:**
```
Group:    kafka-cluster-alert-instant
Interval: 5m
Pending:  30m    ⭐ tolerance สูง — อาจตั้งใจ pause
No data:  OK
Error:    Error
```

**Labels:**
```
component  = strimzi
env        = uat
severity   = info
team       = data-platform
```

**Notifications:**
- Contact: `test_wasin`, Repeat: `6h`  ⭐ ไม่ spam

**Summary:**
```
[INFO] Strimzi resource paused — kind={{ $labels.kind }}, count={{ $values.A }}
```

**Description:**
```
ℹ️  พบ {{ $labels.kind }} ที่ถูก pause reconciliation

Kind:     {{ $labels.kind }}
Paused:   {{ $values.A }} resources
Duration: 30+ นาที

หมายเหตุ:
- pause ถูกตั้งด้วย annotation strimzi.io/pause-reconciliation="true"
- อาจตั้งใจ debug — ถ้าใช่ ignore
- ถ้าไม่รู้ว่าใครตั้ง → ตรวจสอบ

⚡ Action:
1. kubectl get {{ $labels.kind | toLower }} -n nsp-th-u-kafka -o json | jq '.items[] | select(.metadata.annotations."strimzi.io/pause-reconciliation"=="true") | .metadata.name'
2. หา owner ผ่าน git blame / annotations
3. ถ้า unpause: kubectl annotate {{ $labels.kind | toLower }} <name> strimzi.io/pause-reconciliation- -n nsp-th-u-kafka
```

---

### Rule A6: Lock Storm

**Name:** `strimzi-reconcile-locked-storm-uat`

**Query A:**
- Instant, Time range **15m**
```promql
sum by (kind) (
  increase(strimzi_reconciliations_locked_total{namespace="nsp-th-u-kafka"}[15m])
)
```

**Expression C (Threshold):**
- Input: A
- IS ABOVE `10`
- ✓ Alert condition

**Evaluation:**
```
Group:    kafka-cluster-alert-instant
Interval: 5m
Pending:  15m
No data:  OK
Error:    Error
```

**Labels:**
```
component  = strimzi-operator
env        = uat
severity   = warning
team       = data-platform
```

**Notifications:**
- Contact: `test_wasin`, Repeat: `1h`

**Summary:**
```
[WARNING] Strimzi reconciliation lock storm — kind={{ $labels.kind }}, locks={{ $values.A }}
```

**Description:**
```
⚠️ พบ reconciliation ถูก skip เพราะ lock ซ้ำๆ

Kind:           {{ $labels.kind }}
Locked (15m):   {{ $values.A }}
Threshold:      10

Meaning:
- Reconciliation กำลังรันช้า → ตัวถัดไปมาก็ถูก skip
- อาจเกิดจาก long-running rolling update
- หรือ operator stuck ใน reconciliation loop

⚡ Action:
1. เช็ค Rule A4 (reconcile duration) — ถ้าช้าด้วย = confirmed overload
2. kubectl logs -n nsp-th-u-kafka <operator> | grep -i "lock\|already in progress"
3. Consider scale up operator หรือลด CR count
```

---

### Rule A7: No Reconciliation Happening

**Name:** `strimzi-no-reconcile-happening-uat`

**Query A (Operator up):**
- Instant, Time range 5m
```promql
sum(up{namespace="nsp-th-u-kafka", job=~".*strimzi.*"})
```

**Query B (Reconciliations in last 30 min):**
- Instant, Time range **30m**
```promql
sum(increase(strimzi_reconciliations_total{namespace="nsp-th-u-kafka"}[30m])) or vector(0)
```

**Expression C (Math — condition):**
- Type: **Math**
- Expression: `$A > 0 && $B == 0`

**Expression D (Threshold):**
- Input: C
- IS ABOVE `0`
- ✓ Alert condition

**Evaluation:**
```
Group:    kafka-cluster-alert-instant
Interval: 5m
Pending:  30m
No data:  OK
Error:    Error
```

**Labels:**
```
component  = strimzi-operator
env        = uat
severity   = warning
team       = data-platform
```

**Notifications:**
- Contact: `test_wasin`, Repeat: `30m`

**Summary:**
```
[WARNING] Operator alive but no reconciliations in 30 min — UAT
```

**Description:**
```
⚠️ Operator ยังอยู่ แต่ไม่ทำ reconciliation เลย 30 นาที

Operator up:        {{ $values.A }}
Reconciles (30m):   {{ $values.B }}

Meaning:
- Operator อาจ deadlock
- หรือ Kubernetes API server ปฏิเสธ list/watch
- หรือ periodic reconciliation ถูกปิด/config ผิด
- Normal Strimzi reconcile ทุก 2 min → 30 min = ผิดปกติมาก

⚡ Action:
1. kubectl logs -n nsp-th-u-kafka <operator> --tail=500 | grep -iE "error|deadlock|panic"
2. kubectl auth can-i list kafkas.kafka.strimzi.io --as=system:serviceaccount:nsp-th-u-kafka:strimzi-cluster-operator
3. Restart operator ถ้าจำเป็น: kubectl rollout restart deploy/strimzi-cluster-operator -n nsp-th-u-kafka
```

---

### Rule A8: KafkaConnector Not Ready

**⚠️ Prerequisite check:**  
Query `strimzi_resource_state{kind="KafkaConnector"}` ใน Explore ก่อน  
- ถ้ามี → ทำ rule นี้ต่อ  
- ถ้าไม่มี → skip (metric อาจถูก deprecate แล้ว)

**Name:** `strimzi-kafkaconnector-not-ready-uat`

**Query A:**
- Instant, Time range 10m
```promql
sum by (name) (
  strimzi_resource_state{
    kind="KafkaConnector",
    namespace="nsp-th-u-kafka"
  } == 0
)
```

**Expression C (Threshold):**
- Input: A
- IS ABOVE `0`
- ✓ Alert condition

**Evaluation:**
```
Group:    kafka-cluster-alert-instant
Interval: 5m
Pending:  10m
No data:  OK
Error:    Error
```

**Labels:**
```
component  = kafka-connector
env        = uat
severity   = critical
team       = data-platform
```

**Notifications:**
- Contact: `test_wasin`, Repeat: `15m`

**Summary:**
```
[CRITICAL] KafkaConnector NOT READY — name={{ $labels.name }}
```

**Description:**
```
🔴 KafkaConnector อยู่ในสถานะ NotReady

Connector name:  {{ $labels.name }}
Namespace:       nsp-th-u-kafka

Impact:
- Debezium/Connect task อาจไม่ ingest data
- CDC pipeline ค้าง
- Downstream consumer จะไม่เห็น data ใหม่

⚡ Action:
1. kubectl get kafkaconnector {{ $labels.name }} -n nsp-th-u-kafka -o yaml
2. kubectl describe kafkaconnector {{ $labels.name }} -n nsp-th-u-kafka
3. Check status.conditions และ status.tasksMax
4. เข้า Kafka Connect REST API: curl -s http://<connect-svc>:8083/connectors/{{ $labels.name }}/status | jq
```

---

## ✅ Section 4: Verification & Testing

### Step 4.1: ดู State ของ Rule

1. **Alerting** → **Alert rules**
2. ควรเห็นทั้ง 9 rules ใหม่ (H1 + A1-A8)
3. Column "State":
   - **Normal** = ปกติ, ยังไม่ยิง
   - **Pending** = condition true แต่ยังไม่ครบ `for` duration
   - **Firing** = ยิงแล้ว
   - **NoData** = query ไม่ได้ค่ากลับมา
   - **Error** = query error

### Step 4.2: Preview / Test แต่ละ Rule

**Method 1: Preview ในหน้า edit**

1. เปิด rule ที่จะ test
2. เลื่อนไปที่ section "Define query"
3. คลิก **Preview** (ปุ่มด้านล่าง)
4. ดูค่าที่ query คืน:
   - ✓ มีค่า = OK
   - ✗ empty = query ผิดหรือ metric ไม่มี

**Method 2: Test alert firing ด้วย Explore**

1. **Explore** → เลือก Prometheus datasource
2. Query แบบเดียวกับ rule
3. เช็คว่า:
   - ค่า > threshold → rule ควร fire (ตาม pending time)
   - ค่า ≤ threshold → rule ควรปกติ

### Step 4.3: Force-fire เพื่อ test notification

**⚠️ Careful:** จะยิง email จริงเข้า Sin's mailbox

**Trick แบบไม่ต้อง break Kafka:**

1. เปิด rule ที่จะ test (เช่น A1)
2. เปลี่ยน threshold ชั่วคราว:
   - Original: `> 0`
   - Test: `>= 0` (จะเป็นจริงเสมอ)
3. Save
4. รอ (interval + pending) → ควรได้ email
5. เปลี่ยน threshold กลับ → Save

**หรือ:** ใช้ **Test rule** ปุ่มถ้ามี (Grafana เวอร์ชั่นใหม่)

### Step 4.4: Verify Email Format

Email ที่ Sin ได้รับควรมี:

```
✓ Subject line ตาม summary
✓ Description แสดง values ครบ (A, B, C, ...)
✓ Labels แสดงใน metadata
✓ Runbook URL (ถ้ามี)
✓ Silence link + View alert link
```

**ถ้า description ยังแสดง `{{ $values.A }}` แทนที่จะเป็นเลข**  
→ template syntax ผิดหรือ query ไม่ได้ค่า

---

## 🚑 Section 5: Troubleshooting

### Problem 1: Query returns "no data"

**Diagnostics:**

```
1. เข้า Explore → เลือก datasource เดียวกัน
2. Copy query จาก rule มารัน
3. ผลลัพธ์:
   ├── ได้ค่า → rule config มีปัญหา (ดู Problem 3)
   ├── empty → metric ไม่มี / label ไม่ match
   └── error → syntax ผิด
```

**Fix:**
- **Metric ไม่มี:** เช็คว่า Prometheus scrape strimzi operator สำเร็จมั้ย → `up{job=~".*strimzi.*"}`
- **Label ไม่ match:** ลองลด label filter → `strimzi_resources` (no filter) ดูค่าดิบก่อน
- **Namespace ผิด:** เช็คว่า namespace name ถูกจริงมั้ย

### Problem 2: Alert "Error" state

**สาเหตุปกติ:**
- Datasource connection ล่ม
- Query timeout (default 30s)
- Expression syntax ผิด

**Diagnostics:**

1. คลิก rule → ดู "Health" section
2. Error message จะบอกสาเหตุ

**Fix:**
- **Timeout:** ลด time range (from 86400 → 3600)
- **Syntax:** validate PromQL ใน Explore ก่อน
- **Datasource:** เช็ค connection ใน Data sources page

### Problem 3: Threshold ไม่ trigger ตามคาด

**Common causes:**

```
Cause 1: Wrong "Alert condition" checkbox
├── ต้อง check ที่ Expression ตัวสุดท้าย (threshold)
├── ไม่ใช่ที่ query A/B/C

Cause 2: Wrong evaluator type
├── "IS ABOVE"    (>)
├── "IS BELOW"    (<)
├── "IS EQUAL TO" (=)
├── "IS ABOVE OR EQUAL TO" (≥)  ← ที่ Sin ใช้ heartbeat
└── เลือกให้ตรง intent

Cause 3: Reducer type
├── "Last" (default, ปกติ)
├── "Avg", "Min", "Max", "Sum" — depends on use case
```

### Problem 4: Notification ไม่มา email

**Checklist:**

```
□ Contact point config ถูก? (SMTP, receiver email)
□ Notification policy match labels? (severity, team)
□ Rule state = Firing (ไม่ใช่ Normal/Pending)?
□ Silence rule ไม่ active?
□ Spam folder?
```

**Test contact point:**
- **Alerting** → **Contact points** → คลิก **test_wasin** → **Test**
- ถ้า test email มา = contact point OK, ปัญหาอยู่ที่ routing
- ถ้าไม่มา = ปัญหาที่ SMTP/Grafana config

### Problem 5: Template `{{ $values.X }}` ไม่ render

**Common causes:**

```
Cause 1: refId ที่อ้างในไม่มีอยู่จริง
├── description ใช้ {{ $values.I }} แต่ query ไม่มี I

Cause 2: Query returned empty
├── ทำให้ $values.I = null → render เป็น <no value>
├── Fix: ใส่ or vector(0) ที่ query

Cause 3: Value type mismatch
├── ใช้ printf "%.2f" .Value → ต้องเป็น number
├── Non-number → error / no render
```

### Problem 6: Rule ยิง alert ตอน rule ถูกสร้างครั้งแรก

**สาเหตุ:** Grafana evaluate ครั้งแรกทันทีที่ save

**Behavior ที่คาดหวัง:**
- Normal → Pending (ตาม `for` duration) → Firing
- ถ้า `for=0` → ยิงทันที

**Fix:**
- ตั้ง `for` ให้เหมาะสม (5m-15m ปกติ)
- Silence rule ชั่วคราวก่อน initial deployment แล้ว unsilence

---

## 📋 Post-Setup Checklist

หลังสร้างครบทั้ง 9 rules:

```
□ ทุก rule แสดงใน Alerting → Alert rules list
□ ทุก rule state = Normal (ไม่ใช่ Error)
□ ทั้ง 9 rules อยู่ใน folder kafka-clsuter-alert-rule
□ Heartbeat H1 มี evaluation group แยก (kafka-cluster-alert-heartbeat)
□ Alert A1-A8 อยู่ใน evaluation group เดียวกัน (kafka-cluster-alert-instant)
□ Preview ทุก rule ได้ค่า (ไม่ empty)
□ Test contact point test_wasin ส่ง email สำเร็จ
□ รอ 4-5 ชม. → ได้ email heartbeat แรก
□ Force-test A2 (operator down) → ได้ email critical
```

---

## 🚦 Ongoing Maintenance

### สัปดาห์แรก
- เช็คทุกวัน: มี alert ผิดพลาด (false positive) มั้ย?
- Adjust threshold ตาม baseline จริง (P99 duration อาจต้อง tune)

### ก่อนไป PRODUCTION
```
1. Duplicate ทั้ง 9 rules → เปลี่ยน namespace + env label
2. เปลี่ยน receiver จาก test_wasin → real DL
3. Silence UAT rules ระหว่าง maintenance window
4. Set up notification policy routing per severity
```

### เมื่อเพิ่ม Kafka Exporter หรือ JMX Exporter (Phase 2)
- เพิ่ม rules สำหรับ consumer lag, broker health, partition status
- ใช้ pattern เดียวกับ manual นี้

---

## 📚 References

- Strimzi docs: https://strimzi.io/docs/operators/latest/deploying
- Grafana Alerting: https://grafana.com/docs/grafana/latest/alerting/
- Prometheus JMX Exporter: https://github.com/prometheus/jmx_exporter

---

## 🆘 หา Sin ช่วย

ถ้าติดปัญหา:
1. Screenshot rule config + query preview
2. Screenshot email ที่ได้ (หรือไม่ได้)
3. State ของ rule (Normal/Pending/Firing/Error)
4. Prometheus query result ใน Explore

= debug ได้ง่ายกว่า

---

*End of Manual — 2026-08-15*
