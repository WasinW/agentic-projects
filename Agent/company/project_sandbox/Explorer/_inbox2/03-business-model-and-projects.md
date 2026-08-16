# 03 — Business Model, Solution Design & Business Plan (all 5 projects)

> **REWRITTEN 2026-08-08.** Supersedes all earlier versions of this file.
> Read **file 08** for what changed and why, **file 09** for the criteria used.
> Sources: Lumora KB (00-07 + ADR-0001), library-framework KB, regent-ai KB, neurx KB, sentientnet KB, plus market research 2026-08-07.

---

# PART I — THE SHAPE

## 1. One sentence

**Sin builds one thing — Lumora — which accumulates two durable assets (an audience relationship and operating data). Three further layers exist as designs with observable birth triggers, and are not built until a trigger fires.**

## 2. The compass

**Mission:** make advanced capability belong to everyone and be visible, instead of concentrated and opaque. Shorthand: steer toward **Frutiger Aero**, away from **cyberpunk**.

Both futures have identical technology. Only two things differ: **who has access**, and **whether you can see through it**.

Four engineering forks where the compass decides:
1. Does data live with the user or with us?
2. Open API or locked?
3. Can a customer leave and take their work?
4. Can we explain why the system decided what it decided?

**Not retrofittable.** Built in from day one it costs almost nothing; added at a thousand users it becomes a rewrite that never happens. That is how every company becomes cyberpunk — nobody intends it; transparency simply keeps getting deferred.

## 3. The structure

```
                    COMPASS: Frutiger Aero
                            │
        ┌───────────────────┴────────────────────┐
        │   BUILDING NOW                         │
        │                                        │
        │   LUMORA — community #1 (สายมู)        │
        │   ├── Library Framework (measurement)  │
        │   └── post_log (the data asset)        │
        └───────────────────┬────────────────────┘
                            │
              accumulates two durable layers
                            │
        ┌───────────────────┴────────────────────┐
        │  ① audience relationship               │
        │  ② operating data                      │
        └───────────────────┬────────────────────┘
                            │
    ┌───────────────────────┼───────────────────────┐
    │ WAITING ON TRIGGERS (not built, not named)    │
    │                                               │
    │  marketplace layer   ← outsider asks to sell  │
    │  accountability layer ← agent fails untraceably│
    │  revenue-share layer ← >2 parties to pay      │
    │  ecosystem           ← community #2 exists    │
    └───────────────────────────────────────────────┘
```

**The two durable layers are the business.** Products are duplicated and reused on top of them as each era turns.

## 4. Three-layer status of all five projects

| Project | Model | Model status | Product status | Blocking issue |
|---|---|---|---|---|
| **Lumora** | O&O media + commerce | Alive, building | Phase-1 sprint running | Day-90 gate |
| **Library Framework** | Internal IP | Alive, folded in | Is the measurement layer | None |
| **Regent AI** | Sell accountability | **Model alive** — scarcity increasing | **Product dead** | Buyer unreachable solo |
| **NeurX** | Own the shelf | **Model alive vertically** | **Product dead — killed** | Registry layer consolidated by AAIF; A2A v1.2 absorbed the trust wedge |
| **SentientNet** | Sovereignty | **Model alive** — scarcity increasing | **Product dead — parked** | Sovereign buyer inaccessible; state building its own |

---

# PART II — PROJECT SHEETS

## 2.1 Lumora — O&O MCN + Multi-Catalog Lab

| Field | Value |
|---|---|
| Status | **The only active build** |
| Model | O&O MCN + Multi-Catalog Product R&D Lab ("Ruhnn-Beast hybrid") |
| Umbrella | LUMORA → LABS (tech R&D) · STUDIO (own channels) · AGENCY (Phase 2) · INTELLIGENCE (Phase 3) |
| Catalog #1 | สายมู — the first catalog, not the project |
| Current phase | 90-day publish-or-park sprint. Backend **parked** per ADR-0001 |

### Three pillars
1. **Multi-Channel Creator** — Sin owns every channel; no contracted KOLs. Channel count via `1 ≤ N ≤ S×A` with V1/V2/V3 gates; **default N=1**.
2. **Multi-Catalog Incubator** — catalogs are R&D bets tested on owned channels first.
3. **Multi-Platform Commerce** — affiliate → boutique agency → platform intelligence.

### Business plan

**Phase 1 — B2C, own creator (active)**
- Affiliate: เครื่องราง/จี้ 5-15% · ยันต์/ตะกรุด 5-10% · น้ำมัน/ผง 8-15% · crystal 10-15% · oracle deck 5-10%
- Owned digital products, high margin: AI art prints, oracle deck PDF, journal templates, commissions
- Later: subscription, brand partnerships at 50K+ followers
- Target ~50-200K THB/mo
- **Do not rely on Creator Rewards** — AI-labeled content is excluded, and TikTok Shop commission was cut in 2025

**Phase 2 — B2B boutique agency (frozen until the gate passes)**
- Retainers: Basic ~30-50K · Standard ~70-100K · Premium ~150-250K THB/mo, plus campaign add-ons
- **Agency, not SaaS.** Sin operates the backend; the client buys the outcome. *(Sin's 4th recorded pushback — do not re-introduce SaaS framing.)*
- Target ~300-700K THB/mo. Scales linearly with Sin's time — 3-10 clients per person

**Phase 3 — B2P platform intelligence (year 3+, do not chase)**
- Serve TikTok Shop / Shopee / Lazada. Mostly GMV commission. Needs a 5-10 person team.
- Unlocks only after own channels 50K+, agency running 6+ months, 3+ documented case studies

### Honest constraint on Phase 2
The agency model sells time at a better rate than salary. It does not compound and cannot exist without Sin. **It is a better job, not an asset.** The asset in Lumora is the audience, not the retainer.

### The moat
**Human, not automation.** "AI automation at scale" is a 2026 commodity (Korpi, FlowShorts, AutoShorts, VEO3) and actively suppressed by TikTok enforcement (AI-content enforcement up 340% in 2025). Real differentiation: **AI-art aesthetic + สายมู cultural literacy + Sin's voice, ~70/30 human/AI**, AI-labeled from post #1.

### The recorded handicap
**LIVE commerce.** Thai affiliate conversion concentrates in LIVE, which a faceless channel structurally cannot do. Consequences already priced in: the day-90 gate measures **reach, not GMV**, so faceless can pass — but the archetype must not foreclose showing face and going LIVE later.

---

## 2.2 Library Framework — internal IP and measurement layer

| Field | Value |
|---|---|
| Status | **Folded into Lumora as internal IP, 2026-07-18.** Settled |
| Canonical | Lumora `01_creative_library.md` (v3) |
| Spin-out gate | 12 months **and** framework-attributable channel growth |
| If externalized | Content-led authority. **NEVER SaaS** — recorded twice |

**Two levels.** Account-level (Voice/Archetype, Audience Persona, Niche scope) is the **constraint set** — it decides which combos are legal. Post-level (C × T × M, plus optional JTBD and HHH) is the **decision space** — what varies per post.

**Why it is not a footnote:** the C×T×M tag turns every post into a labelled experiment. Without it, performance data is an undifferentiated pile. **It is the control system for Phase 1.** Full architecture in file 06; feedback loop in file 05.

**On naming it an "analytics platform":** the instinct is right — it *is* the analytics layer — but "platform" pulls toward the self-serve product shape rejected twice. Keep **Library Framework** as the IP name; call the capability **the measurement layer**.

---

## 2.3 Regent AI — accountability model, no product

| Field | Value |
|---|---|
| Model | Sell accountability — **alive, scarcity increasing** |
| Product | Enterprise governance platform — **dead** |
| Status | Parked as product (his ADR, 2026-07-18) + market-confirmed (2026-08-07) |
| Positioning | Serves the **regulated entity**, not the regulator |
| Build gate | ≥1 external user **AND** Lumora Phase-1 revenue |
| Current form | Career capital at AIA + weekend dogfood, ~4 hrs/month |

### Why the product died — four-filter test

| Filter | Result |
|---|---|
| Access or code? | **FAIL** — code only |
| Buyer has budget? | PASS — agentic AI spend ~$201.9B in 2026 |
| First customer without permission? | **FAIL** — procurement, security review, SOC2, 6-18 month cycles |
| Dead if a giant ships it? | **FAIL — already shipped.** Microsoft Agent 365 GA 1 May 2026, $15/user/month |

Per-layer: observability consolidating (Langfuse→ClickHouse Jan 2026; Braintrust ~$800M; Axiom $200M) · policy/permission funded and contested (Oasis Security $120M Series B) · evidence least crowded but occupied (Credo AI, Trustible, Holistic AI, Fairly AI) · category funding ~52% concentrated in ten players.

### What survives and is permitted now
The **dogfood**: PreToolUse policy hook as the runtime enforcement point (agent × tool × scope matrix, spend/rate caps, HITL thresholds) + hash-chained JSONL audit with a verify command. Real protection for Lumora's agents **and** a live demo. Capped ~4 hrs/month.

**Substrate rule: build on Cedar or OPA/Rego. Never invent a policy DSL.** Novelty lives strictly above the substrate — HITL thresholds as first-class policy objects, spend caps as a native primitive, A2A handoff trust gates, cross-vendor provenance.

### Untested product forms — not recommendations, open questions
1. **Bottom-up dev tool** — researched: also closing. Skip.
2. **Sell to the auditor, not the audited** — audit practices need tooling to audit AI. Countable, reachable, no Microsoft product aimed at them. Untested.
3. **Thai-market compliance reporting** — SEC/SET/PDPA/Thai energy standards, structurally different from EU/US. The reachable form. His own ADR names the Thai AI Act mapping as a content/consulting play.
4. **Agent failure data for insurers** — insurers exclude AI risk because they can't quantify it. Someone must produce the actuarial data. **A data business, not software** — and it requires an operating fleet, which Lumora provides.

### IP folded in
From NeurX: signed Agent Cards + provenance, rug-pull re-attestation, confused-deputy/capability-spoofing checks across vendors, capability attestation.
From SentientNet: sovereign deployment as a *feature* — data residency, self-host, sovereign audit under local jurisdiction.

### Correction on record
EU AI Act Art. 12 requires automatic logging and retention; it does **not** literally mandate hash-chaining or tamper-evidence. That reading comes from Art. 12/19 together with Art. 15. Over-claiming the literal version loses credibility with compliance buyers.

---

## 2.4 NeurX — killed as registry; marketplace model survives elsewhere

| Field | Value |
|---|---|
| Model | Own the shelf — **alive vertically, dead horizontally** |
| Product | Neutral global A2A agent registry — **KILLED 2026-07-18** |
| Un-kill condition | **None.** A future trust product is a fresh underwrite inheriting nothing |
| Artifact ledger | 0 code, 0 schemas, 0 prototypes after ~1 year |

**Why:** AAIF/Linux Foundation consolidating the registry layer · A2A v1.2 shipping signed AgentCards natively, absorbing the one defensible wedge · hyperscaler marketplaces owning distribution (Microsoft Marketplace 4,000+ agents at 3% fee) · two-sided cold-start unwinnable solo/part-time · trust overlapping ~80% with Regent. Runtime and Observability cut **permanently**.

**Four positioning questions closed on record:** open-source tooling posture, never hosted closed-SaaS · global DX first if ever revived · **Lumora is Regent's customer-zero, not NeurX's** · sit above official registries, never compete on hosting — and even that is moot for a standalone product.

### What was never tested — the marketplace model at vertical scale
Cold-start is only a problem when you hold **neither** side. Amazon opened Marketplace after it had customers; Shopify opened its App Store after it had merchants. **Both entered from the side they already owned.**

If Lumora grows to several communities with real audiences, Sin holds the demand side. Opening it to outside sellers is then monetising existing demand, not cold-starting.

**Crucially: what gets sold in need not be agents.** Assets, services, physical goods, digital products — anything the community wants. That is broader than NeurX ever was, and it means the layer does not die when "agent" stops being the unit.

**But it is not NeurX.** It is a layer above Lumora with its own trigger. Do not reopen the folder or the name.

---

## 2.5 SentientNet — parked; sovereignty model survives

| Field | Value |
|---|---|
| Model | Sovereignty — **alive, scarcity increasing** |
| Product | Decentralized network, chains, federation, micropayments — **PARKED indefinitely** |
| Un-park gate | **ALL THREE:** Track A sustained cash-flow · Regent has external users · a real sovereign-buyer conversation happened. Any two ≠ un-park |
| Maintenance | **Zero.** No re-research, no refresh. Knowledge frozen, assume stale |

**Why:** micropayments rail decided by others (x402 165M+ txns, 69K agents; Google AP2; Skyfire) — pillar **deleted**, adopt as a consumer if ever needed, never build rails · the sovereign buyer is building its own (ThaiLLM, THB 500B+ cloud pledges) so "nobody owns the sovereign framing" is now false · sovereign procurement wants certifications, local entity, references, BD headcount.

**Salvaged:** the sovereign-deployment angle, donated to Regent as a deployment mode + compliance-mapping dimension — same buyer, ~5 years sooner.

### What was never tested — sovereignty for individuals
The buyer changes completely: no procurement, no SOC2, no BD headcount, no local entity. This is the "personal AI as an owned, inheritable asset" idea. **Sin already runs the prototype** — a 100% local, markdown-only, token-thrifty agent stack.

**Honest caveat:** consumer AI is brutal to monetise and this category has produced little revenue. But the scarcity the model charges for — control and ownership — is *increasing*, unlike NeurX's, which was absorbed into a protocol spec.

### The revenue-share layer
**Corrected differentiator.** "Big clouds don't pay developers" is not accurate in 2026 — platforms take 0-30%, Agensi does 80/20, Microsoft charges 3%, OpenAI pays on usage, eight marketplaces matter as of Q2 2026.

**What survives and is stronger:** platforms **compete with their suppliers**, and developers get per-transaction share without **durable participation** — terms change at will.

**So the pitch is "we don't compete with you, and your share cannot be revoked" — not "we pay more."** An immutable on-chain split delivers exactly that, and incumbents cannot copy it, because copying means surrendering the right to change the rules.

**But blockchain has its own trigger:** it is slower and more expensive than a database in every dimension except one — credible commitment where trust is absent. **Its trigger is a counterparty asking how they can be sure the split won't change.** Until then, use a database.

---

# PART III — SOLUTION DESIGN

## 3.1 What exists today (Phase 1, per ADR-0001)

```
  lumora-trend-scan       → external signal
        ▼
  lumora-combo-recommend  → ranks (C × T × M)
        ▼
  lumora-content-batch    → combo → concept → hook → caption → prompt → hashtags
  lumora-art-prompt       → image spec
        ▼
  Sin's thumb             → MANUAL publish (auto-publisher forbidden)
        ▼
  post_log                → ops tracker AND training data
        ▼
  v_post_scores + weekly ritual → adjusted combo spread ──┐
        └───────────────────────────────────────────────────┘
```

**Infrastructure cost $0. Maintenance 0.** Five skills + Claude Code + a log file + a 10-minute weekly ritual.

## 3.2 The data asset — the only thing that must start now

`post_log` (SQLite or spreadsheet), one row per published post:
- Identity: `post_id` (`L{week}-D{day}`), `brand_id`, `account_handle`, `posted_at`
- **Taxonomy: `content_pillar`, `theme`, `media`** ← the reason any of this works
- Context: `jtbd`, `funnel_stage`, `hook_type` (fixed tag), `ai_labeled`
- Performance: `views_24h`, `views_7d`, `likes`, `comments`, `shares`, `saves`, `follows_delta`, `gmv`
- Derived in `v_post_scores`: `save_rate`, `follow_rate`, `tail_multiple`

**Design rules that must hold:** `hook_type` is a fixed-tag lookup, never free text · column names map 1:1 onto Supabase `posts` + `performance` · `brand_id` from row one even with one brand · **empty beats fake** — unmeasurable fields stay NULL, since this is training data.

**Extend it for the accountability layer:** which agent produced this, which prompt version, what it cost. **Logs cannot be backfilled.**

## 3.3 Parked design worth honouring when code resumes

- **Orchestrator-first, LLM-surgical.** ~95% deterministic (SQL, formulas, rules, $0 token); LLM only where human judgment is genuinely needed. ~100× cheaper than agent-does-everything.
- **Combo scoring is a weighted formula, not ML:** `0.30·trend + 0.25·fit + 0.20·lift + 0.10·recency + 0.10·season − fatigue`. Debuggable, explainable, free.
- **Three seams only:** `brand_id` + Postgres RLS everywhere · Source adapter · Generator adapter. Rule: draw an abstraction only where a second implementation already exists.
- **State machine with two human approval points** (combo → asset) — prevents auto-publish structurally. Includes a `revised` state.
- **Fixed-tag reject reasons** so the scorer learns systematically.
- **Decisions archived, never deleted** — unapproved combos become a weekly-reviewed idea bank.
- **Stack if resumed:** Cloudflare Workers + Hono · Modal · Supabase (Postgres + pgvector, dim 1024 / bge-m3) · R2 · Inngest · Replicate FLUX · Claude API. ~$90-135/mo, hard cap $200. **Deliberately not GCP-native** — IP boundary from the day job.

## 3.4 Resurrection trigger
**≥100 posts published AND a named manual step eating >2 hrs/week.** Both. Then build **only that one adapter**. Likely order of pain: metrics collection → generation → trend scanning. **Publishing: never.**

---

# PART IV — WHAT DOES NOT GET BUILT

| Not built | Reason |
|---|---|
| Agent control plane as Phase-1 work | Violates ADR-0001 rules 1, 2, 4, 5. No agent fleet to govern — production is 5 skills invoked by Sin |
| Any automated publisher | ADR-0001 rule 5. A ban destroys the experiment |
| Regent as a company | Fails 3 of 4 filters; Microsoft shipped 1 May 2026 |
| NeurX in any form | Killed. No un-kill condition |
| SentientNet as a network | Parked. Three-condition un-park gate |
| Multi-tenancy, public API, evidence packs | No second tenant, no auditor, no insurer |
| Renaming any parked project | Motion without information gain; destroys the audit trail |
| Naming layers before their trigger fires | Same pattern as the deferred-skills list, deleted 2026-07-18 |
| A second catalog before the first is proven | His own KB rule |
| Content verticals beyond Lumora | Content is red; Lumora is the exception, driven by personal interest |

---

# PART V — SIDE PLAYS (run alongside, not instead)

Decided 2026-08-07: pursue these as smaller plays alongside Lumora, since the domain knowledge already exists. **Content stays Lumora-only.**

| # | Direction | Start cost | Notes |
|---|---|---|---|
| 2 | Agents over Thai documents and rules | Low — solo, no permission needed | Start here |
| 4 | Agent failure dataset | **Near zero** — a byproduct of logging correctly | Start here; same work as the Regent dogfood |
| 1 | Operational data pipelines for agents | Needs a customer first | Wait for signal |
| 3 | Agents for lagging sectors | Needs access first | Wait for signal |

**Products sellable into the Thai AI-infrastructure buildout** — data centre operators, power producers, industrial estates, electrical contractors; a segment forming now on the back of Q1 2026 BOI applications exceeding THB 1.01tn with digital at THB 873.7bn:
- Compliance and carbon reporting to Thai rules (SEC/SET/PDPA/Thai energy standards) — **the reachable form of Regent**
- Data plumbing for operational telemetry — SCADA/BMS/meters → warehouse → reporting
- Predictive maintenance on 2-3 year lead-time equipment
- Interconnection and capacity intelligence — scattered across ERC/BOI notices, nobody aggregating

All four pass Filter 1: **the source data is not on the internet, and it is in a language Sin reads.**
