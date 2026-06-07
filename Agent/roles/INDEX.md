# Roles — Knowledge Index

Deep knowledge files per role. Paired with subagents in `~/.claude/agents/`.

## Structure

```
roles/
├── technical/
│   ├── architect/          (design + governance)
│   ├── engineer/           (build + discuss + implement)
│   ├── consultant/         (cloud + domain experts to consult)
│   └── ops/                (operate + maintain)
└── business/               (BA, domain experts, stakeholders)
```

## How this pairs with subagents

- **Subagent** (`~/.claude/agents/<category>/<role>.md`) = the agent persona spawned via Agent tool. Lightweight system prompt + tool restriction.
- **Knowledge file** (`~/Documents/Projects/Agent/roles/<category>/<role>/knowledge.md`) = deep reference loaded by the subagent when it needs to dig deeper.

## Index

### Technical / Architect
- [data-architect](technical/architect/data-architect/)
- [solution-architect](technical/architect/solution-architect/)
- [platform-architect](technical/architect/platform-architect/)
- [enterprise-architect](technical/architect/enterprise-architect/)
- [ai-architect](technical/architect/ai-architect/)

### Technical / Engineer
- [de-engineer](technical/engineer/de-engineer/)
- [ml-engineer](technical/engineer/ml-engineer/)
- [ai-engineer](technical/engineer/ai-engineer/)
- [devops-engineer](technical/engineer/devops-engineer/)
- [software-engineer](technical/engineer/software-engineer/)
- [data-analyst](technical/engineer/data-analyst/)
- [system-analyst](technical/engineer/system-analyst/)

### Technical / Consultant
- [gcp-expert](technical/consultant/gcp-expert/)
- [aws-expert](technical/consultant/aws-expert/)
- [azure-expert](technical/consultant/azure-expert/)
- [governance-consultant](technical/consultant/governance-consultant/)

### Technical / Ops
- [data-ops](technical/ops/data-ops/)
- [ml-ops](technical/ops/ml-ops/)
- [platform-ops](technical/ops/platform-ops/)

### Business
- [business-analyst](business/business-analyst/)
- [data-domain-expert](business/data-domain-expert/)

## Convention

Each role folder contains:
```
<role>/
├── knowledge.md         ← deep reference (main file)
├── decision_framework.md (optional)
└── references.md         (optional)
```

Start with `knowledge.md` as a single file; split when it gets large.
