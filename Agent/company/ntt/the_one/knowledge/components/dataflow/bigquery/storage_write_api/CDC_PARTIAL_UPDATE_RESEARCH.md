# BigQuery CDC Partial Column Update — Research & Solutions

## Problem Statement

BQ table มี columns: `A1, A2, B3, B4` (primary key: `A1`)

```
Topic A ส่ง: {A1: "001", A2: "value_a2", B3: "value_b3"}         ← ไม่มี B4
Topic B ส่ง: {A1: "001", B3: "value_b3_new", B4: "value_b4"}     ← ไม่มี A2
```

**ปัญหา**: CDC UPSERT จาก Topic B ทับ **ทั้ง row** → `A2` ที่มีค่าอยู่ถูก overwrite เป็น NULL

```
Before Topic B:  A1="001", A2="value_a2", B3="value_b3",     B4=NULL
After Topic B:   A1="001", A2=NULL,       B3="value_b3_new", B4="value_b4"  ← A2 หายไป!
```

## Root Cause

**Storage Write API CDC ทำ partial column update ไม่ได้** — เป็น **full row replacement** keyed by primary key

### ทำไมถึงทำไม่ได้?

1. **CDC UPSERT = row-level operation** — ไม่ใช่ column-level
2. **Proto message**: fields ที่ไม่ส่ง = default value (NULL สำหรับ nullable columns)
3. **`MissingValueInterpretation`** มีใน API แต่ไม่มี option "EXISTING_VALUE" (keep เดิม)
   - `NULL_VALUE` (default): missing = NULL
   - `DEFAULT_VALUE`: missing = column default expression (ไม่ใช่ค่าเดิม)
4. **CDC-enabled tables ใช้ DML ไม่ได้** (DELETE, UPDATE, MERGE ถูก block)

## Solutions

### Option A: Read-Before-Write (Merge in Pipeline)

**Concept**: ก่อน CDC write → query BQ เอา row เดิมมา → merge กับ data ใหม่ → write full row

```
Kafka message → FetchExistingRowDoFn (query BQ) → MergeDoFn → CDC Write
```

**Pros**: Real-time, ทำงานกับ CDC ปัจจุบันได้เลย
**Cons**: เพิ่ม BQ read cost, latency, race condition ระหว่าง topics

**ตัวอย่าง code**: ดู `bigquery_storage_enhanced_example.py` (Option A)

---

### Option B: Separate Tables + COALESCE View

**Concept**: แยก table ต่อ topic → สร้าง VIEW ที่ COALESCE columns

```sql
-- แต่ละ topic write ไป table ของตัวเอง (ไม่ใช้ CDC)
-- refined.coupons_from_created (append/overwrite from topic created)
-- refined.coupons_from_used    (append/overwrite from topic used)

-- VIEW รวม
CREATE VIEW refined.coupons_merged AS
SELECT
  COALESCE(a.A1, b.A1) AS A1,
  a.A2,                         -- มาจาก topic A เท่านั้น
  COALESCE(b.B3, a.B3) AS B3,  -- ใช้ค่าล่าสุดจาก B ถ้ามี
  b.B4                          -- มาจาก topic B เท่านั้น
FROM refined.coupons_from_created a
FULL OUTER JOIN refined.coupons_from_used b ON a.A1 = b.A1
```

**Pros**: ไม่มี data loss, แต่ละ topic เป็นอิสระ
**Cons**: หลาย tables, query cost, ข้อมูลอาจ stale

---

### Option C: GroupByKey Merge in Window

**Concept**: รวม data จากทุก topic → GroupByKey ใน window → merge partial rows → write full row

```
Topic A messages ─┐
                  ├─ Flatten → Key by PK → GroupByKey → MergeFn → CDC Write
Topic B messages ─┘
```

**Pros**: Single table, real-time, ไม่ต้อง query BQ
**Cons**: ต้อง data จากทุก topic มาภายใน window เดียวกัน, complex windowing

---

### Option D: DML MERGE (No CDC)

**Concept**: ปิด CDC → ใช้ scheduled MERGE query แทน

```sql
-- ปิด CDC (remove primary key + max_staleness)
-- เปลี่ยนเป็น append-only staging table

-- Scheduled MERGE (ทุก 5 นาที)
MERGE INTO refined.coupons target
USING staging.coupons_raw source
ON target.coupon_id = source.coupon_id
WHEN MATCHED THEN UPDATE SET
  A2 = COALESCE(source.A2, target.A2),  -- ← partial update!
  B3 = COALESCE(source.B3, target.B3),
  B4 = COALESCE(source.B4, target.B4)
WHEN NOT MATCHED THEN INSERT (A1, A2, B3, B4)
VALUES (source.A1, source.A2, source.B3, source.B4)
```

**Pros**: True partial column update (native BQ MERGE), simple
**Cons**: Not real-time (scheduled), ต้อง staging table

---

### Option E: Fill Missing Columns Before Write

**Concept**: เหมือน Option A แต่ query เฉพาะ columns ที่หาย (ไม่ใช่ทั้ง row)

```python
class FillMissingColumnsDoFn(beam.DoFn):
    """Query BQ for missing columns before CDC write."""

    def process(self, element):
        missing = [col for col in ALL_COLUMNS if col not in element or element[col] is None]
        if missing and element.get("primary_key"):
            existing = query_bq(pk=element["primary_key"], columns=missing)
            for col in missing:
                element[col] = existing.get(col)
        yield element
```

**Pros**: ลด data transfer (query เฉพาะ columns ที่ต้องการ)
**Cons**: BQ read cost, latency

---

## Recommendation

### Option A-E ข้อสรุป

Option A (Read-Before-Write) และ E (Fill Missing) **ไม่แนะนำ** — เปลือง BQ query cost ทุก element ไม่ต่างจาก JOIN
ทั้ง `bigquery.Client.query()` และ `beam.io.ReadFromBigQuery` เสีย cost BQ scan เหมือนกัน

| Use Case | Recommended |
|---|---|
| **Topics มาพร้อมกัน** | Option C (GroupByKey) |
| **ไม่ต้อง real-time** | Option D (DML MERGE) |
| **แยก ownership ต่อ topic** | Option B (Separate Tables) |

---

## Option F: Append + View/MTV (แนวทางใหม่ที่ discuss — น่าสนใจที่สุด)

**Concept**: ไม่ใช้ CDC เลย — Dataflow append ตรงๆ แล้วให้ View หรือ Materialized View จัดการ dedup + COALESCE

```
Kafka → Dataflow → APPEND to raw/staging table (ไม่ต้อง CDC, ไม่ต้อง primary key)
                                ↓
              View / Materialized View (dedup + COALESCE per PK)
                                ↓
                         Consumers query view
```

### ตัวอย่าง View (dedup + COALESCE)

```sql
-- Refined view: ดึง row ล่าสุดต่อ PK + COALESCE columns จากหลาย events
CREATE VIEW refined.coupons_view AS
WITH ranked AS (
  SELECT *,
    ROW_NUMBER() OVER (
      PARTITION BY coupon_id
      ORDER BY ingested_datetime DESC
    ) AS rn
  FROM refined.coupons_raw
)
SELECT
  coupon_id,
  -- COALESCE: ใช้ค่าล่าสุดที่ไม่ใช่ NULL
  FIRST_VALUE(status IGNORE NULLS) OVER (w) AS status,
  FIRST_VALUE(member_id IGNORE NULLS) OVER (w) AS member_id,
  FIRST_VALUE(reward_id IGNORE NULLS) OVER (w) AS reward_id,
  -- ... columns อื่นๆ
FROM refined.coupons_raw
WINDOW w AS (PARTITION BY coupon_id ORDER BY ingested_datetime DESC
             ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)
QUALIFY ROW_NUMBER() OVER (PARTITION BY coupon_id ORDER BY ingested_datetime DESC) = 1
```

### แบ่งตาม Table Type

| Table type | Write mode | Refined layer | เหตุผล |
|---|---|---|---|
| **Master/CDC** (coupons, rewards) | Append | **View** (dedup + COALESCE latest per PK) | ต้อง real-time, data เปลี่ยนบ่อย |
| **Historical/Transaction** (purchases, sales) | Append | **Materialized View** (snapshot periodic) | Query เร็ว, snapshot เวลาง่าย |

### Pros

- **ไม่ต้อง CDC** — ไม่ติด restriction (DML ใช้ได้, ไม่ต้อง primary key + max_staleness)
- **ไม่เสีย BQ read cost** — ไม่ต้อง query existing row
- **Partial update ทำได้** — COALESCE ใน view จัดการให้
- **Append-only = simple** — Dataflow แค่ write ไม่ต้องสนใจ state
- **Audit trail** — ทุก event ถูกเก็บ สามารถย้อนดูได้
- **MTV** — pre-compute สำหรับ consumer, auto-refresh

### Cons

- **View query cost** — scan ทั้ง table ทุกครั้งที่ query (ถ้าไม่ใช้ MTV)
- **Table size** — append ตลอด table โตเรื่อยๆ ต้องมี retention policy / partition expiration
- **MTV staleness** — non-incremental MTV (เพราะมี analytic functions) refresh ทั้ง view
- **Migration** — ต้องเปลี่ยนจาก CDC table → append table + view

### เมื่อไหร่ควรใช้ Option F vs CDC

| Criteria | ใช้ CDC (เดิม) | ใช้ Option F (Append + View) |
|---|---|---|
| ทุก topic ส่ง columns ครบ | ✅ | ไม่จำเป็น |
| Topics ส่ง columns ไม่ครบ (partial) | ❌ data loss | ✅ COALESCE จัดให้ |
| ต้องการ point-in-time query | ❌ CDC เก็บแค่ล่าสุด | ✅ append มีทุก event |
| Table size concern | ✅ เก็บแค่ล่าสุด | ❌ โตเรื่อยๆ (ต้อง expire) |
| DML operations needed | ❌ CDC block DML | ✅ ใช้ได้หมด |

## `MissingValueInterpretation` — ทำไมไม่ช่วย

```protobuf
enum MissingValueInterpretation {
  MISSING_VALUE_INTERPRETATION_UNSPECIFIED = 0;
  NULL_VALUE = 1;     // Missing field = NULL (default)
  DEFAULT_VALUE = 2;  // Missing field = column DEFAULT expression
}
```

- ใช้ได้เฉพาะเมื่อ **field ไม่อยู่ใน proto schema เลย** (ไม่ใช่ field มีแต่ค่าเป็น null)
- `DEFAULT_VALUE` ใช้ column default expression ของ BQ table (ไม่ใช่ "keep existing value")
- **ไม่มี option `EXISTING_VALUE`** — ถ้ามีจะแก้ปัญหานี้ได้เลย

## CDC-Enabled Table Restrictions

เมื่อ enable CDC (primary key + max_staleness) แล้ว:
- **ห้ามใช้ DML**: DELETE, UPDATE, MERGE ทำไม่ได้
- Write ได้เฉพาะผ่าน Storage Write API + `_CHANGE_TYPE` column
- ถ้าอยากกลับไปใช้ DML → ต้อง drop primary key + max_staleness ก่อน

## Sources

- [BigQuery Change Data Capture](https://cloud.google.com/bigquery/docs/change-data-capture)
- [BigQuery Storage Write API](https://cloud.google.com/bigquery/docs/write-api)
- [Beam WriteToBigQuery](https://beam.apache.org/documentation/io/built-in/google-bigquery/)
- [Storage Write API MissingValueInterpretation](https://cloud.google.com/bigquery/docs/reference/storage/rpc/google.cloud.bigquery.storage.v1#missingvalueinterpretation)
