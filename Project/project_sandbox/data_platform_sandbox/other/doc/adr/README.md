# Architecture Decision Records — Data Platform Sandbox

Foundation decisions for the enterprise data platform. One decision per file (Nygard format). ADRs are immutable once Accepted — to change one, write a new ADR that supersedes it.

| # | Title | Status | Date |
|---|---|---|---|
| [0001](0001-table-format-apache-iceberg.md) | Use Apache Iceberg as the canonical open table format | **Proposed** | 2026-06-03 |
| [0002](0002-catalog-iceberg-rest-spec.md) | Use the Iceberg REST Catalog spec (open) as the catalog interface | **Proposed** | 2026-06-03 |
| [0003](0003-storage-compute-separation-unified-engine.md) | Separate storage/compute; one unified open engine for batch + streaming | Accepted | 2026-06-03 |
| [0004](0004-contract-boundaries-and-openlineage.md) | Contract-enforced layer boundaries with classification + OpenLineage from day one | Accepted | 2026-06-03 |

## Deferred (not yet ADRs — decide when requirements sharpen)
- Cloud + specific managed services
- Vector store + embedding model (rebuildable from Gold, so disposable)
- Gold modeling flavor (Kimball star vs wide/OBT) — can coexist per mart
- Flink adoption for sub-second stateful streaming — targeted exception only
- Catalog/lineage *product* (DataHub vs OpenMetadata) — wire format (OpenLineage) standardized now, backend later
