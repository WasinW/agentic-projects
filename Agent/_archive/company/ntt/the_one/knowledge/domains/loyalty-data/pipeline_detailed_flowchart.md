# Members-Collector Detailed Pipeline Flowchart

## Streaming Pipeline (`job_type=normal`)

### Phase 1: Per-Topic Kafka Ingestion

For each topic (`loyalty.members.upgraded`, `loyalty.members.downgraded`):

```
┌──────────────────────────────────────────────────────────────────┐
│  KAFKA TOPIC: loyalty.members.{upgraded|downgraded}              │
└──────────────────────┬───────────────────────────────────────────┘
                       │
                       v
              ┌────────────────┐
              │ ReadFromKafka  │  Confluent Cloud (SASL_SSL + PLAIN)
              │                │  consumer_config: bootstrap.servers,
              │                │  group.id, auto.offset.reset=earliest
              └───────┬────────┘
                      │ (key, value) tuples
                      v
              ┌────────────────┐
              │ ExtractValueDoFn│  Extract value bytes from Kafka record
              └───────┬────────┘
                      │ bytes
                      v
              ┌────────────────┐
              │DecodeAvroOrJson│  Schema Registry lookup (Avro magic byte)
              │     DoFn       │  → Avro decode or JSON fallback
              │                │  Handles: Schema A (flat), B (nested payload),
              │                │           C (stringified message wrapper)
              └───────┬────────┘
                      │ dict (parsed message)
                      v
              ┌────────────────┐
              │  FilterNones   │  Remove decode failures
              └───────┬────────┘
                      │ dict
                      v
              ┌────────────────┐
              │ FixedWindows   │  window_size_seconds (default: 60s)
              │ + Trigger      │  AfterWatermark(early=Repeatedly(AfterProcessingTime))
              │                │  AccumulationMode.DISCARDING
              └───────┬────────┘
                      │ windowed dict
                      v
              ┌────────────────┐
              │AttachEventName │  Handles 3 Kafka message schemas:
              │     DoFn       │  C: {"message": "<json string>"} → json.loads
              │                │  B: {"payload": {inner}} → unwrap
              │                │  A: flat dict → wrap as payload
              │                │  Attaches eventName from message fields
              └───────┬────────┘
                      │ IntermediateEvent (eventName + payload dict)
                      v
              ┌────────────────┐
              │BuildRawEventDoFn│  Build envelope:
              │                │  {eventId, source, eventName,
              │                │   timestamp, payload (JSON string)}
              └───────┬────────┘
                      │ RawEvent dict
                      │
          ┌───────────┼──────────────────────────────────┐
          │           │                                  │
          v           │                                  v
┌──────────────┐      │                        ┌──────────────────────┐
│ Iceberg Sink │      │                        │ BQ Refined (optional)│
│ (Source)     │      │                        │                      │
│              │      │  if upgraded:          │  ExtractTierEvent    │
│ managed.Write│      │  → tier_events_upgraded│  {Upgraded|Downgraded}│
│ via BLMS REST│      │  if downgraded:        │  PayloadDoFn         │
│              │      │  → tier_events_downgrade│                      │
│ table:       │      │                        │  → BQ Storage Write  │
│ tier_events_ │      │                        │    API (append)      │
│ {up|down}    │      │                        │                      │
└──────────────┘      │                        └──────────────────────┘
                      │
                      │ (collected for merge)
                      v
```

### Phase 2: Merge & API Enrichment

```
    ┌─────────────────────────────────┐
    │  raw_events from topic_upgraded │
    └───────────────┬─────────────────┘
                    │
                    ├─── Flatten ──────────> merged_raw_events
                    │                              │
    ┌───────────────┘                              │
    │  raw_events from topic_downgraded            │
    └──────────────────────────────────────────────┘
                                                   │
                                                   v
                                    ┌──────────────────────────┐
                                    │ExtractMemberIdAndTierCode│
                                    │          DoFn            │
                                    │                          │
                                    │ Parse payload JSON       │
                                    │ Find memberId (recursive)│
                                    │ Extract tierCode         │
                                    └────────────┬─────────────┘
                                                 │
                                                 │ (member_id, tier_code) tuples
                                                 │
                               ┌─────────────────┴─────────────────┐
                               │                                   │
                        MEMBER TIER BRANCH                  TIER MAINTENANCE BRANCH
                               │                                   │
                               v                                   v
                ┌──────────────────────┐              ┌────────────────────────┐
                │  DeduplicatePairsDoFn│              │ Map(x[0])              │
                │                      │              │ Extract member_id only │
                │  Dedup by full tuple │              └───────────┬────────────┘
                │  (member_id,tier_code)│                         │
                └──────────┬───────────┘                         v
                           │                          ┌────────────────────────┐
                           v                          │DeduplicateMemberIdsDoFn│
                ┌──────────────────────┐              │                        │
                │  FetchMemberTierDoFn │              │  Dedup by member_id    │
                │                      │              └───────────┬────────────┘
                │  (see CDC DELETE     │                          │
                │   flowchart below)   │                          v
                └──────────┬───────────┘              ┌────────────────────────┐
                           │                          │FetchTierMaintenanceDoFn│
                           │                          │                        │
                     ┌─────┴─────┐                    │ GET /members/{id}/     │
                     │           │                    │   tier-maintenance     │
                     v           v                    │ Explode: 1 row/event   │
              ┌──────────┐ ┌──────────┐               └───────────┬────────────┘
              │ Iceberg  │ │ BigQuery │                           │
              │ member_  │ │ refined. │                    ┌──────┴──────┐
              │ tier     │ │ member_  │                    │             │
              │ (source) │ │ tier     │                    v             v
              │          │ │ (CDC)    │             ┌──────────┐ ┌──────────┐
              │ managed. │ │         │             │ Iceberg  │ │ BigQuery │
              │ Write    │ │ Extract │             │ member_  │ │ refined. │
              └──────────┘ │ Payload │             │ tier_    │ │ member_  │
                           │ → Wrap  │             │ maint.   │ │ tier_    │
                           │ CDC Row │             │ (source) │ │ maint.   │
                           │ → Write │             └──────────┘ └──────────┘
                           └──────────┘
```

## CDC DELETE Flowchart (FetchMemberTierDoFn)

```
                  ┌──────────────────────────────┐
                  │  Input: (member_id, tier_code)│
                  └──────────────┬───────────────┘
                                 │
                                 v
                  ┌──────────────────────────────┐
                  │ GET /members/{id}/tier        │
                  │ → Loyalty API                 │
                  │ → response.data = [tier1, ...]│
                  └──────────────┬───────────────┘
                                 │
                        ┌────────┴────────┐
                        │ tier_code       │
                        │ is None?        │
                        └────────┬────────┘
                           │           │
                        YES│           │NO
                           │           │
                           v           v
              ┌──────────────┐  ┌──────────────────────┐
              │ Yield ALL    │  │ Search API data for   │
              │ tiers from   │  │ item where            │
              │ API response │  │ item.code == tier_code│
              │ (UPSERT)     │  └──────────┬───────────┘
              │              │             │
              │ Original     │     ┌───────┴───────┐
              │ behavior     │     │   Found?      │
              └──────────────┘     └───────┬───────┘
                                     │          │
                                  YES│          │NO (tier removed!)
                                     │          │
                                     v          v
                        ┌──────────────┐  ┌──────────────────────┐
                        │ Yield only   │  │  LAYER 3: Query BQ   │
                        │ matching     │  │                      │
                        │ tier item    │  │  SELECT programCode  │
                        │ (UPSERT)     │  │  FROM refined.       │
                        │              │  │    member_tier        │
                        └──────────────┘  │  WHERE memberId=@id  │
                                          │  AND code=@tier_code │
                                          └──────────┬───────────┘
                                                     │
                                              ┌──────┴──────┐
                                              │ Found in BQ?│
                                              └──────┬──────┘
                                                │         │
                                             YES│         │NO
                                                │         │
                                                v         v
                                   ┌─────────────┐  ┌──────────────┐
                                   │ Yield DELETE │  │ Skip         │
                                   │ row with:    │  │ (new tier    │
                                   │              │  │  never in BQ │
                                   │ _is_delete:  │  │  = nothing   │
                                   │   True       │  │  to delete)  │
                                   │ memberId     │  └──────────────┘
                                   │ programCode  │
                                   │ (from BQ)    │
                                   └──────┬──────┘
                                          │
                                          v
                           ┌──────────────────────────┐
                           │ CDC DELETE 3-Layer Safety │
                           │                          │
                           │ 1. tier_code not None     │
                           │ 2. API doesn't have it    │
                           │ 3. BQ confirms it existed │
                           │                          │
                           │ ALL 3 must be true        │
                           │ before DELETE is emitted   │
                           └──────────────────────────┘
```

## BigQuery CDC Write Path (member_tier)

```
  ┌──────────────────────┐
  │ FetchMemberTierDoFn  │
  │ output dict:         │
  │  {eventId, source,   │
  │   eventName,         │
  │   timestamp,         │
  │   memberId, payload, │
  │   _is_delete: bool}  │
  └──────────┬───────────┘
             │
             v
  ┌──────────────────────────────┐
  │ ExtractMemberTierPayloadDoFn │
  │                              │
  │ if _is_delete:               │
  │   → minimal row (PK only)   │
  │   {memberId, programCode,    │
  │    etlLoadTime, _is_delete}  │
  │                              │
  │ else:                        │
  │   → full row with all fields │
  │   {memberTierId, memberId,   │
  │    code, programCode, ...    │
  │    etlLoadTime}              │
  └──────────┬───────────────────┘
             │
             v
  ┌──────────────────────┐
  │ _WrapCdcRowDoFn      │
  │                      │
  │ Pop _is_delete flag  │
  │ → mutation_type:     │
  │   "DELETE" or "UPSERT"│
  │                      │
  │ Timestamp → ISO str  │
  │                      │
  │ Output:              │
  │ {row_mutation_info:  │
  │   {mutation_type,    │
  │    change_seq_number}│
  │  record: {...}}      │
  └──────────┬───────────┘
             │
             v
  ┌──────────────────────┐
  │ WriteToBigQuery      │
  │ (Storage Write API)  │
  │                      │
  │ use_cdc_writes=True  │
  │ primary_key=         │
  │  [memberId,          │
  │   programCode]       │
  └──────────────────────┘
```

## Batch Pipeline (`job_type=initial_data`)

```
  ┌──────────────────────────────────────────────────────┐
  │ For each enabled source table:                       │
  │                                                      │
  │  ┌─────────────┐     ┌────────────┐    ┌──────────┐ │
  │  │ ReadFromBQ  │────>│ passthrough│───>│  Iceberg  │ │
  │  │ (SQL query) │     │ row mapper │    │managed.   │ │
  │  │             │     │(preserve   │    │Write      │ │
  │  │ source:     │     │ etlLoadTime│    │          │ │
  │  │ BQ staging  │     │ from BQ)   │    │ table:    │ │
  │  └─────────────┘     └────────────┘    │ member_   │ │
  │                                        │ tier /    │ │
  │  Parallel branches via condition_parts │ member_   │ │
  │  (WHERE clause per part)               │ tier_maint│ │
  │                                        └──────────┘ │
  └──────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────┐
  │ For each enabled refined table:                      │
  │                                                      │
  │  ┌─────────────┐     ┌──────────────────────┐        │
  │  │ ReadFromBQ  │────>│ WriteToBigQuery      │        │
  │  │ (SQL query) │     │ (WRITE_APPEND)       │        │
  │  │             │     │ CREATE_NEVER         │        │
  │  │ source:     │     │                      │        │
  │  │ BQ staging  │     │ target: refined.*    │        │
  │  └─────────────┘     └──────────────────────┘        │
  └──────────────────────────────────────────────────────┘
```

## Schema Handling (Kafka Message Variants)

```
  Schema A (flat):
  ┌─────────────────────────────────────┐
  │ {"eventId": "...", "memberId": ...} │
  │  → wrap entire dict as payload      │
  └─────────────────────────────────────┘

  Schema B (nested payload):
  ┌───────────────────────────────────────────────────┐
  │ {"eventId": "...", "payload": {"memberId": ...}}  │
  │  → unwrap inner payload                           │
  └───────────────────────────────────────────────────┘

  Schema C (stringified message):
  ┌──────────────────────────────────────────────────────────────┐
  │ {"message": "{\"eventId\": \"...\", \"payload\": {...}}"}    │
  │  → json.loads(message) → replace payload → fall through to B│
  └──────────────────────────────────────────────────────────────┘

  Processing order in attach_event_name():
  1. Check for Schema C (message key with string value) → parse
  2. Check for Schema B (payload key as dict) → unwrap
  3. Else Schema A (flat) → wrap
```

## Sink Configuration (from main.py)

```
  ┌────────────────────────────────────────────────────────────────────┐
  │                    Composition Root (main.py)                      │
  │                                                                    │
  │  BlmsCatalogConfig (shared)                                        │
  │  ├── warehouse_path: gs://{project}-source                         │
  │  ├── namespace: source                                             │
  │  └── rest_uri: https://biglake.googleapis.com/iceberg/v1/restcatalog│
  │                                                                    │
  │  Iceberg Sinks (4 tables):                                         │
  │  ├── tier_events_upgraded    → IcebergSink(TIER_EVENT_SCHEMA)      │
  │  ├── tier_events_downgraded  → IcebergSink(TIER_EVENT_SCHEMA)      │
  │  ├── member_tier             → IcebergSink(MEMBER_INFO_SCHEMA)     │
  │  └── member_tier_maintenance → IcebergSink(MEMBER_INFO_SCHEMA)     │
  │                                                                    │
  │  BigQuery Sinks (4 tables):                                        │
  │  ├── refined.tier_events_upgraded    → BigQuerySink(append)        │
  │  ├── refined.tier_events_downgraded  → BigQuerySink(append)        │
  │  ├── refined.member_tier             → BigQuerySink(CDC)           │
  │  │   └── PK: [memberId, programCode]                               │
  │  └── refined.member_tier_maintenance → BigQuerySink(append)        │
  └────────────────────────────────────────────────────────────────────┘
```

## Timestamps (Bangkok +7)

```
  Source (Iceberg):
  ├── etlLoadTime: INT64 YYYYMMDDHH (Bangkok +7)
  └── Computed in iceberg_writer.py

  Refined (BigQuery):
  ├── etlLoadTime: TIMESTAMP (now + 7h offset)
  ├── Date/time columns: TIMESTAMP (unix_ts + 7h offset)
  └── CDC path: .to_utc_datetime() preserves +7 baked into micros
```
