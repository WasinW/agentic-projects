# Data Analyst — Comprehensive Knowledge

> Deep reference for the data-analyst subagent.

---

## 1. Foundations

### What a Data Analyst does

Turns data into **decisions**. Sits between data infrastructure and business stakeholders. Owns: queries, dashboards, ad-hoc analysis, metric definitions, sometimes data quality.

### Analyst tiers (org-dependent terms)

- **Data Analyst** — SQL + Excel + BI tool; focused on reporting + ad-hoc
- **Analytics Engineer** — dbt + SQL + data modeling; bridges DE + Analyst
- **BI Engineer** — dashboarding focus + occasionally pipelines
- **Business Analyst** — process + requirements (different track)
- **Data Scientist** — statistics + ML

Modern teams blur these.

### Key skills

- SQL fluency (this is the bread + butter)
- Statistical literacy (means, variance, correlation, significance — not necessarily inference)
- Visualization design
- Business-domain understanding
- Communication (concise findings, executive summaries)
- Python / R basics for occasional analysis

---

## 2. Mental Models / Decision Frameworks

### Always start with the decision

> "What decision does this number drive?"

If no one will act on the output, don't build it. Many dashboards exist as comfort blankets, not decision tools.

### Question → Metric → Source → Method → Output

```
Q: Why did revenue drop last week?
↓
Metric: Daily revenue
↓
Source: orders fact table, time grain = day
↓
Method: trend + slice by product, region, channel
↓
Output: chart + explanation + recommended action
```

Skip steps → wrong answer to the wrong question.

### Define the metric exactly

"Active user" can mean:
- Logged in (when?)
- Made a purchase (when?)
- Took a primary action (which one?)
- Time window (last 7d, 30d, ever)

Get explicit. Document in glossary. Stick to it.

### Sample for exploration, full data for production

Exploration: TABLESAMPLE 1% of huge table — 100× cheaper, still see patterns.
Production reports: full data once decision is made.

### Three types of analysis

| Type | Question | Method |
|---|---|---|
| **Descriptive** | What happened? | Aggregations, trends |
| **Diagnostic** | Why? | Slice, dice, correlate |
| **Predictive / prescriptive** | What will / should happen? | Models (often hand off to DS) |

Analyst's bread + butter: descriptive + diagnostic.

### Correlation vs causation

- "Sales correlate with ice cream consumption" — both caused by hot weather
- Causal claims need: A/B test, natural experiment, or specific causal inference methodology
- "Customers who use feature X churn less" — selection bias if user choice
- Cautious wording in deliverables saves your credibility

### Statistical significance vs business significance

- p < 0.05 doesn't mean "real impact"
- A 0.01% lift can be statistically significant with millions of samples
- Always ask: is the effect size meaningful for the business?

### When to push back

- Vague request → ask for the underlying decision
- "Make a dashboard for X" → "Who uses it for what?"
- "Compare A vs B" → "What's the criterion for picking?"
- Push for specificity early. Saves both sides time.

---

## 3. Standard Practices

### SQL patterns analysts use daily

**Window functions** (essential):
```sql
ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY ts DESC)
SUM(amount) OVER (PARTITION BY user_id ORDER BY ts ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)
LAG(value, 1) OVER (PARTITION BY user_id ORDER BY ts)
```

**CTEs** (readable composition):
```sql
WITH
  recent_orders AS (...),
  user_segments AS (...)
SELECT ... FROM recent_orders JOIN user_segments
```

**Conditional aggregation**:
```sql
SELECT
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE status = 'completed') AS completed,
  COUNT(*) FILTER (WHERE status = 'cancelled') AS cancelled
FROM orders
```

**Date arithmetic** (varies by SQL dialect; memorize yours).

### Cohort analysis

```
For users who first did X in month M, how many did Y in months M, M+1, M+2, ...?
```

Standard chart: triangle (rows = cohorts, cols = period offsets).

### Funnel analysis

```
% completing each step in a sequence
Drop-off between steps = optimization opportunity
```

Watch out for: time windows, definition of "completed", multi-session journeys.

### A/B test analysis

- Pre-register the metric + threshold
- Sample size calculation BEFORE the test
- Bonferroni correction for multiple metrics
- Variance reduction (CUPED) for sensitivity
- Avoid "peeking" (look only at planned milestones)

### Dashboard design principles

- **One question per dashboard** — not "everything for everyone"
- **5-second rule** — viewer should grasp main point in 5s
- **Most important number top-left** — Western reading pattern
- **Annotate context** — "vs last week", "vs target"
- **Color sparingly** — meaningful, not decorative
- **Cap to 1 screen** — scrolling = lost focus
- **Refresh cadence visible** — viewers should know if data is stale

### Visualization choice

| Goal | Chart |
|---|---|
| Compare across categories | Bar |
| Show change over time | Line |
| Show composition | Stacked bar / area |
| Show relationship | Scatter |
| Show distribution | Histogram, box plot |
| Show flow | Sankey |
| Show geography | Map |
| Single number | Big number |

**Avoid**: pie charts >5 slices, 3D charts, dual y-axes (usually misleading).

### Metric definitions (governance)

- Maintained in business glossary
- Reviewed by domain owner
- Versioned (changes annotated)
- Available in semantic layer (dbt metrics / MetricFlow / LookML / Cube)

---

## 4. Tools Landscape (2026)

### SQL editors / BI
- **Hex / Mode / Sigma / Hashboard** — modern collaborative
- **Looker / Looker Studio** — Google
- **Power BI** — Microsoft enterprise
- **Tableau** — classic, strong viz
- **Metabase** — OSS, simple
- **Superset** — Apache OSS, dbt-native
- **Holistics** — emerging
- **Preset** (managed Superset)

### Transformation / modeling
- **dbt Cloud / Core** — analytics engineering standard
- **SQLMesh** — newer alternative
- **Dataform** — GCP-native

### Semantic layer
- **Cube** — open, flexible
- **dbt Semantic Layer / MetricFlow**
- **LookML** (Looker)

### Notebooks
- **Hex** — collaborative
- **Deepnote** — collaborative
- **Jupyter / Google Colab** — DIY
- **Observable** — JS data viz

### Spreadsheet (still ubiquitous)
- **Excel** — enterprise default, surprisingly capable
- **Google Sheets** — collaborative

### Python ecosystem for analysts
- **pandas** — DataFrames
- **polars** — fast pandas alternative
- **DuckDB** — local SQL on Parquet
- **matplotlib / plotly / seaborn / altair** — viz

### Reverse ETL (operational analytics)
- **Hightouch / Census** — push data warehouse → SaaS apps

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Dashboard nobody uses | Wasted effort | Validate use before building |
| Metric defined per dashboard | Inconsistency | Semantic layer |
| Dual y-axis | Misleading | Two separate charts |
| 3D pie chart | Hard to compare | Bar chart |
| Decimals on every number | Noise | Round to meaningful precision |
| One-shot SQL with no comments | Future-you confused | CTE + comments + cleanup |
| "Just one more drill-down" | Endless complexity | Pre-define the questions |
| Analyzing without seeing source | Misinterpret | Check raw rows first |
| Hardcoded date ranges | Stale next quarter | Dynamic date logic |
| Not slicing by user / region | Hides important variation | Always slice on key dims |
| Confusing correlation + causation | Wrong recommendation | Explicit causal language |
| Reporting averages on skewed data | Misrepresents | Median + percentiles |

---

## 6. Advanced / Expert Topics

### Causal inference for analysts

Without a randomized experiment:
- **Difference-in-differences (DiD)** — compare change before/after, treated vs control group
- **Regression discontinuity** — exploit a threshold
- **Synthetic control** — construct counterfactual from similar units
- **Propensity score matching** — match on observables, hope for the best

These are dangerous without statistics training. Be humble.

### Bayesian thinking

- Prior + Evidence → Posterior
- For analysts: useful for combining multiple weak signals
- A/B testing: Bayesian frameworks (e.g., Variance, GrowthBook) more intuitive than frequentist

### Survey + qual research

When the question requires "why" the data can't answer:
- User interviews
- Surveys (with statistical design)
- Mix qual + quant for full picture

Many "data" problems are really "understanding" problems.

### Predictive analytics (without ML)

- Linear regression (still useful)
- Logistic regression for binary outcomes
- Simple time-series (moving avg, exponential smoothing)
- Hand off to DS when complexity grows

### Storytelling with data

- Lead with the headline
- One slide per claim
- Supporting evidence visible
- Acknowledge limitations
- End with recommendation

Books: "Storytelling with Data" — Cole Knaflic.

### Metric trees

Hierarchical decomposition:
```
Revenue
├── # Customers × Revenue per Customer
│   ├── New customers
│   ├── Returning customers
│   └── Churn rate
└── ...
```

Useful for diagnostic analysis ("why did revenue drop?").

### Forecasting basics

- Trend + seasonality + noise
- Tools: Prophet, statsmodels, simple exponential smoothing
- Don't extrapolate too far
- Communicate uncertainty (confidence intervals)

---

## 7. References

### Books
- **Storytelling with Data** — Cole Knaflic
- **The Functional Art** — Alberto Cairo
- **Naked Statistics** — Charles Wheelan
- **Trustworthy Online Controlled Experiments** — Kohavi, Tang, Xu
- **Practical Statistics for Data Scientists** — Bruce, Bruce

### Blogs / Newsletters
- **Locally Optimistic** (Slack + podcast) — analytics engineering community
- **Cassie Kozyrkov** — decision science
- **Stitch Fix Algorithms blog**
- **Towards Data Science**

### Communities
- **dbt Slack** (#analytics-engineering)
- **Locally Optimistic** Slack
- **Analytics Engineering Roundup**

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| Data Engineer | "Need this in the warehouse" |
| Data Architect | "Help me understand the model" |
| ML Engineer | "Translate this into a feature / model" |
| Business stakeholder | "Translate question into analysis plan" |
| Data Domain Expert | "What does this field actually mean?" |
| Product | "A/B test design, metric definition" |
| Governance | "Metric ownership, glossary" |

---

*Analysis is service work. Your job is making decisions easier for the people you serve.*
