# Architecture Decision Guide: Data Platform Selection

> **Version**: 2.0 | **Created**: 2026-03-05 | **Maintainer**: Data Platform Team

## Table of Contents

1. [Decision Framework](#1-decision-framework)
2. [When to Choose GCP](#2-when-to-choose-gcp)
3. [When to Choose AWS](#3-when-to-choose-aws)
4. [When to Choose Azure](#4-when-to-choose-azure)
5. [When to Choose Databricks](#5-when-to-choose-databricks)
6. [Hybrid/Multi-Cloud Patterns](#6-hybridmulti-cloud-patterns)
7. [Migration Playbooks](#7-migration-playbooks)
8. [Architecture Patterns Deep Dive](#8-architecture-patterns-deep-dive)
9. [Real-World Reference: The1 Data Platform](#9-real-world-reference-the1-data-platform)
10. [Platform Selection Scorecard](#10-platform-selection-scorecard)
11. [Team Skill Assessment Framework](#11-team-skill-assessment-framework)
12. [Anti-Patterns and Pitfalls](#12-anti-patterns-and-pitfalls)
13. [Technology Radar](#13-technology-radar)

---

## 1. Decision Framework

### Decision Tree

```
START: What is your primary use case?
│
├── "SQL analytics / BI dashboards"
│   ├── Power BI primary? ──────────────→ Azure (Fabric / Synapse)
│   ├── Looker / Data Studio? ──────────→ GCP (BigQuery)
│   ├── Tableau / QuickSight? ─────────→ AWS (Redshift) or Databricks
│   └── Multiple BI tools? ────────────→ Databricks (open format)
│
├── "Streaming / real-time"
│   ├── Kafka already in place? ───────→ AWS (MSK) or GCP (Dataflow)
│   ├── Serverless streaming? ─────────→ GCP (Pub/Sub + Dataflow)
│   ├── Kafka + Spark? ───────────────→ Databricks (Structured Streaming)
│   └── Event Hubs / Azure native? ───→ Azure (Stream Analytics)
│
├── "ML / AI platform"
│   ├── Full MLOps lifecycle? ─────────→ Databricks (MLflow + Mosaic AI)
│   ├── AutoML / managed? ────────────→ GCP (Vertex AI) or AWS (SageMaker)
│   └── Azure ML + Power BI? ─────────→ Azure
│
├── "Multi-cloud required"
│   ├── Same experience everywhere? ──→ Databricks
│   ├── Open format portability? ─────→ Iceberg + any cloud
│   └── Hybrid on-prem + cloud? ─────→ Azure Arc or Databricks
│
└── "Cost-optimized batch ETL"
    ├── Serverless preferred? ─────────→ GCP (BigQuery + Dataflow)
    ├── Spot/preemptible? ────────────→ AWS (EMR Spot) or GCP (Dataproc)
    └── Complex Spark jobs? ──────────→ Databricks or AWS EMR
```

### Step-by-Step Process

```
Step 1: Assess Current State
├── What data sources exist? (databases, APIs, streams, files)
├── What tools/skills does the team have?
├── What cloud(s) are already in use?
├── What's the annual data platform budget?
└── What compliance/regulatory constraints exist?

Step 2: Define Requirements (with specific metrics)
├── Data volume: GB/TB/PB today? Growth rate %/year?
├── Latency: <1s / <5min / <1hr / daily batch?
├── Query patterns: ad-hoc SQL? scheduled dashboards? ML training?
├── Concurrent users: 10? 100? 1000+?
├── SLA: 99.9%? 99.99%? Downtime tolerance?
└── Multi-cloud: hard requirement or nice-to-have?

Step 3: Evaluate Platforms (weighted scoring)
├── Match requirements to platform strengths
├── Assess lock-in risk vs managed-service value
├── Calculate 3-year TCO (compute + storage + egress + licensing)
├── Factor in team ramp-up time and hiring market
└── Run proof-of-concept on top 2 candidates

Step 4: Design Architecture
├── Choose data format: Iceberg (GCP/AWS) or Delta (Azure/Databricks)
├── Design layer architecture: medallion (bronze/silver/gold)
├── Select processing engine(s): Beam, Spark, SQL
├── Plan governance: catalog, lineage, access control
├── Define CI/CD: IaC tool, deployment pipeline, environments
└── Plan disaster recovery and backup strategy

Step 5: Implement & Iterate
├── Pilot project: 1 domain, 2-4 week sprint
├── Validate: performance, cost, developer experience
├── Harden: security review, load testing, failover testing
├── Scale: additional domains, production traffic
└── Optimize: cost tuning, query performance, pipeline efficiency
```

### Key Questions to Ask

| Category | Questions | Why It Matters |
|----------|-----------|----------------|
| **Data volume** | How much data today? Growth rate? Peak vs steady? | Determines storage tier + compute sizing |
| **Team skills** | Spark? SQL? Python? Beam? Cloud certifications? | Biggest factor in time-to-value |
| **Budget** | CapEx vs OpEx? Total budget? Cost per query tolerance? | Eliminates options early |
| **Compliance** | Data residency? Encryption at rest/transit? Audit logs? | May force specific cloud or region |
| **Multi-cloud** | Hard requirement or future consideration? | If hard req → Databricks or open format |
| **Latency** | Real-time dashboards? Sub-second queries? Batch OK? | Streaming vs batch architecture |
| **BI tools** | Power BI? Looker? Tableau? Custom? | Often dictates cloud choice |
| **ML/AI** | Critical path or nice-to-have? Training or inference? | Affects compute + platform choice |
| **Existing investment** | Current cloud contracts? Committed spend? | Switching cost vs optimization |
| **Data sources** | RDBMS? APIs? Kafka? Files? SaaS connectors? | Determines ingestion architecture |

### TCO Calculation Template

```
3-Year TCO = Compute + Storage + Networking + Licensing + People

Compute:
├── Processing (ETL/ELT): _____ hrs/month × $___/hr = $___/month
├── Warehouse queries: _____ TB scanned/month × $___/TB = $___/month
├── Streaming: _____ workers × 24/7 × $___/hr = $___/month
└── ML training: _____ GPU-hrs/month × $___/hr = $___/month

Storage:
├── Raw/bronze: _____ TB × $___/TB/month = $___/month
├── Refined/silver: _____ TB × $___/TB/month = $___/month
├── Gold/serving: _____ TB × $___/TB/month = $___/month
└── Backups/snapshots: _____ TB × $___/TB/month = $___/month

Networking:
├── Ingestion (ingress): usually free
├── Cross-region: _____ TB × $0.01-0.02/GB = $___/month
├── Cross-cloud egress: _____ TB × $0.08-0.12/GB = $___/month
└── Internet egress (BI/API): _____ TB × $0.08-0.12/GB = $___/month

Licensing:
├── Databricks DBUs: _____ DBU × $___/DBU = $___/month
├── Confluent Kafka: _____ CKU × $___/CKU = $___/month
├── BI tools: _____ seats × $___/seat = $___/month
└── dbt / Dataform / other: $___/month

People (often largest cost):
├── Data engineers: _____ FTE × $___/year
├── Data analysts: _____ FTE × $___/year
├── Platform/DevOps: _____ FTE × $___/year
├── Training/certification: $___/year
└── Hiring/ramp-up cost: $___

Total monthly = $___
Total 3-year = monthly × 36 = $___
```

---

## 2. When to Choose GCP

### Best For
- **Serverless-first** teams wanting minimal ops
- **BigQuery SQL analytics** as primary use case
- **Apache Beam/Dataflow** for unified streaming + batch
- **Google ecosystem** (Google Ads, YouTube, Firebase analytics)
- **Iceberg-native** lakehouse with BigLake/BLMS

### Ideal Team Profile
- Small-to-medium data engineering team (3-15 people)
- SQL-heavy analysts and data scientists
- Teams valuing simplicity over customization
- Organizations already on GCP

### Strengths
- BigQuery: truly serverless, zero-ops warehouse
- Pay-per-query model ideal for variable workloads
- BigLake + BLMS = strongest Iceberg-native experience
- Dataflow: best managed streaming with Beam
- Dataform: free semantic layer (no dbt licensing)
- Dataplex: modern governance replacing Data Catalog

### Weaknesses
- Smaller ecosystem than AWS
- Beam has smaller talent pool than Spark
- BLMS still maturing (PyIceberg issues)
- BigQuery SQL has proprietary extensions

### Decision Signals — Choose GCP When

| Signal | Strength |
|--------|----------|
| Team already uses GCP for apps/infra | Strong |
| BigQuery SQL covers 80%+ of query needs | Strong |
| Variable/unpredictable query workloads | Strong |
| Need simplest managed streaming (Beam) | Strong |
| Google Ads / YouTube / Firebase data sources | Strong |
| Iceberg-native lakehouse required | Moderate |
| Budget-conscious with < 10 TB scanned/month | Moderate |
| Team size < 10 data engineers | Moderate |

### Typical Architecture on GCP

```
┌──────────────────────────────────────────────────────────────────┐
│  Ingestion                Processing              Serving        │
│                                                                  │
│  Kafka ──────→ Dataflow ──→ Iceberg ──→ BigQuery ──→ Dataform   │
│  (Confluent)   (Beam)       (GCS+BLMS)  (refined)    (SQL views)│
│                                                                  │
│  APIs ───────→ Dataflow ──┘             BigQuery ──→ Looker     │
│  (REST/gRPC)   (batch)                  (public)     (BI)       │
│                                                                  │
│  Pub/Sub ────→ Dataflow ──┘                                     │
│  (events)      (streaming)                                       │
│                                                                  │
│  Governance: Dataplex │ CI/CD: GitLab + Terraform               │
└──────────────────────────────────────────────────────────────────┘
```

### GCP Cost Example (10 TB refined, 50 TB scanned/month)

| Component | Monthly Cost |
|-----------|-------------|
| BigQuery storage (10 TB active) | $200 |
| BigQuery queries (50 TB on-demand) | $312 |
| GCS storage (20 TB source) | $520 |
| Dataflow (3 streaming + 2 batch jobs) | $800-1,200 |
| Dataform | Free |
| **Total** | **~$1,800-2,200** |

---

## 3. When to Choose AWS

### Best For
- **Enterprises with existing AWS footprint**
- **Maximum flexibility** and customization
- **Kafka-heavy** streaming architectures
- **Teams comfortable with many service options**
- **Cost-sensitive** at scale (Spot instances, Reserved pricing)

### Ideal Team Profile
- Experienced engineers (5+ years cloud)
- Teams willing to evaluate multiple services
- Organizations with strong DevOps/platform engineering
- Mixed workloads (data, ML, web, microservices)

### Strengths
- Broadest service catalog in cloud
- Most mature ecosystem with largest community
- Strategic Iceberg bet (S3 Tables, Glue Catalog REST)
- EMR: mature Spark with Spot instance savings (60-90% off)
- Zero-ETL integrations (Aurora, DynamoDB → Redshift)
- MSK: best managed Kafka service

### Weaknesses
- Service fragmentation (biggest concern)
- Decision fatigue: too many overlapping services
- Cost complexity across multiple services
- Redshift Python UDF deprecation (June 2026)

### Decision Signals — Choose AWS When

| Signal | Strength |
|--------|----------|
| 50%+ of infrastructure already on AWS | Strong |
| Need broadest service catalog | Strong |
| Kafka/MSK is core infrastructure | Strong |
| Want Spot/Reserved instance savings | Strong |
| Team has AWS certifications | Moderate |
| Zero-ETL (Aurora → Redshift) fits use case | Moderate |
| S3 Tables / Iceberg-native storage appeals | Moderate |
| Need SageMaker for ML | Moderate |

### Typical Architecture on AWS

```
┌──────────────────────────────────────────────────────────────────┐
│  Ingestion                Processing              Serving        │
│                                                                  │
│  MSK ────────→ EMR/Glue ──→ Iceberg ──→ Redshift ──→ QuickSight│
│  (Kafka)       (Spark)      (S3+Glue)   (Spectrum)              │
│                                                                  │
│  Kinesis ────→ Glue ──────┘             Athena ────→ Tableau    │
│  (streams)     (serverless)             (ad-hoc)                │
│                                                                  │
│  DMS ────────→ Glue ──────┘             SageMaker ─→ Endpoints  │
│  (CDC)         (ETL)                    (ML)                     │
│                                                                  │
│  Governance: DataZone / Lake Formation  │ CI/CD: CodePipeline   │
└──────────────────────────────────────────────────────────────────┘
```

### AWS Cost Example (10 TB refined, 50 TB scanned/month)

| Component | Monthly Cost |
|-----------|-------------|
| Redshift RA3.xlplus (2 nodes, Reserved) | $1,100 |
| S3 storage (20 TB) | $460 |
| EMR (3× m5.xlarge Spot, 8hrs/day) | $400-600 |
| Glue (100 DPU-hrs) | $440 |
| MSK (3 brokers kafka.m5.large) | $650 |
| **Total** | **~$3,000-3,200** |

---

## 4. When to Choose Azure

### Best For
- **Microsoft shop** (SQL Server, Power BI, Office 365)
- **Enterprise compliance** (SOC, HIPAA, government)
- **Power BI-centric** BI strategy
- **SQL Server background** teams
- **Fabric** for unified analytics (when mature)

### Ideal Team Profile
- .NET/SQL Server background
- Power BI power users
- Enterprise organizations with Microsoft EA
- Teams preferring visual/low-code tools

### Strengths
- Deep Microsoft integration (M365, Dynamics, Power Platform)
- Fabric: unified experience (when mature) across all analytics
- DirectLake: game-changing Power BI performance (10-100x faster than Import)
- Strong enterprise compliance and governance (Purview)
- SQL Server migration path (minimal rewrite)
- Azure Databricks for complex processing

### Weaknesses
- Fabric maturity gaps (T-SQL limitations, security, CI/CD)
- Synapse dedicated pools: uncertain future
- Delta-only native format (Iceberg via transparent serving layer only)
- Cost complexity (CU billing, multi-dimensional pricing)
- 10-20% Databricks premium vs AWS pricing

### Decision Signals — Choose Azure When

| Signal | Strength |
|--------|----------|
| Organization has Microsoft EA/license agreement | Strong |
| Power BI is the mandated BI tool | Strong |
| SQL Server / .NET background team | Strong |
| M365 / Dynamics 365 data integration needed | Strong |
| Fabric DirectLake fits reporting pattern | Moderate |
| Government / high-compliance workloads | Moderate |
| Team prefers GUI / low-code tools | Moderate |
| Hybrid with on-prem SQL Server via Azure Arc | Moderate |

### Typical Architecture on Azure

```
┌──────────────────────────────────────────────────────────────────┐
│  Ingestion                Processing              Serving        │
│                                                                  │
│  Event Hubs ─→ Fabric ────→ Delta ────→ Fabric WH ─→ Power BI  │
│  (streams)     (notebooks)  (OneLake)   (SQL)        (DirectLake)│
│                                                                  │
│  ADF ────────→ Databricks → Delta ────┘              Purview    │
│  (batch/CDC)   (complex)    (ADLS)                   (governance)│
│                                                                  │
│  Dataverse ──→ Shortcuts ─→ OneLake ──┘                         │
│  (Dynamics)    (mirroring)                                       │
│                                                                  │
│  Governance: Purview + Fabric │ CI/CD: Azure DevOps / Bicep     │
└──────────────────────────────────────────────────────────────────┘
```

### Azure Cost Example (10 TB refined, 50 TB scanned/month)

| Component | Monthly Cost |
|-----------|-------------|
| Fabric F64 (64 CU, reserved) | $6,100 |
| ADLS Gen2 (20 TB hot) | $400 |
| Event Hubs Standard (10 TU) | $600 |
| Power BI Pro (20 users) | $200 |
| Azure Databricks (optional, 500 DBU) | $1,200 |
| **Total (Fabric only)** | **~$7,300** |
| **Total (with Databricks)** | **~$8,500** |

---

## 5. When to Choose Databricks

### Best For
- **Multi-cloud** strategy required
- **Heavy Spark workloads** and expertise
- **ML/AI-first** teams (data scientists + engineers)
- **Open format commitment** (Delta + Iceberg interop via UniForm)
- **Complex ETL** at scale

### Ideal Team Profile
- Data scientists AND data engineers
- Strong Spark/Python expertise
- Organizations on multiple clouds
- Teams building ML platforms

### Strengths
- Only true multi-cloud platform (same experience on AWS, Azure, GCP)
- Best open lakehouse (Delta + UniForm for Iceberg interop)
- Unity Catalog: most complete open governance (open-sourced 2024)
- MLflow + Mosaic AI: best integrated ML platform
- Photon: vectorized SQL performance (2-8x faster)
- Delta Sharing: open data sharing protocol

### Weaknesses
- Consistently most expensive at scale (DBU markup on cloud compute)
- DBU pricing complexity (varies by workload type, cloud, region)
- Operational lock-in despite open data formats
- Learning curve for non-Spark teams
- Overkill for simple SQL analytics

### Decision Signals — Choose Databricks When

| Signal | Strength |
|--------|----------|
| Multi-cloud is a hard requirement | Strong |
| Team has strong Spark expertise | Strong |
| ML/AI is a primary use case | Strong |
| Need same platform across AWS + Azure + GCP | Strong |
| Complex ETL (1000+ transformation steps) | Moderate |
| Delta Sharing needed for external data exchange | Moderate |
| Unity Catalog governance fits org model | Moderate |
| Want open-source governance (UC open-sourced) | Moderate |

### Typical Architecture on Databricks

```
┌──────────────────────────────────────────────────────────────────┐
│  Ingestion                Processing              Serving        │
│                                                                  │
│  Auto Loader ─→ Bronze ───→ Silver ───→ Gold ────→ SQL WH      │
│  (cloud files)  (raw)       (cleaned)   (agg)      (BI serving) │
│                                                                  │
│  Lakeflow ───→ Bronze ───┘                         BI tools     │
│  (SaaS CDC)    (CDC)                               (any)        │
│                                                                  │
│  Kafka ──────→ Structured Streaming → Silver ─────→ MLflow      │
│  (events)      (micro-batch)                       (ML serving) │
│                                                                  │
│  Governance: Unity Catalog │ Format: Delta + UniForm (Iceberg)  │
└──────────────────────────────────────────────────────────────────┘
```

### Databricks Cost Example (10 TB refined, 50 TB scanned/month)

| Component | Monthly Cost |
|-----------|-------------|
| SQL Warehouse (Medium, ~$7/DBU) | $2,500-4,000 |
| Jobs Compute (500 DBU-hrs, Spot) | $1,000-1,500 |
| Cloud storage (20 TB, S3/GCS/ADLS) | $400-520 |
| Unity Catalog | Included |
| MLflow | Included |
| **Total** | **~$4,000-6,000** |

---

## 6. Hybrid/Multi-Cloud Patterns

### Pattern 1: Cross-Cloud Streaming (GCP Analytics + AWS Streaming)

```
┌──────────────────────┐        ┌──────────────────────────────┐
│  AWS (ap-southeast-1) │        │  GCP (asia-southeast1)       │
│                       │        │                              │
│  Confluent Kafka      │  egress│  Dataflow (Apache Beam)      │
│  ├─ topic-1           │───────→│  ├─ streaming-collector      │
│  ├─ topic-2           │        │  ├─ batch-collector          │
│  └─ Schema Registry   │        │  └─ history-collector        │
│                       │        │          │                    │
│  Applications (source)│        │          ▼                   │
│  └─ microservices     │        │  Iceberg (GCS + BLMS)        │
│                       │        │          │                    │
│                       │        │          ▼                   │
│                       │        │  BigQuery → Dataform → BI    │
└──────────────────────┘        └──────────────────────────────┘
```

**When to use**: Streaming sources in AWS (existing Kafka), analytics stack in GCP (BigQuery)
**Real-world example**: The1 Data Platform
**Key concern**: Cross-cloud egress ($0.08-0.12/GB). Mitigate by filtering at source.

**Cost optimization tips**:
- Filter/aggregate in Kafka (reduce egress volume)
- Use Kafka Connect with SMT to drop unused fields before cross-cloud transfer
- Consider Confluent Cluster Linking (replicate only needed topics)
- Choose same region pair for lowest latency (e.g., ap-southeast-1 ↔ asia-southeast1)

### Pattern 2: Databricks Processing + Native Warehouse Serving

```
┌─────────────────────────────────────────────────────┐
│  Any Cloud                                           │
│                                                      │
│  Cloud Storage ──→ Databricks ──→ Delta Lake         │
│  (S3/GCS/ADLS)     (ETL + ML)     (Bronze/Silver)   │
│                                         │            │
│                         ┌───────────────┤            │
│                         ▼               ▼            │
│                   Delta Gold ──→ Native Warehouse    │
│                   (ML features)  (BigQuery/Redshift) │
│                         │               │            │
│                         ▼               ▼            │
│                   ML Serving      BI Dashboards      │
│                   (MLflow)        (Looker/QuickSight)│
└─────────────────────────────────────────────────────┘
```

**When to use**: Complex Spark ETL / ML needs + cost-effective BI serving on native warehouse
**Key benefit**: Databricks for what it does best (Spark, ML), native for BI cost savings
**Key concern**: Data synchronization between Delta and native warehouse

### Pattern 3: Open Format as Portability Layer

```
                    ┌─── BigQuery (SQL analytics)
                    │
Cloud Storage ──→ Apache Iceberg ──├─── Spark / EMR (batch processing)
(S3/GCS/ADLS)     (open format)    │
                                   ├─── Trino / Starburst (federated)
                                   │
                                   ├─── DuckDB (local dev / testing)
                                   │
                                   └─── Flink (streaming analytics)
```

**When to use**: Future-proof architecture, engine flexibility, avoid lock-in
**Key benefit**: Change compute engine without re-writing data
**Key concern**: Not all engines support all Iceberg features equally

### Pattern 4: Azure + Databricks Coexistence

```
┌─────────────────────────────────────────────────────┐
│  Azure                                               │
│                                                      │
│  ┌─────────────┐     ┌───────────────────────┐      │
│  │ Fabric      │     │ Azure Databricks       │      │
│  │ (simple ETL,│     │ (complex ETL, ML,      │      │
│  │  Power BI,  │     │  multi-cloud workloads) │      │
│  │  governance)│     │                         │      │
│  └──────┬──────┘     └──────────┬────────────┘      │
│         │    OneLake / ADLS Gen2│                     │
│         └────────┬──────────────┘                    │
│                  ▼                                    │
│           Delta Lake (shared storage)                │
│                  │                                    │
│         ┌────────┴────────┐                          │
│         ▼                 ▼                           │
│   Power BI            External consumers             │
│   (DirectLake)        (Delta Sharing)                │
└─────────────────────────────────────────────────────┘
```

**When to use**: Microsoft shop with complex processing needs beyond Fabric
**Key benefit**: Best of both worlds — Fabric for BI, Databricks for heavy processing

### Pattern 5: Data Mesh with Federated Ownership

```
┌─────────────────────────────────────────────────────────────────┐
│  Central Platform Team                                           │
│  ├── Shared infrastructure (Terraform modules, CI/CD templates)  │
│  ├── Governance policies (Unity Catalog / Dataplex / Purview)    │
│  └── Self-serve portal (data catalog, lineage viewer)            │
│                                                                   │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐        │
│  │ Domain: Loyalty│  │ Domain: Txn   │  │ Domain: CRM   │        │
│  │ Owner: Team A  │  │ Owner: Team B │  │ Owner: Team C │        │
│  │ Stack: Beam+BQ │  │ Stack: Spark  │  │ Stack: Fabric │        │
│  │ Format: Iceberg│  │ Format: Delta │  │ Format: Delta │        │
│  │                │  │               │  │               │        │
│  │ Data products: │  │ Data products:│  │ Data products:│        │
│  │ - member_tier  │  │ - purchases   │  │ - contacts    │        │
│  │ - tier_history │  │ - returns     │  │ - segments    │        │
│  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘        │
│          │                  │                   │                 │
│          └──────────────────┴───────────────────┘                │
│                             │                                     │
│                     Shared data marketplace                       │
│                     (cross-domain discovery)                      │
└─────────────────────────────────────────────────────────────────┘
```

**When to use**: Large organization (100+ data engineers), multiple autonomous teams
**Key benefit**: Domain teams move fast, central team ensures consistency
**Key concern**: Requires organizational maturity, not just technology

### Anti-Patterns to Avoid

| Anti-Pattern | Problem | Better Approach |
|-------------|---------|-----------------|
| Duplicate workloads on multiple clouds | 2-3x cost, ops burden | Pick primary cloud, use open format for portability |
| Cross-cloud data movement for every query | Egress costs explode | Replicate data to consuming cloud, query locally |
| Different table format per cloud | No interop, double conversion | Standardize on one format + interop layer (UniForm) |
| "Lift and shift" without re-architecture | Cloud costs > on-prem | Re-design for cloud-native patterns |
| Multi-cloud "for resilience" | Complexity explosion | Use multi-region in single cloud instead |
| Building abstraction over every cloud service | Never finishes | Accept some lock-in, abstract only at data layer |

---

## 7. Migration Playbooks

### 7.1 Traditional DW → Cloud Lakehouse

```
Timeline: 6-12 months (typical)

Phase 1: Assessment & Planning (Month 1-2)
├── Inventory all tables, views, stored procs, ETL jobs
├── Classify: lift-and-shift vs re-architect vs deprecate
├── Map source → target equivalents
├── Identify data quality issues (fix now, not during migration)
└── Set up target cloud infrastructure (Terraform)

Phase 2: Parallel Run (Month 3-5)
├── Set up cloud warehouse (BQ/Redshift/Synapse)
├── Replicate data to cloud (CDC or bulk export)
├── Rewrite top 20% most-used queries first
├── Run parallel validation: on-prem results vs cloud results
└── Build automated data comparison framework

Phase 3: Lakehouse Introduction (Month 5-8)
├── Store raw data in open format (Iceberg/Delta on cloud storage)
├── Build medallion architecture (bronze → silver → gold)
├── Migrate ETL from on-prem tool (Informatica/SSIS) to cloud (Beam/Spark/dbt)
├── Connect BI tools to new lakehouse
└── Validate dashboard parity

Phase 4: Cutover & Decommission (Month 8-12)
├── Migrate remaining workloads
├── Redirect all consumers to cloud
├── Run legacy in read-only mode for 1 month (safety net)
├── Decommission legacy warehouse
└── Optimize cloud costs (right-size, reservations)
```

**Key metrics to track during migration:**

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Data parity | 100% match | Row counts + checksum comparison |
| Query performance | Within 2x of legacy | Query benchmark suite |
| Cost | < 80% of legacy TCO | Monthly billing comparison |
| Downtime | < 4 hours total | Cutover window |
| Rollback capability | Full rollback for 30 days | Keep legacy read-only |

### 7.2 Hadoop → Modern Lakehouse

```
Timeline: 9-18 months (depends on Hadoop cluster size)

Phase 1: Inventory (Month 1-2)
├── Catalog all HDFS data (size, format, ownership, access patterns)
├── Map Hive tables → Iceberg/Delta equivalents
├── Identify Pig/MapReduce/Hive scripts → Spark/Beam rewrites
├── Audit security: Ranger/Sentry → cloud IAM mapping
└── Calculate cloud storage costs vs current HDFS

Phase 2: Data Migration (Month 3-5)
├── Set up cloud storage (S3/GCS/ADLS) with proper structure
├── Use distcp / Cloud Storage Transfer for bulk HDFS → cloud copy
├── Convert Parquet/ORC/Avro to Iceberg/Delta tables
├── Validate: row counts, checksums, partition alignment
└── Set up dual-write (Hadoop + cloud) for active tables

Phase 3: Processing Migration (Month 5-10)
├── Migrate Hive SQL → Spark SQL / BigQuery / Databricks SQL
├── Rewrite MapReduce/Pig → Spark / Beam pipelines
├── Convert Oozie/Airflow DAGs → cloud orchestration (Cloud Composer/MWAA/ADF)
├── Migrate Kafka consumers → cloud equivalents
└── Replace Sqoop → cloud ingestion (DMS/Datastream/CDC connectors)

Phase 4: Warehouse Layer (Month 8-12)
├── Add warehouse engine: BigQuery / Redshift / Databricks SQL
├── Build gold layer views for BI serving
├── Migrate BI reports (Hue/Zeppelin → Looker/QuickSight/Power BI)
└── Set up governance (Dataplex/Unity Catalog/DataZone)

Phase 5: Decommission Hadoop (Month 12-18)
├── Verify zero reads from HDFS
├── Archive cold data to object storage (Glacier/Coldline/Archive)
├── Decommission Hadoop cluster nodes
├── Terminate Hadoop licenses (Cloudera/Hortonworks)
└── Celebrate! (seriously, this is a big deal)
```

**Hadoop migration component mapping:**

| Hadoop Component | GCP Equivalent | AWS Equivalent | Azure Equivalent |
|-----------------|----------------|----------------|------------------|
| HDFS | GCS | S3 | ADLS Gen2 |
| Hive | BigQuery | Athena / Redshift | Fabric Warehouse |
| Spark on YARN | Dataproc / Dataflow | EMR | HDInsight / Databricks |
| MapReduce | Dataflow (Beam) | EMR (Spark) | Databricks |
| Oozie | Cloud Composer | MWAA | ADF |
| Sqoop | Datastream | DMS | ADF Copy Activity |
| Ranger | IAM + Dataplex | Lake Formation | Purview + Fabric |
| HBase | Bigtable | DynamoDB | Cosmos DB |
| Kafka (on-prem) | Pub/Sub or Confluent | MSK | Event Hubs |

### 7.3 Oracle / SQL Server → Cloud

```
Phase 1: Assessment
├── Run Oracle AWR / SQL Server DMV analysis for workload profiling
├── Identify PL/SQL / T-SQL stored procedures (rewrite complexity)
├── Map Oracle features → cloud equivalents:
│   ├── Partitioning → native cloud partitioning
│   ├── Materialized views → BQ materialized views / Redshift MV
│   ├── RAC → cloud HA (multi-zone/region)
│   └── Data Guard → cloud replication
└── Estimate license savings (Oracle/SQL Server → cloud)

Phase 2: Schema Migration
├── Use cloud migration tools:
│   ├── GCP: Database Migration Service + BigQuery Migration
│   ├── AWS: Schema Conversion Tool (SCT) + DMS
│   └── Azure: Azure Migrate + Database Migration Service
├── Convert data types (Oracle NUMBER → NUMERIC, etc.)
├── Rewrite stored procedures → cloud SQL or application code
└── Handle sequences, synonyms, database links

Phase 3: Data Migration
├── Full load: bulk export → cloud import
├── CDC for ongoing sync: Oracle GoldenGate / SQL Server CDC → cloud
├── Validate data parity
└── Performance benchmark critical queries

Phase 4: Cutover
├── Application connection string update
├── DNS cutover (if applicable)
├── Monitor for 72 hours
└── Decommission source database
```

### 7.4 Synapse → Fabric Migration

```
Phase 1: Inventory Synapse Assets
├── Dedicated SQL pools: tables, views, stored procs, distributions
├── Serverless SQL pools: OPENROWSET queries, external tables
├── Spark pools: notebooks, libraries
├── Pipelines: ADF-integrated pipelines
└── Linked services: connections to external systems

Phase 2: Set Up Fabric
├── Create Fabric workspace (capacity reservation)
├── Configure OneLake storage
├── Set up Git integration
└── Map Synapse pools → Fabric items:
    ├── Dedicated SQL pool → Fabric Warehouse
    ├── Serverless SQL → Lakehouse SQL endpoint
    ├── Spark pool → Fabric Spark (Runtime 1.3+)
    └── Pipelines → Fabric Data Factory

Phase 3: Migrate
├── Copy Delta/Parquet data to OneLake (via shortcuts or AzCopy)
├── Recreate warehouse tables (T-SQL compatible, minus limitations)
├── Convert stored procs (check T-SQL subset compatibility)
├── Rebuild pipelines in Fabric Data Factory
├── Test DirectLake mode for Power BI reports
└── Address Fabric gaps (no MERGE, limited IDENTITY, etc.)

Phase 4: Validate & Cutover
├── Run query comparison (Synapse vs Fabric)
├── Verify Power BI report equivalence
├── Update downstream consumers
└── Pause/delete Synapse dedicated SQL pools
```

---

## 8. Architecture Patterns Deep Dive

### 8.1 Medallion Architecture (Bronze/Silver/Gold)

Applicable across ALL platforms with platform-specific implementations:

| Layer | Purpose | GCP | AWS | Azure | Databricks |
|-------|---------|-----|-----|-------|------------|
| **Bronze** | Raw, immutable | Iceberg on GCS via BLMS | Iceberg on S3 via Glue Catalog | Delta on ADLS / OneLake | Delta Bronze tables |
| **Silver** | Cleaned, conformed | BigQuery refined dataset | Iceberg on S3 or Redshift | Delta on OneLake (conformed) | Delta Silver tables |
| **Gold** | Business-ready | Dataform views (public) | Redshift views / Athena | Fabric Warehouse / Power BI | Delta Gold + SQL views |

**Key design decisions:**

| Decision | Options | Recommendation |
|----------|---------|----------------|
| Bronze format | Iceberg vs Delta vs raw Parquet | Match platform native (Iceberg for GCP/AWS, Delta for Azure/Databricks) |
| Bronze retention | Forever vs 90 days vs 1 year | Keep raw forever (storage is cheap, re-processing is not) |
| Silver granularity | Per-source vs per-domain vs unified | Per-domain (balance between isolation and usability) |
| Gold materialization | Views vs materialized tables | Views for simple joins, materialized for expensive aggregations |
| Cross-layer references | Same dataset vs separate | Separate datasets/schemas (different access controls) |

### 8.2 Lambda vs Kappa Architecture

```
Lambda Architecture:
┌──────────────────────────────────────────────────────┐
│  Sources → Batch Layer ─────────→ Serving Layer      │
│         └→ Speed Layer ─────────→ (merge at query)   │
│                                                      │
│  Pros: Different SLAs, proven at scale               │
│  Cons: Two codebases, merge complexity               │
└──────────────────────────────────────────────────────┘

Kappa Architecture:
┌──────────────────────────────────────────────────────┐
│  Sources → Single Stream Pipeline → Serving Layer    │
│         (handles both real-time and reprocessing)     │
│                                                      │
│  Pros: One codebase, simpler ops                     │
│  Cons: Reprocessing cost, not all fit streaming      │
└──────────────────────────────────────────────────────┘
```

**Decision matrix:**

| Factor | Lambda Better | Kappa Better |
|--------|--------------|--------------|
| Batch and streaming have different SLAs | Yes | |
| Team can maintain two codebases | Yes | |
| Want simplest operations | | Yes |
| Unified code for batch + streaming | | Yes |
| Very different batch vs stream logic | Yes | |
| Using Apache Beam or Spark Structured Streaming | | Yes |
| Historical reprocessing is frequent | | Yes (replay from Kafka) |
| Cost sensitivity (don't want always-on streaming) | Yes | |

**Recommendation**: Prefer Kappa with Apache Beam (Dataflow) or Spark Structured Streaming. Both frameworks unify batch and streaming with the same code. Use Lambda only when batch and streaming have fundamentally different requirements.

**The1 example**: Members-collector uses Kappa (single Beam pipeline handles both Kafka streaming and batch API). Tiers-collector uses batch-only (no streaming source), which is the simplest variant.

### 8.3 CDC Patterns for Lakehouse

```
Pattern 1: Log-based CDC (recommended for databases)
┌──────────┐     ┌──────────────┐     ┌─────────┐     ┌──────────┐
│ Source DB │────→│ CDC Capture  │────→│ Kafka / │────→│ Lakehouse│
│ (binlog/  │     │ (Debezium/   │     │ Pub/Sub │     │ (Iceberg/│
│  WAL)     │     │  DMS/        │     │         │     │  Delta)  │
│           │     │  Datastream) │     │         │     │          │
└──────────┘     └──────────────┘     └─────────┘     └──────────┘

Pattern 2: API-based CDC (for SaaS / REST APIs)
┌──────────┐     ┌──────────────┐     ┌─────────┐     ┌──────────┐
│ API       │────→│ Batch Fetch  │────→│ Compare │────→│ Lakehouse│
│ (REST/    │     │ (Dataflow/   │     │ (diff   │     │ (UPSERT/ │
│  GraphQL) │     │  Glue/ADF)   │     │  logic) │     │  DELETE) │
└──────────┘     └──────────────┘     └─────────┘     └──────────┘

Pattern 3: CDC to BQ via Storage Write API (The1 approach)
┌──────────┐     ┌──────────────┐     ┌─────────────────────────┐
│ Kafka /   │────→│ Beam DoFn    │────→│ BQ Storage Write API    │
│ API fetch │     │ (transform + │     │ (CDC: UPSERT / DELETE)  │
│           │     │  _is_delete) │     │ primary_key required    │
└──────────┘     └──────────────┘     └─────────────────────────┘
```

**CDC platform comparison:**

| Feature | GCP | AWS | Azure | Databricks |
|---------|-----|-----|-------|------------|
| Database CDC | Datastream | DMS | ADF CDC | Lakeflow Connect |
| CDC to warehouse | Storage Write API (BQ) | Zero-ETL / Glue | Fabric Mirroring | MERGE INTO |
| Streaming CDC | Dataflow + Kafka | MSK + Glue Streaming | Event Hubs + Stream Analytics | Structured Streaming |
| CDC format | Custom (Beam) | Debezium / DMS format | ADF change tracking | Delta CDF |
| Delete handling | Custom `_is_delete` flag | Debezium delete events | ADF soft delete | MERGE with WHEN NOT MATCHED BY SOURCE |

### 8.4 Data Mesh Considerations

**Four principles:**

1. **Domain ownership**: Each domain team owns their data products end-to-end
2. **Data as a product**: Discoverable, documented, SLA-guaranteed
3. **Self-serve platform**: Central team provides tools, not data
4. **Federated governance**: Central policies, domain execution

**Platform fit for data mesh:**

| Capability | Databricks | GCP | AWS | Azure |
|-----------|------------|-----|-----|-------|
| Cross-domain catalog | Unity Catalog (best) | Dataplex | DataZone | Purview |
| Data product registry | UC data products | Dataplex data products | DataZone assets | Purview collections |
| Access control | UC grants (fine-grained) | IAM + BigQuery ACL | Lake Formation | Purview policies |
| Data sharing | Delta Sharing (open protocol) | Analytics Hub | Clean Rooms | OneLake shortcuts |
| Lineage | UC lineage (column-level) | Dataplex lineage | DataZone lineage | Purview lineage |
| Quality monitoring | Lakehouse Monitoring | Dataplex DQ | Glue DQ | Fabric DQ rules |

### 8.5 Event-Driven Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Event-Driven Data Platform                                      │
│                                                                  │
│  Event Sources    Message Broker    Processing       Storage     │
│  ┌──────────┐    ┌────────────┐    ┌────────────┐  ┌─────────┐ │
│  │ App events│───→│ Kafka /    │───→│ Dataflow / │─→│ Iceberg │ │
│  │ DB CDC    │    │ Pub/Sub /  │    │ Flink /    │  │ Delta   │ │
│  │ IoT       │    │ Event Hubs │    │ Spark SS   │  │         │ │
│  │ Webhooks  │    │            │    │            │  │         │ │
│  └──────────┘    └─────┬──────┘    └────────────┘  └────┬────┘ │
│                        │                                 │      │
│                   DLQ (failed)              ┌────────────┘      │
│                   ┌────┴─────┐              │                   │
│                   │ Dead      │         Serving Layer            │
│                   │ Letter    │         ┌─────────────┐         │
│                   │ Queue     │         │ BigQuery /   │         │
│                   └──────────┘         │ Redshift /   │         │
│                                        │ SQL WH       │         │
│                                        └─────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

**Platform ranking for event-driven:**

| Rank | Platform | Stack | Why |
|------|----------|-------|-----|
| 1 | GCP | Pub/Sub + Dataflow | Simplest, fully serverless, exactly-once |
| 2 | AWS | MSK + Flink/Glue | Most flexible Kafka, best ecosystem |
| 3 | Databricks | Kafka + Structured Streaming | Best Spark integration, Delta CDF |
| 4 | Azure | Event Hubs + Stream Analytics | Kafka-compatible, but fewer features |

### 8.6 Real-Time Feature Store Pattern

```
┌─────────────────────────────────────────────────────────┐
│  Online Feature Store Architecture                       │
│                                                          │
│  Streaming          Batch                                │
│  ┌──────────┐      ┌──────────┐                         │
│  │ Kafka    │      │ Scheduled│                          │
│  │ events   │      │ batch    │                          │
│  └────┬─────┘      └────┬─────┘                         │
│       │                  │                               │
│       ▼                  ▼                               │
│  ┌──────────────────────────┐                           │
│  │ Feature Engineering      │                           │
│  │ (Spark / Beam / Flink)   │                           │
│  └────────┬─────────────────┘                           │
│           │                                              │
│     ┌─────┴──────┐                                      │
│     ▼            ▼                                       │
│  ┌────────┐  ┌───────────┐                              │
│  │ Online │  │ Offline   │                               │
│  │ Store  │  │ Store     │                               │
│  │ (Redis/│  │ (Iceberg/ │                               │
│  │ Bigtable│ │ Delta)    │                               │
│  │ DynamoDB│ │           │                               │
│  └───┬────┘  └─────┬─────┘                              │
│      │             │                                     │
│      ▼             ▼                                     │
│  ML Serving    ML Training                               │
│  (<10ms)       (batch)                                   │
└─────────────────────────────────────────────────────────┘
```

**Feature store platform options:**

| Platform | Feature Store | Online Store | Offline Store |
|----------|--------------|--------------|---------------|
| Databricks | Feature Engineering (built-in) | Online Tables | Delta Lake |
| GCP | Vertex AI Feature Store | Bigtable | BigQuery |
| AWS | SageMaker Feature Store | DynamoDB | S3 (Iceberg) |
| Open-source | Feast | Redis | Parquet/Iceberg |

---

## 9. Real-World Reference: The1 Data Platform

### Current Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    The1 Data Platform (GCP)                       │
│                                                                   │
│  ┌─ Streaming Path ──────────────────────────────────────┐       │
│  │ Kafka (AWS ap-southeast-1, Confluent Cloud)           │       │
│  │   Topics: loyalty.members.upgraded / downgraded       │       │
│  │     │                                                  │       │
│  │     ▼                                                  │       │
│  │ members-collector (Dataflow, Apache Beam 2.70)        │       │
│  │   ├─ job_type=normal → streaming Kafka consumer       │       │
│  │   ├─ job_type=initial_data → batch API backfill       │       │
│  │   ├─ Schema A/B/C detection → normalize → Beam Row   │       │
│  │   └─ CDC: UPSERT by memberId + DELETE by tierCode    │       │
│  └───────────────────────────────────────────────────────┘       │
│                                                                   │
│  ┌─ Batch Path ──────────────────────────────────────────┐       │
│  │ Cloud Scheduler (1 AM BKK daily)                      │       │
│  │     │                                                  │       │
│  │     ├─→ tiers-collector (Dataflow batch)              │       │
│  │     │   └─ REST API → all tiers → Iceberg → BQ       │       │
│  │     │                                                  │       │
│  │     └─→ members-tiers-history-collector (batch)       │       │
│  │         └─ REST API → member history → Iceberg → BQ   │       │
│  └───────────────────────────────────────────────────────┘       │
│                                                                   │
│  ┌─ Storage ─────────────────────────────────────────────┐       │
│  │                                                        │       │
│  │  Iceberg (GCS + BLMS REST Catalog)  │  BigQuery       │       │
│  │  ├─ Source layer (raw)               │  ├─ Refined     │       │
│  │  ├─ managed.Write (auto-create)      │  │  (CDC/APPEND)│       │
│  │  └─ Partition: ingestedTHDate (INT)  │  │  Partition:  │       │
│  │                                      │  │  DATE/HOUR   │       │
│  │  Format: Apache Iceberg v2           │  └─ Public      │       │
│  │  Catalog: BLMS REST (vended-creds)   │     (Dataform)  │       │
│  └──────────────────────────────────────┘─────────────────┘       │
│                                                                   │
│  ┌─ CI/CD ───────────────────────────────────────────────┐       │
│  │  GitLab CI + Terraform │ Trunk-based development      │       │
│  │  ├─ STG: auto-deploy on merge                         │       │
│  │  ├─ PROD: manual trigger (deploy:prod)                │       │
│  │  └─ deploy.py: BQ table management (native only)      │       │
│  └───────────────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────────────┘
```

### What Works Well

| Decision | Why It Works | Evidence |
|----------|-------------|---------|
| BigQuery (serverless warehouse) | Zero ops, scales automatically, pay-per-query | No cluster management, cost-effective for variable workloads |
| Iceberg on GCS via BLMS | Open format, multi-engine access, future-proof | Can query from Spark, BigQuery, DuckDB without data copy |
| Dataflow (Apache Beam) | Handles streaming + batch uniformly, autoscaling | Same code for Kafka consumer and API batch — only config differs |
| CDC via Storage Write API | Efficient upsert/delete on BigQuery | Member tier changes reflected in near-real-time |
| Dataform (semantic layer) | Free on GCP, SQL-based, version-controlled | No dbt licensing cost, integrated with BigQuery |
| Trunk-based development | Simple git workflow, fast merge cycles | No long-lived branches, fewer merge conflicts |
| GitLab CI + Terraform | Reliable infra-as-code, reproducible environments | STG and PROD identical infrastructure |
| BLMS REST Catalog (vended-credentials) | Secure, no long-lived service account keys | OAuth token exchange, same pattern as messaging-collector |

### What Could Be Improved

| Issue | Impact | Mitigation Plan |
|-------|--------|-----------------|
| BLMS maturity | PyIceberg compatibility issues (workaround: use managed.Write) | Monitor BLMS releases, PyIceberg issues |
| Beam talent pool | Harder to hire vs Spark developers | Document patterns well, Beam is learnable for Python devs |
| Streaming cancel vs drain | members-collector uses cancel (can lose in-flight data) | Upgrade deploy:prod to drain-first pattern |
| No DLQ yet | Poison messages crash pipeline | Implement DLQ pattern (research done, see docs) |
| No STG→PROD gate | Prod deploy doesn't depend on staging validation | Add staging smoke test as gate |
| Cross-cloud egress cost | Kafka in AWS, processing in GCP | Filter at source (Kafka Connect SMT), monitor egress |

### Alternative Approaches Considered

| Alternative | Pros | Cons | Decision | Confidence |
|------------|------|------|----------|------------|
| Spark on Dataproc vs Beam on Dataflow | Larger talent pool, interactive notebooks, familiar API | More ops, idle cluster costs, not truly serverless | Kept Dataflow | High |
| Delta Lake vs Iceberg | Better Databricks interop, larger community | GCP is Iceberg-native (BLMS), Delta less supported on GCP | Kept Iceberg | High |
| dbt vs Dataform | Multi-cloud, larger community, more features | Licensing cost (~$50-100/seat/month), Dataform free on GCP | Kept Dataform | Medium |
| Pub/Sub vs Kafka | Simpler, GCP-native, no cross-cloud | Kafka already in AWS, Schema Registry, richer ecosystem | Kept Kafka | High |
| Databricks on GCP vs native | Unity Catalog, Spark notebooks, ML platform | Additional cost (DBU markup), native GCP is sufficient | Kept native GCP | High |
| Cloud Composer vs Cloud Scheduler | DAG visualization, retry logic, dependencies | Over-engineered for simple scheduled batch jobs | Kept Scheduler | Medium |

### Lessons Learned

1. **Start with open formats**: Iceberg on GCS proved valuable — BigQuery reads it, Spark reads it, DuckDB reads it. No lock-in at data layer.

2. **Serverless is worth the trade-offs**: Dataflow auto-scales, no cluster management. Beam's smaller talent pool is a real cost, but operational simplicity wins.

3. **CDC is harder than it looks**: Implementing CDC DELETE required 3-layer safety checks (tier_code present → not in API → confirmed in BQ). Don't underestimate CDC complexity.

4. **Schema evolution happens**: Kafka messages arrived in 3 different schemas (A, B, C). Build schema detection into your pipeline, don't assume fixed format.

5. **Cross-cloud works but costs money**: Kafka in AWS → Dataflow in GCP works well functionally. Egress costs are real but manageable with proper filtering.

6. **IaC from day one**: Terraform + GitLab CI meant identical STG and PROD. Worth the upfront investment.

7. **managed.Write auto-creates tables**: No need for deploy.py Iceberg table management. Let the framework handle it.

---

## 10. Platform Selection Scorecard

### Template: Score 1-5 for each criterion, multiply by weight

| Criterion | Weight | GCP | AWS | Azure | Databricks | Notes |
|-----------|--------|-----|-----|-------|------------|-------|
| **Serverless/managed** | 15% | 5 | 3 | 4 | 3 | GCP: BQ+Dataflow truly serverless |
| **Cost efficiency** | 15% | 5 | 3 | 3 | 2 | GCP pay-per-query; DBx most expensive |
| **Open format support** | 10% | 5 | 5 | 3 | 5 | Azure: Delta-only native |
| **Streaming capability** | 10% | 5 | 4 | 3 | 4 | GCP: Beam unified; AWS: MSK strongest |
| **ML/AI platform** | 10% | 3 | 3 | 2 | 5 | Databricks: MLflow+Mosaic unmatched |
| **Governance** | 10% | 4 | 3 | 4 | 5 | Databricks: UC open-sourced |
| **Multi-cloud** | 10% | 2 | 2 | 2 | 5 | Only Databricks is truly multi-cloud |
| **Ecosystem maturity** | 5% | 3 | 5 | 4 | 4 | AWS: broadest service catalog |
| **BI integration** | 5% | 3 | 3 | 5 | 3 | Azure: Power BI DirectLake |
| **Team skill match** | 5% | * | * | * | * | Organization-specific |
| **Existing investment** | 5% | * | * | * | * | Organization-specific |

*Starred items: fill in based on your organization*

### Worked Example: The1 Data Platform Scoring

Assumptions: small team, serverless priority, Kafka streaming, Iceberg required, SQL analytics primary

| Criterion | Weight | GCP Score | Weighted |
|-----------|--------|-----------|----------|
| Serverless/managed | 15% | 5 | 0.75 |
| Cost efficiency | 15% | 5 | 0.75 |
| Open format (Iceberg) | 10% | 5 | 0.50 |
| Streaming | 10% | 5 | 0.50 |
| ML/AI | 10% | 3 | 0.30 |
| Governance | 10% | 4 | 0.40 |
| Multi-cloud | 10% | 2 | 0.20 |
| Ecosystem | 5% | 3 | 0.15 |
| BI integration | 5% | 3 | 0.15 |
| Team skill (GCP certified) | 5% | 5 | 0.25 |
| Existing investment (GCP) | 5% | 5 | 0.25 |
| **Total** | **100%** | | **4.20** |

Compared to: AWS 3.15, Azure 3.05, Databricks 3.60 → **GCP wins for this use case**

### How to Use the Scorecard

1. Copy the template to a spreadsheet
2. **Adjust weights** based on your organization's priorities:
   - Cost-sensitive? Increase cost weight to 20-25%
   - ML-focused? Increase ML weight to 15-20%
   - Multi-cloud mandate? Increase multi-cloud to 15-20%
3. **Score each platform** (1=poor, 5=excellent) based on YOUR requirements
4. **Fill in starred items** based on your team's skills and cloud investments
5. **Calculate weighted totals**: score × weight for each, then sum
6. **Top scorer** = recommended platform
7. **If scores within 0.3**: weight lock-in risk and team productivity as tiebreakers
8. **Validate with PoC**: always run a proof-of-concept on top 1-2 candidates

---

## 11. Team Skill Assessment Framework

### Skill Matrix Template

Rate your team's current skill level (1-5) for each area:

| Skill Area | 1 (None) | 2 (Basic) | 3 (Intermediate) | 4 (Advanced) | 5 (Expert) |
|-----------|----------|-----------|-------------------|---------------|-------------|
| **SQL** | No SQL | SELECT/JOIN | Window functions, CTEs | Query optimization, complex analytics | Can write query engines |
| **Python** | No Python | Scripts, pandas | Data pipelines, testing | Distributed computing, async | Framework contributor |
| **Spark** | Never used | pyspark basics | Spark SQL + DataFrame | Performance tuning, custom UDFs | Spark internals |
| **Beam** | Never used | Basic pipeline | Windowing, triggers | Custom IO, advanced DoFns | Beam contributor |
| **Cloud (GCP)** | No GCP | Console basics | BQ + GCS + IAM | Dataflow + Terraform | Architecture design |
| **Cloud (AWS)** | No AWS | Console basics | S3 + IAM + Lambda | EMR + Glue + MSK | Architecture design |
| **Cloud (Azure)** | No Azure | Portal basics | Blob + SQL + ADF | Fabric + Synapse | Architecture design |
| **Kafka** | Never used | Producer/consumer | Schema Registry, Connect | Operations, tuning | Kafka internals |
| **IaC (Terraform)** | No IaC | Basic resources | Modules, state mgmt | Multi-env, CI/CD | Custom providers |
| **CI/CD** | No CI/CD | Basic pipelines | Multi-stage, testing | Blue/green, canary | Platform engineering |

### Skill → Platform Mapping

| Your Team's Strongest Skills | Best Platform Fit | Ramp-up Time |
|------------------------------|-------------------|--------------|
| SQL + Python + GCP | GCP (BigQuery + Dataflow) | 2-4 weeks |
| SQL + Python + AWS | AWS (Redshift + Glue) | 3-5 weeks |
| Spark + Python | Databricks | 2-4 weeks |
| SQL Server + .NET + Power BI | Azure (Fabric/Synapse) | 3-5 weeks |
| SQL + Python + Kafka | GCP (Dataflow) or AWS (MSK + Glue) | 3-6 weeks |
| Spark + ML + Python | Databricks | 1-3 weeks |

### Hiring Market Reality (2026)

| Skill | Availability | Salary Premium | Trend |
|-------|-------------|----------------|-------|
| Spark/PySpark | High | Moderate | Stable |
| SQL analytics | Very High | Low | Stable |
| Apache Beam | Low | High | Growing slowly |
| Databricks/Delta | High | Moderate | Growing fast |
| BigQuery | Moderate | Moderate | Stable |
| Kafka | High | Moderate | Stable |
| Flink | Low-Moderate | High | Growing |
| Fabric/Synapse | Moderate | Moderate | Growing fast |
| dbt | High | Low-Moderate | Stable |
| Terraform | High | Moderate | Stable |

---

## 12. Anti-Patterns and Pitfalls

### Architecture Anti-Patterns

| Anti-Pattern | Why It's Bad | What to Do Instead |
|-------------|-------------|-------------------|
| **"Build it and they will come"** | Nobody uses the data platform | Start with 1 high-value use case, prove ROI, then expand |
| **Premature multi-cloud** | 2-3x complexity for hypothetical future flexibility | Use open formats (Iceberg/Delta) for portability, single cloud for compute |
| **Over-engineering medallion** | 7 layers instead of 3 (bronze-silver-gold) | Stick to 3 layers. Add intermediates only when proven necessary |
| **Schema-on-read everything** | "We'll figure out the schema later" → nobody can query it | Define schema at silver layer. Bronze can be schema-on-read |
| **No data contracts** | Upstream changes break downstream pipelines silently | Define explicit contracts (schema registry, column-level SLAs) |
| **DIY everything** | Building custom scheduler when Airflow/Cloud Scheduler works | Use managed services. Build custom only for unique requirements |
| **Big bang migration** | 18-month project, high risk, delayed value | Migrate domain by domain, prove value incrementally |

### Cost Anti-Patterns

| Anti-Pattern | Why It's Bad | What to Do Instead |
|-------------|-------------|-------------------|
| **No cost monitoring** | Bill surprises at month-end | Set budgets + alerts from day 1 |
| **On-demand everything** | 3-5x more expensive than committed use | Reserved/committed use for predictable workloads |
| **SELECT * everywhere** | Scan entire table when you need 3 columns | Column pruning, partitioned tables, columnar format |
| **Never cleaning up** | Dev/test tables accumulate forever | Automated TTL policies, regular resource audits |
| **Cross-region for "DR"** | Egress costs without actual DR testing | Use multi-zone (free) before multi-region |
| **Oversized streaming** | 10 workers for 100 msg/sec | Right-size autoscaling, min/max bounds |

### Operational Anti-Patterns

| Anti-Pattern | Why It's Bad | What to Do Instead |
|-------------|-------------|-------------------|
| **No CI/CD** | Manual deployments, snowflake environments | IaC (Terraform) + CI/CD from day 1 |
| **No staging environment** | Test in production | Always have STG that mirrors PROD |
| **Cancel instead of drain** | Streaming job loses in-flight data | Use drain for graceful shutdown |
| **No DLQ** | Poison messages crash entire pipeline | Dead letter queue for unprocessable messages |
| **Shared service accounts** | Can't audit who did what | Per-workload service accounts with least privilege |
| **No schema evolution plan** | Adding columns breaks everything | Design for evolution: additive changes, optional fields |

---

## 13. Technology Radar

### Adopt (use in production now)

| Technology | Category | Why |
|-----------|----------|-----|
| Apache Iceberg | Table Format | Industry standard, multi-engine support, all clouds adopting |
| Delta Lake | Table Format | Databricks/Azure native, UniForm bridges to Iceberg |
| BigQuery | Warehouse | Proven at scale, serverless, Iceberg-native via BLMS |
| Terraform | IaC | Multi-cloud, mature, large community |
| Apache Beam | Processing | Unified batch+stream, GCP-native, portable |
| Spark / PySpark | Processing | Industry standard, huge ecosystem |
| Apache Kafka | Streaming | Standard event streaming, massive ecosystem |

### Trial (evaluate for your use case)

| Technology | Category | Why Trial |
|-----------|----------|-----------|
| Microsoft Fabric | Platform | Unified experience promising, but maturity gaps remain |
| Databricks Unity Catalog (OSS) | Governance | Open-sourced 2024, could be universal catalog |
| Apache Flink | Processing | True streaming (not micro-batch), growing adoption |
| dbt Mesh | Transformation | Cross-project lineage, but licensing cost |
| S3 Tables (AWS) | Storage | Managed Iceberg, could simplify S3-based lakehouses |
| DuckDB | Analytics | Excellent for local dev/testing, embedded analytics |
| Apache XTable | Interop | Convert between Iceberg/Delta/Hudi |

### Assess (watch, not ready for production)

| Technology | Category | Why Assess |
|-----------|----------|------------|
| Polaris Catalog (Snowflake OSS) | Catalog | Open-source Iceberg REST catalog, new |
| Apache Paimon | Table Format | Streaming-first table format, nascent |
| LakeFlow (Databricks) | Ingestion | Declarative ingestion, early stage |
| Fabric Real-Time Intelligence | Analytics | KQL-based streaming analytics, maturing |
| GCP Dataplex v2 | Governance | Data products support, replacing Data Catalog |

### Hold (do not adopt for new projects)

| Technology | Category | Why Hold |
|-----------|----------|----------|
| Apache Hive | Table Format | Replaced by Iceberg/Delta |
| Hadoop HDFS | Storage | Cloud storage is cheaper and more scalable |
| Synapse Dedicated SQL Pools | Warehouse | Uncertain future, Fabric is the direction |
| AWS Glue (v1/v2 legacy) | ETL | Use Glue v4+ or EMR Serverless instead |
| Azure HDInsight | Processing | Being superseded by Fabric Spark |
| Apache Pig | Processing | Dead project |

### Adoption Timeline

```
2024          2025          2026          2027
  │             │             │             │
  ├─ Iceberg GA across GCP/AWS ──────────── mainstream ──→
  ├─ Delta UniForm v2 (Iceberg interop) ──── standard ──→
  ├─ Fabric GA ────── maturity ────────────── consider ──→
  ├─ S3 Tables GA ─── evaluate ────────────── adopt? ───→
  ├─ Unity Catalog OSS ── evaluate ─────────── adopt? ──→
  ├─ Flink managed ──── growing ───────────── niche ────→
  ├─ Synapse ──────── declining ────── hold/migrate ────→
  ├─ Hadoop ───────── decommission ────── gone ─────────→
  └─ Apache Paimon ── nascent ──────── evaluate ────────→
```

---

## References

- [CROSS_CLOUD_COMPARISON.md](./CROSS_CLOUD_COMPARISON.md) — Feature-by-feature comparison across all platforms
- [GCP_DATA_PLATFORM.md](../GCP/DATA_PLATFORM/GCP_DATA_PLATFORM.md) — BigQuery, Iceberg, Dataflow deep dive
- [GCP_CLOUD_SERVICES.md](../GCP/CLOUD_SERVICE/GCP_CLOUD_SERVICES.md) — GCP services, Terraform, CI/CD
- [AWS_DATA_PLATFORM.md](../AWS/DATA_PLATFORM/AWS_DATA_PLATFORM.md) — Redshift, S3 Tables, EMR deep dive
- [AWS_CLOUD_SERVICES.md](../AWS/CLOUD_SERVICE/AWS_CLOUD_SERVICES.md) — AWS services, CloudFormation, CI/CD
- [AZURE_DATA_PLATFORM.md](../AZURE/DATA_PLATFORM/AZURE_DATA_PLATFORM.md) — Synapse, Fabric, DirectLake deep dive
- [AZURE_CLOUD_SERVICES.md](../AZURE/CLOUD_SERVICE/AZURE_CLOUD_SERVICES.md) — Azure services, Bicep, CI/CD
- [DATABRICKS_DATA_PLATFORM.md](../DATABRICKS/DATA_PLATFORM/DATABRICKS_DATA_PLATFORM.md) — Delta Lake, Unity Catalog, MLflow
- [DATABRICKS_CLOUD_SERVICES.md](../DATABRICKS/CLOUD_SERVICE/DATABRICKS_CLOUD_SERVICES.md) — Databricks services, Terraform, CI/CD

---

> **Document Version**: 2.0 | **Last Updated**: 2026-03-05
