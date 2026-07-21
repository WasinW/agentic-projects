-- =====================================================================================
-- Dashboard B — "Genie AI cost" (gross vs billed)   (Topic 2.1 #2)
-- Genie has no per-team tag → team comes from user_team_map keyed on run_as.
-- Free tier (150 DBU/identified user/month, POOLED across surfaces) is applied at
-- user x month grain BEFORE any surface/team split. SP/agents (UUID run_as) get none.
-- Params: :as_of_date (month, default current_date()) · :date_start/:date_end (trend)
--         :free_tier_dbus (default 150 — a pricing-page constant, FLAG G3)
-- =====================================================================================

-- B1  KPI counters — GROSS vs BILLED for the month
WITH per_user AS (
  SELECT run_as, MAX(is_identified_user) AS is_identified_user,
         SUM(dbus) AS gross_dbus, SUM(list_usd) AS gross_list_usd
  FROM ${catalog}.${gold_schema}.v_genie_priced_rls
  WHERE usage_month = date_trunc('MONTH', :as_of_date)
  GROUP BY run_as
)
SELECT
  SUM(gross_dbus)                                                                        AS gross_dbus,
  SUM(CASE WHEN is_identified_user THEN GREATEST(gross_dbus - :free_tier_dbus, 0)
           ELSE gross_dbus END)                                                          AS billed_dbus,
  SUM((CASE WHEN is_identified_user THEN GREATEST(gross_dbus - :free_tier_dbus, 0)
            ELSE gross_dbus END) * (gross_list_usd / NULLIF(gross_dbus, 0)))             AS billed_list_usd,
  COUNT_IF(is_identified_user AND gross_dbus > :free_tier_dbus)                          AS users_over_free_tier,
  COUNT_IF(NOT is_identified_user)                                                       AS sp_or_agents_no_free_tier
FROM per_user;

-- B2  Per USER, gross vs billed (table)
WITH per_user AS (
  SELECT run_as, MAX(is_identified_user) AS is_identified_user,
         SUM(dbus) AS gross_dbus, SUM(list_usd) AS gross_list_usd
  FROM ${catalog}.${gold_schema}.v_genie_priced_rls
  WHERE usage_month = date_trunc('MONTH', :as_of_date)
  GROUP BY run_as
)
SELECT
  run_as, is_identified_user, gross_dbus,
  CASE WHEN is_identified_user THEN GREATEST(gross_dbus - :free_tier_dbus, 0)
       ELSE gross_dbus END                                                        AS billed_dbus,
  gross_list_usd,
  (CASE WHEN is_identified_user THEN GREATEST(gross_dbus - :free_tier_dbus, 0)
        ELSE gross_dbus END) * (gross_list_usd / NULLIF(gross_dbus, 0))           AS billed_list_usd
FROM per_user ORDER BY billed_list_usd DESC;

-- B3  Per SURFACE — GROSS ONLY (free tier is pooled across surfaces → can't net per surface)
SELECT surface, SUM(dbus) AS gross_dbus, SUM(list_usd) AS gross_list_usd
FROM ${catalog}.${gold_schema}.v_genie_priced_rls
WHERE usage_month = date_trunc('MONTH', :as_of_date)
GROUP BY surface ORDER BY gross_list_usd DESC;

-- B4  Per TEAM — billed computed at user grain, THEN summed to team
WITH per_user AS (
  SELECT run_as, MAX(is_identified_user) AS is_identified_user,
         SUM(dbus) AS gross_dbus, SUM(list_usd) AS gross_list_usd
  FROM ${catalog}.${gold_schema}.v_genie_priced_rls
  WHERE usage_month = date_trunc('MONTH', :as_of_date)
  GROUP BY run_as
)
SELECT
  COALESCE(m.team, '<unmapped>') AS team,
  SUM(pu.gross_dbus)                                                                     AS gross_dbus,
  SUM(CASE WHEN pu.is_identified_user THEN GREATEST(pu.gross_dbus - :free_tier_dbus, 0)
           ELSE pu.gross_dbus END)                                                       AS billed_dbus,
  SUM(pu.gross_list_usd)                                                                 AS gross_list_usd,
  SUM((CASE WHEN pu.is_identified_user THEN GREATEST(pu.gross_dbus - :free_tier_dbus, 0)
            ELSE pu.gross_dbus END) * (pu.gross_list_usd / NULLIF(pu.gross_dbus, 0)))    AS billed_list_usd
FROM per_user pu
LEFT JOIN ${gov_catalog}.control.user_team_map m ON lower(pu.run_as) = lower(m.user_identity)
GROUP BY COALESCE(m.team, '<unmapped>') ORDER BY billed_list_usd DESC;

-- B5  Trend (line) — GROSS daily (billed is a monthly concept; free tier resets on the 1st)
SELECT usage_date, SUM(dbus) AS gross_dbus, SUM(list_usd) AS gross_list_usd
FROM ${catalog}.${gold_schema}.v_genie_priced_rls
WHERE usage_date BETWEEN :date_start AND :date_end
GROUP BY usage_date ORDER BY usage_date;

-- LAYOUT (AI/BI Lakeview):
--   row1: B1 x5 Counter (gross DBU · billed DBU · billed$ · #users over free · #SP/agents)
--   row2: B5 Line (wide)
--   row3: B3 Bar by surface (left) | B4 Table per-team gross vs billed (right)
--   row4: B2 Table per-user (wide, sort billed$ desc, badge SP/agent)
-- FILTERS: :as_of_date (month) · :date_start/:date_end (trend) · :free_tier_dbus · surface field-filter.
--
-- VERIFY-IN-TENANT before trusting (flags carried from research):
--   G1 usage_metadata.genie.{surface,agent_id} under-documented → SELECT usage_metadata.genie.* to confirm;
--      if absent, drop B3 and attribute by run_as only.
--   G2 billing_origin_product='GENIE' not in official enum → SELECT DISTINCT billing_origin_product;
--      if absent Genie may ride AI_GATEWAY meter — adjust filter in cost_views.sql.
--   G3 150 free tier is a pricing-page constant → parameterized; verify per region/time.
--   G4 GROSS validated on tenant data (rows exist for users < 150 DBU). Re-check if tenant behaves 'net'.
