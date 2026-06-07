# Loyalty -- Kafka Schema Changes (eligibleTierCode)
**Date: 2026-03-03**

---

## New Kafka Payload (upgraded/downgraded events)

```json
{
  "eventId": "...",
  "source": "loyalty.members",
  "eventName": "loyalty.members.upgraded",
  "timestamp": 1691060098,
  "payload": {
    "accountId": "...",
    "memberId": "...",
    "tierEventId": "...",
    "tierCode": "T1X",           // existing - keep for backward compat
    "eligibleTierCode": "T1X",   // NEW: current user tier (can be empty string)
    "previousTierCode": "T1L3",  // NEW: previous tier before upgrade/downgrade
    "programCode": "programCode", // NEW: program code
    "isExistingTier": true,
    "triggerType": "SPENDING",
    "processedAt": "2024-03-15T00:00:00.000Z",
    "retentionStartDate": "2022-12-31T17:00:00Z"  // NEW
  }
}
```

## Changes Needed (STATUS: PENDING - code with comments, waiting for confirm to uncomment)

### CDC DELETE: Use `eligibleTierCode` instead of `tierCode` for API lookup
- `api_dofns.py` -> `ExtractMemberIdAndTierCodeDoFn`: `payload.get("tierCode")` -> `payload.get("eligibleTierCode")`
- Fallback to `tierCode` if `eligibleTierCode` is empty/None (backward compat)
- `FetchMemberTierDoFn` logic unchanged - just receives different input value

### Tier Events Refined: Add 4 new fields (both upgraded + downgraded)
- `eligibleTierCode` (STRING)
- `previousTierCode` (STRING)
- `programCode` (STRING)
- `retentionStartDate` (TIMESTAMP)

Files to change:
- `schemas.py`: TIER_EVENT_UPGRADED_REFINED_SCHEMA + TIER_EVENT_DOWNGRADED_REFINED_SCHEMA
- `transform_dofns.py`: ExtractTierEventUpgradedPayloadDoFn + DowngradedPayloadDoFn
- `refined_tier_events_upgraded.json` + `refined_tier_events_downgraded.json`
- Tests for above

### NOT changed (important!)
- member_tier schema: NO changes
- member_tier_maintenance schema: NO changes
- Iceberg source layer: NO changes (payload stored as JSON string)
- Only the lookup key changes (tierCode -> eligibleTierCode) and tier_events refined tables get new fields

## Initial Data Migration Plan (2026-03-03)

### Flow:
1. **DTS: S3 -> refined_init BQ** (already set up in `dts.tf`, blocked on AWS permission)
   - `member_tier_init_refined`, `member_tier_maintenance_init_refined`, `members_tiers_history_init_refined`
2. **refined_init BQ -> refined BQ** (straightforward copy/transform)
3. **refined_init BQ -> raw Iceberg** (complex: group schemas to payload, may have new fields from above)

### Note on new fields impact:
- If tier_events schemas get new fields, the init data from S3 (Redshift) may or may not have them
- Need to handle NULLs for new fields in init data
