# _archive — cold storage (machine-excluded)

ทุกอย่างในนี้ **ไม่ถูก embed เข้า RAG, ไม่มี symlink, ไม่อยู่ใน INDEX** แต่ยังอยู่ใน git เต็มรูป

| Path | คืออะไร | Archive เมื่อ | เหตุผล |
|---|---|---|---|
| company/ntt | The-1/NTT engagement KB (269 files) | 2026-07-18 | จบ engagement 2026-06; เก็บเป็น past-experience KB |
| company/scb | SCB Data-X retrospective | 2026-07-18 | past experience |
| company/de-databirck-aws | AWS-angle doc ยุคเข้าใจผิดว่า AIA ใช้ AWS | 2026-07-18 | superseded (AIA = Azure) |
| pipelines | orchestration playbooks (sample เดียว) | 2026-07-18 | ไม่เคยใช้ |
| socratic-lab | KnowledgeOps experiment | 2026-07-18 | ปิด decision: ใช้ kb-synth เป็น curation path เดียว |
| roles/* | retired subagent roles (agent+knowledge คู่กัน) | 2026-07-18 | ไม่มี evidence การใช้; ดู agent-system-redesign-20260718.md |
| skills/* | retired skills | 2026-07-18 | ซ้ำกับ agent/skill อื่น |

**วิธี resurrect:** `git mv _archive/<path> <path เดิม>` + สร้าง symlink กลับใน `~/.claude/{skills,agents}` ถ้าเป็น skill/agent แล้ว reindex
