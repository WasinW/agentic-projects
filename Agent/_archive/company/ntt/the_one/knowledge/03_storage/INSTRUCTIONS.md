# Storage Instructions

> AI: Read this file when writing to Iceberg, BigQuery, defining schemas, or managing table deployment.

## Quick Reference

```
Write Path:
  PCollection → IcebergSink (BLMS REST) → GCS Parquet + Iceberg metadata
  PCollection → BigQuerySink (Storage Write API) → BQ tables

Config Chain (Iceberg):
  YAML → Settings → ConfigAdapter → BlmsCatalogConfig → ManagedIcebergWriteConfig → IcebergSink → managed.Write

Config Chain (BigQuery):
  YAML → Settings → RefinedTableConfig → BigQuerySink → WriteToBigQuery

Schema Chain:
  Beam RowType (iceberg_writer.py) ↔ PyArrow (schemas.py) ↔ BQ JSON (schemas/*.json)
```

---

## 1. Iceberg Write — BLMS REST Catalog

### Config Dataclasses (domain/)

```python
# domain/blms_catalog_config.py
@dataclass(frozen=True)
class BlmsCatalogConfig:
    warehouse_path: str   # "gs://the1-loyalty-data-stg-pipeline-source"
    namespace: str        # "source"
    rest_uri: str         # "https://biglake.googleapis.com/iceberg/v1/restcatalog"
    project_id: str       # "the1-loyalty-data-stg"
    catalog_name: str     # Auto-derived: warehouse_path.split("/")[-1]

    def build_catalog_properties(self) -> dict[str, str]:
        return {
            "type": "rest",
            "uri": self.rest_uri,
            "warehouse": f"gs://{self.catalog_name}",
            "rest.auth.type": "org.apache.iceberg.gcp.auth.GoogleAuthManager",
            "header.X-Iceberg-Access-Delegation": "vended-credentials",
            "header.x-goog-user-project": self.project_id,
            "io-impl": "org.apache.iceberg.gcp.gcs.GCSFileIO",
            "rest-metrics-reporting-enabled": "false",
        }
```

```python
# domain/managed_iceberg_write_config.py
@dataclass(frozen=True)
class ManagedIcebergWriteConfig:
    catalog: BlmsCatalogConfig
    table_name: str                          # e.g. "member_tier"
    triggering_frequency_seconds: int = 60
    partition_fields: list[str] = field(default_factory=list)

    def get_full_table_identifier(self) -> str:
        return f"{self.catalog.namespace}.{self.table_name}"
        # → "source.member_tier"

    def get_table_location(self) -> str:
        return f"gs://{self.catalog.catalog_name}/{self.table_name}"
        # → "gs://the1-loyalty-data-stg-pipeline-source/member_tier"

    def build_writer_config(self) -> dict:
        return {
            "table": self.get_full_table_identifier(),
            "catalog_name": self.catalog.catalog_name,
            "catalog_properties": self.catalog.build_catalog_properties(),
            "table_properties": {"location": self.get_table_location()},
            "triggering_frequency_seconds": self.triggering_frequency_seconds,
            "partition_fields": self.partition_fields,
        }
```

### Writer Function (adapters/output/)

```python
# adapters/output/iceberg_writer.py
import apache_beam as beam
from apache_beam.transforms.managed import managed

def write_to_iceberg(
    pcollection: beam.PCollection,
    config: ManagedIcebergWriteConfig,
    schema: RowTypeConstraint,
    row_mapper: Callable,
    label: str,
) -> beam.PCollection:
    writer_config = config.build_writer_config()
    return (
        pcollection
        | f"{label}_MapToRow" >> beam.Map(row_mapper).with_output_types(schema)
        | f"{label}_WriteIceberg" >> managed.Write(managed.ICEBERG, config=writer_config)
    )
```

### IcebergSink PTransform

```python
# adapters/output/iceberg_sink.py
class IcebergSink(beam.PTransform):
    def __init__(self, config: ManagedIcebergWriteConfig, schema: RowTypeConstraint, row_mapper: Callable):
        self.config = config
        self.schema = schema
        self.row_mapper = row_mapper

    def expand(self, pcollection):
        return write_to_iceberg(pcollection, self.config, self.schema, self.row_mapper, self._label)
```

### Row Mapper + Schema (Beam RowType)

```python
# adapters/output/iceberg_writer.py — schema + mapper

# For tier events (etlLoadTime partition)
TIER_EVENT_SCHEMA = RowTypeConstraint.from_fields([
    ("eventId", str),
    ("source", str),
    ("eventName", str),
    ("timestamp", int),
    ("payload", str),
    ("etlLoadTime", int),       # YYYYMMDDHH Bangkok time
])

def to_tier_event_row(element: dict) -> beam.Row:
    return beam.Row(
        eventId=element["eventId"],
        source=element["source"],
        eventName=element["eventName"],
        timestamp=element["timestamp"],
        payload=element["payload"],
        etlLoadTime=_get_etl_load_time(),
    )

# For member info tables (ingestedTHDate partition)
MEMBER_INFO_SCHEMA = RowTypeConstraint.from_fields([
    ("source", str),
    ("eventName", str),
    ("timestamp", int),
    ("memberId", str),
    ("payload", str),
    ("ingestedTHDate", int),    # YYYYMMDD Bangkok time
])

def to_member_info_row(element: dict) -> beam.Row:
    return beam.Row(
        source=element["source"],
        eventName=element["eventName"],
        timestamp=element["timestamp"],
        memberId=element.get("memberId", ""),
        payload=element["payload"],
        ingestedTHDate=_get_ingested_th_date(),
    )
```

### Wiring in main.py

```python
# main.py — Create sinks, inject into builder
blms_config = BlmsCatalogConfig(
    warehouse_path=config.warehouse,
    namespace=config.blms_namespace,
    rest_uri=f"{config.blms_rest_uri_prefix}/{config.project_id}",
    project_id=config.project_id,
    catalog_name=config.warehouse.split("/")[-1],
)

member_tier_iceberg_config = ManagedIcebergWriteConfig(
    catalog=blms_config,
    table_name=config.iceberg_member_tier_table,
    triggering_frequency_seconds=config.iceberg_triggering_frequency_secs,
    partition_fields=["ingestedTHDate"],   # MUST match schema field name
)

member_tier_iceberg_sink = IcebergSink(
    config=member_tier_iceberg_config,
    schema=MEMBER_INFO_SCHEMA,
    row_mapper=to_member_info_row,
)

# Pass sink to builder
builder = PipelineBuilder(
    options=pipeline_options,
    config=config,
    member_tier_iceberg_sink=member_tier_iceberg_sink,
    # ... other sinks
)
```

### YAML Config for Iceberg

```yaml
# base.yaml
iceberg:
  warehouse: "gs://the1-loyalty-data-{env}-pipeline-source"
  blms_rest_uri_prefix: "https://biglake.googleapis.com/iceberg/v1/restcatalog"
  blms_namespace: "source"
  writer: "managed_io"              # "managed_io" (active) or "manual" (legacy)
  triggering_frequency_secs: 60
  tables:
    member_tier: "member_tier"
    member_tier_maintenance: "member_tier_maintenance"
    tier_events_upgraded: "tier_events_upgraded"
    tier_events_downgraded: "tier_events_downgraded"
```

---

## 2. BigQuery Write — Storage Write API

### Write Modes

| Mode | Method | Semantics | Use Case |
|------|--------|-----------|----------|
| `append` | `STORAGE_WRITE_API` | At-least-once | Default for most tables |
| `cdc` | Storage Write API + CDC | UPSERT/DELETE | `member_tier` (prod) |
| `batch` | `WriteToBigQuery` | WRITE_APPEND | Batch collectors (tiers, m-t-h) |

### BigQuerySink PTransform

```python
# adapters/output/bigquery_sink.py
class BigQuerySink(beam.PTransform):
    def __init__(
        self,
        table: str,                       # "project:dataset.table"
        schema: dict,                     # BQ schema dict
        write_mode: str = "append",       # "append" | "cdc" | "batch"
        partition_field: str = "etlLoadTime",
        primary_key: list[str] | None = None,  # Required for CDC
        triggering_frequency: int = 60,
    ):
        ...

    def expand(self, pcollection):
        if self.write_mode == "cdc":
            return write_to_bigquery_cdc(pcollection, ...)
        elif self.write_mode == "batch":
            return write_to_bigquery_batch(pcollection, ...)
        else:
            return write_to_bigquery_append(pcollection, ...)
```

### Append Mode

```python
# bigquery_storage.py
def write_to_bigquery_append(pcollection, table, schema, partition_field, triggering_frequency):
    return pcollection | WriteToBigQuery(
        table=table,
        schema=_convert_schema_for_beam(schema),  # DATETIME→STRING
        method=WriteToBigQuery.Method.STORAGE_WRITE_API,
        write_disposition=BigQueryDisposition.WRITE_APPEND,
        create_disposition=BigQueryDisposition.CREATE_NEVER,
        time_partitioning=TimePartitioning(type_="DAY", field=partition_field),
        triggering_frequency=triggering_frequency,
        with_auto_sharding=True,
    )
```

### CDC Mode (UPSERT/DELETE)

```python
# bigquery_storage.py — CDC write
def write_to_bigquery_cdc(pcollection, table, schema, primary_key):
    wrapped_schema = _wrap_schema_for_cdc(schema)
    return (
        pcollection
        | "WrapCdc" >> beam.ParDo(_WrapCdcRowDoFn(primary_key))
        | "WriteCdc" >> WriteToBigQuery(
            table=table,
            schema=wrapped_schema,
            method=WriteToBigQuery.Method.STORAGE_WRITE_API,
            create_disposition=BigQueryDisposition.CREATE_NEVER,
            use_cdc_writes=True,
            use_at_least_once=True,
        )
    )

class _WrapCdcRowDoFn(beam.DoFn):
    def process(self, element):
        is_delete = element.pop("_is_delete", False)
        mutation_type = "DELETE" if is_delete else "UPSERT"
        change_seq = str(Timestamp.now().micros)
        yield {
            "row_mutation_info": {
                "mutation_type": mutation_type,
                "change_sequence_number": change_seq,
            },
            "record": element,
        }
```

**CDC Prerequisites:**
- BQ table must have `PRIMARY KEY (...) NOT ENFORCED`
- Set via: `ALTER TABLE project.dataset.table ADD PRIMARY KEY (col1, col2) NOT ENFORCED`
- `write_mode: "cdc"` in YAML config
- `primary_key` field in YAML config

### CDC DELETE Pattern

```python
# In your DoFn — set _is_delete flag
def process(self, element):
    if should_delete:
        element["_is_delete"] = True
        yield element
    else:
        yield element  # Normal UPSERT

# _WrapCdcRowDoFn (bigquery_sink.py) pops _is_delete and sets mutation_type
```

### YAML Config for BigQuery

```yaml
# base.yaml
refined:
  dataset_id: "refined"
  member_tier:
    enable: true
    table: "member_tier"
    partition_field: "ingestedTHDate"  # member tables
    write_mode: "append"               # Override to "cdc" in prod.yaml
    primary_key: ["member_id", "program_code"]
    triggering_frequency: 60
  tier_events:
    upgraded_table: "tier_events_upgraded"
    downgraded_table: "tier_events_downgraded"
    partition_field: "etlLoadTime"     # event tables

# prod.yaml — override write mode
refined:
  member_tier:
    write_mode: "cdc"                  # Enable CDC in prod
```

---

## 3. Timestamp Handling (CRITICAL)

### Iceberg — Bangkok INT field

```python
from datetime import datetime, timedelta, timezone
_BANGKOK_TZ = timezone(timedelta(hours=7))

# For etlLoadTime (YYYYMMDDHH) — tier_events tables
def _get_etl_load_time() -> int:
    return int(datetime.now(_BANGKOK_TZ).strftime("%Y%m%d%H"))

# For ingestedTHDate (YYYYMMDD) — member info tables
def _get_ingested_th_date() -> int:
    return int(datetime.now(_BANGKOK_TZ).strftime("%Y%m%d"))
```

### BigQuery — Beam Timestamp (MUST use this)

```python
# CORRECT — BQ Storage Write API requires .micros attribute
from apache_beam.utils.timestamp import Timestamp
_BANGKOK_OFFSET_SECONDS = 7 * 3600
_BANGKOK_OFFSET_MICROS = _BANGKOK_OFFSET_SECONDS * 1_000_000

ts = Timestamp(micros=Timestamp.now().micros + _BANGKOK_OFFSET_MICROS)

# WRONG — will crash: AttributeError: 'datetime' has no attribute 'micros'
import datetime
ts = datetime.datetime.now()  # NEVER use for BQ writes
```

### BigQuery — DATE string for ingestedTHDate

```python
# For member tables that use DATE partition (not TIMESTAMP)
from datetime import datetime, timedelta, timezone
_BANGKOK_TZ = timezone(timedelta(hours=7))

ingested_th_date = datetime.now(_BANGKOK_TZ).strftime("%Y-%m-%d")
# → "2026-03-05" (string format for BQ DATE type)
```

---

## 4. Partition Strategies

| Table Type | Iceberg Field | BQ Field | Iceberg Type | BQ Type | Partition |
|------------|--------------|----------|-------------|---------|-----------|
| Member info (member_tier, tier_maintenance) | `ingestedTHDate` | `ingestedTHDate` | INT (YYYYMMDD) | DATE | DAY |
| Tier events (upgraded, downgraded) | `etlLoadTime` | `etlLoadTime` | INT (YYYYMMDDHH) | TIMESTAMP | DAY |
| Batch tables (tiers_master) | `etlLoadTime` | `etlLoadTime` | INT (YYYYMMDDHH) | TIMESTAMP | DAY |

**Important**: `partition_fields` in `ManagedIcebergWriteConfig` must match the field name in the Beam RowType schema exactly.

---

## 5. Schema Definitions — 3 Layers

### Layer 1: Beam RowType (Iceberg write)

Defined in `adapters/output/iceberg_writer.py`:

```python
MEMBER_INFO_SCHEMA = RowTypeConstraint.from_fields([
    ("source", str),
    ("eventName", str),
    ("timestamp", int),
    ("memberId", str),
    ("payload", str),
    ("ingestedTHDate", int),
])
```

### Layer 2: BQ Schema dict (refined write)

Defined in `domain/schemas.py`:

```python
MEMBER_TIER_REFINED_SCHEMA = {
    "fields": [
        {"name": "member_tier_id", "type": "STRING", "mode": "NULLABLE"},
        {"name": "member_id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "code", "type": "STRING", "mode": "NULLABLE"},
        {"name": "created_date", "type": "DATETIME", "mode": "NULLABLE"},
        {"name": "etl_created_date", "type": "TIMESTAMP", "mode": "NULLABLE"},
        # ...
    ]
}
```

### Layer 3: BQ JSON schema (deploy.py)

Defined in `infrastructure/{collector}/schemas/refined_*.json`:

```json
{
  "table_name": "member_tier",
  "partition_field": "created_date",
  "partition_type": "DAY",
  "clustering_fields": ["member_id", "code"],
  "primary_key": ["member_id", "program_code"],
  "labels": {
    "service": "members-collector",
    "managed_by": "table_deployer"
  },
  "schema": [
    {"name": "member_tier_id", "type": "STRING", "mode": "NULLABLE"},
    {"name": "member_id", "type": "STRING", "mode": "REQUIRED"},
    ...
  ]
}
```

### Schema Consistency Rule

All 3 layers must define the same fields. When adding a new field:
1. Add to Beam RowType in `iceberg_writer.py` (if source table)
2. Add to BQ schema dict in `schemas.py` (if refined table)
3. Add to JSON schema in `infrastructure/*/schemas/refined_*.json`
4. Add to row mapper function
5. Add to TypedDict in `schemas.py` (for type checking)

---

## 6. Table Deployment (deploy.py)

### What deploy.py Does

- Reads JSON schemas from `infrastructure/{collector}/schemas/refined_*.json`
- Creates BQ tables if they don't exist (`CREATE TABLE IF NOT EXISTS`)
- Smart change detection: skip if no changes, `ALTER TABLE ADD COLUMN` for additive, backup+migrate for breaking
- Skips empty JSON files (`if not content: continue`)
- Source Iceberg tables are NOT created by deploy.py — they are auto-created by `managed.Write`

### Running deploy.py

```bash
# CI/CD runs this in deploy-tables job
cd infrastructure/{collector}/schemas
python3 deploy.py "$PROJECT_ID" "$ENV"

# Optional filters
python3 deploy.py "$PROJECT_ID" "$ENV" --table=member_tier
python3 deploy.py "$PROJECT_ID" "$ENV" --dataset=refined
```

### Change Detection Logic

```python
class ChangeType(Enum):
    NO_CHANGE = "no_change"
    ADDITIVE = "additive"      # New columns only → ALTER TABLE ADD COLUMN
    BREAKING = "breaking"       # Modified/removed columns → backup + recreate + restore

def compare_schemas(current, desired) -> TableChange:
    # Normalizes types: INTEGER→INT64, FLOAT→FLOAT64, BOOLEAN→BOOL
    # Detects: added fields, removed fields, type changes, mode changes
```

### Adding a New BQ Table

1. Create `infrastructure/{collector}/schemas/refined_{table}.json`:
```json
{
  "table_name": "my_new_table",
  "partition_field": "ingestedTHDate",
  "partition_type": "DAY",
  "clustering_fields": ["member_id"],
  "labels": {"service": "members-collector", "managed_by": "table_deployer"},
  "schema": [
    {"name": "id", "type": "STRING", "mode": "REQUIRED"},
    {"name": "ingestedTHDate", "type": "DATE", "mode": "NULLABLE"}
  ]
}
```

2. Add BQ schema dict in `domain/schemas.py`
3. Add to deploy pipeline (CI/CD picks up new JSON files automatically)

### register_table (NOT create_table)

For Iceberg tables managed by BLMS, use `register_table` instead of `create_table`:
- Preserves field IDs across schema evolution
- Preserves partition spec
- `create_table` would reset field IDs, breaking existing data

---

## 7. Schema Type Mapping

| Python | Beam RowType | BQ Schema | BQ JSON |
|--------|-------------|-----------|---------|
| `str` | `str` | `STRING` | `"type": "STRING"` |
| `int` | `int` | `INT64` | `"type": "INTEGER"` or `"INT64"` |
| `float` | `float` | `FLOAT64` | `"type": "FLOAT"` or `"FLOAT64"` |
| `bool` | `bool` | `BOOL` | `"type": "BOOLEAN"` or `"BOOL"` |
| `Timestamp` | N/A | `TIMESTAMP` | `"type": "TIMESTAMP"` |
| `str` (date) | N/A | `DATE` | `"type": "DATE"` |
| `str` (datetime) | N/A | `DATETIME` | `"type": "DATETIME"` |

**CDC schema wrapping**: For CDC mode, `_wrap_schema_for_cdc()` wraps the original schema inside:
```json
{
  "fields": [
    {"name": "row_mutation_info", "type": "RECORD", "fields": [
      {"name": "mutation_type", "type": "STRING"},
      {"name": "change_sequence_number", "type": "STRING"}
    ]},
    {"name": "record", "type": "RECORD", "fields": [/* original schema */]}
  ]
}
```

---

## 8. DO / DON'T

| DO | DON'T |
|----|-------|
| Use `Timestamp` from `apache_beam.utils.timestamp` for BQ | Use `datetime.datetime` for BQ writes |
| Use `beam.Row` with `RowTypeConstraint` for Iceberg | Pass raw dicts to managed.Write |
| Apply Bangkok +7 to ALL timestamps | Assume UTC |
| Use `@dataclass(frozen=True)` for config objects | Use mutable dicts for config |
| Use `register_table` in deploy.py | Use `create_table` (breaks field IDs) |
| Match `partition_fields` to schema field name exactly | Mismatch partition field vs schema |
| Set `primary_key` when `write_mode: "cdc"` | Use CDC without primary key (will crash) |
| Add `PRIMARY KEY ... NOT ENFORCED` via ALTER TABLE | Rely on deploy.py alone for primary keys |
| Use `_is_delete` flag for CDC DELETE | Use DML DELETE on CDC tables |
| Skip empty JSON files in deploy.py | Fail on 0-byte schema files |

---

## 9. File Locations

```
{collector}/
├── src/
│   ├── domain/
│   │   ├── blms_catalog_config.py          # BLMS REST catalog config
│   │   ├── managed_iceberg_write_config.py # Iceberg write config
│   │   └── schemas.py                      # BQ schema dicts + TypedDicts
│   └── adapters/output/
│       ├── iceberg_writer.py               # write_to_iceberg() + Beam RowTypes
│       ├── iceberg_sink.py                 # IcebergSink PTransform
│       ├── bigquery_sink.py                # BigQuerySink PTransform
│       └── bigquery_storage.py             # Low-level BQ write functions

infrastructure/{collector}/
├── schemas/
│   ├── deploy.py                           # BQ table deployer
│   └── refined_*.json                      # BQ table schemas
└── templates/
    └── container_spec.json                 # Flex Template spec
```
