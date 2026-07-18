# Processing Instructions

> AI: Read this file when writing Beam DoFns, transforms, CDC logic, fan-out patterns, or payload extraction.

## Quick Reference

```
DoFn Chain (streaming):
  ExtractValueDoFn → DecodeParseDoFn → AttachEventNameDoFn → BuildRawEventDoFn
    → [domain-specific] ExtractPayloadDoFn → Write

Fan-Out Pattern:
  merged_raw → ExtractMemberIdAndTierCodeDoFn → (member_id, tier_code, tier_event_id)
    ├─ Branch 1: Map → Dedup → FetchMemberTierDoFn → ExtractMemberTierPayloadDoFn → Write
    └─ Branch 2: Map → Dedup → FetchTierMaintenanceDoFn → ExtractTierMaintenancePayloadDoFn → Write

CDC Pattern:
  element["_is_delete"] = True → _WrapCdcRowDoFn → mutation_type: "DELETE"
```

---

## 1. DoFn Patterns

### Standard DoFn Template

```python
class MyDoFn(beam.DoFn):
    """What this DoFn does."""

    def __init__(self, param: str) -> None:
        self._param = param
        # Store config only — NO external clients here

    def setup(self) -> None:
        """Called once per worker. Initialize API clients here."""
        self._client = SomeApiClient(self._param)
        self._counter_seen = Metrics.counter("my_dofn", "seen")
        self._counter_ok = Metrics.counter("my_dofn", "ok")
        self._counter_errors = Metrics.counter("my_dofn", "errors")

    def start_bundle(self) -> None:
        """Called at start of each bundle. Reset per-bundle state."""
        self._seen: set[str] = set()

    def process(self, element: dict[str, Any]) -> Iterator[dict[str, Any]]:
        self._counter_seen.inc()
        try:
            result = self._transform(element)
            self._counter_ok.inc()
            yield result
        except Exception as e:
            self._counter_errors.inc()
            logger.warning("Failed to process: %s", e)
            # Drop record — no DLQ yet

    def teardown(self) -> None:
        """Called once per worker shutdown. Cleanup resources."""
        if self._client:
            self._client.close()
```

### Key Rules

| Rule | Why |
|------|-----|
| API clients in `setup()`, NOT `__init__()` | DoFns are serialized across workers; clients can't be pickled |
| Metrics counters in `setup()` | Counter objects need worker context |
| Per-bundle state in `start_bundle()` | Reset sets/caches for each bundle |
| `yield` (not `return`) in `process()` | Allows multiple outputs per input |
| Handle errors with log + drop | Prevents pipeline crash from bad records |

---

## 2. Pipeline DAG Construction (builder.py)

### Streaming Pipeline (members-collector)

```python
def _build_streaming_pipeline(self):
    with beam.Pipeline(options=self.options) as p:
        all_raw_events = []

        # Per-topic branch: Kafka → RAW Iceberg
        for topic in self.config.kafka_config.topics:
            raw_events = (
                p
                | f"ReadFromKafka_{topic}" >> ReadFromKafka(consumer_config, [topic])
                | f"ExtractValue_{topic}" >> beam.ParDo(ExtractValueDoFn())
                | f"Decode_{topic}" >> beam.ParDo(DecodeParseDoFn())
                | f"Window_{topic}" >> beam.WindowInto(FixedWindows(window_size))
                | f"AttachEventName_{topic}" >> beam.ParDo(AttachEventNameDoFn())
                | f"BuildRawEvent_{topic}" >> beam.ParDo(BuildRawEventDoFn())
            )

            # Write RAW to topic-specific Iceberg table
            if iceberg_sink:
                raw_events | f"{topic}_Iceberg" >> iceberg_sink

            # Extract tier event payload → Write to BQ
            if bq_sink:
                refined = raw_events | f"{topic}_Extract" >> beam.ParDo(ExtractPayloadDoFn())
                refined | f"{topic}_BQ" >> bq_sink

            all_raw_events.append(raw_events)

        # Merge all topics → API enrichment branches
        merged = all_raw_events | "Flatten" >> beam.Flatten()
        self._build_api_branches(merged)
```

### Batch Pipeline (tiers-collector)

```python
def _build_batch_pipeline(self):
    with beam.Pipeline(options=self.options) as p:
        raw = (
            p
            | "Trigger" >> beam.Create([None])
            | "FetchFromAPI" >> beam.ParDo(FetchTiersDoFn(...))
        )

        # Write source (Iceberg)
        raw | "WriteIceberg" >> iceberg_sink

        # Extract refined → Write BQ
        refined = raw | "ExtractPayload" >> beam.ParDo(ExtractTiersPayloadDoFn())
        refined | "WriteBQ" >> bq_sink
```

### Optional Sink Pattern

```python
# All sinks are optional — check before using
if self._bq_member_tier_sink is not None:
    refined = member_tier | "ExtractPayload" >> beam.ParDo(ExtractMemberTierPayloadDoFn())
    refined | "WriteBQ" >> self._bq_member_tier_sink
```

---

## 3. Fan-Out Pattern

### One PCollection → Multiple Outputs

```python
# Pattern 1: beam.Map for 1:1 extraction
member_tier_pairs = triples | beam.Map(lambda x: (x[0], x[1]))  # (member_id, tier_code)
tier_maint_pairs = triples | beam.Map(lambda x: (x[0], x[2]))   # (member_id, tier_event_id)

# Pattern 2: beam.FlatMap for 1:N extraction (sales-collector example)
receipts = events | beam.Map(extract_receipt)           # 1 event → 1 receipt
skus = events | beam.FlatMap(extract_skus)              # 1 event → N SKUs
tenders = events | beam.FlatMap(extract_tenders)        # 1 event → M tenders
```

### Merge Pattern

```python
# Merge multiple PCollections into one
all_events = [topic_a_events, topic_b_events] | beam.Flatten()
```

---

## 4. Payload Extraction DoFns (Refined Layer)

### ExtractMemberTierPayloadDoFn

```python
class ExtractMemberTierPayloadDoFn(beam.DoFn):
    def process(self, element: dict[str, Any]) -> Iterator[dict[str, Any]]:
        is_delete = element.get("_is_delete", False)
        payload = json.loads(element["payload"]) if isinstance(element["payload"], str) else element["payload"]

        if is_delete:
            # CDC DELETE: minimal row with PK fields only
            yield {
                "member_tier_id": None,
                "member_id": payload.get("memberId"),
                "code": None,
                "program_code": payload.get("programCode"),
                "partner_code": None,
                "start_date": None,
                "expiry_date": None,
                "ranking": None,
                "created_date": None,
                "origin_created_date": None,
                "updated_date": None,
                "retention_start_date": None,
                "etl_created_date": None,
                "ingestedTHDate": _get_ingested_th_date_str(),
                "_is_delete": True,
            }
            return

        # Normal UPSERT: full field extraction
        yield {
            "member_tier_id": payload.get("memberTierId"),
            "member_id": payload.get("memberId"),
            "code": payload.get("code"),
            "program_code": payload.get("programCode"),
            "partner_code": payload.get("partnerCode"),
            "start_date": self._parse_timestamp(payload.get("startDate")),
            "expiry_date": self._parse_timestamp(payload.get("expiryDate")),
            "ranking": int(payload["ranking"]) if payload.get("ranking") else None,
            "created_date": self._parse_timestamp(payload.get("createdDate")),
            "origin_created_date": self._parse_timestamp(payload.get("originCreatedDate")),
            "updated_date": self._parse_timestamp(payload.get("updatedDate")),
            "retention_start_date": self._parse_timestamp(payload.get("retentionStartDate")),
            "etl_created_date": Timestamp(micros=Timestamp.now().micros + _BANGKOK_OFFSET_MICROS),
            "ingestedTHDate": _get_ingested_th_date_str(),
        }
```

### Timestamp Parsing Pattern (CRITICAL)

```python
from apache_beam.utils.timestamp import Timestamp
_BANGKOK_OFFSET_SECONDS = 7 * 3600
_BANGKOK_OFFSET_MICROS = _BANGKOK_OFFSET_SECONDS * 1_000_000

def _parse_timestamp(self, ts_str: str | None) -> Timestamp | None:
    """Parse ISO timestamp → Beam Timestamp with Bangkok offset.

    MUST use Beam Timestamp — BQ Storage Write API's RowCoder needs .micros attribute.
    datetime.datetime will crash: AttributeError: 'datetime' has no attribute 'micros'
    """
    if not ts_str:
        return None
    try:
        dt = datetime.datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        utc_ts = Timestamp.from_utc_datetime(dt.astimezone(datetime.UTC))
        return Timestamp(micros=utc_ts.micros + _BANGKOK_OFFSET_MICROS)
    except (ValueError, TypeError):
        return None
```

### Upgraded vs Downgraded Events

Two separate DoFns — NOT one DoFn with branching:

```python
# ExtractTierEventUpgradedPayloadDoFn — includes is_existing_tier
yield {
    "event_id": payload.get("eventId"),
    "tier_code": payload.get("tierCode"),
    "is_existing_tier": payload.get("isExistingTier"),  # Only in upgraded
    "trigger_type": payload.get("triggerType"),
    "etl_created_date": Timestamp(micros=Timestamp.now().micros + _BANGKOK_OFFSET_MICROS),
}

# ExtractTierEventDowngradedPayloadDoFn — NO is_existing_tier
yield {
    "event_id": payload.get("eventId"),
    "tier_code": payload.get("tierCode"),
    # NO is_existing_tier field
    "trigger_type": payload.get("triggerType"),
    "etl_created_date": Timestamp(micros=Timestamp.now().micros + _BANGKOK_OFFSET_MICROS),
}
```

---

## 5. CDC Logic (UPSERT + DELETE)

### CDC UPSERT (Default)

Elements without `_is_delete` flag → wrapped as UPSERT automatically by `_WrapCdcRowDoFn`.

### CDC DELETE

```python
# In FetchMemberTierDoFn — when tier removed from API
def process(self, element):
    member_id, tier_code = element

    api_response = self._client.get_member_tiers(member_id)
    api_tier_codes = {item["code"] for item in api_response.get("data", [])}

    if tier_code and tier_code not in api_tier_codes:
        # Tier removed → query BQ for programCode
        program_code = self._query_bq_for_program_code(member_id, tier_code)
        if program_code:
            yield {
                "source": "loyalty-member-tier-api",
                "eventName": "loyalty.member.tier",
                "timestamp": int(time.time()),
                "memberId": member_id,
                "payload": json.dumps({"memberId": member_id, "programCode": program_code}),
                "_is_delete": True,    # ← This flag triggers DELETE
            }
```

### 3-Layer DELETE Safety

1. `tier_code` is not None (from Kafka event, not Schema A)
2. API doesn't have this tier code for this member
3. BQ confirms the tier existed (has programCode)

All 3 must be true → DELETE emitted.

### How _is_delete Flows Through Pipeline

```
FetchMemberTierDoFn → element with _is_delete: True
  ↓
ExtractMemberTierPayloadDoFn → minimal row with _is_delete: True
  ↓
BigQuerySink (CDC mode) → _WrapCdcRowDoFn
  ↓
_WrapCdcRowDoFn.process():
    is_delete = element.pop("_is_delete", False)
    mutation_type = "DELETE" if is_delete else "UPSERT"
    yield {"row_mutation_info": {"mutation_type": mutation_type, ...}, "record": element}
  ↓
WriteToBigQuery (use_cdc_writes=True)
```

---

## 6. Member ID Extraction

### ExtractMemberIdAndTierCodeDoFn

```python
class ExtractMemberIdAndTierCodeDoFn(beam.DoFn):
    def process(self, element: dict[str, Any]) -> Iterator[tuple[str, str | None, str | None]]:
        payload = json.loads(element["payload"])

        # Recursive search for memberId
        member_id = self._find_member_id(payload)
        if not member_id:
            self._counter_missing.inc()
            return

        tier_code = payload.get("eligibleTierCode")     # Current tier from Kafka
        tier_event_id = payload.get("tierEventId")       # For tier_maintenance filtering

        yield (member_id, tier_code, tier_event_id)
```

### Deduplication Before API Calls

```python
# Bundle-scoped dedup (fast, but not cross-bundle)
deduped = pairs | beam.ParDo(DeduplicatePairsDoFn())

# Cross-bundle dedup (stronger, uses GroupByKey)
deduped = member_ids | beam.Distinct()
```

---

## 7. RawEvent Envelope

All events flow through a standard envelope before writing to Iceberg source:

```python
class RawEvent(TypedDict):
    eventId: str       # UUID v4, auto-generated
    source: str        # e.g. "members-collector"
    eventName: str     # e.g. "loyalty.member.tier" (from topic name)
    timestamp: int     # Unix epoch seconds
    payload: str       # JSON-serialized original payload
```

### IntermediateEvent (Between Decode and Build)

```python
class IntermediateEvent(TypedDict):
    eventName: str
    payload: dict[str, Any]

# attach_event_name() → IntermediateEvent
# build_raw_event(IntermediateEvent) → RawEvent (with uuid, source, json.dumps)
```

---

## 8. Beam Metrics

### Counter Pattern

```python
from apache_beam.metrics import Metrics

class MyDoFn(beam.DoFn):
    def setup(self):
        self._seen = Metrics.counter("namespace", "records_seen")
        self._ok = Metrics.counter("namespace", "records_ok")
        self._errors = Metrics.counter("namespace", "records_errors")

    def process(self, element):
        self._seen.inc()
        try:
            result = transform(element)
            self._ok.inc()
            yield result
        except Exception:
            self._errors.inc()
```

### Standard Metric Namespaces

| DoFn | Namespace | Counters |
|------|-----------|----------|
| ExtractValueDoFn | `extract` | records_seen, records_ok, records_errors |
| DecodeParseDoFn | `decode` | messages_seen, messages_ok, messages_errors |
| AttachEventNameDoFn | `transform` | attach_seen, attach_ok |
| BuildRawEventDoFn | `build` | records_seen, records_ok, records_errors |
| FetchMemberTierDoFn | `fetch_member_tier` | requests_sent, requests_ok, requests_failed, deletes_emitted |
| DeduplicatePairsDoFn | `dedup_pairs` | total_pairs, unique_pairs, duplicate_pairs |

---

## 9. Testing DoFns

### Unit Test Pattern

```python
import apache_beam as beam
from apache_beam.testing.test_pipeline import TestPipeline
from apache_beam.testing.util import assert_that, equal_to

def test_extract_payload():
    input_data = [{"eventId": "uuid", "payload": '{"memberId": "M1"}'}]
    expected = [{"member_id": "M1", ...}]

    with TestPipeline() as p:
        result = (
            p
            | beam.Create(input_data)
            | beam.ParDo(ExtractMemberTierPayloadDoFn())
        )
        assert_that(result, equal_to(expected))
```

### Testing DoFns with API Calls

```python
def test_fetch_member_tier(mocker):
    """Mock API client to test DoFn logic."""
    mock_client = mocker.patch("src.application.pipeline.api_dofns.LoyaltyApiClient")
    mock_client.return_value.get_member_tiers.return_value = {
        "data": [{"code": "T1L1", "memberId": "M1"}]
    }

    dofn = FetchMemberTierDoFn(base_url="http://test", ...)
    dofn.setup()

    results = list(dofn.process(("M1", None)))
    assert len(results) == 1
```

---

## 10. DO / DON'T

| DO | DON'T |
|----|-------|
| Use `Timestamp` from `apache_beam.utils.timestamp` | Use `datetime.datetime` for BQ timestamps |
| Initialize API clients in `setup()` | Create clients in `__init__()` |
| Use `yield` in `process()` | Use `return [list]` |
| Add Beam Metrics counters to every DoFn | Skip observability |
| Handle Schema A/B/C in attach_event_name() | Assume single message format |
| Use `beam.Distinct()` for strong dedup | Rely only on bundle-scoped dedup |
| Use separate DoFns for upgraded vs downgraded | One DoFn with if/else branching |
| Check `is not None` before using optional sinks | Assume all sinks exist |
| Use `_is_delete` flag for CDC DELETE | Use DML DELETE on CDC tables |
| Pass `(member_id, tier_code)` tuples for fan-out | Pass entire dicts through branches |

---

## 11. File Locations

```
{collector}/src/
├── domain/
│   ├── models.py                    # RawEvent, IntermediateEvent TypedDicts
│   ├── transformers.py              # attach_event_name(), build_raw_event() (pure logic)
│   └── schemas.py                   # BQ schema dicts + TypedDicts
├── application/pipeline/
│   ├── builder.py                   # Pipeline DAG construction
│   ├── dofns.py                     # ExtractValue, Decode, AttachEventName, BuildRawEvent
│   ├── avro_dofn.py                 # DecodeAvroOrJsonDoFn
│   ├── transform_dofns.py           # ExtractMemberTierPayloadDoFn, ExtractTierEvent*DoFn
│   └── api_dofns.py                 # FetchMemberTierDoFn, FetchTierMaintenanceDoFn, Dedup
└── adapters/output/
    ├── bigquery_sink.py             # BigQuerySink (append/cdc/batch)
    └── bigquery_storage.py          # _WrapCdcRowDoFn, write functions
```
