# Dataplex Auto-Discovery + Iceberg: Limitations & Workarounds

> **Dataplex auto-discovery ไม่รองรับ Iceberg tables**
> ต้องใช้ manual registration หรือ BigQuery external table เป็น proxy

## 1. ปัญหา

Dataplex Universal Catalog Discovery **ไม่ support Iceberg** (และ Delta Lake):

> "Table formats Iceberg and Delta Lake are not supported by Dataplex Universal Catalog Discovery."
> — [Google Cloud Docs](https://cloud.google.com/dataplex/docs/discover-data)

### Formats ที่ auto-discovery รองรับ:
- Parquet, Avro, ORC, JSON (newline-delimited), CSV

### Iceberg: ไม่อยู่ในรายการ

แม้จะ register Iceberg table ใน BLMS แล้ว → Dataplex discovery ก็ยังไม่ scan

---

## 2. ทางเลือก (เรียงตาม effort น้อย → มาก)

### Option A: BigQuery External Table as Proxy (BLOCKED — ติด externalCatalogDatasetOptions)

**Concept**: สร้าง BQ external table ชี้ไป Iceberg → BQ table auto-appear ใน Dataplex catalog

```sql
-- ใช้ BLMS URI ที่มีอยู่แล้ว
CREATE EXTERNAL TABLE `project.dataset.member_tier`
  WITH CONNECTION `project.region.connection`
  OPTIONS (
    format = 'ICEBERG',
    uris = ['blms://projects/PROJECT/locations/LOCATION/catalogs/CATALOG/databases/DB/tables/TABLE']
  );
```

#### BLOCKER: `externalCatalogDatasetOptions` ยังไม่พร้อม

BQ external table ที่ชี้ไป BLMS Iceberg ต้องใช้ **`externalCatalogDatasetOptions`** บน BQ dataset:
```sql
ALTER SCHEMA `project.source`
SET OPTIONS (
  external_catalog_dataset_options = ...
);
```

**ปัญหาปัจจุบัน:**
- Dataset `source` ถูก share กับ **transaction/ team** → ต้อง coordinate ก่อนเปลี่ยน dataset options
- Terraform `externalCatalogDatasetOptions` ยังไม่ถูก apply (รอ transaction/ team)
- เราเลย**ข้าม BQ external table** แล้วใช้ **BLMS REST query ตรง**แทน
- นี่คือเหตุผลที่ "Option B BQ Table Creation" ถูก DISABLED ในตอนนี้

**สถานะ**: BLOCKED — รอ terraform dataset coordination กับ transaction/ team
เมื่อ `externalCatalogDatasetOptions` พร้อม → Option A จะเป็นทางที่ง่ายที่สุดสำหรับ Dataplex discovery

**ข้อดี (เมื่อพร้อม):**
- BQ tables ถูก ingest เข้า Dataplex catalog อัตโนมัติ
- ไม่ต้อง register/import อะไรเพิ่ม
- ใช้ infrastructure ที่มีอยู่แล้ว (BLMS REST catalog)

**ข้อเสีย:**
- ต้องรอ transaction/ team
- ต้องสร้าง BQ external table ทุกตัว (deploy.py หรือ terraform)
- Discovery เห็นเป็น "BQ table" ไม่ใช่ "Iceberg table"

---

### Option B: Dataplex Metadata Import API (effort ปานกลาง)

**Concept**: สร้าง JSONL file อธิบาย Iceberg tables → run import job → entries ปรากฏใน Dataplex

#### Step 1: สร้าง EntryType + AspectType (ทำครั้งเดียว)

```bash
# สร้าง EntryType
gcloud dataplex entry-types create iceberg-table \
  --project=PROJECT_ID \
  --location=asia-southeast1 \
  --display-name="Iceberg Table" \
  --description="Apache Iceberg table on GCS"

# สร้าง AspectType สำหรับ metadata
gcloud dataplex aspect-types create iceberg-metadata \
  --project=PROJECT_ID \
  --location=asia-southeast1 \
  --display-name="Iceberg Metadata" \
  --metadata-template-file=aspect_template.json
```

#### Step 2: เขียน JSONL import file

```json
{
  "entry": {
    "name": "projects/PROJECT_ID/locations/asia-southeast1/entryGroups/iceberg-tables/entries/member-tier",
    "entryType": "projects/PROJECT_ID/locations/asia-southeast1/entryTypes/iceberg-table",
    "entrySource": {
      "resource": "gs://the1-loyalty-data-stg-source/warehouse/source/member_tier",
      "system": "apache-iceberg",
      "platform": "gcs",
      "displayName": "member_tier",
      "description": "Member tier Iceberg table (source layer)"
    },
    "aspects": {
      "PROJECT_ID.asia-southeast1.iceberg-metadata": {
        "data": {
          "table_location": "gs://the1-loyalty-data-stg-source/warehouse/source/member_tier",
          "partition_spec": "ingestedTHDate (day)",
          "file_format": "parquet",
          "catalog": "the1-loyalty-data-source-stg",
          "namespace": "source"
        }
      }
    }
  },
  "updateMask": "entry.aspects,entry.entrySource",
  "aspectKeys": ["PROJECT_ID.asia-southeast1.iceberg-metadata"]
}
```

#### Step 3: Run import job

```python
from google.cloud import dataplex_v1


def import_iceberg_metadata(
    project_id: str,
    project_number: str,
    location: str,
    import_bucket: str,
) -> None:
    """Import Iceberg table metadata into Dataplex catalog."""
    client = dataplex_v1.CatalogServiceClient()

    metadata_job = dataplex_v1.MetadataJob()
    metadata_job.type_ = dataplex_v1.MetadataJob.Type.IMPORT
    metadata_job.import_spec = dataplex_v1.MetadataJob.ImportJobSpec(
        source_storage_uri=f"gs://{import_bucket}/dataplex-import/",
        scope=dataplex_v1.MetadataJob.ImportJobSpec.ImportJobScope(
            entry_groups=[
                f"projects/{project_id}/locations/{location}/entryGroups/iceberg-tables"
            ],
            entry_types=[
                f"projects/{project_id}/locations/{location}/entryTypes/iceberg-table"
            ],
        ),
        entry_sync_mode=dataplex_v1.MetadataJob.ImportJobSpec.SyncMode.FULL,
        aspect_sync_mode=dataplex_v1.MetadataJob.ImportJobSpec.SyncMode.INCREMENTAL,
    )

    request = dataplex_v1.CreateMetadataJobRequest(
        parent=f"projects/{project_number}/locations/{location}",
        metadata_job=metadata_job,
    )

    operation = client.create_metadata_job(request=request)
    response = operation.result()
    print(f"Import completed: {response.name}")
```

**ข้อดี:**
- Dataplex เห็นเป็น "Iceberg table" จริงๆ (custom entry type)
- ใส่ metadata ได้ครบ (partition, schema, location)
- Automate ผ่าน CI/CD ได้

**ข้อเสีย:**
- ต้อง setup EntryType + AspectType ก่อน
- ต้อง maintain JSONL file เมื่อเพิ่ม/ลบ table

---

### Option C: Dataplex Entry API (Direct Registration)

**Concept**: เรียก REST API ตรงๆ สร้าง entry ทีละตัว — เหมาะสำหรับ integrate ใน pipeline

```python
from google.cloud import dataplex_v1


def register_iceberg_table(
    project_id: str,
    location: str,
    entry_group: str,
    entry_id: str,
    table_location: str,
    display_name: str,
    description: str,
) -> None:
    """Register a single Iceberg table in Dataplex catalog."""
    client = dataplex_v1.CatalogServiceClient()

    entry = dataplex_v1.Entry(
        entry_type=f"projects/{project_id}/locations/{location}/entryTypes/iceberg-table",
        entry_source=dataplex_v1.EntrySource(
            resource=table_location,
            system="apache-iceberg",
            platform="gcs",
            display_name=display_name,
            description=description,
        ),
    )

    request = dataplex_v1.CreateEntryRequest(
        parent=f"projects/{project_id}/locations/{location}/entryGroups/{entry_group}",
        entry_id=entry_id,
        entry=entry,
    )

    response = client.create_entry(request=request)
    print(f"Created entry: {response.name}")


# Usage
register_iceberg_table(
    project_id="the1-loyalty-data-stg",
    location="asia-southeast1",
    entry_group="iceberg-tables",
    entry_id="member-tier",
    table_location="gs://the1-loyalty-data-stg-source/warehouse/source/member_tier",
    display_name="member_tier",
    description="Member tier Iceberg table (streaming, from Kafka)",
)
```

**gcloud equivalent:**
```bash
gcloud dataplex entries create member-tier \
  --project=the1-loyalty-data-stg \
  --location=asia-southeast1 \
  --entry-group=iceberg-tables \
  --entry-type=projects/the1-loyalty-data-stg/locations/asia-southeast1/entryTypes/iceberg-table \
  --entry-source-resource="gs://the1-loyalty-data-stg-source/warehouse/source/member_tier" \
  --entry-source-system="apache-iceberg" \
  --entry-source-platform="gcs" \
  --entry-source-display-name="member_tier"
```

---

### Option D: รอ Google เพิ่ม support (effort = 0)

Google อาจเพิ่ม Iceberg ใน Discovery ในอนาคต แต่ไม่มี timeline ที่ประกาศ

---

## 3. แนะนำสำหรับ Loyalty Data Project

| Layer | Table | วิธี Register |
|-------|-------|--------------|
| **Source (Iceberg)** | member_tier, tier_events_*, etc. | Option B (Metadata Import) หรือ C (Entry API) |
| **Refined (BQ native)** | refined.member_tier, refined.coupons, etc. | **ไม่ต้องทำ** — BQ tables auto-appear ใน Dataplex |
| **Public (BQ views)** | public.enriched_coupons_rewards, etc. | **ไม่ต้องทำ** — BQ views auto-appear ใน Dataplex |

**สรุป:**
- Refined + Public layer → **ไม่ต้องทำอะไร** (BQ auto-ingest)
- Source (Iceberg) layer → ใช้ **Option A** (BQ external table) หรือ **Option B** (Metadata Import)
- Option A ง่ายสุด เพราะมี BLMS infrastructure อยู่แล้ว

---

## 4. Dataplex REST API Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `{parent}/entryTypes` | POST | สร้าง entry type |
| `{parent}/aspectTypes` | POST | สร้าง aspect type |
| `{parent}/entryGroups` | POST | สร้าง entry group |
| `{parent}/entryGroups/*/entries` | POST | สร้าง entry |
| `{parent}/metadataJobs` | POST | Run bulk import |
| `{name}:searchEntries` | POST | ค้นหา entries |
| `{name}:lookupEntry` | GET | ดู entry เฉพาะ |

**Required IAM:**
- `dataplex.entries.create` — สร้าง entries
- `dataplex.entryTypes.create` — สร้าง entry types
- `storage.objectViewer` — อ่าน JSONL import files

## Sources

- [Dataplex Discover Data](https://cloud.google.com/dataplex/docs/discover-data)
- [Dataplex Import Metadata](https://cloud.google.com/dataplex/docs/import-metadata)
- [Dataplex Manage Entries](https://cloud.google.com/dataplex/docs/manage-entries)
- [BigLake Iceberg Tables](https://cloud.google.com/bigquery/docs/iceberg-tables)
- [BLMS Manage Metadata](https://cloud.google.com/bigquery/docs/manage-open-source-metadata)
- [Dataplex REST API Reference](https://cloud.google.com/dataplex/docs/reference/rest)
