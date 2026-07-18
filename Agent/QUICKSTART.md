# Quickstart

1. **Invariant เดียว:** `Agent/` tree เป็นเจ้าของทุกไฟล์ที่ author เอง — `~/.claude/{skills,agents}` มีแต่ symlinks (doctor เช็คให้ทุก session)
2. **เริ่ม session:** doctor รายงาน KB health อัตโนมัติ; ถ้า DRIFT → `Agent/_infra/doctor.sh --fix`
3. **Spawn agent:** เรียกชื่อ role ได้เลย (data-architect, kafka-streaming-expert, databricks-expert, ...) — ดูรายชื่อใน `INDEX.md`
4. **เก็บความรู้:** raw dump → `company/<engagement>/_inbox/YYYYMMDD-topic.md` → `/kb-synth` → `knowledge/` (commit = embed อัตโนมัติ)
5. **New engagement:** copy `company/_template` → `company/<name>`, เขียน CLAUDE.md, แก้ "Current engagement:" ใน `~/.claude/CLAUDE.md` (บรรทัดเดียว), symlink skills ใหม่เข้า `~/.claude/skills/`
6. **New skill:** สร้างใน tree (`Agent/skills/` หรือ `company/*/skills/`) แล้ว `ln -s` เข้า `~/.claude/skills/` — ห้าม copy
7. **Archive:** `git mv` เข้า `_archive/` (ดู `_archive/README.md` — resurrect ได้เสมอ)
8. **Reindex เต็ม:** `Agent/_infra/reindex.sh --reset` (ต้องมี Docker/Qdrant up); incremental เกิดเองตอน commit
9. **Sandbox projects:** เริ่มที่ `company/project_sandbox/projects-knowledge-base/01-projects-master-knowledge.md` — สถานะ/verdict ล่าสุดอยู่ใน `portfolio-review-20260718.md`
10. **Code ≠ context:** code อยู่ `Project/`, ความรู้อยู่ `Agent/` — อย่าปน
