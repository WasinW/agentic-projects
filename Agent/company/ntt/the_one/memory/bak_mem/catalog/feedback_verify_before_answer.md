---
name: verify_before_answer
description: CRITICAL - Root cause patterns of repeated mistakes. Must read before every production change.
type: feedback
---

## Root Cause: แก้โดยไม่เข้าใจ root cause + ไม่ verify ก่อน deploy

### Pattern 1: แก้มั่ว — เดาแล้วลง prod เลย
- SDK crash → เดาว่า OOM → แก้ num_storage_api_streams + logger keys → ไม่ใช่ root cause
- S3 stuck → เดาว่า epoch fix กระทบ → จริงๆ ไม่เกี่ยวเลย (partition path ใช้ window time)
- User feedback: "ที่นี่คือ prod ไม่ใช่ที่ทดลอง ทุกการแก้ต้องมีสาเหตุ"
- **Rule: ห้ามแก้ prod โดยไม่มี proven root cause ห้ามเดา**

### Pattern 2: ไม่ verify กับ actual data/schema ก่อนให้คำตอบ
- CSV เพิ่ม custom_logic column → DTS พัง (ไม่เช็ค column count)
- consentVersion INT64→STRING → CDC พัง (ไม่เช็ค BQ table type)
- member_number alias memberId→memberNumber → memberId หาย ทุก row fail (ไม่เช็คว่า memberId มาจากไหน)
- CURRENT_TIMESTAMP() insert ลง STRING column → error (ไม่เช็ค column type)
- subDistrict vs subdistrict → ไม่เช็ค actual JSON field name
- **Rule: ก่อนแก้อะไร ต้อง verify กับ actual data/schema เสมอ ห้าม assume**

### Pattern 3: แก้ไปเรื่อย ไม่ถอยกลับมาคิด
- S3 write crash → ลอง WriteRecordToGCSDoFn → พังอีก (GlobalWindow) → แก้ → พังอีก (watermark lag) → เพิ่ม batch_size → ไม่ช่วย → CompactAndCopyToS3 ค้าง
- วนแก้ 5 รอบ ทั้งที่ควรถอยกลับมาคิด approach ใหม่ตั้งแต่แรก
- **Rule: ถ้าแก้ 2 ครั้งแล้วยังพัง ต้องหยุด ถอยกลับมาคิด approach ใหม่ ไม่ใช่แก้ไปเรื่อย**

### Pattern 4: ไม่เช็คผลกระทบข้ามระบบ
- แก้ mapping CSV → ไม่เช็คว่า DTS จะ sync ได้ไหม (column count)
- เปลี่ยน alias → ไม่เช็คว่า downstream (CDC, EXPORT) จะพังไหม
- เพิ่ม columns → ไม่เช็คว่า pipeline เดิมจะ break ไหม
- **Rule: ก่อนแก้ file ใดๆ ต้อง trace ว่าใครอ่าน file นั้น แล้วจะกระทบอะไร**

### Pattern 5: มั่นใจเกินไป ไม่ยอมบอกว่าไม่แน่ใจ
- "ไม่มีปัญหาครับ" → พัง
- "ถูกทางครับ ตรงจุด" → ไม่ตรง
- **Rule: ถ้าไม่ได้ verify จริง ต้องบอกว่า "ยังไม่ได้ verify" ไม่ใช่การันตี**

## How to apply (ทุกครั้งก่อนแก้ prod):
1. หา root cause จริงจาก log/data — ไม่ใช่เดา
2. Verify กับ actual BQ schema, actual data, actual CSV format
3. Compare กับ version เก่าที่ work ทุก field
4. Trace ผลกระทบ: ใครอ่าน file นี้? pipeline ไหนใช้? DTS sync ได้ไหม?
5. ถ้าไม่แน่ใจ บอกตรงๆ ว่าไม่แน่ใจ
6. ถ้าแก้ 2 ครั้งแล้วยังพัง → หยุด คิดใหม่ ไม่แก้ต่อ
