# Loyalty Domain -- Pending Work
**Extracted: 2026-04-05 | Sources: SESSION_SUMMARY.md, MEMORY.md**

---

## High Priority

### Members-collector STG verification
- **Status**: Waiting for Kafka messages in STG
- **What**: Verify full streaming pipeline works end-to-end in STG environment
- **Blocked by**: No Kafka messages flowing yet

### Coupons-collector issues
- **event_name conflict**: Kafka vs API race condition (unresolved)
- **CVE**: pyasn1, libc6 vulnerabilities need fixing
- **ingested_at**: str -> int alignment needed (source Iceberg 3-column schema)

### M-T-H rerun safety
- **What**: Need DELETE WHERE + INSERT pattern for safe reruns
- **Risk**: Without this, rerunning produces duplicate data

---

## Medium Priority

### Kafka schema: eligibleTierCode migration
- **Status**: Code written with comments, waiting for confirm to uncomment
- **What**: New fields in Kafka payload (eligibleTierCode, previousTierCode, programCode, retentionStartDate)
- **Impact**: CDC DELETE lookup key change + tier_events refined schema adds 4 fields
- **Detail**: See `loyalty/kafka_schema.md`

### 3 collectors partition/datetime changes
- **Status**: Plan exists, not yet implemented
- **What**: Align partition fields across all 3 collectors

### Tiers-collector sonar scan
- **Status**: Not started (members 24 issues done, m-t-h 7 issues done)

### Backward-compatible-collector STG testing
- **Status**: Scaffolded, needs STG deployment and test

### Init data migration
- **Status**: Blocked on AWS permission
- **What**: DTS S3 -> BQ, then BQ -> BQ + BQ -> Iceberg pipeline
- **Blocked by**: AWS permission for S3 access

---

## Low Priority / Future

### Secret key migration (tiers, m-t-h)
- **What**: DevOps may change secret key from `api_connection` -> `apiCredentials` (like members-collector)
- **Impact**: Must update `configuration_adapter.py` if changed
- **Status**: Depends on DevOps decision

### STG -> PROD dependency chain
- **What**: Add `needs: deploy:stg` to deploy:prod in CI
- **Why**: Currently no gate between STG and PROD deploy

### Members drain-first
- **What**: Upgrade streaming cancel to drain-then-cancel (like [REF: purchases-collector (read-only)])
- **Why**: Cancel may lose in-flight data

### BQ backup before deploy-tables:prod
- **What**: Add backup step to prevent data loss on schema changes
- **Status**: Not implemented

### DLQ implementation
- **What**: Dead Letter Queue for failed records (Phase 1: API DoFns)
- **Doc**: `loyalty/docs/dlq/DLQ_CHECKLIST.md`

### Re-enable Option B BQ table creation
- **What**: Enable `externalCatalogTableOptions` + `tables.patch` refresh
- **Blocked by**: [EXTERNAL: transaction/ team] terraform dataset readiness
- **Steps**: See knowledge_base.md section 4

### Dataplex setup
- **What**: Enable API, create Lake/Zone

### [EXTERNAL: transaction/] biglake-metastore.tf cleanup
- **What**: Remove cross-collector grants after per-collector IAM is deployed

### DoFns alignment with messaging
- **What**: Consider switching from Attach pattern (members/purchases) to Filter pattern (messaging)
- **Detail**: See `memory/dofns_comparison.md`
- **Status**: Low priority, only if alignment needed

### Source Iceberg `timestamp` column type
- **What**: Currently STRING (epoch string), may change to INT in future
- **Scope**: members-collector + tiers-collector (m-t-h does not have this column)

### Remove debug logger.info in dofns.py
- **What**: Lines 107+140 log every message (very noisy), should be debug level

### Verify Schema B/C fix in PROD
- **What**: PROD log showed old behavior, unclear if fix deployed yet

---

## Closed Items (for reference)

### CDC DELETE tierCode -- CLOSED (2026-03-02)
- Decision: Keep tierCode matching as-is. Source sends wrong = source's problem.

### pre-commit modifies [EXTERNAL: transaction/] files
- **Known issue**: `ruff format` fixes trailing whitespace in transactions-collector
- **Mitigation**: Always run `git checkout -- transactions-collector/` after pre-commit
