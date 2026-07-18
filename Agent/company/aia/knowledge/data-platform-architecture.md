# AIA Data Platform — Architecture (from org diagram, 2026-07-12)

> **CONFIRMED-real AIA architecture** (decoded from the team's draw.io org diagram — Sin's screenshots). This is the authoritative "AIA actual" — supersedes earlier fuzzy notes. Scope on the diagram = the **Data Platform** (Sin's team). Some resource IDs are approximate (photo). Sin's new focus = the **ADB (Azure Databricks) compute** parts.

## Flow (left → right)
`SOURCES → CDC/ingest → EVENT PROCESSING (Kafka) → COMPUTATION (Databricks) → DATALAKE + DATABASE → SERVING/CONSUMPTION`, orchestrated by ADF, governed by Purview + Data 360.

## 1. SOURCES (left)
- **RDBMS (many):** AA Admin, Coast, PRS, IVR, eFHC, iAcademy, CMAC, CMIC, iRecruit, QS, SO, Consent Portal, Non-Life, AIO, PDPA, CRM, LPE + **New Sources 2024 [SMR-4397]**: e-Underwriting, Magnum, BBL360, SF360, SmartClaim, iMoSmart, app-submission, LMS + AI Coach / AI Recruit / LPE [SMR-5111/4608/5156] + [SMR-5273 HTDA].
- **Ingenium** (policy admin, separate).
- **Files/Blob:** QSL, HIAS, EAGLE, newLIFE, Coast, CMAC, AMS, FSU, IIPS, SMS, Magnum log, User input files.
- **Azure File Share:** Alive, AIO, Unica. **External AIA:** CLIP (sftp). AIA email server.

## 2. CDC / INGESTION (two CDC tools + file ingest) ⚠️ important correction
- **Qlik (CDC)** — Qlik Replicate does log-based CDC for a set of RDBMS sources (real-time). *(So CDC is NOT only Debezium.)*
- **Debezium** — inside the Kafka Connect Cluster (see §3), CDC for another set of sources → Kafka.
- **Edge Node (RHEL VM):** AutoSys Agent + **SFTP Server** — file-based ingest via SSH/SFTP (`ktl_nas.pub`).
- **ADF Link Service** — batch pull from Files/Blob + Azure File Share into the lake.

## 3. EVENT PROCESSING — Kafka on AKS (**Sin's producer domain**)
`Azure Kubernetes Service - KAFKA` (`aia-th01-…-p-coredata`):
- **Kafka Connect Cluster** (Debezium) · **Kafka Pool (STRIMZI)** · **Generic Pool** (NGINX ingress controller) · **Monitoring Pool** (Grafana).
- **Jenkins** (`bitbucket.org/aia-th/workspace/projects/DTP`) — CI/CD · **Azure Container Registry (ACR)** — images.
- = the `dtp_kafka_*` repos world already documented ([[aia-new-job]]).

## 4. SCHEDULER / ORCHESTRATOR
- **Azure Data Factory + Integration Runtime** — orchestrates batch + link services. Actors: Data Service, Production Control.

## 5. COMPUTATION — Azure Databricks (**Sin's NEW focus**)
- **Azure Databricks – Real-time** (`adb-th01-…-coredata-dlrt01`): **Cluster for Real-time**, Unity Catalog.
- **Azure Databricks – Batch** (`adb-th01-…-coredata-dtbp01`): interactive cluster + **job cluster**; **Cluster for Batch**, Unity Catalog.
- Supporting stores: **Azure SQL MI – "Framework DB"** (`prd_frmwrk_db`) = framework metadata DB for the Databricks jobs. ⚠️ **CORRECTION (Sin, 2026-07-13): this is NOT the same as SCB's RDT config-driven framework** — do not make that analogy; its actual design is not yet documented. **Azure SQL DB – Databricks Metastore**, **Azure Blob – Temporary Storage**.
- Protocol to lake = **ABFSS**; deploy = Jenkins pipeline; secrets = Key Vault.

## 6. DATALAKE — ADLS Gen2 + Blob
- **Azure Data Lake Storage Gen2 (medallion):** **RAW Zone → Persist Zone → Staging Zone** → `staging / adam / data mart / HSM` [SMR-5273 HTDA]. (raw→persist→curated-ish)
- **Azure Blob Storage – Downstream Zone (500 GB):** AA Admin, AMS, FSU, TIPS, SMS, Printing, EDM, OIC, Users Azure Storage.

## 7. DATABASE / serving stores ⚠️ (answers the earlier "outbound?" question — BOTH exist)
- **Azure SQL Managed Instance → ODS** (`prd_ods_db`) — operational data store.
- **Azure Synapse Dedicated SQL pool** (`db_edw_prod`) → **EDW + New QS + Departmental marts (DM / UC / DGO)** — the enterprise warehouse + departmental schemas.

## 8. GOVERNANCE
- **Microsoft Purview** (Data Catalog).
- **Data 360 Data Governance Tooling:** *Data 360 Govern* (CDEs, business definitions, metadata) + *Data 360 Analyze* (DQ rules, assess quality). DGO departmental schemas ingest via Data360.

## 9. SERVING / CONSUMPTION
- **ESB (API Orchestration)** → Front-End App, Mobile Apps.
- **PowerBI Service + PowerBI Gateway** (BI). **SSMS** (SQL Server mgmt).
- Consumers: Advance Users (DBA/Data Service), **Data Stewards Group**, **Dashboard Users**, Business users (many tribes: Business Strategy, OPS Claim, Product Proposition, Distribution, Data Science, Tribe Claim/HSM, BQM, CDM, Agency, CMP/Martech, Unit Linked, Persistency, Actuarial-Reinsurance, Customer Marketing/ECM).

## 10. ANALYTIC — Data Sciences Lab (multiple Databricks workspaces) ⚠️ relevant to cost-dashboard sharing
- **Azure Databricks (mlflow) – DS Lab:** DS Cluster + Blob + ACR + AKS (Data Scientist / ML Engineer).
- **Azure Databricks – Departmental WS** · **Common WS** · **Amplify WS** (Amplify health) — **business units have their OWN Databricks workspaces**, Unity-Catalog-shared (Delta share seen to Amplify WS).
- → **Implication for the cost-dashboard sharing question:** client teams DO have their own Databricks workspaces → **UC cross-workspace / Delta-share is more viable than first assumed** (Option B match ↑, not just 15%). Verify.

## 11. DR
- Separate tabs: "DR solution of Data Platform", "DR architecture", "DR Failover" — full DR design exists (every prod resource has a DR twin; consistent with the Kafka `-dr` pattern).

## Corrections to prior AIA notes
- CDC = **Qlik Replicate + Debezium** (not Debezium-only).
- Outbound = **BOTH ODS (Azure SQL MI) AND Synapse EDW + departmental marts** are real (was "maybe").
- ADB compute = **config-driven via an Azure SQL MI Framework DB** (SCB-RDT-like) — real-time + batch clusters.
- **Multiple Databricks workspaces per business unit** exist (Departmental/Common/Amplify/DS-Lab) — changes the cost-dashboard sharing calculus ([[aia-cost-dashboard-poc]]).

## Sin's scope
- **Owns/came in on:** Event Processing (Kafka/Strimzi/Debezium producer) — [[aia-new-job]].
- **New focus:** the **ADB (Azure Databricks) compute** — real-time + batch clusters + the config-driven framework. (Details to come from Sin.)
- Plus the **cost-monitoring dashboard PoC** ([[aia-cost-dashboard-poc]]).
