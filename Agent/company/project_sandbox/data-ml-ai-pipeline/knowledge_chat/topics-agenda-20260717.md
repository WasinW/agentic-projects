# AIA — Topics / Agenda (noted 2026-07-17)

> **สำหรับ:** สิน — note คร่าวๆ ก่อน ยังไม่ลงรายละเอียด (แต่ละเรื่อง "เดี๋ยวคุยกัน")
> **ที่มา:** ขยาย scope จาก cost dashboard เดิม เป็น 3 workstream
> **ลำดับ:** ทำ Topic 1 + 2 ก่อน · Topic 3 (observability) ไว้ทีหลัง

---

## 📊 Topic 1 — Cost Dashboard: publish to departmental + per-team row-level (เรื่องเดิม)

**= สิ่งที่คุยกันมาตลอด** — dashboard ค่าใช้จ่าย, share ให้ทีมเฉพาะ, คุม row-level access ต่อทีม ที่ coredata

**สถานะล่าสุด (2026-07-15):**
- 🔑 Sarunya ยอมให้ **share table ผ่าน UC** → **D+ ฟื้น (conditional)**
- ⚠️ verify แล้ว: UC GRANT ไม่พอ — ต้องเปิด **network path (PROD compute → DEV storage)** ด้วย
- 🧪 กำลังจะ PoC ที่ coredata UAT (`SELECT LIMIT 10` + decision tree)
- 🔀 email artifact (PDF+Excel) = interim · D+ = target
- ไฟล์: `context-20260715-vscode-uc-share-pivot.md`, `solution-artifact-factory-20260714-2040.md`, `solutions-catalog/compare-20260714-2040.md`

> **แหล่ง cost ของ Topic 1 = Azure infrastructure cost** (Cost Management Export → ADLS, tag ต่อทีม) — **คนละแหล่งกับ Topic 2.1** ⚠️ (สำคัญ ดูข้างล่าง)

---

## 🤖 Topic 2 — Genie AI in Azure Databricks (ใหม่)

**บริบท:** ใน departmental workspace (จริงๆ ทุกที่) — ทีมอยากทำ 2 เรื่อง

### 2.1 — Tracking & monitoring cost (ของ Databricks เอง)
- มี SQL คร่าวๆ แล้ว: ดึงจาก `system.billing.usage` + `system.billing.list_prices`
- 🚨 **ปัญหาที่ยังไม่เคลียร์: ตัวเลขไม่เท่ากับหน้า Cost Management บน Azure Portal**

> **⚠️ hook สำคัญ (น่าจะเป็นเหตุผลหลัก — ไว้คุยรายละเอียด):**
> `system.billing.usage` = **DBU consumption ของ Databricks เท่านั้น** ไม่ใช่บิล Azure ทั้งก้อน
> Portal Cost Management เห็น**มากกว่า** เพราะรวม:
> - **VM/compute จริง** (classic compute → VM ถูกบิลแยกใน Azure ไม่อยู่ใน system.billing)
> - **storage, networking, egress** ฯลฯ
> - `list_prices` = **ราคา list ไม่ใช่ราคาจริง** (ไม่รวม discount / committed-use / EA)
> - อาจต่างเรื่อง **timezone / granularity** ด้วย
> → **Topic 2.1 = Databricks DBU cost · Topic 1 = Azure infra cost — คนละ layer อย่าปน**

### 2.2 — Manage budget + access control ต่อทีมใน departmental
บริบท: จาก dashboard ที่ share ไป → user เข้ามาใช้ **Genie AI** บน workspace นั้นได้

**requirement จากทีม (verbatim):**
> *"consumer access ตัว end goal คือเราอยากให้ business user ใช้เฉพาะ Genie AI/BI ได้ แต่ต้องตั้ง job ไม่ได้ คือ ถ้าเค้าเข้าได้แต่ genie one ก็จะไม่มีปัญหา"*

**→ 2 เรื่องซ้อนกัน:**
| | เรื่อง | hook ที่รู้แล้ว |
|---|---|---|
| **(a)** | **คุมการใช้งาน/สิทธิ์** — business user ใช้ได้แค่ Genie/AI-BI, **สร้าง job ไม่ได้** | ⭐ ตรงกับ **entitlement tier** ที่ research มาแล้ว: **Consumer access = view-only** (รัน dashboard/Genie ได้ แต่ **author/สร้าง job ไม่ได้** — ต้อง Tier 3 SQL access ถึงจะสร้างได้) → **นี่คือ tier ที่ requirement ต้องการพอดี** |
| **(b)** | **budget** — คุมงบต่อทีม | ⭐ **Databricks Budgets GA 2026-07-06** — ตั้ง limit ต่อ user/tag + **block ได้** · Genie เป็น pay-as-you-go LLM DBU (ฟรี 150/user/เดือน) ตั้งแต่ 2026-07-08 |

---

## 🔭 Topic 3 — Observability dashboard (ไว้ทีหลัง)
ดู quality / pipeline status: Databricks **job & cluster**, **Kafka cluster**, **dashboard availability**, อื่นๆ
→ **หลัง Topic 1 + 2 ก่อน**

---

## 🔗 เส้นเชื่อมที่เห็น (ไว้ใช้ตอนลงรายละเอียด)
1. **2 แหล่ง cost อย่าปน:** Topic 1 = Azure infra (Cost Mgmt Export) · Topic 2.1 = Databricks DBU (system.billing)
2. **2.2(a) access control = entitlement tier** ที่ research มาแล้ว (Consumer access = คำตอบ) — มีใน `solutions-catalog-20260714-2040.md` §1
3. **2.2(b) budget = Databricks Budgets (GA 2026-07-06)** + Genie pay-as-you-go
4. Topic 2 อยู่บน departmental workspace → ผูกกับผล PoC ของ Topic 1 (ว่า user เข้า Genie ที่ departmental ได้แค่ไหน)
