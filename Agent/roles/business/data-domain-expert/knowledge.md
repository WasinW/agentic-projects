# Data Domain Expert — Comprehensive Knowledge

> Deep reference for the data-domain-expert subagent.
> Speaks both business and data fluently; owns domain semantics.

---

## 1. Foundations

### What a Data Domain Expert does

Bridges business operations and data systems. Owns:
- Domain glossary + definitions
- Business rules + edge cases
- Data quality requirements (from domain lens)
- Source system semantics
- Data interpretation for analysis
- Stewardship of canonical entities

### The role's value

Engineers can build pipelines for any data. But they can't tell you:
- What "active customer" really means in this business
- Why certain accounts behave differently
- What the special cases are
- Which data quality issues matter to business

Domain experts know this. Without them, technical brilliance produces wrong answers.

### Where DDEs sit

- Embedded in business functions (subject experts)
- Embedded in data team (steward role)
- Part-time (operations expert with data side-role)
- Often emerges from operations, not engineering

---

## 2. Mental Models / Decision Frameworks

### Field name ≠ field meaning

The schema says `customer_status`. But:
- What are the valid values?
- When does "active" become "inactive"?
- Is "dormant" a separate state or sub-state?
- Are there grandfathered statuses?
- How does the operations team actually use this field?

Schema alone tells you almost nothing. Domain knowledge tells you what it means.

### Edge cases are where domain matters

The happy path is easy. The 20% edge cases:
- Special account types (employees, VIPs, regulatory)
- Manual overrides
- Historical "wonky" data
- Legacy systems that handle it differently
- Compliance-driven exceptions

These edge cases live in domain experts' heads. Make them explicit.

### Glossary as governance

Every business term should have:
- Definition (precise, plain language)
- Owner (who maintains it)
- Synonyms + related terms
- Examples (canonical + edge cases)
- Source systems where it lives
- Business rules that touch it

One source of truth per term. Catch + reconcile inconsistencies.

### "What does X mean?" workflow

When asked:
1. Define formally
2. Provide canonical examples
3. List known exceptions
4. Point to source of truth
5. Flag ambiguities (yes, they exist)

Often the same term means different things in different parts of the business. Surface this.

### Quality from domain lens

Generic DQ (uniqueness, null check) is necessary but insufficient. Domain DQ:
- "All orders should have a customer_id" — domain rule
- "Loyalty points balance shouldn't exceed lifetime earned" — invariant
- "Closed accounts shouldn't have new transactions" — temporal rule
- "Refund amount ≤ original purchase" — business constraint

These are domain-specific.

### Decay of domain knowledge

Business changes. Domain rules drift:
- New products + new edge cases
- Policy changes
- M&A integrations
- Regulatory updates

Refresh glossary + rules at least annually. Mark when last reviewed.

---

## 3. Standard Practices

### Glossary entry template

```
Term: Customer Lifetime Value (CLV)
Definition: Estimated total revenue from a customer over their relationship.
Owner: VP Marketing
Calculation: Sum of historical purchases + predicted future purchases (next 24mo) at margin.
Source: data.gold.customer_clv
Excludes: B2B customers (separate model), employees, test accounts
Related: Customer Acquisition Cost, Average Order Value
Examples:
  - Retail customer with $1200 historical + $800 predicted = $2000 CLV
  - Employee account = excluded
Last reviewed: 2026-04
```

### Domain rule documentation

For each business rule:
- Plain language statement
- Quantitative threshold (when applicable)
- Exceptions (always there)
- Where enforced (system / process)
- Owner
- Compliance / regulatory anchor (if relevant)

### Data quality rules from domain

| Generic | Domain-specific |
|---|---|
| customer_id is not null | customer_id is one of {RETAIL_CUSTOMER, B2B, EMPLOYEE} |
| amount > 0 | amount within customer's credit limit |
| timestamp valid | timestamp after customer signup date |
| status in valid values | status transitions follow allowed paths |

### Data source semantics

For each source system:
- What it captures (and what it doesn't)
- When data is created / updated
- Quirks (timezone, special encoding, NULL meanings)
- Integration limitations
- Backfill / restate history

Often documented poorly; DDEs are the institutional memory.

### Reconciliation across sources

When same entity in multiple systems:
- Identify canonical source
- Document how others differ
- Reconciliation logic
- Discrepancy thresholds + resolution

E.g., customer name in CRM vs ERP may differ; CRM is canonical, ERP is for billing.

### Business rule engine vs hardcoded

When business rules change often:
- Externalize into rules engine (Drools, custom)
- Domain expert can update without code change
- Audit trail of changes

When rules are stable:
- Embed in transform code with tests
- Document in glossary

### Edge case capture

When edge cases surface:
- Document immediately (don't trust memory)
- Add to test cases
- Update glossary entry
- Notify downstream consumers if impactful

Edge cases that aren't captured become "ghosts" — bugs that periodically reappear.

---

## 4. Tools Landscape (2026)

### Glossary + catalog
- **Atlan** — strong UX for business users
- **Collibra** — enterprise governance
- **DataHub** — OSS, technical-leaning
- **OpenMetadata** — OSS alternative
- **Microsoft Purview** — Microsoft stack
- **Alation** — established commercial

### Domain modeling
- **Confluence** — wiki-style documentation
- **Notion** — alternative
- **Markdown in Git** — engineer-friendly
- **EventStorming + Miro** — for DDD workshops

### Quality rules engine
- **Soda** — DQ as code
- **Great Expectations** — flexible
- **dbt tests** — in-pipeline
- **Custom in business rule engine** — for ops-side rules

### Reverse ETL (operational use of data)
- **Hightouch / Census** — sync warehouse → SaaS
- **Polytomic** — alternative

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Definitions in someone's head | Bus factor + inconsistency | Glossary as single source |
| Multiple definitions for same term | Reports disagree | One canonical + flag variants |
| No ownership | Decay + ambiguity | Owner per term |
| Engineering-only glossary | Misses business semantics | DDE-owned |
| Static glossary (no review) | Stale | Annual review + change log |
| Generic DQ rules only | Misses domain issues | Domain-specific rules |
| Trust the schema | Says nothing about meaning | Document meaning explicitly |
| Edge cases discovered in production | Recurring bugs | Capture as they surface |
| Tribal knowledge | Hard to onboard | Documented runbooks + glossary |
| Ignoring data source quirks | Wrong interpretation | Document quirks per source |

---

## 6. Advanced / Expert Topics

### Domain-Driven Design alignment

- Ubiquitous language: shared terminology between business + tech
- Bounded contexts: same term can mean different things in different sub-domains (be explicit)
- Aggregates: transactional consistency boundaries (DDE helps identify)
- Event Storming: workshop technique to surface domain events

### Master Data Management (MDM)

For canonical entities (Customer, Product, Location):
- Single source of truth
- Hierarchies + relationships
- De-duplication rules
- Cross-system identifier mapping
- Stewardship workflow for changes

DDE often plays steward role.

### Reference Data Management

For lookup tables (countries, currencies, product types):
- Versioning when codes change
- Effective dates
- Mapping across systems
- Ownership

Often overlooked but causes subtle bugs.

### Data Mesh data products

In Data Mesh, domains own data products. DDE plays critical role:
- Define what data product looks like
- Quality + SLA from domain perspective
- Contract with consumers
- Lifecycle

### Cross-domain semantics

When two domains use same term differently:
- Marketing's "customer" = anyone with an account
- Finance's "customer" = paying customer

Surface + reconcile. May require disambiguation in field names.

### Domain ontology

For complex domains (banking, insurance, healthcare):
- Formal ontology / taxonomy
- Relationships between concepts
- Industry standards (FIBO for finance, HL7/FHIR for healthcare)
- Can drive automated reasoning

Useful for AI / knowledge graphs.

### Stewardship governance

- Steward council (cross-domain representatives)
- Change approval process for canonical terms
- Audit trail of definition changes
- Communication to consumers when definitions change

---

## 7. References

### Books
- **Domain-Driven Design** — Eric Evans (classic)
- **Implementing Domain-Driven Design** — Vaughn Vernon
- **Data Management at Scale** — Piethein Strengholt
- **Event Storming** — Alberto Brandolini (free PDF early chapters)
- **Master Data Management** — Berson, Dubov

### Standards
- **FIBO** (Financial Industry Business Ontology) — for finance
- **HL7 / FHIR** — healthcare
- **GS1** — supply chain
- **DAMA DMBOK** — Data Management Body of Knowledge

### Communities
- **Data Mesh community**
- **DAMA International**
- Industry-specific groups (FIBO, HL7, etc.)

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| Business Analyst | Translate requirements with domain rigor |
| Data Architect | Schema design with semantic input |
| Data Engineer | Edge cases, source quirks |
| Data Analyst | "What does this field mean?" |
| ML Engineer | Feature semantics, target definition |
| Governance | Steward role, classification |
| Stakeholders | Domain knowledge transfer |

---

*DDE = the keeper of meaning. Without them, technical brilliance produces wrong answers.*
