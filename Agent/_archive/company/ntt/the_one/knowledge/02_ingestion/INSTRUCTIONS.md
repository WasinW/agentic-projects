# Ingestion Instructions

> AI: Read this file when implementing Kafka consumers, API batch fetch, PostgreSQL readers, or initial data loads.

## Quick Reference

```
Ingestion Sources:
  Kafka (streaming) → ReadFromKafka → Avro/JSON decode → Window → Transform → Write
  REST API (batch)  → beam.Create([None]) → FetchDoFn → Transform → Write
  PostgreSQL (batch)→ beam.Create([config]) → ReadFromPostgresDoFn → Transform → Write
  BQ staging (init) → ReadFromBigQuery(sql) → Direct write

Schema Detection (Kafka messages):
  Schema C: {"message": "<stringified JSON>"}     → json.loads(message) → fall through
  Schema B: {"eventId", "payload": {dict}}         → unwrap inner payload
  Schema A: {flat fields}                          → wrap entire dict as payload
```

---

## 1. Kafka Streaming Ingestion (members-collector)

### Pipeline Chain

```
ReadFromKafka → ExtractValueDoFn → DecodeAvroOrJsonDoFn → WindowInto
  → AttachEventNameDoFn → BuildRawEventDoFn → Write to Iceberg (per-topic)
  → Flatten all topics → ExtractMemberIdAndTierCodeDoFn → Fan-out branches
```

### ReadFromKafka Setup

```python
# builder.py — per-topic Kafka reader
consumer_config = {
    "bootstrap.servers": config.kafka_config.bootstrap_servers,
    "group.id": config.kafka_config.group_id,
    "auto.offset.reset": "earliest",
}

# Add SASL auth if credentials exist
if config.kafka_config.username:
    consumer_config.update({
        "security.protocol": "SASL_SSL",
        "sasl.mechanism": "PLAIN",
        "sasl.jaas.config": (
            f'org.apache.kafka.common.security.plain.PlainLoginModule required '
            f'username="{config.kafka_config.username}" '
            f'password="{config.kafka_config.password}";'
        ),
    })

kafka_events = (
    p
    | f"ReadFromKafka_{topic}" >> ReadFromKafka(
        consumer_config=consumer_config,
        topics=[topic],
    )
    | f"ExtractValue_{topic}" >> beam.ParDo(ExtractValueDoFn())
)
```

### Avro/JSON Decoding

```python
# Two decoder modes:
# 1. With Schema Registry (Avro-aware)
decoded = kafka_bytes | beam.ParDo(DecodeAvroOrJsonDoFn(
    schema_registry_url=config.kafka_config.schema_registry_url,
    schema_registry_user=config.kafka_config.schema_registry_user,
    schema_registry_password=config.kafka_config.schema_registry_password,
    message_format="auto",  # auto-detect avro vs json
))

# 2. JSON-only (simpler)
decoded = kafka_bytes | beam.ParDo(DecodeParseDoFn())
```

### Windowing (Streaming)

```python
windowed = parsed | beam.WindowInto(
    FixedWindows(window_size_seconds),
    trigger=AfterWatermark(
        early=Repeatedly(AfterProcessingTime(window_size_seconds)),
    ),
    accumulation_mode=AccumulationMode.DISCARDING,
)
```

### YAML Config (Kafka)

```yaml
# base.yaml
kafka:
  topics: ["loyalty.members.upgraded", "loyalty.members.downgraded"]
  group_id: "the1-members-collector"
  window_size_seconds: 10
  message_format: "auto"         # "auto" | "avro" | "json"

# Secret Manager (kafkaCredentials) contains:
# {
#   "bootstrap_servers": "pkc-xxx.confluent.cloud:9092",
#   "username": "...",
#   "password": "...",
#   "schema_registry_url": "https://psrc-xxx.confluent.cloud",
#   "schema_registry_user": "...",
#   "schema_registry_password": "..."
# }
```

---

## 2. Schema Detection — attach_event_name()

Handles 3 Kafka message formats in order:

```python
# domain/transformers.py
def attach_event_name(payload: dict[str, Any]) -> IntermediateEvent:
    event_name = payload.get("eventName", DEFAULT_EVENT_NAME)

    # Schema C: stringified JSON in "message" key
    message = payload.get("message")
    if isinstance(message, str):
        try:
            inner = json.loads(message)
            if isinstance(inner, dict):
                payload = inner
                event_name = payload.get("eventName", event_name)
        except json.JSONDecodeError:
            pass

    # Schema B: nested payload dict → unwrap inner
    inner = payload.get("payload")
    if isinstance(inner, dict):
        return {"eventName": event_name, "payload": inner}

    # Schema A: flat message → wrap entire dict as payload
    return {"eventName": event_name, "payload": payload}
```

### Schema Examples

**Schema A (flat):**
```json
{"memberId": "M123", "tierCode": "T1L1", "eligibleTierCode": "T1L2"}
```
→ `{"eventName": "default", "payload": {entire dict}}`

**Schema B (wrapped):**
```json
{"eventId": "uuid", "source": "...", "eventName": "loyalty.member.tier",
 "timestamp": 123, "payload": {"memberId": "M123", "tierCode": "T1L1"}}
```
→ `{"eventName": "loyalty.member.tier", "payload": {inner payload only}}`

**Schema C (stringified):**
```json
{"message": "{\"eventId\": \"uuid\", \"payload\": {\"memberId\": \"M123\"}}"}
```
→ Parse string → detect Schema B → `{"eventName": "...", "payload": {inner}}`

---

## 3. DoFn Chain — Extract → Decode → Transform → Build

### Standard Chain (4 DoFns)

```python
# 1. ExtractValueDoFn — extract bytes from Kafka record
class ExtractValueDoFn(beam.DoFn):
    def process(self, element):
        yield element[1]  # (key, value) → value bytes

# 2. DecodeParseDoFn — decode bytes to dict
class DecodeParseDoFn(beam.DoFn):
    def process(self, element):
        result = safe_decode_and_parse(element)
        if result is not None:
            yield result

# 3. AttachEventNameDoFn — detect schema + attach eventName
class AttachEventNameDoFn(beam.DoFn):
    def process(self, element):
        yield attach_event_name(element)  # → IntermediateEvent

# 4. BuildRawEventDoFn — wrap in standard envelope
class BuildRawEventDoFn(beam.DoFn):
    def process(self, element):
        yield build_raw_event(element)
        # → {"eventId": uuid, "source": "...", "eventName": "...",
        #    "timestamp": unix_ts, "payload": json.dumps(payload)}
```

### DoFn Best Practices

- Every DoFn has Beam Metrics counters: `seen`, `ok`, `errors`
- API clients initialize in `setup()`, NOT `__init__()` (serialization issue)
- Failed records: log warning + drop (no DLQ yet)
- Use `log_every_n` parameter for periodic progress logging

---

## 4. REST API Batch Fetch (tiers-collector)

### Pattern: Single-Trigger → FetchDoFn

```python
# builder.py — tiers-collector
tiers_master = (
    p
    | "CreateTrigger" >> beam.Create([None])   # Single trigger element
    | "FetchTiers" >> beam.ParDo(
        FetchTiersDoFn(
            base_url=config.loyalty_api_base_url,
            client_id=config.api_client_id,
            client_secret=config.api_client_secret,
            api_id=config.loyalty_api_id,
            token_url=config.loyalty_api_token_url,
        )
    )
)
```

### FetchDoFn Pattern

```python
class FetchTiersDoFn(beam.DoFn):
    def __init__(self, base_url, client_id, client_secret, api_id, token_url):
        self._base_url = base_url
        # ... store credentials (NOT API client)

    def setup(self):
        # Create API client on worker (NOT in __init__)
        self._client = LoyaltyApiClient(
            base_url=self._base_url,
            client_id=self._client_id,
            client_secret=self._client_secret,
        )

    def process(self, _element):  # element is None (trigger)
        response = self._client.get_tiers()
        # Response: {"data": [{"programCode": "P1", "tiers": [...]}, ...]}
        for program in response["data"]:
            for tier in program.get("tiers", []):
                yield {
                    "eventId": str(uuid.uuid4()),
                    "source": "loyalty-tiers-master-api",
                    "eventName": "loyalty.tiers.master",
                    "timestamp": int(time.time()),
                    "payload": json.dumps({
                        "programCode": program["programCode"],
                        "tier": tier,
                    }),
                }
```

### API Fetch with Fan-Out (members-collector)

```python
# builder.py — members-collector (streaming → API enrichment)
# After Kafka RAW events are written, extract member IDs and fetch from API

merged_raw_events = all_topic_events | beam.Flatten()

triples = merged_raw_events | beam.ParDo(ExtractMemberIdAndTierCodeDoFn())
# → (member_id, tier_code, tier_event_id)

# Branch 1: Member Tier
member_tier_pairs = triples | beam.Map(lambda x: (x[0], x[1]))
deduped = member_tier_pairs | beam.ParDo(DeduplicatePairsDoFn())
member_tier = deduped | beam.ParDo(FetchMemberTierDoFn(...))

# Branch 2: Tier Maintenance
tier_maint_pairs = triples | beam.Map(lambda x: (x[0], x[2]))
deduped_maint = tier_maint_pairs | beam.ParDo(DeduplicatePairsDoFn())
tier_maintenance = deduped_maint | beam.ParDo(FetchTierMaintenanceDoFn(...))
```

---

## 5. PostgreSQL Batch Read (members-tiers-history)

### Pattern: SSH Tunnel + Batch Query

```python
# builder.py — members-tiers-history-collector
db_config = PostgresConfig(
    host=config.postgres_config.host,
    port=config.postgres_config.port,
    database=config.postgres_config.database,
    user=config.postgres_config.username,
    password=config.postgres_config.password,
    use_ssh_tunnel=config.ssh_config is not None,
    ssh_host=config.ssh_config.get("host") if config.ssh_config else None,
    ssh_private_key=config.ssh_config.get("private_key") if config.ssh_config else None,
)

# process_date: CLI arg or yesterday
process_date = self.custom.process_date or (date.today() - timedelta(days=1)).isoformat()
query = self._get_query(process_date)  # SQL with {prev_date} placeholder

records = (
    p
    | "CreateConfig" >> beam.Create([{"query": query, "process_date": process_date}])
    | "ReadFromPostgres" >> beam.ParDo(ReadFromPostgresDoFn(db_config, batch_size=10000))
)
```

### ReadFromPostgresDoFn

```python
class ReadFromPostgresDoFn(beam.DoFn):
    def setup(self):
        self._client = PostgresClient(self._db_config)  # Opens connection + SSH tunnel

    def process(self, query_config):
        query = query_config["query"]
        for batch in self._client.execute_query(query, batch_size=self._batch_size):
            for row in batch:
                record = add_etl_metadata(row, source_table, process_date)
                yield convert_to_raw_format(record)
```

### YAML Config (PostgreSQL)

```yaml
# base.yaml — members-tiers-history
postgres:
  database: "loyalty_db"
  batch_size: 10000

# Secret Manager (apiCredentials) contains:
# {
#   "postgres": {"host": "rds.amazonaws.com", "port": 5432, "username": "...", "password": "..."},
#   "ssh": {"host": "bastion.example.com", "username": "ec2-user", "private_key": "-----BEGIN RSA..."}
# }
```

---

## 6. Initial Data Load (job_type=initial_data)

### Trigger

Set GitLab CI variable: `TRIGGER_INIT_DATA_LOAD=1`

```yaml
# .gitlab-ci.yml
if [ "$TRIGGER_INIT_DATA_LOAD" == "1" ]; then
  JOB_TYPE="initial_data"
  JOB_NAME="members-collector-init-$(date +%Y%m%d-%H%M%S)"
  MAX_WORKERS="50"
fi
```

### Pipeline Pattern

```python
# builder.py — members-collector
if self.config.job_type == "initial_data":
    self._build_init_data_pipeline()
else:
    self._build_streaming_pipeline()

def _build_init_data_pipeline(self):
    # Source branch: BQ staging → Iceberg
    for table_name, table_config in config.init_data.get_enabled_source_tables():
        sql = _read_init_sql_file(table_config.script, config.project_id)
        bq_data = p | ReadFromBigQuery(query=sql, use_standard_sql=True)
        write_to_iceberg(bq_data, iceberg_config, MEMBER_INFO_SCHEMA, to_member_info_row_passthrough)

    # Refined branch: BQ staging → BQ refined
    for table_name, table_config in config.init_data.get_enabled_refined_tables():
        sql = _read_init_sql_file(table_config.script, config.project_id)
        bq_data = p | ReadFromBigQuery(query=sql, use_standard_sql=True)
        bq_data | WriteToBigQuery(table=table_config.target, schema=schema)
```

### Init Data Config

```yaml
# base.yaml
init_data:
  source:
    member_tier:
      enabled: true
      script: "init_source_member_tier.sql"
      target: "member_tier"
      condition_parts: []           # Optional: split query for parallel reads
    member_tier_maintenance:
      enabled: true
      script: "init_source_member_tier_maintenance.sql"
      target: "member_tier_maintenance"
  refined:
    member_tier:
      enabled: true
      script: "init_refined_member_tier.sql"
      target: "project:refined.member_tier"
    member_tier_maintenance:
      enabled: true
      script: "init_refined_member_tier_maintenance.sql"
      target: "project:refined.member_tier_maintenance"
```

---

## 7. Deduplication Patterns

### Bundle-Scoped (DeduplicatePairsDoFn)

```python
class DeduplicatePairsDoFn(beam.DoFn):
    def start_bundle(self):
        self._seen_pairs: set[tuple[str, str | None]] = set()

    def process(self, element):
        pair = (element[0], element[1])
        if pair not in self._seen_pairs:
            self._seen_pairs.add(pair)
            yield element
```

**Limitation**: Only deduplicates within a single bundle. Cross-bundle duplicates possible.

### Cross-Bundle (beam.Distinct)

```python
# Used in builder.py for tier_maintenance dedup
deduped_ids = member_ids | beam.Distinct()
```

**Stronger**: GroupByKey-based, deduplicates across the entire window.

---

## 8. DO / DON'T

| DO | DON'T |
|----|-------|
| Initialize API clients in `setup()` | Create clients in `__init__()` (serialization fails) |
| Handle Schema A/B/C in order: C → B → A | Assume single Kafka message format |
| Use `beam.Distinct()` for cross-bundle dedup | Rely only on bundle-scoped dedup |
| Use `consumer_config` dict for Kafka auth | Hardcode Kafka credentials |
| Use `batch_size` for PostgreSQL reads | Load all rows in memory at once |
| Use `log_every_n` for progress logging | Log every single record |
| Add Beam Metrics counters to every DoFn | Skip observability |
| Use `process_date` from CLI or default yesterday | Hardcode dates |
| Use SASL_SSL for Kafka in production | Use plaintext Kafka connections |

---

## 9. File Locations

```
{collector}/
├── src/
│   ├── domain/
│   │   └── transformers.py                 # attach_event_name() (Schema A/B/C)
│   ├── adapters/
│   │   └── input/
│   │       ├── configuration/
│   │       │   ├── settings.py             # KafkaConfig, PostgresConfig, etc.
│   │       │   ├── configuration_adapter.py # YAML → PipelineConfig
│   │       │   └── secret_adapter.py       # Secret Manager → credentials
│   │       └── kafka/                      # Kafka reader (streaming only)
│   └── application/pipeline/
│       ├── builder.py                      # Pipeline DAG (ReadFromKafka wiring)
│       ├── dofns.py                        # ExtractValue, Decode, AttachEventName, BuildRawEvent
│       ├── avro_dofn.py                    # DecodeAvroOrJsonDoFn
│       └── api_dofns.py                    # FetchMemberTierDoFn, FetchTiersDoFn
├── config/
│   ├── base.yaml                           # kafka topics, group_id, API URLs
│   ├── stg.yaml                            # project_id, warehouse, log_level
│   └── prod.yaml                           # project_id, warehouse, log_level
└── resources/init/                         # SQL templates for initial_data load
```
