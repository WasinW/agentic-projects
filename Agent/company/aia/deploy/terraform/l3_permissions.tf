# =====================================================================================
# L3 — Object/Asset ACLs. WORKSPACE-scoped provider.
# databricks_permissions is AUTHORITATIVE per object — it overwrites any ACL set outside TF.
#
# Keep long-lived WAREHOUSE ACLs here (TF). Put per-dashboard/per-job ACLs in the DAB that
# ships the asset (define the asset + its permissions together). See dashboards/databricks.yml.
# =====================================================================================
resource "databricks_sql_endpoint" "team" {
  name             = "wh-${var.team}-${var.env}"
  cluster_size     = var.wh_size
  auto_stop_mins   = var.wh_auto_stop      # cost governance lives here (not budgets)
  max_num_clusters = var.wh_max_clusters
}

resource "databricks_permissions" "wh_acl" {
  sql_endpoint_id = databricks_sql_endpoint.team.id
  access_control {
    group_name       = var.consumer_group_name
    permission_level = "CAN_USE"           # NOT CAN_MANAGE — else consumers can edit compute
  }
}

# Dashboard ACL example (if managing a shared dashboard here rather than in the DAB):
# resource "databricks_permissions" "dash" {
#   dashboard_id = "<dashboard-id>"
#   access_control {
#     group_name       = var.consumer_group_name
#     permission_level = "CAN_READ"          # CAN_READ | CAN_RUN | CAN_EDIT | CAN_MANAGE
#   }
# }
# FLAG: Genie space ACL via databricks_permissions (genie_space_id) is UNCONFIRMED in the
# provider — manage Genie space access via the permissions REST API / Genie API until confirmed.
