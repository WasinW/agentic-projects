# Discussion: Gamification Dataform Issues
Date: 2026-04-05
Status: open
Initiated by: domain-others
Participants: domain-others, architect-data (pending review)

## Context
Investigation of Dataform workflow FAILED + all known issues from `gamification/pending_work.md`.
Covers both `master-collector/dataform/` (missions + ballots) and `account-missions-collector/dataform/` (account_missions).

## Findings

### domain-others says:

---

### Issue 1: Dataform Workflow FAILED -- Root Cause Analysis

**Symptom**: Workflow invocation fails instantly (~200ms) with `state: FAILED` and no action-level detail.

**Root cause**: Missing IAM roles for the Dataform execution SA (`t1-master-collector@the1-gamification-data-{env}.iam.gserviceaccount.com`).

**Evidence from Terraform**:
- `dataform.tf` sets `service_account = "t1-master-collector@..."` on both workflow configs (missions-daily, ballots-daily)
- The SA has these grants in Terraform:
  - `roles/biglake.editor` on source catalog (`biglake-metastore.tf`)
  - `roles/storage.objectAdmin` on Dataflow staging bucket (`gcs-bucket.tf`)
- The SA is **missing** these required grants:
  - `roles/bigquery.jobUser` (project-level) -- required to run BQ queries
  - `roles/bigquery.dataEditor` on `refined` + `public` datasets -- required to CREATE/REPLACE TABLE and VIEW
  - `roles/bigquery.dataViewer` on the source BigLake-linked dataset (the `source` dataset in the source project `the1-gamification-data-source-{env}`) -- required to SELECT from Iceberg source tables
  - Possibly `roles/biglake.viewer` or `objectViewer` on GCS source bucket -- required to read Iceberg data files

**Comparison with message domain**: The message domain's `messages-collector/bigquery.tf` uses a `bigquery-dataset-iam` terraform module to grant `dataOwner` on the source dataset. Gamification has no such module.

**Why it fails instantly**: Without `bigquery.jobUser`, the Dataform workflow cannot even start a BQ job. BQ returns permission denied before any query executes, causing immediate FAILED state with no action-level output.

**Fix**: Add to `infrastructure/master-collector/` (new file, e.g., `bigquery-iam.tf`):
```hcl
# Project-level: allow SA to run BQ jobs
resource "google_project_iam_member" "dataform_sa_bq_job_user" {
  project = local.project_id
  role    = "roles/bigquery.jobUser"
  member  = local.workload_service_account
}

# Dataset-level: allow SA to read from source (BigLake Iceberg tables)
resource "google_bigquery_dataset_iam_member" "dataform_sa_source_viewer" {
  project    = local.project_id
  dataset_id = "source"
  role       = "roles/bigquery.dataViewer"
  member     = local.workload_service_account
}

# Dataset-level: allow SA to write to refined (CREATE TABLE)
resource "google_bigquery_dataset_iam_member" "dataform_sa_refined_editor" {
  project    = local.project_id
  dataset_id = "refined"
  role       = "roles/bigquery.dataEditor"
  member     = local.workload_service_account
}

# Dataset-level: allow SA to write to public (CREATE VIEW)
resource "google_bigquery_dataset_iam_member" "dataform_sa_public_editor" {
  project    = local.project_id
  dataset_id = "public"
  role       = "roles/bigquery.dataEditor"
  member     = local.workload_service_account
}
```

Also need GCS read access for the source bucket (if not already granted):
```hcl
resource "google_storage_bucket_iam_member" "dataform_sa_source_bucket_viewer" {
  bucket = local.gcs_source_bucket_name
  role   = "roles/storage.objectViewer"
  member = local.workload_service_account
}
```

**Debug step**: Run `gcloud dataform workflow-invocations query-actions <invocation_id>` (the deploy script already does this on FAILED, but if the failure is at the SA auth level, no actions will be returned).

**Priority**: CRITICAL -- blocks all Dataform execution.

---

### Issue 2: `missions_outcomes.sqlx` LEFT JOIN UNNEST -- Already Fixed

**Status**: The pending_work.md references `missions_outcomes.sqlx` but this file does **not exist** in the codebase. The outcomes UNNEST is done **inline** in `refined/missions.sqlx` at line 79:
```sql
LEFT JOIN UNNEST(JSON_QUERY_ARRAY(data, '$.outcomes')) AS outcomes ON TRUE
```
This is already using `LEFT JOIN ... ON TRUE` (correct). The same pattern is used in `refined/ballots.sqlx` line 31:
```sql
LEFT JOIN UNNEST(JSON_QUERY_ARRAY(data, '$.rules')) AS rules ON TRUE
```

**Verdict**: No fix needed. Both files already use the correct LEFT JOIN UNNEST pattern. The pending item was likely written before the fix was applied, or refers to a file that was never created (the outcomes were flattened inline instead of as a separate .sqlx).

---

### Issue 3: `missions_assertions.sqlx`: `code` -> `mission_code` -- Already Fixed

**Status**: Both assertion files (`missions_assertions_refined.sqlx` and `missions_assertions_public.sqlx`) reference `mission_code` correctly:
```sql
-- missions_assertions_refined.sqlx line 10:
WHERE mission_id IS NULL OR mission_code IS NULL
-- missions_assertions_public.sqlx line 10:
WHERE mission_id IS NULL OR mission_code IS NULL
```

**Verdict**: No fix needed. Already uses `mission_code` (not `code`).

---

### Issue 4: Test Files Column Names -- Already Fixed

**Status**: Both `missions_test.sqlx` and `ballots_test.sqlx` have been updated to match the current refined query output:
- `missions_test.sqlx`: 184 lines, 3 scenarios (+ 1 filtered), all column names match refined/missions.sqlx output including `outcomes_*` prefixed columns, `user_quotas` STRUCT array, `messages` STRUCT array
- `ballots_test.sqlx`: 72 lines, 4 scenarios (+ 1 filtered), column names match refined/ballots.sqlx output including `rules_*` prefixed columns with SAFE_CAST

**Verdict**: No fix needed. Test files appear up-to-date.

---

### Issue 5: `account_missions.sqlx` -- Broken `${dataform.}` Reference (NEW FINDING)

**File**: `account-missions-collector/dataform/definitions/public/account_missions.sqlx` line 33

**Bug**: The LEFT JOIN references an incomplete Dataform variable:
```sql
LEFT JOIN `${dataform.}` p
  ON a.outcome_code = p.package_code
```

The `${dataform.}` expression is clearly incomplete. Based on `workflow_settings.yaml` which defines:
```yaml
vars:
  commerce_refined_package: "the1-commerce-data-stg.refined.packages"
```

The correct reference should be:
```sql
LEFT JOIN `${dataform.projectConfig.vars.commerce_refined_package}` p
  ON a.outcome_code = p.package_code
```

**Impact**: This will cause a Dataform compilation error. The account-missions Dataform workflow would fail at compile time.

**Note**: This file also references `${ref({schema: "refined", name: "account_missions"})}` but there is no `refined/account_missions.sqlx` in the account-missions-collector Dataform repo. The refined table is likely created by the Dataflow pipeline (BQ sink), not by Dataform. The `dependencies: ["account_missions"]` in the config block handles this via a Dataform declaration (which may not exist yet either).

---

### Issue 6: `ingested_date_time` Missing from Final SELECT

**File**: `refined/missions.sqlx`

**Status**: The `ingested_date_time` column is NOT present in the CTE or final SELECT of `refined/missions.sqlx`. There is no `ingested_date_time` extraction anywhere in this file. The source Iceberg table likely has `ingested_date` (INT) and possibly `ingested_at` (TIMESTAMP), but neither is selected in the refined layer.

**Verdict**: This is intentional -- the refined layer only extracts business fields from the JSON `data` column. If downstream consumers need `ingested_date_time`, it would need to be added to both the CTE and the final SELECT. Low priority as noted in pending_work.md.

---

### Issue 7: Dataform Release Config Schedule (OBSERVATION)

**File**: `infrastructure/master-collector/dataform.tf`

Both release configs (`missions-daily` and `ballots-daily`) use a demo schedule:
```hcl
cron_schedule = "*/5 * * * *" # Every 5 minutes (demo -- change to daily for prod)
```

This compiles the Dataform release every 5 minutes. While the workflow config correctly runs daily at 01:00 BKK, the release config's 5-minute compilation is wasteful and should be changed to daily for production (e.g., `"0 0 * * *"` to compile at midnight before the 1AM workflow run).

---

## Summary Table

| # | Issue | Status | Severity | Action Needed |
|---|-------|--------|----------|---------------|
| 1 | Workflow FAILED (SA missing BQ IAM) | OPEN | CRITICAL | Add IAM grants in Terraform |
| 2 | LEFT JOIN UNNEST | ALREADY FIXED | - | None |
| 3 | `code` -> `mission_code` | ALREADY FIXED | - | None |
| 4 | Test column names | ALREADY FIXED | - | None |
| 5 | `${dataform.}` broken ref | NEW BUG | HIGH | Fix variable interpolation |
| 6 | `ingested_date_time` missing | BY DESIGN | LOW | Add if needed downstream |
| 7 | Release config 5min schedule | OBSERVATION | LOW | Change to daily for prod |

## Recommendation

**Immediate actions (must fix before Dataform can work)**:
1. Add BigQuery IAM grants for `t1-master-collector` SA in Terraform (Issue 1)
2. Fix `${dataform.}` -> `${dataform.projectConfig.vars.commerce_refined_package}` in account_missions.sqlx (Issue 5)

**Before prod deployment**:
3. Change release config `cron_schedule` from `*/5 * * * *` to daily (Issue 7)

**Deferred**:
4. Add `ingested_date_time` to refined/missions.sqlx if downstream needs it (Issue 6)

## Files Referenced

| File | Path |
|------|------|
| refined/missions.sqlx | `gamification/gamification-data/master-collector/dataform/definitions/refined/missions.sqlx` |
| refined/ballots.sqlx | `gamification/gamification-data/master-collector/dataform/definitions/refined/ballots.sqlx` |
| public/missions.sqlx | `gamification/gamification-data/master-collector/dataform/definitions/public/missions.sqlx` |
| public/ballots.sqlx | `gamification/gamification-data/master-collector/dataform/definitions/public/ballots.sqlx` |
| missions_assertions_refined.sqlx | `gamification/gamification-data/master-collector/dataform/definitions/tests/missions_assertions_refined.sqlx` |
| missions_assertions_public.sqlx | `gamification/gamification-data/master-collector/dataform/definitions/tests/missions_assertions_public.sqlx` |
| missions_test.sqlx | `gamification/gamification-data/master-collector/dataform/definitions/tests/missions_test.sqlx` |
| ballots_test.sqlx | `gamification/gamification-data/master-collector/dataform/definitions/tests/ballots_test.sqlx` |
| account_missions.sqlx | `gamification/gamification-data/account-missions-collector/dataform/definitions/public/account_missions.sqlx` |
| dataform.tf | `gamification/gamification-data/infrastructure/master-collector/dataform.tf` |
| biglake-metastore.tf | `gamification/gamification-data/infrastructure/master-collector/biglake-metastore.tf` |
| bigquery.tf (common) | `gamification/gamification-data/infrastructure/common/GCP/bigquery.tf` |

---

### architect-data says:

Verified by reading actual Terraform and Dataform files across gamification, sales, and message domains. Full code-level review follows.

---

#### 1. IAM Fix Validation -- Confirmed CRITICAL, with Additional Findings

**domain-others' analysis is correct.** The SA `t1-master-collector@...` has zero BigQuery permissions. Only `roles/biglake.editor` (on the BLMS catalog) and `roles/storage.objectAdmin` (on the Dataflow staging bucket) exist.

**Required roles (confirmed against GCP docs + working domains):**

| Role | Scope | Why |
|------|-------|-----|
| `roles/bigquery.jobUser` | Project-level | Execute BQ queries. Without this, Dataform fails instantly (no action output). |
| `roles/bigquery.dataEditor` | `refined` dataset | CREATE OR REPLACE TABLE (missions, ballots) |
| `roles/bigquery.dataEditor` | `public` dataset | CREATE OR REPLACE VIEW (missions, ballots) |
| `roles/bigquery.dataViewer` | Source BigLake-linked dataset | SELECT from Iceberg source tables |

**GCS source bucket read access**: The catalog uses `CREDENTIAL_MODE_VENDED_CREDENTIALS`, which means BigLake's own service account reads GCS on behalf of the query (visible in `gcs-bucket.tf` where `biglake_service_account` gets `objectAdmin`). The Dataform SA should NOT need direct `storage.objectViewer` on the source bucket -- BigLake vended credentials handle this. domain-others' suggested `google_storage_bucket_iam_member` for source bucket is likely unnecessary here, but harmless to add as defense-in-depth.

**MISSING from domain-others' analysis -- Dataform Service Agent impersonation:**

The sales domain's `dataform.tf` documents a critical manual step that gamification is also missing:
```
gcloud iam service-accounts add-iam-policy-binding \
  t1-master-collector@the1-gamification-data-<ENV>.iam.gserviceaccount.com \
  --member="serviceAccount:service-<PROJECT_NUMBER>@gcp-sa-dataform.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountTokenCreator"
```
When `invocation_config.service_account` is set on a workflow config, the Dataform service agent (`service-<PROJECT_NUMBER>@gcp-sa-dataform.iam.gserviceaccount.com`) must be able to impersonate that SA via `roles/iam.serviceAccountTokenCreator`. Without this, the workflow will also fail with a permission error. **This could be the real root cause**, happening before the BQ `jobUser` check even gets reached.

**Recommendation**: Add this impersonation grant to Terraform (not manual):
```hcl
data "google_project" "current" {
  project_id = local.project_id
}

resource "google_service_account_iam_member" "dataform_agent_token_creator" {
  service_account_id = "projects/${local.project_id}/serviceAccounts/t1-${var.service_name}@${local.project_id}.iam.gserviceaccount.com"
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:service-${data.google_project.current.number}@gcp-sa-dataform.iam.gserviceaccount.com"
}
```

**Pattern comparison across domains:**
- **Sales domain**: `bigquery-dataset-iam` module grants `dataOwner` on source, refined, public. `jobUser` + `serviceAccountTokenCreator` documented as manual.
- **Message domain**: `bigquery-dataset-iam` module grants `dataOwner` on source. No Dataform (no refined/public in Dataform there).
- **Gamification**: ZERO BigQuery IAM. No dataset access, no project-level `jobUser`, no Dataform agent impersonation.

**Preferred pattern**: Use the `bigquery-dataset-iam` terraform module (already used by sales/message) rather than raw `google_bigquery_dataset_iam_member` resources. This keeps Terraform consistent across domains and leverages the shared module's built-in patterns.

---

#### 2. Dataform SQL Quality Review

**2a. UNNEST patterns -- CORRECT**

Both `refined/missions.sqlx` (line 79) and `refined/ballots.sqlx` (line 31) use:
```sql
LEFT JOIN UNNEST(JSON_QUERY_ARRAY(data, '$.outcomes')) AS outcomes ON TRUE
```
This is the correct pattern. `LEFT JOIN ... ON TRUE` preserves the parent row when the array is empty (`[]`), producing NULL for the UNNEST columns. The test files verify this (Scenario 1 in missions, Scenario 3 in ballots -- empty arrays produce NULL outcome/rule fields).

**2b. JSON extraction functions -- CORRECT with one note**

- `JSON_VALUE()` for scalar extraction -- correct
- `JSON_QUERY()` for nested objects (qualifications, criteria) -- correct
- `JSON_QUERY_ARRAY()` for array unnesting -- correct
- `SAFE_CAST` used in ballots for `spendingRate`/`multiplier` (which may be non-numeric strings) -- correct defensive approach
- **Note**: missions uses `CAST` (not `SAFE_CAST`) for `missionVersion`, `controlGroup`, `missionQuota`, `remainingQuota`, `outcomeQuota`, `sequence`. If any of these source values are malformed strings, the query will fail. Consider switching to `SAFE_CAST` for robustness, same as ballots does for `spendingRate`. Low priority but worth noting.

**2c. nullifyEmpty UDF pattern -- SOUND but has a subtlety**

```js
function nullifyEmpty(col) {
  return `CASE WHEN ${col} IS NULL THEN NULL
          WHEN LOWER(TRIM(CAST(${col} AS STRING))) IN ('', 'undefined', 'null', '[]', '{}') THEN NULL
          ELSE ${col} END`;
}
```

- Correctly handles sentinel strings (`'undefined'`, `'null'`, `'[]'`, `'{}'`)
- The `CAST(${col} AS STRING)` works for most types but will produce unexpected results for DATETIME values (e.g., `DATETIME("2025-01-01 00:00:00")` cast to string will not match any sentinel). This is actually fine -- DATETIME columns will pass through the ELSE branch. No bug.
- The UDF is defined inline in each `.sqlx` file (missions and ballots independently). If the logic needs to change, it must be updated in both files. Consider moving to a shared `includes/` JS file if more tables are added.
- **`user_quotas` and `messages` arrays skip nullifyEmpty** (lines 113, 124 in missions.sqlx). Correct -- you cannot meaningfully apply this string-check to ARRAY<STRUCT> columns.

**2d. Incremental/snapshot patterns -- SNAPSHOT (full replace), NOT incremental**

Both refined tables use `type: "table"` (full CREATE OR REPLACE) with a snapshot pattern:
```sql
WHERE ingested_date = (SELECT MAX(ingested_date) FROM source)
```
This always takes the latest full snapshot from the source Iceberg table. This is the **correct pattern for catalog/reference data** (missions catalog, ballot catalog) that is fully replaced on each API fetch. Each ingestion writes all records with the same `ingested_date`.

**However, this is NOT an incremental pattern.** If the gamification domain later adds high-volume transactional tables (e.g., account missions activity events), this full-replace approach will not scale. The team should be aware that incremental patterns (`type: "incremental"` with `WHERE ingested_date > ${when(...)}`) would be needed for event tables.

---

#### 3. Data Model Assessment

**3a. Source -> Refined -> Public layering -- CORRECT**

```
Source (Iceberg via BigLake) -> Refined (materialized TABLE, JSON extracted) -> Public (VIEW over refined)
```
- Source: BigLake-linked Iceberg tables from the BLMS catalog, declared as Dataform declarations
- Refined: Materialized tables with full JSON extraction, type casting, null cleansing
- Public: Pass-through views for consumer access control

This follows the standard medallion architecture. The public layer is currently a 1:1 pass-through (no filtering, no aggregation), which is fine for now but could add row-level security or column masking later.

**3b. Source declaration database path -- POTENTIAL ISSUE**

The source declarations use:
```js
database: dataform.projectConfig.defaultDatabase + "." + dataform.projectConfig.vars.source_catalog
```
This resolves to `the1-gamification-data-stg.the1-gamification-data-source-stg`, producing a fully qualified reference like:
```
`the1-gamification-data-stg.the1-gamification-data-source-stg`.source.missions
```
This is a 4-part reference (project.catalog-linked-dataset.namespace.table) for BigLake Iceberg tables. **Verify this is the correct syntax for BigLake BLMS-linked tables queried from BQ.** Standard BQ uses 3-part (`project.dataset.table`). If the BigLake catalog creates a dataset named `the1-gamification-data-source-stg` with schema `source`, then this would actually be:
```
project = the1-gamification-data-stg
dataset = the1-gamification-data-source-stg
table   = source.missions  (dot-separated namespace)
```
This only works if `source` is the Iceberg namespace and `missions` is the table within that namespace, and BQ represents this as `namespace.table` within the linked dataset. **This needs runtime validation** -- it may work correctly with BigLake, but if the declaration resolves incorrectly, all queries will fail silently at the `ref()` call.

**3c. Partition/clustering choices -- NOT CONFIGURED**

The refined tables use `type: "table"` with no explicit partition or clustering configuration. Dataform supports:
```
config {
  type: "table",
  bigquery: {
    partitionBy: "DATE(created_date)",
    clusterBy: ["company_code", "status"]
  }
}
```
For catalog/reference data with <100K rows, this is not a problem. But as data grows, adding partition by `created_date` or `mission_start_date` and clustering by `company_code` + `status` would improve query performance. **Low priority for now.**

**3d. CDC / Deduplication concerns**

The snapshot pattern (`WHERE ingested_date = MAX(ingested_date)`) inherently handles deduplication: it always takes the latest full snapshot. There is no CDC concern here because the entire table is replaced.

**However**: The `LEFT JOIN UNNEST(outcomes)` in missions produces row multiplication (1 mission with 3 outcomes = 3 rows). This means `mission_id` is NOT unique in the refined table. The assertions check `WHERE mission_id IS NULL OR mission_code IS NULL` but do NOT check uniqueness. For missions with multiple outcomes, this is by design. But consumers must be aware that the grain of `refined.missions` is `(mission_id, outcomes_sequence)`, not `mission_id` alone. The public view inherits this same grain. **Consider adding a documentation comment or assertion that validates the expected grain.**

**3e. account-missions-collector gaps**

The `account-missions-collector/dataform/` directory has only ONE file: `definitions/public/account_missions.sqlx`. There is:
- No `definitions/source/` declaration for `account_missions`
- No `definitions/refined/` sqlx file
- No test files
- No assertion files

The `dependencies: ["account_missions"]` in the config block references a dependency that does not exist as a Dataform asset. The `${ref({schema: "refined", name: "account_missions"})}` will fail at compile time because no declaration for `refined.account_missions` exists. This table is presumably created by the Dataflow pipeline (BQ sink), but Dataform still needs a declaration to reference it.

**Fix needed**: Add `definitions/source/account_missions.sqlx` (or `definitions/refined/account_missions.sqlx`) as a `type: "declaration"` pointing to the pipeline-created table.

---

#### 4. Issue 5 Deep Dive: `${dataform.}` Broken Reference

Confirmed. Line 33 of `account-missions-collector/dataform/definitions/public/account_missions.sqlx`:
```sql
LEFT JOIN `${dataform.}` p
```

The `workflow_settings.yaml` defines:
```yaml
vars:
  commerce_refined_package: "the1-commerce-data-stg.refined.packages"
```

The fix should be:
```sql
LEFT JOIN `${dataform.projectConfig.vars.commerce_refined_package}` p
```

**Additional concern**: This is a cross-project reference (`the1-commerce-data-stg`). The gamification SA needs `roles/bigquery.dataViewer` on the `refined` dataset in the `the1-commerce-data-stg` project. This IAM grant must be added in the **commerce** domain's Terraform (or via a manual grant by the commerce team). Without it, even after fixing the variable, the JOIN will fail with permission denied.

**Also note**: The `commerce_refined_package` var is hardcoded to `stg`. For prod deployment, the workflow settings must be overridden (via `code_compilation_config.vars` in the account-missions Dataform terraform, similar to how `source_catalog` is overridden in master-collector's `dataform.tf`). Currently, **no `dataform.tf` exists in `infrastructure/account-missions-collector/`** -- the account-missions Dataform setup appears incomplete.

---

#### 5. Prioritized Action Items

**P0 -- CRITICAL (blocks all Dataform execution):**

| # | Action | Owner | Where |
|---|--------|-------|-------|
| 1 | Grant `roles/iam.serviceAccountTokenCreator` to Dataform service agent on master-collector SA | ops-devops | `infrastructure/master-collector/dataform.tf` or new `iam.tf` |
| 2 | Grant `roles/bigquery.jobUser` (project-level) to master-collector SA | ops-devops | `infrastructure/master-collector/` new `bigquery-iam.tf` |
| 3 | Grant `roles/bigquery.dataViewer` on source BigLake dataset to master-collector SA | ops-devops | `infrastructure/master-collector/` via `bigquery-dataset-iam` module |
| 4 | Grant `roles/bigquery.dataEditor` on refined + public datasets to master-collector SA | ops-devops | `infrastructure/master-collector/` via `bigquery-dataset-iam` module |

**P1 -- HIGH (blocks account-missions Dataform):**

| # | Action | Owner | Where |
|---|--------|-------|-------|
| 5 | Fix `${dataform.}` to `${dataform.projectConfig.vars.commerce_refined_package}` | domain-others | `account-missions-collector/dataform/definitions/public/account_missions.sqlx` line 33 |
| 6 | Add `type: "declaration"` for `refined.account_missions` | domain-others | New file: `account-missions-collector/dataform/definitions/refined/account_missions.sqlx` |
| 7 | Create `dataform.tf` for account-missions-collector (repo, release config, workflow config with env-aware vars) | domain-others + ops-devops | `infrastructure/account-missions-collector/dataform.tf` |
| 8 | Grant cross-project `roles/bigquery.dataViewer` on commerce refined dataset to gamification SA | ops-devops + commerce team | Commerce domain Terraform |

**P2 -- Before Prod:**

| # | Action | Owner | Where |
|---|--------|-------|-------|
| 9 | Change release config `cron_schedule` from `*/5 * * * *` to `0 0 * * *` (daily at midnight, before 1AM workflow) | domain-others | `infrastructure/master-collector/dataform.tf` lines 34, 79 |
| 10 | Override `commerce_refined_package` var for prod (currently hardcoded to stg) | domain-others | Account-missions Dataform terraform `code_compilation_config.vars` |
| 11 | Consider `SAFE_CAST` instead of `CAST` for INT64 fields in missions.sqlx | domain-others | `refined/missions.sqlx` |

**P3 -- Low / Deferred:**

| # | Action | Owner | Where |
|---|--------|-------|-------|
| 12 | Add `ingested_date_time` to refined if downstream needs it | domain-others | `refined/missions.sqlx` |
| 13 | Extract `nullifyEmpty` JS function to shared `includes/` directory | domain-others | New `includes/nullifyEmpty.js` |
| 14 | Add grain documentation (mission_id + outcomes_sequence) or uniqueness assertion | domain-others | Tests or config comments |
| 15 | Add partition/clustering config to refined tables when data volume grows | domain-others | `refined/missions.sqlx`, `refined/ballots.sqlx` |

---

## Decision (Human Approval)
- [ ] Approved
- [ ] Rejected
