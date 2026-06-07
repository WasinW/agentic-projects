# Insight Domain — Pending Work

## From Session Summary

| Item | Priority | Notes |
|------|----------|-------|
| customer-profile-pipeline deploy error log | Waiting | User said "deploy error, will send log" -- not yet received |
| `src/customer_profile/` cleanup in collector | Medium | Legacy code structure inside collector, not matching standard (`src/domain/`, `src/application/`) |
| `view_events_consents` terraform state | Low | Terraform wants to destroy but `deletion_protection=true`; needs `state rm` or re-add to `.tf` |
| Dataform IAM for last-purchases | Blocked | Dataform CI commented; waiting for IAM permissions |
| customer-svoc-interim DAG validation | Medium | Changed from Dataflow to BQ EXPORT DATA; needs prod validation |

## Alignment Items (from Knowledge Base)

These items represent areas where insight should align with the loyalty domain patterns:

| # | Item | Detail |
|---|------|--------|
| 1 | **BLMS REST Catalog** | Replace manual Iceberg writer (1000+ lines) with BLMS REST + managed.Write |
| 2 | **Frozen dataclasses** | Adopt BlmsCatalogConfig / ManagedIcebergWriteConfig config pattern |
| 3 | **managed.Write** | Use Beam cross-language IcebergIO instead of manual PyArrow writer |
| 4 | **RowTypeConstraint** | Adopt Iceberg schema pattern for JVM compatibility |
| 5 | **Partition pattern** | Adopt `etlLoadTime INT YYYYMMDDHH` / `ingestedTHDate INT YYYYMMDD` partition |
| 6 | **deploy.py alignment** | Adopt `register_table` pattern (preserves field IDs + partition spec) |
| 7 | **CI/CD standardization** | Kaniko multi-dest (STG+PROD), shared deploy scripts |
| 8 | **Infrastructure** | Per-pipeline Terraform modules (consistent with loyalty collector pattern) |

## Active Plan (Not Started)

Refactor `customer-profile-pipeline` from legacy structure to loyalty collector standard:
- Phase 1: Config system (YAML + Pydantic + PipelineConfig)
- Phase 2: Restructure directories (`src/customer_profile/` -> `src/domain/`, `src/application/`)
- Phase 3: Wire new config flow
- Phase 4: Docker & Tooling (Dockerfile.base, pyproject.toml, uv)
- Phase 5: Cleanup & Verify

Status: Plan exists but execution not started. The collector (`customer-profile-collector`) was refactored separately (builder.py mapping->pure function + CI separation).
