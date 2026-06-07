# Serving Instructions

> AI: Read this file when creating BigQuery views, Dataform transformations, or BI-facing datasets.

## Quick Reference

```
Serving Layers:
  Refined (BQ) → Public views (Dataform/SQL) → Consumers (BI, APIs, Data Science)

Current State:
  - Refined tables: ACTIVE (all collectors)
  - Public layer: PLANNED (Dataform not yet configured)
  - BI integration: via direct BQ access
```

---

## 1. Storage Layer Progression

| Layer | Storage | Who Writes | Who Reads | SLA |
|-------|---------|------------|-----------|-----|
| **Source** | Iceberg on GCS | Pipeline (managed.Write) | Internal analytics, time-travel | Best-effort |
| **Refined** | BigQuery | Pipeline (Storage Write API) | Analysts, downstream pipes | Minutes (streaming), hours (batch) |
| **Public** | BigQuery views | Dataform / SQL DDL | BI dashboards, APIs, partners | Defined per view |

---

## 2. BigQuery Refined Layer (Current)

### Table Summary

| Table | Collector | Partition | Clustering | Write Mode |
|-------|-----------|-----------|------------|------------|
| `refined.member_tier` | members | `ingestedTHDate` (DATE, DAY) | member_id, code | CDC (prod) / append (stg) |
| `refined.member_tier_maintenance` | members | `created_date` (DATETIME, DAY) | member_id, event_type, tier_code | CDC (tierMaintenanceId) |
| `refined.tier_events_upgraded` | members | `etlLoadTime` (TIMESTAMP, DAY) | member_id, tier_code | append |
| `refined.tier_events_downgraded` | members | `etlLoadTime` (TIMESTAMP, DAY) | member_id, tier_code | append |
| `refined.tiers_master` | tiers | none | program_code, tier_code | append |
| `refined.members_tiers_history` | m-t-h | `etlLoadTime` (TIMESTAMP, DAY) | none | append |

### Data Freshness

| Table Type | Expected Freshness | How to Check |
|------------|-------------------|--------------|
| Streaming (member_tier, tier_events) | < 2 minutes | `SELECT MAX(ingestedTHDate) FROM refined.member_tier` |
| Batch (tiers_master, m-t-h) | Daily (1 AM BKK) | `SELECT MAX(etlLoadTime) FROM refined.tiers_master` |

---

## 3. Public Layer (Planned)

### Dataform SQL Views

When Dataform is configured, public layer views will expose refined data with:
- Business-friendly column names
- Filtered/aggregated views for specific consumers
- Materialized views for heavy queries

```sql
-- Example: public.active_member_tiers (Dataform view)
CREATE OR REPLACE VIEW `project.public.active_member_tiers` AS
SELECT
    member_id,
    code AS tier_code,
    program_code,
    start_date,
    expiry_date,
    CASE code
        WHEN 'T1L1' THEN 'Silver'
        WHEN 'T1L2' THEN 'Gold'
        WHEN 'T1L3' THEN 'Platinum'
        WHEN 'T1L4' THEN 'Diamond'
        ELSE code
    END AS tier_name
FROM `project.refined.member_tier`
WHERE expiry_date > CURRENT_DATE();
```

### Materialized Views (for Performance)

```sql
-- Example: pre-aggregated tier counts
CREATE MATERIALIZED VIEW `project.public.tier_count_by_program`
PARTITION BY DATE(snapshot_date)
AS
SELECT
    program_code,
    code AS tier_code,
    COUNT(DISTINCT member_id) AS member_count,
    CURRENT_DATE() AS snapshot_date
FROM `project.refined.member_tier`
GROUP BY program_code, code;
```

---

## 4. Cross-Domain Access (Future)

| Mechanism | Use Case | Status |
|-----------|----------|--------|
| Authorized Views | Expose filtered data to other projects | Planned |
| Authorized Datasets | Grant read access across projects | Planned |
| Analytics Hub | Publish datasets for discovery | Future |

---

## 5. DO / DON'T

| DO | DON'T |
|----|-------|
| Use views in `public` dataset for consumers | Let consumers query `refined` directly (breaks on schema change) |
| Partition and cluster views appropriately | Create unpartitioned public tables |
| Document SLA/freshness per view | Assume all data is real-time |
| Use Dataform for SQL transformations | Write ad-hoc SQL scripts |
