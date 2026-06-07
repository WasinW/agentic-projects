# 03 - Dead Letter Queue (DLQ) Pattern

> Capture failed records instead of dropping them — enable replay + monitoring

## Pattern: TaggedOutput (Manual DLQ)

```python
class FetchMemberTierDoFn(beam.DoFn):
    DLQ_TAG = "dead_letter"
    SUCCESS_TAG = "success"

    def process(self, element):
        try:
            result = self._api_call(element)
            yield beam.pvalue.TaggedOutput(self.SUCCESS_TAG, result)
        except Exception as e:
            yield beam.pvalue.TaggedOutput(self.DLQ_TAG, {
                "id": str(uuid.uuid4()),
                "collector_name": "members-collector",
                "stage": "FetchMemberTierDoFn",
                "error_class": type(e).__name__,
                "error_message": str(e),
                "original_record": json.dumps(element, default=str),
                "is_retryable": isinstance(e, (TimeoutError, ConnectionError)),
                "error_timestamp": datetime.now(UTC).isoformat(),
            })
```

## Pipeline Builder: Route DLQ to BQ

```python
results = (
    input_pcoll
    | "Process" >> beam.ParDo(MyDoFn()).with_outputs(
        MyDoFn.SUCCESS_TAG, MyDoFn.DLQ_TAG
    )
)

# Success path
_ = results[MyDoFn.SUCCESS_TAG] | "WriteSuccess" >> WriteToBigQuery(...)

# DLQ path
_ = results[MyDoFn.DLQ_TAG] | "WriteDLQ" >> WriteToBigQuery(
    table="project.dataset.dead_letter_records",
    schema=DLQ_SCHEMA,
)
```

## BQ CDC Failed Rows (Already Have This!)

```python
# builder.py — ปัจจุบัน log แล้วทิ้ง
_ = (
    cdc_write_result.failed_rows_with_errors
    | "LogFailedCDCRows" >> beam.Map(lambda row: logger.error("FAILED: %s", row))
)

# ปรับปรุง: persist ไป DLQ table
_ = (
    cdc_write_result.failed_rows_with_errors
    | "PersistFailedCDC" >> beam.Map(lambda row: {
        "stage": "WriteToBigQueryCDC",
        "error_message": row.get("error_message", ""),
        "original_record": json.dumps(row.get("failed_row", {}), default=str),
        "error_timestamp": datetime.now(UTC).isoformat(),
    })
    | "WriteCDCDLQ" >> WriteToBigQuery(table="project.dataset.dead_letter_records")
)
```

## DLQ Monitoring Alert

```sql
-- Scheduled query (every 15 min)
SELECT stage, COUNT(*) as error_count
FROM `project.dataset.dead_letter_records`
WHERE error_timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 15 MINUTE)
GROUP BY stage
HAVING error_count > 10
```

## DLQ Table Schema

```json
{
  "schema": [
    {"name": "id", "type": "STRING"},
    {"name": "collector_name", "type": "STRING"},
    {"name": "stage", "type": "STRING"},
    {"name": "error_class", "type": "STRING"},
    {"name": "error_message", "type": "STRING"},
    {"name": "original_record", "type": "STRING"},
    {"name": "is_retryable", "type": "BOOLEAN"},
    {"name": "error_timestamp", "type": "TIMESTAMP"},
    {"name": "resolved", "type": "BOOLEAN"}
  ]
}
```

## Pros / Cons

| Pros | Cons |
|------|------|
| No data loss — failed records saved | Requires code changes in every DoFn |
| Enable replay | DLQ table grows — need cleanup policy |
| Real-time detection | IcebergIO has NO built-in DLQ |
| Audit trail | |

## Applicability

| Pipeline Type | Applicable | Notes |
|--------------|:--:|-------|
| Dataflow Streaming | YES | TaggedOutput in Beam DoFns |
| Dataflow Batch | YES | Same pattern |
| Cloud Run Batch | Manual | Write to BQ/GCS on error |
| Dataform | NO | Dataform handles errors differently |
