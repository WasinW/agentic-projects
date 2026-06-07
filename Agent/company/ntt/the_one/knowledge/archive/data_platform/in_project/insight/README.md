# Insight Project

> **GCP Project:** `the1-insight-{env}` (env: stg, prod)
> **Repository:** `gitlab.com/The1central/The1/the1-insight/insight-api`
> **Team:** Insight Squad
> **Region:** asia-southeast1
> **Last Updated:** 2026-02-20
> **Status:** Active (Production)

---

## Table of Contents

1. [Overview](#1-overview)
2. [Project Structure](#2-project-structure)
3. [Customer Profile Pipeline](#3-customer-profile-pipeline)
4. [Personas API](#4-personas-api)
5. [Audiences API](#5-audiences-api)
6. [Collector](#6-collector)
7. [Triggers](#7-triggers)
8. [Infrastructure](#8-infrastructure)
9. [Technology Stack](#9-technology-stack)
10. [CI/CD](#10-cicd)
11. [Architecture Patterns](#11-architecture-patterns)

---

## 1. Overview

Insight is a **combined project** that includes both data pipeline and application services within the same GCP project. Unlike loyalty-data and sales-data (which are pure data platforms), the Insight project encompasses:

- **Data Pipeline:** Customer Profile Pipeline (Apache Beam / Dataflow)
- **APIs:** Personas API, Audiences API (Kotlin / Spring Boot)
- **Event Collection:** Collector service (Node.js / TypeScript)
- **Batch Processing:** Triggers service (Node.js / TypeScript)

The project serves as the customer intelligence platform, processing real-time customer events and profile data, then exposing them through APIs for downstream consumers.

### High-Level Architecture

```
                    +------------------+
                    | External Sources |
                    | (Pub/Sub, S3,    |
                    |  Bigtable, etc.) |
                    +--------+---------+
                             |
              +--------------+--------------+
              |                             |
   +----------v----------+    +-------------v-----------+
   | Customer Profile     |    | Collector (Node.js)     |
   | Pipeline (Python)    |    | HTTP event ingestion    |
   | - Streaming Dataflow |    +-------------+-----------+
   | - Pub/Sub source     |                  |
   | - Bigtable lookup    |                  v
   +----------+-----------+    +-------------+-----------+
              |                | Triggers (Node.js)      |
              v                | Scheduled batch jobs     |
   +----------+-----------+    +-------------+-----------+
   | BigQuery CDC         |                  |
   | S3 Parquet           |                  v
   | Iceberg Merge        |    +-------------+-----------+
   +-----------+----------+    | Personas API (Kotlin)   |
               |               | - Bigtable + BigQuery   |
               v               +-------------+-----------+
   +-----------+----------+                  |
   | Audiences API        |                  v
   | (Kotlin)             |    +-------------+-----------+
   | - BigQuery +         |    | Personas Resolver       |
   |   ClickHouse         |    | (Kotlin)                |
   +-----------------------+    +-------------------------+
```

---

## 2. Project Structure

### Repository Layout

```
insight-api/
+-- audiences/                    # Audiences API (Kotlin/Spring Boot)
|   +-- build.gradle.kts
|   +-- src/
|   +-- helm/
|   +-- Dockerfile
+-- collector/                    # Event Collector (Node.js/TypeScript)
|   +-- package.json
|   +-- src/
|   +-- Dockerfile
+-- personas/                     # Personas services
|   +-- api/                      # Personas API (Kotlin/Spring Boot)
|   |   +-- build.gradle.kts
|   |   +-- src/
|   |   +-- helm/
|   |   +-- Dockerfile
|   +-- resolver/                 # Personas Resolver (Kotlin/Spring Boot)
|   |   +-- build.gradle.kts
|   |   +-- src/
|   |   +-- Dockerfile
|   +-- qualification/            # Personas Qualification
+-- triggers/                     # Trigger service (Node.js/TypeScript)
|   +-- package.json
|   +-- src/
|   +-- Dockerfile
+-- infrastructure/               # Terraform per-service
|   +-- common/GCP/               # Shared infrastructure
|   +-- common/AWS/               # Cross-cloud resources
|   +-- collector/
|   +-- data-pipeline/
|   +-- messaging-collector/
|   +-- personas/
|   +-- triggers/
+-- contracts/                    # Shared API contracts
+-- libs/                         # Shared libraries
+-- data/                         # Data files
+-- pipeline/                     # Legacy pipeline code
+-- docs/                         # Documentation

customer-profile-pipeline/        # Separate directory (outside insight-api)
+-- src/
+-- dags/
+-- pyproject.toml
+-- Dockerfile
+-- flex-template-spec.json
```

---

## 3. Customer Profile Pipeline

### Overview

| Property | Value |
|----------|-------|
| Version | V3.2.0 |
| Language | Python 3.11 (>=3.11, <3.13) |
| Framework | Apache Beam 2.69.0 |
| Deployment | Dataflow Flex Template |
| Type | Streaming (real-time) |
| Pattern | Hexagonal Architecture + V2 DoFn Pattern |

### Data Sources

- **Pub/Sub** -- Customer profile change events (`ms-personas` topic)
- **Bigtable** -- Profile data lookup + consent data

### Data Sinks

| Sink | Technology | Description |
|------|-----------|-------------|
| BigQuery CDC | Storage Write API (UPSERT) | `ms_personas` table |
| S3 Parquet | Windowed Parquet files | Cross-cloud export to AWS |
| Iceberg Merge | BigLake Iceberg | Historical table merge |

### Architecture Layers

```
config/       --> logging.py, options.py, settings.py
domain/       --> constants.py, models.py, transformers.py, schemas.py
ports/        --> input_ports.py, output_ports.py
adapters/     --> secret_manager.py, bigquery_mapping.py, bigtable_reader.py,
                  bigquery_cdc.py, s3_parquet.py, iceberg_sync.py
pipeline/     --> dofns.py, builder.py
main.py       --> Entry point
```

### Key Features

- **Consent Processing** -- SQL-based consent data loading + S3 export
- **SQL Source Switch** -- Toggle between GCS and embedded resources for SQL files
- **Rate-Limited Logging** -- Prevents log flooding in high-throughput streaming
- **DLQ** -- Dead Letter Queue to BigQuery for failed records

### Dependencies

```toml
dependencies = [
    "apache-beam[gcp]==2.69.0",
    "google-cloud-bigquery>=3.25.0",
    "google-cloud-bigtable>=2.26.0",
    "google-cloud-secret-manager>=2.20.0",
    "pyarrow>=14.0.0,<18.0.0",
    "pandas>=1.5.0,<2.1.0",
    "fastavro>=1.9.0",
    "boto3>=1.34.0",          # AWS S3 support
    "s3fs>=2024.6.1",
    "fsspec>=2024.6.1",
    "pyyaml>=6.0.1",
    "requests>=2.31.0",
]
```

---

## 4. Personas API

### Overview

| Property | Value |
|----------|-------|
| Language | Kotlin (JDK 21) |
| Framework | Spring Boot 3.5.x |
| Build | Gradle (Kotlin DSL) |
| Deployment | Cloud Run / GKE (Helm) |
| Linting | Detekt + ktlint |
| Test Coverage | JaCoCo |

### Sub-services

- **Personas API** (`personas/api/`) -- Main REST API for customer persona data
- **Personas Resolver** (`personas/resolver/`) -- Identity resolution service

### Data Sources

| Source | Technology | Purpose |
|--------|-----------|---------|
| Bigtable | Cloud Bigtable | Profile + persona data storage |
| BigQuery | BigQuery | Analytics queries |

### Key Dependencies

```kotlin
extra["springCloudVersion"] = "2025.0.0"
extra["springSecurityVersion"] = "6.5.4"
extra["awsSdkVersion"] = "2.31.54"
extra["bigQueryVersion"] = "2.43.0"
extra["bigTableVersion"] = "2.52.0"
extra["springCloudAwsVersion"] = "3.4.0"
extra["testContainersVersion"] = "1.20.4"
```

### Features

- Spring Security integration
- AWS SDK integration (cross-cloud)
- BigQuery + Bigtable data access
- Redis caching (via Spring Cloud AWS)
- TestContainers for integration testing
- Helm charts for Kubernetes deployments
- Message transform UDF (`message-transform-udf/`)

---

## 5. Audiences API

### Overview

| Property | Value |
|----------|-------|
| Language | Kotlin (JDK 21) |
| Framework | Spring Boot 3.5.x |
| Build | Gradle (Kotlin DSL) |
| Deployment | Cloud Run / GKE (Helm) |
| Linting | Detekt + ktlint |

### Data Sources

| Source | Purpose |
|--------|---------|
| BigQuery | Audience segment queries |
| ClickHouse | High-performance analytics |

### Features

- Spring Security integration
- kotlinx.serialization for JSON
- Helm charts for Kubernetes deployments
- SonarQube integration
- JaCoCo coverage
- SQL scripts for schema management

### Infrastructure

Separate infrastructure for Audiences API includes:
- `personas/api/` -- BigQuery, Bigtable, Dataflow, Pub/Sub
- `personas/clickhouse/` -- ClickHouse infrastructure

---

## 6. Collector

### Overview

| Property | Value |
|----------|-------|
| Name | insight-collector |
| Language | Node.js (TypeScript) |
| Type | Event collection API |
| Deployment | Cloud Run |
| Description | Collect customer insight data from offline and online sources |

### Key Technologies

- TypeScript (ES modules)
- ESLint for linting
- Mocha + Cucumber.js for testing (unit + integration)
- c8 for coverage
- Biome for formatting
- Prism for API mocking

### Scripts

```json
"build": "rm -rf dist && npm run build:packages && tsc && tsc-alias && ...",
"test": "npm run build && npm run test:unit && npm run test:integration",
"test:unit": "NODE_ENV=test TZ=UTC mocha --config mocha.config.cjs",
"test:integration": "NODE_ENV=test TZ=UTC cucumber-js --config src/tests/cucumber.yaml"
```

### Configuration

- YAML-based configuration (`src/config/**/*.yaml`)
- Mapper configuration (`src/config/mapper/*`)
- Environment-specific: dev, stg, prod

### Infrastructure

Separate Terraform at `infrastructure/messaging-collector/`:
- Collector storage bucket
- Cloud Run services (collector, proxy, adaptor)
- Cloud Functions (proxy function)

---

## 7. Triggers

### Overview

| Property | Value |
|----------|-------|
| Name | triggers |
| Language | Node.js (TypeScript) |
| Type | Batch/scheduled jobs |
| Deployment | Cloud Run + Scheduler |
| Author | Insight Squad |

### Key Technologies

- TypeScript (ES modules)
- tsx for development/testing
- Biome for linting/formatting
- Node.js built-in test runner
- convict for configuration
- Prism for API mocking

### Configuration

- `src/config/` -- Service-specific configurations
- Environment files (`.env`, `.env.test`)

### Scripts

```json
"dev": "tsx watch --env-file=.env --include './src/*' src/index.ts",
"test": "tsx --env-file=.env.test --test 'src/**/*.test.{cts,mts,ts}'",
"lint": "biome check",
"lint:fix": "biome check --write"
```

### Sub-modules

```
src/
+-- index.ts               # Entry point
+-- common/                 # Shared utilities
+-- config/                 # Configuration
+-- services/               # Business logic
+-- tests/                  # Test files
+-- utils/                  # Utility functions
```

---

## 8. Infrastructure

### Common GCP Infrastructure (`infrastructure/common/GCP/`)

| Resource | File | Description |
|----------|------|-------------|
| VPC Network | `vpc-network.tf` | Dataflow VPC (192.168.1.0/24 private subnet) |
| API Services | `api-services.tf` | GCP API enablement |
| Artifact Registry | `artifact-registry.tf` | Docker repos |
| BigQuery | `bigquery.tf` | Datasets |
| BQ Table IAM | `bigquery-table-iam.tf` | Table-level access control |
| Bigtable Instance | `bigtable-instance.tf` | Bigtable cluster |
| Bigtable IAM | `bigtable-instance-iam.tf` | Instance-level access |
| Bigtable Tables | `bigtable-table.tf` | Table definitions |
| GCS Buckets | `gcs-bucket.tf` | Storage buckets |
| Secret Manager | `secret-manager.tf` | Application secrets |
| Cloud Armor | `cloud-armor-policy.tf` | WAF policies |
| Cloud Functions | `cloucfunctions.tf` | Serverless functions |
| Internal LB | `internal-loadbalancer.tf` | Internal load balancing |
| Audit Logging | `audit-log-*.tf` | Audit log config, metrics, alerting, sinks |

### Data Pipeline Infrastructure (`infrastructure/data-pipeline/`)

| Resource | File | Description |
|----------|------|-------------|
| Artifact Registry | `artifact.tf` | Pipeline image repos |
| BigQuery | `bigquery.tf` | Pipeline datasets |
| GCS Buckets | `buckets.tf` | Pipeline storage |
| Cloud Composer | `composer.tf` | Airflow orchestration |
| Dataplex | `dataplex.tf` | Data governance |
| DTS | `dts.tf` | Data Transfer Service |
| Pub/Sub | `pub-sub.tf` | Messaging topics |
| Schemas | `schemas/` | Schema definitions |

### Personas Infrastructure (`infrastructure/personas/`)

| Component | Resources |
|-----------|-----------|
| API | BigQuery, Bigtable, Dataflow, Pub/Sub |
| ClickHouse | ClickHouse cluster infrastructure |
| Qualification | Qualification service infrastructure |
| Resolver | Resolver service infrastructure |

### Common AWS Infrastructure (`infrastructure/common/AWS/`)

Cross-cloud resources for AWS integration:
- ECR (container registry)
- EKS (Kubernetes)
- Route53 (DNS)
- Secret Manager
- IAM roles

---

## 9. Technology Stack

### Multi-Language Stack

| Service | Language | Runtime | Build Tool |
|---------|----------|---------|------------|
| Customer Profile Pipeline | Python 3.11 | Dataflow | uv / pip |
| Personas API | Kotlin (JDK 21) | JVM | Gradle (Kotlin DSL) |
| Personas Resolver | Kotlin (JDK 21) | JVM | Gradle (Kotlin DSL) |
| Audiences API | Kotlin (JDK 21) | JVM | Gradle (Kotlin DSL) |
| Collector | TypeScript | Node.js | npm |
| Triggers | TypeScript | Node.js | npm |

### Data Technologies

| Technology | Service | Purpose |
|-----------|---------|---------|
| Apache Beam | Customer Profile Pipeline | Streaming data processing |
| Google Dataflow | Customer Profile Pipeline | Beam runner |
| Cloud Bigtable | Pipeline, Personas API | Low-latency key-value storage |
| BigQuery | Pipeline, Personas, Audiences | Analytics + CDC storage |
| ClickHouse | Audiences API | High-performance analytics |
| Apache Iceberg | Pipeline | Historical data (BigLake) |
| AWS S3 | Pipeline | Cross-cloud Parquet export |
| Pub/Sub | Pipeline | Event messaging |
| Cloud Composer | Pipeline | Workflow orchestration (Airflow) |
| Redis | Personas API | Caching layer |

### Testing Frameworks

| Service | Unit Tests | Integration Tests | Coverage |
|---------|-----------|------------------|----------|
| Python Pipeline | pytest | pytest | pytest-cov |
| Kotlin APIs | JUnit 5 + MockK | TestContainers | JaCoCo |
| Node.js Collector | Mocha | Cucumber.js | c8 |
| Node.js Triggers | Node.js test runner | - | Built-in coverage |

### Code Quality Tools

| Service | Linting | Formatting | Static Analysis |
|---------|---------|-----------|----------------|
| Python Pipeline | ruff | ruff format | mypy |
| Kotlin APIs | ktlint | ktlint | Detekt |
| Node.js Collector | ESLint | Prettier | TypeScript |
| Node.js Triggers | Biome | Biome | TypeScript |

---

## 10. CI/CD

### Deployment Strategies

| Service | Deployment Target | Method |
|---------|------------------|--------|
| Customer Profile Pipeline | Dataflow | Flex Template launch |
| Personas API | GKE / Cloud Run | Helm charts |
| Personas Resolver | GKE / Cloud Run | Helm charts |
| Audiences API | GKE / Cloud Run | Helm charts |
| Collector | Cloud Run | Docker deploy |
| Triggers | Cloud Run | Docker deploy |

### Pipeline Triggering

Both Personas API and Audiences API have `triggerPipeline/` directories that enable CI/CD pipeline triggering from their respective services.

### Docker Builds

- **Python services:** Multi-stage with uv (builder) + Dataflow base (runtime)
- **Kotlin services:** Multi-stage with Gradle build + JDK runtime
- **Node.js services:** Multi-stage with npm build + Node.js runtime

### Helm Charts

Kotlin services (Personas API, Audiences API) use Helm charts for Kubernetes deployment:
- Located in `{service}/helm/`
- Support for environment-specific values
- Rolling deployment strategy

---

## 11. Architecture Patterns

### Hexagonal Architecture

All services follow the hexagonal (ports and adapters) pattern:

- **Domain Layer** -- Pure business logic, no external dependencies
- **Ports Layer** -- Interfaces defining input/output contracts
- **Adapters Layer** -- Implementations for external systems
- **Pipeline/Application Layer** -- Orchestration and wiring

### Shared Patterns Across Services

1. **Environment Configuration** -- All services support dev/stg/prod via config files or env vars
2. **Health Checks** -- All Cloud Run services expose `/health` endpoints
3. **Secret Management** -- GCP Secret Manager for credentials
4. **Logging** -- Structured logging with rate limiting (pipeline)
5. **Testing** -- Unit + integration tests with coverage reporting
6. **SonarQube** -- Code quality analysis across all services

### Cross-Cloud Architecture

The Insight project is unique in its cross-cloud nature:
- **GCP** -- Primary cloud (Dataflow, BigQuery, Bigtable, Cloud Run)
- **AWS** -- Secondary cloud (S3 for exports, RDS for historical data, EKS for some workloads)
- **Cross-cloud sync** -- Pipeline exports Parquet to S3, boto3/s3fs used for AWS access
