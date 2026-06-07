# Banking Compliance Thailand — PDPA + BoT + Sec

> Thailand-specific data + AI compliance สำหรับ banking/finance
> PDPA, BoT regulations, SEC rules, AI guidelines

---

## 1. ทำไมเรื่องนี้สำคัญ

### สถานะปี 2026

- **PDPA enforcement เริ่มจริง**: สิงหาคม 2025 PDPC ออก fines แรก > 21.5M THB
- **BoT regulations เข้มข้น**: IT risk + outsourcing rules
- **AI Act กำลังจะมา**: Thai AI Act draft 2025-2026
- **ลูกค้า + ธปท. ตรวจสอบจริงจัง**: ไม่ใช่แค่ tick box

### Penalties (เริ่มจริง)

```
PDPA: up to 5M THB per violation + criminal liability
BoT: license revocation possible, individual penalties
SEC: fines + market access restrictions
```

---

## 2. PDPA (Personal Data Protection Act B.E. 2562)

### ภาพรวม

PDPA = Thailand's GDPR-equivalent
- มีผล: 1 มิถุนายน 2022
- บังคับใช้จริง: 2025+ (after grace period)

### Key Concepts

| Term | Meaning |
|---|---|
| **Personal Data** | Data identifying living individual |
| **Sensitive Data** | Health, religion, race, sexual orientation, biometric, criminal record |
| **Data Controller** | Decides why + how to process |
| **Data Processor** | Processes on behalf of controller |
| **Data Subject** | The individual |

### 6 Lawful Bases for Processing

```
1. Consent (explicit, informed, specific)
2. Contract necessity
3. Legal obligation
4. Vital interest (life-threatening)
5. Public interest / official authority
6. Legitimate interest (carefully balanced)
```

### Data Subject Rights

```
1. Right to access (อยากดูข้อมูลของตัวเอง)
2. Right to rectification (แก้ไขข้อมูลผิด)
3. Right to erasure (ขอลบ)
4. Right to restrict processing
5. Right to data portability
6. Right to object
7. Right to withdraw consent
```

### What this means for Data Engineers

```
Must support:
- Locate all data of a person across systems
- Update/correct in all places
- Delete completely (including derived)
- Export in machine-readable format
- Audit who accessed what when
```

---

## 3. PDPA Implementation in Data Platform

### Pattern 1: PII Catalog

ทุก dataset ต้อง classify:

```yaml
dataset: warehouse.silver.customers
classification:
  contains_pii: true
  pii_columns:
    - name: phone
      type: contact
      sensitivity: confidential
      lawful_basis: contract
      retention_days: 2555  # 7 years
    - name: id_card
      type: government_id
      sensitivity: restricted
      lawful_basis: legal_obligation
      retention_days: 3650  # 10 years
    - name: medical_history
      type: sensitive
      lawful_basis: explicit_consent
      retention_days: 1825  # 5 years
```

### Pattern 2: Lineage for "Right to Be Forgotten"

```
User requests deletion
    ↓
Find all derivatives via lineage
    ↓
Delete from:
  - Raw layer
  - Silver layer
  - Gold layer
  - Vector DB
  - Cache
  - Backups (per policy)
  - ML training data
  - Model embeddings
    ↓
Audit log of deletion
```

### Pattern 3: Consent Management

```sql
-- Consent table
CREATE TABLE consent_log (
    user_id STRING,
    purpose STRING,  -- "marketing", "analytics", "cross-sell"
    granted_at TIMESTAMP,
    expires_at TIMESTAMP,
    withdrawn_at TIMESTAMP,
    proof BLOB  -- screenshot, IP, timestamp
);

-- Always check before processing
def can_use_data(user_id, purpose):
    consent = get_latest_consent(user_id, purpose)
    return (
        consent.granted_at is not None and
        consent.withdrawn_at is None and
        consent.expires_at > now()
    )
```

### Pattern 4: PII Masking

```python
# Multiple strategies
def mask_phone(phone):
    """012-345-6789 → 012-XXX-6789"""
    return phone[:3] + "-XXX-" + phone[-4:]

def hash_for_join(value, salt="..."):
    """For joining without exposing"""
    return sha256(value + salt).hexdigest()

def tokenize(value, vault):
    """Reversible mapping for authorized use"""
    return vault.tokenize(value)  # SHA + lookup table
```

### Pattern 5: Differential Privacy (advanced)

```python
# Add noise to aggregated stats
from opendp.measurements import make_base_laplace

# Instead of exact average
exact_avg = df.amount.mean()  # could leak info

# DP version
mechanism = make_base_laplace(scale=1.0)
private_avg = exact_avg + mechanism()  # add noise
```

---

## 4. Cross-Border Data Transfers

### PDPA Restrictions

PDPA Section 28: cannot transfer PII outside Thailand UNLESS:
- Adequate protection in destination country
- Explicit consent
- Necessary for contract performance
- Government approved binding corporate rules

### Implications for Cloud

```
Using AWS us-east-1 with Thai customer data?
   → cross-border transfer
   → need basis

Solutions:
1. Use Thailand region (AWS, GCP, Azure all have)
2. Get consent (mention transfers in privacy policy)
3. Anonymize before transfer
4. Use approved BCRs (binding corporate rules)
```

### LLM/AI Implications

```
Send Thai customer chat to OpenAI (US)?
   → cross-border transfer
   → need consent OR
   → use anonymized data OR
   → use Anthropic (data residency? check)

Practical:
- Mask PII before sending to LLM
- Use Thailand-resident inference where possible
- Privacy policy must disclose
```

---

## 5. BoT (Bank of Thailand) Regulations

### Key Notifications

#### FPG 21/2562 — IT Risk Management

Requirements:
- IT governance framework
- Risk assessment annually
- Business continuity / DR
- Information security
- IT outsourcing controls

#### FPG 8/2557 — Outsourcing

```
Bank using cloud (AWS/GCP) = outsourcing
Requirements:
- Risk assessment of provider
- Right to audit cloud provider
- Data residency considerations
- Exit strategy
- Business continuity plan
```

#### Notification SorTorYor 2/2563 — Cyber Resilience

- Penetration testing
- Security incident reporting
- Vulnerability management
- Supply chain risk management

### Operational Requirements for Data Platform

```yaml
business_continuity:
  rto: 4_hours  # Recovery Time Objective
  rpo: 1_hour   # Recovery Point Objective
  multi_region: true
  
data_residency:
  primary: thailand
  backup: thailand_secondary_region
  cross_border_allowed: case_by_case

audit:
  retention_years: 7  # for transactions
  immutable: true
  scope:
    - data_access
    - configuration_changes
    - admin_actions
    - failed_authentication

security:
  encryption_at_rest: AES-256
  encryption_in_transit: TLS 1.3
  key_management: HSM-backed
  access_review_frequency: quarterly
  privileged_access: just-in-time
```

### Outsourcing Cloud Provider Audit

ต้องสามารถ:
1. Show data location at any time
2. Confirm encryption keys management
3. Verify access controls
4. Demonstrate isolation
5. Provide incident reports
6. Right to audit (or use SOC2 reports)

---

## 6. SEC Thailand (สำนักงาน ก.ล.ต.)

### Applicable to

- Securities companies
- Asset management
- Mutual funds
- Crypto businesses (since 2018)
- Digital assets (NFT, etc.)

### Key Rules

```
Customer due diligence (KYC)
Suspicious transaction reporting
Trade surveillance
Insider trading prevention
```

### Data Implications

```
Must retain:
- All trades + orders for 5+ years
- Customer records 5+ years post-relationship
- Communications (chat, email) related to trades

Must monitor:
- Unusual trading patterns
- Insider lookups
- Front-running detection
```

---

## 7. AML / KYC Specific

### AMLO Requirements

```
KYC tiers:
- Basic (low risk): name + ID verification
- Enhanced (high risk): source of funds, beneficial owners
- Ongoing: transaction monitoring

Reporting:
- Cash > 2M THB → cash transaction report
- Suspicious → STR within 7 days
- Wire > 700K THB international → reporting
```

### Data Platform Implications

```
Must support:
- Risk-based scoring (real-time)
- Sanctions list screening (OFAC, UN, Thai)
- PEP (Politically Exposed Persons) screening
- Transaction monitoring with patterns
- Audit trail of all decisions
- Case management for SAR/STR
```

---

## 8. AI Specific Compliance (emerging 2026)

### Thai AI Ethics Guidelines (2024+)

```
Principles:
1. Effectiveness — AI works as intended
2. Accountability — clear responsibility
3. Transparency — users know they're using AI
4. Fairness — no discrimination
5. Privacy — PDPA compliance
6. Security — robust against attacks
7. Sustainability — environmental + societal
```

### Coming AI Act (draft 2026)

Expected rules:
```
High-risk AI:
- Banking decisions (credit, fraud)
- Healthcare
- Critical infrastructure
- Law enforcement

Requirements likely:
- Risk assessment + documentation
- Human oversight (cannot fully automate)
- Bias monitoring
- Accuracy benchmarks
- Incident reporting
- Right to explanation
```

### Practical AI Compliance Now

```yaml
model_documentation:
  name: fraud_detection_v3
  purpose: Score credit card transactions
  in_scope: card transactions only
  out_of_scope: loan decisions, KYC
  
  training_data:
    snapshot: iceberg.fraud@2026-01
    pii_used: ["card_hash", "amount", "merchant"]
    bias_audit: passed (Apr 2026)
  
  performance:
    auc: 0.94
    precision: 0.85
    recall: 0.78
    fairness:
      demographic_parity_difference: 0.05  # < 0.1 OK
  
  human_oversight:
    threshold_for_block: 0.95  # > = block
    threshold_for_review: 0.7  # 0.7-0.95 = review
    auto_decisions_only: false
  
  monitoring:
    drift_check: weekly
    fairness_check: monthly
    incident_response: documented
  
  approvals:
    risk_committee: 2026-04-15
    compliance_officer: 2026-04-20
    data_steward: 2026-04-22
```

---

## 9. Implementation Architecture

### Compliance Tech Stack

```
┌────────────────────────────────────────────────┐
│  USER-FACING                                   │
│  Privacy notice • Consent UI • Subject rights  │
└──────────────────┬─────────────────────────────┘
                   │
┌──────────────────▼─────────────────────────────┐
│  CONSENT & PREFERENCE MANAGEMENT               │
│  OneTrust / Custom DB                          │
└──────────────────┬─────────────────────────────┘
                   │
┌──────────────────▼─────────────────────────────┐
│  DATA CATALOG WITH PII CLASSIFICATION          │
│  Dataplex / DataHub + custom tags              │
└──────────────────┬─────────────────────────────┘
                   │
┌──────────────────▼─────────────────────────────┐
│  ACCESS CONTROL                                │
│  IAM • Row-level security • Column masking     │
└──────────────────┬─────────────────────────────┘
                   │
┌──────────────────▼─────────────────────────────┐
│  AUDIT LOGGING                                 │
│  Immutable, 7-year retention                   │
└──────────────────┬─────────────────────────────┘
                   │
┌──────────────────▼─────────────────────────────┐
│  DATA LINEAGE                                  │
│  OpenLineage — for impact analysis             │
└──────────────────┬─────────────────────────────┘
                   │
┌──────────────────▼─────────────────────────────┐
│  ENCRYPTION                                    │
│  KMS • CMEK • HSM                              │
└────────────────────────────────────────────────┘
```

### PII Detection Pipeline

```python
# Auto-detect PII in incoming data
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()

# Scan column samples
def scan_column(column_data, column_name):
    sample = column_data.sample(1000)
    detections = []
    for value in sample:
        results = analyzer.analyze(text=str(value), language="en")
        detections.extend([r.entity_type for r in results])
    
    # Find dominant type
    from collections import Counter
    counts = Counter(detections)
    most_common = counts.most_common(1)
    
    if most_common and most_common[0][1] > 100:  # > 10% match
        return most_common[0][0]  # PII type
    return None

# Run on all columns of new dataset
for col in df.columns:
    pii_type = scan_column(df[col], col)
    if pii_type:
        catalog.tag_column(col, pii_type=pii_type)
```

### Right to Be Forgotten Implementation

```python
def delete_user_data(user_id):
    # 1. Find all references
    references = lineage_service.find_all_for_user(user_id)
    
    # 2. Delete in reverse dependency order
    for ref in sorted(references, key=lambda x: -x.depth):
        try:
            if ref.type == "raw":
                # Soft delete with tombstone
                mark_deleted(ref.table, user_id)
            elif ref.type == "silver":
                # Iceberg delete
                spark.sql(f"DELETE FROM {ref.table} WHERE user_id = '{user_id}'")
            elif ref.type == "gold":
                # Re-aggregate without user
                rebuild_aggregate(ref.table, exclude_user=user_id)
            elif ref.type == "vector_db":
                # Delete embeddings
                pinecone.delete(ids=[f"user_{user_id}_*"])
            elif ref.type == "ml_features":
                # Mark for next training run
                add_exclusion(user_id)
        except Exception as e:
            log_failure(ref, e)
            raise  # don't continue if any fail
    
    # 3. Audit log
    audit_log({
        "action": "right_to_erasure",
        "user_id": user_id,
        "deleted_from": [r.location for r in references],
        "completed_at": now()
    })
    
    # 4. Confirm to user
    notify_user(user_id, "Data deletion completed")
```

---

## 10. Audit Logging Specifics

### What to Log (regulatory minimum)

```
EVERY:
- Data access (who, what, when, where)
- Configuration change
- Privileged action
- Authentication (success + failure)
- Authorization decision
- Data export
- Schema change
- ML model deployment / decision
```

### Retention

```
PDPA: as required for purpose
BoT: 7+ years for transactions
AML: 5+ years post-relationship

Practice: 7 years for safety
```

### Immutability

```
Logs MUST be:
- Write-only (cannot edit)
- Hash-chained (detect tampering)
- Replicated to separate system
- Encrypted

Tools:
- AWS CloudTrail (immutable mode)
- GCP Cloud Audit Logs (locked retention)
- Custom: blockchain-style hash chain
```

---

## 11. Common Compliance Mistakes

### Mistake 1: Logging PII
```
❌ Log: "User 123 with email john@example.com viewed profile"
✅ Log: "User 123 viewed profile"

PII in logs = logs become PII = subject to PDPA
```

### Mistake 2: Backup Without Deletion
```
User requests deletion
You delete from production
But: backups still have data
Backup restores → data resurfaces

Fix:
- Document backup retention in privacy policy
- Periodic backup re-encryption with rotated keys
- Or: deletion list checked before restore
```

### Mistake 3: ML Models Memorize PII
```
LLM fine-tuned on customer chats
   → may regurgitate phone numbers, emails, names

Fix:
- Mask PII in training data
- Differential privacy training
- Test outputs for memorization
```

### Mistake 4: Vector DB Leakage
```
RAG indexes documents with PII
User retrieves → sees PII

Fix:
- PII detection + masking pre-indexing
- Access control on retrieval
- User-specific index (multi-tenant)
```

### Mistake 5: Cross-System Inconsistency
```
Delete from main DB
   → app still shows
   → search index still has
   → export sent to vendor still has

Fix:
- Lineage-based deletion
- Confirmed deletion across all systems
- Audit complete
```

### Mistake 6: Cross-Border Without Awareness
```
Use Stripe (US) for payments
   → Thai customer card data → US

Need:
- Disclosure in privacy notice
- Consent (or other lawful basis)
- DPA (Data Processing Agreement) with Stripe
```

---

## 12. Compliance Checklist

### Data Platform Compliance

- [ ] PII catalog complete (all datasets classified)
- [ ] Consent management system in place
- [ ] Data retention policy documented + enforced
- [ ] Right to access workflow tested
- [ ] Right to deletion workflow tested
- [ ] Cross-border transfers documented + lawful
- [ ] Encryption at rest (KMS-backed)
- [ ] Encryption in transit (TLS 1.3)
- [ ] Access controls tested
- [ ] Audit logging immutable + 7-year
- [ ] Lineage tracking for impact analysis
- [ ] DR / business continuity tested
- [ ] Incident response plan documented
- [ ] Privacy Impact Assessment (PIA) for new uses

### AI/ML Specific

- [ ] Model cards for all production models
- [ ] Bias audits performed + documented
- [ ] Human oversight defined per use case
- [ ] No high-risk decisions fully automated
- [ ] Drift monitoring + retraining protocol
- [ ] Right to explanation supported
- [ ] Training data PII handling reviewed

### LLM Specific

- [ ] PII masking before sending to external API
- [ ] Cross-border review for LLM provider
- [ ] User notice that AI is being used
- [ ] No PII in fine-tuning data
- [ ] Output filtering for PII leakage
- [ ] Conversation logs retention policy

---

## 13. Cheat Sheet

### Q: "PDPA สำคัญแค่ไหน?"
> "Banking + finance: เข้มงวด — fines up to 5M THB + criminal
> 2025+ enforcement เริ่มจริง — first major fines 21.5M THB
> Must: PII catalog, consent, retention, right to access/erasure"

### Q: "Cloud + PDPA ทำยังไง?"
> "Use Thailand region when possible (AWS, GCP, Azure all have)
> Cross-border = need lawful basis (consent, BCR, contract)
> DPA with cloud provider mandatory
> Audit rights documented"

### Q: "LLM API + PDPA?"
> "Sending PII to OpenAI/Anthropic = cross-border transfer
> Solutions:
> 1. Mask PII before send (safest)
> 2. Get explicit consent + disclose in privacy policy
> 3. Use Thailand-resident inference (vLLM self-host)
> 4. Use Anthropic with data residency commitments"

### Q: "BoT cloud rules ยังไงบ้าง?"
> "Outsourcing rules: risk assessment, right to audit, exit strategy
> IT risk: BCP/DR with RTO 4hr / RPO 1hr typical
> Cyber resilience: pen test, incident reporting
> Cloud OK but: data residency thinking, contractual rights"

### Q: "ML model compliance ทำอะไร?"
> "Model cards (purpose, training, limits)
> Bias audit
> Human oversight (especially high-risk: credit, KYC)
> Drift monitoring
> Right to explanation
> Coming AI Act will codify these"

---

## Sources

- [Personal Data Privacy Policy Bank of Thailand](https://www.bot.or.th/en/privacy-policy.html)
- [Thailand's PDPA: Essential Compliance Guidelines - BigID](https://bigid.com/blog/thailand-pdpa-compliance/)
- [Thailand Compliance Guide - Huawei Cloud](https://www.huaweicloud.com/intl/en-us/securecenter/compliance/compliance-center/th.html)
- [What is the Thailand PDPA? 2026 guide](https://cookieinformation.com/blog/what-is-the-thailand-pdpa/)
- [Thai PDPA Compliance: The Ultimate Guide - OneTrust](https://www.onetrust.com/blog/the-ultimate-guide-to-thai-pdpa-compliance/)
- [Thailand's PDPA: are companies in Thailand ready? - PwC](https://www.pwc.com/th/en/tax/personal-data-protection-act.html)
- [Thailand's Personal Data Protection Act - Centraleyes](https://www.centraleyes.com/what-is-the-personal-data-protection-act-pdpa-of-thailand/)
- [Data protection laws in Thailand - DLA Piper](https://www.dlapiperdataprotection.com/index.html?t=law&c=TH)
- [Complete Guide to PDPA Compliance in Thailand](https://thundthornthep-ai.github.io/articles/pdpa-compliance-guide-thailand.html)
- [Thailand Data Protection Law Guide - Global Legal Post](https://www.globallegalpost.com/lawoverborders/data-protection-law-guide-1072382791/thailand-2024007059)
