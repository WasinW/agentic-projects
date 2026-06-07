# Iceberg Compaction Analysis: Managed IO vs PyIceberg vs Spark

> Date: 2026-03-22
> Context: Loyalty Data Project — streaming Dataflow pipelines writing Iceberg via Managed IO + BLMS REST Catalog
> Problem: Managed IO ไม่มี compaction built-in → small files สะสม → metadata bloat → CommitTable fail

---

## 1. ชี้แจง: Managed IO กับ Compaction — 2 ประโยคที่ดูย้อนแย้งแต่ถูกทั้งคู่

| ประโยค | หมายความว่า |
|---|---|
| "Managed IO ทำ compaction ไม่ได้" | IcebergIO มีแค่ `AppendFiles` — **ไม่มี `RewriteFiles` API** |
| "Compaction run ขณะ Managed IO write ได้" | **กระบวนการอื่น** (Spark) ทำ compaction ได้ **พร้อมกับ** ที่ Managed IO กำลัง append |

### หลักฐานจาก Iceberg Source Code

**Managed IO ใช้ `AppendFiles` เท่านั้น:**

จาก `AppendFilesToTables.java` (Apache Beam source):
```java
private void appendDataFiles(Table table, Iterable<FileWriteResult> fileWriteResults) {
    AppendFiles update = table.newAppend();
    for (FileWriteResult result : fileWriteResults) {
        DataFile dataFile = result.getDataFile(table.specs());
        update.appendFile(dataFile);
    }
    update.commit();
}
```

**Compaction ใช้ `RewriteFiles` (`REPLACE` operation):**

จาก `DataOperations.java` (Iceberg API):
```java
public static final String APPEND = "append";    // AppendFiles
public static final String REPLACE = "replace";  // RewriteFiles
```

**`APPEND` และ `REPLACE` ไม่ conflict กัน:**

จาก `MergingSnapshotProducer.java`:
```java
// REPLACE ไม่อยู่ใน set นี้ → ไม่ validate conflicting appends
private static final Set<String> VALIDATE_ADDED_FILES_OPERATIONS =
    ImmutableSet.of(DataOperations.APPEND, DataOperations.OVERWRITE);

// APPEND ไม่อยู่ใน set นี้ → ไม่ validate conflicting replaces
private static final Set<String> VALIDATE_DATA_FILES_EXIST_OPERATIONS =
    ImmutableSet.of(DataOperations.OVERWRITE, DataOperations.REPLACE, DataOperations.DELETE);
```

จาก `BaseRewriteFiles.java` validate():
```java
protected void validate(TableMetadata base, Snapshot parent) {
    validateReplacedAndAddedFiles();
    if (!replacedDataFiles.isEmpty()) {
        // เช็คแค่ว่า file ที่จะ replace ยังไม่ถูก delete
        // ไม่ได้เช็ค conflicting appends
        validateNoNewDeletesForDataFiles(base, startingSnapshotId, replacedDataFiles, parent);
    }
}
```

**สรุป:**
- `APPEND` เพิ่ม files ใหม่ (ไม่แตะ files เก่า)
- `REPLACE` สลับ files เก่า → files ใหม่ (ไม่แตะ files ที่กำลังถูก append)
- ทั้งสอง operate on **disjoint sets of files** → Iceberg optimistic concurrency ให้ทั้งสอง commit ผ่าน

**Ref:**
- Apache Beam IcebergIO source: `sdks/java/io/iceberg/src/main/java/org/apache/beam/sdk/io/iceberg/`
- Iceberg API source: `api/src/main/java/org/apache/iceberg/DataOperations.java`
- Iceberg core: `core/src/main/java/org/apache/iceberg/MergingSnapshotProducer.java`
- Iceberg spec: https://iceberg.apache.org/docs/latest/reliability/

---

## 2. PyIceberg ทำได้แค่ไหน?

| Feature | Managed IO | PyIceberg | PyIceberg ทดแทนได้? |
|---|---|---|---|
| **Parallel write** | หลาย workers, coordinated commit | **Single-process only** | **ไม่ได้** |
| **Dedup on retry** | มี (`shouldSkip` ใน `AppendFilesToTables`) | **ไม่มี** | **ไม่ได้** |
| **Streaming** | ได้ (`triggering_frequency`) | **ไม่ได้** | **ไม่ได้** |
| **Compaction** | **ไม่ได้** (ไม่มี `RewriteFiles`) | **ยังไม่ได้** (PR #3124 open, ยัง unmerged) | ไม่ได้ทั้งคู่ |
| **`overwrite()`** | ไม่มี | มี แต่ใช้ `OVERWRITE` op → **conflict กับ `APPEND` ได้** | **อันตราย** |

### PyIceberg Parallel Write — ทำไมไม่ได้

- `table.append(df)` = write + commit ใน 1 call
- ไม่มี API แยก "write data files" กับ "commit snapshot"
- หลาย workers เรียก `append()` พร้อมกัน → `CommitFailedException`
- PyIceberg issue [#1751](https://github.com/apache/iceberg-python/issues/1751) (distributed write) — **OPEN, ยังไม่มี solution**
- PyIceberg issue [#1084](https://github.com/apache/iceberg-python/issues/1084) (concurrent append crash) — **OPEN**

### PyIceberg Compaction — ยังไม่พร้อม

- PR [#3124](https://github.com/apache/iceberg-python/pull/3124) (`table.maintenance.compact()`) — **OPEN, ไม่ได้ merge**
- PR [#3131](https://github.com/apache/iceberg-python/pull/3131) (`.replace()` API) — **OPEN, ไม่ได้ merge**
- ปัจจุบันมีแค่ `expire_snapshots()` สำหรับ maintenance
- Workaround: `table.overwrite(df)` — แต่ใช้ `OVERWRITE` op ซึ่ง **conflict กับ APPEND ได้** (ทั้งสอง validate added files)

### สรุป: PyIceberg ทดแทน Managed IO ไม่ได้

ขาด parallel write, dedup, streaming — และ compaction ก็ยังไม่พร้อม

**Ref:**
- PyIceberg API: https://py.iceberg.apache.org/api/
- PyIceberg distributed write issue: https://github.com/apache/iceberg-python/issues/1751
- PyIceberg concurrent write issue: https://github.com/apache/iceberg-python/issues/1084
- PyIceberg compaction PR: https://github.com/apache/iceberg-python/pull/3124
- PyIceberg replace PR: https://github.com/apache/iceberg-python/pull/3131

---

## 3. Dataflow Daily Compaction Pipeline?

### Managed IO ทำ `replace` ไม่ได้

Managed IO มีแค่ `table.newAppend()` — ไม่มี config ให้เปลี่ยนเป็น `RewriteFiles` หรือ `OverwriteFiles`

จาก `AppendFilesToTables.java`: commit path เดียวคือ `AppendFiles update = table.newAppend()`

### ทางที่ทำได้จริงตอนนี้

#### แนะนำ: Spark `rewrite_data_files` บน Dataproc Serverless

```
Cloud Scheduler (daily 2AM BKK)
  → Dataproc Serverless batch job
    → CALL system.rewrite_data_files('source.table', strategy => 'binpack')
  → expire-snapshots --retain 365
```

**ทำไมแนะนำ:**
- ใช้ `REPLACE` operation → **ไม่ conflict** กับ Managed IO ที่กำลัง `APPEND`
- รัน concurrent กับ streaming pipeline ได้ปลอดภัย
- ไม่ต้อง maintain cluster (serverless)
- Iceberg optimistic concurrency จัดการ retry ให้
- Proven technology — standard Iceberg maintenance approach

**Spark command:**
```sql
CALL catalog.system.rewrite_data_files(
    table => 'source.member_tier',
    strategy => 'binpack',
    options => map('target-file-size-bytes', '134217728')  -- 128MB
)
```

**Dataproc Serverless batch:**
```bash
gcloud dataproc batches submit spark \
    --project=the1-loyalty-data-prod \
    --region=asia-southeast1 \
    --jars=gs://spark-lib/biglake/biglake-catalog-iceberg1.5.2-0.1.0-with-dependencies.jar \
    --class=org.apache.iceberg.spark.actions.RewriteDataFilesSparkAction \
    --properties="spark.sql.catalog.blms=org.apache.iceberg.spark.SparkCatalog,spark.sql.catalog.blms.catalog-impl=org.apache.iceberg.gcp.biglake.BigLakeCatalog,spark.sql.catalog.blms.gcp_project=the1-loyalty-data-prod,spark.sql.catalog.blms.gcp_location=asia-southeast1,spark.sql.catalog.blms.blms_catalog=the1-loyalty-data-source-prod"
```

### `BQ.REFRESH_ICEBERG` ไม่ใช่ compaction

**`BQ.REFRESH_EXTERNAL_METADATA_CACHE` แค่ refresh metadata cache ของ BQ** — ไม่ได้ rewrite Parquet files

จาก BQ docs:
> "you run the BQ.REFRESH_EXTERNAL_METADATA_CACHE system procedure to refresh the metadata cache"

- ไม่ merge small files
- ไม่สร้าง snapshot ใหม่
- ไม่ลด file count
- แค่ sync BQ metadata กับ Iceberg metadata ล่าสุด

**BQ managed Iceberg tables** มี "automatic storage optimization" — แต่ใช้ได้เฉพาะ tables ที่ BQ เป็นคน create/own write path ไม่ใช่ tables ที่ Managed IO write ผ่าน BLMS

**Ref:**
- BQ external metadata cache: https://cloud.google.com/bigquery/docs/external-data-sources
- BQ managed Iceberg tables: https://cloud.google.com/bigquery/docs/iceberg-tables

---

## 4. สรุป Decision Matrix

| Option | Compaction | Concurrent กับ Managed IO | Complexity | Status |
|---|---|---|---|---|
| **Spark `rewrite_data_files` (Dataproc Serverless)** | ได้ (REPLACE op) | **ปลอดภัย** (ไม่ conflict กับ APPEND) | Medium | **พร้อมใช้** |
| PyIceberg `overwrite()` | ได้ แต่ใช้ OVERWRITE op | **อันตราย** (conflict กับ APPEND) | Medium | ใช้ได้แต่ไม่แนะนำ |
| PyIceberg `compact()` (PR #3124) | จะได้ (REPLACE op) | จะปลอดภัย | Low | **ยังไม่ merge** |
| Managed IO | **ไม่ได้** | N/A | N/A | ไม่มี API |
| BQ.REFRESH_ICEBERG | **ไม่ใช่ compaction** | N/A | N/A | metadata only |
| Skip compaction + `expire-snapshots` | ไม่ compact แต่ลด metadata | N/A | **ต่ำสุด** | **พร้อมใช้** |

### แนะนำ

**Short-term** (ทำได้เลย): `expire-snapshots --retain 365` → ลด metadata bloat → แก้ CommitTable fail

**Medium-term**: Spark `rewrite_data_files` on Dataproc Serverless (daily schedule) + `expire-snapshots --retain 365`

**Long-term**: รอ PyIceberg PR #3124 merge → ใช้ `table.maintenance.compact()` (Python native, ไม่ต้อง Spark)

---

## 5. Iceberg Table Properties สำหรับลด Small Files (Prevention)

ตั้ง table properties ตอน create หรือ ALTER:

```
commit.manifest-merge.enabled: "true"   -- merge manifests ทุก commit
write.target-file-size-bytes: "134217728"  -- 128MB target file size
```

จาก config YAML:
```yaml
iceberg:
  table_properties:
    commit.manifest-merge.enabled: "true"
    write.target-file-size-bytes: "134217728"
```

**Note:** เป็น table creation properties — ต้อง ALTER สำหรับ tables ที่มีอยู่แล้ว

**Ref:**
- Iceberg table configuration: https://iceberg.apache.org/docs/latest/configuration/
- Iceberg maintenance: https://iceberg.apache.org/docs/latest/maintenance/
