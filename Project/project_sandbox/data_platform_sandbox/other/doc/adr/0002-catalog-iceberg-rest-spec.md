# 0002. Use the Iceberg REST Catalog spec (open) as the catalog interface

- Status: Proposed
- Date: 2026-06-03
- Deciders: Wasin + data-architect
- Note (2026-06-04): Reverted Accepted → Proposed. Depends on the format decision in [[0001-table-format-apache-iceberg]], which is itself un-confirmed. If Delta/Unity Catalog is chosen, the catalog interface decision changes. Re-decide together with 0001.
- Tags: catalog, metadata, cloud-portability, irreversible

## Context
The table format being open ([[0001-table-format-apache-iceberg]]) does not by itself guarantee portability — the catalog (which tracks table metadata, pointers, and governs commits) is where cloud lock-in actually hides. A proprietary catalog (Glue-only, Unity-only) quietly re-couples the platform to one cloud even when the data format is open. Cloud is deliberately undecided, so the catalog interface must not pre-commit us.

## Options considered
- **Iceberg REST Catalog spec — open interface (chosen)** — a standard wire protocol clients talk to; the backing implementation can change (different vendors/self-hosted) without changing any client. Keeps every major cloud's door open. Con: must run/operate a REST catalog service (or use a managed one that implements the open spec).
- **AWS Glue Data Catalog (proprietary)** — convenient on AWS, but couples metadata to AWS; moving clouds means a catalog migration and client rewiring.
- **Databricks Unity Catalog (proprietary)** — strong governance features, but ties the catalog plane to Databricks — the exact vendor decision being deferred.

## Decision
All Iceberg clients interact through the **Iceberg REST Catalog spec** as the catalog interface. The concrete catalog backend is chosen later and may be swapped, as long as it implements the open REST spec. No client may depend on a cloud-proprietary catalog API directly.

## Consequences
- **Positive:** the catalog backend becomes a swappable implementation detail; changing cloud is a migration of one service, not a rewrite of every pipeline. This is what makes [[0001-table-format-apache-iceberg]]'s portability real rather than nominal.
- **Cost / accepted:** we take on running (or sourcing a managed) REST-spec-compliant catalog, rather than defaulting to the cloud's built-in one. Slightly more operational surface now in exchange for not re-coupling later.
- **Deferred:** the catalog *product* (DataHub vs OpenMetadata vs Unity vs a managed REST catalog) is deferred — only the *interface* is locked now.

## Related
- [[0001-table-format-apache-iceberg]] — the format this catalog governs.
- [[0004-contract-boundaries-and-openlineage]] — governance/lineage metadata that rides alongside the catalog.
