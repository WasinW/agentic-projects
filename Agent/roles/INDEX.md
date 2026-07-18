# Roles — Index (21 active)

แต่ละ role = atomic pair `{agent.md, knowledge.md}` — agent.md ถูก symlink เข้า `~/.claude/agents/<cat>/<name>.md` (spawn ได้ทันที) Updated 2026-07-18.

## technical/

- **architect/** — ai-architect, data-architect, platform-architect, solution-architect
- **consultant/** — azure-expert (AIA-primary), databricks-expert, governance-consultant, kafka-streaming-expert (ใหม่ 2026-07-18)
- **design/** — ui-designer, ux-designer
- **engineer/** — ai-art-director, ai-engineer, data-analyst, de-engineer, devops-engineer, security-engineer, software-engineer
- **ops/** — data-ops (ดูด FinOps จาก platform-ops เดิม)

## business/

analyst (merge business-analyst + system-analyst), content-strategist, finance-consultant

## Retired (15 — ดู ../_archive/roles/)

enterprise-architect, blockchain-architect, blockchain-consultant, business-analyst, system-analyst, data-domain-expert, investment-consultant, marketing-consultant, sales-consultant, aws-expert, gcp-expert, frontend-engineer, ml-engineer, ml-ops, platform-ops — resurrect: `git mv` กลับ + symlink

## Conventions

- Agent template: evergreen knowledge-sources block (knowledge.md fixed-path ก่อน → engagement context → RAG optional)
- `KNOWLEDGE_CHECKLIST.md` — ใช้ตอนเขียน knowledge.md ใหม่
