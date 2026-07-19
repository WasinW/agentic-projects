# Databricks notebook source
# ============================================================================
# GENIE COST — matched to Azure Portal (assembled end-to-end)
# ----------------------------------------------------------------------------
# เหลือเติม INPUT เดียว: portal_dbu_meter_actual_usd (§STEP 0)
#   = เลข Portal (Azure Cost Management) ของ "Azure Databricks" DBU meter เดือน settled
#     ⚠️ เอาเฉพาะ meter DBU (Azure Databricks) — อย่ารวม "Virtual Machines" (VM คนละ meter, DBU↔DBU เท่านั้น)
#     ⚠️ ถ้า Portal เป็น THB → แปลงเป็น USD ก่อน หรือใช้ CostInUsd ใน Export
#
# logic (validated concepts):
#   1. Genie billed DBU = per-user floor: GREATEST(0, genie_dbus - 150)  (GROSS table, หัก free tier ต่อ identified user)
#      - SP/agent (run_as = UUID ไม่มี '@') ไม่มี free tier → ไม่หัก
#   2. total_billed_list$ = Genie billed list$  +  non-Genie gross list$   (ตัวหารของ effective_rate)
#   3. effective_rate = Portal DBU-meter actual $  ÷  total_billed_list$   (= discount × FX × tax, blended)
#   4. Genie reconciled actual $ = Genie billed list$ × effective_rate
#
# ⚠️ CAVEATS (พูดกับ stakeholder ตามนี้ — เป็น approximation ไม่ใช่ invoice line):
#   (a) สมมติ discount×FX×tax "uniform" ทั่วทุก DBU SKU — ถ้า discount ต่าง SKU ต้องทำ per-meter (§note)
#   (b) Portal input = DBU meter only (ไม่รวม VM/networking) เพื่อเทียบ DBU↔DBU
#   (c) per-user เป็น proportional allocation ของ actual ระดับ meter — ไม่ใช่บิลต่อคนจริง
#   (d) validate: รันเดือน settled (มิ.ย.) เทียบกับ Portal จริง — ถ้าเพี้ยนมาก แปลว่า discount ไม่ uniform → ไป §note
# ============================================================================

# COMMAND ----------
spark.sql("DECLARE OR REPLACE VARIABLE start_date DATE DEFAULT DATE'2026-06-01'")
spark.sql("DECLARE OR REPLACE VARIABLE end_date   DATE DEFAULT DATE'2026-06-30'")
# ⬇️⬇️ เติมเลข Portal ตรงนี้ (Azure Databricks DBU meter, USD, เดือน settled) ⬇️⬇️
spark.sql("DECLARE OR REPLACE VARIABLE portal_dbu_meter_actual_usd DECIMAL(18,2) DEFAULT NULL")
# ตัวอย่าง: spark.sql("SET VAR portal_dbu_meter_actual_usd = 250000.00")

# COMMAND ----------
# ── FINAL — Genie cost matched to Portal ──
print("### Genie cost reconciled to Portal (settled month)")
spark.sql("""
WITH genie_per_user AS (         -- 1) รวม Genie DBU ต่อ user (pooled ทุก surface)
  SELECT identity_metadata.run_as AS run_as, SUM(usage_quantity) AS g_dbus
  FROM system.billing.usage
  WHERE billing_origin_product='GENIE' AND usage_date BETWEEN start_date AND end_date
  GROUP BY ALL
),
genie AS (                       -- Genie billed DBU (หัก free 150 per identified user; SP ไม่หัก)
  SELECT SUM(GREATEST(g_dbus - CASE WHEN run_as LIKE '%@%' THEN 150 ELSE 0 END, 0)) AS billed_dbus,
         SUM(g_dbus) AS gross_dbus
  FROM genie_per_user
),
genie_rate AS (                  -- blended Genie effective_list rate ($/DBU)
  SELECT SUM(u.usage_quantity*p.pricing.effective_list.default)/NULLIF(SUM(u.usage_quantity),0) AS rate
  FROM system.billing.usage u JOIN system.billing.list_prices p
    ON p.sku_name=u.sku_name AND p.cloud=u.cloud
   AND u.usage_start_time>=p.price_start_time AND (p.price_end_time IS NULL OR u.usage_start_time<p.price_end_time)
  WHERE u.billing_origin_product='GENIE' AND u.usage_unit='DBU' AND u.usage_date BETWEEN start_date AND end_date
),
nongenie_list AS (               -- 2) non-Genie gross list$ (DBU only, ไม่มี free tier → gross = billed)
  SELECT SUM(u.usage_quantity*p.pricing.effective_list.default) AS list_usd
  FROM system.billing.usage u JOIN system.billing.list_prices p
    ON p.sku_name=u.sku_name AND p.cloud=u.cloud
   AND u.usage_start_time>=p.price_start_time AND (p.price_end_time IS NULL OR u.usage_start_time<p.price_end_time)
  WHERE u.billing_origin_product<>'GENIE' AND u.usage_unit='DBU' AND u.usage_date BETWEEN start_date AND end_date
)
SELECT
  ROUND(g.gross_dbus,2)                                          AS genie_gross_dbus,
  ROUND(g.billed_dbus,2)                                         AS genie_billed_dbus,      -- หลังหัก free
  ROUND(gr.rate,4)                                              AS genie_list_rate,
  ROUND(g.billed_dbus*gr.rate,2)                                AS genie_billed_list_usd,   -- ก่อน discount
  ROUND(g.billed_dbus*gr.rate + ng.list_usd,2)                  AS total_billed_list_usd,   -- ตัวหาร effective_rate
  portal_dbu_meter_actual_usd                                   AS portal_actual_usd,       -- ← input ของคุณ
  ROUND(portal_dbu_meter_actual_usd/NULLIF(g.billed_dbus*gr.rate + ng.list_usd,0),4) AS effective_rate, -- discount×FX×tax
  -- ⭐ ตัวเลขสุดท้าย: Genie cost ที่ "ตรง Portal" (approximate)
  ROUND(g.billed_dbus*gr.rate * (portal_dbu_meter_actual_usd/NULLIF(g.billed_dbus*gr.rate + ng.list_usd,0)),2)
                                                                AS genie_reconciled_actual_usd
FROM genie g CROSS JOIN genie_rate gr CROSS JOIN nongenie_list ng
""").display()

# COMMAND ----------
# ── ถ้ามี Cost Management Export เป็น table แล้ว → ไม่ต้องเติมเลข Portal เอง (auto) ──
# แก้ <cost_export_table> + column names แล้ว uncomment:
# spark.sql("""
#   ... (join Export meter 'Azure Databricks' เพื่อดึง portal actual อัตโนมัติ) ...
# """).display()
#
# §note — ถ้า validate แล้วเพี้ยน (discount ไม่ uniform):
#   ทำ effective_rate "per meter/SKU" แทน whole-account: หาร actual÷list ที่ระดับ SKU กลุ่มเดียวกัน
#   (Genie SKU = PREMIUM_SERVERLESS_REAL_TIME_INFERENCE_* ซึ่ง share กับ MODEL_SERVING+VECTOR_SEARCH)
