# 16 — SILVER: Criteria & Priority Layer

> **Criteria as data, not as logic buried in someone's head.** Change a weight here and re-run — never edit BRONZE.
> BRONZE = files 14 (80 groups) + 15 (1,185 entities, CSV). GOLD = the views at the end of this file, all of which can be thrown away and regenerated.

---

## Why the layers are separated

Judging and discarding in one pass sets a thing's future probability to zero permanently. By the time it turns out to matter, the data is gone and has to be re-collected — which is the "right direction, 18 months late" failure twice over.

**BRONZE keeps everything, including what was called red, dead, or unbuyable. Filtering happens here, at query time.**

---

# THE CRITERIA REGISTER

Each criterion has an id, a definition, a field it reads, a weight, and a date. Weights are a starting proposal — change them freely; that is the point of the layer.

## C-BUY — Buyability gate *(runs first, filters rather than scores)*

| id | condition | action |
|---|---|---|
| BUY-1 | `buy = live` | proceed to scoring |
| BUY-2 | `buy = restricted-access` | check broker access, then score |
| BUY-3 | `buy = private-ipo-watch` | **route to watchlist. Stop valuation research.** Review quarterly for S-1 or funding news |
| BUY-4 | `buy = foundation-family-state` | find the proxy; remove from the active buy list; **flag as build-space candidate** |
| BUY-5 | `buy = absorbed` | remove; substitute the acquirer |
| BUY-6 | `buy = policy-restricted` | competitive tracking only |

**Current distribution across 1,185 entities:** live 712 · restricted-access 256 · private-ipo-watch 127 · foundation-family-state 43 · policy-restricted 28 · absorbed 19

---

## C-STRUCT — Structural criteria *(the ones that decide most outcomes)*

| id | criterion | reads | weight | logic |
|---|---|---|---|---|
| **ST-1** | **Constrained asset vs component** | `owns` | **0.25** | Owning grid interconnection, licensed fuel, land, long-lead manufacturing slots, processing capacity, or qualification lock-in survives an overbuild. Components compete away. |
| **ST-2** | **Data location** | `data` | **0.20** | `inside` = access required before anyone can build. `internet` = anyone can, so you're always late. |
| **ST-3** | **Scarcity trend** | `scarcity` | **0.20** | A model dies when what it charges for stops being scarce. ↑ scores highest; ↓ is disqualifying regardless of current profit. |
| **ST-4** | **Chokepoint degree** | derived from `depends_on` | **0.15** | Count how many groups depend on this one, divided by number of viable alternatives. |
| **ST-5** | **Customer concentration** | `customer` | **0.10** | Selling to four hyperscalers is concentration risk, not a moat. |
| **ST-6** | **Era survival** | derived | **0.10** | Buildout (now) · operation (2028+) · consolidation (post-shakeout). Score things that survive more than one. |

## C-PRICE — Valuation criteria *(applied after structure, never before)*

| id | criterion | logic |
|---|---|---|
| PR-1 | AI revenue share | What percentage of revenue is genuinely AI/DC exposed? Many industrials are under 10%. |
| PR-2 | Already discounts 2030? | Infrastructure booms deliver demand as forecast while first-round investors lose money to overbuild. Railways and 2000-era fibre both did this. |
| PR-3 | Run-up already occurred | Q2 2026 saw SK Hynix +690%, Samsung +378%, Kioxia +3,151%. Present in BRONZE regardless; price in the score. |
| PR-4 | Liquidity floor | Average daily volume minimum. |
| PR-5 | Market cap floor | Set by position size. |

## C-ACCESS — Personal criteria *(specific to Sin, not general)*

| id | criterion | logic |
|---|---|---|
| AC-1 | **Readable in Thai** | 🇹🇭 entities can be followed via BOI, ERC and SET filings continuously, with no translation lag. This is the only genuine information edge in the whole map. |
| AC-2 | Broker reachability | Which exchanges are actually tradeable. Removes roughly 40% if JP/KR/TW/EU are out. |
| AC-3 | Timezone tractability | Can it be monitored without disrupting a day job? |

## C-BUILD — Criteria that switch the question from "invest" to "build"

| id | condition | meaning |
|---|---|---|
| **BD-1** | high `ST-4` chokepoint **AND** `buy = foundation-family-state` | **Unbuyable chokepoint = build-space.** Demand is proven and capital cannot enter through the market. |
| **BD-2** | `owns` is empty across a whole group **AND** demand exists | Whitespace — nobody has claimed the constraint yet. |
| **BD-3** | `depends_on` includes something that does not exist yet | A missing input. F7 AI-risk insurance depends on loss data that has never been collected. |
| **BD-4** | `data = inside` **AND** AC-1 = true | Data he can reach and others cannot. **This is the intersection that matters most.** |

---

# GOLD — derived views

Regenerable. Never edit these by hand; change a weight above and rebuild.

## View 1 — Chokepoints, ranked by dependency

| group | depended on by | buyability | read |
|---|---|---|---|
| C1 copper | B10, A12, A11, A10 | ✅ live | Buy the chokepoint |
| B10 transformers | B2, A13, A12 | ✅ live | Buy the chokepoint |
| C3 GOES | B10, B5 | ✅ 🟡 | Buy the chokepoint |
| C7 qualification lock-in | A3, A4 | ✅ mixed | Buy where possible |
| D8 skilled trades | A13, A12, B10 | ✅ live | Underpriced attention |
| F5 powered land | A14, A13 | ✅ 🇹🇭 | **Reachable in Thailand** |
| **A20 deep upstream** | A4, A5 | 🏛️ **mostly unbuyable** | **BD-1 → build-space, or ASML as aggregation point** |
| **C9 EUV materials** | A20, A4 | 🏛️ **no proxy for HPQ** | **BD-1 → pure build-space** |
| **F7 AI loss data** | E3 | **does not exist** | **BD-3 → whitespace** |

## View 2 — BD-4 intersection: inside-data AND Thai-readable

The narrowest and most actionable set in the entire map.

| group | why it qualifies |
|---|---|
| G1 Thai power producers | Licences and PPAs published in Thai; BOI/ERC notices are primary sources |
| G2 Thai industrial estates | Land, utilities and DC siting disclosed locally first |
| G3 Thai electronics supply | DELTA and Fabrinet are the most direct Thai AI-hardware exposures |
| G4 Thai contractors | Project awards appear in Thai news before anywhere else |
| G5 Thai telecom & digital | Spectrum and fibre positions |
| **Products sellable into G1-G4** | Compliance/carbon reporting to Thai rules · operational telemetry plumbing · predictive maintenance on 2-3 year lead-time equipment · interconnection and capacity intelligence |

> This view is the one that answers **"what to build,"** not "what to buy." Every entry passes ST-2 (`inside`) and AC-1 (Thai-readable) simultaneously.

## View 3 — IPO watchlist, reviewed quarterly

127 entities at `private-ipo-watch`. Highest-signal by chokepoint position:
- **F3:** Databricks, ClickHouse *(acquired Langfuse; ~$15B)*
- **A15:** OpenAI, Anthropic, Mistral
- **A1:** Cerebras, Groq
- **A14:** AirTrunk, Vantage, Aligned, Switch, Compass
- **B3/B7/B9:** X-energy, TerraPower, Kairos, Form Energy, Fervo
- **C8:** Redwood Materials, Cyclic Materials
- **D1/D5/D6:** Figure, Physical Intelligence, Anduril, SpaceX
- **F1/F4:** Oasis Security, Stripe

**Cadence: 30 minutes per quarter.** The cheapest edge on the map, and the direct inverse of the "18 months late" pattern.

## View 4 — Access vehicles for 🔒 names

| vehicle | holds | caution |
|---|---|---|
| SoftBank 9984.T | ARM, OpenAI stake, broad private AI book | Most direct listed proxy for a private AI portfolio |
| Scottish Mortgage SMT.L | SpaceX, ByteDance, private growth | Trust discount/premium |
| Destiny Tech100 DXYZ | SpaceX, OpenAI, Anthropic | **Frequently trades at a large premium to NAV** |
| Berkshire BRK.B | Mouser, TTI, industrial distribution | Indirect but real |
| BX / KKR / APO / ARES / OWL / BAM / DBRG | AirTrunk, QTS, digital infra platforms | Own the sponsor rather than the asset |
| Prosus PRX.AS / Naspers NPN.JO | Tencent, private tech | — |
| ARK Venture ARKVX | private AI names | Interval fund — check liquidity terms |

**These solve access, not valuation.** Premium/discount, fee layers and holding opacity stack on top of the underlying.

---

# HOW TO RUN THIS

```
1. Load BRONZE (files 14 + 15). Change nothing.
2. Apply C-BUY. Route, don't delete — every routed entity stays in BRONZE.
3. Apply C-ACCESS. Removes the largest volume fastest.
4. Score with C-STRUCT weights.
5. Apply C-PRICE last. Never first — that is the TAM-without-competitive-structure error.
6. Check C-BUILD separately. It answers a different question with the same data.
7. Regenerate GOLD. Keep BRONZE untouched.
```

**When a criterion changes, note the date and reason here.** The criteria register is itself a dataset with history — that history is what will show whether the judgement was improving or drifting.

## Change log

| date | change | reason |
|---|---|---|
| 2026-08-08 | Layer created, weights set | Pre-filtering at ingest was destroying optionality |
| | | |

---

# VERIFICATION PROTOCOL (added 2026-08-08)

**Scope note first: this exploration is not tied to any project.** It exists to find opportunities. If something worth building appears, it becomes a separate discussion. If not, the outcome is simply an investment list. Nothing here obligates a build.

**The rule for the verification pass: verify and validate, but never filter out.**

| Action | Allowed? |
|---|---|
| Correct a wrong ticker, exchange, country, or status | ✅ |
| Add a missing entity or group | ✅ |
| Populate `source`, `confidence`, `as_of` | ✅ **required** |
| Update `buy` when a company lists, is acquired, or becomes restricted | ✅ |
| Enrich `business_model`, `product`, `depends_on`, `owns` | ✅ |
| Remove a row for irrelevance | ❌ never |
| Remove a row because unbuyable, dead, or acquired | ❌ never — change `buy` and keep it |
| Shortlist inside BRONZE | ❌ never — shortlisting belongs in GOLD |

**Empty beats fake.** A null field is recoverable; a confident wrong value silently corrupts every SILVER query built on it. Known error rate from the file-07 exercise: ~9%.

**Fields the verification pass should add to file 15:**

| field | why |
|---|---|
| `source` | where the fact came from |
| `confidence` | high / medium / low |
| `as_of` | date checked — without this the file rots invisibly |
| `depends_on` | entity-level upstream dependency; refines the chokepoint view |
| `owns` | the scarce thing controlled |
| `ai_revenue_share` | criterion PR-1 needs it |
| `mcap`, `adv` | criteria PR-4, PR-5 need them |

**Suggested cadence:** full verification pass once, then quarterly for `buy` status changes only — S-1 filings, acquisitions, delistings, sanctions. Roughly 30 minutes per quarter for the watchlist portion.
