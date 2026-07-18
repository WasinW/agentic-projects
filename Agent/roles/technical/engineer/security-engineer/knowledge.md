# Security Engineer — Comprehensive Knowledge

> Deep reference for the security-engineer subagent — the **technical security implementer** (AppSec + cloud security + DevSecOps). Distinct from governance-consultant (policy/compliance) and devops-engineer (delivery).
>
> *Current primary cloud = **Azure** (AIA, since 2026-07). The-1 (GCP-primary, retail loyalty, Central Group) appears only as an explicitly-marked past-engagement example — never the default lens.*

---

## 1. Foundations

### What a Security Engineer does

Owns **building and operating security controls** — not writing policy, not shipping features, but making sure the things that ship are hard to compromise and easy to detect when they are. Touches: AppSec (SAST/DAST/SCA), cloud security posture, IAM design, network segmentation, encryption/KMS, secrets, vuln management, detection engineering, and security incident response.

The security engineer translates risk into **controls in code and infra** — guardrails, scans, policies-as-code, detections — that hold without a human in the loop.

### vs governance-consultant vs devops-engineer

| Role | Owns | Output | Example (The-1, past engagement) |
|---|---|---|---|
| **governance-consultant** | Policy, compliance mapping, risk acceptance | PDPA/BoT control matrices, audit evidence | "PDPA Art. 37 requires a security control here" |
| **security-engineer** (this) | Technical controls, detection, secure design | Semgrep rules, IAM policy, CSPM config, detections | "Here's the WAF rule + KMS key policy that satisfies it" |
| **devops-engineer** | Delivery pipeline, infra, reliability | CI/CD, Terraform, K8s, observability | "I'll wire your scan into the GitHub Actions gate" |

Boundary: governance says *what must be true*, security engineer makes it *technically true and verifiable*, devops *runs the pipeline it lives in*. Overlap with devops is DevSecOps — own the security stages, not the whole pipeline.

### CIA triad — the goal function

- **Confidentiality** — only authorized parties read it (encryption, IAM, masking)
- **Integrity** — data/code not tampered (signing, provenance, checksums, WORM)
- **Availability** — it's there when needed (DDoS protection, rate limits, redundancy)

Every control maps to one or more. Past-engagement example (The-1, retail loyalty): customer PII = confidentiality-heavy (PDPA); loyalty point ledgers = integrity-heavy (fraud, BoT-adjacent).

### Core principles

- **Defense in depth** — no single control is trusted; layer identity → network → app → data → runtime → detection. One layer fails, others hold.
- **Least privilege** — every identity (human, workload, service) gets the minimum it needs, time-boxed where possible. Default deny.
- **Zero trust** — never trust based on network location. Authenticate + authorize every request, every hop. "The network is hostile" as the baseline assumption.
- **Secure by default** — the easy path is the safe path. Encryption on by default, public access off by default, deny-by-default policies.

---

## 2. Mental Models / Decision Frameworks

### Threat modeling — STRIDE

For any system, walk each category and ask "how could this happen here, what stops it":

| STRIDE | Threat | Control class |
|---|---|---|
| **S**poofing | Impersonate identity | AuthN, MFA, mTLS |
| **T**ampering | Alter data/code | Signing, integrity checks, WORM |
| **R**epudiation | Deny an action | Audit logs, non-repudiation |
| **I**nfo disclosure | Leak data | Encryption, IAM, masking |
| **D**enial of service | Exhaust resources | Rate limit, quotas, autoscale |
| **E**levation of privilege | Gain more access | Least privilege, segmentation |

Do it at design time, on a data-flow diagram, focused on **trust boundaries** (where data crosses from less-trusted to more-trusted). Attack trees complement STRIDE for a *specific* high-value target: root = goal (e.g. "exfil customer PII"), branches = paths, prune by feasibility.

### Risk = Likelihood × Impact

Don't fix everything — rank. A critical CVE on an internet-facing, unauthenticated service beats a critical CVE on an air-gapped internal tool. Adjust likelihood by **exploitability + exposure** (is it reachable? is there an exploit in the wild? — EPSS score), impact by **blast radius + data sensitivity**. This is how you triage a 4,000-finding scan report into 12 things that matter this week.

### Shift-left (but don't shift-only-left)

Find issues early where they're cheap to fix — IDE, PR, CI — *and* keep runtime controls (CSPM, runtime detection) because not everything is knowable pre-deploy. "Shift-left" without runtime is half a program. Pair with **shift-right**: detection + response for what gets through.

### Blast radius & segmentation

Assume any single component will be compromised. Design so the blow-up is contained: network segments, separate accounts/projects per environment, scoped IAM roles, separate KMS keys per data domain. The question is never "can they get in" but "when they're in *here*, what else can they reach?"

### Assume-breach

Stop designing only to keep attackers out; design to **detect and limit** them once in. Drives investment toward detection engineering, segmentation, short-lived credentials, and tested IR — not just a bigger perimeter wall. Prevention + detection + response, budgeted together.

### Secure-by-default as the lever

The highest-leverage security work is making the **paved road** safe so engineers get security for free: a hardened base image, a Terraform module with encryption + private networking baked in, a service template with authn wired up. You scale security by removing decisions, not by reviewing every PR.

---

## 3. Standard Practices

### AppSec — OWASP Top 10 (2025) as the checklist

The OWASP Top 10 was refreshed (final **2025** release, Jan 2026). Know the current shape — it changed meaningfully from 2021:

- **A01 Broken Access Control** — still #1; now **absorbs SSRF**. Authz bugs (IDOR/BOLA), missing function-level checks.
- **A02 Security Misconfiguration** — jumped from #5 → #2 (cloud + IaC sprawl).
- **A03 Software Supply Chain Failures** — new/expanded from "Vulnerable Components"; dependencies, build systems, distribution.
- Plus Injection, Insecure Design, Cryptographic Failures, Authentication Failures, and a new **Mishandling of Exceptional Conditions**.
- **API Security Top 10** is a *separate* list (BOLA, mass assignment) — use it for API-heavy systems (past-engagement example: The-1's customer-profile / loyalty APIs).

### The scanning trio — SAST / DAST / SCA

| Type | What | When | Catches |
|---|---|---|---|
| **SAST** | Static analysis of source | PR / CI | Injection, hardcoded secrets, insecure patterns |
| **DAST** | Black-box against running app | Staging / pre-prod | Runtime auth bugs, misconfig, real exploitability |
| **SCA** | Dependency + license scan | PR / CI + continuous | Known CVEs in OSS, transitive vulns |

SAST = "is the code wrong"; DAST = "is the deployed thing exploitable"; SCA = "is what we imported vulnerable". You want all three; they overlap little.

### Secrets management

- Never in code, config, env files committed to Git, or CI logs. Scan for them (gitleaks, trufflehog) in pre-commit *and* CI.
- Cloud-native first (**Azure Key Vault** on the current Azure-primary stack, AIA; was **GCP Secret Manager** on the past The-1 engagement), Vault for multi-cloud / dynamic secrets.
- **Workload identity > long-lived keys** — GCP Workload Identity Federation, IAM service-account impersonation, short-lived tokens. A leaked 1-hour token beats a leaked permanent key.
- Rotate on a schedule and on suspected compromise; make rotation automated or it won't happen.

### IAM + least privilege

- Start from **deny-all**, grant narrowly, prefer roles/groups over per-user grants.
- **No long-lived keys** for workloads — federation/impersonation.
- **Time-bound elevation (JIT)** for humans needing admin; standing admin is the #1 cloud risk.
- Audit unused permissions; GCP **IAM Recommender** / AWS Access Analyzer surface over-grants. Right-size quarterly.
- Separate identities per environment; no shared service accounts across prod/non-prod.

### Network security

- **Segment** — VPC/subnet boundaries, separate projects per env, private service access. East-west traffic is not implicitly trusted (zero trust).
- **Deny-by-default** firewall/security groups; explicit allow only.
- **WAF** in front of public apps (managed rules + custom for app-specific) — Cloud Armor on GCP.
- **Private by default** — databases, internal APIs never get public IPs; reach via private connectivity (Private Service Connect, VPC peering).
- mTLS for service-to-service where the threat model warrants (service mesh).

### Encryption + key management (KMS)

- **At rest**: default cloud encryption everywhere; **CMEK** (customer-managed keys) for regulated/sensitive data so *you* control rotation and revocation — currently (AIA, Azure) that's customer-managed keys in Azure Key Vault, not platform-managed default; on the past The-1 engagement it was CMEK in GCP Cloud KMS.
- **In transit**: TLS 1.2+ everywhere, no plaintext internal hops for sensitive data.
- **Key hygiene**: separate keys per data domain (blast-radius), automatic rotation, key access logged + alerted, HSM-backed keys for the most sensitive (Cloud HSM / external key manager for crypto-shredding requirements).
- **Field/app-level** encryption or tokenization for the crown jewels (card-adjacent data) — defense beyond disk encryption.

### Vulnerability management + patching

- Continuous SCA + container scanning + CSPM, not point-in-time.
- **Triage by exploitability** (EPSS + KEV catalog + reachability), not raw CVSS. A CVSS 9.8 in unreachable code < a CVSS 7.5 actively exploited and internet-facing.
- SLAs by severity (e.g. critical-internet-facing: 24–72h; others: 30/90 days) — agree these with governance-consultant so they map to compliance.
- Patch via the **immutable path** — rebuild + redeploy, not patch-in-place (devops owns the pipeline; you own the policy gate).

### Secure SDLC

Embed controls at each stage, not a security review bolted on at the end:

```
Design   → threat model, secure-design review
Code     → secure coding, pre-commit secret scan, SAST in IDE
PR       → SAST + SCA + IaC scan as required checks
Build    → sign artifacts (Sigstore), generate SBOM + provenance
Deploy   → policy gate (admission control), CSPM baseline
Runtime  → runtime detection, drift detection, logging
Respond  → detections → IR playbook → postmortem
```

### Container / K8s security

- Minimal base (distroless/scratch), non-root, read-only root FS, drop capabilities.
- Scan images (Trivy/Grype) in CI **and** in registry continuously (new CVEs appear after build).
- **Admission control** — OPA/Gatekeeper or Kyverno to reject non-compliant pods (no privileged, no `:latest`, must have limits, signed images only).
- NetworkPolicies for pod-level segmentation (default-deny namespace).
- Pod Security Standards (restricted), no host mounts, no hostNetwork.
- **Runtime detection** — Falco/Tetragon for syscall-level anomalies.

---

## 4. Tools Landscape (2026)

### SAST / DAST
- **Semgrep** — fast (10–30s PR scans), YAML rules, OSS CLI free for commercial; best when you need org-specific custom rules. Default pick for "scan first-party code in CI".
- **Snyk Code** — DeepCode AI engine, semantic dataflow, strong remediation suggestions.
- **CodeQL** (GitHub) — deep dataflow, strong for OSS / GitHub-native.
- **DAST** — OWASP ZAP (OSS), Burp Suite (manual + pro), StackHawk / Beagle (API + business-logic, CI-friendly).

### SCA / dependencies
- **Snyk** — best-in-class SCA breadth (15M+ packages), proprietary vuln DB, **auto-fix PRs**. Default for "manage known CVEs in dependencies".
- **Dependabot / Renovate** — automated dependency bumps.
- **Trivy / Grype** — OSS, also do container + IaC.

> Common pattern: **Semgrep for custom SAST + Snyk for SCA** — they started at opposite ends (Semgrep=SAST engine, Snyk=SCA) and overlap little. Running both is normal.

### CSPM / CNAPP (the big 2025–2026 shift)
The market **consolidated** — standalone CSPM/CWPP/CIEM/DSPM tools merged into **CNAPP** (Cloud-Native Application Protection Platform). Gartner: by 2027, 60% of enterprises adopt CNAPP. Deep SOC integration now distinguishes mature CNAPPs.
- **Wiz** — CNAPP market leader; agentless, **graph-based** (the differentiator: maps attack paths across CSPM+CWPP+CIEM+DSPM). Acquired by Google (~$32B, agreed Mar 2025) — was relevant for the past The-1 engagement's GCP-primary stance; less central now that the current primary cloud is Azure (AIA).
- **Prisma Cloud → Cortex Cloud** (Palo Alto, rebranded Feb 2025) — CNAPP + CDR engine.
- **Orca, Uptycs, Aqua** — alternatives.
- **GCP Security Command Center (SCC)** — cloud-native CSPM/CNAPP for GCP-only; cheaper entry, less cross-cloud.

### IaC scanning
- **Checkov** (Prisma/Bridgecrew) — broad, many frameworks.
- **tfsec** — Terraform-focused (folding into Trivy).
- **Terrascan**, **KICS** — alternatives. Run in PR before `terraform apply`.

### Secrets
- **HashiCorp Vault** — multi-cloud, dynamic secrets, PKI, encryption-as-a-service.
- **Azure Key Vault** — cloud-native secrets on the current Azure-primary stack (AIA).
- **GCP Secret Manager** — cloud-native; was the default on the past The-1 engagement.
- **External Secrets Operator** — sync cloud secrets into K8s.
- **gitleaks / trufflehog** — secret *detection* in code/history.

### Detection / SIEM / runtime
- **Falco** (CNCF) / **Tetragon** (eBPF) — runtime threat detection in K8s.
- **Microsoft Defender / Sentinel** — cloud-native detection on the current Azure-primary stack (AIA). **GCP SCC + Chronicle** (Google SecOps SIEM) was cloud-native detection on the past The-1 engagement.
- **Wazuh** (OSS SIEM), **Elastic Security**, **Splunk ES** — alternatives.
- Detection-as-code with **Sigma** rules (vendor-neutral).

### Supply chain
- **Sigstore / Cosign** — keyless artifact signing (OIDC-backed).
- **SLSA** (v1.0 / v1.1, Apr 2025) — build provenance levels.
- **Syft** (SBOM gen), **Grype** (SBOM scan), **GUAC** (supply-chain graph).
- **Kyverno / Sigstore policy-controller** — verify signatures at admission.

### Policy-as-code
- **OPA / Rego**, **Kyverno** (K8s-native), **Gatekeeper**, Cloud org policies (GCP Org Policy / AWS SCP).

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Secrets in code / config / CI logs | Leak = instant compromise, lives in Git history forever | Secret manager + scanning + workload identity |
| Flat network, everything reachable | One foothold = total access | Segmentation, deny-by-default, zero trust |
| Security as a gate at the end | Found late = expensive, blocks releases, breeds resentment | Shift-left into PR + paved-road defaults |
| Over-permissioned IAM / standing admin | Huge blast radius, #1 cloud breach cause | Least privilege + JIT elevation + recommender |
| Alert fatigue (page on everything) | Real alerts missed in noise | Tune, risk-rank, tiered routing, detection-as-code |
| CVSS-only triage | Drowns in criticals, fixes wrong things | Exploitability (EPSS+KEV) + reachability + exposure |
| Long-lived cloud keys | Leaked key works forever | Federation / short-lived tokens |
| Encryption-at-rest = "done" | Misses app-layer, key mgmt, in-use | CMEK + field-level + tokenization for crown jewels |
| Trusting the internal network | Lateral movement unchecked | Zero trust, mTLS, authz every hop |
| Scan once, ship, forget | New CVEs appear post-build | Continuous registry + runtime scanning |
| Manual, undocumented IR | Slow, panicked, no learning | Playbooks + tabletop drills + blameless postmortem |
| Security tool sprawl, no ownership | Findings ignored, no triage | Consolidate (CNAPP), assign owners, SLAs |
| "Compliance = secure" | Checkbox passes, still breachable | Compliance is the floor; threat-model beyond it |

---

## 6. Advanced / Expert Topics

### Zero-trust architecture
Beyond the buzzword: **identity-aware proxy** in front of apps (GCP IAP / BeyondCorp), per-request authz, device posture checks, micro-segmentation, mTLS service-to-service. The network grants nothing; identity + context grants everything. Roll out incrementally — start with the most sensitive apps behind IAP, kill the VPN-as-trust model over time.

### Supply-chain security (SLSA + SBOM + provenance)
- **SLSA levels** (v1.0/v1.1): L0 none → **L1** provenance exists → **L2** signed provenance from a hosted build → **L3** hardened, non-falsifiable build platform. L2 is achievable in weeks with Cosign + GitHub OIDC.
- **SBOM** (CycloneDX / SPDX) = *what's in* the artifact. **Provenance** = *how it was built*. Complementary — SBOM for vuln response ("am I affected by X?"), provenance for integrity ("was this built from the source I think?").
- Verify at admission: only run signed images with valid provenance (Kyverno/policy-controller).
- A03:2025 making supply chain a top-3 OWASP risk reflects xz, npm, and CI-compromise incidents — this is now table stakes, not advanced.

### Cloud security per provider
| | IAM model | CSPM-native | Key gotcha |
|---|---|---|---|
| **GCP** (past The-1 engagement) | Resource hierarchy (org→folder→project), IAM bindings, **Org Policy** constraints | Security Command Center | Project-level blast radius; service-account key sprawl; default networks too open |
| **AWS** | IAM policies + SCPs, accounts as boundary | Security Hub + GuardDuty | IAM policy complexity; over-broad `*` actions; public S3 |
| **Azure** (current primary, AIA) | RBAC + Entra ID, mgmt groups | Defender for Cloud | RBAC/Entra split confusion; over-privileged app registrations |

Cross-cloud (The-1, past engagement, was multi-cloud) → a **CNAPP (Wiz)** gives one pane vs three native tools; native tools are cheaper per-cloud. Decision: single-cloud-heavy → native + targeted tooling; genuinely multi-cloud + regulated → CNAPP. Current context (AIA) is Azure-primary — native Defender for Cloud is the first-stop pick unless multi-cloud sprawl emerges.

### Detection engineering
Treat detections as code: **Sigma rules** in Git, tested against sample logs, CI-deployed to the SIEM, versioned, peer-reviewed. Map coverage to **MITRE ATT&CK** to find gaps. Measure detections by true-positive rate and time-to-detect, retire noisy ones. Cloud-native: Defender/Sentinel on the current Azure-primary stack (AIA); was GCP SCC findings + Chronicle/Google SecOps on the past The-1 engagement.

### Threat hunting
Proactive search for what detections missed — hypothesis-driven ("if an attacker were living off the land here, I'd expect X"). Pull from ATT&CK TTPs, recent threat intel, anomalies in IAM/network logs. Output feeds new detections (hunt → find → codify into a Sigma rule).

### Security for data / ML
- **Data exfil** — the dominant data-platform threat. Controls: egress restrictions (Azure Private Link / Network Security Perimeter for the current Azure-primary stack — AIA's Databricks/ADLS; was VPC-SC perimeters on GCP for the past The-1 engagement's BigQuery/data lake), DLP scanning + classification, column-level access + masking, query audit + anomaly detection. Coordinate with **data-architect** on classification.
- **Model security** — protect training data (poisoning), model artifacts (theft via signed registry), and inference endpoints (abuse, extraction).
- **LLM / prompt injection** — **OWASP LLM Top 10 (2025)**: prompt injection is #1 (direct + indirect; indirect via poisoned RAG/tool content is the hard one — LLMs don't separate instructions from data). Agentic systems (LLMs calling tools/APIs/DBs autonomously) got their **own OWASP Top 10** in late 2025 — the model's *actions* become the attack surface. Controls: treat all model output as untrusted, least-privilege the agent's tools, human-in-loop for high-impact actions, output filtering, sandboxing. **Hand the deep version to ai-engineer**; you own the *infra-side* controls (tool scoping, network egress from the agent, secrets the agent can reach).

### Incident response (security-specific)
Distinct from devops outage IR — here the system may be **actively adversarial**:
- **Prepare** — playbooks per scenario (creds leaked, ransomware, data exfil, supply-chain compromise), break-glass access, retainer with forensics if needed.
- **Detect & analyze** — scope it; assume the attacker watches your response.
- **Contain** — isolate (don't tip off prematurely), revoke creds, rotate keys, snapshot for forensics **before** wiping (evidence).
- **Eradicate & recover** — remove persistence, rebuild from known-good, validate.
- **Post-incident** — blameless, regulatory notification clock (PDPA breach notification — loop in **governance-consultant** immediately; the legal clock starts at awareness).

---

## 7. References

### Standards / frameworks
- **OWASP Top 10:2025** — https://owasp.org/Top10/2025/ ; **API Security Top 10** — https://owasp.org/API-Security/
- **OWASP GenAI / LLM Top 10 (2025)** — https://genai.owasp.org/llm-top-10/
- **NIST CSF 2.0** (Feb 2024; new **Govern** function, 6 functions) — https://www.nist.gov/cyberframework
- **NIST SP 800-53 Rev. 5** — control catalog; **SP 800-61** (incident handling)
- **CIS Benchmarks** + **CIS Controls v8** (18 controls) — https://www.cisecurity.org/
- **SLSA v1.0/v1.1** — https://slsa.dev/ ; **Sigstore** — https://www.sigstore.dev/
- **MITRE ATT&CK** — https://attack.mitre.org/ ; **MITRE ATLAS** (AI threats) — https://atlas.mitre.org/
- **EPSS** — https://www.first.org/epss/ ; **CISA KEV** — https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- **PDPA** (Thailand) + **BoT** notices — map via governance-consultant

### Books
- **The Web Application Hacker's Handbook** — Stuttard, Pinto
- **Threat Modeling: Designing for Security** — Adam Shostack
- **Security Engineering** — Ross Anderson (free online)
- **Practical Cloud Security** — Chris Dotson
- **Building Secure and Reliable Systems** — Google (free)
- **Container Security** — Liz Rice

### Communities
- **OpenSSF** (supply chain), **CNCF security TAG**, **Cloud Security Alliance**

---

## 8. Working With Other Roles

| Role | Handoff / boundary |
|---|---|
| **governance-consultant** | They map controls to PDPA/BoT/ISO; I implement + produce evidence. Breach → they own notification clock, I own technical IR. Risk acceptance is theirs; control design is mine. |
| **devops-engineer** | I define the security pipeline stages (SAST/SCA/IaC gates, signing, admission control); they own the pipeline + infra it runs in. DevSecOps = our shared surface. |
| **cloud experts (GCP / AWS / Azure)** | Per-cloud IAM, CSPM, encryption, network specifics. Azure expert is primary for the current engagement (AIA — Defender for Cloud, Entra ID, Private Link, Key Vault CMK); GCP expertise (SCC, Org Policy, VPC-SC, CMEK) reflects the past The-1 engagement. I set the security *bar*; they implement per-cloud. |
| **ai-engineer** | LLM/agent security — they own model behavior + prompt-injection defenses in the app; I own infra controls (tool scoping, egress, secrets, sandboxing). OWASP LLM Top 10 is shared ground. |
| **data-architect** | Data classification, column-level access, masking, VPC-SC perimeters, exfil controls. They model the data; I secure its movement + access. |
| **software-engineer** | Secure coding, fixing SAST/SCA findings, threat-model participation. I give paved-road defaults + rules; they build on them. |

---

*Security engineering in 2026 = controls as code, assume-breach, consolidate the tools (CNAPP), and make the safe path the easy path. Compliance is the floor, not the goal — threat-model past it.*
