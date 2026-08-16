# 03 — Business Model & Project Design

> Ecosystem design as agreed on 2026-08-05.
> Scope: Lumora, Library Framework, Regent AI, NeurX, SentientNet.
> Out of scope: Crypto Trading Engine (personal investing tool), anything involving the employer.

---

## 1. The compass

**Mission:** make advanced capability belong to everyone and be visible, instead of concentrated and opaque.

Shorthand: **steer toward Frutiger Aero, away from cyberpunk.** Both futures have identical technology. Only access and transparency differ.

Every project below must be checkable against four questions:
1. Does the user own their data, or do we?
2. Can they leave and take their work?
3. Can we explain why the system decided what it decided?
4. Is the capability we built available to a small player, or only to us?

---

## 2. The ecosystem in one paragraph

**Lumora is a real content business that makes money.** Running it requires controlling a fleet of agents with revenue attached, which forces the construction of a control plane. **That control plane is the seed of Regent AI.** When outside parties want in — third-party agents, external revenue splitting — **NeurX and SentientNet** become justified. Nothing in Track B is built speculatively; each emerges under real pressure from the layer below.

```
                         COMPASS: Frutiger Aero
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
   TRACK A (revenue)        THE BRIDGE              TRACK B (vision)
        │                         │                         │
   ┌────┴─────┐          ┌────────┴────────┐     ┌──────────┴──────────┐
   │ Lumora   │─────────▶│  Control Plane  │────▶│  Regent AI          │
   │          │  forces  │  (inside Lumora │split│  (governance/audit) │
   │ Library  │─────────▶│   phase 0-1)    │     └──────────┬──────────┘
   │ Framework│          └─────────────────┘                │
   └──────────┘                                   pressure from outside
                                                            │
                                              ┌─────────────┴────────────┐
                                              │                          │
                                        ┌─────┴─────┐          ┌─────────┴────────┐
                                        │  NeurX    │          │  SentientNet     │
                                        │ (registry)│          │ (revenue split)  │
                                        └───────────┘          └──────────────────┘
```

---

## 3. Project sheets

### 3.1 Lumora — AI-automated MCN / production house

| Field | Value |
|---|---|
| Track | A (revenue) |
| Type | Operating business, not a platform |
| Status | Build first, everything else waits |
| Phase 1 vertical | Spiritual/lifestyle content — legend-telling, location reviews — distributed across media platforms; monetised via affiliate on bracelets, auspicious stones, consecrated items, Ganesha figures |
| Later verticals | PC building, others TBD |
| Ownership model | Sin owns the content; no external creators in phase 1 |

**What it actually is:** a content production house where agents do the work. A back-end marketing platform covers strategy planning, content production, and analytics. Content volume exists partly to PoC the market.

**Why it matters strategically — three things, in order of importance:**
1. **Revenue that removes the need to fundraise.** Preserves control of direction, which matters enormously for a mission-driven founder.
2. **A real system to point at.** "I have run an agent fleet with real money attached for two years" is a credential no deck can substitute for.
3. **Understanding of what agent control problems actually look like** — which cannot be known in advance.

**What it does NOT provide:** validation of Regent's market. Different buyer entirely.

**Success test at 6 months:** Lumora has real users/revenue and NeurX does not exist yet. That is success. Three complete platforms and no users is failure.

---

### 3.2 Library Framework — content taxonomy

| Field | Value |
|---|---|
| Track | A |
| Type | Internal structure now; possible analytics platform later |
| Status | Build alongside Lumora as internal infrastructure |

**What it is:** the taxonomy system that makes content reproducible and reusable across Lumora's output.

**Spin-out path:** could become a marketing analytics company. If so, it becomes a Regent customer in its own right — but only under the same rule as everything else: **wait for the second use case.**

---

### 3.3 Regent AI — agent governance and audit

| Field | Value |
|---|---|
| Track | B (vision) |
| Type | Control plane → product |
| Status | Built inside Lumora during phase 0-1 as an isolated module; split when a second real user exists |
| Buyer | Risk officer / CTO at an organisation deploying agents and bearing liability |
| Name | **Lock as "Regent AI."** "RegentX" is not the record name. |

**Core thesis — why this survives the death of "agents":** what endures is not the word "agent" but the problem that **self-deciding software needs identity, permissions, boundaries, and audit trails.** Whatever it is called in ten years — agent, worker, process — as long as it acts autonomously and someone bears liability, the problem persists and grows. This is the difference between selling a registry of objects (dies with the object) and selling accountability (persists).

**Market context:** state regulation is being actively blocked — hundreds of millions in super PAC and lobbying spend in the US; the EU Digital Omnibus pushed high-risk AI obligations from August 2026 to December 2027/August 2028 under industry pressure. **This is bullish, not bearish, for private assurance:** organisations must still manage risk but have no state standard to anchor to, so they buy privately. The 2026-2028 gap is the window.

**Positioning rule:** do not stand on the side that forbids people. Stand on the side that lets people act with confidence. Same technology, different customer, and nobody lobbies against the party they are paying.

**Scope — see file 04 for the four layers in detail.**

---

### 3.4 NeurX — agent registry / runtime

| Field | Value |
|---|---|
| Track | B |
| Type | Marketplace + registry/runtime |
| Status | **Deferred.** Do not build in phase 0-1. |

**Honest assessment:** as a marketplace this loses. Marketplaces are the worst business for a small player — two-sided chicken-and-egg, high winner-take-all dynamics, impossible without prior distribution. Sin has no market share and no existing customer base, and is late versus AWS/GCP/Azure.

**But three distinct businesses were being conflated:**

| Form | Requirement | Verdict |
|---|---|---|
| **Marketplace** | Liquidity on both sides | Loses. Can drop. |
| **Protocol / standard** | Be first and neutral; value accrues from what others build on top | Viable — doesn't need many customers |
| **Tool** | Sells to one customer at a time; no network effect needed | Viable immediately |

**Trigger to build:** an outside party wants to sell their agent to other users inside your system. Not before. Building a marketplace before demand exists produces an empty marketplace — the exact failure already diagnosed.

**Alternative framing worth keeping:** third-party layer on top of hyperscalers. This is not a consolation prize — Databricks, Snowflake, Datadog, Stripe, HashiCorp and Confluent all built enormous businesses sitting *on* AWS/GCP/Azure rather than competing with them. Clouds sell raw resources and deliberately avoid hard, small-TAM specialised problems.

---

### 3.5 SentientNet — sovereign agent network / revenue sharing

| Field | Value |
|---|---|
| Track | B |
| Type | Decentralised revenue-sharing layer, blockchain-based |
| Status | **Deferred.** Last in sequence. |

**Trigger to build:** real money flowing between multiple parties in volumes that can no longer be split manually. It should exist because there is revenue to divide, **not because blockchain is interesting.**

**Design caution:** the value is transparent multi-party attribution, not decentralisation for its own right. If a database solves it at current scale, use a database and keep the interface clean enough to swap later.

---

## 4. Business model

### 4.1 Revenue flow

**Phase 0-1 — Lumora only**
- Affiliate commission on spiritual/lifestyle goods
- Content platform monetisation across media platforms
- Possible direct supplier partnerships

**Phase 2 — Regent split out**
- Subscription per agent fleet under management, or per governed action
- Evidence pack generation as a premium tier
- Design target: the buyer is the party bearing risk — a CFO or risk officer signing off on agent deployment

**Phase 3 — ecosystem**
- NeurX: take rate on third-party agents transacting in the system
- SentientNet: settlement fee on multi-party revenue splits
- New operating companies per vertical, each becoming a Regent customer

### 4.2 The venture studio model — and its trap

Sin's expansion model: spin up operating companies per vertical (interior design built on designer agents; Library Framework as a marketing analytics company), each becoming a Regent customer, with Lumora as customer #1.

**This is a real model. The trap is that customers you own are not evidence you can sell.** In-house companies never refuse, never negotiate price, never churn, never say a feature is bad. The result is a control plane that fits you perfectly and nobody outside will buy. AWS escaped this only because Amazon Retail was a brutal, enormous, demanding customer whose internal problem happened to match the world's. Sin's companies will all be small — a control plane that handles ten agents well says nothing about enterprise scale.

**Hard gate: acquire one external paying customer who is not yours before splitting any company out.** One customer who can complain is worth more than five in-house companies.

**Second trap — vertical proliferation.** Spiritual content, PC building and interior design share suppliers, customers, rules and sales motions far less than they appear to. Only the agent stack is genuinely shared. Opening too fast yields five shallow companies instead of one deep, profitable one.

### 4.3 Why this sequence and not the reverse

Every successful platform emerged from a concrete product, never the other way round:

| Platform | Emerged from |
|---|---|
| AWS | Internal infrastructure for Amazon's own retail operation |
| Databricks | Spark, built by a team solving their own problem |
| Confluent | Kafka, built for internal use at LinkedIn |
| Shopify | A snowboard shop that couldn't find good software |

**Nobody built a platform and waited for people to plug in. Everyone built one thing extremely well and the platform fell out of it.**

Corollary for fundraising: nobody funds a platform with no users. They fund a **product with paying customers.** Ten paying creators makes any conversation possible; three platforms with no users leaves nothing to say. And if Lumora makes real money, fundraising may be unnecessary — which is better, because it preserves control of direction.

---

## 5. What has been rejected and why

| Rejected | Reason |
|---|---|
| Insurance / employer as a business angle | Out of scope by explicit instruction. Day job is technical growth and income only. |
| NeurX as a first build | Empty marketplace. No distribution, no liquidity, too late versus hyperscalers. |
| Building Regent standalone from day one | Cannot design a control plane before having something to control. Design would come from imagination and be wrong. |
| Building all platforms in parallel | Turns "do one thing" into "do four things" — heavier than the original plan and the exact failure already diagnosed. |
| Regulator-as-police positioning | Conflicts directly with incumbent interests; evidence shows such efforts get crushed by lobbying and legislative rollback. |
| Frutiger Aero as a later feature | Cannot be retrofitted. Near-zero cost now; full rewrite at a thousand users, which means it never happens. |
