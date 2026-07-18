# System Analyst — Comprehensive Knowledge

> Deep reference for the system-analyst subagent.

---

## 1. Foundations

### What a System Analyst does

Makes **implicit understanding explicit** before anyone codes. Bridge between business stakeholders and engineering.
- Elicit requirements
- Map current ("as-is") state
- Design future ("to-be") state
- Document processes + data flows
- Translate ambiguity into specs
- Trace requirements through delivery

### How it differs

- **Business Analyst** — business-side requirements + processes
- **Solution Architect** — picks technical components based on requirements
- **Product Manager** — what to build + why (market-focused)
- **System Analyst** — what + how at the system level (engineering-focused)

In practice these overlap heavily; titles vary by org.

### Core deliverables

- Requirements documents (functional + non-functional)
- Process diagrams (BPMN, swimlanes)
- Data flow diagrams
- Use cases / user stories
- Sequence diagrams
- Acceptance criteria
- Traceability matrix

---

## 2. Mental Models / Decision Frameworks

### As-is before to-be

Don't propose changes until you understand the current state.
- Talk to actual users (not just managers)
- Observe (process mining if data exists)
- Map exceptions + edge cases
- Identify pain points + workarounds

Most failed projects skipped this step.

### Stakeholders ≠ requirements

What stakeholders say:
- "I want a dashboard"

What they mean:
- "I want to spot issues before customers complain"

What they need:
- Anomaly detection alerts (not a dashboard)

Translation is the SA's value-add.

### MoSCoW prioritization

Each requirement is:
- **Must have** — release fails without it
- **Should have** — important but not blocking
- **Could have** — nice-to-have
- **Won't have** — this release

Forces stakeholders to make trade-offs.

### INVEST criteria for user stories

- **I**ndependent (deliverable alone)
- **N**egotiable (room for discussion)
- **V**aluable (clear user benefit)
- **E**stimable (can be sized)
- **S**mall (fits in a sprint)
- **T**estable (can verify done)

### Functional vs Non-Functional Requirements

**Functional** — what the system does:
- "User can reset password"
- "Order is confirmed via email"

**Non-Functional** — qualities of the system:
- Performance (latency, throughput)
- Reliability (uptime, MTTR)
- Security (auth model, data protection)
- Usability (accessibility, learnability)
- Maintainability
- Scalability

NFRs are often overlooked — and the source of late-project pain.

### Trace every requirement

Requirements traceability matrix:
```
Req ID | Source | Description | Design doc | Test case | Status
```

Anything not traced is at risk of being missed.

### Edge cases live in the gaps

The 80% happy path is easy. The 20% edge cases consume 80% of dev time.
- Negative paths: what if X is null, missing, invalid?
- Boundary conditions: max value, empty input, off-by-one
- Concurrency: two users do X at the same time
- Failure modes: downstream service down

Actively hunt these in requirements gathering.

---

## 3. Standard Practices

### Requirements gathering techniques

| Technique | When |
|---|---|
| **Interviews** | Default; structured open questions |
| **Workshops** | Multiple stakeholders, alignment |
| **Observation** | Process mining, shadowing |
| **Surveys** | Many stakeholders, structured |
| **Document analysis** | Existing artifacts |
| **Prototypes** | Tangible feedback |
| **Use case workshops** | Process clarity |

### Process modeling notations

- **BPMN 2.0** — business process standard (rich, complex)
- **Swimlane** — actor-based, simpler
- **Value stream map** — Lean-derived, flow focus
- **UML sequence diagram** — interaction over time
- **UML activity diagram** — flowchart-like

Pick one and stick with it for a project.

### User story format

```
As a [role]
I want [goal]
So that [benefit]

Acceptance Criteria:
- Given [context]
- When [action]
- Then [outcome]
```

The "So that" forces stakeholders to justify value.

### Use case template

```
Name:
Actors:
Preconditions:
Main flow:
  1. Actor does X
  2. System does Y
  3. ...
Alternative flows:
  ...
Postconditions:
Exceptions:
```

### Data dictionary

For every entity / field:
- Name
- Type
- Description (business meaning)
- Constraints (length, format, valid values)
- Source system
- PII / sensitivity classification
- Owner

Critical for downstream eng + governance.

### State machine modeling

For entities with lifecycles (Order, User, Subscription):
```
[Pending] →placeOrder→ [Submitted] →pay→ [Paid] →ship→ [Shipped] → ...
                                                                ↓ cancel
                                                            [Cancelled]
```

Explicit state machines prevent ambiguous transitions.

### Gap analysis

Current state vs future state, what's missing:
- People
- Process
- Technology
- Data

Use to estimate effort + identify dependencies.

### Risk register

For every project:
- Risk description
- Probability (L/M/H)
- Impact (L/M/H)
- Owner
- Mitigation plan

Review weekly with project lead.

### Acceptance criteria

Specific, testable, achievable. Bad vs good:

**Bad**: "System should be fast."
**Good**: "API responses < 500ms p95 under 100 req/s load."

**Bad**: "User-friendly."
**Good**: "New user can complete signup in <3 minutes without support."

---

## 4. Tools Landscape (2026)

### Diagramming
- **draw.io / diagrams.net** — free, ubiquitous
- **Lucidchart** — collaborative
- **Miro** — workshop/whiteboard
- **Visio** — Microsoft enterprise
- **Mermaid** — text-as-diagram, version-controlled

### Requirements management
- **Jira** — most common (Atlassian)
- **Azure DevOps** — Microsoft stack
- **GitLab Issues** — Git-integrated
- **Linear** — modern, popular at startups
- **DOORS** — heavyweight, legacy aerospace/defense
- **Notion / Confluence** — wiki-style

### Process mining
- **Celonis** — enterprise
- **UiPath Process Mining**
- **Disco**

### Modeling
- **Enterprise Architect** (Sparx) — UML/BPMN heavy
- **MEGA / ARIS** — enterprise BPM
- **Camunda Modeler** — BPMN execution

### Wiki / documentation
- **Confluence** — enterprise standard
- **Notion** — modern collaborative
- **Markdown in Git** — engineer-friendly

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Skipping as-is mapping | Designing wrong solution | Map current state honestly |
| One stakeholder interview | Biased view | Multiple perspectives |
| Requirements without NFRs | Late surprises | NFRs first-class |
| Vague acceptance criteria | Done-ness disputes | Specific + testable |
| Doc once, never update | Stale knowledge | Living docs in Git/wiki |
| Hundred-page BRD | Nobody reads | Concise + structured |
| Skipping edge cases | Defects in production | Actively hunt edge cases |
| Designed by committee | Diluted, unclear | One DRI for the spec |
| Spec drift during build | Confusion | Change control + versioning |
| No traceability | Missed requirements | Traceability matrix |

---

## 6. Advanced / Expert Topics

### Domain modeling

Going beyond CRUD:
- Entity-Relationship modeling (ERD)
- Event Storming (domain events, commands, aggregates) — DDD method
- Context maps (DDD bounded contexts)

### Stakeholder mapping

Power-Interest matrix:
- High power + high interest → manage closely
- High power + low interest → keep satisfied
- Low power + high interest → keep informed
- Low power + low interest → monitor

### Workshop facilitation

For a successful requirements workshop:
- Clear objective stated upfront
- Pre-work shared in advance
- Time-boxed agenda
- Capture decisions + open questions
- Send writeup within 24h
- Track action items

### Change management

When the spec changes mid-flight:
- Impact assessment (dev + test + docs + deploy)
- Stakeholder communication
- Re-prioritization
- Update traceability

A change without these is technical debt waiting to happen.

### Compliance + regulatory requirements

In regulated industries:
- Map each control to specific requirements
- Audit trail of decisions
- Sign-offs from compliance / legal
- Document for regulator inspection

### Integration analysis

When connecting systems:
- API contracts (shape, semantics, versioning)
- Data mapping (source → target field + transform)
- Error handling (timeouts, retries, dead-letters)
- Volume + latency expectations
- Sequencing dependencies

### Modernization / migration analysis

Before replacing a legacy system:
- Catalog existing functionality (often more than expected)
- Identify unused features (don't migrate)
- Map data + dependencies
- Plan transition (strangler fig is usually right)
- Define decommission criteria

### Requirements Traceability Matrix (RTM) — methodology

**What it links.** An RTM is the spine that connects each requirement to its lineage and its proof of delivery: **business req → functional/non-functional req → design artifact → code/component → test case → defect → status**. Each row is one requirement with a stable ID; columns hold the linked artifacts. Per BABOK, traceability "identifies and documents the lineage of each requirement, including its backward traceability, its forward traceability, and its relationship to other requirements."

**Three directions.**
- **Forward** — requirement → design → code → test. Proves every requirement is built and tested.
- **Backward** — test/code → requirement. Proves nothing was built that no one asked for (gold-plating, scope creep).
- **Bidirectional** — both; the only form that gives full coverage and clean impact analysis when something changes.

**Build + maintain.** Assign IDs at requirement capture (never reuse). Link artifacts as they're created, not retroactively. Treat it as a **living document** wired into change control — a spec change updates the RTM in the same motion. Stale matrices are worse than none because they're trusted.

**Coverage analysis.** Two queries earn their keep: **orphan requirements** (no design/test linked → at risk of being missed) and **orphan artifacts** (code/tests with no parent requirement → scope creep). Also flag **untested requirements** before release sign-off.

**Tools (2025-2026).** Jira + plugins (Requirement Yogi, Xray, RTM for Jira); Azure DevOps work-item links; IBM DOORS / Visure / Jama for heavyweight regulated work; a spreadsheet is legitimate for small projects.

**When it's worth it.** Mandatory in regulated/audited domains (medical, aerospace, finance, gov) where auditors demand requirement-to-control evidence. For small agile teams, lightweight alternatives — epic→story→test links in the tracker, or a "Definition of Done" tied to acceptance criteria — usually beat a formal matrix. Reach for a full RTM when audit, safety, contract, or large multi-team scope makes missed requirements expensive.

Refs: [IIBA/BABOK — Requirements Traceability](https://www.softwaretestinghelp.com/requirements-traceability-matrix/) · [Visure — What is an RTM](https://visuresolutions.com/alm-guide/requirements-traceability-matrix/)

---

## 7. References

### Books
- **Software Requirements** — Karl Wiegers (the bible)
- **User Stories Applied** — Mike Cohn
- **The Business Analyst's Handbook** — Cadle, Paul, Yeates
- **Event Storming** — Alberto Brandolini
- **Domain-Driven Design** — Eric Evans

### Standards
- **BPMN 2.0** — bpmn.org
- **UML 2.x** — omg.org
- **BABOK Guide** — Business Analysis Body of Knowledge
- **IIBA certifications** (CBAP, CCBA)

### Communities
- **IIBA** (International Institute of Business Analysis)
- **Modern Analyst** (community)
- **Bridging the Gap** (blog)

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| Business Analyst | Overlap on requirements; BA more business-focused, SA more system-focused |
| Solution Architect | "Here are the requirements — design the system" |
| Domain Expert | "Help me understand the business" |
| Engineering | "Translate spec to implementation plan" |
| Product | "Prioritize + scope" |
| QA | "Acceptance criteria become test cases" |
| Stakeholders | "Validate understanding" |

---

*The SA's value is making the implicit explicit. Code is the easy part — agreement on what to build is the hard part.*
