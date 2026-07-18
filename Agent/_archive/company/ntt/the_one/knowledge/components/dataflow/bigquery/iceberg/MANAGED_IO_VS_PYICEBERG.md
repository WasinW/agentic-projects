# Managed IO (IcebergIO) vs PyIceberg: Research & Decision

> **Decision: ใช้ Managed IO ต่อ — ไม่เปลี่ยนเป็น PyIceberg**
> PyIceberg ไม่ช่วยเรื่อง Dataplex auto-lineage และเพิ่มปัญหา parallel write

## 1. สรุปปัญหา

Managed IO (IcebergIO) เป็น cross-language Java transform ที่ใช้ write Iceberg tables
Dataplex auto-lineage **ไม่ track** IcebergIO — คำถามคือ เปลี่ยนเป็น PyIceberg (native Python) จะช่วยได้มั้ย?

**คำตอบ: ไม่ได้** — ปัญหาไม่ใช่ cross-language แต่เป็น **IcebergIO ไม่มี code report lineage**

## 2. Root Cause ของ Lineage ไม่ทำงาน

Dataflow auto-lineage ทำงานโดย connector ต้อง call `Lineage.getSinks()` / `Lineage.getSources()` ใน Java code

### Connectors ที่ support lineage (Beam 2.63+):
- BigQueryIO, KafkaIO, BigtableIO, GCS FileIO, JDBC, Pub/Sub, Spanner

### IcebergIO: **ไม่มี lineage code**
- ไม่มี commit, PR, หรือ issue ใน Apache Beam ที่เพิ่ม lineage ให้ IcebergIO
- แม้จะรันเป็น pure Java pipeline ก็ยังไม่มี lineage เหมือนกัน
- **ไม่เกี่ยวกับ cross-language**

## 3. เปรียบเทียบ Managed IO vs PyIceberg

| Feature | Managed IO (IcebergIO) | PyIceberg in DoFn |
|---------|----------------------|-------------------|
| **Beam integration** | Native PTransform | Manual inside DoFn |
| **Parallel writes** | หลาย workers, coordinated commit | **Single-process only** — concurrent = crash |
| **Deduplication** | Built-in (skip committed files) | ไม่มี — retry = duplicate |
| **Snapshot management** | อัตโนมัติ ทุก triggering_frequency | Manual ทุก `append()` call |
| **Conflict resolution** | Internal Java Iceberg retry | ไม่มี — ต้องเขียน retry เอง |
| **BLMS REST catalog** | รองรับ | รองรับ |
| **Dataplex lineage** | **ไม่รองรับ** | **ไม่รองรับ** |
| **Performance** | Production-grade, autosharding | Single-threaded |

## 4. ปัญหาถ้าเปลี่ยนเป็น PyIceberg

### 4.1 ไม่ support Distributed Write

PyIceberg issue [#1751](https://github.com/apache/iceberg-python/issues/1751) — open feature request
- ไม่สามารถแยก "write data files" กับ "commit snapshot" ได้ใน public API
- `DataFile` objects serialize ข้าม process ไม่ได้ (partition metadata หาย)

### 4.2 Concurrent Write = Crash

PyIceberg issue [#1084](https://github.com/apache/iceberg-python/issues/1084):
```
CommitFailedException: branch main has changed: expected id [X], found [Y]
```
- หลาย Beam workers เรียก `table.append()` พร้อมกัน → crash
- ไม่มี built-in retry (issues #269, #819 ยังเปิดอยู่)

### 4.3 Snapshot Explosion

- ทุก `append()` = 1 snapshot commit
- Streaming pipeline = พัน snapshots ต่อชั่วโมง
- Iceberg performance แย่ลงเมื่อ snapshot มากเกินไป

### 4.4 ต้อง Rebuild ทุกอย่าง

ถ้าจะทำให้เทียบเท่า Managed IO ต้อง:
- Custom stateful DoFn with timer (buffer + batch commit)
- Snapshot coordinator (single writer)
- Retry logic with dedup detection
- = เขียน IcebergIO ใหม่ทั้งหมดเป็น Python

## 5. แนวทางแก้ Dataplex Auto-Lineage

### Option A: Custom Lineage API (Short-term, แนะนำ)

เพิ่ม DoFn ที่ report lineage ไป Dataplex Data Lineage API:

```python
class ReportLineageDoFn(beam.DoFn):
    """Report custom lineage event to Dataplex after Iceberg write."""

    def process(self, element):
        # Use Data Lineage API to report:
        # source: kafka://bootstrap/topic
        # target: iceberg://catalog/namespace.table
        lineage_client.create_lineage_event(...)
        yield element
```

### Option B: BigLake Table via BigQuery (Medium-term)

Iceberg tables ที่ register เป็น BigLake tables ใน BigQuery:
- BQ query ที่อ่าน BigLake Iceberg table → lineage ถูก track อัตโนมัติ
- ใช้ `bq_metadata_refresh` (Option B BQ table creation) ช่วย
- Dataplex governance apply ผ่าน BigLake integration

### Option C: Apache Beam Feature Request (Long-term)

File feature request บน [apache/beam](https://github.com/apache/beam/issues):
- ขอให้เพิ่ม `Lineage.getSinks()` ใน IcebergIO
- Reference: BigQueryIO (PR #31823), BigtableIO (PR #32068), KafkaIO (PR #32170)
- Related issues: [#33981](https://github.com/apache/beam/issues/33981) OpenLineage integration, [#36790](https://github.com/apache/beam/issues/36790) pluggable lineage

## 6. Conclusion

**ใช้ Managed IO ต่อ** — ไม่คุ้มกับการเปลี่ยน เพราะ:
1. Lineage ก็ไม่ได้ (ปัญหาอยู่ที่ Beam ไม่ใช่ lib ที่ใช้ write)
2. เสีย parallel write + dedup + snapshot management
3. ต้อง rebuild coordinator logic ทั้งหมด
4. Risk สูง — production streaming pipeline

**สำหรับ lineage**: ใช้ Custom Lineage API (Option A) + BigLake integration (Option B) แทน

## Sources

- [Dataflow Lineage Documentation](https://docs.cloud.google.com/dataflow/docs/guides/lineage)
- [Dataplex About Data Lineage](https://docs.cloud.google.com/dataplex/docs/about-data-lineage)
- [Managed I/O Connectors](https://beam.apache.org/documentation/io/managed-io/)
- [Dataflow Managed IO for Iceberg](https://docs.cloud.google.com/dataflow/docs/guides/managed-io-iceberg)
- [PyIceberg API](https://py.iceberg.apache.org/api/)
- [PyIceberg Distributed Write #1751](https://github.com/apache/iceberg-python/issues/1751)
- [PyIceberg Concurrent Write Failures #1084](https://github.com/apache/iceberg-python/issues/1084)
- [Beam OpenLineage Integration #33981](https://github.com/apache/beam/issues/33981)
- [Beam Pluggable Lineage #36790](https://github.com/apache/beam/issues/36790)
