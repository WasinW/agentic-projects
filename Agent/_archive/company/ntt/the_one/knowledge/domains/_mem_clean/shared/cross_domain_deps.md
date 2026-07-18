# Cross-Domain Dependencies & Ownership

## 1. Common Library Version Matrix

| Domain | Collector | common-dataflow | common-cloudrun |
|--------|-----------|----------------|-----------------|
| loyalty | members, tiers, m-t-h, coupons, purchases | 0.0.23 | -- |
| loyalty | rewards | -- | (unknown) |
| sales | sales-collector | 0.0.32 | -- |
| gamification | account-missions | 0.0.24 | -- |
| gamification | master | -- | 0.0.35 |
| message | messages | 0.0.24 | -- |
| message | master | -- | 0.0.35 |
| partner | master | -- | 0.0.35 |
| catalog | products | 0.0.23 | -- |

**Key**: common-dataflow = Beam/Dataflow utilities (IcebergSink, BigQueryWriterAdapter, DoFn base classes). common-cloudrun = FastAPI/CloudRun utilities (PyIceberg writer, health checks, scheduler integration).

## 2. Cross-Domain Data Dependencies

```
partner master ──→ sales (Dataform JOINs: companies_branch_brand)
partner master ──→ catalog (Dataform JOINs: ms_product_all)
gamification account-missions ──→ insight (Bigtable martech_map lookup)
message messages ──→ insight (Bigtable martech_map + PubSub)
loyalty refined tables ──→ loyalty-mart (BQ views/transformations)
```

**Impact**: Changes to source schemas in upstream domains can break downstream Dataform SQL or Bigtable lookups. Always trace dependencies before schema changes.

## 3. Ownership Map

### OUR team (full ownership)
- **loyalty**: members-collector, tiers-collector, members-tiers-history-collector, coupons-collector
- **loyalty backward-compat**: maintaining existing patterns
- **sales**: sales-collector
- **insight**: customer-profile-pipeline, customer-activity-pipeline
- **catalog**: products-collector
- **gamification**: account-missions-collector, gamification-master
- **message**: messages-collector, message-master
- **partner**: partner-master
- **common**: common-dataflow, common-cloudrun libraries
- **loyalty-mart**: BQ mart layer on top of loyalty refined tables

### EXTERNAL (other team -- coordinate before changes)
- **loyalty/transactions-collector**: owned by another team
  - pre-commit in monorepo will touch their files -- always revert
  - `transaction/` directory changes require their approval

### READ-ONLY (reference implementation)
- **loyalty/purchases-collector**: use as reference for patterns, do not modify

### DEPRECATED
- **loyalty/backup/member-tiers**: old implementation, do not use

## 4. Alignment Gaps (areas where domains diverge)

### BLMS REST Catalog adoption
- **Adopted**: loyalty (members, tiers, m-t-h), sales, catalog
- **Not yet**: insight collectors still use older patterns
- **Goal**: all Dataflow collectors should use BlmsCatalogConfig + ManagedIcebergWriteConfig

### Frozen dataclasses
- **Adopted**: loyalty (BlmsCatalogConfig, ManagedIcebergWriteConfig as frozen dataclasses)
- **Not yet**: insight, older collectors may use plain dicts or non-frozen classes

### managed.Write
- **Adopted**: loyalty, sales, catalog
- **Not yet**: insight may still use PyIceberg or older write patterns in Dataflow

### Partition field naming
- **loyalty members**: `ingestedTHDate` (INT YYYYMMDD / DATE)
- **loyalty tier_events**: `etlLoadTime` (INT YYYYMMDDHH / TIMESTAMP HOUR)
- **Other domains**: varies -- check per-collector config

### deploy.py alignment
- **loyalty**: cleaned -- Iceberg code removed, native BQ only (~370 lines)
- **sales**: similar pattern
- **Others**: may still have legacy Iceberg code in deploy.py

### CI/CD standardization
- **loyalty**: PROD uncommented, no STG-to-PROD gate
- **purchases/transactions**: have STG-to-PROD dependency gate
- **Goal**: standardize CI/CD patterns across all domains
