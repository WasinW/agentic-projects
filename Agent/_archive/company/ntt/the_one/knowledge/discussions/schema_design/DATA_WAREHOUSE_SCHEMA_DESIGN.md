# Data Warehouse Schema Design: Star, Snowflake, Denormalization

> **Purpose**: Research + แนะนำ schema design patterns สำหรับ data warehouse
> โดยเฉพาะ use case ที่มี heavy joins ในชั้น refined/semantic (เช่น sales × lookups, coupon × rewards)
> เพื่อลด query cost และเพิ่ม performance ใน BigQuery
>
> **Target**: ทีม data engineering / data platform
> **Context**: The1 Data Platform — Sales, Coupons, Loyalty, Transactions

---

## Table of Contents

1. [Schema Design Fundamentals](#1-schema-design-fundamentals)
2. [Star Schema vs Snowflake vs Denormalization](#2-star-schema-vs-snowflake-vs-denormalization)
3. [BigQuery-Specific Considerations](#3-bigquery-specific-considerations)
4. [สถานะปัจจุบัน: Schema Analysis ของ Sales & Coupons](#4-สถานะปัจจุบัน-schema-analysis)
5. [ปัญหาที่เกิดจาก Schema Design ปัจจุบัน](#5-ปัญหาที่เกิดจาก-schema-design-ปัจจุบัน)
6. [แนวทางปรับปรุง: เลือก Pattern ตาม Use Case](#6-แนวทางปรับปรุง)
7. [Cost Analysis & Optimization](#7-cost-analysis--optimization)
8. [Decision Framework](#8-decision-framework)
9. [Implementation Roadmap](#9-implementation-roadmap)

---

## 1. Schema Design Fundamentals

### 1.1 Normalization vs Denormalization — ทำไมต้องเลือก?

ใน OLTP (transactional database) เรา normalize เพื่อลด data redundancy:
```
3NF: ทุก column ขึ้นกับ primary key, the whole key, and nothing but the key
```

แต่ใน **data warehouse (OLAP)** วัตถุประสงค์ต่างกัน:

| เป้าหมาย | OLTP (Normalized) | OLAP (Data Warehouse) |
|-----------|-------------------|----------------------|
| Optimize for | Write speed (INSERT/UPDATE) | Read speed (SELECT/JOIN) |
| Redundancy | ลดให้น้อยที่สุด | ยอมรับได้ ถ้า query เร็วขึ้น |
| Join ตอน query | น้อย (app ดึงทีละ table) | เยอะ (analytics ต้อง cross-table) |
| Schema change | บ่อย (app evolves) | ไม่บ่อย (stable reporting) |
| Cost driver | Storage + write IOPS | **Query scan volume** (BQ) |

**ข้อสรุป**: ใน data warehouse, **denormalization ไม่ใช่ anti-pattern** — มันเป็น optimization technique ที่ต้องเลือกใช้ให้เหมาะกับ use case

### 1.2 สาม Patterns หลัก

```
┌────────────────────────────────────────────────────────────────┐
│                    Schema Design Spectrum                       │
│                                                                │
│  Normalized                                    Denormalized    │
│  (3NF/Snowflake)          Star Schema         (Flat/Wide)      │
│  ◄──────────────────────────┼──────────────────────────────►   │
│  Many tables, many joins    │                  1 giant table   │
│  Low redundancy             │                  High redundancy │
│  High query complexity      │                  Low query cost  │
│  Easy maintenance           │                  Hard maintenance│
└────────────────────────────────────────────────────────────────┘
```

---

## 2. Star Schema vs Snowflake vs Denormalization

### 2.1 Star Schema

```
                    ┌──────────────┐
                    │  dim_member   │
                    │  member_id    │
                    │  member_name  │
                    │  tier_code    │
                    └──────┬───────┘
                           │
┌──────────────┐    ┌──────┴───────┐    ┌──────────────┐
│  dim_partner  │    │  fact_sales   │    │  dim_product  │
│  partner_code ├────┤  receipt_no   ├────┤  sku          │
│  partner_name │    │  member_id    │    │  product_name │
│  category     │    │  partner_code │    │  category     │
└──────────────┘    │  branch_code  │    └──────────────┘
                    │  sku          │
                    │  quantity     │    ┌──────────────┐
                    │  amount       ├────┤  dim_store    │
                    │  trans_date   │    │  branch_code  │
                    └──────────────┘    │  branch_name  │
                                       │  province     │
                                       └──────────────┘
```

**หลักการ**:
- **Fact table** ตรงกลาง: มี measures (numbers) + foreign keys ไป dimensions
- **Dimension tables** รอบนอก: มี descriptive attributes
- **Join depth = 1**: Fact JOIN Dim เสมอ (ไม่มี Dim JOIN Dim)

**Pros**:
- Query เข้าใจง่าย (`fact JOIN dim ON key`)
- BQ optimizer handle ได้ดี (broadcast join สำหรับ small dims)
- Dimension เปลี่ยนอิสระจาก fact (เช่น branch เปลี่ยนชื่อ → update dim_store เท่านั้น)
- BI tools (Looker, Tableau) ชอบ star schema (auto-detect relationships)

**Cons**:
- ยังต้อง JOIN ทุกครั้งที่ query (cost ตาม scan volume)
- Dimension tables ต้อง maintain (SCD — Slowly Changing Dimensions)

**เมื่อไหร่ควรใช้**:
- Dimension data เปลี่ยนบ่อย (เช่น partner เพิ่ม/ลด branches ทุกสัปดาห์)
- หลาย fact tables share dimension เดียวกัน
- BI tools ต้องการ star schema structure
- มี data governance ที่ต้อง single source of truth ต่อ dimension

### 2.2 Snowflake Schema

```
┌──────────────┐    ┌──────────────┐
│  dim_province │    │  dim_region   │
│  province_id  ├────┤  region_id    │
│  province_name│    │  region_name  │
│  region_id    │    └──────────────┘
└──────┬───────┘
       │
┌──────┴───────┐    ┌──────────────┐    ┌──────────────┐
│  dim_store    │    │  fact_sales   │    │  dim_category │
│  branch_code  ├────┤  receipt_no   ├────┤  category_id  │
│  branch_name  │    │  branch_code  │    │  category_name│
│  province_id  │    │  sku          │    │  dept_id      │
└──────────────┘    │  quantity     │    └──────┬───────┘
                    │  amount       │           │
                    └──────────────┘    ┌──────┴───────┐
                                       │  dim_dept     │
                                       │  dept_id      │
                                       │  dept_name    │
                                       └──────────────┘
```

**หลักการ**:
- เหมือน Star แต่ **Dimension ถูก normalize ต่ออีกชั้น** (dim → sub-dim)
- Join depth > 1: Fact → Dim → Sub-dim

**Pros**:
- Storage ประหยัดที่สุด (ไม่มี redundancy)
- Data integrity สูงสุด (1 place to update)
- เหมาะกับ dimension hierarchy ที่ซ้อนกันลึก

**Cons**:
- **Query cost สูง**: ทุก query ต้อง multi-hop JOIN
- BQ ชาร์จ per bytes scanned → **ยิ่ง JOIN เยอะ ยิ่งแพง**
- Query complexity สูง (3-4 level JOIN chains)
- BI tools ส่วนใหญ่ไม่ support snowflake ดี

**เมื่อไหร่ควรใช้**:
- Dimension hierarchy ลึก + เปลี่ยนบ่อยมาก (เช่น organizational hierarchy)
- Storage cost เป็น constraint สำคัญ (ไม่ค่อยเป็นใน BQ)
- Query frequency ต่ำ (ad-hoc analysis ไม่กี่ครั้ง/วัน)

> **สำหรับ BigQuery**: Snowflake schema **ไม่แนะนำ** ในเกือบทุก use case
> เพราะ BQ charge per scan — JOIN หลายชั้นแพงกว่า denormalized table ที่ scan ครั้งเดียว

### 2.3 Denormalization (Flat/Wide Table)

```
┌───────────────────────────────────────────────────────────────┐
│                     flat_sales_complete                        │
│                                                               │
│  receipt_no, transaction_date, member_id, member_name,        │
│  member_tier, partner_code, partner_name, partner_category,   │
│  branch_code, branch_name, province, region,                  │
│  sku, product_name, product_category, product_dept,           │
│  quantity, unit_price, subtotal, discount,                    │
│  payment_type, card_bin, issuer_bank,                         │
│  sales_channel, sales_channel_group,                          │
│  etl_updated_date                                             │
│                                                               │
│  Partition: transaction_date (DAY)                            │
│  Clustering: partner_code, member_id, branch_code             │
└───────────────────────────────────────────────────────────────┘
```

**หลักการ**:
- **ทุกอย่างอยู่ใน table เดียว** — ไม่ต้อง JOIN เลย
- Dimension attributes ถูก copy ลง fact table โดยตรง

**Pros**:
- **Query cost ต่ำสุด**: scan 1 table, 0 JOIN
- **Query simple**: `SELECT ... FROM flat_sales WHERE partner_code = 'CDS'`
- **Performance ดีที่สุด**: BQ scan columnar → เลือกแค่ columns ที่ต้องการ
- BI tools ทำงานได้ง่ายที่สุด

**Cons**:
- **Data redundancy สูง**: partner_name ซ้ำทุก row (แต่ BQ compression ช่วยได้มาก)
- **Maintenance ยาก**: ถ้า partner เปลี่ยนชื่อ → ต้อง backfill ทุก row (หรือยอมรับ historical name)
- **Write amplification**: ต้อง resolve ทุก dimension ตอน ingest → pipeline ซับซ้อนขึ้น
- **Data freshness**: ถ้า dimension เปลี่ยน → ต้อง re-process fact rows ที่อ้างอิง dimension นั้น

**เมื่อไหร่ควรใช้**:
- Query frequency สูง (dashboard refresh ทุก 5 นาที)
- Dimension data เปลี่ยนไม่บ่อย (เช่น partner list, branch list)
- Cost optimization สำคัญมาก (BQ on-demand pricing)
- Downstream consumers ต้องการ simple table (ML features, exports)

### 2.4 Hybrid: Star + Selective Denormalization (แนะนำ)

```
                    ┌──────────────┐
                    │  dim_member   │  ← shared dim (used by many facts)
                    └──────┬───────┘
                           │
┌──────────────┐    ┌──────┴────────────────────────────────┐
│  dim_partner  │    │  fact_sales_enriched                   │
│  (shared)     ├────┤  receipt_no, trans_date, member_id    │
└──────────────┘    │  partner_code, branch_code             │
                    │  sku, quantity, amount                  │
                    │                                        │
                    │  ── Denormalized from lookups ──        │
                    │  sales_channel (resolved)               │
                    │  sales_channel_group                    │
                    │  branch_name, province (from dim_store) │
                    │  issuer_bank (from creditcard_master)   │
                    │  product_name (from dim_product)        │
                    └────────────────────────────────────────┘
```

**หลักการ**:
- **Fact table + frequently-joined dims denormalized ลงไป**
- **Shared dims ยังแยก** (เพื่อ reuse ข้าม fact tables)
- **Query ลด JOIN** จาก 5-8 เหลือ 0-2

**Pros**:
- Best of both worlds: low query cost + maintainable dims
- BI tools ยังเข้าใจ (some joins, but not many)
- Dimension ที่เปลี่ยนไม่บ่อย → denormalize (branch name, partner name)
- Dimension ที่เปลี่ยนบ่อย → ยังแยก (member tier, coupon status)

**เมื่อไหร่ควรใช้**:
- **เกือบทุก use case ใน BigQuery** ← แนะนำ
- มี mix ของ slowly-changing dims + frequently-changing dims
- ต้อง balance ระหว่าง query cost กับ maintenance

---

## 3. BigQuery-Specific Considerations

### 3.1 BQ Pricing Model กำหนด Schema Design

```
BQ On-Demand Pricing:
  Query cost = $6.25 per TB scanned
  Storage cost = $0.02 per GB/month (active)

ดังนั้น:
  Denormalized table ใช้ storage เพิ่ม (redundancy) → +$0.02/GB/month
  แต่ query ลด JOIN → scan น้อยลง → -$6.25/TB ต่อ query

  ตัวอย่าง:
  Query 1: SELECT ... FROM fact JOIN dim1 JOIN dim2 JOIN dim3
    → Scan: fact (10GB) + dim1 (500MB) + dim2 (200MB) + dim3 (100MB) = 10.8GB
    → Cost: 10.8GB × $6.25/TB = $0.0675/query

  Query 2: SELECT ... FROM fact_denormalized
    → Scan: fact_denormalized (11GB) — เพิ่มขึ้นจาก redundancy
    → Cost: 11GB × $6.25/TB = $0.06875/query

  ดูเหมือนใกล้เคียง... แต่:
  → Query 1 ต้อง JOIN = shuffle = slot time สูง = ช้ากว่า
  → Query 2 ไม่ JOIN = fast columnar scan = เร็วกว่า
  → ถ้า query 100 ครั้ง/วัน: Query 1 = $6.75/day, Query 2 = $6.875/day
  → Cost difference น้อยมาก แต่ speed difference มาก
```

**สรุป**: ใน BQ, **storage ถูกมาก** ($0.02/GB) เทียบกับ **query scan** ($6.25/TB)
→ Denormalize ได้เลย ถ้าลด JOIN ได้

### 3.2 Columnar Storage + Compression

```
BQ เก็บ data เป็น columnar format:

┌─────────────┬─────────────┬─────────────┬─────────────┐
│ partner_code│ branch_code │ branch_name │ province    │
├─────────────┼─────────────┼─────────────┼─────────────┤
│ CDS         │ 001         │ Central     │ Bangkok     │
│ CDS         │ 001         │ Central     │ Bangkok     │  ← ซ้ำ! แต่ BQ
│ CDS         │ 001         │ Central     │ Bangkok     │  ← compress ได้
│ CDS         │ 002         │ Chidlom     │ Bangkok     │  ← ดีมาก
│ B2S         │ 101         │ Siam        │ Bangkok     │  ← (dictionary
│ B2S         │ 101         │ Siam        │ Bangkok     │  ←  encoding)
└─────────────┴─────────────┴─────────────┴─────────────┘

branch_name ซ้ำกันเป็นล้าน rows → BQ compress เหลือ bytes
→ Redundancy จาก denormalization ไม่เพิ่ม storage มากเท่าที่คิด
```

### 3.3 Partitioning + Clustering Strategy

```
Partition: ลด scan volume ด้วยการแบ่ง data ตามเวลา
Clustering: เรียง data ใน partition ตาม columns ที่ query บ่อย

สำหรับ sales:
  PARTITION BY transaction_date (DAY)
  CLUSTER BY partner_code, member_id, branch_code

  Query: WHERE transaction_date BETWEEN '2026-03-01' AND '2026-03-31'
           AND partner_code = 'CDS'
  → BQ scan: เฉพาะ March partitions + CDS cluster blocks
  → ลด scan 90%+ เทียบกับ full table scan
```

**กฎสำคัญ**:
1. **Partition column = ใน WHERE clause ของทุก query** (ส่วนใหญ่ = transaction_date)
2. **Cluster columns = ใน WHERE + JOIN clause** (max 4 columns, order by cardinality ต่ำ→สูง)
3. **อย่า partition + cluster ด้วย column เดียวกัน**

### 3.4 Materialized Views — Pre-computed JOINs

```sql
-- Materialized View: pre-compute ผล JOIN ไว้
CREATE MATERIALIZED VIEW `project.semantic.enriched_coupons_mtv`
OPTIONS (
  enable_refresh = true,
  refresh_interval_minutes = 30,
  max_staleness = INTERVAL "4" HOUR
)
AS
SELECT c.*, r.reward_internal_name, r.partner_code, ...
FROM `project.refined.coupons` c
LEFT JOIN `project.refined.rewards` r ON c.reward_id = r.reward_id;
```

**Pros**:
- BQ auto-maintains (incremental refresh ถ้าเป็น inner join + append-only)
- Query automatic rewrite: query ที่ match pattern → ใช้ MTV แทน base table
- ไม่ต้อง maintain ETL เพิ่มเติม

**Cons**:
- **LEFT JOIN + CDC ทำ incremental refresh ไม่ได้** → full refresh ทุกครั้ง
- Refresh cost = cost ของ full JOIN query ทุก interval
- Max staleness = data delay ที่ยอมรับได้

**เมื่อไหร่ควรใช้**:
- JOIN pattern ซ้ำกันบ่อย (dashboard ดึง 100+ ครั้ง/วัน)
- Base tables ไม่ใหญ่มาก (< 100GB total) → refresh cost ไม่สูง
- ยอมรับ staleness ได้ (30 min - 4 hours)

### 3.5 Nested/Repeated Fields — BQ Native Denormalization

```sql
-- แทนที่จะมี 3 tables: receipt, sku, tender
-- สามารถ nest เป็น 1 table:
CREATE TABLE `project.semantic.sales_complete` (
  receipt_number STRING,
  transaction_date DATE,
  member_id STRING,
  partner_code STRING,
  total_price NUMERIC,

  -- Nested: items per receipt
  items ARRAY<STRUCT<
    line_number STRING,
    sku STRING,
    product_name STRING,
    quantity NUMERIC,
    unit_price NUMERIC,
    subtotal NUMERIC
  >>,

  -- Nested: payments per receipt
  tenders ARRAY<STRUCT<
    payment_type STRING,
    amount NUMERIC,
    reference_number STRING,
    issuer_bank STRING
  >>
)
PARTITION BY transaction_date
CLUSTER BY partner_code, member_id;
```

**Pros**:
- **0 JOINs** สำหรับ receipt + items + tenders query
- BQ ยังเป็น columnar → scan เฉพาะ nested fields ที่ต้องการ
- Natural 1:N relationship → ไม่มี fan-out (ไม่ต้อง GROUP BY กลับ)
- **BI tools สมัยใหม่** (Looker, BigQuery BI Engine) support nested fields

**Cons**:
- UNNEST() syntax ซับซ้อนกว่า JOIN
- ไม่ทุก BI tool support ARRAY/STRUCT
- Update nested fields = replace entire array
- Max nested depth = 15 levels, max record size = 10MB

**เมื่อไหร่ควรใช้**:
- **1:N relationship ที่ query ด้วยกันเสมอ** (receipt + items)
- N ไม่ใหญ่เกินไป (< 1000 items per parent)
- Consumers support nested (BQ SQL, Looker, Python/pandas)

---

## 4. สถานะปัจจุบัน: Schema Analysis

### 4.1 Sales Collector — Current Schema

```
REFINED LAYER (3 tables, Star-ish):
┌────────────────────────┐
│  sales_receipt (header) │  61 columns, PK = composite 6 fields
│  Partition: trans_date  │  Clustering: partner, member, branch
├────────────────────────┤
│  sales_sku (items)     │  64 columns, PK = composite 7 fields
│  1 receipt → N items   │  Clustering: partner, sku, member
├────────────────────────┤
│  sales_tender (pay)    │  57 columns, PK = composite 8 fields
│  1 receipt → M pays    │  Clustering: partner, payment_type, member
└────────────────────────┘

LOOKUP/REFERENCE (8 tables):
  sales_channel_branch    (partner_code + branch_code → sales_channel_id)
  sales_channel_tender    (partner_code + tender_type → sales_channel_id)
  sales_channel_product   (partner_code + sku → sales_channel_id)
  sales_channel_sap       (partner_code + sap_channel → sales_channel_id)
  sales_channel_code      (sales_channel_code → sales_channel_id)
  sales_info              (translator_id → sales_channel_id + rank)
  creditcard_master       (rangecodestart/end → issuer_bank)
  sales_channel_partner   (sales_channel_id → partner/assist channel)

SEMANTIC LAYER (Dataform views):
  public.sales_receipt  = refined.sales_receipt
                          LEFT JOIN public.companies_branch_brand_cg_location
                          + CASE logic (channel_group, partner_code_group, crc_flag)
  public.sales_sku      = passthrough
  public.sales_tender   = passthrough
```

**ปัญหาที่สังเกต**:
1. **Receipt header columns ซ้ำใน 3 tables** — receipt, sku, tender ทุกตัวมี 19 header fields ซ้ำกัน
2. **Sales channel already resolved ใน pipeline** (6-level priority chain) → ดีมาก ไม่ต้อง JOIN ตอน query
3. **Semantic layer ยัง JOIN companies** ทุกครั้งที่ query public.sales_receipt
4. **3 tables ยังต้อง JOIN กัน** ถ้าต้องการ receipt + items + payments ในคราวเดียว

### 4.2 Coupons Collector — Current Schema

```
REFINED LAYER (1 table):
┌────────────────────────┐
│  refined.coupons       │  34 columns, PK = coupon_id
│  Partition: acquired_dt│  Clustering: member_id, status
└────────────────────────┘

ENRICHMENT VIEWS:
┌─────────────────────────────────────────────┐
│  refined.enriched_coupons_rewards (VIEW)     │  105+ columns
│  = coupons LEFT JOIN rewards ON reward_id    │  ← HEAVY: 34 + 74 columns
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  enriched_coupons_rewards_mtv (MAT. VIEW)    │  Same as above
│  Refresh: 30 min, Staleness: 4 hr           │  ← Full refresh (LEFT JOIN)
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  public.enriched_coupons_rewards (VIEW)      │  47 columns (subset)
│  = refined.enriched_coupons_rewards → select │
└─────────────────────────────────────────────┘
```

**ปัญหาที่สังเกต**:
1. **105+ columns** ใน enriched view — ส่วนใหญ่ query ใช้แค่ 10-20 columns
2. **LEFT JOIN ทำ incremental refresh ไม่ได้** → MTV refresh = full query ทุก 30 นาที
3. **rewards data เปลี่ยนไม่บ่อย** (master data) → ควร denormalize ลง coupons ได้

### 4.3 Cross-Domain Joins (ปัญหาใหญ่ที่สุดที่อาจเกิดขึ้น)

```
Scenario: BI ต้องการ "Sales + Coupons + Member Tier"

Query:
  SELECT s.receipt_number, s.total_price,
         c.coupon_code, c.redemption_value,
         m.tier_code
  FROM public.sales_receipt s
  LEFT JOIN public.enriched_coupons_rewards c
    ON s.member_id = c.member_id
    AND s.transaction_date BETWEEN c.validity_start AND c.validity_end
  LEFT JOIN refined.member_tier m
    ON s.member_id = m.member_id

  → sales_receipt: 100M+ rows
  → enriched_coupons: 50M+ rows
  → member_tier: 10M+ rows
  → JOIN: 100M × 50M ← MASSIVE SCAN + SHUFFLE
  → Cost: $$$ per query
```

**นี่คือ transaction × transaction join ที่คุณพูดถึง — cost พุ่งมาก**

---

## 5. ปัญหาที่เกิดจาก Schema Design ปัจจุบัน

### 5.1 ปัญหาเรียงตาม Impact

| # | ปัญหา | Impact | ตรงไหน |
|---|--------|--------|--------|
| 1 | **Receipt header ซ้ำ 3 tables** | Storage waste + JOIN ถ้าต้อง combine | sales_receipt/sku/tender |
| 2 | **Semantic view JOIN companies ทุก query** | Query cost × N queries/day | public.sales_receipt |
| 3 | **Coupons × Rewards = 105+ columns** | Scan 105 columns แม้ใช้แค่ 10 | enriched_coupons_rewards |
| 4 | **MTV full refresh ทุก 30 min** | Refresh cost = full JOIN cost | enriched_coupons_rewards_mtv |
| 5 | **Cross-domain JOIN ไม่มี pre-built table** | Ad-hoc = expensive scan | sales × coupons × members |
| 6 | **sales_sku + tender แยกจาก receipt** | 2 extra JOINs ทุกครั้งที่ต้อง combine | semantic layer queries |

### 5.2 Cost Estimation (ถ้า BQ On-Demand)

```
สมมติ:
  sales_receipt: 50GB (100M rows)
  sales_sku: 200GB (500M rows, 5 items/receipt avg)
  sales_tender: 80GB (200M rows, 2 payments/receipt avg)
  coupons: 20GB (50M rows)
  rewards: 2GB (500K rows)
  companies_branch: 100MB

Query 1: "Sales performance by partner" (daily dashboard, 50 queries/day)
  → Scan: sales_receipt full + companies_branch = 50.1GB
  → Cost: 50.1GB × $6.25/TB × 50 = $15.66/day

Query 2: "Sales + SKU + Payment analysis" (weekly report)
  → Scan: receipt + sku + tender = 330GB (JOIN 3 tables)
  → Cost: 330GB × $6.25/TB = $2.0625/query

Query 3: "Coupon redemption × Sales" (monthly analysis)
  → Scan: sales_receipt + enriched_coupons = 50GB + 20GB + 2GB = 72GB
  → Cost: 72GB × $6.25/TB = $0.45/query
  → แต่ถ้า date range ไม่ partition-prune ดี → could be 10x

Query 4: Materialized View refresh (ทุก 30 นาที)
  → Scan: coupons + rewards = 22GB × 48 times/day = 1,056GB/day
  → Cost: 1,056GB × $6.25/TB = $6.60/day (just for MTV refresh!)
```

---

## 6. แนวทางปรับปรุง

### 6.1 Sales: Hybrid Star + Selective Denormalization

**แนวทาง: Denormalize companies info ลง receipt ตอน ingest**

```
ปัจจุบัน:
  public.sales_receipt = refined.sales_receipt JOIN companies (every query)

แนะนำ:
  refined.sales_receipt ← denormalize branch_name, province, region ลงตอน pipeline
  public.sales_receipt = refined.sales_receipt (no join needed!)
```

**Implementation**:
```python
# ใน pipeline: resolve branch_name, province, region จาก companies lookup
# แล้วใส่ลง refined.sales_receipt ตรงๆ (เหมือนที่ทำ sales_channel แล้ว)

# เพิ่ม columns ใน refined.sales_receipt:
# - branch_name_en (from companies_branch)
# - province (from companies_branch)
# - region (from companies_branch)
# - store_cluster (from companies_branch)
```

**ผลลัพธ์**:
- ลด 1 JOIN ต่อ query × 50 queries/day
- companies data เปลี่ยนไม่บ่อย (master data) → denormalize ปลอดภัย
- ถ้า companies เปลี่ยน → refresh cache → new records ได้ค่าใหม่ (historical ไม่ต้อง backfill)

### 6.2 Sales: Nested STRUCT สำหรับ Semantic Layer

**แนวทาง: สร้าง pre-joined table ด้วย ARRAY<STRUCT>**

```sql
-- Option A: Materialized Table (scheduled rebuild)
CREATE OR REPLACE TABLE `project.semantic.sales_complete`
PARTITION BY transaction_date
CLUSTER BY partner_code, member_id
AS
SELECT
  r.*,

  -- Nested items
  ARRAY(
    SELECT AS STRUCT
      s.line_number, s.sku, s.quantity, s.unit_price,
      s.subtotal_price, s.net_subtotal_price, s.sales_channel_main
    FROM `project.refined.sales_sku` s
    WHERE s.receipt_number = r.receipt_number
      AND s.partner_code = r.partner_code
      AND s.branch_code = r.branch_code
      AND s.transaction_date = r.transaction_date
  ) AS items,

  -- Nested tenders
  ARRAY(
    SELECT AS STRUCT
      t.payment_type, t.amount, t.reference_number, t.issuer_bank
    FROM `project.refined.sales_tender` t
    WHERE t.receipt_number = r.receipt_number
      AND t.partner_code = r.partner_code
      AND t.branch_code = r.branch_code
      AND t.transaction_date = r.transaction_date
  ) AS tenders

FROM `project.refined.sales_receipt` r;
```

**Query ง่ายขึ้นมาก**:
```sql
-- Before: 3-table JOIN
SELECT r.receipt_number, r.total_price,
       s.sku, s.quantity,
       t.payment_type, t.amount
FROM sales_receipt r
JOIN sales_sku s ON r.receipt_number = s.receipt_number AND ...
JOIN sales_tender t ON r.receipt_number = t.receipt_number AND ...
WHERE r.transaction_date = '2026-03-27';

-- After: 1-table query with UNNEST
SELECT receipt_number, total_price,
       item.sku, item.quantity,
       tender.payment_type, tender.amount
FROM `semantic.sales_complete`,
  UNNEST(items) AS item,
  UNNEST(tenders) AS tender
WHERE transaction_date = '2026-03-27';
```

**Pros**:
- 0 JOINs → fast scan
- Natural parent-child structure
- BI Engine support UNNEST

**Cons**:
- ต้อง rebuild table (scheduled job) → staleness
- UNNEST syntax ต้อง educate users

### 6.3 Coupons: Selective Denormalization ลง refined.coupons

**แนวทาง: Denormalize key reward fields ลง coupons ตอน pipeline**

```
ปัจจุบัน:
  refined.coupons (34 cols) LEFT JOIN refined.rewards (74 cols) = 105+ cols enriched view

แนะนำ:
  refined.coupons (34 + 10 key reward cols = 44 cols)
  → Denormalize เฉพาะ fields ที่ query บ่อย:
    - reward_internal_name
    - partner_code (from reward)
    - exchange_rate
    - global_quota_total_available
    - global_quota_remaining
    - financial_information_discount_type
    - financial_information_discount_value
    - eligibility_tiers
    - redeemable
    - outcome_type
```

**ผลลัพธ์**:
- enriched view ลด columns: 105 → 44 (scan ลดมาก)
- หลาย queries ไม่ต้อง JOIN rewards เลย (ข้อมูลอยู่ใน coupons แล้ว)
- MTV ยังมีไว้สำหรับ query ที่ต้องการ full reward detail (74 cols)
- **MTV refresh ถูกลง** เพราะ query ที่ไม่ต้อง full rewards ไม่ trigger MTV

### 6.4 Cross-Domain: Pre-built Aggregate Tables

**แนวทาง: สร้าง aggregate tables สำหรับ common cross-domain queries**

```sql
-- ตัวอย่าง: Daily sales summary per member (aggregate ก่อน join)
CREATE TABLE `project.semantic.daily_member_sales_summary`
PARTITION BY transaction_date
CLUSTER BY partner_code, member_id
AS
SELECT
  transaction_date,
  member_id,
  partner_code,
  COUNT(DISTINCT receipt_number) AS receipt_count,
  SUM(total_price) AS total_sales,
  SUM(total_discount) AS total_discount,
  SUM(total_payment) AS total_payment,
  COUNT(DISTINCT sku) AS unique_skus  -- from pre-joined
FROM `project.refined.sales_receipt`
GROUP BY 1, 2, 3;

-- จากนั้น join กับ coupons ที่ aggregate ระดับเดียวกัน:
SELECT
  s.transaction_date, s.member_id,
  s.total_sales,
  c.coupons_used_count,
  c.total_redemption_value
FROM `semantic.daily_member_sales_summary` s
LEFT JOIN (
  SELECT member_id, DATE(used_datetime) AS used_date,
         COUNT(*) AS coupons_used_count,
         SUM(redemption_value) AS total_redemption_value
  FROM `refined.coupons`
  WHERE status = 'used'
  GROUP BY 1, 2
) c ON s.member_id = c.member_id AND s.transaction_date = c.used_date;
```

**Key Insight: Aggregate ก่อน JOIN ดีกว่า JOIN แล้ว Aggregate**:
```
BAD:  sales (100M rows) JOIN coupons (50M rows) → 500M rows → GROUP BY
GOOD: sales GROUP BY (1M rows) JOIN coupons GROUP BY (500K rows) → 1.5M rows

Cost difference: 100x+ ลดลง
```

---

## 7. Cost Analysis & Optimization

### 7.1 Optimization Comparison

| Approach | Current Cost/Day | After Optimization | Saving |
|----------|:----------------:|:------------------:|:------:|
| **Sales semantic JOIN** | ~$15.66 (50 queries × companies JOIN) | ~$12.50 (0 JOINs, denormalized) | 20% |
| **Sales 3-table combine** | ~$2.06/query | ~$0.80/query (nested STRUCT) | 60% |
| **Coupon enriched view** | ~$6.60 (MTV refresh 48x/day) | ~$2.20 (denormalized, MTV only for full) | 67% |
| **Cross-domain aggregate** | ~$4.50/query (100M × 50M) | ~$0.30/query (1M × 500K) | 93% |

### 7.2 Storage vs Compute Tradeoff

```
Denormalization storage overhead:

sales_receipt + branch_name/province/region:
  100M rows × 50 bytes extra per row = 5GB extra
  Cost: 5GB × $0.02/month = $0.10/month

vs. saved query cost:
  50 queries/day × $0.0625 saved per query × 30 days = $93.75/month

ROI: $93.75 / $0.10 = 937x return
```

### 7.3 BQ Slot Reservations vs On-Demand

```
ถ้าใช้ BQ Editions (slot-based):
  → Cost ไม่ขึ้นกับ scan volume → JOIN cost ≈ denormalized cost (compute time only)
  → แต่ heavy JOINs ยังช้ากว่า (shuffle overhead)
  → Denormalization ยัง benefit จาก speed ถึงแม้ cost เท่ากัน

สรุป: Denormalization ดีทั้ง on-demand (cost) และ slot-based (speed)
```

---

## 8. Decision Framework

### 8.1 เมื่อไหร่ใช้ Pattern ไหน

```
Q1: Table นี้ถูก JOIN บ่อยแค่ไหน?
├─ ไม่บ่อย (< 10 queries/day) → ใช้ VIEW (lazy JOIN)
├─ บ่อย (10-100 queries/day) → ใช้ Materialized View
└─ บ่อยมาก (> 100 queries/day) → Denormalize ลง table

Q2: Dimension เปลี่ยนบ่อยแค่ไหน?
├─ ไม่บ่อย (weekly/monthly) → Denormalize ได้เลย (refresh via pipeline cache)
├─ บ่อย (daily) → Star schema (JOIN ตอน query)
└─ บ่อยมาก (realtime) → ยังแยก + use latest dim lookup

Q3: Join type เป็นอะไร?
├─ Fact × Dim (1:1 or N:1) → Denormalize dim ลง fact ได้
├─ Fact × Fact (N:M) → AGGREGATE ก่อน JOIN เสมอ
└─ Parent × Children (1:N) → ใช้ Nested STRUCT ถ้า N ไม่ใหญ่เกิน

Q4: ใครเป็น consumer?
├─ BI dashboard → Denormalized / Star schema (BI tools ชอบ)
├─ Data scientist (SQL) → Star schema + pre-built aggregates
├─ ML pipeline → Denormalized flat table (feature store)
└─ API → Pre-computed summary tables (low latency)
```

### 8.2 สรุป Recommendation ตาม Use Case

| Use Case | Current | Recommended | Effort |
|----------|---------|-------------|--------|
| **Sales receipt + store info** | VIEW JOIN companies | **Denormalize** branch info ลง pipeline cache | Low |
| **Sales receipt + sku + tender** | 3 tables JOIN | **Nested STRUCT** table (semantic) | Medium |
| **Coupons + rewards** | VIEW/MTV 105+ cols | **Selective denorm** top-10 reward fields | Low |
| **Sales × Coupons analysis** | Ad-hoc N×M JOIN | **Pre-built aggregates** per member/day | Medium |
| **Sales enrichment (pipeline)** | 6-level cache lookup | **Keep current** (already optimal!) | None |
| **Member tier + sales** | Ad-hoc JOIN | **Denormalize** current tier ลง sales | Low |
| **Historical tier + sales** | Ad-hoc point-in-time | **SCD Type 2 dim** + star schema JOIN | High |

### 8.3 อะไรไม่ควรทำ

| Anti-Pattern | ทำไมไม่ควร | ใช้อะไรแทน |
|-------------|-----------|-----------|
| **Snowflake schema ใน BQ** | Multi-hop JOIN แพง, BQ storage ถูก | Star หรือ denormalized |
| **Full denormalize ทุก table เป็น 1 giant table** | Maintenance nightmare, 200+ columns | Selective denorm (เฉพาะ dim ที่ใช้บ่อย) |
| **JOIN transaction × transaction ตรงๆ** | Cost explosion (N×M rows scanned) | Aggregate ก่อน JOIN |
| **Materialized View สำหรับ LEFT JOIN + CDC** | Full refresh ทุกครั้ง (แพง) | Denormalize ลง pipeline แทน |
| **Over-normalize lookup tables** | 8 lookups → 8 JOINs ตอน query | Resolve ใน pipeline → store result (ซึ่ง sales ทำแล้ว!) |
| **Schema เหมือนกันทุก layer** | Source = Refined = Semantic → ไม่มี optimization | แต่ละ layer optimize ต่าง (raw → star → denorm) |

---

## 9. Implementation Roadmap

### Phase 1: Quick Wins (1-2 สัปดาห์)

**1A: Denormalize companies info ลง sales_receipt**
```
- เพิ่ม branch_name, province, region ใน refined.sales_receipt
- ใช้ pipeline cache เหมือน sales_channel (MasterCache pattern)
- public.sales_receipt view → ลด JOIN companies ออก
- Impact: ลด query cost 20% สำหรับ dashboard queries
```

**1B: Selective denormalize reward fields ลง coupons**
```
- เพิ่ม 10 key reward fields ใน refined.coupons (FetchCouponDoFn ดึง reward ด้วย)
- หรือ: เพิ่ม reward lookup ใน pipeline (ถ้า API return reward info)
- Impact: ลด MTV refresh cost 67%
```

### Phase 2: Semantic Optimization (2-4 สัปดาห์)

**2A: Sales complete nested table**
```
- สร้าง semantic.sales_complete ด้วย Dataform (scheduled query)
- receipt + ARRAY<items> + ARRAY<tenders>
- Refresh: daily (ต่อจากวันก่อน, incremental append)
- Impact: ลด 3-table JOIN cost 60%
```

**2B: Pre-built aggregate tables**
```
- semantic.daily_member_sales_summary (per member/day/partner)
- semantic.daily_coupon_usage_summary (per member/day)
- Refresh: daily (simple GROUP BY, low cost)
- Impact: Cross-domain queries ลด cost 90%+
```

### Phase 3: Advanced (ถ้าจำเป็น)

**3A: SCD Type 2 for slowly-changing dimensions**
```
- Member tier history (effective_from, effective_to)
- สำหรับ point-in-time analysis: "member tier ณ วันที่ transaction เกิด"
- Complex แต่ accurate สำหรับ financial/audit reports
```

**3B: Wide event table (activity stream)**
```
- Combine sales + coupons + purchases + tier changes เป็น activity timeline
- 1 row per event, all fields optional (sparse)
- สำหรับ ML feature engineering + customer journey analysis
```

---

## Appendix A: Schema Pattern Comparison Matrix

| Pattern | Query Cost | Storage | Maintenance | Query Simplicity | Best For |
|---------|:----------:|:-------:|:-----------:|:----------------:|----------|
| **3NF (Normalized)** | สูงสุด | ต่ำสุด | ง่าย | ยาก (5+ JOINs) | OLTP only |
| **Snowflake** | สูง | ต่ำ | ง่าย | ยาก (multi-hop) | ❌ ไม่แนะนำใน BQ |
| **Star** | กลาง | กลาง | กลาง | ดี (1-hop JOIN) | General DW |
| **Star + Selective Denorm** | ต่ำ-กลาง | กลาง | กลาง | ดีมาก | ✅ แนะนำ |
| **Nested STRUCT** | ต่ำ | กลาง | กลาง | ดี (UNNEST) | 1:N relationships |
| **Full Denormalized** | ต่ำสุด | สูง | ยาก | ง่ายที่สุด | High-frequency dashboards |
| **Materialized View** | auto | auto | auto | ง่าย | Moderate freq JOINs |
| **Pre-built Aggregate** | ต่ำมาก | เพิ่มเล็กน้อย | กลาง | ง่าย | Cross-domain analytics |

## Appendix B: BQ Cost Quick Reference

```
On-Demand:
  Query: $6.25 / TB scanned (first 1TB free/month)
  Storage: $0.02 / GB / month (active)
  Storage: $0.01 / GB / month (long-term, 90+ days untouched)
  Streaming insert: $0.05 / GB

Editions (Slot-based):
  Standard: $0.04 / slot-hour
  Enterprise: $0.06 / slot-hour
  Enterprise Plus: $0.10 / slot-hour

สูตรประมาณ:
  1 TB scanned ≈ 100 slot-seconds (varies)
  → On-demand: $6.25/TB
  → Standard: 100 slots × $0.04/3600 = $0.0011/TB ← ถูกกว่า 5,600x
  → แต่ต้อง commit minimum slots

ข้อสรุป: ถ้าใช้ Editions → cost ไม่ขึ้นกับ scan volume
          → optimization ยังสำคัญเรื่อง SPEED (ไม่ใช่ cost)
```

## Appendix C: Recommended Reading

- Kimball, Ralph. "The Data Warehouse Toolkit" (3rd Ed.) — Star schema bible
- Google Cloud: [BigQuery Best Practices](https://cloud.google.com/bigquery/docs/best-practices-performance-overview)
- Google Cloud: [Materialized Views](https://cloud.google.com/bigquery/docs/materialized-views-intro)
- Google Cloud: [Using Nested and Repeated Fields](https://cloud.google.com/bigquery/docs/nested-repeated)
- Google Cloud: [Partitioning and Clustering](https://cloud.google.com/bigquery/docs/partitioned-tables)
