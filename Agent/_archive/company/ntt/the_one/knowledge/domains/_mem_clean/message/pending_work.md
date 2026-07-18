# Message Domain -- Pending Work

> Extracted from codebase scan (2026-04-05)

## MEDIUM Priority

### 1. Legacy Iceberg catalog and bucket cleanup
- **Files**: `infrastructure/messages-collector/biglake-metastore.tf`, `infrastructure/messages-collector/gcs-bucket.tf`
- **Issue**: Legacy resources with old naming convention `the1-<domain>-<env>-<layer>` (should be `the1-<domain>-<layer>-<env>`) still exist
- **Details**: Both `legacy_source_bucket` and `legacy_catalog` are marked `TODO(legacy)` with note "Remove after confirming no downstream dependencies". Catalog has `prevent_destroy = true`. Bucket is non-empty.
- **Action**: Confirm no downstream dependencies, then plan manual cleanup before Terraform destroy

### 2. communications-collector and templates-collector activation
- **Location**: `communications-collector/`, `templates-collector/`
- **Current state**: Both directories are empty (only `.ruff_cache`). CI includes are commented out in root `.gitlab-ci.yml`
- **Context**: Originally planned as separate streaming collectors, but data collection was consolidated into `master-collector` (batch via Cloud Run). These may be removed or repurposed
- **Decision needed**: Remove empty directories or implement if separate streaming collection is needed

### 3. Hard-coded admin emails in terraform
- **File**: `infrastructure/master-collector/biglake-metastore.tf`
- **Issue**: Two admin users hard-coded as `biglake.admin` IAM members:
  - `user:eukasiphat@the1.co.th`
  - `user:sujitlada@the1.co.th`
- **Also in**: `infrastructure/messages-collector/biglake-metastore.tf` (`sujitlada@the1.co.th`)
- **Recommendation**: Parameterize via terraform variables or use a group/role-based approach

### 4. Refined/public GCS buckets commented out
- **File**: `infrastructure/messages-collector/gcs-bucket.tf`
- **Issue**: `message_collector_refined_bucket` and `message_collector_public_bucket` modules are commented out with note "Do not being used currently, kept for future use"
- **Action**: Uncomment and deploy when refined/public GCS buckets are needed, or remove if not planned

## LOW Priority

### 5. Dataform release config schedule (demo vs prod)
- **File**: `infrastructure/master-collector/dataform.tf`
- **Issue**: Release config `cron_schedule` is set to `*/5 * * * *` (every 5 minutes) with comment "demo -- change to daily for prod"
- **Note**: Workflow config is correctly set to daily `0 1 * * *`, so this may not cause issues in practice since workflow is the actual execution trigger

### 6. Dataform workflow SA inconsistency
- **File**: `infrastructure/master-collector/dataform.tf`
- **Issue**: Workflow service_account uses `local.service_account_iac` (IAC SA) rather than a dedicated workload SA like gamification domain uses (`t1-master-collector@...`)
- **Risk**: IAC SA may have broader permissions than needed for Dataform execution
