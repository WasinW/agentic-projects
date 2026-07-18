# Schema Mapping Reference — Sales-Collector

[< Back to README](./README.md)

---

## Kafka Event Structure (Schema B)

```json
{
  "eventId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "source": "pos-system",
  "eventName": "loyalty.sales.created",
  "timestamp": 1740200000,
  "payload": {
    "receiptNumber": "R20260222001",
    "saleTypeCode": "SALE",
    "partnerCode": "CDS",
    "branchCode": "00123",
    "cardNumber": "1234567890123456",
    "memberId": "M000001234",
    "deviceNumber": "POS-01",
    "transactionDate": 1740200000,
    "businessDate": "2026-02-22T00:00:00+07:00",
    "invoiceDate": "2026-02-22",
    "deliveryDate": null,
    "displayReceiptNumber": "D-R20260222001",
    "customerType": "MEMBER",
    "transactionChannelId": "STORE",
    "staffId": "EMP001",
    "voidInformation": {
      "originalReceiptNumber": null,
      "isAll": false
    },
    "receipt": {
      "totalPrice": {"string": "1500.00"},
      "items": {"array": [
        {
          "lineNumber": "1",
          "sku": "SKU001",
          "barcode": "8851234567890",
          "skuName": "Product A",
          "deptCode": "D01",
          "deptName": "Department 1",
          "subDeptCode": "SD01",
          "productBrandId": "BR001",
          "quantity": 2,
          "unitPrice": {"string": "500.00"},
          "subtotalPrice": {"string": "1000.00"},
          "netUnitPrice": {"string": "450.00"},
          "netSubtotalPrice": {"string": "900.00"},
          "totalDiscount": {"string": "100.00"}
        }
      ]}
    },
    "payments": {"array": [
      {
        "itemSeqNo": "1",
        "amount": {"string": "1500.00"},
        "reference": {
          "paymentType": "CREDIT_CARD",
          "paymentReferenceNumber": "XXXX-XXXX-XXXX-1234",
          "issuerBank": "SCB"
        }
      }
    ]}
  }
}
```

> **Note:** Values wrapped as `{"string": "..."}` or `{"array": [...]}` are Avro union representations — unwrapped automatically by the pipeline.

---

## Source Layer — Iceberg Schema

`source.raw_sales_created` / `source.raw_sales_updated`

| Column | PyArrow Type | Mode | Source |
|--------|-------------|------|--------|
| `eventId` | `string` | Required | Wrapper `eventId` |
| `source` | `string` | Nullable | Wrapper `source` |
| `eventName` | `string` | Nullable | Wrapper `eventName` |
| `timestamp` | `int64` | Nullable | Wrapper `timestamp` (unix seconds) |
| `payload` | `string` | Nullable | Inner payload dict (JSON-serialized) |
| `etlLoadTime` | `int64` | Required | System-generated `YYYYMMDDHH` (Bangkok +7) |

**Partition:** `identity(etlLoadTime)` — one partition per hour.

---

## Refined Layer — Header Fields (Shared Across All 3 Tables)

All three BQ tables share these 14 header fields + 3 partition fields, extracted by `_extract_header_fields()`:

| # | BQ Column | Kafka Path (primary) | Fallback 1 | Fallback 2 | BQ Type | Converter |
|---|-----------|---------------------|------------|------------|---------|-----------|
| 1 | `receipt_no` | `receiptNumber` | `receiptNo` | `receipt_no` | STRING | `_safe_str` |
| 2 | `trans_type` | `saleTypeCode` | `transType` | `trans_type` | STRING | `_safe_str` |
| 3 | `partner_code` | `partnerCode` | `partner_code` | — | STRING | `_safe_str` |
| 4 | `branch_code` | `branchCode` | `branch_code` | — | STRING | `_safe_str` |
| 5 | `card_no` | `cardNumber` | `cardNo` | `card_no` | STRING | `_safe_str` |
| 6 | `member_number` | `memberId` | `memberNumber` | `member_number` | STRING | `_safe_str` |
| 7 | `pos_no` | `deviceNumber` | `posNo` | `pos_no` | STRING | `_safe_str` |
| 8 | `trans_date` | `transactionDate` | `transDate` | `trans_date` | TIMESTAMP | `_parse_timestamp` (+7h) |
| 9 | `business_date` | `businessDate` | `business_date` | — | TIMESTAMP | `_parse_timestamp` (+7h) |
| 10 | `invoice_date` | `invoiceDate` | `invoice_date` | — | STRING | `_safe_str` |
| 11 | `delivery_date` | `deliveryDate` | `delivery_date` | — | STRING | `_safe_str` |
| 12 | `display_receipt_no` | `displayReceiptNumber` | `displayReceiptNo` | `display_receipt_no` | STRING | `_safe_str` |
| 13 | `display_receipt_no_2` | `displayReceiptNo2` | `display_receipt_no_2` | — | STRING | `_safe_str` |
| 14 | `etl_updated_date` | (system-generated) | — | — | TIMESTAMP | `_get_bangkok_timestamp()` |
| 15 | `par_month` | derived from `trans_date` | — | — | STRING | `"%Y%m"` (e.g. `"202602"`) |
| 16 | `par_day` | derived from `trans_date` | — | — | STRING | `"%d"` (e.g. `"22"`) |
| 17 | `par_hour` | derived from `trans_date` | — | — | STRING | `"%H"` (e.g. `"14"`) |

---

## sales_receipt — Receipt-Level Fields

**One row per Kafka event.** Function: `to_receipt_row()`

BQ partitioning: `MONTH` on `trans_date`. Clustering: `partner_code`, `member_number`, `branch_code`.

| # | BQ Column | Kafka Path | Fallback 1 | Fallback 2 | BQ Type | Notes |
|---|-----------|-----------|------------|------------|---------|-------|
| | *(17 header + partition fields)* | | | | | See above |
| 18 | `orig_receipt_no` | `voidInformation.originalReceiptNumber` | `origReceiptNo` | `orig_receipt_no` | STRING | Nested in voidInformation |
| 19 | `item_seq_no` | `itemSeqNo` | `item_seq_no` | — | STRING | Top-level field |
| 20 | `net_price_tot` | `receipt.totalPrice` | `totalPrice` | `net_price_tot` | NUMERIC | Nested in receipt object |
| 21 | `customer_type` | `customerType` | `customer_type` | — | STRING | |
| 22 | `sales_channel` | `transactionChannelId` | `salesChannel` | `sales_channel` | STRING | |
| 23 | `return_all_flag` | `voidInformation.isAll` | `returnAllFlag` | `return_all_flag` | STRING | Bool→"Y"/"N" conversion |
| 24 | `staff_id` | `staffId` | `staff_id` | — | STRING | |
| 25 | `storage_location` | `storageLocation` | `storage_location` | — | STRING | |
| 26 | `channel_type` | `channelType` | `channel_type` | — | STRING | |
| 27 | `sap_channel` | `sapChannel` | `sap_channel` | — | STRING | |
| 28 | `online_order_id` | `onlineOrderId` | `online_order_id` | — | STRING | |
| 29 | `sales_channel_main` | `salesChannelMain` | `sales_channel_main` | — | STRING | |
| 30 | `sales_channel_assist` | `salesChannelAssist` | `sales_channel_assist` | — | STRING | |
| 31 | `sales_info` | `salesInfo` | `sales_info` | — | STRING | |
| 32 | `sales_channel_platform` | `salesChannelPlatform` | `sales_channel_platform` | — | STRING | |

**Special: `return_all_flag` conversion:**
```python
is_all = void_info.get("isAll")
if isinstance(is_all, bool):
    return "Y" if is_all else "N"
else:
    return _safe_str(data.get("returnAllFlag") or data.get("return_all_flag"))
```

**Special: `net_price_tot` path:**
```python
receipt_obj = data.get("receipt") or {}
net_price_tot = _parse_numeric(receipt_obj.get("totalPrice"))
# fallback: data.get("totalPrice") or data.get("net_price_tot")
```

---

## sales_sku — SKU Line Item Fields

**N rows per Kafka event** (one per `receipt.items[]` element). Function: `to_sku_rows()`

BQ partitioning: `MONTH` on `trans_date`. Clustering: `partner_code`, `sku_code`, `member_number`.

### Items Array Navigation

```python
receipt_obj = data.get("receipt")
if isinstance(receipt_obj, dict):
    items = unwrap_avro_array(receipt_obj.get("items") or [])  # primary
else:
    items = unwrap_avro_array(data.get("items") or data.get("skus") or [])  # fallback
```

### Per-Item Fields

| # | BQ Column | Kafka Path (per item) | Fallback 1 | Fallback 2 | BQ Type | Notes |
|---|-----------|----------------------|------------|------------|---------|-------|
| | *(17 header + partition fields)* | | | | | From top-level data |
| 18 | `item_seq_no` | `item.lineNumber` | `item.itemSeqNo` | `item.item_seq_no` | STRING | |
| 19 | `sku_code` | `item.sku` | `item.skuCode` | `item.sku_code` | STRING | |
| 20 | `barcode` | `item.barcode` | — | — | STRING | |
| 21 | `sku_name` | `item.skuName` | `item.sku_name` | — | STRING | |
| 22 | `dept_code` | `item.deptCode` | `item.dept_code` | — | STRING | |
| 23 | `dept_name` | `item.deptName` | `item.dept_name` | — | STRING | |
| 24 | `sub_dept_code` | `item.subDeptCode` | `item.sub_dept_code` | — | STRING | |
| 25 | `brand_code` | `item.productBrandId` | `item.brandCode` | `item.brand_code` | STRING | |
| 26 | `qty` | `item.quantity` | `item.qty` | — | NUMERIC | |
| 27 | `price_unit` | `item.unitPrice` | `item.priceUnit` | `item.price_unit` | NUMERIC | |
| 28 | `price_tot` | `item.subtotalPrice` | `item.priceTot` | `item.price_tot` | NUMERIC | |
| 29 | `net_price_unit` | `item.netUnitPrice` | `item.netPriceUnit` | `item.net_price_unit` | NUMERIC | |
| 30 | `net_price_tot` | `item.netSubtotalPrice` | `item.netPriceTot` | `item.net_price_tot` | NUMERIC | |
| 31 | `discount_tot` | `item.totalDiscount` | `item.discountTot` | `item.discount_tot` | NUMERIC | |
| 32 | `customer_type` | `item.customerType` | `data.customerType` | `data.customer_type` | STRING | Item-level first, then event-level |
| 33 | `sales_channel_main` | `item.salesChannelMain` | `data.salesChannelMain` | `data.sales_channel_main` | STRING | Item-level first, then event-level |
| 34 | `sales_channel_assist` | `item.salesChannelAssist` | `data.salesChannelAssist` | `data.sales_channel_assist` | STRING | Item-level first, then event-level |
| 35 | `sales_info` | `item.salesInfo` | `data.salesInfo` | `data.sales_info` | STRING | Item-level first, then event-level |
| 36 | `sales_channel_platform` | `item.salesChannelPlatform` | `data.salesChannelPlatform` | `data.sales_channel_platform` | STRING | Item-level first, then event-level |

---

## sales_tender — Tender/Payment Fields

**M rows per Kafka event** (one per `payments[]` element). Function: `to_tender_rows()`

BQ partitioning: `MONTH` on `trans_date`. Clustering: `partner_code`, `tender_type`, `member_number`.

### Payments Array Navigation

```python
tenders = unwrap_avro_array(data.get("payments") or data.get("tenders") or [])
```

### Per-Tender Fields

| # | BQ Column | Kafka Path (per tender) | Fallback 1 | Fallback 2 | BQ Type | Notes |
|---|-----------|------------------------|------------|------------|---------|-------|
| | *(17 header + partition fields)* | | | | | From top-level data |
| 18 | `item_seq_no` | `tender.itemSeqNo` | `tender.item_seq_no` | — | STRING | |
| 19 | `tender_type` | `tender.reference.paymentType` | `tender.tenderType` | `tender.tender_type` | STRING | Nested in reference |
| 20 | `credit_card` | `tender.reference.paymentReferenceNumber` | `tender.creditCard` | `tender.credit_card` | STRING | Nested in reference |
| 21 | `issuing_bank` | `tender.reference.issuerBank` | `tender.issuingBank` | `tender.issuing_bank` | STRING | Nested in reference |
| 22 | `net_price_tot` | `tender.amount` | `tender.netPriceTot` | — | NUMERIC | |
| 23 | `customer_type` | `tender.customerType` | `data.customerType` | `data.customer_type` | STRING | Tender-level first, then event |
| 24 | `orig_receipt_no` | `voidInformation.originalReceiptNumber` | `data.origReceiptNo` | `data.orig_receipt_no` | STRING | From top-level voidInformation |
| 25 | `sales_channel` | `data.transactionChannelId` | `tender.salesChannel` | `data.salesChannel` | STRING | Event-level first |
| 26 | `return_all_flag` | `tender.returnAllFlag` | `tender.return_all_flag` | — | STRING | No bool conversion (raw string) |
| 27 | `sales_channel_main` | `tender.salesChannelMain` | `data.salesChannelMain` | `data.sales_channel_main` | STRING | Tender-level first, then event |
| 28 | `sales_channel_assist` | `tender.salesChannelAssist` | `data.salesChannelAssist` | `data.sales_channel_assist` | STRING | Tender-level first, then event |
| 29 | `sales_info` | `tender.salesInfo` | `data.salesInfo` | `data.sales_info` | STRING | Tender-level first, then event |
| 30 | `sales_channel_platform` | `tender.salesChannelPlatform` | `data.salesChannelPlatform` | `data.sales_channel_platform` | STRING | Tender-level first, then event |

---

## Type Conversion Reference

### Timestamp Parsing (`_parse_timestamp`)

| Input | Detection | Conversion |
|-------|-----------|------------|
| Unix seconds (int/float `<= 1e12`) | `isinstance(raw, (int, float))` | `Timestamp(seconds=int(ts) + 25200)` |
| Unix milliseconds (int/float `> 1e12`) | `ts > 1e12` → divide by 1000 | `Timestamp(seconds=int(ts/1000) + 25200)` |
| ISO string (`"2026-02-22T..."`) | `isinstance(raw, str)` | `fromisoformat()` → `Timestamp(seconds=unix + 25200)` |
| ISO string with `Z` suffix | Replace `"Z"` → `"+00:00"` | Same as above |
| `None` / empty | — | `None` |

All timestamps add `+7 * 3600` seconds (Bangkok offset). Output type: `apache_beam.utils.timestamp.Timestamp`.

### Numeric Parsing (`_parse_numeric`)

```python
raw = unwrap_avro_value(value)  # {"string": "1500.00"} → "1500.00"
return Decimal(str(raw))        # str() handles int/float/str safely
```

Output type: `decimal.Decimal` — prevents float precision loss for BQ NUMERIC.

### String Parsing (`_safe_str`)

```python
raw = unwrap_avro_value(value)
s = str(raw)
return s if s else None         # empty string → None
```

### Avro Union Unwrapping

| Input | Function | Output |
|-------|----------|--------|
| `{"string": "abc"}` | `unwrap_avro_value` | `"abc"` |
| `{"int": 42}` | `unwrap_avro_value` | `42` |
| `None` | `unwrap_avro_value` | `None` |
| `"plain"` | `unwrap_avro_value` | `"plain"` (passthrough) |
| `{"array": [1,2,3]}` | `unwrap_avro_array` | `[1,2,3]` |
| `[1,2,3]` | `unwrap_avro_array` | `[1,2,3]` (passthrough) |
| `None` | `unwrap_avro_array` | `[]` (empty list) |

### Fallback Field Name Priority

All field lookups follow a consistent fallback pattern:

```
1. Kafka primary name     (camelCase from current API spec)
2. Legacy camelCase        (older API version)
3. snake_case              (alternative format)
```

Example: `receiptNumber` → `receiptNo` → `receipt_no`

---

## Column Presence Matrix

| Column | receipt | sku | tender |
|--------|:---:|:---:|:---:|
| receipt_no | Y | Y | Y |
| trans_type | Y | Y | Y |
| partner_code | Y | Y | Y |
| branch_code | Y | Y | Y |
| card_no | Y | Y | Y |
| member_number | Y | Y | Y |
| pos_no | Y | Y | Y |
| trans_date | Y | Y | Y |
| business_date | Y | Y | Y |
| invoice_date | Y | Y | Y |
| delivery_date | Y | Y | Y |
| display_receipt_no | Y | Y | Y |
| display_receipt_no_2 | Y | Y | Y |
| etl_updated_date | Y | Y | Y |
| par_month / par_day / par_hour | Y | Y | Y |
| orig_receipt_no | Y | — | Y |
| item_seq_no | Y | Y | Y |
| net_price_tot | Y | Y | Y |
| customer_type | Y | Y | Y |
| sales_channel | Y | — | Y |
| return_all_flag | Y | — | Y |
| staff_id | Y | — | — |
| storage_location | Y | — | — |
| channel_type | Y | — | — |
| sap_channel | Y | — | — |
| online_order_id | Y | — | — |
| sales_channel_main | Y | Y | Y |
| sales_channel_assist | Y | Y | Y |
| sales_info | Y | Y | Y |
| sales_channel_platform | Y | Y | Y |
| sku_code | — | Y | — |
| barcode | — | Y | — |
| sku_name | — | Y | — |
| dept_code | — | Y | — |
| dept_name | — | Y | — |
| sub_dept_code | — | Y | — |
| brand_code | — | Y | — |
| qty | — | Y | — |
| price_unit | — | Y | — |
| price_tot | — | Y | — |
| net_price_unit | — | Y | — |
| discount_tot | — | Y | — |
| tender_type | — | — | Y |
| credit_card | — | — | Y |
| issuing_bank | — | — | Y |
