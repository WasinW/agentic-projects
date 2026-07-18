# NTT / The-1 — Knowledge Index

## Project files

- [CLAUDE.md](CLAUDE.md) — agent instructions for this project
- [memory/](memory/) — facts that persist across sessions
- [knowledge/](knowledge/) — domain knowledge (write as you go)
- [skills/](skills/) — project-specific skills (optional)

## Knowledge files to populate (suggested)

```
knowledge/
├── architecture.md         — system architecture, components, data flow
├── domains.md              — loyalty, insight, sale, catalog, message, partner
├── conventions.md          — naming, folder, code style, deploy
├── framework.md            — Beam config-driven framework (step registry)
├── tech_stack.md           — versions, services, configs
├── compliance.md           — PDPA, BoT, audit requirements
├── pending_discussions.md  — open architectural debates
├── pain_points.md          — known issues + workarounds
└── glossary.md             — domain terms (member, partner, sku, etc.)
```

## Migration from legacy (old memory)

Old memory at `~/.claude/projects/-Users-wasin-Documents-ntt-project-the-one-realproject/` contains 42 files. Decide which to migrate:

**High-value candidates to copy → here:**
- `loyalty_knowledge_base.md` → `knowledge/domains_loyalty.md`
- `insight_knowledge_base.md` → `knowledge/domains_insight.md`
- `sales_knowledge_base.md` + `sales_pipeline_knowledge_base.md` → `knowledge/domains_sale.md`
- `catalog_products_knowledge_base.md` → `knowledge/domains_catalog.md`
- `common_data_knowledge_base.md` → `knowledge/common_data.md`
- `foundry_svoc_knowledge_base.md` → `knowledge/foundry_svoc.md`
- `loyalty_insights_knowledge_base.md` (from `the_one` variant) → `knowledge/domains_loyalty_insights.md`
- `kafka_schema_changes.md` → `knowledge/kafka_schemas.md`
- `mistakes_and_rules.md` → `knowledge/mistakes_and_rules.md`
- `dofns_comparison.md` → `knowledge/dofns_comparison.md`
- `agent_system_setup.md` → `knowledge/agent_setup_old.md` (reference)
- `feedback_*.md` → `memory/feedback_*.md` (preserve as-is)
- `project_*.md` → `memory/project_*.md` (preserve as-is)
- `reference_cost_labeling.md` → `knowledge/cost_labeling.md`

**Do later (when relevant comes up):**
- All `transactions_*` files (5 files)
- `sales_schema_migration*` files (3 files)
- Domain-specific deployment notes

## Sources to also pull from (legacy workspace)

- `~/Documents/ntt_project/the_one/learning/data_platform/` — comprehensive blueprint docs (33 files from prior sessions)
- `~/Documents/ntt_project/the_one/realproject/the1-re-data-platform/` — main repo docs (most complete)
- `~/Documents/ntt_project/the_one/gcp-data-platform/` — reference template
- `~/Documents/ntt_project/the_one/the1-replatform/` — legacy / older version
- `~/Documents/ntt_project/the_one/realproject/{loyalty,insight,sale,message,catalog,partner}/` — per-domain docs

## Default subagents for this project

When invoking via `Agent({subagent_type: ...})`:
- `data-architect` — system design
- `de-engineer` — Beam / Dataflow / BigQuery
- `gcp-expert` — GCP-specific
- `ml-engineer` — Vertex AI workflows
- `ai-engineer` — GenAI / RAG (if working on AI features)
- `data-ops` — pipeline reliability, monitoring
