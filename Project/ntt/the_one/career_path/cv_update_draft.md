# CV Update Draft — Wasin Wangsombut

> Draft สำหรับ review ด้วยกัน ก่อนเอาไปใส่ CV จริง
> เน้น solution design, tech decisions, impact — ไม่ใช่แค่ code-level details

---

## SUMMARY (Updated)

Experienced Data Engineer with 8+ years of comprehensive background in designing and implementing data platforms across telecommunications, banking, and retail loyalty industries. Proficient in modern cloud-native data technologies including real-time streaming pipelines, lakehouse architecture, and Change Data Capture patterns on Google Cloud Platform and Azure. Strong focus on data quality, scalable architecture, and cross-team collaboration to deliver production-grade data solutions.

---

## SKILLS (Updated — เพิ่ม section ใหม่จากงาน The 1)

**Programming Languages:** Python, PySpark, Node.js (React)

**Data Engineering:** Data Pipeline Design (Streaming & Batch), Data Modeling, Schema Design (BigQuery, Iceberg), ETL/ELT Development, Data Validation, Change Data Capture (CDC), Data Profiling

**Stream Processing:** Apache Beam, Google Cloud Dataflow, Apache Kafka (Confluent Cloud), Avro/Schema Registry, Google Cloud Pub/Sub

**Lakehouse & Storage:** Apache Iceberg, BigLake Metastore (BLMS REST Catalog), Google BigQuery, Google Cloud Storage, AWS S3 (Parquet)

**Big Data Technologies:** Azure Databricks, Databricks Workspace API, Data Factory API, Unity Catalog

**Cloud Services (GCP):** Dataflow (Flex Templates), BigQuery (Storage Write API, CDC), Cloud Bigtable, Secret Manager, Artifact Registry, Cloud Scheduler

**Cloud Services (Azure):** Data Factory, Synapse Analytics, Storage Account, Key Vault

**Infrastructure & DevOps:** Terraform (IaC), GitLab CI/CD, Docker/Kaniko, Jenkins, GitHub Workflow

**Databases:** BigQuery, PostgreSQL, SQL Server, Hive, Teradata

**Testing & Quality:** pytest (600+ tests), mypy, ruff, SonarQube, pre-commit hooks

**Version Control:** Git (GitLab, GitHub, GitHub Enterprise Cloud)

---

## WORK EXPERIENCE (Updated)

### Data Engineer (Consultant), NTT DATA — Client: The 1 Central Group
**January 2025 - Present**

Designed and implemented 5 production data pipelines for Thailand's largest retail loyalty platform, processing real-time member activity, sales transactions, and customer profile data on Google Cloud Platform.

**Solution Design & Architecture:**
- Designed real-time streaming architecture ingesting events from Confluent Kafka into Apache Iceberg (source layer) and BigQuery (refined layer) using Apache Beam on Google Cloud Dataflow.
- Designed batch pipeline architecture for daily incremental loads from PostgreSQL and REST APIs, with parameterized date-range queries and scheduled triggers via Cloud Scheduler.
- Architected a multi-destination fan-out pattern where a single Kafka consumer feeds multiple downstream tables (up to 4 Iceberg + 4 BigQuery tables from one pipeline).
- Designed a CDC (Change Data Capture) solution with UPSERT and DELETE semantics for near real-time data consistency, using BigQuery Storage Write API with composite primary keys.
- Designed a 3-layer CDC DELETE safety pattern: validate tier removal via Kafka event, verify against upstream API, and confirm record existence in BigQuery before issuing DELETE — preventing accidental data loss.
- Designed a multi-schema message handling solution that auto-detects and normalizes 3 Kafka message formats (flat JSON, nested payload, stringified wrapper) into a unified processing pipeline.
- Designed denormalization strategy for sales data: transforming a single sales event into receipt-level, item-level (SKU), and payment-level (tender) rows with proper composite primary keys for CDC.

**Data Modeling & Schema Design:**
- Designed BigQuery schemas for 16 tables (8 Iceberg source + 8 BigQuery refined) across loyalty, sales, and customer profile domains.
- Designed partitioning strategies (DAY/HOUR) and clustering keys to optimize query performance for downstream analytics.
- Designed Iceberg table schemas with Apache PyArrow, leveraging BigLake Metastore (BLMS REST Catalog) for automatic table creation and schema management.

**Iceberg Lakehouse Migration:**
- Led migration of Iceberg write path from Hadoop Catalog to BigLake Managed Storage (BLMS) REST Catalog with Google-managed vended credentials across all collectors.
- Standardized Iceberg writer pattern (domain config models + managed.Write) and applied consistently across 4 pipeline projects.

**Data Transformation & Processing:**
- Developed data transformers handling Kafka messages with Confluent Avro deserialization, Avro union unwrapping, and multi-format auto-detection (Avro/JSON).
- Implemented timezone-aware timestamp processing (Bangkok UTC+7) for both Iceberg (INT partition) and BigQuery (DATE/TIMESTAMP) layers.
- Implemented cross-bundle deduplication using Beam windowing (GroupByKey + Distinct) to prevent duplicate API calls and writes in streaming pipelines.

**Testing & Quality:**
- Developed 600+ unit tests across 5 projects using pytest, covering transformers, API integration, CDC logic, schema validation, and configuration.
- Maintained code quality through mypy (static typing), ruff (linting), SonarQube analysis, and pre-commit hooks in CI pipeline.

**Infrastructure & CI/CD:**
- Provisioned per-service GCP resources using Terraform: GCS buckets, Artifact Registry, BigLake catalog IAM, Secret Manager, and BigQuery datasets.
- Built multi-stage GitLab CI/CD pipelines with automated testing, Docker image builds (Kaniko), Terraform deployment, and Dataflow job submission for both STG and PROD environments.
- Developed automated BigQuery table management scripts (CREATE, ALTER, backup/restore, schema comparison) for deployment automation.

**Cross-Team Coordination:**
- Coordinated with Kafka platform team on message schema alignment, topic configuration, and Confluent Schema Registry integration.
- Collaborated with infrastructure team on Terraform resource provisioning, IAM policies, and BigLake catalog setup.
- Aligned BigQuery schema design with downstream analytics consumers to ensure query efficiency and data accessibility.

---

### Data Engineer, SCB Data-X
**January 2023 - December 2024**

_(เหมือนเดิมใน CV)_

---

## PROJECTS (Updated — เพิ่ม section NTT / The 1)

### NTT DATA — The 1 Central Group

**1. Loyalty Data Platform — Members Pipeline (Streaming)**
- Designed and implemented a real-time streaming pipeline consuming member tier events from Confluent Kafka, enriching with Loyalty REST API data, and writing to Apache Iceberg and BigQuery.
- Designed CDC DELETE pattern for maintaining data consistency when member tiers are removed, with 3-layer safety validation (Kafka → API → BigQuery).
- Handled 3 Kafka message schema variants (flat, nested payload, stringified JSON) with auto-detection logic.
- Developed 220+ unit tests covering message parsing, API enrichment, CDC logic, and schema validation.
- Tech: Python, Apache Beam, Dataflow, Kafka (Confluent), Iceberg (BigLake BLMS), BigQuery (CDC/Storage Write API), Terraform, GitLab CI/CD

**2. Loyalty Data Platform — Tiers Master Pipeline (Batch)**
- Designed and implemented a batch pipeline polling loyalty tiers master data from REST API, transforming nested tier structures into flat BigQuery rows.
- Implemented WRITE_TRUNCATE strategy for reference data tables with daily Cloud Scheduler triggers.
- Developed 197 unit tests.
- Tech: Python, Apache Beam, Dataflow, Iceberg (BigLake BLMS), BigQuery, Cloud Scheduler

**3. Loyalty Data Platform — Members Tiers History Pipeline (Batch)**
- Designed and implemented a daily incremental batch pipeline reading member tier history from PostgreSQL with parameterized date-range queries.
- Designed BigQuery table with clustering on (member_id, tier_code) for optimized downstream queries.
- Developed 104 unit tests.
- Tech: Python, Apache Beam, Dataflow, PostgreSQL, Iceberg (BigLake BLMS), BigQuery, Cloud Scheduler

**4. Sales Data Platform — Sales Pipeline (Streaming)**
- Designed and implemented a real-time streaming pipeline consuming sales events from Confluent Kafka and denormalizing into 3 BigQuery tables: receipt, SKU (line items), and tender (payments).
- Designed composite primary keys and CDC UPSERT strategy for all 3 refined tables.
- Implemented Confluent Avro deserialization with Schema Registry and Avro union unwrapping for complex nested payloads.
- Developed 126 unit tests covering Avro handling, timestamp parsing, denormalization, and configuration validation.
- Tech: Python, Apache Beam, Dataflow, Kafka (Confluent, Avro/Schema Registry), Iceberg (BigLake BLMS), BigQuery (CDC/Storage Write API), Terraform, GitLab CI/CD

**5. Insight Data Platform — Customer Profile Pipeline (Streaming)**
- Designed and implemented a streaming pipeline processing customer persona events from Pub/Sub, enriching with Cloud Bigtable profile data, and writing to BigQuery (CDC), AWS S3 (Parquet), and Iceberg.
- Implemented hexagonal architecture (ports/adapters) for clean separation of pipeline infrastructure and business logic.
- Designed dynamic column mapping using BigQuery reference tables for flexible schema reconciliation.
- Tech: Python, Apache Beam, Dataflow (Flex Templates), Pub/Sub, Bigtable, BigQuery (CDC), AWS S3, Iceberg (BigLake), Cloud Composer (Airflow)

---

> **Notes สำหรับ review:**
> - SCB Data-X end date เปลี่ยนเป็น December 2024 (ถ้า overlap กับ NTT ให้ปรับตามจริง)
> - ใน WORK EXPERIENCE ผมเขียนแบบ solution-focused — ไม่ลง function name / file name
> - ใน PROJECTS ผมเขียนแบบ concise + มี tech stack ท้ายแต่ละ project
> - bullet ไหนที่ไม่ได้ทำจริง ช่วย mark ไว้ ผมจะลบออก
> - bullet ไหนที่ขาดไป ช่วยบอก ผมจะเพิ่ม
