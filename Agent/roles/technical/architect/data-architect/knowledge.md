# Data Architect — Comprehensive Knowledge

> Deep reference for the data-architect subagent.
> Generic + standard-industry — not project-biased.
>
> *Examples are illustrative and domain-neutral. The-1 / loyalty / Central should appear only as one optional example when a question is explicitly in that domain — never as the default lens.*

---

## 1. Foundations

### What a Data Architect does

Designs the **structure** of how data is stored, modeled, integrated, governed, and consumed across an organization.
- Not a data engineer (that's implementation).
- Not a DBA (that's operations).
- Not an enterprise architect (that's portfolio-level).
- The data architect is the **subject matter expert** for the data layer's blueprint.

### Core responsibilities

- **Data models** — logical / physical / canonical
- **Storage strategy** — warehouse / lakehouse / mesh / fabric decisions
- **Integration patterns** — ETL / ELT / streaming / CDC
- **Schema evolution** — how data changes over time without breaking consumers
- **Lineage + catalog** — where data comes from, who uses it
- **Data contracts** — formal interfaces between producers and consumers
- **Governance hooks** — classification, retention, access patterns
- **Trade-off communication** — explain to non-technical stakeholders

### Adjacent roles + handoffs

| Role | Handoff |
|---|---|
| Solution Architect | Data architect designs the data shape; solution architect picks components around it |
| Enterprise Architect | Data architect implements EA's data principles at the platform level |
| Data Engineer | Data architect designs; DE implements pipelines |
| DBA | Architect designs schema; DBA tunes + operates |
| Governance / Privacy | Architect designs lineage hooks; governance enforces policy |
| Domain Expert | Domain provides meaning; architect translates to structure |

---

## 2. Mental Models / Decision Frameworks

### The 4 layers (every data system has these)

```
┌─────────────────────────────────────────┐
│ STORAGE      — where data sits          │
│ COMPUTE      — what transforms it       │
│ ORCHESTRATION — how + when it runs      │
│ GOVERNANCE   — who can do what          │
└─────────────────────────────────────────┘
```

Storage ↔ Compute separation is the **single most important architectural principle** of the cloud era. Anything that couples them tightly (legacy MPP DW) trades flexibility for performance.

### Warehouse vs Lake vs Lakehouse vs Mesh vs Fabric — when to use which

| Pattern | Use when | Avoid when |
|---|---|---|
| **Warehouse** (Snowflake, BQ, Redshift) | Mostly structured, BI-focused, single-team | Unstructured data, ML workloads, multi-domain governance |
| **Data Lake** | Cheap storage of raw, large volume, varied formats | Need ACID, point-in-time correctness, transactional reads |
| **Lakehouse** (Delta / Iceberg / Hudi + Spark/Trino/Databricks) | Both BI + ML, want open format, cost-conscious | Don't want operational complexity of pipelining |
| **Data Mesh** | 30+ data engineers across domains, central team is bottleneck | Smaller orgs, no domain ownership maturity |
| **Data Fabric** | Many existing sources, can't centralize, AI-driven discovery | Greenfield projects (overkill) |

> Table-format choice (Delta vs Iceberg vs Hudi) is a separate, conditional decision — see `roles/technical/consultant/databricks-expert/knowledge.md` and the `delta_vs_iceberg_vs_hudi.md` guide. Default to the format your primary compute engine treats as native (Delta on Databricks, Iceberg on Snowflake/Trino/Flink) rather than a fixed default.

ปี 2026 reality: most enterprises blend — Lakehouse storage + Mesh ownership + Fabric metadata.

### 3 Modeling Paradigms

| Paradigm | Strength | Weakness |
|---|---|---|
| **Dimensional / Kimball (star schema)** | BI-friendly, analyst-readable | Costly to evolve, snapshots are awkward |
| **Data Vault (hub-link-satellite)** | History-friendly, auditable, integration-friendly | Complex queries, needs strong tooling |
| **Wide (denormalized / OBT)** | Cheap on columnar storage, fast queries | Update anomalies, hard to share |
| **Activity Schema (event-centric)** | Recent (Narrator.ai) — modular, additive | Smaller ecosystem |

Most modern lakehouses converge on: **Bronze (raw) → Silver (cleaned, normalized) → Gold (dimensional or wide for BI)**.

### Decision: ETL vs ELT vs Streaming

```
Latency required?
  Sub-second  → Streaming (Kafka + Flink/Beam + materialize)
  Minutes     → Micro-batch (Spark Structured Streaming)
  Hours-T+1   → Batch ELT (Airflow + dbt)
  Hybrid      → Tiered: hot ⊂ warm ⊂ cold (most common)
```

### Decision: One copy or many?

The classic trap: data team copies data 10 times for 10 use cases → 10 sources of truth.

Default: **single canonical storage** in an open table format (Delta, Iceberg, or Hudi — chosen per engine fit) with multiple compute engines reading it. Only copy when:
- Cross-region latency makes single-copy infeasible
- Compliance forces region-locked copies
- Use case truly needs a different representation (e.g., vector embeddings)

### Storage Type Selector

| Data shape | Engine |
|---|---|
| Wide tabular, structured | Columnar (Parquet, ORC) in lakehouse |
| Document / nested | JSON / Avro in lakehouse, or document DB |
| Time series | Specialized TSDB (InfluxDB, TimescaleDB) or partitioned columnar |
| Graph | Graph DB (Neo4j, Neptune) or columnar with edge tables |
| Vector (embeddings) | Vector DB (Pinecone, Qdrant, pgvector, BigQuery Vector) |
| Key-value lookup | KV store (Redis, DynamoDB, Bigtable) |
| Append-only events | Log (Kafka) + landing in lakehouse |

---

## 3. Standard Practices (industry common)

### Always

- Separate storage from compute
- Pick an open table format (Delta / Iceberg / Hudi) — the right one depends on your primary compute engine, catalog, and upsert pattern; see `delta_vs_iceberg_vs_hudi.md`. Avoid a proprietary primary format unless there's a strong vendor reason.
- Use hidden partitioning when format supports (Iceberg)
- Cluster on high-cardinality access keys (BQ clustering, Delta Z-order / liquid clustering, Iceberg sort order)
- Version everything — schema, transformations, data (snapshots)
- Maintain explicit lineage — column-level if possible
- Document with examples — not just "what" but "why" and "when"

### Schema Evolution Rules

- Adding nullable columns → safe
- Adding required columns → breaking (unless you backfill)
- Renaming → breaking (always); use deprecation cycle
- Type widening (int → bigint, float → double) → safe
- Type narrowing → breaking
- Use **column IDs** instead of names internally (Iceberg natively; Delta via column mapping)

### Data Contracts (the modern way)

A contract = formal agreement between producer + consumer about:
- Schema (fields, types, nullability)
- Semantics (what fields mean)
- SLA (freshness, completeness, quality thresholds)
- Versioning + evolution policy
- Owner + escalation

Modern enforcement: contract-as-code (YAML), enforced in CI of the producer service. Tools: dbt contracts, Data Contract CLI, Confluent Schema Registry, Buf for Protobuf.

### Lineage Standards

- **OpenLineage** — open standard for lineage events; integrates with dbt, Airflow, Spark, Flink, Beam.
- **DataHub / OpenMetadata / Marquez** — receive + visualize OpenLineage events.
- Column-level lineage is now table stakes for any regulated industry.

### Catalog Patterns

- **Technical catalog** — tables, schemas, owners (DataHub, Unity Catalog, Dataplex)
- **Business glossary** — terms with definitions (Atlan, Alation, OpenMetadata)
- **Active metadata** — reactive: usage-driven recommendations (Atlan's positioning)

### Partitioning + Clustering

- **Partition by access predicate** — usually date, sometimes tenant_id
- **Cluster by filter + join keys** — high-cardinality, used in WHERE/JOIN
- **Don't over-partition** — too many small files = metadata cost > scan savings
- **Use bucketing / clustering** for join collocation (Iceberg bucketing, Hive, Spark; Delta liquid clustering)

### Naming Conventions

- Layer prefix: `raw_`, `stg_`, `int_`, `fct_`, `dim_`, `mart_`
- Domain prefix: `sales.fct_orders`, `marketing.dim_campaigns` (e.g., in a loyalty context, `loyalty.fct_transactions`)
- Avoid abbreviations; favor self-documenting names

---

## 4. Tools Landscape (2026)

### Open Table Formats
| | Iceberg | Delta Lake | Hudi |
|---|---|---|---|
| Multi-engine support | ★★★★★ | ★★★ | ★★★ |
| Hidden partitioning | ★★★★★ | ★★ | ★★★ |
| Schema evolution | ★★★★★ | ★★★★ | ★★★★ |
| Time travel | ★★★★ | ★★★★ | ★★★★ |
| Merge-on-read | ★★★★ | ★★★ (improving) | ★★★★★ |
| Cloud-native catalog | REST Catalog | Unity Catalog | Hudi Catalog |
| Best fit when… | Multi-engine / Snowflake / Trino / Flink-centric; REST catalog | Databricks-centric; Unity Catalog; need Photon/liquid clustering | High-frequency streaming upserts at scale |

*There is no single 2026 default — Delta and Iceberg are peers, and the choice is driven by your primary compute engine and catalog. Ask: Which engine owns the writes? What catalog? Streaming-upsert heavy? See `databricks-expert/knowledge.md` and `delta_vs_iceberg_vs_hudi.md` before recommending.*

### Catalog / Lineage
- **DataHub** (open) — most powerful, ops-heavy
- **OpenMetadata** (open) — easier to deploy, growing fast
- **Unity Catalog** (open, Databricks origin) — best on Databricks stack
- **Atlan** (commercial) — enterprise UX, governance
- **Dataplex** (GCP) — cloud-native, less mature on lineage
- **AWS Lake Formation + Glue Catalog** — AWS-native

### Data Quality
- **dbt tests** — in-pipeline, simple
- **Soda** — data quality as code, growing
- **Great Expectations** — flexible, complex
- **Monte Carlo** (commercial) — observability + lineage

### Vendor Warehouses (when not lakehouse)
- **BigQuery** — strong for analytics + AI integration, BigLake for open format
- **Snowflake** — strong on multi-cloud, Iceberg support, performance
- **Databricks SQL** — best Spark integration, Photon engine
- **Redshift** — AWS-native, mature

### Modeling / Transform
- **dbt** — de facto standard for SQL transform
- **SQLMesh** — newer, semantic versioning
- **Dataform** — GCP-native, similar to dbt

---

## 5. Anti-Patterns

| Anti-pattern | Why it's bad | What to do instead |
|---|---|---|
| One giant denormalized table for all use cases | Wastes storage, joins still happen at query time, slow | Layered architecture (raw → cleaned → mart) |
| Copy data to a new system for every use case | Multiple sources of truth, sync nightmare | Single canonical + virtualization or federation |
| Hardcoded partition column duplicated alongside timestamp | Forgetting to filter both = full table scan | Hidden / generated partitioning (Iceberg `days(ts)`, Delta generated columns) |
| Schema in DDL only, no semantic doc | New consumers can't understand fields | Contracts + glossary |
| Lineage gathered manually from team interviews | Always stale, never trusted | OpenLineage auto-emission |
| "We'll add governance later" | It's never added; technical debt compounds | Governance hooks from day one (classification, owner) |
| Vendor-proprietary format for primary storage | Lock-in, expensive migration | Open table format (Delta / Iceberg / Hudi) |
| Same model for all consumers (BI + ML + API) | Each has different shape needs | Layer marts, expose curated views per consumer |
| Updating raw data | Breaks audit, no rollback | Always append; mutations in upper layers |

---

## 6. Advanced / Expert Topics

### Lakehouse internals

**Iceberg**
- Snapshot → manifest list → manifest files → data files
- Hidden partitioning via partition transforms (`years`, `months`, `days`, `bucket`, `truncate`)
- Schema evolution: column IDs, not names
- Time travel: query AS OF snapshot ID or timestamp
- Branching + tagging (Iceberg v3): WAP (write-audit-publish) pattern

**Delta**
- Transaction log: ordered JSON commits in `_delta_log/` + periodic Parquet checkpoints (snapshot of log state)
- Column mapping: ID/name-based mapping enables safe rename + drop without rewriting data
- Deletion vectors: merge-on-read deletes/updates without rewriting whole files
- Liquid clustering: adaptive clustering that replaces rigid partitioning + Z-order
- Time travel: query by version number or timestamp

For Delta-log internals (transaction log, deletion vectors, liquid clustering) see `databricks-expert/knowledge.md`; for a side-by-side see `delta_vs_iceberg_vs_hudi.md`.

### Stream-Table Duality

A table is a materialized view over a stream of changes. A stream is the history of mutations to a table.
- CDC (Change Data Capture) — Debezium converts table changes → events
- Materialized views — collapse streams back to tables
- Kappa architecture — stream is the source of truth

### Slowly Changing Dimensions (SCD)

| Type | Behavior | Use |
|---|---|---|
| SCD1 | Overwrite (no history) | When history doesn't matter |
| SCD2 | New row with valid_from/valid_to | Common — preserves history |
| SCD3 | Limited columns track previous values | Rare; specific use cases |
| SCD6 | Combination | When you need both type 1 + 2 |

dbt `snapshots` automates SCD2.

### Federation vs Centralization

- **Federation** — leave data where it is, query across via virtualization (Trino, Starburst, BigLake)
- **Centralization** — copy data into one place (warehouse / lake)
- Modern enterprises pick **federation for breadth, centralization for depth**

### Active vs Passive Metadata

- **Passive** — catalog is a viewer; humans read it
- **Active** — catalog drives behavior: alerts, auto-recommendations, auto-classification, governance enforcement
- The shift to active metadata is the 2026 trend (Atlan's term, but everyone's doing it)

### Multi-region / Multi-cloud strategy

- Data gravity: query close to data (not data close to compute)
- Replication: bidirectional sync is hard; favor unidirectional + read replicas
- Compliance: data residency requirements often dictate region choice

### Data Contracts at Scale

When contracts get widely adopted (50+ producers):
- Schema registry becomes critical infrastructure
- Breaking change governance is needed (deprecation periods, semver)
- Auto-generated documentation + downstream impact analysis
- Producer SLA monitoring (am I meeting my contract?)

### OpenLineage Instrumentation (how-to)

**What.** OpenLineage (LF AI & Data) is the open standard for *automatically emitting* lineage as pipelines run — you don't interview teams, the runtime tells you. The data model is three entities + facets: a **Job** (a process definition — an Airflow task, a dbt model, a Spark job), a **Run** (one execution instance, UUID-keyed), and **Datasets** (inputs/outputs). Everything else hangs off these as **facets** — modular, versioned JSON metadata blobs (schema, columnLineage, dataQualityMetrics, sql, dataSource, ownership). The wire format is the **RunEvent**: a producer emits `START` when a run begins, then `COMPLETE`/`FAIL`/`ABORT` (and optional `RUNNING`) at the end, each carrying `eventTime`, `producer`, `job`, `run`, and `inputs`/`outputs` arrays. Spec is JsonSchema + OpenAPI at openlineage.io.

**Why.** Manual lineage is always stale and never trusted (see anti-patterns). Auto-emission makes lineage a byproduct of execution, so it's correct by construction and survives refactors.

**Patterns + when.** Push-based is the norm — integrations ship events over a **transport** (HTTP, Kafka, file, console). Use **Kafka transport** when you have high event volume or want fan-out to multiple consumers; **HTTP** for direct-to-backend simplicity. Integrations: **Airflow** (native provider, operator-level interception), **dbt** (`dbt-ol` / native, captures `ref()`/`source()`), **Spark** (listener intercepts read/write plans, emits schema + columnLineage), **Flink** (agent for streaming, no code change). **Marquez** is the reference backend (collect/aggregate/visualize); DataHub and OpenMetadata also ingest OpenLineage natively. **Column-level lineage** uses the `columnLineage` dataset facet: per output column, an `inputFields` array of source columns, each with a `transformations` array classified **DIRECT** (`IDENTITY`/`TRANSFORMATION`/`AGGREGATION`) or **INDIRECT** (`JOIN`/`GROUP_BY`/`FILTER`/`WINDOW`), plus a `masking` flag — gold for impact analysis and PII propagation in regulated industries. Custom facets: namespace your own (`my_company_*`) for org-specific metadata; keep them additive.

**Anti-patterns.** Hand-rolling lineage parsers instead of using shipped integrations; emitting only `COMPLETE` (you lose run duration + failure lineage); proprietary lineage formats that lock you out of Marquez/DataHub.

**Tools (2025-2026):** OpenLineage 1.3x integrations, Marquez backend, DataHub/OpenMetadata ingestion. Reference: [openlineage.io column lineage facet](https://openlineage.io/docs/spec/facets/dataset-facets/column_lineage_facet/), [marquezproject.ai](https://marquezproject.ai/).

### Active Metadata Patterns (implementation)

**What.** Active metadata moves the catalog from a *read-only viewer* to a *system that acts*. Instead of metadata sitting passively for humans to browse, it is continuously collected from real-time signals (query logs, lineage events, usage, run state) and fed back into the tools where work happens. Gartner frames this as the **active metadata** market; the practical shift is event-driven + reverse flow.

**Why.** Passive catalogs decay — nobody curates them, trust erodes, governance lags reality. Active metadata keeps context fresh automatically and puts it *at the point of decision* (the IDE, the BI tool, the warehouse), which is the only place it changes behavior.

**Patterns + when.** (1) **Event-driven metadata** — metadata changes (new column, deprecated table, freshness breach) emit events that trigger downstream actions. DataHub's **Actions Framework** is the canonical example: subscribe to entity-change events on Kafka, run handlers (Slack alert, ticket, tag propagation). Use when you need automation, not just visibility. (2) **Reverse metadata** — push catalog context *back into source/consumer tools*: column descriptions and PII tags into the warehouse, ownership into Slack, certified-status badges into the BI tool. Use when adoption is the problem (people won't leave their tool to check a catalog). (3) **Usage-driven recommendations** — rank/recommend datasets by query frequency + downstream popularity, surface "most-used / certified" and deprecate cold tables. (4) **Metadata activation use cases** — auto-tag-propagation along lineage (a PII tag flows to every downstream column), data-quality-circuit-breakers, auto-deprecation, cost attribution.

**Anti-patterns.** Treating the catalog as a documentation graveyard ("we'll curate later" — it never happens); building active flows without lineage as the spine (propagation needs the graph); over-automating tag propagation without a human-in-loop for sensitive reclassification.

**Tools (2025-2026):** **Atlan** (active-metadata positioning, Gartner/Forrester leader, tag propagation + reverse into source systems), **DataHub** (Actions Framework, streaming/Kafka-first), **OpenMetadata** (unified model, enrichment-focused). Reference: [datahubproject.io](https://datahubproject.io/), [Atlan active metadata guide](https://atlan.com/active-metadata-101/).

---

## 7. References

### Books (foundational)
- **Designing Data-Intensive Applications** — Martin Kleppmann (must-read)
- **The Data Warehouse Toolkit** — Ralph Kimball (still useful for dimensional)
- **Building the Data Lakehouse** — Bill Inmon (lakehouse perspective)
- **Fundamentals of Data Engineering** — Joe Reis, Matt Housley (modern overview)
- **Data Mesh** — Zhamak Dehghani (mesh principles)

### Specifications
- **Apache Iceberg spec** — iceberg.apache.org/spec/
- **OpenLineage spec** — openlineage.io
- **Delta Lake protocol** — github.com/delta-io/delta
- **Data Contract spec** — datacontract.com
- **Delta vs Iceberg vs Hudi guide** — internal: `roles/technical/architect/data-architect/delta_vs_iceberg_vs_hudi.md`

### Vendor docs to know
- **Databricks Lakehouse architecture** — best comprehensive reference
- **BigLake / BigQuery Open Lakehouse** — Google's open lakehouse positioning
- **Snowflake Iceberg tables** — managed vs external
- **Confluent Kafka + Schema Registry** — streaming patterns

### Industry blogs
- **Modern Data 101** (Substack) — pragmatic
- **Towards Data Science** — broad
- **Maxime Beauchemin** (Airflow + Superset author) — functional data engineering
- **Joe Reis** (Substack) — data engineering practice

### Standards bodies / communities
- **OpenLineage community** (Linux Foundation)
- **Open Data Initiative** (Microsoft / Adobe / SAP)
- **DAMA International** — Data Management Body of Knowledge (DMBOK)

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| Solution Architect | "What components implement this data design?" |
| Enterprise Architect | "How does this fit org-wide data principles?" |
| Platform Architect | "How does this consume the platform's capabilities?" |
| AI Architect | "What's the shape of training + inference data?" |
| Data Engineer | "Here's the design — what's the implementation plan?" |
| Governance | "Where are the PII / sensitive data hooks?" |
| Domain Expert | "Help me name + define these entities correctly." |

When to escalate up: enterprise-level alignment, org-wide standards. Escalate down (or stay): implementation, code review.

---

*This file is a comprehensive reference. Read sections selectively based on the question at hand.*
