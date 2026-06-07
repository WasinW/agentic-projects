# Business Analyst — Comprehensive Knowledge

> Deep reference for the business-analyst subagent.

---

## 1. Foundations

### What a Business Analyst does

Bridges business needs and engineering. Owns:
- Requirements elicitation
- Business process analysis + improvement
- BRDs (Business Requirements Documents)
- User stories
- Stakeholder facilitation
- Gap analysis
- Solution validation

### BA vs System Analyst vs Product Manager

- **Business Analyst** — business problems, requirements, process improvement
- **System Analyst** — system-level requirements, technical specs
- **Product Manager** — what to build + why (market, strategy)
- **UX Researcher** — user behavior + needs

Heavy overlap in smaller teams.

### Where BAs operate

- IT projects (most common historical role)
- Process improvement initiatives
- M&A integration
- Regulatory compliance projects
- Digital transformation

---

## 2. Mental Models / Decision Frameworks

### User goal > feature request

Stakeholder says: "I want a button to export to Excel"
You ask: "What will you do with the Excel?"
Real goal: "I need to send a list to a partner monthly"

Maybe the answer is a scheduled email, not an export button.

Translate from "solution" to "underlying need" before agreeing.

### Acceptance criteria are the contract

For each requirement, define:
- Given (context / preconditions)
- When (action / trigger)
- Then (expected outcome)

Specific. Testable. Observable.

### MoSCoW prioritization

- **Must have** — release fails without
- **Should have** — important, not blocking
- **Could have** — nice-to-have
- **Won't have** — explicitly out

Forces hard prioritization decisions.

### RACI (responsibility matrix)

For each major decision / deliverable:
- **R**esponsible (does the work)
- **A**ccountable (owns the outcome, one person)
- **C**onsulted (provides input)
- **I**nformed (kept aware)

Eliminates "I thought you were doing it" confusion.

### Stakeholder analysis (Power-Interest)

| Power | Interest | Strategy |
|---|---|---|
| High | High | Manage closely |
| High | Low | Keep satisfied |
| Low | High | Keep informed |
| Low | Low | Monitor |

Spend BA time proportional to power × interest.

### Estimation honesty

- Range, not point ("3-5 weeks", not "4 weeks")
- Assumptions explicit ("if data is clean")
- Update as you learn
- Don't over-promise to please stakeholders

### Process improvement focus

When mapping a process, ask:
- Where do delays occur?
- Where do errors happen?
- Where is duplication?
- Where is manual work?
- Where is rework?

These are the improvement opportunities.

### "Why" before "what"

Stakeholder describes a feature. You ask why. They tell you. Ask why again.

Repeat until you reach the underlying need that maybe doesn't require the original feature.

---

## 3. Standard Practices

### Requirements gathering techniques

| Technique | When |
|---|---|
| **Interviews** | Default for individuals |
| **Workshops** | Alignment across stakeholders |
| **Observation** | Process mining, job shadowing |
| **Surveys** | Quantitative input from many |
| **Document analysis** | Existing artifacts |
| **Prototypes** | Tangible feedback |
| **JAD sessions** | Joint Application Design — collaborative spec |

### BRD anatomy

```
1. Executive Summary
2. Business Objective + Scope
3. Stakeholders (with roles)
4. Current State (as-is)
5. Future State (to-be)
6. Functional Requirements
7. Non-Functional Requirements
8. Assumptions + Constraints
9. Dependencies
10. Risks + Mitigations
11. Acceptance Criteria
12. Approval / Sign-off
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

Stories should be INVEST:
- **I**ndependent
- **N**egotiable
- **V**aluable
- **E**stimable
- **S**mall
- **T**estable

### Process mapping

Capture:
- Trigger (what starts the process)
- Actors (who does each step)
- Steps (sequence)
- Decisions (branches)
- Inputs + outputs per step
- Time per step
- Tools/systems used
- Exceptions

Notations: BPMN, swimlane diagrams, flow charts.

### Gap analysis structure

For each business capability:
- Current state (what we do today)
- Future state (what we want)
- Gap (delta)
- Impact (cost, time, complexity)
- Recommended action

Drives prioritization + roadmap.

### Workshop facilitation

For productive workshops:
- Clear objective stated upfront
- Pre-work shared in advance
- Time-boxed agenda
- Equal participation (introvert-friendly techniques)
- Capture decisions + open questions
- Send writeup within 24h
- Track action items

### Change management basics

When new system / process rolls out:
- Stakeholder communication plan
- Training plan
- Support during transition
- Feedback channels
- Adoption metrics

Adoption is harder than build.

### Quantifying business value

Tie requirements to one of:
- Revenue increase
- Cost reduction
- Risk reduction
- Compliance
- Customer experience
- Employee productivity

Quantify when possible ($, %, hours). Even rough estimates help prioritization.

---

## 4. Tools Landscape (2026)

### Requirements management
- **Jira** — most common
- **Azure DevOps** — Microsoft stack
- **Linear** — modern, startup-favored
- **Notion / Confluence** — wiki-style
- **DOORS** — heavyweight (aerospace, defense)

### Diagramming
- **draw.io / diagrams.net** — free, ubiquitous
- **Lucidchart** — collaborative
- **Miro** — workshop / whiteboard
- **Visio** — Microsoft enterprise
- **Mermaid** — text-as-diagram

### Process modeling
- **Camunda Modeler** — BPMN execution
- **Signavio** — process mining + modeling
- **Bizagi** — BPM platform

### Workshops + collaboration
- **Miro / Mural / FigJam** — whiteboard
- **Loom** — async video
- **Zoom / Teams / Meet** — synchronous

### Documentation
- **Confluence** — enterprise wiki
- **Notion** — modern, flexible
- **Markdown in Git** — version-controlled

### Process mining
- **Celonis** — enterprise
- **UiPath Process Mining**
- **Disco** — desktop

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Take stakeholder requests literally | Wrong solution | Probe for underlying need |
| Skip as-is mapping | Bad solution design | Map current state |
| One-stakeholder interview | Biased view | Multiple perspectives |
| Vague acceptance criteria | Done-ness disputes | Specific + testable |
| 100-page BRD | Nobody reads | Concise + structured |
| Spec frozen for 6 months | Reality changes | Iterative refinement |
| No quantification | Hard to prioritize | Even rough estimates |
| Build everything | Scope creep | MoSCoW + ruthless cutting |
| BA writes solution | Eng owns how | BA writes what, eng writes how |
| Workshop without agenda | Wasted time | Structured + outcome-focused |
| Stakeholders disagree silently | Sandbagging later | Surface + resolve early |

---

## 6. Advanced / Expert Topics

### Lean / Agile BA practices

- Continuous discovery > big upfront spec
- Slice work small + deliver iteratively
- Embedded with delivery team
- Validate with users early + often

### Domain-Driven Design alignment

When working with engineering on DDD:
- Ubiquitous language sessions
- Event Storming workshops
- Bounded context identification
- Aggregate design

BA helps facilitate; engineers own technical impl.

### Process mining (data-driven BA)

Instead of asking how the process works:
- Mine event logs from systems
- Visualize actual flow + variants
- Identify deviations from ideal
- Quantify time per step + bottlenecks

Far more accurate than interviews for high-volume processes.

### Customer Journey mapping

For customer-facing processes:
- Phases (awareness, consideration, purchase, use, advocacy)
- Touchpoints
- Emotions
- Pain points
- Opportunities

Connects business process to customer experience.

### Outcome-based requirements

Instead of "implement X":
- "Reduce customer onboarding time by 50%"
- "Increase conversion by 20%"
- "Achieve compliance with regulation Y"

Lets engineering propose better solutions to reach the outcome.

### Cost-benefit analysis

For prioritization:
- Costs (build, maintain, opportunity)
- Benefits (revenue, cost saving, risk reduction)
- NPV / payback period
- Sensitivity analysis (what if assumptions wrong?)

Even rough numbers beat pure opinion.

### Stakeholder facilitation

When stakeholders disagree:
- Surface the disagreement explicitly
- Map each position + reasoning
- Find common ground
- Escalate to decision-maker if needed
- Document the decision + rationale

Avoid: pretending alignment exists when it doesn't.

---

## 7. References

### Books
- **Business Analysis Techniques: 99 Essential Tools for Success** — Cadle, Paul, Yeates
- **Lean Startup** — Eric Ries
- **Inspired** — Marty Cagan (Product Management, useful for BA too)
- **The Lean Product Playbook** — Dan Olsen
- **Storytelling with Data** — Cole Knaflic

### Standards / Bodies
- **BABOK Guide** — Business Analysis Body of Knowledge
- **IIBA** (International Institute of Business Analysis)
- **PMI Professional in Business Analysis (PMI-PBA)**

### Communities
- **IIBA** chapters
- **Modern Analyst** community
- **Bridging the Gap** (blog + community)

### Certifications
- **CBAP** (Certified Business Analysis Professional)
- **CCBA** (entry)
- **PMI-PBA**

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| System Analyst | BA owns business needs; SA owns system needs |
| Solution Architect | Translate requirements → tech design |
| Product Manager | What + Why (often overlapping with BA) |
| Engineering | Translate spec → implementation |
| Domain Expert | Deepen understanding |
| Stakeholders | Elicit + validate |
| UX | User research + design |
| Project Manager | Scope, schedule |

---

*BA = bridge. Make the implicit explicit; the contentious negotiable; the ambitious achievable.*
