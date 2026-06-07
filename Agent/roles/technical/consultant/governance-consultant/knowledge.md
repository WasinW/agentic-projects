# Governance Consultant — Comprehensive Knowledge

> Deep reference for the governance-consultant subagent.
> Privacy, compliance, audit, AI regulation.

---

## 1. Foundations

### What a Governance Consultant does

Translates **regulations + policies** into **engineering controls + processes**. Sits between legal/compliance + engineering. Owns: data classification, access policy, audit trails, lineage, retention, emerging AI regulation.

### The compliance translation challenge

Compliance teams speak: "We need to comply with GDPR Article 17."
Engineers need: "User can request deletion via API, system deletes within 30 days, audit log records the deletion."

The governance consultant bridges the gap.

### Major regulation regimes (2026)

**Privacy**
- **GDPR** (EU) — strictest globally; the model others copy
- **PDPA** (Thailand, Singapore) — GDPR-inspired
- **CCPA / CPRA** (California) — US state-level
- **LGPD** (Brazil) — Portuguese GDPR

**Banking + Finance**
- **BoT** (Bank of Thailand) — IT risk + outsourcing
- **MAS** (Singapore) — technology risk management
- **PCI-DSS** — card data
- **Basel III/IV** — operational risk
- **SOX** — financial reporting

**Healthcare**
- **HIPAA** (US)
- **PDPA** with sensitive data provisions

**AI specific (emerging)**
- **EU AI Act** — high-risk AI obligations from 2026+
- **NIST AI Risk Management Framework** — voluntary
- **Singapore Model AI Governance Framework**
- **Thailand National AI Ethics Guidelines** (developing)

**Industry-agnostic**
- **ISO 27001** — information security management
- **SOC 2** — service organization controls

---

## 2. Mental Models / Decision Frameworks

### The 7 GDPR / PDPA principles (universal)

1. **Lawfulness, fairness, transparency**
2. **Purpose limitation**
3. **Data minimization**
4. **Accuracy**
5. **Storage limitation**
6. **Integrity + confidentiality** (security)
7. **Accountability**

Memorize. Every privacy regulation maps to these.

### Data classification scheme

Most orgs use 4 levels:
- **Public** — no harm if disclosed (marketing material)
- **Internal** — for employees only
- **Confidential** — limited internal access
- **Restricted / Highly Confidential** — sensitive (PII, secrets, IP)

Each level has minimum controls (encryption, access, logging).

### Lawful basis for processing personal data

Each processing activity needs one:
1. **Consent**
2. **Contract** (necessary for performance)
3. **Legal obligation** (required by law)
4. **Vital interests** (life or death)
5. **Public interest** (government function)
6. **Legitimate interest** (balanced against rights)

Consent is the riskiest (can be withdrawn). Prefer contract or legitimate interest when applicable.

### Defense in depth (security)

- **Identity** (who you are)
- **Authentication** (proving identity)
- **Authorization** (what you can do)
- **Encryption** (at rest, in transit, in use)
- **Audit** (what happened)
- **Detection** (anomaly, intrusion)
- **Response** (incident process)

A single layer is insufficient.

### Shift-left vs shift-right governance

- **Shift-left**: build controls into design + dev (preferred)
- **Shift-right**: catch issues in production (necessary fallback)

Both required. Shift-left is cheaper but doesn't catch everything.

### Risk-based approach

Not all data is equal. Apply controls proportional to:
- Sensitivity (PII vs public)
- Volume (1 record vs millions)
- Access pattern (rare vs broad)
- Regulatory regime

Don't gold-plate everything. Don't under-protect anything sensitive.

---

## 3. Standard Practices

### Data inventory

Maintain:
- Where data lives (systems, tables, files)
- What it contains (categories, sensitivity)
- Who can access (groups, roles)
- How long it's kept (retention)
- Where it flows (lineage)
- Who owns it (steward)

Tools: data catalog (DataHub, Atlan, Collibra, Purview, Dataplex).

### PII handling

- **Discovery** — DLP scanning, classification ML
- **Pseudonymization** — replace with token (reversible by key)
- **Anonymization** — irreversibly remove identifying info
- **Masking** — show only partial (e.g., `***-***-1234`)
- **Encryption** — at rest + in transit + key management

Use Microsoft Presidio, AWS Macie, GCP Sensitive Data Protection for automated detection.

### Right of access (GDPR Article 15)

User asks for all their data. You must:
- Identify all systems containing it (lineage helps!)
- Extract + provide in portable format (often within 30 days)
- Include processing purposes, recipients, retention period

Engineering needs: identity lookup across services, data export pipelines.

### Right to erasure (GDPR Article 17)

User asks for deletion. You must:
- Delete from all systems (production, backups, derivatives, logs!)
- Within reasonable timeframe (30 days typical)
- Confirm to user
- Exceptions: legal obligation to retain (tax records, etc.)

Hardest engineering challenge: backups + ML training datasets + log archives.

Pattern: "tombstone" deletion request, age out from backups over the next backup cycle, document the policy.

### Right to data portability (GDPR Article 20)

User exports their data in machine-readable format (JSON, CSV).

Engineering: data export API, scheduled async job, secure download link.

### Data Processing Agreements (DPAs)

Required when sharing data with third parties (cloud providers, SaaS):
- Define purpose, duration, security measures, sub-processors
- Cross-border transfer mechanisms (SCCs, BCRs)
- Audit rights

Cloud provider DPAs (AWS, GCP, Azure) are usually acceptable as-is.

### Audit logging requirements

- **Tamper-resistant** (append-only, hash chain ideal)
- **Comprehensive** (data access, schema changes, admin actions)
- **Retained** (regulatory requirement — often 7+ years for banking)
- **Reviewable** (searchable + queryable)
- **Protected** (audit logs are sensitive)

Industry tools: SIEM (Splunk, Sentinel), cloud-native audit (CloudTrail, Audit Logs).

### Data residency

Some regulations require data stays in country/region:
- PDPA Thailand: prefer Thai region
- GDPR: prefer EU region + watch for cross-border to "adequate" countries
- China: data must stay in China (PIPL)

Design: regional data partitioning at app + storage layer.

### Retention + deletion policy

For each data category:
- Retention period (years)
- Deletion trigger (time elapsed, user request, account closure)
- Backup retention overlay
- Exceptions (legal hold)

Make it explicit. Implement with lifecycle policies + scheduled jobs.

### Privacy Impact Assessment (PIA / DPIA)

Required for "high risk" processing:
- New product features touching PII
- Large-scale processing
- AI / automated decision-making

Document: purpose, data flows, risks, mitigations, residual risk.

---

## 4. AI-Specific Governance (2026)

### EU AI Act (in force 2025-2027)

Categorizes AI by risk:
- **Unacceptable risk** — banned (social scoring, real-time biometric ID with exceptions)
- **High risk** — extensive obligations (hiring, credit, critical infrastructure)
- **Limited risk** — transparency (chatbots disclose they're AI)
- **Minimal risk** — no obligation

High-risk requires:
- Risk management system
- Data governance + quality
- Technical documentation
- Logging
- Transparency
- Human oversight
- Accuracy, robustness, cybersecurity
- Conformity assessment

### Model cards

Document for every production AI model:
- Purpose + intended use
- Training data summary + biases
- Performance metrics (overall + by slice)
- Limitations + ethical considerations
- Owner + contact
- Last updated + retraining cadence

Standardized by Google (model cards), Hugging Face, etc.

### Bias audits

For models making decisions about people:
- Test performance across demographic groups
- Identify disparate impact
- Document mitigation efforts
- Periodic re-audit

### Explainability

For high-impact decisions (credit, hiring, justice):
- SHAP / LIME / counterfactual explanations
- "Right to explanation" emerging in regulation
- Document model decision logic at the level required

### LLM-specific concerns

- **Prompt injection** — adversarial inputs
- **PII memorization** — model regurgitating training data
- **Hallucination** — confidently wrong
- **Bias** — reflecting training data biases
- **Misuse** — generating harmful content

Mitigations: input/output guardrails, audit, eval, content safety.

### EU AI Act — obligations per risk tier + timeline (2025-2027)

**Why it matters.** First binding horizontal AI law; extraterritorial (applies to any provider/deployer placing AI on the EU market or whose output is used in the EU). Penalties exceed GDPR: up to **€35M or 7% of global turnover** for prohibited practices; **€15M or 3%** for high-risk non-compliance; **€7.5M or 1%** for supplying incorrect information to authorities.

**The four risk tiers + obligations.**
- **Unacceptable risk (banned, Art. 5)** — social scoring, manipulative/subliminal techniques, untargeted facial-recognition scraping, emotion recognition in workplace/education, most real-time remote biometric ID in public. **In force since 2 Feb 2025.**
- **High risk (Annex III + product-safety, Art. 8-15)** — hiring, credit scoring, insurance, critical infrastructure, education, biometrics, law enforcement, migration. Requires: risk management system, data governance/quality, technical documentation, automatic logging, transparency to deployers, human oversight, accuracy + robustness + cybersecurity, conformity assessment + CE marking + EU database registration.
- **Limited risk (transparency, Art. 50)** — chatbots must disclose they are AI; AI-generated/manipulated content (deepfakes, synthetic media) must be machine-readable labelled.
- **Minimal risk** — no obligation (spam filters, game AI). Voluntary codes of conduct encouraged.

**Plus a cross-cutting AI literacy duty (Art. 4)** for providers and deployers — in force since 2 Feb 2025.

**GPAI (general-purpose AI model) obligations — Art. 53-55.** All GPAI providers: technical documentation, copyright policy, public training-data summary. GPAI with **systemic risk** (>10^25 FLOPs training compute, e.g. frontier models): model evaluations, adversarial testing, systemic-risk mitigation, incident reporting, cybersecurity. **In force since 2 Aug 2025.** Signing the EU AI Office's voluntary **GPAI Code of Practice** (July 2025) grants a presumption of conformity.

**Timeline.** 2 Feb 2025 prohibitions + literacy → 2 Aug 2025 GPAI + governance + penalties → **2 Aug 2026 most high-risk obligations apply** → 2 Aug 2027 high-risk-as-product-component + pre-2025 GPAI compliance deadline. (A Nov 2025 "Digital Omnibus" simplification pushed some Annex III high-risk dates toward Dec 2027 — track closely.)

**Pitfalls.** Assuming you're a "deployer" not a "provider" (fine-tuning or rebranding can make you a provider); ignoring extraterritorial reach from outside the EU; treating the voluntary Code of Practice as optional when it is the cheapest route to conformity.

References: [EU AI Act implementation timeline](https://artificialintelligenceact.eu/implementation-timeline/) · [European Commission — AI Act regulatory framework](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| "Governance is legal's problem" | Engineering blind to risk | Embedded compliance in dev process |
| Policy documents nobody reads | Theater | Controls in tooling |
| Data inventory in spreadsheet | Stale | Catalog with automated discovery |
| One-off PIA, never updated | Stale risk picture | Update on change |
| No data deletion process | GDPR violation | Automated deletion workflows |
| Audit logs in same system as data | Tampering risk | Separate audit storage |
| Encrypt everything (uniformly) | Cost + complexity | Risk-based encryption |
| No access reviews | Stale entitlements | Quarterly reviews |
| Trust users with "anonymized" data | Re-identification risk | Differential privacy / k-anonymity |
| Ignoring AI Act | Fines + reputation | Compliance program now |
| No model cards | Can't explain decisions | Model cards mandatory for prod |

---

## 6. Advanced / Expert Topics

### Privacy-enhancing technologies (PETs)

- **Differential privacy** — mathematical guarantee on individual privacy
- **Federated learning** — train without data leaving devices
- **Homomorphic encryption** — compute on encrypted data
- **Secure multi-party computation** — joint compute without revealing inputs
- **Synthetic data** — generated to preserve statistics, not individuals

Emerging but increasingly required for sensitive workloads.

### PETs — deeper, per technique (maturity + use cases, 2025-2026)

A risk-based selection guide. Maturity scale: production / piloting / research.

**Differential privacy (DP) — production.** Adds mathematically calibrated noise so a query result is (nearly) unchanged whether or not any single individual is in the dataset. The **privacy budget ε (epsilon)** quantifies leakage: lower ε = stronger privacy, more noise, less utility. Rule of thumb: ε ≤ 1 strong, 1-10 moderate, >10 weak. Budget is *consumed* across queries (composition) — track it in a "privacy ledger." Use cases: aggregate analytics, telemetry (Apple, Google), the **2020 US Census**. Pitfall: ε is not intuitive to stakeholders; a single large ε across many queries silently exhausts the guarantee.

**Federated learning (FL) — production-ish.** Train a model across decentralized data; only gradient/weight updates leave the device or silo, raw data never moves. Use cases: mobile keyboards, cross-hospital/cross-bank models under data-localization rules. Pitfall: updates can leak data (gradient inversion) — combine with DP + secure aggregation, not FL alone.

**Homomorphic encryption (HE) — piloting.** Compute directly on ciphertext (see encryption-in-use subsection). Fully HE (FHE) still 1000x+ slower; partial/leveled HE is usable for narrow operations (encrypted scoring, private set intersection). Use cases: encrypted ML inference, private analytics on outsourced data.

**Secure multi-party computation (SMPC) — piloting.** Multiple parties jointly compute a function over their combined inputs while each input stays secret. Use cases: cross-bank fraud/AML signals, salary-equity studies, ad measurement. Pitfall: network/communication-heavy; needs honest-majority or trust assumptions made explicit.

**Synthetic data — production for test/dev, piloting for analytics.** Generate artificial records preserving aggregate statistics, not individuals. Use cases: dev/test environments, ML training, demos, data sharing. Pitfall: not automatically anonymous — generative models can memorize and re-emit real outliers; validate with membership-inference and DP-trained generators.

**Selection heuristic.** Data must move to one place but parties distrust each other → SMPC. Data cannot move → FL. Need to publish/share statistics → DP or synthetic. Need to outsource compute on encrypted data → HE / confidential computing (cheaper, see below).

References: [UN Guide on PETs for Official Statistics](https://unstats.un.org/bigdata/task-teams/privacy/guide/) · [ITIF — What Are Privacy-Enhancing Technologies? (2025)](https://itif.org/publications/2025/09/02/itif-technology-explainer-privacy-enhancing-technologies/)

### DLP (Data Loss Prevention) — full lifecycle + tooling

**Why.** Prevents sensitive data (PII, PHI, PCI, secrets, IP) from leaving controlled boundaries through exfiltration, misconfiguration, or accident — a core control for PDPA/GDPR breach-avoidance and PCI-DSS.

**The lifecycle (six stages).**
1. **Discover** — scan repositories, databases, buckets, endpoints, SaaS for where sensitive data lives.
2. **Classify** — match against info-type detectors (regex, dictionaries, ML, exact-data-match) and apply sensitivity labels.
3. **Protect** — de-identify (mask, tokenize, redact), encrypt, or apply rights-management at rest/in motion.
4. **Detect** — monitor data in motion (egress, email, upload) and in use (clipboard, print, screen) against policies.
5. **Respond** — block, quarantine, alert, require justification, auto-remediate.
6. **Audit** — log every match + action for evidence, tune false positives, report to compliance.

**Deployment surfaces.** **Endpoint DLP** (agent on laptops — clipboard/USB/print), **network DLP** (egress, email gateway, web proxy), **cloud/SaaS DLP** (API + CASB inline across M365, Google Workspace, Slack, and now GenAI prompts).

**Tools (2025-2026).**
- **Google Cloud Sensitive Data Protection** (formerly Cloud DLP) — 200+ built-in infoType detectors; discovery, inspection, de-identification, risk analysis via the DLP API; strong for data-at-rest on GCP/BigQuery.
- **Microsoft Purview DLP** — Identify→Monitor→Protect across at-rest/in-use/in-motion; centrally managed in the Purview portal; integrates sensitivity labels, adaptive protection, and **GenAI/Copilot prompt** controls.
- **Nightfall AI** — API-first + lightweight agents; real-time detection of PII/PHI/PCI/secrets across Slack, M365, Workspace, browsers, GenAI tools; image OCR, auto-remediation.

**Pitfalls.** Block-only policies before tuning → alert fatigue + user workarounds (start in monitor/audit mode). Endpoint-only coverage misses SaaS and GenAI egress (the fastest-growing leak vector). DLP without an upstream **data inventory + classification** produces noise. Discovery that never re-runs goes stale.

References: [Google Cloud — Sensitive Data Protection docs](https://cloud.google.com/security/products/dlp) · [Microsoft — Learn about data loss prevention](https://learn.microsoft.com/en-us/purview/dlp-learn-about-dlp)

### Encryption "in use" — confidential computing + when it's worth it

**The gap.** Encryption at rest + in transit leaves data **plaintext in RAM during processing**, exposed to the host OS, hypervisor, cloud operator, and co-tenants. Encryption-in-use closes this third state.

**Approaches.**
- **Confidential computing (hardware TEEs)** — data + code run inside a hardware-encrypted, attestable enclave. **Intel SGX** = process-level enclaves (now largely Xeon-only). **Intel TDX** + **AMD SEV-SNP** = full-VM confidential VMs (memory + CPU-state encryption, integrity). **AWS Nitro Enclaves** = isolated VM carved from an EC2 instance, no networking/persistent storage, no operator access. **GCP Confidential VMs** + **Azure Confidential Computing** wrap SEV-SNP/TDX. **Remote attestation** (cryptographic proof of the enclave's identity/state before releasing keys) is the load-bearing feature — without it you only have encryption, not trust.
- **Homomorphic encryption** — compute on ciphertext, data never decrypted; strongest model, but FHE remains orders of magnitude slower.
- **Secure enclaves / SMPC** — software-cryptographic alternatives where no trusted hardware exists.

**When each is worth it.**
- **Confidential computing** — the pragmatic default for most "protect data from the cloud operator" needs: multi-party data clean rooms, processing regulated data on public cloud, protecting model weights during inference, key/secret handling. Near-native performance; the main cost is attestation plumbing + limited OS/image support.
- **Homomorphic encryption** — only when you genuinely cannot trust *any* hardware/operator and the computation is narrow (encrypted scoring, private set intersection). Otherwise the latency tax is rarely justified.
- **SMPC** — cross-organization joint compute with mutual distrust and no shared trusted host.

**Pitfalls.** Treating a TEE as a black box and skipping attestation. Assuming "confidential" hides everything — side channels, memory-access patterns, and a large guest trusted-computing-base remain. Image/OS compatibility and attestation support vary by provider and change frequently — verify before designing around it.

References: [AWS Nitro Enclaves](https://aws.amazon.com/ec2/nitro/nitro-enclaves/) · [Google Cloud — Confidential VM attestation](https://docs.cloud.google.com/confidential-computing/confidential-vm/docs/attestation)

### Banking-specific compliance — BoT (Thailand) + MAS (Singapore) concrete controls

**Why.** Financial regulators impose prescriptive, auditable IT-risk controls with hard reporting clocks — far stricter than baseline PDPA.

**Bank of Thailand (BoT).** IT Risk Management Guidelines (refreshed Nov 2023) require:
- **IT risk governance** — board-level IT governance framework; annual IT risk self-assessment **reported to BoT within 30 days**; third-party/outsourcing risk-management submissions.
- **Outsourcing / cloud** — governed by the IT Outsourcing notification (FPG 19/2559): due diligence, supervision, service-provider management, security + integrity, availability, customer protection, exit/control; cloud receives heightened scrutiny.
- **Incident reporting** — notify BoT (System Examination / Financial Technology Dept) **within 24 hours** of a material IT incident being detected; plus strengthened fraud-incident reporting in the 2023-25 updates.
- **BCM / DR** — business-continuity framework with periodic DR testing; vulnerability management.
- **Data localization** — PDPA + sector practice favors keeping data in the Thai region; cross-border requires safeguards.

**Monetary Authority of Singapore (MAS).** Technology Risk Management (TRM) Guidelines + binding Notices:
- **IT risk governance** — board + senior-management accountability, technology-risk framework, third-party/cyber-hygiene controls.
- **Incident reporting** — notify MAS **within 1 hour** of discovering a relevant incident; submit a **root-cause + impact analysis within 14 days**.
- **Outsourcing / cloud** — Notice 658 (banks) / 1121 (merchant banks) on Management of Outsourced Relevant Services, **effective 11 Dec 2024**: assess, manage, monitor third-party risk with contractual cybersecurity, performance, and incident-response provisions.
- **BCM / DR** — defined recovery time objectives, regular DR + BCP testing, system resilience/availability targets.

**Pitfalls.** Missing the asymmetric clocks (BoT 24h vs MAS 1h) → reportable breach. Assuming a hyperscaler's compliance posture transfers the duty — shared responsibility means the FI still owns notification, exit, and oversight. Both providers publish mapped compliance baselines (Google Cloud, Azure) — use them as evidence, not as a substitute for your own control attestations.

References: [BoT IT Risk Management Guidelines (Google Cloud compliance)](https://cloud.google.com/security/compliance/bot-thailand) · [MAS TRM Guidelines (Google Cloud compliance)](https://cloud.google.com/security/compliance/mas-trm)

### Banking-specific (BoT, MAS, etc.)

BoT IT Risk requirements (Thailand):
- IT governance framework
- Risk assessment annually
- Outsourcing controls (cloud needs additional scrutiny)
- BCM (business continuity)
- Vulnerability management
- Incident reporting

Use Azure or Google's documented BoT-compliance posture as a baseline.

### Cloud compliance shared responsibility

Provider covers: physical security, infrastructure, hypervisor.
Customer covers: identity, data, application, network config.

Don't assume the provider handles compliance — they enable it.

### Data sovereignty + sovereign cloud

Some jurisdictions require sovereign cloud:
- France: Cloud de Confiance (S3NS = Google + Thales)
- Germany: BSI requirements
- Australia: IRAP for government

Hyperscalers offer sovereign regions in select markets.

### Vendor risk management

For each third-party data processor:
- Compliance attestations (SOC 2, ISO, etc.)
- DPA in place
- Periodic risk review
- Incident notification clauses
- Exit strategy

### Cross-border data transfer mechanisms

When data leaves jurisdiction:
- **Adequacy decisions** — destination country deemed adequate
- **Standard Contractual Clauses (SCCs)** — most common GDPR fallback
- **Binding Corporate Rules (BCRs)** — for multinational groups
- **Derogations** — specific case-by-case (rare)

Post-Schrems II (2020): SCCs alone aren't enough; needed Transfer Impact Assessment.

### Incident response (regulatory aspect)

- Detection within reasonable time
- Notify regulator (often within 72h for GDPR breaches)
- Notify affected individuals if high risk
- Document everything (chronology, scope, mitigation)
- Postmortem + corrective action

---

## 7. References

### Standards
- **GDPR text + EDPB guidelines** — eur-lex.europa.eu
- **PDPA Thailand** — pdpc.or.th
- **NIST Cybersecurity Framework / Privacy Framework / AI RMF**
- **ISO 27001 / 27701 / 27018**
- **PCI-DSS** — pcisecuritystandards.org
- **EU AI Act** — official text

### Books
- **Privacy by Design** — Ann Cavoukian
- **The Privacy Engineer's Manifesto** — Dennedy et al.
- **Trustworthy Machine Learning** — Varshney

### Communities
- **IAPP** (International Association of Privacy Professionals) — certifications + resources
- **OneTrust / TrustArc** community
- **Open Privacy** projects

### Certifications
- **CIPP** (privacy professional)
- **CIPT** (privacy technologist)
- **CIPM** (privacy management)

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| Solution Architect | Privacy + security architecture |
| Data Architect | Classification, lineage, retention design |
| Data Engineer | DLP scanning, masking, audit hooks |
| AI Architect / Engineer | AI Act compliance, model cards, bias |
| Platform Architect | Org-wide policy enforcement |
| DevOps / SRE | Audit trails, encryption |
| Legal | Translating regulation to controls |
| Risk + Audit | Evidence collection |

---

*Governance translates regulation into engineering controls. Make compliance happen via tooling, not policy memos.*
