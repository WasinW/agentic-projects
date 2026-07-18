# Memory Export Prompt Template
**ใช้ prompt นี้ copy ไปวางที่ session อื่นๆ เพื่อ export memory ออกมา**

---

## วิธีใช้
1. เปิด session ที่ต้องการ export
2. Copy prompt ด้านล่าง → paste ที่ session นั้น
3. แก้ `<DOMAIN_NAME>` เป็นชื่อ domain (เช่น sales, insight, coupons, partner)
4. Claude จะสร้าง SESSION_SUMMARY.md + copy memory files ให้

---

## Prompt (Copy ทั้งหมดด้านล่างนี้)

```
ผมต้องการ export memory และ context ทั้งหมดของ session นี้ออกมาเป็นไฟล์ เพื่อนำไปใช้กับ multi-agent system ที่จะสร้างใหม่

ขั้นตอน:
1. สร้าง directory: `/Users/wasin/Documents/ntt_project/the_one/realproject/the1-re-data-platform/agent/bak_mem/<DOMAIN_NAME>/`

2. Copy memory files ทั้งหมดจาก auto memory ของ session นี้ไปวางที่ directory ข้างบน
   - ดู memory path จาก MEMORY.md ที่ load อยู่ใน context ของคุณ

3. สร้างไฟล์ SESSION_SUMMARY.md ที่ directory เดียวกัน โดยมีเนื้อหาครอบคลุม:

   a. **Session Owner & Role** — ข้อมูล user (role, working style, language preference)
   
   b. **Project Overview** — GCP project, repo location, tech stack
   
   c. **Architecture** — system diagram (data flow จาก source → sink)
   
   d. **Components Managed** — list ทุก component/collector/pipeline ที่ดูแล พร้อม mode, source, sink, status
   
   e. **Key Technical Decisions** — ทุก decision สำคัญที่ตัดสินใจไปแล้ว (architecture, pattern, tool choice) พร้อมเหตุผล
   
   f. **Completed Work** — list งานที่เสร็จแล้ว (major items)
   
   g. **Pending Work** — list งานที่ยังค้าง/รอ
   
   h. **Memory Files Exported** — table แสดง filename + description ของทุกไฟล์ที่ export
   
   i. **Key Rules** — rules/constraints สำคัญสำหรับ domain นี้ (เช่น path ที่ถูก, validation steps, ข้อห้าม)
   
   j. **Common Errors & Fixes** — errors ที่เคยเจอ + วิธีแก้
   
   k. **Cross-Domain Dependencies** — ถ้ามี dependency กับ domain อื่น (เช่น shared infra, common library)

4. ห้ามหลุด context สำคัญ — ถ้ามี session summary จาก /compact ให้รวมข้อมูลจากนั้นด้วย

5. เขียนเป็น Markdown ให้ structured, อ่านง่าย, ใช้ table/code block ตามเหมาะสม

6. ถ้ามี plan file (จาก plan mode) ให้ copy plan content เข้าไปใน SESSION_SUMMARY.md ด้วย ในส่วน "Active Plan"

บอกผมด้วยว่า export ไปกี่ไฟล์ และมีอะไรบ้าง
```

---

## หลัง Export ทุก Session แล้ว

Structure ที่ควรได้:
```
the1-re-data-platform/agent/bak_mem/
├── EXPORT_PROMPT_TEMPLATE.md      ← ไฟล์นี้
├── loyalty/
│   ├── SESSION_SUMMARY.md
│   ├── MEMORY.md
│   ├── loyalty_knowledge_base.md
│   ├── mistakes_and_rules.md
│   └── ... (14 files)
├── sales/
│   ├── SESSION_SUMMARY.md
│   └── ... (memory files)
├── insight/
│   ├── SESSION_SUMMARY.md
│   └── ... (memory files)
├── coupons/
│   ├── SESSION_SUMMARY.md
│   └── ... (memory files)
└── <other-domain>/
    └── ...
```

นำ directory นี้ทั้งหมดไปใช้กับ **agent-builder session** (ดู AGENT_BUILDER_PROMPT.md)
