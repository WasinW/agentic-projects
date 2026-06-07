# Quickstart — How to Use This Setup

> Read this once. Then refer to it when you forget something.

---

## The 30-second mental model

```
You work in:        ~/Documents/Projects/Project/<company>/<project>/   (code + docs)
Claude reads:       ~/.claude/CLAUDE.md                        (global)
                    ~/Documents/Projects/Agent/INDEX.md                 (directory)
                    ~/Documents/Projects/Agent/company/<...>/CLAUDE.md  (project context)
You spawn agents:   ~/.claude/agents/<category>/<role>.md      (18 roles ready)
Deep knowledge:     ~/Documents/Projects/Agent/roles/<...>/knowledge.md (write as you go)
```

---

## Day-to-day usage

### Starting a session on The-1 work

```bash
cd ~/Documents/Projects/Project/ntt/the_one/
claude
```

Claude will automatically:
- Load `~/.claude/CLAUDE.md` (global)
- Load `~/Documents/Projects/Project/ntt/the_one/CLAUDE.md` (workspace pointer)
- Know about `~/Documents/Projects/Agent/` and the subagents

### Invoking a role-based agent

In the conversation, say:
> "ลอง data-architect review architecture นี้หน่อย"
> หรือ
> "Get gcp-expert opinion on Dataflow vs Dataproc"

Claude (main) will then call:
```
Agent({subagent_type: "data-architect", prompt: "..."})
```

Available subagents:
- **Architects**: `data-architect`, `solution-architect`, `platform-architect`, `enterprise-architect`, `ai-architect`
- **Engineers**: `de-engineer`, `ml-engineer`, `ai-engineer`, `devops-engineer`, `software-engineer`, `data-analyst`, `system-analyst`
- **Consultants**: `gcp-expert`, `aws-expert`, `azure-expert`, `governance-consultant`
- **Ops**: `data-ops`, `ml-ops`, `platform-ops`
- **Business**: `business-analyst`, `data-domain-expert`

### Multi-agent workflows

For complex tasks needing several roles:
- See `~/Documents/Projects/Agent/pipelines/playbooks/` for recipes (e.g., `design_new_pipeline.md`).
- Write your own playbook when you find yourself repeating a multi-agent sequence.

---

## When you start your next role

1. Rename `~/Documents/Projects/Project/new_company/` → actual company name.
2. Rename `~/Documents/Projects/Agent/company/new_company/` → actual company name.
3. Fill in `~/Documents/Projects/Agent/company/<new>/CLAUDE.md` with company-specific conventions.
4. Update `~/Documents/Projects/Agent/INDEX.md` and `~/Documents/Projects/Agent/company/INDEX.md`.
5. Capture knowledge in `~/Documents/Projects/Agent/company/<new>/knowledge/` as you go.

The Project/ folder is for code, the Agent/company/<new>/ folder is for context.
**Don't mix the two.**

---

## When to populate knowledge files

| File | When |
|---|---|
| `Agent/roles/<...>/knowledge.md` | When you learn something role-generic worth keeping. Lean toward writing — future-you will thank you. |
| `Agent/company/<...>/knowledge/` | When you learn something project-specific. Especially capture domain semantics, non-obvious patterns, and historical decisions. |
| `Agent/company/<...>/memory/` | For facts that should auto-load each session (user preferences, project quirks, ongoing decisions). |
| `Agent/pipelines/playbooks/` | When you repeat a multi-agent flow >2 times. |

---

## Migrating from the legacy setup

Old memory + workspace are preserved at:
- `~/Documents/ntt_project/the_one/` (old workspace)
- `~/.claude/projects/-Users-wasin-Documents-ntt-project-*/` (old memory stores)

They will still load if you open Claude in the old path. No need to delete.

To gradually migrate The-1 content:
1. Copy `~/Documents/ntt_project/the_one/learning/data_platform/` → consider where it fits:
   - Role-generic deep dives → `~/Documents/Projects/Agent/roles/<role>/knowledge.md`
   - The-1 specific → `~/Documents/Projects/Agent/company/ntt/the_one/knowledge/`
2. Copy legacy memory KBs (loyalty, insight, sales) → `Agent/company/ntt/the_one/knowledge/domains_*.md`.
3. Copy feedback rules → `Agent/company/ntt/the_one/memory/`.

See `~/Documents/Projects/Agent/company/ntt/the_one/INDEX.md` for the recommended migration list.

---

## What NOT to do

- **Don't put code under `~/Documents/Projects/Agent/`** — that's for knowledge + context.
- **Don't put context docs under `~/Documents/Projects/Project/`** — that's for active code + docs you're authoring.
- **Don't edit subagent files lightly** — they affect every session. Test first.
- **Don't migrate old patterns blindly into new companies** — each engagement has its own constraints.
- **Don't delete legacy paths** until you're certain you've moved what matters.

---

## Settings to consider next

- **Add allowed bash commands** to `~/.claude/settings.json` to reduce permission prompts (e.g., `gh pr view`, `gsutil ls`).
- **Add user-level skills** in `~/.claude/skills/` for repeated tasks (e.g., "deploy-dataform", "run-eval-suite").
- **Customize keybindings** in `~/.claude/keybindings.json` if you have ergonomic preferences.

---

## Inventory

```
Created in this setup:
~/.claude/
  ├── CLAUDE.md                  (global instructions)
  └── agents/                    (18 subagents)
      ├── architect/ (5)
      ├── engineer/  (7)
      ├── consultant/(4)
      ├── ops/       (3)
      └── business/  (2)

~/Documents/
  ├── Project/                   (3 workspaces — code goes here)
  │   ├── ntt/the_one/CLAUDE.md
  │   ├── scb/datax/CLAUDE.md
  │   └── new_company/CLAUDE.md
  └── Agent/                     (knowledge + orchestration)
      ├── INDEX.md
      ├── QUICKSTART.md          (this file)
      ├── company/               (3 projects scaffolded)
      ├── roles/                 (18 role knowledge.md placeholders + 5 INDEX.md)
      └── pipelines/             (1 sample playbook)
```

Total new files: ~50, total cost: zero of the legacy stuff was touched.
