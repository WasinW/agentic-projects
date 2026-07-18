# Insight Data Pipeline - Complete Knowledge Base

## Overview
insight-api เป็นโปรเจ็คใหญ่ (audiences, collector, contracts, personas, segment, ssc, triggers)
data pipeline เป็นแค่ **part เดียว** ใน insight-api (ไม่เหมือน loyalty ที่เป็น ETL app ล้วน)

## Key Paths
```
insight/insight-api/
├── data/
│   ├── customer-profile-pipeline/    # V3 Streaming (Hexagonal Architecture) ★ MAIN FOCUS
│   ├── orchestrator/airflow/dags/    # 10 Airflow DAGs
│   └── processor/dataflow/
│       ├── common/                   # V1 framework (config-driven orchestrator)
│       ├── common_v2/                # V2 framework (PTransform pattern)
│       ├── configs/                  # YAML configs (batch_initial + realtime)
│       ├── schemas/                  # Table JSON schemas
│       └── scripts/                  # Pipeline entry scripts
├── infrastructure/data-pipeline/     # Terraform (BQ, Composer, Buckets, DTS, Dataplex, Pub/Sub)
└── pipeline/data/
    ├── ms-personas.gitlab-ci.yml     # V1/V2 CI/CD (874 lines)
    └── customer-profile-data-pipeline.gitlab-ci.yml  # V3 CI/CD (318 lines)
```

## THREE Pipeline Generations
| Gen | Framework | Pattern | Entry | Status |
|-----|-----------|---------|-------|--------|
| V1 | common/ | Config+Orchestrator+Steps | batch_initial_pipeline.py | Legacy |
| V2 | common_v2/ | PTransform direct | realtime_v2, batch_pipeline.py | Current |
| V3 | customer-profile-pipeline/ | Hexagonal (Ports+Adapters) | main.py + builder.py | Recommended ★ |

## V3 Customer Profile Pipeline (Hexagonal Architecture)
```
config/ → logging.py, options.py, settings.py
domain/ → constants.py, models.py, schemas.py, transformers.py (600+ lines, 20+ pure funcs)
ports/ → input_ports.py, output_ports.py (Protocol interfaces)
adapters/
  input/ → bigquery_mapping.py, bigtable_reader.py, secret_manager.py, sql_loader.py
  output/ → bigquery_cdc.py, s3_parquet.py, iceberg_writer.py (1000+ lines manual), iceberg_sync.py
pipeline/ → dofns.py (12 DoFns), builder.py (PipelineBuilder)
resources/sql/streaming/ → 6 SQL templates
core/ → logging_utils.py (RateLimitedLogger)
```

### Data Flow (Streaming)
```
Pub/Sub → ExtractPersonasDoFn → FetchFromBigtableDoFn → FilterEmptyPKDoFn
  ├→ profiles → TransformSchemasDoFn → MapToCdcTableRowDoFn → WriteToBigQuery CDC (ms_personas)
  ├→ profiles → TransformSchemasDoFn → FullfillSchemasDoFn → Window(5min) → S3 Parquet
  ├→ consents → TransformSchemasDoFn → WriteToBigLakeDoFn → Manual Iceberg Writer (events_consents)
  └→ Periodic: SyncToIcebergDoFn (MERGE ms_personas → ms_personas_iceberg)
```

### Key Patterns
- **Mapping-driven transformation**: BQ mapping table → 3 types (path, logic, constant) → refreshed every 5min
- **Self-contained DoFns**: imports inside setup()/process() for Dataflow serialization
- **Multi-target**: BQ CDC + S3 Parquet + Iceberg (manual writer + sync)
- **CDC format**: {row_mutation_info: {mutation_type, change_sequence_number}, record: {...}}
- **DLQ**: Tagged output to BQ dlq table
- **Rate-limited logging**: prevents log flooding in streaming

## Infrastructure (Terraform)
- **Backend**: GCS `devops-terraformstate-nonprod` prefix `the1-insight/services/personas/ms-personas`
- **BigQuery**: 4 datasets (data_raw, source, data_structure, data_refined) + BigLake connection
- **Composer**: HA (2 schedulers, 2-6 workers), Airflow 2.10.5, asia-southeast1
- **Buckets**: 4 (composer, data-staging, audit-logs, data-source)
- **GAR**: `insight-datapipeline-dataflow-common`
- **DTS**: 3 transfers (mapping hourly, member daily 6AM, consent disabled)
- **Dataplex**: insight-lake → bq-insight-zone (CURATED)
- **Pub/Sub**: DLQ topic + main subscription (exactly-once, 5 retries)
- **Project IDs**: `the1-insight-stg` / `the1-insight-prod`
- **SA**: `t1-ins-{env}-sa-data@the1-insight-{env}.iam.gserviceaccount.com`

## CI/CD
### ms-personas.gitlab-ci.yml (V1/V2 - 874 lines)
- Build: sec scan + test + build wheel
- Deploy STG: terraform plan/apply + deploy-tables + create-image (Kaniko) + upload wheel + upload scripts + setup composer vars
- Deploy PROD: same pattern, manual gates
- **Key**: Uploads wheel + DAGs + scripts + configs to Composer GCS bucket
- **Airflow variables**: 9 vars (project_id, environment, bucket_composer, etc.)

### customer-profile-data-pipeline.gitlab-ci.yml (V3 - 318 lines)
- Build: sec scan + test
- Deploy STG: build image (Kaniko) + upload (Flex Template spec + DAG)
- Deploy PROD: same pattern
- **Key**: Flex Template pattern (not direct Dataflow submission)
- **Template**: `gs://{composer_bucket}/template/customer-profile-pipeline/spec.json`
- **Airflow variables**: 2 vars (flex_template_bucket, workspace_env)

## Airflow DAGs (10 DAGs)
1. dag_customer_profile_batch_initial.py — One-time batch load (8 workers, n1-standard-8)
2. dag_customer_profile_v3.py — V3 Streaming via Flex Template ★
3. dag_customer_profile_realtime_v2_test.py — V2 Streaming (config-driven)
4. dag_customer_profile_realtime.py — V1 Streaming (original)
5. dag_customer_profile_batch_test.py — V2 Batch
6. dag_trigger_dts.py — Trigger BQ Data Transfer Service
7. dag_customer_profile_clear_job.py — Cancel/Drain Dataflow jobs
8. clear_bucket.py — Delete GCS contents
9. copy_gcs_to_s3.py — GCS→S3 copy utility
10. simple_bigquery_query_dag.py — Ad-hoc BQ queries

## deploy.py (Table Deployment - ~800 lines)
- 3 table types: native, managed (BigQuery Managed Iceberg), external_iceberg
- Change detection: NO_CHANGE, ADDITIVE, BREAKING
- Schema comparison: type, mode, partition, clustering
- Auto dummy data for external Iceberg tables
- PyIceberg optional dependency

## Tables (12 total)
| Table | Type | Dataset | Purpose |
|-------|------|---------|---------|
| ms_personas | native (CDC) | insight | Main personas (97 cols, partitioned by timestamp, clustered by memberId) |
| events_consents | managed Iceberg | insight | Consent events (BigLake connection) |
| ms_personas_iceberg | external Iceberg | data_refined | Historical personas (Iceberg merge) |
| mapping_reconcile | native | insight | Mapping config (from S3 DTS) |
| ms_member | native | insight | Member data (from S3 DTS) |
| data_pipeline_dlq | native | insight | Dead letter queue |
| ms_personas_consents_history | native | data_refined | Consent history |
| ms_personas_consents_history_s3 | native | data_refined | S3 consent history |
| ms_personas_consents_internal_partner | native | data_refined | Internal partner consents |
| ms_personas_consents_external_partner | native | data_refined | External partner consents |
| ms_personas_suppression | native | data_refined | Suppression data |

## KEY DIFFERENCES: Insight vs Loyalty

| Aspect | Insight | Loyalty |
|--------|---------|---------|
| **Orchestration** | Airflow (Composer) | Custom Python (Beam) |
| **Job Submission** | Flex Template via Airflow DAG | Direct gcloud dataflow |
| **Scheduler** | Airflow scheduler (HA) | Cloud Scheduler |
| **Python Package** | Uploaded as .whl to GCS | Built into container |
| **Config Pattern** | YAML config uploaded to GCS + settings.py | YAML deep-merge in code |
| **S3 Integration** | Yes (Parquet + DTS) | No |
| **Iceberg Writer** | Manual (PyArrow + Avro metadata) | Managed I/O (BLMS REST) |
| **Iceberg Sync** | MERGE query (BQ→Iceberg) | N/A |
| **Monitoring** | Airflow sensors + health checks | Dataflow metrics only |
| **DLQ** | BQ table (implemented) | Not yet implemented |
| **Dataplex** | Active (lake/zone/asset) | Not used |
| **DTS** | Active (S3→BQ hourly/daily) | N/A |
| **Hex Architecture** | V3 has it | All collectors have it |
| **Project Structure** | Part of larger API project | Standalone ETL apps |

## What Insight Needs to Align with Loyalty
1. **BLMS REST Catalog** for Iceberg writes (replace manual writer)
2. **Frozen dataclasses** for config (BlmsCatalogConfig, ManagedIcebergWriteConfig)
3. **managed.Write** (Beam cross-language IcebergIO)
4. **RowTypeConstraint** for Iceberg schema (JVM compatibility)
5. **etlLoadTime INT YYYYMMDDHH** partition pattern
6. **deploy.py** alignment (register_table pattern)
7. **CI/CD**: Kaniko multi-dest (STG+PROD), deploy scripts standardization
8. **Infrastructure**: Per-pipeline Terraform modules (consistent with loyalty)

## Dependencies (CRITICAL - Tested Compatible Set)
```
apache-beam[gcp]==2.69.0
pyarrow>=14.0.0,<18.0.0 (or ==14.0.2 for v1/v2)
numpy>=1.21,<2 (CRITICAL for pyarrow compatibility)
boto3==1.34.106 (exact - S3 dependency chain)
botocore==1.34.106
aiobotocore==2.13.0
s3fs==2024.6.1
fsspec==2024.6.1
pandas>=1.5.0,<2.1.0
fastavro>=1.9.0
google-cloud-bigquery>=3.25.0
google-cloud-bigtable>=2.26.0
google-cloud-secret-manager>=2.20.0
```

## Gotchas
- `use_public_ips=True` REQUIRED for S3 access
- `sdkContainerImage` must include boto3
- numpy<2 CRITICAL for pyarrow compiled with numpy 1.x
- S3 dep chain (s3fs→aiobotocore→botocore) has EXACT version requirements
- `RUN_PYTHON_SDK_IN_DEFAULT_ENVIRONMENT=1` for S3 boto3 in Dockerfile
- Java 17 required for BigQuery CDC expansion service
