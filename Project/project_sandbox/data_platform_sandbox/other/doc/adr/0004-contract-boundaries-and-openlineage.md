# 0004. Contract-enforced layer boundaries with classification baked in, and OpenLineage from day one

- Status: Accepted
- Date: 2026-06-03
- Deciders: Wasin + data-architect
- Tags: governance, data-contract, lineage, pdpa, irreversible

## Context
The data is regulated (PDPA Thailand + BoT-style controls). Retrofitting data contracts and lineage onto an existing platform is expensive, and hand-maintained lineage is never trusted once it drifts. Silent schema drift discovered in a regulator's audit is the failure mode to design out. Therefore contracts, classification, and lineage must be foundational — emitted as a byproduct of execution, not a manual phase-2 artifact.

## Options considered
- **Contract-as-code, dual-enforced, classification in the contract, OpenLineage auto-emit (chosen)** — contracts are versioned YAML in the producer's repo, enforced in (a) producer CI (can't merge a breaking change) and (b) runtime at each layer boundary (reject/quarantine non-conforming data, never silently drop). Streaming ingress adds a schema registry. Each contract carries schema (column IDs/semver), semantics, SLA (freshness/completeness/quality), and PDPA classification + retention + masking per field. Lineage auto-emitted via OpenLineage from Spark/Flink/dbt/Airflow. Con: runtime enforcement adds latency and ops burden (quarantine handling, alerting).
- **Docs-only contracts / manual lineage** — cheap upfront, but drifts immediately and is untrustworthy in an audit. Rejected for regulated data.
- **Defer governance to phase 2** — rejected: retrofitting is expensive and the lineage is never believed once manual.

## Decision
Every layer boundary (Source→Landing/Bronze, Bronze→Silver, Silver→Gold, Gold→consumer) is governed by a contract-as-code. Contracts include PDPA classification, retention, and masking policy per field. Enforcement is dual (producer CI + runtime quarantine); streaming ingress is additionally guarded by a schema registry. OpenLineage auto-emission is enabled from day one. All artifacts use open formats (YAML + JSON Schema / Protobuf / OpenLineage facets) — no cloud-proprietary contract service.

## Consequences
- **Positive:** producer-commits/consumer-relies is enforced, not documented; classification baked into the contract is the hook that makes PDPA/BoT governance executable; classification propagates downstream (incl. into the GenAI embedding projection) and enables right-to-erasure tracing via lineage.
- **Cost / accepted:** runtime enforcement adds latency and operational burden — quarantine handling, alerting, deprecation-cycle management for breaking changes. Accepted as non-negotiable for regulated loyalty/banking-adjacent data.
- **Schema-evolution policy locked:** add-nullable = safe; add-required / rename / type-narrow = breaking → deprecation window. Reinforced by Iceberg's column-ID evolution ([[0001-table-format-apache-iceberg]]).
- **Deferred:** the catalog/lineage *product* (DataHub vs OpenMetadata) is deferred, but the OpenLineage *wire format* is standardized now.

## Related
- [[0001-table-format-apache-iceberg]] — column-ID schema evolution reinforces contract evolution rules.
- [[0002-catalog-iceberg-rest-spec]] — governance metadata rides alongside the open catalog.
- [[0003-storage-compute-separation-unified-engine]] — WAP publish gate is where streaming contracts are enforced at runtime.
