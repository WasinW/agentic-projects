# Partner Domain -- Pending Work

## 1. Cloud Scheduler SA Migration

**Status:** TODO comments in terraform code
**Location:** `infrastructure/master-collector/cloud-run.tf`, `secret-manager.tf`
**Details:** Multiple `# TODO: Revert to t1-${var.service_name} after creating the new service account` comments throughout:
- CloudRun `service_account_email`
- Cloud Scheduler OIDC token `service_account_email` (all 4 schedulers)
- CloudRun `invoker_members`
- Secret Manager `secret_accessors_list`

Currently using existing SA naming convention. Planned to migrate to a new dedicated SA but the SA hasn't been created yet.

## 2. Dataform Release Config: Change Demo Schedule to Daily

**Status:** Hardcoded demo schedule in terraform
**Location:** `infrastructure/master-collector/dataform.tf` line 37
**Details:** `cron_schedule = "*/5 * * * *"` with comment `# Every 5 minutes (demo -- change to daily for prod)`
The workflow config already has a daily schedule (`0 3 * * *`), but the release config compiles every 5 minutes. Should be changed to daily (e.g., once before the workflow runs).

## 3. Remove Deprecated Empty Collectors

**Status:** Empty directories remain in repo
**Locations:**
- `branches-collector/` (contains only empty `tests/` dir)
- `companies-collector/` (contains only empty `tests/` dir)
- `infrastructure/master-companies/` (contains only `variable.tf`)

These were the original single-entity collectors before `master-collector` consolidated all 4 entities. They should be cleaned up to avoid confusion.

## 4. Parameterize Hardcoded Values in Terraform

**Status:** Minor cleanup items
**Details:**
- `main.tf` backend prefix is `the1-partner-data/services/partner-data/data-pipeline-master-branchs` (typo: "branchs" should be "branches", and name reflects old single-entity collector)
- CloudRun VPC network/subnet use hardcoded naming pattern with `terraform.workspace` -- works but could be variables
- `bigquery.tf` labels reference "master-branches-pipeline" even though this now handles all 4 entities

## 5. Confluent Kafka Dependencies

**Status:** Unused dependencies in pyproject.toml
**Details:** `confluent-kafka` with avro/schemaregistry extras are listed in `master-collector/pyproject.toml` dependencies but master-collector only uses REST API sources. These appear to be copy-paste artifacts and could be removed to reduce image size.
