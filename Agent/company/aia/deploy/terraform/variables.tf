# variables.tf — GENERIC placeholders. Real values go in envs/<env>.tfvars (git-ignored if sensitive).
variable "databricks_account_id" { type = string }
variable "env"                   { type = string }              # dev | uat | prod
variable "catalog"               { type = string }
variable "gold_schema"           { type = string, default = "gold" }

# The consumer team this stack manages. Model one stack per team, or a map for many.
variable "team"                  { type = string }              # e.g. "alpha"
variable "consumer_group_name"   { type = string }              # e.g. "consumer-alpha" (ACCOUNT group)

# Warehouse sizing (cost governance lives here, not in budgets).
variable "wh_size"          { type = string, default = "Small" }
variable "wh_auto_stop"     { type = number, default = 10 }     # minutes
variable "wh_max_clusters"  { type = number, default = 1 }
