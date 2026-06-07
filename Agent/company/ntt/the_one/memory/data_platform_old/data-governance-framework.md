# Data Governance Framework

## Data Quality Frameworks

### Dataplex Data Quality (GCP Native)
Dataplex provides declarative data quality rules executed on serverless infrastructure.

**Rule Types:**
- **Completeness:** Non-null checks on required fields.
- **Uniqueness:** Primary key uniqueness validation.
- **Validity:** Range checks, regex patterns, allowed values.
- **Accuracy:** Cross-reference validation against source of truth.
- **Freshness:** Verify data updated within expected timeframe.

**Implementation:**
```yaml
# Dataplex auto data quality spec
rules:
  - column: member_id
    non_null_expectation: {}
  - column: tier_code
    set_expectation:
      values: ["SILVER", "GOLD", "PLATINUM"]
  - column: ingestedTHDate
    range_expectation:
      min_value: "20240101"
      max_value: "20261231"
    row_condition_expectation:
      sql_expression: "ingestedTHDate IS NOT NULL"
```

**Scheduling:** Run via Dataplex scheduler or embed in pipeline via API. Results stored in BigQuery and/or Cloud Logging.

### Dataform Assertions (SQL-Based)
For teams already using Dataform for transformation:
```sql
-- assertion: unique_member_tier
SELECT member_id, tier_code, COUNT(*) as cnt
FROM ${ref("refined_member_tier")}
GROUP BY member_id, tier_code
HAVING cnt > 1
```
Assertions run as part of the Dataform DAG and block downstream dependencies on failure.

### Pipeline-Level Quality Checks
Implement quality gates within Beam pipelines:
```python
class QualityGateDoFn(beam.DoFn):
    def __init__(self, required_fields):
        self.required_fields = required_fields
    
    def process(self, element):
        missing = [f for f in self.required_fields if not element.get(f)]
        if missing:
            yield beam.pvalue.TaggedOutput('rejected', {
                'element': element,
                'missing_fields': missing
            })
        else:
            yield beam.pvalue.TaggedOutput('valid', element)
```

### Quality Monitoring Dashboard
Track these metrics over time in BigQuery:
- **Null rate per column:** Detect schema drift or upstream issues.
- **Record count per partition:** Detect missing/duplicate data loads.
- **Value distribution shifts:** Detect data quality degradation.
- **Schema change frequency:** Track unexpected schema evolution.

## Naming Conventions

### BigQuery
```
Project:     the1-re-data-platform-{env}
Dataset:     loyalty_{source/refined}     (e.g., loyalty_source, loyalty_refined)
Table:       {entity_name}                (e.g., member_tier, tier_events_upgraded)
Column:      camelCase                    (e.g., memberId, tierCode, etlLoadTime)
View:        v_{entity_name}              (e.g., v_member_tier_current)
```

### Kafka
```
Topic:       {domain}.{entity}.{event}    (e.g., loyalty.member.tier-changed)
Consumer:    {service}-{env}              (e.g., members-collector-stg)
Schema:      {topic}-value / {topic}-key
```

### GCS
```
Bucket:      the1-re-{env}-{collector}-{purpose}
             (e.g., the1-re-stg-members-collector-source)
Path:        gs://bucket/{namespace}/{table}/{partition}/
```

### Infrastructure
```
Service Account: sa-{collector}-{env}@project.iam.gserviceaccount.com
Dataflow Job:    {collector}-{env}-{job_type}  (e.g., members-collector-stg-streaming)
Cloud Run Job:   {collector}-{env}-batch
Scheduler:       {collector}-{env}-daily
```

## Data Lineage and Catalog

### Dataplex Universal Catalog
Dataplex automatically discovers and catalogs GCP data assets:
- **BigQuery tables/views:** Automatic metadata harvesting.
- **Cloud Storage objects:** File-level discovery and profiling.
- **Pub/Sub topics:** Schema metadata integration.

### Lineage Tracking
Dataplex captures lineage automatically for:
- **BigQuery jobs:** Table-to-table and column-to-column lineage.
- **Dataflow pipelines:** Source-to-sink lineage (requires Dataflow lineage integration).
- **Dataform:** Transformation lineage within Dataform DAGs.

**Column-level lineage** enables:
- Impact analysis: Which downstream tables are affected if a source column changes?
- Root cause analysis: Where did a data quality issue originate?
- Compliance: Which PII columns flow into which downstream systems?

### Custom Lineage
For pipeline components not auto-tracked:
```python
from google.cloud import datacatalog_lineage_v1

client = datacatalog_lineage_v1.LineageClient()
# Register custom lineage for Kafka -> Iceberg -> BQ
process = client.create_process(parent=f"projects/{project}/locations/{location}", process={
    "display_name": "members-collector-streaming",
})
```

### Data Products (Dataplex)
Organize related datasets as governed data products:
- Group tables, views, and documentation into a logical product.
- Define owners, consumers, and SLAs.
- Enable self-service discovery for data consumers.

## Access Control Patterns

### IAM Hierarchy
```
Organization
  └── Project (the1-re-data-platform-{env})
       ├── Dataset-level roles (BigQuery Data Viewer/Editor)
       │    └── Table-level roles (fine-grained)
       ├── Bucket-level roles (Storage Object Viewer/Creator)
       └── Service Account roles (per-collector)
```

### Column-Level Security (Policy Tags)
```sql
-- Create taxonomy
CREATE SCHEMA IF NOT EXISTS `project.taxonomy_dataset`;

-- Apply policy tag to sensitive columns
ALTER TABLE my_dataset.member_tier
ALTER COLUMN phoneNumber SET OPTIONS (
  policy_tags = ['projects/my-project/locations/us/taxonomies/123/policyTags/456']
);
```

**Policy tag hierarchy:**
```
PII (root)
  ├── High: national_id, passport_number
  ├── Medium: email, phone_number, address
  └── Low: first_name, last_name
```

Grant `roles/datacatalog.categoryFineGrainedReader` on specific policy tags to authorized users.

### Dynamic Data Masking
Apply masking rules without changing underlying data:
- **SHA256:** Hash sensitive values for joining without exposing raw data.
- **Default masking:** Replace with NULL or fixed value for unauthorized users.
- **Custom masking:** UDF-based masking for partial redaction (e.g., mask last 4 digits).

### Service Account Strategy
- **One SA per collector:** Isolates permissions. A bug in one collector can't access another's resources.
- **Least privilege:** Grant only needed roles (e.g., `bigquery.dataEditor` on specific datasets, not project-wide).
- **Workload Identity** for GKE/Dataflow: Bind Kubernetes SA to GCP SA without key files.
- **Short-lived credentials:** Use token-based authentication, not downloaded JSON keys.

## PII Handling and Compliance

### Data Classification
| Level | Examples | Controls |
|-------|----------|----------|
| Restricted | National ID, passport, credit card | Encrypted, policy-tagged, audit-logged |
| Confidential | Email, phone, address | Policy-tagged, role-restricted |
| Internal | Member ID, tier code, transaction amounts | Standard IAM, no masking |
| Public | Product categories, store locations | Open to all authenticated users |

### Sensitive Data Protection (Cloud DLP)
- **Discovery:** Scan BigQuery tables for PII patterns automatically.
- **Classification:** Apply taxonomy tags based on detected PII types.
- **De-identification:** Transform PII using tokenization, bucketing, or masking.
- **Integration:** Run DLP inspections as part of pipeline quality gates.

### Compliance Checklist
- [ ] All PII columns tagged with appropriate policy tags.
- [ ] Column-level security enforced on Restricted and Confidential data.
- [ ] Audit logs enabled for data access (BigQuery audit logs).
- [ ] Data retention policies defined and automated (partition expiration).
- [ ] Right to deletion process documented and tested.
- [ ] Cross-border data transfer controls in place (data residency).

## SLA/SLO for Data Pipelines

### Define SLOs by Pipeline Type

| Pipeline Type | Freshness SLO | Availability SLO | Completeness SLO |
|---------------|---------------|-------------------|-------------------|
| Streaming (members) | < 5 min from Kafka event | 99.5% uptime | > 99.9% records processed |
| Batch daily (tiers) | Ready by 3 AM BKK | 99% (daily success) | 100% API records loaded |
| Batch daily (m-t-h) | Ready by 3 AM BKK | 99% (daily success) | 100% API records loaded |

### Freshness Monitoring
```sql
-- Check data freshness per pipeline
SELECT
  table_name,
  MAX(ingestedTHDate) as latest_partition,
  DATE_DIFF(CURRENT_DATE('Asia/Bangkok'), PARSE_DATE('%Y%m%d', CAST(MAX(ingestedTHDate) AS STRING)), DAY) as days_stale
FROM `project.loyalty_source.INFORMATION_SCHEMA.PARTITIONS`
GROUP BY table_name
HAVING days_stale > 1;  -- Alert if more than 1 day stale
```

### Alert Strategy
- **Streaming freshness:** Alert if Dataflow `data_freshness` > 10 minutes.
- **Batch completeness:** Alert if Cloud Scheduler job fails or row count < expected.
- **Data quality:** Alert if Dataplex quality scan fails or null rate exceeds threshold.
- **Infrastructure:** Alert on Dataflow worker errors, OOM, or pipeline drain.

### Incident Response
1. **Detect:** Automated alerts via Cloud Monitoring.
2. **Triage:** Check Dataflow UI, Kafka consumer lag, API health.
3. **Mitigate:** Restart pipeline, scale workers, or switch to fallback.
4. **Resolve:** Fix root cause, backfill missing data if needed.
5. **Review:** Post-incident review, update SLOs and runbooks.

---

*Sources: [Dataplex Universal Catalog](https://docs.cloud.google.com/dataplex/docs/introduction), [BigQuery Data Governance](https://docs.cloud.google.com/bigquery/docs/data-governance), [Column-Level Security](https://docs.cloud.google.com/bigquery/docs/column-level-security), [Policy Tags Best Practices](https://docs.cloud.google.com/bigquery/docs/best-practices-policy-tags), [Data Lineage](https://docs.cloud.google.com/dataplex/docs/about-data-lineage), [Sensitive Data Protection](https://docs.cloud.google.com/sensitive-data-protection/docs/dlp-bigquery)*
