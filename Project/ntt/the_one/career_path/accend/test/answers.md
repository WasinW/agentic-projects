# Data Engineer Assessment – BigQuery SQL Test

## Task 1: Upload CSV Files to GCS

ตัว SQL เองมันทำ upload ขึ้น GCS ตรงๆไม่ได้ ต้องใช้ gsutil ครับ

```bash
gsutil cp costco_transaction.csv gs://your-bucket-name/data/
gsutil cp paypay_transaction.csv gs://your-bucket-name/data/
gsutil cp walmart_transaction.csv gs://your-bucket-name/data/
gsutil cp customer_demographic.csv gs://your-bucket-name/data/
```

---

## Task 2: Ingest Data into BigQuery using SQL

ดู data แล้วมันเป็น pipe-delimited `|` เลยต้องใส่ field_delimiter ด้วย

ตอน inspect data เจอว่า costco มี customer_id เป็น float (เช่น `27626.0`) เพราะน่าจะ export มาจาก pandas ที่มี null ปนอยู่ กับ walmart ใช้ชื่อ column เป็น `user_id` แทน `customer_id`

```sql
-- สร้าง dataset ไว้ก่อน
CREATE SCHEMA IF NOT EXISTS assessment;
```

```sql
-- costco: customer_id มาเป็น float string เช่น "27626.0" เพราะ column มี null ปน
-- BQ จะ infer เป็น FLOAT64 ซึ่ง cast เป็น INT64 ทีหลังได้
LOAD DATA OVERWRITE assessment.costco_transaction
FROM FILES (
  format = 'CSV',
  field_delimiter = '|',
  uris = ['gs://your-bucket-name/data/costco_transaction.csv'],
  skip_leading_rows = 1
);

-- paypay
LOAD DATA OVERWRITE assessment.paypay_transaction
FROM FILES (
  format = 'CSV',
  field_delimiter = '|',
  uris = ['gs://your-bucket-name/data/paypay_transaction.csv'],
  skip_leading_rows = 1
);

-- walmart: column ชื่อ user_id (ไม่ใช่ customer_id), มีแค่ date กับ month ไม่มี full datetime
LOAD DATA OVERWRITE assessment.walmart_transaction
FROM FILES (
  format = 'CSV',
  field_delimiter = '|',
  uris = ['gs://your-bucket-name/data/walmart_transaction.csv'],
  skip_leading_rows = 1
);

-- customer_demographic: gender มี 3 ค่า (M, F, Undefined), age มีบาง row เป็น 0
LOAD DATA OVERWRITE assessment.customer_demographic
FROM FILES (
  format = 'CSV',
  field_delimiter = '|',
  uris = ['gs://your-bucket-name/data/customer_demographic.csv'],
  skip_leading_rows = 1
);
```

---

## Task 3: Create table customer_member

เอา customer_id จากทุก transaction table มารวมกัน แล้ว flag ว่าเคยซื้อที่ไหนบ้าง

costco customer_id ต้อง cast จาก FLOAT64 เป็น INT64 ก่อนเพราะมันมาเป็น `27626.0`
walmart ใช้ column `user_id` แทน

```sql
CREATE OR REPLACE TABLE assessment.customer_member AS

-- รวม customer ทั้งหมดก่อน filter เฉพาะที่มี id
WITH all_cust AS (
  SELECT DISTINCT CAST(customer_id AS INT64) AS customer_id
  FROM assessment.costco_transaction
  WHERE customer_id IS NOT NULL
  UNION DISTINCT
  SELECT DISTINCT CAST(customer_id AS INT64)
  FROM assessment.paypay_transaction
  WHERE customer_id IS NOT NULL
  UNION DISTINCT
  SELECT DISTINCT CAST(user_id AS INT64)
  FROM assessment.walmart_transaction
  WHERE user_id IS NOT NULL
),

costco_cust AS (
  SELECT DISTINCT CAST(customer_id AS INT64) AS customer_id
  FROM assessment.costco_transaction WHERE customer_id IS NOT NULL
),
walmart_cust AS (
  SELECT DISTINCT CAST(user_id AS INT64) AS customer_id
  FROM assessment.walmart_transaction WHERE user_id IS NOT NULL
),
paypay_cust AS (
  SELECT DISTINCT CAST(customer_id AS INT64) AS customer_id
  FROM assessment.paypay_transaction WHERE customer_id IS NOT NULL
)

SELECT
  a.customer_id,
  (cc.customer_id IS NOT NULL) AS is_costco_member,
  (wc.customer_id IS NOT NULL) AS is_walmart_member,
  (pc.customer_id IS NOT NULL) AS is_paypay_member
FROM all_cust a
LEFT JOIN costco_cust cc ON a.customer_id = cc.customer_id
LEFT JOIN walmart_cust wc ON a.customer_id = wc.customer_id
LEFT JOIN paypay_cust pc ON a.customer_id = pc.customer_id
;
```

---

## Task 4: Create table customer_summary

สรุป txn count กับ total amount แยกตาม merchant แล้ว join demographic เอา age, gender

note: demographic มี gender = 'Undefined' กับ age = 0 อยู่ ตรงนี้เก็บไปตามที่เป็นก่อน ไม่ได้ clean เพราะโจทย์ไม่ได้บอกให้ทำ

```sql
CREATE OR REPLACE TABLE assessment.customer_summary AS

WITH costco_agg AS (
  SELECT CAST(customer_id AS INT64) AS customer_id,
         COUNT(*) AS txn_count,
         SUM(sales_amount) AS total_amount
  FROM assessment.costco_transaction
  WHERE customer_id IS NOT NULL
  GROUP BY 1
),
walmart_agg AS (
  -- walmart column ชื่อ user_id ไม่ใช่ customer_id ต้อง map ให้ตรงกัน
  SELECT CAST(user_id AS INT64) AS customer_id,
         COUNT(*) AS txn_count,
         SUM(sales_amount) AS total_amount
  FROM assessment.walmart_transaction
  WHERE user_id IS NOT NULL
  GROUP BY 1
),
paypay_agg AS (
  SELECT CAST(customer_id AS INT64) AS customer_id,
         COUNT(*) AS txn_count,
         SUM(sales_amount) AS total_amount
  FROM assessment.paypay_transaction
  WHERE customer_id IS NOT NULL
  GROUP BY 1
),
all_cust AS (
  SELECT customer_id FROM costco_agg
  UNION DISTINCT
  SELECT customer_id FROM walmart_agg
  UNION DISTINCT
  SELECT customer_id FROM paypay_agg
)

SELECT
  a.customer_id,
  d.age,
  d.gender,
  IFNULL(c.txn_count, 0) AS costco_txn_count,
  IFNULL(c.total_amount, 0) AS costco_total_amount,
  IFNULL(w.txn_count, 0) AS walmart_txn_count,
  IFNULL(w.total_amount, 0) AS walmart_total_amount,
  IFNULL(p.txn_count, 0) AS paypay_txn_count,
  IFNULL(p.total_amount, 0) AS paypay_total_amount
FROM all_cust a
LEFT JOIN assessment.customer_demographic d ON a.customer_id = d.cust_id
LEFT JOIN costco_agg c ON a.customer_id = c.customer_id
LEFT JOIN walmart_agg w ON a.customer_id = w.customer_id
LEFT JOIN paypay_agg p ON a.customer_id = p.customer_id
;
```

---

## Task 5: Create view active_customers

3 table นี้ schema ต่างกัน join ตรงๆไม่ได้ เลย normalize ให้เป็น format เดียว (customer_id, txn_date, merchant) แล้ว union รวมกันก่อน จากนั้นหา latest date แล้ว filter 30 วันทีเดียว

walmart มีแค่ column date กับ month ไม่มี year — ดูจาก costco range (2022-09 ถึง 2023-08) กับ walmart month ที่มี (6,7,8) น่าจะเป็นช่วง 2023 เลย assume year = 2023

```sql
CREATE OR REPLACE VIEW assessment.active_customers AS

-- normalize ทุก merchant ให้เป็น format เดียวกันก่อน
WITH all_txn AS (
  SELECT CAST(customer_id AS INT64) AS customer_id,
         DATE(PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', sales_at)) AS txn_date,
         'costco' AS merchant
  FROM assessment.costco_transaction WHERE customer_id IS NOT NULL

  UNION ALL

  -- walmart ไม่มี year เลย construct date เอง
  SELECT CAST(user_id AS INT64),
         DATE(2023, CAST(month AS INT64), CAST(date AS INT64)),
         'walmart'
  FROM assessment.walmart_transaction WHERE user_id IS NOT NULL

  UNION ALL

  SELECT CAST(customer_id AS INT64),
         DATE(PARSE_TIMESTAMP('%Y-%m-%d %H:%M:%S', sales_at)),
         'paypay'
  FROM assessment.paypay_transaction WHERE customer_id IS NOT NULL
),
-- หา cutoff date จาก latest txn ของทุก merchant รวมกัน
cutoff AS (
  SELECT DATE_SUB(MAX(txn_date), INTERVAL 30 DAY) AS since FROM all_txn
)

SELECT DISTINCT t.customer_id, t.merchant
FROM all_txn t, cutoff c
WHERE t.txn_date >= c.since
;
```

---

## Task 6: Export customer_member to GCS

```sql
EXPORT DATA OPTIONS(
  uri = 'gs://your-bucket-name/export/customer_member_*.csv',
  format = 'CSV',
  overwrite = true,
  header = true
) AS
SELECT * FROM assessment.customer_member;
```
