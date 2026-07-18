# Sin's Projects Knowledge Base

> **Version**: 2026-06-27 · **Updated 2026-07-18 (portfolio review)**
> **Owner**: Sin (วศิน วังสมบัติ / ภัค)
> **Purpose**: Master context document for individual project sessions. Every project-specific session should load this first to understand the portfolio, then focus on its assigned project.
> **Companion (read before acting on portfolio strategy)**: `portfolio-review-20260718.md` — the review that produced the 2026-07-18 changes (see its §1 Executive Summary, §2 Portfolio Strategy, §4 90-Day Plan).

---

## 0. How to Use This Document

This document is the **shared baseline** across all 6 project sessions. Each project will have its own dedicated VS Code / Claude Code session, but they all reference this file to stay aligned.

Workflow:
1. Session opens → read this file first (full read, not skim)
2. Session reads `INDEX.md` of personal KB (`~/Documents/Projects/Agent/INDEX.md`) to know available agents/skills
3. Session identifies its assigned project from the bootstrap prompt
4. Session focuses ONLY on that project, but is aware of cross-project connections noted here

**Do not** mix project work across sessions — that defeats the purpose of the split.

---

## 1. Personal Context (relevant to all projects)

### Who Sin is as a builder

- **Role**: Senior Data Engineer at **AIA** (insurance), started **2026-07-01**. Day job is Azure-heavy: Azure Databricks, Kafka/Strimzi/Debezium CDC on AKS, Spark, Terraform. (Previous: DE at The1 / Central Group — GCP stack; now archived reference, not the current employer.)
- **Career direction**: Founder / IC Specialist track. Skills roadmap aimed at vector databases, RAG, LangGraph, agent evaluation, agentic AI patterns.
- **Mindset**: Builder / architect, not "engineer who ships tickets". Thinks in systems, abstractions, long-term framework before code.
- **Style**: Divergent and library-based. Prefers breadth before convergence. Multi-direction creative options preferred over premature lock-in.

### Communication preferences

- Thai-English mix. Technical terms in English, narrative/feel in Thai.
- Peer-level intellectual tone. **Not** instructional ("ลองทำแบบนี้สิ"). **Not** corporate ("Best practice คือ...").
- Push back when wrong. Sin has corrected sessions multiple times when:
  1. Conflating different concepts (e.g., Microsoft Fabric vs. Data Fabric)
  2. Diving into B2B strategy when he wanted basics
  3. Forcing single aesthetic when he wanted multi-direction
  4. Drawing SaaS when he had specified agency model
- Honest reality checks > polite agreement.
- Brevity over throat-clearing.

### Big why (frame for everything)

Sin lost his mother in November 2024. He stores that as fuel, not as something to express outward. The drive across all projects is **to build something stable enough that the people he loves are protected** — not personal ego or status. This is relevant context because it explains why he runs commercial track + vision track in parallel: commercial track must pay; vision track is the actual point.

Don't bring this up in conversation unprompted. It's context, not content.

### Employer IP boundary (AIA) — restated 2026-07-18

Sin is a full-time employee at **AIA**, a regulated insurer. Hard boundary for every portfolio project (this text was previously written for The1; restated for AIA):

- **No AIA internals in any public content or repo** — no code, data, schemas, architecture, credentials, customer/PII, or confidential material from AIA, and nothing derived from them that would expose AIA systems. Applies to Lumora posts/repos, the crypto engine, and any Track B artifact.
- **Personal projects on personal time and personal equipment only** — never on AIA laptops, networks, or accounts.
- AIA-specific engineering knowledge lives in the separate AIA project KB, not here and not in anything published.

---

## 2. Portfolio Overview

Sin runs **two tracks in parallel**:

### Track A — Commercial / Cash Flow
Projects that generate revenue or could. Job: **fund Sin's exit from employment** (not "fund Track B" — see revised thesis below).

- **A1. Lumora** — O&O Multi-Channel Network for Thai creators (AI-automated) — **PIVOT: 90-day content sprint, backend FROZEN**
- **A2. Library Framework** — content taxonomy + production system — **FOLDED into Lumora (no longer a standalone project)**
- **A3. Crypto Trading Engine** — Personal trading tool, not a product — **GO-VIABLE (conditional), kill date 2026-08-31**

### Track B — AI Ecosystem Vision
Long-term bets reframed for the agentic era. The 2024 versions assumed "AI = model" — obsolete. **As of 2026-07-18, all three are killed-as-registry / parked. Track B is an OPTION, not an active roadmap** (see thesis + verdicts table below).

- **B1. NeurX** — Agent Infrastructure & Registry — **KILLED as registry; trust/provenance IP merged into Regent**
- **B2. Regent AI** — Agent Governance & Trust Layer — **PARKED as product; kept as career capital + dogfood**
- **B3. SentientNet** — Sovereign / Decentralized Agent Network — **PARKED indefinite**

### Thesis — how the two tracks actually relate (rewritten 2026-07-18)

> **Track A funds Sin's exit from employment.** Track B = an **OPTION** that must be **re-underwritten from a fresh landscape scan at unlock time** — not a roadmap waiting to execute.

Why the rewrite: the old thesis ("Track A funds Track B; specs are ready to execute") assumed Track B's 2024-era positioning would still hold when Track A finally pays. It won't. **Every landscape KB in this portfolio rotted in <13 months** — micropayments rail lost to x402/AP2, registry consolidating under the Linux Foundation (AAIF), the enforcement point taken by Entra Agent ID / Okta / free Microsoft OSS. So any Track B spec written today is archaeology by the earliest unlock (2027–28).

Consequences:
- Do **not** "maintain" Track B vision during the Track A sprint. If an un-park trigger fires, re-scan the market from scratch and re-underwrite before building anything.
- The only Track B value bankable on today's horizon is **career capital**: Sin works inside a regulated insurer (AIA) that will face real agent-governance questions — the Regent KB monetizes *now* as "the person who understands agent audit/policy," at build cost ≈ 0.

### Verdicts (2026-07-18 portfolio review)

6 projects → **1.5 active workstreams + 1 self-run tool**. Nothing valuable is lost — 4 of 6 were already 0-LOC or mock-only.

| Project | Verdict | Status / next action | Un-park / kill trigger |
|---|---|---|---|
| **Lumora** | **PIVOT** | 90-day content sprint; backend **FROZEN**; publish, don't engineer | Active — gated by the Lumora gate (below) |
| **Library Framework** | **FOLDED into Lumora** | Not standalone; canonical = Lumora `01_creative_library.md` v3, rest are pointers; never a SaaS/license | Revisit in 12 mo *only if* ≥1 Lumora channel shows framework-attributable growth |
| **Crypto Trading Engine** | **GO-VIABLE (conditional)** | 1 weekend: backtest → automate → journal | **Kill date 2026-08-31** — if still unused → archive with KB |
| **NeurX** | **KILLED as registry** | Trust/provenance IP **merged into Regent** (Agent Trust & Governance); Runtime + Observability cut permanent | Does **not** re-open as a registry; trust thesis lives on inside Regent |
| **Regent AI** | **PARKED as product** | Career capital + **dogfood** (PreToolUse policy hook + hash-chained audit on own fleet) | No product build until merged Track B has ≥1 external user **AND** Lumora Phase-1 revenue |
| **SentientNet** | **PARKED indefinite** | Narrative only; micropayments pillar **deleted**; sovereign angle donated to Regent | Un-park only if **ALL 3**: Track A sustained cash-flow + NeurX/Regent external users + a real sovereign-buyer conversation |

### Market-contact rule (portfolio-wide, 2026-07-18)

**No project gets additional engineering / docs / KB hours until it completes its own next market-facing action.**

- **Lumora** → next market action = **publish** (post). No new backend adapter until ≥100 posts published AND a named manual step costs >2 hrs/week.
- **Crypto** → next market action = **use it live for 1 week**. No new features until it has actually been run.
- **Parked / killed projects** (NeurX-as-registry, Regent-as-product, SentientNet, Library-standalone) → next market action = none → they **stay parked** and earn **zero hours**.

Rationale: the best-maintained thing in this portfolio is the one with no market contact — that's a warning sign, not success. Planning hours on a project that hasn't touched the market is procrastination by definition.

### Hours-tracking directive (starts 2026-07-18)

The master doc never modeled hours/week — the biggest hole in the whole strategy. Honest budget during AIA ramp: **6–10 hrs/week this quarter**.

- **Track actual side-project hours for 4 weeks starting 2026-07-18.** This number — not any roadmap — decides every schedule below.
- **If actual < 6 hrs/week → rescope the Lumora sprint to 3 posts/week** (saymu-oracle as daily anchor) instead of missing the target silently.

---

## 3. Project Track A: Commercial

### A1. Lumora — O&O MCN for Thai Creators

**One line**: AI-automated holding company that owns multiple content channels across Thai cultural verticals.

**Status**: **PIVOT (2026-07-18 portfolio review)** — 90-day content sprint, backend **FROZEN**. 8 months of build produced 0 posts / 0 followers / 0 THB; the fix is to *publish*, not to engineer. Reposition differentiation from "AI automation at scale" (commodity + platform-suppressed) → **AI-art aesthetic + สายมู cultural literacy + Sin's own voice**, ~70/30 human/AI, AI-labeled from post #1, no unofficial auto-publisher. See §2 verdicts table + `portfolio-review-20260718.md` §3.1.

**Inspired by**: Ruhnn Holdings (China, 190+ KOLs, Alibaba-backed) and Beast Industries (MrBeast's closed-loop content-to-commerce).

**Differentiation**:
- **Multi-catalog O&O** — Thai market has zero equivalent. AnyMind is affiliate (brand-side), Sin is creator-side.
- **AI-automated production** — cost edge over traditional MCNs that burn $1M+/month.
- **Cultural specificity** — สายมู, อาหารไทย, ท่องเที่ยว, gadget, art, สุขภาพ. Enterprise tools can't replicate.
- **Lean ops** — Phase 1 budget $80-150/month.

**Architecture (Two-Service)**:
- **Data Service** — Sources → Data Fabric → AI Agents that decide content combos (topic × theme × format).
- **Marketing Service** — Content Production → Multi-account Posting → Performance Tracking.
- Connected by Sin-built AI agents.

**Roadmap (3 phases)**:
- **Phase 1 (RE-MODELED 2026-07-18)**: Solo creator, 90-day content sprint. Base-case revenue **0–10K THB/mo in the first 6 months OF POSTING** (posting hasn't started yet). The old "50–200K THB/month" was a **top-percentile outcome mislabeled as base case** — deleted as a target. Budget $80-150/mo. **What decides whether Track A is real is NOT a revenue band — it's the Lumora gate: 1 post ≥50K views OR 1K followers by day 90.** Miss → change tone/catalog or park the project. Backend frozen for the whole sprint.
- **Phase 2 (FROZEN until Phase-1 gate passes)**: Boutique agency; retainer clients. Do no thinking/architecture here until a real Phase-1 case study exists.
- **Phase 3 (FROZEN)**: Platform Intelligence Service. Vision only — not on any current horizon.

**Locked decisions**:
- Agency model, NOT SaaS.
- Sin's first 1-3 accounts are his own, not clients.
- AI-native from day one, not retrofit.

**Open questions**:
- First vertical to launch? (สายมู? อาหาร? — needs validation)
- Voice/persona strategy per channel (still using Library Framework axes)
- Tech stack: which agent framework, which model APIs

**Connection to Track B**: (superseded 2026-07-18) — Lumora's Phase-1 "pipeline" is the **5 existing `lumora-*` skills + Claude Code + Sin's thumb** ($0 infra), not a NeurX customer. Do not build Lumora-as-customer-zero of any parked Track B project — "platform from one customer" is how solo founders drown. If Lumora ever needs agent plumbing, build it as Lumora-internal, not as NeurX.

---

### A2. Library Framework — Content × Theme × Media

**One line**: A generalizable taxonomy + production system for AI-driven content — now **internal IP inside Lumora**, not a separate product.

**Status**: **FOLDED into Lumora (2026-07-18 portfolio review)** — no longer a standalone project. Canonical source = Lumora `01_creative_library.md` v3; every other copy becomes a pointer (reconcile the Hero/Hub/**Hygiene** vs Help drift and fix the channel-count formula to `1 ≤ N ≤ S×A`, gates decide). Standalone SaaS/license is **ruled out** (commodity market, no proof). The only possible moat — a combo-performance dataset — accrues *only* inside Lumora once it starts posting. Revisit in 12 months only if ≥1 channel shows framework-attributable growth.

**Why split from Lumora**: Same reason AWS split from Amazon retail. The framework solves a general problem (how do you systematically generate diverse content at scale without homogenization), not just Lumora's. Other creators / agencies / brands could license it.

**The framework**:

Three post-level axes:
- **C — Content pillars** (C1-C10): topical buckets per channel
- **T — Theme clusters**: Future-tech, Historical, Liminal, Cosmic, etc. — cross-cutting moods/lenses
- **M — Media formats** (M1-M12): video, carousel, long-form, podcast, etc.

Account-level fixed tags:
- **Voice/Archetype** — channel personality
- **Audience Persona** — who the channel speaks to
- **Niche Scope** — narrowness/breadth

Per-post optional tags:
- **JTBD** — Job-to-be-done
- **HHH funnel stage** — Hero/Hub/Help (YouTube's framework)

**Channel Count Formula**:
`MIN(S, A) ≤ N ≤ S × A` where S = subject/topic breadth, A = audience segment count.
Three audience-side variables:
- **V1**: overlap threshold ~30%
- **V2**: viable audience size > 10K
- **V3**: positioning distinctness test

**Productization options**:
- (a) Internal-only tool for Lumora
- (b) SaaS / framework license for other creators
- (c) Consulting offering — Sin sets up the framework for a brand
- (d) Open-source the framework, monetize the agent that runs it

**Open questions**:
- Should this even be a separate product? Or pure internal IP for Lumora?
- If productized, who's the customer? Solo creators? Agencies? Brand marketing teams?
- License model vs. SaaS vs. open-core

**Connection to Track B**: This is conceptually an "agent prompt + workflow library" — directly relevant to NeurX (where agent workflows would live).

---

### A3. Crypto Trading Decision-Support Engine

**One line**: Personal hybrid Python engine + TradingView overlay for crypto trade decisions. Not a product.

**Status**: **GO-VIABLE, conditional (2026-07-18 portfolio review)** — v1 is actually done (1,623 LOC, 30 tests pass, 9 ADRs) but **dormant since 2026-06-07**; friction is the manual CLI, not the day job. 1-weekend timebox, in order: **backtest harness → automate (cron + Telegram push) → journal**, then optional (playbook table + `confidence.floor` wiring + position sizing + Elliott fix). **Kill date: 2026-08-31 — if still unused → archive with KB, no guilt.** Freeze roadmap: no dashboard, no predictive ML, no webhooks. Never productize (unvalidated tool + Thai SEC advisory liability).

**Important framing**:
- **NOT data engineering / pipeline work**. Don't apply DE mindset.
- **NOT a startup project**. No customers, no SaaS, no scale design. Personal tool.
- **NOT related to The1 / NTT / SCB / day job**.

**Architecture**:
- **Local Python engine** — ingest OHLCV from Binance/ccxt → store local (DuckDB/parquet) → compute features (MA stack, RSI, ATR, structure HH/HL·LH/LL, pivots, S/R) → emit structured JSON.
- **TradingView** — visualization layer only. Pine Script can't fetch external APIs, so engine outputs hardcoded levels → manually pasted into Pine snippets.
- **Two-step workflow**:
  - Step 1: deterministic local analysis → JSON artifact
  - Step 2: human review + TradingView integration

**JSON contract includes**: regime, bias, levels with invalidation, Elliott Wave per-timeframe (low weight, supplementary only), signals array with weights, confluence score, trading plan, daily/weekly/monthly summaries.

**Locked decisions**:
- Two-layer (deterministic + interpretive) architecture
- Hybrid Python + TradingView
- Elliott Wave = low weight in signal scoring
- LLM API called at engine runtime (not Claude Code) for interpretive layer
- Build-time = Claude Code; runtime = direct API

**Open decisions** (flagged for Sin to confirm before code):
- Folder name typo: `crypto-tranding` → `crypto-trading`?
- Final signal weighting scheme
- Symbol/timeframe scope for v1 (BTCUSDT 1h/4h/1d as default)

**Subagent routing**:
- `architect/solution` — one-time architecture sanity check
- `engineer/software` — lead build (Python engine)
- `engineer/data-analyst` — feature/indicator computation
- `business/investment` — signal logic, weights, playbook→plan mapping, invalidation
- (later) `engineer/ml` — predictive layer
- (later) `engineer/frontend` + `design/ui` + `design/ux` — dashboard

**Skills**:
- Existing: `adr` for logging decisions
- To create: `crypto-ta-math`, `risk-management`
- Later phases: `backtesting-discipline`, `pine-script-v6`

**Connection to other projects**: Standalone. No direct linkage to other projects. Treat as separate concern.

---

## 4. Project Track B: AI Ecosystem Vision

### The reframing principle

Original vision (2024) assumed the unit of AI is the **model**. In 2026, the unit is the **agent + workflow + context**. Models are commodities you swap with one API line. The interesting problems moved up the stack.

All three projects are reframed from "model-centric" to "agent-centric".

```
SentientNet (sovereignty)     ← who owns it
        ↑
Regent AI (governance)        ← what can it do, what's auditable
        ↑
NeurX (infrastructure)        ← where agents live, how they discover each other
        ↑
        Agents (unit of work)
```

---

### B1. NeurX — Agent Infrastructure & Registry

**One line**: The "npm of agents" — registry, runtime, interop layer for AI agents.

**Status**: **KILLED as registry (2026-07-18 portfolio review)** — the neutral-registry window closed (Linux Foundation **AAIF** consolidation + hyperscaler marketplaces + A2A v1.2 signed AgentCards absorbing the trust wedge). A solo part-timer can't win a two-sided cold-start against foundation gravity. The one defensible pillar — **trust/provenance** — is **MERGED into Regent** as the "Agent Trust & Governance" project. **Runtime + Observability pillars are cut permanently** (each is a whole company). This does **not** re-open as a registry; re-scan the market before believing any positioning below. See `portfolio-review-20260718.md` §3.4.

**New vision**: Agent-centric infrastructure.

**Pillars**:
- **Agent Registry** — devs publish agents (not models). Discovery, versioning, ratings.
- **Agent Interop Layer** — agents talk to agents. Built on MCP, A2A protocols.
- **Agent Runtime** — host LangGraph / CrewAI / custom agents serverless.
- **Agent Observability** — trace, debug, replay agent runs.

**Why now**:
- MCP launched late 2024, still early-adopter phase.
- LangSmith dominates observability but only for LangChain.
- No clear winner for "agent npm" — registry is open.

**Possible angles**:
- **Global play** — compete on developer experience.
- **Thai/SEA play** — local agent registry, Thai-language agents, PDPA-compliant by default.
- **Vertical play** — agents for specific industries (content, e-commerce, finance).

**Open questions** (need Sin's answers):
- Open-source core + paid hosting, or closed SaaS?
- Solo build vs. raise vs. co-founder needed?
- 2-year MVP target or 5-year platform play?
- Does Lumora count as customer zero?

**Connection to Track A**: Lumora is potential first customer (Lumora needs agent infra). Library Framework could ship as agent workflows on NeurX.

---

### B2. Regent AI — Agent Governance & Trust Layer

**One line**: Audit, policy, and human-in-the-loop layer for agents that act in the real world.

**Status**: **PARKED as product (2026-07-18 portfolio review)** — the market validates the thesis, but a solo *unaudited* vendor cannot sell to compliance buyers (vendor-risk review = a locked door, not a hard sale). **CONVERT to career capital + dogfood**: build a PreToolUse policy enforcer + hash-chained JSONL audit on Sin's *own* agent fleet (1 weekend) — permission matrix, spend/rate caps, HITL threshold, chain verification — which doubles as protection for Lumora's content agents and as a live Regent demo. Position self as the agent-governance person at AIA. Substrate decision: **Cedar (or OPA/Rego), never invent a DSL**. Fix the EU AI Act Art. 12 wording (tamper-evidence is a defensible Art. 15 interpretation, not a literal mandate). **No product build until the merged Track B has ≥1 external user AND Lumora Phase-1 revenue.** This project is now also the home for NeurX's trust IP and SentientNet's sovereign-deployment angle. See §3.5.

**New vision**: Agent autonomy is the actual unsolved problem.

**Pillars**:
- **Agent Audit Trail** — agent decided X, based on Y, calling tools Z. Full replay.
- **Policy Engine** — declarative guardrails. "Agent can spend up to $100. Agent cannot send email to external domains. Agent must request approval for...".
- **Multi-Agent Compliance** — when 5 agents work together and something goes wrong, who's responsible? Provenance graph.
- **Human-in-the-loop Checkpoints** — agents request approval at defined risk thresholds.

**Why now**:
- EU AI Act in force.
- US executive orders on AI.
- Singapore AI Verify.
- Thailand drafting AI regulation.
- Enterprises afraid to deploy autonomous agents without audit/control → market pull.

**Possible angles**:
- **Compliance-first SaaS** — sell to enterprises in regulated industries (finance, healthcare, gov).
- **Thai/SEA-first** — PDPA + future Thai AI Act compliance built-in.
- **Open-source policy engine** — monetize hosted version + audit dashboard.

**Open questions**:
- Generic compliance platform, or vertical (finance, healthcare)?
- B2B SaaS or open-core?
- How does it relate to NeurX (separate product or layer on top)?

**Connection to other projects**: NeurX is the host, Regent is the policy layer. Lumora uses Regent to audit AI content decisions for brand safety.

---

### B3. SentientNet — Sovereign / Decentralized Agent Network

**One line**: Agents that aren't owned by US Big Tech.

**Status**: **PARKED indefinite (2026-07-18 portfolio review)** — activation probability ≈ 0 (product of 4 conditions each <50%); the micropayments rail is already lost (x402: 165M+ txns; Google AP2), and "nobody owns the sovereign-agent framing" is already false (ioMoVo, Nagent, hyperscaler sovereign clouds, Thailand's own ThaiLLM). **DELETE the micropayments pillar** — if agents ever need to pay, adopt x402/AP2 as a consumer, never build rails. The sovereign-deployment angle is **donated to Regent** (a *feature*, not a company). Keep ~150 lines of narrative for free; KB is **FROZEN — assume stale**; re-research from scratch at un-park, never incrementally. **Un-park only if ALL 3 fire**: Track A sustained cash-flow + NeurX/Regent external users + a real sovereign-buyer conversation. See §3.6.

**New vision**: Less about crypto, more about sovereignty.

**Pillars**:
- **User-owned agents** — your agent runs on your infra, not OpenAI's.
- **Agent-to-agent micropayments** — agents pay agents (this is where crypto rails actually make sense).
- **Sovereign deployment** — Thai government, SEA companies, EU enterprises that don't want US dependency.
- **Federated agent learning** — agents learn across organizations without centralizing data.

**Why now (and why later)**:
- Geopolitical AI sovereignty is a real and growing concern.
- BUT — this is the **furthest-out vision**. 3-5+ years.
- Existing players: Bittensor, Gensyn, Akash, Render, Ritual (crypto/decentralized AI). None own the "sovereign agent" framing yet.

**Possible angles**:
- **SEA Sovereign Agent Network** — ASEAN-scale infrastructure for governments/enterprises.
- **Thai national AI infrastructure play** — partner with government/Bot/regulator.
- **Federated agent platform for enterprises** — sell to multinationals that can't share data across borders.

**Open questions**:
- Crypto rails (yes/no/eventually)?
- Government play vs. enterprise play vs. consumer play?
- Realistic timeline: 3 years? 5? 10?
- This requires Track A profitable AND Track B (NeurX + Regent) established. Likely Phase 3+ of company.

**Connection to other projects**: Long-term destination. Builds on NeurX (infra) + Regent (governance) + real-world deployments (Lumora-style).

---

## 5. Cross-Project Connections

```
Track A (commercial)              Track B (vision)
────────────────────────          ────────────────────────
Lumora ─────────────────────┬───→ NeurX (uses agent infra)
                            │
Library Framework ──────────┼───→ NeurX (workflows live here)
                            │
                            └───→ Regent (governs Lumora's agents)
                                  ↑
                                  └─── SentientNet (long-term sovereignty)

Crypto Engine ───── (standalone, no direct linkage)
```

**Diagram note (2026-07-18)**: the Track B arrows above are **vision-era**. NeurX is killed-as-registry, Regent is parked-as-product, SentientNet is parked-indefinite (see §2 verdicts). Lumora's real Phase-1 "pipeline" is the 5 `lumora-*` skills + Claude Code, not a custom backend or a NeurX dependency.

**Key sequencing insight (revised 2026-07-18)**: Track A funds **Sin's exit from employment** — not Track B directly. Track B is an **option** to be re-underwritten from a fresh scan at unlock (2027–28 earliest), because every landscape KB here rotted in <13 months. Phase-1 revenue base case is **0–10K THB/mo in the first 6 months of posting** (the old 50–200K was a mislabeled top-percentile outcome). What proves Track A is real is the **Lumora gate** (1 post ≥50K views OR 1K followers by day 90), **not a revenue band**.

---

## 6. Open Decisions (portfolio-level)

Several 2026-06 open items were resolved by the 2026-07-18 review; kept here for the record.

1. ~~**Lumora vs. Library Framework — 1 project or 2?**~~ **RESOLVED (2026-07-18): 1** — Library Framework folded into Lumora as internal IP.
2. **First vertical for Lumora**: leaning **สายมู** for the sprint (belief-driven, high affiliate conversion) — but record the LIVE-commerce handicap in the KB *before* locking archetype. Decide in one sitting; don't drag into research.
3. ~~**NeurX positioning**: Global vs Thai/SEA-first.~~ **MOOT (2026-07-18)** — NeurX killed as registry; the question no longer applies.
4. **Funding model**: Bootstrap (fail-cheap posture). Note: bootstrap funds **Sin's exit**, not Track B — Track B is a re-underwritten option, not a funded roadmap.
5. **Solo vs. co-founder**: Sin solo. Co-founder question is dormant while Track B is parked.
6. **Day job exit timing**: revenue ≥ salary × 1.5 for 6 months is a **2028+ event** in every credible scenario. Stop implying Year-1 escape velocity — that expectation is what kept 6 projects alive when one should get the oxygen.

---

## 7. Session Etiquette

When a Claude Code session works on one of these projects:

- **Do** load this doc + KB INDEX.md first.
- **Do** use existing subagents in `~/.claude/agents/` — don't create new ones unless skill gap is clear.
- **Do** push back if Sin's instruction conflicts with locked decisions here. Surface the conflict, don't just override.
- **Do** flag when reality (2026) contradicts plans written in 2024.
- **Do** mirror the KB layout used for Lumora: `memory/`, `knowledge/`, `skills/` under `~/Documents/Projects/Agent/company/project_sandbox/{project_name}/`.
- **Do** enforce the **market-contact rule** (§2): no project earns more engineering/docs/KB hours until it completes its own next market-facing action.
- **Do** respect the **hours-tracking directive** (§2) — if actual < 6 hrs/week, rescope the Lumora sprint to 3 posts/week, don't miss silently.
- **Do** honor the AIA **employer IP boundary** (§1) in anything that could become public.
- **Don't** mix project work across sessions.
- **Don't** apply DE/pipeline mindset to the Crypto Engine (it's a builder project, not data eng).
- **Don't** apply SaaS framing to Lumora (it's an agency/MCN).
- **Don't** assume "AI = model" — the unit is agent + workflow + context.
- **Don't** resurrect or spend hours on **killed/parked** projects (NeurX-as-registry, Regent-as-product, SentientNet, Library-standalone). They earn zero hours until their un-park trigger fires (§2 verdicts). Old vision prose is history, not a to-do list.

---

## 8. Living Document

This file should be updated when:
- A locked decision changes.
- An open question gets resolved.
- A new project enters the portfolio.
- Reality shifts (new competitor, new tech) that changes positioning.

Update version date at top whenever modified.

---

*End of master knowledge document.*
