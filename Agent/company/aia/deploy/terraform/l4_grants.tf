# =====================================================================================
# L4 — STRUCTURAL grants only (catalog/schema level, low churn). WORKSPACE-scoped provider.
#
# ⚠ SCOPE: keep in TF ONLY the low-churn structural grants (USE CATALOG / USE SCHEMA).
# High-churn per-team TABLE/ROW grants belong to the reconciliation JOB (../jobs/rls_reconcile.py),
# NOT here — putting them in TF means a PR+plan+apply per team change and a ballooning state.
#
# ⚠ USE databricks_grant (granular, per-principal, additive) — NEVER databricks_grants
# (authoritative, overwrites ALL grants on the securable) on any object whose CHILDREN the
# runtime job touches. Authoritative here would revert the job's table-level grants each apply.
# This is the rule that keeps CI and the runtime job from fighting.
# =====================================================================================
resource "databricks_grant" "catalog_use" {
  catalog    = var.catalog
  principal  = var.consumer_group_name
  privileges = ["USE_CATALOG"]
}

resource "databricks_grant" "schema_use" {
  schema     = "${var.catalog}.${var.gold_schema}"
  principal  = var.consumer_group_name
  privileges = ["USE_SCHEMA"]
}

# Table SELECT + FUNCTION EXECUTE + ROW FILTER binding are intentionally NOT here.
# They are high-churn and data-driven -> managed by ../jobs/rls_reconcile.py from the control table.
