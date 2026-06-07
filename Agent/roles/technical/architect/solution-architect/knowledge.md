# Solution Architect — Comprehensive Knowledge

> Deep reference for the solution-architect subagent.

---

## 1. Foundations

### What a Solution Architect does

Designs **end-to-end systems** that meet business requirements within non-functional constraints (latency, cost, reliability, security, compliance).

The SA is the **glue** between domain logic and infrastructure. They:
- Translate requirements into an architecture
- Choose components and integrate them
- Verify the design works under expected load + failure modes
- Hand off implementable specs to engineers

### Not to be confused with

- **Enterprise Architect** — portfolio-level, multi-year, org-wide
- **Data Architect** — specialized in data layer
- **Software Architect** — application + framework focused
- **Cloud Architect** — cloud-platform specialist (this overlaps with SA on cloud projects)

### Core deliverables

- Architecture diagram (C4 model is the modern standard)
- Component selection with reasoning
- Non-functional requirements satisfied
- Failure mode analysis
- Cost envelope
- Deployment + rollback plan
- Open questions / assumptions

---

## 2. Mental Models / Decision Frameworks

### The 5 Lenses (always evaluate a design through these)

| Lens | Question |
|---|---|
| **Functional** | Does it do what the business needs? |
| **Performance** | Does it meet latency / throughput SLAs? |
| **Reliability** | What happens when a component fails? |
| **Security** | Who can access what? Is data protected? |
| **Cost** | What does it cost to run + scale? |

A design that's strong on 4 lenses but weak on 1 is fragile. Pick the design that's balanced or where the weak lens has a mitigation plan.

### Build vs Buy Decision

```
Is this commodity?  → buy / managed service
Is this core differentiation?  → build
Does it require deep ops?  → buy unless you have the team
Is the SaaS cost > $200k/year and stable?  → consider build
```

Default: managed service. Self-host only when there's a real reason.

### Latency Budget (every system has one)

A 1-second response is typically:
```
Network in:           50ms
Auth + routing:       10ms
Service logic:       100ms (your code)
Database query:      200ms
Downstream service:  400ms (recursive — they have their own budget)
Response serialize:   30ms
Buffer:              210ms
```

Allocate per component. If sum > target, redesign.

### Reliability: 9s Math

| Uptime | Allowable downtime/year |
|---|---|
| 99% | 3.6 days |
| 99.9% | 8.7 hours |
| 99.95% | 4.3 hours |
| 99.99% | 52 minutes |
| 99.999% | 5 minutes |

Each extra 9 typically multiplies cost by 3-10x. Match SLA to business need.

### Coupling spectrum

```
Tight                                              Loose
[Monolith] [Modular monolith] [Services] [Microservices]
```

Tight = simpler to develop, fragile to change
Loose = independent deploy, complex to operate

**The 2026 industry-standard advice**: start modular monolith, extract services when you have evidence of need (team boundaries, scale boundaries, language boundaries).

### Failure modes to design for

- **Component failure** — single instance dies
- **Zone failure** — AZ goes down
- **Region failure** — entire region offline
- **Dependency failure** — downstream service or DB unavailable
- **Slow failure** — latency spike, not outage
- **Cascading failure** — retry storm, capacity exhaustion
- **Data corruption** — silent or noisy

Design responses: replication, retry+backoff, circuit breakers, bulkheads, timeouts.

### Cost levers (in order of magnitude)

1. **Architecture** — serverless vs always-on (huge)
2. **Right-sizing** — instance types matched to workload
3. **Pricing tier** — spot, reserved, savings plans
4. **Storage class** — hot vs cold vs archive
5. **Egress** — region + cloud boundaries
6. **Unused resources** — orphan dev clusters, idle volumes

Cost optimization happens at design time; you can't refactor your way to 50% savings.

---

## 3. Standard Practices

### C4 Model (architecture diagrams)

Four levels of zoom:
1. **System Context** — system + users + external systems
2. **Container** — major runtime units (web app, mobile app, DB, service)
3. **Component** — internal modules of a container
4. **Code** — class diagrams (rarely needed)

Most communication uses levels 1 + 2. Level 3 for detailed design.

Tools: Structurizr, draw.io, mermaid, ASCII for chat.

### NFR (Non-Functional Requirements) Template

For every project, define:
```
- Throughput: X requests/sec at peak
- Latency: p50, p95, p99 targets
- Availability: 9s + acceptable downtime/month
- Recovery: RTO (time to restore) + RPO (data loss tolerance)
- Scalability: 10x growth without redesign
- Security: data classifications, encryption, access model
- Compliance: regulations + auditability
- Cost: monthly envelope + per-unit economics
```

If business hasn't defined these, propose defaults and confirm.

### Integration patterns (Enterprise Integration Patterns by Hohpe is the canon)

| Pattern | When |
|---|---|
| Synchronous request/reply (REST/gRPC) | Need immediate answer; failure visible |
| Async message queue (SQS, RabbitMQ) | Decouple, smooth load, retry built-in |
| Pub/sub (Kafka, Pub/Sub) | Multiple consumers, event-driven |
| Webhooks | Notify external systems |
| Polling | When you can't get pushed updates (least preferred) |
| Saga / orchestration | Multi-step distributed transactions |

### Cloud Reference Architectures

Every major cloud has well-architected frameworks:
- **AWS Well-Architected** — 6 pillars (operational, security, reliability, performance, cost, sustainability)
- **Azure Well-Architected**
- **Google Cloud Architecture Framework**

These are the SA's reference manuals. Read once, refer often.

### Migration Patterns

| Pattern | When |
|---|---|
| **Lift and shift** | Time pressure, will optimize later |
| **Replatform** | Move + use cloud services (RDS instead of self-managed DB) |
| **Refactor / Re-architect** | Capture cloud benefits, accept rewrite cost |
| **Strangler Fig** | Incrementally replace old system, route by feature |
| **Big Bang** | Replace all at once (high risk; rarely justified) |

### Vendor selection rubric

| Criterion | Weight (typical) |
|---|---|
| Functional fit | 30% |
| Total cost of ownership (3-5 yr) | 20% |
| Operational complexity | 15% |
| Vendor stability + roadmap | 10% |
| Security + compliance posture | 10% |
| Ecosystem + community | 10% |
| Lock-in risk | 5% |

Quantify even subjective ones. Avoid "feels best".

---

## 4. Tools Landscape (2026)

### Diagramming
- **Structurizr** — C4-native
- **draw.io / diagrams.net** — free, ubiquitous
- **Mermaid** — text-as-diagram, version-controlled
- **Excalidraw** — sketchy aesthetic, fast
- **Miro / Lucid** — collaborative

### Architecture decision tracking
- **ADR (Architecture Decision Records)** in markdown in the repo — gold standard
- **adr-tools** CLI for managing them

### NFR / Capacity testing
- **k6 / Locust** — load testing
- **Vegeta** — HTTP load
- **Chaos Mesh / Gremlin** — chaos engineering

### Cost modeling
- **Infracost** — Terraform-based estimates
- **CloudHealth / Cloudability** — running costs
- **AWS Pricing Calculator / GCP Pricing Calculator** — manual

### Service mesh / API gateway (when needed)
- **Istio / Linkerd** — service mesh
- **Kong / Apigee / AWS API Gateway** — API gateway
- Don't add unless you've proven need

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Architecture astronaut | Designs for hypothetical scale | Design for current + 2x |
| Latest-tech-itis | Picks new shiny tools | Pick boring tech with track record |
| Single point of failure | One component, no replica | Identify SPOFs early; eliminate or accept with mitigation |
| Synchronous everything | Cascading latency + brittleness | Async where possible |
| No backpressure | One slow consumer takes down producer | Queues + timeouts + rate limits |
| No idempotency | Retries cause duplicates | Idempotency keys / natural keys |
| Tight DB coupling | Multiple services share DB | Service owns its data; communicate via API |
| Premature optimization | Wasted complexity | Measure first, optimize second |
| No rollback plan | Can't recover from bad deploy | Blue/green or canary; database migrations forward-compatible |
| Architecture without measurement | Don't know if SLAs met | Observability from day one |

---

## 6. Advanced / Expert Topics

### Event Sourcing

Store the sequence of state changes as immutable events. Current state = fold(events). 
- Use when: full audit trail required, temporal queries common, multiple read models
- Avoid when: simple CRUD is sufficient (most apps)

### CQRS (Command Query Responsibility Segregation)

Separate read model from write model.
- Pairs well with event sourcing
- Allows independent scaling of reads vs writes
- Higher complexity — only use when justified

### Saga / Compensating Transactions

For distributed multi-step operations, instead of distributed ACID:
- Each step has a compensation
- On failure, run compensations in reverse
- Choreography (event-driven) vs Orchestration (central coordinator)

### Service mesh trade-offs

- **Pros**: traffic management, observability, mTLS, retries, traffic splitting
- **Cons**: operational complexity, latency, debugging difficulty
- **Rule**: don't add until you have >10 services with mutual traffic

### Multi-region active-active

The hardest distributed systems problem.
- Conflict resolution (CRDTs, last-write-wins, application-specific)
- Eventual consistency between regions
- Routing: GeoDNS + health checks
- Most teams should accept active-passive or single-region with DR backups

### Multi-region active-active — concrete patterns (per cloud)

**What/why**: Serve writes from 2+ regions simultaneously for low local latency and region-failure survival. The cost is consistency — you trade away a single source of truth. **Default to NOT doing this.** Most "global" apps are served fine by single-region + read replicas, or active-passive with a warm standby. Active-active is justified only when you genuinely need sub-100ms writes on multiple continents *and* near-zero RTO — payments, gaming, global SaaS control planes.

**Data replication — the core decision**:
- **Sync replication** — write acked only after a remote region confirms. Strong consistency, but every write pays cross-region RTT (80-200ms+). Caps throughput; a partition stalls writes.
- **Async replication** — local write acks immediately, replicates in background. Fast, partition-tolerant, but introduces replication lag and **write conflicts** (same key written in two regions). This is what most "active-active" stores actually do.

**Conflict resolution** (only needed with async multi-writer):
- **Last-write-wins (LWW)** — simplest, silently drops the loser. Fine for caches/sessions, dangerous for money.
- **Version vectors / vector clocks** — detect concurrent writes, surface conflicts to the app to merge.
- **CRDTs** — data types (counters, sets, registers) that merge deterministically with no coordination. Best when your data model fits them.
- Best practice: design keys so different regions own different partitions (sharded ownership) — sidesteps conflicts entirely.

**Patterns + when**:
- *Read-local / write-global* — reads local, all writes routed to one home region. Simple, no conflicts; write latency suffers for far users. Good first step.
- *Sharded-by-geo ownership* — each region is authoritative for its users' data. Scales cleanly, no conflicts; cross-shard ops are hard.
- *True multi-writer* — any region accepts any write. Maximum availability, maximum conflict complexity. Only with conflict-free data or a store that handles it.

**Global data stores (2025-2026)**:
- **AWS** — DynamoDB Global Tables (async, LWW; **multi-Region strong consistency / MRSC went GA mid-2025** for sync semantics); Aurora Global Database (async, one primary + read-only secondaries, ~1s lag, fast managed failover — *not* true multi-writer).
- **GCP** — Cloud Spanner (synchronous, externally consistent global writes via TrueTime — the gold standard, at premium cost); AlloyDB for regional + cross-region read pools.
- **Azure** — Cosmos DB multi-region writes (async, configurable conflict policies incl. LWW or custom stored-proc merge; 5 consistency levels).
- **Multi-cloud** — CockroachDB / YugabyteDB (Spanner-style synchronous, self-hostable).

**Traffic routing**:
- **AWS** — Route 53 latency/geo routing (DNS, slow failover) or Global Accelerator (anycast IPs over AWS backbone, fast sub-DNS failover, TCP/UDP).
- **GCP** — global anycast L7 LB (single IP, built-in, routes over Google backbone — most elegant).
- **Azure** — Front Door (anycast L7, WAF, HTTP/S only) or Traffic Manager (DNS).

**Anti-patterns**: active-active "for resilience" when active-passive meets your RTO (90% of cases); LWW on financial/inventory data; multi-writer without a conflict strategy; assuming the DB makes the app correct — *your* code must be conflict-aware.

**References**:
- AWS multi-region app architecture — https://docs.aws.amazon.com/whitepapers/latest/aws-multi-region-fundamentals/aws-multi-region-fundamentals.html
- Cloud Spanner consistency — https://cloud.google.com/spanner/docs/true-time-external-consistency
- Azure Cosmos DB multi-region writes — https://learn.microsoft.com/azure/cosmos-db/multi-region-writes

### Tenancy models

| Model | Pros | Cons |
|---|---|---|
| Single-tenant | Isolation, custom config per customer | Cost, ops overhead |
| Shared infra, isolated DB | Balance | Schema migrations harder |
| Fully shared | Cheapest, simplest | Noisy neighbor, security risk |

Multi-tenant SaaS usually picks shared infra + isolated data per tenant.

### Decisions you'll revisit

These are reversible enough to start simple:
- Specific framework / library
- Specific cloud (mostly)
- Pricing tier

These are sticky — design carefully:
- Data model
- Data residency
- Public API contract
- Identity model (auth + authz)
- Tenancy model

---

## 7. References

### Books
- **Designing Data-Intensive Applications** — Kleppmann (universal)
- **Building Evolutionary Architectures** — Ford, Parsons, Kua
- **Software Architecture: The Hard Parts** — Ford, Richards
- **Enterprise Integration Patterns** — Hohpe, Woolf (classic)
- **Release It!** — Michael Nygard (production patterns)
- **Site Reliability Engineering** — Google (free online)

### Frameworks
- **C4 Model** — c4model.com
- **AWS Well-Architected** — aws.amazon.com/architecture/well-architected/
- **Google Cloud Architecture Framework** — cloud.google.com/architecture/framework
- **Azure Well-Architected** — learn.microsoft.com/azure/well-architected/
- **TOGAF** (for enterprise context)

### Blogs / Communities
- **martinfowler.com** — Martin Fowler's blog
- **The InfoQ Architecture queue**
- **High Scalability** (oldie but goldie)
- **ThoughtWorks Technology Radar** — twice yearly trend analysis

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| Enterprise Architect | "Does this align with org-wide direction?" |
| Data Architect | "What's the data layer design?" |
| Platform Architect | "How does this consume the platform?" |
| AI Architect | "What's the AI component's place in the system?" |
| Engineers | "Here's the spec — what's missing? What can be simplified?" |
| Product Manager | "Translate requirements into NFRs and constraints" |
| Security | "What's the threat model?" |
| Ops / SRE | "What's the operational + on-call plan?" |

---

*Reference selectively. Solution architecture is breadth-first; the specifics belong to deeper specialists.*
