#!/usr/bin/env bash
# =====================================================================================
# bootstrap_cli.sh — the SHELL + Databricks CLI ALTERNATIVE to the Terraform module.
# GENERIC TEMPLATE. No company identifiers.
#
# WHEN TO USE THIS INSTEAD OF TERRAFORM:
#   * one-off bootstrap of a brand-new workspace before CI exists
#   * an operation the TF provider doesn't cover (row-filter DDL, SCIM entitlement PATCH)
#   * you explicitly do NOT want state to manage (throwaway / sandbox)
# WHEN NOT TO: as the ONGOING declarative layer. Shell has no state, no drift detection,
#   no plan preview — for anything long-lived, Terraform (L1-L4) is the right home.
#
# AUTH: expects DATABRICKS_HOST + DATABRICKS_CLIENT_ID + DATABRICKS_CLIENT_SECRET in env
#       (OAuth M2M), same as the Jenkins pipeline.
# =====================================================================================
set -euo pipefail

CATALOG="${CATALOG:-main}"
GOLD="${GOLD_SCHEMA:-gold}"
GROUP="${CONSUMER_GROUP:-consumer-alpha}"   # ACCOUNT group (pre-created via SCIM/Entra)

echo "==> L2 entitlement: make '${GROUP}' Consumer-access only (workspace_consume as SOLE entitlement)"
# SCIM entitlements PATCH — the reliable path when the TF provider version lacks workspace_consume.
GID="$(databricks account groups list --output json | jq -r --arg g "$GROUP" '.[] | select(.displayName==$g) | .id')"
databricks account groups patch "$GID" --json '{
  "schemas":["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
  "Operations":[
    {"op":"add","path":"entitlements","value":[{"value":"workspace-consume"}]}
  ]
}'
# NOTE: also REMOVE workspace-access / databricks-sql-access if inherited, or the lockdown breaks.

echo "==> L4 structural grants (USE CATALOG / USE SCHEMA) — granular, additive"
databricks grants update catalog "$CATALOG" \
  --json "{\"changes\":[{\"principal\":\"$GROUP\",\"add\":[\"USE_CATALOG\"]}]}"
databricks grants update schema "${CATALOG}.${GOLD}" \
  --json "{\"changes\":[{\"principal\":\"$GROUP\",\"add\":[\"USE_SCHEMA\"]}]}"

echo "==> L4 view/control DDL (idempotent) — run the SQL bundle via the CLI"
# databricks sql exec / a warehouse statement API call runs jobs/access_control_ddl.sql + dashboards/cost_views.sql
# (substitute the \${...} placeholders first). Per-table SELECT/EXECUTE + row-filter binding are left to
# jobs/rls_reconcile.py — do NOT hand-grant them here (high churn belongs to the reconciler).

echo "Done. High-churn per-team access is owned by the reconciliation job, not this script."
