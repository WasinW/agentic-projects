# Finance Consultant — Comprehensive Knowledge

> Deep reference for the finance-consultant subagent. Senior corporate finance / FP&A advisor on the financial side of data/tech projects — business cases, unit economics, cost/ROI. Current context: AIA (regulated insurer), cloud cost/FinOps angle. The-1 (retail loyalty, Central Group) appears only as an explicitly-marked past-engagement example, never the default lens.

---

## 1. Foundations

### What a Finance Consultant does

Turns a technical proposal into a **defensible financial decision**. The job is not bookkeeping — it's framing money so a CFO/CIO can say yes/no with confidence.
- Build the **business case** — cost, benefit, ROI, payback, NPV
- Model **unit economics** — cost-per-customer, cost-per-query, margin per data product
- Run **FP&A** — budget, forecast, variance, scenario
- **Cost allocation** — turn a shared cloud bill into per-team / per-product cost
- Translate between **engineering reality and finance language** (opex/capex, accruals, fully-loaded cost)

The deliverable is almost always: a model + a one-page recommendation + the 2-3 numbers that actually drive the decision.

### The mindset

Finance is the language of **tradeoffs under uncertainty**. Every number is an assumption with a confidence interval. A senior finance consultant is opinionated about *which assumptions matter* (the drivers) and ruthless about ignoring the rest. Precision is cheap; being directionally right on the big drivers is everything.

### Adjacent roles

- **Investment Consultant** — does formal project appraisal (NPV/IRR, capital allocation, hurdle rates). Finance consultant builds the operating model that *feeds* the appraisal.
- **Business Analyst** — defines requirements + benefits in business terms; finance consultant prices them.
- **Platform Ops / FinOps Engineer** — owns the cloud-cost data + allocation tags; finance consultant consumes that to build unit economics. (See §8.)
- **Data Analyst** — produces the actuals + cohorts; finance consultant turns them into forecasts + variance.
- **Controller / Accountant** — owns the books + GAAP/IFRS treatment; finance consultant works *forward-looking*, the controller works *backward-looking*.

The rule of thumb: **accounting tells you what happened, FP&A tells you what's likely to happen and what to do about it.**

---

## 2. Mental Models / Decision Frameworks

### The three financial statements (and how they link)

| Statement | Question it answers | Time view |
|---|---|---|
| **P&L (Income Statement)** | Are we profitable? | A period (accrual) |
| **Balance Sheet** | What do we own/owe right now? | A snapshot |
| **Cash Flow** | Where did the cash actually go? | A period (cash) |

They link, and this linkage is the single most important model in finance:
- Net income (bottom of P&L) → flows into **retained earnings** on the balance sheet.
- Net income → top of the **cash flow statement**, then adjusted for non-cash items (depreciation) + working-capital changes → ending cash → back onto the balance sheet.
- Balance sheet must **balance**: Assets = Liabilities + Equity.

If you can't explain how a $1M software purchase moves through all three (capex on BS → depreciation on P&L → cash out on CFS), you don't yet understand the proposal.

### Cash vs Accrual — the trap that fools engineers

- **Accrual** — revenue/expense recognized when *earned/incurred*, not when cash moves. This is the P&L.
- **Cash** — when money actually leaves/arrives. This is the CFS.

Why it matters for data projects: a $360K/yr annual cloud commit paid upfront is **one cash outflow now** but **$30K expense per month** on the P&L. A project can be P&L-positive and cash-negative simultaneously. Always ask *which* you're being shown.

### Opex vs Capex — directly relevant to cloud

| | Capex | Opex |
|---|---|---|
| What | Buy an asset, use it over years | Consume a service as you go |
| P&L hit | Spread via **depreciation/amortization** | Full expense in the period |
| Example | On-prem cluster, perpetual license, internal software dev (capitalizable) | Cloud subscription, SaaS, managed pipelines |
| Cash | Big upfront | Smooth monthly |

The cloud shift is fundamentally a **capex → opex shift**. This is a feature (no upfront, scales with use) and a trap (no asset on the books, costs grow silently, CFO loses the one-time-approval gate). Note: internally-developed software can often be **capitalized** (IAS 38 / ASC 350-40) — building the data platform in-house may put dev cost on the balance sheet rather than the P&L. Flag this; it changes the headline numbers.

### Unit economics — the heart of any data/loyalty business case

The discipline of profit-and-cost **per single unit** (a customer, a transaction, a query, a model inference). It separates "the bill went up" from "the cost per customer is out of control."

**Contribution margin** = Revenue − Variable Cost, per unit.
```
Contribution Margin per unit = Price − Variable Cost per unit
CM Ratio = Contribution Margin / Revenue
Breakeven volume = Fixed Costs / Contribution Margin per unit
```
Contribution margin is what's left to cover fixed costs + profit. It's the number that tells you whether *one more unit* helps or hurts.

**CAC (Customer Acquisition Cost)**
```
CAC = (Sales + Marketing spend in period) / New customers acquired in period
```
Include fully-loaded cost — salaries, tooling, agency fees — not just ad spend.

**LTV (Customer Lifetime Value)** — use the *gross-margin* version, never raw revenue:
```
LTV (revenue) = AOV × Purchase Frequency × Customer Lifespan
LTV (profit)  = LTV(revenue) × Gross Margin %
        or    = (ARPU × Gross Margin %) / Churn Rate     (subscription form)
```
Example (retail loyalty): AOV ฿800 × 3 visits/yr × 2.5 yr = ฿6,000 revenue × 65% margin ≈ **฿3,900 profit LTV**.

**LTV:CAC ratio** — the headline health metric.
- **< 1:1** — losing money on every customer
- **1–3:1** — under-investing or unprofitable acquisition
- **3:1** — the canonical "healthy" target
- **> 5:1** — likely *under*-spending on growth (leaving customers on the table)

**CAC Payback Period** — how long to recover acquisition cost:
```
CAC Payback (months) = CAC / (Monthly Revenue per Customer × Gross Margin %)
```
This is a *cash/risk* metric — LTV:CAC can look great while payback is 30 months and starves cash. Always show both.

### Fixed vs Variable cost

- **Fixed** — don't move with volume short-term (salaries, reserved instances, platform licenses).
- **Variable** — scale with usage (per-query compute, egress, per-API-call SaaS).
- **Step-fixed** — fixed until a threshold, then jump (a new node, a license tier).

Cloud is mostly variable, which is why it's hard to budget. The FinOps job is partly to *convert* variable into committed/fixed (reservations, savings plans) where demand is predictable.

### Gross vs Net margin

```
Gross Margin = (Revenue − COGS) / Revenue
Operating Margin = Operating Income / Revenue   (after opex, before interest/tax)
Net Margin = Net Income / Revenue                (after everything)
```
For a data platform, the interesting question is what counts as **COGS** — increasingly, *cloud + data infrastructure cost is COGS*, not overhead. That reframing is what makes cloud unit economics a margin conversation, not an IT-budget conversation.

### NPV / discounting — intro (hand the formal appraisal to investment-consultant)

Money now ≠ money later. Discount future cash flows to present value:
```
NPV = Σ [ CFₜ / (1 + r)ᵗ ]  − Initial Investment
```
where `r` = discount rate (cost of capital / hurdle rate, often 8–15%), `t` = period.
- **NPV > 0** → creates value, accept
- **IRR** = the `r` that makes NPV = 0; compare to hurdle rate
- **Payback** = years to recoup investment (ignores time value — simple but blunt)

Rule: for projects under ~1 year, payback is fine; for multi-year platform bets, insist on NPV.

---

## 3. Standard Practices

### Budgeting + forecasting (FP&A core)

| Method | What | When to use |
|---|---|---|
| **Incremental (last-year +%)** | Adjust prior budget | Stable, low-effort, lazy default |
| **Zero-based (ZBB)** | Justify every line from zero | Cost-cutting drives, bloated budgets |
| **Driver-based** | Model outputs from operational drivers | Modern default — see §6 |
| **Rolling forecast** | Continuously re-forecast 12–18 mo forward | Volatile environments; replaces the annual-budget death march |

A rolling forecast: as each period closes, actuals replace forecast and a new period is added at the far end. Driver-based modeling is what makes rolling forecasts *sustainable* — update the drivers, the model re-flows.

### Variance analysis

Actual vs Plan, then explain the gap.
```
Variance = Actual − Budget
Favorable / Unfavorable depending on direction
```
Decompose the variance — don't just report it:
- **Volume variance** — did we sell more/fewer units?
- **Rate/price variance** — did unit price/cost change?
- **Mix variance** — did the product/customer mix shift?

The value is the *why* (which driver missed, why, how to correct), not the number. GenAI in 2026 is heavily used to draft variance narratives — useful, but verify the drivers.

### Cost allocation

Turning a shared cost into per-consumer cost. Methods, weakest to strongest:
1. **Even split** — lazy, wrong, breeds resentment.
2. **Proportional by a driver** — allocate cloud cost by query volume / storage GB / seats. Defensible.
3. **Activity-based costing (ABC)** — trace cost to the activities that consume it, then to products. Most accurate, most work.

For data platforms: tag everything (team, product, environment), allocate shared/un-taggable cost by a fair driver, and **show the un-allocated "shared tax" explicitly** rather than hiding it.

### Pricing basics

- **Cost-plus** — cost × (1 + markup). Simple, ignores value.
- **Value-based** — price to the value delivered to the buyer. Highest margin, hardest to do.
- **Competitive** — anchor to market. Safe, commoditizing.

For internal data products, the analog is **chargeback** (bill teams real cost) vs **showback** (show cost, don't bill). Showback first to build cost-awareness; chargeback once allocation is trusted.

### ROI / payback for projects

```
ROI = (Net Benefit − Cost) / Cost
Simple Payback = Initial Investment / Annual Net Cash Inflow
```
The hard part is **quantifying the benefit honestly** — see anti-patterns. Categorize benefits as: hard cost savings (defensible), revenue uplift (estimate with a cohort/conversion model), risk avoidance (probability-weighted), and soft/strategic (name them but don't put them in the ROI numerator).

### Financial KPIs / dashboards

The set a finance consultant watches for a data/loyalty business:
- **Margin** — gross, contribution, operating
- **Unit economics** — CAC, LTV, LTV:CAC, payback, ARPU
- **Efficiency** — Rule of 40 (growth% + margin% ≥ 40 for SaaS-like), magic number
- **Cloud-as-%-of-revenue** — the FinOps north star (15–25% is common for digital-heavy businesses)
- **Cash** — burn, runway, working-capital cycle (CCC)

### Scenario + sensitivity analysis

- **Scenario** — coherent bundles: Base / Bull / Bear, each a consistent set of driver values.
- **Sensitivity** — flex *one* driver, hold the rest, see impact. Reveals which assumption the answer hinges on.
- **Monte Carlo** — distribution on each driver, simulate thousands of outcomes. Overkill for most cases; use when the decision is large and uncertainty is genuinely probabilistic.

Always present a range, never a single point estimate. A single number signals false precision and invites the wrong fight.

---

## 4. Tools Landscape (2026)

### FP&A / planning platforms

| Tool | Sweet spot | Notes |
|---|---|---|
| **Anaplan** | Large enterprise, connected planning across functions | Proprietary "Hyperblock" engine; powerful but steep learning curve, costly, rigid reporting |
| **Pigment** | Mid / upper-mid market wanting agility | Fastest-growing modern alternative; cleaner UX, real-time collab; requires model rebuild in its native env |
| **Cube** | Mid-market, spreadsheet-native | Keeps Excel/Sheets as the front-end, adds AI forecasting + automated variance; high "spreadsheet continuity" |
| **Workday Adaptive Planning** | Mid-size, already on Workday | Solid consolidation + planning; not SaaS-metric specialized |
| **Planful / Vena / Datarails / Jedox** | Excel-continuity mid-market | Vena/Datarails lean hard on Excel familiarity |
| **Runway / Drivetrain** | Modern startup/scale-up FP&A | Driver-based, data-native, fast to stand up |

Opinion: for a Central-Group-scale entity, **Anaplan** is the incumbent-safe choice but heavy; **Pigment** is the better bet for 80% of modern finance teams that value speed + UX over maximal complexity. If the team lives in Excel and won't leave, **Cube** is the pragmatic answer.

### BI for finance

- **Power BI** — dominant in enterprise finance, strong DAX for financial calcs
- **Tableau** — viz-first, weaker on financial structure
- **Looker / Looker Studio** — good if data is already modeled in the warehouse (LookML = governed metrics)
- Increasingly: finance metrics defined once in a **semantic/metrics layer** (dbt Semantic Layer, Cube) and consumed by both BI and FP&A

### Spreadsheet modeling

Still the universal substrate. Excel/Google Sheets for the model itself; the FP&A tool is the system-of-record + collaboration + version control around it. **Never let a load-bearing business case live in one analyst's un-versioned spreadsheet** — that's an audit and bus-factor failure.

### Cloud-cost → finance bridge (FinOps)

| Tool | Role |
|---|---|
| **CloudZero** | Cloud unit economics — cost per customer/feature/product |
| **Amnic / Vantage / Ternary** | Cost allocation + unit-economics for multi-cloud + data platforms |
| **Apptio Cloudability / Flexera** | Enterprise FinOps, mature allocation + governance |
| **Native** (AWS Cost Explorer, GCP Billing, Snowflake/Databricks usage views) | First stop; query-level telemetry is where 2026 leaders are pushing visibility |

2026 FinOps reality: mature practice has moved past cost *visibility* to cost *intelligence* — **unit economics, AI-cost quantification, and influencing tech selection upstream**. For data platforms specifically (Snowflake/Databricks/BigQuery), leaders push attribution down to **query level**, normalizing proprietary units (credits, slots, DBUs) into one comparable view to get true data-product unit economics. Warehouse-level cost alone is no longer enough to understand value.

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| **Ignoring fully-loaded cost** | Counts ad spend but not the team's salary, tooling, overhead | Load every cost: people, infra, licenses, allocated overhead |
| **Vanity ROI** | Cherry-picks benefits, buries cost, assumes 100% adoption | Probability-weight benefits; bear-case the adoption curve |
| **Revenue ≠ cash thinking** | A "profitable" project that drains cash via upfront commits | Show P&L *and* cash flow; flag working-capital impact |
| **Single-point forecast** | False precision; one number to be wrong about | Always a range — Base/Bull/Bear + sensitivity |
| **Sunk-cost reasoning** | "We've already spent ฿5M, must continue" | Decide on *future* cash flows only; sunk cost is gone |
| **LTV without gross margin** | Revenue-LTV overstates value 30–50% | Always margin-adjusted LTV; show the assumption |
| **LTV:CAC with no payback** | Great ratio hiding a 30-month cash hole | Always pair LTV:CAC with CAC payback |
| **Discounting nothing** | Multi-year benefits counted at face value | Discount to NPV at the real cost of capital |
| **Allocating cloud cost evenly** | Penalizes light users, hides the heavy ones | Allocate by a real driver; surface shared tax |
| **Opex creep with no gate** | Cloud bill grows silently because no one re-approves | Budget owner + monthly variance + anomaly alerts |
| **Confusing capex savings with value** | "We avoided buying servers!" while opex quietly exceeds it | Compare total cost of ownership over the horizon, both modes |
| **Benefit double-counting** | Same headcount "saved" claimed by three projects | One benefit, one owner, one project — reconcile centrally |

---

## 6. Advanced / Expert Topics

### Driver-based modeling

Model financial outputs as functions of **operational drivers**, not as standalone line items.
```
Revenue = Active Customers × Visits/Customer × AOV × Attach Rate
Cloud Cost = Queries × Avg Cost/Query + Storage GB × $/GB + Egress GB × $/GB
```
Why it wins: change the *driver* (conversion +2pp, churn −1pp) and the whole model re-flows consistently. It makes forecasts explainable, ties variance to the specific driver that missed, and makes scenario/rolling forecasts cheap. Pitfall (per FP&A Trends): too many drivers → unmaintainable; pick the 5–10 that move 80% of the outcome and hold the rest as ratios.

### Cohort-based unit economics

Group customers by acquisition period (month/channel) and track each cohort's revenue, retention, and margin over its life. Reveals:
- True **retention curve** (and where it flattens — your real "lifespan")
- **Payback by cohort + channel** — which channels acquire *valuable* customers, not just *cheap* ones
- Whether unit economics are **improving or decaying** over time

This is the single most credible way to defend an LTV assumption to a skeptical CFO — show the actual cohort curves, not a single blended number. Past-engagement example (The-1 loyalty): cohort by enrollment campaign, track visits + basket + margin, and you can price the loyalty program's true return.

### Contribution-margin analysis (for product/feature decisions)

When deciding what to build/keep/kill in a data product portfolio, rank by contribution margin, not revenue. A high-revenue data product with high variable compute cost may have *lower* contribution than a small, cheap one. Breakeven volume + CM ratio tell you the floor each product must clear.

### Build vs Buy — the financials

| Dimension | Build | Buy |
|---|---|---|
| Upfront cost | High (eng time — often capitalizable) | Low (subscription) |
| Ongoing cost | Maintenance + opportunity cost of eng | Recurring license, grows with scale |
| Time to value | Slow | Fast |
| Customization | Total | Limited |
| Risk | Execution + key-person | Vendor lock-in + price hikes |

The honest model: **3–5 year TCO** of both, including the *opportunity cost* of engineers who build instead of building differentiating product, plus a risk adjustment. Build usually loses on a pure NPV basis unless the capability is core/differentiating — then strategic value (not in the numerator) tips it. Don't let "we can build it" decide a "should we build it" question.

### Data-platform cost-to-value

The frontier question (past-engagement example: The-1) was whether the data platform *pays for itself*. In the current context (AIA), this is the cloud/Databricks FinOps question — does platform spend justify the value it enables for underwriting/claims/actuarial use cases. Frame it as:
```
Platform Value = Σ (incremental margin from data-driven decisions)
              − Total platform cost (infra + people + tooling, fully loaded)
```
Attribute value to concrete use cases (better targeting → conversion uplift → incremental margin; churn model → retention → saved LTV). Be conservative and cohort-prove the uplift. Cost side: push to **per-data-product unit economics** (cost per pipeline, per dashboard, per ML feature) so you can kill the long tail of expensive, low-value products. Most platform cost hides in a few heavy products and a long tail nobody uses.

### Working capital

Cash tied up in operations: `Working Capital = Current Assets − Current Liabilities`. The **Cash Conversion Cycle** (DSO + DIO − DPO) measures how long cash is locked up. Less relevant for a pure-software data platform, but very relevant if the project touches **inventory, receivables, or supplier terms** (e.g., a demand-forecasting platform that reduces inventory frees cash — that cash release is a *real, often-ignored* benefit worth modeling).

### AI/ML cost economics (2026)

A live theme: inference + training cost is now a first-class unit-economics line. Cost per inference, per model, per AI-feature. The FinOps 2026 agenda is dominated by **quantifying AI value vs AI cost** — don't let "AI" escape the same fully-loaded, per-unit scrutiny as any other cost driver.

---

## 7. References

### Books
- **Financial Intelligence** — Berman & Knight (the bridge book for non-finance people — read first)
- **Financial Intelligence for IT Professionals** — Berman & Knight (same, tech-flavored)
- **The Lords of Strategy / HBR Guide to Building Your Business Case** — business-case framing
- **Corporate Finance** — Berk & DeMarzo (the rigorous textbook for NPV/IRR/cost of capital)
- **Lean Analytics** — Croll & Yoskovitz (unit economics + cohorts for digital businesses)
- **Financial Modeling** — Simon Benninga (the modeling reference)

### CFA-level / rigorous sources
- **CFA Institute curriculum** — Corporate Issuers + Financial Statement Analysis levels
- **Corporate Finance Institute (CFI)** — practical FP&A + valuation courses and guides — https://corporatefinanceinstitute.com/resources/fpa/driver-based-planning-guide/
- **Wall Street Prep / Wall Street Oasis** — LTV/CAC, modeling, valuation — https://www.wallstreetprep.com/knowledge/ltv-cac-ratio/
- **Damodaran Online** (NYU Stern) — valuation, cost of capital, the free gold standard

### FP&A + FinOps current (2025-2026)
- **FP&A Trends** — driver-based forecasting, modern FP&A practice — https://fpa-trends.com/article/driver-based-forecasting-fpa
- **State of FinOps 2026** — FinOps Foundation annual survey — https://data.finops.org/
- **FinOps for Data Cloud Platforms** — why warehouse cost ≠ value — https://www.finops.org/insights/finops-for-data-cloud-platforms/
- **CloudZero blog** — cloud unit economics — https://www.cloudzero.com/blog/finops-tools/
- **Cube** — FP&A tooling comparisons — https://www.cubesoftware.com/blog/best-fpa-software-tools
- **Saras Analytics** — ecommerce/retail LTV, CAC payback — https://www.sarasanalytics.com/blog/cac-payback-period
- **Beancount.io** — 2026 SaaS metrics stack (LTV, CAC, NRR, Rule of 40) — https://beancount.io/blog/2026/05/10/saas-metrics-founders-must-track-2026-ltv-cac-nrr-churn-cac-payback-benchmarks-guide

---

## 8. Working With Other Roles

| Role | Handoff / common discussion |
|---|---|
| **Investment Consultant** | "Here's the operating model + cash flows — run the formal NPV/IRR appraisal and capital-allocation decision." Finance consultant owns assumptions; investment consultant owns the appraisal verdict. |
| **Platform Ops / FinOps Engineer** | "Give me tagged, allocated cloud-cost data down to query/product level — I'll build the unit economics on top." They own the cost telemetry + tags; you own the cost-to-value narrative. |
| **Data Analyst** | "Pull me cohort retention, AOV, visit frequency, conversion — I need actuals to anchor the LTV/CAC model and variance." |
| **Business Analyst** | "Quantify the benefit you've scoped — what's the revenue/cost mechanism, and what adoption curve do we assume?" They define value in business terms; you price it. |
| **Data Architect / Engineer** | "What drives the cost — compute, storage, egress, frequency? I need the cost drivers to build the model and to find the savings levers." |
| **CFO / Finance leadership** | "Here's the one-page recommendation, the 2-3 decision-driving numbers, the range, and the key assumption the answer hinges on." |
| **Controller / Accounting** | "Confirm the opex/capex + capitalization treatment so the headline P&L numbers are right." |

---

*Finance is the language of tradeoffs under uncertainty. Be ruthless about the few drivers that matter, honest about the assumptions, and always show a range — never a single number pretending to be a fact.*
