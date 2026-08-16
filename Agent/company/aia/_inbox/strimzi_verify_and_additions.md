# Strimzi alerts — Verify Checklist + Additions (no new exporter)

> คู่กับ `strimzi_alerts.yaml`. env = UAT `nsp-th-u-kafka` (ทำ PROD ก็เปลี่ยนเป็น `nsp-th-p-kafka`).
> **PART A** = query ที่ต้องรัน verify ก่อน (ตัดสินว่า rule ไหนมี data / No Data เงียบ).
> **PART B** = alert/query เพิ่มได้เลยจาก metric ที่มีอยู่ (operator metrics) — **ไม่ต้อง deploy JMX/Kafka-Exporter/KSM**.
> 🔒 generic — ไม่มี AIA data จริงในไฟล์.

---

# PART A — VERIFY CHECKLIST (รันก่อน deploy/แก้)

## A0. Master check (kubectl — เห็นทุก metric+label ทีเดียว)
```bash
kubectl exec -n nsp-th-u-kafka deploy/strimzi-cluster-operator \
  -- curl -s localhost:8080/metrics \
  | grep -E '^strimzi_(reconciliations|resources|resource_state)' | sort -u
```
- [ ] เห็น metric อะไรบ้าง + label อะไรบ้าง (`kind`, `namespace`, `selector`, `name`)
- [ ] มี `..._duration_seconds_bucket` มั้ย (มี = histogram เปิด)
- [ ] `strimzi_resources` มี `kind` อะไรบ้าง (KafkaConnect? KafkaConnector? KafkaTopic?)

## A1. ⭐ `up` linchpin (รันใน Grafana **Explore**) — critical สุด
```promql
up{namespace="nsp-th-u-kafka"}
```
- [ ] อ่าน label **`job`** จริง (เอาไปแทนใน `job=~".*strimzi.*"`)
- [ ] operator pod อยู่ namespace `nsp-th-u-kafka` จริงมั้ย (ถ้าอยู่ ops namespace อื่น → H1 deadman + A2 พังเงียบ)
- **ผลบอก:** H1-A, **A2 (operator-down)**, A7 จะทำงานถูกก็ต่อเมื่อ selector นี้คืน series

## A2. reconciliation counters (Explore ทีละอัน)
```promql
strimzi_reconciliations_failed_total{namespace="nsp-th-u-kafka"}
strimzi_reconciliations_successful_total{namespace="nsp-th-u-kafka"}
strimzi_reconciliations_total{namespace="nsp-th-u-kafka"}
strimzi_reconciliations_locked_total{namespace="nsp-th-u-kafka"}
```
- [ ] `successful_total` ชื่อตรงมั้ย (ผิด = H1-F เงียบ)
- [ ] `_total` มีจริงมั้ย (ใช้ทำ failure ratio ใน B)
- [ ] label `kind` มี value อะไรบ้าง

## A3. duration histogram (ตัดสิน A4 + H1-I)
```promql
strimzi_reconciliations_duration_seconds_bucket{namespace="nsp-th-u-kafka"}
```
- [ ] **มี `_bucket` มั้ย?** ไม่มี = **A4 (p99) + H1-I (p95) ว่างทั้งคู่** → ต้องลบ 2 อันนั้น หรือเปิด histogram
- ถ้าไม่มี bucket แต่มี `_sum`/`_count` → ใช้ average แทน: `rate(_sum)/rate(_count)`

## A4. resources gauge + kinds (ตัดสิน H1-E, A5)
```promql
count by (kind) (strimzi_resources{namespace="nsp-th-u-kafka"})
count by (kind) (strimzi_resources_paused{namespace="nsp-th-u-kafka"})
```
- [ ] `strimzi_resources` มี `kind="KafkaTopic"` มั้ย (มักไม่มี — มาจาก Topic Operator แยก scrape → **H1-E จะอ่าน 0**)
- [ ] `strimzi_resources_paused` มี `kind="KafkaConnector"` มั้ย (**issue #6569 = ไม่มี → A5 บอด paused connector**)

## A5. resource_state (ตัดสิน A8 + B ตัวที่ใช้ state)
```promql
count by (kind) (strimzi_resource_state{namespace="nsp-th-u-kafka"})
```
- [ ] มี `kind="KafkaConnector"` มั้ย (doc coverage ไม่มี → A8 อาจ No Data แม้แก้ logic)
- [ ] ⚠️ metric นี้ **deprecated ลบ 0.51** → ของชั่วคราว

## A6. (bonus) operator JVM/process metrics มีมั้ย — ปลดล็อก free alert ใน B
```bash
kubectl exec -n nsp-th-u-kafka deploy/strimzi-cluster-operator \
  -- curl -s localhost:8080/metrics | grep -E '^(process_start_time_seconds|jvm_memory_used_bytes)'
```
- [ ] มี `process_start_time_seconds` มั้ย → ถ้ามี = ทำ **operator-restart alert ได้ฟรี** (B4 — ตรงกับ incident restart ของคุณ!)
- [ ] มี `jvm_memory_used_bytes` มั้ย → operator memory pressure alert ได้ฟรี

### สรุป decision จาก PART A
| ถ้าเจอ | ทำอะไร |
|---|---|
| `_bucket` ไม่มี | ลบ A4 + H1-I (หรือใช้ avg `_sum/_count`) |
| `up` job ไม่ตรง | แก้ selector ทุกที่ที่ใช้ `up` |
| paused ไม่มี KafkaConnector | ยอมรับว่า A5 บอด connector (ใช้ A11 ใน B แทน) |
| resource_state ไม่มี KafkaConnector | A8 ใช้ไม่ได้ → ใช้ proxy (reconcile_failed) |
| มี process/jvm | เพิ่ม B4 (restart) + B5 (memory) ฟรี |

---

# PART B — ADDITIONS จาก metric ที่มีอยู่ (ไม่ต้อง deploy เพิ่ม)

> ทั้งหมดใช้ operator metrics ที่ verify ใน A แล้ว. เพิ่มได้ทันทีใน 2 rule group เดิม.

## B1. เพิ่ม query ใน HEARTBEAT (H1) — status ให้ครบขึ้น
เพิ่ม refId ต่อจาก I (จำ: ทุกตัว `instant: true`, ใช้ `.Value` ตอนโชว์):

```promql
# K: failure ratio 24h (สัญญาณดีกว่า count ดิบ)
sum(increase(strimzi_reconciliations_failed_total{namespace="nsp-th-u-kafka"}[24h]))
  / clamp_min(sum(increase(strimzi_reconciliations_total{namespace="nsp-th-u-kafka"}[24h])), 1)

# L: locked reconciliations 24h (contention)
sum(increase(strimzi_reconciliations_locked_total{namespace="nsp-th-u-kafka"}[24h])) or vector(0)

# M: resources NotReady ตอนนี้ (ขณะ resource_state ยังมี — ก่อน 0.51)
count(strimzi_resource_state{namespace="nsp-th-u-kafka"} == 0) or vector(0)

# N: p50 duration (คู่กับ p95 เดิม — เห็น distribution)
histogram_quantile(0.50, sum(rate(strimzi_reconciliations_duration_seconds_bucket{namespace="nsp-th-u-kafka"}[24h])) by (le)) or vector(0)

# O: operator uptime วินาที  [VERIFY A6: ต้องมี process_start_time_seconds]
time() - max(process_start_time_seconds{namespace="nsp-th-u-kafka", job=~".*strimzi.*"})
```
เพิ่มใน description:
```
🔄 Failure ratio (24h): {{ printf "%.1f%%" (mul $values.K.Value 100.0) }}
🔒 Locked (24h):        {{ $values.L.Value }}
🔴 NotReady now:        {{ $values.M.Value }}
⏱️  p50/p95:            {{ printf "%.2f" $values.N.Value }}s / {{ printf "%.2f" $values.I.Value }}s
🟢 Operator uptime:     {{ printf "%.0f" (div $values.O.Value 3600.0) }}h
```

## B2. NEW alert rules (เพิ่มจาก metric เดิม)

### A9 — Reconcile failure RATIO สูง (ดีกว่านับ count ดิบ) ✅ ready
```promql
sum by (kind)(increase(strimzi_reconciliations_failed_total{namespace="nsp-th-u-kafka"}[1h]))
  / sum by (kind)(increase(strimzi_reconciliations_total{namespace="nsp-th-u-kafka"}[1h]))
> 0.5
```
- **เช็ค:** ใน 1 ชม. reconcile ของ kind นั้น fail เกิน 50% = systemic (ไม่ใช่ fail ครั้งเดียว). `for: 15m`, severity warning
- ต่างจาก A1 (ยิงทุก fail) → อันนี้ยิงเฉพาะ "fail เยอะเป็นสัดส่วน" = ลด noise

### A10 — Operator เห็น resource = 0 / metric หาย (catastrophic) ✅ ready
```promql
absent(strimzi_resources{namespace="nsp-th-u-kafka"})
```
- **เช็ค:** operator ไม่เห็น resource เลย (โดนลบเกลี้ยง หรือ scrape พัง). `for: 5m`, severity critical, `noDataState: Alerting`

### A11 — ANY resource NotReady (generalize A8 → ทุก kind) ✅ ready (แทน A8 เดิม)
```promql
count by (kind, name) (strimzi_resource_state{namespace="nsp-th-u-kafka"} == 0) > 0
```
- **เช็ค:** resource ใดๆ NotReady (Kafka/Connect/Bridge/... ไม่ใช่แค่ connector) — ใช้ **`count` (แก้ bug A8)**
- ⚠️ resource_state deprecated 0.51 + verify coverage (A5). semantics = CR Ready ไม่ใช่ Debezium task
- summary: `[CRITICAL] {{ $labels.kind }}/{{ $labels.name }} NotReady`

### A12 — Operator RESTART detection 🎯 (ตรงกับ incident ของคุณ) [VERIFY A6]
```promql
changes(process_start_time_seconds{namespace="nsp-th-u-kafka", job=~".*strimzi.*"}[1h]) > 0
```
- **เช็ค:** operator pod restart ใน 1 ชม. (start_time เปลี่ยน) — **นี่คือ incident restart ที่คุณเจอ!** จับได้ทันที
- ⚠️ ใช้ได้ก็ต่อเมื่อ A6 เจอ `process_start_time_seconds`. `for: 0`, severity warning
- (fallback ถ้าไม่มี process metric: `resets(...)` counter ใดๆ หรือรอ kube-state-metrics)

### A13 — Operator memory สูง [VERIFY A6]
```promql
max(jvm_memory_used_bytes{namespace="nsp-th-u-kafka", job=~".*strimzi.*", area="heap"})
  / max(jvm_memory_max_bytes{namespace="nsp-th-u-kafka", job=~".*strimzi.*", area="heap"})
> 0.85
```
- **เช็ค:** heap > 85% = operator ใกล้ OOM (เกี่ยวกับ restart loop). `for: 10m`, warning. [ต้องมี jvm metric]

## B3. สรุป: เพิ่มได้ตอนนี้กี่อัน
| จาก metric เดิม | ทำได้เลย | ต้อง verify A6 ก่อน |
|---|---|---|
| Heartbeat +5 query (K-O) | K,L,M,N | O (uptime) |
| Alert ใหม่ | A9 (ratio), A10 (wipe), A11 (any-NotReady=แทน A8) | A12 (restart)⭐, A13 (memory) |

> **highlight:** A12 (operator restart) ตอบ incident ของคุณตรงๆ — ถ้า A6 เจอ `process_start_time_seconds` = ได้ alert restart **ฟรี ไม่ต้อง kube-state-metrics**

## B4. สิ่งที่ยัง**ทำไม่ได้**จนกว่าจะ deploy exporter (อย่าเสียเวลาลอง)
- Debezium **task RUNNING/FAILED + source lag** → ต้อง **Connect JMX** (สำคัญสุดสำหรับ CDC)
- **consumer lag / under-replicated / offline partition** → Kafka JMX + Kafka Exporter
- **pod CrashLoop/OOMKill/PVC-full** (ละเอียดกว่า A12) → kube-state-metrics
