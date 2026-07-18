# Agent System Redesign — เดิม / ใหม่ / ผสม?

**Date:** 2026-07-18
**Owner:** Sin (Wasin)
**Scope:** ทั้ง 4 layers — subagents (`~/.claude/agents`), skills (3 locations), knowledge (`~/Documents/Projects/Agent/`), infra+memory (Qdrant RAG, MCP, hooks, settings)

---

## 1. Executive Summary — คำตอบตรงๆ

**คำตอบ: ผสม (HYBRID-REDESIGN)** — ไม่ใช่ "แบบเดิมแล้ว patch" และไม่ใช่ "รื้อทำใหม่หมด"

เหตุผลสั้นๆ:

- **โครงสร้างเดิม "ถูกออกแบบดี" แต่ "ตายเพราะ sync manual + ชีวิตเปลี่ยน"** — template ของ agents สม่ำเสมอมาก (34/34 ไฟล์ format เดียวกัน, roles/ mapping 1:1 perfect, zero orphans), skills frontmatter ถูกทุกไฟล์, knowledge คุณภาพสูง แต่ระบบทั้งหมด freeze อยู่ที่ยุค NTT/The-1 ขณะที่ Sin ย้ายไป AIA ตั้งแต่ 2026-07-01
- **อาการหนักสุด 3 อย่าง:**
  1. **Skills งาน AIA ทั้ง 9 ตัว invoke ไม่ได้** — cluster เดียวที่แก้ active (แก้วันนี้ก็มี) ไม่มี symlink ใน `~/.claude/skills`
  2. **RAG index drift 46/439 ไฟล์ (10.5%)** — Track B ทั้งหมด + crypto ADRs + AIA docs ใหม่สุด หายจาก Qdrant เพราะ reindex เป็น manual 100% (docstring อ้าง pre-commit hook ที่ไม่มีอยู่จริง)
  3. **Navigation maps ทั้ง 4 ไฟล์ stale 7 สัปดาห์** — INDEX.md ยังบอก ntt/the_one = "current" และไม่รู้จัก AIA / project_sandbox / skills layer เลย
- **สิ่งที่ต้องเปลี่ยนจริงคือ 2 root causes:** (a) ไม่มี single source of truth (skills มี 3 conventions: symlink / copy / orphan), (b) sync ทุกอย่าง manual ไม่มี feedback loop

**Design ใหม่:** Single-root invariant — `Agent/` tree เป็นเจ้าของทุก byte, `~/.claude/` มีแต่ symlinks + settings + auto-memory; agent fleet ตัดจาก 34 → ~20 ตาม evidence การใช้จริง; RAG เก็บไว้แต่ demote ออกจาก critical path (knowledge.md แบบ fixed-path Read เป็น primary, RAG เป็น enhancement); automation 2 hooks (pre-commit embed + SessionStart doctor)

**Migration:** 6 phases, evening-sized, รวม ~11-14 ชม. แต่ละ phase ship ได้อิสระ — Phase 1 คืนเดียวได้ payoff ใหญ่สุด (AIA skills invoke ได้ทันที)

---

## 2. สถานะปัจจุบัน

### 2.1 Inventory สรุป

| Area | ขนาด | สภาพ | Freshness |
|---|---|---|---|
| **Subagents** | 34 agents / 6 categories / 1,278 lines | Template discipline ดีมาก, roles/ mapping 1:1 perfect | 33/34 ไม่แตะตั้งแต่ Jun 3; databricks-expert (Jul 18) ตัวเดียวที่เป็นยุค AIA |
| **Skills** | 32 unique names ใน 3 locations | Frontmatter ถูกทุกไฟล์, ไม่มี broken symlink | 9 ตัว AIA (active สุด) invoke ไม่ได้; 19 ตัวไม่เคยแก้หลัง scaffold |
| **Knowledge** | 439 .md / ~8MB (+ _infra 942MB) | roles/ ลึกและ opinionated; AIA docs คุณภาพสูงแต่กระจาย 3 ที่ | maps ทั้ง 4 stale ตั้งแต่ 2026-05-30 |
| **Infra/Memory** | Qdrant 6,519 points, 1 MCP server, 0 hooks | Code สะอาด, idempotent incremental design ดี | Index ขาด 46 ไฟล์; settings 642 rules ส่วนใหญ่ซาก NTT |

**Subagents (34):** architect 6, business 8, consultant 5, design 2, engineer 10, ops 3 — ทุกตัว `model: inherit`, RAG-first, read-only advisor contract

**Skills แยกตาม location:**

| Location | จำนวน | สถานะ |
|---|---|---|
| `~/.claude/skills` (ที่เดียวที่ invoke ได้) | 23 = 15 symlinks + 8 real dirs | 4 real dirs เป็น orphan ไม่มี source ใน Agent tree |
| `Agent/skills` (common DE) | 10 | symlink ครบ, zero drift |
| `Agent/company/**/skills` (per-project) | 18 SKILL.md | **9 ตัว data-ml-ai-pipeline (AIA) ไม่มี link → invoke ไม่ได้** |

**Knowledge tree:** company/ntt = 4.8MB frozen archive (269 ไฟล์, mislabeled "current"), company/AIA = 1 ไฟล์ (!), ตัวจริงของงาน AIA อยู่ผิดที่ใน project_sandbox/data-ml-ai-pipeline (68 ไฟล์ รวม knowledge_chat 41 ไฟล์ uncurated), Track B scaffolds 4 โปรเจกต์

**Infra:** Qdrant local (BAAI/bge-large-en-v1.5, H2 chunking), FastMCP stdio server ใน `~/.claude.json`, venv 834MB torch pinned 2.2.2 (Intel Mac ceiling), qdrant_storage ไม่มี backup, **hooks = 0**

### 2.2 ปัญหาที่เจอ (ranked)

| # | ปัญหา | Severity | Area |
|---|---|---|---|
| 1 | 9 AIA skills ไม่มี symlink → Skill tool มองไม่เห็น cluster เดียวที่ active | **Critical** | skills |
| 2 | RAG index drift 46/439 ไฟล์ — Track B ทั้งหมด, crypto ADRs, AIA docs ใหม่สุด หายเงียบๆ | **Critical** | infra |
| 3 | Phantom automation — docstring อ้าง pre-commit hook, ของจริงไม่มี hook ใดๆ ในระบบ | **Critical** | infra |
| 4 | AIA context กระจาย 3 ที่ (company/AIA 1 ไฟล์, data-ml-ai-pipeline, auto-memory) — QUICKSTART procedure สำหรับงานใหม่ถูก skip ทั้งหมด | High | knowledge |
| 5 | 27/34 agents มี stale boilerplate `company_filter="ntt"`; 0/34 พูดถึง AIA; 0/34 รู้จัก Kafka/Strimzi/Debezium (งานประจำวัน) | High | agents |
| 6 | Maps ทั้ง 4 (INDEX, QUICKSTART, company/INDEX, roles/INDEX) stale — ชี้ทางผิด precisely ในจุดที่ active สุด | High | knowledge |
| 7 | Mirror mechanism 3 แบบพร้อมกัน: 15 symlinks / 4 byte-copies (drift-prone) / 4 orphans ไม่มี source | High | skills |
| 8 | knowledge_chat 41 ไฟล์ raw dump ไม่อยู่ใน SKIP_DIRS — `--reset` ครั้งหน้าจะ flood RAG ด้วย chat dumps + ntt archive 1.9MB | High | knowledge+infra |
| 9 | azure-expert frame เป็น "SCB retrospective" ทั้งที่ Azure คือ primary stack ของนายจ้างปัจจุบัน; ไม่มี kafka/streaming expert | Med-High | agents |
| 10 | SPOF chain: Docker Desktop → agent-qdrant → venv pinned; 34 agents พึ่ง RAG ใน critical path | Medium | infra |
| 11 | Dead weight: enterprise-architect, aws-expert, business-analyst≈system-analyst dupe, sales/marketing consultant The-1-shaped; 10 common skills + 4 Track-B skills แบบ batch-scaffold ไม่เคยแก้ | Medium | agents+skills |
| 12 | settings.json 642 allow rules (ซาก NTT) + 25 additionalDirectories ส่วนใหญ่ legacy | Medium | infra |
| 13 | Git ตามหลัง working state: kb_synth.py, socratic-lab, 5 AIA skill files uncommitted; `~/.claude` ไม่มี version control เลย | Medium | infra |
| 14 | Hygiene: `de-databirck-aws/` (typo + wrong-cloud superseded doc), `00_overview 2.md`, Declaration form.pdf ใน KB, 6 empty skills dirs, saymu-oracle ซ้ำกับ lumora-* | Low | all |

**Diagnosis รวม:** โครงสร้าง per-se ไม่ได้พัง — มันแค่ (a) ไม่มี invariant ว่าไฟล์จริงอยู่ที่ไหน และ (b) พึ่ง discipline ของคนคนเดียวที่มี full-time job แทนที่จะพึ่ง automation งานเปลี่ยน 1 ครั้งเลยทำให้ทั้งระบบ stale พร้อมกันหมด

---

## 3. Design ที่แนะนำ

### 3.1 The Invariant (กติกาข้อเดียวที่ต้องจำ)

> **`~/Documents/Projects/Agent/` (git repo เดิม + private remote) เป็นเจ้าของทุก byte ที่ author เอง
> `~/.claude/` (git init ใหม่) มีแค่ symlinks + settings + CLAUDE.md + auto-memory
> ไฟล์จริงใดๆ ใน `~/.claude/{skills,agents}` = bug ที่ doctor ต้องรายงาน**

### 3.2 Target tree

```
~/Documents/Projects/Agent/
├── INDEX.md                # ≤60 บรรทัด, ACTIVE only; 1 บรรทัดชี้ _archive/README.md
├── QUICKSTART.md           # ≤10 บรรทัด: new-engagement procedure (ใช้ company/_template)
├── roles/<cat>/<role>/     # ~20 roles; ATOMIC UNIT: {agent.md, knowledge.md} คู่กัน
├── skills/                 # cross-project: adr, kb-synth, spark-tune, table-format-decision,
│                           # pipeline-design, data-contract-review, incident-runbook,
│                           # lakehouse-maintenance, dpia-assessment, npv-appraisal
├── company/
│   ├── aia/                # lowercase; ดูด data-ml-ai-pipeline เข้ามาทั้งก้อน
│   │   ├── CLAUDE.md       # role, Azure-not-AWS guard, workstreams, skill list
│   │   ├── INDEX.md
│   │   ├── knowledge/      # curated: knowledge/ เดิม + aia/ teaching docs
│   │   ├── skills/         # 9 ตัว: databricks-*, kafka-strimzi-cdc, airflow, de-solution
│   │   └── _inbox/         # ex-knowledge_chat; ชื่อไฟล์ YYYYMMDD-topic.md; ไม่ embed
│   ├── _template/          # rename จาก new_company
│   └── project_sandbox/{lumora, crypto-trading, library-framework, neurx,
│                         regent-ai, sentientnet, projects-knowledge-base}/
│                           # crypto-trading/skills/ รับ crypto-ta-math + risk-management
├── _infra/                 # embed_knowledge.py, mcp_server.py, reindex.sh, kb_synth.py,
│                           # doctor.sh, hooks/{pre-commit, session-start.sh}, docker-compose
└── _archive/               # git-versioned cold storage; EXCLUDED จาก RAG/skills/INDEX
    ├── README.md           # อะไร/ทำไม/วิธี resurrect (git mv กลับ + relink)
    └── company/{ntt/, scb/, de-databirck-aws/}, roles/, skills/, pipelines/, socratic-lab/

~/.claude/   (git init; .gitignore: projects/* ยกเว้น */memory/)
├── CLAUDE.md               # rewrite ~40 บรรทัด; มีบรรทัด "Current engagement: aia"
├── settings.json           # prune เหลือ ~40 rules, 2-3 additionalDirectories, SessionStart hook
├── agents/<cat>/<name>.md  → symlink → Agent/roles/<cat>/<name>/agent.md  (มี gate test ก่อน)
├── skills/<name>           → symlink only (~24 links)
└── projects/*/memory/      # auto-memory — ไม่แตะ
```

### 3.3 Source-of-truth + sync table

| Asset | Source of truth | ~/.claude | Sync mechanism |
|---|---|---|---|
| Agent prompts | `roles/<cat>/<role>/agent.md` | symlink | ไม่ต้อง sync |
| Skills | Agent tree (common หรือ per-company/project) | symlink | ไม่ต้อง sync |
| Role knowledge | colocated `knowledge.md` ข้าง agent.md | — | agent Read fixed path |
| Curated knowledge | `company/*/knowledge/` | — | pre-commit hook → Qdrant |
| Raw dumps | `company/*/_inbox/` | — | kb-synth promote → dump ย้าย `_inbox/processed/` |
| Memory | auto-memory (native) | native | ไม่เปลี่ยน |
| Qdrant index | derived, disposable, ไม่ backup | — | rebuild ได้ด้วย `reindex.sh --reset` |

### 3.4 Sync: ตัดทิ้งที่ตัดได้, automate ที่เหลือ

1. **Symlinks ฆ่า sync ของ skills/agents ทิ้ง** — แก้ไฟล์ใน tree = แก้ของจริง; doctor เช็คว่า `~/.claude/{skills,agents}` ไม่มี non-symlink
2. **pre-commit hook (~15 บรรทัด)** — staged `Agent/**/*.md` นอก SKIP list → `reindex.sh --files ...` — commit = embed (ทำ hook ที่ docstring โม้ไว้ให้เป็นจริงสักที)
3. **SessionStart hook → `_infra/doctor.sh` (~30 บรรทัด)** — เช็ค Qdrant healthz, disk-vs-index diff, broken/non-symlink, uncommitted .md count, INDEX เก่ากว่า content ล่าสุดไหม → พิมพ์บรรทัดเดียว: `KB OK (≈90 files)` หรือ `DRIFT: ... — run doctor --fix`
4. **`SKIP_DIRS += {_archive, _inbox, archive, knowledge_base_legacy, memory, bak_mem, _template}`** แล้ว `--reset` 1 ครั้ง → curated index สะอาด ~90 ไฟล์ (จาก 439 ปนขยะ)

### 3.5 RAG policy: เก็บไว้ แต่เอาออกจาก critical path

Template ใหม่ของทุก agent (sed fleet-wide แทน The-1 boilerplate):

1. `Read Agent/roles/<cat>/<self>/knowledge.md ก่อนเสมอ (fixed path — ทำงานได้ offline, ไม่พึ่ง Docker)`
2. `Engagement context: Read Agent/company/<current engagement ตาม ~/.claude/CLAUDE.md>/CLAUDE.md`
3. `ถ้า agent-knowledge MCP available → search เพิ่มด้วย company_filter=<active engagement>; ถ้าไม่ → ทำงานต่อได้เลย`

Qdrant/Docker/torch stack อยู่ต่อในฐานะ optional cache — **checkpoint +3 เดือน:** ถ้า doctor แสดงว่า RAG แดง/ไม่ถูกใช้ทั้ง quarter → decommission (tar `_infra`, `docker compose down`, ลบ mcpServers entry) โดยไม่มีอะไร break

### 3.6 Agent fleet: 34 → ~20

**Keep (20):** databricks-expert, azure-expert (rewrite เป็น AIA-primary), **kafka-streaming-expert (ใหม่** — สร้างจาก kafka-strimzi-cdc reference/ + aia teaching docs ตาม template ของ databricks-expert), governance-consultant, data-architect, solution-architect, ai-architect (+บรรทัด bridge ไป Track-B skills), platform-architect (re-anchor), de-engineer (re-anchor: CDC/Strimzi, ตัด Beam rules), ai-engineer, software-engineer, devops-engineer, security-engineer, data-analyst (+WebFetch), data-ops, ui-designer, ux-designer, content-strategist (saymu→lumora), ai-art-director (saymu→lumora), finance-consultant, **analyst** (merge business-analyst + system-analyst; +WebFetch)

**Archive (13, ย้าย role dir ทั้งก้อน agent+knowledge):** enterprise-architect, aws-expert, gcp-expert, blockchain-architect, blockchain-consultant, ml-engineer, frontend-engineer, marketing-consultant, sales-consultant, investment-consultant, data-domain-expert, business-analyst, system-analyst

**กติกา template:** agent ที่มี sibling skills ต้อง list ชื่อ skills (ตาม pattern databricks-expert); read-only advisor = convention ยอมรับว่า Bash เขียนไฟล์ได้ (soft restriction); เติม `roles/technical/design/INDEX.md` ที่หายไป

### 3.7 Skills

- **ย้าย:** adr, kb-synth (+`kb_synth.py` เข้า `scripts/`) → `Agent/skills/`; crypto-ta-math, risk-management → `crypto-trading/skills/`; 4 copies (Track-B + content-taxonomy) → เปลี่ยนเป็น symlinks; 9 AIA skills → `company/aia/skills/` + symlink global ทั้งหมด (ไม่ทำ cwd-scoped)
- **ลบ:** saymu-oracle (fold เข้า lumora-content-batch), 6 empty skills dirs
- **Archive:** user-story-gen (ซ้ำ analyst), deployment-checklist (ml-engineer archived); dpia-assessment + npv-appraisal อยู่ต่อ (unique static coverage)
- **กติกา:** description ≤3 บรรทัด; body >150 บรรทัด split เข้า `reference/` (kafka-strimzi-cdc คือ model — สองตัว 20KB+ ค่อย split ตอนแตะครั้งหน้า ไม่ทำระหว่าง migration); ตัด "STARTER" markers

### 3.8 Naming rules

lowercase-kebab ทุกที่; ห้าม space / ` 2` copies; `_underscore` prefix = machine-excluded (ไม่ embed/link/index — กฎเดียวแก้ทั้ง knowledge_chat pollution และ archive-indexing); inbox = `YYYYMMDD-topic.md`; knowledge unit = `topic-name.md` ไม่ใส่วันที่ (git คือ timeline); ADR = `NNNN-title.md`; ทุก active dir มี CLAUDE.md + INDEX.md + knowledge/ พอดี

### 3.9 สิ่งที่ "เหมือนเดิม" ชัดๆ

L1 workspaces ไม่แตะ; auto-memory ไม่แตะ; invocation habits ทั้งหมดเหมือนเดิม (ชื่อ agents, ชื่อ skills, `/kb-synth`); global-CLAUDE.md convention เดิม (rewrite แค่เนื้อหา); RAG code ไม่แก้ (config-only); crypto ADR discipline + lumora v3 skills คงไว้; kb-synth เป็น curation path เดียว (socratic-lab → archive, ปิด decision)

---

## 4. ทางเลือกที่พิจารณาแล้วไม่เลือก

### Proposal 1 — "Conservative: เก็บเกือบหมด + เติม automation"
Keep 31 agents / 28 skills, แก้ boilerplate, เติม 2 hooks, migrate แบบ phased
- **เอามา:** phased evening-sized migration (ตรง lifestyle คนมี full-time job — git history ของ Sin เองแสดง multi-day uncommitted stretches), evergreen boilerplate, doctor hook
- **ไม่เอา:** ขนาด fleet — ~90% ของ roles ไม่ถูกแตะตั้งแต่ Jun 6 (*ก่อน* เปลี่ยนงาน) แปลว่า sprawl ไม่ใช่ผลของ drift แต่คือของที่ไม่เคยถูกใช้; เก็บ sales/marketing/blockchain/enterprise ไว้ trace ไปหา need ที่ observe จริงไม่ได้

### Proposal 2 — "Radical: ลบ RAG, 13 agents, cwd-scoped skills"
Git-everything, ลบ Qdrant stack ทิ้ง, ตัดเหลือ 13 agents, skills ตาม cwd
- **เอามา:** git-init `~/.claude` (ก่อนหน้านี้ agents 34 ตัว + orphan skills ไม่มี version control เลย), insight ว่า "index ที่เน่าเงียบๆ แย่กว่าไม่มี index"
- **ไม่เอา:** ลบ RAG ขัด traceability — ปัญหาที่ observe คือ *silent drift* + *SPOF ใน critical path* ไม่ใช่ตัว vector search; ขัด decision ที่ Sin บันทึกไว้เอง ("Agent KB = Azure KBaaS pattern; keep local") + use case past-experience KB (NTT/SCB retrospective) + Track B dogfooding; cwd-scoped skills สร้าง silent failure mode ใหม่ (ผิด cwd = ไม่มี skills) ทั้งที่ global symlinks พิสูจน์แล้วว่า work; 13 agents ตัด static-but-unique coverage ที่ต้นทุนแทบศูนย์

### Proposal 3 — "Restructure: single-root + evidence-pruned + weekend migration"
โครงเดียวกับ final design แต่ migrate รวดเดียว weekend เดียว, agents ยัง RAG-first
- **เอามา:** เกือบทั้ง skeleton — kept/archived split audit ได้จาก git activity; colocate `agent.md`+`knowledge.md` = atomic unit ฆ่า drift class ของ 1:1 mapping; `_underscore` = machine-excluded
- **ไม่เอา:** "one weekend sitting" คือแผนที่เสี่ยง stall กลางทางที่สุดสำหรับ solo operator; และการให้ 34 prompts พึ่ง Docker ใน critical path — แก้โดย invert template ให้ knowledge.md เป็น primary, RAG เป็น optional

---

## 5. Migration Plan — 6 phases, evening-sized (~11-14 ชม. รวม)

Hard ordering: 0→1→2→3→4 (index reset ต้องมาหลัง moves ทั้งหมด) Phase 5-6 ลากตามได้เป็นสัปดาห์ — hooks ใน Phase 4 หยุด drift ใหม่แล้ว Rollback ต่อ phase = `git revert`; symlinks ย้อนได้ trivially

### Phase 0 — Safety net (30 นาที คืนนี้)

```bash
cd ~/Documents/Projects
git add -A && git commit -m "checkpoint: pre-redesign (kb_synth, socratic-lab, AIA skills, knowledge docs)"
# สร้าง private GitHub remote แล้ว push
gh repo create <private-repo> --private --source . --push

cd ~/.claude
git init
git add CLAUDE.md settings.json agents skills
git commit -m "baseline: 34 agents + 23 skills entries ก่อน redesign"
printf 'projects/*\n!projects/*/memory/\n' > .gitignore
```
ถึงจุดนี้: ไม่มีอะไรหายได้อีกแล้ว (orphan skills 4 ตัว + agents 34 ตัวเข้า git ครั้งแรก)

### Phase 1 — AIA promotion (1 evening — ทำก่อน, pain relief สูงสุด)

```bash
cd ~/Documents/Projects/Agent
# rename ผ่านชื่อชั่วคราว (APFS case-insensitive)
git mv company/AIA company/aia_tmp && git mv company/aia_tmp company/aia

PS=company/project_sandbox/data-ml-ai-pipeline
git mv $PS/skills company/aia/skills
mkdir -p company/aia/knowledge
git mv $PS/knowledge/* $PS/aia/* company/aia/knowledge/
git mv $PS/knowledge_chat company/aia/_inbox
# rename ไฟล์ชื่อมี space → YYYYMMDD-topic.md; .py + scripts/ → _inbox/scripts/

git mv $PS/de-databirck-aws _archive/company/   # (สร้าง _archive ก่อนถ้ายัง)
mv "company/aia/knowledge/Declaration form.pdf" ~/Documents/   # เอาออกจาก KB

# แก้ aia-new-job.md frontmatter: AWS+Airflow → Azure
# เขียน company/aia/CLAUDE.md + INDEX.md (จาก aia-new-job.md + auto-memory)

for s in ~/Documents/Projects/Agent/company/aia/skills/*/; do
  ln -s "$s" ~/.claude/skills/$(basename "$s")
done
```
**Payoff วันนี้เลย: 9 AIA skills invoke ได้** — commit ทั้ง 2 repos

### Phase 2 — Skills unification (1 ชม.)

```bash
A=~/Documents/Projects/Agent
# orphans กลับบ้าน
git -C $A mv ... # crypto-ta-math, risk-management → company/project_sandbox/crypto-trading/skills/
mv ~/.claude/skills/adr $A/skills/adr
mv ~/.claude/skills/kb-synth $A/skills/kb-synth
mkdir $A/skills/kb-synth/scripts && git -C $A mv _infra/kb_synth.py skills/kb-synth/scripts/
# symlink กลับทุกตัว

# 4 copies → symlinks (diff ก่อน — วันนี้ byte-identical)
for s in agent-policy-engine agent-registry-patterns audit-trail-design content-taxonomy; do
  diff -r ~/.claude/skills/$s <source-in-tree>/$s && rm -rf ~/.claude/skills/$s \
    && ln -s <source-in-tree>/$s ~/.claude/skills/$s
done

rm ~/.claude/skills/saymu-oracle   # fold pillar เข้า lumora-content-batch ก่อนลบ source
# archive: user-story-gen, deployment-checklist; ตัด STARTER markers

# verify: ต้องว่าง
find ~/.claude/skills -mindepth 1 -maxdepth 1 ! -type l
```

### Phase 3 — Archive sweep + hygiene (1 ชม.)

```bash
cd ~/Documents/Projects/Agent
mkdir -p _archive/company _archive/roles _archive/skills
git mv company/ntt company/scb pipelines _infra/socratic-lab _archive/...
# เขียน _archive/README.md (what/why/resurrect = git mv กลับ + relink)
git mv company/new_company company/_template
rm "company/project_sandbox/lumora/knowledge/00_overview 2.md"
rmdir _reviews   # (หลังย้ายเอกสารนี้ไปที่ที่ควรอยู่) + 6 empty skills dirs
git commit -m "archive sweep: ntt/scb/pipelines/socratic-lab; template rename; hygiene"
```

### Phase 4 — Automation (1-2 ชม.)

```bash
# 1) embed_knowledge.py: SKIP_DIRS += {_archive, _inbox, archive, knowledge_base_legacy,
#    memory, bak_mem, _template}
# 2) เขียน _infra/hooks/pre-commit (staged Agent/**/*.md ลบ SKIP → reindex.sh --files)
ln -s ../../_infra/hooks/pre-commit ~/Documents/Projects/.git/hooks/pre-commit
# 3) เขียน _infra/doctor.sh; ผูก SessionStart hook ผ่าน /update-config skill
# 4) แก้ _infra/README.md (mcpServers อยู่ ~/.claude.json ไม่ใช่ settings.json; upsert note)
# 5) rebuild index สะอาด
_infra/reindex.sh --reset          # ปล่อยรัน unattended; เช็ค point count ≈ curated corpus
# 6) prune settings.json (ใช้ fewer-permission-prompts skill) + additionalDirectories → 2-3
```
Doctor ต้องรายงาน 0 drift หลัง phase นี้

### Phase 5 — Fleet (2-3 evenings — งาน judgment, ลากตามได้)

- **Gate ก่อน:** symlink agent เดียว (เช่น data-ops.md → tree) แล้ว verify ว่า Claude Code list/spawn ได้ — ถ้า fail: agents อยู่เป็นไฟล์จริงใน `~/.claude/agents` (ตอนนี้ git-versioned แล้ว = SoT ที่นั่น ไม่มี sync problem) แล้ว colocate เฉพาะ knowledge.md
- ถ้า pass: ย้าย kept agents → `roles/<cat>/<name>/agent.md` + symlink กลับ; `git mv` 13 retired role dirs (agent+knowledge คู่กัน) → `_archive/roles/`
- Scripted sed sweep: The-1 filter boilerplate → evergreen 3-line block; saymu→lumora; +WebFetch ให้ 4 ตัวที่ขาด
- Rewrite azure-expert (AIA-primary); เขียน kafka-streaming-expert; merge analysts → analyst.md; re-anchor de-engineer/platform-architect; +Track-B skill lines ใน ai-architect; +design/INDEX.md

### Phase 6 — Maps (30 นาที)

- Regenerate `Agent/INDEX.md` (≤60 บรรทัด, ACTIVE only)
- Rewrite `~/.claude/CLAUDE.md` (~40 บรรทัด, มี **"Current engagement: aia"** — เปลี่ยนงานครั้งหน้า = แก้บรรทัดเดียว)
- QUICKSTART → 10 บรรทัด (procedure ใช้ `company/_template`)
- Commit + push ทั้ง 2 repos

### Ongoing

- Weekly ~30 นาที: kb-synth pass ทับ `company/aia/_inbox`
- Calendar note +3 เดือน: review doctor history → keep หรือ decommission Qdrant

---

## 6. Appendix — Full Inventory

### A. Subagents (34 ไฟล์, 1,278 บรรทัด, `~/.claude/agents/`)

ทุกตัว: `model: inherit`, RAG-first (`role_filter=<ตัวเอง>`), fallback ไป `roles/.../knowledge.md`, ปิดด้วย "Your final response IS the deliverable" — **R** = Read, Glob, Grep + RAG×2; WS = WebSearch, WF = WebFetch

| Agent | Cat | Lines | Tools นอกจาก R | Notes | Verdict |
|---|---|---|---|---|---|
| ai-architect | architect | 39 | WS, WF | ntt filter stale | Keep (+Track-B skill bridge) |
| blockchain-architect | architect | 35 | WS, WF | generic filter | Archive |
| data-architect | architect | 41 | WS, WF | เขียนดีสุดใน architect (de-biased จาก The-1) | Keep |
| enterprise-architect | architect | 37 | WS, WF | org-scale framing, ไม่มี org | Archive |
| platform-architect | architect | 38 | WS, WF | stale "The-1/Beam → project CLAUDE.md" | Keep (re-anchor) |
| solution-architect | architect | 39 | WS, WF | ntt filter | Keep |
| blockchain-consultant | business | 34 | WS, WF | คู่สะอาดกับ blockchain-architect | Archive |
| business-analyst | business | 38 | WS | near-dupe ของ system-analyst | Merge → analyst |
| content-strategist | business | 36 | WS, WF | ยังเรียก saymu-creator (rename → Lumora) | Keep (fix name) |
| data-domain-expert | business | 36 | WS | anchor The-1 loyalty (stale) | Archive |
| finance-consultant | business | 37 | WS, WF | — | Keep |
| investment-consultant | business | 37 | WS, WF | overlap npv-appraisal skill | Archive |
| marketing-consultant | business | 37 | WS, WF | The-1-shaped loyalty framing | Archive |
| sales-consultant | business | 37 | WS, WF | B2B2C loyalty framing | Archive |
| aws-expert | consultant | 38 | Bash, WS, WF | ไม่มี AWS ใน portfolio ปัจจุบัน | Archive |
| azure-expert | consultant | 38 | Bash, WS, WF | frame เป็น SCB retrospective — ผิดยุค | Keep (**rewrite AIA-primary**) |
| databricks-expert | consultant | 49 | Bash, WS, WF | ตัวเดียวยุค AIA (Jul 18); list 8 skills; template ต้นแบบ | Keep |
| gcp-expert | consultant | 39 | Bash, WS, WF | hard-code The-1 Beam rules | Archive |
| governance-consultant | consultant | 38 | WS, WF | PDPA/BoT/SEC — ยัง relevant (AIA=insurance) | Keep |
| ui-designer | design | 34 | WS, WF | — | Keep |
| ux-designer | design | 35 | WS, WF | DevEx/platform-UX เข้ากับ Track B | Keep |
| ai-art-director | engineer | 37 | Bash, WS, WF | ยังเรียก saymu-creator; core Lumora | Keep (fix name) |
| ai-engineer | engineer | 39 | Bash, WS, WF | ไม่ mention sibling agent-* skills | Keep |
| data-analyst | engineer | 38 | Bash, WS (no WF) | tool combo แปลก | Keep (+WF) |
| de-engineer | engineer | 39 | Bash, WS, WF | The-1 Beam conventions เป็น current | Keep (re-anchor CDC/Strimzi) |
| devops-engineer | engineer | 36 | Bash, WS, WF | — | Keep |
| frontend-engineer | engineer | 34 | Bash, WS, WF | — | Archive |
| ml-engineer | engineer | 38 | Bash, WS, WF | — | Archive |
| security-engineer | engineer | 37 | Bash, WS, WF | boundary สะอาดกับ governance | Keep |
| software-engineer | engineer | 38 | Bash, WS, WF | — | Keep |
| system-analyst | engineer | 37 | WS | near-dupe ของ business-analyst | Merge → analyst |
| data-ops | ops | 38 | Bash, WS, WF | — | Keep |
| ml-ops | ops | 38 | Bash, WS, WF | — | Archive (ตาม ml-engineer) |
| platform-ops | ops | 37 | Bash, WS, WF | FinOps angle เข้ากับงาน cost AIA | Keep/fold เข้า data-ops |
| *(ใหม่)* kafka-streaming-expert | consultant | — | Bash, WS, WF | จาก kafka-strimzi-cdc + aia docs | **สร้างใหม่** |

Stats: stale ntt filter 27/34 · AIA mentions 0/34 · Kafka/Strimzi mentions 0/34 · last modified: 33 ไฟล์ ≤ Jun 3, databricks-expert Jul 18

### B. Skills (32 unique names)

**`~/.claude/skills` (23 entries — ที่เดียวที่ invoke ได้):**

| Skill | Type | Source of truth | Project | Modified | Verdict |
|---|---|---|---|---|---|
| adr | real dir | orphan | common | Jun 03 | ย้าย → Agent/skills + link |
| agent-policy-engine | copy | regent-ai (identical) | Track B | Jun 27 | copy → symlink |
| agent-registry-patterns | copy | neurx (identical) | Track B | Jun 27 | copy → symlink |
| audit-trail-design | copy | regent-ai (identical) | Track B | Jun 27 | copy → symlink |
| content-taxonomy | copy | library-framework (identical) | Track A | Jun 27 | copy → symlink |
| crypto-ta-math | real dir | orphan | crypto | Jun 07 | ย้าย → crypto-trading/skills + link |
| kb-synth | real dir | orphan (code ใน _infra) | Agent infra | Jul 15 | ย้าย → Agent/skills + link |
| risk-management | real dir | orphan | crypto | Jun 07 | ย้าย → crypto-trading/skills + link |
| 10 common (data-contract-review, deployment-checklist, dpia-assessment, incident-runbook, lakehouse-maintenance, npv-appraisal, pipeline-design, spark-tune, table-format-decision, user-story-gen) | symlinks | Agent/skills | common | Jun 04 | Keep 8; archive user-story-gen, deployment-checklist |
| 5 lumora (lumora-art-prompt, -combo-recommend, -content-batch, -trend-scan, saymu-oracle) | symlinks | lumora/skills | Track A | Jun 04 | Keep 4; ลบ saymu-oracle |

**data-ml-ai-pipeline (9 — ไม่มี link, cluster ที่ active สุด):**

| Skill | Lines/KB | Modified | Notes |
|---|---|---|---|
| databricks-uc-governance-sharing | 453 / 27.5KB | Jul 18 (git M) | body ใหญ่เกิน — split reference/ ตอนแตะครั้งหน้า |
| databricks-genie-governance | 278 / 19.5KB | Jul 18 (untracked) | คุณภาพสูง, trap-focused triggers |
| databricks-cost-optimization | 265 / 17.3KB | Jul 18 (git M) | ตัด "STARTER" prefix |
| de-solution-architecture | 199 / 22.9KB | Jul 13 | body ใหญ่ — split ทีหลัง |
| databricks-observability | 169 / 12.3KB | Jul 18 (untracked) | workstream deferred แต่ skill มีแล้ว |
| databricks-streaming-pattern | 164 / 8.8KB | Jun 30 | STARTER จริง |
| databricks-serverless-networking | 158 / 11.1KB | Jul 18 (untracked) | คู่กับ UC-sharing |
| airflow-databricks-orchestration | 110 / 6.5KB | Jun 30 | MWAA angle อาจ stale (AIA = Azure) |
| kafka-strimzi-cdc | 87 / 8.2KB + reference/ ×3 | Jul 02 | โครงสร้างดีสุด — เป็น model |

อื่นๆ: library-framework 1 (content-taxonomy), neurx 1, regent-ai 2 — ทั้งหมด duplicated ไม่ใช่ symlink; empty skills dirs 6 (AIA, new_company, ntt, scb, crypto-trading, sentientnet)

### C. Knowledge tree (439 .md ไม่รวม _infra, ~8MB)

| Path | ไฟล์/ขนาด | CLAUDE/INDEX | Status |
|---|---|---|---|
| INDEX.md, QUICKSTART.md, company/INDEX, roles/INDEX | 4 maps | — | ทั้งหมด stale 2026-05-30 |
| roles/ (34 roles) | 760KB | design/ ไม่มี INDEX | คุณภาพสูง, ~90% frozen ก่อน Jun 6 |
| company/AIA | 1 ไฟล์ 8.6KB | ไม่มีทั้งคู่ | งานปัจจุบัน — KB บางสุด; frontmatter ยังบอก AWS |
| company/ntt/the_one | 269 ไฟล์ / 4.8MB | มี (May 30) | archive mislabeled "current"; archive/+legacy 1.9MB |
| company/scb/datax | 5 ไฟล์ / 73KB | มี | archive ถูก label, refresh Jun 30 |
| company/new_company | 2 placeholder | มี | rename → _template |
| ps/data-ml-ai-pipeline | 68 ไฟล์ | ไม่มีทั้งคู่ | **ศูนย์กลางจริงของงาน AIA** — knowledge 6, knowledge_chat 41, skills 9, aia/ 6, agents/ 1, de-databirck-aws/ 2 |
| ps/lumora | 9 + skills | มี (Jun 4) | dormant ~6 wks; มี `00_overview 2.md` dup |
| ps/crypto-trading | 10 ADRs + INDEX | มี (Jun 7) | ADR discipline ดีเยี่ยม; skills/ ว่าง |
| ps/{library-framework, neurx, regent-ai, sentientnet} | 2-3 ต่อโปรเจกต์ | มี (Jun 27) | scaffolded, vision-stage |
| ps/projects-knowledge-base | 2 | ไม่มี | predates AIA corrections |
| pipelines/ | 1 sample playbook | มี | dead — archive |
| _reviews/ | ว่าง | — | ลบ |

### D. Infra + Memory

| Component | รายละเอียด | Condition |
|---|---|---|
| Qdrant | collection `agent_knowledge`, 6,519 points, green, up 4 days, storage 108MB (gitignored, no backup) | **ขาด 46/439 ไฟล์ (10.5%)**: Track B ทั้งหมด, crypto ADRs ×10, AIA docs Jul 17-18, lumora dup; stale 0 |
| embed_knowledge.py | 6.7K, Jun 1 — H2 chunk, bge-large-en-v1.5 1024-dim, per-file delete-then-upsert (idempotent) | ดี แต่ docstring อ้าง pre-commit hook ที่ไม่มี; SKIP_DIRS ไม่ครอบ knowledge_chat/archive |
| mcp_server.py | 5.3K, Jun 6 — FastMCP stdio, 3 tools | solid; config อยู่ `~/.claude.json` (README ชี้ผิดว่า settings.json) |
| .venv | 834MB, torch pinned 2.2.2 (Intel Mac ceiling) | fragile — upgrade/เปลี่ยนเครื่อง = rebuild |
| kb_synth.py + socratic-lab | Jul 15, untracked | curation paths 2 ทาง — ปิด decision: ใช้ kb-synth, archive socratic-lab |
| Hooks | **0** | เพิ่ม pre-commit + SessionStart doctor |
| settings.json | 642 allow rules (ซาก NTT), 0 deny, 25 additionalDirectories (ส่วนใหญ่ legacy) | prune → ~40 rules, 2-3 dirs |
| Auto-memory (current) | MEMORY.md + 11 topic files, ล่าสุด Jul 18 | Healthy — ไม่แตะ |
| Legacy memory (The-1) | 3 copies: legacy stores 47, bak_mem 63, ntt KB | read-only archive — ยอมรับ, note ใน INDEX |

### E. เป้าหมายหลัง migration (นับเลข)

| Metric | ก่อน | หลัง |
|---|---|---|
| Agents active | 34 (27 stale boilerplate, 0 AIA-aware) | ~20 (evergreen template, AIA-first, +kafka expert) |
| Skills invocable | 23 (0 จาก AIA cluster) | ~24 (รวม AIA 9 ตัว), symlink 100% |
| Skill sync conventions | 3 (symlink/copy/orphan) | 1 (symlink only + doctor enforce) |
| RAG index | 393/439 ไฟล์ ปน archive+chat dumps | ~90 curated files, hook-driven, doctor-checked |
| Hooks | 0 | 2 (pre-commit embed, SessionStart doctor) |
| Navigation maps | 4 ไฟล์ stale 7 สัปดาห์ | INDEX ≤60 บรรทัด + staleness nag ใน doctor |
| Version control | Agent repo ตามหลัง; ~/.claude ไม่มี git | 2 repos, private remote, ทุก authored byte tracked |
| เปลี่ยนงานครั้งหน้า | แก้ 27+ agents + maps + settings | แก้ 1 บรรทัด ("Current engagement:") + copy _template |
