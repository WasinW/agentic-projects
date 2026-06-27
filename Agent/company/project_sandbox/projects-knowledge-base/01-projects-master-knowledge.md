# Sin's Projects Knowledge Base

> **Version**: 2026-06-27
> **Owner**: Sin (วศิน วังสมบัติ / ภัค)
> **Purpose**: Master context document for individual project sessions. Every project-specific session should load this first to understand the portfolio, then focus on its assigned project.

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

- **Role**: Data Engineer at The1 (Central Group Thailand). Day job is GCP-heavy: Apache Beam/Dataflow, BigQuery, Bigtable, Pub/Sub, Cloud Composer, Iceberg/BigLake, Kafka, Terraform.
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

---

## 2. Portfolio Overview

Sin runs **two tracks in parallel**:

### Track A — Commercial / Cash Flow
Projects that generate revenue or could in 1-3 years. Job: fund the vision track and reduce dependence on full-time employment.

- **A1. Lumora** — O&O Multi-Channel Network for Thai creators (AI-automated)
- **A2. Library Framework** — Generalizable content taxonomy + production system
- **A3. Crypto Trading Engine** — Personal trading tool, not a product

### Track B — AI Ecosystem Vision
Long-term bets reframed for the agentic era. The original 2024 versions assumed "AI = model" — that assumption is now obsolete. Reframed below.

- **B1. NeurX** — Agent Infrastructure & Registry
- **B2. Regent AI** — Agent Governance & Trust Layer
- **B3. SentientNet** — Sovereign / Decentralized Agent Network

### Why both tracks at once

Track A → real revenue, real users, real product feedback. Lumora especially serves as **prototype customer** for Track B (uses agents, needs governance, eventually wants sovereignty over its data).

Track B → defines where the company is going. Without it, Sin becomes a one-off content business owner. With it, he's building toward a platform.

---

## 3. Project Track A: Commercial

### A1. Lumora — O&O MCN for Thai Creators

**One line**: AI-automated holding company that owns multiple content channels across Thai cultural verticals.

**Status**: Active. Most-developed framework so far.

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
- **Phase 1**: Solo creator, 3 accounts owned by Sin. Target 50-200K THB/month. Budget $80-150/mo.
- **Phase 2**: Boutique agency. Take on clients at 30-150K THB/month retainer. Target 300-700K THB/month.
- **Phase 3**: Platform Intelligence Service. Sell directly to TikTok Shop / Shopee / Lazada. Six service types defined (creator discovery, trend intelligence, campaign mgmt, audience insights, content licensing, MCN partnership).

**Locked decisions**:
- Agency model, NOT SaaS.
- Sin's first 1-3 accounts are his own, not clients.
- AI-native from day one, not retrofit.

**Open questions**:
- First vertical to launch? (สายมู? อาหาร? — needs validation)
- Voice/persona strategy per channel (still using Library Framework axes)
- Tech stack: which agent framework, which model APIs

**Connection to Track B**: First customer of NeurX (agent infra), governed by Regent, eventually sovereign via SentientNet.

---

### A2. Library Framework — Content × Theme × Media

**One line**: A generalizable taxonomy + production system for AI-driven content, where Lumora is the first customer.

**Status**: Designed inside Lumora, but conceptually separable.

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

**Status**: Active personal builder project. Specs locked, Step 1 implementation pending.

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

**Old vision (deprecated)**: AI model marketplace. Dead because Hugging Face + Replicate + Together + Fireworks + OpenRouter own that space.

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

**Old vision (deprecated)**: Model explainability + AI ethics platform. Crowded space (Credo, Fiddler, Arize, W&B).

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

**Old vision (deprecated)**: Federated learning + decentralized compute + AI DAO + token economy. Crypto/Web3 framing.

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

**Key sequencing insight**: Track A funds Track B. Lumora needs to hit Phase 1 revenue (50-200K THB/month) before NeurX/Regent receive serious development time. SentientNet stays as vision document until NeurX has users.

---

## 6. Open Decisions (portfolio-level)

These are unresolved at the portfolio level and may come up in any session:

1. **Lumora vs. Library Framework — 1 project or 2?** Currently treated as 2. Sin may merge back. Sessions should ask before assuming.
2. **First vertical for Lumora**: สายมู, อาหาร, ท่องเที่ยว, gadget, art, สุขภาพ — undecided.
3. **NeurX positioning**: Global compete or Thai/SEA-first.
4. **Funding model**: Bootstrap vs. raise. Currently bootstrap (Track A funds Track B), but may change at Phase 2 of Lumora.
5. **Solo vs. co-founder**: Sin currently solo. Co-founder need will emerge if NeurX/Regent grow into real products.
6. **Day job exit timing**: Track A revenue threshold for quitting The1. Not yet locked.

---

## 7. Session Etiquette

When a Claude Code session works on one of these projects:

- **Do** load this doc + KB INDEX.md first.
- **Do** use existing subagents in `~/.claude/agents/` — don't create new ones unless skill gap is clear.
- **Do** push back if Sin's instruction conflicts with locked decisions here. Surface the conflict, don't just override.
- **Do** flag when reality (2026) contradicts plans written in 2024.
- **Do** mirror the KB layout used for Lumora: `memory/`, `knowledge/`, `skills/` under `~/Documents/Projects/Agent/company/project_sandbox/{project_name}/`.
- **Don't** mix project work across sessions.
- **Don't** apply DE/pipeline mindset to the Crypto Engine (it's a builder project, not data eng).
- **Don't** apply SaaS framing to Lumora (it's an agency/MCN).
- **Don't** assume "AI = model" — the unit is agent + workflow + context.

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
