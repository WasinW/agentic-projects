# deploy/ — AIA Databricks governance + monitoring scaffolds

Generic, parameterized reference code for the platform-governance checklist. **No AIA identifiers** — every `${...}` / `<...>` is a placeholder. Pair with the two docs in `../knowledge/`:

- **[governance-monitoring-web-ui-manual.md](../knowledge/governance-monitoring-web-ui-manual.md)** — Doc 1: click-paths for every layer (do it in the UI)
- **[governance-management-deployment-options.md](../knowledge/governance-management-deployment-options.md)** — Doc 2: which tool for which layer + why, ownership boundary, Jenkins vs job

## The one idea: choose the tool by CHURN, not one-tool-for-everything

| Layer | Churn | Modality | Files |
|---|---|---|---|
| 1.1 Identity (users) | constant | **SCIM** from Entra (never TF/UI membership) | — (IdP team) |
| 1.1 Group shells | low | TF `databricks_group` (optional) | `terraform/l1_identity.tf` |
| **1.2 Entitlement** ⭐ | low, high blast | **Terraform** (PR-gated) | `terraform/l2_entitlements.tf` |
| 1.3 Object ACLs | moderate | **DAB** (asset+ACL together) · TF for warehouses | `terraform/l3_permissions.tf`, `dashboards/databricks.yml` |
| **1.4 Data grant + RLS** ⭐ | **high** | structural→TF · per-team→**reconciliation JOB** | `terraform/l4_grants.tf`, `jobs/` |
| **2.1 Dashboards ×2** ⭐ | build-once | **DAB** + SQL | `dashboards/` |
| SA / SP / network | — | **infra team's TF** (not yours) | — |

## Layout

```
deploy/
├── dashboards/            # Topic 2.1 — both cost dashboards (READY TO RUN)
│   ├── cost_views.sql            # shared base + RLS secure views + team maps
│   ├── dashboard_a_departmental.sql   # per-team all-service (7 visuals)
│   ├── dashboard_b_genie.sql          # Genie gross vs billed (5 visuals)
│   └── databricks.yml            # DAB: view-DDL job + 2 dashboards (embed_credentials:false)
├── jobs/                  # Topic 1.4 — governance-as-data
│   ├── access_control_ddl.sql    # control tables + row-filter UDF + example rows
│   └── rls_reconcile.py          # daily reconcile: desired vs actual -> apply delta (dry-run default)
├── terraform/             # Layer A — L1-L4 structural, low-churn (Jenkins-deployed)
│   ├── providers.tf  variables.tf  l1_identity.tf  l2_entitlements.tf
│   ├── l3_permissions.tf  l4_grants.tf  envs/dev.tfvars
│   └── Jenkinsfile.terraform      # plan-on-PR / apply-on-merge, dev->uat->prod
└── shell/
    └── bootstrap_cli.sh          # the CLI alternative to TF (one-off / API-only ops)
```

## Order to stand it up

1. **infra team** provisions SA / access connector / SP / network → hands you the connector resource ID (you don't TF this — see Doc 2 ownership boundary).
2. **UC wiring** (you or central admin): storage credential → external location → catalog/schema.
3. **TF (Jenkins)**: L1 group ref → L2 entitlement lockdown → L3 warehouse ACL → L4 structural grants.
4. **jobs**: run `access_control_ddl.sql` once, then schedule `rls_reconcile.py` daily (dry-run first).
5. **dashboards**: `databricks bundle deploy` → build visuals in UI → export `.lvdash.json` → commit → redeploy.

## Non-negotiables (baked into the code, don't undo)

- `is_account_group_member()` — never `is_member()` (silently FALSE for account users).
- Consumer groups are **account** groups, not workspace-local.
- Dashboards publish with **`embed_credentials: false`** (default `true` leaks all rows).
- L2 `workspace_consume` must be the **sole** entitlement (additive trap).
- L4 TF uses **`databricks_grant`** (granular), never `databricks_grants` (authoritative) on objects the job touches.
- `rls_reconcile.py` runs **dry-run** until you've watched the diff; SP **owns** the managed securables.
