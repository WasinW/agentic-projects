# Test Architecture — Data Platform Collectors

> **Scope:** All collectors: members, tiers, members-tiers-history, purchases (loyalty), sales (sales-data)
> **Last Updated:** 2026-02-22

---

## High-Level Test Architecture

```mermaid
graph TB
    subgraph "Test Pyramid"
        UNIT["Unit Tests<br/>All collectors — 100% coverage target"]
        INT["Integration Tests<br/>purchases-collector only<br/>(TestStream + DirectRunner)"]
        E2E["E2E / Manual<br/>Dataflow STG environment"]

        E2E --> INT --> UNIT
    end

    subgraph "Test Categories"
        DOM["Domain Tests<br/>transformers, schemas, validators<br/>Pure Python — no mocks"]
        PIPE["Pipeline Tests<br/>DoFns, PTransforms<br/>Beam TestPipeline or direct .process()"]
        ADAPT["Adapter Tests<br/>config, secrets, writers<br/>unittest.mock patches"]
    end

    UNIT --- DOM
    UNIT --- PIPE
    UNIT --- ADAPT
```

---

## Test Structure Per Collector

All collectors follow identical directory layout:

```
{collector}/tests/
├── __init__.py
├── conftest.py                          # Root fixtures (domain-specific sample data)
├── integration/                         # Integration tests (mostly empty/placeholder)
│   └── pipeline/
└── unit/
    ├── adapters/
    │   ├── input/
    │   │   └── configuration/           # Settings, ConfigAdapter, Logging, Secret
    │   └── output/                      # BigQuery, Iceberg sinks
    ├── domain/                          # Transformers, schemas, validators
    └── pipeline/                        # DoFns, PipelineBuilder
```

### Test File Count by Collector

| Layer | members | tiers | m-t-h | purchases | sales |
|-------|:---:|:---:|:---:|:---:|:---:|
| adapters/input | 6 | 5 | 5 | 4 | 1 |
| adapters/output | 3 | 3 | 3 | 2 | 1 |
| domain | 2 | 2 | 1 | 4 | 3 |
| pipeline | 3 | 2 | 0 | 1 | 1 |
| integration | 0 | 0 | 0 | 1 | 0 |
| **Total** | **14** | **12** | **9** | **12** | **6** |

---

## Test Toolchain

```mermaid
flowchart LR
    subgraph "Quality Gates"
        RUFF["ruff check + format<br/>Linting & formatting"]
        MYPY["mypy<br/>Static type checking"]
        PYTEST["pytest<br/>Unit + integration tests"]
        COV["pytest-cov<br/>Coverage (HTML + XML)"]
        PC["pre-commit<br/>Runs per-collector on file change"]
    end

    subgraph "CI Pipeline"
        LINT_CI["sales-collector:linter<br/>ruff + mypy"]
        TEST_CI["sales-collector:test<br/>poe test:cov"]
        SONAR["sonar-scan<br/>coverage.xml ingestion"]
    end

    RUFF --> LINT_CI
    MYPY --> LINT_CI
    PYTEST --> TEST_CI
    COV --> TEST_CI
    TEST_CI --> SONAR

    PC -.->|"local dev"| RUFF
    PC -.->|"local dev"| PYTEST
```

### Shared Configuration (all collectors)

```toml
# pyproject.toml — pytest
[tool.pytest.ini_options]
addopts = "-v"
testpaths = ["tests"]
pythonpath = ["."]       # or ["src"]

# pyproject.toml — poethepoet tasks
[tool.poe.tasks]
test       = "pytest"
"test:cov" = "pytest --cov=src --cov-report=html --cov-report=xml:coverage.xml"
"test:unit" = "pytest tests/unit"
lint       = ["format", "check", "typecheck"]   # sequential chain
```

### Pre-commit Hooks (workspace level)

```mermaid
flowchart TB
    COMMIT["git commit"] --> PC["pre-commit"]
    PC --> GITLEAKS["gitleaks<br/>Secret scanning"]
    PC --> GITLAB_CI["check-gitlab-ci<br/>YAML schema validation"]

    PC --> LINT1["lint-{collector}<br/>uv run poe lint"]
    PC --> TEST1["pytest-{collector}<br/>uv run poe test"]

    LINT1 -->|"only if files changed<br/>in that collector"| RUFF_FMT["ruff format ."]
    RUFF_FMT --> RUFF_CHK["ruff check --fix ."]
    RUFF_CHK --> MYPY_RUN["mypy ."]

    style GITLEAKS fill:#ffe0e0
    style GITLAB_CI fill:#e0f0ff
```

Each collector has its own `lint-{collector}` and `pytest-{collector}` hook with `files: ^{collector}/` filter and `pass_filenames: false`.

---

## Detailed Test Patterns

### 1. Domain Tests — Pure Python Functions

```mermaid
flowchart LR
    INPUT["Test data<br/>(dict / fixture)"] --> FUNC["Pure function<br/>transformers.py<br/>bq_transformers.py"]
    FUNC --> ASSERT["assert ==<br/>assert isinstance<br/>assert is None"]
```

**Pattern:** Direct function call → assert return value. No mocking, no Beam runtime.

```python
class TestBuildRawEvent:
    def test_schema_b_extracts_wrapper_fields(self):
        payload = {"eventId": "e1", "source": "pos", "timestamp": 1700000000,
                   "payload": {"receiptNo": "R1"}}
        result = build_raw_event(payload)
        assert result["eventId"] == "e1"
        assert result["source"] == "pos"
```

**Tested modules:** `transformers.py`, `bq_transformers.py`, `validators.py`, `schemas.py`

**Private function testing:** Tests import and test `_`-prefixed functions directly:
```python
from src.domain.bq_transformers import _parse_timestamp, _safe_str, _extract_header_fields
```

---

### 2. DoFn Tests — Two Approaches

```mermaid
flowchart TB
    subgraph "Approach A: Direct .process() (loyalty collectors)"
        DOFN_A["dofn = MyDoFn()"]
        MOCK_A["_mock_metrics(dofn)<br/>dofn._seen = MagicMock()"]
        CALL_A["results = list(dofn.process(element))"]
        ASSERT_A["assert len(results) == 1<br/>assert results[0]['field'] == value"]
        DOFN_A --> MOCK_A --> CALL_A --> ASSERT_A
    end

    subgraph "Approach B: Beam TestPipeline (sales, purchases)"
        PIPE_B["with TestPipeline() as p:"]
        CREATE_B["p | beam.Create([input])"]
        PARDO_B["| beam.ParDo(MyDoFn())"]
        ASSERT_B["assert_that(output, equal_to([...]))<br/>assert_that(output, is_not_empty())"]
        PIPE_B --> CREATE_B --> PARDO_B --> ASSERT_B
    end
```

**Approach A** — Loyalty collectors (members, tiers, m-t-h):
- Call `dofn.process(element)` directly, collect results with `list()`
- Must mock Beam metric counters (`_seen`, `_ok`, `_errors`) because no Beam runtime
- Faster execution, fine-grained assertions

**Approach B** — Sales-collector, purchases-collector DoFn tests:
- Use `with TestPipeline() as p:` context manager (DirectRunner)
- Use `beam.testing.util.assert_that` with matchers: `equal_to([...])`, `is_not_empty()`
- Dropped elements verified with `equal_to([])`
- Runs full Beam pipeline (slower but more realistic)

---

### 3. Adapter Tests — Mock External Dependencies

```mermaid
flowchart LR
    subgraph "Mocking Targets"
        SECRET["SecretAdapter<br/>GCP Secret Manager"]
        AUTH["google.auth.default<br/>GCP credentials"]
        CATALOG["RestCatalog<br/>PyIceberg"]
        WRITER["write_to_iceberg<br/>Beam managed.Write"]
        BQ["WriteToBigQuery<br/>Beam BQ sink"]
    end

    subgraph "Mock Method"
        PATCH["@patch('module.path.Class')"]
        MAGIC["MagicMock()"]
        FIXTURE["@pytest.fixture → yield mock"]
    end

    PATCH --> SECRET
    PATCH --> AUTH
    PATCH --> CATALOG
    PATCH --> WRITER
    MAGIC --> BQ
```

**Pattern — PTransform sink delegation:**
```python
@patch("src.adapters.output.iceberg_sink.write_to_iceberg")
def test_delegates_to_write(self, mock_write: MagicMock):
    sink = IcebergSink(config=config, schema=SCHEMA, row_mapper=mapper)
    mock_pcoll = MagicMock()
    sink.expand(mock_pcoll)
    mock_write.assert_called_once_with(pcoll=mock_pcoll, config=config, ...)
```

**Pattern — Config adapter with Secret Manager:**
```python
@pytest.fixture
def mock_secret_adapter(self) -> Generator:
    with mock.patch("...configuration_adapter.SecretAdapter") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        yield mock_instance
```

---

### 4. Pydantic / Dataclass Validation Tests

```mermaid
flowchart LR
    VALID["_valid_config() → dict"] --> MODEL["Model.model_validate(data)"]
    MODEL --> OK["assert result.field == expected"]

    INVALID["del data['required_field']<br/>data['field'] = bad_value"] --> MODEL2["Model.model_validate(data)"]
    MODEL2 --> RAISES["pytest.raises(ValueError, match='field')"]
```

**Pattern — Pydantic v2 model testing:**
```python
def _valid_config() -> dict:
    return {"project": "my-project", "secret_name": "my-secret", ...}

class TestDataflowConfigDto:
    def test_valid(self):
        cfg = DataflowConfigDto.model_validate(_valid_config())
        assert cfg.project == "my-project"

    def test_missing_project_raises(self):
        data = _valid_config()
        del data["project"]
        with pytest.raises(ValueError, match="project"):
            DataflowConfigDto.model_validate(data)
```

**Pattern — Dataclass `__post_init__` validation:**
```python
def test_empty_project_id_raises(self):
    with pytest.raises(ValueError, match="project_id"):
        BigQueryWriterConfig(project_id="", dataset_id="refined", table_id="tbl")
```

---

### 5. Integration Tests (purchases-collector only)

```mermaid
flowchart TB
    subgraph "Integration Test Setup"
        TS["TestStream<br/>Synthetic Kafka records"]
        FAKE_K["FakeKafkaReader<br/>Custom PTransform"]
        FAKE_S["FakeOutputSink<br/>Captures output"]
        OPT["PipelineOptions<br/>--runner=DirectRunner<br/>--streaming"]
    end

    subgraph "Execution"
        BUILDER["PipelineBuilder(options, config,<br/>kafka_reader=fake, ...)"]
        RUN["builder.run()"]
    end

    TS --> FAKE_K --> BUILDER
    FAKE_S --> BUILDER
    OPT --> BUILDER
    BUILDER --> RUN
    RUN --> VERIFY["VerifyingSink<br/>assert_that()"]
```

This is the only collector with actual integration tests. Uses DirectRunner with `--streaming` to simulate real Dataflow behavior.

---

## Fixture Architecture

### Shared Fixtures (conftest.py at tests/ root)

```mermaid
graph TB
    subgraph "sales-collector"
        SKP["sample_kafka_payload<br/>Full Kafka message dict"]
        SIE["sample_intermediate_event<br/>depends on sample_kafka_payload"]
        SRE["sample_raw_event<br/>depends on sample_kafka_payload"]
        SAWP["sample_avro_wrapped_payload<br/>Independent — Avro union fields"]
        SKP --> SIE
        SKP --> SRE
    end

    subgraph "loyalty collectors"
        SMTP["sample_member_tier_payload<br/>(members)"]
        STAR["sample_tiers_api_response<br/>(tiers)"]
        SDBS["sample_db_secrets<br/>(m-t-h)"]
    end

    subgraph "purchases-collector"
        MSA["mock_secret_adapter<br/>@patch SecretAdapter"]
        SPKP["sample_kafka_payload"]
        SPIE["sample_intermediate_event"]
        LPCE["loyalty_purchases_created_event_payload"]
    end
```

### Local Test Helpers (in-file, not fixtures)

Pattern used across collectors — module-level helper functions:

```python
# In test files (not conftest)
def _make_raw_event(payload: dict) -> RawEvent:
    return RawEvent(eventId="test-id", source="test", ...)

def _valid_config() -> dict:
    return {"project": "test", ...}

def _mock_metrics(dofn: Any) -> None:
    dofn._seen = MagicMock()
    dofn._ok = MagicMock()
    dofn._errors = MagicMock()
```

---

## Bangkok Timezone Testing

All collectors verify +7h offset handling:

```mermaid
flowchart LR
    UTC["UTC unix timestamp<br/>1700000000"] -->|"+7h (25200s)"| BKK["Bangkok Timestamp<br/>Timestamp(seconds=1700025200)"]
    BKK --> ASSERT["assert isinstance(result, Timestamp)<br/>assert result.seconds() == unix + 25200"]

    NOW["Timestamp.now()"] -->|"+7h micros"| ETL["etl_updated_date<br/>Timestamp(micros=now + 25200000000)"]
    ETL --> ASSERT2["assert isinstance(result, Timestamp)"]
```

**Key assertion:** All TIMESTAMP fields must be `apache_beam.utils.timestamp.Timestamp`, NOT `datetime.datetime`.

---

## Coverage Gaps (Common Across Collectors)

| Module | Typically Tested | Notes |
|--------|:---:|-------|
| `domain/transformers.py` | Yes | Pure functions, thorough |
| `domain/bq_transformers.py` | Yes | Field mappings, type conversions |
| `domain/validators.py` | Yes | Validation edge cases |
| `domain/schemas.py` | Partial | Schema structure, not content |
| `adapters/input/configuration/settings.py` | Yes | Pydantic validation |
| `adapters/input/configuration/configuration_adapter.py` | Yes (loyalty) / No (sales) | Secret Manager mocked |
| `adapters/output/iceberg_sink.py` | Yes (loyalty) / No (sales) | Delegation mocked |
| `adapters/output/bigquery_writer.py` | Partial | Config tested, writer mocked |
| `application/pipeline/builder.py` | No (all) | Complex wiring — integration-level |
| `main.py` | No (all) | Entry point — E2E level |
