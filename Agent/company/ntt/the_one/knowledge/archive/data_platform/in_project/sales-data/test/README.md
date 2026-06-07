# Test Architecture — Sales-Collector

[< Back to Sales-Collector Docs](../README.md) | [General Test Architecture](../../../test/README.md)

---

## High-Level Test Overview

```mermaid
graph LR
    subgraph "Unit Tests (6 files, ~110 tests)"
        DOM["Domain<br/>3 files"]
        PIPE["Pipeline<br/>1 file"]
        ADAPT["Adapters<br/>2 files"]
    end

    subgraph "Quality Gates"
        RUFF["ruff check + format"]
        MYPY["mypy (strict)"]
        PYTEST["pytest -v"]
        COV["coverage (HTML+XML)"]
    end

    DOM --> PYTEST
    PIPE --> PYTEST
    ADAPT --> PYTEST
    RUFF --> CI["CI: linter job"]
    MYPY --> CI
    PYTEST --> CI2["CI: test job"]
    COV --> CI2
    CI2 --> SONAR["SonarQube"]
```

### Test File Map

```
tests/
├── conftest.py                                        # 4 shared fixtures
└── unit/
    ├── adapters/
    │   ├── input/configuration/
    │   │   └── test_settings.py                      # DataflowConfigDto (Pydantic v2)
    │   └── output/bigquery/
    │       └── test_bigquery_writer_config.py         # BigQueryWriterConfig (dataclass)
    ├── domain/
    │   ├── test_transformers.py                       # Core: extract, decode, attach, build
    │   ├── test_bq_transformers.py                    # Fan-out: receipt, sku, tender rows
    │   └── test_validators.py                         # Input validation helpers
    └── pipeline/
        └── test_dofns.py                             # Beam DoFns via TestPipeline
```

---

## Detailed Test Architecture

### Layer-by-Layer Coverage

```mermaid
flowchart TB
    subgraph "Domain Layer (3 files)"
        T_TRANS["test_transformers.py<br/>6 test classes, ~20 tests<br/>extract_value, safe_decode_and_parse,<br/>attach_event_name, build_raw_event,<br/>is_avro_message, etl_load_time"]
        T_BQ["test_bq_transformers.py<br/>9 test classes, ~40 tests<br/>unwrap_avro, parse_timestamp/numeric,<br/>to_receipt/sku/tender_row,<br/>Kafka field names (Excel spec)"]
        T_VAL["test_validators.py<br/>5 test classes, ~15 tests<br/>require_non_empty_str,<br/>require_positive_int, etc."]
    end

    subgraph "Pipeline Layer (1 file)"
        T_DOFN["test_dofns.py<br/>4 test classes, ~8 tests<br/>ExtractValue, DecodeParse,<br/>AttachEventName, BuildRawEvent<br/>Beam TestPipeline + DirectRunner"]
    end

    subgraph "Adapter Layer (2 files)"
        T_SET["test_settings.py<br/>3 test classes, ~20 tests<br/>DataflowConfigDto validation,<br/>WriteMode, RefinedTableConfig"]
        T_BQC["test_bigquery_writer_config.py<br/>1 test class, ~5 tests<br/>BigQueryWriterConfig __post_init__"]
    end

    subgraph "Not Yet Tested"
        NT1["configuration_adapter.py"]
        NT2["secret_adapter.py"]
        NT3["logging_adapter.py"]
        NT4["gcs_biglake_iceberg_writer.py"]
        NT5["biglake_metastore_config.py"]
        NT6["gcs_biglake_iceberg_writer_config.py"]
        NT7["builder.py (PipelineBuilder)"]
        NT8["main.py"]
    end

    style NT1 fill:#fff3e0,stroke:#e65100
    style NT2 fill:#fff3e0,stroke:#e65100
    style NT3 fill:#fff3e0,stroke:#e65100
    style NT4 fill:#fff3e0,stroke:#e65100
    style NT5 fill:#fff3e0,stroke:#e65100
    style NT6 fill:#fff3e0,stroke:#e65100
    style NT7 fill:#fff3e0,stroke:#e65100
    style NT8 fill:#fff3e0,stroke:#e65100
```

---

## Fixture Architecture

```mermaid
graph TB
    subgraph "conftest.py (tests/ root)"
        SKP["sample_kafka_payload<br/>Full Kafka event dict<br/>Schema B with receiptNo,<br/>1 item, 1 tender"]
        SIE["sample_intermediate_event<br/>IntermediateEvent wrapping payload"]
        SRE["sample_raw_event<br/>RawEvent with JSON-serialized payload<br/>etlLoadTime=2026022215"]
        SAWP["sample_avro_wrapped_payload<br/>All fields Avro-union wrapped<br/>{'string':'...'}, {'array':[...]}"]

        SKP --> SIE
        SKP --> SRE
    end

    subgraph "In-file helpers (not fixtures)"
        MRE["_make_raw_event(payload)<br/>Quick RawEvent factory"]
        KSP["_kafka_sample_payload()<br/>Realistic Excel-spec Kafka data"]
        VCF["_valid_config()<br/>Minimal valid DataflowConfigDto dict"]
        RTB["_refined_table(table, **overrides)<br/>RefinedTableConfig dict builder"]
    end

    SRE --> T_BQ_USE["test_bq_transformers.py<br/>TestToReceiptRow<br/>TestToSkuRows<br/>TestToTenderRows"]
    SAWP --> T_BQ_USE

    MRE --> T_BQ_USE
    KSP --> T_KAFKA["TestKafkaFieldNames<br/>(Excel spec verification)"]
    VCF --> T_SET_USE["test_settings.py<br/>TestDataflowConfigDto"]
    RTB --> T_SET_USE
```

### Fixture Data Flow

```mermaid
flowchart LR
    subgraph "sample_kafka_payload"
        KP_STRUCT["dict with:<br/>eventName, source, eventId,<br/>timestamp=time.time(),<br/>payload.receiptNo='RCP-001',<br/>payload.items[1],<br/>payload.tenders[1]"]
    end

    subgraph "sample_raw_event"
        RE_STRUCT["RawEvent(<br/>eventId='evt-001',<br/>source='pos-system',<br/>eventName='loyalty.sales.created',<br/>payload=json.dumps(inner),<br/>etlLoadTime=2026022215<br/>)"]
    end

    KP_STRUCT -->|"json.dumps(payload)"| RE_STRUCT
    RE_STRUCT -->|"to_receipt_row()"| RECEIPT["1 receipt row"]
    RE_STRUCT -->|"to_sku_rows()"| SKU["N SKU rows"]
    RE_STRUCT -->|"to_tender_rows()"| TENDER["M tender rows"]
```

---

## Test Pattern Details

### Pattern 1: Pure Domain Function Tests (no mocks, no Beam)

```mermaid
flowchart LR
    INPUT["Hardcoded dict<br/>or fixture"] --> FUNC["transformers.func()"]
    FUNC --> CHECK{"Return value"}
    CHECK -->|"Valid"| ASSERT_EQ["assert == expected"]
    CHECK -->|"Invalid input"| ASSERT_NONE["assert is None"]
    CHECK -->|"Error case"| RAISES["pytest.raises(TypeError/ValueError)"]
```

**Example — `test_transformers.py`:**

| Test Class | Function Tested | # Tests | Key Assertions |
|-----------|----------------|:---:|----------------|
| `TestIsAvroMessage` | `is_avro_message(bytes)` | 4 | Magic byte `\x00` + 4-byte schema ID detection |
| `TestExtractValue` | `extract_value(record)` | 7 | Tuple/list/dict/bytes unwrapping, TypeError/ValueError on bad input |
| `TestSafeDecodeAndParse` | `safe_decode_and_parse(bytes)` | 3 | JSON parse success, invalid→None, string input support |
| `TestAttachEventName` | `attach_event_name(dict)` | 2 | Attach eventName, default fallback |
| `TestIsWrappedEvent` | `_is_wrapped_event(dict)` | 4 | Schema B detection: eventId + inner payload dict |
| `TestBuildRawEvent` | `build_raw_event(dict)` | 6 | Schema B→RawEvent, Schema A→None, missing/non-dict payload→None |
| `TestGetEtlLoadTimeBangkok` | `_get_etl_load_time_bangkok()` | 1 | Returns 10-digit int (YYYYMMDDHH) |

### Pattern 2: BQ Transformer Tests (fixtures + helpers)

```mermaid
flowchart TB
    subgraph "Two Data Sources"
        LEGACY["conftest fixtures<br/>Legacy camelCase<br/>(receiptNo, transType)"]
        KAFKA["_kafka_sample_payload()<br/>Current Kafka names<br/>(receiptNumber, saleTypeCode)"]
    end

    subgraph "Transformers Under Test"
        RECEIPT["to_receipt_row()"]
        SKU["to_sku_rows()"]
        TENDER["to_tender_rows()"]
    end

    subgraph "Assertions"
        FIELD["Field mapping correct<br/>receipt_no == 'RCP-001'"]
        TYPE["Type conversion correct<br/>isinstance(trans_date, Timestamp)<br/>net_price_tot == Decimal('1500.50')"]
        COUNT["Row count correct<br/>len(rows) == N"]
        EMPTY["Empty input → [] or {}"]
    end

    LEGACY --> RECEIPT
    LEGACY --> SKU
    LEGACY --> TENDER
    KAFKA --> RECEIPT
    KAFKA --> SKU
    KAFKA --> TENDER

    RECEIPT --> FIELD
    RECEIPT --> TYPE
    SKU --> COUNT
    TENDER --> EMPTY
```

**Example — `test_bq_transformers.py`:**

| Test Class | Function Tested | # Tests | Key Assertions |
|-----------|----------------|:---:|----------------|
| `TestUnwrapAvroValue` | `unwrap_avro_value` | 5 | `{"string":"x"}`→`"x"`, None→None, multi-key passthrough |
| `TestUnwrapAvroArray` | `unwrap_avro_array` | 4 | `{"array":[...]}`→`[...]`, None→`[]` |
| `TestParseTimestamp` | `_parse_timestamp` | 5 | Unix seconds, millis (>1e12), Avro-wrapped, None, invalid |
| `TestParseNumeric` | `_parse_numeric` | 5 | int→Decimal, string→Decimal, Avro→Decimal, None, invalid |
| `TestSafeStr` | `_safe_str` | 4 | String, Avro, None, empty→None |
| `TestExtractSalesPayload` | `_extract_sales_payload` | 3 | Nested payload, flat, invalid JSON |
| `TestExtractHeaderFields` | `_extract_header_fields` | 2 | CamelCase mapping, missing→None |
| `TestToReceiptRow` | `to_receipt_row` | 2 | Full row extraction, empty payload→`{}` |
| `TestToSkuRows` | `to_sku_rows` | 4 | Items extraction, Avro-wrapped, no items→`[]`, multiple |
| `TestToTenderRows` | `to_tender_rows` | 4 | Tenders extraction, Avro-wrapped, no tenders→`[]`, multiple |
| `TestKafkaFieldNames` | All 3 extractors | 7 | Real Kafka names from Excel spec, void info, isAll bool→Y/N |

### Pattern 3: Beam TestPipeline DoFn Tests

```mermaid
flowchart LR
    subgraph "TestPipeline Pattern"
        CREATE["p | beam.Create([input])"]
        PARDO["| beam.ParDo(DoFn())"]
        ASSERT["assert_that(output, matcher)"]
    end

    subgraph "Matchers Used"
        EQ["equal_to([expected])<br/>Exact match"]
        EMPTY["equal_to([])<br/>Element dropped"]
        NE["is_not_empty()<br/>Loose — something produced"]
    end

    CREATE --> PARDO --> ASSERT
    ASSERT --> EQ
    ASSERT --> EMPTY
    ASSERT --> NE
```

**Example — `test_dofns.py`:**

| Test Class | DoFn | # Tests | Valid Input Matcher | Invalid Input Matcher |
|-----------|------|:---:|-----|------|
| `TestExtractValueDoFn` | `ExtractValueDoFn` | 3 | `equal_to([b"value"])` | `equal_to([])` (dropped) |
| `TestDecodeParseDoFn` | `DecodeParseDoFn` | 2 | `equal_to([{"key":"value"}])` | `equal_to([])` (dropped) |
| `TestAttachEventNameDoFn` | `AttachEventNameDoFn` | 1 | `is_not_empty()` | — |
| `TestBuildRawEventDoFn` | `BuildRawEventDoFn` | 2 | `is_not_empty()` | `equal_to([])` (Schema A dropped) |

**DoFn chaining in tests:**
```python
# BuildRawEvent requires AttachEventName first
output = (
    p
    | beam.Create(input_data)
    | beam.ParDo(AttachEventNameDoFn())
    | beam.ParDo(BuildRawEventDoFn())
)
assert_that(output, is_not_empty())
```

### Pattern 4: Pydantic Model Validation Tests

```mermaid
flowchart TB
    subgraph "Builder Pattern"
        VALID["_valid_config() → dict<br/>All required fields present"]
    end

    subgraph "Test Variations"
        DEL["del data['field']<br/>→ pytest.raises(ValueError)"]
        BAD["data['field'] = bad_value<br/>→ pytest.raises(ValueError)"]
        CUSTOM["data['field'] = custom<br/>→ assert cfg.field == custom"]
        EXTRA["data['unknown'] = val<br/>→ pytest.raises (extra=forbid)"]
        DEFAULT["no override<br/>→ assert cfg.field == default"]
    end

    VALID --> DEL
    VALID --> BAD
    VALID --> CUSTOM
    VALID --> EXTRA
    VALID --> DEFAULT
```

**Example — `test_settings.py`:**

| Test Class | Model | # Tests | Key Validations |
|-----------|-------|:---:|-----------------|
| `TestDataflowConfigDto` | `DataflowConfigDto` | 17 | Required fields, empty lists, invalid enums, extra fields forbidden, kafka_topics↔iceberg_tables cross-validation |
| `TestWriteMode` | `WriteMode` enum + config | 4 | append/cdc modes, CDC requires primary_key |
| `TestRefinedTableConfig` | `RefinedTableConfig` | 4 | Partitioning, clustering, custom trigger freq, defaults |

### Pattern 5: Dataclass Post-Init Validation Tests

```mermaid
flowchart LR
    CTOR["BigQueryWriterConfig(<br/>project_id='', ...)"] --> POST["__post_init__"]
    POST --> RAISE["pytest.raises(ValueError,<br/>match='project_id')"]

    CTOR2["BigQueryWriterConfig(<br/>project_id='ok', ...)"] --> POST2["__post_init__"]
    POST2 --> OK["assert cfg.write_disposition == 'WRITE_APPEND'"]
```

---

## Type Conversion Test Coverage

```mermaid
flowchart TB
    subgraph "Timestamp Parsing Tests"
        TS1["Unix seconds (1700000000)<br/>→ Timestamp (+7h)"]
        TS2["Unix millis (1700000000000)<br/>→ Timestamp (÷1000 +7h)"]
        TS3["Avro wrapped {'long': ...}<br/>→ unwrap → Timestamp"]
        TS4["None → None"]
        TS5["Invalid string → None"]
    end

    subgraph "Numeric Parsing Tests"
        NUM1["int (100) → Decimal('100')"]
        NUM2["string ('99.99') → Decimal('99.99')"]
        NUM3["Avro {'string':'50.25'} → Decimal"]
        NUM4["None → None"]
        NUM5["Invalid ('abc') → None"]
    end

    subgraph "String Parsing Tests"
        STR1["'hello' → 'hello'"]
        STR2["Avro {'string':'world'} → 'world'"]
        STR3["None → None"]
        STR4["'' → None"]
    end
```

---

## Running Tests

```bash
# All tests
cd sales-collector && uv run pytest

# With coverage
uv run poe test:cov

# Unit only
uv run poe test:unit

# Specific file
uv run pytest tests/unit/domain/test_bq_transformers.py -v

# Specific class
uv run pytest tests/unit/domain/test_bq_transformers.py::TestKafkaFieldNames -v

# Full quality check
uv run poe lint          # ruff format + ruff check + mypy
uv run poe test:cov      # pytest + coverage
```

### CI Quality Gate Flow

```mermaid
flowchart LR
    LINT["linter job<br/>ruff check .<br/>ruff format --check .<br/>mypy ."]
    TEST["test job<br/>uv run poe test:cov"]
    IMAGE["create-image"]
    SONAR["sonar-scan<br/>coverage.xml"]

    LINT --> TEST
    TEST --> IMAGE
    TEST --> SONAR
```

---

## Coverage Summary by Module

| Module | Test File | Coverage Level |
|--------|-----------|:-:|
| `domain/transformers.py` | `test_transformers.py` | High |
| `domain/bq_transformers.py` | `test_bq_transformers.py` | High |
| `domain/validators.py` | `test_validators.py` | High |
| `domain/models.py` | (via other tests) | Indirect |
| `domain/schemas.py` | (via bq_transformer tests) | Indirect |
| `domain/config/pipeline_config.py` | — | None |
| `domain/config/bigquery_sales_config.py` | — | None |
| `adapters/input/configuration/settings.py` | `test_settings.py` | High |
| `adapters/input/configuration/configuration_adapter.py` | — | None |
| `adapters/input/configuration/secret_adapter.py` | — | None |
| `adapters/input/configuration/logging_adapter.py` | — | None |
| `adapters/output/bigquery/bigquery_writer_config.py` | `test_bigquery_writer_config.py` | High |
| `adapters/output/bigquery/bigquery_writer.py` | — | None |
| `adapters/output/gcs/biglake_metastore_config.py` | — | None |
| `adapters/output/gcs/gcs_biglake_iceberg_writer_config.py` | — | None |
| `adapters/output/gcs/gcs_biglake_iceberg_writer.py` | — | None |
| `application/pipeline/dofns.py` | `test_dofns.py` | High |
| `application/pipeline/builder.py` | — | None |
| `main.py` | — | None |
