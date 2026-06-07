# Insight: customer-profile-collector Refactor Audit

**Date**: 2026-04-05
**Status**: Research Complete
**Participants**: domain-insight, architect-data

---

## Context

`customer-profile-collector` was refactored from `customer-profile-pipeline` to follow the standard collector structure used by loyalty collectors (purchases-collector, members-collector, etc.). This audit compares the refactored version against both the original pipeline and the reference standard.

**Paths:**
- Refactored: `insight/insight-api/data/customer-profile-collector/`
- Original: `insight/insight-api/data/customer-profile-pipeline/`
- Reference: `loyalty/loyalty_paralel/loyalty-data/purchases-collector/`

---

## 1. Alignment Score: ~55%

The new `src/` structure is created and partially functional, but the legacy `src/customer_profile/` package is **still the active runtime code** and has NOT been removed or fully migrated.

---

## 2. What's Done

### 2.1 New directory structure created (matches standard layout)
```
src/
  __init__.py
  main.py                           -- NEW composition root
  adapters/
    input/
      configuration/
        configuration_adapter.py     -- ConfigurationAdapter + DataflowCliOptions
        logging_adapter.py           -- LoggingAdapter with RunIdFilter
        secret_adapter.py            -- SecretAdapter (GCP Secret Manager)
        settings.py                  -- DataflowConfigDto (Pydantic, matches base.yaml)
      bigquery_mapping.py            -- BigQueryMappingFetcher (uses src.domain)
      bigtable_reader.py             -- BigtableRowFetcher (uses src.domain)
      sql_loader.py
    output/
      bigquery_cdc.py                -- get_bq_schema (uses src.domain.schemas)
      iceberg_sync.py                -- BigQueryIcebergSyncer (uses src.domain)
      iceberg_writer.py              -- write_events_consents_to_iceberg
      s3_parquet.py                  -- S3ParquetWriter (uses src.domain)
  application/
    pipeline/
      builder.py                     -- PipelineBuilder(options, config)
      dofns.py                       -- DoFns using src.* imports
  domain/
    __init__.py
    constants.py
    logging_utils.py
    models.py                        -- TypedDicts (CdcRow, DlqRecord, etc.)
    pipeline_config.py               -- PipelineConfig frozen dataclass
    schemas.py                       -- build_cdc_schema()
    transformers.py                  -- Pure functions (uses src.domain.constants)
  resources/
    sql/streaming/*.sql              -- 6 SQL files
```

### 2.2 Configuration pattern adopted
- `ConfigurationAdapter` loads `base.yaml` + env overlay (base64 or `--env` flag)
- `DataflowConfigDto` (Pydantic `BaseModel`, `extra="forbid"`) validates YAML structure
- `PipelineConfig` (frozen dataclass) holds resolved runtime values
- YAML config files: `config/base.yaml`, `config/stg.yaml`, `config/prod.yaml`
- Supports both new pattern (`--dataflow_config` base64) AND legacy (`--env` flag)

### 2.3 Composition root (src/main.py)
- Clean separation: loads config -> configures logging -> builds pipeline
- Uses `ConfigurationAdapter` and `LoggingAdapter`
- Injects `PipelineConfig` into `PipelineBuilder`

### 2.4 New DoFns use `src.*` imports
- All DoFns in `src/application/pipeline/dofns.py` import from `src.domain.*` and `src.adapters.*`
- Self-contained pattern (imports inside `setup()`/`process()`) for Dataflow worker compatibility

### 2.5 Domain models properly separated
- `models.py`: TypedDicts (MappingValue, BigtableRow, CdcRow, DlqRecord, etc.)
- `schemas.py`: CDC schema builder
- `transformers.py`: Pure functions
- `constants.py`: Type converters, SQL function mapping, timezone

### 2.6 Test structure mirrors standard layout
```
tests/
  conftest.py
  unit/
    adapters/input/configuration/    -- test_configuration_adapter, test_logging_adapter, test_secret_adapter
    adapters/input/                   -- test_bigquery_mapping, test_sql_loader
    adapters/output/                  -- test_iceberg_sync, test_s3_parquet
    core/                            -- test_logging_utils
    domain/                          -- test_transformers, test_constants, test_bq_transformers, test_pipeline_config
    pipeline/                        -- test_dofns
  integration/
    pipeline/                        -- test_consent_processing
```
- Tests import from `src.*` (not `customer_profile.*`)

### 2.7 pyproject.toml updated
- Name: `customer-profile-collector`
- Entry point: `src.main:run`
- `pythonpath = ["src"]` in pytest config
- Python 3.12, Beam 2.71.0, Pydantic

---

## 3. What's NOT Done (Critical Issues)

### 3.1 CRITICAL: Dockerfile still uses LEGACY entrypoint
```dockerfile
ENV FLEX_TEMPLATE_PYTHON_PY_FILE="/app/src/customer_profile/main.py"
```
**Impact**: In production, the OLD `customer_profile/main.py` runs, NOT `src/main.py`. The entire new `src/` structure is dead code in deployed containers.

### 3.2 CRITICAL: New builder.py still imports from legacy package
```python
# src/application/pipeline/builder.py line 119:
from src.customer_profile.domain.bq_transformers import to_ms_personas_row
```
The new builder depends on the legacy package for `bq_transformers.py`. This file exists ONLY in `src/customer_profile/domain/` -- there is no `src/domain/bq_transformers.py`.

### 3.3 CRITICAL: flex-template-spec.json uses legacy `--env` pattern
```json
{
  "name": "env",
  "label": "Environment",
  "helpText": "Environment to run the pipeline (stg, uat, prod)",
  "isOptional": false
}
```
No `--dataflow_config` parameter defined. The flex template will invoke the legacy `--env` path.

### 3.4 Legacy `customer_profile/` package is COMPLETE and ACTIVE
The entire old package structure is fully intact and operational:
```
src/customer_profile/
  main.py                   -- ACTIVE entrypoint (Dockerfile uses this)
  pipeline.py               -- 1832-line monolith (original V1 pipeline)
  config/
    logging.py              -- configure_logging() function
    options.py              -- CustomOptions (--env required)
    settings.py             -- get_config(env) dict-based config
  pipeline/
    builder.py              -- PipelineBuilder using customer_profile.* imports
    dofns.py                -- DoFns using customer_profile.* imports (~60 such imports)
  adapters/input/           -- bigquery_mapping, bigtable_reader, secret_manager, sql_loader
  adapters/output/          -- bigquery_cdc, iceberg_sync, iceberg_writer, s3_parquet
  domain/
    bq_transformers.py      -- to_ms_personas_row (NOT migrated to src/domain/)
    constants.py
    models.py
    schemas.py
    transformers.py
  core/logging_utils.py
  ports/                    -- Protocol interfaces (input_ports.py, output_ports.py)
  resources/                -- (would be in customer_profile package)
```
All legacy files use `from customer_profile.*` imports (~60+ occurrences).

### 3.5 `bq_transformers.py` not migrated
This critical file (pure transformation: Bigtable row -> ms_personas BQ row) exists only in the legacy package. The new `src/domain/` has no equivalent.

### 3.6 `ports/` layer not migrated
Legacy has `ports/input_ports.py` and `ports/output_ports.py` with Protocol interfaces. The new structure has no `ports/` directory. The standard (purchases-collector) doesn't use ports either, so this may be intentional.

### 3.7 `pipeline.py` monolith (1832 lines) still present
The original V1 monolith file (`src/customer_profile/pipeline.py`) is still in the codebase. This should be deleted once the refactored builder.py is proven.

### 3.8 `__pycache__` artifacts in legacy package
Multiple `__pycache__` directories exist under `src/customer_profile/`, indicating it was recently executed.

### 3.9 `PipelineConfig.to_legacy_config_dict()` bridge method
The new builder.py calls `self._pipeline_config.to_legacy_config_dict()` to convert the frozen dataclass back to a dict. This is a transitional bridge -- the builder still uses `config["key"]["subkey"]` dict access throughout instead of typed attribute access.

### 3.10 No dependency injection in new builder
The standard (purchases-collector) injects PTransforms via constructor:
```python
# purchases-collector: main.py creates adapters, injects into builder
builder = PipelineBuilder(options=options, config=config, kafka_reader=kafka_reader, ...)
```
The customer-profile builder directly instantiates adapters inside `configure()` and `build_and_run()`:
```python
# customer-profile: builder creates everything internally
from src.adapters.output.bigquery_cdc import get_bq_schema
from src.application.pipeline.dofns import ExtractPersonasDoFn, ...
```

---

## 4. Dual Package Resolution Plan

### What to KEEP (src/ new structure)
Everything under `src/` except `src/customer_profile/` -- the new adapters, domain, application layers are properly structured.

### What to MIGRATE from legacy before deletion
| Legacy file | Action |
|---|---|
| `customer_profile/domain/bq_transformers.py` | **MUST COPY** to `src/domain/bq_transformers.py`, update imports |
| `customer_profile/pipeline.py` (1832-line monolith) | **DELETE** -- fully replaced by `src/application/pipeline/builder.py` |
| `customer_profile/config/settings.py` (`get_config()`) | **DELETE** -- replaced by `ConfigurationAdapter` + YAML |
| `customer_profile/config/options.py` | **DELETE** -- replaced by `DataflowCliOptions` in configuration_adapter.py |
| `customer_profile/config/logging.py` | **DELETE** -- replaced by `LoggingAdapter` |
| `customer_profile/pipeline/builder.py` | **DELETE** -- replaced by `src/application/pipeline/builder.py` |
| `customer_profile/pipeline/dofns.py` | **DELETE** -- replaced by `src/application/pipeline/dofns.py` |
| `customer_profile/adapters/*` | **DELETE** -- replaced by `src/adapters/*` |
| `customer_profile/domain/*` (except bq_transformers) | **DELETE** -- replaced by `src/domain/*` |
| `customer_profile/core/logging_utils.py` | **DELETE** -- replaced by `src/domain/logging_utils.py` |
| `customer_profile/ports/` | **DELETE** -- not used in standard pattern |
| `customer_profile/resources/` | **VERIFY** vs `src/resources/` -- ensure SQL files match, then delete |
| `customer_profile/main.py` | **DELETE** -- replaced by `src/main.py` |

### What to DELETE entirely
The entire `src/customer_profile/` directory after migration of `bq_transformers.py`.

---

## 5. Dimension-by-Dimension Comparison

| Dimension | Standard (purchases) | Customer-profile NEW (src/) | Customer-profile LEGACY (customer_profile/) | Score |
|---|---|---|---|---|
| **Directory layout** | src/adapters, domain, application | Matches standard | Old flat layout | 90% |
| **Config pattern** | ConfigurationAdapter + Pydantic DTO + base64 YAML | Implemented correctly | Dict-based get_config(env) | 80% |
| **Composition root** | main.py: creates adapters, injects into builder | Partially clean (no DI for sinks) | Mixed: options + builder.configure() | 60% |
| **PipelineConfig** | Pydantic BaseModel in domain/config/ | Frozen dataclass in domain/ + to_legacy_dict() bridge | None (raw dict) | 50% |
| **DoFn location** | application/pipeline/dofns.py | Same pattern | Same pattern (parallel copy) | 80% |
| **Adapter consistency** | IcebergSink/BigQuerySink PTransforms | Direct BQ writes in builder (no adapter PTransform) | Same as NEW | 30% |
| **Builder DI** | PTransforms injected via constructor | No injection, direct instantiation | Same as original | 20% |
| **Test structure** | tests/unit/adapters/, domain/, pipeline/ | Matches standard, imports src.* | N/A | 85% |
| **Entrypoint** | Dockerfile: src/main.py | Dockerfile: customer_profile/main.py (LEGACY!) | Active | 0% |
| **Dead code** | None | 1832-line pipeline.py monolith, full legacy package | Active | 10% |

---

## 6. Ordered Refactoring Checklist

### Phase 1: Make new entrypoint active (BLOCKING)
- [ ] **1.1** Copy `src/customer_profile/domain/bq_transformers.py` to `src/domain/bq_transformers.py`
- [ ] **1.2** Update import in `src/application/pipeline/builder.py` line 119: `from src.customer_profile.domain.bq_transformers` -> `from src.domain.bq_transformers`
- [ ] **1.3** Update `Dockerfile`: `FLEX_TEMPLATE_PYTHON_PY_FILE="/app/src/main.py"`
- [ ] **1.4** Update `flex-template-spec.json`: add `dataflow_config` parameter (or verify `--env` compatibility in new main.py -- it IS supported via ConfigurationAdapter's legacy path)
- [ ] **1.5** Run full test suite to verify all tests pass with new imports
- [ ] **1.6** Deploy to STG and verify pipeline works with new entrypoint

### Phase 2: Remove legacy package
- [ ] **2.1** Verify no runtime code references `customer_profile.*` (only via `src.customer_profile` bridge or legacy imports)
- [ ] **2.2** Delete entire `src/customer_profile/` directory
- [ ] **2.3** Remove `customer_profile_pipeline.egg-info` if present
- [ ] **2.4** Run tests again to catch any broken imports
- [ ] **2.5** Update `pyproject.toml` if it has legacy package references

### Phase 3: Eliminate `to_legacy_config_dict()` bridge
- [ ] **3.1** Refactor `builder.py` to use `self._pipeline_config.attribute` instead of `config["key"]["subkey"]`
- [ ] **3.2** Remove `to_legacy_config_dict()` method from `PipelineConfig`
- [ ] **3.3** Consider migrating `PipelineConfig` from frozen dataclass to Pydantic BaseModel (matches purchases-collector)

### Phase 4: Adopt dependency injection pattern (optional, high-effort)
- [ ] **4.1** Create adapter PTransforms (e.g., `BigQueryCdcSink`, `S3ParquetSink`) as standalone classes
- [ ] **4.2** Move adapter instantiation from builder to `main.py`
- [ ] **4.3** Inject PTransforms into builder via constructor (like purchases-collector)
- [ ] **4.4** This enables mock-based integration testing of the full pipeline

### Phase 5: Cleanup
- [ ] **5.1** Remove commented-out consent processing code blocks (if permanently disabled)
- [ ] **5.2** Remove commented-out iceberg writer import in builder.py
- [ ] **5.3** Remove `Dockerfile.old` (6453 bytes, legacy)
- [ ] **5.4** Verify `src/resources/sql/` matches what was in `customer_profile/resources/`

---

## 7. Key Architectural Differences from Standard

| Aspect | purchases-collector (standard) | customer-profile-collector |
|---|---|---|
| **Input source** | Kafka (via common lib KafkaReaderAdapter) | Pub/Sub (native Beam ReadFromPubSub) |
| **Enrichment** | None (message self-contained) | Bigtable lookup per message |
| **Output sinks** | Iceberg (managed.Write) + BQ (WriteToBigQuery) + PubSub | BQ CDC (WriteToBigQuery) + S3 Parquet + Iceberg merge |
| **Iceberg write** | BLMS REST Catalog + managed.Write | NOT managed.Write -- uses MERGE from BQ CDC to Iceberg table |
| **S3 output** | No | Yes (Parquet to S3 via secret-manager AWS creds) |
| **CDC pattern** | None (append-only) | BQ Storage Write API CDC (UPSERT with primary key) |
| **Mapping** | Static schema | Dynamic mapping table from BQ (periodic refresh) |
| **Consent processing** | No | Yes (currently disabled/commented) |

These architectural differences explain why the refactor is not a 1:1 copy of the standard pattern. The customer-profile pipeline is fundamentally different in its data flow -- it's a Pub/Sub-to-BQ-CDC streaming pipeline with Bigtable enrichment, not a Kafka-to-Iceberg pipeline. The standard structure is adopted for organization, not for identical adapter implementations.

---

## 8. Risk Assessment

| Risk | Severity | Mitigation |
|---|---|---|
| Production runs legacy code (Dockerfile) | **HIGH** | Fix Dockerfile FLEX_TEMPLATE_PYTHON_PY_FILE first |
| Missing bq_transformers.py in new domain | **HIGH** | Copy before switching entrypoint |
| to_legacy_config_dict() bridge hides typing | **MEDIUM** | Phase 3 cleanup |
| No DI in builder (hard to test) | **LOW** | Phase 4, optional |
| 1832-line pipeline.py monolith is dead code | **LOW** | Delete after Phase 2 |
| Commented consent blocks (~100 lines) | **LOW** | Phase 5 cleanup |

---

### architect-enterprise cross-review

**1. Dual package (legacy + new) is a governance failure -- this should never have been merged to main.**
A half-migrated codebase where the Dockerfile still points to the OLD entrypoint means the new code is untested in production. From a governance perspective, this violates the principle of "deployable increments." Recommendation: establish a **Refactor Definition of Done** checklist that MUST be satisfied before any refactor MR is merged: (a) Dockerfile points to new entrypoint, (b) legacy package deleted or isolated behind feature flag, (c) flex-template-spec.json updated, (d) STG deployment verified, (e) no cross-layer imports. MR reviewers should block merges that leave dual active codepaths.

**2. The Dockerfile divergence is systemic, not just this collector.**
The CVE audit found 4 distinct Dockerfile patterns (distroless + boot-builder, distroless basic, CloudRun distroless, legacy pip-based). customer-profile-pipeline's Dockerfile uses `pip install --force-reinstall` with no lockfile -- the worst pattern in the fleet. The code-structure comparison found products-collector has dual config systems. This is a pattern: refactors are started but not finished across the platform. Recommendation: platform-wide **Dockerfile Standard** as part of the Architecture Decision Record, with a compliance deadline for all collectors.

**3. The `to_legacy_config_dict()` bridge method is a compliance risk.**
It converts typed configuration back to an untyped dict, bypassing the Pydantic validation that the data-governance-framework expects for data quality. If a config key is misspelled in the dict access (`config["key"]["subky"]`), it fails at runtime not at validation time. This bridge should be on the Phase 3 critical path, not optional.

**4. Missing DI in builder contradicts the platform's hexagonal architecture standard.**
The code-structure comparison identifies purchases-collector as the reference, which injects PTransforms via constructor. customer-profile-collector creates sinks internally in `build_and_run()`. This makes integration testing impossible without spinning up real BQ/S3/Bigtable. The governance implication: untestable code leads to untested deployments, which leads to production incidents. Phase 4 should be elevated from "optional" to "recommended before next major feature."

**5. No rollback plan documented.**
The 5-phase plan assumes forward-only migration. What happens if Phase 1.6 (STG deployment) fails? There is no documented rollback to the legacy entrypoint. Governance requires that any production-impacting change has a rollback procedure. Add a rollback step to each phase: revert Dockerfile, re-enable legacy package, verify legacy tests still pass.

**6. `__pycache__` artifacts in legacy package indicate CI hygiene gap.**
These should be in `.gitignore` and never committed. Their presence suggests the CI pipeline does not enforce clean builds. Add `**/__pycache__/` to `.gitignore` and add a CI lint step that fails on committed build artifacts.

**7. Timeline and ownership are undefined.**
The 5-phase checklist has no dates, no owners, and no priority relative to other platform work. Per the cross-domain deps doc, the insight team owns this collector but the CVE audit flags it as needing urgent Dockerfile modernization (VUL-04). These two workstreams should be combined: modernize Dockerfile + complete refactor in one coordinated effort with a deadline.

---

### architect-cloud cross-review

**1. Dockerfile pointing to legacy main.py -- the Dataflow Flex Template is fundamentally broken.**
`FLEX_TEMPLATE_PYTHON_PY_FILE` controls which Python file the Dataflow worker harness executes. If it points to `customer_profile/main.py`, then the entire new `src/` layer (ConfigurationAdapter, Pydantic DTO, new domain models) is never loaded on any worker VM. The Flex Template metadata in GCS references this container image, so every job launch (manual or scheduled) runs legacy code. Critically, this also means the new `config/base.yaml` and `config/stg.yaml` are unused -- the legacy `get_config(env)` dict is active. Any config changes made to YAML files have zero effect in production.

**2. flex-template-spec.json with only `--env` -- Dataflow job management is limited.**
The spec defines only one parameter (`env`). Standard collectors pass `--dataflow_config` (base64-encoded YAML) which allows overriding any config value at launch time without rebuilding the container. With only `--env`, you cannot: (a) change pipeline parallelism for a backfill, (b) override BQ dataset for testing, (c) adjust Kafka consumer group for replay, (d) toggle feature flags. Every config change requires a container rebuild + template re-upload. This multiplies the operational cost of any configuration change by the Flex Template build time (~5-7 minutes).

**3. Two main.py files = Dataflow worker classpath ambiguity risk.**
Dataflow Flex Templates package the entire `/app/` directory into the worker container. Both `src/main.py` and `src/customer_profile/main.py` exist in the container filesystem. If any import path resolves ambiguously (e.g., a DoFn importing `from main import ...`), different workers could load different modules depending on `sys.path` order. This is especially dangerous with Dataflow's `--save_main_session` flag, which pickles the main module and distributes it to workers. If the pickled session contains references from the wrong main.py, workers will crash with `ImportError` or silently use stale code.

**4. Missing `--dataflow_config` means no Dataflow job update compatibility.**
When updating a streaming Dataflow job (drain old + launch new), the new job must be launched with the same parameter schema as the old job. If you later add `--dataflow_config` to the flex-template-spec and try to update a running job that was launched with only `--env`, the parameter mismatch will cause the update to fail. You would need to cancel (not drain) the old job and launch a fresh one, losing any in-flight state. Plan the parameter migration during a maintenance window.

**5. Bigtable enrichment on Dataflow workers -- cost and performance consideration.**
The customer-profile pipeline does per-message Bigtable lookups in DoFns. Each Dataflow worker opens its own Bigtable connection. With autoscaling, N workers = N concurrent Bigtable clients. Bigtable pricing is node-based -- if the pipeline autoscales to many workers during a traffic spike, Bigtable read throughput must keep up or lookups will timeout, causing bundle retries and further autoscaling. This is a positive feedback loop that can escalate cost. The refactored builder should implement Bigtable connection pooling per worker (via `setup()` method) and batch lookups where possible. Neither the legacy nor the new builder appears to address this.

**6. S3 Parquet output from Dataflow -- cross-cloud egress cost.**
This collector writes Parquet to S3 (AWS). Dataflow workers run in GCP. Every byte written to S3 incurs GCP internet egress charges ($0.12/GB for asia-southeast1). If the pipeline processes significant volume, this cross-cloud egress becomes a material cost line item. The refactor audit does not mention this. Verify: (a) is the S3 write still active or was it disabled during refactor? (b) if active, is there a GCS mirror that could replace S3 for downstream consumers? (c) if S3 is required, consider using a VPN/Interconnect to reduce egress costs.

**7. The `to_legacy_config_dict()` bridge has a hidden Dataflow implication.**
Dataflow Flex Templates serialize pipeline options for display in the Dataflow UI. Pydantic models and frozen dataclasses serialize cleanly. A raw dict converted from `to_legacy_config_dict()` may produce unreadable or overly verbose entries in the Dataflow job's "Pipeline Options" tab, making debugging harder. More importantly, if the dict contains secrets (API keys from Secret Manager), they could appear in plaintext in the Dataflow UI, which is visible to anyone with `dataflow.jobs.get` permission.

---

### architect-solution cross-review:

**1. Complete the refactor, do NOT start fresh.**
The new src/ structure is 55% done but the remaining 45% is well-defined: migrate bq_transformers.py, switch Dockerfile entrypoint, delete legacy package. Starting fresh re-does the 55% that works. Cost-benefit: completing = ~2-3 days; starting fresh = ~2 weeks with higher regression risk. Phase 1 (switching entrypoint) is the critical path -- do it first, deploy to STG, then clean up legacy in Phase 2.

**2. The `to_ms_personas_row` pure function pattern is BETTER for its use case but not universally applicable.**
The mapping-driven approach (dict-in, dict-out, explicit field mapping) works well here because the transformation is a flat Bigtable-to-BQ mapping with type conversions, no external I/O. For collectors doing API enrichment (members, coupons, sales), DoFn-based transforms are correct because they need `setup()` for HTTP clients and `process()` for per-element calls. Guideline: pure functions for stateless data mapping, DoFns when lifecycle management is needed. Both patterns should coexist.

**3. PubSub vs Kafka: do NOT standardize the transport.**
customer-profile uses PubSub because its source is GCP-native (Bigtable change streams). Loyalty collectors use Kafka because The1 event platform produces to Kafka. Forcing one transport on all collectors creates unnecessary integration complexity. The MESSAGE FORMAT (event envelope schema) should be standardized, not the transport. A PubSubReaderAdapter in common lib would complete the picture alongside the existing KafkaReaderAdapter.

**4. The `to_legacy_config_dict()` bridge should be elevated to Phase 2 priority.**
This bridge converts typed config back to untyped dict, defeating the purpose of Pydantic validation and enabling runtime key-miss errors invisible to mypy. The secret leakage risk architect-cloud identified (secrets in Dataflow UI) makes this urgent. Eliminate it immediately after switching the entrypoint -- do not wait for a separate Phase 3.

**5. Phase 4 (DI in builder) is conditional: only invest if integration tests are planned.**
Without DI, the builder creates real adapters internally, preventing mock-based pipeline graph testing on DirectRunner. With DI, integration tests can inject mock PTransforms. This is the same payoff purchases-collector gets. Recommend Phase 4 only if the team commits to adding integration tests; otherwise the DI refactor has no consumer and adds indirection for no benefit.
