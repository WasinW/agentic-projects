# 00 — INDEX & SITUATION BRIEF

> **Read this first.** Written for a local agent picking up this work with no prior context.
> Sessions covered: 2026-08-05 → 2026-08-09.

---

# THE MOST IMPORTANT THING

**There are TWO separate workstreams in this folder. Do not merge them.**

| | **Workstream 1 — THE BUILD** | **Workstream 2 — EXPLORATION** |
|---|---|---|
| What | Lumora and its deferred layers | AI-ecosystem map for investing |
| Status | Active, governed by binding ADRs | Pure exploration, tied to no project |
| Files | 01-06, 08, 09 | 07, 10-16 |
| Rule | ADR-0001s are binding; do not violate | Nothing here obligates any build |

**Workstream 2 exists to find opportunities, not to create work.** If it surfaces a good idea, that gets discussed separately as a possible project. If nothing is worth building, the outcome is simply: invest in those companies. **Do not fold the stock map into the Lumora plan.**

---

# WORKSTREAM 1 — THE BUILD

## Current state, one paragraph

**Not five projects. One thing being built.** Lumora — an accumulator for two durable assets: an audience relationship and operating data. Library Framework is its measurement layer, folded in as internal IP. Three further layers exist as designs with observable birth triggers and consume zero hours now: marketplace, accountability, revenue-share. NeurX is killed, SentientNet parked, Regent parked as a product — all by Sin's own ADRs dated 2026-07-18.

## Binding constraints — violating these is the main failure mode

**Lumora ADR-0001 (2026-07-18):**
1. No new adapter until ≥100 posts published **AND** a named manual step eats >2 hrs/week
2. Phase-1 pipeline = 5 skills + Claude Code + manual posting. That is the whole system
3. The only backend needed is a per-post log (spreadsheet or SQLite)
4. All Phase 2/3 work frozen — thinking **and** architecture
5. **Never** build or use an unofficial auto-publisher

**Regent ADR-0001 (2026-07-18):** parked as a product. Permitted: career capital + a ~4 hrs/month dogfood (PreToolUse policy hook + hash-chained JSONL audit). Build on Cedar or OPA — **never invent a policy DSL.** Build gate: ≥1 external user **AND** Lumora Phase-1 revenue.

**NeurX ADR-0001:** killed, not parked. No un-kill condition. Any future trust product is a fresh underwrite inheriting nothing.

**SentientNet:** parked indefinitely. Un-park needs **all three** of Track A cash-flow, Regent external users, and a real sovereign-buyer conversation.

> **An earlier version of file 04 violated four of Lumora's five hard rules at once.** It has been rewritten. If any plan here seems to require building a control plane, event log, policy engine, or publisher — stop and re-read the ADR.

## The only action the deferred layers require today

**Log correctly from post #1.** Audience is already accumulating; transaction records arrive with the marketplace; **logs cannot be backfilled.** That is the entire present-day obligation.

## Reading order

| # | File | Read it for |
|---|---|---|
| **08** | Decision & Change Log | **Read before trusting any other file.** 17 requirements changed, with causes |
| **09** | Criteria & Frameworks | The portable part. Survives every project being cancelled |
| **03** | Business Model & Solution Design | All 5 projects, model/product/strategy separated |
| **04** | Phases, Requirements & Architecture | Built on ADR-0001. Phase 1 = post_log only |
| **05** | Library Framework & Feedback Loop | The measurement layer; the C×T×M control loop |
| **06** | Library Framework Architecture | Schema-level; marked [KB]/[INF]/[GAP] for review |
| **02** | Notes Register | Working notes, market reality check §G, KB findings §H |
| **01** | Chat History | Full record, 28 threads |

---

# WORKSTREAM 2 — EXPLORATION

## Purpose

Map the AI ecosystem broadly enough that nothing gets missed, then filter with criteria that can change. **Exploration only.** Output is either an investment list or, occasionally, an idea worth discussing as a build.

## Architecture — lakehouse, three layers

```
BRONZE  files 14 (80 groups) + 15 (1,185 entities, CSV)
        Everything. Including what was called red, dead, or unbuyable.
        No filtering at ingest, ever.

SILVER  file 16
        Criteria as data — id, definition, weight, date.
        Change a weight, re-run. Never edit BRONZE.

GOLD    views at the end of file 16
        Derived. Disposable. Regenerate freely.
```

**Why:** judging and discarding in one pass sets a thing's future probability to zero permanently. By the time it matters, the data is gone. This is the same failure as "right direction, 18 months late," which has already happened twice.

## Verification protocol — READ THIS BEFORE TOUCHING BRONZE

**Verify and validate. Never filter out.**

| Action | Allowed? |
|---|---|
| Correct a wrong ticker, exchange, or status | ✅ Yes |
| Add a missing entity | ✅ Yes |
| Add `source`, `confidence`, `as_of` | ✅ Yes — **required** |
| Update `buy` status when a company lists, is acquired, or is restricted | ✅ Yes |
| Remove a row because it "isn't relevant" | ❌ **Never** |
| Remove a row because it's unbuyable, dead, or acquired | ❌ **Never** — change `buy` to `absorbed` / `foundation-family-state` and keep it |
| Filter to a shortlist inside BRONZE | ❌ **Never** — that belongs in GOLD |

**Empty beats fake.** Leave a field null rather than guessing. An agent filling 1,185 rows will produce confident-looking wrong data unless `source`/`confidence`/`as_of` are enforced — and bad BRONZE silently corrupts every SILVER query built on it.

**Known error rate:** file 07 found 9 wrong entries in a 100-name source list. Assume ~9% here. The data is designed to be corrected in place, not to be right first time.

## Exploration file map

| # | File | Contents |
|---|---|---|
| **14** | BRONZE groups | 80 groups × business model, product, customer, depends_on, owns, buyability, data location, scarcity trend |
| **15** | BRONZE entities | 1,185 rows CSV. live 712 · restricted-access 256 · private-ipo-watch 127 · foundation-family-state 43 · policy-restricted 28 · absorbed 19 |
| **16** | SILVER criteria + GOLD views | Criteria register with weights; chokepoint view, BD-4 intersection, IPO watchlist, access vehicles |
| **13** | Buyability & IPO watchlist | The six-status taxonomy, proxies for unbuyable names, access vehicles |
| **12** | Missing groups & deep upstream | 13 groups added, incl. edge AI, ASML-tier suppliers, EUV exotic materials |
| **11** | Expanded checklist | 10-20 names per group, narrative form |
| **10** | Sector map | The three structural findings; 67 → 80 group build-up |
| **07** | Original checklist verification | Found 5 delisted + 4 non-investable in a 100-name list |

## Three structural findings worth keeping

1. **Copper is the story, not chips.** ~82-83% of AI data-centre mineral demand, with grid infrastructure taking two-thirds of that. The binding constraint is processing and refining capacity, not geology.
2. **The deeper upstream you go, the less investable it becomes.** Zeiss, TRUMPF, Schott, Heraeus, VDL, Sibelco — foundation- or family-owned, never listing. ASML is the aggregation point.
3. **Unbuyable chokepoints are build-space.** Proven demand that capital cannot enter through the market. Criterion BD-1 in file 16 detects this automatically.

---

# HOW THE TWO WORKSTREAMS CONNECT

**Only through one criterion: BD-4 in file 16** — `data = inside` **AND** Thai-readable.

That intersection produces the Thailand groups (G1-G5) and four products sellable into the Thai AI-infrastructure buildout. **That is the only place the exploration is allowed to generate build candidates**, and even then it produces a discussion, not a commitment.

Everything else in Workstream 2 stays an investment question.

---

# STANDING DISCIPLINES

- A list of skills never scaffolded is fake progress, not an asset. Same for named projects with no artifact.
- A parked project carries **zero** recurring maintenance — no re-research, no refresh.
- A dead thing stated clearly is cheaper than a dead thing left ambiguous.
- **Do not rename parked projects.** Renaming is motion without information gain and destroys the record of why they died. Name unborn layers by function; name them when a trigger fires.
- Don't validate more than one catalog at once.
- Wait for the second use case before extracting or abstracting anything.
- **Read the canonical docs before specifying anything.** The largest errors in this folder all came from reasoning without reading source documents.
