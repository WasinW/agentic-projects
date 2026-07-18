# Gamification Domain -- Pending Work

> Extracted from SESSION_SUMMARY.md (2026-04-02)

## HIGH Priority

### 1. missions_outcomes.sqlx LEFT JOIN UNNEST fix
- **Issue**: Uses implicit INNER JOIN via `, UNNEST(...)` which silently drops rows with empty arrays
- **Fix**: Change to `LEFT JOIN UNNEST(...) ON TRUE`
- **Note**: Same bug was already fixed in `missions.sqlx` and `ballots.sqlx` by user

### 2. missions_assertions.sqlx: `code` -> `mission_code`
- **Issue**: References column `code` which does not exist in the query output -- causes runtime error
- **Fix**: Change column reference from `code` to `mission_code`

### 3. Dataform workflow FAILED investigation
- **Issue**: Workflow invocation fails instantly (~200ms) with `state: FAILED` and no action-level detail
- **Likely cause**: SA permission issue (missing `bigquery.jobUser`, `bigquery.dataEditor`, or BigLake access)
- **Debug**: Run `gcloud dataform workflow-invocations query-actions <invocation_id>` to get details
- **Needed roles**: bigquery.jobUser, bigquery.dataEditor, BigLake catalog access for SA

## MEDIUM Priority

### 4. Test files column name updates
- **Files**: `missions_test.sqlx`, `ballots_test.sqlx`
- **Issue**: Column names in test assertions don't match updated query output (after UNNEST/SAFE_CAST fixes)
- **Fix**: Update expected column names in test .sqlx files to match refined query output

### 5. account-missions-collector Iceberg write error
- **Error**: `Expected all data writers to be closed, but found 1 data writer(s) still open`
- **Cause**: Known Apache Beam IcebergIO bug -- race condition in `RecordWriterManager.close()`
- **Possible mitigations**:
  - Increase `triggering_frequency_seconds` (currently STG=60s, PROD=300s)
  - Reduce max_workers
  - Upgrade Beam version (currently 2.72.0rc2)
- **Status**: Intermittent, does not always occur

## LOW Priority

### 6. ingested_date_time missing from SELECT
- **File**: `missions.sqlx` (refined)
- **Issue**: Column `ingested_date_time` is created in CTE but not included in final SELECT statement
- **Fix**: Add to final SELECT if downstream consumers need it
