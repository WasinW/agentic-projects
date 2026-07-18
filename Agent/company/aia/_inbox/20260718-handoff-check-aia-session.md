# Handoff check — AIA session ตรวจก่อน push (2026-07-18)

> **สำหรับ:** Claude session ที่ดูงาน AIA / data-ml-ai-pipeline
> **จาก:** session redesign (agent system migration Phase 1-6)
> **งานของคุณ:** เช็คว่า migration ไม่ทำอะไรหาย + งาน AIA ทำงานต่อได้ แล้วเขียนผลลง §4 ข้างล่าง

## 1. อะไรย้ายไปไหน (ทั้งหมด `git mv` — history อยู่ครบ, ยังไม่ push)

| เดิม | ใหม่ |
|---|---|
| `Agent/company/project_sandbox/data-ml-ai-pipeline/knowledge/*` (6) | `Agent/company/aia/knowledge/` |
| `.../data-ml-ai-pipeline/aia/*` (teaching docs 5) | `Agent/company/aia/knowledge/` |
| `.../data-ml-ai-pipeline/aia/agent-draft.md` | `Agent/company/aia/_inbox/agent-draft-aia-de.md` |
| `.../data-ml-ai-pipeline/agents/aia-de.md` | `Agent/company/aia/_inbox/agent-aia-de.md` |
| `.../data-ml-ai-pipeline/knowledge_chat/*` (36) | `Agent/company/aia/_inbox/` (3 ไฟล์ชื่อมี space ถูก rename เป็น `20260713-*.md`) |
| `.../data-ml-ai-pipeline/skills/*` (9) | `Agent/company/aia/skills/` + symlink เข้า `~/.claude/skills/` → **invoke ได้แล้ว** (ก่อนหน้านี้ invoke ไม่ได้เลย) |
| `.../data-ml-ai-pipeline/de-databirck-aws/` | `Agent/_archive/company/de-databirck-aws/` (superseded — AIA = Azure) |
| `Declaration form.pdf` | `~/Documents/Declaration-form-AIA.pdf` (เอาออกจาก KB) |
| `Agent/company/AIA/knowledge/*` (1) | `Agent/company/aia/knowledge/` |

**สถานะปัจจุบัน:** `knowledge/` 12 ไฟล์ · `_inbox/` 39 ไฟล์ · `skills/` 9 (symlink ครบ 9)
`data-ml-ai-pipeline/` ถูกลบแล้ว (ว่างเปล่าหลังย้าย) — **path เก่าใช้ไม่ได้แล้ว**

## 2. สิ่งที่กำลังถูกสร้างเพิ่ม (subagent กำลังเขียน อาจเสร็จแล้วตอนคุณอ่าน)

- `Agent/company/aia/CLAUDE.md` — engagement context (workstreams, stack guard, skill list)
- `Agent/company/aia/INDEX.md` — map ของ knowledge/skills/_inbox
- Agent ใหม่: `kafka-streaming-expert` (จาก kafka-strimzi-cdc + event-processing docs)
- `azure-expert` ถูก rewrite เป็น AIA-primary

## 3. Checklist ให้เช็ค

- [ ] `ls Agent/company/aia/knowledge/` — ไฟล์ workstream ครบมั้ย (cost/RLS, UC cross-workspace, Genie, kafka, proxy, ...)? มีอะไรที่คุณจำได้ว่าเคยมีแต่หาไม่เจอ?
- [ ] `_inbox/` 39 ไฟล์ — knowledge_chat เดิมครบมั้ย (topic-2.1/2.2 ล่าสุด 20260717-18, solution-d-plus-resurrection)?
- [ ] Skill ใช้ได้จริง: ลองเรียก skill ที่ใช้บ่อย (เช่น databricks-genie-governance / databricks-uc-governance-sharing) — โหลดขึ้นมั้ย
- [ ] อ่าน `CLAUDE.md` + `INDEX.md` ใหม่ (ถ้าเสร็จแล้ว) — workstream/ชื่อทีม/สถานะถูกต้องตามความจริงมั้ย? **คุณรู้บริบท AIA ดีสุด — แก้ได้เลยถ้าผิด**
- [ ] Memory/notes ของ session คุณที่อ้าง path เก่า `data-ml-ai-pipeline` → update เป็น `company/aia`
- [ ] มีไฟล์/ข้อมูลที่ต้องใช้ทำงานต่อ แต่หาไม่เจอ → เขียนลง §4

**หมายเหตุ:** RAG (Qdrant) ยังไม่ reindex — `mcp__agent-knowledge__search_knowledge` อาจคืน path เก่าจนกว่าจะรัน `--reset` (คิวไว้หลังเช็คนี้) ให้เชื่อไฟล์บน disk เป็นหลัก

## 4. ผลการเช็ค (AIA session เขียนตรงนี้)

- สถานะ: ⬜ ยังไม่เช็ค / ⬜ ผ่าน — ไม่ขาดอะไร / ⬜ เจอปัญหา (ระบุด้านล่าง)
- ปัญหา/ของหาย:
- แก้ไปแล้ว:
