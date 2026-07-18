---
name: Sales Collector Schema Migration Plan
description: Major schema rename + logic changes for sales-collector refined BQ tables (receipt/sku/tender) — column renames, new fields, sign-flip expansion, filter change, CDC PK changes
type: project
---

## Sales Collector Schema Migration (2026-03-17)

Team profiled source data and updated `PIPELINE_ARCHITECTURE.md` with new column names + logic. SQL reference: `sale/doc/refined_sales.sql`

**Full plan**: `sale/sales-data/sales-collector/doc/SCHEMA_MIGRATION_PLAN.md`

**Why:** Team redesigned refined schema to better match Kafka field names and add missing fields. Previous schema used abbreviated names (receipt_no, trans_type, qty, etc.) — new schema uses full names (receipt_number, sale_type_code, quantity, etc.)

**How to apply:**
- Before starting: read the plan doc for exact field mappings
- 8 code files + 4 test files to change
- Key risk: CDC PK change + column rename on live BQ tables needs coordination
- Open questions in plan doc — verify with team before implementing

### Key Changes Summary
1. **Header rename**: receipt_no→receipt_number, trans_type→sale_type_code, card_no→card_number, member_number→member_id, pos_no→device_number, etc.
2. **Receipt**: +8 fields (source, sale_id, sale_number, transaction_channel, total_price, total_payment, total_payable_amount, total_point), -4 fields (storage_location, channel_type, sap_channel, online_order_id)
3. **SKU**: rename all item fields, +4 placeholder columns (sales_channel_main/assist/info/platform), +unit_vat_amount
4. **Tender**: major restructure — tender_type→payment_type, add entity_type/reference_number, remove card_carrier/financing/issuer_brand/issuer_card_type
5. **Sign-flip**: expand from 2→6 fields (receipt), add tender flip
6. **Filter**: `"03"` → `"SALE_CLEAR_DEPOSIT"`
7. **CDC PK**: sku uses line_number instead of sku, tender uses payment_type instead of tender_type+member_number
8. **display_receipt_no_2**: now extracted from `references[]` array, not flat field
