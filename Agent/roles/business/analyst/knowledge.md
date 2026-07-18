# Analyst — Comprehensive Knowledge

> Deep reference for the `analyst` subagent. Merges the former **business-analyst** (business framing, requirements, process improvement, stakeholders) and **system-analyst** (system-level requirements, data flows, traceability, edge cases). One role for "understand + translate business need".

---

## 1. Foundations

### What an Analyst does

Bridges business needs and engineering, and makes **implicit understanding explicit** before anyone codes. Owns:
- Requirements elicitation (functional + non-functional)
- Business process analysis + improvement; current ("as-is") and future ("to-be") state
- BRDs, user stories, use cases, data-flow diagrams
- Stakeholder facilitation + communication
- Gap analysis, solution validation, requirements traceability

### Related roles (how it differs)

- **Analyst (this role)** — business problems + system-level requirements; the "what + why", and the "how" only at the requirements level.
- **Solution Architect** — picks technical components/design based on the requirements.
- **Product Manager** — what to build + why (market, strategy).
- **UX Researcher** — user behavior + needs.

Heavy overlap in smaller teams; titles vary by org. This role deliberately spans the old BA/SA split.

### Where analysts operate

IT / delivery projects, process-improvement initiatives, digital transformation, M&A integration, regulatory-compliance projects, legacy modernization/migration.

### Core deliverables

Requirements documents (functional + non-functional), process diagrams (BPMN / swimlane), data-flow diagrams, use cases / user stories, sequence + state diagrams, acceptance criteria, gap analysis, traceability matrix, BRD.

---

## 2. Mental Models / Decision Frameworks

### User goal > feature request ("Why" before "what")

Stakeholder: "I want a button to export to Excel." → Ask: "What will you do with it?" → Real goal: "Send a partner a list monthly." → Maybe the answer is a scheduled email, not an export button. Ask "why" repeatedly until you reach the underlying need that may not require the original feature.

### As-is before to-be

Don't propose changes until you understand the current state.
- Talk to actual users (not just managers).
- Observe (process mining if the data exists).
- Map exceptions, edge cases, pain points, workarounds.

Most failed projects skipped this step.

### Stakeholders' words ≠ requirements

What they say ("I want a dashboard") ≠ what they mean ("spot issues before customers complain") ≠ what they need (anomaly-detection alerts, not a dashboard). Translation is the analyst's value-add.

### Acceptance criteria are the contract

For each requirement: **Given** (context/preconditions) → **When** (action/trigger) → **Then** (expected outcome). Specific. Testable. Observable.

### MoSCoW prioritization

- **Must have** — release fails without it.
- **Should have** — important, not blocking.
- **Could have** — nice-to-have.
- **Won't have** — explicitly out (this release).

Forces hard trade-offs.

### INVEST (user-story quality)

**I**ndependent · **N**egotiable · **V**aluable · **E**stimable · **S**mall · **T**estable.

### Functional vs Non-Functional Requirements

- **Functional** — what the system does ("user can reset password", "order confirmed via email").
- **Non-Functional** — qualities: performance (latency/throughput), reliability (uptime/MTTR), security (auth, data protection), usability (accessibility), maintainability, scalability.

NFRs are often overlooked — and the source of late-project pain. Treat them first-class.

### Trace every requirement

Requirements traceability matrix: `Req ID | Source | Description | Design doc | Test case | Status`. Anything not traced is at risk of being missed. (Full RTM methodology in §6.)

### Edge cases live in the gaps

The 80% happy path is easy; the 20% edge cases consume 80% of dev time.
- Negative paths: X is null / missing / invalid?
- Boundaries: max value, empty input, off-by-one.
- Concurrency: two users do X at once.
- Failure modes: downstream service down.

Actively hunt these during requirements gathering.

### RACI (responsibility matrix)

Per major decision/deliverable: **R**esponsible (does the work), **A**ccountable (owns outcome, one person), **C**onsulted (input), **I**nformed (kept aware). Eliminates "I thought you were doing it".

### Stakeholder analysis (Power-Interest)

| Power | Interest | Strategy |
|---|---|---|
| High | High | Manage closely |
| High | Low | Keep satisfied |
| Low | High | Keep informed |
| Low | Low | Monitor |

Spend analyst time proportional to power × interest.

### Estimation honesty

Range not point ("3-5 weeks"); assumptions explicit ("if data is clean"); update as you learn; don't over-promise to please stakeholders.

### Process improvement focus

When mapping a process, ask where the **delays, errors, duplication, manual work, and rework** occur — those are the improvement opportunities.

---

## 3. Standard Practices

### Requirements gathering techniques

| Technique | When |
|---|---|
| **Interviews** | Default for individuals; structured open questions |
| **Workshops / JAD** | Alignment across stakeholders, collaborative spec |
| **Observation** | Process mining, job shadowing |
| **Surveys** | Quantitative input from many |
| **Document analysis** | Existing artifacts |
| **Prototypes** | Tangible feedback |
| **Use-case workshops** | Process clarity |

### BRD anatomy

```
1. Executive Summary          7. Non-Functional Requirements
2. Business Objective + Scope 8. Assumptions + Constraints
3. Stakeholders (with roles)  9. Dependencies
4. Current State (as-is)      10. Risks + Mitigations
5. Future State (to-be)       11. Acceptance Criteria
6. Functional Requirements    12. Approval / Sign-off
```

Adapt to your org's template. Keep it usable, not exhaustive.

### User story format

```
As a [role]
I want [goal]
So that [benefit / business value]

Acceptance Criteria:
- Given [context]
- When [action]
- Then [outcome]
```

The "So that" forces stakeholders to justify value. Stories should be INVEST. (The `user-story-gen` skill is archived — write stories directly.)

### Use case template

```
Name:            Main flow:
Actors:            1. Actor does X
Preconditions:     2. System does Y
Postconditions:  Alternative flows: ...
Exceptions:      ...
```

### Process mapping

Capture: trigger, actors, steps (sequence), decisions (branches), inputs/outputs per step, time per step, tools/systems, exceptions.

Notations: **BPMN 2.0** (rich standard), **swimlane** (actor-based, simpler), **value stream map** (Lean flow focus), **UML sequence** (interaction over time), **UML activity** (flowchart-like). Pick one and stick with it per project.

### Data dictionary

Per entity/field: name, type, description (business meaning), constraints (length/format/valid values), source system, PII / sensitivity classification, owner. Critical for downstream eng + governance.

### State machine modeling

For entities with lifecycles (Order, User, Subscription):
```
[Pending] →placeOrder→ [Submitted] →pay→ [Paid] →ship→ [Shipped]
                                                     ↓ cancel
                                                 [Cancelled]
```
Explicit state machines prevent ambiguous transitions.

### Gap analysis

Per business capability: current state → future state → gap (delta) → impact (cost/time/complexity) → recommended action. Slice the gap across **People / Process / Technology / Data**. Drives prioritization, effort estimate, dependencies, and roadmap.

### Risk register

Per project: risk description, probability (L/M/H), impact (L/M/H), owner, mitigation plan. Review weekly with the project lead.

### Acceptance criteria — bad vs good

- Bad: "System should be fast." → Good: "API responses < 500ms p95 under 100 req/s load."
- Bad: "User-friendly." → Good: "New user completes signup in < 3 minutes without support."

### Workshop facilitation

Clear objective upfront · pre-work shared in advance · time-boxed agenda · equal participation (introvert-friendly) · capture decisions + open questions · send writeup within 24h · track action items.

### Change management

When a spec changes mid-flight: impact assessment (dev + test + docs + deploy), stakeholder communication, re-prioritization, update traceability. When a **system/process rolls out**: communication plan, training, transition support, feedback channels, adoption metrics. Adoption is harder than build; a change without these is technical debt waiting to happen.

### Quantifying business value

Tie each requirement to one of: revenue increase, cost reduction, risk reduction, compliance, customer experience, employee productivity. Quantify when possible ($, %, hours) — even rough estimates beat opinion for prioritization.

---

## 4. Tools Landscape (2026)

### Requirements management
Jira (most common) · Azure DevOps (Microsoft stack) · GitLab Issues (Git-integrated) · Linear (modern, startup-favored) · Notion / Confluence (wiki) · DOORS (heavyweight — aerospace/defense).

### Diagramming
draw.io / diagrams.net (free, ubiquitous) · Lucidchart (collaborative) · Miro (workshop/whiteboard) · Visio (MS enterprise) · **Mermaid** (text-as-diagram, version-controlled).

### Process modeling
Camunda Modeler (BPMN execution) · Signavio (mining + modeling) · Bizagi (BPM) · Enterprise Architect / Sparx (UML/BPMN heavy) · MEGA / ARIS (enterprise BPM).

### Process mining
Celonis (enterprise) · UiPath Process Mining · Disco (desktop).

### Workshops + collaboration
Miro / Mural / FigJam (whiteboard) · Loom (async video) · Zoom / Teams / Meet (sync).

### Documentation
Confluence (enterprise standard) · Notion (modern, flexible) · **Markdown in Git** (version-controlled, engineer-friendly).

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Take requests literally | Wrong solution | Probe for the underlying need |
| Skip as-is mapping | Bad solution design | Map the current state honestly |
| One-stakeholder interview | Biased view | Multiple perspectives |
| Requirements without NFRs | Late surprises | NFRs first-class |
| Vague acceptance criteria | Done-ness disputes | Specific + testable |
| Skip edge cases | Defects in production | Actively hunt them |
| 100-page BRD | Nobody reads | Concise + structured |
| Doc once, never update | Stale knowledge | Living docs in Git/wiki |
| Spec drift / frozen 6 mo | Confusion, reality changes | Change control + iterate |
| No traceability | Missed requirements | Traceability matrix |
| No quantification | Hard to prioritize | Even rough estimates |
| Build everything | Scope creep | MoSCoW + ruthless cutting |
| Analyst writes the solution | Eng owns "how" | Analyst writes "what", eng writes "how" |
| Designed by committee | Diluted, unclear | One DRI for the spec |
| Silent disagreement | Sandbagging later | Surface + resolve early |

---

## 6. Advanced / Expert Topics

### Lean / Agile analysis
Continuous discovery > big upfront spec · slice small + deliver iteratively · embed with the delivery team · validate with users early + often.

### Domain modeling (DDD alignment)
ER modeling (ERD) · Event Storming (domain events, commands, aggregates) · context maps / bounded contexts · ubiquitous-language sessions. Analyst facilitates; engineers own technical impl.

### Process mining (data-driven analysis)
Instead of asking how a process works: mine event logs, visualize actual flow + variants, identify deviations from ideal, quantify time-per-step + bottlenecks. Far more accurate than interviews for high-volume processes.

### Customer journey mapping
For customer-facing processes: phases (awareness → consideration → purchase → use → advocacy), touchpoints, emotions, pain points, opportunities. Connects business process to customer experience.

### Outcome-based requirements
Instead of "implement X": "reduce onboarding time by 50%", "increase conversion by 20%", "achieve compliance with regulation Y". Lets engineering propose better solutions to reach the outcome.

### Cost-benefit analysis
Costs (build, maintain, opportunity) vs benefits (revenue, cost saving, risk reduction); NPV / payback; sensitivity analysis (what if assumptions are wrong?). Even rough numbers beat pure opinion.

### Stakeholder facilitation (conflict)
Surface the disagreement explicitly → map each position + reasoning → find common ground → escalate to the decision-maker if needed → document the decision + rationale. Avoid pretending alignment exists when it doesn't.

### Compliance + regulatory requirements
Map each control to specific requirements · audit trail of decisions · sign-offs from compliance/legal · document for regulator inspection.

### Integration analysis
When connecting systems: API contracts (shape, semantics, versioning) · data mapping (source → target field + transform) · error handling (timeouts, retries, dead-letters) · volume + latency expectations · sequencing dependencies.

### Modernization / migration analysis
Before replacing a legacy system: catalog existing functionality (usually more than expected) · identify unused features (don't migrate) · map data + dependencies · plan transition (strangler fig is usually right) · define decommission criteria.

### Requirements Traceability Matrix (RTM) — methodology

**What it links.** The spine connecting each requirement to its lineage and proof of delivery: **business req → functional/NFR → design artifact → code/component → test case → defect → status**. Each row is one requirement with a stable ID; columns hold linked artifacts. Per BABOK, traceability "identifies and documents the lineage of each requirement, including its backward traceability, its forward traceability, and its relationship to other requirements."

**Three directions.**
- **Forward** — requirement → design → code → test. Proves every requirement is built and tested.
- **Backward** — test/code → requirement. Proves nothing was built that no one asked for (gold-plating, scope creep).
- **Bidirectional** — both; the only form giving full coverage and clean impact analysis when something changes.

**Build + maintain.** Assign IDs at requirement capture (never reuse). Link artifacts as created, not retroactively. Treat it as a **living document** wired into change control — a spec change updates the RTM in the same motion. Stale matrices are worse than none because they're trusted.

**Coverage analysis.** Two queries earn their keep: **orphan requirements** (no design/test linked → at risk of being missed) and **orphan artifacts** (code/tests with no parent requirement → scope creep). Also flag **untested requirements** before release sign-off.

**When it's worth it.** Mandatory in regulated/audited domains (medical, aerospace, finance, gov) where auditors demand requirement-to-control evidence. For small agile teams, lightweight alternatives — epic→story→test links in the tracker, or a Definition of Done tied to acceptance criteria — usually beat a formal matrix. Reach for a full RTM when audit, safety, contract, or large multi-team scope makes missed requirements expensive.

Refs: [IIBA/BABOK — Requirements Traceability](https://www.softwaretestinghelp.com/requirements-traceability-matrix/) · [Visure — What is an RTM](https://visuresolutions.com/alm-guide/requirements-traceability-matrix/)

---

## 7. References

### Books
- **Software Requirements** — Karl Wiegers (the bible)
- **User Stories Applied** — Mike Cohn
- **Business Analysis Techniques: 99 Essential Tools** / **The Business Analyst's Handbook** — Cadle, Paul, Yeates
- **Event Storming** — Alberto Brandolini
- **Domain-Driven Design** — Eric Evans
- **Lean Startup** — Eric Ries · **Inspired** — Marty Cagan · **The Lean Product Playbook** — Dan Olsen
- **Storytelling with Data** — Cole Knaflic

### Standards / Bodies
- **BABOK Guide** — Business Analysis Body of Knowledge · **IIBA**
- **BPMN 2.0** — bpmn.org · **UML 2.x** — omg.org
- **PMI Professional in Business Analysis (PMI-PBA)**

### Communities
IIBA chapters · Modern Analyst · Bridging the Gap (blog + community).

### Certifications
CBAP (Certified Business Analysis Professional) · CCBA (entry) · PMI-PBA.

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| Solution Architect | "Here are the requirements — design the system" |
| Data Architect | Data model + semantics behind the requirements |
| Data Analyst | Metrics / cohort data to quantify value + validate |
| Engineering (`de-engineer` / `software-engineer`) | Translate spec → implementation plan |
| Finance Consultant | Benefit definition, business case, cost-benefit |
| Product | Prioritize + scope (what + why) |
| QA | Acceptance criteria become test cases |
| UX | User research + design |
| Stakeholders | Elicit + validate understanding |

---

*The analyst is the bridge. Make the implicit explicit, the contentious negotiable, the ambitious achievable. Code is the easy part — agreement on what to build is the hard part.*
