# Databricks notebook source
# ============================================================================
# AIA — Cost discovery (Genie + Databricks) vs Azure Portal
# ----------------------------------------------------------------------------
# รันใน Databricks notebook (attach cluster/warehouse ที่มี SELECT บน system.billing.*)
# แล้ว capture output ทั้ง 5 query มาให้ดู → จะได้เห็นของจริงในระบบ + บอก logic ที่ตรง Portal ได้
#
# บริบท (verified 2026-07-18, doc-cited):
#   * system.billing = DBU x effective_list = LIST price ล้วน (Databricks เรียกเอง "list-price cost")
#   * pricing struct มี 3 key: default / promotional / effective_list — ไม่มี "negotiated discount"
#     (effective_list != default = PUBLIC promo ที่ทุกลูกค้าได้ ไม่ใช่ discount ของ AIA)
#   * discount จริงของบริษัท + FX(USD->THB) + tax อยู่ใน INVOICE เท่านั้น -> derive ได้จาก
#     Azure Cost Management Export / (list) ไม่ใช่หยิบจาก system table
#   * Genie: free 150 LLM DBU/user/เดือน ดูเหมือน pre-excluded อยู่แล้ว -> "อย่าลบ 150" (Q5 validate)
#
# วิธีใช้ผล: เอา list_usd จาก Q3 (เดือน settled) ไปหารกับเลข Portal เดือนนั้น
#            = effective_rate จริงของ AIA (discount x FX x tax รวมกัน)
# ============================================================================

since = "2026-05-01"   # ปรับได้ — ครอบเดือนที่ settled แล้ว

# COMMAND ----------
# ── Q1 ── product/SKU อะไรถูกใช้จริง + unit/type (มี Genie รึยัง + meter ไหนบ้าง)
print("### Q1 — usage by product / sku / unit / type")
spark.sql(f"""
  SELECT billing_origin_product, sku_name, usage_unit, usage_type,
         count(*) AS rows, round(sum(usage_quantity),2) AS dbus
  FROM system.billing.usage
  WHERE usage_date >= '{since}'
  GROUP BY ALL ORDER BY dbus DESC
""").display()

# COMMAND ----------
# ── Q2 ── pricing struct เต็ม (พิสูจน์ key ที่มี + list vs promo, ไม่มี discount field)
print("### Q2 — pricing struct (full JSON) for SKUs in use")
spark.sql(f"""
  SELECT DISTINCT lp.sku_name, lp.currency_code, lp.price_start_time,
         lp.pricing.default                AS list_default,
         lp.pricing.promotional.default    AS promo_default,
         lp.pricing.effective_list.default AS eff_default,
         to_json(lp.pricing)               AS pricing_full_json
  FROM system.billing.list_prices lp
  WHERE lp.cloud='AZURE'
    AND lp.sku_name IN (SELECT DISTINCT sku_name FROM system.billing.usage WHERE usage_date >= '{since}')
  ORDER BY lp.sku_name, lp.price_start_time DESC
""").display()

# COMMAND ----------
# ── Q3 ── list$ ต่อเดือน ต่อ product (เทียบกับ Portal เดือนเดียวกัน -> ratio = discount x FX x tax)
print("### Q3 — LIST cost per month per product  (เทียบ Portal เพื่อหา effective_rate)")
spark.sql(f"""
  SELECT date_trunc('MONTH', u.usage_date) AS month, u.billing_origin_product,
         round(sum(u.usage_quantity),2) AS dbus,
         round(sum(u.usage_quantity * p.pricing.effective_list.default),2) AS list_usd
  FROM system.billing.usage u
  JOIN system.billing.list_prices p
    ON p.sku_name=u.sku_name AND p.cloud=u.cloud
   AND u.usage_start_time >= p.price_start_time
   AND (p.price_end_time IS NULL OR u.usage_start_time < p.price_end_time)
  WHERE u.usage_date >= '{since}'
  GROUP BY ALL ORDER BY month DESC, list_usd DESC
""").display()

# COMMAND ----------
# ── Q4 ── 1 row Genie เต็มๆ (ระบบให้อะไรต่อ surface — ถ้าว่าง = ยังไม่มี Genie usage)
print("### Q4 — full GENIE rows (what the system provides per surface)")
spark.sql("""
  SELECT usage_date, sku_name, usage_type, usage_unit, usage_quantity,
         usage_metadata.genie.surface AS surface,
         identity_metadata.run_as     AS billed_user,
         to_json(usage_metadata)      AS meta_json,
         to_json(product_features)    AS features_json,
         custom_tags
  FROM system.billing.usage
  WHERE billing_origin_product='GENIE'
  ORDER BY usage_start_time DESC LIMIT 20
""").display()

# COMMAND ----------
# ── Q5 ── Genie DBU ต่อ user ต่อเดือน เรียงน้อย->มาก (gross-vs-net: มี user <150 DBU มั้ย)
print("### Q5 — monthly Genie DBU per user (free-tier gross/net check)")
spark.sql("""
  SELECT date_trunc('MONTH', usage_date) AS month,
         identity_metadata.run_as AS user, round(sum(usage_quantity),2) AS genie_dbus
  FROM system.billing.usage
  WHERE billing_origin_product='GENIE'
  GROUP BY ALL HAVING genie_dbus > 0
  ORDER BY genie_dbus ASC LIMIT 40
""").display()
