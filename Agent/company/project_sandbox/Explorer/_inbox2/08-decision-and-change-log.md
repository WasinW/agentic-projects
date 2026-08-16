# 08 — Decision & Change Log

> Every requirement that changed during the 2026-08-05 → 2026-08-08 sessions, with the cause.
> Read this before trusting any earlier file. Where a file was superseded, the correction is listed here first.

---

## Legend

| Cause code | Meaning |
|---|---|
| **C1** | Claude reasoned without reading the source documents |
| **C2** | Market research contradicted an earlier assumption |
| **C3** | Sin corrected a misreading of his own plan |
| **C4** | A binding ADR of Sin's was discovered that the plan violated |
| **C5** | A distinction was drawn that hadn't been drawn before (no one was wrong; the analysis got finer) |

---

## CHANGE-01 — Insurance / employer removed from scope
**Was:** an "insurance → civilization risk model" business idea, proposed on the grounds that Sin works at a regulated insurer.
**Now:** out of scope permanently. The day job provides technical growth and income only.
**Cause:** C3. Sin's employer is not part of his business model.
**Affects:** file 01 thread 7, file 02.

---

## CHANGE-02 — Regent AI: from "future company" to "no product build"
**Was:** the control plane grows into a sellable governance company; the assurance market ($0.6B → $23B) was cited as an opening.
**Now:** no product build. Not a standalone company.
**Cause:** C2 + C4.
- Four-filter test fails 3 of 4: the edge is code not access; no first customer reachable without enterprise procurement; Microsoft Agent 365 reached GA 1 May 2026 at $15/user/month.
- Layer-by-layer the category is consolidating: Langfuse acquired by ClickHouse Jan 2026; Braintrust ~$800M; Axiom raised $200M; Oasis Security took $120M Series B for exactly the policy/permission layer. Top ten hold ~52% of category funding.
- **And Sin's own Regent ADR-0001 (2026-07-18) had already parked it**, three weeks before this research.
**Method error to not repeat:** the original recommendation cited market size and growth without checking who occupies the position. TAM without competitive structure is not analysis.
**Affects:** file 02 §G, file 03 §3.3, file 04 (rewritten).

---

## CHANGE-03 — The control plane: from Phase-1 build to not-built
**Was:** file 04 specified an event log, policy engine, SDK enforcement wrapper, halt mechanism, approval gates, evidence packs — hundreds of hours of new code — as Lumora Phase 0-1 work.
**Now:** retracted in full. Phase 1 builds a per-post log and nothing else.
**Cause:** C4. **Lumora ADR-0001 (2026-07-18) was violated on four of its five hard rules simultaneously:** no new adapter until ≥100 posts AND a named manual step >2 hrs/week (rule 1); Phase-1 pipeline is the 5 skills + Claude Code + manual posting (rule 2); all Phase 2/3 work frozen including architecture (rule 4); never an unofficial auto-publisher — yet `platform.post.create` was drafted as an agent capability (rule 5).
This was the exact "factory before the first product" trap that ADR was written to prevent.
**Affects:** file 04, fully rewritten.

---

## CHANGE-04 — Library Framework: from "footnote / possible analytics platform" to "the measurement layer"
**Was:** described as internal structure that might spin out as an analytics platform.
**Now:** folded into Lumora as internal IP on 2026-07-18 — a settled decision, not an open question. Canonical file is Lumora's `01_creative_library.md`. Spin-out gated at 12 months **and** framework-attributable channel growth. If ever externalized: content-led authority, **never SaaS** — recorded twice in his own docs.
**Cause:** C1 + C3. Sin pushed back that the proposed control plane had no mechanism for taking channel feedback into analytics — which is precisely what Library Framework does.
**The substantive correction:** the C×T×M tag on every post is what turns content into labelled experiments. `post_log` → `v_post_scores` → weekly review → adjusted combo spread. **That loop is the control system for Phase 1** — not agent permissions.
**Affects:** file 05 (created for this), file 03 §3.2.

---

## CHANGE-05 — Sprint settings: from "decided" to "recommended"
**Was:** channel @มูมีแสง, archetype Explorer × Magician, pillars C2/C1/C6/C9 stated as locked.
**Now:** these come from a recommendation package that says outright Sin makes the final call. Lumora's `CLAUDE.md` and `INDEX.md` still list as PENDING: channel name + bio + visual identity · voice positioning · archetype (weigh the LIVE-commerce handicap) · first 30-day batch · affiliate-first vs digital-product day 1 · show face on camera.
**Cause:** C1.
**Affects:** file 04 Part II.

---

## CHANGE-06 — Employer staleness claim, half-retracted
**Was:** "the Lumora KB is stale on the employer change."
**Now:** `CLAUDE.md` is current — Senior DE at AIA, Azure Databricks + Kafka/Strimzi/Debezium, IP boundary naming AIA. Only `knowledge/00_overview.md` still says The1 with a GCP/Beam/BigQuery stack.
**Cause:** C1.

---

## CHANGE-07 — NeurX and SentientNet: from "Claude recommends cancelling" to "already killed/parked by Sin"
**Was:** presented as a research finding.
**Now:** Sin killed NeurX and parked SentientNet on **2026-07-18**, with sharper reasoning than the later research produced — AAIF/Linux Foundation consolidating the registry layer, A2A v1.2 shipping signed AgentCards natively (absorbing the trust wedge), hyperscaler marketplaces owning distribution, two-sided cold-start unwinnable solo. NeurX is a **kill, not a park** — no un-kill condition exists.
**Cause:** C1. The research arrived three weeks late and added nothing.

---

## CHANGE-08 — Regent positioning: not a regulator
**Was:** written ambiguously as "governance/audit," readable as Sin building a regulatory authority.
**Now:** Regent serves the **regulated entity** — helping it prepare and deliver what the regulator requires. The buyer bears the compliance burden; it is not the authority.
**Cause:** C3.
**Note:** this does not change CHANGE-02. What blocks it is buyer reachability, not positioning.

---

## CHANGE-09 — The "plug Regent into Lumora" concept: Claude's, not Sin's
**Was:** written as though it were the existing plan.
**Now:** it is a new, unrefined idea originating in this conversation. Sin has not decided whether it would attach to Lumora or to Library Framework.
**Cause:** C3.
**Partial credit:** the seed exists in Sin's own docs — Regent ADR §(b) says the dogfood is "real protection for Lumora's content agents *and* a live Regent demo," and NeurX ADR answers "Lumora is Regent's customer-zero, not NeurX's." But "Regent as a module inside Lumora" went further than either document says.

---

## CHANGE-10 — Structure inverted: Regent is the platform, Lumora is community #1
**Was:** Regent as a module inside Lumora.
**Now:** Sin's actual model — Regent AI as the platform, Lumora as community #1 (สายมู content agents). More communities added over time, each owned by him.
**Cause:** C3.
**Consequence:** the "plugging into a zero-user platform" criticism partly falls away, because Lumora is a tenant rather than the destination. What remains true is that internally-owned tenants prove the tool works, never that a market will buy.

---

## CHANGE-11 — From "the projects are dead" to "the models live, the products died"
**This is the largest change in the whole set.**
**Was:** repeated verdicts that NeurX, SentientNet and Regent were dead.
**Now:** three layers must be separated before judging anything:

| Layer | Lifespan | Verdict |
|---|---|---|
| **Business model** | Many eras | **All three survive.** Each charges for a scarcity that is *increasing* |
| **Product** | One era | All three died. Correctly. |
| **Strategy** | Changeable | The shared error: **buyers Sin cannot reach** |

- Marketplace charges for **matching** — dead horizontally, still scarce vertically
- Sovereignty charges for **control and ownership** — becoming *more* scarce
- Accountability charges for **someone to bear liability** — becoming more scarce as agents proliferate

**Cause:** C5 — and Sin's insistence. Earlier answers judged at product level and never separated the layers.
**The one strategy change that follows: lock the reachable buyer, let the product change with the era.** Reachable = himself, his own audience, individuals, small Thai firms, audit practices.

---

## CHANGE-12 — Product framing: "disposable" → "duplicate and reuse"
**Was:** make the product disposable, keep the buyer relationship and data durable.
**Now:** the product layer is duplicated and reused, not discarded — throwing away a product throws away its revenue too.
**Cause:** C3. Sin's framing is better.

---

## CHANGE-13 — Revenue-share differentiator sharpened
**Was:** "big clouds don't share revenue with developers."
**Now:** not accurate for 2026. Developer platforms take 0-30%; Agensi does 80/20 for creators; Microsoft Marketplace charges 3%; OpenAI GPT Store pays on usage; eight marketplaces already matter as of Q2 2026.
**What survives, and is stronger:** platforms **compete with their suppliers** (the Sherlocking problem), and developers get per-transaction share without **durable participation** — terms can change at any time.
**So the pitch is "we don't compete with you, and your share cannot be revoked," not "we pay more."** That is precisely what an immutable on-chain split provides — and it is the one thing incumbents cannot copy, because copying means surrendering the right to change the rules.
**Cause:** C2.

---

## CHANGE-14 — From "5 projects" to "1 build + 3 triggered layers"
**Was:** five projects, variously alive, parked or dead.
**Now:** **Building: Lumora** (audience + operating-data accumulator, Library Framework as its measurement layer). **Waiting on triggers:** marketplace layer · accountability layer · revenue-share layer. **Ecosystem** arrives with community #2.
**Cause:** C5.
**Why it matters:** the substance is identical, but it consumes none of the 6-10 hrs/week now. Naming things that don't exist is the same pattern as the deferred-skills list Sin deleted on 2026-07-18 — "a list of skills never scaffolded is fake progress, not an asset."
**Decision taken:** **do not rename the parked projects.** Renaming is motion without information gain, makes dead things feel alive, and destroys the audit trail of why they died. NeurX's own ADR requires any future trust product to be a fresh underwrite inheriting nothing — a new name today would be inheritance in disguise. Refer to future layers by function until a trigger fires; name them then.

---

## CHANGE-15 — Only one thing must start now
**New finding.** The three deferred layers differ by whether their raw material can be collected retroactively:

| Layer | Raw material | Backfillable? |
|---|---|---|
| Marketplace | Audience | Already accumulating via Lumora |
| Revenue-share | Transaction records | Arrives with the marketplace |
| **Accountability** | **Logs** | **No — uncaptured logs are lost permanently** |

**Therefore the only action the deferred layers require today is logging correctly from post #1.** Not building a system — capturing which agent did what, when, with what result.
**Cause:** C5.

---

## CHANGE-16 — Blockchain has its own trigger
**Was:** blockchain treated as the revenue-share implementation.
**Now:** blockchain is always slower and more expensive than a database. What it provides is **credible commitment where trust is absent.**
**Its trigger is therefore not "there is money to split" but "a counterparty asks how they can be sure the split won't change."** Until someone asks that question, a database is better in every dimension.
**Cause:** C5.

---

## CHANGE-17 — Investment framing: from stock picks to ecosystem map
**Was:** answered "which stocks are worth buying" with a consensus-bullish market summary sourced partly from trading-platform content marketing — while simultaneously warning against exactly those sources.
**Now:** Sin's purpose is **broad diversification across the AI ecosystem, then narrowing** — a checklist to explore, not recommendations. His method: small equal-weight first tranche across all candidates, then research decides what scales.
**Delivered instead:** file 07 — verification of the source list (5 dead tickers, 4 non-investable entries out of 100) plus 9 missing tiers.
**Cause:** C3.

---

## Still open

1. Which channel name, archetype, and first 30-day batch Sin actually locks
2. Whether "community" ever comes to mean external creators — it currently does not, and doing so would collide with the O&O model and the never-SaaS decision
3. `01-batch-30day.md` and the five Lumora skills have not been read
4. `knowledge/00_overview.md` employer detail needs a one-line fix
5. `content-taxonomy/SKILL.md` still carries two drifts the canonical corrected: the frontmatter `description` advertises `MIN(S,A)≤N≤S×A`, and HHH appears as Hero/Hub/**Help** instead of **Hygiene**. The description matters most — it is what an agent reads when deciding whether to invoke the skill
