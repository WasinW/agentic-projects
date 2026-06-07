# DevOps Engineer — Comprehensive Knowledge

> Deep reference for the devops-engineer subagent.

---

## 1. Foundations

### What a DevOps Engineer does

Owns the path from **code in Git to running in production**, the infrastructure underneath, and the feedback loops back to developers. Touches: CI/CD, IaC, Kubernetes, observability, security, supply chain.

### The DevOps movement (origin)

Pre-DevOps: Dev throws code over the wall to Ops. Ops gets paged. Antagonism.

DevOps culture: shared ownership, automated everything, fast feedback, blameless culture.

Today the term is bloated; many "DevOps engineers" are really **platform / infra / SRE engineers**.

### Closely related roles

- **SRE** (Google) — engineering applied to ops; SLO + error budget
- **Platform Engineer** — builds Internal Developer Platforms
- **Cloud Engineer** — cloud-specific infra
- **Security Engineer** — DevSecOps overlap

---

## 2. Mental Models / Decision Frameworks

### The CALMS model (DevOps culture)

- **Culture** — shared ownership, blameless
- **Automation** — toil reduction
- **Lean** — flow over busywork
- **Measurement** — DORA metrics (deploy frequency, lead time, MTTR, change failure rate)
- **Sharing** — knowledge + tools

### Everything as Code

- Infrastructure as Code (Terraform)
- Configuration as Code (Ansible, Helm)
- Policy as Code (OPA)
- Pipelines as Code (GitHub Actions YAML)
- Documentation as Code (Markdown + docs sites)

If it's not in Git, it doesn't exist.

### GitOps

- Desired state in Git
- Reconciliation operator continuously aligns running state
- Pull-based (cluster pulls config) over push-based
- ArgoCD / Flux are the standards

### Immutable infrastructure

- Build artifacts (containers, AMIs) — never mutate
- Replace, don't patch
- Logging + monitoring as the change observability

### Defense in depth (security)

- Identity / IAM
- Network segmentation
- Application boundaries
- Encryption at rest + in transit
- Supply chain (sign artifacts, verify)
- Runtime detection (Falco, runtime monitoring)
- Least-privilege everywhere

### Observability is non-negotiable

Three pillars (metrics, logs, traces) + ahead-of-curve practices:
- SLO + error budget management
- Continuous profiling
- eBPF-based observability (Cilium, Pixie)
- Distributed tracing (OpenTelemetry)

If you can't see it, you can't fix it.

### Reversible vs irreversible deploys

- Reversible: blue/green, canary, feature flags
- Irreversible: DB migrations (forward-only), one-way doors
- Treat irreversible carefully: pre-prod test, manual approval, runbook

### Cost as a discipline

- Tagging mandatory (team, env, project)
- Showback / chargeback to teams
- Budget alerts before bills hit
- Spot / preemptible for retryable workloads
- Right-sizing reviews quarterly

---

## 3. Standard Practices

### CI/CD pipeline standard stages

```
Commit
  ↓
[Lint + Format]
  ↓
[Unit tests]
  ↓
[Security scan — SAST]
  ↓
[Dependency scan — SCA]
  ↓
[Build artifact — container, package]
  ↓
[Push to registry with tag]
  ↓
[Integration tests]
  ↓
[Deploy to staging]
  ↓
[E2E tests]
  ↓
[Deploy to production — canary / blue-green]
  ↓
[Smoke tests]
  ↓
[Promote / rollback]
```

### Terraform best practices

- Modules — reusable, versioned
- Remote state — S3/GCS with locking
- Workspaces for envs (or separate state files)
- `terraform plan` review in PR
- Atlantis or similar for automation
- Don't put secrets in state — use Vault / SOPS / cloud secrets

### Kubernetes essentials

- Pod, Deployment, Service, Ingress
- Namespaces for isolation
- ResourceQuota / LimitRange for fairness
- RBAC for access
- NetworkPolicies for segmentation
- HPA / VPA for scaling
- Operators / CRDs for complex apps

### Observability stack (modern OSS)

- **OpenTelemetry** — instrumentation standard
- **Prometheus** — metrics
- **Grafana** — dashboards
- **Loki** — logs (Prometheus-style)
- **Tempo / Jaeger** — traces
- **Alertmanager** — routing

Or all-in-one commercial: Datadog, New Relic, Honeycomb.

### Container security

- Minimal base images (distroless, alpine, scratch)
- Sign images (Cosign / Sigstore)
- Scan vulnerabilities (Trivy, Grype, Snyk)
- Don't run as root
- Read-only filesystem where possible
- SBOM (Software Bill of Materials)

### Secrets management

- Never in code
- Cloud-native (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault)
- HashiCorp Vault for multi-cloud
- External Secrets Operator for K8s
- Workload identity > long-lived credentials

### Deployment strategies

| Strategy | Use |
|---|---|
| Recreate | Dev, tolerable downtime |
| Rolling | Default; gradual replacement |
| Blue-green | Quick rollback; doubles infra briefly |
| Canary | Gradual % shift, monitor metrics |
| Feature flags | App-layer control |
| Shadow | Test new without affecting users |

### Incident response

- Detect (alerts)
- Triage (severity, on-call)
- Mitigate (rollback, scale, redirect)
- Resolve (root cause fix)
- Postmortem (blameless, action items)
- Track action items to completion

### Hot-fix in production (without full redeploy)

When prod is broken and the normal pipeline (PR → CI → staging → canary) is too slow, you need a fast path that stays auditable.

- **Rollback beats hot-fix** — if a known-good artifact exists, redeploy it (or `kubectl rollout undo`, revert the Git SHA in GitOps). Fastest, lowest-risk. Hot-fix only when there's nothing good to roll back to.
- **Roll forward, don't edit live** — with immutable infra + GitOps, the legit hot-fix is a tiny PR fast-tracked through an expedited pipeline, not `kubectl edit` on a live resource (which drifts from Git and gets reverted by the reconciler).
- **Object-level scope** — redeploy only the broken unit: one service, one Helm release, one Terraform target (`-target`, used sparingly), one Lambda alias shift — not the whole stack.
- **Feature-flag kill switch** — the fastest "hot-fix" is often flipping a flag (LaunchDarkly / config) to disable the broken path with zero deploy. Design risky changes behind flags so this is possible.
- **Break-glass procedure** — emergency access/change with reduced approval but mandatory audit trail: ticket, reason, time-boxed elevated permissions (JIT), two-person rule. Reduced gate, never reduced record.

**After**: open a follow-up PR to land the fix through the normal pipeline (a hot-fix outside Git = config drift); add the missing test/alert; post-incident review if SEV1/2.

**Anti-patterns**: `kubectl edit`/SSH-and-patch with no Git change; disabling CI to "push faster"; hot-fix that never gets promoted to main; standing admin access used as the break-glass path.

### SRE practices

- SLI (indicator) — what to measure (latency, errors)
- SLO (objective) — target (99.9%)
- Error budget — allowed unreliability
- Toil reduction — automate repetitive work
- Production readiness reviews

---

## 4. Tools Landscape (2026)

### IaC
- **Terraform / OpenTofu** — standard
- **Pulumi** — code (Python, TS, Go)
- **CDK** (AWS / Terraform CDK) — language-native
- **Crossplane** — K8s-as-IaC

### CI/CD
- **GitHub Actions** — ubiquitous
- **GitLab CI** — strong
- **Jenkins** — legacy but everywhere
- **CircleCI / Buildkite / Drone** — alternatives

### Container orchestration
- **Kubernetes** — dominant
- **ECS / Fargate** — AWS-native simpler
- **Cloud Run / Container Apps** — serverless containers
- **Nomad** — alternative
- **Docker Swarm** — niche today

### Service mesh
- **Istio** — full features, complex
- **Linkerd** — simpler, Rust
- **Cilium** — eBPF-based, network + observability
- **Consul Connect** — HashiCorp ecosystem

### GitOps
- **ArgoCD** — most popular
- **Flux** — CNCF alternative
- **Jenkins X** — Jenkins-flavored

### Observability
- **Datadog / New Relic / Dynatrace** — commercial APM
- **Grafana stack** (LGTM) — OSS
- **Honeycomb** — observability-driven dev
- **Splunk** — enterprise

### Security
- **Trivy / Grype** — vuln scanning
- **Snyk / Dependabot** — SCA
- **OPA / Kyverno / Gatekeeper** — policy
- **Falco** — runtime security
- **Vault / SOPS** — secrets

### Cost
- **Infracost** — IaC cost estimation
- **CloudHealth / Cloudability / Vantage** — running cost
- **OpenCost / KubeCost** — K8s cost

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Snowflake servers | Drift, can't reproduce | Immutable infra |
| Manual deploys | Slow, error-prone | CI/CD automation |
| Secrets in code/config | Exposure risk | Secrets manager |
| One giant Terraform state | Slow plans, conflicts | Modular state |
| Everyone is admin | Security risk | RBAC + least privilege |
| Monitoring as afterthought | Find issues from users | Observability first |
| No SLOs | Don't know what good is | SLI/SLO + error budget |
| Always page on warning | Alert fatigue | Tiered alerting |
| YOLO Kubernetes | Misconfig everywhere | Helm + linters + OPA |
| Ignoring supply chain | Compromise risk | Sign + scan + SBOM |
| Single point of failure | Outages | Redundancy + chaos testing |
| No runbooks | Slow incident response | Runbook per alert |

---

## 6. Advanced / Expert Topics

### eBPF revolution

eBPF lets safe userspace programs run in kernel:
- Cilium (networking)
- Pixie (observability)
- Tetragon (security)
- Lower overhead than sidecars

Will likely replace service-mesh sidecars for many cases.

### Multi-cluster patterns

- Federation (legacy)
- Cluster mesh (Cilium)
- Multi-cluster service discovery
- Cross-cluster traffic management

### Progressive delivery

Beyond canary:
- Flagger / Argo Rollouts — automated metric-based promotion
- Feature flags as decoupling layer (LaunchDarkly, Unleash, Flagsmith)
- Experimentation platforms

### Platform engineering

Treat developer experience as a product:
- IDP (Backstage, Port, Compass)
- Golden paths
- Self-service everything
- Reduce cognitive load (Team Topologies)

### FinOps practice

- Cost allocation + showback
- Reserved/Committed/Savings plans
- Spot strategy
- Right-sizing automation
- Carbon awareness

### Supply chain security

- Sigstore / Cosign for signing
- SLSA framework for build provenance
- SBOM (CycloneDX, SPDX)
- Sigstore policy controller
- Reproducible builds

### Chaos engineering

- Hypothesis-driven failure injection
- Tools: Chaos Mesh, Litmus, Gremlin
- Game days
- Auto-resilience testing in CI/CD

### GitOps at scale

- ApplicationSets (ArgoCD)
- App-of-apps pattern
- Helm + Kustomize layering
- Multi-tenancy with projects

### Object-level redeploy / rollback

**What/why**: Rolling back *one unit* — not nuking the whole stack. When a single service regresses, you want the smallest reversible action that restores known-good state with the least blast radius and fastest MTTR. Each object type has its own rollback verb and its own state-recovery caveats.

**Mechanics per object type**:
- **K8s Deployment** — `kubectl rollout undo deployment/foo --to-revision=N`. Re-points to a prior ReplicaSet template. Stateless only; nothing rolls back PVC data or external side effects.
- **Helm release** — `helm history foo` → `helm rollback foo N`. Reverts the rendered manifest set as one transaction. Caveat: Helm hooks (jobs, migrations) re-run.
- **Argo CD / Flux (GitOps)** — never `kubectl edit` live; `git revert <sha>` and let the reconciler converge. Argo also has `argocd app rollback foo N`, but it drifts from Git and gets auto-reverted unless you also revert Git — so **revert in Git is the canonical path**.
- **Lambda** — shift the alias back to the prior version (`update-alias --function-version`), or roll back weighted alias routing. Instant, no rebuild; versions are immutable.
- **Terraform** — `-target=module.foo` to apply only the affected resource (use sparingly; bypasses full-graph consistency). True "rollback" = revert the `.tf` + re-apply, since state moves forward only.
- **dbt model** — re-run the single model (`dbt run --select foo+`) from the prior Git SHA; no global rebuild.

**State recovery is the hard part**: code rolls back cleanly; **data does not**. This is why **DB migrations follow expand-contract** — Expand (add new column/table, backward-compatible), dual-write + backfill, then Contract (drop old) only once nothing reads it. Each step is independently deployable and reversible under the N/N-1 rule (new code works with old schema and vice versa). A forward-only/destructive migration is a **one-way door** — you cannot `rollout undo` your way out of a dropped column.

**Anti-patterns**: rolling back app code while leaving a contracted (destroyed) schema; `kubectl edit` on GitOps-managed objects; `-target` as a routine workflow; assuming `rollout undo` recovers data.

**Tools (2025-2026)**: Argo Rollouts (`undo`), Helm 3, Argo CD / Flux, AWS Lambda weighted aliases, Atlantis for targeted plans. Refs: [kubectl rollout undo](https://kubernetes.io/docs/reference/kubectl/generated/kubectl_rollout/kubectl_rollout_undo/), [Expand and Contract pattern](https://www.tim-wellhausen.de/papers/ExpandAndContract/ExpandAndContract.html).

### OpenTelemetry instrumentation patterns

**What/why**: OTel is the vendor-neutral standard for traces, metrics, and logs. Generic "use OTel" is not enough — the value is in *how* you instrument, correlate signals, and shape the pipeline so you keep the useful data and drop the noise without losing failures.

**Patterns + when**:
- **Auto first, manual where it matters** — zero-code auto-instrumentation (Java agent, Node/Python/.NET/Go) gives you HTTP/DB/RPC spans for free; add **manual spans** for business logic, custom retrieval/eval paths, or frameworks lacking an instrumentor. Start auto, enrich manually.
- **Signal correlation** — propagate W3C `traceparent`; inject `trace_id`/`span_id` into structured logs; attach **exemplars** to metrics so a latency spike on a histogram links straight to an offending trace. Consistent `service.name` and resource attributes are what stitch the three pillars together.
- **Collector pipeline** — run the **OTel Collector** (agent on each node + gateway tier) as `receivers → processors → exporters`. Key processors: `batch`, `memory_limiter`, `resource`/`attributes` for enrichment, `tail_sampling`. Apps export OTLP to the Collector, not directly to the backend, so you can re-route vendors without touching app code.
- **Sampling** — **head sampling** (decide at span start, cheap, stateless) vs **tail sampling** (decide after the full trace assembles, in the gateway Collector). Standard policy: keep 100% of error/slow traces + ~10% of successes. Tail sampling needs all spans of a trace at one Collector instance (load-balancing exporter by trace ID).
- **Semantic conventions** — use the standard attribute names (`http.request.method`, `db.system`, `service.name`, plus GenAI conventions for LLM/agent spans) so backends auto-understand your data. Don't invent ad-hoc keys.

**Anti-patterns**: app exports straight to a vendor (lock-in, no central control); head-sampling away errors; cardinality bombs from unbounded attribute values; inconsistent `service.name` breaking correlation; reinventing attribute names.

**Tools (2025-2026)**: OTel Collector (contrib), language SDKs + auto-instrumentation agents, OpenTelemetry Operator (K8s auto-injection), backends Tempo/Jaeger, Prometheus, Loki, Grafana, Honeycomb, SigNoz. Refs: [OTel Instrumentation](https://opentelemetry.io/docs/concepts/instrumentation/), [Collector configuration](https://opentelemetry.io/docs/collector/configuration/).

---

## 7. References

### Books
- **The Phoenix Project + The Unicorn Project** — Gene Kim
- **The DevOps Handbook** — Kim, Humble, Debois, Willis
- **Accelerate** — Forsgren, Humble, Kim
- **Site Reliability Engineering** — Beyer et al. (free)
- **Infrastructure as Code** — Kief Morris
- **Kubernetes Patterns** — Ibryam, Huss

### Communities / Standards
- **CNCF** — Cloud Native Computing Foundation landscape
- **OpenTelemetry** — observability standard
- **OpenSSF** — open source security foundation
- **SLSA** — supply chain levels for software artifacts

### Blogs
- **Google SRE Books** (free online)
- **AWS / GCP / Azure architecture centers**
- **Hashicorp blog**
- **CNCF blog**

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| Platform Architect | Capability + IDP design |
| Solution Architect | Deployment + ops plan |
| Software Engineer | CI/CD + observability + on-call |
| Data Engineer | Pipeline orchestration infra |
| ML Engineer | Model serving infra |
| Security | DevSecOps integration |
| Finance | Cost optimization |
| Cloud experts | Cloud-specific best practices |

---

*DevOps in 2026 = software engineering applied to infrastructure + ops. Be a software engineer first.*
