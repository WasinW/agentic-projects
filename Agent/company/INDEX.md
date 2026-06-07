# Companies — Index

Project-scoped agent context. One folder per (company, sub-project).

## Active

| Company / Project | Status | Path |
|---|---|---|
| ntt / the_one | current (NTT DATA on-site at The-1) | [ntt/the_one/](ntt/the_one/) |
| scb / datax | archive (previous role) | [scb/datax/](scb/datax/) |
| new_company | placeholder (next role) | [new_company/](new_company/) |

## Per-project folder layout

```
<company>/<sub_project>/
├── CLAUDE.md          ← agent instructions when working on this project
├── INDEX.md           ← project knowledge index
├── memory/            ← facts that persist across sessions
├── knowledge/         ← domain knowledge files (architecture, conventions, ...)
└── skills/            ← project-specific skills (optional)
```

## Convention

- **company name** = parent organization (NTT, SCB, etc.) — capture employer side
- **sub_project** = the actual engagement (the_one = client at NTT, datax = team at SCB)
- One project = one engagement context. Multiple projects per company is fine.
