# Sales-Collector: Initial Data Load & Members Pattern Alignment

## Date: 2026-02-26

## What Changed (Alignment with Members Pattern)

### TF Infrastructure
- `bigquery.tf`: Removed `external_catalog_dataset_options` from source dataset
- `biglake-metastore.tf`: Changed collector SA `biglake.admin` → `biglake.editor`

### New Files (Members Pattern)
- `src/domain/blms_catalog_config.py` — BLMS REST Catalog config (frozen dataclass)
- `src/domain/managed_iceberg_write_config.py` — Writer config with `partition_fields: list[str]`
- `src/adapters/output/iceberg_writer.py` — `write_to_iceberg()` + `build_beam_schema()`
- `src/adapters/output/iceberg_sink.py` — `IcebergSink(config, schema, row_mapper)`

### Deleted Files
- `src/adapters/output/gcs/biglake_metastore_config.py`
- `src/adapters/output/gcs/gcs_biglake_iceberg_writer_config.py`
- `src/adapters/output/gcs/gcs_biglake_iceberg_writer.py`

### Removed
- `_cleanup_blms_entry()` from main.py — user does manual BLMS cleanup via `blms_helper 1.py`

## Initial Data Load Feature

### How It Works
```
BQ prev_raw_sales (external table over old parquet)
  → --job_type=initial_data
  → ReadFromBigQuery (SQL from resources/init/)
  → to_raw_event_row_passthrough (preserve ingestedTHDate/Hour)
  → managed.Write(ICEBERG) batch (no triggering_frequency)
  → gs://bucket/raw_sales/ (correct flat path)
```

### Config (stg.yaml / prod.yaml)
```yaml
init_data:
  source:
    raw_sales:
      enabled: true
      script: "load_raw_sales_source.sql"
      target: "raw_sales"
      # condition_parts: ["ingestedTHDate >= 20260101"]  # for parallel split
```

### CLI
```bash
# Normal streaming
python -m src.main --dataflow_config=... --job_type=normal

# Batch initial data load
python -m src.main --dataflow_config=... --job_type=initial_data
```

### Files Changed
| File | Change |
|------|--------|
| `settings.py` | `JobType` enum, `InitDataConfig` models, `--job_type` CLI |
| `pipeline_config.py` | `job_type` + `init_data` fields |
| `configuration_adapter.py` | Parse `job_type`, validate `init_data` |
| `row_mappers.py` | `to_raw_event_row_passthrough()` |
| `builder.py` | `_build_init_data_pipeline()`, `_read_init_sql_file()` |
| `resources/init/load_raw_sales_source.sql` | SQL for BQ read |
| `config/stg.yaml` | `init_data` section |
| `config/prod.yaml` | `init_data` section with `condition_parts` example |

### Tests: 148 total (128 existing + 20 new)
- `tests/unit/test_init_data.py`: 20 tests covering:
  - JobType enum
  - InitDataConfig models (has_any_enabled, get_enabled_source_tables)
  - DataflowConfigDto with init_data
  - Row mapper passthrough
  - SQL file reading + condition appending

## Migration Steps
1. User: Drop BLMS entry via `blms_helper 1.py`
2. User: Delete BLMS dataset `source`
3. User: Create `prev_raw_sales` BQ external table over old parquet
4. Deploy streaming (normal) — Iceberg recreates at flat path
5. Deploy batch (`--job_type=initial_data`) — re-ingest old data
6. Verify row counts match
7. Disable init_data in config, clean up prev_raw_sales
