# Session Bootstrap Prompt Template

Use this prompt at the start of each project-specific Claude Code session. Replace `{PROJECT_NAME}` with one of:

- `Lumora`
- `Library Framework`
- `Crypto Trading Engine`
- `NeurX`
- `Regent AI`
- `SentientNet`

---

## 📋 The Prompt (paste into Claude Code)

```
Bootstrap session — focused on project: {PROJECT_NAME}

## Step 1 — Read in this order (full read, not skim):

1. /Users/wasin/Documents/projects/Project/project_sandbox/projects-knowledge-base/01-projects-master-knowledge.md
   (Master context — all 6 projects + portfolio strategy + locked decisions + cross-project connections)

2. ~/Documents/Projects/Agent/INDEX.md
   (Personal KB entry point — agents available, skills available, playbooks available)

3. ~/Documents/Projects/Agent/company/project_sandbox/{project_folder}/memory/  (ถ้ามี)
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
- Mode for this project (apply consistently):
  • Lumora / Library Framework → builder + business strategist mindset, not DE/pipeline.
  • Crypto Trading Engine → builder/product, not DE/pipeline.
  • NeurX / Regent / SentientNet → architect + product strategist, reframed for agentic era.
- Communication: Thai-English mix is fine, peer-level intellectual tone, no instructional framing.
- Push back if I'm wrong. Honest reality checks > polite agreement.

Begin with Step 1.
```

---

## 🎯 Per-Project Variant Notes

Each project has slightly different routing. Add these notes to the prompt if useful:

> Subagent names below are real `subagent_type` values (all COMMON, in ~/.claude/agents).
> Skills tagged **[specific]** live in the project's own `skills/`; the rest are common (in ~/.claude/skills).

### Lumora
- Subagents to lean on: `content-strategist`, `marketing-consultant`, `software-engineer`, `ai-engineer`, `enterprise-architect` (strategy)
- Skills: `lumora-*` (combo-recommend/content-batch/trend-scan/art-prompt/saymu-oracle) **[specific, exist]**
- Watch out: don't draw it as SaaS, it's agency/MCN.

### Library Framework
- Subagents: `solution-architect`, `content-strategist`, `enterprise-architect`, `business-analyst`
- Skills: `content-taxonomy` **[specific, to create]**, `agent-workflow-design` (common, to create)
- Key question to revisit early: is this a separate product or internal IP?

### Crypto Trading Engine
- Subagents: `solution-architect` (one-time), `software-engineer` (lead), `data-analyst`, `investment-consultant`
- Skills: `crypto-ta-math`, `risk-management` **[specific, exist]**
- Later phase: `ml-engineer`, `frontend-engineer`, `ui-designer`, `ux-designer`
- Critical: NOT a data-engineering project. NOT a product. Personal builder tool.

### NeurX
- Subagents: `ai-architect`, `platform-architect`, `ai-engineer`, `solution-architect`, `enterprise-architect`, `security-engineer`
- Skills: `agent-registry-patterns` **[specific, to create]**; `agent-protocol-design`, `mcp-integration` (common, to create)
- Critical: agent-centric, not model-centric. Old vision is dead.

### Regent AI
- Subagents: `governance-consultant`, `security-engineer`, `ai-architect`, `ai-engineer`, `solution-architect`
- Skills: `agent-policy-engine`, `audit-trail-design` **[specific, to create]**; `ai-regulation-knowledge` (common, to create); `dpia-assessment` (common, exists)
- Critical: agent autonomy & liability, not model explainability.

### SentientNet
- Subagents: `blockchain-architect`, `blockchain-consultant`, `enterprise-architect`, `ai-architect`, `governance-consultant`
- Skills: `decentralized-systems`, `agent-federation`, `sovereignty-frameworks` **[specific, later]**
- Critical: this is vision-stage. Don't try to build, try to clarify position + roadmap.

---

## ⚙️ Path Setup (one-time)

Suggested folder structure for the master knowledge file:

```
~/Documents/projects/Project/project_sandbox/projects-knowledge-base/
├── 01-projects-master-knowledge.md   ← drop the master doc here
└── 02-session-bootstrap-prompt.md    ← drop this prompt template here
```

Then each project lives at its own session-scoped folder + KB folder:

```
Per-project working dir (VS Code):
~/Documents/projects/Project/project_sandbox/{project_name}/

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
