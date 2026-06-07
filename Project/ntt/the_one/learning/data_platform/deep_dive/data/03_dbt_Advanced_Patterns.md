# dbt — Advanced Patterns Deep Dive

> Semantic layer, exposures, contracts, snapshots, packages
> สิ่งที่แยก dbt power user ออกจาก beginner

---

## 1. dbt Mental Model — มองให้ชัด

### dbt คืออะไร / ไม่ใช่อะไร

✅ **คืออะไร**:
- Transform layer ใน ELT (T ใน E-L-T)
- SQL → DAG ของ models
- Test framework
- Documentation generator
- Lineage tracker

❌ **ไม่ใช่**:
- Orchestrator (ใช้ Airflow/Dagster ภายนอก)
- ETL tool (ไม่ extract/load data)
- Data warehouse (ใช้ BQ/Snowflake/Redshift/etc.)

### dbt Project Structure

```
my_dbt_project/
├── dbt_project.yml          # config
├── packages.yml             # external packages
├── models/
│   ├── staging/             # raw → renamed/typed
│   │   ├── stg_orders.sql
│   │   └── stg_customers.sql
│   ├── intermediate/        # business logic
│   │   └── int_orders_by_customer.sql
│   ├── marts/               # final tables for BI
│   │   ├── core/
│   │   │   ├── dim_customers.sql
│   │   │   └── fct_orders.sql
│   │   └── marketing/
│   │       └── customer_360.sql
│   └── schema.yml           # tests + docs + contracts
├── snapshots/               # SCD2 history
├── macros/                  # reusable SQL
├── analyses/                # ad-hoc SQL
├── seeds/                   # CSV → tables
└── tests/                   # custom tests
```

---

## 2. Layered Modeling (Best Practice)

### 3-Layer Pattern

```
┌────────────────────────────────────────────┐
│  MARTS (gold)                              │
│  Business-facing, denormalized, aggregated │
│  fct_orders, dim_customers, customer_360   │
└──────────────────┬─────────────────────────┘
                   │
┌──────────────────▼─────────────────────────┐
│  INTERMEDIATE (silver)                     │
│  Business logic, joins, calculations       │
│  int_orders_with_customer                  │
└──────────────────┬─────────────────────────┘
                   │
┌──────────────────▼─────────────────────────┐
│  STAGING (bronze cleaned)                  │
│  1:1 with source, renamed/typed            │
│  stg_orders, stg_customers                 │
└──────────────────┬─────────────────────────┘
                   │
┌──────────────────▼─────────────────────────┐
│  SOURCES (raw)                             │
│  External tables, no transformations       │
│  source.raw.orders                         │
└────────────────────────────────────────────┘
```

### Naming Conventions

```
stg_<source>__<entity>      stg_stripe__charges
int_<entity>_<verb>_<entity> int_orders_grouped_by_customer
fct_<entity>                fct_orders     (facts/events)
dim_<entity>                dim_customers  (dimensions/entities)
mart_<domain>_<entity>      mart_marketing_attribution
```

### Sources Definition

```yaml
# models/staging/sources.yml
version: 2

sources:
  - name: stripe                     # source system
    database: raw                    # warehouse db
    schema: stripe_data
    tables:
      - name: charges
        description: "Raw Stripe charges"
        loaded_at_field: _loaded_at
        freshness:
          warn_after: {count: 12, period: hour}
          error_after: {count: 24, period: hour}
        columns:
          - name: id
            tests:
              - unique
              - not_null
```

### Use sources in models

```sql
-- models/staging/stg_stripe__charges.sql
SELECT
    id AS charge_id,
    amount / 100 AS amount_usd,
    customer_id,
    created::TIMESTAMP AS charged_at
FROM {{ source('stripe', 'charges') }}
WHERE NOT _deleted
```

---

## 3. Macros — Reusable SQL

### Built-in Macros ที่ใช้บ่อย

```sql
{{ ref('model_name') }}              -- Reference another model
{{ source('schema', 'table') }}      -- Reference source
{{ var('my_var') }}                  -- Project variable
{{ this }}                           -- Current model
{{ target.name }}                    -- 'dev' / 'prod'
```

### Custom Macros

```sql
-- macros/cents_to_dollars.sql
{% macro cents_to_dollars(column_name) %}
    ({{ column_name }} / 100)::NUMERIC(16, 2)
{% endmacro %}
```

```sql
-- Use in model
SELECT
    id,
    {{ cents_to_dollars('amount') }} AS amount_dollars
FROM {{ source('stripe', 'charges') }}
```

### Generate dynamic SQL

```sql
-- macros/pivot_amounts_by_status.sql
{% macro pivot_amounts(statuses) %}
    {% for status in statuses %}
        SUM(CASE WHEN status = '{{ status }}' THEN amount END) 
            AS amount_{{ status }}
        {% if not loop.last %},{% endif %}
    {% endfor %}
{% endmacro %}
```

```sql
SELECT
    customer_id,
    {{ pivot_amounts(['paid', 'failed', 'refunded']) }}
FROM {{ ref('stg_charges') }}
GROUP BY customer_id
```

### dbt-utils package — must have

```yaml
# packages.yml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.1
```

```sql
-- Useful patterns
{{ dbt_utils.surrogate_key(['col1', 'col2']) }}
{{ dbt_utils.pivot('status', dbt_utils.get_column_values(...)) }}
{{ dbt_utils.deduplicate(...) }}
```

---

## 4. Materializations — When to Use Each

### Types

| Type | What it does | Use case |
|---|---|---|
| `view` | Just CREATE VIEW | Cheap models, frequently changing |
| `table` | CREATE TABLE AS | Default, materialized result |
| `incremental` | Append/merge new rows | Large fact tables |
| `ephemeral` | Inline as CTE | Reusable logic, no materialization |
| `materialized_view` | Native MV | Auto-refresh aggregates |

### Configuration

```sql
-- In model file
{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge',
    on_schema_change='sync_all_columns'
) }}

SELECT ...
```

### Incremental Pattern

```sql
{{ config(materialized='incremental', unique_key='order_id') }}

SELECT
    order_id,
    customer_id,
    amount,
    created_at
FROM {{ source('stripe', 'orders') }}

{% if is_incremental() %}
    -- Only new records since last run
    WHERE created_at > (SELECT MAX(created_at) FROM {{ this }})
{% endif %}
```

### Incremental Strategies

| Strategy | What |
|---|---|
| `append` | Just INSERT new rows |
| `merge` | INSERT or UPDATE on key match |
| `delete+insert` | DELETE matching, then INSERT |
| `insert_overwrite` | Replace partition entirely |

---

## 5. Tests — Beyond Basics

### Built-in Tests

```yaml
# models/marts/schema.yml
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: status
        tests:
          - accepted_values:
              values: ['paid', 'pending', 'cancelled']
      - name: customer_id
        tests:
          - relationships:
              to: ref('dim_customers')
              field: customer_id
```

### dbt-utils Tests

```yaml
columns:
  - name: amount
    tests:
      - dbt_utils.expression_is_true:
          expression: ">= 0"
      - dbt_utils.not_null_proportion:
          at_least: 0.95
```

### Singular Tests (custom SQL)

```sql
-- tests/no_duplicate_orders_per_day.sql
SELECT
    customer_id,
    DATE(created_at) AS order_date,
    COUNT(*) AS order_count
FROM {{ ref('fct_orders') }}
GROUP BY 1, 2
HAVING COUNT(*) > 50  -- Suspicious: > 50 orders/day per customer
```

If this query returns rows → test fails

### Generic Tests (reusable)

```sql
-- tests/generic/test_within_range.sql
{% test within_range(model, column_name, min_val, max_val) %}
    SELECT *
    FROM {{ model }}
    WHERE {{ column_name }} < {{ min_val }} OR {{ column_name }} > {{ max_val }}
{% endtest %}
```

```yaml
columns:
  - name: amount
    tests:
      - within_range:
          min_val: 0
          max_val: 1000000
```

---

## 6. dbt Contracts (2024+) — Schema Enforcement

### Why Contracts

Without contracts:
- Add new column → downstream pipeline breaks silently
- Rename column → BI dashboard breaks
- Type change → wrong data in reports

### Contract Syntax

```yaml
# models/marts/schema.yml
models:
  - name: dim_customers
    config:
      contract:
        enforced: true  # ← turn on
    columns:
      - name: customer_id
        data_type: string  # required when contract enforced
        constraints:
          - type: not_null
          - type: primary_key
      - name: email
        data_type: string
        constraints:
          - type: not_null
      - name: signup_date
        data_type: date
```

### What Contracts Enforce

- ✅ Column names match
- ✅ Data types match
- ✅ Constraints (PK, FK, NOT NULL)
- ✅ Order of columns

If model query produces different schema → `dbt build` fails

### Versioned Models (consume safely)

```yaml
models:
  - name: dim_customers
    latest_version: 2
    versions:
      - v: 1
        defined_in: dim_customers_v1
        config: {alias: dim_customers_v1}
      - v: 2
        # current
```

```sql
-- Downstream model
SELECT * FROM {{ ref('dim_customers', v=2) }}
```

---

## 7. Snapshots — SCD Type 2 History

### Problem

Customer's address changes. Need to know address at time of past order.

### Solution: dbt Snapshots

```sql
-- snapshots/customers_snapshot.sql
{% snapshot customers_snapshot %}

{{
    config(
      target_schema='snapshots',
      unique_key='customer_id',
      strategy='timestamp',
      updated_at='updated_at',
    )
}}

SELECT * FROM {{ source('crm', 'customers') }}

{% endsnapshot %}
```

### What it produces

```
customers_snapshot table:
customer_id | name    | address    | dbt_valid_from         | dbt_valid_to
----------- | ------- | ---------- | ---------------------- | ----------------------
1           | Alice   | Old Addr   | 2026-01-01 00:00:00    | 2026-04-15 12:00:00
1           | Alice   | New Addr   | 2026-04-15 12:00:00    | NULL  (current)
2           | Bob     | ...        | 2026-01-01 00:00:00    | NULL  (current)
```

### Strategies

#### Timestamp Strategy (preferred)
```yaml
strategy='timestamp'
updated_at='last_modified'
```
Compare `updated_at` column to detect changes

#### Check Strategy
```yaml
strategy='check'
check_cols: ['email', 'address']
```
Compare specified columns to detect changes (slow but works without timestamp)

### Use snapshot in models

```sql
-- Get customer info as of order time
SELECT
    o.order_id,
    o.created_at,
    c.name,
    c.address  -- address as it was when order placed
FROM {{ ref('fct_orders') }} o
LEFT JOIN {{ ref('customers_snapshot') }} c
    ON o.customer_id = c.customer_id
    AND o.created_at >= c.dbt_valid_from
    AND (o.created_at < c.dbt_valid_to OR c.dbt_valid_to IS NULL)
```

---

## 8. Exposures — Document Downstream Usage

### Why Exposures

Lineage stops at dbt model — but what about Tableau dashboards, Python ML?

### Define Exposure

```yaml
# models/exposures.yml
version: 2

exposures:
  - name: customer_360_dashboard
    type: dashboard
    maturity: high
    url: https://tableau.example.com/views/customer-360
    description: "Customer 360 dashboard for sales team"
    
    depends_on:
      - ref('dim_customers')
      - ref('fct_orders')
      - ref('mart_customer_lifetime_value')
    
    owner:
      name: Sales Analytics Team
      email: sales-analytics@example.com
  
  - name: churn_prediction_model
    type: ml
    maturity: medium
    url: https://vertex.example.com/models/churn-v3
    depends_on:
      - ref('mart_customer_features')
    owner:
      name: Data Science
      email: ds@example.com
```

### What you get

- **Lineage extends** to dashboards / ML models
- **Impact analysis**: "if I change `dim_customers`, what dashboards break?"
- **Documentation**: dbt docs site shows exposures

```bash
dbt ls --select +exposure:customer_360_dashboard
# Shows all upstream models
```

---

## 9. Semantic Layer (dbt Mesh / dbt Cloud Semantic Layer)

### Problem: "What is Active User?"

5 dashboards = 5 different definitions of "Active User"
- Marketing: logged in last 30 days
- Product: opened app last 7 days
- Sales: any activity ever
- Finance: paid customer
- CEO: combined?

### Solution: Semantic Layer

Define metrics ONCE in dbt:

```yaml
# models/marts/customers/customers.yml
semantic_models:
  - name: orders
    model: ref('fct_orders')
    
    entities:
      - name: order
        type: primary
        expr: order_id
      - name: customer
        type: foreign
        expr: customer_id
    
    measures:
      - name: order_count
        agg: count
      - name: gmv
        expr: amount
        agg: sum
      - name: avg_order_value
        expr: amount
        agg: avg
    
    dimensions:
      - name: order_date
        type: time
        type_params:
          time_granularity: day
      - name: status
        type: categorical

metrics:
  - name: revenue
    description: "Gross merchandise value"
    type: simple
    type_params:
      measure: gmv
  
  - name: revenue_growth
    description: "MoM revenue growth"
    type: derived
    type_params:
      expr: (revenue - revenue_prev_month) / revenue_prev_month
      metrics:
        - name: revenue
        - name: revenue
          alias: revenue_prev_month
          offset_window: 1 month
```

### Query the Metric

```python
from dbt_metricflow import Client

client = Client()

# Get revenue by month
df = client.query_metric(
    metric="revenue",
    group_by=["order_date__month"]
)

# Get revenue with filter
df = client.query_metric(
    metric="revenue",
    where="status = 'paid'",
    group_by=["customer__country"]
)
```

Tableau, Looker, Hex, Streamlit can call same API → all show same number

---

## 10. dbt Mesh (Multi-Project)

### Problem: Single dbt Project Doesn't Scale

500+ models in one project:
- Slow runs
- Merge conflicts
- Unclear ownership

### Solution: Multi-Project (dbt Mesh)

```
Project: marketing/
  ├── models/
  │   ├── customer_segments.sql
  │   └── attribution.sql
  └── public_models.yml
       (declares which models other projects can use)

Project: finance/
  ├── models/
  │   └── revenue_by_segment.sql
  └── (depends on marketing)

Project: ml/
  ├── models/
  │   └── churn_features.sql
  └── (depends on marketing + finance)
```

### Cross-Project Reference

```sql
-- In ml project, reference marketing model
SELECT * FROM {{ ref('marketing', 'customer_segments') }}
```

### Benefits

- ✅ Each team owns their project
- ✅ Public/private model boundaries
- ✅ Lineage cross-project
- ✅ Independent CI/CD
- ✅ Faster runs

---

## 11. Performance Tuning

### Run only what changed

```bash
# Run modified models + downstream
dbt build --select state:modified+ \
          --state ./manifest_prod/

# Useful in CI
```

### Parallel execution

```bash
dbt run --threads 8
```

```yaml
# dbt_project.yml
models:
  +threads: 8
```

### Materialization choices

| Model size | Run frequency | Materialization |
|---|---|---|
| Small (< 1M rows) | Hourly | view or table |
| Medium (1M-100M) | Daily | table |
| Large (> 100M) | Daily | incremental |
| Aggregate | Hourly | table or materialized_view |
| One-time logic | N/A | ephemeral (CTE) |

### Avoid full refresh on incrementals

```sql
{{ config(
    materialized='incremental',
    unique_key='id',
    incremental_strategy='merge',
    cluster_by=['date'],
    partition_by={
        'field': 'date',
        'data_type': 'date',
        'granularity': 'day'
    }
) }}
```

---

## 12. dbt + Iceberg (2025+)

### Setup

```yaml
# dbt_project.yml or profiles.yml
models:
  +file_format: iceberg
  +location_root: gs://warehouse/iceberg
```

### Materialized as Iceberg

```sql
{{ config(
    materialized='table',
    file_format='iceberg',
    table_properties={
        'write.format.default': 'parquet',
        'write.delete.mode': 'merge-on-read'
    }
) }}

SELECT ...
```

### Incremental on Iceberg

```sql
{{ config(
    materialized='incremental',
    file_format='iceberg',
    incremental_strategy='merge',
    unique_key='id',
    partition_by=[{'field': 'event_date', 'transform': 'days'}]
) }}
```

---

## 13. Anti-Patterns

### ❌ SELECT * everywhere
```sql
-- Bad
SELECT * FROM {{ ref('huge_table') }}

-- Good
SELECT customer_id, amount, status FROM {{ ref('huge_table') }}
```

### ❌ Wide DAG with no layers
```
500 models all referencing source directly
→ no logical organization
→ hard to find logic
```

### ❌ Not using staging models
```sql
-- Bad: business logic mixed with cleaning
SELECT 
    UPPER(name) AS name,
    amount / 100 AS amount,
    SUM(amount) OVER (PARTITION BY customer_id) AS lifetime_value
FROM {{ source('stripe', 'orders') }}

-- Good: separate concerns
-- stg_orders: clean
-- int_orders: business logic
-- fct_orders: final shape
```

### ❌ No tests
Pipeline runs successfully ≠ data is correct

### ❌ Over-using ephemeral
Ephemeral creates inline CTE → can blow up SQL size, hard to debug

### ❌ Hardcoded values
```sql
-- Bad
WHERE country IN ('TH', 'SG', 'MY')

-- Good (using variables)
WHERE country IN ({{ "'" + var('countries') | join("','") + "'" }})
```

---

## 14. Cheat Sheet

### Q: "ทำไม dbt เป็น standard?"
> "1. SQL = ใช้ skill ที่ analyst มีอยู่แล้ว
> 2. Git workflow = version control + PR review
> 3. Tests inline = quality ติด pipeline
> 4. Docs auto-gen = lineage + business glossary
> 5. Modular = reusable, testable
> ทำให้ analytics engineering เป็น software engineering discipline"

### Q: "Materialization ใช้ตัวไหน?"
> "view: เร็ว build, query slow — เหมาะ small/dev
> table: standard — ส่วนใหญ่ใช้
> incremental: large + frequently appended — fact tables
> ephemeral: inline CTE — small reusable logic
> materialized view: warehouse-managed refresh"

### Q: "Contracts vs tests ต่างกัน?"
> "Tests: validate data quality (nulls, ranges, uniqueness)
> Contracts: enforce schema shape (column names, types, constraints)
> Tests run after build, contracts validate during build"

### Q: "Semantic layer ดียังไง?"
> "นิยาม metric ที่เดียว — ทุก dashboard ดึงค่าเดียวกัน
> ลด 'CEO Dashboard ตัวเลขไม่ตรง' problem
> ใช้ MetricFlow API เป็น layer กลาง"

---

## Sources

- [dbt Documentation](https://docs.getdbt.com/)
- [dbt Best Practices Guide](https://docs.getdbt.com/best-practices)
- [Implementing shift-left governance in your dbt stack](https://www.getdbt.com/resources/coalesce-on-demand/implementing-shift-left-governance-in-your-dbt-stack-practical-application-of-data-contracts-and)
- [dbt Data Contracts: Quick Primer](https://atlan.com/dbt-data-contracts/)
- [How to build reliable data pipelines with data quality checks](https://www.getdbt.com/blog/data-pipeline-quality-checks)
