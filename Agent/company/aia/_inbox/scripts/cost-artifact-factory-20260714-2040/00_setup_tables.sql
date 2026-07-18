-- =============================================================================
-- Cost Artifact Factory — control tables
-- Generic template. Run once in the coredata DEV workspace.
-- Replace <catalog> with your actual catalog name.
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS <catalog>.ops;

-- -----------------------------------------------------------------------------
-- 1. team_recipient_map — THE single source of truth for "who gets what"
--    Onboard a team  = INSERT 1 row + approval.  No code change.
--    Offboard a team = SET active_to.            No code change.
--    NEVER hand-edit in a notebook: MERGE from a Git-reviewed YAML seed.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS <catalog>.ops.team_recipient_map (
    team_tag          STRING        NOT NULL COMMENT 'MUST equal gold.cost_wide.tag_team exactly',
    display_name      STRING        NOT NULL COMMENT 'Goes in the artifact title + email subject',
    recipients_to     ARRAY<STRING> NOT NULL,
    recipients_cc     ARRAY<STRING>,
    delivery_channel  STRING        NOT NULL COMMENT 'EMAIL | SHAREPOINT | BOTH',
    formats           ARRAY<STRING> NOT NULL COMMENT "e.g. ['HTML','PDF','XLSX']",
    sharepoint_path   STRING,
    cost_centers      ARRAY<STRING>,
    active_from       DATE          NOT NULL,
    active_to         DATE                   COMMENT 'NULL = current. SCD2 → full audit history',
    requested_by      STRING        NOT NULL,
    approved_by       STRING        NOT NULL COMMENT 'NOT NULL by design: no approval, no delivery',
    approved_at       TIMESTAMP     NOT NULL,
    change_ticket     STRING
)
COMMENT 'Recipient mapping. Two-person rule: the DE who runs the job may not be the approver.';

-- -----------------------------------------------------------------------------
-- 2. artifact_ledger — what was RENDERED (recipients snapshotted at render time)
--    T3 (deliver) reads recipients from HERE, not from the map.
--    That binds render + send to the same decision → the map cannot change mid-run.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS <catalog>.ops.artifact_ledger (
    run_id               STRING    NOT NULL,
    team_tag             STRING    NOT NULL,
    period               STRING    NOT NULL COMMENT 'YYYYMM',
    gold_version         BIGINT    NOT NULL COMMENT 'Delta version pinned for the whole run → reproducible',
    artifact_path        STRING    NOT NULL,
    artifact_format      STRING    NOT NULL,
    sha256               STRING    NOT NULL COMMENT 'Idempotency key: same sha + DELIVERED → skip',
    row_count            BIGINT    NOT NULL,
    total_cost           DECIMAL(18,4),
    recipients_snapshot  ARRAY<STRING> NOT NULL,
    status               STRING    NOT NULL COMMENT 'RENDERED | VERIFIED | DELIVERED | FAILED',
    rendered_at          TIMESTAMP NOT NULL,
    delivered_at         TIMESTAMP,
    smtp_message_id      STRING
);

-- -----------------------------------------------------------------------------
-- 3. delivery_audit — append-only. Answers "prove what we sent in March".
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS <catalog>.ops.delivery_audit (
    run_id          STRING    NOT NULL,
    team_tag        STRING    NOT NULL,
    period          STRING    NOT NULL,
    recipients      ARRAY<STRING> NOT NULL,
    artifact_sha256 STRING    NOT NULL,
    channel         STRING    NOT NULL,
    outcome         STRING    NOT NULL,
    message_id      STRING,
    event_ts        TIMESTAMP NOT NULL
)
COMMENT 'APPEND ONLY. Never UPDATE, never DELETE.';


-- -----------------------------------------------------------------------------
-- Seed example
-- -----------------------------------------------------------------------------
INSERT INTO <catalog>.ops.team_recipient_map VALUES
 ('team_a', 'Team A Platform',
  array('team-a-lead@example.com'), array('team-a-mgr@example.com'),
  'EMAIL', array('HTML','PDF','XLSX'), NULL, array('CC1001'),
  DATE'2026-07-01', NULL, 'sin', 'sarunya', current_timestamp(), 'SNOW-12345');


-- -----------------------------------------------------------------------------
-- Pre-flight guard: FAIL CLOSED if any team in gold is not in the map.
-- A team with cost but no recipient = an unowned bucket. Do not silently drop it.
-- -----------------------------------------------------------------------------
SELECT g.tag_team AS unmapped_team, SUM(g.cost) AS orphan_cost
FROM   <catalog>.cost.cost_wide g
LEFT ANTI JOIN (SELECT team_tag FROM <catalog>.ops.team_recipient_map
                WHERE active_to IS NULL) m
       ON g.tag_team = m.team_tag
WHERE  g.period = :period
GROUP BY g.tag_team;
-- ^ non-empty result ⇒ ABORT THE RUN.
