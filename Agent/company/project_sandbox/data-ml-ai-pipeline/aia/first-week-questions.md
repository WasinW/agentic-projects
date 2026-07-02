# AIA — First-Week Questions (Senior DE)

> Prep for day-1 at AIA (insurance), Senior Data Engineer. Stack (known): **AWS + Airflow + Databricks + Spark**, both **streaming + batch**. Likely starting on **maintenance of an existing platform**, with a probable **migration / re-platform to cut cost** on the horizon. Goal of these questions: get the system context fast, sound senior, and surface the migrate/cost angle early without committing to anything before you understand it.
>
> Tip: in week 1, ask to *read* before you ask people — request repo access, the Airflow UI, the Databricks workspace, and any architecture/runbook docs first; use these questions to fill the gaps those don't answer.

## 1. Platform & architecture (get the map)
- What's the high-level data architecture? Lakehouse on Databricks (Delta + Unity Catalog) or something older? Where does AWS-native (S3/Glue/EMR/Redshift) fit vs Databricks?
- Medallion layering — what are the actual zone names + ownership (bronze/silver/gold or custom)? Where's the boundary between "raw ingest" and "curated/business"?
- Streaming vs batch split — what runs as Spark Structured Streaming vs batch jobs? What are the SLAs on each?
- Orchestration — is Airflow the single control plane, or does Databricks Workflows/Jobs also schedule things? How do they hand off (Airflow → Databricks Jobs API / dbx / notebooks)?
- Source systems — what feeds the platform? (policy admin, claims, agent/CRM, payments, actuarial...) Batch files, CDC, Kafka/Kinesis?

## 2. The migration / cost angle (surface early, carefully)
- Is there an active or planned **re-platform / cost-optimization** initiative? What's the driver — Databricks DBU spend, EMR, storage, egress?
- Where does the cost actually go today — always-on clusters, oversized jobs, small-file/compaction problems, full reprocessing, streaming idle cost?
- Has anyone profiled it (Databricks system tables / cost dashboards / AWS CUR)? Can I see it?
- Any direction already chosen (Photon, serverless SQL, job-cluster right-sizing, Spark→DBSQL, moving cold paths off streaming)? Or is the approach still open?
- What's been tried and *didn't* work? (avoids me re-proposing dead ends)

## 3. My scope & ownership
- Which domains/pipelines am I picking up? Who owned them before, and are they still around to hand over?
- What's on fire right now / the current pain points? (frequent failures, slow jobs, data-quality complaints, cost spikes)
- What does the on-call / incident model look like — am I in the rotation, and how soon?
- What's the definition of "done" here — tests, data-quality checks, code review, deployment gates?

## 4. Engineering practices (map to what I know)
- CI/CD — GitLab/GitHub Actions/Azure DevOps? IaC — Terraform? How do pipelines get deployed (notebooks vs packaged wheels/jobs, dbx/asset bundles)?
- Config-driven framework or per-pipeline bespoke code? (I've built metadata/config-driven ETL frameworks before — want to know what their abstraction is.)
- How are Spark jobs structured — notebooks, JARs, Python wheels? Shared libraries?
- Data quality / contracts — Great Expectations, DLT expectations, custom? Schema-change handling?
- Environments — dev/stg/prod separation, how is data promoted, how is access controlled (Unity Catalog, IAM)?

## 5. Insurance-domain specifics (I'm new to insurance data)
- What are the core entities/grains I'll deal with — policy, claim, premium, agent, customer? Any actuarial/reserving data?
- Regulatory/compliance constraints on the data (OIC in Thailand, PDPA, data residency, audit/lineage requirements)? (I've done BOT regulatory reporting at SCB — want to know the AIA equivalent.)
- Any reference data / code-list complexity (product codes, channel, riders) I should learn early?

## 6. Access & onboarding (unblock myself week 1)
- Repo access, Airflow UI, Databricks workspace, AWS console/role, Unity Catalog grants, secrets/vault — who provisions these?
- Where's the documentation (architecture, runbooks, data dictionary, glossary)? Is it trustworthy/current?
- Who are my go-to people — platform/infra, domain SME, my reviewer, the person who knows where the bodies are buried?

---

### What I bring (transferable — frame it when relevant, don't oversell day 1)
- **Config/metadata-driven ETL framework design** (SCB RDT: config tables → pluggable scripts → audit-log state machine → dependency/incremental checks). Directly maps to building/maintaining a Databricks+Airflow framework.
- **Spark on Databricks** (SCB RDT/CardX on ADB) + **streaming pipeline ops** (The-1 Dataflow: watermark/sink/backpressure incidents, idempotent partition-overwrite by business date).
- **E2E delivery**: GitLab CI → Terraform → deploy → pipeline → mart (The-1, my domains).
- **Regulatory/compliance data** (BOT reporting) — relevant lens for insurance (OIC/PDPA).
- **Cost-aware re-platform instinct** — exactly the migrate/cost-reduction angle they hint at.
