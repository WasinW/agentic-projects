-- =====================================================================================
-- access_control_ddl.sql — L4 governance-as-data control tables + RLS UDFs
-- GENERIC TEMPLATE. No company identifiers. Replace ${gov_catalog} ${catalog} ${gold_schema}.
--
-- This is the DESIRED-STATE store the reconciliation job (rls_reconcile.py) reads.
-- Onboarding a team / a table = INSERT rows here. No DDL, no PR for routine access change.
-- =====================================================================================

CREATE SCHEMA IF NOT EXISTS ${gov_catalog}.control;

-- -------------------------------------------------------------------------------------
-- The unified control table. rule_type discriminates GRANT / ROW_FILTER / COLUMN_MASK / ABAC_POLICY.
-- -------------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ${gov_catalog}.control.access_control (
  rule_id          STRING,        -- stable hash of the natural key (idempotency anchor)
  rule_type        STRING,        -- 'GRANT' | 'ROW_FILTER' | 'COLUMN_MASK' | 'ABAC_POLICY'
  securable_type   STRING,        -- 'CATALOG' | 'SCHEMA' | 'TABLE' | 'FUNCTION'
  securable_fqn    STRING,        -- fully qualified, e.g. '<catalog>.gold.cost_by_team'
  principal        STRING,        -- ACCOUNT group, e.g. 'consumer-<team>' (NULL for tag-driven ABAC)
  privilege        STRING,        -- GRANT rows: 'SELECT'|'USE CATALOG'|'USE SCHEMA'|'EXECUTE'|'MODIFY'
  policy_name      STRING,        -- ABAC_POLICY rows: the CREATE POLICY name
  function_fqn     STRING,        -- ROW_FILTER/COLUMN_MASK/ABAC: the UDF used
  target_columns   ARRAY<STRING>, -- row-filter args, masked column, or USING COLUMNS
  tag_predicate    STRING,        -- ABAC only, e.g. "has_tag_value('team','alpha')"
  desired_state    STRING,        -- 'PRESENT' | 'ABSENT'  (ABSENT = explicit revoke/unbind)
  environment      STRING,        -- 'dev' | 'uat' | 'prod'  (scopes which run touches it)
  enabled          BOOLEAN,       -- soft on/off without deleting the row
  owner            STRING,        -- requester / approver (audit)
  ticket_ref       STRING,        -- change-request id (audit)
  updated_at       TIMESTAMP
) USING DELTA;

-- Decouples data-tag value from group name. Shared with the dashboards (cost_views.sql).
CREATE TABLE IF NOT EXISTS ${gov_catalog}.control.team_access_map (
  team_tag       STRING,
  account_group  STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS ${gov_catalog}.control.user_team_map (
  user_identity  STRING,
  team           STRING,
  account_group  STRING
) USING DELTA;

-- Run-log the reconciler appends to (audit trail; reconcile vs system.access.audit for drift).
CREATE TABLE IF NOT EXISTS ${gov_catalog}.control.reconcile_audit (
  run_id     STRING,
  ts         TIMESTAMP,
  rule_id    STRING,
  action     STRING,       -- GRANT | REVOKE | SET_ROW_FILTER | DROP_ROW_FILTER | SET_MASK | ...
  statement  STRING,
  status     STRING,       -- PLANNED | APPLIED | FAILED
  error      STRING,
  dry_run    BOOLEAN
) USING DELTA;

-- -------------------------------------------------------------------------------------
-- The row-filter UDF (mapping-table driven). is_account_group_member() — NEVER is_member().
-- One gold table per domain → a single per-table filter is the pragmatic choice.
-- Graduate to ABAC CREATE POLICY when table count outgrows hand-binding (see Doc 2 §L4).
-- -------------------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION ${catalog}.${gold_schema}.fn_team_rls(team_tag STRING)
RETURN
  is_account_group_member('${platform_group}')            -- platform bypass sees all rows
  OR EXISTS ( SELECT 1 FROM ${gov_catalog}.control.team_access_map m
              WHERE m.team_tag = team_tag
                AND is_account_group_member(m.account_group) );

-- Example bind (the reconciler does this from a ROW_FILTER control row):
--   ALTER TABLE ${catalog}.${gold_schema}.cost_by_team
--     SET ROW FILTER ${catalog}.${gold_schema}.fn_team_rls ON (team_tag);
-- Don't forget the paired grant (the #1 gotcha):
--   GRANT EXECUTE ON FUNCTION ${catalog}.${gold_schema}.fn_team_rls TO `consumer-<team>`;

-- =====================================================================================
-- Example desired-state rows for onboarding one team ('alpha'). The 4 grants move together.
-- =====================================================================================
-- INSERT INTO ${gov_catalog}.control.team_access_map VALUES ('alpha','consumer-alpha');
-- INSERT INTO ${gov_catalog}.control.access_control (rule_type,securable_type,securable_fqn,principal,privilege,function_fqn,target_columns,desired_state,environment,enabled) VALUES
--   ('GRANT','CATALOG','${catalog}','consumer-alpha','USE CATALOG',NULL,NULL,'PRESENT','prod',true),
--   ('GRANT','SCHEMA','${catalog}.${gold_schema}','consumer-alpha','USE SCHEMA',NULL,NULL,'PRESENT','prod',true),
--   ('GRANT','TABLE','${catalog}.${gold_schema}.cost_by_team','consumer-alpha','SELECT',NULL,NULL,'PRESENT','prod',true),
--   ('GRANT','FUNCTION','${catalog}.${gold_schema}.fn_team_rls','consumer-alpha','EXECUTE',NULL,NULL,'PRESENT','prod',true),
--   ('ROW_FILTER','TABLE','${catalog}.${gold_schema}.cost_by_team',NULL,NULL,'${catalog}.${gold_schema}.fn_team_rls',array('team_tag'),'PRESENT','prod',true);
