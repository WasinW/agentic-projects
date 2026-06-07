# CV Update — Final Version

---

## SUMMARY

Experienced Data Engineer with 8+ years of comprehensive background in designing and implementing data platforms across telecommunications, banking, and retail industries. Proficient in cloud-native data technologies including real-time streaming pipelines, lakehouse architecture, and Change Data Capture (CDC) patterns on Google Cloud Platform and Azure. Strong focus on scalable architecture, data quality, and cross-team collaboration to deliver production-grade data-driven solutions.

---

## SKILLS

**Programming Languages:** Python, PySpark, Node.js (React)

**Data Engineering:** Data Pipeline Design (Streaming & Batch), Data Modeling, Schema Design, ETL/ELT Development, Data Validation, Change Data Capture (CDC), Schema Synchronization, Data Profiling

**Stream Processing:** Apache Beam, Google Cloud Dataflow, Apache Kafka (Confluent Cloud, Schema Registry, Avro), Google Cloud Pub/Sub

**Lakehouse & Storage:** Apache Iceberg, BigLake Metastore (BLMS REST Catalog), Google BigQuery, Google Cloud Storage, AWS S3 (Parquet)

**Big Data Technologies:** Azure Databricks, Databricks Workspace API, Data Factory API, Unity Catalog, HD Insight

**Cloud Services (GCP):** Dataflow (Flex Templates), BigQuery (Storage Write API, CDC), Cloud Bigtable, Secret Manager, Artifact Registry, Cloud Scheduler, Cloud Composer (Airflow)

**Cloud Services (Azure):** Data Factory, Synapse Analytics, ADLS Gen2, Storage Account, Key Vault

**Infrastructure & DevOps:** Terraform (IaC), GitLab CI/CD, Docker, Kaniko, Jenkins, GitHub Workflow

**Databases:** BigQuery, PostgreSQL, SQL Server, Hive, Teradata

**Testing & Quality:** pytest, mypy, ruff, SonarQube, pre-commit hooks

**Data Security and Governance:** Role-Based Access Control (RBAC)

**Version Control:** Git (GitLab, GitHub, GitHub Enterprise Cloud)

---

## WORK EXPERIENCE

### Data Engineer (Consultant), NTT DATA — Client: The 1 Central Group
**January 2025 - Present**

Production data pipelines for a large-scale retail loyalty platform on Google Cloud Platform, covering both real-time streaming and scheduled batch workloads.

- Real-time streaming pipeline architecture: Confluent Kafka → Apache Beam (Dataflow) → two-layer lakehouse (Apache Iceberg as source of truth, BigQuery as refined/analytics layer).
- Batch pipeline architecture: daily incremental loads from PostgreSQL and REST APIs into the same Iceberg + BigQuery lakehouse.
- Fan-out pipeline patterns: single Kafka consumer branching into multiple downstream Iceberg and BigQuery tables.
- CDC (Change Data Capture) solution for near real-time data consistency across lakehouse layers.
- Multi-format Kafka message handling: auto-detection and normalization of multiple message schemas into a unified processing flow.
- Event denormalization strategy: complex nested events split into multiple normalized target tables with CDC support.
- Two-layer schema design (Iceberg source + BigQuery refined) with partition and clustering optimization for analytics workloads.
- Iceberg lakehouse migration: Hadoop Catalog → BigLake Managed Storage (BLMS) REST Catalog, standardized across all pipeline projects.
- Data transformers: Confluent Avro deserialization, multi-format auto-detection, timezone-aware timestamp processing, cross-bundle deduplication.
- Comprehensive unit test suites (pytest) covering transformers, API integration, CDC logic, schema validation, and configuration.
- Code quality enforcement: static typing (mypy), linting (ruff), SonarQube, pre-commit hooks.
- GCP infrastructure provisioning via Terraform: GCS, Artifact Registry, BigLake catalog, Secret Manager, BigQuery datasets.
- Multi-stage GitLab CI/CD: automated testing, Docker image builds (Kaniko), Terraform deployment, Dataflow job submission (STG/PROD).
- Automated BigQuery schema management tooling for deployment (creation, migration, backup/restore).
- Cross-team coordination: Kafka platform team (schema alignment, Schema Registry), infrastructure team (Terraform, IAM, BigLake), analytics team (schema design, query optimization).

---

### Data Engineer, SCB Data-X
**January 2023 - December 2024**

_(เหมือนเดิม)_

---

## PROJECTS

### NTT DATA — The 1 Central Group

**1. Real-Time Event Streaming Pipelines (Kafka → Iceberg → BigQuery)**
- Streaming data pipelines: Confluent Kafka → Apache Beam on Dataflow → two-layer lakehouse (Iceberg + BigQuery).
- CDC solution for data consistency in the refined layer. Multi-format Kafka message handling (JSON, Avro/Schema Registry) with auto-detection.
- Tech: Python, Apache Beam, Dataflow, Kafka (Confluent), Avro/Schema Registry, Iceberg (BigLake BLMS), BigQuery CDC, Terraform, GitLab CI/CD

**2. Batch Data Ingestion Pipelines (API / PostgreSQL → Iceberg → BigQuery)**
- Batch pipelines: daily incremental loads from REST APIs and PostgreSQL → Iceberg + BigQuery lakehouse.
- Table partitioning and clustering strategies optimized for analytics workloads.
- Tech: Python, Apache Beam, Dataflow, PostgreSQL, Iceberg (BigLake BLMS), BigQuery, Cloud Scheduler, Terraform

**3. Customer Profile Streaming Pipeline (Pub/Sub → Bigtable → Multi-Destination)**
- Streaming pipeline: Pub/Sub events enriched with Cloud Bigtable lookups → BigQuery (CDC), AWS S3 (Parquet), and Iceberg.
- Data reconciliation framework for pipeline migration validation.
- Tech: Python, Apache Beam, Dataflow (Flex Templates), Pub/Sub, Bigtable, BigQuery CDC, AWS S3, Iceberg (BigLake), Cloud Composer (Airflow)
