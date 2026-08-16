# 02 — Notes Register

> Everything explicitly flagged "note this" during the 2026-08-05 session, plus the decisions and corrections that constrain future work.
>
> **REVISED 2026-08-07.** Market research invalidated the plan to spin Regent AI out as a company. See **Section G — Market Reality Check** at the end of this file. Read that section before acting on anything in Section A.

---

## A. The four control plane layers (primary note)

The scope question that determines whether Regent becomes a sellable product or merely Lumora's logging system.

| # | Layer | What it answers | Difficulty | Competitive landscape *(corrected 2026-08-07)* | Sellable standalone? |
|---|---|---|---|---|---|
| 1 | **Observability** | Which agent did what, when, how many tokens, what cost, what latency, what errors | Low | **Closed and consolidating.** Langfuse acquired by ClickHouse Jan 2026; Braintrust ~$800M valuation; Axiom raised $200M Mar 2026; further DevOps-platform acquisitions expected through 2026-27 | No |
| 2 | **Lineage & attribution** | This output came from which agent, which prompt version, which model, which input data | Medium | Thin as a standalone category, but absorbed into the observability/eval platforms above | No |
| 3 | **Policy & permission** | Which agent may touch what; what requires approval; can it be halted mid-flight | High | **Funded and contested.** Oasis Security raised $120M Series B specifically for non-human identity and agentic access governance; Microsoft Agent 365 shipped GA 1 May 2026 at $15/user/month; AWS AgentCore already manages identity, tool access and observability | No |
| 4 | **Evidence** | Can I hand an auditor or insurer a package they will accept | Highest | Least crowded of the four, but occupied — Credo AI, Trustible, Holistic AI, Fairly AI | Not from this position |

**Rules attached to this note:**

- Layers 1-2 must be built regardless, purely to keep Lumora from breaking. They are table stakes, not differentiation.
- Layers 3-4 are what turn the control plane into a company.
- **Layer 3 must be designed before the first line of code.** Permission models are the only one of the four that cannot be retrofitted. Agent identity and scope decisions propagate through everything; getting them wrong means a rebuild. Layers 1, 2 and 4 can always be extended later from data already captured.
- ~~Market context supporting layer 4: independent third-party AI audit projected at ~37% market share in 2026; assurance market ~$0.6B in 2026 growing toward $23B by 2036.~~ **RETRACTED 2026-08-07.** Those figures are real but were used as TAM without competitive structure — a basic analytical error. Demand is real; the entry position is not available from this vantage point. See Section G.

---

## B. Ideas flagged to keep

**Physical AI** — robotics and AI operating in the unstructured physical world. Noted as one of the two most interesting future directions.

**Interface AI** — the human-to-agent interface layer. If everyone runs ten agents in twenty years, how do we command, inspect, and trust them? Nobody has designed this UX well. Directly adjacent to Regent.

**PC — Personal Character** — AI-driven virtual idols/characters, the inverse of "NPC," in the Hatsune Miku vein. Key insight recorded: Miku's power came not from AI but from **fans as co-creators** — anyone could write songs for her, so the character belonged to everyone. The thing to design isn't a clever character but a **shared ownership system**: who holds rights to an identity that hundreds of thousands of people helped build. Unsolved legally and commercially. Secondary insight: a character with real persistent memory, wants, and relationships across millions of people would be a new kind of cultural organism — and what you must build to keep it coherent is a **persistent world model**, one of AI's hardest open problems.

**Memory prosthetic** — not note-taking, but lifelong searchable memory augmentation. Open problem: can humans tolerate never forgetting?

---

## C. Design principles adopted

**The Musk pattern (Sin's formulation):** structure a commercial business so the visionary goal is produced as a *byproduct* of it, rather than being funded separately afterwards. Stronger than "make money first, then dream," because the dream sits in the cost structure from day one and can't be quietly dropped. Closest real example: Starlink — a profitable internet business whose structure forces the highest launch cadence in the world, which is exactly what Mars requires.

**The change filter:** *"If the world changed twice as fast, would this be worth more or less?"* Build things that **benefit** from change rather than merely surviving it — intermediaries, converters, registries, standards, migration tooling, verification systems. Every new thing that appears gives them more work.

**The capability test:** replace *"is this new?"* with *"if this works, who can do what they couldn't yesterday?"* Innovation lives in newly-possible human capability, not in business-model novelty. Almost no large company won by being first — Google, Facebook, iPhone, Tesla, SpaceX all took existing categories and changed the cost structure.

**Vertical beats horizontal when small.** A neutral marketplace serving everyone dies. A system going deep enough on one vertical that hyperscalers won't bother has a chance.

**Wait for the second use case.** Don't extract or abstract anything until two real users exist. Premature abstraction kills more platforms than late abstraction.

**Don't charge for prohibition; charge for permission.** Successful governance businesses are permission-granters, not police — UL, Michelin, TÜV, ISO. The buyer is the party bearing risk (a CFO who must sign off), not the public.

---

## D. The compass — Frutiger Aero over cyberpunk

**Mission statement:** *make advanced capability belong to everyone and be visible, instead of concentrated and opaque.*

The difference between cyberpunk and Frutiger Aero is not technological — both have identical technology. Only two things differ: **who has access**, and **whether you can see through it**. Cyberpunk technology is opaque and corporate-owned. Frutiger Aero imagery is built on transparency as a core visual element — it communicates that the technology hides nothing and belongs to you.

**This resolves into concrete engineering forks.** At each one, the short-term-more-profitable answer and the compass answer usually differ:
- Does data live with us or with the user?
- Open API, or locked in?
- Can a customer's agents leave and take their work?
- Can we explain why the system decided what it decided?

**Discipline note:** this is not a feature to add later. Built in from day one it costs almost nothing. Retrofitted at a thousand users it becomes a full rewrite and won't happen. That is how every company becomes cyberpunk — nobody intends it; transparency simply keeps getting deferred because it is never urgent.

---

## E. Corrections that bind future work

1. **Insurance / the employer is out of scope.** Sin's day job at AIA provides technical growth and income only. It is not part of any business model discussion. Do not reintroduce.
2. **Naming must be locked.** The record says **Regent AI**; "RegentX" appeared only in conversation. A drifting name signals unsettled scope. Pick one.
3. **Lumora is a production house, not a governance play.** Sin owns the content. Nobody in Lumora needs regulating. The control plane exists because *he* needs to control his own agent fleet.
4. **Lumora proves Regent's technology, not Regent's market.** Regent's buyer is a risk officer or CTO at an organisation afraid of litigation — a completely different person from a creator. AWS escaped this trap only because Amazon Retail happened to be a brutal, enormous customer whose internal problem matched the world's. Not guaranteed here.
5. **Venture studio trap: customers you own are not evidence you can sell.** In-house companies never refuse, never negotiate, never churn, never call a feature bad. Get one external paying customer who can complain before considering any company split.
6. **Vertical proliferation trap.** Spiritual content → PC building → interior design share suppliers, customers, rules and sales motions far less than expected. Only the agent stack is genuinely shared. Opening too fast yields five shallow companies instead of one deep profitable one.
7. **Crypto Trading Engine is outside this ecosystem.** Personal investing tool; the clean-energy company list feeds it. Track A income, not a main build, not part of the platform architecture.
8. **Belief/spiritual-vertical discussion is closed here.** Sin will build a dedicated agent to consult on that separately. This track stays focused on platform and product architecture.

---

## F. Investment note (separate from the build)

**Method:** first tranche is a small equal-weight probe across every candidate on the list; research and analysis then determine which get scaled up. FOMO is acknowledged as a feeling, not an allocation strategy.

**Energy stack layers identified** *(industry map, not financial advice)*:
1. Power producers with hyperscaler contracts — Vistra, Constellation
2. Equipment and physical bottlenecks — turbines, transformers, switchgear, transmission, cooling
3. Fast-deploy dispatchable clean energy — fuel cells (Bloom Energy), and critically **grid-scale batteries**, since intermittency is what disqualifies solar/wind for AI loads
4. SMR/new nuclear — Oklo, X-energy, Kairos, TerraPower, NuScale, GE Hitachi. High risk; IEA projects only 10-25 GWe globally by 2035. Fuel is the more durable angle: Centrus as the only licensed US HALEU producer is a toll-collector model.
5. **Thailand/SEA — most accessible, least discussed.** Q1 2026 Thai investment applications exceeded THB 1.01tn with digital at THB 873.7bn; BOI approved a THB 842bn TikTok data center expansion in May 2026 across Bangkok, Samut Prakan, Chachoengsao; H1 2026 energy sector had 221 projects, 198 of them clean. Thai listed IPP/SPP operators, industrial estate operators, and electrical contractors are winning this work. Readable in a familiar language — an edge over US equities already covered by a hundred thousand analysts.

**Caution recorded:** the theme has run two years; many prices already discount 2030. Infrastructure booms (railways, fibre 2000) show demand materialises as forecast while first-round investors lose money to overbuild and price competition.

---

## G. Market Reality Check — 2026-08-07

Research run after the original session. **Conclusion: Regent AI does not work as a standalone company. Build the control plane for Lumora's own use only.**

### G.1 The four-filter test

Applied to Regent AI as a standalone enterprise governance product:

| # | Filter | Result | Evidence |
|---|---|---|---|
| 1 | Is my edge **access** or **code**? | **FAIL** | All four layers are code. No privileged access to risk officers, auditors, or underwriters. Code advantage has ~6 months of life; access advantage lasts years. |
| 2 | Does the buyer already have this budget? | **PASS** | Gartner projects agentic AI spending at ~$201.9B in 2026, growing >100% YoY in early years. |
| 3 | Can I get a first paying customer without anyone's permission? | **FAIL** | Enterprise governance sales require procurement, security review, SOC2, reference customers. 6-18 month cycles. Not reachable solo from Thailand. |
| 4 | If OpenAI/Google/Microsoft ships this next month, am I dead? | **FAIL — already shipped** | Microsoft Agent 365 with MCP gateway, GA 1 May 2026 at $15/user/month. Google added agentic automation to Security Operations with MCP server support. AWS AgentCore already manages memory, session, tool access, identity and observability. |

**Three of four fail. Filter 1 is the decisive one.**

### G.2 Funding and consolidation KPIs

| Metric | Value | Implication |
|---|---|---|
| AI agent governance funding, March 2026 alone | >$375M | Axiom $200M, Kai $125M, JetStream $34M, ArmorCode $16M, Geordie $6.5M |
| Agentic AI security funding, 10-26 March 2026 | >$392M in two weeks | Oasis Security $120M (non-human identity), XBOW $120M, Surf AI $57M, RunSybil $40M, Qevlar $30M, Eclypsium $25M |
| Top 10 agentic AI security startups, cumulative | $3.6B raised | |
| Funding concentration, AI governance | Top 10 startups hold ~52% of identified funding | Investors have already picked category leaders |
| Top 10 AI governance startups by value | ~$3.9B midpoint, ~54.5% of category value | |
| North America share of agentic AI funding, 2026 YTD | ~82% of capital, ~79% of deals ($863M / 23 deals) | Capital and proximity are both concentrated in one geography |
| Observability consolidation | Langfuse acquired by ClickHouse, Jan 2026 (within ClickHouse's $400M Series D at $15B) | Category is exiting, not entering |
| Durable execution anchor | Temporal $430M cumulative, $5B valuation after $300M Series D, Feb 2026 | |
| Evaluation leader | Braintrust $120M cumulative, $800M valuation | |
| Agent Execution Infrastructure share of 2026 YTD deals | 20.7% | Runtimes, identity, observability, control layers — actively funded |
| Agentic AI spending forecast, 2026 | ~$201.9B | Demand is not the problem |
| AI cybersecurity segment | $10.82B (2024) → ~$26B (2025) → $172B projected (2029), 73.9% CAGR | |

### G.3 The one real gap — and why it is not reachable

Analysis in the space notes that **98% of enterprises are deploying AI agents in some capacity, while 79% lack governance policies spanning their full agent footprint.** Platform vendors have no incentive to make their governance data interoperable with competitors, so each platform-native governance investment deepens the fragmentation it claims to solve. The gap is a genuine **cross-platform governance layer sitting above all of them.**

**Why it is not available from here:** that position requires neutrality *and* enterprise distribution simultaneously. It is the same lesson as the earlier data marketplace — right direction, roughly 18 months late, and the required position is occupied by people sitting in the same rooms as the buyers.

### G.4 What this changes

**Still true:**
- Lumora needs a control plane regardless. Build it because you need it.
- Boundary discipline (separate module, own data store, interface-only) is good engineering and stays.
- The Frutiger Aero compass is a design principle, not a product. Unaffected.

**No longer true:**
- That the control plane grows into a sellable company.
- That the assurance market represents an opening.
- That "regulation being blocked is bullish for private assurance" implies an opportunity *for Sin specifically*. The statement is true about the market; it says nothing about entry position.

**Method error to avoid repeating:** the original recommendation cited market size and growth rate without checking who already occupies the position. TAM without competitive structure is not analysis.

### G.5 The remaining question

**"What access do I have that a founder in San Francisco does not?"**

From everything on record, the honest list is short:
1. The Thai and SEA market, language, and regulatory context
2. Operating data from an agent fleet actually running with revenue attached
3. Domain-specific ground truth in whatever vertical Lumora enters

**All three live in Lumora. None live in Track B.**

---

## H. What reading the Lumora KB changed — 2026-08-07

The KB and ADR-0001 were read for the first time on 2026-08-07. Sections A-G above were written without them.

### H.1 The binding constraint that was missed

**ADR-0001 (2026-07-18, Accepted) parks the Lumora backend.** Hard rules: no new adapter until ≥100 posts AND a named manual step >2 hrs/week · Phase-1 pipeline is the 5 skills + Claude Code + manual posting · the only backend needed is a per-post log · all Phase 2/3 work frozen · **never** an unofficial auto-publisher.

The control plane specified in the earlier file 04 violated rules 1, 2, 4 and 5 at once. It was the "factory before the first product" trap the ADR was written to prevent. File 04 has been rewritten.

### H.2 Library Framework was never cancelled

**Folded into Lumora as internal IP on 2026-07-18.** Canonical = Lumora's `01_creative_library.md`. Spin-out gated at 12 months plus framework-attributable channel growth. If ever externalized: **content-led authority, NEVER SaaS** — recorded twice.

**And it is the measurement layer.** The C×T×M tag on every post is what makes the feedback loop possible: `post_log` → `v_post_scores` → weekly review → adjusted combo spread. Without the taxonomy there is nothing to learn from. Full detail in file 05.

### H.3 Lumora's real shape

O&O MCN + Multi-Catalog Lab, umbrella brand with four arms, three pillars, three business-model phases (B2C → B2B agency → B2P platform). สายมู is catalog #1, not the project. **Phase 2 is an agency, explicitly not SaaS** — Sin's 4th recorded pushback in an earlier session.

Current state: 90-day publish-or-park sprint. Channel @มูมีแสง. Explorer × Magician. Pillars C2 + C1/C6 + C9. Day-90 gate = 1 post ≥50K views OR 1,000 followers. Miss → change tone/catalog or park.

### H.4 The four layers, re-judged against reality

| Layer | Verdict for Lumora Phase 1 |
|---|---|
| 1 Observability | Exists as `post_log`. Sufficient. |
| 2 Lineage | The `(C,T,M)` tuple *is* the lineage at the fidelity needed. |
| 3 Policy & permission | **No subject.** No agent acts without Sin. The real policy set is the content compliance table in file 05 §4. |
| 4 Evidence | No auditor, no insurer. The only external compliance reader is TikTok's AI-labeling enforcement. |

### H.5 Method errors to not repeat

1. **Specified an architecture without reading the project's canonical docs.** The pipeline in the earlier file 04 was invented.
2. **Did not check for a binding ADR** before proposing a build.
3. **Treated a folded-in component as a footnote** — Library Framework is the measurement layer, not a side asset.
4. Compounding the earlier error in Section G: TAM without competitive structure, then architecture without source documents. Same failure shape — reasoning from a model instead of from the material.

### H.6 Stale detail spotted in the Lumora KB

`knowledge/00_overview.md` describes the day job as Data Engineer at The1 with a GCP/Beam/BigQuery stack. **`CLAUDE.md` is already current** — Senior DE at AIA, Azure Databricks + Kafka/Strimzi/Debezium, IP boundary updated to name AIA. Only the one knowledge file lags; worth a small edit so the two don't contradict each other.

### H.7 Correction to H.3 — sprint settings are recommended, not locked

The account-decisions package states outright that Sin makes the final call, and Lumora's `CLAUDE.md` + `INDEX.md` still list as **PENDING**: channel name + bio + visual identity · voice positioning · archetype (weigh the LIVE-commerce handicap) · first 30-day batch (which 2-3 combos to prove first) · affiliate-first vs digital-product day 1 · show face on camera.

Files 04 and 05 previously stated these as decided. Corrected.

### H.8 Canonical document set

`00_overview` · `01_creative_library` · `02_content_and_channels` · `03_monetization` · `04_tech_backend` · `05_multi_account` · `06_architecture_agency` · `07_platform_design` (frozen under ADR-0001) · **ADR-0001**.

Five skills: `lumora-combo-recommend` (the decide step) · `lumora-content-batch` (combo → post) · `lumora-art-prompt` · `lumora-trend-scan` · `saymu-oracle` (folded into content-batch as oracle mode 2026-07-18, used as the daily anchor).

**Not yet read:** `01-batch-30day.md`.
