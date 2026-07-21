# =====================================================================================
# providers.tf — Databricks governance-as-code (Layer A: L1 groups, L2 entitlements,
#                L3 ACLs, L4 structural grants). GENERIC TEMPLATE, no company identifiers.
#
# CRITICAL: L1 account groups use the ACCOUNT-scoped provider; L2/L3/L4 use the
# WORKSPACE-scoped provider. Mixing them is the #1 Terraform-on-Databricks mistake.
# =====================================================================================
terraform {
  required_version = "= <pinned-terraform-version>"          # pin exactly; no ranges in prod
  required_providers {
    databricks = { source = "databricks/databricks", version = "~> 1.121" }  # 1.121.0 = 2026-07-07
    azurerm    = { source = "hashicorp/azurerm", version = "~> <pin>" }
  }
  backend "azurerm" {}   # values injected via -backend-config in Jenkins (see Jenkinsfile.terraform)
}

# Workspace-scoped (L2/L3/L4). host/client_id/client_secret from DATABRICKS_* env in Jenkins.
provider "databricks" {}

# Account-scoped (L1 account groups, account-level entitlement migration).
provider "databricks" {
  alias      = "accounts"
  host       = "https://accounts.azuredatabricks.net"
  account_id = var.databricks_account_id
  # client_id / client_secret from env
}
