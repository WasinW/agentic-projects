# =====================================================================================
# L2 — Entitlements. WORKSPACE-scoped provider. Low churn, HIGH blast radius -> codify + PR-gate.
#
# THE LOCKDOWN: entitlements are ADDITIVE. Consumer access only locks down (Genie-only,
# no jobs/clusters/notebooks) if workspace_consume is the SOLE entitlement — every other
# flag MUST stay false, or the lockdown silently breaks.
#
# 2026 MIGRATION: post-enforcement (auto 2026-07-27, enforced 2026-09-14) you may NOT write
# entitlements on the `users`/`admins` SYSTEM groups — target account groups (as below).
# =====================================================================================
resource "databricks_entitlements" "consumers" {
  group_id                   = data.databricks_group.consumers.id
  workspace_consume          = true    # Consumer access — Genie-only lockdown
  workspace_access           = false
  databricks_sql_access      = false   # power-team variant is a SWAP (this true, consume false), NOT additive
  allow_cluster_create       = false
  allow_instance_pool_create = false
}
# FLAG: verify your provider version exposes workspace_consume; if not, set via SCIM entitlements PATCH.
