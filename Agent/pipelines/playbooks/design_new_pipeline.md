# Playbook: Design a New Data Pipeline

> Two-layer playbook. **Layer 1** (orchestration) is precise + stable — it's the reusable part.
> **Layer 2** (domain answers) stays loose — the agents + vector DB generate it fresh each run.

---

## When to use this

| Use the full playbook | Ad-hoc (single subagent) is enough |
|---|---|
| New pipeline touches regulated data (PDPA / BoT) | Small addition to an existing pipeline |
| Cost > ~1M฿/yr or customer-facing SLA | One-off backfill / POC |
| Spans more than one domain | Single clear question |

If two of the left-column apply → playbook. Otherwise just ask one agent.

---

# Layer 1 — Orchestration (precise, stable)

This is the part worth encoding. It does **not** name tools or technologies — only *who does what, in what order, consuming what*. It survives tech changes.

## Agents + handoff contracts

Each stage consumes a defined input and emits a defined output. The contract — not the prose — is what makes this repeatable.

| # | Stage | Agent | Consumes | Emits (contract) |
|---|---|---|---|---|
| 1 | Discover | `business-analyst` | use-case description | `requirements`: consumers, latency, freshness, volume, retention, sensitivity |
| 2 | Data design | `data-architect` | `requirements` | `design`: tables, keys, partition/cluster, table format, contracts |
| 3 | Component choice | `solution-architect` | `requirements` + `design` | `stack`: ingest / transform / serve components + reasoning |
| 4a | Compliance | `governance-consultant` | `design` + `stack` | `compliance`: PII map, masking, retention, consent, **blocker? y/n** |
| 4b | Build plan | `de-engineer` | `design` + `stack` | `buildplan`: steps, risks, effort estimate |
| 5 | Ops plan | `data-ops` | `buildplan` | `opsplan`: SLA, monitoring, alerting, runbook |
| 6 | Synthesize | main agent | all of the above | single design doc |

> Every agent pulls reference knowledge via `mcp__agent-knowledge__search_knowledge` (role-filtered) before answering — so contracts stay thin; depth comes from the vector DB.

## Orchestration shape (the DAG)

```
        ┌─ 1. business-analyst ─┐
        │      (requirements)   │
        ▼                       
   2. data-architect            
        │   (design)            
        ▼                       
   3. solution-architect        
        │   (design + stack)    
        ▼                       
   ┌────┴─────────────┐   ◄── 4a + 4b run in PARALLEL (both consume design+stack)
   ▼                  ▼
4a. governance    4b. de-engineer
 (compliance)      (buildplan)
   │                  │
   │                  ▼
   │            5. data-ops
   │              (opsplan)
   └────────┬─────────┘
            ▼
      ⟂ GATE: compliance.blocker == y ?
            │
       yes ─┴─► loop back to step 2 (data-architect) with the blocker
            │
        no ─┴─► 6. synthesize → design doc
```

Three things v1 lacked, encoded here:
1. **Parallelism** — governance + de-engineer don't depend on each other; run them together.
2. **Handoff contracts** — each arrow carries a named payload, not "expected output: stuff".
3. **A quality gate** — a governance blocker loops back instead of silently flowing downstream.

---

# Layer 2 — How to run it

Pick one. Both keep domain answers loose.

## Option A — Ad-hoc (paste into a session)

Fastest. Claude orchestrates, adapting as it goes.

```
ออกแบบ <pipeline> ใหม่ตาม playbook design_new_pipeline:
1. business-analyst สรุป requirements ก่อน
2. data-architect ออกแบบ schema/storage
3. solution-architect เลือก components
4. ขนานกัน: governance-consultant (PDPA/BoT) + de-engineer (build plan)
5. data-ops วาง SLA/monitoring จาก build plan
ถ้า governance เจอ blocker ให้วนกลับ data-architect
สุดท้ายรวมเป็น design doc เดียว
```

## Option B — Workflow (deterministic, repeatable)

When you want the exact DAG above enforced — parallel stages, gate, every run identical. Type **"workflow"** to trigger, or hand this skeleton to Claude. It spawns the real role subagents (`agentType`), each of which uses the vector DB.

```javascript
export const meta = {
  name: 'design-new-pipeline',
  description: 'Design a production data pipeline end-to-end across role agents',
  phases: [
    { title: 'Discover' }, { title: 'Design' },
    { title: 'Review' }, { title: 'Ops' }, { title: 'Synthesize' },
  ],
}

const USECASE = args?.usecase ?? 'describe the pipeline here'

// 1-3: sequential design pipeline
phase('Discover')
const requirements = await agent(
  `Refine requirements for: ${USECASE}. Output consumers, latency, freshness, volume, retention, data sensitivity.`,
  { agentType: 'business-analyst', label: 'discover' })

phase('Design')
const design = await agent(
  `Given these requirements:\n${requirements}\nDesign tables, keys, partition/cluster, table format, data contracts.`,
  { agentType: 'data-architect', label: 'data-design' })

const stack = await agent(
  `Requirements:\n${requirements}\nData design:\n${design}\nChoose ingest/transform/serve components with reasoning.`,
  { agentType: 'solution-architect', label: 'components' })

// 4a + 4b: PARALLEL review (both consume design + stack)
phase('Review')
const [compliance, buildplan] = await parallel([
  () => agent(
    `Design:\n${design}\nStack:\n${stack}\nAssess PDPA/BoT: PII map, masking, retention, consent. ` +
    `End with a line "BLOCKER: yes" or "BLOCKER: no".`,
    { agentType: 'governance-consultant', phase: 'Review', label: 'compliance' }),
  () => agent(
    `Design:\n${design}\nStack:\n${stack}\nGive a step-by-step build plan, risks, effort estimate.`,
    { agentType: 'de-engineer', phase: 'Review', label: 'buildplan' }),
])

// 5: ops plan consumes the build plan
phase('Ops')
const opsplan = await agent(
  `Build plan:\n${buildplan}\nDefine SLA tiers, monitoring (5 pillars), alerting, runbook outline.`,
  { agentType: 'data-ops', label: 'ops' })

// GATE: re-design if governance flagged a blocker
let finalDesign = design
if (/BLOCKER:\s*yes/i.test(compliance)) {
  phase('Design')
  finalDesign = await agent(
    `Your prior design hit a compliance blocker.\nDesign:\n${design}\nBlocker:\n${compliance}\nRevise the data design to resolve it.`,
    { agentType: 'data-architect', label: 'redesign' })
}

// 6: synthesize
phase('Synthesize')
return { usecase: USECASE, requirements, design: finalDesign, stack, compliance, buildplan, opsplan }
```

Run it with the use case in `args`:
```
workflow design-new-pipeline   (args: { usecase: "ingest POS transactions → customer 360, near-real-time" })
```

---

## Output (both options)

A self-contained design doc: use case + requirements → architecture (data design + stack) → compliance posture → build plan → ops plan. The Workflow returns it as structured JSON for the main agent to render.

## The-1 notes

- Pass `company_filter="ntt"` intent so agents surface project context from the vector DB.
- Also load `~/Documents/Projects/Agent/company/ntt/the_one/CLAUDE.md`.
- Reindex (`_infra/reindex.sh`) if knowledge changed since last run, or agents search stale content.

## Why two layers (the design principle)

Detail belongs on the **orchestration** (stable, reusable, non-obvious) — not the **domain answers** (which rot and over-specify). v1 was loose on both; v2 tightens only the half that benefits from it.
