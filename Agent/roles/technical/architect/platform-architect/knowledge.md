# Platform Architect — Comprehensive Knowledge

> Deep reference for the platform-architect subagent.

---

## 1. Foundations

### What a Platform Architect does

Designs **internal platforms** that other engineers consume to build products faster, more safely, more consistently.

A platform is **not infrastructure**. It's a curated set of capabilities + interfaces + opinions + guardrails that turn "you can use AWS" into "your team can ship a service in a day."

### The Core Insight

> If every new use case requires the platform team's involvement, it's not a platform — it's a service bureau.

The metric for platform success is **autonomous adoption**, not uptime.

### What a platform offers (the capability map)

A real platform offers some subset of:
- **Compute** — run my code (containers, functions, jobs)
- **Storage** — persist my data (DB, object, queues, caches)
- **Networking** — connect services + clients
- **Identity + access** — who can do what
- **Observability** — see what's happening
- **Build + deploy** — CI/CD as a service
- **Data + ML platform** — pipelines, features, models
- **Developer experience** — portal, CLI, templates, docs
- **Cost + budget** — visibility + control
- **Governance** — policy, audit, compliance

Pick what your org needs. Don't build the union of everyone else's capabilities.

### Adjacent roles

- **Enterprise Architect** — sets capability strategy, you implement
- **Solution Architect** — consumes the platform to build solutions
- **Platform Engineers** — build + operate
- **Developer Experience** — usability, docs, onboarding

---

## 2. Mental Models / Decision Frameworks

### Platform as a Product

The most influential mental model from the Team Topologies / IDP movement:
- Internal teams are your **users**
- They have alternatives (build it themselves, use raw cloud)
- You need to win adoption — not mandate it
- Treat the platform like a SaaS product: roadmap, metrics, marketing internally

### Cognitive Load (from Team Topologies)

A platform exists to **reduce extraneous cognitive load** on stream-aligned teams so they can focus on solving the business problem.

If using the platform is more painful than using raw cloud, the platform is failing its mission.

### Golden Paths

The **opinionated, supported, blessed way** to do common things.
- Heroku: golden path is `git push heroku main`
- Internal example: golden path for a new service = scaffold from template → deploy via CI → observe via standard dashboards

Side-paths exist but get no support guarantees.

### Stream-Aligned vs Platform Teams (Team Topologies)

| Team type | Optimizes for |
|---|---|
| Stream-aligned | Fast flow of value to specific business stream |
| Platform | Reduce cognitive load for stream-aligned teams |
| Enabling | Help stream-aligned teams adopt new tech |
| Complicated subsystem | Owned by specialists; black-box to others |

Platform team = optimizes for the **velocity** of stream-aligned teams, not its own velocity.

### Decision: thin vs thick platform

| Thin platform | Thick platform |
|---|---|
| Provides primitives | Provides workflows |
| "Here's a Kubernetes cluster" | "Here's a deploy command" |
| Flexible, high cognitive load | Opinionated, low cognitive load |
| Engineers love it; PM-types don't use it | PM-types love it; power-users feel constrained |

Most successful internal platforms are **thick by default, thin escape hatches available**.

### Decision: who owns operations?

| Model | Pros | Cons |
|---|---|---|
| **Platform team operates everything** | Consistent ops, app teams focus on logic | Platform team is bottleneck, app teams lose ownership |
| **You build it, you run it** | Strong ownership, fast iteration | App teams need ops skills, inconsistent ops |
| **Hybrid (you build, platform runs)** | Best of both | Communication overhead at the seam |

Modern trend: thin shared platform + you-build-you-run with great platform observability.

### Multi-tenancy strategy

Platforms always have multi-tenancy. Decisions:
- Isolation level (process / VM / cluster / cloud account)
- Quota + fair-use enforcement
- Noisy neighbor handling
- Cost attribution per tenant
- Tenant-specific config + secrets

### Capability vs feature

- **Capability** = a thing the platform can do (deploy a service, run a query, send a metric)
- **Feature** = a specific way it does it (push-based CI/CD vs pull-based)

Capabilities are stable; features evolve. Communicate capabilities to consumers; iterate on features internally.

---

## 3. Standard Practices

### IDP (Internal Developer Platform) pattern

The 2025-2026 movement: present capabilities through a **developer portal** (Backstage is the leader).

```
[Developer]
   ↓ asks portal for...
[Portal: Backstage / Port / Compass]
   ↓ orchestrates
[Capabilities: deploy, scaffold, manage secrets, observe, etc.]
   ↓ implemented by
[Underlying tech: K8s, Terraform, CI/CD, observability]
```

### Self-service interface levels

```
LEVEL 1: Documentation only ("here's how to do it yourself")
LEVEL 2: CLI tooling
LEVEL 3: Web portal
LEVEL 4: API / SDK (programmable)
LEVEL 5: Auto-orchestrated (the platform decides + executes)
```

Most platforms target Level 3 + Level 4.

### Service catalog

The list of "things you can ask the platform for" — typically in Backstage or similar:
- Templates ("scaffold a new microservice")
- Services (existing ones, with owners, dependencies, on-call)
- Resources (DBs, queues, buckets — provisioned + tracked)
- APIs (with docs, schema, usage)

### Paved roads vs trail markers

- **Paved roads** — fully supported, recommended, documented
- **Trail markers** — sometimes supported, "here be dragons"
- **Off-road** — at your own risk, no support

Be explicit about which is which. Don't claim everything is supported.

### Cost attribution

Every resource provisioned via the platform should be:
- Tagged with team / cost-center / environment / purpose
- Visible in a per-team cost dashboard
- Subject to budgets + alerts

Without attribution, cost optimization is impossible.

### Observability standards

Define + enforce:
- Required metrics (RED: rate, errors, duration; USE: utilization, saturation, errors)
- Standard log format + tagging
- Standard tracing context propagation (OpenTelemetry)
- Default dashboards + alerts

Make the easy path the right path.

### Policy as code

- **OPA (Open Policy Agent)** — generic policy engine
- **Sentinel** (HashiCorp) — Terraform-native
- **Kyverno / Gatekeeper** — Kubernetes policy

Enforce: required tags, image source restrictions, resource limits, network rules.

### Migration strategy

When you change platform capabilities, existing consumers must migrate. Plan for:
- Deprecation timeline (typically 6-12 months for breaking changes)
- Automated migration tools where possible
- Office hours / help during migration
- Sunset enforcement (block new usage, then block all)

---

## 4. Tools Landscape (2026)

### Developer Portals
- **Backstage** (Spotify, CNCF) — most popular, open source, heavy customization
- **Port** — commercial, lower setup
- **Cortex** — commercial, service catalog focus
- **Compass** (Atlassian) — for Atlassian shops

### IaC
- **Terraform / OpenTofu** — most common; OpenTofu is the OSS fork
- **Pulumi** — code instead of HCL
- **CDK (AWS / Terraform CDK)** — language-native

### Kubernetes platform
- **Argo CD** — GitOps deployment
- **Flux** — GitOps alternative
- **Crossplane** — provision cloud resources via K8s API
- **KCL / cdk8s** — config languages

### CI/CD
- **GitHub Actions** — ubiquitous
- **GitLab CI** — strong, integrated
- **Jenkins** — legacy but everywhere
- **CircleCI / Buildkite** — commercial alternatives

### Service mesh (when needed)
- **Istio** — full-featured, complex
- **Linkerd** — simpler, Rust-based
- **Cilium** — eBPF-based, network + observability

### Observability
- **Prometheus + Grafana** — open metrics + dashboards
- **Tempo / Jaeger / Zipkin** — distributed tracing
- **Loki / OpenSearch** — log aggregation
- **Datadog / New Relic / Honeycomb** — commercial all-in-one

### Identity
- **Auth0 / Okta / Entra ID** — commercial identity providers
- **Keycloak** — open source
- **SPIFFE / SPIRE** — workload identity standard

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Platform is everyone's hobby project | No ownership, inconsistent | Dedicated team with PM |
| Platform team builds in isolation | Wrong abstractions, low adoption | Embed with consumer teams; user research |
| Mandate without value | Teams find workarounds | Earn adoption via usefulness |
| Same platform for every tier | Over-engineered for small needs, under-powered for big | Tiered offerings |
| No deprecation discipline | Tech debt accumulates | Sunset capabilities with clear timeline |
| Hidden cost | Teams use platform until bill arrives | Real-time cost visibility per tenant |
| Documentation as an afterthought | Adoption fails | Docs as first-class deliverable |
| Platform team owns the on-call | Bottleneck, doesn't scale | You build it, you run it — platform provides observability |
| One golden path that doesn't fit some teams | Forced workarounds | Multiple golden paths; user research |

---

## 6. Advanced / Expert Topics

### Backstage deep

The dominant developer portal. Key concepts:
- **Catalog** — entities (component, system, API, resource, group, user) with relationships
- **Software templates** — scaffold new things
- **Plugins** — extend functionality
- **TechDocs** — markdown-as-docs from the same repo

Backstage is heavyweight to operate. Have a dedicated team or buy managed (Spotify Backstage Plus, Roadie, others).

### Platform engineering vs DevOps

DevOps = culture + practice (you write code + run it)
Platform engineering = providing tools to make DevOps practical at scale

DevOps without platform engineering = each team reinvents
Platform engineering without DevOps culture = bureaucratic blockers

### Measuring platform success

| Metric | What it tells you |
|---|---|
| Adoption rate | % teams using platform |
| Time-to-first-deploy | New service → production |
| Time-to-restore | Incident response speed |
| Platform NPS | User satisfaction |
| Self-service rate | % requests not needing platform team intervention |
| Cost per tenant | Efficiency over time |
| Deprecation completion rate | Tech debt management |

### Multi-cluster, multi-region, multi-cloud

Each level adds complexity:
- **Multi-cluster** — workload distribution within a cloud
- **Multi-region** — DR + global latency
- **Multi-cloud** — vendor leverage + compliance, comes with abstraction tax

Most enterprises shouldn't be multi-cloud for the same workload. Multi-cloud across workloads is fine.

### Internal marketplace

Some advanced platforms expose:
- An app store of templates + services
- Discovery + search
- Cost calculator before provisioning
- Approval workflows for sensitive resources

This is Internal Developer Platform Level 5+ — only worth it at scale.

### Policy enforcement layers

```
Design time — schema validation, IaC linting
Build time — CI checks, dependency scanning
Deploy time — admission controllers, OPA
Runtime — monitoring, anomaly detection, sandbox boundaries
```

Defense in depth: don't rely on a single layer.

---

## 7. References

### Books
- **Team Topologies** — Skelton, Pais (organizational design)
- **Platform Strategy** — Geoffrey Parker (broader platform business model)
- **The DevOps Handbook** — Kim, Humble, Debois, Willis
- **The Phoenix Project** + **The Unicorn Project** — Kim (narrative)
- **Accelerate** — Forsgren, Humble, Kim (research-backed practices)

### Frameworks + standards
- **CNCF Landscape** — what's out there in cloud native
- **OpenTelemetry** — observability standard
- **OpenAPI** — API specs
- **Backstage docs** — backstage.io
- **CDK / Crossplane** for provisioning

### Communities
- **Platform Engineering Community** (Slack, conferences)
- **Internal Developer Platform** (internaldeveloperplatform.org)
- **Team Topologies Academy**
- **CNCF events** (KubeCon, etc.)

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| Enterprise Architect | "How does platform serve strategic capabilities?" |
| Solution Architect | "Which platform capabilities does this solution use?" |
| Stream-aligned engineers | "What's missing for you to be self-sufficient?" |
| Platform engineers | "Build vs buy for this capability?" |
| Security | "How do we enforce policy across all tenants?" |
| Finance | "Cost attribution + showback model?" |

---

*Platforms succeed via adoption. Build what they want, not what you think they should want.*
