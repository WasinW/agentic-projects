# Context Map — The1 Data Platform Multi-Agent System

> Master index for `mem_clean_context/` — cleaned, categorized context for all domains.
> Generated: 2026-04-05 | Source: bak_mem exports + codebase deep scans

---

## Domain → Files

| Domain | Files | Source |
|--------|-------|--------|
| **loyalty/** | `knowledge_base.md`, `mistakes.md`, `pending_work.md`, `kafka_schema.md` | Cleaned from bak_mem/loyalty/ |
| **sales/** | `knowledge_base.md`, `mistakes.md`, `pending_work.md`, `schema_migration.md` | Cleaned from bak_mem/loyalty/ (sales files) + bak_mem/sales/ |
| **insight/** | `knowledge_base.md`, `pending_work.md` | Cleaned from bak_mem/insight/ |
| **catalog/** | `knowledge_base.md`, `pending_work.md` | Cleaned from bak_mem/catalog/ |
| **gamification/** | `knowledge_base.md`, `pending_work.md` | Deep scan from codebase |
| **message/** | `knowledge_base.md`, `pending_work.md` | Deep scan from codebase |
| **partner/** | `knowledge_base.md`, `pending_work.md` | Deep scan from codebase |
| **common/** | `knowledge_base.md`, `pending_work.md` | Deep scan from codebase |
| **loyalty-mart/** | `knowledge_base.md`, `pending_work.md` | Cleaned from bak_mem/loyalty-insights/ |
| **shared/** | `common_patterns.md`, `common_mistakes.md`, `common_infrastructure.md`, `cross_domain_deps.md`, `architecture_overview.md` | Synthesized cross-domain |

**Total: 27 files across 10 directories**

---

## Collector Inventory

### Streaming Pipelines (Dataflow + Kafka)

| Domain | Collector | Data Source | Kafka Topics | Sinks | Common Lib | Status |
|--------|-----------|-------------|-------------|-------|------------|--------|
| loyalty | members-collector | Kafka | loyalty.member.* | Iceberg + BQ refined (CDC) | dataflow 0.0.23 | PROD |
| loyalty | coupons-collector | Kafka | loyalty.coupon.* | Iceberg + BQ refined | dataflow 0.0.23 | STG testing |
| loyalty | backward-compatible-collector | Kafka | (various) | Iceberg + BQ refined | dataflow 0.0.23 | STG testing |
| loyalty | transactions-collector | Kafka | loyalty.transaction.* | Iceberg + BQ refined | dataflow (ext) | PROD `[EXTERNAL]` |
| sales | sales-collector | Kafka | loyalty.sales.created/updated | Iceberg + BQ refined (CDC) | dataflow 0.0.32 | PROD |
| gamification | account-missions-collector | Kafka | gamification.missions.* (5) | Iceberg (5 tables) + Bigtable + BQ | dataflow 0.0.24 | PROD |
| message | messages-collector | Kafka | messaging.messages.* (5) | Iceberg + BQ + PubSub + Bigtable | dataflow 0.0.24 | PROD |

### Batch Pipelines (Cloud Scheduler → Dataflow)

| Domain | Collector | Data Source | Schedule | Sinks | Status |
|--------|-----------|-------------|----------|-------|--------|
| loyalty | tiers-collector | REST API | 1AM BKK | Iceberg + BQ refined | PROD |
| loyalty | members-tiers-history-collector | **PostgreSQL** | 1AM BKK | Iceberg + BQ refined | PROD |

### Batch Pipelines (Cloud Scheduler → CloudRun)

| Domain | Collector | Data Source | Schedule | Sinks | Common Lib | Status |
|--------|-----------|-------------|----------|-------|------------|--------|
| gamification | master-collector | REST API | 1AM BKK | Iceberg (missions+ballots) | cloudrun 0.0.35 | PROD |
| message | master-collector | REST API | 1-2AM BKK | Iceberg (communications+templates) | cloudrun 0.0.35 | PROD |
| partner | master-collector | REST API | 1-2:30AM BKK | Iceberg (branches/companies/brands/subscriptions) | cloudrun 0.0.35 | PROD |
| loyalty | rewards-collector | REST API | (unknown) | Iceberg | cloudrun (unknown) | PROD `[CloudRun]` |

### DTS / Dataform / Other

| Domain | Pipeline | Type | Data Source | Sink | Status |
|--------|----------|------|-------------|------|--------|
| catalog | products-collector | DTS (S3→BQ) | S3 Parquet | BQ refined → Dataform public | STG active |
| insight | customer-svoc-interim | BQ EXPORT DATA | BQ (DTS S3→BQ) | GCS Parquet (Airflow) | PROD |
| insight | customer-profile-collector (V3) | PubSub→Bigtable→BQ | PubSub | BQ CDC + S3 + Iceberg | PROD |
| insight | last-purchases | BQ→BQ | BQ (sales refined) | BQ public | PROD |
| loyalty-mart | earn-analysis | Dataform only | BQ refined (loyalty) | BQ public views | Scaffold only |

### Reference / External / Deprecated

| Domain | Collector | Tag |
|--------|-----------|-----|
| loyalty | purchases-collector | `[REF: read-only]` — canonical reference pattern |
| loyalty | transactions-collector | `[EXTERNAL: other team]` — streaming Kafka pipeline |
| loyalty | member-tiers | `[DEPRECATED]` |
| message | communications-collector | Placeholder (empty) |
| message | templates-collector | Placeholder (empty) |
| partner | branches-collector | Deprecated (empty, replaced by master-collector) |
| partner | companies-collector | Deprecated (empty, replaced by master-collector) |

### Collector Counts by Domain

| Domain | Active Collectors | Notes |
|--------|-------------------|-------|
| **Loyalty** | 8 | members, tiers, m-t-h, coupons, backward-compat, purchases`[REF]`, transactions`[EXT]`, rewards`[CloudRun]` |
| **Sales** | 1 | sales-collector |
| **Insight** | 4 | customer-profile-collector V3, customer-svoc-interim, last-purchases, (+ legacy V1/V2) |
| **Catalog** | 1 | products-collector (DTS only, Kafka pipeline code not active) |
| **Gamification** | 2 | account-missions-collector, master-collector |
| **Message** | 2 | messages-collector, master-collector |
| **Partner** | 1 | master-collector |
| **Loyalty-Mart** | 1 | earn-analysis (Dataform only, scaffold) |

### Data Source Types

| Source Type | Collectors Using It |
|-------------|---------------------|
| **Kafka** (Confluent Cloud) | members, coupons, backward-compat, transactions, sales, account-missions, messages, products (future) |
| **REST API** (Keycloak auth) | tiers, rewards, gamification master, message master, partner master |
| **PostgreSQL** (direct DB) | members-tiers-history-collector |
| **PubSub** (GCP) | customer-profile-collector V3 |
| **S3** (AWS via DTS) | products-collector (current), customer-svoc-interim |
| **BQ** (internal) | last-purchases, earn-analysis |

---

## Coverage Assessment

| Domain | KB Depth | Pending Items | Mistakes Log | Notes |
|--------|----------|--------------|-------------|-------|
| **loyalty** | DEEP (13KB) | 19 items | 4 mistakes + 7 rules | Most mature — months of session work |
| **sales** | DEEP (20KB) | 12 items | 6 mistakes | Schema migration complete, BQ writes pending |
| **insight** | DEEP (9KB) | 13 items | — | V1/V2/V3 split, alignment gaps with loyalty |
| **catalog** | DEEP (10KB) | 9 items | — | Setup done, code adaptation pending |
| **gamification** | DEEP (6KB) | 6 items | — | Deep scan: staggered flush, Bigtable row keys, BQ join enrichment |
| **message** | DEEP (6KB) | 6 items | — | Deep scan: multi-sink fanout, API detail enrichment, Dataform 30+ fields |
| **partner** | DEEP (6KB) | 5 items | — | Deep scan: FARM_FINGERPRINT CDC, ROW_NUMBER dedup, nullifyEmpty UDF |
| **common** | DEEP (9KB) | 5 items | — | Deep scan: KafkaReader composite, BQ CDC mode, IcebergAdapter, ApiEnrichment |
| **loyalty-mart** | LIGHT (Dataform scaffold) | 5 items | — | Definitions empty, waiting for content |

---

## Cross-Domain Dependencies

```text
partner ──→ sales (Dataform JOINs: companies_branch_brand)
partner ──→ catalog (Dataform JOINs: ms_product_all)
gamification/account-missions ──→ insight (Bigtable: martech_map)
message/messages ──→ insight (Bigtable: martech_map + PubSub)
loyalty-mart ──→ loyalty (BQ refined tables)
ALL domains ──→ common (common-python-dataflow / common-python-cloudrun)
```

---

## Ownership Map

### Our Team (can modify)

- loyalty: members, tiers, m-t-h, coupons, backward-compat, rewards collectors
- sales: sales-collector
- insight: customer-profile-pipeline, last-purchases, svoc-interim
- catalog: products-collector
- gamification: account-missions, master
- message: messages, master
- partner: master
- common: common-python-dataflow, common-python-cloudrun
- loyalty-mart: earn-analysis

### External (coordinate before changes)

- loyalty/transactions-collector — other team

### Read-Only (reference only)

- loyalty/purchases-collector — canonical pattern source

### Deprecated (do not touch)

- loyalty/backup/member-tiers
- partner/branches-collector, partner/companies-collector (empty)
- message/communications-collector, message/templates-collector (empty placeholders)

---

## Shared Context Files

| File | Purpose | Key for |
|------|---------|---------|
| `shared/architecture_overview.md` | Platform-wide architecture, layers, tech stack | All agents |
| `shared/common_patterns.md` | 11 reusable patterns (BLMS, CDC, deploy, config, BKK timezone) | All agents |
| `shared/common_mistakes.md` | 7 rules + 5 shared mistakes + 5 verification patterns | All agents |
| `shared/common_infrastructure.md` | BigLake, CI templates, TF patterns, networking | Ops/Cloud agents |
| `shared/cross_domain_deps.md` | Version matrix, data deps, ownership, alignment gaps | Architecture agents |

---

## Phase 0 Completion Notes

### What was done

1. Read 15 bak_mem files + 5 domain SESSION_SUMMARYs
2. Scanned 4 new domain codebases (gamification, message, partner, common)
3. Categorized all content by domain (no content lost)
4. Separated cross-domain bleeding (sales from loyalty, shared from domain-specific)
5. Created 27 clean context files across 10 directories
6. **Phase 0.5 deep scan** (2026-04-05): Enhanced all domain KBs with architecture details from full codebase exploration

### Cross-domain bleeding resolved

- MEMORY.md sales content → `sales/knowledge_base.md`
- mistakes_and_rules.md sales mistakes → `sales/mistakes.md`
- mistakes_and_rules.md shared rules → `shared/common_mistakes.md`
- insight_knowledge_base.md loyalty comparison → `shared/cross_domain_deps.md`
- feedback_verify_before_answer.md → `shared/common_mistakes.md`
- dofns_comparison.md → `shared/common_patterns.md`
- sales_*.md (6 misplaced files) → `sales/` directory

### Ready for Phase 1

This context map + cleaned files provide the foundation for agent architecture design.
Each agent can be assigned `mem_clean_context/<domain>/` + `shared/` as its knowledge base.
