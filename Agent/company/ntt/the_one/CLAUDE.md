# NTT / The-1 — Project Instructions

When working in `~/Documents/Projects/Project/ntt/the_one/`, follow these.

## Context

- **Employer**: NTT DATA (consult)
- **Client**: Central The-1 Card (CRM + loyalty platform)
- **Role**: Senior Data Engineer (on-site)
- **Cloud**: GCP
- **Stack**: Apache Beam (Dataflow), BigQuery, BigLake/Iceberg, Bigtable, Pub/Sub, Cloud Composer, Dataform, Cloud Run, Terraform
- **Pattern**: Config-driven Beam framework (YAML + step registry) with domain split (loyalty, insight, sale, catalog, message, partner)

## Project conventions

- **Hexagonal architecture** in `insight/` domain — Wasin has reservations; document trade-offs when proposing changes.
- **No BigQuery writes** from Beam streaming pipelines without explicit approval — go via Iceberg/BigLake.
- **Dataform** owns semantic layer / mart logic; do not duplicate transforms in Beam.
- **CDC via Dataflow Iceberg writes** with atomic snapshots; cloudrun is NOT a substitute (see discussion docs).
- **PII handling**: hash + mask early in pipeline; never log raw PII.
- **PDPA + BoT compliance** must be considered for any new data flow (see [../../roles/business/](../../roles/business/) and [knowledge/compliance.md](knowledge/compliance.md) when written).

## Knowledge files

See [INDEX.md](INDEX.md) for the full list. Key entries:

- `knowledge/architecture.md` — system overview (write when ready)
- `knowledge/domains.md` — loyalty, insight, sale, etc.
- `knowledge/conventions.md` — coding + naming + folder rules
- `knowledge/compliance.md` — PDPA, BoT, audit requirements
- `memory/` — facts gathered across sessions

## Legacy

Old workspace + memory live under `~/Documents/ntt_project/the_one/` and `~/.claude/projects/-Users-wasin-Documents-ntt-project-*/`. Treat as read-only reference until explicitly migrated.

## When invoking subagents

Default subagents for The-1 work:
- `data-architect` for system design
- `de-engineer` for Beam / Dataflow / BigQuery work
- `gcp-expert` for GCP-specific questions
- `ml-engineer` if touching ML pipelines (Vertex AI)

For multi-step work, see [../../../pipelines/INDEX.md](../../../pipelines/INDEX.md).
