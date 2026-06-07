# Delta Lake vs Apache Iceberg vs Apache Hudi — Decision Guide

> Neutral comparison ของ 3 open table formats สำหรับ lakehouse.
> **ไม่มี "ตัวที่ดีที่สุด"** — ทั้ง 3 เป็น peers ที่แข็งคนละด้าน. เลือกตามเงื่อนไขจริงของทีม + engine + governance.

---

## TL;DR

- **Delta Lake, Apache Iceberg, Apache Hudi เป็น peers** — production-grade ทั้งหมด, มี ACID, time travel, schema evolution, upsert/delete ได้หมด.
- **ไม่มี default** — อย่าเริ่มจาก "ใช้ตัวนี้ไว้ก่อน". เริ่มจากเงื่อนไข: engine ที่ทีมใช้จริง, รูปแบบ write (batch vs heavy streaming upsert), catalog strategy, ระดับ vendor-neutrality ที่ต้องการ.
- **จุดเด่นแบบ caricature** (ไว้จำ ไม่ใช่ไว้ฟันธง):
  - **Delta** → ลื่นสุดใน Databricks/Spark/Microsoft Fabric, governance via Unity Catalog, installed base ใหญ่สุด.
  - **Iceberg** → multi-engine + vendor-neutral ดีสุด, partition evolution, กำลังกลายเป็น interoperability lingua franca.
  - **Hudi** → write-path สำหรับ high-frequency streaming upsert / CDC ดีสุด (record-level index, merge-on-read).
- **ปี 2025-2026 เกมเปลี่ยน** — Delta UniForm + Iceberg REST Catalog ทำให้ "lock-in argument" อ่อนลงมาก. หลาย platform เขียน format นึงแต่ expose เป็น Iceberg ได้. เลือกผิดน้อยลง, แก้ทีหลังถูกลง.

---

## Comparison table

ให้ balanced — ระบุจุดแข็งจริงของแต่ละตัว ไม่ใช่ checkmark ล้วน.

| มิติ | **Delta Lake** | **Apache Iceberg** | **Apache Hudi** |
|---|---|---|---|
| **Multi-engine support** | แข็งสุดบน Spark; engine อื่น (Trino, Flink, DuckDB) อ่านได้แต่ second-class. UniForm ช่วยเปิดทางออก | **กว้างสุด** — Spark, Flink, Trino, Snowflake, BigQuery, DuckDB, StarRocks อ่าน/เขียนได้ native | ดีกับ Spark/Flink; engine อื่นรองรับจำกัดกว่า. Hudi 1.0 ออก Iceberg-format ได้เพื่อแก้จุดนี้ |
| **Streaming upsert / CDC** | upsert ได้ดี (MERGE); deletion vectors ลด write amplification. เหมาะ micro-batch | upsert ได้ (MoR/COW), v3 ปรับปรุง row-lineage; ไม่ได้ออกแบบมาเพื่อ high-frequency upsert โดยเฉพาะ | **แข็งสุด** — record-level index, merge-on-read เขียนเฉพาะ column ที่เปลี่ยน, รับ out-of-order + dedup, NBCC (multi-writer) ใน 1.0 |
| **Catalog + lock-in** | Unity Catalog (multi-format: Delta/Iceberg/Hudi/files). เคยผูก Databricks; OSS UC + Iceberg REST API ลดข้อกังวลลง | **vendor-neutral สุด** — Iceberg REST Catalog spec; Polaris (ASF TLP), Snowflake Open Catalog, AWS Glue, Nessie หลายตัวเลือก | catalog ecosystem เล็กกว่า; พึ่ง Hive Metastore / Glue เป็นหลัก |
| **Ecosystem maturity** | installed base ใหญ่สุด (>60% Fortune 500 ผ่าน Databricks), เอกสาร/ชุมชนหนา | momentum แรงสุดในการ adopt ใหม่ปี 2025-2026; ผู้ขายใหญ่ลงเดิมพันพร้อมกัน | ชุมชนเล็กกว่า แต่ feature streaming ลึกที่สุด; ผู้ใช้เน้น use case เฉพาะทาง |
| **Cloud portability** | ดีขึ้นมากผ่าน UniForm; เดิมรู้สึกผูก Databricks/Fabric | **สูงสุด** — เป็นมาตรฐาน de-facto ข้าม cloud (S3 Tables, BigQuery managed Iceberg, Snowflake) | portable ระดับ format (เป็นไฟล์เปิด) แต่ tooling/engine รอบข้างแคบกว่า |
| **Governance** | ครบสุดเมื่อใช้ Unity Catalog (lineage, RBAC, attribute-based, credential vending) | governance มาผ่าน catalog (Polaris zero-trust + temp credential vending); แยก format ออกจาก governance ได้สะอาด | governance พึ่ง catalog/engine ภายนอกเป็นหลัก |
| **Cost / performance** | deletion vectors + Z-order/liquid clustering ดี; perf ดีสุดบน Databricks runtime | partition evolution + hidden partitioning ลด full rewrite; perf สม่ำเสมอข้าม engine | write-amplification ต่ำสุดสำหรับ upsert-heavy; แต่ MoR แลกด้วย read ช้าลงจน compaction |

> หมายเหตุ: ทุกแถวเปลี่ยนเร็ว — format ทั้ง 3 ไล่ feature กันตลอด (convergence). ใช้ตารางนี้เป็นกรอบ ไม่ใช่ข้อเท็จจริงตายตัว.

---

## Interop ที่เปลี่ยนเกม

จุดนี้สำคัญต่อการตัดสินใจมากกว่า feature checklist — เพราะมันลดน้ำหนักของ "lock-in argument" ที่เคยเป็นตัวตัดสินหลัก.

### Delta UniForm — write once, read anywhere
- Delta table เขียนแบบ Delta ปกติ แต่ generate Iceberg (และ Hudi) metadata บน **ไฟล์ข้อมูลชุดเดียว** — ไม่ copy data.
- ต่อ Delta reader → เห็นเป็น Delta; ต่อ Iceberg reader → เห็นเป็น Iceberg.
- ผลคือ: เลือก Delta ไม่ได้แปลว่าตัด Iceberg consumer ออก.

### Iceberg REST Catalog — มาตรฐานกลางของ control plane
- Iceberg REST API spec ให้ engine ใด ๆ ต่อ catalog เดียวกันได้ (Snowflake, Trino, Athena, BigQuery, Flink, Spark).
- **Unity Catalog implement Iceberg REST API** แล้ว — Databricks เขียน Iceberg/UniForm ที่ Snowflake/BigQuery/Trino อ่านได้ทันที ไม่ต้อง convert.
- **Apache Polaris** (graduate เป็น ASF Top-Level Project ก.พ. 2026) เป็น catalog เปิด vendor-neutral, zero-trust + credential vending.

### นัยต่อการเลือก
- **lock-in ที่จริงในปี 2026 อยู่ที่ "catalog + compute" ไม่ใช่ "table format"**.
- เลือก format ผิดในวันนี้ แก้ทีหลังถูกลงมาก เพราะ interop layer โตขึ้น — ลดความกดดันในการ "เลือกให้ถูกตั้งแต่แรก".

---

## เลือกตัวไหนเมื่อ...

หลายเงื่อนไขชนกันได้ — ไม่ฟันธงตัวเดียว. อ่านเป็น "น้ำหนักเอนไปทาง" ไม่ใช่ "ต้องใช้".

### เอนไปทาง Delta Lake เมื่อ...
- ทีมอยู่ใน **Databricks-centric** หรือ **Microsoft Fabric** (Delta เป็น native default).
- workload เป็น **Spark-heavy** + ต้องการ runtime optimization (liquid clustering, deletion vectors).
- ต้องการ **governance ครบ + จัดการน้อย** ผ่าน Unity Catalog (และยอมรับ managed model).
- มี installed base/skill Delta อยู่แล้ว — ไม่มีเหตุผลแรงพอจะย้าย.

### เอนไปทาง Apache Iceberg เมื่อ...
- ต้องการ **multi-engine open** จริง — BigQuery + Snowflake + Trino + Spark อ่าน table เดียวกัน.
- ให้ความสำคัญ **vendor-neutral / cloud-portability** เป็นข้อกำหนดเชิงสถาปัตยกรรม.
- ต้องการ **partition evolution** (เปลี่ยน daily→hourly เป็น metadata op).
- อยากแยก **catalog/governance ออกจาก format** อย่างสะอาด (Polaris / REST catalog).

### เอนไปทาง Apache Hudi เมื่อ...
- workload เป็น **heavy streaming upsert / database CDC** ความถี่สูง.
- ต้องการ **incremental processing** + record-level index เพื่อเลี่ยง full scan.
- รับ **out-of-order records, bursty traffic, dedup** ใน ingestion layer.
- เน้น **write efficiency** (เขียนเฉพาะ column ที่เปลี่ยน) มากกว่า read latency ทันที.
- หมายเหตุ: Hudi 1.0 ออก Iceberg format ได้ → ใช้ write-path Hudi แต่ expose เป็น Iceberg ให้ consumer ก็ได้.

### เงื่อนไขชนกัน — ตัวอย่าง
- "Databricks อยู่แล้ว **แต่** ต้อง share ออก Snowflake/BigQuery" → **Delta + UniForm** (ไม่ต้องย้ายไป Iceberg).
- "ต้องการ open สุด **แต่** ingestion เป็น streaming upsert หนัก" → **Hudi write-path → Iceberg output**, catalog เป็น Iceberg REST.
- "Multi-engine open **และ** governance vendor-neutral" → **Iceberg + Polaris**.

---

## Anti-patterns ของการเลือก

- **เลือกตาม hype / momentum อย่างเดียว** — "Iceberg กำลังชนะ" ไม่ใช่เหตุผลพอ ถ้าทั้งทีมอยู่บน Databricks/Spark และไม่มี multi-engine requirement.
- **ละเลย engine ที่ทีมใช้จริง** — เลือก format ที่ engine หลักของทีมรองรับแบบ second-class → เจ็บทุกวันใน production.
- **ลืม catalog strategy** — โฟกัส format จนลืมว่า lock-in + governance จริงอยู่ที่ catalog. เลือก format ก่อน catalog = ตัดสินใจกลับด้าน.
- **คิดว่าต้องเลือกถาวร** — มองข้าม UniForm / Iceberg output ของ Hudi ที่ทำให้ interop + migration ถูกลง; over-engineer การตัดสินใจที่ reversible.
- **เลือก Hudi เพราะ "ครบ feature" แต่ไม่มี upsert-heavy workload** — แบก operational complexity (compaction, NBCC tuning) โดยไม่ได้ใช้จุดแข็ง.
- **เลือก format ก่อนรู้ access pattern** — batch analytics vs streaming CDC vs BI federation ให้คำตอบคนละตัว. ถามรูปแบบ read/write ก่อนเสมอ.
- **ปล่อยให้ vendor เลือกแทน** — รับ default ของ platform โดยไม่ map กับ requirement ของตัวเอง.

---

## References

- Onehouse — *Apache Iceberg vs Delta Lake vs Apache Hudi: Feature Comparison Deep Dive* — https://www.onehouse.ai/blog/apache-hudi-vs-delta-lake-vs-apache-iceberg-lakehouse-feature-comparison
- RisingWave — *Apache Iceberg vs Delta Lake vs Hudi (2026)* — https://risingwave.com/blog/apache-iceberg-vs-delta-lake-vs-hudi-2026/
- Dremio — *Comparison of Data Lake Table Formats* — https://www.dremio.com/blog/comparison-of-data-lake-table-formats-apache-iceberg-apache-hudi-and-delta-lake/
- Reintech — *Apache Iceberg vs Delta Lake vs Apache Hudi 2026* — https://reintech.io/blog/apache-iceberg-vs-delta-lake-vs-apache-hudi-2026-table-format-comparison
- Databricks — *Delta UniForm: a universal format for lakehouse interoperability* — https://www.databricks.com/blog/delta-uniform-universal-format-lakehouse-interoperability
- Capital One Tech — *Lakehouse Convergence: Delta Lake & Iceberg* — https://www.capitalone.com/tech/cloud/lakehouse-format-convergence-delta-lake-iceberg/
- Databricks Docs — *Unity Catalog managed tables for Delta Lake and Apache Iceberg* — https://docs.databricks.com/aws/en/tables/managed
- Apache Polaris — https://polaris.apache.org/
- Snowflake — *Introducing Polaris Catalog* — https://www.snowflake.com/en/blog/introducing-polaris-catalog/
- Estuary — *Iceberg Catalog Showdown: Apache Polaris vs Unity Catalog* — https://estuary.dev/blog/iceberg-catalog-apache-polaris-vs-unity-catalog/
- DataLakehouse Hub — *Choosing the Right Iceberg Control Plane (2026)* — https://datalakehousehub.com/blog/2026-05-choosing-iceberg-control-plane/
- Apache Hudi — https://hudi.apache.org/
- Onehouse — *Getting Started: Incrementally process data with Apache Hudi* — https://www.onehouse.ai/blog/getting-started-incrementally-process-data-with-apache-hudi
