# Customer SVOC Interim Solution - Design Document

## 1. Context & Motivation

### Current State (AWS)
- SVOC (Single View of Customer) table lives on AWS data mart
- Table: `full_customer_svoc` — 727 columns, ~21M records, ~20GB
- Updated monthly (par_month=YYYYMM)
- S3 path: `s3://t1-analytics/analysis/the1_support/full_customer_svoc/par_month=YYYYMM/`
- Consumed by: Insight app (via Scala Spark export), loyalty analytics (via LEFT JOIN), BI tools

### Problem
- Multiple GCP services (Insight, Loyalty Insights, future marts) need SVOC data
- Native SVOC on GCP does not exist yet — depends on future mart development
- Cannot wait — downstream consumers need data now

### Interim Solution
DTS the SVOC from AWS S3 into GCP BigQuery (Insight project), then:
1. Expose via `public` dataset for cross-domain sharing
2. Export subset (~280 cols) to GCS Parquet for Insight app consumption

### Future State
- Native SVOC pipeline built on GCP mart layer
- AWS DTS deprecated
- GCS export may continue (or switch to direct BQ read)

---

## 2. Architecture

```
AWS S3 (par_month=YYYYMM, 727 cols, Parquet)
  |
  | DTS (on-demand, WRITE_TRUNCATE)
  v
refined.full_customer_svoc_ingt          <-- Landing table (raw from S3)
  |
  | Scheduled Query or View (alias mapping)
  v
refined.full_customer_svoc               <-- Curated table (aliased columns)
  |
  | VIEW
  v
public.full_customer_svoc                <-- Semantic layer (sharing)
  |
  | Dataflow (Beam, SQL-based, batch)
  | SELECT ~280 cols with alias + optional filter
  v
GCS Parquet (10-20 files)                <-- For Insight app consumption
gs://the1-insight-{env}-data-pipeline-export/svoc/{par_month}/*.parquet
```

---

## 3. Components

### 3.1 DTS Configuration (Terraform)
- **Source**: `s3://t1-analytics/analysis/the1_support/full_customer_svoc/par_month=YYYYMM/`
- **Destination**: `the1-insight-{env}.refined.full_customer_svoc_ingt`
- **Format**: Parquet
- **Write Mode**: WRITE_TRUNCATE (full replace each run)
- **Schedule**: On-demand (manual trigger, ~monthly)
- **Credentials**: AWS access key from Secret Manager

### 3.2 BigQuery Tables

| Table | Dataset | Type | Columns | Purpose |
|-------|---------|------|---------|---------|
| `full_customer_svoc_ingt` | `refined` | Native table | 727 | DTS landing (raw from S3) |
| `full_customer_svoc` | `refined` | Native table or View | 727 | Curated with alias mapping |
| `full_customer_svoc` | `public` | View | 727 | Semantic layer for sharing |

### 3.3 Export Pipeline (Dataflow)

| Property | Value |
|----------|-------|
| **Name** | `customer-svoc-interim` |
| **Type** | Batch (Dataflow Flex Template) |
| **Input** | BigQuery SQL query (~280 cols from `refined.full_customer_svoc_ingt`) |
| **Output** | GCS Parquet files (10-20 files, controlled by Beam) |
| **Trigger** | On-demand via Airflow DAG |
| **Location** | `insight-api/data/customer-svoc-interim/` |

### 3.4 Export Column Selection

From the existing Scala `SvocSchema.svocSchema`, approximately 280 columns are selected from the 727-column source. These include:

**Categories of exported columns:**
- Demographics: `member_number`, `life_stage`, `have_kids`, `kids_*`
- Location: `most_visit_*`, `address_*`
- Spending: `active_spend_*`, `total_crc_*`
- Rankings: `crc_ranking_*`, `cds_ranking_*`, etc. (by year)
- Segments: `*_rfm_*_segment`, `*_relevance_segment`
- Preferences: `beauty_*`, `fashion_*`, `food_*`, `electronics_*`
- App engagement: `app_active*`, `have_*_app`
- Wallet share: `cfr_share_of_wallet_*`, `ssp_share_of_wallet_*`
- Flags: various boolean flags

Full column list maintained in `src/resources/sql/export_svoc.sql`.

---

## 4. File Structure

```
insight-api/
├── data/
│   └── customer-svoc-interim/
│       ├── src/
│       │   ├── __init__.py
│       │   ├── main.py                      # Composition root
│       │   ├── adapters/
│       │   │   └── input/
│       │   │       └── configuration/
│       │   │           ├── configuration_adapter.py
│       │   │           └── settings.py
│       │   ├── application/
│       │   │   └── pipeline/
│       │   │       └── builder.py           # Beam pipeline (BQ SQL -> GCS Parquet)
│       │   └── resources/
│       │       └── sql/
│       │           └── export_svoc.sql      # SELECT ~280 cols with aliases
│       ├── config/
│       │   ├── base.yaml
│       │   ├── stg.yaml
│       │   └── prod.yaml
│       ├── Dockerfile
│       ├── Dockerfile.base
│       └── pyproject.toml
├── infrastructure/
│   └── customer-svoc-interim/
│       ├── schemas/
│       │   ├── full_customer_svoc_ingt.json  # 727 cols (DTS landing)
│       │   ├── full_customer_svoc.json       # 727 cols (aliased)
│       │   └── deploy.py                     # Schema deployer
│       ├── dts.tf                             # S3 -> BQ DTS config
│       └── templates/
│           └── container_spec.json            # Flex template spec
├── data/orchestrator/airflow/dags/
│   └── dag_customer_svoc_interim.py           # Airflow DAG (on-demand)
└── pipeline/data/
    └── customer-svoc-interim.gitlab-ci.yml    # CI/CD
```

---

## 5. Pipeline Design (Dataflow)

### Beam Pipeline Flow
```python
with beam.Pipeline(options=options) as p:
    # Step 1: Read from BigQuery using SQL
    rows = (
        p
        | "ReadBQ" >> beam.io.ReadFromBigQuery(
            query=export_sql,        # ~280 cols with aliases
            use_standard_sql=True,
            project=config.project_id,
        )
    )

    # Step 2: Write to GCS as Parquet
    rows | "WriteParquet" >> beam.io.WriteToParquet(
        file_path_prefix=f"{config.gcs_export_path}/{config.par_month}/svoc",
        schema=parquet_schema,
        num_shards=config.num_export_files,  # 10-20
        file_name_suffix=".parquet",
    )
```

### Key Design Decisions

1. **SQL-based selection**: Export query lives in `src/resources/sql/export_svoc.sql` — easy to update columns/aliases without code changes
2. **Controlled file count**: `num_shards` parameter limits output to 10-20 files
3. **Batch mode**: No streaming — runs once per trigger
4. **Alias-ready**: All columns go through alias mapping in SQL (currently 1:1, future: rename)

---

## 6. DTS Configuration

```hcl
resource "google_bigquery_data_transfer_config" "svoc_transfer" {
  display_name           = "SVOC S3 Import"
  data_source_id         = "amazon_s3"
  destination_dataset_id = "refined"
  location               = "asia-southeast1"

  params = {
    destination_table_name_template = "full_customer_svoc_ingt"
    data_path                       = "s3://t1-analytics/analysis/the1_support/full_customer_svoc/par_month=${par_month}/**"
    access_key_id                   = data.google_secret_manager_secret_version.aws_access_key.secret_data
    secret_access_key               = data.google_secret_manager_secret_version.aws_secret_key.secret_data
    file_format                     = "PARQUET"
    write_disposition               = "WRITE_TRUNCATE"
  }

  # On-demand: no schedule, triggered manually
  disabled = true
}
```

---

## 7. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| S3 schema changes (new columns added monthly) | DTS may fail or miss columns | WRITE_TRUNCATE + auto-detect schema; monitor DTS logs |
| 20GB data size causing Dataflow OOM | Export pipeline crashes | Use batch mode, sufficient workers, controlled shards |
| AWS credentials rotation | DTS stops working | Credentials in Secret Manager, alerting on DTS failure |
| Column alias changes | Downstream breakage | All aliases in SQL file, versioned in git |
| par_month format mismatch | DTS reads wrong partition | Parameterize par_month in DAG, validate format |

---

## 8. Operational Runbook

### Monthly Refresh Procedure
1. **Trigger DTS**: Run DTS transfer with `par_month=YYYYMM` parameter
2. **Verify landing**: Check `refined.full_customer_svoc_ingt` row count + sample
3. **Refresh curated**: If using scheduled query, verify `refined.full_customer_svoc` updated
4. **Trigger export**: Run Airflow DAG `customer_svoc_interim_export`
5. **Verify GCS**: Check `gs://bucket/svoc/YYYYMM/` has 10-20 parquet files
6. **Notify consumers**: Inform Insight app team that new SVOC export is ready
