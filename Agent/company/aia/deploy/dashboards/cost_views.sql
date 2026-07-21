-- =====================================================================================
-- cost_views.sql  —  shared curated views for BOTH cost dashboards (Topic 2.1)
-- -------------------------------------------------------------------------------------
-- GENERIC TEMPLATE. No company identifiers. Replace ${...} placeholders at deploy time
-- (these are DAB variables — see ../dashboards/databricks.yml).
--
--   ${catalog}        data catalog that holds the gold layer            e.g. main
--   ${gold_schema}    schema for published views                        e.g. gold
--   ${gov_catalog}    governance catalog holding control tables         (may equal ${catalog})
--   ${team_tag_key}   the custom_tags key that carries the team         e.g. CostCenter | BusinessUnit | team
--   ${platform_group} account group that may see ALL teams (FinOps)     e.g. platform-finops
--
-- WHY VIEWS (not row filters on system tables):
--   * system.billing.* cannot have ALTER TABLE ... SET ROW FILTER attached, and has
--     retention limits. So per-team RLS is a SECURE-VIEW PREDICATE baked into the view.
--   * custom_tags is MAP<STRING,STRING>; a UC row filter can't bind to a map element, so
--     the team tag is projected to a real top-level column (team_tag) here.
--
-- RLS RULES (do not change):
--   * use is_account_group_member() — is_member() silently returns FALSE for account users.
--   * consumer groups MUST be ACCOUNT groups, not workspace-local.
--   * publish the dashboard with Individual data permissions (embed_credentials:false),
--     otherwise every viewer runs as the publisher and sees ALL rows.
--
-- COST BASIS: pricing.effective_list.default = LIST price (attribution). Actual $ needs a
--   Cost Management Export meter-rate reconcile. Reconcile DBU-meter <-> DBU-meter, never
--   DBU <-> Portal total. Dashboard A is DBU-only (excludes classic-compute VM cost).
-- =====================================================================================

-- -------------------------------------------------------------------------------------
-- Control tables (governance catalog). Onboard a team = INSERT one row (no DDL).
-- These are the SAME mapping tables the L4 RLS reconciliation job manages
-- (see ../jobs/access_control_ddl.sql). Keep them in one place.
-- -------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ${gov_catalog}.control.team_access_map (
  team_tag       STRING,   -- the value found in custom_tags[${team_tag_key}]
  account_group  STRING    -- the account group that team belongs to, e.g. 'consumer-<team>'
) USING DELTA;

CREATE TABLE IF NOT EXISTS ${gov_catalog}.control.user_team_map (
  user_identity  STRING,   -- identity_metadata.run_as (email) for Genie attribution
  team           STRING,
  account_group  STRING
) USING DELTA;

-- =====================================================================================
-- DASHBOARD A base — all-service priced usage, team projected to a column
-- Grant SELECT on this base view to the PLATFORM/FinOps group ONLY.
-- =====================================================================================
CREATE OR REPLACE VIEW ${catalog}.${gold_schema}.v_billing_priced AS
SELECT
  u.usage_date,
  u.workspace_id,
  u.billing_origin_product                              AS service,
  u.sku_name,
  u.usage_quantity                                      AS dbus,
  u.usage_metadata,
  u.identity_metadata.run_as                            AS run_as,
  COALESCE(NULLIF(trim(u.custom_tags['${team_tag_key}']), ''), '<unattributed>') AS team_tag,
  u.usage_quantity * lp.pricing.effective_list.default  AS list_usd
FROM system.billing.usage u
JOIN system.billing.list_prices lp
  ON  u.sku_name = lp.sku_name
  AND u.cloud    = lp.cloud
  AND u.usage_start_time >= lp.price_start_time                     -- point-in-time price
  AND (lp.price_end_time IS NULL OR u.usage_start_time < lp.price_end_time)
WHERE u.usage_unit = 'DBU';
-- Corrections: RETRACTION rows carry negative qty; SUM() self-nets. Do NOT also filter them.

-- Secure view the published dashboard reads. Grant to each consumer team account group.
CREATE OR REPLACE VIEW ${catalog}.${gold_schema}.v_billing_priced_rls AS
SELECT * FROM ${catalog}.${gold_schema}.v_billing_priced b
WHERE is_account_group_member('${platform_group}')                 -- FinOps sees all teams
   OR EXISTS ( SELECT 1 FROM ${gov_catalog}.control.team_access_map m
               WHERE m.team_tag = b.team_tag
                 AND is_account_group_member(m.account_group) );

-- =====================================================================================
-- DASHBOARD B base — Genie only. Free tier forces billed math at user x month grain.
-- =====================================================================================
CREATE OR REPLACE VIEW ${catalog}.${gold_schema}.v_genie_priced AS
SELECT
  date_trunc('MONTH', u.usage_date)          AS usage_month,
  u.usage_date,
  u.identity_metadata.run_as                 AS run_as,
  u.usage_metadata.genie.surface             AS surface,     -- One/Agents/Code (under-documented — see FLAG G1)
  u.usage_metadata.genie.agent_id            AS agent_id,     -- populated for Agents only
  u.usage_quantity                           AS dbus,
  u.usage_quantity * lp.pricing.effective_list.default AS list_usd,
  (u.identity_metadata.run_as LIKE '%@%')    AS is_identified_user  -- '@' => human (has free tier); UUID => SP/agent (none)
FROM system.billing.usage u
JOIN system.billing.list_prices lp
  ON  u.cloud = lp.cloud AND u.sku_name = lp.sku_name
  AND u.usage_start_time >= lp.price_start_time
  AND (lp.price_end_time IS NULL OR u.usage_start_time < lp.price_end_time)
WHERE u.billing_origin_product = 'GENIE'      -- FLAG G2: verify this value exists in your tenant
  AND u.usage_unit = 'DBU';

-- Secure view: a Genie user sees own rows + their team; platform sees all.
CREATE OR REPLACE VIEW ${catalog}.${gold_schema}.v_genie_priced_rls AS
SELECT g.* FROM ${catalog}.${gold_schema}.v_genie_priced g
LEFT JOIN ${gov_catalog}.control.user_team_map m ON lower(g.run_as) = lower(m.user_identity)
WHERE is_account_group_member('${platform_group}')
   OR lower(g.run_as) = lower(current_user())
   OR (m.account_group IS NOT NULL AND is_account_group_member(m.account_group));

-- =====================================================================================
-- GRANTS to wire it up (run once; or let the L4 reconciler own these going forward)
--   GRANT SELECT ON VIEW ${catalog}.${gold_schema}.v_billing_priced_rls TO `<consumer-team>`;
--   GRANT SELECT ON VIEW ${catalog}.${gold_schema}.v_genie_priced_rls   TO `<consumer-team>`;
-- Giving each team SELECT lets them query from THEIR OWN warehouse (real chargeback) instead of
-- only viewing the publisher-funded dashboard. Ship both: published link + the grant.
-- =====================================================================================
