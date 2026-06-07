# Enterprise Architect — Comprehensive Knowledge

> Deep reference for the enterprise-architect subagent.

---

## 1. Foundations

### What an Enterprise Architect does

Operates at **org-wide, multi-year horizons**. Aligns technology with business strategy. Makes decisions that affect multiple systems, multiple teams, multiple budgets.

- Not designing one system (that's solution architect)
- Not picking tech for one team (that's their tech lead)
- Setting **principles, capabilities, roadmaps, governance** that shape how the org thinks about technology

### The 4 EA domains (TOGAF heritage, still useful)

```
BUSINESS    — strategy, processes, capabilities, value streams
DATA        — entities, flows, ownership, governance
APPLICATION — systems, integrations, lifecycle
TECHNOLOGY  — infrastructure, platforms, standards
```

EA thinks across all four. Most EAs over-index on Technology/Application. The mature ones lead with Business + Data.

### Common deliverables

- **Capability maps** — what the org can do, organized hierarchically
- **Reference architectures** — templates for common patterns
- **Roadmaps** — current → 1yr → 3yr horizons
- **Tech radar** — adopt / trial / assess / hold by category
- **Principles + standards** — non-negotiable patterns + acceptable variations
- **Decision records** — ADRs for org-level decisions
- **Governance framework** — review boards, policies, exceptions

### Adjacent roles

- **CTO / CIO** — sets strategy; EA implements it as architecture
- **Solution Architects** — work within EA's principles to deliver specific systems
- **Domain Architects** (Data, AI, Security, etc.) — deep specialists
- **Business Architecture / Strategy** — provides business context

---

## 2. Mental Models / Decision Frameworks

### Conway's Law (and the reverse)

> Any organization that designs a system will produce a design whose structure is a copy of the organization's communication structure.

Corollary: changing architecture without changing org structure rarely works.

The **Inverse Conway Maneuver** — design the architecture you want, then reorganize teams to match.

### 3 Horizons (Baghai / McKinsey, adapted for tech)

```
Horizon 1 (now)        — Run + improve existing systems
Horizon 2 (1-3 years)  — Build adjacent capabilities
Horizon 3 (3+ years)   — Explore disruptive bets
```

Budget by horizon: typically 70/20/10. Don't let H1 starve H2/H3.

### Capability-led thinking

Don't start with "we need Snowflake" — start with "we need an analytics capability." Then evaluate which solutions provide it.

A **capability** = a business-defined function (e.g., "process customer orders").
A **capability map** = hierarchical breakdown of all capabilities.

Then map: capabilities ↔ systems ↔ ownership ↔ investment level.

### Build vs Buy vs Adopt at enterprise scale

| | Build | Buy | Adopt OSS |
|---|---|---|---|
| Differentiation | High | Low (commodity) | Medium |
| Control | Full | Limited | Full but ops cost |
| TCO | High initial, low marginal | Predictable | Variable |
| Lock-in risk | Self-imposed | Vendor | Community |
| Best for | Core differentiation | Non-core | Strategic infra |

### Standards vs flexibility trade-off

Too many standards → slow + bureaucratic
Too few → fragmented + expensive

**Standardize the boring** (identity, observability, data formats, security baseline).
**Vary the strategic** (specific tooling, language choice within reason, deployment patterns).

### Reversibility quadrant

| Decision | Cost to reverse | EA involvement |
|---|---|---|
| Reversible + cheap | Low | Let teams decide |
| Reversible + expensive | Medium | EA review, recommend |
| Irreversible + cheap | Medium | EA review |
| Irreversible + expensive | High | EA strong opinion, governance |

Don't EA-review reversible cheap decisions. You'll be the bottleneck.

### The Tech Radar method (from ThoughtWorks)

Categorize tools / techniques into:
- **Adopt** — proven, recommended
- **Trial** — promising, worth piloting
- **Assess** — interesting, watch
- **Hold** — avoid for new work

Refresh quarterly. Make it visible org-wide.

### Decommissioning is a feature

Every system needs an end-of-life plan from day one.
- When will it be reviewed for retirement?
- What replaces it?
- Migration cost?
- Data preservation?

EAs are the only ones who consistently think about this. Most product teams want to ship + move on.

---

## 3. Standard Practices

### TOGAF / Zachman / FEAF

The classic EA frameworks. Pragmatically:
- **TOGAF** — most widely taught, has the ADM (architecture development method) cycle
- **Zachman** — matrix of perspectives × abstractions; conceptual
- **FEAF** — US Federal; useful in regulated industries

Modern EA practice rarely uses TOGAF as gospel. Use the language + concepts; skip the bureaucracy.

### ADRs at the EA level

Architecture Decision Records — same as project ADRs but for org-wide decisions:
- "Our org will use OpenLineage as the lineage standard"
- "All new services will use Iceberg as the canonical storage format"
- "We will not multi-cloud the same workload"

Number them, version them, link to consequences as they emerge.

### Capability heatmaps

Plot capabilities on a 2D grid:
- X-axis: strategic importance (low → high)
- Y-axis: current maturity (low → high)
- Color: investment trend (declining / stable / growing)

The output guides investment: high-importance + low-maturity = invest now.

### Reference architectures

Common patterns documented as templates:
- "Standard microservice"
- "Standard data pipeline"
- "Standard analytics dashboard"

Teams start from the reference, deviate with reason. Reduces decision fatigue.

### Governance review boards

The EA's most-loved/hated role. Best practice:
- **Lightweight** — async approvals where possible, in-person only for big bets
- **Criteria-based** — "approved if X" not "approved if reviewer's mood"
- **Time-boxed** — explicit SLA on response
- **Exception handling** — process for justified non-conformance

### Architecture principles

Short, durable statements that guide many specific decisions. Examples:
- "Buy don't build for commodity capabilities."
- "Open formats over proprietary unless quantified ROI."
- "Single canonical source of truth per business entity."
- "All systems emit standard observability signals."
- "No personally-identifiable information leaves region without explicit approval."

10-15 max. If you have 50, no one remembers them.

### Tech debt portfolio management

Treat tech debt like financial debt:
- Inventory (where + how much)
- Interest rate (how much slow-down per quarter)
- Principal repayment plan
- Trade-off vs new investment

Make trade-offs visible to business leadership.

---

## 4. Tools / Frameworks Landscape (2026)

### EA tools (commercial)
- **LeanIX** — enterprise architecture management
- **MEGA / Sparx EA** — modeling-heavy
- **Avolution ABACUS** — analysis-focused
- **Bizzdesign** — TOGAF-aligned

### Capability mapping
- Spreadsheets are still the most common. Don't overthink.
- Specialized tools (LeanIX, Ardoq) add value at scale.

### Tech radar
- **ThoughtWorks Technology Radar** — public reference
- **Backstage Tech Radar plugin** — easy internal radar

### Architecture documentation
- **Markdown in Git** — most pragmatic; ADRs + reference architectures
- **C4 model** — diagram method
- **Confluence / Notion** — broader doc home
- **Structurizr** — C4-native, version-controlled

### Decision tracking
- **ADR tools** — adr-tools CLI, dotADR
- **DACI / RACI** — decision-rights frameworks
- **Loom / video walkthroughs** — for nuance prose can't capture

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Ivory tower EA | Disconnected from delivery teams | Embed with product teams quarterly |
| One-and-done capability map | Stale after 6 months | Quarterly refresh, treat as living artifact |
| All standards, no exceptions | Brittle, breeds workarounds | Clear exception process + sunset of exceptions |
| All exceptions, no standards | Fragmentation, no leverage | Pick the 5-10 standards that matter most |
| Reorganization without architecture change | Same problems, new boxes | Inverse Conway: design then reorg |
| Vendor-led roadmap | Vendor's interest ≠ yours | Vendor-agnostic capability roadmap; vendors are tools |
| Avoiding decommissioning | Tech debt compounds | Built-in EOL planning |
| TOGAF as religion | Slow, bureaucratic | TOGAF as vocabulary, not process |
| Architecture diagrams nobody reads | Wasted effort | Plain text + C4 + ADRs for decisions |

---

## 6. Advanced / Expert Topics

### M&A architecture integration

When a company acquires another:
- Identity / SSO consolidation (highest priority)
- Data integration (longest tail)
- Cost: typically 2-3x what's estimated
- Timeline: 12-36 months for meaningful integration
- "Coexist" pattern is usually the practical outcome

### Multi-business-unit governance

Large enterprises with autonomous BUs (think conglomerates):
- Federate the EA function — central EA + BU-level EAs
- Shared services for cross-cutting capabilities
- Tax & charge model for shared services
- Principles + minimal standards at center; BU autonomy below

### Vendor strategy

- Avoid >40% spend with a single vendor in any category
- Negotiate renewals 6-12 months early
- RFP every 3 years for major spend
- Build internal advocates AND skeptics for each vendor

### Compliance + Risk lens

Modern EAs deal with:
- **Data residency** — region-locked data + processing
- **Regulatory reporting** — auditability + lineage
- **AI Act / model risk** — emerging governance for ML/LLM
- **PDPA / GDPR / CCPA** — privacy
- **PCI-DSS / HIPAA / SOX** — industry regimes

EA work increasingly intersects with risk + audit functions.

### Sustainability / FinOps + GreenOps

Newer EA concern:
- Cost transparency per team / product / business unit
- Carbon accounting (cloud providers now publish per-region carbon)
- Workload scheduling for clean energy availability
- This will become mandatory reporting in some jurisdictions

### Roadmap communication

EAs spend 50%+ of their time on communication:
- Executive briefings (1-page, exec-friendly)
- Engineering audiences (technical depth)
- Cross-functional councils
- Vendor + partner conversations
- Adapt the message; don't reuse the same deck

---

## 7. References

### Books
- **Enterprise Architecture As Strategy** — Ross, Weill, Robertson (classic)
- **Strategy as Practice** — Whittington
- **Continuous Architecture** — Erder, Pureur
- **Team Topologies** — Skelton, Pais
- **The Lean Enterprise** — Humble, Molesky, O'Reilly
- **Building Evolutionary Architectures** — Ford, Parsons, Kua

### Frameworks
- **TOGAF** — opengroup.org/togaf (the big reference)
- **Zachman Framework**
- **ArchiMate** — modeling language for EA
- **NIST Enterprise Architecture Framework**

### Industry publications
- **InfoQ Architecture queue**
- **ThoughtWorks Technology Radar** — twice yearly
- **Gartner Hype Cycle + Magic Quadrants** (skeptically)
- **McKinsey / BCG / Bain** — industry digital trends

### Communities
- **Open Group** (TOGAF custodian)
- **Iasa Global** (architecture certification)
- **Architecture Tribe** (Substack / community)

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| C-Suite | Translate strategy into capability investment |
| Solution Architects | Make sure their designs align with principles |
| Data Architect | Org-wide data principles + capability priorities |
| Platform Architect | Capabilities the platform should provide |
| AI Architect | AI strategy, model governance |
| Domain leaders | Capability ownership, roadmap alignment |
| Finance | Tech investment portfolio |
| Risk + Compliance | Policy translation to architecture |
| Vendors | Strategic partnerships, contracts |

---

*EA is a long game. The decisions you make today play out over years.*
