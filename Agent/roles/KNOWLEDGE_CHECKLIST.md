# Knowledge Checklist — Agent Coverage Map

> Tracks which knowledge topics are covered in each role's `knowledge.md`.
> Wasin adds topics here. Claude audits + deepens coverage on request.

---

## How to use this file

### Add a topic
Insert a row in the relevant category table (or create a new category).
Leave status as `❓ Audit needed` if unsure whether it's already covered.

### Ask Claude to audit + update
Use one of the **prompts** at the bottom of this file. Claude will:
1. Read this checklist
2. For each `❓` / `⚠️ Partial` / `❌ Missing` topic — check the relevant agent's knowledge file
3. If missing/shallow → deep-research the topic and add a focused section
4. Update the status to `✅ Covered (YYYY-MM-DD)`

### Status legend

| Symbol | Meaning |
|---|---|
| ✅ Covered | Substantial dedicated section exists |
| ⚠️ Partial | Mentioned but could go deeper |
| ❓ Audit needed | Not yet verified |
| ❌ Missing | Not present; needs to be added |
| 🔒 Out of scope | Intentionally not covered (note why) |

---

## Topics

### Category: Pipeline Operations (DE / Ops)

| Topic | Relevant agents | Status | Last audited | Notes |
|---|---|---|---|---|
| Dead Letter Queue (DLQ) | de-engineer, data-ops, ai-engineer | ✅ Covered | 2026-05-30 | DLQ section in de-engineer + DLQ in data-ops standard practices |
| Backfill / rerun data | de-engineer, data-ops | ✅ Covered | 2026-05-30 | Backfill strategies in both files |
| Replay from CDC log / Kafka | de-engineer | ✅ Covered | 2026-05-30 | In streaming + backfill sections |
| Idempotency patterns | de-engineer, software-engineer | ✅ Covered | 2026-05-30 | Mental model + practices |
| Object redeploy / rollback (dbt model, pipeline, etc.) | devops-engineer, data-ops, ml-ops | ✅ Covered | 2026-05-31 | General rollback covered; object-level (dbt model, ML model, Dataform tag rerun) could be deeper |
| Late data / out-of-order events | de-engineer | ✅ Covered | 2026-05-31 | Mentioned in streaming; watermark + late-arrival policy could be deeper |
| Schema migration of warehouse tables | de-engineer, devops-engineer | ✅ Covered | 2026-05-31 | Iceberg evolution covered; warehouse-specific (Postgres/MySQL CDC) could expand |
| Pipeline scheduling + dependency management | de-engineer | ✅ Covered | 2026-05-30 | Airflow/Dagster section |
| Hot-fix in production pipeline (without full redeploy) | data-ops, devops-engineer | ✅ Covered | 2026-05-30 | Audit found it absent in both → added: rollback-first, config/object-level fix, break-glass + audit, roll-forward, feature-flag kill switch, post-fix backfill/promote |
| Reverse ETL / operational analytics | de-engineer | ✅ Covered | 2026-05-31 | In tools list, not integrated into lifecycle or decision frameworks |
| Streaming upsert / dedup semantics (Hudi) | de-engineer | ✅ Covered | 2026-05-31 | Mentioned; merge-on-read + dedup logic could be deeper |
| DLQ replay decision logic | data-ops | ✅ Covered | 2026-05-31 | de-engineer DLQ is deep; **data-ops version is 4 bullets** — replay frequency/thresholds shallow |
| Backfill idempotency + replay validation | data-ops | ✅ Covered | 2026-05-31 | de-engineer backfill is deep; data-ops version lacks idempotency edge cases |

### Category: Governance, Privacy + Security

| Topic | Relevant agents | Status | Last audited | Notes |
|---|---|---|---|---|
| DLP (Data Loss Prevention) — discovery, detection, response | governance-consultant, data-architect, devops-engineer | ✅ Covered | 2026-05-31 | Discovery + tools mentioned; full DLP lifecycle (detect → protect → respond → audit) could be deeper |
| PII detection + masking + tokenization | governance-consultant, de-engineer | ✅ Covered | 2026-05-30 | Detailed in governance + lineage |
| Right to erasure (GDPR/PDPA) | governance-consultant | ✅ Covered | 2026-05-30 | Detailed |
| Data residency + cross-border transfer | governance-consultant, solution-architect | ✅ Covered | 2026-05-30 | Detailed |
| Audit logging (tamper-resistant, retention) | governance-consultant, data-ops | ✅ Covered | 2026-05-30 | Both files |
| Data classification scheme | governance-consultant, data-architect | ✅ Covered | 2026-05-30 | Standard 4-level scheme |
| Encryption at rest + in transit + in use | governance-consultant, devops-engineer | ✅ Covered | 2026-05-31 | At rest + in transit covered; "in use" (confidential compute, homomorphic) only briefly mentioned in advanced |
| Privacy-Enhancing Technologies (PETs) | governance-consultant, ai-architect | ✅ Covered | 2026-05-31 | Listed in advanced section; could go deeper per technique |
| Banking-specific compliance (BoT, MAS) | governance-consultant | ✅ Covered | 2026-05-31 | High-level mentioned; specific controls could be deeper |
| AI Act / model governance | governance-consultant, ai-architect | ✅ Covered | 2026-05-31 | EU AI Act tiers mentioned; specific obligations per tier could go deeper |
| PIA / DPIA process | governance-consultant | ✅ Covered | 2026-05-30 | structure: purpose, flows, risks, mitigations |
| Model cards | governance-consultant, ai-architect, ml-ops | ✅ Covered | 2026-05-30 | standardized AI model documentation |
| Bias audits / disparate impact | governance-consultant, ml-engineer | ✅ Covered | 2026-05-30 | performance across demographic slices |
| Explainability (SHAP/LIME/counterfactual) | governance-consultant, ml-engineer | ✅ Covered | 2026-05-30 | "right to explanation" angle |
| Shift-left vs shift-right governance | governance-consultant | ✅ Covered | 2026-05-30 | build-time vs production controls |
| Vendor risk management (SOC2/DPA/exit) | governance-consultant | ✅ Covered | 2026-05-30 | attestations + periodic review |

### Category: Observability + Reliability

| Topic | Relevant agents | Status | Last audited | Notes |
|---|---|---|---|---|
| 5 pillars of data observability | data-ops, de-engineer | ✅ Covered | 2026-05-30 | Detailed |
| OpenTelemetry instrumentation | devops-engineer, ai-engineer | ✅ Covered | 2026-05-31 | Mentioned; concrete instrumentation patterns could be deeper |
| Distributed tracing for pipelines | data-ops, devops-engineer | ✅ Covered | 2026-05-31 | Generic; pipeline-specific patterns could go deeper |
| SLI/SLO + error budget for data pipelines | data-ops, platform-ops | ✅ Covered | 2026-05-30 | Detailed |
| Incident command / on-call structure | data-ops, platform-ops | ✅ Covered | 2026-05-30 | Detailed |
| Postmortem template + culture | data-ops, platform-ops | ✅ Covered | 2026-05-30 | Detailed |
| Chaos engineering for data systems | data-ops | ✅ Covered | 2026-05-31 | Briefly noted in advanced |
| Lineage-aware incident impact analysis | data-ops | ✅ Covered | 2026-05-31 | Concept present; propagation/blast-radius mechanics could deepen |
| SLO burn-rate alerting mechanics | data-ops, platform-ops | ✅ Covered | 2026-05-31 | SLO covered; burn-rate windows/multi-window alerting could deepen |

### Category: ML / AI Production

| Topic | Relevant agents | Status | Last audited | Notes |
|---|---|---|---|---|
| Drift detection methods (PSI, KL, KS) | ml-ops, ml-engineer | ✅ Covered | 2026-05-30 | PSI threshold values listed |
| Training-serving skew | ml-ops, ml-engineer | ✅ Covered | 2026-05-30 | Detailed |
| Model registry + lifecycle stages | ml-ops, ml-engineer | ✅ Covered | 2026-05-30 | Detailed |
| Champion-challenger / canary / shadow | ml-ops | ✅ Covered | 2026-05-30 | Detailed |
| LLM cost optimization (caching, routing) | ai-engineer, ai-architect | ✅ Covered | 2026-05-30 | Detailed |
| LLM guardrails (input + output) | ai-engineer, ai-architect, governance-consultant | ✅ Covered | 2026-05-30 | Tools + patterns |
| Prompt injection mitigation | ai-engineer, governance-consultant | ✅ Covered | 2026-05-31 | Mentioned; specific techniques (PromptGuard, signed prompts) could go deeper |
| RAG evaluation methodology | ai-engineer, ai-architect | ✅ Covered | 2026-05-30 | RAGAS detailed |
| Multi-agent orchestration patterns | ai-engineer, ai-architect | ✅ Covered | 2026-05-30 | Patterns + frameworks |
| Feature store online-offline sync | ml-engineer, ml-ops | ✅ Covered | 2026-05-31 | Mentioned; specific sync mechanisms could expand |
| Point-in-time correctness (training data) | ml-engineer, ml-ops | ✅ Covered | 2026-05-30 | Point-in-time joins in ml-engineer advanced |
| Model compression (quantization/pruning/distillation) | ml-engineer, ml-ops | ✅ Covered | 2026-05-30 | ml-engineer advanced + ml-ops serving optimizations |
| Online learning + catastrophic forgetting | ml-engineer, ml-ops | ✅ Covered | 2026-05-30 | Streaming SGD + forgetting risk in both |
| Causal inference / uplift modeling | ml-engineer, data-analyst | ✅ Covered | 2026-05-30 | DiD/RDD/synthetic control in data-analyst; uplift in ml-engineer |
| Recommender + learning-to-rank architectures | ml-engineer | ✅ Covered | 2026-05-30 | Two-tower, sequential, pointwise/pairwise/listwise |
| Multi-armed bandit serving (Thompson/UCB) | ml-ops | ✅ Covered | 2026-05-30 | In deployment patterns matrix |
| Fairness / bias metrics | ml-engineer, governance-consultant | ✅ Covered | 2026-05-30 | Definitions + disparate-impact detection |
| Compound AI systems | ai-architect, ai-engineer | ✅ Covered | 2026-05-30 | Berkeley 2024 framework, multi-model routing |
| Computer-use / browser agents | ai-engineer, ai-architect | ✅ Covered | 2026-05-31 | Capability + use cases named; underexplored |
| Model Context Protocol (MCP) | ai-engineer, ai-architect | ✅ Covered | 2026-05-31 | Mentioned in standards; not integrated into core patterns |
| Semantic caching (correctness trade-offs) | ai-engineer | ✅ Covered | 2026-05-31 | Mentioned for cost; correctness trade-offs shallow |

### Category: Architecture + Design

| Topic | Relevant agents | Status | Last audited | Notes |
|---|---|---|---|---|
| Open table format internals (Iceberg) | data-architect, de-engineer | ✅ Covered | 2026-05-30 | Detailed |
| Hidden partitioning + clustering | data-architect, gcp-expert | ✅ Covered | 2026-05-30 | Detailed |
| Schema evolution rules | data-architect | ✅ Covered | 2026-05-30 | Detailed |
| Data contracts (CI enforcement) | data-architect, de-engineer | ✅ Covered | 2026-05-30 | Detailed |
| OpenLineage instrumentation | data-architect, data-ops | ✅ Covered | 2026-05-31 | Mentioned; how-to instrument could be deeper |
| Active metadata patterns | data-architect, governance-consultant | ✅ Covered | 2026-05-31 | Concept covered; implementation patterns could expand |
| Saga / compensating transactions | solution-architect, software-engineer | ✅ Covered | 2026-05-30 | Detailed |
| Event sourcing + CQRS | solution-architect, software-engineer | ✅ Covered | 2026-05-30 | Detailed |
| Multi-region active-active | solution-architect, gcp-expert, aws-expert | ✅ Covered | 2026-05-31 | Mentioned; specific patterns per cloud could go deeper |
| Stream-table duality / Kappa | data-architect, de-engineer | ✅ Covered | 2026-05-30 | data-architect advanced |
| SCD types + dbt snapshots | data-architect, de-engineer | ✅ Covered | 2026-05-30 | data-architect advanced |
| 5 Lenses SA evaluation framework | solution-architect | ✅ Covered | 2026-05-30 | functional/perf/reliability/security/cost |
| Latency budgeting (per-component allocation) | solution-architect | ✅ Covered | 2026-05-30 | SA mental models |
| Coupling spectrum / service decomposition | solution-architect, software-engineer | ✅ Covered | 2026-05-30 | monolith→microservices with 2026 advice |
| Tenancy models (single/shared-infra/fully-shared) | solution-architect, platform-architect | ✅ Covered | 2026-05-30 | Both files |
| Reversible vs sticky decisions | solution-architect, enterprise-architect | ✅ Covered | 2026-05-30 | SA + EA reversibility quadrant |
| Hexagonal / Clean architecture + DDD | software-engineer, data-domain-expert, system-analyst | ✅ Covered | 2026-05-30 | bounded contexts, aggregates, Event Storming |
| SOLID principles | software-engineer | ✅ Covered | 2026-05-31 | Only 'S' explicit; full set could expand |
| Circuit breakers / retry / backpressure | software-engineer, solution-architect | ✅ Covered | 2026-05-30 | distributed-systems realities |
| Property-based testing | software-engineer | ✅ Covered | 2026-05-30 | flagged as "underused gem" with tools |
| CAP / eventual consistency realities | software-engineer, solution-architect | ✅ Covered | 2026-05-30 | advanced topics |
| Strangler fig (incremental migration) | software-engineer, solution-architect, system-analyst | ✅ Covered | 2026-05-30 | all three files |

### Category: FinOps + Cost

| Topic | Relevant agents | Status | Last audited | Notes |
|---|---|---|---|---|
| Cost attribution + tagging policies | platform-ops, devops-engineer | ✅ Covered | 2026-05-30 | Detailed |
| BigQuery cost optimization | gcp-expert, de-engineer, platform-ops | ✅ Covered | 2026-05-30 | Detailed |
| Snowflake cost optimization | platform-ops, de-engineer | ✅ Covered | 2026-05-31 | Mentioned; specific Snowflake levers could deepen |
| Databricks cost optimization | platform-ops, de-engineer | ✅ Covered | 2026-05-31 | Photon + DBU mentioned; deeper patterns could expand |
| Spot/Preemptible strategy | platform-ops, devops-engineer | ✅ Covered | 2026-05-30 | Detailed |
| Showback vs Chargeback | platform-ops | ✅ Covered | 2026-05-30 | Detailed |
| Carbon accounting / GreenOps | platform-ops | ✅ Covered | 2026-05-31 | Briefly in advanced |
| Reserved capacity pooling / purchasing mix | platform-ops | ✅ Covered | 2026-05-30 | on-demand/reserved/spot mix in platform-ops |

### Category: Enterprise & Platform Strategy

| Topic | Relevant agents | Status | Last audited | Notes |
|---|---|---|---|---|
| Conway's Law + Inverse Conway Maneuver | enterprise-architect, platform-architect | ✅ Covered | 2026-05-30 | design arch then reorganize teams |
| 3 Horizons / 70-20-10 budget model | enterprise-architect | ✅ Covered | 2026-05-30 | EA mental models |
| Capability heatmaps (importance × maturity) | enterprise-architect | ✅ Covered | 2026-05-30 | investment guidance grid |
| Tech debt portfolio management | enterprise-architect | ✅ Covered | 2026-05-30 | interest/principal made visible to business |
| Vendor strategy (40% rule, RFP cadence) | enterprise-architect | ✅ Covered | 2026-05-30 | avoid >40% single-vendor |
| Decommissioning as a deliberate feature | enterprise-architect | ✅ Covered | 2026-05-30 | EOL planning from day one |

### Category: Platform Engineering

| Topic | Relevant agents | Status | Last audited | Notes |
|---|---|---|---|---|
| Platform-as-product | platform-architect | ✅ Covered | 2026-05-30 | core mental model |
| Golden paths / paved roads vs trail markers | platform-architect, devops-engineer | ✅ Covered | 2026-05-30 | both files |
| IDP self-service interface levels | platform-architect | ✅ Covered | 2026-05-30 | 5-level progression docs→auto |
| Team Topologies / cognitive load | platform-architect | ✅ Covered | 2026-05-30 | stream-aligned vs platform vs enabling |
| Backstage / developer portal + TechDocs | platform-architect | ✅ Covered | 2026-05-30 | catalog, templates, plugins |
| Policy enforcement defense-in-depth | platform-architect, devops-engineer | ✅ Covered | 2026-05-30 | design/build/deploy/runtime layers |
| Platform success metrics | platform-architect, platform-ops | ✅ Covered | 2026-05-30 | adoption %, time-to-deploy, NPS |
| Multi-tenancy isolation levels + quotas | platform-architect, solution-architect | ✅ Covered | 2026-05-30 | process/VM/cluster/account |

### Category: Cloud Platform Services

| Topic | Relevant agents | Status | Last audited | Notes |
|---|---|---|---|---|
| GCP: Dataform / BigLake Metastore / Dataplex / AlloyDB | gcp-expert | ✅ Covered | 2026-05-30 | named in services map; could deepen per service |
| GCP: BigQuery internals (Dremel/Capacitor/Colossus) | gcp-expert | ✅ Covered | 2026-05-30 | architecture + slot model |
| AWS: Karpenter / DMS / Aurora I/O-Optimized / AFT | aws-expert | ✅ Covered | 2026-05-30 | named; some not in decision tables |
| Azure: Fabric RTA / Purview / Conditional Access / Arc | azure-expert | ✅ Covered | 2026-05-31 | named; emerging-importance ones thin |
| Thailand / APAC cloud specifics (PDPA, regions, latency) | gcp-expert, governance-consultant | ✅ Covered | 2026-05-30 | explicit SE-Asia guidance in gcp-expert |

### Category: Requirements & Process Analysis (SA / BA)

| Topic | Relevant agents | Status | Last audited | Notes |
|---|---|---|---|---|
| Event Storming | system-analyst, data-domain-expert, business-analyst | ✅ Covered | 2026-05-30 | DDD-derived domain analysis |
| Process mining (Celonis/Disco) | system-analyst, business-analyst | ✅ Covered | 2026-05-30 | data-driven discovery |
| Stakeholder Power-Interest matrix | system-analyst, business-analyst | ✅ Covered | 2026-05-30 | both files |
| MoSCoW + INVEST | system-analyst, business-analyst | ✅ Covered | 2026-05-30 | prioritization + story criteria |
| Gap analysis (people/process/tech/data) | system-analyst | ✅ Covered | 2026-05-30 | 4-dimension framework |
| Traceability matrix (RTM) | system-analyst, business-analyst | ✅ Covered | 2026-05-31 | concept present; methodology could deepen |
| Master Data + Reference Data Management | data-domain-expert | ✅ Covered | 2026-05-30 | stewardship + versioning |
| Data Mesh data products / quality contracts | data-domain-expert, data-architect | ✅ Covered | 2026-05-30 | DDE advanced topics |

---

## Prompts (copy-paste when running an audit / update)

### Prompt A — Full audit pass

```
Read /Users/wasin/Documents/Projects/Agent/roles/KNOWLEDGE_CHECKLIST.md.

For every row marked '⚠️ Partial', '❓ Audit needed', or '❌ Missing':
1. Open the relevant agent's knowledge.md (look up the right path under /Users/wasin/Documents/Projects/Agent/roles/).
2. Search for the topic to verify the current coverage state.
3. If genuinely Partial/Missing: deep-research the topic. Prefer:
   - Vendor docs (current 2025-2026)
   - Standards bodies (CNCF, Apache foundation, NIST, etc.)
   - Recognized industry blogs (Martin Fowler, Maxime Beauchemin, MLOps Community, etc.)
   - Cite 2-3 sources in the new content
4. Append a focused section (200-500 words) to the relevant knowledge.md under the most appropriate existing section ('Standard Practices' or 'Advanced Topics').
5. Update the checklist row: change status to '✅ Covered', update 'Last audited' to today's date, add a short note about what was added.

Work through topics sequentially. Use the Agent tool with subagent_type='Explore' for research where helpful. Report progress in chunks (every 5 topics).
```

### Prompt B — One topic deep dive

```
Topic: <PASTE TOPIC NAME>

Relevant agents (from checklist): <PASTE RELEVANT AGENTS>

For each relevant agent:
1. Open /Users/wasin/Documents/Projects/Agent/roles/.../<agent>/knowledge.md
2. Find the appropriate section ('Standard Practices' or 'Advanced Topics')
3. Add or expand a focused subsection (300-600 words) covering:
   - What it is (concise definition)
   - Why it matters in production
   - Standard patterns + when to use each
   - Anti-patterns / pitfalls
   - Tools (current 2025-2026)
   - 1-2 reference links

Then update KNOWLEDGE_CHECKLIST.md: mark the row '✅ Covered', set Last audited to today.
```

### Prompt C — Add new topics from a list

```
I want to add the following topics to KNOWLEDGE_CHECKLIST.md (and have them researched + added to relevant agents):

- Topic 1
- Topic 2
- ...

For each:
1. Identify the right category (existing or new).
2. Identify relevant agents (which knowledge.md files should reference this).
3. Add the row to KNOWLEDGE_CHECKLIST.md under the right category, status = ❓ Audit needed.
4. Then run Prompt A on the new topics.
```

### Prompt D — Cross-check coverage (sanity audit)

```
Read every knowledge.md under /Users/wasin/Documents/Projects/Agent/roles/.

For each, summarize:
- File path
- Top 5 most substantial sections (heading + 1-line summary)
- Topics that ARE covered but not in the checklist (so I can add them)
- Sections that feel shallow

Output as a markdown report. Don't modify any files in this pass.
```

---

## Maintenance

- Review this checklist quarterly. Mark topics as `🔒 Out of scope` if they've become irrelevant (and note why).
- When the AI/data landscape shifts (new dominant tool, new standard), add a row for the new topic.
- Don't let the checklist grow unbounded — archive old `Out of scope` rows when there are >10.

---

## Related files

- `INDEX.md` (this directory) — directory of agent categories
- `~/.claude/CLAUDE.md` — global instructions (loaded every session)
- `/Users/wasin/Documents/Projects/Agent/INDEX.md` — top index for the whole agent system
