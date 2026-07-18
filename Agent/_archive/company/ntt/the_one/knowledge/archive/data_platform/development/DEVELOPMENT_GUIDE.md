# Data Platform - Development Guide

> **Last Updated:** 2026-02-20
> **Scope:** Development practices for all Data Platform Python collectors (loyalty-data, sales-data)
> **Applies to:** members-collector, tiers-collector, members-tiers-history-collector, sales-collector, purchases-collector, transactions-collector

---

## Table of Contents

1. [Repository Structure](#1-repository-structure)
2. [Hexagonal Architecture](#2-hexagonal-architecture)
3. [Configuration System](#3-configuration-system)
4. [Testing Strategy](#4-testing-strategy)
5. [Code Quality Tools](#5-code-quality-tools)
6. [Docker Build](#6-docker-build)
7. [Common Library](#7-common-library)
8. [Key Patterns](#8-key-patterns)
9. [Dependencies](#9-dependencies)
10. [Local Development Setup](#10-local-development-setup)
11. [Workflow Checklist](#11-workflow-checklist)

---

## 1. Repository Structure

### Per-Collector Layout

Each collector follows the same directory structure:

```
{collector}/
+-- src/
|   +-- __init__.py
|   +-- main.py                              # Pipeline entry point
|   +-- domain/                              # Domain layer (pure logic)
|   |   +-- __init__.py
|   |   +-- models.py                        # Domain models (dataclasses/Pydantic)
|   |   +-- schemas.py                       # Beam RowType, Iceberg, BQ schemas
|   |   +-- transformers.py                  # Pure transform functions
|   |   +-- validators.py                    # Input validation (optional)
|   |   +-- blms_catalog_config.py           # BLMS REST Catalog config
|   |   +-- managed_iceberg_write_config.py  # Managed IcebergIO write config
|   |   +-- pipeline_config.py               # Aggregated runtime config
|   |   +-- config/                          # Config domain models (optional)
|   +-- adapters/                            # Adapters layer (I/O)
|   |   +-- __init__.py
|   |   +-- input/
|   |   |   +-- configuration/               # YAML loading + Pydantic settings
|   |   |   +-- kafka/                       # Kafka reader (streaming collectors)
|   |   +-- output/
|   |       +-- iceberg_writer.py            # Iceberg write adapter
|   |       +-- iceberg_sink.py              # IcebergSink convenience class
|   |       +-- bigquery_sink.py             # BigQuery write adapter
|   |       +-- bigquery_storage.py          # BQ writer config
|   |       +-- bq_metadata_refresh.py       # Option B refresh (disabled)
|   +-- application/                         # Application layer (pipeline wiring)
|       +-- pipeline/
|           +-- builder.py                   # Pipeline construction
+-- config/
|   +-- base.yaml                            # Base config (shared settings)
|   +-- stg.yaml                             # STG environment overrides
|   +-- prod.yaml                            # PROD environment overrides
+-- tests/
|   +-- __init__.py
|   +-- conftest.py                          # Shared fixtures
|   +-- unit/                                # Unit tests
|   +-- integration/                         # Integration tests (optional)
+-- pyproject.toml                           # Project metadata + tool config
+-- uv.lock                                  # Dependency lock file
+-- Dockerfile                               # Multi-stage Docker build
+-- sonar-project.properties                 # SonarQube config
+-- README.md                                # Collector-specific docs
```

### Infrastructure Layout

```
infrastructure/
+-- common/
|   +-- GCP/                                 # Shared GCP resources
|   +-- AWS/                                 # Cross-cloud resources (if any)
+-- {collector}/
    +-- main.tf                              # Provider + backend
    +-- variables.tf                         # Input variables
    +-- terraform.tfvars                     # Variable values
    +-- artifact.tf                          # GAR repository
    +-- bucket.tf                            # GCS bucket(s)
    +-- secret-manager.tf                    # Service secret
    +-- biglake-metastore.tf                 # BigLake IAM
    +-- scheduler.tf                         # Cloud Scheduler (batch only)
    +-- schemas/
    |   +-- deploy.py                        # BQ table deployment script
    +-- templates/
        +-- container_spec.json              # Flex Template specification
```

---

## 2. Hexagonal Architecture

### Pattern Diagram

```
+-----------------------------------------------------------------------+
|                           EXTERNAL SYSTEMS                            |
|  Kafka / API / PostgreSQL          BigQuery / Iceberg / GCS           |
+----------+------------------------------+-----------------------------+
           |                              |
           v                              v
+----------+----------+    +--------------+-----------+
|   INPUT ADAPTERS     |    |    OUTPUT ADAPTERS       |
| - Configuration      |    | - IcebergWriter          |
| - KafkaReader        |    | - IcebergSink            |
| - APIClient          |    | - BigQuerySink           |
| - PostgresReader     |    | - BqMetadataRefresh      |
+----------+----------+    +--------------+-----------+
           |                              ^
           v                              |
+----------+------------------------------+-----------------------------+
|                                                                       |
|                        DOMAIN LAYER (Pure Logic)                      |
|                                                                       |
|  +---------------+  +---------------+  +------------------+           |
|  |    Models     |  | Transformers  |  |     Schemas      |           |
|  | (dataclasses) |  | (pure funcs)  |  | (Beam/Iceberg/BQ)|           |
|  +---------------+  +---------------+  +------------------+           |
|                                                                       |
|  +-------------------------------+  +-----------------------------+   |
|  | BlmsCatalogConfig             |  | ManagedIcebergWriteConfig   |   |
|  | (frozen dataclass)            |  | (frozen dataclass)          |   |
|  +-------------------------------+  +-----------------------------+   |
|                                                                       |
+-----------------------------------------------------------------------+
           ^                              |
           |                              v
+----------+------------------------------+-----------------------------+
|                   APPLICATION LAYER (Pipeline Wiring)                 |
|                                                                       |
|  PipelineConfig --> Builder --> Apache Beam Pipeline                   |
|                                                                       |
+-----------------------------------------------------------------------+
```

### Layer Rules

| Layer | Can Import | Must Not Import | Contains |
|-------|-----------|-----------------|----------|
| Domain | Python stdlib only | adapters, application | Models, schemas, transformers, validators |
| Adapters | domain | application | I/O implementations (Kafka, BQ, Iceberg, config) |
| Application | domain, adapters | (nothing restricted) | Pipeline construction, orchestration |
| main.py | Everything | - | Entry point, CLI args |

### Domain Model Guidelines

- Use `@dataclass(frozen=True)` for immutable configuration objects
- Use Pydantic `BaseModel` for validated configuration
- Domain models must be pure Python (no Beam, no GCP imports)
- Transformers must be pure functions (no side effects)

---

## 3. Configuration System

### YAML + Pydantic Pattern

```
base.yaml + {env}.yaml --> YamlLoader --> Pydantic Settings --> PipelineConfig
```

### Configuration Flow

1. **base.yaml** -- Default settings shared across all environments
2. **{env}.yaml** -- Environment-specific overrides (stg.yaml, prod.yaml)
3. **Deep merge** -- Environment config overrides base config (nested merge for sections like `iceberg`, `refined`)
4. **Pydantic validation** -- Settings model validates and transforms raw YAML
5. **ConfigAdapter** -- Transforms Settings into domain config objects
6. **PipelineConfig** -- Final runtime configuration used throughout the pipeline

### Example Settings Model

```python
from pydantic import BaseModel, ConfigDict

class PipelineConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    project_id: str
    kafka_config: KafkaReaderConfig
    iceberg_config: GcsIcebergWriterConfig
    bq_config: BigQuerySalesConfig
    window_size_seconds: int
    log_level: str
```

### Config in Dataflow

Configuration is passed to Dataflow as a base64-encoded YAML string:
```bash
dataflow_config = base64encode(yamlencode(merged_config))
```

The pipeline decodes this at startup via the `--dataflow_config` parameter.

---

## 4. Testing Strategy

### Test Types

| Type | Directory | Purpose | Framework |
|------|-----------|---------|-----------|
| Unit Tests | `tests/unit/` | Test individual functions/classes in isolation | pytest |
| Integration Tests | `tests/integration/` | Test adapter interactions (optional) | pytest |
| DoFn Tests | `tests/unit/` | Test Beam DoFn transform logic | pytest + TestPipeline |

### Test Conventions

```python
# File naming: test_{module_name}.py
# Function naming: test_{function_name}_{scenario}

class TestExtractPayloadDoFn:
    """Tests for ExtractPayloadDoFn."""

    def test_process_valid_event(self):
        """Should extract payload from valid event."""
        ...

    def test_process_missing_field(self):
        """Should handle missing field gracefully."""
        ...
```

### DoFn Testing Pattern

```python
import apache_beam as beam
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to

def test_transform_dofn():
    with TestPipeline() as p:
        input_data = [{"key": "value"}]
        result = (
            p
            | beam.Create(input_data)
            | beam.ParDo(MyTransformDoFn())
        )
        assert_that(result, equal_to([expected_output]))
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/unit/test_transformers.py

# Run with coverage
uv run pytest --cov=src --cov-report=html --cov-report=xml:coverage.xml

# Run unit tests only
uv run pytest tests/unit

# Run integration tests only
uv run pytest tests/integration
```

### Fixtures (conftest.py)

Common fixtures in `tests/conftest.py`:
- Sample Kafka messages
- Mock configurations
- Pydantic model factories
- Beam TestPipeline setup

---

## 5. Code Quality Tools

### Required Tools

All three tools MUST pass before any code changes are considered complete:

#### 1. Ruff (Linter + Formatter)

```bash
# Check for lint errors
uv run ruff check .

# Auto-fix lint errors
uv run ruff check --fix .

# Format code
uv run ruff format .
```

Configuration in `pyproject.toml`:
```toml
[tool.ruff]
line-length = 120

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "F",    # pyflakes
    "I",    # isort
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "SIM",  # flake8-simplify
    "C4",   # flake8-comprehensions
    "RUF",  # ruff-specific rules
]
```

#### 2. Mypy (Type Checker)

```bash
uv run mypy src tests
```

Configuration in `pyproject.toml`:
```toml
[tool.mypy]
python_version = "3.12"
strict = true
disallow_untyped_defs = true
plugins = ["pydantic.mypy"]

[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true

# Apache Beam stubs not available
[[tool.mypy.overrides]]
module = ["apache_beam", "apache_beam.*"]
follow_imports = "skip"
ignore_missing_imports = true

# PyArrow stubs not complete
[[tool.mypy.overrides]]
module = "pyarrow"
ignore_missing_imports = true

# Common library
[[tool.mypy.overrides]]
module = ["common", "common.*"]
follow_imports = "skip"
ignore_missing_imports = true
disable_error_code = ["import-untyped"]
```

#### 3. Pytest

```bash
uv run pytest
```

### Pre-commit Hooks

```bash
# Install hooks
uv run pre-commit install

# Run all hooks manually
uv run pre-commit run --all-files
```

### Workflow After Code Changes

```bash
uv sync              # Ensure dependencies are up to date
uv run ruff check .  # Lint
uv run ruff format . # Format
uv run mypy src tests  # Type check
uv run pytest        # Tests
uv run pre-commit run --all-files  # All hooks
```

### Task Runner (poethepoet)

Some collectors use `poe` tasks defined in `pyproject.toml`:

```bash
uv run poe test          # Run all tests
uv run poe test:cov      # Tests with coverage
uv run poe test:unit     # Unit tests only
uv run poe format        # Format code
uv run poe check         # Lint code
uv run poe typecheck     # Type check
uv run poe lint          # All quality checks (format + check + typecheck)
uv run poe clean         # Remove build artifacts
```

---

## 6. Docker Build

### Multi-Stage Build Pattern

All Dataflow collectors use the same two-stage Docker build:

```dockerfile
# Stage 1: Builder (dependency resolution)
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS builder
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1

# For private Git dependencies (common-data-python)
ARG CI_JOB_TOKEN
RUN if [ -n "$CI_JOB_TOKEN" ]; then \
    git config --global url."https://gitlab-ci-token:${CI_JOB_TOKEN}@gitlab.com/".insteadOf "ssh://git@gitlab.com/"; \
    fi

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

COPY . .
RUN uv sync --frozen --no-dev
RUN uv run python -m compileall src

# Stage 2: Runtime (Dataflow Flex Template)
FROM gcr.io/dataflow-templates-base/python312-template-launcher-base:flex_templates_base_image_release_20260112_RC00

# Java 17 required for Kafka cross-language transforms
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/.venv/lib/python3.12/site-packages:/app:$PYTHONPATH"
ENV FLEX_TEMPLATE_PYTHON_PY_FILE="/app/src/main.py"
ENTRYPOINT ["/opt/apache/beam/boot"]
```

### Key Build Details

- **uv** -- Used instead of pip for fast, reproducible dependency resolution
- **`--frozen`** -- Ensures `uv.lock` is respected exactly (no resolution changes)
- **`--no-dev`** -- Excludes development dependencies from runtime image
- **Java 17** -- Required for Apache Beam Kafka cross-language transforms (SchemaTransform)
- **CI_JOB_TOKEN** -- GitLab CI token for pulling private Git dependencies (common-data-python)
- **Bytecode compilation** -- `compileall src` for faster startup

### Cloud Run (rewards-collector)

The rewards-collector uses a different pattern since it runs on Cloud Run, not Dataflow:
- FastAPI + uvicorn runtime
- No Java required (no Kafka)
- Standard HTTP health checks

---

## 7. Common Library

### common-data-python

| Property | Value |
|----------|-------|
| Package | `common-data-python` |
| Repository | `gitlab.com/The1central/The1/the1-data/common-data` |
| Subdirectory | `common-python` |
| Python | >= 3.12 |
| Build Backend | hatchling |

### Installation

Referenced as a Git dependency in `pyproject.toml`:
```toml
[tool.uv.sources]
common-data-python = {
    git = "ssh://git@gitlab.com/The1central/The1/the1-data/common-data.git",
    subdirectory = "common-python",
    tag = "0.0.9"
}
```

### What It Provides

```
common/
+-- __init__.py
+-- beam/
    +-- __init__.py
    +-- adapters/
        +-- input/
            +-- kafka_reader.py        # KafkaReaderConfig + Kafka cross-language transform
```

**Key class: `KafkaReaderConfig`**
- Kafka bootstrap servers
- Topic list
- Consumer group ID
- Message format (auto/json/avro)
- Confluent Schema Registry connection
- Authentication (API key + secret)

### Dependencies

```toml
dependencies = [
    "apache-beam[gcp]>=2.70.0",
    "confluent-kafka>=2.8.0",
    "confluent-kafka[avro]>=2.8.0",
    "confluent-kafka[schemaregistry]>=2.8.0",
]
```

### common-data-python-cloudrun

Separate package for Cloud Run services (rewards-collector):
```toml
common-data-python-cloudrun = {
    git = "ssh://git@gitlab.com/The1central/The1/the1-data/common-data.git",
    subdirectory = "common-python-cloudrun",
    tag = "0.0.10"
}
```

---

## 8. Key Patterns

### Bangkok Timezone (+7)

**CRITICAL:** All timestamps in both source (Iceberg) and refined (BigQuery) layers MUST use Bangkok timezone (UTC+7).

#### Source Layer (Iceberg)

```python
from datetime import datetime, timedelta, timezone

_BANGKOK_TZ = timezone(timedelta(hours=7))

# etlLoadTime as INT64 in YYYYMMDDHH format
etl_load_time = int(datetime.now(_BANGKOK_TZ).strftime("%Y%m%d%H"))
```

#### Refined Layer (BigQuery)

```python
from apache_beam.utils.timestamp import Timestamp

_BANGKOK_OFFSET_SECONDS = 7 * 3600
_BANGKOK_OFFSET_MICROS = _BANGKOK_OFFSET_SECONDS * 1_000_000

# Current time with Bangkok offset
etl_load_time = Timestamp(micros=Timestamp.now().micros + _BANGKOK_OFFSET_MICROS)

# Convert Unix timestamp to Bangkok
timestamp_val = Timestamp(seconds=unix_ts + _BANGKOK_OFFSET_SECONDS)

# ISO string to Bangkok Beam Timestamp
dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
bkk_ts = Timestamp.from_utc_datetime(dt.astimezone(datetime.UTC))
# Then add Bangkok offset to micros
```

### BigQuery Timestamp (MUST use Beam Timestamp)

**CRITICAL:** BigQuery Storage Write API RowCoder uses `MicrosInstant` which calls `value.micros`. You MUST use `apache_beam.utils.timestamp.Timestamp` -- NOT `datetime.datetime`.

```python
# CORRECT
from apache_beam.utils.timestamp import Timestamp
ts = Timestamp(seconds=unix_seconds)
ts = Timestamp(micros=unix_micros)
ts = Timestamp.now()
ts = Timestamp.from_utc_datetime(utc_aware_datetime)

# WRONG - will raise AttributeError: 'datetime' object has no attribute 'micros'
import datetime
ts = datetime.datetime.now()  # DO NOT use this for BQ writes
```

### Avro Unwrapping

Kafka messages from Confluent use Avro with union types. The common library handles this with `message_format: "auto"` in config:

1. Auto-detects Avro vs JSON format
2. Deserializes using Confluent Schema Registry
3. Unwraps union types (e.g., `{"string": "value"}` to `"value"`)

### etlLoadTime Pattern

- **Iceberg (source):** INT64, format YYYYMMDDHH (Bangkok time)
- **BigQuery (refined):** TIMESTAMP (Beam Timestamp with +7h offset baked in)
- **Partition:** `identity(etlLoadTime)` in Iceberg

### CDC Write Mode

```yaml
# base.yaml
refined:
  member_tier:
    write_mode: "append"

# prod.yaml (override)
refined:
  member_tier:
    write_mode: "cdc"
    primary_key: ["memberTierId"]
```

CDC mode uses BigQuery Storage Write API UPSERT:
- `.to_utc_datetime()` preserves the +7 offset baked into Timestamp micros
- Primary key defines the dedup key for UPSERT operations

### Job Types

| Type | Mode | Trigger | Use Case |
|------|------|---------|----------|
| `normal` | Streaming | Continuous (Kafka) | Real-time data ingestion |
| `initial_data` | Batch | GitLab CI (`TRIGGER_INIT_DATA_LOAD=1`) | Historical data load |

---

## 9. Dependencies

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `apache-beam[gcp,hadoop]` | 2.70.0 | Dataflow pipeline framework |
| `google-cloud-secret-manager` | >= 2.26.0 | Secret retrieval |
| `pyarrow` | >= 14.0.0, < 18.0.0 | Arrow/Parquet support |
| `pydantic` | >= 2.12.5 | Configuration validation |
| `common-data-python` | 0.0.9 (Git tag) | Shared library (Kafka reader) |

### Dev Dependencies

| Package | Purpose |
|---------|---------|
| `mypy` | Static type checking |
| `ruff` | Linting + formatting |
| `pytest` | Test framework |
| `pytest-cov` | Coverage reporting |
| `pytest-asyncio` | Async test support |
| `pre-commit` | Git hooks |
| `poethepoet` | Task runner |
| `pyiceberg[pyarrow,sql-sqlite]` | Iceberg testing utilities |
| `types-pyyaml` | PyYAML type stubs |

### Version Constraints

- **Python:** >= 3.12
- **PyArrow:** Must be < 18.0.0 (Beam compatibility)
- **Beam:** Fixed at 2.70.0 (all collectors aligned)

---

## 10. Local Development Setup

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (fast Python package manager)
- Java 17 JRE (for Kafka cross-language transforms in integration tests)

### Initial Setup

```bash
# Clone the repository
# (example for loyalty-data)
cd loyalty-data/members-collector

# Install all dependencies (including dev)
uv sync

# Verify installation
uv run python -c "import apache_beam; print(apache_beam.__version__)"
```

### Development Workflow

```bash
# 1. Make code changes

# 2. Run quality checks
uv run ruff check --fix .
uv run ruff format .
uv run mypy src tests

# 3. Run tests
uv run pytest -v

# 4. Run pre-commit hooks
uv run pre-commit run --all-files

# 5. Verify all pass before pushing
```

### IDE Setup

For VS Code or PyCharm, point the Python interpreter to the `.venv` created by uv:
```
.venv/bin/python
```

Recommended VS Code extensions:
- Python (Microsoft)
- Ruff (astral-sh)
- mypy Type Checker

### Environment Variables (for local testing)

```bash
# GCP project (for integration tests)
export GOOGLE_CLOUD_PROJECT=the1-loyalty-data-stg

# Logging
export LOG_LEVEL=DEBUG
```

### Running Pipeline Locally (DirectRunner)

```bash
uv run python src/main.py \
    --runner DirectRunner \
    --dataflow_config $(base64 < config/stg.yaml)
```

Note: Local runs require access to external services (Kafka, GCP). Use mocks for unit tests.

---

## 11. Workflow Checklist

### Before Making Code Changes

- [ ] Read the existing code (do not guess)
- [ ] Check `memory/mistakes_and_rules.md` for known pitfalls
- [ ] Understand which collector(s) are affected

### After Making Code Changes

- [ ] `uv sync` -- Ensure dependencies are synchronized
- [ ] `uv run ruff check --fix .` -- Fix lint issues
- [ ] `uv run ruff format .` -- Format code
- [ ] `uv run mypy src tests` -- Type check passes
- [ ] `uv run pytest` -- All tests pass
- [ ] `uv run pre-commit run --all-files` -- All hooks pass

### Common Mistakes to Avoid

| Mistake | Correct Approach |
|---------|-----------------|
| Using `datetime.datetime` for BQ writes | Use `apache_beam.utils.timestamp.Timestamp` |
| Forgetting Bangkok +7 offset | Always apply `_BANGKOK_OFFSET_SECONDS` or `_BANGKOK_TZ` |
| Modifying `transactions-collector` directly | Coordinate with other team first |
| Modifying `purchases-collector` | Reference only (read-only) |
| Using non-raw regex strings | Use `r"pattern"` to avoid Ruff RUF043 |
| Skipping `uv sync` after dependency changes | Always run `uv sync` first |
| Creating Iceberg tables with `create_table` | Use `register_table` (preserves field IDs + partition spec) |
| Assuming UTC timestamps | All timestamps must be Bangkok (+7) |
