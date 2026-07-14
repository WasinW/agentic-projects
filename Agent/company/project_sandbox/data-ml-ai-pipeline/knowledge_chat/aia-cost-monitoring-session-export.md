---
title: AIA Azure Cost Monitoring — Complete Session Export
project: Cost Monitoring Dashboard PoC at AIA
role: Senior Data Engineer (Sin / วศิน)
team_context:
  - พี่ Sarunya (Senior DE, solution-level guidance)
  - บูม (น้อง, existing dashboard owner)
  - Sin (assigned to help บูม + Sarunya's guidance)
session_date: 2026-07-10
purpose: Full context export for VS Code continuation
---

# AIA Azure Cost Monitoring — Complete Session Export

## Table of Contents

1. [Business Context & Requirements](#1-business-context--requirements)
2. [Technical Approach Evolution](#2-technical-approach-evolution)
3. [Authentication Journey](#3-authentication-journey)
4. [Cost Management Export Deep Dive](#4-cost-management-export-deep-dive)
5. [Tag Handling Design](#5-tag-handling-design)
6. [Pipeline Architecture (5 Layers)](#6-pipeline-architecture-5-layers)
7. [Development Pattern](#7-development-pattern)
8. [Dashboard Storytelling](#8-dashboard-storytelling)
9. [Multi-Tenant Access Options](#9-multi-tenant-access-options)
10. [Dashboard Deployment](#10-dashboard-deployment)
11. [Automation Strategy](#11-automation-strategy)
12. [Team Structure & Communication](#12-team-structure--communication)
13. [Open Questions & Next Actions](#13-open-questions--next-actions)

---

## 1. Business Context & Requirements

### Original Request
- Need: Databricks notebook → dashboard monitoring cost per service in resource groups
- PoC scope: pull resources info + cost from Azure

### Refined Scope (from พี่ Sarunya's meeting info)
```
Requirements ที่ยืนยัน:
1. AIA policy: no data cross env (except cost from Portal)
2. Cost data มาจาก Portal → cross-env exception ok
3. Dashboard เห็น cost ทุก env (แม้ pipeline อยู่ DEV)
4. Tag ตามทีม → chargeback per team
5. Dashboard อยู่บน "IT workspace" (Sin's team's workspace)
6. User (client teams) ไม่มีสิทธิ์เข้า IT workspace
7. ต้องหา "วิธีการแชร์" dashboard
8. แจ้ง user ทุกเดือน (monthly cadence signal)
```

### Team Assignment
- หัวหน้าจริง assign Sin → ช่วยบูม (existing dashboard owner)
- พี่ Sarunya = Senior DE, provides solution-level guidance (คล้าย SA)
- Existing pipeline มีอยู่แล้ว — Sin จะ enhance หรือ new track TBD

---

## 2. Technical Approach Evolution

### Options Considered

#### Option A: Query API from Databricks
```
Databricks → Azure Cost Management API (query)
├── Real-time (4hr delay)
├── Complex code (retry, rate limits)
├── Free API, has QPU limits
└── Needs auth (SPN/MI/User)
```

#### Option B: Cost Management Exports → ADLS → Databricks ⭐
```
Portal Export (schedule) → ADLS (Parquet)
   ↓ Auto Loader
Databricks reads
├── No API rate limits
├── Automated
├── Rich data (40+ columns)
└── No auth complexity (system-driven)
```

#### Option C: Manual Portal Download → Databricks
```
Sin download CSV → upload Databricks Volume
├── Simplest
├── Manual weekly
├── No infrastructure change
└── Works with user's Portal access
```

### Colleague's Actual Approach (Discovered)
พี่เค้าใช้ **Cost Management Exports** (Option B pattern):
1. Schedule export on Portal → writes to ADLS
2. Run ingest job (config-driven, similar to SCB)
3. Transform layers: ingest → persist → prepare → summary
4. Dashboard reads from summary table
5. **Removes tags** in transform (Sin's differentiator = keep tags)

### Cost Management API Pricing (Researched)
- **Free** — no per-call cost
- Rate limits (429 Too Many Requests)
- QPU quotas (1 QPU per month of data queried)
- Data refresh every 4 hours
- Microsoft recommends 1x/day query cadence
- Max 12 months historical (API), 13 months (Portal Exports)
- Up to 7 years via REST API historical

---

## 3. Authentication Journey

### Attempts & Blockers

#### Attempt 1: Device Code Flow
```python
from azure.identity import DeviceCodeCredential
credential = DeviceCodeCredential(
    tenant_id=AIA_TENANT_ID,
    client_id="04b07795-8ddb-461a-bbee-02f9e1bf7b46"  # Azure CLI public
)
```
**Result:** ❌ AADSTS530033 — "Remote device flow blocked due to device-based conditional access"

**Root cause:**
- CA policy requires managed device
- Databricks cluster = not managed
- Token recipient device check fails

#### Auth Options Analysis
| Method | Works at AIA? | Complexity |
|---|---|---|
| Device Code Flow | ❌ Blocked (530033) | Low |
| User Credential | ❌ Same CA block | Low |
| Azure CLI Credential | ❌ Same CA block | Low |
| Service Principal (SPN) | ✅ Works | High (Key Vault + Secret Scope) |
| Managed Identity (MI) | ✅ Should work | Medium (Access Connector) |

### Concepts Refreshed
- **Microsoft Entra ID** = identity provider (auth service)
- **Tenant** = organization boundary in Entra ID
- **Tenant ID** = AIA's org GUID
- **Service Principal (SPN)** = app identity (not human)
- **App Registration** = process to create SPN
- **Client ID** = SPN's "employee ID"
- **Client Secret** = SPN's "password"
- **Access Token** = temporary "visitor badge" (~1hr)
- **RBAC** = permission assignment (Role at Scope)
- **Key Vault** = secret storage
- **Databricks Secret Scope** = connector to Key Vault

### Public Client ID Note
For Device Code Flow, use Microsoft's well-known public client IDs (no admin needed):
- Azure CLI: `04b07795-8ddb-461a-bbee-02f9e1bf7b46`
- Azure PowerShell: `1950a258-227b-4e31-a9cf-717495945fc2`
- Visual Studio: `872cd9fa-d31f-45e0-9eab-6e460a02d1f1`
- VS Code: `aebc6443-996d-45c2-90f0-388ff96faa56`

### Key Insight
- Auth ≠ Authorization
- Any identity type can access Cost Management API IF granted `Cost Management Reader` role
- Sin's confusion: mixing "auth method" with "permission"

### Solution Realization
Since API-based approaches all failed (or need heavy setup), **Cost Management Export (Option B)** is elegant because:
- Azure Cost Management system runs export with its own identity
- Writes to ADLS
- Databricks just reads ADLS (existing capability)
- Zero auth complexity for Databricks side

---

## 4. Cost Management Export Deep Dive

### 4 Export Types

#### 1. ActualCost (2023-05-01)
- "Billing view" — as-billed
- Reservation purchase = single spike on buy date
- ChargeType: Usage, Purchase, Refund
- Best for: Invoice reconciliation, cash flow

#### 2. AmortizedCost (2023-05-01)
- "Usage view" — smoothed
- Reservation cost spread daily
- ChargeType: Usage, UnusedReservation, UnusedSavingsPlan
- Best for: Daily trends, chargeback, FinOps

#### 3. PriceSheet (2023-05-01)
- "Rate card" — no usage data
- Meter → price mapping
- ~20 fields
- Join key: MeterId
- Best for: Cost optimization analysis

#### 4. FOCUS (1.0r2)
- Cross-cloud standard (FinOps Foundation)
- Combines Actual + Amortized in single file
- Fields: BilledCost, EffectiveCost, ContractedCost, ListCost
- Tags = proper JSON (no wrapping needed)
- ⚠️ Management Group scope not supported

### Comparison Table

| Feature | ActualCost | AmortizedCost | PriceSheet | FOCUS |
|---|---|---|---|---|
| Latest version | 2023-05-01 | 2023-05-01 | 2023-05-01 | 1.0r2 |
| Has ResourceId | ✅ | ✅ | ❌ | ✅ |
| Has Tags | ✅ (near-JSON) | ✅ (near-JSON) | ❌ | ✅ (JSON) |
| Reservation timing | Purchase spike | Spread daily | N/A | Both fields |
| Best for | Finance | FinOps | Optimization | Future-proof |

### Format Options
- **CSV** (no compression or +Gzip)
- **Parquet** (no compression or +Snappy) ⭐
- File partitioning: ON by default
- File overwrite: ON option (same-day rerun)

### Customization
- **Portal UI**: No custom columns (all included)
- **REST API / Bicep / Terraform**: 
  - Pick columns via `configuration.columns`
  - Filter via `configuration.filters`
  - Specify `configuration.dataVersion`

### Path Structure
```
<storage>.dfs.core.windows.net/
  <container>/
    <root>/
      <export-name>/
        <YYYYMMDD-YYYYMMDD>/    # billing period
          <YYYYMMDD>/            # run date
            _manifest.json       # index
            part_0_001.parquet
            part_0_002.parquet
```

### Historical Backfill
- Portal: 13 months back
- REST API: up to 7 years back

### Colleague's Setup (Discovered Pattern)
Colleague uses **3-4 exports** with full pipeline:
- ActualCost
- AmortizedCost
- PriceSheet
- (Possibly FOCUS)

Pipeline: schedule export → ingest → persist → prepare → join & summary

---

## 5. Tag Handling Design

### Problem Discovery
- Cost Management Export has **1 Tags column** (near-JSON format)
- All tag key-value pairs stored as string: `"Environment":"Prod","Owner":"team-a"`
- Missing `{` `}` wrapping (legacy format)
- Colleague's pipeline **removes tags** in transform — Sin's key differentiator = **retain tags**

### Sin's Case Refinement
Actual state Sin observed:
- Table from colleague has `tagAksxxx`, `tagXxx` columns
- Not raw export — already processed
- Custom transform pipeline splits tags into columns
- AKS-focused (specific tag keys)

### Design Options Analysis

#### Option 1: MAP<string, string> ⭐ Chosen
```sql
from_json(
    CASE WHEN Tags IS NOT NULL AND Tags != ''
         THEN CONCAT('{', Tags, '}')
         ELSE NULL END,
    'MAP<STRING, STRING>'
) AS tags
```
- ✅ Schema stable
- ✅ New keys auto-work
- ✅ All tags preserved

#### Option 2: STRUCT (Typed)
- ❌ Rigid — new keys ignored

#### Option 3: Explode to Long Format
- ✅ Great for governance queries
- ❌ Row explosion

#### Option 4: Map + Common Column Extracts
- ✅ Best of both

### Terminology Clarified
| Operation | Meaning | Use Case |
|---|---|---|
| **explode** | 1 row → N rows (long format) | Governance |
| **expand/flatten/pivot** | 1 row map → 1 row N cols (wide) | Dashboard ⭐ |

### Sin's Chosen Approach: MAP + Wide Expand

**Layered pattern:**
```
silver_cost         → MAP-based (compact, flexible)
silver_cost_wide    → Wide format (dashboard-friendly) ⭐
silver_cost_by_tag  → Long format view (governance)
```

**Wide expansion pattern (Python):**
```python
def expand_tags_to_columns(df, min_occurrence_pct=1.0):
    """Auto-discover + expand tag keys as columns"""
    total_rows = df.count()
    threshold = total_rows * (min_occurrence_pct / 100)
    
    tag_stats = (df
        .select(explode("tags").alias("k", "v"))
        .groupBy("k").count()
        .filter(f"count >= {threshold}")
        .collect())
    
    for row in tag_stats:
        safe_col = "tag_" + re.sub(r'[^a-z0-9]+', '_', row["k"].lower())
        df = df.withColumn(safe_col, col("tags").getItem(row["k"]))
    
    return df
```

**Config-driven (SCB-style):**
```yaml
expand_config:
  min_occurrence_pct: 0.5
  force_include_keys: [environment, costcenter, owner, compliance]
  force_exclude_keys: [temp, test]
  key_aliases:
    tag_environment: [environment, env, Environment, ENV]
    tag_cost_center: [costcenter, cost_center, CostCenter, cc]
```

---

## 6. Pipeline Architecture (5 Layers)

### Layer Design (Matches Colleague's Pattern + Tags)

```
Portal Exports (schedule)
      ↓
ADLS Landing Zone
      ↓
┌─────────────────────────────────────┐
│ Layer 1: Bronze (raw ingest)        │
│  ├── bronze_actual                   │
│  ├── bronze_amortized                │
│  └── bronze_pricesheet               │
├─────────────────────────────────────┤
│ Layer 2: Persist (typed + tags MAP) │
│  ├── persist_actual (+ tags) ⭐     │
│  ├── persist_amortized (+ tags) ⭐  │
│  └── persist_pricesheet             │
├─────────────────────────────────────┤
│ Layer 3: Prepare (enrichment)       │
│  ├── prep_actual                     │
│  ├── prep_amortized                  │
│  └── prep_pricesheet                 │
├─────────────────────────────────────┤
│ Layer 4: Summary (JOIN 3 sources)   │
│  └── summary_cost_with_tags ⭐⭐   │
├─────────────────────────────────────┤
│ Layer 5: Gold (Dashboard views)     │
│  ├── gold_cost_wide (tags → cols)   │
│  ├── gold_monthly_by_service         │
│  ├── gold_cost_by_environment        │
│  ├── gold_chargeback                 │
│  └── gold_top_resources              │
└─────────────────────────────────────┘
```

### Layer 2: Persist SQL (Tags Parsing)

```sql
CREATE OR REPLACE TABLE sandbox.cost.persist_actual
USING DELTA
PARTITIONED BY (usage_date)
AS
SELECT 
    BillingAccountId AS billing_account_id,
    SubscriptionId AS subscription_id,
    ResourceGroup AS resource_group,
    ResourceId AS resource_id,
    ResourceType AS resource_type,
    ServiceFamily AS service_family,
    ServiceName AS service_name,
    MeterCategory AS meter_category,
    MeterId AS meter_id,          -- ⭐ join key
    MeterName AS meter_name,
    Date AS usage_date,
    CAST(Quantity AS DECIMAL(18, 6)) AS quantity,
    CAST(EffectivePrice AS DECIMAL(18, 6)) AS effective_price,
    CAST(CostInBillingCurrency AS DECIMAL(18, 4)) AS cost,
    BillingCurrency AS currency,
    ChargeType AS charge_type,
    PricingModel AS pricing_model,
    ReservationId AS reservation_id,
    -- ⭐ TAGS retained as MAP (Sin's addition)
    from_json(
        CASE WHEN Tags IS NOT NULL AND Tags != ''
             THEN CONCAT('{', Tags, '}') ELSE NULL END,
        'MAP<STRING, STRING>'
    ) AS tags
FROM sandbox.cost.bronze_actual
WHERE CostInBillingCurrency IS NOT NULL;
```

### Layer 4: Summary SQL (Join 3 Sources)

```sql
WITH actual_agg AS (
    SELECT 
        usage_date, subscription_id, resource_group,
        resource_id, service_name, meter_id,
        SUM(quantity) AS actual_quantity,
        SUM(cost) AS actual_cost,
        currency,
        first(tags, true) AS tags,  -- ⭐ tags kept
        first(pricing_model, true) AS pricing_model,
        first(reservation_id, true) AS reservation_id
    FROM prep_actual
    GROUP BY usage_date, subscription_id, resource_group,
             resource_id, service_name, meter_id, currency
),
amortized_agg AS (
    SELECT 
        usage_date, subscription_id, resource_group,
        resource_id, service_name, meter_id,
        SUM(quantity) AS amortized_quantity,
        SUM(cost) AS amortized_cost,
        currency
    FROM prep_amortized
    GROUP BY usage_date, subscription_id, resource_group,
             resource_id, service_name, meter_id, currency
)
SELECT 
    COALESCE(a.usage_date, am.usage_date) AS usage_date,
    COALESCE(a.subscription_id, am.subscription_id) AS subscription_id,
    COALESCE(a.resource_group, am.resource_group) AS resource_group,
    COALESCE(a.resource_id, am.resource_id) AS resource_id,
    COALESCE(a.service_name, am.service_name) AS service_name,
    COALESCE(a.meter_id, am.meter_id) AS meter_id,
    
    -- PriceSheet enrichment
    ps.meter_category, ps.meter_subcategory,
    ps.meter_name, ps.product_name, ps.sku_name, ps.unit,
    
    -- Both cost views
    a.actual_cost,
    am.amortized_cost,
    
    -- Price benchmarking
    ps.list_price,
    (am.amortized_cost - a.actual_cost) AS reservation_amortization_diff,
    
    -- ⭐ Tags retained
    a.tags,
    
    COALESCE(a.currency, am.currency) AS currency
FROM actual_agg a
FULL OUTER JOIN amortized_agg am
    ON a.usage_date = am.usage_date
    AND a.resource_id = am.resource_id
    AND a.meter_id = am.meter_id
LEFT JOIN prep_pricesheet ps
    ON COALESCE(a.meter_id, am.meter_id) = ps.meter_id;
```

### Layer 5: Gold Views

```sql
-- Tags expanded to columns
CREATE OR REPLACE VIEW gold_cost_wide AS
SELECT *,
    tags['environment'] AS tag_environment,
    tags['costcenter'] AS tag_cost_center,
    tags['owner'] AS tag_owner,
    tags['application'] AS tag_application,
    tags['akscluster'] AS tag_aks_cluster,
    tags['aksnamespace'] AS tag_aks_namespace,
    tags['compliance'] AS tag_compliance
FROM summary_cost_with_tags;

-- Chargeback view
CREATE OR REPLACE VIEW gold_chargeback AS
SELECT 
    COALESCE(tag_cost_center, 'untagged') AS cost_center,
    COALESCE(tag_owner, 'unknown') AS owner,
    date_trunc('month', usage_date) AS month,
    SUM(amortized_cost) AS chargeback_amount,
    currency
FROM gold_cost_wide
GROUP BY tag_cost_center, tag_owner,
         date_trunc('month', usage_date), currency;
```

---

## 7. Development Pattern

### Dev Phase (Notebook Exploration)

```python
# Build with WITH statements → df → temp view
persist_actual_df = spark.sql("""
    WITH parsed AS (
        SELECT ..., 
               from_json(CONCAT('{', Tags, '}'), 
                         'MAP<STRING, STRING>') AS tags
        FROM bronze_actual
    )
    SELECT * FROM parsed
""")

persist_actual_df.createOrReplaceTempView("persist_actual")

# Fast iteration, no I/O
```

### Prod Phase (Job Execution)

```sql
INSERT OVERWRITE TABLE sandbox.cost.persist_actual
    PARTITION (usage_date = '{TARGET_DATE}')
SELECT ... FROM persist_actual  -- reuse dev SQL
WHERE usage_date = '{TARGET_DATE}'
```

**Benefit:** SQL logic identical between dev and prod

### Config-Driven Pattern (SCB-style)
```python
LAYER_CONFIG = [
    {
        "name": "persist_actual",
        "source": "bronze_actual",
        "sql_file": "sql/persist_actual.sql",
        "partition_col": "usage_date",
    },
    # ... more layers
]

def run_layer(config, mode="dev"):
    if mode == "dev":
        df = spark.sql(open(config["sql_file"]).read())
        df.createOrReplaceTempView(config["name"])
    elif mode == "prod":
        spark.sql(f"""
            INSERT OVERWRITE TABLE {config['name']}
                PARTITION ({config['partition_col']} = '{target_date}')
            {sql}
        """)
```

### Profile / Validation Cells

```python
# Row counts per layer
for name, df in [("persist_actual", persist_actual_df), ...]:
    print(f"{name}: {df.count():,} rows, {len(df.columns)} cols")

# Tag coverage
spark.sql("""
    SELECT COUNT(*) AS total,
           COUNT(tags) AS has_tags,
           ROUND(100.0 * COUNT(tags) / COUNT(*), 2) AS coverage_pct
    FROM summary_cost_with_tags
""")

# Discover tag keys
spark.sql("""
    SELECT tag_key, COUNT(DISTINCT resource_id) AS resource_count
    FROM summary_cost_with_tags
    LATERAL VIEW OUTER explode(tags) t AS tag_key, tag_value
    GROUP BY tag_key
    ORDER BY resource_count DESC
""")
```

---

## 8. Dashboard Storytelling

### 5 Levels Framework

| Level | Question | Audience | Purpose |
|---|---|---|---|
| **1. What?** | เท่าไหร่แล้ว? | Everyone | Current state pulse |
| **2. Where?** | เงินไปที่ไหน? | Managers | Distribution |
| **3. When?** | เปลี่ยนแปลงยังไง? | FinOps | Trends |
| **4. Who?** | ใครเป็นเจ้าของ? | Finance | Accountability |
| **5. Why?** | ทำไม? | Engineers | Investigation |

### Multi-Page Structure
- Page 1: Overview (Level 1)
- Page 2: Breakdown (Level 2)
- Page 3: Trends & Anomalies (Level 3)
- Page 4: Chargeback (Level 4)
- Page 5: Deep Dive (Level 5)

### Sin's Original Overview Design (Reviewed)
1. Sum cost per project (pie)
2. Sum cost per region (pie)
3. Sum cost per month per project (area)
4. Sum cost per month per app service (area)
5. Sum cost per cloud service (pie)
6. Sum cost per month per service (area)

**Issues identified:**
- No KPI headline (user doesn't know current cost)
- No change indicator
- 3 pies = redundant, hard to compare
- 3 area charts = time-heavy
- No anomaly indicators

### Recommended Overview Layout
```
Row 1: 4 KPI Tiles
  ├── MTD Cost
  ├── vs Last Month
  ├── Forecast (end of month)
  └── Alerts

Row 2: Trend + Top Drivers
  ├── Daily Cost Trend (30 days) with 7-day MA
  └── Top 5 Cost Drivers list

Row 3: Distribution (3 breakdowns)
  ├── By Project (bar)
  ├── By Environment (donut)
  └── By Region (bar)

Row 4: Monthly by Category
  └── Stacked area chart (6 months)
```

### Chart Type Guide
- **KPI Card**: single number, current state
- **Line**: daily trends (30-90 days)
- **Stacked area**: monthly composition
- **Horizontal bar (sorted)**: top N comparisons
- **Donut/Pie**: 3-5 category composition only
- **Heatmap**: day × hour patterns

---

## 9. Multi-Tenant Access Options

### 3 Databricks Sharing Features
1. **Delta Sharing** — cross-org/cross-cloud open protocol
2. **Unity Catalog cross-workspace** — within Databricks account
3. **AI/BI Dashboard sharing** — dashboard-level share (formerly Lakeview)

### Compute Chargeback Models

#### Model 1: Unity Catalog Cross-Workspace (BigQuery-like) ⭐
```
Client workspace queries Sin's table:
  Client cluster runs query
    → Reads data from ADLS (Sin's storage)
  Compute → billed to Client's workspace ✓
  Storage → billed to Sin's workspace
```

#### Model 2: Delta Sharing
```
Cross-platform:
  Client compute (any tool)
    → Delta Sharing protocol
  Compute → billed to Client's platform
  Storage → billed to Sin's ADLS
  Egress may apply
```

#### Model 3: AI/BI Dashboard Sharing
```
Client browser → opens dashboard link
  Queries run on OWNER's SQL Warehouse
  Compute → billed to Sin's workspace ⚠️
  Client just consumes
```

### Row-Level Security (Unity Catalog)
```sql
-- Create row filter function
CREATE FUNCTION project_row_filter(project STRING)
RETURNS BOOLEAN
RETURN 
    is_account_group_member('de-team') OR
    (is_account_group_member('client-a') AND project LIKE 'proj-a-%');

-- Apply to table
ALTER TABLE cost_platform.gold.cost_with_tags
SET ROW FILTER project_row_filter ON (project);

-- Grant access
GRANT USE CATALOG ON CATALOG cost_platform TO `client-a`;
GRANT SELECT ON TABLE cost_platform.gold.cost_with_tags TO `client-a`;
```

### Solution Matching to พี่ Sarunya's Info

Based on requirements:
- "User ไม่มีสิทธิ์เข้า IT workspace" ✅ ต้อง external delivery
- "แจ้ง user ทุกเดือน" ✅ monthly cadence
- "เก็บเงินตามทีม" ✅ chargeback formal
- AIA traditional culture ✅ simple preferred

**Match Score:**
- **Option C (Monthly Report)**: 95% match ⭐
- **Option A (Live Dashboard Share)**: 40% match
- **Option B (Client Workspace)**: 15% match

**Uncertainty:** "dashboard" คำเดียวยัง ambiguous — Sin ต้อง verify

### Power BI Ruled Out
- Sin decided no Power BI (over-engineered + license cost)
- Focus on Databricks-native solutions

---

## 10. Dashboard Deployment

### 3 Dashboard Products in Databricks
1. **Databricks SQL Dashboard** (Legacy, being phased out)
2. **AI/BI Dashboard** (formerly Lakeview) ⭐ Recommended
3. **Notebook-based Dashboard**

### 5 Deployment Approaches

#### A. Manual (UI click-through)
- Best for: Quick PoC
- Cons: No version control, no CI/CD

#### B. CLI + JSON Export/Import
```bash
databricks lakeview dashboards get \
    --dashboard-id abc123 > dashboard.json

databricks lakeview dashboards create \
    --input-file dashboard.json \
    --parent-path "/Workspace/Prod/Dashboards"
```

#### C. Databricks Asset Bundles (DAB) ⭐
```yaml
# databricks.yml
bundle:
  name: cost-monitoring

targets:
  dev:
    workspace:
      host: https://adb-xxx.azuredatabricks.net
  prod:
    workspace:
      host: https://adb-yyy.azuredatabricks.net

resources:
  dashboards:
    cost_overview:
      display_name: "Cost Overview"
      file_path: ./dashboards/cost_overview.lvdash.json
      warehouse_id: ${var.warehouse_id}
```

Deploy:
```bash
databricks bundle deploy --target dev
databricks bundle deploy --target prod
```

#### D. Terraform (Enterprise IaC)
```hcl
resource "databricks_dashboard" "cost_overview" {
  display_name = "Cost Overview"
  warehouse_id = databricks_sql_endpoint.warehouse.id
  serialized_dashboard = file("dashboards/cost_overview.json")
}
```

#### E. DAB + CI/CD (Jenkins) ⭐⭐ Best for AIA
Matches AIA's Bitbucket + Jenkins pattern (like Kafka platform):

```groovy
// Jenkinsfile
pipeline {
    stages {
        stage('Validate') {
            steps { sh 'databricks bundle validate' }
        }
        stage('Deploy UAT') {
            when { branch 'develop' }
            steps { sh 'databricks bundle deploy --target uat' }
        }
        stage('Deploy Prod') {
            when { branch 'main' }
            input { message "Deploy to Production?" }
            steps { sh 'databricks bundle deploy --target prod' }
        }
    }
}
```

### Comparison
| Approach | Complexity | Version Ctrl | CI/CD | Multi-env |
|---|---|---|---|---|
| A: Manual | Low | ❌ | ❌ | ⚠️ |
| B: CLI + JSON | Med | ✅ | ⚠️ | ⚠️ |
| C: DAB ⭐ | Med | ✅ | ✅ | ✅ |
| D: Terraform | High | ✅ | ✅ | ✅ |
| E: DAB + CI/CD ⭐⭐ | High | ✅ | ✅ Full | ✅ |

### Recommendation for AIA
- **PoC**: Manual (Approach A)
- **Team dev**: DAB (Approach C)
- **Production**: DAB + Jenkins (Approach E)
- Reason: Matches AIA existing Bitbucket + Jenkins + Kafka platform patterns

### Gotchas
1. Warehouse ID differs per env → use variable substitution
2. Dashboard references catalog/schema → parameterize
3. Permissions may need separate handling
4. Dashboard filter state not persisted
5. Databricks CLI must be v0.205+

---

## 11. Automation Strategy

### Both Options Support Automation

#### Option C: Monthly Report Automation
```
Databricks Job (monthly, 1st of month)
├── Task 1: Ingest cost data
├── Task 2: Generate reports per team
│   ├── Query gold_cost_wide
│   ├── Filter by team tag
│   └── Export PDF/Excel per team
├── Task 3: Deliver
│   ├── Upload SharePoint per team folder
│   ├── Email attachment to team leads
│   └── Post to Teams channel
└── Task 4: Notification + audit log
```

#### Option A: Live Dashboard Automation
```
Daily Databricks Job
├── Task 1: Incremental ingest
├── Task 2: Refresh dashboard data
├── Task 3: Verify data quality
└── (Live dashboard stays current)

Optional: Monthly notification email
```

### Hybrid (Best Coverage)
```
Daily Job:
  └── Refresh dashboard data (live view)

Monthly Job (1st of month):
  ├── Generate PDF/Excel per team
  ├── Auto-deliver via email + SharePoint
  └── Include link to live dashboard
```

### Automation Stack Options
1. **Databricks Job only** (simplest)
2. **Databricks Job + ADF orchestration**
3. **Databricks Asset Bundles + Jenkins CI/CD** ⭐

### Recommendation
For AIA: **Level 3 (DAB + Jenkins)** matches Kafka platform pattern

### Automation Components Needed

For Option C:
- Python libs: openpyxl, reportlab, plotly, smtplib
- Delivery: SharePoint API, SMTP, Teams webhook, ADLS
- Metadata: team → email, team → SharePoint path mapping

For Option A:
- SQL Warehouse (compute)
- AI/BI Dashboard
- Row-level security config
- Share link + notification email

---

## 12. Team Structure & Communication

### Team Structure
```
├── หัวหน้าจริง (not directly mentioned yet)
├── พี่ Sarunya (Senior DE, solution-level guidance, คล้าย SA)
├── Sin (สิน) — new team member
└── บูม (น้อง, existing dashboard owner, มาก่อน Sin)
```

### Assignment
- หัวหน้าจริง assign Sin → help บูม on dashboard
- พี่ Sarunya provides context + requirements
- Existing cost pipeline maintained by บูม (or other team member)

### Sarunya's Info (from Teams message)
```
Facts:
1. AIA policy: no data cross env (except Portal cost)
2. Cost data from Portal → covers all env
3. Dashboard shows all cost (even pipeline in DEV)
4. Dashboard tags per team → chargeback
5. Dashboard on "IT workspace"
6. User (client teams) ไม่มีสิทธิ์เข้า IT workspace
7. ต้อง "หาวิธีการแชร์"
8. แจ้ง user ทุกเดือน
```

### Sin's Questions to Sarunya (In Progress)

**Q1: Dashboard แยกทุก env หรือ prod อย่างเดียว?**
- Sin's guess: prod only
- Reason: dashboard = report, not pipeline data
- Cost data cross-env exception ok

**Q2: IT workspace อยู่ไหน + user เข้าไม่ได้ + deploy?**
- IT workspace = Sin's team workspace (verify identity)
- User access options: link share, client workspace, static report
- Deploy via DAB + Jenkins recommended

**Q3: [pending]** — Sin will decide what to ask

### Existing Pipeline (Colleague's)
- Config-driven ingest (similar to SCB pattern)
- Layers: ingest → persist → prepare → summary
- **Removes tags** — Sin will retain
- Raw layer unclear (needs investigation)
- Located in team's workspace

### Decision Point (Pending)
- Enhance existing pipeline (add tag columns) — if consumers manageable
- Or new parallel pipeline — safer PoC
- Recent update: พี่ (colleague, not Sarunya) offered to add tags
- Still need to clarify solution before commit

---

## 13. Open Questions & Next Actions

### Questions Pending พี่ Sarunya's Answer
1. Dashboard: all env vs prod only?
2. IT workspace identity + user access model?
3. Delivery model:
   - Interactive dashboard (share link)
   - Client's own workspace + table share
   - Monthly static report
   - Hybrid
4. "Dashboard" meaning:
   - Live interactive UI, or
   - Report visualization
5. Chargeback flow:
   - Sin generates report → hand to Finance
   - User teams self-service
   - Both

### Questions for บูม (colleague)
1. Existing pipeline architecture details
2. Config style (table vs YAML)
3. Raw layer existence
4. Consumers of persist table
5. Tag handling logic

### Technical Verifications Needed
1. AIA Databricks account structure (single account across workspaces?)
2. Unity Catalog enabled? (both workspaces?)
3. Client workspaces exist? (assumption)
4. Sin's permissions on existing tables
5. ADLS path structure for cost exports

### Decisions Deferred
- Solution option (A/C/Hybrid) — awaiting Sarunya
- Enhance vs new pipeline — awaiting colleague sync
- Tag naming convention — waiting design phase
- Automation cadence — depends on solution choice

### Immediate Sin's Actions
1. Send 3 questions to Sarunya
2. Sync with บูม on existing pipeline details
3. Investigate IT workspace details
4. Prepare 3 solution proposals for Sarunya to choose
5. Wait for requirements before code implementation

### Sin's Preparation Strategy
Prepare parallel proposals:
- Proposal 1: Monthly Report (Option C) ⭐ likely fit
- Proposal 2: Live Dashboard Share (Option A)
- Proposal 3: Hybrid (both A + C)

Present to Sarunya → let her choose → implement chosen path

---

## Appendix A: Public Client IDs Reference

| App | Client ID |
|---|---|
| Azure CLI | `04b07795-8ddb-461a-bbee-02f9e1bf7b46` |
| Azure PowerShell | `1950a258-227b-4e31-a9cf-717495945fc2` |
| Visual Studio | `872cd9fa-d31f-45e0-9eab-6e460a02d1f1` |
| VS Code | `aebc6443-996d-45c2-90f0-388ff96faa56` |
| MS Graph Explorer | `de8bc8b5-d9f9-48b1-a8ad-b748da725064` |

**Note:** Public clients bypass admin registration needs, but AIA CA policy still blocks device code flow (530033).

---

## Appendix B: RBAC Roles Needed

| Role | Purpose | Option A (Query API) | Option B (Exports) | Option C (Manual) |
|---|---|---|---|---|
| Reader | List resources | ✅ | ✅ | ✅ (implicit) |
| Cost Management Reader | Query cost data | ✅ | ✅ | ✅ (Sin's user has) |
| Cost Management Contributor | Create exports | ❌ | ✅ setup | ❌ |
| Storage Blob Data Reader | Read export files | ❌ | ✅ | ❌ |

---

## Appendix C: Cost Export Fields Reference (Full List)

Typical schema from 2023-05-01:

**Billing hierarchy:**
- BillingAccountId, BillingAccountName
- BillingProfileId, BillingProfileName
- InvoiceSectionId, InvoiceSectionName
- BillingPeriodStartDate, BillingPeriodEndDate

**Account & Subscription:**
- AccountName, AccountOwnerId
- SubscriptionId, SubscriptionName

**Resource identification:**
- ResourceGroup, ResourceGroupName
- ResourceId, ResourceLocation, ResourceType
- Location, Tags

**Service categorization:**
- ServiceFamily, ServiceName
- ProductName, PartNumber
- PublisherType, PublisherName

**Meter details:**
- MeterCategory, MeterSubCategory
- MeterId, MeterName, MeterRegion
- UnitOfMeasure

**Usage & pricing:**
- Date, Quantity
- UnitPrice, EffectivePrice
- CostInBillingCurrency, CostInPricingCurrency
- BillingCurrency, PricingCurrency
- ChargeType

**Reservation/Savings Plan:**
- ReservationId, ReservationName
- BenefitId, BenefitName
- Term

**Other:**
- Frequency, AdditionalInfo
- ServiceInfo1, ServiceInfo2
- CostCenter, PayGPrice, PricingModel

---

## Appendix D: Related Anthropic/Azure Concepts

### AIA Cost Concerns Related
- SQL MI cost concern: verified as NOT Databricks-related
- SQL MI ≠ Databricks SQL Warehouse (different products)
- Cost dashboard should split by resource type owner

### Databricks Products Referenced
- Unity Catalog (metastore)
- AI/BI Dashboard (Lakeview replacement)
- Databricks Asset Bundles (IaC)
- Delta Sharing (cross-org protocol)
- SQL Warehouse (Photon compute)
- Access Connector for ADB (MI mechanism)

### AIA Stack Referenced
- Azure Databricks + AKS + ADF + ADLS + Synapse + ACR
- Jenkins + Bitbucket
- Traditional insurance (PDPA, OIC compliance)
- Air-gapped office machines
- Screenshots only policy

---

## Session Meta

**Key Learnings from This Session:**
1. Enterprise auth = SPN/MI mandatory (device code doesn't work)
2. Cost Export = elegant solution (no auth complexity)
3. Tags stored as MAP, expanded to columns for dashboards
4. Multi-tenant sharing = 3 distinct patterns (UC, Delta Sharing, Dashboard)
5. Requirements come from senior (Sarunya) — Sin should propose, not decide
6. Automation applies to all delivery options

**Communication Patterns:**
- Sin's name: วศิน / สิน / ศิน / sin (no 's)
- Response style: bilingual technical, mobile-friendly
- Pushback on inaccuracy welcomed
- Air-gapped context: screenshots only, no code paste from AIA
- Discipline: separate confirmed AIA reality from generic possibilities

**Files/Artifacts Referenced:**
- Portal Teams screenshot from Sarunya (IMG_0112.jpeg)
- Colleague's existing cost pipeline (patterns discussed)
- AIA new job memory file (previous session)

---

*End of Export — Ready for VS Code continuation*
