---
name: Sales schema migration completed
description: Schema migration for sales-collector refined tables completed (column renames, new fields, sign-flip, filter, CDC PK changes) — 2026-03-17
type: project
---

## Sales Schema Migration — COMPLETED (2026-03-17)

All code changes done, 269 tests pass, mypy clean, pre-commit green.

### What was changed

**Files modified:**
- `src/domain/bq_transformers.py` — renamed all fields, added new fields, new sign-flip, display_receipt_no_2 from references[]
- `src/domain/schemas.py` — rewrote all 3 BQ schemas with _HEADER_FIELDS shared pattern
- `src/domain/enrichment_logic.py` — `_EXCLUDED_TRANS_TYPES` from `{"03"}` → `{"SALE_CLEAR_DEPOSIT"}`
- `config/base.yaml` — CDC PKs renamed, clustering renamed, partition field `trans_date` → `transaction_date`, triggering_frequency 300→1800
- `infrastructure/sales-collector/schemas/deploy.py` — fixed INTERVAL syntax bug
- 5 test files updated

### Key field mapping (old → new)
- `receipt_no` → `receipt_number`
- `trans_type` → `sale_type_code`
- `card_no` → `card_number`
- `member_number` → `member_id`
- `pos_no` → `device_number`
- `orig_receipt_no` → `original_receipt_number`
- `return_all_flag` → `is_all`
- `net_price_tot` → `net_total_price` (receipt) / `net_subtotal_price` (sku)
- `discount_tot` → `total_discount`
- `item_seq_no` → `line_number`
- `qty` → `quantity`
- `price_unit` → `unit_price`
- `price_tot` → `subtotal_price`
- `tender_type` → `payment_type`
- `issuing_bank` → `issuer_bank`

### New fields added
- Receipt: `source`, `sale_id`, `sale_number`, `transaction_channel`, `total_price`, `total_payment`, `total_payable_amount`, `total_point`
- SKU: `unit_vat_amount`, `sales_channel_main`, `sales_channel_assist`, `sales_info`, `sales_channel_platform`
- Tender: `entity_type`, `reference_number`
- All 3: `display_receipt_no_2` now extracted from `references[]` array

### Fields removed
- Receipt: `storage_location`, `channel_type`, `sap_channel`, `online_order_id`, `customer_type`
- Tender: `card_carrier`, `financing`, `issuer_brand`, `issuer_card_type`

### Deployment notes
- **BQ tables need schema migration** — column renames require ALTER or recreate
- **CDC PK changes** need `ALTER TABLE DROP PRIMARY KEY` + `ADD PRIMARY KEY`
- **deploy.py INTERVAL bug fixed** — was `'0'`, now `'0:0:0'`

### Pending research (agent was running)
- Streaming join with 5 large batch tables (15M rows each) for sales enrichment
- Agent was doing web research on Bigtable/Redis/BQ scheduled queries/Beam Enrichment
- If agent didn't finish, re-run the research in next session
