# Session Bootstrap Prompt Template

> **Updated 2026-07-18 (portfolio review)** — the portfolio narrowed from 6 projects to **1.5 active workstreams + 1 self-run tool**. Do not spin up sessions for killed/parked projects.

Use this prompt at the start of each project-specific Claude Code session. Replace `{PROJECT_NAME}` with one of the **active** projects (dispositions per `portfolio-review-20260718.md`):

- `Lumora` — **ACTIVE**: 90-day content sprint, backend frozen (the only funded workstream)
- `Crypto Trading Engine` — **ACTIVE but time-boxed**: 1 weekend; kill date 2026-08-31
- `Agent Trust & Governance` — **CAPPED (~4 hrs/month)**: the merged NeurX+Regent, dogfood + career capital only

Killed / parked — **do NOT open a build session for these** (they earn zero hours until their un-park trigger fires, see master doc §2):

- `Library Framework` — FOLDED into Lumora (internal IP, not standalone)
- `NeurX` — KILLED as registry (trust IP absorbed into Agent Trust & Governance)
- `SentientNet` — PARKED indefinite (narrative only)

---

## 📋 The Prompt (paste into Claude Code)

```
Bootstrap session — focused on project: {PROJECT_NAME}

## Step 1 — Read in this order (full read, not skim):

1. /Users/wasin/Documents/Projects/Agent/company/project_sandbox/projects-knowledge-base/01-projects-master-knowledge.md
   (Master context — current verdicts table, revised Track A/B thesis, market-contact rule, hours directive, per-project status)

2. /Users/wasin/Documents/Projects/Agent/company/project_sandbox/projects-knowledge-base/portfolio-review-20260718.md  (§1, §2, §4)
   (The review that produced the current dispositions — read before acting on any portfolio-strategy question)

3. ~/Documents/Projects/Agent/INDEX.md
   (Personal KB entry point — agents available, skills available, playbooks available)

4. ~/Documents/Projects/Agent/company/project_sandbox/{project_folder}/memory/  (ถ้ามี)
   (Project-specific memory if previously created)

## Step 2 — Confirm understanding

After reading, output a short summary (5-10 lines):
- Which project this session is for
- Current status of that project
- Locked decisions you'll respect
- Open questions you're aware of
- Cross-project connections relevant to this work
- Which subagents you plan to delegate to

Then STOP and wait for my next instruction. Don't start work yet.

## Step 3 — Workspace setup (if KB home doesn't exist)

If ~/Documents/Projects/Agent/company/project_sandbox/{project_folder}/ doesn't exist:
- Create it
- Mirror the Lumora layout: memory/ + knowledge/ + skills/
- Add a README.md with project one-liner + link back to master knowledge doc

## Step 4 — Rules of engagement

- This is a project-focused session. Don't pull in work from other projects.
- Use existing subagents in ~/.claude/agents/ (33 across architect/engineer/consultant/ops/business/design — the COMMON consulting layer mirrored in Agent/roles/). They serve ALL projects, not just these 6. Don't create new ones unless there's a clear skill gap.
- If my instruction conflicts with a locked decision in the master doc, FLAG IT before acting. Don't silently override.
- **Market-contact rule (hard):** don't add engineering/docs/KB hours to a project until it completes its next market-facing action (Lumora → publish; Crypto → use it live 1 week; parked projects → none, they stay parked).
- **Don't resurrect killed/parked projects.** NeurX-as-registry, standalone Library Framework, and SentientNet are dead/parked — treat their old vision prose as history, not a backlog. Only touch them if I explicitly ask, or an un-park trigger in master doc §2 has fired.
- **Employer IP boundary (AIA):** never put AIA internals (code/data/schemas/architecture) into public content, repos, or KB. Personal projects on personal time/equipment only.
- **Hours reality:** if I report <6 side-project hrs/week, rescope the Lumora sprint to 3 posts/week rather than letting the target slip silently.
- Mode for this project (apply consistently):
  • Lumora → builder + business strategist mindset, not DE/pipeline; it's an agency/MCN, not SaaS. Sprint mode: publish, don't engineer (backend frozen).
  • Crypto Trading Engine → builder/product, not DE/pipeline; time-boxed to the 2026-08-31 kill date.
  • Agent Trust & Governance (merged NeurX+Regent) → dogfood + career-capital only, capped; no product build.
- Communication: Thai-English mix is fine, peer-level intellectual tone, no instructional framing.
- Push back if I'm wrong. Honest reality checks > polite agreement.

Begin with Step 1.
```

---

## 🎯 Per-Project Variant Notes

Each project has slightly different routing. Add these notes to the prompt if useful:

> Subagent names below are real `subagent_type` values (all COMMON, in ~/.claude/agents).
> Skills tagged **[specific]** live in the project's own `skills/`; the rest are common (in ~/.claude/skills).

### Lumora — ACTIVE (90-day content sprint, backend frozen)
- Subagents to lean on: `content-strategist`, `marketing-consultant`, `ai-engineer` (light); skip `software-engineer`/`enterprise-architect` — no backend work during the sprint.
- Skills: `lumora-*` (combo-recommend/content-batch/trend-scan/art-prompt/saymu-oracle) **[specific, exist]** — these + Claude Code ARE the Phase-1 pipeline.
- Watch out: not SaaS (agency/MCN); publish, don't engineer; AI-label from post #1; no unofficial auto-publisher; ~70/30 human/AI. Gate = 1 post ≥50K views OR 1K followers by day 90.

### Crypto Trading Engine — ACTIVE but time-boxed (kill date 2026-08-31)
- Subagents: `software-engineer` (lead), `data-analyst`, `investment-consultant`
- Skills: `crypto-ta-math`, `risk-management` **[specific, exist]**
- Scope for the one weekend: backtest harness → automate (cron + Telegram) → journal. No dashboard/ML/webhooks.
- Critical: NOT a data-engineering project, NOT a product. If unused by 2026-08-31 → archive.

### Agent Trust & Governance (merged NeurX + Regent) — PARKED / CAPPED (~4 hrs/month)
- Only sanctioned work: **dogfood** — a PreToolUse policy enforcer + hash-chained JSONL audit on Sin's own agent fleet — plus folding lessons back into 2 skills. **No product build.**
- Subagents: `governance-consultant`, `security-engineer`, `ai-engineer` (for the dogfood weekend only)
- Skills: `agent-policy-engine`, `audit-trail-design`, `agent-registry-patterns` **[specific, exist]**; `dpia-assessment` (common, exists)
- Substrate decision: use Cedar/OPA, never invent a DSL. NeurX registry is dead — do not rebuild it. Fix the Art. 12 over-claim wording. Value = career capital at AIA, not a product.

### SentientNet — PARKED indefinite (do not open a build session)
- Narrative only; micropayments pillar deleted; sovereign angle lives in Agent Trust & Governance now.
- No subagents, no skills (the 3 planned skills were phantom — removed). Un-park only if all 3 triggers in master doc §2 fire, and re-research from scratch first.

---

## ⚙️ Path Setup (one-time)

Actual location of the master knowledge files:

```
~/Documents/Projects/Agent/company/project_sandbox/projects-knowledge-base/
├── 01-projects-master-knowledge.md   ← master doc (single source of truth)
├── 02-session-bootstrap-prompt.md    ← this prompt template
└── portfolio-review-20260718.md      ← the 2026-07-18 review (read §1/§2/§4)
```

Then each project lives at its own session-scoped folder + KB folder:

```
Per-project working dir (VS Code):
~/Documents/Projects/Project/project_sandbox/{project_name}/

Per-project KB:
~/Documents/Projects/Agent/company/project_sandbox/{project_name}/
├── memory/
├── knowledge/
└── skills/
```

---

## 🔄 Updating the Master Doc

When any session surfaces a decision or change that affects portfolio-level context, update `01-projects-master-knowledge.md`:
- Bump version date at top.
- Move resolved items from "Open Questions" → "Locked Decisions".
- Add new entries to relevant project section.

Treat the master doc as the **single source of truth** for portfolio strategy. Individual sessions can specialize, but should not contradict it silently.
