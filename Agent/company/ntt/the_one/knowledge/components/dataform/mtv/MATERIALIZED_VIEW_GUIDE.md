# BigQuery Materialized View (MTV) Guide

## Overview

Materialized View (MTV) คือ view ที่ pre-compute และ cache ผลลัพธ์ไว้ — query เร็วกว่า view ปกติ เพราะไม่ต้องคำนวณใหม่ทุกครั้ง

## Materialized View มี 2 ประเภท

| | Incremental MTV | Non-Incremental MTV |
|---|---|---|
| **Refresh** | เฉพาะ data ที่เปลี่ยน (delta) | Recompute ทั้ง view |
| **LEFT JOIN** | **Preview** (มีข้อจำกัด) | **Full support** |
| **UNION ALL** | **Preview** | support |
| **HAVING** | ไม่ support | support |
| **Analytic functions** | ไม่ support | support |
| **Smart Tuning** | support (ยกเว้น LEFT JOIN/UNION ALL) | **ไม่ support** |
| **Config** | default | `allow_non_incremental_definition = true` + **ต้องมี `max_staleness`** |

**สำคัญ**:

- LEFT JOIN ใน Incremental → right-side table เปลี่ยน = ไม่สามารถ incremental refresh + disable smart tuning
- LEFT JOIN ใน Non-Incremental → full support แต่ refresh ทั้ง view ทุกครั้ง + ต้องระบุ `max_staleness`

## SQL Restrictions (Incremental MTV)

ห้ามใช้ features เหล่านี้:

- `LEFT JOIN` / `RIGHT JOIN` / `FULL OUTER JOIN`
- `UNION` / `UNION ALL`
- `HAVING`
- Window / Analytic functions (`ROW_NUMBER()`, `RANK()`, `LAG()`, etc.)
- Subqueries in SELECT
- `DISTINCT`
- Non-deterministic functions (`CURRENT_TIMESTAMP()`, `RAND()`, etc.)

## Auto-Refresh

| Setting | Value |
|---------|-------|
| Default refresh | 5-30 นาทีหลัง base table เปลี่ยน |
| Minimum frequency | 1 นาที |
| Maximum frequency | 7 วัน |
| Behavior | Best-effort (ไม่ guarantee exact timing) |

Manual refresh:
```sql
CALL BQ.REFRESH_MATERIALIZED_VIEW('project.dataset.materialized_view');
```

## Cost

- Auto-refresh: billed ที่ project ของ MTV
- Manual refresh: billed ที่ project ที่ run refresh job
- **Storage cost**: เก็บ data จริง ≠ view ที่ไม่มี storage cost
- **Benefit**: ลด compute cost สำหรับ query ที่ซ้ำบ่อย
- Monitor: `total_bytes_processed`, `total_slot_ms`

## Operational Restrictions

- MTV SQL **แก้ไขหลังสร้างไม่ได้** — ต้อง DROP แล้ว CREATE ใหม่
- ไม่สามารถ COPY, EXPORT, LOAD, WRITE, DML กับ MTV ตรงๆ
- ไม่สามารถ `CREATE OR REPLACE` — ต้อง DROP ก่อน
- Base tables ต้องอยู่ใน org เดียวกัน (หรือ project เดียวกัน)
- **CDC-enabled tables**: MTV ที่ ref CDC table จะไม่ได้ smart tuning

## Dataform Configuration

### Basic Syntax (.sqlx)

```sqlx
config {
  type: "view",
  materialized: true,
  schema: "refined",
  name: "my_mtv",
  tags: ["coupons"],
  description: "Basic materialized view.",
  bigquery: {
    additionalOptions: {
      enable_refresh: "true",
      refresh_interval_minutes: "30"
    }
  }
}

SELECT c.coupon_id, c.member_id
FROM ${ref("refined", "coupons")} c
```

### Non-Incremental (required for LEFT JOIN)

```sqlx
config {
  type: "view",
  materialized: true,
  schema: "refined",
  name: "enriched_coupons_rewards_mtv",
  description: "Non-incremental MTV with LEFT JOIN.",
  bigquery: {
    additionalOptions: {
      allow_non_incremental_definition: "true",
      enable_refresh: "true",
      refresh_interval_minutes: "30",
      max_staleness: 'INTERVAL "4" HOUR'
    }
  }
}

SELECT
  c.coupon_id,
  c.member_id,
  r.brand_code
FROM ${ref("refined", "coupons")} c
LEFT JOIN ${ref("refined", "rewards")} r
  ON c.reward_id = r.reward_id
```

**Note**: `allow_non_incremental_definition` ต้องมี `max_staleness` คู่กันเสมอ — ไม่งั้น BQ จะ reject

## When to Use MTV vs View

### Use MTV when:
- Query ถูกเรียกบ่อยจากหลาย consumer
- Data ไม่เปลี่ยนบ่อย (batch pipeline, วันละครั้ง)
- Query cost สูง (large table scan)
- ต้องการ query speed < 1 วินาที

### Use View when:
- Data เปลี่ยนบ่อย (streaming/CDC) → refresh cost สูง
- SQL ซับซ้อน (analytic functions, subqueries) ที่ MTV ไม่ support
- Storage cost เป็น concern
- ต้องการ `CREATE OR REPLACE` ง่ายๆ (MTV ต้อง DROP + CREATE)

## Concern สำหรับ Coupons Use Case

| Concern | Assessment |
|---------|-----------|
| LEFT JOIN (coupons + rewards) | ต้องใช้ non-incremental → refresh ทั้ง view ทุกครั้ง |
| CDC table (`refined.coupons`) | MTV จะไม่ได้ smart tuning |
| Streaming data | Refresh อาจไม่ทัน real-time use case |
| Schema changes | ต้อง DROP + CREATE ใหม่ทุกครั้งที่เปลี่ยน schema |
| Deploy | Dataform ไม่ support `CREATE OR REPLACE` สำหรับ MTV → deploy ต้อง handle DROP |

**Recommendation**: สำหรับ coupons ที่มี CDC + LEFT JOIN + schema เปลี่ยนบ่อย → **view ปกติเหมาะกว่า** ในตอนนี้ ค่อยเปลี่ยนเป็น MTV เมื่อ schema stable แล้ว

## Sources

- [Create materialized views | BigQuery](https://cloud.google.com/bigquery/docs/materialized-views-create)
- [Introduction to materialized views | BigQuery](https://cloud.google.com/bigquery/docs/materialized-views-intro)
- [Use materialized views | BigQuery](https://cloud.google.com/bigquery/docs/materialized-views-use)
- [Manage materialized views | BigQuery](https://cloud.google.com/bigquery/docs/materialized-views-manage)
- [Overview of logical and materialized views](https://cloud.google.com/bigquery/docs/logical-materialized-view-overview)
- [Create tables | Dataform](https://docs.cloud.google.com/dataform/docs/create-tables)
