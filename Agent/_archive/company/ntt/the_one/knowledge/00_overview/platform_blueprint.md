# Modern Data & AI Platform — Architect's Blueprint

> เอกสารตกผลึก สำหรับ Wasin
> เขียนในมุม **Expert Data & AI Architect + Enterprise Solution Architect**
> ตอบตรงประเด็นที่คุยใน Gemini chat — แก้จุดที่ Gemini ตอบไม่ครบ/ตอบจาก outdated docs
> Last update: 2026-05

---

## 0. ทำไมคุณถึง "หลงทาง" — ก่อนอื่นต้องเข้าใจสาเหตุ

ก่อนตอบเรื่อง pattern, tech stack หรือ Spark vs Beam ผมขอวินิจฉัยปัญหาที่คุณบอกว่า "พอรู้เยอะแล้วสับสน" ก่อนครับ:

### 3 อาการที่ทำให้คนสาย Data Architect หลงทาง

| อาการ | สาเหตุที่แท้จริง | วิธีแก้ |
|---|---|---|
| **1. Tool-first thinking** | เริ่มจาก "ใช้ Databricks vs ใช้ Dataflow ดี?" แทนที่จะเริ่มจากโจทย์ business | บังคับตัวเองเขียน **Workload Profile** ก่อน (ดูส่วนที่ 2) |
| **2. Architecture-as-religion** | มอง Lakehouse/Mesh/Fabric เป็น "ค่าย" ที่ต้องเลือกข้าง | ปี 2026 ของจริงคือ **ผสม 3 แบบนี้** ในระบบเดียว |
| **3. Pattern envy** | เห็น Netflix/Uber ทำแบบนี้ก็อยากทำตาม | ขนาดและทีมต่างกันคนละชั้น — เลือก pattern ตาม **maturity ขององค์กร** ไม่ใช่ตามแฟชั่น |

### แกนที่ต้องยึด — 4 มิติ ไม่ว่าจะเป็น Platform ไหน

ถ้าคุณงงครั้งหน้า ให้กลับมาที่ 4 มิตินี้เสมอ:

```
                  ┌─────────────────────────┐
                  │   1. STORAGE LAYER      │  Where data sits at rest
                  │   (Open / Closed format)│  → Iceberg, Delta, BQ native
                  └─────────────────────────┘
                              │
                  ┌─────────────────────────┐
                  │   2. COMPUTE LAYER      │  How data gets transformed
                  │   (Engine + Runtime)    │  → Spark, Beam, BQ, Trino
                  └─────────────────────────┘
                              │
                  ┌─────────────────────────┐
                  │   3. ORCHESTRATION /    │  How pipelines are built/run
                  │      INTERFACE LAYER    │  → Airflow, dbt, Config-driven
                  └─────────────────────────┘
                              │
                  ┌─────────────────────────┐
                  │   4. GOVERNANCE LAYER   │  Trust, lineage, contracts
                  │                         │  → Unity, Dataplex, DataHub
                  └─────────────────────────┘
```

**กฎเหล็ก**: เวลาออกแบบ ห้ามให้ tool ของชั้นใดชั้นหนึ่งกระโดดข้ามไปกลืนชั้นอื่น
- BigQuery กลืนทั้ง Storage + Compute = vendor lock-in
- Databricks กลืนทั้ง 4 ชั้น = ง่ายแต่ผูกขาด
- Dataflow ทำได้แค่ชั้น 2 = ห้ามฝืนให้เป็น "platform"

---

## 1. Decision Framework — ก่อนเลือก Architecture ตอบ 5 คำถามนี้

ทุกครั้งที่ต้องออกแบบหรือ defend architecture เริ่มจาก 5 คำถามนี้ ตอบให้ครบก่อน:

### Q1. Latency SLA จริงๆ คืออะไร? (ไม่ใช่ที่ business บอก)

| SLA | Pattern ที่เหมาะ | ตัวอย่าง Use case |
|---|---|---|
| < 1 second | True Streaming (Beam/Flink + Online Feature Store) | Fraud detection, real-time bidding |
| 1 sec – 5 min | Micro-batch (Spark Structured Streaming, Beam Streaming) | Real-time CRM, contextual marketing |
| 5 – 60 min | Mini-batch / scheduled trigger | Near real-time dashboards |
| Hourly / Daily | Batch ELT (dbt + warehouse) | Reporting, ML training |

**เคล็ดลับ**: 80% ของโจทย์ที่ business บอกว่า "real-time" จริงๆ คือ near real-time (5–15 นาที) เพียงพอแล้ว — ใช้คำถามนี้:
> "ถ้าข้อมูล delay 5 นาที จะเสียเงินจริงๆ เท่าไหร่?"

### Q2. Data Volume / Cardinality ขนาดไหน?

- **< 100 GB/วัน, simple schema** → ไม่ต้องคิดมาก ใช้ BQ + Dataform / Snowflake + dbt จบ
- **100 GB – 10 TB/วัน, complex transform** → ต้อง Lakehouse จริงจัง (Iceberg/Delta + Spark/Beam)
- **> 10 TB/วัน + ต้อง join ข้าม domain** → ต้อง Data Mesh + Open table format

### Q3. Team Maturity จริงๆ มีกี่คน เก่งระดับไหน?

| ขนาดทีม DE | Architecture ที่เหมาะ | ห้ามทำอะไร |
|---|---|---|
| 1–3 คน | Managed PaaS (BQ + dbt + Airflow managed) | ห้ามสร้าง custom framework |
| 4–10 คน | Lakehouse + Config-driven framework | ห้ามทำ Data Mesh เด็ดขาด |
| 10–30 คน | Hybrid: central platform + domain teams | ห้ามแยกท่อแบบ pure mesh |
| 30+ คน | Data Mesh / Federated | ห้ามทำ monolithic platform |

**ปัญหาที่ผมเห็นบ่อย**: ทีม 5 คนพยายามทำ Data Mesh เพราะอ่านบทความของ Zhamak Dehghani — แล้วก็พังในปีที่ 2

### Q4. Cost Sensitivity ระดับไหน?

- **Predictable budget สำคัญกว่า scale** → ใช้ Reserved capacity (BQ slots, Databricks Reserved) + Batch
- **Pay-per-use OK ถ้าควบคุมได้** → Serverless (Dataflow, BQ on-demand) + Streaming
- **Cost optimization เป็นโจทย์หลัก** → Open table format บน object storage + Spot/Preemptible workers

### Q5. Governance + Compliance หนักแค่ไหน?

- **PII heavy / Banking / Healthcare** → Centralized governance (Unity Catalog หรือ Dataplex) + Data Contracts mandatory
- **Marketing / Internal analytics** → Federated governance พอ
- **Public data / Research** → Lightweight catalog (DataHub / OpenMetadata)

---

## 2. Architecture Patterns ที่มีอยู่จริง — ทั้ง 6 แบบ (ไม่ใช่แค่ 2)

Gemini บอกแค่ Lakehouse กับ Mesh — จริงๆ มี 6 patterns ที่ enterprise ปี 2026 ใช้กัน:

### Pattern A: **Monolithic Lakehouse** (สิ่งที่คุณทำที่ Data-X)

```
┌────────────────────────────────────────────────────┐
│              UNIFIED PLATFORM (Databricks)         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Bronze  │→│  Silver  │→│  Gold (Semantic)  │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│       ↑           ↑              ↑                 │
│  ┌─────────────────────────────────────────┐       │
│  │  Config-driven Framework (Spark + YAML) │       │
│  └─────────────────────────────────────────┘       │
│  Unity Catalog + MLflow + SQL Warehouse            │
└────────────────────────────────────────────────────┘
```

- **เหมาะกับ**: 1 ทีมกลาง / องค์กร mid-size / Data Maturity ต่ำ-กลาง
- **จุดอ่อน**: Single point of failure, Vendor lock-in (Databricks)
- **ข้อเท็จจริงที่ Gemini ไม่บอก**: Unity Catalog เปิด Iceberg native แล้ว → ไม่ lock-in มาก

### Pattern B: **Data Mesh** (สิ่งที่คุณทำที่ The-1)

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Domain: CRM │  │ Domain: Tx  │  │ Domain: Mkt │
│  Own data   │  │  Own data   │  │  Own data   │
│  Own team   │  │  Own team   │  │  Own team   │
└─────────────┘  └─────────────┘  └─────────────┘
       ↓               ↓               ↓
┌────────────────────────────────────────────────┐
│   Self-Service Platform (central infra only)   │
│   + Federated Computational Governance         │
└────────────────────────────────────────────────┘
```

- **เหมาะกับ**: องค์กร 30+ คน / ทุก domain มี Data Engineer ของตัวเอง
- **จุดอ่อน**: Skill gap, lineage ขาดตอน, ไม่มี single source of truth
- **ทำไม The-1 มันรู้สึก "เป็น pipeline ไม่ใช่ platform"**: เพราะ The-1 ทำ Mesh **ด้วย infrastructure** แต่ไม่มี **Self-Service Platform layer ที่แท้จริง** — ทีมกลางยังต้องเขียน pipeline ให้ทุก domain อยู่ดี = "Distributed Monolith"

### Pattern C: **Data Fabric** ⭐ (Gemini พูดผ่านๆ)

```
┌────────────────────────────────────────────────┐
│    AI-Driven Active Metadata Layer (Fabric)    │
│  • Auto-discovery  • Auto-lineage  • Knowledge │
│    Graph + Semantic Search                     │
└────────────────────────────────────────────────┘
        ↑           ↑           ↑           ↑
   ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
   │ Source │  │ DW (BQ)│  │ Lake   │  │ App DB │
   │   1    │  │        │  │ (S3)   │  │        │
   └────────┘  └────────┘  └────────┘  └────────┘
```

- **เหมาะกับ**: องค์กรที่มี data sources กระจัดกระจาย ย้ายไม่ได้/ไม่อยากย้าย
- **Tech**: Atlan, Collibra, Informatica IDMC, Microsoft Purview
- **ความเข้าใจผิด**: Fabric ไม่ใช่ "อีก architecture หนึ่ง" — มันคือ **metadata layer** ที่ไป overlay บน Lakehouse/Mesh ที่มีอยู่
- **2026 Reality**: Lakehouse + Fabric + Mesh ใช้ **ผสมกัน** ไม่ได้เลือกอย่างเดียว

### Pattern D: **Hub-and-Spoke / Federated Lakehouse** ⭐⭐

```
            ┌──────────────────────┐
            │  HUB (Central Team)  │
            │  • Open Table Format │
            │  • Governance Tools  │
            │  • Data Contracts    │
            │  • Shared Templates  │
            └──────────────────────┘
              ↓        ↓        ↓
       ┌────────┐ ┌────────┐ ┌────────┐
       │ Spoke  │ │ Spoke  │ │ Spoke  │
       │ Domain │ │ Domain │ │ Domain │
       │   A    │ │   B    │ │   C    │
       └────────┘ └────────┘ └────────┘
       (use central tools, build their own pipelines)
```

- **เหมาะกับ**: องค์กร 10–30 คน — **คือ sweet spot ของ The-1 ตอนนี้**
- **จุดเด่น**: ได้ standard กลาง (Hub) แต่ scale ตาม domain (Spoke)
- **คือสิ่งที่ Gemini พยายามอธิบายแต่ไม่ตั้งชื่อให้**

### Pattern E: **Lambda / Kappa** (Processing Pattern, ไม่ใช่ Data Architecture)

- **Lambda**: แยก Batch + Streaming เป็น 2 ท่อ → Pre-2020 pattern, ปัจจุบัน **ตกยุคแล้ว**
- **Kappa**: ใช้ Streaming เป็นแกนเดียว, Batch = "Stream replay" → ปัจจุบัน Tech ชั้นนำใช้
- **2026 evolution**: **Unified Batch+Stream** บน Open Table Format (Iceberg + Spark Structured Streaming หรือ Beam) → ไม่ต้องเลือก Lambda/Kappa อีกแล้ว

### Pattern F: **Modern Open Lakehouse** ⭐⭐⭐ (สิ่งที่ Tech Giants ใช้ปี 2026)

```
LAYER 1 (Source):       Apps + DBs + Logs + IoT
                              ↓ CDC (Debezium) / Events
LAYER 2 (Transport):    Kafka / PubSub (data backbone)
                              ↓
LAYER 3 (Storage):      Open Table Format (Iceberg)
                        on Object Storage (S3/GCS)
                              ↓ READ BY ANY
LAYER 4 (Compute):      ┌─────────┬─────────┬──────────┐
                        │ Spark   │ Beam/   │ Trino /  │
                        │(heavy)  │Dataflow │ DuckDB   │
                        │         │(stream) │ (query)  │
                        └─────────┴─────────┴──────────┘
                              ↓
LAYER 5 (Semantic):     dbt / Dataform (SQL business logic)
                              ↓
LAYER 6 (Catalog):      Iceberg REST Catalog +
                        Active Metadata (DataHub/Dataplex)
                              ↓
LAYER 7 (Consume):      BI / ML / GenAI / RAG
```

- **เหมาะกับ**: Modern enterprise / Tech company / องค์กรไหนก็ตามที่ห่วงเรื่อง vendor lock-in
- **คือคำตอบของ "เร็ว+ถูก+เปิด+ใช้ของไหนก็ได้"**

---

## 3. ลึกใน 2 โปรเจกต์ของคุณ — Verdict ตรงไปตรงมา

### 3.1 SCB Data-X (Databricks Config-Driven)

#### มันคือ Pattern A: Monolithic Lakehouse + Metadata-Driven Framework

| มิติ | Pros | Cons |
|---|---|---|
| **Operations** | Single point of control, predictable SLA | High blast radius — เปลี่ยน framework ทีละครั้ง = เสี่ยงพังหมด |
| **Maintenance** | Onboard ข้อมูลใหม่ = แค่เพิ่ม config | Debugging ยาก เพราะ log ทุก job หน้าตาเหมือนกัน, "YAML Hell" เมื่อ logic ซับซ้อน |
| **Time-to-Market** | Standard use case = ออกได้ใน 1 วัน | Custom logic = ติด framework, ต้องรอ DE กลาง |
| **Real-time** | ทำได้ผ่าน Spark Structured Streaming + Trigger Available Now (cost ใกล้ batch) | ไม่ใช่ true streaming, latency 1–5 sec ขั้นต่ำ |
| **AI/ML** | MLflow native, batch ML perfect | Real-time inference ต้อง bolt-on online feature store |
| **Cost** | Job cluster spin-up time แพง — ไป Serverless แก้ได้ | Databricks markup สูง |
| **Governance** | Unity Catalog ครบ end-to-end | Vendor lock-in (แม้ปี 2026 จะเปิด Iceberg แล้ว) |

#### **ข้อจำกัดที่คนไม่เห็น** (เก็บไปตอบสัมภาษณ์ได้)

1. **Backward compatibility nightmare** — เปลี่ยน framework version ใหม่ = ต้องมั่นใจ config 100+ ตัวยังรันได้
2. **Concurrency limit ที่ Job Cluster** — รัน 100 jobs พร้อมกัน = workspace quota เต็ม → คอขวดที่ infrastructure ไม่ใช่ที่ logic
3. **Vendor pricing risk** — Databricks ขึ้นราคา = หนีไปไหนไม่ได้ใน 6 เดือน

### 3.2 NTT-DATA / The-1 Card (GCP Dataflow + Mesh)

#### มันไม่ใช่ Mesh จริง — มันคือ "Distributed Pipeline Collection"

ผมต้องพูดตรงๆ ครับ — โครงสร้างที่ทำมา (จาก repo ที่สำรวจ) คือ:
- ✅ Apache Beam config-driven (YAML + step registry 25+ steps) — ดีแล้ว
- ✅ Domain split (loyalty, insight, sale, catalog, etc.) — ดี
- ✅ Hexagonal refactor ใน insight/ — overengineered แต่เข้าใจเจตนา
- ⚠️ ขาด **Self-Service Platform layer** — ทุก pipeline ยังเขียนโดยทีมกลาง = ไม่ใช่ Mesh จริง
- ⚠️ ขาด **Iceberg REST Catalog ที่ใช้ร่วมกัน** — แต่ละ domain เก็บข้อมูลแยกกันใน BQ + Iceberg มั่วๆ
- ⚠️ ขาด **Data Contracts** — schema breaking changes ยังมาจับเอาที่ปลายน้ำ

| มิติ | Pros | Cons |
|---|---|---|
| **Operations** | Isolated failure per domain | ท่อ streaming 24/7 = cost, watermark/late data ปวดหัว |
| **Maintenance** | Clear ownership per domain (ในทฤษฎี) | จริงๆ ทีมกลางยัง maintain ให้ — Mesh "ครึ่งใบ" |
| **Time-to-Market** | Real-time campaigns = ทำได้จริง | New campaign = รอ DE เขียน Dataflow ใหม่ ทุกครั้ง |
| **Real-time** | True streaming, milliseconds latency | Backfill = ปวดหัวสุด ๆ |
| **AI/ML** | Real-time inference natural | Online Feature Store ต้องสร้างเอง |
| **Cost** | Pay-per-streaming + autoscale | 24/7 compute = ค่าใช้จ่ายโดด |
| **Governance** | Federated theory | Lineage ขาดตอนข้าม domain, ขาด catalog กลาง |

#### **ทำไม The-1 มัน "feel like pipeline ไม่ใช่ platform"** — ผมเห็นใน repo ของคุณแล้ว

**สาเหตุ**: คุณมี **Engine ที่ดี** (Beam config-driven) แต่ขาด **3 ส่วน** ที่ทำให้เป็น Platform จริง:

1. **Storage layer ที่เปิด** — ตอนนี้คุณ write ลง BQ + S3 + Bigtable + Iceberg ผสมกัน → **ไม่มี single canonical storage**
2. **Self-Service Interface** — ตอนนี้ DE เขียน YAML เอง → ไม่ได้เปิดให้ Domain Team กรอก
3. **Active Metadata Layer** — ตอนนี้ไม่มี catalog กลางที่ทุกท่อ register เข้าไป → lineage หาไม่เจอ

**สิ่งที่ขาดไป = นิยามของคำว่า "Platform" จริงๆ**

---

## 4. "Common + Fast + Low Cost + Easy Launch + Easy Gov" — เป็นไปได้แค่ไหน?

### Reality Check: Pentagram Trade-off

```
                    Common
                      ●
                     / \
                    /   \
              Easy ●─────● Fast
              Gov  │     │
                   │     │
                   ●─────●
              Easy        Low
              Launch      Cost
```

**ความจริง**: คุณ "เลือกได้ 3 จาก 5" ในระบบเดียว, จะเอา 5 ครบ = ต้องลงทุน 2x ขึ้นไป

**ความจริงข้อ 2 (สำคัญกว่า)**: 5 อย่างนี้ **ไม่ต้องอยู่ในระบบเดียว** — เลือก trade-off ต่างกันต่อ workload

### Solution: **Tiered Workload Strategy**

แทนที่จะหา "1 platform ที่ทำทุกอย่างได้สมบูรณ์" → แบ่ง workload เป็น 3 tier:

```
┌─────────────────────────────────────────────────────────┐
│ TIER 1: HOT (5–10% of data, 80% of business value)      │
│ ────────────────────────────────────────────────────    │
│ • Real-time fraud, real-time CRM, customer 360         │
│ • SLA: < 5 sec                                          │
│ • Stack: Kafka → Beam/Flink → Iceberg + Online FS       │
│ • Cost: HIGH (accept it)  Gov: HIGH                     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ TIER 2: WARM (30% of data, 15% of business value)       │
│ ────────────────────────────────────────────────────    │
│ • Hourly dashboards, near real-time reports            │
│ • SLA: 5–60 min                                         │
│ • Stack: CDC → Iceberg → Spark micro-batch / dbt        │
│ • Cost: MEDIUM  Gov: MEDIUM                             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ TIER 3: COLD (60–65% of data, 5% of business value)     │
│ ────────────────────────────────────────────────────    │
│ • ML training data, monthly reports, archives          │
│ • SLA: T+1 / weekly                                     │
│ • Stack: Batch CDC → Iceberg + dbt nightly              │
│ • Cost: LOW (Spot/Preemptible)  Gov: LOW                │
└─────────────────────────────────────────────────────────┘
```

**Insight สำคัญ**: ลูกค้าส่วนใหญ่จับ Tier 1 ผิด — จับเป็น 80% แทนที่จะเป็น 5–10%

### 5 หลักการที่ใช้ Hack Pentagram Trade-off

#### 1. **Single Storage, Multi-Compute** (แก้ปัญหา Common + Cost)
- ใช้ Iceberg เป็น storage เดียว, ปล่อยให้ Spark/Beam/Trino/Python ทุกตัวมาอ่าน
- ห้ามทำ data duplication ข้าม engine เด็ดขาด

#### 2. **Shift-Left Governance via Data Contracts** (แก้ปัญหา Easy Gov)
- ทุก source system ต้องประกาศ Data Contract (YAML/Avro/Protobuf)
- Schema breaking change = CI/CD pipeline ของแอป FAIL ก่อน deploy
- ปัญหาแก้ที่ต้นทาง ไม่ใช่ที่ Data Platform

#### 3. **Self-Service Platform-as-Product** (แก้ปัญหา Easy Launch)
- ทีม Platform เขียน "Template" + "Portal" ไม่ใช่เขียน pipeline ให้ domain
- Domain ทีมกรอก config → Platform spin-up pipeline ให้เอง
- Measure platform success ด้วย DAU ของ domain teams ไม่ใช่ uptime

#### 4. **dbt as Semantic Single Source of Truth** (แก้ปัญหา Common)
- Business logic อยู่ใน dbt model เท่านั้น
- ห้าม Dashboard / ML / API คำนวณซ้ำ — ต้องดึงจาก dbt mart
- รวมถึง real-time → ใช้ Materialize / RisingWave หรือ Spark continuous materialization

#### 5. **Tiered Compute by Workload** (แก้ปัญหา Fast + Cost)
- Hot tier: Streaming engine (แพง แต่จำเป็น)
- Warm tier: Micro-batch (cost middle)
- Cold tier: Batch + Spot instance (ถูกที่สุด)

---

## 5. Spark vs Beam — Decision ที่ตกผลึก (พร้อม Fact Update 2026)

### 5.1 ข้อเท็จจริงที่ Gemini ตอบผิด/ไม่รู้

| ประเด็น | Gemini บอก | ความจริงปี 2026 |
|---|---|---|
| Dataproc Serverless + Spark Streaming | "ใช้แทน Databricks ได้" | **❌ Dataproc Serverless ไม่รองรับ Spark Streaming** ([source](https://dev.to/stack-labs/serverless-spark-on-gcp-how-does-it-compare-with-dataflow--2o8n)) |
| Beam ZetaSQL | "ใช้ ZetaSQL ใน Beam ได้เลย" | **❌ ZetaSQL ถูก remove จาก Beam 2.68.0+** ([source](https://beam.apache.org/documentation/dsls/sql/zetasql/overview/)) — ใช้ได้แค่ Calcite SQL |
| Beam SQL = full SQL platform | "เขียน SQL ใน YAML จบ" | ⚠️ Beam SQL ยังขาด features หลายอย่าง (window functions, complex CTE) — production ใช้ Python/Java SDK ดีกว่า |

### 5.2 Decision Matrix ที่ใช้ได้จริง

| โจทย์ | คำตอบ | เหตุผล |
|---|---|---|
| Batch + Mid-latency streaming + ใช้ Cloud อะไรก็ได้ | **Spark on Databricks** | Unified, mature, MLflow built-in |
| Batch + ใช้ GCP เป็นหลัก | **Spark on Dataproc Serverless (batch only)** หรือ **Beam on Dataflow** | Dataproc Serverless = batch ราคาดี |
| True streaming + GCP | **Beam on Dataflow** เท่านั้น | Dataproc Serverless ไม่มี streaming |
| Heavy stream + complex CEP | **Flink** (ไม่ใช่ Beam ไม่ใช่ Spark) | Flink เหนือกว่าทั้งสอง stateful ops |
| All-in-GCP + want feel like Databricks | **BigQuery + dbt + Dataform** เป็นแกน, ใช้ Dataflow แค่ ingest streaming | Beam ไม่ใช่ platform ให้ฝืน |

### 5.3 Verdict สำหรับคุณ

> **ถ้าคุณยืนกราน "อยากได้ Databricks experience บน GCP โดยไม่ใช้ Databricks" — ความจริงคือ มันไม่มี**

GCP ออกแบบมาให้ใช้ **Decoupled Specialized Tools** (Dataflow + BQ + Dataform + Cloud Composer + Vertex AI) ไม่ได้ออกแบบให้มี Unified Platform แบบ Databricks

**ทางเลือกจริงของคุณมี 3 ทาง:**

#### Option 1: ยอมจ่าย → ย้ายไป Databricks บน GCP
- Databricks มี GCP edition แล้ว
- ได้ Spark unified + Unity Catalog + Delta/Iceberg
- Cost: สูงสุด (Databricks markup + GCP infra)

#### Option 2: ยอมรับว่า GCP ไม่ unified → สร้าง Orchestration Layer
- Cloud Composer (Airflow) = Mediator
- Dataflow = Streaming ingest
- BigQuery + Dataform = Transform + Semantic
- BigLake Iceberg = Open storage
- Cost: กลาง, Maintenance: ปานกลาง
- **คือสิ่งที่ The-1 ควรเป็น แต่ยังไม่เสร็จ**

#### Option 3: Open Lakehouse บน GCP (Modern, ปี 2026)
- ดูส่วนถัดไป ⬇️

---

## 6. Open Lakehouse บน GCP — Blueprint ที่คุณควรเดินไป

หลังจากที่คุณมี base ของ The-1 อยู่แล้ว (Beam config-driven + 25 step registry + Hexagonal patterns) สิ่งที่ต้องเติมคือ:

### 6.1 Detailed Architecture (E2E)

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SOURCE SYSTEMS LAYER                            │
│  Apps (POS, Mobile, Web)   |   Operational DB (Postgres, MySQL)        │
│             │                              │                            │
│             ▼                              ▼                            │
│   ┌─────────────────────┐    ┌────────────────────────────┐            │
│   │  Data Contract      │    │  Debezium (CDC)            │            │
│   │  Validation         │    │  Schema Registry           │            │
│   │  (CI Gate at App)   │    │                            │            │
│   └─────────────────────┘    └────────────────────────────┘            │
└─────────────────┬───────────────────────────┬──────────────────────────┘
                  │                           │
                  ▼                           ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    TRANSPORT / EVENT BACKBONE                          │
│   Pub/Sub  ←→  Kafka (if cross-cloud needed)                           │
└─────────────────┬──────────────────────────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    INGEST + LIGHT TRANSFORM (Dataflow)                 │
│   Beam Pipeline (config-driven, your 25-step registry)                 │
│   • Schema validation     • Late data handling                         │
│   • PII masking (early)   • DLQ for bad records                        │
└─────────────────┬──────────────────────────────────────────────────────┘
                  │
                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│              STORAGE LAYER — BIGLAKE ICEBERG ON GCS                    │
│  Bronze (raw)  →  Silver (cleansed)  →  Gold (aggregated)              │
│  All in Apache Iceberg format, on GCS object storage                   │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │   BigLake Metastore (Iceberg REST Catalog)                   │      │
│  │   ↑ readable by ANY engine: BQ, Spark, Trino, Flink, Dataflow│      │
│  └──────────────────────────────────────────────────────────────┘      │
└─────┬─────────────────┬──────────────────┬─────────────────────────────┘
      │                 │                  │
      ▼                 ▼                  ▼
┌──────────┐  ┌────────────────┐  ┌─────────────────────┐
│ Dataform │  │ BigQuery       │  │ Dataflow Streaming  │
│ (SQL DAG)│  │ (Ad-hoc + BI)  │  │ (Continuous compute │
│ Semantic │  │                │  │ on Iceberg)         │
│ Layer    │  │                │  │                     │
└────┬─────┘  └────────┬───────┘  └──────────┬──────────┘
     │                 │                     │
     └─────────────────┼─────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     GOVERNANCE / METADATA LAYER                        │
│  Dataplex (catalog + lineage + quality)                                │
│  + DataHub / OpenMetadata (cross-cloud federation)                     │
│  + Iceberg snapshot history (time travel built-in)                     │
└────────────────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    CONSUMPTION LAYER                                   │
│  • BI: Looker/Tableau (via BigQuery on Iceberg)                        │
│  • ML Training: Vertex AI (read Iceberg directly via Spark)            │
│  • Real-time API: Dataflow → Bigtable / Firestore (online FS)          │
│  • GenAI/RAG: Iceberg Gold → Vertex Vector Search                      │
└────────────────────────────────────────────────────────────────────────┘
```

### 6.2 ทำไม Architecture นี้ตอบโจทย์ทั้ง 5 ของคุณ

| โจทย์ | กลไกที่ตอบ |
|---|---|
| **Common** | Iceberg เป็น storage เดียว, ทุก engine อ่านผ่าน BigLake Metastore + dbt/Dataform เป็น semantic เดียว |
| **Fast** | CDC + Pub/Sub + Dataflow Streaming → Iceberg streaming write (atomic) |
| **Low Cost** | Storage ราคา GCS, Compute pay-per-job, ไม่มี always-on warehouse slot |
| **Easy Launch** | Domain ทีมแค่เขียน YAML config → Platform Kernel spawn Dataflow Flex Template |
| **Easy Gov** | Data Contract + Iceberg schema evolution + Dataplex auto-lineage |

### 6.3 ทำไมไม่หนัก BigQuery (ตอบคำถามที่คุณถาม Gemini)

> **คุณถาม Gemini**: "Compute มันก็จะไปหนัก BQ อยู่ดีไง"

**คำตอบที่ถูกต้อง** (Gemini ตอบครึ่งๆ กลางๆ):

1. **Heavy Transform เกิดที่ Dataflow** (Beam SQL หรือ Beam Python) — ใช้ Worker VM (Spot ได้) ราคา ~$0.05/vCPU-hour
2. **เขียนผลลัพธ์ลง Iceberg บน GCS** ไม่ใช่ BQ native — storage cost = $0.02/GB/month
3. **BigQuery ทำหน้าที่แค่ Query Engine บน External Table (BigLake)** — pay-per-query 5$/TB scanned
4. **ถ้า Pre-aggregate ดี + partition/cluster ใน Iceberg ดี** → query scan แค่ไม่กี่ MB → BQ cost แทบ 0

#### เปรียบเทียบ Cost (Heavy Join 1 TB ทุกวัน):

| ทาง | Storage/เดือน | Compute/วัน | Total/เดือน |
|---|---|---|---|
| BQ ELT แบบเดิม (Storage BQ + Slot reserved) | ~$200 (BQ active storage) | $200/วัน × 30 = $6,000 | **~$6,200** |
| Open Lakehouse (Iceberg on GCS + Dataflow heavy + BQ thin query) | ~$20 (GCS) | $80/วัน Dataflow Spot | **~$2,420** |

**ประหยัด 60–70%** ในขนาด workload ใหญ่ (อ้างอิงจาก case Tech company ทั่วไป)

### 6.4 ความเข้าใจที่ถูกต้องเรื่อง Beam SQL บน Dataflow Workers

(แก้คำตอบของ Gemini ที่ถูกบางส่วน แต่ตกข้อมูลปี 2026)

#### Execution Model จริงๆ:

```
1. SqlTransform("SELECT a, COUNT(*) FROM events GROUP BY a")
        │
        ▼ (compile time)
2. Calcite Parser → Logical Plan → Physical Plan
        │
        ▼ (Beam DAG generation)
3. ParDo + GroupByKey + Combine PTransforms
        │
        ▼ (submit to runner)
4. Dataflow Runner schedules to Workers
        │
        ▼ (runtime)
5. Workers execute on local CPU/RAM
   + Dataflow Shuffle Service (managed) handles GroupBy across workers
   + State stored in Streaming Engine (managed)
```

**สำคัญ**: 
- ✅ Beam SQL = **executes on Dataflow Workers** (ไม่ push-down ไป BigQuery)
- ✅ Shuffle = **offloaded to Google managed service** → worker ไม่ต้องอุ้ม state ใหญ่ใน RAM
- ⚠️ **ZetaSQL ถูกถอด** จาก Beam 2.68.0 → ใช้ได้แค่ Calcite SQL ซึ่ง syntax ต่างจาก BQ
- ✅ ใช้ Beam YAML SDK (เพิ่งออก stable ปี 2025) จะดีกว่าเขียน Python ด้วย — declarative มากขึ้น

#### Scan 100GB ด้วย RAM 10GB (ตอบคำถามของคุณ):

| Configuration | Latency | Cost | Reliability |
|---|---|---|---|
| Max workers = 1 worker × 10GB RAM | ช้ามาก (1+ ชม.) | ถูกที่สุด | ⚠️ OOM ถ้า join ใหญ่ |
| Max workers = 10 workers × 10GB RAM (90 GB total) | เร็ว (5–10 นาที) | กลาง | ✅ ปลอดภัย |
| Max workers = 1 worker × 100GB RAM | กลาง (15+ นาที) | กลาง | ✅ แต่ไม่ scale ได้ |

**Best Practice ปี 2026**: ใช้ **Horizontal Scaling** + **Dataflow Shuffle Service** + **Streaming Engine** เปิด — ให้ Google จัดการ memory pressure แทนที่จะอัด RAM ตัวเอง

---

## 7. Code Pattern — Hexagonal เหมาะหรือไม่?

### 7.1 คุณคิดถูก — Hexagonal Overkill สำหรับ Data Pipeline

(จุดที่ Gemini เห็นด้วยกับคุณตอนหลัง — ผมยืนยัน)

**เหตุผล**:
- Hexagonal เกิดจาก Application Domain ที่มี complex business rules + multiple actors
- Data Pipeline = DAG ของ transform + I/O = **linear flow**
- Indirection เยอะของ Hexagonal = ทำ debugging ยาก + slow down development
- Data Engineer ส่วนใหญ่อ่าน Functional code ออกง่ายกว่า OOP layered code

### 7.2 Pattern ที่เหมาะกับ Data Pipeline จริงๆ

#### A. **Functional Data Engineering** (Maxime Beauchemin's pattern, ใช้กันใน Airbnb/Lyft)

```python
# Pure function - input → output, no side effect
def clean_phone(record: Row) -> Row:
    record.phone = normalize_phone(record.phone)
    return record

def filter_active(record: Row) -> bool:
    return record.status == "active"

# Compose
pipeline = (
    read_source(config)
    | beam.Map(clean_phone)
    | beam.Filter(filter_active)
    | beam.Map(enrich)
    | write_sink(config)
)
```

**ทำไมเหมาะ**:
- Idempotent (run ซ้ำได้ผลเหมือนเดิม)
- Easy to test (pure function)
- Easy to reason about (composition)

#### B. **Declarative + Kernel-Plugin Pattern** (ตามที่ Gemini แนะนำ — ใช่)

```yaml
# config.yaml (declarative)
pipeline:
  name: customer_360
  steps:
    - id: read
      type: ReadFromBigQuery
      params: { table: "raw.customer_events" }
    - id: clean
      type: SqlTransform
      params: { sql: "SELECT * FROM PCOLLECTION WHERE status='active'" }
    - id: enrich
      type: SideInput
      params: { lookup: "ref.customer_master" }
    - id: write
      type: WriteToIceberg
      params: { table: "silver.customer_360" }
```

```python
# Kernel (one piece of code, generic)
class PipelineKernel:
    def __init__(self, registry: dict[str, type[PTransform]]):
        self.registry = registry

    def build(self, config: dict) -> beam.Pipeline:
        p = beam.Pipeline()
        prev = None
        for step in config["steps"]:
            transform_cls = self.registry[step["type"]]
            transform = transform_cls(**step["params"])
            prev = (p | step["id"] >> transform) if prev is None else (prev | step["id"] >> transform)
        return p
```

**Insight**: นี่คือสิ่งที่ repo `the1-replatform` ของคุณทำอยู่แล้ว (25 step registry) — **คุณมาถูกทางแล้ว** แค่ขาด:
1. Self-service portal บน Kernel นี้
2. Iceberg standardization
3. Catalog integration

### 7.3 Verdict — Code Pattern ที่ควรใช้

```
┌────────────────────────────────────────────────────┐
│                                                    │
│  Outer Layer:    Declarative Config (YAML)         │
│                  ↓                                 │
│  Middle Layer:   Generic Kernel (Python/Java)      │
│                  + Plugin Registry                 │
│                  ↓                                 │
│  Inner Layer:    Functional Transforms             │
│                  (pure functions, composable)      │
│                                                    │
└────────────────────────────────────────────────────┘
```

**ห้ามทำ**:
- Hexagonal สำหรับ pipeline ทั่วไป
- DDD สำหรับ data transform
- Microservice สำหรับแต่ละ step

**ทำเฉพาะกรณี**:
- มี business rule ซับซ้อนระดับ application (เช่น loyalty point calculation มี 100+ rules) → ค่อย Hexagonal เฉพาะ rule engine นั้น

---

## 8. Enterprise Data Governance — มาตรฐานปี 2026

### 8.1 5 องค์ประกอบที่ต้องมีครบ

| Pillar | What | Tool ปี 2026 |
|---|---|---|
| **1. Data Catalog** | ค้นหา data assets ได้, มี business glossary | Dataplex, DataHub, Unity Catalog, OpenMetadata |
| **2. Data Lineage** | Trace ข้อมูลตั้งแต่ source ถึง consumer | Auto จาก Dataplex / dbt / DataHub |
| **3. Data Quality** | Validation, monitoring, alerting | Great Expectations, Soda, dbt tests |
| **4. Access Control** | RBAC, ABAC, row/column-level security | Unity Catalog, BigQuery IAM, Ranger |
| **5. Data Contracts** | Producer–consumer agreement enforced in CI | Atlan, dbt contracts, Confluent Schema Registry |

### 8.2 Centralized vs Federated — เลือกอย่างไร

| สถานการณ์ | เลือก | เหตุผล |
|---|---|---|
| 1 ทีมกลาง, < 50 data assets | Centralized | Overhead Federated ไม่คุ้ม |
| 5+ domains, 200+ data assets | Federated | Central คอขวด |
| Banking / Healthcare | Centralized + Strict | Compliance > Speed |
| Tech company, fast-moving | Federated + Contract | Speed + Quality |

### 8.3 Shift-Left Governance — มาตรฐานใหม่ปี 2026

**Old way (broken)**:
```
App developer → DB → ETL → DW → Catch error in DW → "Why phone column missing?"
                                       ↑
                                   pain เกิดที่นี่
```

**New way (Shift-Left)**:
```
App developer → Data Contract YAML in Git
              → CI runs validation
              → If breaking change: PR blocked
              → Only valid contracts can deploy → DB → ETL → DW
                                                                     ↑
                                                          ปลอดภัยตั้งแต่ต้น
```

**ตัวอย่าง Data Contract**:
```yaml
# contracts/orders.yaml
domain: commerce
entity: order
schema_version: 2.0.0
fields:
  - name: order_id
    type: string
    required: true
    pii: false
  - name: customer_phone
    type: string
    required: true
    pii: true
    masking: hash_sha256
  - name: amount
    type: decimal(10,2)
    required: true
sla:
  freshness: 5_minutes
  completeness: 99.9%
breaking_change_policy: major_version_bump
```

CI/CD ของ App ต้อง validate ทุก commit ว่า code ยังตรงกับ contract นี้

### 8.4 Implementation Roadmap (3 เดือน)

```
Month 1: Foundation
├─ Set up DataHub / Dataplex catalog
├─ Auto-ingest metadata จาก BQ + Dataflow
└─ Define top 10 critical assets

Month 2: Data Contracts
├─ Pick 2 domains (high-value)
├─ Define contracts in Git
└─ Add CI check for schema drift

Month 3: Lineage + Quality
├─ Wire dbt + Beam lineage to catalog
├─ Add Great Expectations / Soda checks
└─ Dashboard for data SLA monitoring
```

---

## 9. ML/AI ต่อยอด — Data Platform → AI Platform

### 9.1 Maturity Levels

```
Level 1: Ad-hoc ML        → Notebook + manual training
Level 2: Batch ML         → MLflow + scheduled training
Level 3: Feature Platform → Feature Store + Online inference
Level 4: Real-time ML     → Streaming features + sub-second inference
Level 5: GenAI/RAG        → Vector DB + LLM orchestration
Level 6: Agentic AI       → Multi-agent + tool use
```

ปี 2026 มาตรฐาน enterprise = Level 3–5

### 9.2 Stack ที่แนะนำ (GCP)

```
┌───────────────────────────────────────────────────────┐
│                  GENAI / RAG LAYER                    │
│  Vertex Vector Search + Gemini / Claude API           │
│  + LangChain / LlamaIndex                             │
└───────────────────────────────────────────────────────┘
                       ↑
┌───────────────────────────────────────────────────────┐
│                  ML SERVING LAYER                     │
│  Vertex AI Endpoints (real-time)                      │
│  + Bigtable (online feature store)                    │
└───────────────────────────────────────────────────────┘
                       ↑
┌───────────────────────────────────────────────────────┐
│                  ML TRAINING LAYER                    │
│  Vertex AI Pipelines (Kubeflow)                       │
│  + Read training data from Iceberg directly           │
│  + MLflow / Vertex Experiments                        │
└───────────────────────────────────────────────────────┘
                       ↑
┌───────────────────────────────────────────────────────┐
│                  FEATURE PLATFORM                     │
│  Feast / Vertex Feature Store                         │
│  • Offline FS: Iceberg Gold layer                     │
│  • Online FS: Bigtable / Firestore                    │
└───────────────────────────────────────────────────────┘
                       ↑
                 (เชื่อมเข้า Data Platform)
```

### 9.3 Critical Decision: Real-time Feature Store

นี่คือจุดที่ The-1 ของคุณยังขาด:

```
Streaming events → Dataflow → Bigtable (online FS, ms-latency lookup)
                          ↓
                          → Iceberg (offline FS, training data)
```

**Pattern**: Feature ตัวเดียวกัน เขียนทั้ง 2 ทาง (Bigtable + Iceberg) — เพื่อให้ training-serving consistency

### 9.4 GenAI/RAG บน Data Platform

```
1. Pick canonical data จาก Iceberg Gold
2. Chunk + Embed (Vertex Embedding API)
3. Index ลง Vector Search
4. User query → Retrieve top-K → Inject context → Gemini/Claude → Answer
5. Log conversation → Iceberg → ใช้ train RLHF
```

**ข้อระวัง**: Vector DB ห้าม become "second source of truth" — ต้องเป็นแค่ derivative ของ Iceberg + sync regularly

---

## 10. แกนที่คุณควรยึด — Cheat Sheet ตอนหลงทาง

### 10.1 หลักการ 7 ข้อที่ใช้ตัดสินใจทุกครั้ง

1. **Decouple Storage จาก Compute** — เสมอ, ไม่มียกเว้น
2. **เลือก Open Format ก่อน Vendor** — Iceberg/Delta/Parquet > proprietary
3. **Tiered SLA — ห้ามให้ทุก data ต้อง real-time**
4. **Shift-Left Governance — ปัญหาแก้ที่ source, ไม่ใช่ที่ sink**
5. **Platform-as-Product — measure success ที่ DAU ของ user**
6. **Functional Pipeline > OOP Pipeline** — pipeline ไม่ใช่ application
7. **Match architecture กับ team maturity** — Mesh ก่อน 30 คนคือฆ่าตัวตาย

### 10.2 Cheat Sheet ตอบสัมภาษณ์ / ออกแบบจริง

#### Q: "ออกแบบ Data Platform ให้บริษัท X" — เริ่มยังไง?

```
Step 1: Workload Profile (10 นาที)
   → Volume? Latency SLA? Complexity? Cardinality?

Step 2: Constraint Discovery (10 นาที)
   → Team size? Cloud lock-in? Compliance? Budget?

Step 3: Pattern Selection (5 นาที)
   → Match กับ Pattern A-F (ดูส่วนที่ 2)

Step 4: Tier Workloads (5 นาที)
   → Hot/Warm/Cold + tech stack ต่อ tier

Step 5: Design Governance Layer (5 นาที)
   → Catalog + Contract + Lineage strategy
```

#### Q: "Data-X vs The-1 อันไหนดีกว่า?"

**คำตอบที่ผมจะให้คุณตอบ**:

> "ทั้งสองแบบไม่ใช่คำตอบสุดท้าย — Data-X เก่งเรื่อง batch + governance รวมศูนย์ แต่ launch real-time campaign ช้า The-1 เก่งเรื่อง real-time แต่ governance ขาดตอน + ดูเป็น pipeline collection มากกว่า platform จริง 
> 
> ปี 2026 Tech leaders ผสม 2 อย่างเป็น **Open Lakehouse with Tiered Compute** — Iceberg เป็น storage กลาง, Beam สำหรับ streaming ingest, Spark/dbt สำหรับ heavy transform, BigQuery เป็น query interface, Dataplex/DataHub เป็น governance กลาง 
>
> แต่ความสำเร็จที่แท้จริงไม่ได้อยู่ที่ tech stack — อยู่ที่ Data Contracts + Self-service platform layer ที่ลด blast radius ของ DE กลาง"

#### Q: "ทำไมไม่ใช้ Beam แทน Spark ทุกอย่าง?"

**คำตอบ**:

> "Beam คือ programming model — มันเก่งเรื่อง pipe ข้อมูลเร็วและ unified batch/stream syntactically แต่ไม่ใช่ data platform Spark + Databricks unify ตั้งแต่ ingest ถึง ML lifecycle ในขณะที่ Beam ต้องเย็บกับ BigQuery + Dataform + Composer GCP ปี 2026 ก็เลยมี BigLake Iceberg + Iceberg REST Catalog เพื่อแก้ปัญหานี้ — ให้ Beam ทำหน้าที่ของมันคือ stream processing แล้วใช้ engine อื่นจัดการส่วนที่เหมาะกว่า"

---

## 11. แอ็คชันที่คุณทำได้ทันที (Next 90 Days)

### Week 1–2: Self-Diagnosis
- [ ] เปิด repo `the1-replatform` หา list ของ pipelines ทั้งหมด
- [ ] จัด tier (Hot/Warm/Cold) ทุก pipeline
- [ ] หา pipeline ที่ "ฝืน" — Cold tier ใช้ Streaming โดยไม่จำเป็น

### Week 3–4: Storage Standardization
- [ ] เลือก Iceberg เป็น canonical storage format
- [ ] Migrate 1 pipeline pilot จาก BQ native → BigLake Iceberg
- [ ] Set up BigLake Metastore (REST Catalog)

### Week 5–8: Self-Service Layer
- [ ] เขียน CLI / Portal ให้ Domain team กรอก YAML config
- [ ] CI/CD เชื่อม config → Dataflow Flex Template
- [ ] Document onboarding (1-day path สำหรับ new pipeline)

### Week 9–12: Governance
- [ ] ติดตั้ง DataHub หรือ Dataplex
- [ ] Auto-ingest metadata จาก Beam jobs
- [ ] Define top 5 Data Contracts สำหรับ critical entities (member, order, transaction, etc.)

---

## 12. ทรัพยากรอ่านต่อ (Curated, ไม่ใช่ list ยาวๆ)

### Architecture
- **Designing Data-Intensive Applications** by Martin Kleppmann — bible ของ data architect
- **The Data Engineering Lifecycle** by Joe Reis & Matt Housley — ทันสมัยกว่า

### Patterns
- **Functional Data Engineering** by Maxime Beauchemin (Medium article)
- **Data Mesh Principles** by Zhamak Dehghani — ต้นฉบับ ไม่ใช่ตีความสองทอด

### GCP Specific
- **BigLake Iceberg Tables** — `cloud.google.com/biglake`
- **Apache Beam YAML SDK** (เพิ่ง stable ปี 2025) — declarative ดีกว่า Python

### Industry Trends
- **moderndata101.substack.com** — เน้น 2026 evolution
- **Kai Waehner's blog** — Shift-Left + Streaming
- **Towards Data Science** — Data Engineering survival guides

---

## Final Words

คุณไม่ได้ "หลงทาง" — คุณรู้เยอะแล้ว ปัญหาคือคุณยังไม่มี **กรอบตัดสินใจ** (decision framework) ที่ทำให้ตกผลึกได้

ทุกครั้งที่งงครั้งหน้า กลับมาที่:

1. **4 มิติของ Platform** (Storage / Compute / Orchestration / Governance) — ส่วน 0
2. **5 คำถามก่อนออกแบบ** (Latency / Volume / Team / Cost / Governance) — ส่วน 1
3. **3-Tier Workload Strategy** (Hot / Warm / Cold) — ส่วน 4
4. **7 หลักการตัดสิน** — ส่วน 10.1

อย่ายึดติด tool, อย่ายึดติด pattern — ยึดติดที่โจทย์ของ business และ maturity ของทีม

— เอกสารนี้พร้อมใช้ตอบสัมภาษณ์, defend architecture, หรือ pitch ให้ executive ครับ
