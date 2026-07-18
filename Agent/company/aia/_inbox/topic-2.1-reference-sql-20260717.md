# Topic 2.1 — Reference SQL + "diff กับ SQL ของคุณ" checklist

> **วันที่:** 2026-07-17 · คู่กับ `topic-2.1-cost-reconciliation-20260717.md` (เหตุผล + citation)
> **จุดประสงค์:** implementation อ้างอิงที่ถูกต้อง — เอา SQL ปัจจุบันของคุณมา diff กับตัวนี้ได้เลย
> ⚠️ **ยังต้องการ SQL ปัจจุบันของคุณ** มา review ทีละบรรทัด — ด้านล่างคือ reference + จุดที่คนพลาดบ่อย

---

## 1. Reference query — DBU cost (list price) ต่อ team / SKU

```sql
-- ============================================================================
-- DBU COST (LIST PRICE) — attribution ledger
-- ⚠️ list price + DBU only — ไม่ใช่เงินจริง ไม่รวม classic VM (ดู §3)
-- ============================================================================
SELECT
    u.workspace_id,
    u.sku_name,
    u.billing_origin_product,
    u.custom_tags['team']             AS team,
    u.product_features.is_photon      AS is_photon,
    u.product_features.is_serverless  AS is_serverless,
    SUM(u.usage_quantity)                                    AS dbus,
    SUM(u.usage_quantity * p.pricing.effective_list.default) AS list_cost_usd
FROM system.billing.usage u
JOIN system.billing.list_prices p
  ON  p.sku_name = u.sku_name
  AND p.cloud    = u.cloud
  AND u.usage_end_time >= p.price_start_time
  AND (p.price_end_time IS NULL OR u.usage_end_time < p.price_end_time)
WHERE u.usage_date BETWEEN :start_date AND :end_date
GROUP BY ALL
ORDER BY list_cost_usd DESC;
```

## 2. Genie LLM cost ต่อ user (Topic 2.2 เชื่อมตรงนี้)
```sql
SELECT
    u.identity_metadata.run_as        AS user,
    u.usage_metadata.genie.surface    AS genie_surface,
    SUM(u.usage_quantity)             AS llm_dbus,
    SUM(u.usage_quantity * p.pricing.effective_list.default) AS list_cost_usd
FROM system.billing.usage u
JOIN system.billing.list_prices p
  ON  p.sku_name = u.sku_name AND p.cloud = u.cloud
  AND u.usage_end_time >= p.price_start_time
  AND (p.price_end_time IS NULL OR u.usage_end_time < p.price_end_time)
WHERE u.billing_origin_product = 'GENIE'
  AND u.usage_date BETWEEN :start_date AND :end_date
GROUP BY ALL
ORDER BY llm_dbus DESC;
```

## 3. Reconcile กับ Azure Portal — เทียบ DBU-line ↔ DBU-line (ไม่ใช่ DBU ↔ total)
```sql
-- 3a. DBU side จาก system.billing (list) — เทียบกับ meter "Azure Databricks" ใน Cost Mgmt Export
-- 3b. classic VM side ต้องมาจาก Cost Mgmt Export (meter "Virtual Machines" ใน managed RG)
--     → ไม่มีใน system.billing ต้อง JOIN Export
-- best-match total ≈ (DBU$ actual จาก Export DBU meter) + (VM$ จาก Export VM meter, allocate ตาม team tag/DBU share)

-- ตัวอย่างโครง join กับ Cost Mgmt Export ที่ ingest เป็น table แล้ว (Topic 1 มีอยู่แล้ว):
WITH dbu AS (   -- attribution จาก system.billing
  SELECT custom_tags['team'] AS team, SUM(usage_quantity) AS dbus
  FROM system.billing.usage
  WHERE usage_date BETWEEN :start_date AND :end_date
  GROUP BY ALL
),
azure_cost AS (  -- actual $ จาก Cost Management Export (Topic 1 pipeline)
  SELECT
    tags['team']       AS team,
    meter_category,               -- 'Azure Databricks' (DBU) vs 'Virtual Machines' (VM)
    SUM(cost_in_billing_currency) AS actual_usd
  FROM <cat>.cost.cost_export     -- table ที่ ingest จาก Export แล้ว
  WHERE billing_period = :period
    AND resource_group LIKE 'databricks-rg-%'  -- managed RG
  GROUP BY ALL
)
SELECT * FROM azure_cost;  -- แยก DBU$ กับ VM$ ตาม meter_category
```

---

## 4. 🔍 Checklist — diff SQL ของคุณกับ reference (จุดที่คนพลาดบ่อย)

| # | เช็คว่า SQL คุณ... | ถ้าไม่มี → อาการ |
|---|---|---|
| 1 | **join `list_prices` แบบ point-in-time** (`usage_end_time` between `price_start_time` และ `price_end_time`, + branch `price_end_time IS NULL`) | ❌ ไม่มี → **fan-out** (usage × N price rows) → **cost บวมหลายเท่า** |
| 2 | ใช้ **`pricing.effective_list.default`** (ไม่ใช่ `pricing.default`) | ❌ ใช้ผิด → ราคาผิดตอนมี promo active |
| 3 | join **`cloud`** ด้วย | ❌ ไม่มี → SKU-name ชนข้าม cloud (ถ้า multi-cloud) |
| 4 | **`SUM(usage_quantity)`** (ไม่ใช่ COUNT rows) | ❌ COUNT → นับ RETRACTION/RESTATEMENT ผิด |
| 5 | period เป็น **UTC** (`usage_date` / `usage_end_time` UTC) | ❌ ใช้ local → drift ขอบเดือน |
| 6 | เข้าใจว่าผลลัพธ์ = **DBU list เท่านั้น ไม่รวม classic VM** | ❌ ไม่รู้ → เทียบกับ Portal total แล้วงงว่าทำไมขาด 40-60% |
| 7 | ถ้าเทียบ Portal → เทียบ **DBU-meter ↔ DBU-meter** | ❌ เทียบ DBU ↔ total → "ตัวเลขไม่ตรง" (error คลาสสิก) |
| 8 | attribution ใช้ **`usage_metadata.*`** เป็น fallback เมื่อ tag หาย | ❌ พึ่ง custom_tags อย่างเดียว → workload ที่ไม่ได้ tag หลุด |
| 9 | รู้ว่า **`list_prices` = list ไม่ใช่ actual** (ไม่รวม EA/DBCU discount) | ❌ ไม่รู้ → คิดว่า over-report คือ bug |

---

## 5. คำถามที่จะถามคุณตอนได้ SQL มา
1. ดึงจาก `system.billing.usage` อย่างเดียว หรือ join `list_prices` ด้วย?
2. join `list_prices` แบบไหน (point-in-time หรือ latest price)?
3. เอาไปเทียบกับ Portal **ตัวเลขไหน** — total Databricks หรือ DBU meter อย่างเดียว?
4. ต่างกันประมาณกี่ % และทางไหน (system.billing ต่ำกว่า = น่าจะ missing VM · สูงกว่า = list vs discount)?
5. workload เป็น classic เยอะ หรือ serverless เยอะ? (classic → gap VM ใหญ่ · serverless → ใกล้กันกว่า)
6. มี Cost Management Export ingest เป็น table แล้วหรือยัง? (ใช้ join หา actual + VM)

> **ส่ง SQL มาได้เลย เดี๋ยวไล่ทีละบรรทัดเทียบ checklist §4 แล้วบอกว่าขาด/เกินตรงไหน**
