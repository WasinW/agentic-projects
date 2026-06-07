# Migration Playbooks — Deep Dive

> Real-world playbooks: BQ → Iceberg, monolithic → mesh, on-prem → cloud
> Risk-managed step-by-step migrations

---

## 1. Migration Mental Model

### Migration ≠ Lift and Shift

```
Bad: "Migrate all 500 tables in 1 quarter"
Good: "Migrate critical 50 tables with new patterns,
       deprecate legacy gradually"
```

### Strangler Fig Pattern (default)

```
1. Build new alongside old (both work)
2. Gradually move workloads to new
3. When confident, deprecate old
4. Old becomes archival reference
```

### Migration Risk Hierarchy

```
LOW RISK:
- Add new tables/views
- Add columns
- Backfill new derived data

MEDIUM RISK:
- Change pipelines
- Migrate dashboards
- Switch source systems

HIGH RISK:
- Replace primary storage
- Change schemas
- Cut over consumers

CRITICAL:
- Production decisioning
- Customer-facing systems
- Compliance/regulatory data
```

---

## 2. Playbook 1: BigQuery → Iceberg (Open Lakehouse)

### Why Migrate

- Cost (BQ storage + slot reservations expensive at scale)
- Vendor flexibility (work across Spark, Trino, Flink)
- Open format (no lock-in)
- Multi-engine analytics

### Pre-Migration Assessment

```
Inventory:
- How many tables?
- What size? (>1TB priority)
- Query patterns? (heavy compute → Iceberg wins)
- Update patterns? (CDC, batch, streaming)
- Consumer apps? (BI, ML, API)
- Dependencies between tables?
```

### Migration Phases

#### Phase 1: Foundation (Month 1-2)

```
Setup:
- Choose Iceberg catalog (REST, BigLake, Unity)
- Set up object storage layout
- Configure Spark/Dataflow with Iceberg
- Test small pilot table

Pilot:
- Pick 1-3 tables: medium size, non-critical
- Convert from BQ → Iceberg
- Run BOTH for 30 days
- Compare data + costs
```

#### Phase 2: Standardize (Month 3-4)

```
Patterns established:
- Standard ingestion path (Kafka → Beam → Iceberg)
- Standard transform path (dbt on Iceberg)
- Standard consumption (BQ External / Trino)

Migration tooling:
- BQ → Iceberg backfill scripts
- Schema mapping rules
- Validation framework

Run through 5-10 tables
Iterate on tooling
```

#### Phase 3: Bulk Migration (Month 5-9)

```
Batch by category:
- Easy: append-only fact tables
- Medium: dimension tables
- Hard: tables with frequent updates
- Last: tables with regulatory constraints

Per table:
1. Backfill historical to Iceberg
2. Set up new ingestion to write both BQ + Iceberg
3. Monitor parity for N weeks
4. Switch readers to Iceberg
5. Eventually: stop writing to BQ
6. Archive BQ table
```

#### Phase 4: Decommission (Month 10-12)

```
- Move final consumers
- Update documentation
- Archive BQ tables (cold storage)
- Eventually delete after retention period
```

### Tooling

#### Backfill Pattern

```python
# spark job
def migrate_table(source_bq, target_iceberg):
    # Read from BQ
    df = spark.read.format("bigquery") \
        .option("table", source_bq) \
        .load()
    
    # Map schema (handle BQ types not in Iceberg)
    df = transform_for_iceberg(df)
    
    # Write to Iceberg with partitioning
    df.write.format("iceberg") \
        .mode("overwrite") \
        .option("write-distribution-mode", "hash") \
        .partitionBy("event_date") \
        .saveAsTable(target_iceberg)
```

#### Dual-Write Pattern (during transition)

```python
@beam.PTransform
class WriteBoth(beam.PTransform):
    def expand(self, pcoll):
        # Write to both BQ and Iceberg
        bq_results = pcoll | "WriteBQ" >> WriteToBigQuery(table=bq_table)
        iceberg_results = pcoll | "WriteIceberg" >> WriteToIceberg(table=iceberg_table)
        return pcoll
```

#### Parity Validation

```sql
-- Daily check
WITH bq_counts AS (
    SELECT date, COUNT(*) AS n FROM bq_table GROUP BY date
),
iceberg_counts AS (
    SELECT date, COUNT(*) AS n FROM iceberg_table GROUP BY date
)
SELECT 
    bq.date,
    bq.n AS bq_count,
    ic.n AS iceberg_count,
    bq.n - ic.n AS diff
FROM bq_counts bq
JOIN iceberg_counts ic ON bq.date = ic.date
WHERE ABS(bq.n - ic.n) > 0;
```

### Rollback Plan

```
At any phase:
- Both systems still running (until decommission)
- Switch readers back to BQ
- Investigate issue
- Re-attempt
```

### Cost Tracking

```
Before:
  BQ storage: $X
  BQ compute (slots/on-demand): $Y
  Total: $X+Y

After:
  GCS storage (Iceberg): ~10% of $X
  Compute (Spark/Dataflow on demand): variable
  BQ compute on external Iceberg: 50-80% of $Y
  Total: usually 30-60% reduction
```

---

## 3. Playbook 2: On-Prem → Cloud Data Platform

### Reasons to Migrate

- Reduce TCO (long-term)
- Faster innovation
- Better managed services
- Disaster recovery
- Modernization (banking move from Hadoop → cloud)

### Pre-Migration Assessment

```
Infrastructure:
- Existing systems (Hadoop, Teradata, Oracle, etc.)
- Data volume + growth rate
- Network bandwidth available
- Compliance constraints (data residency)

Application:
- Number of pipelines
- Programming languages used
- Custom code volume
- Test coverage

People:
- Cloud skills?
- Training needed?
- Vendor support?
```

### Migration Strategies

#### Strategy 1: Lift-and-Shift (legacy)
```
Move existing infra to cloud as-is
Pros: fastest, less risk
Cons: doesn't realize cloud benefits, cost similar
Use case: tight timeline, will modernize later
```

#### Strategy 2: Re-Platform (better)
```
Move + slight refactor
Hadoop → Dataproc / EMR (managed Spark)
Oracle → Cloud SQL / RDS
Pros: easier ops, some benefits
Cons: still legacy patterns
```

#### Strategy 3: Re-Architect (best)
```
Move + redesign for cloud
Hadoop → Lakehouse (Iceberg + Spark/Dataflow)
Teradata → BigQuery / Snowflake
Pros: full cloud benefits
Cons: most effort
```

### Phased Approach

#### Phase 1: Foundation (Month 1-3)
```
- Cloud account setup (organization, billing, IAM)
- Network (VPN, Direct Connect/Interconnect)
- Identity (federation with corporate IdP)
- Security baseline (encryption, audit, access)
- Compliance framework
- Cost controls (budgets, alerts)
```

#### Phase 2: Pilot (Month 4-6)
```
- Pick 1 use case (low-risk, high-visibility)
- Build entire cloud stack for it
- Migrate data + pipelines
- Run in parallel with on-prem
- Measure: cost, performance, reliability
- Iterate on platform learnings
```

#### Phase 3: Wave Migration (Month 7-18)
```
Group workloads by:
- Business priority
- Technical complexity
- Risk level

Wave 1 (Month 7-9): low risk, well-understood
Wave 2 (Month 10-12): medium complexity
Wave 3 (Month 13-18): critical / complex

Per workload:
1. Assessment
2. Design cloud version
3. Build alongside on-prem
4. Migrate data
5. Validate
6. Cutover
7. Decommission on-prem
```

#### Phase 4: Optimization (Month 19+)
```
- Cost optimization (right-sizing, reserved capacity)
- Performance tuning
- Modern patterns adoption (streaming, ML)
- Decommission remaining on-prem
```

### Data Transfer Methods

#### Method 1: Network Transfer
```
For: smaller volumes (< 10 TB)
Tools: gsutil, aws s3 cp, distcp

Speed:
  10 Gbps: ~1 GB/sec → 10 TB in ~3 hours
  1 Gbps:  ~100 MB/sec → 10 TB in ~30 hours
```

#### Method 2: Physical Transfer
```
For: large volumes (100 TB+)
Tools: AWS Snowball, GCP Transfer Appliance, Azure Data Box

Process:
1. Order device (large disk array)
2. Ship to your DC
3. Copy data locally
4. Ship back to cloud
5. Cloud uploads to bucket

Speed: ~1-2 weeks for hundreds of TB
```

#### Method 3: Streaming Replication
```
For: live data, ongoing sync
Tools: Debezium CDC, Storage Transfer Service

Continuous replication during migration period
Cutover when source stops
```

### Application Migration Patterns

#### Pattern 1: Spark Jobs
```
On-prem Hadoop Spark → Cloud Dataproc / EMR / Databricks

Code changes minimal:
- File paths (HDFS → S3/GCS)
- Cluster config
- Some library compatibility
```

#### Pattern 2: Hive → BigQuery / Athena
```
HiveQL mostly compatible with Spark SQL
Some functions different
Test thoroughly
```

#### Pattern 3: Oracle → BigQuery / Cloud SQL
```
Schema mapping (data types)
PL/SQL → stored procedures or rewrite
ETL jobs → Dataflow or Composer
```

#### Pattern 4: Teradata → BigQuery / Snowflake
```
SQL dialect translation
Stored procedures rewrite
Reports validation
Performance tuning
```

---

## 4. Playbook 3: Monolithic → Data Mesh

### Why (and Why Not)

✅ Migrate to Mesh when:
- 30+ data engineers spread across domains
- Central team is clear bottleneck
- Domains have data + tech maturity
- Clear domain boundaries exist

❌ Don't migrate when:
- < 20 engineers total
- Domains lack data skills
- No clear domain boundaries
- Just chasing trend

### Migration Approach

#### Phase 1: Self-Service Platform (Month 1-6)
```
Goal: empower domains BEFORE giving ownership

Build:
- Self-service pipeline templates
- Self-service data catalog access
- Self-service dashboard creation
- Standardized tools

Result: domains can do MORE without DE
```

#### Phase 2: First Domain Spin-out (Month 7-9)
```
Pick: one volunteer domain with data savvy
- Marketing or Customer Insights typically

Process:
1. Identify domain's data products
2. Move ownership to domain team
3. Central team becomes "consultants"
4. Domain owns pipelines + quality

Learn from this domain
Iterate platform
```

#### Phase 3: Scale (Month 10-24)
```
Per domain (3-6 month each):
- Train team
- Move ownership gradually
- Establish data contracts
- Federated governance

Scale 3-5 domains in parallel after first
```

#### Phase 4: Mature Mesh (Month 24+)
```
Central team:
- Maintains platform (no pipelines)
- Sets standards (governance)
- Enables (training, support)

Each domain:
- Owns data products
- Maintains pipelines
- Publishes data contracts
- Consumes from other domains
```

### Critical Success Factors

```
1. Tooling enables self-service (or fail)
2. Data contracts mandatory between domains
3. Central catalog visible across mesh
4. Governance federation (not central enforcement)
5. Cultural change (not just technical)
```

### Common Failure Modes

```
❌ Mesh without platform = Distributed Monolith
   (everyone does their own thing, no standards)

❌ Mesh without skills = Data Mess
   (domains lack capability, quality drops)

❌ Premature mesh = wasted effort
   (organization too small, central works fine)

❌ Mesh as 100% transition
   (everything mesh = some workloads better central)
```

---

## 5. Playbook 4: Schema Evolution Migration

### Common Scenario

```
Production schema: V1
Need: change column type / rename / restructure
Constraint: zero downtime, no data loss
```

### Pattern: Expand-Contract

#### Step 1: Expand (add new alongside old)
```sql
-- V1: customer_email
-- Add: email (new column)
ALTER TABLE customers ADD COLUMN email STRING;

-- Backfill new from old
UPDATE customers SET email = customer_email;

-- Producers write BOTH
-- Consumers can read either
```

#### Step 2: Migrate consumers
```
1. Update consumer code to read 'email'
2. Deploy + verify
3. Continue maintaining both
```

#### Step 3: Producers stop writing old
```
After all consumers migrated:
1. Producer writes only 'email'
2. Old column becomes stale (still exists)
```

#### Step 4: Contract (drop old)
```sql
-- After deprecation period (30+ days)
ALTER TABLE customers DROP COLUMN customer_email;
```

### Pattern: Versioned Tables

```sql
-- Keep V1 + create V2
CREATE TABLE customers_v2 AS ...;

-- Switch consumers gradually
-- V1 + V2 both written

-- Eventually: drop V1
```

### Schema Migration Tools

#### Iceberg (best for lakehouse)
```sql
-- Iceberg tracks columns by ID, not name
ALTER TABLE customers RENAME COLUMN email TO email_address;
-- Existing files compatible (still read by ID)

ALTER TABLE customers ADD COLUMN phone STRING;
-- Old files: phone is null

ALTER TABLE customers DROP COLUMN deprecated_col;
-- Just metadata change
```

#### Liquibase (relational DB)
```xml
<changeSet id="add-email-column">
    <addColumn tableName="customers">
        <column name="email" type="VARCHAR(255)"/>
    </addColumn>
</changeSet>
```

#### Flyway (relational DB)
```sql
-- V1.4__add_email_column.sql
ALTER TABLE customers ADD COLUMN email VARCHAR(255);
```

---

## 6. Playbook 5: Streaming Pipeline Migration

### Hardest Migration: Live Streaming

```
Old streaming pipeline: running 24/7, processing real events
New version: better/different
Goal: cutover with minimal data loss
```

### Pattern: Dual-Run

```
1. Deploy NEW pipeline alongside OLD
2. Both consume same source (Kafka/PubSub)
   - Use different consumer group ID
3. Both produce to different sinks
   - OLD writes to current_table
   - NEW writes to new_table
4. Compare outputs for parity (X days)
5. Switch consumers from old → new
6. Stop old pipeline
```

### Backfill Strategy

```
NEW pipeline launches → starts from current time
Old data only in OLD output

To backfill:
- Replay Kafka from beginning
- OR: Read from Iceberg snapshots
- OR: Run batch backfill alongside

Tricky: deduplication if both pipelines wrote same data period
```

### State Migration

```
OLD pipeline has stateful operators (counters, sessions)
NEW pipeline starts with empty state

Options:
1. Wait for state to "warm up" (best for short windows)
2. Save state from old, load in new (Flink: savepoints)
3. Re-process from start (Kafka replay)
```

### Cutover Protocol

```
Day 0: Deploy NEW (parallel)
Day 1-7: Both running, compare outputs
Day 8: Investigate any discrepancies
Day 9: Fix and continue
Day 10-14: Full parity confirmed
Day 15: Switch consumers to NEW
Day 16-21: Monitor closely
Day 22: Stop OLD, archive
```

---

## 7. Playbook 6: ML Model Migration

### Scenarios

- Replace v1 model with v2 (better accuracy)
- Migrate from cloud ML service to self-hosted
- Switch ML framework (TF → PyTorch)
- Move from prototype to production

### Shadow Deployment

```
Production traffic
   ├──→ V1 (current) → response to user
   └──→ V2 (new) → log only (no impact)

Compare V1 vs V2 outputs offline
When confident: V2 takes over
```

### Canary Deployment

```
Day 1: 5% traffic → V2, 95% → V1
        Monitor V2 metrics
Day 3: 10% → V2 (if OK)
Day 7: 25% → V2
Day 10: 50% → V2
Day 14: 100% → V2

Roll back if metrics degrade
```

### A/B Testing

```
Cohort A: see V1 predictions
Cohort B: see V2 predictions
Run for X weeks
Compare business metrics (conversion, engagement)
Statistical test → pick winner
```

### Model Cards & Approval

```
Document V2:
- Performance metrics
- Comparison vs V1
- Bias audit
- Limitations
- Training data + version
- Reviewer sign-offs

Required before promotion to production
```

---

## 8. Playbook 7: Vendor Migration (e.g., Snowflake → Databricks)

### Why

- Cost optimization
- Feature gaps
- Strategic shift (e.g., toward open formats)
- Acquired by competitor (e.g., Tecton acquisition)

### Phases

#### Phase 1: Inventory
```
- All databases / schemas / tables
- All views / stored procedures
- All BI tools and reports
- All ML pipelines
- All ETL jobs
- Data dependencies
```

#### Phase 2: Compatibility Audit
```
SQL dialect differences
Function compatibility
Data type compatibility
Performance characteristics
Cost model differences
```

#### Phase 3: Prioritize
```
Easy first:
- Append-only fact tables
- Simple SELECT queries

Hardest last:
- Complex stored procedures
- Tightly-coupled pipelines
- Heavily-customized features
```

#### Phase 4: Migrate in Waves
```
Wave 1: Pilot
Wave 2: Low-risk domains
Wave 3: Mid-risk
Wave 4: Critical
```

### Tools

```
- dbt portability (SQL mostly works)
- BigQuery/Snowflake to Iceberg utilities
- Apache Spark for cross-platform jobs
- Vendor-provided migration tools
```

---

## 9. Risk Management Across Migrations

### Always Have:

#### 1. Rollback Plan
```
Document exact steps to revert
Test rollback in staging
Time the rollback (need to know SLA)
```

#### 2. Parallel Run Period
```
Both old + new running
Compare outputs
Verify before cutover
```

#### 3. Data Validation
```
Row counts match
Sums match
Distribution check
Sample records verified
```

#### 4. Monitoring
```
Both old + new monitored
Same dashboards
Alert on divergence
```

#### 5. Communication Plan
```
Stakeholders know:
- Schedule
- What to expect
- How to report issues
- Who to contact
```

### Anti-Patterns

```
❌ Big-bang migration ("flip the switch")
❌ No rollback plan
❌ No validation
❌ Skip pilot
❌ Underestimate ops complexity
❌ Ignore cost during migration (running 2x)
```

---

## 10. Migration Cost (don't ignore)

### Hidden Costs

```
- 2x infrastructure during overlap (often months)
- Engineering time (massive!)
- Training/upskilling
- Tool licenses (migration tools)
- Consulting (often needed)
- Lost productivity during migration
```

### Realistic Estimate

```
Migration takes 2-3x longer than expected
Costs 1.5-2x estimated
Always budget contingency
```

### ROI Timeline

```
Migration: -X over 1 year (cost)
Optimization: +Y/year ongoing (savings)

Break-even: typically 2-3 years
Long-term ROI: 3-5x
```

---

## 11. Common Mistakes Across All Migrations

### Mistake 1: Underestimating Effort
```
Quote: "We'll migrate 100 tables in 1 quarter"
Reality: 4 quarters

Lesson: pilot first, extrapolate
```

### Mistake 2: No Sponsor / Funding
```
Migration started, money runs out, half-done state
Worst-of-both-worlds (legacy + new running)

Lesson: secure full funding upfront
```

### Mistake 3: Skipping Validation
```
"It compiled, ship it"
Production: data corrupted, nobody noticed
Discovery 2 months later

Lesson: parity validation mandatory
```

### Mistake 4: No User Training
```
Move from Postgres → Snowflake
Engineers still use Postgres patterns
Slow queries, high cost

Lesson: invest in training
```

### Mistake 5: Forgetting Compliance
```
Migrate Thai data to US-region cloud
GDPR/PDPA violation

Lesson: compliance review pre-migration
```

### Mistake 6: Boil the Ocean
```
"Modernize EVERYTHING"
3 years later: nothing complete

Lesson: incremental, prioritized
```

### Mistake 7: Not Measuring Success
```
Migration "complete"
But: still using old patterns
Cost not reduced
Speed not improved

Lesson: define + measure outcomes
```

---

## 12. Cheat Sheet

### Q: "เริ่ม migration ยังไง?"
> "1. Inventory + assess (don't underestimate)
> 2. Pilot 1-3 things (learn)
> 3. Build tooling + patterns
> 4. Wave migration (priority order)
> 5. Validate parity ALWAYS
> 6. Decommission gradually"

### Q: "BQ → Iceberg ใช้เวลานานแค่ไหน?"
> "Pilot: 1-2 months
> Bulk migration: 6-9 months for 100+ tables
> Full decommission: 12-18 months
> Cost reduction realized: ongoing after"

### Q: "Lift-and-shift หรือ re-architect?"
> "Lift-and-shift: faster but doesn't realize cloud benefits
> Re-architect: most value but 2-3x effort
> Pragmatic: re-architect critical, lift-and-shift legacy"

### Q: "Streaming pipeline migrate ยังไง?"
> "Hardest! Dual-run pattern:
> 1. Deploy NEW alongside OLD
> 2. Both consume + produce
> 3. Compare outputs
> 4. Switch consumers to NEW
> 5. Decommission OLD"

### Q: "Migration ล้มเหลวเพราะอะไร?"
> "Top causes:
> 1. Underestimating effort (2-3x typical)
> 2. No rollback plan
> 3. Skipping validation
> 4. Boiling the ocean
> 5. Lost executive sponsorship"

---

## Sources

- [Strangler Fig Pattern - Martin Fowler](https://martinfowler.com/bliki/StranglerFigApplication.html)
- [Cloud Migration Strategies - AWS](https://aws.amazon.com/cloud-migration/how-to-migrate/)
- [Google Cloud Migration Center](https://cloud.google.com/migration-center)
- [Iceberg Migration Guide](https://iceberg.apache.org/docs/latest/spark-procedures/#snapshot)
- [Data Mesh Migration Patterns - Zhamak Dehghani](https://www.thoughtworks.com/insights/blog/data-mesh-principles-and-logical-architecture)
- [Database Migration Best Practices - Oracle](https://www.oracle.com/database/migration/cloud/)
- [Apache Iceberg Migration Guide](https://iceberg.apache.org/spark-procedures/#snapshot)
