# Guideline — เพิ่ม exporter/metric (สำหรับตอนได้ requirement)

> ไว้ตอนจะเพิ่ม metric ที่ operator metrics ให้ไม่ได้ (Debezium task/lag, consumer lag, partition health, pod restart).
> คู่กับ `strimzi_verify_and_additions.md` (§B4 = ตัวที่ต้อง exporter). env `nsp-th-u-kafka`. repos: `dtp_kafka_{build_ci,cluster,connector}`.
> 🔒 generic pattern — ไม่มี AIA config จริง.

---

## 0. หลักการก่อน (แก้ความเข้าใจผิดสำคัญ)

**"เพิ่ม metric = ต้อง rebuild image + restart ทุก topic" — จริงแค่บางเคส:**
- **JMX exporter agent อยู่ใน Strimzi image อยู่แล้ว** → เปิด metric ส่วนใหญ่ = **แก้ CR (config) ไม่ใช่ rebuild image**
- ตัวที่กระทบ broker จริง = **broker JMX เท่านั้น** (แก้ Kafka CR → rolling restart broker ทีละตัว) — แต่ก็ยังเป็น rolling ไม่ใช่ down ทั้ง cluster
- **Kafka Exporter, kube-state-metrics ไม่แตะ broker เลย** (คนละ pod)

**🔑 gate จริง = Prometheus scrape ยังไง (verify ครั้งเดียว):**
```bash
kubectl get podmonitor,servicemonitor -n nsp-th-u-kafka 2>/dev/null
```
- ถ้ามี **PodMonitor/ServiceMonitor** (Prometheus Operator) → เปิด metric = แค่แก้ CR แล้ว Prometheus เห็นเอง = **เบา**
- ถ้า **baked scrape config** (Prometheus config ฝังใน image/configmap) → ต้องเพิ่ม scrape target + redeploy Prometheus ด้วย = **หนักขึ้น** (นี่คือที่คุณเคยเจอว่า "ต้อง rebuild")

---

## 1. ตารางตัดสินใจ — ทำ low-impact ก่อน

| # | Exporter | ปลดล็อก | แก้ที่ (CR/repo) | rebuild image? | กระทบ restart | effort |
|---|---|---|---|---|---|---|
| 1 | **Kafka Exporter** | consumer lag, topic offset | `spec.kafkaExporter` บน Kafka CR (`dtp-kafka_cluster`) | ❌ | **ไม่แตะ broker** (pod แยก) | 🟢 ต่ำสุด |
| 2 | **kube-state-metrics** | pod restart/OOM/CrashLoop/PVC + ตัวแทน `resource_state` | deploy standalone (manifest/Helm) | ❌ | ไม่แตะ Kafka | 🟢 ต่ำ |
| 3 | **Connect JMX** | **Debezium task RUNNING/FAILED, source lag, snapshot** ⭐ | `spec.metricsConfig` บน KafkaConnect CR (`dtp-kafka_cluster`) | ❌ (agent มีใน image) | rolling restart **Connect** (ไม่ใช่ broker) | 🟡 กลาง |
| 4 | **Broker JMX** | under-replicated/offline partition, ISR, broker JVM | `spec.kafka.metricsConfig` บน Kafka CR | ❌ (agent มีใน image) | **rolling restart broker ทุกตัว** | 🔴 สูงสุด (ต้อง change window) |

**ลำดับแนะนำตาม value×impact:** (1) Kafka Exporter → (3) Connect JMX → (2) KSM → (4) Broker JMX ท้ายสุด

---

## 2. รายละเอียดแต่ละตัว

### ① Kafka Exporter — consumer lag (ทำก่อน, ไม่แตะ broker)
เพิ่มใน **Kafka CR** (`dtp-kafka_cluster`):
```yaml
spec:
  kafkaExporter:
    topicRegex: ".*"
    groupRegex: ".*"
    # resources: {...}
```
- operator สร้าง **pod ใหม่** (kafka-exporter) — ต่อ Kafka แบบ consumer อ่าน lag → **ไม่ restart broker**
- Prometheus: scrape pod นี้ (PodMonitor `strimzi.io/kind: KafkaExporter` หรือ port 9404)
- ปลดล็อก: `kafka_consumergroup_lag`, `kafka_topic_partitions`, offset → **alert consumer lag ได้** (ตัวสำคัญของ seam)

### ② kube-state-metrics — pod health + resource_state replacement
- deploy **standalone** (Helm `kube-state-metrics` หรือ manifest) ใน cluster — **ไม่เกี่ยวกับ Kafka image/CR**
- + ใส่ **Strimzi CustomResourceState config** (จาก `strimzi examples/metrics`) → ได้ `strimzi_kafka_resource_info{ready="true|false"}` = **ตัวแทน `resource_state` ที่ deprecated (survive 0.51)**
- Prometheus: scrape KSM service
- ปลดล็อก: `kube_pod_container_status_restarts_total`, CrashLoopBackOff, OOMKilled, PVC usage → **pod-level restart/OOM (ละเอียดกว่า A12)** + resource-ready ยั่งยืน

### ③ Connect JMX — Debezium task health ⭐ (value สูงสุดสำหรับ CDC)
เพิ่มใน **KafkaConnect CR** (`dtp-kafka_cluster`):
```yaml
spec:
  metricsConfig:
    type: jmxPrometheusExporter
    valueFrom:
      configMapKeyRef:
        name: connect-metrics        # ConfigMap เก็บ JMX exporter rules
        key: metrics-config.yml
```
- + สร้าง ConfigMap `connect-metrics` (rules จาก Strimzi `examples/metrics/kafka-connect-metrics.yaml`)
- **ไม่ rebuild image** (agent มีอยู่) แต่ operator **rolling restart Connect pods** (ไม่ใช่ broker) — connector ค้าง connect ใหม่ ~นาที
- Prometheus: scrape port 9404 ของ Connect
- ปลดล็อก: `kafka_connect_connector_task_status` (RUNNING/FAILED), `debezium_metrics_MilliSecondsBehindSource` (source lag), snapshot progress → **แก้ blind spot A8 ที่แท้จริง** (task state จริง ไม่ใช่แค่ CR Ready)

### ④ Broker JMX — partition health (impact สูงสุด, ทำท้าย)
เพิ่มใน **Kafka CR** `spec.kafka.metricsConfig` (pattern เดียวกับ ③ + ConfigMap `kafka-metrics`)
- **ไม่ rebuild image** แต่ **rolling restart broker ทุกตัว** (KafkaRoller ทีละตัว) → ต้อง **change window** (แต่ละ broker down ชั่วครู่, rolling = ไม่ down ทั้ง cluster ถ้า RF≥3 + minISR ตั้งถูก)
- ปลดล็อก: `kafka_server_replicamanager_underreplicatedpartitions`, offline partition, ISR shrink, request rate, controller, JVM

---

## 3. Deploy path (ตาม flow เดิมของคุณ)
```
CR/ConfigMap change (dtp-kafka_cluster)
  → Bitbucket → Jenkins → kubectl apply -f (raw manifest)
  → Strimzi operator reconcile
     → ①②: สร้าง pod ใหม่ (ไม่ restart broker)
     → ③: rolling restart Connect
     → ④: rolling restart brokers (KafkaRoller)
```
- **ไม่แตะ `dtp_kafka_build_ci`** (ไม่ rebuild image) — **ยกเว้น** ถ้า custom image ของคุณตัด JMX agent ออก → ต้องเช็คว่า base ยังมี `/opt/prometheus/jmx_prometheus_javaagent` (Strimzi image มาตรฐานมี)
- **KSM (②)** = คนละ manifest/deploy (ขอ infra หรือ add ใน cluster repo)

## 4. Checklist ตอนจะทำจริง (ต่อ exporter)
- [ ] verify Prometheus ใช้ PodMonitor หรือ baked scrape (§0) — ตัดสิน effort
- [ ] ถ้า PodMonitor: มี PodMonitor ครอบ label ของ target ใหม่มั้ย (บางที ต้องเพิ่ม)
- [ ] ทำใน UAT (`nsp-th-u-kafka`) ก่อน → ดู metric ขึ้น Prometheus → ค่อย PROD
- [ ] ④ broker JMX: เช็ค RF≥3 + min.insync.replicas ก่อน rolling restart (กัน topic ขาด)
- [ ] เพิ่ม alert rule ใหม่ที่ปลดล็อก (consumer lag, task FAILED, under-replicated, pod restart)

---

## 5. สรุป 1 บรรทัด
เกือบทุก exporter = **แก้ CR ไม่ rebuild image**; ทำ **Kafka Exporter (lag) + Connect JMX (Debezium task) ก่อน** (ไม่แตะ broker/แตะแค่ Connect) — **broker JMX ทำท้ายสุด** (ตัวเดียวที่ rolling restart broker). gate จริง = **PodMonitor vs baked scrape** ต้อง verify ครั้งเดียว
