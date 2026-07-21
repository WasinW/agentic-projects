# =====================================================================================
# L1 — Identity (account group SHELL only). ACCOUNT-scoped provider.
#
# CHURN: users = constant (joiner/mover/leaver) -> SCIM from Entra, NEVER Terraform.
#        group shells = low -> optional here. LEAVE MEMBERSHIP TO SCIM (don't manage
#        databricks_group_member in TF or it fights the sync).
#
# Most shops: the Entra group already exists and is synced down. Then DON'T create it here —
# just reference it by display_name in L2/L3/L4. Create it here only if your org lets a
# workspace/account admin mint Databricks-side account groups (confirm — usually an IAM request).
# =====================================================================================
# resource "databricks_group" "consumers" {
#   provider     = databricks.accounts
#   display_name = var.consumer_group_name   # ACCOUNT group — resolves cross-workspace + is_account_group_member()
# }

# Recommended instead: look up the Entra-synced group (do not own its lifecycle here).
data "databricks_group" "consumers" {
  provider     = databricks.accounts
  display_name = var.consumer_group_name
}
