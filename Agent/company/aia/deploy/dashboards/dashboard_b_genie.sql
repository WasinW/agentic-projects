-- =====================================================================================
-- Dashboard B — "Genie AI cost" (gross vs billed)   (Topic 2.1 #2)
-- ⭐ CORRECTED 2026-07-26 to the SKU-SPLIT model (Databricks `genie/monitor-cost`, 2026-07-20):
--   BILLED = rows where NOT is_free_tier (sku_name <> 'GENIE_FREE_USAGE').  DO NOT subtract 150.
--   FREE   = rows where is_free_tier (sku_name = 'GENIE_FREE_USAGE') — recorded but $0, no price row.
--   The 25% promo is already baked into usage_quantity. SPs/agents get no free tier (all their rows billed).
-- Reads v_genie_priced_rls (carries sku_name + is_free_tier + list_usd). Genie has no per-team tag →
--   team comes from user_team_map keyed on run_as. Params: :as_of_date (month) · :date_start/:date_end (trend).
-- =====================================================================================

-- B1  KPI counters — GROSS vs FREE vs BILLED for the month
SELECT
  ROUND(SUM(dbus), 0)                                              AS gross_dbus,
  ROUND(SUM(CASE WHEN is_free_tier THEN dbus ELSE 0 END), 0)       AS free_dbus,
  ROUND(SUM(CASE WHEN NOT is_free_tier THEN dbus ELSE 0 END), 0)   AS billed_dbus,
  ROUND(SUM(CASE WHEN NOT is_free_tier THEN COALESCE(list_usd,0) ELSE 0 END), 2) AS billed_list_usd,
  COUNT(DISTINCT CASE WHEN NOT is_free_tier THEN run_as END)       AS users_with_billed,
  COUNT(DISTINCT CASE WHEN NOT is_identified_user THEN run_as END) AS sp_or_agents
FROM ${catalog}.${gold_schema}.v_genie_priced_rls
WHERE usage_month = date_trunc('MONTH', :as_of_date);

-- B2  Per USER, gross vs billed (table)
SELECT
  run_as,
  is_identified_user,
  ROUND(SUM(dbus), 0)                                              AS gross_dbus,
  ROUND(SUM(CASE WHEN is_free_tier THEN dbus ELSE 0 END), 0)       AS free_dbus,
  ROUND(SUM(CASE WHEN NOT is_free_tier THEN dbus ELSE 0 END), 0)   AS billed_dbus,
  ROUND(SUM(CASE WHEN NOT is_free_tier THEN COALESCE(list_usd,0) ELSE 0 END), 2) AS billed_list_usd
FROM ${catalog}.${gold_schema}.v_genie_priced_rls
WHERE usage_month = date_trunc('MONTH', :as_of_date)
GROUP BY run_as, is_identified_user
ORDER BY billed_list_usd DESC;

-- B3  Per SURFACE — gross + billed (free tier is pooled, but SKU split lets us show both)
SELECT
  surface,
  ROUND(SUM(dbus), 0)                                              AS gross_dbus,
  ROUND(SUM(CASE WHEN NOT is_free_tier THEN dbus ELSE 0 END), 0)   AS billed_dbus,
  ROUND(SUM(CASE WHEN NOT is_free_tier THEN COALESCE(list_usd,0) ELSE 0 END), 2) AS billed_list_usd
FROM ${catalog}.${gold_schema}.v_genie_priced_rls
WHERE usage_month = date_trunc('MONTH', :as_of_date)
GROUP BY surface ORDER BY billed_list_usd DESC;

-- B4  Per TEAM (billed) — join user_team_map on run_as
SELECT
  COALESCE(m.team, '<unmapped>') AS team,
  ROUND(SUM(g.dbus), 0)                                              AS gross_dbus,
  ROUND(SUM(CASE WHEN NOT g.is_free_tier THEN g.dbus ELSE 0 END), 0) AS billed_dbus,
  ROUND(SUM(CASE WHEN NOT g.is_free_tier THEN COALESCE(g.list_usd,0) ELSE 0 END), 2) AS billed_list_usd
FROM ${catalog}.${gold_schema}.v_genie_priced_rls g
LEFT JOIN ${gov_catalog}.control.user_team_map m ON lower(g.run_as) = lower(m.user_identity)
WHERE g.usage_month = date_trunc('MONTH', :as_of_date)
GROUP BY COALESCE(m.team, '<unmapped>') ORDER BY billed_list_usd DESC;

-- B5  Trend (line) — daily gross vs billed DBU
SELECT
  usage_date,
  ROUND(SUM(dbus), 0)                                              AS gross_dbus,
  ROUND(SUM(CASE WHEN NOT is_free_tier THEN dbus ELSE 0 END), 0)   AS billed_dbus,
  ROUND(SUM(CASE WHEN NOT is_free_tier THEN COALESCE(list_usd,0) ELSE 0 END), 2) AS billed_list_usd
FROM ${catalog}.${gold_schema}.v_genie_priced_rls
WHERE usage_date BETWEEN :date_start AND :date_end
GROUP BY usage_date ORDER BY usage_date;

-- LAYOUT (AI/BI Lakeview):
--   row1: B1 x6 Counter (gross DBU · free DBU · billed DBU · billed$ · #users billed · #SP/agents)
--   row2: B5 Line (daily gross vs billed)
--   row3: B3 Bar by surface (left) | B4 Table per-team (right)
--   row4: B2 Table per-user (wide, sort billed$ desc, badge SP/agent)
-- FILTERS: :as_of_date (month) · :date_start/:date_end (trend) · surface field-filter.
--
-- ⭐ VERIFY IN-TENANT before trusting (run first):
--   SELECT DISTINCT sku_name, usage_unit, usage_type, usage_metadata.genie.surface
--   FROM system.billing.usage WHERE billing_origin_product='GENIE' ORDER BY sku_name;
--   Expect: GENIE_FREE_USAGE (free) + ENTERPRISE_SERVERLESS_REAL_TIME_INFERENCE_<REGION> (billed), both usage_unit='DBU'.
--   Free/billed sanity per user (sub-150 users → free_dbus>0, paid_dbus=0 = working as documented):
--     SELECT identity_metadata.run_as,
--            SUM(CASE WHEN sku_name='GENIE_FREE_USAGE' THEN usage_quantity ELSE 0 END) AS free_dbus,
--            SUM(CASE WHEN sku_name!='GENIE_FREE_USAGE' THEN usage_quantity ELSE 0 END) AS paid_dbus
--     FROM system.billing.usage WHERE billing_origin_product='GENIE'
--       AND usage_date >= date_trunc('MONTH', current_date()) GROUP BY 1;
--   Transition: GENIE_FREE_USAGE only from 2026-07-20; Genie One/Agents free thru 2026-07-31 (billed grows Aug).
--   Portal reconciliation = DBU-meter↔DBU-meter vs Cost Mgmt Export (list ≠ invoice: discount/FX/tax).
