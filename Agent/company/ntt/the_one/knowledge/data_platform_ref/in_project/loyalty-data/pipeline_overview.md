# Members-Collector Pipeline Overview

## High-Level Architecture

```
                              members-collector (Dataflow)
                    =============================================

  +-----------+        +-------------------+        +------------------+
  |  Confluent |       | Per-Topic Branch  |       | Source Layer      |
  |  Kafka     |------>| (Decode, Window,  |------>| (Iceberg via BLMS |
  |            |       |  Build Raw Event) |       |  REST Catalog)   |
  +-----------+        +-------------------+        +------------------+
                              |                            |
   Topics:                    |                     +-----------------+
   - loyalty.members.upgraded |                     | Refined Layer   |
   - loyalty.members.downgraded                     | (BigQuery)      |
                              |                     | tier_events_*   |
                              v                     +-----------------+
                       +-------------+
                       |   Merge     |
                       |   Topics    |
                       +-------------+
                              |
                   +----------+----------+
                   |                     |
                   v                     v
          +----------------+     +------------------+
          | Member Tier    |     | Tier Maintenance |
          | Branch         |     | Branch           |
          +----------------+     +------------------+
                   |                     |
                   v                     v
          +----------------+     +------------------+
          | Loyalty API    |     | Loyalty API      |
          | GET member-tier|     | GET tier-maint   |
          +----------------+     +------------------+
                   |                     |
            +------+------+       +------+------+
            |             |       |             |
            v             v       v             v
       +---------+  +---------+  +---------+  +---------+
       | Iceberg |  |BigQuery |  | Iceberg |  |BigQuery |
       | member_ |  |refined. |  | member_ |  |refined. |
       | tier    |  |member_  |  | tier_   |  |member_  |
       |(source) |  |tier     |  |maint.   |  |tier_    |
       |         |  |(CDC)    |  |(source) |  |maint.   |
       +---------+  +---------+  +---------+  +---------+
```

## Two Pipeline Modes

### 1. Streaming Mode (`job_type=normal`)
```
Kafka --> Decode --> Window --> Transform --> Iceberg + BigQuery
                                    |
                                    +--> API Enrichment --> Iceberg + BigQuery
```

### 2. Batch Mode (`job_type=initial_data`)
```
BigQuery Staging --> ReadFromBigQuery --> Iceberg (source)
                                     --> BigQuery (refined)
```

## Data Flow Summary

| Stage | Input | Output | Tables |
|-------|-------|--------|--------|
| Per-Topic (Kafka) | Kafka messages | Raw events | `tier_events_upgraded` (Iceberg) |
| | | | `tier_events_downgraded` (Iceberg) |
| | | | `refined.tier_events_upgraded` (BQ) |
| | | | `refined.tier_events_downgraded` (BQ) |
| Member Tier (API) | member_id + tier_code | API response | `member_tier` (Iceberg) |
| | | | `refined.member_tier` (BQ, CDC) |
| Tier Maintenance (API) | member_id | API response | `member_tier_maintenance` (Iceberg) |
| | | | `refined.member_tier_maintenance` (BQ) |

## Sink Types

| Layer | Writer | Mode | Details |
|-------|--------|------|---------|
| Source (Iceberg) | `managed.Write` via BLMS REST Catalog | Append | BigLake Metastore, partition: `identity(etlLoadTime)` |
| Refined (BigQuery) | Storage Write API | Append or CDC | CDC = UPSERT + DELETE, PK: `memberId + programCode` |

## Key Components

| Component | File | Role |
|-----------|------|------|
| Composition Root | `main.py` | Wires sinks, creates PipelineBuilder |
| Pipeline Builder | `builder.py` | Orchestrates Beam pipeline graph |
| Config Adapter | `configuration_adapter.py` | Loads YAML + secrets |
| Kafka DoFns | `dofns.py` | Extract, Decode, AttachEventName, BuildRawEvent |
| Avro Decoder | `avro_dofn.py` | Schema Registry + Avro/JSON decode |
| API DoFns | `api_dofns.py` | Extract member_id, Dedup, Fetch API, CDC DELETE |
| Transform DoFns | `transform_dofns.py` | Extract payloads for BQ refined |
| Iceberg Sink | `iceberg_sink.py` | IcebergSink PTransform (managed.Write) |
| BigQuery Sink | `bigquery_sink.py` + `bigquery_storage.py` | BQ write (append/CDC/batch) |
