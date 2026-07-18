# Agent System — Top Index

> Updated 2026-07-18 (post-redesign). ACTIVE only — archived things live in `_archive/` (ดู `_archive/README.md`).
> **Invariant:** tree นี้เป็น source of truth ทุกไฟล์; `~/.claude/{skills,agents}` = symlinks เท่านั้น (doctor เช็คทุก session)

## Layout

```
Agent/
├── INDEX.md · QUICKSTART.md
├── roles/<cat>/<role>/{agent.md, knowledge.md}   ← fleet 21 agents (atomic pair)
├── skills/                                       ← cross-project skills (10)
├── company/
│   ├── aia/          ← CURRENT engagement (knowledge/ + skills/ 9 + _inbox/)
│   ├── _template/    ← copy เมื่อเริ่ม engagement ใหม่
│   └── project_sandbox/   ← personal projects
├── _infra/    ← RAG (Qdrant) + doctor.sh + reindex.sh + hooks/
├── _archive/  ← cold storage (ntt, scb, retired roles/skills, pipelines)
└── _reviews/  ← system reviews (agent-system-redesign-20260718.md)
```

## Agents (21) — spawn ตามชื่อ

- **architect:** ai-architect, data-architect, platform-architect, solution-architect
- **business:** analyst, content-strategist, finance-consultant
- **consultant:** azure-expert, databricks-expert, governance-consultant, kafka-streaming-expert
- **design:** ui-designer, ux-designer
- **engineer:** ai-art-director, ai-engineer, data-analyst, de-engineer, devops-engineer, security-engineer, software-engineer
- **ops:** data-ops

## Skills (29 invocable ผ่าน symlink)

| กลุ่ม | Source | รายการ |
|---|---|---|
| Common DE (10) | `skills/` | adr, data-contract-review, dpia-assessment, incident-runbook, kb-synth, lakehouse-maintenance, npv-appraisal, pipeline-design, spark-tune, table-format-decision |
| AIA (9) | `company/aia/skills/` | databricks-{cost-optimization, genie-governance, observability, serverless-networking, streaming-pattern, uc-governance-sharing}, airflow-databricks-orchestration, de-solution-architecture, kafka-strimzi-cdc |
| Lumora (5) | `lumora/skills/` + `library-framework/skills/` | lumora-{trend-scan, combo-recommend, content-batch, art-prompt}, content-taxonomy |
| Crypto (2) | `crypto-trading/skills/` | crypto-ta-math, risk-management |
| Track B (3) | `neurx/`, `regent-ai/` skills | agent-registry-patterns, agent-policy-engine, audit-trail-design |

## Sandbox projects — สถานะ 2026-07-18 (ดู `projects-knowledge-base/portfolio-review-20260718.md`)

lumora **PIVOT** (90-day content sprint, backend frozen — `sprint-2026-07/`) · crypto-trading **GO-VIABLE** (kill date 2026-08-31) · library-framework **folded → lumora** · neurx **KILLED-as-registry** · regent-ai **PARKED** (career capital + dogfood) · sentientnet **PARKED indefinite**

## Ops

- Session health: doctor รายงานอัตโนมัติ (SessionStart) — แก้ด้วย `_infra/doctor.sh --fix`
- Curation: `company/*/_inbox/YYYYMMDD-topic.md` → `/kb-synth` → `knowledge/` (commit = auto-embed)
- Reindex เต็ม: `_infra/reindex.sh --reset` · MCP config อยู่ `~/.claude.json` (ไม่ใช่ settings.json)
- `_prefix` dir = machine-excluded (ไม่ embed / ไม่ index)
