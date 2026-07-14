---
title: Feature Deep-Dive — AI/BI Dashboard vs Databricks Apps
subtitle: Sharing Solution Analysis for AIA Cost Monitoring PoC
date: 2026-07-13
author: Session notes for สิน (วศิน)
context: Cost dashboard sharing with cross-env constraint (DEV table → PROD/no-WS-access users)
---

# AI/BI Dashboard vs Databricks Apps — Deep Comparison

## Table of Contents

1. [Context & Problem Statement](#context--problem-statement)
2. [Feature 3: AI/BI Dashboard (Deep Dive)](#feature-3-aibi-dashboard-deep-dive)
3. [Feature 4: Databricks Apps (Deep Dive)](#feature-4-databricks-apps-deep-dive)
4. [Requirements Verification Matrix](#requirements-verification-matrix)
5. [Security Model Comparison](#security-model-comparison)
6. [Pricing Comparison](#pricing-comparison)
7. [Preparation Checklists](#preparation-checklists)
8. [Implementation How-To](#implementation-how-to)
9. [Watch-outs & Risks](#watch-outs--risks)
10. [Decision Framework](#decision-framework)

---

## Context & Problem Statement

### Sin's Requirements (from พี่ Sarunya)

```
R1: Cost table stays in DEV environment (AIA policy)
R2: Dashboard co-located with table (DEV IT workspace)
R3: Client users access via PROD workspaces (but doesn't need to actually)
R4: NO IT workspace access for clients (STRICT)
R5: Same Databricks metastore across workspaces (verified ✓)
R6: Chargeback tag-based (RLS by team)
R7: Monthly notification to users
R8: Multiple client teams (not just one)
```

### Sin's Blocker with Original Solution

```
Original approach: UC RLS + AI/BI Dashboard Publish + Share to workspace
Problem: SQL Warehouse compute affinity requires workspace membership
Conflict: Contradicts R4 (no IT workspace access)
```

### Sin's Additional Constraints

```
1. No permission to create dashboards in departmental workspaces (rules out Option 1)
2. Cross-env is required (not optional exception)
3. Feature 3 perceived as "not secure" per AIA policy
4. Focus on Feature 4 (Databricks Apps) preferred
```

---

## Feature 3: AI/BI Dashboard (Deep Dive)

### Naming History

```
2023: Lakeview (preview)
2024: Lakeview (GA) → renamed to AI/BI Dashboard
2025-2026: AI/BI Dashboard (current)

CLI/API endpoint still uses "lakeview":
  databricks lakeview dashboards create ...
  
UI shows: "Dashboard" or "AI/BI Dashboard"
```

### Core Capability

From official Databricks documentation:

> "If a dashboard is published with shared data permissions and shared with a specific user, group, or all users in the account, those users can access it regardless of whether they have access to the originating workspace."

**Key insight:** Account-level sharing bypasses workspace membership requirement

### 3-Tier User Model

```
Tier 1: Workspace Users
├── Members of a specific workspace
├── Have Databricks SQL / Consumer entitlement
├── Can create + edit dashboards
└── NOT what Sin needs

Tier 2: Consumer Access Users
├── Workspace member with view-only role
└── Still workspace member — NOT Sin's target

Tier 3: Account Users ⭐ Sin's Target
├── Registered in Databricks Account only
├── NOT workspace member
├── View published dashboards only
├── No workspace navigation UI
└── Perfect fit for R4
```

### 2 Publishing Modes

#### Mode A: Shared Data Permissions

```
Behavior:
├── Viewers use PUBLISHER's credentials
├── Sin's identity runs queries
├── All viewers see same data
├── ⚠️ RLS uses Sin's identity (may bypass row filter)
└── Compute paid by Sin's warehouse

Use case:
├── All viewers should see same public data
├── No per-user data restrictions needed
└── ⚠️ Not ideal for chargeback (R6)
```

#### Mode B: Individual Data Permissions ⭐

```
Behavior:
├── Viewers use OWN credentials
├── RLS applies per viewer
├── Each user sees own filtered data
├── ⭐ Chargeback works (R6)
└── Compute paid by Sin's warehouse (access via warehouse)

Requirements:
├── Client user must have SELECT grant on table
├── Row filter function defined
├── Client account groups exist
└── Column mask (optional)

Use case:
├── Multi-tenant dashboards (Sin's case)
├── Team-specific views
└── Compliance requirements
```

### Critical Gotcha: Workspace-Bound Catalogs

From documentation:

> "Account users can view dashboards published with shared or individual data permissions. However, account users cannot access data from workspace-bound securables, such as workspace-bound catalogs. Dashboard widgets that query workspace-bound securables do not display data for account users."

**Implication:**
```
If cost_platform catalog is workspace-bound → account users see empty widgets
Solution: catalog must NOT be workspace-bound (default = accessible from any WS on metastore)
```

### IP Access Lists

> "If IP access lists are configured, dashboards are only accessible if users access them from within the approved IP range, such as when using a VPN."

**AIA implication:** Client users may need VPN access, or AIA must configure IP list

### Recent 2026 Updates

- **Mar 2026:** SDK/REST API for sharing with all account users (GA)
- **Apr 2026:** Embedding for External Users (Public Preview) — dashboards embeddable in external portals
- **Apr 2026:** Embedding with SSO (Private Preview) — corporate SSO flows through
- **Publish with service principal credentials** — new option beyond user credentials
- **Databricks One Mobile** — mobile app for viewing dashboards

### Compute Model

```
Dashboard runs queries on SQL Warehouse:
├── Serverless SQL Warehouse (recommended) → scales to zero
├── Or Classic/Pro SQL Warehouse
└── Warehouse lives in DEV IT workspace (Sin's)

Pricing:
├── Serverless SQL: ~$0.70/DBU (bundled infra)
├── Classic: ~$0.22/DBU + VM cost separately
└── Pro: ~$0.55/DBU + VM cost separately

Cost model:
├── Per-query billing
├── Idle = no cost (serverless)
└── Auto-scale to zero
```

---

## Feature 4: Databricks Apps (Deep Dive)

### Overview

Databricks Apps = containerized web applications on Databricks serverless platform.

Supported frameworks:
- Python: Streamlit, Dash, Gradio, Flask
- Node.js: React, Angular, Svelte, Express

### Sharing Model

From documentation:

> "After deployment, app developers can share an app with users or groups by granting the CAN_USE or CAN_MANAGE permission on the app instance. Users don't need to belong to the same workspace, but they must be part of the same Databricks account."

**Sin's requirement match:** ✅ Cross-workspace access via Account membership

### Critical Limitations

**Cannot be Public:**
> "You can't make Databricks apps public. Anonymous access and bypassing single sign-on (SSO) are not supported."

**External Users Need Federation:**
> "To give access to external collaborators, use identity federation with SCIM and JIT provisioning to onboard users through your identity provider without granting full workspace access."

### 2 Authorization Models

#### Model 1: App Authorization (Service Principal)

```
How it works:
├── App has dedicated SP identity
├── Developer sets SP permissions once
├── All users share same SP data access
└── SP acts on behalf of all users

Pros:
├── Simple setup
├── Consistent behavior
└── SP permissions controlled centrally

Cons:
├── ⚠️ No per-user data filtering
├── ⚠️ RLS doesn't apply naturally
└── Chargeback logic in app code
```

#### Model 2: User Authorization (Public Preview) ⭐

```
How it works:
├── App runs queries as USER's identity
├── UC RLS applies per user
├── Row filters + column masks work
└── Access via OAuth 2.0

Pros:
├── ⭐ UC RLS enforced automatically
├── ⭐ Consistent with workspace governance
├── ⭐ No hardcoded permission logic
└── User's UC permissions applied

Cons:
├── ⚠️ Public Preview status
├── Workspace admin must enable
└── Requires user consent

Requirement:
├── Users must be Databricks account members
├── OAuth scopes configured
└── User authorization enabled in workspace
```

### Compute Sizes (Azure)

Source: Microsoft Learn official docs (May 2026)

| Size | CPU | Memory | Cost per hour | When to use |
|---|---|---|---|---|
| Medium | Up to 2 vCPUs | 6 GB | 0.5 DBU | Standard apps, dashboards, forms (default) |
| Large | Up to 4 vCPUs | 12 GB | 1 DBU | Large datasets, high concurrency |

Default: Medium (if not specified)

### Pricing Reality — 24/7 Billing

**Critical:** Databricks Apps run 24/7 with no native scale-to-zero.

From Databricks community (June 2026):
> "Databricks Apps run 24/7 with no native scale-to-zero. ~$350/mo per app (720 hrs), but internal dashboards/admin tools only get used a few hours/day. You pay for 100%, use ~15%."

### Workaround: Manual Automation

Community pattern (76% cost reduction):

```python
# Databricks Job 1: Start app at 8 AM (weekdays)
# Cron: 0 8 * * 1-5
import requests

def start_app(app_name):
    response = requests.post(
        f"{WORKSPACE_URL}/api/2.0/apps/{app_name}/start",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    return response.json()

start_app("cost-dashboard-app")


# Databricks Job 2: Stop app at 7 PM (weekdays)
# Cron: 0 19 * * 1-5
def stop_app(app_name):
    response = requests.post(
        f"{WORKSPACE_URL}/api/2.0/apps/{app_name}/stop",
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    return response.json()

stop_app("cost-dashboard-app")
```

Trade-offs:
- ✅ ~76% cost reduction (50 hrs/week vs 168)
- ⚠️ Users outside hours see app down
- ⚠️ Need retry logic
- ⚠️ Manual override for special cases

### Horizontal Scaling (Beta)

```
For higher availability + concurrency:
├── Multiple instances of same app
├── Load balancing
└── Beta feature (2026)
```

---

## Requirements Verification Matrix

| Requirement | Feature 3 (AI/BI Dashboard) | Feature 4 (Databricks Apps) |
|---|---|---|
| **R1: Table in DEV** | ✅ Compatible | ✅ Compatible |
| **R2: Dashboard w/ table (DEV)** | ✅ Dashboard in IT WS | ✅ App in IT WS |
| **R3: Client via PROD WS** | ✅ Not needed! Account-level share | ✅ Not needed! Account-level share |
| **R4: No IT WS access** | ✅ Account users only | ✅ Account users only |
| **R5: Same metastore** | ✅ Required | ✅ Required |
| **R6: RLS chargeback** | ✅ Individual data mode | ✅ User authorization mode |
| **R7: Monthly notification** | ✅ Email subscription built-in | ⚠️ Custom code needed |
| **R8: Multiple client teams** | ✅ Share to multiple groups | ✅ Share to multiple groups |

**Both features match all requirements** if configured correctly.

---

## Security Model Comparison

### Common Security Foundation

Both features use:
- Databricks Account authentication (SSO/Entra ID)
- Unity Catalog authorization
- Row-Level Security (RLS)
- Column masks
- Audit logging

### Detailed Comparison

| Security Aspect | Feature 3 (Mode B) | Feature 4 (User Auth) |
|---|---|---|
| **Authentication** | SSO / Entra ID | SSO / Entra ID |
| **Authorization** | UC grants + row filter | UC grants + row filter |
| **Data access identity** | Viewer's | User's |
| **Session isolation** | Yes | Yes |
| **Audit trail** | Query logs | Query logs |
| **RLS enforcement** | Native UC | Native UC |
| **Row filter** | ✅ | ✅ |
| **Column mask** | ✅ | ✅ |
| **IP restrictions** | ✅ (IP access lists) | ✅ (IP access lists) |
| **Compliance profile** | ✅ | ✅ |
| **MFA** | Via IdP | Via IdP |

### Sin's "Feature 3 not secure" Concern

**Analysis:**

If Sin means:
- **Mode A (Shared Data Permissions):** Valid concern — publisher's credentials, no per-user RLS
- **Mode B (Individual Data Permissions):** Same security as Feature 4 with user auth

**Verify with Sarunya:**
- What specific security concern applies?
- Is it Mode A that's disallowed, or the entire feature?
- Is it an AIA-specific policy or a general perception?

### Public URL Concern (if that's the issue)

**Reality:** AI/BI Dashboard is NOT truly public
- Viewers must be Databricks account users
- SSO authentication required
- One-time passcode or SSO login
- No anonymous access allowed

**Similar to Databricks Apps in this respect:**
- Both require account membership
- Both require SSO
- Neither can be truly public

### Where Feature 4 Might Be More Secure

```
1. Custom logic:
   - App can implement additional checks
   - Custom rate limiting
   - Custom data masking

2. Managed dependencies:
   - App SP has explicit permissions
   - No shared credentials pattern

3. Isolation:
   - App runs in own container
   - Separate from workspace UI
```

### Where Feature 3 Is Equivalent

```
1. RLS enforcement:
   - Same UC row filter mechanism
   - Same account group check

2. Auth pipeline:
   - Same SSO
   - Same OAuth
   - Same MFA

3. Compliance:
   - Both work with compliance security profile
   - Both audit-logged
```

---

## Pricing Comparison

### Cost Formula

```
Feature 3 (AI/BI Dashboard):
Total = Serverless SQL Warehouse cost (per-query)
     = DBUs × warehouse_size × active_query_time

Feature 4 (Databricks Apps):
Total = App instance cost (per-hour) + Warehouse cost
     = (DBU/hr × hours_running × DBU_rate) + query cost
```

### Realistic Cost Estimate (Sin's Use Case)

**Assumptions:**
- 5 client teams × 10-20 users each
- Access frequency: 2-3x/week per user
- Session length: 5-10 minutes
- Peak: 1st week of month
- Total actual usage: ~100-200 hours/month
- Azure Premium tier

**Feature 3 (AI/BI Dashboard):**

```
Serverless SQL Warehouse queries:
├── Small warehouse: 6 DBU/hour when active
├── Active time: ~50 hours/month (spread across all queries)
├── 6 × 50 × $0.70 = ~$210/month
└── Actually often less due to autoscaling

Storage: negligible (Delta on ADLS)
Dashboard hosting: free (built into workspace)

Estimated total: $35-70/month ⭐
```

**Feature 4 (Databricks Apps 24/7):**

```
Medium app running 24/7:
├── 0.5 DBU/hour × 720 hours × $0.55 = $198/month
├── + SQL Warehouse for queries: ~$35/month
└── Total: ~$233/month

Large app running 24/7:
├── 1 DBU/hour × 720 hours × $0.55 = $396/month
├── + SQL Warehouse: ~$35/month
└── Total: ~$431/month
```

**Feature 4 with Business Hours Automation:**

```
Medium app 9 AM - 6 PM weekdays:
├── 9 hours × 5 days × 4 weeks = 180 hours
├── 0.5 × 180 × $0.55 = $50/month
├── + SQL Warehouse: ~$35/month
└── Total: ~$85/month

Medium app 24/7 weekdays only:
├── 24 × 5 × 4 = 480 hours
├── 0.5 × 480 × $0.55 = $132/month
├── + SQL Warehouse: ~$35/month
└── Total: ~$167/month
```

### Cost Summary Table

| Configuration | Monthly Cost | Notes |
|---|---|---|
| **Feature 3 (AI/BI Dashboard)** | $35-70 | Serverless, scale-to-zero |
| **Feature 4 + Business Hours** | $85 | Weekday 9-6, ~76% saving |
| **Feature 4 + Weekdays 24/7** | $167 | 5 days/week |
| **Feature 4 (24/7 Medium)** | $233 | Always available |
| **Feature 4 (24/7 Large)** | $431 | Always available, high capacity |

### Multi-App Scenario

If Sin needs multiple apps (e.g., separate app per client team):

```
5 client teams = 5 apps needed?
Feature 4: 5 × $233 = $1,165/month (24/7)
Feature 4 automated: 5 × $85 = $425/month

= expensive for cost dashboard use case
```

**Feature 3 scales better:** 1 dashboard, RLS per team = single instance

---

## Preparation Checklists

### Feature 3 (AI/BI Dashboard) Preparation

```
□ 1. Databricks Account Admin cooperation:
   □ Register client users as Account Users
   □ Or enable Automatic Identity Management (Entra ID sync)
   □ Create account-level groups (e.g., client-underwriting)

□ 2. SSO / Authentication:
   □ Unified SSO enabled?
   □ JIT provisioning configured?
   □ Or one-time passcode acceptable?

□ 3. Same metastore verified:
   □ DEV WS metastore = confirmed
   □ Account users can access

□ 4. Cost catalog NOT workspace-bound:
   □ Check via: databricks workspace-bindings list
   □ If bound: unbind or use different approach

□ 5. IP Access List check:
   □ Configured?
   □ Client IPs allowed?
   □ Or clients need VPN?

□ 6. RLS setup on gold table:
   □ team_row_filter function created
   □ ALTER TABLE SET ROW FILTER applied
   □ Grant SELECT to client groups
   □ Grant EXECUTE on filter function

□ 7. SQL Warehouse:
   □ Serverless warehouse in DEV WS
   □ Sizing (Small usually sufficient)
   □ Auto-stop configured
```

### Feature 4 (Databricks Apps) Preparation

```
□ 1. Databricks Runtime & Environment:
   □ Apps feature enabled in workspace
   □ Premium tier (default for AIA)
   □ Compliance security profile compatible
   □ Workspace admin enabled Apps in Previews page

□ 2. Development skills:
   □ Python framework (Streamlit / Dash / Gradio)
   □ SQL for data queries
   □ HTML/CSS basics (optional)
   □ Git integration

□ 3. Authentication setup:
   □ OAuth 2.0 configured
   □ User authorization scopes (Public Preview) enabled
   □ Service principal created
   □ SSO working

□ 4. UC + RLS (same as Feature 3):
   □ cost_platform.gold.cost_wide with row filter
   □ Client account groups exist
   □ GRANT SELECT to client groups
   □ EXECUTE permission on filter function

□ 5. Cost planning:
   □ Sizing decision (Medium vs Large)
   □ Business hours schedule (automation)
   □ Budget approval (~$85-400/month)
   □ Monitoring alerts

□ 6. Compliance security profile:
   □ AIA compliance profile status
   □ Apps feature enabled by workspace admin
   □ Reference: docs "Manage workspace-level previews"

□ 7. Deployment infrastructure:
   □ Git repository setup
   □ CI/CD via GitHub Actions or DAB
   □ App configuration files
```

---

## Implementation How-To

### Feature 3 (AI/BI Dashboard) — Full Flow

#### Phase 1: Setup UC Foundation

```sql
-- Create catalog + schema (metastore admin)
CREATE CATALOG IF NOT EXISTS cost_platform;
CREATE SCHEMA IF NOT EXISTS cost_platform.gold;

-- Create table
CREATE TABLE cost_platform.gold.cost_wide (
    usage_date DATE,
    subscription_id STRING,
    resource_group STRING,
    resource_id STRING,
    service_name STRING,
    tag_team STRING,        -- Used for RLS
    tag_environment STRING,
    tag_cost_center STRING,
    amortized_cost DECIMAL(18,4)
) USING DELTA
PARTITIONED BY (usage_date);

-- Row filter function
CREATE OR REPLACE FUNCTION cost_platform.gold.team_row_filter(team STRING)
RETURN
    is_account_group_member('de-team')
    OR is_account_group_member(concat('client-', lower(team)));

-- Apply filter
ALTER TABLE cost_platform.gold.cost_wide
    SET ROW FILTER cost_platform.gold.team_row_filter ON (tag_team);

-- Grant to client groups
GRANT USE CATALOG ON CATALOG cost_platform TO `client-underwriting`;
GRANT USE SCHEMA ON SCHEMA cost_platform.gold TO `client-underwriting`;
GRANT SELECT ON TABLE cost_platform.gold.cost_wide TO `client-underwriting`;
GRANT EXECUTE ON FUNCTION cost_platform.gold.team_row_filter
    TO `client-underwriting`;
```

#### Phase 2: Build Dashboard

```
UI Steps:
1. Sidebar → + New → Dashboard
2. Data tab → Add dataset
   - Query: SELECT * FROM cost_platform.gold.cost_wide
   - Attach SQL Warehouse
3. Canvas tab → Design pages
   - KPI cards
   - Time-series charts
   - Breakdown by team/service
4. Save as draft
5. Test filters + interactivity
```

#### Phase 3: Publish

```
UI Steps:
1. Click "Publish" (top right)
2. Choose credential mode:
   → Individual Data Permissions ⭐ (for RLS)
3. Confirm publish
```

#### Phase 4: Share

```
UI Steps:
1. Click "Share" (top right)
2. Add client account groups:
   - client-underwriting
   - client-claims
   - etc.
3. Permission: CAN VIEW
4. ☑ Notify via email
5. Save
```

#### Phase 5: Monthly Schedule

```
UI Steps:
1. Dashboard → Schedule
2. Frequency: Monthly (1st of month)
3. Time: 08:00
4. Recipients: client group emails
5. Format: PDF + link
6. Save
```

### Feature 4 (Databricks Apps) — Full Flow

#### Phase 1: Setup UC Foundation (same as Feature 3)

Reuse SQL from Feature 3 Phase 1.

#### Phase 2: Build Streamlit App

```python
# app.py
import streamlit as st
import pandas as pd
from databricks import sql
from databricks.sdk.core import Config
import os

st.set_page_config(page_title="Cost Dashboard", layout="wide")

# Get user identity from Databricks Apps headers
user_email = st.context.headers.get("X-Forwarded-Email")
user_token = st.context.headers.get("X-Forwarded-Access-Token")

# Configure connection with user's token (for RLS)
cfg = Config(token=user_token)

def get_cost_data():
    with sql.connect(
        server_hostname=os.getenv("DATABRICKS_HOST"),
        http_path=os.getenv("SQL_WAREHOUSE_HTTP_PATH"),
        credentials_provider=lambda: cfg.authenticate
    ) as conn:
        return pd.read_sql("""
            SELECT 
                usage_date,
                service_name,
                tag_team,
                SUM(amortized_cost) AS cost
            FROM cost_platform.gold.cost_wide
            WHERE usage_date >= current_date() - 30
            GROUP BY usage_date, service_name, tag_team
        """, conn)

# UI
st.title("Azure Cost Dashboard")
st.write(f"Welcome, {user_email}")

df = get_cost_data()

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Cost (30d)", f"${df['cost'].sum():,.0f}")
col2.metric("Services", df['service_name'].nunique())
col3.metric("Teams", df['tag_team'].nunique())

# Charts
st.subheader("Cost by Service")
st.bar_chart(df.groupby('service_name')['cost'].sum())

# Details
st.subheader("Details")
st.dataframe(df)
```

#### Phase 3: Configuration & Deploy

```yaml
# app.yaml
command: ["streamlit", "run", "app.py"]

env:
  - name: SQL_WAREHOUSE_HTTP_PATH
    value: "/sql/1.0/warehouses/abc123"

scopes:
  - "sql"
  - "dashboards.execute"
```

```bash
# Deploy via CLI
databricks apps create cost-dashboard-app
databricks apps deploy cost-dashboard-app \
    --source-code-path ./app \
    --command "streamlit run app.py"
```

#### Phase 4: Grant Access

```
UI Steps:
1. Databricks Apps → cost-dashboard-app
2. Share button
3. Add: client-underwriting (Account Group)
4. Permission: CAN USE
5. Save

Repeat per client group.
```

#### Phase 5: Setup Auto Start/Stop

```python
# Databricks Job 1: Start weekday 8 AM
# Schedule: 0 8 * * 1-5
import requests
import os

def start_app(app_name):
    workspace_url = os.getenv("DATABRICKS_HOST")
    token = os.getenv("DATABRICKS_TOKEN")
    
    response = requests.post(
        f"{workspace_url}/api/2.0/apps/{app_name}/start",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(response.json())

start_app("cost-dashboard-app")


# Databricks Job 2: Stop weekday 7 PM
# Schedule: 0 19 * * 1-5
def stop_app(app_name):
    workspace_url = os.getenv("DATABRICKS_HOST")
    token = os.getenv("DATABRICKS_TOKEN")
    
    response = requests.post(
        f"{workspace_url}/api/2.0/apps/{app_name}/stop",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(response.json())

stop_app("cost-dashboard-app")
```

#### Phase 6: Client Access

```
Client flow:
1. Receive URL from Sin
2. Open in browser
3. SSO login (Entra ID)
4. Authenticate as Databricks Account User
5. See Streamlit app UI
6. RLS filters data automatically
7. Interactive dashboard experience
```

---

## Watch-outs & Risks

### Common Risks (Both Features)

**Risk 1: Workspace-Bound Catalog**

```
If cost_platform catalog is workspace-bound to DEV:
→ Account users cannot access data
→ Dashboard/app shows empty

Mitigation:
├── Verify: databricks workspace-bindings list
├── Ensure catalog is NOT bound
└── Or ask admin to unbind
```

**Risk 2: IP Access Lists**

```
If AIA enforces IP access lists:
→ Client users outside approved IPs = access denied

Mitigation:
├── Check AIA IP policy
├── If enforced → clients need VPN
└── Or admin adjusts IP list
```

**Risk 3: External User Registration**

```
Automatic identity management (recent 2026 feature):
> "Users, service principals, and members of groups are 
   automatically added to the Databricks account upon login"

Verification needed:
├── Is auto identity management enabled?
├── Or manual account user registration required?
└── Ask Databricks account admin
```

**Risk 4: Compliance Security Profile**

```
If AIA has compliance profile enabled:
├── Some features may be restricted
├── Apps requires admin enable in Previews
└── Feature availability may differ
```

### Feature 3 Specific Risks

**Risk 5: Mode A Data Leak**

```
Shared Data Permissions mode:
→ All viewers see same data
→ No per-user filtering

Mitigation:
└── Always use Mode B (Individual Data Permissions)
```

**Risk 6: Compute Cost Concentration**

```
All viewer queries run on Sin's SQL Warehouse:
→ Cost concentrated in DEV workspace
→ Not chargeback-friendly per user

Mitigation:
├── Use serverless warehouse (per-query billing)
├── Tag warehouse for cost tracking
└── Accept centralized model
```

### Feature 4 Specific Risks

**Risk 7: 24/7 Cost Surprise**

```
Databricks Apps run 24/7 by default:
→ Pay even when no one uses
→ ~$200-400/month per app

Mitigation:
├── Implement start/stop automation
├── Monitor via system.billing.usage
└── Budget alerts
```

**Risk 8: User Authorization Preview Status**

```
User authorization is Public Preview:
→ May change before GA
→ Behavior may evolve
→ Not recommended for critical production

Mitigation:
├── Test thoroughly
├── Monitor Databricks release notes
└── Have fallback to app authorization if needed
```

**Risk 9: Development Complexity**

```
Requires Python + web framework knowledge:
→ More effort than dashboard
→ Ongoing maintenance
→ Custom bugs possible

Mitigation:
├── Assess team capacity
├── Simple Streamlit for start
└── Iterate incrementally
```

**Risk 10: Compute Hidden in App**

```
App runs as containerized service:
→ Not obvious what's running
→ Idle apps forgotten (69-day story from community)
→ Cost accumulates silently

Mitigation:
├── Cost monitoring alerts
├── Regular audits
├── Auto-stop policies
└── Ownership tags
```

---

## Decision Framework

### When to Choose Feature 3 (AI/BI Dashboard)

**Choose if:**
```
✓ Simple dashboard use case (KPIs, charts, tables)
✓ Cost-conscious ($35-70/month vs $85-400)
✓ No custom UI needed
✓ No Python dev capacity
✓ Native RLS chargeback is enough
✓ Monthly email notification suffices
✓ Multiple client teams share single dashboard
```

**Do NOT choose if:**
```
✗ Custom interactive workflows needed
✗ Multi-step forms required
✗ Complex user actions beyond viewing
✗ Non-tabular UI (rich visualizations)
✗ Real-time data (>1 min refresh)
```

### When to Choose Feature 4 (Databricks Apps)

**Choose if:**
```
✓ Custom interactive UI required
✓ Complex user workflows
✓ Multi-step forms / user input
✓ Non-standard visualizations
✓ Integration with external services
✓ Willing to accept 24/7 cost
✓ Have Python/Streamlit dev capacity
✓ Willing to build monthly notification code
```

**Do NOT choose if:**
```
✗ Simple dashboard suffices
✗ Cost is major concern
✗ No dev capacity
✗ Need free monthly email
```

### Sin's Specific Scenario Analysis

```
Sin's Use Case:
├── Cost monitoring dashboard
├── Multiple teams view own cost
├── Chargeback tag-based
├── Monthly notification required
├── AIA policy considerations

Feature 3 fit: 95% match
├── ✅ Purpose-built for dashboards
├── ✅ Native RLS
├── ✅ Cheaper (5x)
├── ✅ Native email schedule
└── ? Only concern = "not secure" perception

Feature 4 fit: 80% match  
├── ✅ Cross-workspace share
├── ✅ RLS (user auth mode - Preview)
├── ⚠️ 24/7 cost (need automation)
├── ⚠️ Custom code for notification
└── ⚠️ Dev complexity

Recommendation:
1. Clarify "Feature 3 not secure" reason with Sarunya
2. If misconception → use Feature 3 Mode B
3. If real AIA policy → use Feature 4
4. Otherwise: PoC both, let Sarunya decide with real data
```

### Hybrid Approach (Best of Both)

```
Consider running both:
├── Feature 3: Primary dashboard for most users
├── Feature 4: Advanced app for power users
└── Same underlying UC table

Benefits:
├── Cost-effective for majority
├── Advanced features for those who need
└── Same governance model
```

---

## Sin's Decision Points

### Questions to Clarify with Sarunya/พี่

```
1. "ทำไม Feature 3 (AI/BI Dashboard Mode B) ถือว่า not secure?
   - เป็น AIA specific policy?
   - เป็น concern จาก concept?
   - Mode B ใช้ UC RLS เหมือน Feature 4"

2. "Budget สำหรับ dashboard นี้ ~เท่าไหร่/month?"

3. "Team มี capacity ทำ Streamlit/Python app มั้ย?"

4. "Feature ที่พี่หมายถึง = Feature 3 หรือ Feature 4?"

5. "Cost catalog สามารถไม่ workspace-bound มั้ย?
   หรือ AIA policy กำหนดให้ bound?"
```

### Verification Tasks

```
□ Test with 1 test user (POC):
  □ Add test client as account user
  □ Publish test dashboard
  □ Share with test user
  □ Verify: sees dashboard, RLS works, no WS access
  □ Verify: monthly email schedule works

□ Cost calibration:
  □ Estimate query volume for realistic month
  □ Set up cost monitoring alerts
  □ Compare actuals vs estimates

□ Security review:
  □ Confirm with security team what's allowed
  □ Document approved configuration
  □ Get formal sign-off
```

---

## Appendix: Reference Sources

### Official Documentation

- Databricks Dashboards: https://docs.databricks.com/aws/en/dashboards/
- AI/BI Administration: https://docs.databricks.com/aws/en/ai-bi/admin
- Databricks Apps: https://docs.databricks.com/aws/en/dev-tools/databricks-apps/
- Compute Sizes (Azure): https://learn.microsoft.com/en-us/azure/databricks/dev-tools/databricks-apps/compute-size
- Workspace-Catalog Binding: https://docs.databricks.com/aws/en/data-governance/unity-catalog/access-control/workspace-catalog-binding

### Blog Posts & Community

- Sharing AI/BI Dashboards: https://www.databricks.com/blog/sharing-aibi-dashboards
- Embedding for External Users: https://www.databricks.com/blog/how-embed-databricks-aibi-dashboards-customer-facing-applications
- Databricks Apps Cost (76% reduction workaround): community.databricks.com posts
- AI/BI April 2026 Updates: https://aibilakehouse.substack.com/p/april-2026-whats-new-in-databricks

### 2026 Release Highlights

- Mar 2026: SDK/REST API sharing with all account users (GA)
- Apr 2026: Embedding for External Users (Ungated Public Preview)
- Apr 2026: Automatic identity management (GA)
- May 2026: Databricks One Mobile
- Publish with Service Principal credentials
- Genie Code non-table outputs
- Tabular attachments in email subscriptions

---

*End of Feature Comparison Document*

*Recommended: Combine with `chat_hist_20260713_01.md` for full context*
