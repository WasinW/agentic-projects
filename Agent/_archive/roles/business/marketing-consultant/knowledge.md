# Marketing Consultant — Comprehensive Knowledge

> Deep reference for the marketing-consultant subagent. Senior CRM/loyalty strategy lens, biased toward retail + customer data. Default context: **The-1** (Central Group, Thailand's largest loyalty platform).

---

## 1. Foundations

### What a Marketing Consultant does

Advises on the **business side** of data/tech projects: turning customer data into revenue, retention, and lifetime value. Not a campaign operator — a strategist who connects data capability to commercial outcome.
- Segmentation + targeting strategy
- Loyalty program design + economics
- Lifecycle / CRM marketing (acquisition → retention → win-back)
- Measurement: attribution, incrementality, marketing ROI
- Translating "we have a CDP / a churn model" into "here's the campaign and the P&L impact"

The job is to make sure the data team builds things that move a business metric, not a vanity metric.

### The lens: every initiative maps to one of four levers

```
Revenue = Customers × Frequency × Basket × Margin
            ↑           ↑          ↑         ↑
        acquisition  retention  cross/up   mix/promo
                     + loyalty    -sell    discipline
```

If a proposed model/pipeline/campaign doesn't move one of these four, push back.

### Adjacent roles

- **Business Analyst** — scopes requirements + process; marketing consultant owns the *commercial* hypothesis behind them
- **Data Analyst** — runs the numbers; consultant frames the question + interprets for the business
- **Sales** — owns the deal/transaction; marketing owns demand + the relationship before and after
- **Brand / Creative** — owns message + positioning; consultant owns who-gets-what-when (targeting + lifecycle)
- **Product** — owns the in-app experience; heavy overlap on loyalty mechanics + personalization
- **ML Engineer** — builds propensity/CLV/uplift models the consultant specifies and consumes

---

## 2. Mental Models / Decision Frameworks

### STP — the spine of any strategy

**Segmentation → Targeting → Positioning.** Segment the base, choose which segments to serve, position the offer for each. Most "personalization" projects fail because they skip straight to messaging without doing STP first.

### Segmentation approaches

| Approach | Basis | Best for |
|---|---|---|
| **RFM** | Recency, Frequency, Monetary | Retail/loyalty default; cheap, explainable, actionable |
| **Behavioral** | Actions: browse, redeem, channel | Lifecycle triggers, journey design |
| **Demographic / firmographic** | Age, geo, life stage | Brand + media targeting; weak alone |
| **Needs / attitudinal** | Survey, zero-party | Positioning, proposition design |
| **Value-based (CLV tiers)** | Predicted lifetime value | Budget allocation, VIP treatment |
| **ML clustering** | Unsupervised on features | Discovery; *must* be made interpretable before use |

**Opinion:** start with RFM. It explains 80% of what fancy clustering finds, the business already understands it, and it's directly actionable. Graduate to CLV-tiered + behavioral once RFM is operationalized. For The-1, RFM on transaction + redemption data is the obvious first cut.

### RFM in practice

Score each customer 1–5 on R, F, M (quintiles). Named cells that matter:
- **Champions** (555) — protect, reward, advocacy
- **Loyal** (high F) — upsell, tier progression
- **At-risk** (was high, R dropping) — win-back trigger; highest-ROI intervention
- **Hibernating / lost** (low R, low F) — cheap reactivation only; don't overspend
- **New** (high R, low F) — onboarding to second purchase (the critical conversion)

### CLV / LTV models

| Model | When | Note |
|---|---|---|
| **Historic CLV** | Reporting baseline | Backward-looking; undervalues new customers |
| **Predictive CLV (BG/NBD + Gamma-Gamma)** | Non-contractual retail (The-1 fits) | Models repeat-purchase + spend separately; the standard |
| **ML CLV (GBM/DL on features)** | Rich feature set, scale | Better accuracy, less interpretable; needs ML eng |
| **Cohort-based** | Subscription/contractual | Retention curves × ARPU |

CLV gates the whole economics: **allowable acquisition cost (CAC) ≤ CLV-margin**, and it sets how much you can spend to retain. If marketing can't state CLV by segment, it's flying blind.

### Funnel / AARRR (pirate metrics)

**Acquisition → Activation → Retention → Revenue → Referral.** Diagnose where the base leaks. In mature loyalty businesses the binding constraint is almost always **Retention + Revenue (frequency)**, not Acquisition — yet most spend goes to the top. Reallocating is usually the single biggest win a consultant delivers.

### Retention vs Acquisition economics

- Acquiring a new customer costs **5–7×** retaining one (directional, well-worn but true).
- A **5% retention lift → 25–95% profit lift** (Reichheld) — because retained customers buy more, cost less to serve, and refer.
- **Implication:** in a loyalty business, retention/frequency programs almost always beat broad acquisition on ROI. But don't over-rotate — a leaky bucket with no top-of-funnel eventually starves.

### Attribution models — and why they're dying

| Model | Logic | Verdict |
|---|---|---|
| **First-touch** | 100% to first interaction | Biases to awareness; rarely useful alone |
| **Last-touch** | 100% to last | Default in GA but badly overcredits bottom-funnel/brand search |
| **Linear / time-decay / position** | Spread credit | Arbitrary rules dressed as insight |
| **Data-driven (DDA, Shapley/Markov)** | Algorithmic credit | Best of the user-level family, but… |
| **Incrementality / geo-experiment** | Causal: holdout vs treated | **The real answer.** Measures lift, not correlation |
| **MMM** | Regression on aggregate spend → outcome | Privacy-safe, channel-level; resurgent (see §6) |

**Opinion (2026):** user-level multi-touch attribution is structurally broken — signal loss, walled gardens, cross-device gaps. The credible stack is **MMM (strategic budget) + incrementality experiments (validate channels) + DDA (in-platform tactical)**, triangulated. Anyone selling deterministic last-touch dashboards as "truth" is selling a comfort blanket.

---

## 3. Standard Practices

### Campaign design checklist

1. **Objective** — tied to a lever (§1), with a target metric + baseline
2. **Audience** — segment definition + size + exclusions (suppression lists!)
3. **Offer** — value, mechanic, margin impact modeled *before* launch
4. **Channel + timing** — where the segment actually is; frequency caps
5. **Control group** — a holdout, always (see A/B + incrementality)
6. **Measurement plan** — defined before launch, not reverse-engineered after
7. **Consent check** — is this audience opted-in for this channel? (PDPA, §3)

### A/B testing + experimentation

- **Randomize at the unit you're treating** (usually customer), keep a clean **holdout** even on "obvious winner" campaigns — it's the only way to claim incremental lift vs. people who'd have bought anyway.
- **Power the test**: minimum detectable effect → sample size *before* launch. Underpowered tests are how teams "learn" noise.
- **One variable per test** for clean reads; use multivariate only with scale.
- **Stat significance ≠ business significance** — a 0.3% lift that's significant at n=2M may not pay for the effort.
- **Beware peeking** — fixed horizon or sequential testing, not "stop when green."

### Personalization

Maturity ladder: **segment-based → rule-based triggers → 1:1 model-driven (NBA) → real-time contextual.** Don't sell rung 4 to a client on rung 1. Most retailers capture the majority of value at rung 2–3. Personalization needs (a) identity resolution, (b) a content/offer library, (c) a decisioning layer, (d) a channel to deliver. Missing any one = no personalization.

### Loyalty program mechanics

| Mechanic | Drives | Watch-out |
|---|---|---|
| **Points (earn/burn)** | Frequency, data capture | Liability on balance sheet; breakage assumptions |
| **Tiers** | Aspiration, retention of top spenders | Tier inflation; clear, attainable thresholds |
| **Gamification** (streaks, challenges, badges) | Engagement, habit | Novelty decay; must tie to real value |
| **Experiential / partner rewards** | Differentiation, emotional loyalty | Partner economics + ops complexity |
| **Paid loyalty** (e.g. Amazon Prime model) | Committed, high-LTV members | Only works with strong value stack |

**Economics that must be modeled:** earn rate (cost %), redemption/breakage rate, point liability, incremental margin from increased frequency. A program is healthy when **incremental margin > program cost + liability accrual**. 2026 consensus: points programs endure (flexible, gamifiable, AI-personalizable redemptions); 45% of brands investing in gamification; ~87% of gamified programs out-retain non-gamified. The-1's scale makes breakage + liability modeling the single most important finance conversation.

### Churn / retention

- **Define churn first** — in non-contractual retail there's no cancellation event; use a lapse definition (e.g. no purchase in N×median-interpurchase-time) or a predicted-active probability (BG/NBD).
- **Predict, then act, then measure** — a churn score is worthless without a tied intervention and a holdout to prove the intervention worked.
- **Target the persuadable, not the doomed** — this is why uplift > propensity for retention (§6).

### Consent + PDPA in marketing (Thailand)

- **Consent must be explicit, granular, logged, and revocable** — separate consents per purpose + channel; pre-ticked boxes are invalid.
- **Right to object to direct marketing** is absolute — honor opt-outs across all channels; maintain suppression lists as a first-class data asset.
- **Direct marketing registration** (OCPB, Direct Sales/Marketing Act) + a forthcoming **national Do-Not-Call list** (PDPC) — outbound calling carries extra obligations.
- **Grace period is over** — PDPC issued its first major fines (>THB 21.5M) in Aug 2025. Treat consent as a hard gate, not a checkbox.
- **Lawful basis** — consent is the safe default for marketing; "legitimate interest" is narrower in TH than GDPR practice — don't lean on it for cold outreach.

### Marketing KPIs (the ones that matter)

| Stage | KPI |
|---|---|
| Acquisition | CAC, CAC payback period, CAC:CLV ratio (target ≥ 3:1) |
| Activation | Onboarding/2nd-purchase conversion, time-to-second-purchase |
| Engagement | Active rate, redemption rate, channel engagement |
| Retention | Repeat rate, churn/lapse rate, retention curve by cohort |
| Monetization | AOV/basket, purchase frequency, share of wallet |
| Value | CLV, CLV by segment, point liability, margin per member |
| Efficiency | ROAS, **iROAS (incremental)**, marketing contribution margin |

**Opinion:** if a client reports ROAS but not **incremental** ROAS, they're likely overcrediting marketing for organic demand. Push every headline metric toward its incremental version.

---

## 4. Tools Landscape (2026)

### CDP (Customer Data Platform)
The unification + activation layer. Three architectures:
- **Packaged / pure-play** — **Twilio Segment** (700+ connectors, market default), **mParticle** (mobile-first, acquired 2025, moving warehouse-ward), **Tealium** (1,300+ integrations, AudienceStream), **Treasure Data** (enterprise, APAC strong)
- **Suite-embedded** — **Salesforce Data Cloud**, **Adobe Real-Time CDP** — pick if already deep in that suite
- **Composable / warehouse-native** — **RudderStack** (open-source, cost-effective), **Hightouch** + **Census** (reverse-ETL CDPs on top of BigQuery/Snowflake)

**Opinion:** for a data-mature org that already owns a warehouse/lakehouse (The-1's posture), **composable CDP** (warehouse as source of truth + Hightouch/Census activation) avoids duplicating the customer 360 inside a black-box SaaS and avoids vendor lock-in. Packaged CDP wins when you lack data engineering muscle and need speed. Don't buy a CDP until identity resolution across ≥ several tools is genuinely painful.

### CRM
- **Salesforce**, **HubSpot**, **Microsoft Dynamics** — system of record for the customer relationship. CRM ≠ CDP: CRM is operational + sales-led, CDP is analytical + behavioral. Most enterprises run both.

### Campaign / Marketing Automation (MA)
- **Braze** — best-in-class omnichannel real-time engagement (push, in-app, email, web); retail/fintech/streaming strength
- **Salesforce Marketing Cloud** — enterprise journeys, deep SF integration
- **HubSpot** — default for SMB/mid-market B2B, all-in-one
- **Klaviyo** — e-commerce/Shopify default, deep catalog + flows
- **Iterable, MoEngage, Insider, Bloomreach** — strong omnichannel challengers; **MoEngage/Insider** notably strong in APAC
- **2026 reality:** agentic AI (message-level personalization, autonomous journey optimization, MCP support) is now table-stakes on enterprise tiers, not a differentiator. Choose on **data/CRM integration architecture + channel fit**, not the AI feature list.

### Analytics
- **GA4** — web/app analytics default (event-based; the only GA now)
- **Amplitude / Mixpanel** — product + behavioral analytics, funnels, retention
- **Looker / Power BI / Tableau** — BI on top of the warehouse for marketing reporting

### Attribution + Measurement
- **MMM:** Google **Meridian** (replaced LightweightMMM, Jan 2025; added non-media vars, geo via **GeoX**), Meta **Robyn** (open-source, ridge + Nevergrad), **Recast**, **Mutiny/Haus** (geo-incrementality)
- **Incrementality:** **Haus**, **Rockerbox**, in-platform conversion-lift (Meta/Google geo holdouts)
- **In-platform DDA** for tactical optimization only

### Personalization / Decisioning
- Native MA personalization (Braze/Klaviyo AI), **Dynamic Yield**, **Insider**, plus warehouse-native NBA via reverse-ETL (Hightouch's NBA pattern)

### Privacy / Consent
- **OneTrust**, **Cookiebot/Usercentrics**, **Cookie Information** — CMP + consent ledger; non-negotiable for PDPA/GDPR

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Spray-and-pray blasts | Fatigue, opt-outs, brand erosion | Segmented + triggered with frequency caps |
| No holdout / control group | Can't prove incrementality; credits organic | Always keep a holdout, even on "winners" |
| Last-touch attribution as truth | Overcredits bottom-funnel + brand search | MMM + incrementality + DDA triangulated |
| Optimizing for opens/clicks | Vanity; doesn't equal revenue | Optimize to downstream conversion + margin |
| Discount as default lever | Trains discount-seeking, kills margin | Value/relevance first; discount last + targeted |
| Targeting the doomed (high churn score) | Wastes spend on un-saveable + un-needers | Uplift model → target the *persuadable* |
| Buying a CDP to "have data strategy" | Tool ≠ strategy; shelfware | Define use cases + STP first, then tool |
| Ignoring point liability / breakage | Balance-sheet surprise; unsustainable program | Model earn/burn/breakage in finance from day 1 |
| Personalization without identity resolution | "1:1" on fragmented profiles = wrong 1 | Fix identity graph before promising personalization |
| Treating consent as a checkbox | PDPA fines now real (THB 21.5M+) | Granular, logged, per-purpose consent as hard gate |
| CAC measured without CLV | Can't tell good acquisition from bad | Gate spend on CAC:CLV ≥ 3:1 by segment |
| One-size lifecycle for all segments | New ≠ loyal ≠ at-risk | Differentiated journeys per RFM/value tier |
| Vanity NPS with no closed loop | Score theater | Tie detractor follow-up to action + retention |

---

## 6. Advanced / Expert Topics

### Marketing Mix Modeling (MMM)

Aggregate regression of outcome (sales) on spend by channel + controls (price, promo, seasonality, macro). Decomposes contribution + estimates **diminishing returns (saturation)** and **adstock (carryover)** per channel → optimal budget allocation.
- **Why resurgent (2026):** privacy-safe (no user-level data), works in walled-garden + cookieless world, board-level explainability.
- **Stack:** Google **Meridian** (Bayesian, now with non-media vars + geo), Meta **Robyn** (frequentist, ridge + evolutionary tuning), **Recast** (continuous/commercial).
- **Gotchas:** correlated spend (multicollinearity), needs 2–3 yrs of weekly data, can't do tactical/creative decisions. **Calibrate MMM priors with incrementality experiments** — that's the modern best practice.

### Uplift / incrementality modeling

Models **treatment effect**, not outcome probability. Splits the base into:
- **Persuadables** — convert *only if* treated → the ROI
- **Sure things** — convert anyway → wasted incentive
- **Lost causes** — won't convert regardless → wasted spend
- **Do-not-disturbs** (sleeping dogs) — treatment *hurts* → actively avoid

**This is the single highest-leverage modeling idea in retention marketing.** A propensity-to-churn model tells you who *will* churn; an uplift model tells you who you can *save with this action* — a different, smaller, more profitable list. Methods: two-model (T-learner), class-transformation, uplift trees, causal forests. Requires experimental (randomized) training data — design the experiment first.

### Propensity models

Supervised P(event): purchase, churn, upgrade, redeem. The workhorse for scoring the base. Pipeline: features (RFM + behavioral + recency) → GBM (XGBoost/LightGBM) → calibrated probability → thresholded into action. **Always pair a propensity score with an intervention + a holdout** — a score nobody acts on is a dashboard. Hand spec to ML eng; consultant owns label definition + business thresholds.

### Next-Best-Action (NBA)

Decisioning layer that, per customer per moment, picks the single best action across a catalog of offers/messages/channels. Best version = **uplift per action**, then choose argmax expected incremental value (often net of cost). Real-time NBA needs a decisioning engine + feature store + channel delivery. Most orgs start with **batch NBA via reverse-ETL** from the warehouse to the MA tool — far cheaper, captures most value. Don't promise real-time until batch is operational and proven.

### Real-time personalization

Triggered on live behavior (browse, cart, geo, in-app event) within seconds. Requires streaming events → real-time profile → decisioning → delivery. High value for high-frequency/high-intent moments (cart abandon, in-store app). Expensive + operationally heavy — justify with the specific moments, not "be real-time" as a goal.

### Privacy-first / cookieless marketing

Despite Google **keeping** third-party cookies in Chrome (U-turn Jul 2024, confirmed Apr 2025 with a user-choice model), **cookieless is the operating standard in 2026** — signal loss is structural (Safari/Firefox ITP, app ATT, regulation, walled gardens). Four pillars:
1. **First-party data** — your own transaction/behavioral data; the durable moat (loyalty programs are *built* for this — The-1's structural advantage)
2. **Zero-party data** — what customers volunteer (preferences, intent via quizzes/profiles); consent-clean + high-signal
3. **Contextual targeting** — content/context not identity
4. **Privacy-preserving measurement** — MMM, geo-experiments, clean rooms (Google Ads Data Hub, Amazon Marketing Cloud), Privacy Sandbox APIs (low adoption, ~32% of buyers)

### Loyalty economics (deep)

The P&L of a points program:
- **Point liability** = outstanding points × redemption value × expected redemption rate. A balance-sheet item; actuarial.
- **Breakage** = points that expire unredeemed → margin, but over-engineering breakage damages trust + perceived value.
- **Cost of program** = earn cost + redemption cost + ops + tech.
- **Incremental margin** = margin from behavior change (↑frequency, ↑basket, retention) attributable to the program — **must be measured against a non-member/holdout baseline**, not assumed.
- **Healthy program:** incremental margin > total program cost + liability accrual. **Most loyalty ROI claims fail because they count all member spend as "driven by" the program** — the classic selection-bias trap. The consultant's job is to insist on the incremental cut.
- **Tier design:** thresholds attainable enough to motivate, scarce enough to mean something; model migration between tiers + the cost of the top-tier benefit stack.

### Marketing P&L / budget allocation

Move from "how much did we spend" to **marginal ROI per channel** (from MMM saturation curves) → reallocate to equalize marginal returns. The board question is always "what's the next dollar's best home" — MMM + incrementality answer it; attribution dashboards don't.

---

## 7. References

### Books
- **Marketing Management** — Kotler & Keller (the canon)
- **This Is Marketing** — Seth Godin (positioning + permission)
- **The Loyalty Effect / The Ultimate Question (NPS)** — Fred Reichheld (retention economics)
- **Customer Centricity** + **The Customer-Base Audit** — Peter Fader / Bruce Hardie (CLV, BG/NBD — essential for non-contractual retail)
- **How Brands Grow** — Byron Sharp (mental/physical availability, penetration vs loyalty — the contrarian counterweight)
- **Lean Analytics** — Croll & Yoskovitz (AARRR, stage-appropriate metrics)
- **Trustworthy Online Controlled Experiments** — Kohavi, Tang, Xu (the A/B testing bible)

### Blogs / Resources
- **CDP Institute** — cdpinstitute.org (CDP definitions, RealCDP)
- **Google Meridian** — github.com/google/meridian ; **Meta Robyn** — facebookexperimental.github.io/Robyn
- **Hightouch / Census blogs** — composable CDP + NBA + reverse-ETL
- **Braze, Klaviyo, Amplitude blogs** — lifecycle + retention practice
- **Recast / Haus blogs** — MMM + incrementality
- **PDPC Thailand** — pdpc.or.th (PDPA guidance + enforcement)

### Source URLs (2025-2026)
- CDP landscape: https://cdp.com/basics/cdp-vendors/ , https://www.rudderstack.com/competitors/mparticle-cdp-alternatives/
- MA platforms: https://www.digitalapplied.com/blog/marketing-automation-platform-comparison-2026
- Cookieless status: https://www.cookieyes.com/blog/google-cookie-deprecation/ , https://www.dinmo.com/third-party-cookies/
- MMM 2026: https://www.digitalapplied.com/blog/marketing-mix-modeling-2026-mmm-vs-attribution-playbook , https://improvado.io/blog/what-is-marketing-mix-modeling-complete-guide
- Loyalty/gamification: https://www.customerexperiencedive.com/news/why-points-based-loyalty-programs-will-rule-2026/808053/ , https://www.capillarytech.com/blog/comprehensive-guide-to-gamification-in-loyalty-programs/
- Uplift vs churn: https://www.sciencedirect.com/science/article/pii/S0020025519312022 , https://hightouch.com/blog/next-best-action
- Thailand PDPA: https://cookieinformation.com/blog/what-is-the-thailand-pdpa/ , https://www.onetrust.com/blog/the-ultimate-guide-to-thai-pdpa-compliance/

---

## 8. Working With Other Roles

| Role | Hand-off / discussion |
|---|---|
| **Data Analyst** | "Here's the segmentation + hypothesis — pull the RFM cells, retention curves, and size the at-risk segment." Consultant frames + interprets; analyst computes. |
| **ML Engineer** | "Here's the label definition (churn = N-day lapse), the action, and the holdout design — build the propensity/CLV/uplift model. I own thresholds + business eval, you own the model." |
| **DE Engineer** | "Activation needs these traits/audiences synced from warehouse → CDP/MA via reverse-ETL. Here are the identity keys + freshness SLA." |
| **Data Architect** | "Customer 360 + identity resolution + consent flags must live here so activation is governed, not duplicated per tool." |
| **Governance / Privacy Consultant** | "These audiences require this consent + purpose; honor suppression + DNC; log lawful basis." Consent is a hard gate before any campaign ships. |
| **Business Analyst** | "Here's the commercial hypothesis + KPI tree — translate into requirements + process." |
| **Finance** | "Here's point liability, breakage, and incremental-margin model for the loyalty P&L." |
| **Product** | "Loyalty mechanics + in-app personalization moments — joint ownership of the member experience." |

---

*Marketing strategy = making the data team build things that move Customers × Frequency × Basket × Margin. If you can't name the lever and the holdout, it's not a strategy — it's a hope.*
