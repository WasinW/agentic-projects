# Governance Instructions

> AI: Read this file when implementing DLQ, data quality checks, naming conventions, or access control.

## Quick Reference

```
Validation Layers:
  1. Configuration → Pydantic DTOs (startup)
  2. Runtime → DoFn try/except + Beam Metrics (per record)
  3. Storage → Iceberg schema + BQ REQUIRED fields (on write)
  4. Post-Write → Dataplex quality scans (scheduled)

DLQ Pattern (planned):
  DoFn error → TaggedOutput("dead_letter") → BQ dead_letter dataset → Replay
```

---

## 1. Data Validation Layers

### Layer 1: Configuration (Pydantic)

```python
# adapters/input/configuration/settings.py
class DataflowConfigDto(BaseModel):
    """Validates YAML config at startup. Invalid config = pipeline won't start."""
    kafka: KafkaConfig
    iceberg: IcebergConfig
    refined: RefinedConfig

    @model_validator(mode="after")
    def validate_cdc_requires_primary_key(self):
        if self.refined.member_tier.write_mode == "cdc" and not self.refined.member_tier.primary_key:
            raise ValueError("CDC write mode requires primary_key")
        return self
```

### Layer 2: Runtime (DoFns)

```python
# Current behavior: log + drop invalid records
class MyDoFn(beam.DoFn):
    def process(self, element):
        self._counter_seen.inc()
        try:
            result = self._transform(element)
            self._counter_ok.inc()
            yield result
        except Exception as e:
            self._counter_errors.inc()
            logger.warning("Failed: %s | Element: %s", e, element)
            # Record is dropped — no DLQ yet
```

### Layer 3: Storage Schema

- **Iceberg**: Beam RowType schema enforces column types on write
- **BigQuery**: `mode: REQUIRED` fields reject NULL values; type mismatches fail

### Layer 4: Post-Write (Dataplex)

Currently **NOT ENABLED**. When enabled:
- Dataplex auto data profiling: null rates, distributions, cardinality
- Dataplex quality scans: freshness, volume, completeness, validity
- Scheduled scans: 6h incremental (streaming), daily (batch)
- Quality score target: >= 95%

---

## 2. DLQ Strategy (Planned)

### Pattern: TaggedOutput → BQ Dead Letter Table

```python
# Future implementation
from apache_beam.pvalue import TaggedOutput

class MyDoFn(beam.DoFn):
    def process(self, element):
        try:
            yield self._transform(element)
        except Exception as e:
            yield TaggedOutput("dead_letter", {
                "original_record": json.dumps(element),
                "error_message": str(e),
                "step_name": "MyDoFn",
                "timestamp": datetime.now().isoformat(),
            })

# In builder.py
results = input | beam.ParDo(MyDoFn()).with_outputs("dead_letter", main="main")
results.main | "WriteGood" >> good_sink
results.dead_letter | "WriteDLQ" >> dlq_sink  # BQ dead_letter dataset
```

### DLQ Storage

```sql
-- dead_letter.{collector}_errors
CREATE TABLE dead_letter.members_collector_errors (
    original_record STRING,
    error_message STRING,
    step_name STRING,
    error_timestamp TIMESTAMP,
    pipeline_job_id STRING,
    _PARTITIONTIME TIMESTAMP
) PARTITION BY DATE(_PARTITIONTIME);
```

### Replay Strategy

1. Query DLQ for failed records
2. Fix root cause (schema, validation, data issue)
3. Replay via batch pipeline reading from DLQ table

---

## 3. Data Quality Rules

### Seven Quality Dimensions

| Dimension | Description | Example Rule |
|-----------|-------------|--------------|
| **Freshness** | Data is up-to-date | `ingestedTHDate` within last 2h (streaming) or 24h (batch) |
| **Volume** | Expected row count | Row count > 0 per daily partition |
| **Completeness** | Required fields populated | `member_id` NOT NULL rate >= 99.9% |
| **Validity** | Values in expected range | `tier_code` IN known tier codes |
| **Consistency** | Cross-source agreement | member count matches tiers count |
| **Accuracy** | Reflects real-world truth | Cross-validate against source API |
| **Uniqueness** | No unintended duplicates | `(member_id, program_code)` unique in CDC table |

### Freshness Check Queries

```sql
-- Streaming table freshness (should be within 2 hours)
SELECT MAX(ingestedTHDate) as latest_partition,
       DATE_DIFF(CURRENT_DATE('Asia/Bangkok'), MAX(ingestedTHDate), DAY) as days_behind
FROM `project.refined.member_tier`;

-- Batch table freshness (should be within 24 hours)
SELECT MAX(etlLoadTime) as latest_load
FROM `project.refined.tiers_master`;
```

---

## 4. Naming Conventions

### GCP Resources

| Resource | Pattern | Example |
|----------|---------|---------|
| Project | `the1-{domain}-{env}` | `the1-loyalty-data-prod` |
| GCS Bucket (source) | `the1-{domain}-source-{env}` | `the1-loyalty-data-source-prod` |
| Service Account | `t1-{collector}@{project}.iam` | `t1-members-collector@...` |
| Secret | `{collector}` | `members-collector` |

### BigQuery

| Dataset | Purpose |
|---------|---------|
| `source` | Iceberg-backed external tables |
| `refined` | Transformed analytics tables |
| `public` | Published views for consumers |
| `dead_letter` | Failed records (planned) |

### Tables

| Convention | Example |
|-----------|---------|
| snake_case | `member_tier`, `tier_events_upgraded` |
| Prefix by entity | `member_*`, `tier_*`, `sales_*` |
| Refined prefix | `refined.member_tier` |

### Iceberg

| Component | Convention | Example |
|-----------|-----------|---------|
| Namespace | `source` | `source` |
| Table | snake_case entity | `source.member_tier` |

---

## 5. Access Control

### Per-Collector IAM

Each collector's service account has scoped access:

| Role | Scope | Purpose |
|------|-------|---------|
| `roles/biglake.editor` | BigLake catalog | Iceberg table management |
| `roles/storage.objectAdmin` | Source GCS bucket | Read/write Iceberg data |
| `roles/bigquery.dataEditor` | Source + refined datasets | BQ table writes |
| `roles/secretmanager.secretAccessor` | Collector secret | Read credentials |
| `roles/serviceusage.serviceUsageConsumer` | Project | Use GCP APIs |

### IAM is managed via Terraform

```
infrastructure/{collector}/biglake-metastore.tf
→ Grants SA access to source + refined datasets
```

---

## 6. Current State

| Feature | Status |
|---------|--------|
| Config validation (Pydantic) | IMPLEMENTED |
| Runtime validation (DoFn try/except) | IMPLEMENTED |
| Storage schema enforcement | IMPLEMENTED |
| Naming conventions | ESTABLISHED |
| Per-collector IAM | IMPLEMENTED |
| Dataplex profiling | NOT YET ENABLED |
| Dataplex quality scans | NOT YET ENABLED |
| Data lineage | NOT YET ENABLED |
| DLQ | NOT YET IMPLEMENTED |
| Cross-domain data sharing | NOT YET IMPLEMENTED |

---

## 7. DO / DON'T

| DO | DON'T |
|----|-------|
| Use Pydantic for config validation | Skip validation on YAML input |
| Add Beam Metrics counters in every DoFn | Skip observability |
| Log + drop failed records (current) | Let pipeline crash on bad data |
| Follow naming conventions consistently | Invent new naming patterns |
| Use per-collector service accounts | Share SAs across collectors |
| Store secrets in Secret Manager | Put credentials in YAML or code |
