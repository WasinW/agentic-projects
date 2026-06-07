# Sales Consultant — Comprehensive Knowledge

> Deep reference for the sales-consultant subagent. Senior sales strategy / revenue operations advisor for the business side of data/tech projects. Context: **The-1** — Thailand retail loyalty platform (Central Group), so the lens is retail sales, partner/channel sales, and B2B2C — not pure SaaS quota carrying.

---

## 1. Foundations

### What a Sales Consultant does

Advises leadership on **how revenue gets made, predicted, and grown** — then operationalizes it.
- Go-to-market (GTM) motion design: sales-led, product-led, channel-led, retail-led
- Pipeline + forecasting discipline (the CFO-facing number)
- Sales process + qualification methodology
- RevOps: the systems, data, and incentives that make the team repeatable
- Commercial deal strategy: pricing, packaging, partner economics
- Diagnosis: "where is revenue leaking, and is it a top-of-funnel, conversion, or retention problem?"

The job is not "selling harder." It's making revenue **predictable, efficient, and scalable** — and being honest with the board about the number.

### The revenue engine (mental picture)

```
Demand → Lead → Qualified Opp → Pipeline → Closed-Won → Onboard → Retain → Expand
   ▲                                                                          │
   └──────────────── feedback: which segments retain + expand ───────────────┘
         (Undercurrents: data/CRM hygiene, comp + incentives, enablement, RevOps)
```

A sales consultant works across all of it — not just the part before the signature. In retail/loyalty (The-1), "Closed-Won" is often a **partner signing a co-marketing or data deal**, and "Retain/Expand" is **transaction volume and basket through that partner**.

### Adjacent roles

- **Marketing / demand gen** — fills top-of-funnel; sales converts. The SLA between them is where most revenue dies.
- **Business Analyst** — models the numbers + requirements; consultant decides the commercial strategy.
- **Finance / FP&A** — owns the official forecast and unit economics; consultant supplies the bottoms-up pipeline view.
- **Product** — owns what's sold; sell-through + loss data is the consultant's gift back to them.
- **Customer Success (CS)** — owns retention + expansion (NRR); in modern GTM this *is* part of the revenue engine, not an afterthought.
- **Data / Analytics** — builds the pipeline analytics + propensity models the consultant designs.

---

## 2. Mental Models / Decision Frameworks

### Funnel / pipeline stages (canonical B2B)

| Stage | Definition | Who owns |
|---|---|---|
| **MQL** | Marketing-qualified lead — fits ICP, showed intent | Marketing |
| **SQL / SAL** | Sales-accepted — rep agreed it's worth working | SDR → AE |
| **Opportunity** | Active deal, qualified | AE |
| **Proposal / Negotiation** | Commercials on the table | AE |
| **Closed-Won / Lost** | Signed or dead | AE |

Stages must be **exit-criteria defined** (a verifiable buyer action moves the deal), not feeling-defined. "Customer seems interested" is not a stage gate; "customer agreed to a paid pilot" is.

### Qualification: BANT vs MEDDIC — pick by deal complexity

| | **BANT** | **MEDDIC / MEDDPICC** |
|---|---|---|
| Stands for | Budget, Authority, Need, Timing | Metrics, Economic buyer, Decision criteria, Decision process, Identify pain, Champion (+ Paper process, Competition) |
| Best for | SMB, < ~$50K ACV, cycles < 45 days, high volume | Enterprise, > $50K, 3–12 mo cycles, 5–10 stakeholders |
| Strength | Fast, simple, screen volume | Depth, control, forecast accuracy |
| Weakness | Misses champion + decision process | Heavy; overkill on small deals |

**Opinion:** run the **hybrid** — SDRs use BANT to screen, AEs apply MEDDIC on accepted opps. For The-1 partner deals (multi-stakeholder, long, political inside Central + the partner brand), MEDDIC's *Economic buyer* and *Champion* fields are the two that actually predict the close. ([Salesforce](https://www.salesforce.com/blog/sales/bant-vs-meddic/), [my-outreach](https://www.my-outreach.com/blog/bant-vs-meddic))

### Forecasting methods — run several, compare accuracy

| Method | How | When | Failure mode |
|---|---|---|---|
| **Weighted pipeline** | Σ (deal value × stage probability) | Default for staged B2B pipeline | Probabilities set by optimism not history |
| **Bottoms-up (rep commit)** | Reps call each deal commit/best-case/pipeline | Late-stage, near quarter-end | Sandbagging + happy ears |
| **Run-rate / trend** | Recent close rate × time | Stable, high-volume, transactional | Breaks on seasonality + market shifts |
| **Multivariate / predictive** | Regression / ML on deal signals | Mature data, enough history | Black box; needs continuous re-tuning |
| **Sales-cycle (timing)** | Deals by age vs avg cycle length | Diagnosing stalls | Ignores deal quality |

**The discipline that matters more than the method:** set stage probabilities from **historical conversion data, not the team's gut**. If "Proposal" closes 52% historically, don't let reps weight it at 75% under quarter-end pressure. Review the forecast **weekly** — monthly is too late to fix a stall. Run 2–3 methods in parallel and track which is most accurate over several quarters. ([RevPartners](https://blog.revpartners.io/en/revops-articles/sales-forecasting-methods-high-growth/), [Forecastio](https://forecastio.ai/blog/sales-forecasting-best-practices))

### Sales velocity (the single most useful diagnostic equation)

```
Sales Velocity = (# Opportunities × Avg Deal Value × Win Rate) / Sales Cycle Length
```

It tells you **which of four levers** to pull to grow revenue. Most teams reflexively chase more opportunities (the hardest, most expensive lever). Often **win rate** or **cycle length** is the cheaper win. Always ask: which term is the bottleneck?

### Quota + territory

- **Quota** should be ~3–5× of OTE-driven target coverage; **pipeline coverage** of 3–4× quota is the healthy rule of thumb (lower if win rates are high + predictable).
- **Territory** by geography, segment, vertical, or named-account. Balance *potential* not just headcount — equal account counts with unequal TAM guarantees attrition.
- For The-1: "territory" maps to **partner category** (grocery, fashion, F&B, fuel) — each has different deal size, cycle, and data value.

### Unit economics: CAC, payback, LTV

| Metric | Formula | Healthy (SaaS-ish) |
|---|---|---|
| **CAC** | Fully-loaded S&M spend / new customers | — |
| **CAC payback** | CAC / (new monthly gross-margin revenue) | < 12 mo great, < 18 mo ok |
| **LTV:CAC** | LTV / CAC | > 3:1 |
| **Magic number** | Net-new ARR / prior-Q S&M | > 0.75 |

CAC rose ~14% in 2025, which is *why* expansion revenue (selling more to existing accounts) is now the most efficient growth path. ([Optifai](https://optif.ai/learn/questions/b2b-saas-net-revenue-retention-benchmark/))

### B2B vs B2C vs B2B2C / retail — the motion is fundamentally different

| | **B2B** | **B2C** | **B2B2C / Retail (The-1)** |
|---|---|---|---|
| Buyer | Committee | Individual | Partner brand buys; end-consumer transacts |
| Cycle | Weeks–months | Seconds–days | Long partner deal + ongoing consumer flow |
| Deal value | High, few | Low, many | Partner contract + per-transaction economics |
| Forecast unit | Opportunities | Cohorts + conversion | Partner pipeline **and** sell-through volume |
| Growth lever | Win rate, ACV | Conversion, AOV, retention | Partner acquisition **×** member engagement |
| Key metric | Pipeline coverage | LTV, repeat rate | Active members, redemption, partner sell-through |

**The-1 specific:** you sell a deal to the *partner* (B2B motion — use MEDDIC), but the value realized is *consumer behavior* through that partner (B2C analytics — sell-through, basket, redemption). A consultant here must speak **both** languages and connect partner-deal pipeline to downstream member transaction lift, because that lift is the renewal/expansion argument.

---

## 3. Standard Practices

### Pipeline management

- **Stage hygiene** — every open opp has a next step + a future close date. Deals with a close date in the past are the #1 forecast poison.
- **Pipeline coverage** tracked weekly per rep + per segment (target 3–4× quota).
- **Stage conversion rates** measured per stage — that's where you find the leak.
- **Aging / stalled deals** — flag opps past 1.5× average cycle; they're usually dead, not slow.
- **Pipeline reviews** — weekly deal inspection, not a status read-out; AE must defend why each commit deal closes.

### Forecasting cadence

- Weekly forecast call: commit / best-case / pipeline, roll up rep → manager → VP.
- Track **forecast accuracy** as its own KPI (was the call within ±X%?). A consistently-low caller and a sandbagger are both problems.
- Quarter-end "happy ears" is the predictable failure — discount rep optimism with historical stage probabilities.

### RevOps (the operational backbone)

The function that unifies the **systems, data, process, and enablement** across marketing, sales, and CS so the revenue engine runs on one source of truth.
- One funnel definition, one set of stage exit criteria, one ICP — shared across teams.
- Clean attribution + reporting so the forecast is trustworthy.
- 2026 RevOps is increasingly **AI-augmented**: auto-CRM-entry, deal-risk scoring, forecast assist. ([Salesmotion](https://salesmotion.io/blog/revops-best-practices), [thesmarketers](https://thesmarketers.com/blogs/revops-b2b-2026/))

### CRM hygiene

- **Garbage in = garbage forecast.** CRM data quality is the foundation of every downstream model.
- Mandate: every stage change requires updated fields (MEDDIC fields, next step, amount).
- Automate entry where possible (conversation-intelligence auto-logging) — reps hate manual entry and it's where data rots.
- Dedup + enrich accounts continuously; stale contacts kill outbound.

### Lead scoring

- **Fit (ICP match)** × **Intent (behavioral signal)** = priority.
- Start rules-based (firmographics + key actions), graduate to model-based once you have enough closed-won/lost history.
- Score must drive **routing + prioritization**, not just sit in a field. A score nobody acts on is theater.

### Sales–Marketing SLA

The contract that stops the "leads are bad" / "sales doesn't follow up" blame loop:
- Marketing commits a **volume + quality** of MQLs; Sales commits **follow-up speed + feedback**.
- Shared definition of MQL/SQL and a closed-loop feedback so marketing learns which leads actually convert.
- Measured: MQL→SQL conversion, speed-to-lead, % MQLs worked.

### Channel / partner sales

- **Recruit → enable → manage → grow** the partner lifecycle.
- Partner economics: margin/rev-share, MDF (market development funds), incentive tiers tied to *sell-through*, not just sell-in.
- Capture **partner sales data** to set growth goals + reward tiers — this is also the analytics asset. ([Lift & Shift](https://www.lift-and-shift.com/b2b-loyalty-programs/channel-partner-rewards-programs), [Martal](https://martal.ca/channel-sales-lb/))
- For The-1: partners are both **customers** (they pay/commit) and **distribution** (members transact through them). Tier partners by data value + transaction volume, not just contract size.

### Sales comp basics

- **OTE = base + variable**; variable split should track what you want behavior on (logos vs ARR vs expansion).
- Keep it **simple** — a plan reps can't compute in their head doesn't change behavior.
- Accelerators above quota, decelerators/clawbacks for churn-in-X-months.
- Comp the **whole engine**: if expansion matters, comp CS/AMs on it, not just new-logo AEs.

### Conversion optimization

- Find the worst-converting stage first (biggest leak), fix that, re-measure.
- Win/loss analysis on a regular cadence — ask buyers, not just reps.
- Speed-to-lead is one of the highest-ROI fixes that nobody prioritizes.

---

## 4. Tools Landscape (2026)

> Major 2026 shift: **Salesloft completed its merger with Clari (Dec 2025)** (~$450M ARR combined), so engagement + revenue-intelligence + forecasting now converge in one platform — directly challenging Gong's RI position. Both Gong and Outreach adopted **Model Context Protocol (MCP)** in Feb 2026 so AI tools share context without custom integrations. 2026 stacks emphasize **autonomous execution + predictive intelligence** over basic automation. ([Maxiq](https://www.getmaxiq.com/blog/clari-salesloft-merger-guide), [Mutiny](https://www.mutinyhq.com/blog/the-best-ai-sales-tools-in-2026-a-buyer-s-guide-for-b2b-gtm-teams))

### CRM (system of record)
- **Salesforce** — enterprise standard; Einstein AI native; infinitely customizable (and complex)
- **HubSpot** — SMB/mid-market; faster to deploy; Breeze AI; strong all-in-one with marketing
- **Microsoft Dynamics** — if you're a Microsoft shop

### Sales engagement (sequencing + outbound)
- **Outreach** — enterprise engagement leader
- **Salesloft** — now merged with Clari; engagement + forecasting in one
- **Apollo** — data + engagement combined, strong mid-market value

### RevOps / revenue intelligence / forecasting
- **Gong** — conversation intelligence leader; deal + forecast intelligence from call data
- **Clari** (now Salesloft) — forecasting + pipeline inspection pedigree
- **Chorus** (ZoomInfo) — conversation intelligence alternative

### Enablement + content
- **Highspot**, **Seismic** — content management, training, sell-through enablement

### Account intelligence / intent (named-account motions)
- **6sense** — intent + predictive; **Mutiny** — account personalization

### CPQ (configure-price-quote)
- **Salesforce CPQ / Revenue Cloud**, **DealHub**, **Conga** — for complex pricing/quoting/contracting

### Loyalty / B2B2C (The-1 relevant)
- **Loyalty platforms**: Zinrelo (B2C/B2B/B2B2C flexible), Brierley, Wildfire (white-label rewards + retail media monetization)
- These matter because The-1's "product" *is* the loyalty + data layer — partner sales pitch is built on this platform's analytics + member reach. ([Aziro](https://medium.com/@AziroTech/top-10-leading-customer-loyalty-platforms-in-2026-12bad96692ae), [Brierley](https://www.brierley.com/blog/best-customer-rewards-platforms))

**Stack rule of thumb:** most B2B teams run **4–6 tools**, chosen by *which part of the funnel actually leaks*. Don't buy the full stack on day one — buy against your measured bottleneck.

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Feeling-based pipeline stages | Forecast is fiction | Exit-criteria stages tied to verifiable buyer actions |
| Stage probabilities set by optimism | Quarter-end happy-ears miss | Set from historical conversion data; review weekly |
| Forecasting once a month | Too late to fix a stall | Weekly forecast + deal inspection |
| Chasing more leads to fix revenue | Most expensive lever | Use sales-velocity equation; often win-rate/cycle is cheaper |
| MEDDIC on every $5K deal | Process overhead kills volume | BANT for screen, MEDDIC for complex opps |
| CRM as a graveyard | Garbage in → garbage forecast | Mandate field updates per stage; automate entry |
| Comp plan reps can't compute | Doesn't change behavior | Simple plan tied to 1–2 priority behaviors |
| New-logo obsession, ignore retention | NRR leaks out the back; CAC wasted | Comp + measure expansion/retention as revenue |
| Sales–marketing blame loop | Leads "bad" / no follow-up | Two-way SLA + closed-loop feedback on conversions |
| Sandbagging / hero-balling tolerated | Forecast unreliable both ways | Track forecast-accuracy per rep as a KPI |
| Partner sell-**in** mistaken for sell-**through** | Inventory/contracts ≠ revenue | Incentivize + measure actual end-consumer sell-through |
| One forecasting method, trusted blindly | No way to know if it's wrong | Run 2–3 methods, track accuracy over quarters |
| Buying the full salestech stack upfront | Spend without fixing the leak | Buy against measured funnel bottleneck |

---

## 6. Advanced / Expert Topics

### Predictive forecasting

Move beyond weighted-pipeline to **multivariate regression / ML** on deal-level signals (engagement, stage velocity, contact seniority, email sentiment from conversation intelligence). It's *not* set-and-forget — assumptions + algorithms need continuous re-tuning as the business evolves. Always benchmark the model against the simple weighted forecast; if it's not beating it, it's complexity for its own sake. ([RevenueOps](https://www.revenueopsllc.com/forecasting-models-every-revops-team-should-know/), [Forecastio](https://forecastio.ai/blog/pipeline-forecasting))

### Propensity-to-buy / propensity-to-expand

- Score accounts on **likelihood to convert (acquisition)** and **likelihood to expand (existing)**.
- Needs: enough labeled history (won/lost, expanded/churned) + clean features.
- The expand model is often higher ROI than the acquire model — cheaper to act on, given rising CAC.
- For The-1: propensity to **redeem / increase basket** per member segment is the analog — feeds both partner pitches and member targeting.

### Churn + expansion: NRR is the modern north star

```
NRR = (Starting ARR + Expansion − Contraction − Churn) / Starting ARR
```

2025–26 benchmarks (private B2B SaaS — directional, segment matters enormously):
- **Median ~106%**; Enterprise (>$100K ACV) ~118%, Mid-market ~108%, SMB (<$25K) ~97%; top quartile > 130%.
- Expansion ARR grew from ~25% of new ARR (2022) to ~40% (2024), reaching 58–67% above $50M ARR.
- Public SaaS > 120% NRR trade at ~9.3x EV/revenue vs ~3.1x below 100% — **NRR is a valuation multiplier, not just an ops metric.**
- Typical churn ~3.5% (2.6% voluntary / 0.8% involuntary). ([Optifai](https://optif.ai/learn/questions/b2b-saas-net-revenue-retention-benchmark/), [DigitalApplied](https://www.digitalapplied.com/blog/net-revenue-retention-benchmarks-2026-saas-expansion-data))

**The-1 translation:** NRR ≈ are partners renewing + spending more (deeper data deals, more campaigns), and are members transacting more over time. Same math, retail substrate.

### Pipeline analytics (what good looks like)

- **Cohort the pipeline** — by source, segment, rep, quarter-created. Aggregate close rates lie.
- **Conversion waterfall** per stage to localize the leak.
- **Created-vs-closed** + **pipeline aging** to catch top-of-funnel droughts early.
- **Forecast accuracy trend** as a first-class dashboard.
- **Win/loss reason coding** — structured, queryable, fed back to product + marketing.

### Sales-data feedback loops to product

Loss reasons, competitive-loss patterns, and feature-gap objections are **structured product input**. The consultant's job is to make these queryable (not buried in CRM free-text) and route them to product on a cadence. Closed-lost is a dataset, not a graveyard.

### Retail sell-through analytics (The-1 core)

- **Sell-in vs sell-through** — sell-in is what the partner committed; **sell-through is what consumers actually bought**. Only sell-through is real, repeatable revenue. Comp + renewals must hang on sell-through.
- **Basket / AOV, redemption rate, repeat rate, member frequency** per partner per category — these are the renewal + upsell argument to the partner.
- **Attribution**: connect a partner campaign/deal to downstream member transaction lift. This closes the loop that justifies the next, bigger partner deal.
- AI in distributed/channel sales models can lift sales by up to ~20% — relevant to how The-1 equips partner-facing teams. ([BCG](https://www.bcg.com/publications/2026/how-ai-can-reshape-sales-channels-in-emerging-markets), [Martal](https://martal.ca/channel-sales-lb/))

### Deal desk / commercial strategy

For complex partner deals: standardize discounting guardrails, approval thresholds, and packaging so reps don't give away margin to close. CPQ enforces this; absent CPQ, a lightweight deal-desk approval still beats free-for-all discounting.

---

## 7. References

### Books
- **Predictable Revenue** — Aaron Ross (the SDR/outbound + specialized-roles bible)
- **SPIN Selling** — Neil Rackham (question-led consultative selling; research-backed)
- **The Challenger Sale** — Dixon & Adamson (teach-tailor-take-control)
- **The Qualified Sales Leader** — John McMahon (MEDDPICC + forecasting discipline)
- **From Impossible to Inevitable** — Ross & Lemkin (scaling the revenue engine)
- **Cracking the Sales Management Code** — Jordan & Vazzana (managing the right metrics)
- **The Sales Acceleration Formula** — Mark Roberge (data-driven sales building)

### Blogs / sources
- **Pavilion** (community + content for revenue leaders)
- **SaaStr** — Jason Lemkin on SaaS GTM + metrics
- **Gong Labs** — data-backed sales research
- **Forecastio**, **RevPartners**, **Salesmotion** — RevOps + forecasting practice (2026)
- **Salesforce / HubSpot blogs** — methodology + CRM practice
- **Winning by Design** — SaaS sales process + math (bowtie model)
- **McKinsey / BCG B2B sales** — strategy + AI-in-channel research

### Communities
- **Pavilion**, **RevGenius**, **Modern Sales Pros**, **Wizards of Ops** (RevOps)

---

## 8. Working With Other Roles

| Role | Handoff / common discussion |
|---|---|
| **Data Analyst** | "Build the pipeline conversion waterfall, cohorted by source/segment; track forecast accuracy." Consultant defines the metrics + stage logic; analyst builds the views. |
| **ML Engineer** | "Here's labeled won/lost + churn/expansion history — build propensity-to-buy + propensity-to-expand scoring. Benchmark against weighted forecast." Consultant frames the target + features. |
| **Marketing Consultant** | "Here's the MQL→SQL conversion + which sources actually close — let's set the SLA and reallocate demand spend." Closed-loop feedback both directions. |
| **Finance Consultant** | "Here's the bottoms-up pipeline forecast + CAC/payback/NRR; reconcile with the top-down plan." Consultant supplies the pipeline view; finance owns the official number. |
| **Product** | "Here are coded loss reasons + competitive gaps from the field." Sales-data feedback loop. |
| **Data Engineer** | "CRM + transaction + partner data need to land clean in the warehouse for this analytics to be trustworthy." Garbage in → garbage forecast. |
| **Customer Success** | "Retention + expansion are revenue — let's instrument NRR and comp on it." |

---

*Good sales consulting = making revenue predictable, efficient, and honest. The forecast you can defend to the board beats the forecast that makes everyone feel good.*
