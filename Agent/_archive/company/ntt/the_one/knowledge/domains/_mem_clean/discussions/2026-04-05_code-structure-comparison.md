# Code Structure Comparison: All Collectors (2026-04-05)

## TL;DR

**Reference collector: purchases-collector** -- confirmed as the most complete Dataflow-pattern collector with full hexagonal architecture, Pydantic validation, integration tests, and all adapter layers.

However, **members-collector** has the richest domain complexity (multi-sink, CDC DELETE, init/fix job modes, API enrichment). **sales-collector** is the closest to purchases in structural fidelity but with improvements (domain-level config/ subdirectory, BQ lookup cache, enrichment DoFns).

**customer-profile-collector (refactored)** is a separate lineage -- V3 refactored with our adapter pattern applied on top of the original V3 pipeline code.

---

## 1. Reference Collector Selection

### purchases-collector (REFERENCE)

**Why**: It established the canonical patterns that all other Dataflow collectors follow:

| Trait | Detail |
|---|---|
| Dir structure | `src/adapters/input/configuration/`, `src/adapters/output/{gcs,bigquery}/`, `src/application/pipeline/`, `src/domain/config/` |
| Composition root | `main.py` wires adapters, injects PTransforms into `PipelineBuilder.__init__()` |
| Config pattern | `--dataflow_config` base64 YAML -> Pydantic `DataflowConfigDto` -> Secret Manager -> `PipelineConfig` (Pydantic) |
| Iceberg | `GcsIcebergWriterAdapter` (own adapter class wrapping managed.Write + BLMS catalog) |
| BigQuery | `BigQueryWriterAdapter` wrapping `WriteToBigQuery` with schema override logic |
| PubSub | `PubSubSink` adapter |
| Tests | `tests/unit/` (mirror src structure) + `tests/integration/pipeline/` |
| Config YAML | `config/{base,stg,prod}.yaml` |
| DLQ/Error | None (no TaggedOutput/DLQ) |
| Metrics | Counters in `dofns.py` + `avro_dofn.py` |

---

## 2. Comparison Table

### Legend
- OK = matches reference pattern
- BETTER = goes beyond reference
- PARTIAL = partially follows pattern
- DIFF = different architecture (not wrong, just different)
- MISSING = pattern not present

### 2.1 Loyalty Data Collectors (Dataflow)

| Dimension | purchases (REF) | members | tiers | m-t-h | coupons |
|---|---|---|---|---|---|
| **A. Directory Structure** | | | | | |
| src/main.py | OK | OK | OK | OK | OK |
| adapters/input/configuration/ | OK | OK | OK | OK | OK |
| adapters/output/ | gcs/, bigquery/ subdirs | flat files (bigquery_sink, iceberg_sink) | flat files | flat files | flat files |
| application/pipeline/ | builder.py, dofns.py, avro_dofn.py | builder.py, dofns.py, avro_dofn.py, api_dofns.py, transform_dofns.py | builder.py, api_dofns.py, transform_dofns.py | builder.py, dofns.py | builder.py, dofns.py, avro_dofn.py, api_dofns.py, transform_dofns.py |
| domain/ | config/ subdir (pipeline_config, bq_config), models, schemas, transformers | flat (pipeline_config, models, schemas, transformers, blms_catalog_config, managed_iceberg_write_config) | flat (same as members) | flat (same) | flat (same) |
| domain/config/ subdir | YES | NO | NO | NO | NO |
| ports/ | NO | NO | NO | NO | NO |
| **B. Composition Root** | | | | | |
| main.py wires adapters | OK | OK (+ sink factories) | OK | OK | OK |
| DI into builder | PTransforms via __init__ | PTransforms via __init__ | PTransforms via __init__ | PTransforms via __init__ | PTransforms via __init__ |
| ConfigurationAdapter class | OK | OK | OK | OK | OK |
| Secret Manager | SecretAdapter | SecretAdapter | SecretAdapter | SecretAdapter | SecretAdapter |
| **C. Configuration** | | | | | |
| YAML base+env override | base/stg/prod.yaml | base/stg/prod.yaml | base/stg/prod.yaml | base/stg/prod.yaml | base/stg/prod.yaml |
| Pydantic DTO validation | DataflowConfigDto (Pydantic BaseModel) | DataflowConfigDto (Pydantic) | DataflowConfigDto (Pydantic) | DataflowConfigDto (Pydantic) | DataflowConfigDto (Pydantic) |
| PipelineConfig type | Pydantic BaseModel | frozen dataclass | frozen dataclass | frozen dataclass | dataclass |
| CLI: --dataflow_config b64 | OK | OK | OK | OK | OK |
| **D. Pipeline Builder** | | | | | |
| PipelineBuilder class | OK | OK | OK | OK | OK |
| Method name | `run()` | `build_and_run()` | `build_and_run()` | `build_and_run()` | `build_and_run()` |
| Fan-out (multi-sink) | Kafka -> 2 Iceberg + 3 BQ + 1 PubSub | Kafka -> 4 Iceberg + 4 BQ + CDC DELETE | Iceberg + BQ refined | Iceberg + BQ refined | Kafka -> N Iceberg + BQ enriched |
| Job modes | single (streaming) | 3 modes (normal/initial_data/fix_data) | single (batch) | single (batch) | single (streaming) |
| **E. Domain Models** | | | | | |
| TypedDicts | NO | NO | NO | NO | NO |
| Pydantic models | PipelineConfig, DataflowConfigDto | DataflowConfigDto only (PipelineConfig=dataclass) | DataflowConfigDto only | DataflowConfigDto only | DataflowConfigDto only |
| Beam RowTypeConstraint | PURCHASE_ICEBERG_SCHEMA | RAW_EVENT_SCHEMA, MEMBER_INFO_SCHEMA... | TIER_EVENT_SCHEMA | HISTORY_RECORD_SCHEMA | RAW_EVENT_SCHEMA |
| PyArrow schema | NO (uses Beam managed) | YES (for manual writer) | YES (for manual writer) | YES (for manual writer) | NO |
| **F. Adapter Patterns** | | | | | |
| Iceberg sink | GcsIcebergWriterAdapter (own adapter wrapping managed.Write) | IcebergSink + ManualIcebergSink (dual-mode) | IcebergSink + ManualIcebergSink | IcebergSink + ManualIcebergSink | IcebergSink only |
| BQ sink | BigQueryWriterAdapter (wraps WriteToBigQuery) | BigQuerySink (wraps Storage Write API: append/cdc/batch) | BigQuerySink | BigQuerySink | BigQuerySink |
| CDC mode | NO | YES (member_tier, tier_maintenance) | NO (batch truncate) | NO (batch truncate/append) | YES |
| BLMS catalog config | BlmsCatalogConfig in adapters/output/gcs/ | BlmsCatalogConfig in domain/ | domain/ | domain/ | domain/ |
| ManagedIcebergWriteConfig | GcsIcebergWriterConfig in adapters/output/gcs/ | ManagedIcebergWriteConfig in domain/ | domain/ | domain/ | domain/ |
| **G. Error Handling** | | | | | |
| DLQ | NO | NO | NO | NO | NO |
| TaggedOutput | NO | NO | NO | NO | NO |
| Metrics/Counters | YES (dofns.py, avro_dofn.py) | YES (api_dofns, dofns, transform_dofns, avro_dofn) | NO | NO | NO |
| **H. Testing** | | | | | |
| tests/unit/ (mirror src) | OK (adapters/input/config, adapters/output, domain, pipeline) | OK (same structure) | OK | OK | OK (no adapters/input tests) |
| tests/integration/ | YES (pipeline/) | YES (empty dir) | YES (empty dir) | YES (empty dir) | NO |
| conftest.py | YES | YES | YES | YES | YES |
| Test count | ~18 test files | ~25 test files (215+ tests) | ~23 test files (197 tests) | ~20 test files (104 tests) | ~13 test files |

### 2.2 Non-Loyalty Dataflow Collectors

| Dimension | sales | products (catalog) | backward-compat | last-purchases |
|---|---|---|---|---|
| **A. Directory Structure** | | | | |
| src/main.py | OK | OK (clone of purchases) | OK | OK |
| adapters/input/configuration/ | OK | OK (clone) | OK (minimal) | OK |
| adapters/output/ | flat (iceberg_sink, iceberg_writer) | gcs/, bigquery/ subdirs (clone) | s3_writer only | bigquery_sink, bigquery_storage, bigquery_cdc |
| application/pipeline/ | builder, dofns, enrich_dofns, sales_enrich_dofn | builder, dofns, avro_dofn (clone) | builder only | builder, dofns |
| domain/ | config/ subdir + validators, enrichment_logic, bq_lookup_cache | config/ subdir + bq_transformers, transformers (clone) | pipeline_config only | models, transformers, bq_transformers |
| domain/config/ subdir | YES | YES (clone of purchases) | NO | NO |
| ports/ | NO | NO | NO | NO |
| **B. Composition Root** | | | | |
| main.py wires adapters | OK (+ MasterCache) | OK (clone of purchases) | OK (minimal) | OK (minimal) |
| ConfigurationAdapter | OK | OK (clone) | OK (different: b64 dataflow + b64 job) | OK |
| Secret Manager | SecretAdapter | SecretAdapter (clone: GCPSecretProvider) | NO (creds from YAML/CI) | NO |
| **C. Configuration** | | | | |
| YAML base+env | base/stg/prod.yaml | base/stg/prod.yaml | base.yaml + jobs/*.yaml | base/stg/prod.yaml |
| Pydantic DTO | DataflowConfigDto (Pydantic) | DataflowConfig (Pydantic, clone of purchases SettingsLoader) | NO (custom YAML parsing) | NO (inline parsing) |
| PipelineConfig | Pydantic BaseModel | Pydantic BaseModel (clone) | dataclass | inline in ConfigurationAdapter |
| **D. Pipeline Builder** | | | | |
| PipelineBuilder class | OK | OK (clone) | OK | OK |
| Method name | `run()` | `run()` | `build_and_run()` | `build_and_run()` |
| Fan-out | 3 Iceberg + 3 BQ (enriched) | 2 Iceberg + 3 BQ + PubSub | BQ -> Parquet -> GCS | PubSub -> BQ CDC |
| **E. Domain Models** | | | | |
| Pydantic models | YES (PipelineConfig, BigQuerySalesConfig) | YES (clone: PipelineConfig, BigQueryPurchasesConfig) | NO | NO |
| Beam RowTypeConstraint | YES (RAW_EVENT_FIELDS dynamic build) | YES (PURCHASE_ICEBERG_SCHEMA) | NO (no Iceberg) | NO (no Iceberg) |
| **F. Adapter Patterns** | | | | |
| Iceberg sink | IcebergSink (domain-level config) | GcsIcebergWriterAdapter (clone of purchases) | NONE | NONE |
| BQ sink | BigQueryWriterAdapter (from common) | BigQueryWriterAdapter (clone) | NONE (ReadFromBQ only) | BigQuerySink (same as members pattern) |
| BLMS/Iceberg config | domain/ (BlmsCatalogConfig + ManagedIcebergWriteConfig) | adapters/output/gcs/ (BlmsCatalogConfig + GcsIcebergWriterConfig) | N/A | N/A |
| **G. Error Handling** | | | | |
| Metrics/Counters | YES (dofns, kafka_reader, enrich_dofn) | NO | NO | NO |
| DLQ | NO | NO | NO | NO |
| **H. Testing** | | | | |
| tests/unit/ | RICH (31+ files, including domain, adapters, application) | OK (clone of purchases, ~18 files) | EMPTY (only __init__.py) | EMPTY (only __init__.py) |
| tests/integration/ | YES (with conftest, pipeline test) | YES (pipeline test) | NO | NO |

### 2.3 Insight Collectors

| Dimension | customer-profile-pipeline (V3 old) | customer-profile-collector (V3 refactored) | customer-svoc-interim |
|---|---|---|---|
| **A. Directory Structure** | | | |
| Package structure | `src/customer_profile/` (nested package) | DUAL: `src/customer_profile/` (old) + `src/` (new adapter layer) | `src/` (standard) |
| adapters/input/configuration/ | NO (config/ instead) | YES (new layer) + old config/ | YES |
| adapters/output/ | YES (bigquery_cdc, iceberg_writer, s3_parquet) | YES (both layers) | NO (no adapters/output/) |
| application/pipeline/ | NO (pipeline/ under customer_profile) | YES (new layer) + old pipeline/ | YES |
| domain/ | YES (models, schemas, transformers, constants) | YES (both layers) | NO |
| ports/ | YES (input_ports, output_ports — Protocol classes) | YES (inherited from old) | NO |
| **B. Composition Root** | | | |
| main.py pattern | `PipelineBuilder(options).configure().build_and_run()` | ConfigurationAdapter + PipelineBuilder(options, config) | ConfigurationAdapter + PipelineBuilder(options, config) |
| Config loading | `get_config(env)` returns dict (hardcoded) | ConfigurationAdapter (YAML b64) | ConfigurationAdapter (YAML b64) |
| DI pattern | NO (builder loads config internally) | PARTIAL (config injected, sinks created inside builder) | NO (builder creates sinks) |
| **C. Configuration** | | | |
| YAML config | NO (hardcoded dict in settings.py) | YES (base/stg/prod.yaml) | YES (base/stg/prod.yaml) |
| Pydantic | NO | Pydantic settings in new layer | NO |
| PipelineConfig | dict | frozen dataclass | inline in ConfigurationAdapter |
| **D. Pipeline Builder** | | | |
| DI of sinks | NO (sinks created inside builder) | NO (sinks created inside builder) | NO |
| `configure().build_and_run()` | YES (fluent) | YES (fluent) | NO (just `build_and_run()`) |
| **E. Domain Models** | | | |
| Protocol ports | YES (SecretProvider, MappingProvider, BigtableReader, ParquetWriter, IcebergSyncer) | YES (inherited) | NO |
| **F. Adapter Patterns** | | | |
| Iceberg | iceberg_writer + iceberg_sync (MERGE) | iceberg_sync (MERGE via BQ managed table) | NONE |
| BigQuery | CDC via `bigquery_cdc.py` (wraps WriteToBigQuery with row_mutation_info) | same (bigquery_cdc.py) | NONE (BQ read only) |
| **G. Error Handling** | | | |
| DLQ | YES (TaggedOutput to BQ DLQ table) | YES (TaggedOutput) | NO |
| Metrics | NO | NO | NO |
| **H. Testing** | | | |
| Tests | NOT in this dir (separate) | YES (~26 files, unit+integration) | NO tests dir |

### 2.4 Special Architecture: rewards-collector (CloudRun)

| Dimension | rewards-collector |
|---|---|
| Architecture | **CloudRun** (FastAPI), NOT Dataflow |
| Entry point | `create_app()` returns FastAPI instance |
| Package structure | `src/infrastructure/`, `src/adapters/input/http/`, `src/adapters/output/gcs_iceberg/` |
| Config | `pydantic-settings` via `common_cloudrun.infrastructure.settings` |
| YAML config | `config/{base,stg,prod}.yml` (note: `.yml` not `.yaml`) |
| Pipeline | `BatchPipeline` from `common_cloudrun` (Source -> Transform -> Destinations) |
| Builder dicts | `AUTH_BUILDERS`, `SOURCE_BUILDERS`, `DESTINATION_BUILDERS`, `TRANSFORM_BUILDERS` |
| DI pattern | YAML-driven dispatch to builder dicts (plugin architecture) |
| Lineage | `DataLineageAdapter` (GCP Data Lineage API) |
| Tests | unit/ + integration/ + stg/ (environment test) |
| Comparable to | NONE (completely different architecture from Dataflow collectors) |

---

## 3. Key Architectural Patterns Observed

### Pattern A: "purchases-collector pattern" (original)
Used by: purchases, products (catalog clone), sales (evolved)
- Pydantic PipelineConfig
- Adapter subdirectories (gcs/, bigquery/)
- `GcsIcebergWriterAdapter` / `BigQueryWriterAdapter`
- `run()` method on builder

### Pattern B: "members-collector pattern" (refactored D-H)
Used by: members, tiers, m-t-h, coupons
- Frozen dataclass `PipelineConfig` (or plain dataclass)
- Flat adapter files (`iceberg_sink.py`, `bigquery_sink.py`)
- `IcebergSink` / `ManualIcebergSink` / `BigQuerySink` (domain-level config objects)
- `BlmsCatalogConfig` + `ManagedIcebergWriteConfig` in domain/
- `build_and_run()` method on builder

### Pattern C: "insight V3 pipeline"
Used by: customer-profile-pipeline (old), customer-profile-collector (refactored)
- Protocol ports (hexagonal DI interfaces)
- DLQ via TaggedOutput
- Fluent builder `.configure().build_and_run()`
- Hardcoded config dict (old) or YAML + frozen dataclass (refactored)

### Pattern D: "simple batch"
Used by: backward-compatible, customer-svoc-interim
- Minimal structure, no adapter abstractions
- Direct Beam I/O in builder
- No tests

### Pattern E: "CloudRun plugin"
Used by: rewards-collector
- FastAPI + builder dicts + YAML-driven dispatch
- `common_cloudrun` framework
- Completely separate from Dataflow patterns

---

## 4. Per-Collector Alignment Checklist

### 4.1 members-collector -> align with reference

| Item | Status | Action |
|---|---|---|
| domain/config/ subdir | MISSING | Move `pipeline_config.py`, `blms_catalog_config.py`, `managed_iceberg_write_config.py` into `domain/config/` |
| PipelineConfig type | DIFF (frozen dataclass vs Pydantic) | LOW PRIORITY -- dataclass is fine, but inconsistent with purchases/sales |
| adapters/output/ subdir | DIFF (flat vs nested) | LOW PRIORITY -- flat is cleaner for this collector's complexity |
| Builder method name | `build_and_run()` vs `run()` | Trivial rename -- align or document as convention |
| Dataflow lineage | MISSING | Add `enable_lineage=true` (purchases/tiers/m-t-h have it, members does NOT) |
| DLQ | MISSING | Consider adding for streaming resilience |
| Integration tests | EMPTY | Add at least one DirectRunner integration test |

### 4.2 tiers-collector -> align with reference

| Item | Status | Action |
|---|---|---|
| domain/config/ subdir | MISSING | Move config models to `domain/config/` |
| Metrics/Counters | MISSING | Add Beam Counters for API call tracking |
| Integration tests | EMPTY | Add DirectRunner integration test |
| Dataflow lineage | OK | Already has `enable_lineage=true` |

### 4.3 members-tiers-history-collector -> align with reference

| Item | Status | Action |
|---|---|---|
| domain/config/ subdir | MISSING | Move config models to `domain/config/` |
| Metrics/Counters | MISSING | Add Beam Counters |
| Integration tests | EMPTY | Add DirectRunner integration test |
| Dataflow lineage | OK | Already has `enable_lineage=true` |

### 4.4 coupons-collector -> align with reference

| Item | Status | Action |
|---|---|---|
| domain/config/ subdir | MISSING | Move config models to `domain/config/` |
| Metrics/Counters | MISSING | Add Beam Counters |
| Integration tests | MISSING | No integration/ dir at all |
| Dataflow lineage | OK | Already has `enable_lineage=true` |
| adapters/input/ tests | MISSING | No test_configuration_adapter, test_settings |

### 4.5 sales-collector -> align with reference

| Item | Status | Action |
|---|---|---|
| domain/config/ subdir | OK | Already has `domain/config/` |
| Dataflow lineage | MISSING | Add `enable_lineage=true` in main.py |
| Pydantic PipelineConfig | OK | Matches reference |
| BLMS config location | DIFF (domain/ not adapters/output/gcs/) | OK -- evolved pattern, better separation |
| Iceberg sink | IcebergSink (not GcsIcebergWriterAdapter) | DIFF from purchases but matches members pattern |
| BQ sink | BigQueryWriterAdapter from common | OK (uses common lib) |
| Integration tests | OK | Has conftest + pipeline test |

### 4.6 products-collector (catalog) -> align with reference

| Item | Status | Action |
|---|---|---|
| Structure | OK (direct clone of purchases) | Already aligned |
| Domain names | WRONG -- still has `bigquery_purchases_config.py` | Rename to `bigquery_products_config.py` |
| Settings class | SettingsLoader (old purchases name) not ConfigurationAdapter | Inconsistent with all other collectors |
| PipelineConfig location | settings.py (inside adapters/input/configuration/) | Should be in domain/config/ (it IS in domain/config/ for the new one, but SettingsLoader has its own PipelineConfig) |
| Has 2 config systems | settings.py (SettingsLoader + PipelineConfig) AND configuration_adapter.py (ConfigurationAdapter + domain PipelineConfig) | CLEANUP: remove legacy SettingsLoader or unify |
| Integration tests | OK | Has pipeline test |

### 4.7 backward-compatible-collector

| Item | Status | Action |
|---|---|---|
| Tests | EMPTY | Add unit tests for s3_writer, configuration_adapter, builder |
| No adapters/input/configuration/settings.py | MISSING | Add Pydantic DTO validation |
| No domain/models.py | MISSING | Add if domain logic grows |
| Metrics | MISSING | Low priority (batch) |
| No logging adapter | MISSING | Uses `logging.basicConfig()` directly |

### 4.8 last-purchases-collector

| Item | Status | Action |
|---|---|---|
| Tests | EMPTY (only __init__.py) | Add unit tests |
| No secret adapter | DIFF | Config inline, no Secret Manager integration |
| No Pydantic DTO | MISSING | Add validation |
| No logging adapter | MISSING | Uses `logging.basicConfig()` directly |
| PipelineConfig | Defined inside configuration_adapter.py | Move to domain/ |

### 4.9 customer-profile-collector (refactored)

| Item | Status | Action |
|---|---|---|
| Dual code layers | TECH DEBT | Has both `src/customer_profile/` (old V3) and `src/adapters/` (new adapter layer) |
| Sink DI | MISSING | Builder creates sinks internally (not injected from main.py) |
| DLQ | OK | Has TaggedOutput DLQ pattern |
| Ports (Protocol) | OK | Inherited from V3 -- good pattern |
| Tests | OK (26 files) | Good coverage |

### 4.10 customer-svoc-interim

| Item | Status | Action |
|---|---|---|
| Tests | NONE | Add tests |
| No domain/ | MISSING | Add domain layer if logic grows |
| No adapters/output/ | MISSING | BQ read + Parquet write done inline |
| No Pydantic | MISSING | Add DTO validation |
| No logging adapter | MISSING | Uses `logging.basicConfig()` directly |

### 4.11 customer-profile-pipeline (V3 old)

| Item | Status | Action |
|---|---|---|
| Config system | Hardcoded dict (`get_config(env)`) | SUPERSEDED by collector refactored version |
| No YAML config | DIFF | Uses `--env` flag + hardcoded settings |
| DLQ | OK | Has TaggedOutput pattern |
| Ports | OK | Has Protocol interfaces (best DI pattern in codebase) |
| Status | BEING REPLACED by customer-profile-collector | Migration target |

### 4.12 rewards-collector (CloudRun)

| Item | Status | Action |
|---|---|---|
| Architecture | DIFF (CloudRun, not Dataflow) | Not comparable -- follow `common_cloudrun` patterns instead |
| Config | OK (pydantic-settings + YAML deep merge) | Good pattern |
| Lineage | OK (DataLineageAdapter) | Best lineage implementation in codebase |
| Tests | OK (unit + integration + stg env test) | Good coverage |

---

## 5. Summary: Priority Actions

### HIGH (structural inconsistency that blocks maintainability)

1. **products-collector**: Remove legacy `SettingsLoader` + inline `PipelineConfig` from `settings.py`. Keep only `ConfigurationAdapter` + domain `PipelineConfig`. Rename `bigquery_purchases_config.py` -> `bigquery_products_config.py`.
2. **members-collector**: Add `enable_lineage=true` (only collector missing it among the loyalty Dataflow group).
3. **last-purchases-collector, customer-svoc-interim, backward-compatible**: Add basic unit tests.

### MEDIUM (pattern alignment, not blocking)

4. **All D-H collectors** (members, tiers, m-t-h, coupons): Consider `domain/config/` subdirectory for config models -- matches purchases and sales pattern.
5. **coupons-collector**: Add integration test directory and adapters/input tests.
6. **tiers, m-t-h**: Add Beam metrics/counters.
7. **customer-profile-collector**: Clean up dual code layers (old V3 package + new adapter layer).

### LOW (nice to have)

8. Standardize builder method name: `run()` vs `build_and_run()` across all collectors.
9. Add DLQ pattern to streaming collectors (members, coupons, sales) -- currently only insight collectors have it.
10. Consider Protocol ports (from customer-profile-pipeline V3) as a pattern for future collectors.
11. Standardize `PipelineConfig` type: Pydantic BaseModel (purchases, sales) vs frozen dataclass (members, tiers, m-t-h, insight-refactored) -- pick one convention.

---

## 6. Architectural Evolution Map

```
Generation 1 (oldest):
  customer-profile-pipeline (V3)  -- hardcoded dict config, Protocol ports, DLQ, no YAML

Generation 2 (purchases era):
  purchases-collector             -- YAML b64, Pydantic, adapter subdirs, GcsIcebergWriterAdapter
  products-collector (clone)      -- direct copy, needs cleanup

Generation 3 (D-H refactor):
  members-collector               -- frozen dataclass, flat adapters, IcebergSink/BigQuerySink, CDC, init/fix modes
  tiers-collector                 -- batch variant of Gen 3 pattern
  m-t-h-collector                 -- batch+Postgres variant
  coupons-collector               -- streaming variant with API enrichment

Generation 3.5 (sales evolution):
  sales-collector                 -- Gen 2 structure + Gen 3 domain patterns, BQ enrichment cache

Generation 4 (cross-pollination):
  customer-profile-collector      -- Gen 1 pipeline + Gen 3 adapter layer on top
  last-purchases-collector        -- minimal Gen 3 (PubSub->BQ CDC)
  customer-svoc-interim           -- minimal batch (BQ->GCS)

CloudRun (separate lineage):
  rewards-collector               -- FastAPI + common_cloudrun framework, YAML plugin dispatch

Legacy batch:
  backward-compatible             -- BQ->Parquet->S3, minimal structure
```

---

### architect-enterprise cross-review

**1. Five architectural generations = absence of an Architecture Decision Record (ADR) process.**
Each generation was created ad-hoc without a governing standard. The data-governance-framework defines naming conventions and data quality rules but has NO section on code structure standards or architectural patterns. Recommendation: create a **Platform Architecture Standard** ADR that designates the canonical collector pattern (currently purchases-collector, Pattern A/B hybrid). All new collectors MUST follow it; existing collectors get a compliance timeline.

**2. A collector cookiecutter/template is overdue.**
With 12 collectors across 5 generations, every new collector risks inventing a 6th generation. A cookiecutter template should enforce: (a) directory structure (adapters/input/configuration, adapters/output, application/pipeline, domain/config), (b) ConfigurationAdapter + Pydantic DTO + base64 YAML pattern, (c) Dockerfile.base with boot-builder stage, (d) pre-wired CI jobs from shared GitLab CI includes, (e) `uv` with lockfile. This is the single highest-leverage governance action for preventing future drift.

**3. Naming inconsistencies are a governance problem, not just cosmetic.**

- `run()` vs `build_and_run()` -- builder method name varies by generation
- `GcsIcebergWriterAdapter` vs `IcebergSink` vs `ManualIcebergSink` -- same concept, 3 names
- `.yaml` vs `.yml` (rewards-collector uses `.yml`, all others use `.yaml`)
- `SettingsLoader` vs `ConfigurationAdapter` (products-collector has both)
- `PipelineConfig` as Pydantic BaseModel vs frozen dataclass -- same role, two types

The data-governance-framework defines naming conventions for BQ, Kafka, GCS, and IAM but NOT for code-level naming. Extend the governance framework to cover: adapter class naming pattern, builder method naming, config file extension standard, and domain model base type.

**4. Structural patterns to promote to MANDATORY vs OPTIONAL.**

- **MANDATORY**: ConfigurationAdapter + Pydantic DTO validation, YAML base+env config, uv.lock committed, Dockerfile.base with distroless, unit test directory mirroring src structure, Beam Counters/Metrics for observability.
- **RECOMMENDED**: domain/config/ subdirectory, frozen dataclass PipelineConfig, DLQ via TaggedOutput for streaming collectors.
- **OPTIONAL**: Protocol ports (only customer-profile uses them, added complexity for most collectors), Pydantic vs dataclass for PipelineConfig.

**5. Zero-test collectors (backward-compatible, last-purchases, svoc-interim) should be flagged as non-compliant.**
The governance framework defines Completeness SLOs for data but not for code quality. Recommend: minimum test coverage threshold (e.g., 60% line coverage) as a CI gate. Collectors below threshold get a compliance deadline. This prevents the "no tests" pattern from spreading.

**6. Cross-domain dependency on `common-dataflow` library versions creates hidden coupling.**
The cross_domain_deps doc shows versions ranging from 0.0.23 to 0.0.32. A breaking change in common-dataflow at 0.0.30 affects sales-collector but not loyalty collectors (still on 0.0.23). There is no compatibility matrix or changelog governance. Recommendation: common-dataflow should follow semver, publish a changelog, and have a minimum supported version policy.

**7. The "dual code layers" anti-pattern (products-collector, customer-profile-collector) needs a Definition of Done.**
Both have legacy + new code coexisting. This is a half-done refactor that accumulates governance risk (which layer runs in prod? which gets security patches?). Define a **Refactor Definition of Done**: (a) new entrypoint active in Dockerfile, (b) legacy package deleted, (c) no cross-layer imports, (d) all tests pass against new layer only, (e) deployed and verified in STG. No refactor is "done" until all 5 criteria are met.

---

### architect-cloud cross-review

**1. Missing Beam Metrics in 7 collectors -- direct impact on Cloud Monitoring and cost visibility.**
Only purchases, members, and sales have Beam Counters. The other 7 Dataflow collectors emit zero custom metrics. This means Cloud Monitoring dashboards for those collectors show only system-level metrics (CPU, memory, backlog) but NOT business metrics (records processed, API calls made, errors by type). Without custom counters, you cannot set up meaningful alerting policies -- you will only know a pipeline is sick when system lag spikes, which is a lagging indicator. Beam Counters propagate automatically to the Dataflow monitoring UI and Cloud Monitoring as `custom.googleapis.com/dataflow/*` metrics at zero additional cost. This is the highest-ROI gap to close.

**2. DLQ pattern (only in insight collectors) -- SHOULD be platform standard for streaming Dataflow.**
members-collector, coupons-collector, and sales-collector are streaming pipelines that process Kafka events. If a single malformed message causes a DoFn exception, Beam retries the entire bundle indefinitely (streaming default). Without DLQ (TaggedOutput to a dead-letter sink), one poison message can stall the entire pipeline. The insight collectors already solved this with `TaggedOutput` routing failed elements to a BQ DLQ table. For Dataflow streaming, DLQ is not optional -- it is a production resilience requirement. The cost of NOT having DLQ is a stuck pipeline requiring manual intervention, which in streaming means growing Kafka consumer lag and potential data loss if retention expires.

**3. Autoscaling configuration differences are invisible but cost-critical.**
The comparison covers code structure but NOT Dataflow job parameters. Key questions the audit should answer: (a) Which collectors set `maxNumWorkers`? An uncapped streaming job can autoscale to 100+ workers during a spike, costing hundreds of dollars per hour. (b) Which collectors use Streaming Engine (`--enable_streaming_engine`)? Without it, state is stored on worker disks, increasing both cost and OOM risk. (c) Which batch collectors could use FlexRS (Flexible Resource Scheduling) for 40-60% cost savings? tiers-collector and m-t-h run at 1 AM BKK with no latency SLA -- they are ideal FlexRS candidates. Recommend auditing `deploy_dataflow.sh` and `prepare_dataflow_config.sh` across all collectors.

**4. `run()` vs `build_and_run()` is NOT just naming -- it affects Dataflow job update behavior.**
Collectors using `run()` (purchases, sales, products) return a `PipelineResult` that can be used for `wait_until_finish()` with a timeout. Collectors using `build_and_run()` may or may not propagate the result. For streaming jobs, this matters: if the deploy script does not call `wait_until_finish()` after launching an update, the script exits before confirming the new job is healthy. The old job is already draining/cancelled. If the new job fails to start, you have zero running instances. Verify that all streaming collector deploy scripts handle this correctly.

**5. No Dataflow Lineage (`enable_lineage`) in members-collector is a Data Catalog gap.**
members-collector is the only loyalty Dataflow collector without `enable_lineage=true`. This means Data Catalog / Dataplex will show lineage for tiers, m-t-h, and purchases tables but NOT for member_info or member_tier tables. For compliance and data governance, lineage gaps are audit findings. This is a one-line fix in main.py pipeline options.

**6. batch collectors without integration tests = no confidence in Dataflow DirectRunner behavior.**
tiers-collector and m-t-h have empty `tests/integration/` directories. DirectRunner integration tests are the cheapest way to validate that a pipeline runs end-to-end without launching a Dataflow job (which costs money and takes 5+ minutes). Without them, every code change requires deploying to STG to verify -- that is slow and expensive. One DirectRunner test per collector would pay for itself in reduced STG deploy cycles.

---

### architect-solution cross-review:

**1. "Align everything to purchases-collector" is NOT the right strategy.**
purchases-collector is Gen 2 -- it predates the D-H refactor improvements. The Gen 3 pattern (members/tiers/m-t-h) is cleaner: frozen dataclass PipelineConfig gives true immutability, flat adapter files reduce nesting for collectors with few sinks, and domain-level BlmsCatalogConfig/ManagedIcebergWriteConfig make Iceberg config self-documenting. The correct reference should be a HYBRID: Gen 2 directory structure (domain/config/ subdir) + Gen 3 domain patterns (frozen dataclass, IcebergSink, BigQuerySink). sales-collector (Gen 3.5) is closest to this hybrid and should be the new de-facto reference.

**2. Batch vs streaming alignment: structural yes, behavioral no.**
tiers and m-t-h are batch collectors that naturally lack Kafka readers, DLQ, and streaming-specific patterns. Forcing streaming patterns onto them adds complexity for zero benefit. The structural alignment (domain/config/ subdir, test layout, metrics counters) is worth doing. The behavioral alignment (DLQ, streaming error handling) is NOT applicable.

**3. DLQ platform architecture recommendation.**
A `DlqSink` PTransform in `common-data-python-dataflow` that accepts TaggedOutput "bad" elements and writes to a per-collector BQ DLQ table with standard schema (timestamp, element_json, error_message, pipeline_name, step_name). Each collector wraps processing DoFns with Beam's `.with_exception_handling()` (2.50+). Start with members-collector (streaming, most complex, highest risk). This is NOT a per-collector problem -- it is a common library concern.

**4. Common library scope: infra adapters IN, domain adapters OUT.**
What should be in common lib: BlmsCatalogConfig + ManagedIcebergWriteConfig (identical across collectors), BigQuerySink PTransform (append/cdc/batch logic duplicated), DlqSink, SecretAdapter (already shared). What must stay per-collector: IcebergSink (different row_mapper), PipelineBuilder (domain-specific), PipelineConfig (different fields).

**5. Effort prioritization for structural work:**
- products-collector cleanup (remove SettingsLoader, rename files): 2 hours, highest confusion reduction.
- members-collector `enable_lineage=true`: 5 minutes, closes only gap in loyalty group.
- domain/config/ subdir for D-H collectors: 30 min each, cosmetic -- defer.
- Integration tests for untested collectors: high value, high effort -- add incrementally with feature work.
