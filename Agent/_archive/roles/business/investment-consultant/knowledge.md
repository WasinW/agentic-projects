# Investment Consultant — Comprehensive Knowledge

> Deep reference for the investment-consultant subagent. Senior investment appraisal / business-case / capital-allocation consultant. Context: The-1 (Central Group retail loyalty) — deciding whether data/AI platform initiatives are worth funding.

---

## 1. Foundations

### What an Investment Consultant does

Decides — with numbers — **whether to spend capital on an initiative, and how much**. Not "is this cool tech," but "does this beat the next-best use of the same money."

- Builds the **business case**: costs, benefits, assumptions, timing, risk.
- Translates an engineering roadmap into **cash flows** the CFO recognizes.
- Ranks competing initiatives under a fixed budget (**capital rationing**).
- Designs **funding structure**: stage-gates, kill-criteria, option value.
- Tracks **benefit realization** after the cheque clears (most orgs skip this — it's where credibility lives).

The deliverable is a **decision + a defensible number**, not a model. A model nobody can poke holes in is a model nobody believes.

### The core question hierarchy

```
1. Should we spend money at all?        → NPV > 0 at hurdle rate
2. Is this the BEST use of the money?   → ranked vs portfolio (capital rationing)
3. How much, and when?                  → staged / option-based funding
4. Did it actually pay off?             → benefit realization tracking
```

Most failed "data ROI" conversations skip straight to #4 with no #1 baseline.

### Adjacent roles

- **Finance / FP&A** — owns the WACC, the hurdle rate, the actuals. You borrow their discount rate; you don't invent one.
- **Enterprise Architect** — owns the roadmap + dependency map; you put a price on each node and sequence by value.
- **Business Analyst** — sources the benefit assumptions (adoption %, conversion lift, hours saved). You stress-test them.
- **Finance-consultant (unit economics)** — owns CAC / LTV / contribution margin; you consume their per-unit numbers as model inputs.
- **Platform Architect** — owns build-vs-buy technical reality; you turn it into TCO + option value.

You are the **bridge between the roadmap and the balance sheet**. Speak both languages or you're useless to either side.

---

## 2. Mental Models / Decision Frameworks

### Time value of money (the one axiom)

฿1 today > ฿1 next year. A future cash flow is worth its **present value**:

```
PV = CF_t / (1 + r)^t
```

Everything else in this file is a corollary of this line. `r` is the discount rate — your opportunity cost of capital.

### NPV — the gold standard

Sum of discounted incremental free cash flows, minus the upfront investment:

```
NPV = Σ [ CF_t / (1 + r)^t ]   for t = 0..N
    = -C0 + CF_1/(1+r) + CF_2/(1+r)^2 + ... + CF_N/(1+r)^N
```

**Rule: invest if NPV > 0.** NPV measures value *created* in today's baht. It's additive across a portfolio and it's the only metric that directly answers "are shareholders better off."

Use **incremental free cash flow vs the do-nothing baseline**, not accounting profit:
- Cash in: incremental revenue, cost savings (as lower outflow), avoided losses.
- Cash out: capex, one-time build cost, incremental opex, working capital, **tax**.
- Ignore sunk costs. Include **opportunity cost** (the engineers could build something else).

### IRR — the percentage everyone asks for

The discount rate where NPV = 0:

```
0 = -C0 + Σ CF_t / (1 + IRR)^t
```

**Rule: invest if IRR > hurdle rate.** Intuitive for execs ("23% return") but has traps:
- **Multiple/no IRR** when cash flows flip sign more than once (common in staged platform spend).
- **Scale-blind** — a 40% IRR on ฿1M can lose to a 15% IRR on ฿100M. NPV wins ties.
- **Reinvestment assumption** — IRR implicitly reinvests at IRR; use **MIRR** if that's unrealistic.

When NPV and IRR disagree on mutually-exclusive projects, **trust NPV**.

### Payback & discounted payback

```
Payback        = years until cumulative (undiscounted) CF ≥ C0
Discounted PB  = years until cumulative DISCOUNTED CF ≥ C0
```

Payback is a **liquidity / risk** screen, not a value metric. It ignores everything after the cutoff and (plain payback) ignores TVM. Use it as a guardrail ("must pay back in <3 yrs") alongside NPV, never instead of it. Typical thresholds: IT infra ~5 yrs, software/data initiatives ~2-3 yrs.

### Hurdle rate / WACC (intro)

The discount rate `r` you plug into NPV. Two common choices:

| Rate | Use |
|---|---|
| **WACC** | Default for projects with company-average risk. Blended cost of debt + equity. |
| **Risk-adjusted hurdle** | WACC + premium for riskier-than-average bets (new AI, unproven adoption). |

```
WACC = (E/V)·Re + (D/V)·Rd·(1 − Tax)
```

Get this from FP&A — don't invent it. For Central Group / Thai corp, a real hurdle is often **10-15%**; speculative AI bets get pushed to **20%+** to reflect execution risk. Higher hurdle = you're demanding the project clear a taller bar.

### Capital budgeting under constraint

Budget is fixed; you can't fund everything NPV-positive. Rank by **bang-per-baht**, not raw NPV:

```
Profitability Index (PI) = PV of future cash flows / Initial investment
```

Fund highest-PI projects until the budget is exhausted. PI > 1 ⟺ NPV > 0. This is the right lens when capital is rationed (it almost always is).

### Risk-adjusted return

Two honest ways to handle risk — **never both at once** (double-counting):
1. **Adjust the cash flows** — probability-weight benefits (expected value), haircut the hockey-stick.
2. **Adjust the discount rate** — bump `r` for risk class.

Prefer adjusting cash flows + running scenarios; reserve rate-bumps for systematic (un-diversifiable) risk.

### Real options thinking

A staged initiative isn't a single bet — it's a **sequence of options**. The right to expand, delay, or abandon has value that NPV-as-a-point-estimate misses.

```
Strategic value = Static NPV + Option value (flexibility)
```

A platform you can build incrementally and kill cheaply is worth more than its naive NPV. This is the core argument for funding a **thin first slice** instead of the whole platform up front (see §6).

### Portfolio prioritization — weighted scoring & RICE/ICE

When cash-flow precision is impossible (early-stage data/AI bets), score and rank:

```
RICE  = (Reach × Impact × Confidence) / Effort
ICE   = (Impact × Confidence × Ease)            ← lighter, faster
```

Or a **weighted scoring model**: strategic fit, revenue upside, risk, cost, time-to-value — each weighted, summed, ranked. Use scoring to **shortlist**, then NPV the finalists. Scoring ranks; NPV justifies the spend.

| Method | When to use |
|---|---|
| NPV / IRR | Cash flows are estimable; need a fund/no-fund decision |
| PI ranking | Capital-rationed portfolio of NPV'd projects |
| RICE / ICE | Many small initiatives, fuzzy benefits, need fast triage |
| Weighted scoring | Strategic bets where intangibles dominate |
| Real options | Staged, high-uncertainty, expand/abandon flexibility exists |

---

## 3. Standard Practices

### Building a business case

A credible case has five parts. Skip any one and a sharp CFO kills it:

1. **Costs** — capex + one-time build + ongoing opex (TCO over the horizon, not just year 1). Include people, cloud, licenses, integration, change management, decommissioning.
2. **Benefits** — incremental, monetized, mapped to a P&L line owned by a named exec. "Better data" is not a benefit; "฿X campaign uplift owned by CMO" is.
3. **Assumptions** — every benefit traces to an explicit, falsifiable assumption (adoption %, lift %, hours saved × loaded rate). Put them in one table.
4. **Sensitivity** — which 2-3 assumptions move NPV most? Tornado chart. If NPV flips on a single soft number, say so.
5. **Scenarios** — base / downside / stress. Base = honest best estimate, not the pitch number.

### Cost-benefit analysis — the benefit ladder

Rank benefits by how defensible they are; lead with the bottom rungs:

| Tier | Type | Defensibility |
|---|---|---|
| 1 | **Hard cost takeout** (headcount, license retirement, cloud savings) | Highest — CFO believes it |
| 2 | **Cost avoidance** (won't need to hire, avoided penalty) | Medium |
| 3 | **Revenue uplift** (conversion, retention, basket size) | Lower — needs attribution |
| 4 | **Strategic / optionality** (faster future projects, data asset) | Lowest — narrative, not number |

The trick for data/AI cases: anchor the NPV on Tier 1-2, treat Tier 3-4 as **upside that makes it a no-brainer**, not as load-bearing.

### Worked mini-example (The-1 flavored)

Personalization platform. Invest **฿20M** upfront (Y0). Hurdle **r = 12%**, 4-year horizon. Incremental free cash flow from retention + campaign uplift, net of opex + tax:

| Year | CF (฿M) | Discount factor 1/(1.12)^t | PV (฿M) |
|---|---|---|---|
| 0 | −20.0 | 1.000 | −20.00 |
| 1 | 6.0 | 0.893 | 5.36 |
| 2 | 9.0 | 0.797 | 7.18 |
| 3 | 11.0 | 0.712 | 7.83 |
| 4 | 12.0 | 0.636 | 7.63 |

```
NPV = −20.00 + 5.36 + 7.18 + 7.83 + 7.63 = +฿8.0M   → FUND
PI  = (5.36+7.18+7.83+7.63) / 20 = 28.0 / 20 = 1.40
IRR ≈ 26%   (NPV = 0 around r ≈ 0.26)  → well above 12% hurdle
Payback (undiscounted): cum CF = -20,-14,-5,+6 → between Y2 and Y3 ≈ 2.5 yrs
```

Verdict: NPV +฿8M, PI 1.40, IRR ~26%, payback ~2.5y — fund it. Now stress it: if uplift lands at 60% of plan, redo the cash flows before celebrating. If NPV stays positive at 60%, it's robust; if it goes negative, the case rests on a number nobody has proven.

### Build vs buy vs partner — the financial lens

| Option | Cost shape | Speed | Owns IP / option value | Best when |
|---|---|---|---|---|
| **Build** | High capex, low marginal | Slow | Yes | Core differentiator; The-1's customer data IS the moat |
| **Buy** (SaaS) | Opex, predictable | Fast | No | Commodity capability; speed > control |
| **Partner** | Shared/variable | Medium | Shared | Need capability + don't want full risk |

Compare on **risk-adjusted TCO over the same horizon**, plus **option value of owning it**. A common error: comparing build capex to buy *year-1* subscription — annualize both over 3-5 yrs. For The-1, the loyalty/customer graph leans **build**; surrounding plumbing (CDP connectors, BI) leans **buy**.

### Valuation basics (when you need an asset value)

- **DCF** — project free cash flows, discount at WACC, add terminal value. Same machinery as NPV; used to value a data product / business unit / the platform as an asset.
- **Multiples** — value = metric × comparable multiple (EV/EBITDA, EV/Revenue, ฿/active-member). Fast sanity-check against the market; weak when no clean comps exist (most data assets).
- **Terminal value** — `TV = CF_(N+1) / (r − g)` (Gordon growth). Dominates long-horizon DCFs; be conservative on `g`.

### Benefit realization tracking

The cheque clearing is the *start*, not the end:
- Define **KPIs + baseline + target + owner** before funding (no baseline = no proof later).
- **Post-implementation review** at 6/12 months: actual vs business-case benefits.
- Feed misses back into the next case's assumptions (calibration beats optimism).
- This is the single biggest credibility lever — orgs that track actuals get their *next* ask approved.

### Stage-gate funding

Don't write one ฿20M cheque; write a **series of small cheques with kill criteria**:

```
Gate 0: Discovery (฿0.5M)   → validated problem + benefit hypothesis
Gate 1: PoC / thin slice    → measured signal on the key assumption
Gate 2: Pilot               → benefit realized in one BU / segment
Gate 3: Scale               → full rollout, only if pilot NPV holds
```

Each gate is an option to continue, kill, or pivot. This is real-options thinking operationalized and it's how you fund uncertain AI bets without betting the farm.

---

## 4. Tools Landscape (2026)

### Modeling
- **Excel / Google Sheets** — still the lingua franca; every CFO can open it. Build NPV/IRR with `=NPV()`, `=XNPV()`, `=IRR()`, `=XIRR()` (use the X-variants for irregular dates).
- **Causal, Pigment, Runway** — modern driver-based modeling; scenario + sensitivity native, far better than spreadsheet sprawl.
- **@RISK / Oracle Crystal Ball** — Monte Carlo add-ins for NPV distributions.
- **Python (numpy-financial, `npf.npv`/`npf.irr`)** — for Monte Carlo + sensitivity at scale; reproducible.

### Business-case templates
- **McKinsey / Deloitte / PwC** value-case templates (cost-benefit + sensitivity + scenarios).
- **Umbrex consultant business-case guide** — practical NPV/IRR/payback + scenario structure.
- Internal **TBM (Technology Business Management)** taxonomy for IT cost allocation.

### Portfolio / IT investment management
- **Apptio (IBM)** — TBM, IT financial management, investment planning; enterprise standard.
- **ServiceNow SPM / Planview / Clarity / Jira Align** — project portfolio management, capacity + value ranking.
- **Productboard / Aha!** — product-side RICE prioritization.

### Benefit tracking / FinOps
- **FinOps tooling** (CloudHealth, Apptio Cloudability) — actual cloud TCO vs business-case assumption.
- **dbt + BI** — instrument the KPIs the business case promised; close the realization loop with real numbers.

---

## 5. Anti-Patterns

| Anti-pattern | Why it's wrong | Better |
|---|---|---|
| NPV on garbage assumptions | Precise math on fictional inputs; "GIGO with decimals" | Stress the inputs first; sensitivity before precision |
| Ignoring opportunity cost | Counts only out-of-pocket; engineers' time is "free" | Cost the next-best use of the same capital + people |
| Sunk-cost reasoning | "We've spent ฿10M, must continue" | Only future cash flows matter; sunk = irrelevant |
| Hockey-stick benefits | Flat for 2 yrs then magic in Y3 to force NPV>0 | Probability-weight; demand evidence for the ramp |
| Hurdle-rate gaming | Lowering `r` until the project clears | Use FP&A's rate; if it fails at hurdle, it fails |
| Double-counting risk | Risk-adjust cash flows AND bump the rate | Pick one risk channel |
| Cherry-picked horizon | Stretch to 7 yrs so benefits accumulate | Match horizon to asset life + tech obsolescence |
| Benefits with no owner | "฿20M uplift" no exec will sign for | Every benefit booked to a named P&L owner |
| Ignoring TCO tail | Capex only; forgets run/maintain/decommission | Full TCO over horizon |
| Build because it's fun | Engineering preference dressed as strategy | Build-vs-buy on risk-adjusted TCO + option value |
| No baseline | Can't prove benefit after the fact | Set baseline + KPI before funding |
| Single point estimate | One number, no range, false confidence | Base/downside/stress + tornado |
| Vanity AI ROI | Funding the model, not the P&L outcome | Tie to a business metric (MIT: ~5% of AI pilots hit real P&L) |

---

## 6. Advanced / Expert Topics

### Real options / staged investment (deep)

Treat each phase as a **call option** on the next. The value of being able to abandon after a cheap PoC is real and quantifiable. Rough framing: a staged plan's value = NPV(committed slice) + value of the option to expand − cost of the option. Black-Scholes-style valuation exists but for most internal cases the discipline matters more than the Greek: **buy information cheaply before committing capital.** Defer irreversible spend until uncertainty resolves.

### Monte Carlo on NPV

Point-estimate NPV hides the distribution. Instead:
1. Make key drivers distributions (adoption ~ triangular(low, base, high); uplift ~ normal).
2. Sample 10k times, compute NPV each run.
3. Report **P(NPV > 0)**, P10/P50/P90, and which input drives variance.

A project with +฿8M expected NPV but **only 55% chance of being positive** is a different decision than one at 90%. CFOs respond well to "85% chance this clears the hurdle."

### Risk-adjusted discount rates

For genuinely riskier project classes (new AI, unproven adoption), add a **risk premium** to WACC — but only for **systematic** risk you can't diversify away. Project-specific risk (will adoption hit?) belongs in the **cash flows** (scenarios / Monte Carlo), not the rate. Mixing them double-penalizes and kills good projects.

### Valuing data & AI assets

No clean market, so triangulate three approaches (Deloitte's framing):
- **Cost approach** — what it cost / would cost to recreate the dataset. Floor value, ignores usefulness.
- **Income approach** — DCF of incremental cash flows the data/model enables (campaigns, retention, monetization). The real number; hardest to defend.
- **Market approach** — comparable data deals / ฿-per-record benchmarks. Sanity bound.

Reality check (2025): firms treating data as a managed asset see **2-3× ROI** on key metrics, *but* MIT found only ~5% of enterprise AI pilots delivered measurable P&L. Lesson: **value the outcome, not the asset's existence.** For The-1, the data asset's value is overwhelmingly the *income approach* — the customer graph's worth = the cash flows it unlocks across Central Group, not its storage cost.

### Platform investment economics — the option value of a platform

A platform's NPV looks ugly as a standalone (high upfront, diffuse benefits). Its real value is **the cheaper, faster initiatives it enables later** — each future use case is an option the platform creates:

```
Platform value = NPV(direct use cases) + Σ option value(future enabled initiatives)
```

Make the argument concrete: name 3-5 future initiatives the platform makes cheaper/faster, estimate the time-to-value and cost reduction per future project, and book *that* as the platform's payoff. A platform funded only on its first use case is almost always NPV-negative and almost always still the right call — because the second through tenth use cases are nearly free. This is the single most important argument an investment consultant makes at The-1.

### TCO vs ROI — different questions

- **TCO** answers "what does owning this cost over its life?" — a denominator. Capex + opex + run + decommission, fully loaded.
- **ROI / NPV** answers "is it worth it?" — needs benefits too.

A low-TCO option can be a terrible investment (cheap but delivers nothing); a high-TCO platform can be the best NPV (expensive but unlocks ฿100M of downstream value). **Never let a TCO comparison stand in for an investment decision** — TCO without the benefit side is half a sentence.

---

## 7. References

### Books
- **Principles of Corporate Finance** — Brealey, Myers, Allen (the bible: TVM, NPV, real options, WACC).
- **Valuation: Measuring and Managing the Value of Companies** — McKinsey / Koller, Goedhart, Wessels.
- **Investment Valuation** — Aswath Damodaran (DCF, multiples; his NYU site + spreadsheets are free gold).
- **The Lean Startup** — Ries (validated learning = real-options thinking for early bets).
- **Competing on Analytics** — Davenport (the data-asset value narrative).

### Sources
- Deloitte — Valuing data assets: https://www.deloitte.com/us/en/insights/topics/digital-transformation/valuing-data-assets.html
- Deloitte — AI and tech investment ROI: https://www.deloitte.com/us/en/insights/topics/digital-transformation/ai-tech-investment-roi.html
- PwC — Decoding ROI from AI: https://www.pwc.com/gx/en/issues/technology/ai-performance.html
- WEF — How CFOs secure ROI from AI: https://www.weforum.org/stories/2025/10/cost-productivity-gains-cfo-ai-investment/
- IBM — Maximize AI ROI in 2026: https://www.ibm.com/think/insights/ai-roi
- Umbrex — Business case financials (NPV/IRR/payback/scenarios): https://umbrex.com/resources/the-busy-consultants-guide-to-writing-business-cases/financials-economics/
- Investment appraisal techniques (NPV/IRR/payback/ARR): https://businesscasestudies.co.uk/investment-appraisal-techniques-npv-irr-payback-period-arr/
- CTG Albany — ROI in IT, a guide for managers: https://www.ctg.albany.edu/media/pubs/pdfs/roi.pdf
- Damodaran Online (valuation data + spreadsheets): https://pages.stern.nyu.edu/~adamodar/

---

## 8. Working With Other Roles

| Role | Handoff / common discussion |
|---|---|
| **Finance-consultant (unit economics)** | "Give me CAC, LTV, contribution margin per member — I'll turn them into the cash flows." Their per-unit numbers ARE my model inputs. |
| **FP&A / Finance** | "What's the official WACC / hurdle? What tax rate?" I borrow the rate, never invent it; they own the actuals for benefit tracking. |
| **Enterprise Architect** | "Here's the roadmap + dependency graph — I'll price each node and sequence by PI / option value." They own sequence logic; I own the value ranking. |
| **Platform Architect** | "Build-vs-buy technical reality + what future use cases does this platform enable?" — feeds TCO + platform option value. |
| **Business Analyst** | "Where does the adoption %, the uplift, the hours-saved come from?" — I stress-test their benefit assumptions into base/downside/stress. |
| **Product / PM** | "RICE-rank the initiative backlog; I'll NPV the finalists." Scoring shortlists, NPV justifies. |
| **Exec sponsor / CFO** | "Here's the decision, the number, and what it rests on." Deliver a fund/no-fund call + the 2 assumptions that would change it. |

---

*Investment appraisal = turning a roadmap into a defensible number. The math is easy; the assumptions are the job. A model nobody can attack is a model nobody believes — lead with the soft numbers, not the decimal places.*
