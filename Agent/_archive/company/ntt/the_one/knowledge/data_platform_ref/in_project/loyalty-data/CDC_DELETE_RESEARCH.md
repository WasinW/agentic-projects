# BigQuery CDC DELETE: Research Summary

> **Project**: loyalty-data (members-collector)
> **Full Document**: `loyalty/docs/bigquery/CDC_DELETE_RESEARCH.md`
> **Created**: 2026-02-24

---

## Problem

`refined.member_tier` uses CDC mode (`use_cdc_writes=True`) with PK `(memberId, programCode)`.
CDC UPSERT handles additions/updates, but when the API no longer returns a programCode for a member,
that stale row stays in BQ forever — no mechanism to remove it.

**CDC-enabled tables CANNOT use DML** (DELETE, UPDATE, MERGE) — the only way to delete is via
CDC DELETE through the Storage Write API.

---

## CDC DELETE Protocol

```python
# DELETE envelope — same structure as UPSERT, just change mutation_type
{
    "row_mutation_info": {
        "mutation_type": "DELETE",                # ← "DELETE" instead of "UPSERT"
        "change_sequence_number": "1708992000000000",
    },
    "record": {
        "memberId": "M001",        # PK — REQUIRED
        "programCode": "c1",       # PK — REQUIRED
        # Non-PK fields can be None (NULLABLE) or placeholder (REQUIRED)
    }
}
```

**Key rules**:
- PK columns must be populated
- `change_sequence_number` must be higher than last UPSERT for that PK
- Non-PK NULLABLE fields can be None
- Non-PK REQUIRED fields need placeholder values
- Beam maps `mutation_type` → `_CHANGE_TYPE` pseudocolumn automatically

---

## Implementation (DONE 2026-02-24)

### Chosen Approach: Variant of Approach A — TierCode Match + BQ Query for DELETE

Instead of full diff (query ALL BQ tiers for a member), we carry `tierCode` from Kafka
and match it against the API response. BQ query only needed for DELETE case (to look up `programCode`).

```
Kafka downgrade event has: tierCode (e.g., "T1X")
→ Call API: get_member_tier(member_id)
→ If tierCode found in API response → UPSERT only that item
→ If tierCode NOT found in API     → tier removed → query BQ for programCode → CDC DELETE
```

BQ query only happens when tier is removed (rare). No BQ query for UPSERT path.

### Pipeline Flow

```
merged_raw_events → ExtractMemberIdAndTierCodeDoFn (yields tuple[str, str|None])
  → pairs (shared)
  ├── member_tier:     DeduplicatePairsDoFn → FetchMemberTierDoFn (CDC DELETE support)
  └── tier_maintenance: Map(x[0]) → DeduplicateMemberIdsDoFn → FetchTierMaintenanceDoFn
```

### Files Changed

| File | Change |
|------|--------|
| `api_dofns.py` | +`ExtractMemberIdAndTierCodeDoFn`, +`DeduplicatePairsDoFn`, modified `FetchMemberTierDoFn` |
| `bigquery_storage.py` | `_WrapCdcRowDoFn`: pop `_is_delete` → set `mutation_type` |
| `transform_dofns.py` | `ExtractMemberTierPayloadDoFn`: DELETE path (minimal PK-only row) |
| `builder.py` | Split pipeline: pairs branch + member_id branch, CDC params |
| `base.yaml` | Comment update (PK reference) |
| `test_api_dofns.py` | 10 new tests |
| `test_transform_dofns.py` | 2 new tests |
| `test_bigquery_storage.py` | 5 new tests (NEW file) |

### DELETE Safety: 3-Layer Check

DELETE is only emitted when ALL conditions are met:

| # | Check | Purpose |
|---|-------|---------|
| 1 | `tier_code ≠ None` | Kafka event has tierCode |
| 2 | API does NOT contain `tier_code` | Tier was removed from member |
| 3 | BQ has row with `memberId` + `code = tier_code` | Confirms tier existed in BQ |

If any check fails → no DELETE emitted.

### Edge Case (MUST VERIFY)

`tierCode` in Kafka — is it the **current** tier (after downgrade) or **old** tier (before downgrade)?
- If current tier + downgrade 2→1: API has it → UPSERT ✓
- If old tier + downgrade 2→1: API doesn't have old tier → false DELETE ⚠️
- Both interpretations are safe for 1→0 (tier completely removed)

**Must verify with actual Kafka data.**

### Tests

215 tests passing (members-collector), ruff/mypy/pre-commit green.

---

## Viable Approaches (Research)

| # | Approach | Latency | Complexity | Physical Delete |
|---|---------|---------|------------|-----------------|
| A | **CDC DELETE via Diff** (query BQ, compare with API, emit DELETE) | Real-time | Medium-High | Yes |
| B | **Batch Snapshot Diff** (periodic full comparison) | Hours | High | Yes |
| C | **Soft Delete** (UPSERT with `isActive=FALSE`) | Real-time | Medium | No |
| D | **Separate Non-CDC Table** + DML | Hours | High | Yes |
| E | **Kafka Tombstone** (upstream emits delete event) | Real-time | Low* | Yes |
| F | **Pipeline Pause + DML** (stop stream, run DML) | 90min+ downtime | Low (one-time) | Yes |

*\*Low only if upstream backend supports it*

---

## Limitations

- `max_staleness = 30min`: DELETE applied during next merge cycle
- BQ read in streaming DoFn adds ~100-500ms latency per query (DELETE path only)
- Delete retention: 2 days before physical removal
- No DML on CDC tables — ever (unless you stop streaming + wait 90min)
- CDC does not enforce PK uniqueness

---

## References

| Doc | Location |
|-----|----------|
| Full research + implementation | `loyalty/docs/bigquery/CDC_DELETE_RESEARCH.md` |
| CDC vs Append deep-dive | `loyalty/docs/bigquery/BIGQUERY_STORAGE_WRITE_API_APPEND_VS_CDC.md` |
| GCP CDC docs | https://cloud.google.com/bigquery/docs/change-data-capture |
| insight DELETE impl | `insight/.../customer_profile/domain/transformers.py` line 351 |
