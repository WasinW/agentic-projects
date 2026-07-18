---
name: Sales deploy.py max_staleness INTERVAL fix
description: Fixed BQ INTERVAL syntax error in deploy.py that prevented PK changes on CDC tables with max_staleness
type: project
---

## deploy.py max_staleness INTERVAL fix (2026-03-17)

**Bug**: `deploy.py` ใช้ `INTERVAL '0' HOUR TO SECOND` เพื่อ disable max_staleness ก่อนเปลี่ยน PK → BQ reject เพราะ format ผิด

**Fix**: เปลี่ยนเป็น `INTERVAL '0:0:0' HOUR TO SECOND` (ต้องเป็น H:M:S format)

**File**: `sale/sales-data/infrastructure/sales-collector/schemas/deploy.py` lines 141, 171

**Why:** BQ ต้องการ INTERVAL ในรูปแบบ `'H:M:S'` HOUR TO SECOND — `'0'` ไม่ถูก syntax

**How to apply:** ถ้าเจอ INTERVAL errors ใน deploy.py อื่นๆ ตรวจ format ให้เป็น `'H:M:S'`
