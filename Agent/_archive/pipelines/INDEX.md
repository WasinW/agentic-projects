# Pipelines / Playbooks — Index

Multi-agent orchestration recipes. When a task needs more than one role to chime in, capture the sequence here.

## Structure

```
pipelines/
├── INDEX.md           ← this file
└── playbooks/
    └── <topic>.md     ← one playbook per recurring multi-agent flow
```

## When to write a playbook

- The same task crosses 3+ subagents and you've done it more than once.
- You want to share a "how we work" recipe with future-you (or a teammate).
- Example: "Design a new pipeline" → solution-architect → de-engineer → governance-consultant → data-ops.

## When NOT to write one

- One-off discussions.
- Single-agent tasks (just spawn that subagent).

## Sample playbook (placeholder)

- [playbooks/design_new_pipeline.md](playbooks/design_new_pipeline.md) — example shape; rewrite when used.

## Convention

Each playbook captures:

```
## Goal
What outcome are we after?

## Agents involved
- agent-1 (role)
- agent-2 (role)
...

## Sequence
1. Spawn agent-1 with prompt X → expect output Y
2. Feed Y to agent-2 → ...
3. Synthesize

## Output
What the final deliverable looks like.

## When to use this vs ad-hoc
Conditions that justify running the full playbook.
```
