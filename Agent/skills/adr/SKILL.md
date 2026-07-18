---
name: adr
description: Capture an Architecture Decision Record (ADR) — a single, dated, numbered decision with context, options considered, the choice, and consequences. Use during architecture/platform consultations to record "why we chose X over Y" so the reasoning survives. Trigger when a decision is reached (cloud, storage format, layering, data contract, tooling) or the user says "เก็บเป็น ADR" / "record this decision".
---

# adr

Capture one architecture decision as a lightweight ADR (Michael Nygard format, trimmed). One decision = one file. Keep it short — an ADR is a record, not a design doc.

## When to use

- A consultation reaches a real decision (cloud, lakehouse vs warehouse, table format, layering, data contract style, orchestration tool, batch vs streaming).
- User says "เก็บเป็น ADR", "record this", "ลงบันทึกการตัดสินใจ".
- NOT for trivial choices or things still under debate (use status `Proposed` if not yet final).

## Where ADRs live

Default: `docs/adr/` under the current platform/project working directory. Create the folder if missing. Filename: `NNNN-kebab-title.md` (zero-padded, sequential). Find the next number by listing existing files; start at `0001`.

If the user works under the Agent workspace for a specific company/project, prefer `~/Documents/Projects/Project/<company>/<sub_project>/docs/adr/` — ask only if ambiguous.

## Inputs

- **title** — the decision in a few words ("Use Iceberg as table format")
- **context** — what forces the decision (requirements, constraints, the problem)
- **options** — the alternatives weighed (at least the chosen one + 1 rejected)
- **decision** — what was chosen
- **status** — `Proposed` | `Accepted` | `Superseded by NNNN` (default `Accepted`)

If any are missing, infer from the conversation; only ask when genuinely unclear.

## Template

```markdown
# NNNN. <Title>

- Status: <Accepted | Proposed | Superseded by NNNN>
- Date: <YYYY-MM-DD>
- Deciders: <who — e.g. Wasin + data-architect>
- Tags: <e.g. storage, cloud, governance>

## Context
<The forces at play: requirements, constraints, the problem being solved. 2-5 sentences.>

## Options considered
- **<Option A (chosen)>** — pros / cons
- **<Option B>** — pros / cons
- **<Option C>** — pros / cons (if any)

## Decision
<What was chosen, stated plainly.>

## Consequences
- <Positive: what this enables>
- <Negative / cost: what we accept or must mitigate>
- <Follow-ups / things this blocks or unblocks>

## Related
- Links to other ADRs (e.g. `[[0002-...]]`), tickets, or docs.
```

## Steps

1. Determine the target `docs/adr/` dir; find the next `NNNN`.
2. Fill the template from the conversation. Use today's date from session context — do NOT call a date function.
3. Write the file. Keep Context + Decision tight; Consequences is the part people read later — be honest about the cost/trade-off, not just upside.
4. Reply with the path and a one-line summary. If it supersedes an earlier ADR, update that ADR's Status to `Superseded by NNNN`.

## Notes

- One decision per file. If a session produces several decisions, write several ADRs.
- ADRs are immutable once Accepted — to change a decision, write a new ADR that supersedes it rather than editing the old one.
- Keep a running `docs/adr/README.md` index (one line per ADR: number, title, status) if it exists; create it on the first ADR.
