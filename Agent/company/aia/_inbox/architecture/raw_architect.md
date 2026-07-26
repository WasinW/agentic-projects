# AIA Data Platform — raw architecture transcription

> Transcribed by Claude from Sin's screen-photo of the official AIA "Data Platform" diagram
> (Authorize by [redacted], dated 10-Sep-2024). **Raw dump** — faithful to the image, not curated.
> `[?]` = best-effort read (photo blur); verify against the source diagram.
> 🔒 AIA-internal — private KB only, do not share externally. Companion: `aia-data-platform.drawio`.
> Cross-ref confirmed context: `../../knowledge/data-platform-architecture.md`, CLAUDE.md.

Left→right data flow: **SOURCES → CDC/ingest → EVENT PROCESSING (Kafka) → COMPUTATION (Databricks)
→ DATABASE (SQL MI / Synapse) + DATALAKE (ADLS) → SERVING/CONSUMPTION**, with SCHEDULER (ADF) on top
and GOVERNANCE (Data 360 / Purview) + DS-Lab on the right.

---

## 1. SOURCES (far left)

### 1.1 RDBMS — "Existing source" (SQL Server / DB icons)
- Row group A: `AA Admin`, `Coail`[?], `PRS`, `IVM`[?], `eFHC`[?], `iAcademy`[?]
- Row group B: `CMAC`, `CMC`, `iRecruit`, `QS`, `SO`, `Consent Portal`
- Row group C: `Non-Life`, `AIO`, `PIDIYA`[?]
- **[SMR-4397] New Sources 2024** + **[SMR-5273] HTDA**: `e-Underwriting`, `Magnum`, `BBL 360`,
  `SF360`, `SmartClaim`[?], `SF360`; `app_submission LMS`
- **[SMR-5111] AI Coach**, **[SMR-4618] AI Recruit**, **[SMR-5156] LPE**: `CRM`, `LPE`
- `Ingenium` (separate source, real-time dashed line out)

### 1.2 Files Blob
- `GHSL`[?], `HIAS`, `EAGLE`, `none-LIFE`[?]
- `Ingenium (IGM)`, `FWS`[?], `Coail`, `CMAC`, `AA Admin`
- `AMS`, `FSU`, `iMPS`[?], `SMS`, `User's Input files`
- **[SMR-4397] New Sources 2024**; `Magnum log`

### 1.3 Azure File Share
- `Alive`[?], `AIO`, `Unitas`[?]
- (bottom) `AIA mail server`[?]

---

## 2. CDC / INGESTION (between sources and Kafka)

- **Qlik (CDC)** — Qlik Replicate, real-time capture from RDBMS. Line: `TLS 1.2 (https)`.
- **Debezium** — CDC connector running inside the Kafka Connect Cluster (see §3).
- **Edge Node** (RedHat / RHEL VM):
  - `AutoSys Agent`, `SFTP Server`, `kz_txw.pub`[?]
  - VMs: `THAZE/PLAY0038`[?], `THAZE/PLAY0055`[?], `WINDOWS VM`, `RHEL VM`
  - Lines: `SSH`, `TLS 1.2 (https)`
- Note: two CDC paths — **Qlik Replicate** (log-based, some sources) + **Debezium** (Kafka-native, others).

---

## 3. EVENT PROCESSING — Azure Kubernetes Service (AKS) / KAFKA

- **Kafka Connect Cluster**: `Debezium`
- **Kafka Pool**: `STRIMZI` (the broker cluster, operator-managed)
- **Generic Pool**: (managed by Strimzi)[?]
- **Monitoring Pool**: `Grafana`
- **Jenkins** ("used existing") — CI/CD, repo `https://bitbucket.org/aia-th/workspace/projects/DTP`
- **Azure Container Registry (ACR)** — `acith01axaspahared01`[?]
- Deploy path: Bitbucket → Jenkins → ACR → AKS → Strimzi operator reconcile.
- Out to COMPUTATION: `TLS 1.2 (https)` (real-time, dashed blue).

> Maps to Sin's producer domain (`dtp_kafka_{build_ci,cluster,connector}`), the "Kafka MFEC" platform.

---

## 4. SCHEDULER / ORCHESTRATOR (top center)

- Actors: `Data Service` (person), `Production Control` (person)
- **Azure Data Factory** + **Integration Runtime** — `thazepdf0002`[?]  (batch orchestrator, NOT Airflow)

---

## 5. COMPUTATION — Azure Databricks

### 5.1 Real-time (top)
- **Azure Databricks – Real-time** — `aidb-th01-xxx-p-coredata-dbrs01`[?]
- **Cluster for Real-time** (consumes Kafka topics → Structured Streaming)

### 5.2 Batch (bottom)
- **Azure Databricks – Batch**
  - `aidb-th01-xxx-p-coredata-dtkp01`[?] → **Interactive cluster**
  - `aidb-th01-xxx-p-coredata-dtlpp01`[?] → **Job Cluster**
- **Cluster for Batch**

### 5.3 Computation supporting stores
- **Azure SQL MI – Framework DB** — `prd_frmwrk_db / thazepmdb0029`  (config-driven ETL framework)
- **Azure SQL Database – Databricks Metastore**
- **Azure Blob Storage – Temporary Storage** — `aaith01axaspahared01`[?]
- Databricks ↔ ADLS: `TLS 1.2 (abfss)`, `PROTOCOL: ABFSS / AUTHENTICATION: RBAC`

---

## 6. DATABASE (serving stores)

### 6.1 Azure SQL Managed Instance — ODS
- `ODS` — `prd_odw_db / thazepmdb0030`

### 6.2 Azure Synapse Dedicated SQL pool — `db_edw_prod / thazepdb0001`
- `HSAC → EDW`
- `HSAC → New QS`
- `Departmental (DM)`
- `Departmental (UC)`
- `Departmental (DGO)`

---

## 7. DATALAKE — Azure Data Lake Storage Gen2 (center-bottom)

### 7.1 Medallion zones
- **RAW Zone**
- **Persist Zone**
- **Staging Zone**: `staging`, `adam`, `data mart`, `HSM` **[SMR-5273 HTDA]** — `aaith01axaspdp01share01`[?]

### 7.2 Downstream Zone — Azure Blob Storage (500 GB) — `aaith01axaspdp01share01`[?]
- `AA Admin`, `AMS`, `FSU`, `TIPS`, `Users Azure Storage`
- `SMS`, `Printing`, `EDM`, `OIC`
- Access to serving: `Read-only`, RBAC.

---

## 8. SERVING / CONSUMPTION (right)

- **ESB (API Orchestration)** → `Front-End Application`, `Mobile Apps`
- **PowerBI Service** + **PowerBI Gateway**
- **SSMS / SQL Server Management** ("used existing")
- Lines to consumers: `TLS 1.2 (https)`, `User access`, `APIs Call`

---

## 9. DATA GOVERNANCE (right)

### 9.1 Data Catalog
- **Heading**[?] — MS Purview — `THAZE/PWAP/KA82U88`[?]  (box partly a Lorem-ipsum placeholder in the diagram)

### 9.2 Data 360 Data Governance Tooling
- **Data 360 Govern**: Define CDEs, Business Definitions, Metadata
- **Data 360 Analyze**: Define data quality rules, Assess data quality
- DGO Departmental schemas: `dp_dgo_dm` via Data360Analyze; Databricks ingest to
  `dp_dgo_dm.DATA_PREPARATION`[?] / `dp_dgo_dm.DATA360_INV`[?]; Data360Govern ingest to `dp_dgo_govern`[?];
  Data360 Governance access via web app.

---

## 10. ANALYTIC — Data Sciences Lab (right, mlflow)

- **Azure Databricks (mlflow)** — `aidb-th01-xxx-p-dsl2-en01`[?] (several workspaces listed)
  - **DS Cluster**, **Blob storage**
- `ACR`, `AKS`
- Users: Data Scientist, ML Engineer, Data Service

---

## 11. Departmental / Business Databricks workspaces (right, Unity Catalog)

- **Azure Databricks – Departmental WS** — `aidb-th01-xxx-p-departmental-enb01`[?]
  - **Cluster**: `Persist`, `staging`, `cdn` **[SMR-5273 HTDA]** — Unity catalog
  - Users: Business user
- **Azure Databricks – Common WS** — `aidb-th01-xxx-p-commonws-enb01`[?]
  - **Cluster** — Unity catalog; Users: Business user
- **Azure Databricks – Amplify WS** — `aidb-th01-xxx-p-...-shdn01`[?] — Unity catalog
- (All UC-shared; matches "multiple Databricks workspaces per business unit".)

---

## 12. CONSUMERS / USER GROUPS (right edge, people icons)

- **Data Stewards Users Group** — DGO Departmental schemas: `dp_dgo_uc` via Power BI, `dp_dgo_dm` via
  SSM[?]; Databricks/ADF ingest to `dp_dgo_uc`; access report via Power BI; access Investigation tables.
- **Dashboard Users**, **Data Service**
- **Advance Users**, **DBA**, **Data Service**
- **Business domains** (Power BI / dashboard consumers): Business Strategy, CS, OPS OA, OPS Claim,
  Product Proposition (PP), DS (Distribution Service), Data Science, Tribe Claim (HSM), BQM, CDM,
  Agency, CMP (Martech), Unit Linked, Vitality, Persistency Tribe, Actuarial-Reinsurance,
  Customer Marketing / ECM / CIA
- **Data Governance**, **Data Scientist / ML Engineer**, **Business user**

---

## 13. DOWNSTREAMS / STORAGE (bottom-left)

- `SOS`, `EDM`, `Direct Marketing (DM)`
- **(red box)** `IGM  BAS4PA01.aia.biz`, `EAGLE  BAS4HIAS.aia.biz`, `Customer BI  https://SalvageAccount.dfs.core.windows.net`[?]
- `EBiz`, `ePos`, `Easy M (ECM App)`
- `Smart Claims (Medix)`, `iMo Smart (Line App)`, `d'via BBL` — various `thazepmdb*`[?] hosts

---

## 14. LINE DEFINITION (legend)

| Style | Meaning |
|---|---|
| blue dashed | Real-time Process |
| black solid | Batch Process |
| — | ADF Link Service |
| — | ABFSS Databrick Protocol |
| — | Jenkin Deployment Pipeline |
| — | ADF Pipeline |
| — | Key Vault access |
| dashed | DataMart Access TLS 1.2 (https) |
| — | User access |
| — | APIs Call |

**Protocols seen on edges:** `TLS 1.2 (https)`, `TLS 1.2 (abfss)`, `SSH`, `Read-only`,
`PROTOCOL: ABFSS / AUTHENTICATION: RBAC`.

---

## 15. How Sin's 4 focus areas map onto this diagram

1. **Access Management (4 layers)** — applies across the **Databricks workspaces (§11) + Unity Catalog
   + Synapse Departmental schemas (§6.2) + Data360 schemas (§9.2)**. Identity/entitlement/permission/
   grant = the governance layer over these consumers.
2. **Monitoring & Observability** — Cost dashboards = over the workspaces/§11 + DSL/§10; Genie = business
   users/§12; **Observability infra/job/DQ** = the **Monitoring Pool Grafana (§3)** for Kafka +
   Databricks system tables + Data360 DQ (§9.2).
3. **Streaming provider** — the **EVENT PROCESSING / AKS-Kafka zone (§3)** + Qlik/Debezium CDC (§2);
   the alert work rides the Monitoring Pool.
4. **Databricks consumer (stream-join-stream)** — the **Real-time cluster (§5.1)** consuming Kafka →
   the stream-static-join pattern (see `../google_ai_chat/adb-consume-stream-join-CURATED`).

---

## 16. Uncertain reads to verify against the source diagram
- Exact Databricks workspace hostnames (`aidb-th01-xxx-p-*`) — the `xxx` token + suffixes are blurry.
- Storage account names (`aaith01axaspdp01share01`, `acith01axaspahared01`).
- Edge-node VM names (`THAZE/PLAY00xx`).
- Data360 schema names (`dp_dgo_*`) and the Purview host.
- A few source-system names in §1 (marked `[?]`).
