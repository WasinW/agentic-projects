Verification complete. Key results: `billing_origin_product='GENIE'` and `usage_metadata.genie.surface` are **confirmed correct** by the authoritative Genie budgets doc (2026-07-15), even though the billing system-table reference enum hasn't been updated to list GENIE. `pricing.effective_list.default` is confirmed the correct field. But I found several real errors: `SET VAR` without `DECLARE` won't run, the join column diverges from the documented canonical, an inaccurate `usage_unit='DBU'` filter/comment, and a genuine arithmetic scope-mismatch in the §3A/§3B reconciliation. Here is the corrected deliverable.

---

# Genie / Databricks Cost SQL — reconcile to the Azure Portal

> **สำหรับ:** สิน — Topic 2.1 (cost reconciliation) + Topic 2.2 (Genie cost)
> **Grounded in:** `databricks-genie-governance` §4 · `databricks-cost-optimization` §0.1 / §9 · official Genie budgets doc (2026-07-15) · billing/pricing system-table refs
> **Verified date:** 2026-07-18 (re-reviewed) · `[CONFIRMED-DOCS]` vs `[INFERENCE]` แยกไว้ในคอมเมนต์ · ⚠ Preview flag ตามจุด
> **IP:** generic template — placeholders `<catalog>` / `<cost_export_table>` เท่านั้น, ไม่มี AIA identifier

**BLUF — อ่านก่อนรัน:**
จาก system tables คุณได้ **LIST-price DBU estimate** เท่านั้น. จะให้ตรง Portal เป๊ะ ต้องเอา **actual billed \$** จาก Azure Cost Management Export มา reconcile (discount / FX / tax / timing อยู่ downstream ของ system table ทั้งหมด). ข้างล่างคือ **closest-achievable + วิธี reconcile 2 ทาง**. ข่าวดีของ Genie: มัน **serverless ล้วน → ไม่มี classic-VM gap** (ต่างจาก Databricks cost ทั่วไปที่ VM หาย 40-60% ใน managed RG).

> ⚠ **สิ่งที่ SQL ทำไม่ได้:** ไม่มี query ไหนให้เลข "ตรง Portal ถึงเซนต์" ได้จาก system tables. §3 ให้ **actual \$ จาก Export** แล้ว *allocate* ด้วย DBU-share — per-user เป็น **proportional attribution** (ไม่ใช่ invoice line ต่อคน). พูดกับ stakeholder ตามนี้ อย่าโฆษณาเกินจริง.

---

```sql
-- ############################################################################
-- ## SECTION 0 — PARAMETERS & PREREQUISITES
-- ############################################################################
-- Prereq [CONFIRMED-DOCS]:
--   * account admin เปิด system schema `billing` แล้ว
--   * reader มี SELECT บน system.billing.usage + system.billing.list_prices
--   * (สำหรับ §3) Cost Management Export ของ Topic 1 ingest เป็น Delta table แล้ว
-- Docs:
--   system.billing.usage       https://learn.microsoft.com/azure/databricks/admin/system-tables/billing
--   system.billing.list_prices https://learn.microsoft.com/azure/databricks/admin/system-tables/pricing
--   Genie budgets/free-tier    https://learn.microsoft.com/azure/databricks/genie/budgets
--
-- ⚠ FIX: session variables ต้อง DECLARE ก่อน — `SET VAR` เฉย ๆ (ไม่ declare) จะ error.
--        [CONFIRMED-DOCS — DECLARE VARIABLE, DBR 14.1+]
-- ตั้งค่า reporting window เป็น UTC (system.billing = UTC) เพื่อกัน drift ขอบเดือน
DECLARE OR REPLACE VARIABLE start_date DATE DEFAULT DATE'2026-06-01';
DECLARE OR REPLACE VARIABLE end_date   DATE DEFAULT DATE'2026-06-30';   -- เลือก "settled month" สำหรับ reconcile
-- (อ้างใน query ด้วยชื่อ start_date / end_date ตรง ๆ — ไม่ใช่ :start_date)


-- ############################################################################
-- ## SECTION 1 — CORE : Genie LLM cost per user / surface / team / month
-- ##             (LIST-price estimate — attribution ledger)
-- ############################################################################
-- ทำไม "ไม่ลบ 150":
--   Free tier ≈ 150 LLM DBU / identified user / month "ดูเหมือน" ถูก pre-excluded ออกจาก
--   system.billing.usage แล้ว — row ที่เห็นคือ BILLED (post-free-tier) DBU. ถ้าลบ 150
--   เองอีก = double-deduct → cost ต่ำเกินจริง.
--   ⚠ [INFERENCE — DOC-SILENT] official docs ไม่ได้ยืนยัน gross-vs-net ตรง ๆ; อนุมานจาก
--   canonical query ของ Databricks (ไม่มี term free-tier) + community dashboard. VALIDATE:
--   user ที่ใช้ < 150 DBU/เดือน ควร "ไม่มี GENIE row เลย" เดือนนั้น. ถ้ามี row = สมมติฐานผิด.
--   หมายเหตุ: 150 เป็นค่าจาก pricing page (ไม่ใช่ billing docs, verify per region) — อย่า hardcode ใน SQL.
--
-- ทำไม filter product (ไม่ hardcode sku_name):
--   ทั้ง 3 surface (Genie One / Agents / Code) รายงานเป็น billing_origin_product='GENIE'
--   และแชร์ tag เดียว databricks-product:genie → filter product แล้ว JOIN ราคาเข้ามา.
--   [CONFIRMED-DOCS — Genie budgets doc, canonical query 2026-07-15]
--   ⚠ หมายเหตุ robustness: enum ใน billing.md (ref doc) ยัง "ไม่ลิสต์" ค่า GENIE (stale หลัง GA 2026-07-08)
--     — authority คือ Genie budgets doc ที่ใช้ WHERE billing_origin_product='GENIE' ตรง ๆ.

SELECT
    date_trunc('MONTH', u.usage_date)                 AS usage_month,
    u.identity_metadata.run_as                        AS user_identity,   -- billed principal [CONFIRMED]
    u.usage_metadata.genie.surface                    AS genie_surface,   -- One/Agents/Code [CONFIRMED-DOCS]
    -- chargeback key: custom_tags['team'] ตามที่ขอ  ⚠ GOTCHA ด้านล่าง
    COALESCE(u.custom_tags['team'], dt.team, 'UNATTRIBUTED') AS team,
    u.sku_name,
    SUM(u.usage_quantity)                             AS billed_dbus,     -- already NET of free tier
    SUM(u.usage_quantity * p.pricing.effective_list.default) AS list_cost_usd
FROM system.billing.usage u
JOIN system.billing.list_prices p
      ON  p.sku_name = u.sku_name                     -- JOIN, ไม่ hardcode
      AND p.cloud    = u.cloud                        -- กัน SKU-name ชนข้าม cloud
      AND u.usage_start_time >= p.price_start_time    -- ⚠ FIX: usage_START_time (ตาม canonical doc)...
      AND (p.price_end_time IS NULL OR u.usage_start_time < p.price_end_time) -- ...half-open interval = 1 match, no fan-out
-- OPTIONAL: user→team dimension (ดู GOTCHA) — ถ้าไม่มี ให้ลบ LEFT JOIN นี้ทิ้ง
LEFT JOIN <catalog>.<schema>.dim_user_team dt
      ON dt.user_email = u.identity_metadata.run_as
WHERE u.billing_origin_product = 'GENIE'              -- ครอบทั้ง 3 surface [CONFIRMED-DOCS]
  AND u.usage_date BETWEEN start_date AND end_date    -- UTC calendar boundary
GROUP BY ALL                                          -- self-nets RETRACTION/RESTATEMENT — อย่า COUNT rows
ORDER BY list_cost_usd DESC;

-- ⚠ FIX (usage_unit): ลบ filter `usage_unit='DBU'` ออกแล้ว.
--   เหตุผล: (1) canonical query ของ Databricks ไม่มี filter นี้;
--   (2) "TOKEN / ANSWER" เป็นค่าของคอลัมน์ `usage_type` ไม่ใช่ `usage_unit` — คอมเมนต์เดิม conflate 2 คอลัมน์;
--   (3) การ JOIN ราคาแบบ per-SKU (sku_name+cloud) บังคับ unit ให้ตรงกันอยู่แล้ว (แต่ละ SKU มี usage_unit ของตัวเอง);
--   (4) ถ้า Genie มี meter รองที่ไม่ใช่ DBU การ filter DBU ทิ้งอาจ "ตัด row จริงทิ้ง → understate".
--   ถ้าอยากกันจริง ให้ inspect ด้วย HELPER ข้างล่าง แล้วตัดสินใจบนข้อมูล ไม่ใช่ assume.

-- ⚠ GOTCHA — team tag บน Genie มักว่าง [CONFIRMED-DOCS — genie skill §3.2 / cost skill §9.1]:
--   Serverless usage/budget policies (⚠ Public Preview) "ไม่ครอบ Genie และ SQL warehouse" → Genie LLM row
--   มักไม่มี custom_tags['team'] → chargeback ต่อทีมของ Genie ต้อง map ผ่าน "user → team"
--   (dim_user_team ข้างบน) ไม่ใช่ tag. ตั้ง COALESCE order: tag → dim → 'UNATTRIBUTED'.

-- HELPER — ค้น sku_name / usage_type จริงของ Genie ใน tenant คุณ (ใช้ต่อใน §2/§3, อย่าเดา):
--   SELECT DISTINCT sku_name, usage_unit, usage_type
--   FROM system.billing.usage
--   WHERE billing_origin_product='GENIE'
--     AND usage_date BETWEEN start_date AND end_date;
```

---

```sql
-- ############################################################################
-- ## SECTION 2 — HOW GENIE APPEARS IN THE AZURE PORTAL  (อ่านเป็น comment)
-- ############################################################################
--
-- 2.1  meter/category ไหน?  [INFERENCE grounded + CONFIRMED serverless=Databricks meter]
--   Genie LLM DBU = serverless, tracked ผ่าน "Unity AI Gateway" (resource type ที่ Databricks
--   Budget ใช้: Genie budgets doc §"Create a budget", tag databricks-product:genie).
--   บน Azure Cost Management มันโผล่ใต้:
--       MeterCategory = "Azure Databricks"                        [CONFIRMED — DBU ทั้งหมดอยู่ category นี้]
--       MeterName/SubCategory = serverless AI / real-time inference meter   [INFERENCE — verify ด้วย discovery]
--   VM ของ Genie ถูก bundle เข้า DBU price แล้ว (serverless) → ไม่มี line VM แยกใน managed RG.
--   ⚠ tag `databricks-product:genie` เป็น tag ฝั่ง Databricks Budget (Unity AI Gateway) — ไม่การันตีว่า
--     โผล่เป็น Azure resource tag ใน Cost Management Export (serverless = ไม่มี resource ใน managed RG).
--
-- 2.2  Genie แยกออกมาได้ไหมบน Portal?  → **โดยทั่วไป NO** [INFERENCE — สำคัญ]
--   Azure Cost Management group ตาม METER ไม่ใช่ตาม billing_origin_product.
--   billing_origin_product='GENIE' เป็น concept ฝั่ง Databricks system table เท่านั้น —
--   Portal มองไม่เห็นคำว่า "GENIE". Genie LLM ใช้ serverless AI meter อาจ "ร่วมกับ" AI Gateway
--   consumption อื่น (pay-per-token model serving, ai_query batch). ถ้า sku/meter เดียวกัน →
--   บน Portal จะ **แยก Genie ออกจากพี่น้อง AI-Gateway ไม่ได้**.
--
--   ⇒ ตัวเลข Portal ของ meter นั้น = (Genie LLM) + (AI-Gateway LLM อื่นที่ map meter เดียวกัน).
--     ใครแยก Genie ล้วนได้? → system.billing (billing_origin_product='GENIE') เท่านั้น.
--     ⇒ reconcile ที่ระดับ METER (Genie+พี่น้อง) แล้วใช้ system.billing "split ภายใน" ให้ Genie.
--
--   DISCOVERY (รันครั้งเดียว — จด (ก) Genie SKUs, (ข) SKUs อื่นที่ใช้ meter เดียวกัน,
--             (ค) Azure meter names → ใส่ :genie_meter_list ใน §3):
--     -- (ก) Genie SKUs:
--     SELECT DISTINCT u.sku_name FROM system.billing.usage u
--     WHERE u.billing_origin_product='GENIE';
--     -- (ข) มี product อื่นใช้ sku เดียวกันไหม (ถ้าใช่ = meter share, แยกบน Portal ไม่ได้):
--     -- SELECT billing_origin_product, sku_name, COUNT(*)
--     -- FROM system.billing.usage
--     -- WHERE sku_name IN (<genie skus>) GROUP BY ALL;
--   ถ้า Genie มี sku_name เฉพาะ map 1:1 กับ Azure meter → แยกได้บน Portal (case ง่าย).
--   ถ้า share → ตามข้างบน (ต้อง split ด้วย system.billing).
```

---

```sql
-- ############################################################################
-- ## SECTION 3 — RECONCILE TO PORTAL  (two methods)
-- ##  เทียบ DBU-meter ↔ DBU-meter เท่านั้น — ห้ามเทียบ DBU ↔ Portal total (error คลาสสิก)
-- ##  ⚠ กติกาความถูกต้อง: numerator (actual) กับ denominator (list) ต้อง "scope เดียวกัน".
-- ##     ถ้า actual = ทั้ง meter (Genie+พี่น้อง) list ก็ต้อง = ทั้ง meter — ไม่งั้น rate เพี้ยน.
-- ############################################################################

-- ----------------------------------------------------------------------------
-- ## 3A — DISCOUNT-FACTOR CALIBRATION  (ไม่ต้อง join per-user; เร็ว, ทำ dashboard ได้)
-- ----------------------------------------------------------------------------
-- แนวคิด: สำหรับเดือนที่ settled แล้ว คำนวณ effective_rate ที่ "meter scope เดียวกัน":
--     effective_rate = (actual $ จาก Azure Export, ทั้ง meter)
--                      ────────────────────────────────────────
--                      (list  $ จาก system.billing, ทั้ง meter)     << ⚠ FIX: list ต้อง scope = meter, ไม่ใช่ Genie-only
--   แล้วคูณ factor นี้กลับเข้า per-user Genie list estimate ใน §1 (valid ถ้า discount% uniform ทั้ง meter).
--   factor "ห่อ" discount + FX + tax + rounding รวมเป็นตัวเดียว (blended) — ประมาณ, ตรงระดับ meter.
--
--   :meter_sku_list = ทุก sku_name ที่ map เข้า :genie_meter_list (จาก §2 discovery — Genie + พี่น้อง).
--   ถ้า Genie มี meter 1:1 → :meter_sku_list = Genie SKUs เท่านั้น (สูตรลดรูปเป็น Genie-only เอง).

WITH list_est AS (   -- ฝั่ง system.billing: list $ ของ "ทั้ง meter" (scope ตรงกับ actual), settled month
    SELECT
        date_trunc('MONTH', u.usage_date) AS usage_month,
        SUM(u.usage_quantity * p.pricing.effective_list.default) AS list_usd
    FROM system.billing.usage u
    JOIN system.billing.list_prices p
          ON  p.sku_name = u.sku_name AND p.cloud = u.cloud
          AND u.usage_start_time >= p.price_start_time
          AND (p.price_end_time IS NULL OR u.usage_start_time < p.price_end_time)
    WHERE u.sku_name IN (:meter_sku_list)                     -- ⚠ FIX: ทั้ง meter (ไม่ใช่ billing_origin_product='GENIE')
      AND u.usage_date BETWEEN start_date AND end_date
    GROUP BY ALL
),
actual AS (          -- ฝั่ง Azure Export: actual $ ของ meter เดียวกัน (จาก §2 discovery)
    SELECT
        date_trunc('MONTH', c.<date_col>) AS usage_month,
        SUM(c.<cost_col>)                 AS actual_usd     -- CostInBillingCurrency (THB) หรือ CostInUsd
    FROM <cost_export_table> c
    WHERE c.<meter_category_col> = 'Azure Databricks'
      AND c.<meter_name_col> IN (:genie_meter_list)         -- meter จาก §2 (hardcode literal — marker ไม่ expand list)
      AND c.<date_col> BETWEEN start_date AND end_date
    GROUP BY ALL
)
SELECT
    l.usage_month,
    l.list_usd,
    a.actual_usd,
    a.actual_usd / NULLIF(l.list_usd, 0) AS effective_rate  -- << blended discount rate (โดยทั่วไป < 1)
FROM list_est l
JOIN actual   a USING (usage_month);

-- นำ effective_rate ไปคูณ per-user Genie estimate (§1):
--   SELECT usage_month, user_identity, team,
--          list_cost_usd,
--          list_cost_usd * :effective_rate AS reconciled_cost_usd  -- approximate, blended
--   FROM (<< §1 query >>) ;
-- ⚠ ใช้ factor จาก "settled" month เท่านั้น. เดือนปัจจุบันยังไม่ settle → ตัวเลขจะขยับ.
-- ⚠ นี่คือ approximation ระดับ meter — ไม่ใช่ per-invoice-line ต่อ user.


-- ----------------------------------------------------------------------------
-- ## 3B — DIRECT ALLOCATION จาก Cost Management Export  (REUSE table ของ Topic 1)
-- ----------------------------------------------------------------------------
-- แนวคิด: ตี "actual $/DBU (blended)" ของ meter จาก Export ÷ total DBU ของ meter (system.billing)
-- แล้วคูณด้วย Genie-DBU ต่อ user. นี่คือ per-user actual-$ attribution ที่ดีที่สุดเท่าที่ทำได้ —
-- **ไม่ใช่ invoice line ต่อคน**: มันคือ Genie DBU × blended actual rate ของ meter.
--
-- ⚠ FIX (arithmetic scope): เวอร์ชันเดิมเอา actual ทั้ง meter (Genie+พี่น้อง) มา allocate ทับ
--    "Genie-only total DBU" → OVER-allocate เมื่อ meter share. เวอร์ชันนี้หารด้วย
--    "total DBU ของทั้ง meter" → แต่ละ Genie DBU ได้ราคา blended actual ที่ถูกต้อง (พี่น้องไม่ปน).

WITH genie_dbu AS (       -- attribution ต่อ user (Genie-only)
    SELECT
        date_trunc('MONTH', u.usage_date) AS usage_month,
        u.identity_metadata.run_as        AS user_identity,
        COALESCE(u.custom_tags['team'], 'UNATTRIBUTED') AS team,
        SUM(u.usage_quantity)             AS dbus
    FROM system.billing.usage u
    WHERE u.billing_origin_product = 'GENIE'
      AND u.usage_date BETWEEN start_date AND end_date
    GROUP BY ALL
),
meter_dbu AS (            -- ⚠ FIX: total DBU ของ "ทั้ง meter" (ตัวหารที่ถูก scope)
    SELECT
        date_trunc('MONTH', u.usage_date) AS usage_month,
        SUM(u.usage_quantity)             AS meter_total_dbus
    FROM system.billing.usage u
    WHERE u.sku_name IN (:meter_sku_list)                     -- Genie + พี่น้องที่ share meter (§2)
      AND u.usage_date BETWEEN start_date AND end_date
    GROUP BY ALL
),
meter_actual AS (         -- actual $ ต่อเดือน (Azure Export, ทั้ง meter)
    SELECT
        date_trunc('MONTH', c.<date_col>) AS usage_month,
        SUM(c.<cost_col>)                 AS meter_actual_usd
    FROM <cost_export_table> c
    WHERE c.<meter_category_col> = 'Azure Databricks'
      AND c.<meter_name_col> IN (:genie_meter_list)
      AND c.<date_col> BETWEEN start_date AND end_date
    GROUP BY ALL
)
SELECT
    g.usage_month,
    g.user_identity,
    g.team,
    g.dbus,
    (ma.meter_actual_usd / NULLIF(md.meter_total_dbus, 0)) AS actual_usd_per_dbu,   -- blended actual rate
    g.dbus * (ma.meter_actual_usd / NULLIF(md.meter_total_dbus, 0)) AS reconciled_actual_usd
FROM genie_dbu     g
JOIN meter_dbu     md USING (usage_month)
JOIN meter_actual  ma USING (usage_month)
ORDER BY reconciled_actual_usd DESC;

-- หมายเหตุ join key + ความหมายของเลข:
--   * allocate ที่ระดับ "เดือน + meter" (ไม่ใช่ resource_id) เพราะ Genie serverless ไม่มี
--     managed-RG resource ให้ join ตรง — ต่างจาก classic compute (§5).
--   * SUM(reconciled_actual_usd) ทุก Genie user = Genie's proportional share ของ meter actual
--     (ไม่ใช่ยอด meter ทั้งก้อน, ไม่ใช่ยอด Portal total). ห้ามพูดว่า "ตรงถึงเซนต์ต่อคน".
--   * ถ้า meter เป็น Genie 1:1 (:meter_sku_list = Genie SKUs) → meter_total_dbus = Genie DBU
--     และ SUM(reconciled) = meter_actual_usd พอดี (ยัง proportional ต่อ user).
```

---

```sql
-- ############################################################################
-- ## SECTION 4 — THE IRREDUCIBLE RESIDUAL  (จะเหลือต่างเสมอ แม้ทำ §3 แล้ว)
-- ############################################################################
-- แม้ reconcile DBU-meter↔DBU-meter แล้ว ตัวเลขจาก system.billing (list) ยังต่างจาก Portal เพราะ:
--
--   1) NEGOTIATED / DBCU DISCOUNT  — effective_list = LIST ไม่ใช่ EA/MCA rate หรือ DBCU
--      prepurchase drawdown → list สูงกว่า actual ตาม discount% (10-40%+).   [CONFIRMED — topic-2.1]
--   2) FX (USD → THB)             — system.billing = USD list; Portal = billing currency (THB) + FX
--      ของวัน settle → ต่างตาม FX.                                          [CONFIRMED]
--   3) TAX / ROUNDING            — Portal เป็น post-tax, billing currency; system.billing pre-tax USD.
--   4) TIMING                    — system.billing UTC + refresh "ทุกไม่กี่ ชม." ไม่มี SLA + late RETRACTION/
--      RESTATEMENT; Portal finalize ตอน invoice → same-day/ขอบเดือน จะเหลื่อมกันไม่กี่ ชม.–วัน.
--                                 [CONFIRMED — Genie budgets doc: system.billing.usage "updates every few hours"]
--
--   ✅ Genie = serverless ล้วน → **ไม่มี classic-VM gap** (VM bundle ใน DBU price แล้ว).
--      นี่คือเหตุผลที่ Genie reconcile "ใกล้" กว่า Databricks cost ทั่วไป (ที่ VM หาย 40-60% ใน managed RG).
--
--   ประโยคเดียวที่ต้องพูดกับ stakeholder:
--   ▶ "อยากได้เลข to-the-cent ให้ใช้ Azure Cost Management Export เป็น source of truth —
--      ไม่ใช่ system tables. system.billing ใช้ทำ per-user / per-surface attribution ที่ Export ให้ไม่ได้.
--      per-user เป็น proportional allocation ของยอด actual ระดับ meter."
```

---

```sql
-- ############################################################################
-- ## SECTION 5 — GENERALIZED : ขยายไป "ทุก" Databricks DBU cost
-- ##             (เพิ่ม classic-VM managed-RG reconciliation จาก cost-optimization §0.1)
-- ############################################################################
-- Genie ง่ายเพราะ serverless (no VM gap). พอ generalize ไปทุก workload ต้องเพิ่ม 2 อย่าง:
--
--   A) เอา filter billing_origin_product='GENIE' ออก → group ตาม sku_name / billing_origin_product /
--      custom_tags['team'] / usage_metadata.{job_id,warehouse_id,cluster_id,dlt_pipeline_id}.
--      (usage_metadata = attribution ที่ระบบการันตี ใช้เป็น fallback เมื่อ tag หาย.)
--
--   B) 🔴 CLASSIC-VM GAP — VM/disk/IP ของ classic compute "ไม่อยู่ใน system.billing"
--      (บิลแยกใน managed resource group, meter "Virtual Machines"). serverless ไม่มีปัญหานี้
--      (VM bundle ใน DBU). ⇒ best-match total ต้องบวก VM$ จาก Export เข้าบน DBU$:
--
--        approx_portal_total = (DBU$ actual, Export "Azure Databricks" meter)
--                            + (VM$      actual, Export "Virtual Machines" meter, managed RG)
--
--      allocate VM$ ต่อทีม 2 ทาง: (ก) cluster custom tag propagate ไป VM ใน managed RG → group ตรง
--      (verify propagation ก่อน) · (ข) pro-rate VM$ ตาม DBU share ต่อทีม.   [CONFIRMED — cost skill §0.1/§9]
--      ⚠ managed-RG name ไม่ fix — default `databricks-rg-...` แต่ตั้งเองได้ตอนสร้าง workspace → verify ชื่อจริง.

WITH dbu AS (   -- attribution (list) จาก system.billing — ทุก product
    SELECT
        COALESCE(u.custom_tags['team'], 'UNATTRIBUTED') AS team,
        SUM(u.usage_quantity)                                    AS dbus,
        SUM(u.usage_quantity * p.pricing.effective_list.default) AS dbu_list_usd
    FROM system.billing.usage u
    JOIN system.billing.list_prices p
          ON  p.sku_name = u.sku_name AND p.cloud = u.cloud
          AND u.usage_start_time >= p.price_start_time
          AND (p.price_end_time IS NULL OR u.usage_start_time < p.price_end_time)
    WHERE u.usage_date BETWEEN start_date AND end_date
    GROUP BY ALL
),
azure_dbu AS (   -- actual DBU$ (Export, meter "Azure Databricks")
    SELECT c.<tags_col>['team'] AS team, SUM(c.<cost_col>) AS dbu_actual_usd
    FROM <cost_export_table> c
    WHERE c.<meter_category_col> = 'Azure Databricks'
      AND c.<resource_group_col> LIKE 'databricks-rg-%'   -- managed RG pattern (verify ชื่อจริง)
      AND c.<date_col> BETWEEN start_date AND end_date
    GROUP BY ALL
),
azure_vm AS (    -- actual VM$ (Export, meter "Virtual Machines" ใน managed RG) — ตัวที่ system.billing ไม่มี
    SELECT c.<tags_col>['team'] AS team, SUM(c.<cost_col>) AS vm_actual_usd
    FROM <cost_export_table> c
    WHERE c.<meter_category_col> = 'Virtual Machines'
      AND c.<resource_group_col> LIKE 'databricks-rg-%'
      AND c.<date_col> BETWEEN start_date AND end_date
    GROUP BY ALL
)
SELECT
    COALESCE(d.team, ad.team, vm.team)                          AS team,
    d.dbu_list_usd,                                             -- system.billing (list, attribution)
    ad.dbu_actual_usd,                                          -- Export DBU meter (money truth)
    vm.vm_actual_usd,                                           -- Export VM meter (หายจาก system.billing)
    COALESCE(ad.dbu_actual_usd,0) + COALESCE(vm.vm_actual_usd,0) AS approx_portal_total  -- << ใกล้ Portal
FROM dbu d
FULL OUTER JOIN azure_dbu ad USING (team)
FULL OUTER JOIN azure_vm  vm USING (team)
ORDER BY approx_portal_total DESC;
-- reconcile check: dbu_list_usd ควรอยู่ในช่วง (dbu_actual_usd / (1 - discount%)) ± tax/FX/latency.
-- ยังเทียบ DBU-meter↔DBU-meter; VM$ เป็น "ก้อนที่ต้องบวกเพิ่ม" ไม่ใช่ตัวเทียบ.
```

---

## Watch-outs (สรุปสั้น — pin ไว้ข้าง dashboard)

| # | Watch-out | ผล |
|---|---|---|
| 1 | **อย่าลบ 150 free tier ใน SQL** — pre-excluded อยู่แล้ว (⚠ INFERENCE, doc-silent → validate) | ลบ = understate cost (double-deduct) |
| 2 | **`pricing.effective_list.default`** ไม่ใช่ `pricing.default` (effective_list = "price used for calculating cost") | `pricing.default` ผิดตอนมี promo active |
| 3 | **join `sku_name` + `cloud` + `usage_start_time`** (branch `price_end_time IS NULL`) | ไม่ bound → ไม่ match doc; half-open = 1 row, no fan-out |
| 4 | **อย่า filter `usage_unit='DBU'`** — TOKEN/ANSWER เป็นค่า `usage_type` คนละคอลัมน์ | filter ผิดคอลัมน์อาจตัด Genie row จริงทิ้ง |
| 5 | **`SET VAR` ต้องมี `DECLARE` ก่อน** | รันดิบ ๆ = error (unresolved variable) |
| 6 | **Genie team tag มักว่าง** (usage policies ⚠Preview ไม่ครอบ Genie+warehouse) | chargeback ต้อง map user→team, ไม่ใช่ tag |
| 7 | **Portal แยก Genie ไม่ได้** (group by meter ไม่ใช่ product) | reconcile ที่ meter, split ด้วย system.billing |
| 8 | **reconcile: numerator/denominator ต้อง scope เดียวกัน** (§3A/§3B ใช้ `:meter_sku_list`) | list Genie-only ÷ actual ทั้ง meter = rate เพี้ยน |
| 9 | **per-user = proportional allocation**, ไม่ใช่ invoice line | อย่าโฆษณา "to-the-cent ต่อคน" |
| 10 | **`effective_list` = LIST** ไม่ใช่ actual (discount/FX/tax downstream) | over-report ตาม discount ไม่ใช่ bug |
| 11 | **Genie serverless → ไม่มี VM gap**; แต่ generalize (§5) ต้องบวก VM$ จาก Export | Databricks ทั่วไป VM หาย 40-60% |
| 12 | **reconcile เฉพาะ settled month**; refresh ทุกไม่กี่ ชม. ไม่มี SLA | same-day/intra-day จะดูขาดเสมอ |

**Placeholders ที่ต้องเติมก่อนรัน:** `<catalog>.<schema>.dim_user_team` (optional), `<cost_export_table>`, `<date_col>` (เช่น `Date`/`UsageDate`), `<meter_category_col>` (`MeterCategory`), `<meter_name_col>` (`MeterName`), `<cost_col>` (`CostInBillingCurrency` = THB, หรือ `CostInUsd` เพื่อเทียบ USD↔USD ก่อน แล้วค่อยดู FX), `<resource_group_col>` (`ResourceGroup`), `<tags_col>` (`Tags`), `:genie_meter_list` (Azure meter names จาก §2 — hardcode เป็น literal list, parameter marker ไม่ expand list), `:meter_sku_list` (Databricks SKUs ที่ map เข้า meter นั้น, จาก §2 discovery).

**Lock-in note:** ทุก query นี้พึ่ง `system.billing.*` (proprietary UC system tables) + Databricks pricing model — ไม่ portable ออกนอก Databricks. Azure Cost Management Export ฝั่ง `<cost_export_table>` เป็นกลาง (Azure-native) → ถ้าย้าย platform ในอนาคต ฝั่ง actual-\$ reuse ได้ แต่ attribution layer (per-user/surface DBU) ต้องเขียนใหม่.

**Escalate:** schema จริงของ Cost Management Export + managed-RG IAM/tag-propagation plumbing + Azure meter naming ของ serverless AI → `azure-expert`; ว่า Genie-meter share sku กับ AI-Gateway อื่นจริงไหมใน tenant → รัน discovery §2 ในสภาพแวดล้อมจริง (ยืนยันด้วย data, อย่า assert).

Sources:
- [system.billing.usage](https://learn.microsoft.com/en-us/azure/databricks/admin/system-tables/billing) · [system.billing.list_prices](https://learn.microsoft.com/en-us/azure/databricks/admin/system-tables/pricing)
- [Manage budgets and cost controls for Genie](https://learn.microsoft.com/en-us/azure/databricks/genie/budgets) (canonical Genie cost query, 2026-07-15)
- [DECLARE VARIABLE](https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/sql-ref-syntax-ddl-declare-variable) · [SET variable](https://learn.microsoft.com/en-us/azure/databricks/sql/language-manual/sql-ref-syntax-aux-set-variable)
- [Create and monitor budgets](https://learn.microsoft.com/en-us/azure/databricks/admin/account-settings/budgets)
- Skills (verified 2026-07): `databricks-genie-governance` §3-4, `databricks-cost-optimization` §0.1/§9

---

## Reviewer changes

1. **`SET VAR` → `DECLARE OR REPLACE VARIABLE` (runnability bug, §0).** `SET VAR start_date = ...` with no prior `DECLARE` errors out (variable unresolved). Verified against the Databricks DECLARE VARIABLE / SET VARIABLE docs. Also removed the stray `-- :start_date` marker comments — these are session variables referenced by bare name, not `:param` markers.
2. **Point-in-time join column `usage_end_time` → `usage_start_time` (§1, §3A, §5).** The deliverable claimed `[CONFIRMED-DOCS]` but diverged from the documented canonical, which uses `usage_start_time`. Both avoid fan-out (the join is a half-open interval → exactly one price row), so this was not a fan-out bug, but I aligned it to the doc/skill for consistency and accuracy of the CONFIRMED tag.
3. **Removed the `usage_unit = 'DBU'` filter + fixed its comment (§1, §3A, §3B).** The comment said "not the TOKEN/ANSWER meter," but `TOKEN`/`ANSWER` are values of the **`usage_type`** column, not `usage_unit` — the two were conflated. The official canonical query has no such filter; per-SKU price join already keeps units consistent, and filtering on the wrong column risks silently dropping a legitimate Genie meter (understatement). Added a `usage_type` to the discovery HELPER so the decision is data-driven.
4. **Fixed the arithmetic scope-mismatch in §3A.** The discount factor divided **whole-meter actual \$** (Export, Genie + siblings) by **Genie-only list \$** (`billing_origin_product='GENIE'`) — mismatched numerator/denominator scope → an inflated `effective_rate`. Rewrote `list_est` to sum the **same meter scope** (`:meter_sku_list`). Uniform-discount argument now actually holds.
5. **Fixed the over-allocation bug in §3B.** The original allocated **whole-meter actual \$** across **Genie-only total DBU** → over-attributes the siblings' cost to Genie users whenever the meter is shared (which §2.2 says is the common case). Rewrote as `Genie_DBU × (meter_actual_\$ / meter_total_DBU)` so each Genie DBU is priced at the meter's blended actual rate and siblings drop out cleanly.
6. **Softened the "to-the-cent" claim (§3B, BLUF, §4, Watch-out #9).** Per the review mandate: removed "นี่คือ to-the-cent ที่สุดเท่าที่ทำได้" and stated explicitly that per-user is a **DBU-proportional allocation of the meter actual**, not a per-invoice line. Added a BLUF caveat up top.
7. **Confirmed and hardened `billing_origin_product='GENIE'` and `usage_metadata.genie.surface`.** These are **correct** — the authoritative Genie budgets doc (2026-07-15) uses both verbatim. Noted inline that the `billing.md` reference enum is **stale** (does not yet list `GENIE` after the 2026-07-08 GA), so a skeptic checking that page won't wrongly conclude the filter is invalid.
8. **Confirmed `pricing.effective_list.default` is right (Watch-out #2 kept, wording sharpened).** The pricing doc explicitly says `effective_list` "contains the effective list price used for calculating the cost" — so this beats `pricing.default` when a promo is active.
9. **Minor:** added a note that `:genie_meter_list` / `:meter_sku_list` must be hardcoded literals (scalar parameter markers don't expand a list in `IN (...)`); flagged that the managed-RG name (`databricks-rg-%`) is configurable, not fixed; added `usage_type` to discovery.
10. **No-subtract-150 + honest caveat: kept, strengthened.** The `[INFERENCE — DOC-SILENT]` framing and the "< 150 DBU ⇒ no rows" validation are present and correct; I promoted "doc-silent" into the comment and Watch-out #1 so the hedge travels with the SQL.

**Scope note:** only the **SQL deliverable** was provided. The user-manual checklist (entitlement names `workspace-consume`/`databricks-sql-access`/`workspace-access`, UI labels, additivity trap, migration timeline 2026-07-27 auto / 2026-09-14 enforced, Genie-only budget block, Consumer-cannot-create-jobs, RLS-contested / Genie-not-a-security-boundary hedges) could **not** be applied — no user-manual document was included in this task. Those checks remain outstanding.