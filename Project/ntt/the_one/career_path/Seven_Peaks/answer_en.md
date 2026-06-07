# Seven Peaks — Pre-Interview Answers

---

## Q1: Why are you looking to change your current job?

### Full version

My current role is a consultant position, which has given me a lot of valuable experience. However, the main reason I'm looking for a change is the **working structure**.

The Scope of Work was defined quite broadly during the presale phase, so once we moved into delivery, requirements changed frequently under the same timeline. On top of that, the client site operates under a multi-vendor structure where each party has different priorities, making alignment quite challenging.

What I did to manage this was to break the work into release phases — core requirements were delivered first, while anything beyond the original scope was separated into an enhancement phase. This approach helped us launch on time per commitment while allowing proper time to clarify the enhancement scope with the client.

That said, the technology and the variety of features on this data platform are genuinely interesting. But from my experience, unclear scope and evolving client requirements from the start can impact long-term commitment and deliverable quality. So I'm looking for a new opportunity that offers more clarity in this regard.

### Short version

My current role is a consultant — great learning experience, but the scope was defined broadly during presale, which led to frequent requirement changes during delivery. I managed this by splitting work into release phases to meet commitments, but unclear scope from the start can impact deliverable quality long-term. I'm looking for an opportunity with more clarity on that front.

---

## Q2: How many years of experience do you have in Data Engineering?

8 years (June 2017 – Present)

---

## Q3: Which databases are you familiar?

SQL Server, PostgreSQL, Hive, BigQuery

---

## Q4: Have you worked with data platforms? If so, which ones?

- Azure Databricks — data modeling, schema synchronization, automated testing, RBAC (SCB Data-X, 2+ years)
- GCP (Dataflow + BigQuery + Iceberg) — 5 production pipelines covering both streaming and batch (NTT DATA / The 1, current)
- Azure Data Factory / Synapse Analytics — orchestration and data integration (SCB Data-X)

---

## Q5: Could you describe your experience working with Databricks?

I used Databricks at SCB Data-X for about 2 years on Azure, primarily with **PySpark / PySpark SQL**:

- Designed data models and data validation processes
- Built automated tests via **Databricks Workspace API** and **Data Factory API**
- Designed schema synchronization processes to detect schema drift between source databases and the data warehouse
- Conducted POC migration to **Unity Catalog**
- Developed **RBAC** to separate access levels by team (risk, compliance, analytics)
- Performance tuning: broadcast joins, partition pruning, repartitioning before large joins, caching intermediate DataFrames

---

## Q6: What data sources did you integrate?

- **Kafka (Confluent Cloud)** — streaming events with Schema Registry + Avro
- **REST APIs** — loyalty member/tier data, enrichment
- **PostgreSQL** — batch daily incremental
- **Pub/Sub** — streaming customer profile events
- **Cloud Bigtable** — profile lookup for enrichment
- **SQL Server, Hive, Teradata** — ETL pipelines (SCB, AIS, DTAC)
- **Web Crawlers** — data gathering (AIS)

---

## Q7: What do you believe is the core business of a consulting firm and what essential mindset is critical for thriving in this field?

The core business of a consulting firm is bringing specialized expertise to help clients solve problems or build solutions they don't have the resources or know-how to do themselves. What you're really selling is **trust** and **tangible deliverables**.

Essential mindset:
1. **Adaptability** — ability to quickly ramp up on the client's tech stack, domain, and culture
2. **Ownership** — treat every deliverable as your own, even as a consultant
3. **Communication** — coordinate clearly across multiple teams
4. **Value-driven** — every effort should serve the client's business value, not just getting the code done

---

## Q8: What AI tools are you familiar with, and how have you used them?

I primarily use **Claude Code (Anthropic)** as an AI coding assistant — for code review, drafting unit tests, writing documentation, and refactoring. I always review the output myself before applying it.

---

## Q9: Please indicate your current salary and expected salary per month?

Expected salary: **95,000 THB/month** (negotiable)

---

## Q10: Would you be interested in a Permanent role, or a Contractual role, or both?

**Permanent**

---

## Q11: What is your preferred starting date?

Available within **1 month** after receiving an offer.
