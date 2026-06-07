# Agent System — Top Index

> The canonical directory of agent knowledge, project context, and orchestration.
> When in doubt about where something lives, start here.

---

## Layout

```
~/Documents/Projects/Agent/
├── INDEX.md                  ← this file
├── company/                  ← Part 2: project-scoped context
│   ├── INDEX.md
│   ├── ntt/the_one/
│   ├── scb/datax/
│   └── new_company/
├── roles/                    ← Part 3: role-based deep knowledge
│   ├── INDEX.md
│   ├── technical/
│   │   ├── architect/
│   │   ├── engineer/
│   │   ├── consultant/
│   │   └── ops/
│   └── business/
└── pipelines/                ← Part 4: orchestration playbooks
    ├── INDEX.md
    └── playbooks/
```

Subagents live separately in `~/.claude/agents/` (global, spawnable via Agent tool).

---

## Quick links

### Companies / Projects
- [ntt/the_one](company/ntt/the_one/INDEX.md) — The-1 Card data platform (current)
- [scb/datax](company/scb/datax/INDEX.md) — SCB Data-X (archive)
- [new_company](company/new_company/INDEX.md) — placeholder

### Roles (knowledge files)
- [Technical → Architect](roles/technical/architect/INDEX.md)
- [Technical → Engineer](roles/technical/engineer/INDEX.md)
- [Technical → Consultant](roles/technical/consultant/INDEX.md)
- [Technical → Ops](roles/technical/ops/INDEX.md)
- [Business](roles/business/INDEX.md)

### Pipelines
- [Pipelines / Playbooks](pipelines/INDEX.md)

---

## How the system works

### When user opens Claude in a Project directory

```
1. Claude reads ~/.claude/CLAUDE.md      → knows about Agent/ system
2. Claude reads Project/.../CLAUDE.md     → project-specific guidance (if exists)
3. Claude consults Agent/company/<name>/<project>/ for that project's knowledge
4. Claude can spawn subagents from ~/.claude/agents/ for role-based discussions
5. Subagents pull deeper knowledge from Agent/roles/.../knowledge.md
```

### When user invokes a role-based agent

```
User: "ลอง data architect review architecture นี้หน่อย"
   ↓
Claude: Agent({subagent_type: "data-architect", prompt: "...context..."})
   ↓
Subagent (data-architect):
  - Reads ~/Documents/Projects/Agent/roles/technical/architect/data-architect/knowledge.md
  - Reads project context if relevant
  - Returns analysis
```

### Multi-agent orchestration (Part 4)

```
For complex topics, use pipeline playbooks:
   Agent/pipelines/playbooks/<topic>.md
   describes which subagents to invoke + sequence + handoffs
```

---

## Conventions

- **One INDEX.md per level** — every folder has its own to make navigation discoverable.
- **Subagents are roles, not projects** — each subagent represents a function, not a company.
- **Knowledge in roles/ is generic; knowledge in company/ is specific** — don't duplicate, link instead.
- **Companies = real engagements** (where you've worked or will work) — drives memory + project conventions.

---

## Related

- Global instructions: `~/.claude/CLAUDE.md`
- Subagent definitions: `~/.claude/agents/`
- Settings: `~/.claude/settings.json`
- Legacy memory (archive): `~/.claude/projects/-Users-wasin-Documents-ntt-project-*/`
- Legacy workspace (archive): `~/Documents/ntt_project/the_one/`
