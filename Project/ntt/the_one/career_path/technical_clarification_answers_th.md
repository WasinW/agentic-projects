# Technical Clarification — คำตอบ (ภาษาไทย)

> อ้างอิงจากประสบการณ์จริงจาก NTT DATA (The 1 Central Group) และ SCB Data-X
> ส่วนไหนที่ประสบการณ์ยังไม่ลึกจะบอกตรงๆ

---

## 1. Lakehouse Project ที่ซับซ้อนที่สุด — End-to-End Architecture

**โปรเจค:** Loyalty Data Platform — The 1 Central Group (NTT DATA, 2025–ปัจจุบัน)

**บริบท:** The 1 เป็นโปรแกรมสะสมแต้มรายใหญ่ที่สุดของไทย แพลตฟอร์มต้อง ingest ข้อมูลแบบ real-time จาก Confluent Kafka และ batch จาก PostgreSQL กับ REST APIs เข้าสู่ analytics layer สำหรับทีม downstream

**สถาปัตยกรรมทั้งหมด:**

```
[Sources]                    [Processing]              [Storage - Two-Layer Lakehouse]
Confluent Kafka ──────┐
  (Avro/JSON)         ├──→ Apache Beam ──→ Dataflow ──→ Apache Iceberg (GCS)  ← Source of truth
PostgreSQL ───────────┤      (Python)                    │
REST APIs ────────────┘                                  ↓ (refined transforms)
                                                       BigQuery (CDC)  ← Analytics/refined layer
```

- **Storage:** Google Cloud Storage (GCS) เป็น Iceberg warehouse, BigQuery เป็น refined analytics layer
- **Compute:** Apache Beam pipelines รันบน Google Cloud Dataflow (ทั้ง streaming และ batch runners)
- **Table Format:** Apache Iceberg สำหรับ source layer — เลือกเพราะรองรับ schema evolution, time-travel และแยก storage กับ compute ออกจากกัน
- **Catalog:** Migrate จาก Hadoop Catalog ไปเป็น BigLake Managed Storage (BLMS) REST Catalog พร้อม Google-managed vended credentials เป็น migration ที่สำคัญ — Hadoop Catalog ต้องจัดการ metadata เอง และไม่ integrate กับ GCP แบบ native ในขณะที่ BLMS REST มี automatic catalog registration, IAM-based access control และเชื่อมกับ BigQuery ได้เลย
- **Partitioning:** Iceberg tables partition ด้วย ingestion date (integer YYYYMMDD) สำหรับ source layer ส่วน BigQuery refined tables partition ด้วย DATE (DAY granularity) พร้อม clustering บน field ที่มี high cardinality
- **Write Pattern:** ใช้ Apache Beam `managed.Write` transform กับ IcebergIO — pipeline เขียนตรงไป Iceberg ผ่าน BLMS REST โดย table จะถูกสร้างอัตโนมัติตอน write ครั้งแรก ไม่ต้องมี script สร้าง table ล่วงหน้า

**ปัญหา Small-File และ Read Performance:**

Small-file problem เป็นปัญหาที่มากับ streaming writes โดยธรรมชาติ — แต่ละ Dataflow worker สร้าง Parquet files เล็กๆ ทุก commit:
- **Managed.Write จัดการ file sizing** — Beam's managed Iceberg writer batch records ก่อน commit ลด file count เมื่อเทียบกับ per-record writes
- **Partition strategy** — ใช้ DAY partition (ไม่ใช่ HOUR) ลดจำนวน partition และรวม files ไว้ใน directory น้อยลง
- **Read performance** — Read path หลักคือ BigQuery (refined layer) ไม่ใช่ Iceberg โดยตรง BigQuery อ่าน Iceberg ผ่าน BigLake external tables ซึ่ง query engine ของ BigQuery จัดการ file scanning ได้ดี สำหรับ Iceberg source layer ใช้อ่านเพื่อ reconciliation และ debugging เป็นหลัก

> **หมายเหตุ:** ยังไม่จำเป็นต้องทำ compaction jobs เพราะ data volume ปัจจุบันยังไม่มีปัญหา small-file รุนแรง ถ้า scale ขึ้น จะใช้ Iceberg `rewrite_data_files` หรือ scheduled compaction pipeline

---

## 2. CDC, Schema Evolution และ Deterministic Replay

**CDC Implementation (The 1 — NTT DATA):**

Implement CDC ที่ BigQuery refined layer โดยใช้ BigQuery Storage Write API กับ primary keys:

- **UPSERT pattern:** BigQuery table แต่ละตัวมี primary key ที่กำหนดไว้ (เช่น composite key) records ที่เข้ามาจะเขียนด้วย CDC semantics — BigQuery deduplicate ตาม primary key อัตโนมัติ

- **DELETE pattern:** สำหรับกรณีที่ข้อมูลถูกลบจาก upstream ต้องออกแบบ verification flow:
  - Pipeline ได้รับ Kafka event
  - เรียก upstream API — ถ้าไม่เจอข้อมูลใน API response แสดงว่าอาจเป็น DELETE
  - ก่อน DELETE จริง pipeline query BigQuery เพื่อยืนยันว่า record มีอยู่จริง (ป้องกัน phantom deletes)
  - ทำ DELETE เฉพาะเมื่อผ่านทุก check

  เป็น design challenge จริงๆ — ถ้าทำแบบง่ายๆ อาจ delete ข้อมูลผิดตอน API outage หรือ race condition การ check หลายชั้นทำให้มั่นใจว่า delete เฉพาะสิ่งที่ถูกลบจริง

- **CDC table setup:** Primary keys ประกาศเป็น `NOT ENFORCED` ใน BigQuery (BigQuery ไม่ enforce uniqueness แต่ Storage Write API ใช้สำหรับ CDC semantics)

**Schema Evolution:**

- **Iceberg layer:** `managed.Write` จัดการ schema evolution ได้ — ถ้ามี field ใหม่ Iceberg เพิ่มเข้าไปอัตโนมัติ แต่เราก็ควบคุม schema อย่างชัดเจนผ่าน PyArrow schema definitions เพื่อป้องกัน unintended drift
- **BigQuery layer:** ใช้ deployment tooling เปรียบเทียบ live schema กับ JSON schema definitions ใน repo แล้ว `ALTER TABLE ADD COLUMN` สำหรับ field ใหม่ ไม่เคย drop หรือ modify column ที่มีอยู่
- **ตัวอย่างจริง:** เคย rename partition field จาก `etlLoadTime` (INT, YYYYMMDDHH, HOUR partition) เป็น `ingestedTHDate` (INT, YYYYMMDD / DATE, DAY partition) ข้าม 14 ไฟล์ ต้องแก้ทั้ง Iceberg writer configs, BigQuery schemas, SQL init scripts และ pipeline transforms — มี 220 tests validate ความถูกต้อง

**Deterministic Replay:**

- **Streaming pipelines:** Dataflow มี exactly-once processing guarantees พร้อม checkpointing ถ้า pipeline fail จะ resume จาก Kafka offset ล่าสุด รวมกับ CDC UPSERT ใน BigQuery ทำให้ replayed records overwrite ตัวเอง — output เป็น idempotent
- **Batch pipelines:** Parameterized ด้วยวันที่ — รันซ้ำด้วยวันเดิมได้ผลเหมือนเดิม เป็น deterministic

> **หมายเหตุ:** ไม่ได้ใช้ Talend — CDC และ replay ทั้งหมดสร้างบน Apache Beam + Dataflow + BigQuery Storage Write API

---

## 3. Data-Freshness SLAs — Ingestion Cadence, Streaming vs Batch

**การออกแบบ SLA (The 1 — NTT DATA):**

มี freshness สองระดับ:

| Pipeline | Type | Cadence | Target Freshness |
|----------|------|---------|-----------------|
| Events (streaming) | Streaming | Continuous | Near real-time (วินาที-นาที) |
| Master data | Batch | Daily 1AM BKK (UTC+7) | D-1 |
| Historical data | Batch | Daily 1AM BKK (UTC+7) | D-1 |

**Streaming:**
- Confluent Kafka consumer รันบน Dataflow streaming runner
- Dataflow จัดการ checkpointing อัตโนมัติ — Kafka offsets commit หลัง process สำเร็จ
- Watermarking จัดการผ่าน Beam windowing — ใช้ GlobalWindows สำหรับ Iceberg write (append-only) ส่วน BigQuery refined write ใช้ event timestamp กำหนด partition
- Pipeline รันต่อเนื่อง — ไม่ใช่ micro-batch ข้อมูลพร้อมใช้ใน BigQuery ภายในไม่กี่นาทีหลัง Kafka event ถูก produce

**Batch:**
- Trigger ด้วย Cloud Scheduler เวลา 1AM เวลาไทยทุกวัน
- Pipeline อ่านจาก upstream source (REST API, PostgreSQL) แล้วเขียนไป Iceberg + BigQuery
- "D-1" หมายความว่าข้อมูลของเมื่อวานพร้อมใช้ตอนเช้า — ทีม analytics มีข้อมูลพร้อมตอนเริ่มงาน

**ทำไมเลือก Streaming vs Batch:**
- Events ที่ต้อง real-time เพราะ business ต้องการตอบสนองทันที
- Master data และ history เป็น batch เพราะเปลี่ยนไม่บ่อย — daily load เพียงพอและ operate ง่ายกว่า

**Checkpointing:**
- Streaming: Dataflow built-in checkpointing กับ Kafka offset tracking ถ้า pipeline crash จะ resume จาก offset ล่าสุด
- Batch: ไม่ต้อง checkpointing — pipeline เป็น idempotent รันซ้ำได้ผลเดิม

---

## 4. Data Quality และ Observability Stack

**Pipeline-Level Quality (The 1 — NTT DATA):**

- **Schema validation ตอน ingestion:** pipeline validate message ที่เข้ามากับ schema ที่คาดไว้ มี multi-format auto-detection ทำให้จัดการ Kafka message ได้ทุกรูปแบบโดยไม่สูญเสียข้อมูล
- **Transform validation:** Transformers มี checks สำหรับ null handling, type coercion, timezone conversion (UTC → Bangkok UTC+7) record ที่ invalid จะถูก log ไม่ใช่ drop แบบเงียบๆ
- **CDC consistency checks:** การ verify หลายชั้นก่อน DELETE ก็เป็น data quality measure ในตัว — ป้องกัน false deletes

**Testing เป็น Quality Gate:**
- Unit tests (pytest) ครอบคลุมทุก pipeline projects — ทั้ง message parsing, API integration, CDC logic, schema validation, timestamp handling และ edge cases
- Static typing (mypy) จับ type mismatches ตั้งแต่ development
- Linting (ruff) และ SonarQube enforce code quality standards
- Pre-commit hooks + GitLab CI ทำให้ code ที่ไม่ผ่าน test ไม่ถูก deploy

**Monitoring และ Observability:**
- Dataflow มี built-in metrics: throughput, latency, backlog size, error counts — ดูได้ใน GCP Console
- Pipeline failures trigger Dataflow alerts
- Batch pipelines ใช้ Cloud Scheduler + Dataflow job status เป็น freshness monitoring พื้นฐาน

**Data Platform Level (SCB Data-X):**
- ที่ SCB ทำ data validation เป็นงานหลักบน Azure Databricks — ตรวจ row counts, null ratios, schema consistency ระหว่าง source databases กับ data warehouse
- Schema synchronization processes (PySpark บน Databricks) ตรวจจับและ reconcile schema drift

> **หมายเหตุ:** ยังไม่ได้ใช้ dedicated observability platform (เช่น Monte Carlo หรือ Great Expectations) ที่ The 1 Observability อาศัย Dataflow built-in metrics + manual monitoring เป็นหลัก ถ้ามีโอกาสพัฒนาเพิ่ม จะแนะนำ structured DQ metrics (row counts, null rates, freshness timestamps) และ alerting ผ่าน Cloud Monitoring

---

## 5. Performance Tuning บน Spark Job ระดับ Terabyte

**บริบท (SCB Data-X — RDT Project):**

โปรเจค Regulatory Data Transformation (RDT) ที่ SCB ประมวลผล regulatory data ของธนาคารบน Azure Databricks ด้วย PySpark ข้อมูลมีขนาดใหญ่ (multi-TB จาก transaction และ account data)

**คอขวดที่พบ:**
- **Shuffle-heavy joins:** Regulatory models ต้อง join หลายตาราง (accounts, transactions, customers) naive joins ทำให้ shuffle มากเกินไป Spark stages ใช้เวลาส่วนใหญ่กับ network I/O
- **Skewed keys:** บาง account types มี transactions มากกว่าปกติ ทำให้เกิด task skew ใน joins
- **Schema sync overhead:** กระบวนการ schema synchronization เปรียบเทียบ schemas ข้าม databases ซึ่งบน datasets ใหญ่ต้อง full-table scans

**วิธีแก้:**
- **Broadcast joins:** สำหรับ dimension tables ขนาดเล็ก (reference/lookup) ใช้ broadcast hints เพื่อไม่ต้อง shuffle เลย — driver ส่ง table เล็กไปทุก executor
- **Partition pruning:** ใช้ partition columns ใน filter predicates เพื่อให้ Spark ข้าม partitions ที่ไม่เกี่ยว
- **Repartitioning ก่อน join:** สำหรับ large-to-large joins repartition ทั้งสองฝั่งด้วย join key ก่อน join เพื่อลด shuffle — ให้ matching keys อยู่บน partition เดียวกัน
- **Cache intermediate results:** สำหรับ models ที่ใช้ dataset เดิมหลายรอบ cache intermediate DataFrame เพื่อไม่ต้อง compute ซ้ำ

**Apache Beam / Dataflow (The 1 — NTT DATA):**

บน Dataflow (ไม่ใช่ Spark แต่หลักการ performance คล้ายกัน):
- **Fan-out optimization:** แทนที่จะ process แต่ละ output table ใน pipeline แยก (อ่าน Kafka ซ้ำ) ออกแบบ fan-out pattern — Kafka consumer เดียว แตก branch ไปหลาย writers ลด Kafka read load และจำนวน Dataflow workers
- **Cross-bundle deduplication:** เปลี่ยนจาก per-bundle in-memory dedup (ที่ miss duplicates ข้าม bundles) เป็น GroupByKey-based dedup สำหรับ cross-bundle deduplication ที่เชื่อถือได้
- **Partition field optimization:** เปลี่ยนจาก HOUR เป็น DAY partition granularity เพื่อลดจำนวน Iceberg file commits และ BigQuery partition maintenance

> **หมายเหตุ:** ประสบการณ์ Spark tuning ลึกที่สุดมาจาก SCB Data-X บน Databricks ที่ The 1 ใช้ Apache Beam บน Dataflow ซึ่ง performance tuning เน้นเรื่อง pipeline topology (fan-out, dedup strategy, worker scaling) มากกว่า Spark-specific knobs (shuffle partitions, join strategies)

---

## 6. Data Governance — PII Masking และ Access Control

**SCB Data-X (ธนาคาร — ข้อมูลความลับสูง):**

ข้อมูลธนาคารที่ SCB มีข้อกำหนดด้าน regulatory เข้มงวด (ข้อกำหนดของธนาคารแห่งประเทศไทย)

- **RBAC implementation:** พัฒนาระบบ Role-Based Access Control บน Azure Databricks ทีมต่างๆ (risk, compliance, analytics) มีระดับ access ต่างกันสำหรับ datasets เดียวกัน implement ผ่าน Databricks workspace permissions และ Unity Catalog access policies
- **Data classification:** ส่วนหนึ่งของ RDT CardX project — profile data sources เพื่อจำแนก fields ตามระดับ sensitivity ก่อน migrate ไป platform ใหม่

**The 1 — NTT DATA (Retail Loyalty):**

- **Secret management:** Credentials ทั้งหมด (Kafka, API, database) เก็บใน GCP Secret Manager อ้างอิงผ่าน service account — ไม่มี secrets ใน code หรือ config files
- **IAM per-collector:** แต่ละ pipeline มี GCP service account ของตัวเองด้วย least-privilege access IAM bindings กำหนดใน Terraform — แต่ละ collector เข้าถึงได้เฉพาะ datasets ของตัวเองใน BigLake และ BigQuery
- **Network isolation:** Dataflow jobs รันใน VPC subnets ที่ controlled network access

> **หมายเหตุ:** ยังไม่เคย implement column-level PII masking (เช่น dynamic masking, tokenization) ใน production ประสบการณ์ governance เน้นที่ access control และ infrastructure level (RBAC, IAM, secret management) สำหรับ PII masking เข้าใจ patterns (BigQuery column-level security, policy tags, Data Catalog) แต่ยังไม่ได้ implement end-to-end

---

## 7. Production Incident ที่กระทบ Data Freshness

**Incident: Schema C — Kafka Messages รูปแบบไม่คาดคิดใน STG (The 1, 2025)**

**เกิดอะไรขึ้น:**
หลัง deploy pipeline ไป STG ครั้งแรก pipeline start สำเร็จแต่ BigQuery refined tables มี fields เป็น empty/null Iceberg source layer แสดง payload structure ที่ซ้อนกันผิดปกติ

**การ Triage:**
1. ตรวจ Dataflow logs — ไม่มี errors pipeline running ปกติ
2. ตรวจ Iceberg source data — เจอ `payload.payload.{actual_fields}` แทนที่จะเป็น `payload.{actual_fields}`
3. ตรวจ raw Kafka messages — พบว่า messages มาในรูปแบบที่ไม่คาดคิด: `{"message": "<stringified JSON>"}` ซึ่ง inner value เป็น **string** ไม่ใช่ parsed JSON object
4. Root cause: Kafka producer (ไม่ใช่ทีมเรา) wrap messages ใน outer `message` key โดย serialize original JSON เป็น string Pipeline เราจัดการได้แค่สองรูปแบบ (flat JSON กับ nested `payload` dict) — รูปแบบที่สามนี้ไม่มี document

**การแก้ไข:**
เพิ่ม three-schema detection flow ใน message transformer:
1. **Schema C** (ใหม่): ตรวจพบ `message` key ที่มีค่าเป็น string → parse string → extract inner payload
2. **Schema B**: ตรวจพบ `payload` key เป็น dict → unwrap inner payload
3. **Schema A**: flat message → wrap เป็น payload

แก้ไขและ deploy ได้ภายในวันเดียว เพิ่ม regression tests สำหรับ Schema C

**การป้องกัน:**
- เพิ่ม schema detection tests สำหรับทุก message format ที่รู้จัก
- ประสานกับทีม Kafka platform เพื่อ document message envelope formats ทั้งหมด
- Multi-format auto-detection pattern กลายเป็น standard สำหรับทุก Kafka consumers — จัดการ format ที่ไม่คุ้นเคยได้แทนที่จะทำข้อมูลเสียแบบเงียบๆ

**Incident: Kafka Config Migration — Silent Timeout (The 1, 2025)**

**เกิดอะไรขึ้น:**
หลัง migrate โครงสร้าง Kafka credentials ใน Secret Manager (เปลี่ยนชื่อ key) pipeline deploy สำเร็จแต่ Kafka consumer timeout เงียบๆ — ไม่มี events ถูกอ่านเลย

**การ Triage:**
1. Pipeline ไม่แสดง errors — Dataflow job "running" แต่ process records เป็นศูนย์
2. ตรวจ Kafka consumer lag — เพิ่มขึ้นเรื่อยๆ แสดงว่า consumer ไม่ได้อ่าน
3. พบว่า pipeline code ยังอ่าน secret key ชื่อเดิม — secret มีอยู่แต่ไม่มีค่าภายใต้โครงสร้างใหม่ Kafka client จึง initialize ด้วย credentials ว่างแล้ว timeout

**การแก้ไข:**
อัพเดท secret key references ใน pipeline configuration เพิ่ม validation ตอน pipeline startup ให้ fail-fast ถ้า credential fields ว่างหรือหายไป

**การป้องกัน:**
- เพิ่ม configuration validation ตอน pipeline initialization — ถ้า required secret fields ว่าง pipeline fail ทันทีด้วย error message ชัดเจน แทนที่จะเสื่อมประสิทธิภาพแบบเงียบๆ
- Document โครงสร้าง secret key และใส่ใน deployment checklist
