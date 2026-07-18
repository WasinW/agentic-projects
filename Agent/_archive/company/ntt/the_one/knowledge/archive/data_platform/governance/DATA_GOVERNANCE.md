# Data Governance

Comprehensive data governance strategy for The1 Data Platform, covering data profiling, quality, lineage, validation, sharing, and naming conventions across all domain projects.

## Table of Contents

- [Vision](#vision)
- [Platform Architecture](#platform-architecture)
- [Data Governance with Dataplex](#data-governance-with-dataplex)
  - [1. Data Profiling](#1-data-profiling)
  - [2. Data Quality](#2-data-quality)
  - [3. Data Lineage](#3-data-lineage)
  - [4. Data Validation](#4-data-validation)
  - [5. Data Sharing](#5-data-sharing)
- [Naming Conventions](#naming-conventions)
- [Current State](#current-state)
- [Implementation Roadmap](#implementation-roadmap)

---

## Vision

The1 Data Platform is an enterprise-grade data platform built on GCP with three core design principles:

1. **Domain Isolation** -- Each business domain (loyalty, sales, insight) runs in its own GCP project with dedicated service accounts, networking, and IAM boundaries.
2. **Central Observability** -- A cross-domain observability project aggregates metrics, logs, lineage, and quality results for unified monitoring and governance.
3. **Data Governance via Dataplex** -- GCP Dataplex serves as the governance hub for data profiling, quality scanning, lineage tracking, and metadata management across all domains.

```mermaid
graph TB
    subgraph "Domain Projects"
        LP["the1-loyalty-data-{env}<br/>Loyalty Domain"]
        SP["the1-sales-data-{env}<br/>Sales Domain"]
        IP["the1-insight-{env}<br/>Insight Domain"]
    end

    subgraph "Central Observability"
        OBS["the1-data-platform-obs"]
        OBS --> CM["Cloud Monitoring<br/>Cross-project metrics"]
        OBS --> CL["Cloud Logging<br/>Centralized log sink"]
        OBS --> DPX["Dataplex<br/>Data governance hub"]
        OBS --> BQA["BigQuery<br/>Analytics on metrics"]
        OBS --> DASH["Looker / Data Studio<br/>Dashboards"]
    end

    LP --> OBS
    SP --> OBS
    IP --> OBS

    style OBS fill:#4285F4,color:#fff
    style LP fill:#34A853,color:#fff
    style SP fill:#FBBC04,color:#000
    style IP fill:#EA4335,color:#fff
```

---

## Platform Architecture

Each domain project follows a consistent internal architecture for data flow, storage, and governance:

```mermaid
graph LR
    subgraph "Ingestion"
        K["Kafka Topics"]
        API["REST APIs"]
    end

    subgraph "Processing"
        DF["Dataflow Jobs<br/>(Apache Beam)"]
    end

    subgraph "Storage"
        ICE["Iceberg Tables<br/>(GCS + BigLake Metastore)"]
        BQ["BigQuery Tables<br/>(source / refined / public)"]
    end

    subgraph "Governance (Dataplex)"
        PROF["Data Profiling"]
        QUAL["Data Quality"]
        LIN["Data Lineage"]
    end

    subgraph "Consumers"
        DASH2["Dashboards"]
        DS["Data Science"]
        APIS["Downstream APIs"]
    end

    K --> DF
    API --> DF
    DF --> ICE
    ICE --> BQ
    BQ --> DASH2
    BQ --> DS
    BQ --> APIS

    BQ --> PROF
    BQ --> QUAL
    DF --> LIN
    BQ --> LIN

    style DF fill:#4285F4,color:#fff
    style ICE fill:#34A853,color:#fff
    style BQ fill:#FBBC04,color:#000
```

---

## Data Governance with Dataplex

### 1. Data Profiling

Dataplex auto data profiling provides statistical analysis of BigQuery tables without writing any code. It scans table data and produces a profile report covering distributions, null rates, cardinality, min/max values, and more.

#### What Data Profiling Provides

| Metric | Description |
|--------|-------------|
| **Null Rate** | Percentage of NULL values per column |
| **Distinct Count** | Number of unique values (cardinality) |
| **Distribution** | Value frequency histograms for string/numeric columns |
| **Min / Max / Mean** | Statistical bounds for numeric columns |
| **String Length** | Min/max/avg length for string columns |
| **Top N Values** | Most frequent values per column |
| **Pattern Detection** | Regex patterns detected in string columns |

#### Profiling Configuration

- **Scope**: Refined BigQuery tables (the primary consumer-facing layer).
- **Schedule**: Weekly profiling scans (sufficient for analytical tables; daily for high-change tables if needed).
- **Sampling**: Dataplex supports sampling for large tables to reduce cost. Use 10% sampling for tables over 10M rows.
- **Export**: Profile results are stored in Dataplex and can be exported to BigQuery for custom dashboards.

#### Profiling Targets by Collector

| Collector | Table | Priority | Notes |
|-----------|-------|----------|-------|
| members-collector | `refined.members` | HIGH | Core entity, monitor cardinality + null rates |
| tiers-collector | `refined.member_tier` | HIGH | Tier distribution, validity checks |
| members-tiers-history | `refined.members_tiers_history` | MEDIUM | Historical, large volume |
| purchases-collector | `refined.raw_sales` | HIGH | Transaction data, financial accuracy |

```mermaid
graph TD
    BQ["BigQuery Table<br/>(refined dataset)"]
    DPX["Dataplex<br/>Auto Data Profiling"]
    REPORT["Profile Report<br/>Null rates, distributions,<br/>cardinality, patterns"]
    EXPORT["BigQuery Export<br/>Profile results table"]
    DASH["Dashboard<br/>Profile trends over time"]

    BQ -->|"Scheduled scan"| DPX
    DPX --> REPORT
    REPORT --> EXPORT
    EXPORT --> DASH

    style DPX fill:#4285F4,color:#fff
    style REPORT fill:#34A853,color:#fff
```

---

### 2. Data Quality

Dataplex auto data quality provides rule-based quality scanning for BigQuery tables. Rules are defined declaratively, executed on schedule, and results are exported for monitoring and alerting.

#### Seven Quality Dimensions

| Dimension | Description | Example Rule |
|-----------|-------------|--------------|
| **Freshness** | Data is up-to-date and timely | `etlLoadTime` within last 2 hours (streaming) or 24 hours (batch) |
| **Volume** | Expected data volume is present | Row count > 0 for daily partitions; row count within expected range |
| **Completeness** | Required fields are populated | `member_id` NOT NULL rate >= 99.9% |
| **Validity** | Values conform to expected format/range | `tier_name` IN ('Silver', 'Gold', 'Platinum', 'Diamond') |
| **Consistency** | Data is consistent across sources | `members.count` matches `members_tiers_history.distinct(member_id)` |
| **Accuracy** | Data reflects real-world truth | Cross-validate against source API (sample-based) |
| **Uniqueness** | No unintended duplicates | `(member_id, etlLoadTime)` is unique in append mode |

#### Rule Types

**Predefined Rules** (no SQL required):

| Rule Type | Usage | Example |
|-----------|-------|---------|
| **Range** | Numeric bounds check | `etlLoadTime BETWEEN 2024010100 AND 2030123123` |
| **Null** | Null rate threshold | `member_id` null rate < 0.1% |
| **Set** | Allowed values | `tier_name IN ('Silver', 'Gold', 'Platinum', 'Diamond')` |
| **Regex** | Pattern matching | `member_id MATCHES '^[A-Z0-9]{10,20}$'` |
| **Uniqueness** | Duplicate detection | `event_id` is unique within partition |

**Custom SQL Rules** (for complex logic):

```sql
-- Freshness: latest partition is within expected window
SELECT COUNT(*) = 0 AS rule_passed
FROM `project.refined.members`
WHERE etlLoadTime < FORMAT_TIMESTAMP('%Y%m%d%H', TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 3 HOUR))
  AND _PARTITIONTIME = TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), DAY)

-- Volume: daily row count within expected range
SELECT COUNT(*) BETWEEN 1000 AND 1000000 AS rule_passed
FROM `project.refined.members`
WHERE DATE(_PARTITIONTIME) = CURRENT_DATE()

-- Consistency: member_id exists in members table
SELECT COUNT(*) = 0 AS rule_passed
FROM `project.refined.members_tiers_history` h
LEFT JOIN `project.refined.members` m ON h.member_id = m.member_id
WHERE m.member_id IS NULL
```

#### Scan Configuration

- **Incremental Scans**: Scan only new data since last scan (recommended for streaming tables). Uses partition filter to process only recent partitions.
- **Full Table Scans**: Scan entire table (recommended for batch tables or periodic deep validation).
- **Schedule**: Streaming tables -- every 6 hours (incremental). Batch tables -- daily after batch job completes.
- **Results Export**: All quality scan results are exported to a dedicated BigQuery dataset for dashboarding.
- **Notifications**: Email alerts sent to data team on quality rule failures via Cloud Monitoring alert policies.

#### Quality Score

Dataplex computes a quality score per scan as: `passed_rules / total_rules * 100`. Target: maintain >= 95% quality score across all tables.

```mermaid
graph TD
    subgraph "Quality Scan Configuration"
        RULES["Quality Rules<br/>Predefined + Custom SQL"]
        SCHED["Schedule<br/>6h incremental / daily full"]
    end

    subgraph "Execution"
        SCAN["Dataplex Quality Scan"]
        BQ_TABLE["BigQuery Table"]
    end

    subgraph "Results & Actions"
        RESULTS["Scan Results<br/>Pass/Fail per rule"]
        EXPORT_BQ["BigQuery Export<br/>Quality results dataset"]
        ALERT["Cloud Monitoring<br/>Email alerts on failure"]
        DASH["Quality Dashboard<br/>Score trends, failures"]
    end

    RULES --> SCAN
    SCHED --> SCAN
    BQ_TABLE --> SCAN
    SCAN --> RESULTS
    RESULTS --> EXPORT_BQ
    RESULTS --> ALERT
    EXPORT_BQ --> DASH

    style SCAN fill:#4285F4,color:#fff
    style ALERT fill:#EA4335,color:#fff
```

---

### 3. Data Lineage

Dataplex Data Lineage API provides end-to-end visibility into how data flows through the platform -- from source systems through processing to consumption.

#### Auto-Captured Lineage

When the Data Lineage API is enabled, GCP automatically captures lineage from:

| Service | What is Captured | Granularity |
|---------|-----------------|-------------|
| **BigQuery** | Query jobs, copy jobs, load jobs | Table-level (column-level for some operations) |
| **Dataflow** | Pipeline read/write operations | Table-level (source and sink) |
| **Dataproc** | Spark/Hive jobs | Table-level |

#### End-to-End Lineage for The1 Data Platform

```mermaid
graph LR
    subgraph "Sources"
        K1["Kafka<br/>loyalty.members.created"]
        K2["Kafka<br/>loyalty.tiers.updated"]
        API1["Loyalty API<br/>/tiers"]
        API2["Loyalty API<br/>/members-tiers"]
    end

    subgraph "Processing"
        DF1["members-collector<br/>(Dataflow Streaming)"]
        DF2["tiers-collector<br/>(Dataflow Batch)"]
        DF3["members-tiers-history<br/>(Dataflow Batch)"]
    end

    subgraph "Source Layer"
        ICE1["Iceberg: source.members"]
        ICE2["Iceberg: source.member_tier"]
        ICE3["Iceberg: source.members_tiers_history"]
    end

    subgraph "Refined Layer"
        BQ1["BQ: refined.members"]
        BQ2["BQ: refined.member_tier"]
        BQ3["BQ: refined.members_tiers_history"]
    end

    subgraph "Consumers"
        DASH["Dashboards"]
        DS["Data Science"]
        PUB["Public APIs"]
    end

    K1 --> DF1
    K2 --> DF1
    API1 --> DF2
    API2 --> DF3

    DF1 --> ICE1
    DF2 --> ICE2
    DF3 --> ICE3

    ICE1 --> BQ1
    ICE2 --> BQ2
    ICE3 --> BQ3

    BQ1 --> DASH
    BQ2 --> DS
    BQ3 --> PUB

    style DF1 fill:#4285F4,color:#fff
    style DF2 fill:#4285F4,color:#fff
    style DF3 fill:#4285F4,color:#fff
```

#### Custom Lineage Events

For services not automatically tracked (Kafka, REST APIs), custom lineage events can be registered via the Data Lineage API:

```python
from google.cloud import datacatalog_lineage_v1

client = datacatalog_lineage_v1.LineageClient()

# Create a lineage event for Kafka -> Dataflow
process = client.create_process(
    parent=f"projects/{project}/locations/{location}",
    process=datacatalog_lineage_v1.Process(
        display_name="members-collector",
        attributes={"collector": "members-collector", "job_type": "streaming"},
    ),
)

run = client.create_run(
    parent=process.name,
    run=datacatalog_lineage_v1.Run(
        display_name=f"run-{job_id}",
        state=datacatalog_lineage_v1.Run.State.STARTED,
        start_time=timestamp_pb2.Timestamp(seconds=int(time.time())),
    ),
)

event = client.create_lineage_event(
    parent=run.name,
    lineage_event=datacatalog_lineage_v1.LineageEvent(
        source=datacatalog_lineage_v1.EntityReference(
            fully_qualified_name="kafka:loyalty.members.created"
        ),
        target=datacatalog_lineage_v1.EntityReference(
            fully_qualified_name=f"bigquery:projects/{project}/datasets/source/tables/members"
        ),
    ),
)
```

#### Impact Analysis

With lineage in place, you can answer critical operational questions:

- **Upstream impact**: "If Kafka topic `loyalty.members.created` has a schema change, which tables and dashboards are affected?"
- **Downstream impact**: "If I drop the `tier_name` column from `refined.member_tier`, what breaks?"
- **Root cause**: "Dashboard shows stale data -- trace lineage back to find which pipeline is delayed."

---

### 4. Data Validation

Data validation is implemented at multiple layers in the platform to catch errors as early as possible.

#### Validation Layers

```mermaid
graph TD
    subgraph "Layer 1: Configuration"
        PYDANTIC["Pydantic DTOs<br/>Schema validation at config load"]
    end

    subgraph "Layer 2: Runtime (DoFns)"
        DOFN["Apache Beam DoFns<br/>try/except per record"]
        LOG["Cloud Logging<br/>Structured error logs"]
        DROP["Drop invalid record<br/>(current behavior)"]
        DLQ["Dead Letter Queue<br/>(planned)"]
    end

    subgraph "Layer 3: Storage"
        ICEBERG["Iceberg Schema<br/>Type enforcement on write"]
        BQ_SCHEMA["BigQuery Schema<br/>REQUIRED fields, type checks"]
    end

    subgraph "Layer 4: Post-Write"
        DATAPLEX["Dataplex Quality Scans<br/>Rule-based validation"]
    end

    PYDANTIC -->|"valid config"| DOFN
    DOFN -->|"valid record"| ICEBERG
    DOFN -->|"invalid record"| LOG
    LOG --> DROP
    LOG -.->|"future"| DLQ
    ICEBERG --> BQ_SCHEMA
    BQ_SCHEMA --> DATAPLEX

    style PYDANTIC fill:#34A853,color:#fff
    style DOFN fill:#4285F4,color:#fff
    style DATAPLEX fill:#FBBC04,color:#000
    style DLQ fill:#EA4335,color:#fff
```

#### Layer 1: Configuration Validation (Pydantic)

All collector configurations are validated at startup using Pydantic models. Invalid configuration prevents the pipeline from starting.

- YAML config files (`base.yaml`, `stg.yaml`, `prod.yaml`) are loaded and merged.
- `PipelineSettings` (Pydantic BaseSettings) validates all required fields, types, and constraints.
- `ConfigAdapter` transforms settings into domain-specific frozen dataclasses (`BlmsCatalogConfig`, `ManagedIcebergWriteConfig`, etc.).

#### Layer 2: Runtime Validation (DoFns)

Each processing step (DoFn) wraps its logic in try/except to handle malformed records:

- **Current behavior**: Log the error with structured metadata (record content, step name, error message) and drop the record.
- **Planned behavior**: Route failed records to a Dead Letter Queue (DLQ) for later replay. See [DLQ_STRATEGY.md](./DLQ_STRATEGY.md) for details.

#### Layer 3: Storage Schema Enforcement

- **Iceberg**: PyArrow schema enforces column types on write. Type mismatches raise exceptions caught by Layer 2.
- **BigQuery**: Table schema with `mode: REQUIRED` fields rejects NULL values for mandatory columns. Type mismatches fail the write operation.

#### Layer 4: Post-Write Quality (Dataplex)

After data is written, Dataplex quality scans provide a safety net to catch issues that passed through earlier layers. See [Section 2: Data Quality](#2-data-quality).

---

### 5. Data Sharing

Data sharing controls who can access which data across projects and domains.

#### Current: Per-Collector IAM

Each collector's service account has scoped access to only the datasets it writes to:

```mermaid
graph TD
    subgraph "Loyalty Domain Project"
        SA1["t1-members-collector SA"]
        SA2["t1-tiers-collector SA"]
        SA3["t1-members-tiers-history SA"]

        DS_SRC["source dataset"]
        DS_REF["refined dataset"]
    end

    SA1 -->|"dataEditor"| DS_SRC
    SA1 -->|"dataEditor"| DS_REF
    SA2 -->|"dataEditor"| DS_SRC
    SA2 -->|"dataEditor"| DS_REF
    SA3 -->|"dataEditor"| DS_SRC
    SA3 -->|"dataEditor"| DS_REF

    style SA1 fill:#4285F4,color:#fff
    style SA2 fill:#4285F4,color:#fff
    style SA3 fill:#4285F4,color:#fff
```

IAM is granted via Terraform in each collector's `biglake-metastore.tf`:
- Source dataset: `roles/bigquery.dataEditor` on the BigLake-managed source dataset.
- Refined dataset: `roles/bigquery.dataEditor` on the refined dataset.

#### Future: Cross-Domain Data Sharing

| Mechanism | Use Case | Status |
|-----------|----------|--------|
| **Authorized Views** | Expose filtered subsets of data to other projects | Planned |
| **Authorized Datasets** | Grant read access to entire datasets across projects | Planned |
| **Analytics Hub** | Publish datasets as listings for discovery and subscription | Future |
| **Central Analytics Project** | Dedicated project for cross-domain queries and dashboards | Future |

#### Cross-Domain Sharing Architecture (Future)

```mermaid
graph TB
    subgraph "Loyalty Project"
        L_REF["refined.members<br/>refined.member_tier"]
    end

    subgraph "Sales Project"
        S_REF["refined.raw_sales<br/>refined.transactions"]
    end

    subgraph "Central Analytics Project"
        AV1["authorized_view:<br/>loyalty_members"]
        AV2["authorized_view:<br/>sales_summary"]
        CROSS["Cross-domain joins<br/>Member + Purchase analysis"]
    end

    subgraph "Consumers"
        DASH["Dashboards"]
        DS["Data Science"]
    end

    L_REF -->|"authorized dataset"| AV1
    S_REF -->|"authorized dataset"| AV2
    AV1 --> CROSS
    AV2 --> CROSS
    CROSS --> DASH
    CROSS --> DS

    style CROSS fill:#4285F4,color:#fff
```

---

## Naming Conventions

Consistent naming conventions are critical for governance, discoverability, and automation.

### GCP Projects

| Pattern | Example | Description |
|---------|---------|-------------|
| `the1-{domain}-data-{env}` | `the1-loyalty-data-stg` | Domain data project (with `-data` suffix) |
| `the1-{domain}-{env}` | `the1-insight-prod` | Domain project (no `-data` suffix) |
| `the1-data-platform-obs` | `the1-data-platform-obs` | Central observability (single project) |

Environments: `dev`, `stg`, `prod`

### Service Accounts

| Pattern | Example |
|---------|---------|
| `t1-{service}@the1-{domain}-data-{env}.iam.gserviceaccount.com` | `t1-members-collector@the1-loyalty-data-stg.iam.gserviceaccount.com` |
| `t1-{service}@the1-{domain}-data-{env}.iam.gserviceaccount.com` | `t1-tiers-collector@the1-loyalty-data-prod.iam.gserviceaccount.com` |
| `t1-{service}@the1-{domain}-data-{env}.iam.gserviceaccount.com` | `t1-members-tiers-history@the1-loyalty-data-stg.iam.gserviceaccount.com` |

### GCS Buckets

| Type | Pattern | Example |
|------|---------|---------|
| **Source** | `the1-{domain}-source-{env}` | `the1-loyalty-source-stg` |
| **Per-Collector** | `the1-{domain}-{env}-{collector}` | `the1-loyalty-stg-members-collector` |
| **Config** | `the1-{domain}-config-{env}` | `the1-loyalty-config-prod` |
| **Terraform State** | `devops-terraformstate-nonprod` | Shared across all projects |

### BigQuery Datasets

| Dataset | Purpose | Access |
|---------|---------|--------|
| `source` | Raw/Iceberg-backed tables (BigLake external tables) | Collector SAs (write), analysts (read) |
| `refined` | Transformed analytics-ready tables | Collector SAs (write), analysts (read) |
| `public` | Published/shared tables for downstream consumers | Read-only for consumers |
| `golden` | Curated, deduplicated tables (e.g., purchases) | Read-only, highest quality |
| `dead_letter` | Failed records from DLQ (planned) | Collector SAs (write), ops team (read) |

### Iceberg Tables

| Component | Convention | Example |
|-----------|-----------|---------|
| **Catalog** | BigLake Metastore (BLMS REST) | `projects/{project}/locations/{location}/catalogs/default` |
| **Namespace** | `source` | `source` |
| **Table** | `{entity_name}` (snake_case) | `source.members`, `source.member_tier`, `source.members_tiers_history` |

### Kafka Topics

| Pattern | Example |
|---------|---------|
| `loyalty.{entity}.{event}` | `loyalty.members.created` |
| `loyalty.{entity}.{action}` | `loyalty.tiers.updated` |

### Terraform State

| Pattern | Example |
|---------|---------|
| `devops-terraformstate-nonprod/the1-{domain}/services/{service}/{component}` | `devops-terraformstate-nonprod/the1-loyalty/services/members-collector/infrastructure` |

---

## Current State

Summary of what is implemented versus planned:

| Governance Feature | Status | Details |
|-------------------|--------|---------|
| **Data Profiling** | NOT YET ENABLED | Dataplex API not enabled; profiling scans not configured |
| **Data Quality** | NOT YET ENABLED | Dataplex API not enabled; quality rules not defined |
| **Data Lineage** | NOT YET ENABLED | Dataplex Lineage API not enabled (Dataflow auto-capture available when enabled) |
| **Data Validation (Config)** | IMPLEMENTED | Pydantic DTOs validate all config at startup |
| **Data Validation (Runtime)** | IMPLEMENTED | try/except in DoFns, structured logging, record drop |
| **Data Validation (Schema)** | IMPLEMENTED | Iceberg PyArrow schema + BigQuery REQUIRED fields |
| **Data Sharing (Per-Collector IAM)** | IMPLEMENTED | Each collector SA has scoped dataset access via Terraform |
| **Data Sharing (Cross-Domain)** | NOT YET IMPLEMENTED | Authorized views/datasets planned for future |
| **Naming Conventions** | ESTABLISHED | Followed consistently across all projects and collectors |
| **DLQ** | NOT YET IMPLEMENTED | Research complete; see [DLQ_STRATEGY.md](./DLQ_STRATEGY.md) |

---

## Implementation Roadmap

### Phase 1: Enable Dataplex Foundation

**Prerequisites**: Dataplex API enabled in all domain projects.

| Step | Action | Project(s) | Owner |
|------|--------|-----------|-------|
| 1.1 | Enable Dataplex API | All domain projects | Platform team |
| 1.2 | Create Dataplex Lake per domain | `the1-loyalty-data-{env}`, `the1-sales-data-{env}` | Platform team |
| 1.3 | Create Zones per lake | `source`, `refined`, `curated` per lake | Platform team |
| 1.4 | Register BigQuery datasets as Dataplex assets | All datasets in all projects | Platform team |

### Phase 2: Data Profiling

| Step | Action | Priority |
|------|--------|----------|
| 2.1 | Enable auto data profiling on `refined` tables | HIGH |
| 2.2 | Configure weekly profiling schedule | MEDIUM |
| 2.3 | Export profile results to BigQuery | MEDIUM |
| 2.4 | Build profile trend dashboard | LOW |

### Phase 3: Data Quality

| Step | Action | Priority |
|------|--------|----------|
| 3.1 | Define quality rules per table (freshness, completeness, validity) | HIGH |
| 3.2 | Configure incremental scans for streaming tables (6h) | HIGH |
| 3.3 | Configure daily full scans for batch tables | HIGH |
| 3.4 | Export quality results to BigQuery | MEDIUM |
| 3.5 | Set up email alerts on quality failures | HIGH |
| 3.6 | Build quality score dashboard | MEDIUM |

### Phase 4: Data Lineage

| Step | Action | Priority |
|------|--------|----------|
| 4.1 | Enable Data Lineage API in all projects | HIGH |
| 4.2 | Verify auto-capture from Dataflow and BigQuery | HIGH |
| 4.3 | Register custom lineage events for Kafka sources | MEDIUM |
| 4.4 | Register custom lineage events for REST API sources | MEDIUM |
| 4.5 | Build lineage visualization dashboard | LOW |

### Phase 5: Central Observability

| Step | Action | Priority |
|------|--------|----------|
| 5.1 | Create central observability project (`the1-data-platform-obs`) | HIGH |
| 5.2 | Configure cross-project log sinks | HIGH |
| 5.3 | Configure cross-project metric scopes | HIGH |
| 5.4 | Set up Dataplex governance hub in central project | MEDIUM |
| 5.5 | Build unified dashboards (Looker / Data Studio) | MEDIUM |

### Phase 6: Cross-Domain Data Sharing

| Step | Action | Priority |
|------|--------|----------|
| 6.1 | Define authorized views for cross-domain access | MEDIUM |
| 6.2 | Set up authorized datasets between projects | MEDIUM |
| 6.3 | Create central analytics project | LOW |
| 6.4 | Evaluate Analytics Hub for data marketplace | LOW |

```mermaid
gantt
    title Data Governance Implementation Roadmap
    dateFormat  YYYY-MM
    axisFormat  %Y-%m

    section Phase 1: Foundation
    Enable Dataplex API          :p1a, 2026-03, 2w
    Create Lakes & Zones         :p1b, after p1a, 2w
    Register Assets              :p1c, after p1b, 1w

    section Phase 2: Profiling
    Enable Auto Profiling        :p2a, after p1c, 1w
    Configure Schedules          :p2b, after p2a, 1w
    Profile Dashboards           :p2c, after p2b, 2w

    section Phase 3: Quality
    Define Quality Rules         :p3a, after p1c, 2w
    Configure Scans              :p3b, after p3a, 1w
    Alerts & Dashboards          :p3c, after p3b, 2w

    section Phase 4: Lineage
    Enable Lineage API           :p4a, after p1c, 1w
    Verify Auto-Capture          :p4b, after p4a, 1w
    Custom Lineage Events        :p4c, after p4b, 2w

    section Phase 5: Central Obs
    Create Obs Project           :p5a, after p3c, 2w
    Cross-Project Config         :p5b, after p5a, 2w
    Unified Dashboards           :p5c, after p5b, 3w

    section Phase 6: Sharing
    Authorized Views/Datasets    :p6a, after p5c, 3w
    Central Analytics Project    :p6b, after p6a, 3w
```

---

## References

- [GCP Dataplex Documentation](https://cloud.google.com/dataplex/docs)
- [Dataplex Data Quality](https://cloud.google.com/dataplex/docs/auto-data-quality-overview)
- [Dataplex Data Profiling](https://cloud.google.com/dataplex/docs/auto-data-profiling-overview)
- [Dataplex Data Lineage](https://cloud.google.com/dataplex/docs/data-lineage)
- [BigQuery Authorized Views](https://cloud.google.com/bigquery/docs/authorized-views)
- [DLQ Strategy](./DLQ_STRATEGY.md)
- [Monitoring & Observability](../operations/MONITORING_OBSERVABILITY.md)
