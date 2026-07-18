# Sales -- Schema Migration Summary

> Merged from: sales_schema_migration.md (plan) + sales_schema_migration_done.md (completion)
> Updated: 2026-04-05

---

## Status: CODE COMPLETE (2026-03-17)

All code changes done, 269 tests pass, mypy clean, pre-commit green.
BQ table migration (ALTER/recreate) still needed for production.

---

## Overview

Team profiled source data and redesigned refined schema to better match Kafka field names and add missing fields. Previous schema used abbreviated names (`receipt_no`, `trans_type`, `qty`) -- new schema uses full names (`receipt_number`, `sale_type_code`, `quantity`).

**Full plan doc**: `sale/sales-data/sales-collector/doc/SCHEMA_MIGRATION_PLAN.md`
**SQL reference**: `sale/doc/refined_sales.sql`

---

## Changes Summary

### 1. Column Renames (old -> new)
| Old | New |
|-----|-----|
| receipt_no | receipt_number |
| trans_type | sale_type_code |
| card_no | card_number |
| member_number | member_id |
| pos_no | device_number |
| orig_receipt_no | original_receipt_number |
| return_all_flag | is_all |
| net_price_tot (receipt) | net_total_price |
| net_price_tot (sku) | net_subtotal_price |
| discount_tot | total_discount |
| item_seq_no | line_number |
| qty | quantity |
| price_unit | unit_price |
| price_tot | subtotal_price |
| tender_type | payment_type |
| issuing_bank | issuer_bank |
| trans_date | transaction_date |

### 2. New Fields Added
- **Receipt**: `source`, `sale_id`, `sale_number`, `transaction_channel`, `total_price`, `total_payment`, `total_payable_amount`, `total_point`
- **SKU**: `unit_vat_amount`, `sales_channel_main`, `sales_channel_assist`, `sales_info`, `sales_channel_platform`
- **Tender**: `entity_type`, `reference_number`
- **All 3**: `display_receipt_no_2` now extracted from `references[]` array (not flat field)

### 3. Fields Removed
- **Receipt**: `storage_location`, `channel_type`, `sap_channel`, `online_order_id`, `customer_type`
- **Tender**: `card_carrier`, `financing`, `issuer_brand`, `issuer_card_type`

### 4. Sign-Flip Expansion
- Expanded from 2 -> 6 fields for receipt
- Added tender sign-flip
- Types: `RETURN_NORMAL`, `RETURN_DEPOSIT`, `VOID`, `VOID_SALE_DEPOSIT`

### 5. Filter Changes
- Old: `"03"` (numeric code)
- New: `"SALE_CLEAR_DEPOSIT"` (descriptive name)
- CEN partner filtered

### 6. CDC Primary Key Changes
- **Receipt**: unchanged (receipt_number + sale_type_code)
- **SKU**: uses `line_number` instead of `sku_code`
- **Tender**: uses `payment_type` instead of `tender_type + member_number`

### 7. Config Changes
- `base.yaml`: CDC PKs renamed, clustering renamed, partition field `trans_date` -> `transaction_date`
- `triggering_frequency_seconds`: 300 -> 1800 (then reduced to 60 due to OOM)

---

## Files Modified

### Code (8 files)
| File | Change |
|------|--------|
| `src/domain/bq_transformers.py` | Renamed all fields, added new fields, new sign-flip, display_receipt_no_2 from references[] |
| `src/domain/schemas.py` | Rewrote all 3 BQ schemas with `_HEADER_FIELDS` shared pattern |
| `src/domain/enrichment_logic.py` | `_EXCLUDED_TRANS_TYPES` from `{"03"}` -> `{"SALE_CLEAR_DEPOSIT"}` |
| `config/base.yaml` | CDC PKs, clustering, partition field renamed |
| `infrastructure/sales-collector/schemas/deploy.py` | Fixed INTERVAL syntax bug (`'0'` -> `'0:0:0'`) |

### Tests (5 files)
- All test files updated for new field names and schemas

---

## Deployment Notes

### BQ Table Migration Required
- Column renames require ALTER TABLE or recreate (backup -> drop -> create -> restore)
- CDC PK changes need: `ALTER TABLE DROP PRIMARY KEY` + `ADD PRIMARY KEY (...) NOT ENFORCED`
- deploy.py handles BREAKING changes via backup/restore flow

### deploy.py INTERVAL Fix
- **Bug**: `INTERVAL '0' HOUR TO SECOND` -- BQ rejected invalid format
- **Fix**: `INTERVAL '0:0:0' HOUR TO SECOND` (H:M:S format required)
- **File**: `infrastructure/sales-collector/schemas/deploy.py` lines 141, 171

---

## Pending After Schema Migration

1. **Streaming join research** -- agent was running web research on Bigtable/Redis/BQ/Beam Enrichment for 5 large batch table joins. MasterCache approach adopted.
2. **Date column renames** -- `trans_date` -> `transaction_datetime` (further rename to match data type, see pending_work.md)
