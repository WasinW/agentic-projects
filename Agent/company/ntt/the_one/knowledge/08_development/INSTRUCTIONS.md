# Development Instructions

> AI: Read this file when writing or modifying code in any collector.

## Quick Reference

```bash
# After ANY code change — run all 5:
uv sync && uv run ruff check --fix . && uv run ruff format . && uv run mypy src tests && uv run pytest
```

---

## 1. Repository Structure — Where to Put Code

```
{collector}/
├── src/
│   ├── main.py                              # Entry point (CLI args → PipelineConfig → build)
│   ├── domain/                              # PURE LOGIC — no I/O, no Beam imports
│   │   ├── models.py                        # @dataclass(frozen=True) domain objects
│   │   ├── schemas.py                       # Beam RowType + Iceberg + BQ JSON schemas
│   │   ├── transformers.py                  # Pure transform functions
│   │   ├── blms_catalog_config.py           # BLMS REST Catalog config (frozen dataclass)
│   │   ├── managed_iceberg_write_config.py  # Managed IcebergIO write config (frozen dataclass)
│   │   └── pipeline_config.py               # Aggregated runtime config
│   ├── adapters/                            # I/O — Kafka, BQ, Iceberg, config loading
│   │   ├── input/
│   │   │   ├── configuration/               # YAML loading + Pydantic Settings
│   │   │   └── kafka/                       # Kafka reader (streaming only)
│   │   └── output/
│   │       ├── iceberg_writer.py            # write_to_iceberg() function
│   │       ├── iceberg_sink.py              # IcebergSink(config, schema, row_mapper)
│   │       ├── bigquery_sink.py             # BigQuery write adapter
│   │       └── bigquery_storage.py          # BQ writer config (CDC/APPEND)
│   └── application/
│       └── pipeline/
│           └── builder.py                   # Pipeline construction (Beam DAG)
├── config/
│   ├── base.yaml                            # Shared defaults
│   ├── stg.yaml                             # STG overrides
│   └── prod.yaml                            # PROD overrides
├── tests/
│   ├── conftest.py                          # Shared fixtures
│   └── unit/                                # All test files here
├── pyproject.toml                           # Dependencies + tool config
└── Dockerfile                               # Multi-stage build
```

## 2. Layer Rules — MUST FOLLOW

| Layer | CAN import | MUST NOT import | Put here |
|-------|-----------|-----------------|----------|
| **domain/** | Python stdlib only | `apache_beam`, `google.cloud`, adapters, application | Models, schemas, transformers, validators, config dataclasses |
| **adapters/** | domain/ | application/ | Kafka reader, BQ writer, Iceberg writer, YAML config loader |
| **application/** | domain/, adapters/ | — | Pipeline builder (wiring Beam DAG) |
| **main.py** | everything | — | CLI args, config loading, builder invocation |

**Rule**: If your code does I/O (network, disk, GCP) → adapters/. If it's pure logic → domain/.

## 3. Configuration — YAML + Pydantic

```
base.yaml + {env}.yaml → YamlLoader → Pydantic Settings → ConfigAdapter → PipelineConfig
```

### Adding a new config field:

1. Add to `config/base.yaml` (default value)
2. Override in `config/stg.yaml` and/or `config/prod.yaml` if needed
3. Add field to Pydantic Settings model in `adapters/input/configuration/settings.py`
4. If it creates a domain config, add to `domain/pipeline_config.py`
5. Use in builder/DoFn via `PipelineConfig`

### Example Settings model:

```python
from pydantic import BaseModel, ConfigDict

class RefinedTableConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    dataset: str
    table: str
    write_mode: str = "append"        # "append" or "cdc"
    primary_key: list[str] | None = None
    partition_field: str = "ingestedTHDate"
```

## 4. Key Patterns — Copy These

### Bangkok Timezone (CRITICAL)

ALL timestamps must use Bangkok +7. Never use UTC directly.

```python
# For Iceberg source layer (INT field like 20260305)
from datetime import datetime, timedelta, timezone
_BANGKOK_TZ = timezone(timedelta(hours=7))

def _get_ingested_th_date() -> int:
    return int(datetime.now(_BANGKOK_TZ).strftime("%Y%m%d"))
```

```python
# For BigQuery refined layer (Beam Timestamp)
from apache_beam.utils.timestamp import Timestamp
_BANGKOK_OFFSET_SECONDS = 7 * 3600
_BANGKOK_OFFSET_MICROS = _BANGKOK_OFFSET_SECONDS * 1_000_000

ts = Timestamp(micros=Timestamp.now().micros + _BANGKOK_OFFSET_MICROS)
```

### BigQuery Timestamp — MUST use Beam Timestamp

```python
# CORRECT — BQ Storage Write API requires .micros attribute
from apache_beam.utils.timestamp import Timestamp
ts = Timestamp(seconds=unix_seconds)

# WRONG — will crash: AttributeError: 'datetime' has no attribute 'micros'
import datetime
ts = datetime.datetime.now()  # NEVER use this for BQ writes
```

### CDC Write Mode

```yaml
# prod.yaml
refined:
  member_tier:
    write_mode: "cdc"
    primary_key: ["memberTierId"]
```

CDC uses BQ Storage Write API UPSERT. The primary key must match the BQ table's primary key (set via `ALTER TABLE ... ADD PRIMARY KEY ... NOT ENFORCED`).

### CDC DELETE pattern

```python
# In your DoFn, set _is_delete flag on the element
element["_is_delete"] = True
# _WrapCdcRowDoFn in bigquery_sink.py pops this flag
# and sets mutation_type="DELETE" for BQ Storage Write API
```

### Job Types

| Type | Mode | Trigger | When to use |
|------|------|---------|-------------|
| `normal` | Streaming | Kafka (continuous) | Default for streaming collectors |
| `initial_data` | Batch | GitLab CI (`TRIGGER_INIT_DATA_LOAD=1`) | Historical backfill |

## 5. Testing

### Test conventions

```python
# File: tests/unit/test_{module_name}.py
# Function: test_{function}_{scenario}

class TestMyDoFn:
    def test_process_valid_input(self):
        """Should transform valid input correctly."""
        ...

    def test_process_missing_field(self):
        """Should handle missing field gracefully."""
        ...
```

### DoFn testing pattern

```python
import apache_beam as beam
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to

def test_my_transform():
    with TestPipeline() as p:
        result = (
            p
            | beam.Create([{"key": "value"}])
            | beam.ParDo(MyDoFn())
        )
        assert_that(result, equal_to([expected]))
```

### Running tests

```bash
uv run pytest                        # All tests
uv run pytest -v                     # Verbose
uv run pytest tests/unit/test_x.py   # Specific file
uv run pytest --cov=src              # With coverage
```

## 6. Code Quality — All 3 Must Pass

```bash
uv run ruff check --fix .   # Lint (auto-fix)
uv run ruff format .        # Format
uv run mypy src tests       # Type check
```

### Ruff config (pyproject.toml):

```toml
[tool.ruff]
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "C4", "RUF"]
```

### Mypy config (pyproject.toml):

```toml
[tool.mypy]
python_version = "3.12"
strict = true
plugins = ["pydantic.mypy"]

[[tool.mypy.overrides]]
module = ["apache_beam", "apache_beam.*"]
follow_imports = "skip"
ignore_missing_imports = true
```

## 7. Docker Build

All collectors use the same 2-stage pattern:

```dockerfile
# Stage 1: Builder
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev
COPY . .
RUN uv sync --frozen --no-dev

# Stage 2: Runtime (Dataflow Flex Template)
FROM gcr.io/dataflow-templates-base/python312-template-launcher-base:...
USER root
RUN apt-get update && apt-get install -y openjdk-17-jre-headless  # Java 17 for Kafka
COPY --from=builder /app /app
ENV FLEX_TEMPLATE_PYTHON_PY_FILE="/app/src/main.py"
```

**Why Java 17?** Apache Beam Kafka uses cross-language transforms (SchemaTransform) that need JRE.

## 8. Common Library

```toml
# pyproject.toml — install from GitLab
[tool.uv.sources]
common-data-python = {
    git = "ssh://git@gitlab.com/The1central/The1/the1-data/common-data.git",
    subdirectory = "common-python",
    tag = "0.0.9"
}
```

Provides: `KafkaReaderConfig` (bootstrap servers, topics, consumer group, Schema Registry).

## 9. DO / DON'T

| DO | DON'T |
|----|-------|
| Use `Timestamp` from `apache_beam.utils.timestamp` for BQ | Use `datetime.datetime` for BQ writes |
| Apply Bangkok +7 to ALL timestamps | Assume UTC |
| Use `@dataclass(frozen=True)` for domain configs | Use mutable dicts for config |
| Use `register_table` in deploy.py | Use `create_table` (breaks field IDs) |
| Run `uv sync` before any code quality check | Skip `uv sync` after dependency changes |
| Use `r"pattern"` for regex strings | Use plain strings (Ruff RUF043) |
| Keep domain/ pure (no Beam/GCP imports) | Import `apache_beam` in domain/ |
| Read existing code before modifying | Guess how code works |

## 10. Workflow Checklist

### Before coding:
- [ ] Read existing code in the affected files
- [ ] Check which collector(s) are affected
- [ ] `purchases-collector` is READ-ONLY (reference only)
- [ ] `transactions-collector` is NOT ours — coordinate with other team

### After coding:
- [ ] `uv sync`
- [ ] `uv run ruff check --fix . && uv run ruff format .`
- [ ] `uv run mypy src tests`
- [ ] `uv run pytest`
- [ ] `uv run pre-commit run --all-files`
