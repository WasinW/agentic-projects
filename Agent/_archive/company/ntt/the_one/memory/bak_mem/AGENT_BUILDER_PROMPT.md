# Agent Builder Session — Opening Prompt
**Copy prompt ด้านล่างนี้ไปเปิด session ใหม่สำหรับสร้าง multi-agent system**

---

## Pre-requisites
- Memory ถูก export ไว้แล้วที่ `the1-re-data-platform/agent/bak_mem/loyalty/` (15 files)
- ทุก session share memory เดียวกัน (working dir เดียวกัน) → ไฟล์ใน bak_mem เป็น master copy แล้ว ไม่ต้อง export เพิ่ม
- Session นี้ควรเปิดที่ working directory: `/Users/wasin/Documents/ntt_project/the_one/realproject/`

---

## Prompt (Copy ทั้งหมดด้านล่างนี้)

```
# Multi-Agent System Builder

## Context
ผมเป็น Data Engineer / Tech Lead ดูแล data platform ของ The1
ปัจจุบันผมใช้ Claude Code หลาย session แยกตาม domain แต่ทุก session share auto-memory เดียวกัน (เพราะ working dir เดียวกัน)
ผมต้องการสร้าง multi-agent system ที่ให้ agent เหล่านี้ทำงานร่วมกัน consult กัน ถกเถียงกัน และ implement ได้

## Working Style ของผม
- สั้น กระชับ ลงมือทำ — ไม่ต้องอธิบายยาว
- อ่าน code/docs จริงก่อนพูด อย่าเดา — verify ก่อนตอบเสมอ
- ถ้าไม่แน่ใจ → ถามก่อน อย่าแก้ code ทันที
- No git commands (no branch, add, commit, push) จนกว่าผมจะบอก
- Present design ก่อน implement เสมอ
- ทุก Phase ต้องได้ approve ก่อนไป Phase ถัดไป

---

## PHASE 0: Inventory + Clean + Categorise Context

### 0.1 อ่าน Exported Memory (master copy)
อ่านทุกไฟล์ใน:
`/Users/wasin/Documents/ntt_project/the_one/realproject/the1-re-data-platform/agent/bak_mem/loyalty/`

ไฟล์สำคัญ:
| File | เนื้อหา |
|------|---------|
| SESSION_SUMMARY.md | สรุป context ทั้งหมดจาก loyalty session |
| MEMORY.md | Main memory index (338 lines, มี cross-domain content) |
| loyalty_knowledge_base.md | Loyalty KB ครบ — all collectors, infra, schemas |
| mistakes_and_rules.md | Rules + mistakes log (มี sales bugs ปนอยู่ ~25%) |
| sales_knowledge_base.md | Sales domain KB |
| sales_pipeline_knowledge_base.md | Sales pipeline specifics |
| insight_knowledge_base.md | Insight domain KB |
| catalog_products_knowledge_base.md | Catalog/products KB |
| kafka_schema_changes.md | Kafka schema (eligibleTierCode) |
| feedback_verify_before_answer.md | Verification guidelines (generic) |
| dofns_comparison.md | DoFn comparison members vs messaging |
| sales_deploy_fix.md | Sales deploy.py fix |
| sales_initial_data.md | Sales initial data load |
| sales_schema_migration.md | Sales schema migration |
| sales_schema_migration_done.md | Sales migration completion |

### 0.2 Known Cross-Domain Bleeding Issues
| File | ปัญหา | Severity |
|------|--------|----------|
| MEMORY.md | Sales content ~15% (schema migration, deploy fix, checklist ปนใน loyalty) | SEVERE |
| mistakes_and_rules.md | Sales bugs ~25% (Mistake 10-15: managed transform, CDC write, timestamp Z) | SEVERE |
| loyalty_knowledge_base.md | transaction/ domain references ปนอยู่ | MODERATE |
| dofns_comparison.md | messaging/purchases comparison (reference, minor) | MINOR |
| sales_*.md (6 files) | ไฟล์ Sales ทั้งหมดอยู่รวมกับ loyalty | MISPLACED |

### 0.3 Scan Codebase — Domains ที่ Memory ไม่ Cover
Memory มี KB เฉพาะ 4 domains (loyalty, sales, insight, catalog) — **อีก 5 domains ต้อง scan codebase จริง**:

| Domain | Path | Collectors | มี KB? | Action |
|--------|------|------------|--------|--------|
| **loyalty** | `loyalty/loyalty_paralel/loyalty-data/` | members-collector, tiers-collector, members-tiers-history-collector, coupons-collector, purchases-collector, rewards-collector, transactions-collector | YES | Clean only |
| | `loyalty/loyalty_paralel/backward-compatible/` | backward-compatible-collector | Partial (in SESSION_SUMMARY) | Clean only |
| **sale** | `sale/sales-data/sales-collector/` | sales-collector (receipt, sku, tender) | YES | Clean only |
| **insight** | `insight/customer-profile-pipeline/` | customer-profile-pipeline (V3 Hexagonal) | YES | Clean only |
| | `insight/insight-api/data/processor/dataflow/` | V1/V2 batch+realtime pipelines | Partial | Clean only |
| **catalog** | `catalog/catalog-data/products-collector/` | products-collector | YES | Clean only |
| **gamification** | `gamification/gamification-data/` | account-missions-collector, master-collector | **NO KB** | **SCAN + CREATE KB** |
| **message** | `message/messaging-data/` | messages-collector, master-collector | **NO KB, NO bak_mem** | **SCAN + CREATE KB** |
| **partner** | `partner/partner-data/` | master-collector | **NO KB, NO bak_mem** | **SCAN + CREATE KB** |
| **common** | `common/common-data/` | common-python-dataflow, common-python-cloudrun | **NO KB** | **SCAN + CREATE KB** |
| **loyalty-mart** | `loyalty-mart/loyalty-insights/` | loyalty-insights (Dataform/analytics) | Partial (in bak_mem/loyalty-insights/) | Clean only |

**NOTE**: `loyalty/loyalty_paralel/loyalty-data/transactions-collector/` = ไม่ใช่ของเรา ดูแลโดย team อื่น (ใส่ tag ว่า external)
**NOTE**: `loyalty/purchases-data/` = reference collector (อ่านได้ แก้ไม่ได้)
**NOTE**: `loyalty/backup/member-tiers/` = DEPRECATED ไม่ต้อง scan

### 0.4 Task: สร้าง Clean Context
สร้าง directory structure ที่ `the1-re-data-platform/agent/mem_clean_context/`:

```
agent/mem_clean_context/
├── CONTEXT_MAP.md              ← Master index: domain → files → coverage → gaps
│
├── loyalty/
│   ���── knowledge_base.md       ← Loyalty-only content (จาก loyalty_knowledge_base.md, cleaned)
│   ├── mistakes.md             ← Loyalty-specific mistakes only
│   ├── pending_work.md         ← Pending items for loyalty
│   └── kafka_schema.md         ← eligibleTierCode migration
│
├── sales/
│   ├── knowledge_base.md       ← Sales-only content
│   ├── mistakes.md             ← Sales-specific mistakes (Mistake 10-15)
│   ├── pending_work.md         ← Pending items for sales
│   └── schema_migration.md     ← Schema migration summary
│
├── insight/
│   ├── knowledge_base.md       ← Insight-only content
│   └── pending_work.md
│
├── catalog/
│   ├── knowledge_base.md       ← Catalog-only content
│   └���─ pending_work.md
│
├── gamification/
│   ├── knowledge_base.md       ← **NEW** — scan codebase + create
│   └── pending_work.md
│
├── message/
│   ├── knowledge_base.md       ← **NEW** — scan codebase + create
│   └��─ pending_work.md
│
├── partner/
│   ├── knowledge_base.md       ← **NEW** — scan codebase + create
│   └── pending_work.md
│
├── common/
│   ├─��� knowledge_base.md       ← **NEW** — scan shared libraries
│   └── pending_work.md
│
├── loyalty-mart/
│   ├── knowledge_base.md       ← From loyalty-insights bak_mem
│   └── pending_work.md
│
└── shared/
    ├── common_patterns.md      ← Patterns ใช้ข้าม domain:
    │                              - Iceberg/BLMS REST setup
    │                              - BQ Storage Write API + CDC
    │                              - Dataflow deploy pattern
    │                              - Config-driven pipeline pattern
    │                              - Schema evolution
    │                              - Bangkok timezone +7 convention
    ├── common_mistakes.md      ← Mistakes ที่ apply ทุก domain:
    │                              - อ่าน code ก่อนพูด
    │                              - validate ทุกครั้ง (ruff/mypy/pytest/pre-commit)
    ��                              - ดู path ให้ชัด
    │                              - แก้ปัญหาเฉพาะหน้าก่อน
    ├── common_infrastructure.md ← Shared infra:
    │                              - BigLake catalog (common/GCP/biglake-metastore.tf)
    │                              - Common scripts (deploy_dataflow, prepare_*)
    │                              - Common CI templates (.uv_base, .common-sonar-scan)
    │                              - Terraform patterns
    ├── cross_domain_deps.md    ← Dependency map:
    │                              - transaction/ team coordination
    │                              - common-python-dataflow shared by loyalty+sales
    │                              - messaging as reference pattern
    │                              - purchases-collector as reference/read-only
    └── architecture_overview.md ← Platform-wide architecture:
                                   - All domains + data flow
                                   - GCP project mapping
                                   - Layer model (source → refined → public)
```

### 0.5 Rules for Categorisation
- **Domain-specific** content (collector code, domain schema, domain config) → `<domain>/knowledge_base.md`
- **Pattern/practice** ใช้ข้าม domain (BLMS, CDC, deploy) → `shared/common_patterns.md`
- **Mistake/rule** ที่ apply ทุก domain → `shared/common_mistakes.md`
- **Mistake/rule** เฉพาะ domain → `<domain>/mistakes.md`
- **ห้ามทิ้ง content** — ทุกอย่างต้องอยู่ที่ไหนสักที่
- **Cross-reference** ได้ แต่ tag ชัด: `[REF: loyalty pattern]`, `[REF: purchases-collector]`
- **NEW KB** (gamification, message, partner, common): scan pyproject.toml, src/, config/, .gitlab-ci.yml, infrastructure/ → สรุปเป็น KB format เดียวกับ domain อื่น

### 0.6 สร้าง CONTEXT_MAP.md
Index ที่ต้องมี:
- **Domain → files** ที่เกี่ยวข้องใน mem_clean_context/
- **Collector inventory**: ทุก collector ทุก domain + mode + status
- **Coverage assessment**: domain ไหนมี context ลึก/ตื้น/ไม่มี
- **Cross-domain dependencies**: ใครพึ่งใคร
- **Ownership map**: ของเรา vs team อื่น vs reference-only

### 0.7 Present ให้ approve ก่อนไป Phase 1

---

## PHASE 1: Design Agent Architecture (หลัง Phase 0 approved)

### 9 Agents ที่ต้องการ

#### Tier 1: Domain Experts (ดูแล domain-specific collectors/pipelines)
1. **Domain Expert: Loyalty** — members, tiers, m-t-h, coupons, backward-compatible, rewards collectors
2. **Domain Expert: Sales** — sales-collector (receipt, sku, tender)
3. **Domain Expert: Insight** — customer-profile-pipeline, V1/V2/V3 frameworks
4. **Domain Expert: Others** — catalog, partner, gamification, message (รวมกัน หรือแยกตามเหมาะสม — recommend based on Phase 0 findings)

#### Tier 2: Specialized Experts
5. **Data Architecture + Data Platform** — schema design, data modeling, pipeline architecture, Iceberg/BQ patterns
6. **Enterprise Architecture** — cross-domain governance, standards, compliance
7. **Solution Architecture** — end-to-end solution design, technology selection, trade-offs
8. **Expert Cloud Solution Architect** — GCP services (Dataflow, BQ, Iceberg, Cloud Scheduler, IAM, networking)

#### Tier 3: Ops Experts
9. **DevOps + DataOps + Infrastructure** — CI/CD (GitLab), Terraform, deployment, monitoring, Dataflow operations

### Knowledge Assignment
- **Domain agents** → อ่าน `mem_clean_context/<domain>/` + `shared/`
- **Specialized agents** → อ่าน `shared/` + ทุก domain ที่เกี่ยว
- **Ops agents** → อ��าน `shared/` + infra sections จากทุก domain

### Design Tasks
1. เลือก approach (SDK subagents, Agent Teams, Hybrid, .claude/agents/)
2. กำหนด system prompt แต่ละ agent (ใช้ cleaned context เป็น base knowledge)
3. กำหนด tools/permissions แต่ละ agent
4. ออกแบบ inter-agent communication pattern
5. ออกแบบ shared state mechanism (MCP/files/DB)
6. ออกแบบ human approval flow
7. ออกแบบ memory update flow (agent ทำงานเสร็จ → update mem_clean_context/ ยังไง)

### Present design ให้ approve ก่อน���ป Phase 2

---

## PHASE 2: Implement (���ลัง Phase 1 approved)
- สร้าง agent definitions
- Setup MCP if needed
- Test with 2-3 agents first
- Scale to 9 agents

---

## Research Questions (ทำระหว่าง Phase 1)

### MCP for Shared State
- MCP server แบบไหนเหมาะ (filesystem, SQLite, custom)
- Setup ยังไง
- Present เป็น option ให้เลือก

### Vertex AI Integration
- ถ้าจะ design agent system ให้ทำงานกับ Vertex AI Agent Engine ด้วย ทำได้มั้ย
- Claude agents + Vertex AI agents ทำงานร่วมกันยังไง
- Present เป็น option ให้เลือก

### .claude/agents/ Directory
- สามารถใช้ `.claude/agents/*.md` define agent ได้ (markdown-based, persist ข้าม session)
- Research ว่า approach นี้เพียงพอมั้ย หรือต้องใช้ SDK
- ถ้าใช้ .claude/agents/ → สร้าง agent definitions ไว้ที่ไหน (project root vs per-domain)
```

---

## Notes for Opening the Session
- **Working directory**: `/Users/wasin/Documents/ntt_project/the_one/realproject/`
- **Additional directories** (add ใน settings):
  - `/Users/wasin/Documents/ntt_project/the_one/realproject/the1-re-data-platform/doc/`
  - `/Users/wasin/Documents/ntt_project/the_one/realproject/the1-re-data-platform/agent/`
  - `/Users/wasin/.claude/projects/-Users-wasin-Documents-ntt-project-the-one-realproject/memory/`
