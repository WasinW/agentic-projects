-- =====================================================================================
-- Dashboard A — "Departmental per-team, ALL-service cost"   (Topic 2.1 #1)
-- One query per visual. All read v_billing_priced_rls so per-team RLS applies.
-- Params: :date_start :date_end (default last 30d) · :as_of_date (default current_date())
-- Reads views from cost_views.sql. ${catalog}.${gold_schema} replaced at deploy.
-- =====================================================================================

-- A1  KPI counters. pct_unattributed = tag-hygiene health signal.
SELECT
  SUM(dbus)                                                                 AS total_dbus,
  SUM(list_usd)                                                             AS total_list_usd,
  COUNT(DISTINCT CASE WHEN team_tag <> '<unattributed>' THEN team_tag END)  AS teams_attributed,
  ROUND(100 * SUM(CASE WHEN team_tag = '<unattributed>' THEN list_usd END)
            / NULLIF(SUM(list_usd), 0), 1)                                  AS pct_unattributed
FROM ${catalog}.${gold_schema}.v_billing_priced_rls
WHERE usage_date BETWEEN :date_start AND :date_end;

-- A2  Daily trend (line)
SELECT usage_date, SUM(list_usd) AS list_usd, SUM(dbus) AS dbus
FROM ${catalog}.${gold_schema}.v_billing_priced_rls
WHERE usage_date BETWEEN :date_start AND :date_end
GROUP BY usage_date ORDER BY usage_date;

-- A3  Cost by service = billing_origin_product (bar)
SELECT service, SUM(dbus) AS dbus, SUM(list_usd) AS list_usd
FROM ${catalog}.${gold_schema}.v_billing_priced_rls
WHERE usage_date BETWEEN :date_start AND :date_end
GROUP BY service ORDER BY list_usd DESC;

-- A4  Team x Service matrix (stacked bar / pivot)
SELECT team_tag, service, sku_name, SUM(list_usd) AS list_usd, SUM(dbus) AS dbus
FROM ${catalog}.${gold_schema}.v_billing_priced_rls
WHERE usage_date BETWEEN :date_start AND :date_end
GROUP BY team_tag, service, sku_name ORDER BY list_usd DESC;

-- A5  Per-team + month-over-month (table)
WITH m AS (
  SELECT team_tag, date_trunc('MONTH', usage_date) AS mth, SUM(list_usd) AS list_usd
  FROM ${catalog}.${gold_schema}.v_billing_priced_rls
  WHERE usage_date >= add_months(date_trunc('MONTH', :as_of_date), -1)
    AND usage_date <  add_months(date_trunc('MONTH', :as_of_date),  1)
  GROUP BY team_tag, date_trunc('MONTH', usage_date)
)
SELECT
  team_tag,
  MAX(CASE WHEN mth = date_trunc('MONTH', :as_of_date)                 THEN list_usd END) AS this_month_usd,
  MAX(CASE WHEN mth = add_months(date_trunc('MONTH', :as_of_date), -1) THEN list_usd END) AS last_month_usd,
  ROUND(100 * (
      COALESCE(MAX(CASE WHEN mth = date_trunc('MONTH', :as_of_date) THEN list_usd END), 0)
    - COALESCE(MAX(CASE WHEN mth = add_months(date_trunc('MONTH', :as_of_date), -1) THEN list_usd END), 0)
  ) / NULLIF(MAX(CASE WHEN mth = add_months(date_trunc('MONTH', :as_of_date), -1) THEN list_usd END), 0), 1)
                                                                                          AS mom_pct
FROM m GROUP BY team_tag ORDER BY this_month_usd DESC NULLS LAST;

-- A6  Top compute / objects by cost (table)
SELECT
  service,
  COALESCE(usage_metadata.job_id, usage_metadata.warehouse_id, usage_metadata.cluster_id,
           usage_metadata.dlt_pipeline_id, usage_metadata.endpoint_name, usage_metadata.app_id) AS object_id,
  COALESCE(usage_metadata.job_name, usage_metadata.app_name, usage_metadata.endpoint_name)       AS object_name,
  SUM(dbus) AS dbus, SUM(list_usd) AS list_usd
FROM ${catalog}.${gold_schema}.v_billing_priced_rls
WHERE usage_date BETWEEN :date_start AND :date_end
GROUP BY 1, 2, 3 ORDER BY list_usd DESC LIMIT 25;

-- A7  Unattributed bucket detail (table) — drives tag remediation
SELECT workspace_id, service, sku_name, SUM(dbus) AS dbus, SUM(list_usd) AS list_usd
FROM ${catalog}.${gold_schema}.v_billing_priced_rls
WHERE usage_date BETWEEN :date_start AND :date_end
  AND team_tag = '<unattributed>'
GROUP BY workspace_id, service, sku_name ORDER BY list_usd DESC;

-- LAYOUT (AI/BI Lakeview):
--   row1: A1 x4 Counter (total DBU · total list$ · #teams · %unattributed)
--   row2: A2 Line (wide)
--   row3: A3 Bar (left) | A5 Table+MoM% conditional color (right)
--   row4: A4 Stacked bar / pivot (wide)
--   row5: A6 Table top-25 (left) | A7 Table unattributed (right)
-- FILTERS: :date_start/:date_end (date range) · :as_of_date · service field-filter.
--   A team dropdown is CONVENIENCE only, NOT the security boundary (RLS is — see cost_views.sql).
