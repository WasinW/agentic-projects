# NTT / The-1 — Knowledge Base Index

> Consolidated knowledge from `the1-re-data-platform/doc/` + `agent/` (re-organized by topic).
> Total: 192 knowledge files + 70 memory files.

---

## Quick map

| Section | What's in it |
|---|---|
| [00_overview/](00_overview/) | README, Claude instructions, platform blueprint |
| [01_architecture/](01_architecture/) | System architecture + overall EA |
| [02_ingestion/](02_ingestion/) | Data ingestion patterns (Beam, CDC, streaming) |
| [03_storage/](03_storage/) | Storage layer (BQ, Iceberg, BigLake) |
| [04_processing/](04_processing/) | Transformation + compute layer |
| [05_serving/](05_serving/) | Serving layer (consumer apps, APIs) |
| [06_governance/](06_governance/) | Data governance, lineage, contracts |
| [07_cicd/](07_cicd/) | CI/CD pipelines + automation |
| [08_development/](08_development/) | Development conventions + tooling |
| [09_operations/](09_operations/) | Operations, on-call, monitoring |
| [10_security/](10_security/) | Security, IAM, compliance |
| [components/](components/) | Per-component: dataflow, dataform, monitoring |
| [domains/](domains/) | Per-domain: loyalty, insight, sales, partner, common, etc. |
| [discussions/](discussions/) | Open architectural debates + pending decisions |
| [data_platform_ref/](data_platform_ref/) | Detailed platform reference (architecture, governance, ops, dev) |
| [knowledge_base_legacy/](knowledge_base_legacy/) | Vendor / comparison notes (AWS, Azure, GCP, Databricks) |
| [common_repo/](common_repo/) | Shared library / common-repo conventions |
| [archive/](archive/) | Older content (kept for reference) |
| [scancode/](scancode/) | Scancode-related issues |

---

## Cross-cutting topics (when in doubt)

### Architecture / Design
→ Start: `01_architecture/INSTRUCTIONS.md`, then `00_overview/platform_blueprint.md`

### Data Engineering Lifecycle (which stage?)
- Ingestion → `02_ingestion/`
- Storage → `03_storage/`
- Processing → `04_processing/`
- Serving → `05_serving/`
- Governance → `06_governance/`
- CI/CD → `07_cicd/`
- Development → `08_development/`
- Operations → `09_operations/`
- Security → `10_security/`

### Per-component deep
- Dataflow → `components/dataflow/`
- Dataform → `components/dataform/`
- Monitoring → `components/monitoring/`

### Per-domain
- Loyalty / member tiers → `domains/loyalty-data/`, `domains/_mem_clean/loyalty/`, `domains/_mem_clean/loyalty-mart/`
- Insight / customer profile → `domains/insight/`, `domains/_mem_clean/insight/`
- Sales → `domains/sales-data/`, `domains/_mem_clean/sales/`
- Partner → `domains/partner-data/`, `domains/_mem_clean/partner/`
- Common / shared → `domains/common-data/`, `domains/_mem_clean/common/`, `domains/_mem_clean/shared/`
- Catalog / products → `domains/_mem_clean/catalog/`
- Message → `domains/_mem_clean/message/`
- Gamification → `domains/_mem_clean/gamification/`

### Active discussions / pending decisions
→ `discussions/` and `data_platform_ref/discussion/`

### Vendor / cloud comparison
→ `knowledge_base_legacy/` (GCP, AWS, Azure, Databricks side-by-side)

---

## Memory (different from knowledge)

`../memory/` contains:
- `bak_mem/` — historic memory per domain (sales, loyalty, insight, etc.)
- `data_platform_old/` — older data platform agent context

Memory = facts / rules / preferences that persist across sessions.
Knowledge = reference material to consult while working.

---

## What's NOT in here

The following live outside this folder:

- **Role-generic knowledge** (data architect, ML engineer, etc.) → [`../../../../../roles/`](../../../../../roles/)
- **Other companies** (SCB, future) → `../../../`
- **Workspace code** → `~/Documents/Projects/Project/ntt/the_one/`
- **Legacy raw memory** → `~/.claude/projects/-Users-wasin-Documents-ntt-project-*/`
- **Original source** (untouched archive) → `~/Documents/ntt_project/the_one/realproject/the1-re-data-platform/`

---

## When to update this index

- Adding a new section → add to "Quick map".
- Renaming a section → update both Quick map + cross-cutting links.
- Significant new domain → add to "Per-domain" section.

---

## When to consult this vs role knowledge

| Question | Look in... |
|---|---|
| "How does The-1 specifically handle X?" | This folder (project-scoped) |
| "What's the standard industry practice for X?" | `~/Documents/Projects/Agent/roles/.../knowledge.md` |
| "What's the open discussion about X in our team?" | `discussions/` |
| "What does loyalty domain mean by Y?" | `domains/loyalty-*/` |
| "What rule did we agree on for Z?" | `../memory/` |

Use both. The-1 knowledge is the *specific*, role knowledge is the *generic*.
