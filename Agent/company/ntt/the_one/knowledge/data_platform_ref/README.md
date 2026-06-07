# The1 Data Platform Documentation

> **Last Updated:** 2026-02-20

Master index for all data platform documentation across loyalty, sales, insight, partner, and common projects.

---

## Architecture

| Document | Description |
|----------|-------------|
| [High-Level Architecture](architecture/HIGH_LEVEL_ARCHITECTURE.md) | Platform overview, GCP project structure, data mesh topology |
| [Data Pipeline Architecture](architecture/DATA_PIPELINE_ARCHITECTURE.md) | Pipeline types (streaming, batch, Cloud Run), data flow patterns |

## Development

| Document | Description |
|----------|-------------|
| [Development Guide](development/DEVELOPMENT_GUIDE.md) | Hexagonal architecture, configuration system, testing, Docker, common patterns |

## CI/CD

| Document | Description |
|----------|-------------|
| [CI/CD Pipeline](cicd/CICD_PIPELINE.md) | GitLab CI stages, shared extends, deployment flow, environment management |

## Operations

| Document | Description |
|----------|-------------|
| [Data Operations](operations/DATA_OPERATIONS.md) | Initial setup, day-to-day operations, troubleshooting runbooks |
| [Monitoring & Observability](operations/MONITORING_OBSERVABILITY.md) | Central observability vision, alerting, dashboards, cost monitoring, lineage |

## Governance

| Document | Description |
|----------|-------------|
| [Data Governance](governance/DATA_GOVERNANCE.md) | Dataplex governance: profiling, quality (7 dimensions), lineage, validation, sharing |
| [DLQ Strategy](governance/DLQ_STRATEGY.md) | Dead Letter Queue: TaggedOutput pattern, BQ storage, replay strategies |

## Discussion

| Document | Description |
|----------|-------------|
| [CI/CD Pipeline vs Dataform](discussion/CICD_PIPELINE_VS_DATAFORM.md) | Comprehensive comparison: CI/CD-triggered SQL vs Dataform for transformation layer |

## Reference

| Document | Description |
|----------|-------------|
| [Project Inventory](reference/PROJECT_INVENTORY.md) | Complete resource inventory: projects, services, buckets, IAM, schedulers, network |

## Per-Project Documentation

| Project | Document | Description |
|---------|----------|-------------|
| Loyalty Data | [loyalty-data/README.md](in_project/loyalty-data/README.md) | 6 collectors, Option B migration, Iceberg/BQ write paths, CI/CD |
| Sales Data | [sales-data/README.md](in_project/sales-data/README.md) | sales-collector (streaming), 3 BQ tables, per-table config |
| Insight | [insight/README.md](in_project/insight/README.md) | Combined project: Pipeline + APIs (Kotlin) + Collector (Node.js) |
| Common Data | [common-data/README.md](in_project/common-data/README.md) | Shared library monorepo: Beam adapters (common-python) + Cloud Run utilities (common-python-cloudrun) |
| Partner Data | [partner-data/README.md](in_project/partner-data/README.md) | companies-collector + master-collector (Cloud Run, Parquet, Iceberg) |

## Sales-Specific Documentation

Located at [`sale/doc/`](../../sale/doc/):

| Document | Description |
|----------|-------------|
| [Sales Pipeline Architecture](../../sale/doc/architecture/SALES_PIPELINE_ARCHITECTURE.md) | Detailed pipeline architecture, domain models, fan-out pattern |
| [Sales CI/CD](../../sale/doc/cicd/SALES_CICD.md) | Sales-specific CI/CD jobs, deployment flow, Terraform resources |
| [Sales Operations](../../sale/doc/operations/SALES_OPERATIONS.md) | Sales-specific operations runbook, troubleshooting, CDC enablement |

---

## Document Map

```
doc/data_platform/
├── README.md                              ← You are here
├── architecture/
│   ├── HIGH_LEVEL_ARCHITECTURE.md
│   └── DATA_PIPELINE_ARCHITECTURE.md
├── development/
│   └── DEVELOPMENT_GUIDE.md
├── cicd/
│   └── CICD_PIPELINE.md
├── operations/
│   ├── DATA_OPERATIONS.md
│   └── MONITORING_OBSERVABILITY.md
├── governance/
│   ├── DATA_GOVERNANCE.md
│   └── DLQ_STRATEGY.md
├── discussion/
│   └── CICD_PIPELINE_VS_DATAFORM.md
├── reference/
│   └── PROJECT_INVENTORY.md
└── in_project/
    ├── loyalty-data/README.md
    ├── sales-data/README.md
    ├── insight/README.md
    ├── common-data/README.md
    └── partner-data/README.md

sale/doc/
├── architecture/
│   └── SALES_PIPELINE_ARCHITECTURE.md
├── cicd/
│   └── SALES_CICD.md
├── operations/
│   └── SALES_OPERATIONS.md
└── claude_ai/
    ├── SALES_PIPELINE_KNOWLEDGE_BASE.md
    └── IMPLEMENTATION_CHECKLIST.md
```
