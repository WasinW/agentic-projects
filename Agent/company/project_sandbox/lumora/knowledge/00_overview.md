# LUMORA — Project Overview

> Project-context knowledge base for **LUMORA** — Sin's part-time, AI-native **Owned & Operated Multi-Channel Network (O&O MCN) + Multi-Catalog Lab**. สายมู (spiritual/mystical) is **catalog #1**, not the whole project.
> Distilled from `session_context_export.md` (v1) → `_v6` (**v6 supersedes** — names the project **LUMORA**, reframes the business model from "agency" to **O&O MCN + Multi-Catalog Lab**, makes the niche **multi-catalog / niche-agnostic**, and splits monetization into **3 business-model phases** B2C → B2B → B2P). Earlier versions added the **two-service architecture** (Data + Marketing) and the lean modern stack separate from The1, both still valid.

---

## What This Project Is

**One-paragraph summary** — **LUMORA** is a part-time, AI-native creator business built as an **Owned & Operated Multi-Channel Network (O&O MCN) with a Multi-Catalog Product R&D Lab**. Sin owns every channel (not contracted KOLs) and uses an automated AI-art + content pipeline as an **invisible tech moat** that lets him run many channels across many catalogs with a cost edge no hand-built creator can match. The **first catalog** is the Thai **สายมู** (spiritual / mystical) niche — AI-generated mystical art with a **comedy / anime / cinematic** tone on short-form video — but the model is **niche-agnostic**: อาหาร / สุขภาพ / ท่องเที่ยว / gadget / art catalogs follow (Phase 1.5+). The front end is content + commerce (affiliate **ปักตะกร้า** + owned high-margin digital products); the back end productizes over time from B2C affiliate → B2B boutique agency → B2P platform-intelligence services. The unifier per channel is not a single aesthetic but a consistent **creator voice**: a curious explorer — Thai roots × global art language — sometimes contemplative, sometimes funny, never a guru.

### Brand Architecture — LUMORA (umbrella) → 4 arms

LUMORA is the parent/umbrella brand. It illuminates ("Lumi" = light) product opportunities across catalogs and time ("ora" = era/aura). Four arms map to the phases:

| Arm | Role | Active from |
|---|---|---|
| **LUMORA LABS** | Tech R&D — the two-service backend + AI agent pipeline | Phase 1+ |
| **LUMORA STUDIO** | Creator arm — Sin's own multi-channel content | Phase 1 |
| **LUMORA AGENCY** | B2B services — boutique agency for SMB brands | Phase 2 |
| **LUMORA INTELLIGENCE** | Platform / B2P services — serve TikTok Shop / Shopee / Lazada | Phase 3 |

Each **catalog** gets its own **sub-brand** under the umbrella (e.g. Lumora-มู / Mystic, Lumora-อาหาร / Eats, Lumora-Travel / Pilgrimage), with channels per the Channel Count Formula. See `session_context_export_v6.md` "PROJECT IDENTITY: LUMORA" for the naming decision log, trademark (NICE classes 35/41/42), and domain/handle strategy.

**The two-service architecture (the backend).** The invisible moat is split into two internal services that Sin owns end-to-end, connected by an **AI agent**:

| Service | Role | Does |
|---|---|---|
| **Data Service** | the **brain** | Aggregates multi-platform feeds (TikTok Shop / Shopee / Lazada / social analytics) into a Data Fabric → embeds + detects trends → AI agents recommend **Content × Theme × Media** combos and trigger generation |
| **Marketing Service** | the **hands** | Executes production (AI art, video, captions) → multi-account scheduling + posting → performance tracking, which feeds back into the Data Service (closes the loop) |

The **AI agent** is the connective tissue: it watches trends, matches them to a library combo, predicts performance, triggers generation, and proposes a posting schedule — Sin reviews/approves. Without it, Sin would hand-pick combos daily; with it, the framework becomes operational at scale across **N channels × N catalogs**. The same two services (operated as **LUMORA LABS**) serve **Sin's own channels** in Phase 1, **own + B2B agency clients** in Phase 2, and feed **platform-intelligence** services in Phase 3 — unchanged, because `brand_id` / `catalog_id` are threaded everywhere. See `04_tech_backend.md` + `06_architecture_agency.md`.

---

## Who — Sin

| | |
|---|---|
| **Day job** | Data Engineer at **The1** (Central Group, Thailand), ~10+ yrs |
| **Stack** | Apache Beam/Dataflow (Python), BigQuery, Bigtable, Pub/Sub, Cloud Composer (Airflow), Iceberg, BigLake |
| **Cross-cloud** | AWS (S3, RDS), Confluent Kafka; GitLab CI/CD, Terraform, VPC-SC |
| **Built** | `dataflow_common` — shared wheel + Docker image artifact |
| **Domain** | Retail / loyalty data, Customer 360, realtime customer-profile pipelines, CDC |

**Creative thinking style** — **divergent**. Prefers keeping a wide library of ideas and combining them selectively per piece, rather than force-merging everything into one direction. This is a core design principle for the whole project (see Strategic Principles).

**Communication style** — Thai mixed with English technical terms. Practical, specific, mobile-friendly. **Pushes back** when an answer drifts off-topic or assumes the wrong model (happened 4× across source sessions — see meta-principle #6). Wants **honest takes, not generic positivity**. Short or deep depending on topic. Likes tables / structured comparison; avoids over-formatting and excess emoji.

---

## The Business Model — O&O MCN + Multi-Catalog Lab

**The model (v6, supersedes the old "agency-as-the-model" framing).** LUMORA is an **Owned & Operated Multi-Channel Network + Multi-Catalog Lab** — a **"Ruhnn-Beast hybrid"**: Ruhnn's *influencers + incubator + supply-chain* 3-pillar MCN, but with **owned** channels (not contracted KOLs) like a single creator, plus MrBeast's *content → demand → product → margin → content* flywheel, plus an **AI-automated production** cost edge neither had. Agency is **one pillar / one phase**, not the whole business.

**3 pillars:**

1. **Multi-Channel Creator** — Sin owns 3–5 channels per catalog (per the Channel Count Formula), each a distinct (Segment × Aesthetic) combo. Sin ideates + reviews; the AI agent produces.
2. **Multi-Catalog Incubator** — catalogs are R&D bets tested on Sin's own channels first: **สายมู = catalog #1** (Phase-1 start) → อาหาร / สุขภาพ / ท่องเที่ยว / gadget / art (Phase 1.5+). Winners expand or productize.
3. **Multi-Platform Commerce** — affiliate (Phase 1) → boutique agency (Phase 2) → platform-intelligence services (Phase 3) across TikTok Shop / Shopee / Lazada.

### The 3 Business-Model Phases (aligns with the §0.5 3-axis library)

```
Phase 1 — B2C: own creator (NOW)
  Sin's own multi-channel content; revenue = affiliate (ปักตะกร้า) + owned digital products
  + LUMORA LABS internal backend (own tool, NOT for sale)
  → ~50–200K THB/mo

Phase 2 — B2B: boutique agency (Later)
  ⚠️ Agency, NOT SaaS. Sin operates the LABS backend himself, sells the OUTCOME
  to SMB/lifestyle brands as a done-for-you service (retainer, not self-serve tool)
  → own creator + 3–5 clients = ~300–700K THB/mo

Phase 3 — B2P: platform-intelligence (Year 3+, far-future)
  Serve the PLATFORMS (TikTok Shop / Shopee / Lazada): creator/product discovery,
  trend intelligence, campaign mgmt, data products — mostly commission on GMV
  → ~1–10M THB/mo (needs a 5–10 person team; do NOT chase in Year 1)
```

**The pattern** — build owned creator channels first → grow an invisible tooling moat underneath (LABS) → ladder monetization **B2C → B2B → B2P** without changing the backend (`brand_id` / `catalog_id` keyed). Same creator-founder spirit as **Pieter Levels / Justin Welsh / Marc Lou**, but the vehicle is an **O&O MCN**, not a SaaS product.

- **Phase 1 (B2C) is the only active phase.** Content + audience + selling come first across Sin's own channels; the backend stays internal and minimal-viable, scaled only on actual need.
- **Phase 2 (B2B) is an AGENCY, not a SaaS.** Sin operates the two-service backend **himself** and sells the *outcome* — **not** a multi-tenant subscription where clients self-serve the tool. (This was Sin's 4th pushback: Claude had drawn it as multi-tenant SaaS; corrected to agency, then reframed in v6 as just *one pillar* of the MCN.)
  - **Pricing** — retainer per client (Basic ~30–50K / Standard ~70–100K / Premium ~150–250K THB/mo) + one-time campaign/launch add-ons (~50–200K). Not a $50–200/mo subscription.
  - **Why agency** — higher ticket, Sin keeps quality control, no customer-facing UI to ship, the tool stays a secret moat, clients pay more *because* they don't have to learn it.
  - **Trade-off** — scales **linearly** with Sin's time (1 person ≈ 3–10 clients). Hire a team only past ~10 clients.
- **Phase 3 (B2P) is a far-future vision** — only unlocks after Phase 1+2 proof: own channels at 50K+, agency running 6+ months, 3+ documented case studies, platform-side relationships. **ห้าม** skip to it by pitching platforms early.
  - See `06_architecture_agency.md` for the agency-vs-SaaS comparison, service tiers, and trigger conditions; `session_context_export_v6.md` §15 for the 6 Phase-3 service types.

---

## "หนีงาน" Progression Framework

A staged exit from full-time employment. **ห้ามกระโดดข้ามขั้น** (no skipping stages).

| ขั้น | State |
|---|---|
| **0** | ประจำ (full-time job only) — *current* |
| **1** | ประจำ + side project |
| **2** | ประจำ + side income (real paying customers) |
| **3** | ประจำ part-time + business ~60% |
| **4** | Business full-time — gate: revenue ≥ salary × 1.5, sustained 6 months |

Sin is at **ขั้น 0**, moving toward ขั้น 1 with this project.

---

## Strategic Principles

1. **Divergent then selective** — keep the idea pool wide; combine dimensions per piece. Don't converge prematurely. (Sin's own insight; applies to all creative work.)
2. **Voice > aesthetic** — what unifies the channel is the creator's perspective, not a single visual style. Caption/tone consistency matters more than feed uniformity.
3. **Creator-first** — content + audience + selling before any product.
4. **Tech as an invisible moat** — automate what others do by hand (AI generation, data aggregation, scheduling). The tech is craft, not the product.
5. **Cross-aesthetic = cross-monetization** — different aesthetics unlock different revenue pockets (traditional → larger/lower-AOV affiliate; cyber-spiritual → premium prints/collab; comedy → viral reach; travel → hotel partnerships).
6. **Respect the topic** — each catalog's audience detects insincerity fast (สายมู especially). Comedy must be self-deprecating, never mocking others. Position as a "fellow explorer," not a guru.
7. **Domain expertise > technical novelty** — Sin's 10+ yrs retail/loyalty + cultural specificity per catalog is the real moat (especially for the B2B agency and B2P platform phases), more than any clever stack. The moat is **tool + Sin's expertise + cultural depth**, not the tool alone.
8. **Niche-agnostic, catalog-as-bet** — the framework is not tied to สายมู; it's a reusable engine. Each catalog is an R&D bet validated on owned channels before expanding. Don't scale to 5+ catalogs before validating #1.

### Meta-principles — how Claude should work with Sin

These govern *how* Claude collaborates with Sin, distilled from the v3 session (§18 "Key Meta-Lessons"). They matter as much as the content above.

1. **Don't converge prematurely** — Sin thinks in breadth. Offer options; don't collapse to a single answer too early.
2. **Multi-direction > single-direction** — present multiple viable paths with their trade-offs rather than one "right" recommendation.
3. **Verify frameworks against established theory** — Sin wants frameworks grounded in real marketing/industry theory, not invented on the spot. Check before proposing.
4. **Confirm understanding before deep-dive** — restate the ask and confirm scope before going deep (Sin pushed back 4× across sessions when Claude drifted or dove into the wrong layer).
5. **Library mindset** — keep options expandable and modular; structure things so new ideas can be added later without rework.
6. **Don't assume the business model — ask** — verify the model (SaaS vs agency vs consultancy vs B2C) *before* deep-diving; don't default to SaaS. This was the **4th pushback**: Claude drew Phase 2 as multi-tenant SaaS, Sin corrected it to an agency. The prior three: (1) answered Microsoft Fabric instead of the Data Fabric concept, (2) dove into B2B strategy when Sin wanted content-niche basics, (3) forced "Cyber-Spiritual only" convergence when Sin wanted multi-direction.

---

## The1 IP Boundary

A hard line to protect both the day job and the side business.

- **OK to use** — patterns, mental models, lessons learned that are publicly shareable.
- **Not OK** — proprietary code, proprietary data, anything internal/confidential to The1.
- **Sequence** — build (and ideally validate) the side business **before leaving**. Safer than burning bridges first.
- Use The1 only as a *sandbox for personal skill-building* and general brand credibility — never as a source of assets.

---

## Catalog #1 & Creative Approach

**Catalog #1 (the Phase-1 start):** Spiritual / Mystical (**สายมู**) — treated as a **broad theme**, not a narrow aesthetic. It is the *first* catalog the framework is applied to, **not** the whole project. Subsequent catalogs (อาหาร / สุขภาพ / ท่องเที่ยว / gadget / art, Phase 1.5+) reuse the same Level-1/Level-2 framework below.

**Why สายมู was picked to go first** — it was the only answer appearing across all 3 discovery questions (what Sin spends time/money on, what friends ask about, what content Sin never tires of: "อยากทำ art สายมู"). Convergence signal = ของมู + Art + multi-interest (anime, comedy, tech). It earns the #1 slot on *founder energy + cultural depth*, but the engine is niche-agnostic.

**Creative approach — the 2-level framework (v3).** The framework is now structured in **two levels**, grounded in established marketing theory (Content Pillars, Jung archetypes, JTBD, HHH, STP). See `01_creative_library.md` for the full reference.

**Level 1 — Account-level** (fixed per channel, defined once):

| Element | Industry grounding |
|---|---|
| **Voice / Archetype** | Brand Voice + the 12 Jungian archetypes (Magician, Explorer, Sage, Jester…) + derived persona |
| **Audience Persona** | Fictional character of the target audience (STP target) |
| **Niche scope** | Broad vs narrow positioning (STP segment/position) |

**Level 2 — Post-level Library** (vary per post — the mix-and-match engine):

| Axis | Industry grounding |
|---|---|
| **Content** | Content Pillars — what to sell + topic bucket |
| **Theme** | World / setting / era (Sin's open-ended, expandable axis) |
| **Media** | Format / production type |
| *Optional* **JTBD / Intent** | "What job does this post do for the audience" (Christensen) |
| *Optional* **Funnel stage** | Hero / Hub / Hygiene cadence (HHH, Google/YouTube) |

The **Theme axis is intentionally open-ended** — Sin adds clusters anytime; it's navigation, not a constraint. Combine selectively per post (Content × Theme × Media ≈ years of unique content). This replaces the v2 "4-dimension library" framing — the same divergent, mix-and-match spirit, now validated against industry-standard frameworks and split into account-fixed vs post-varying levels.

**Aesthetic DNA Sin likes** (calibrated from IG refs @odysseyml, @hellopersonality, @abeastinside, @metronovon): cinematic + atmospheric, moody lighting (neon+dark, lantern+mist), lone figure in a vast world, sci-fi/cyberpunk × fantasy fusion, anime/manga influence, first-person POV framing.

---

## Monetization (summary)

- **Affiliate (ปักตะกร้า):** เครื่องราง/จี้/สร้อย (5–15%), ยันต์/ตะกรุด (5–10%), น้ำมัน/ผง/เครื่องหอม (8–15%), crystal/หิน (10–15%), oracle/tarot/หนังสือ (5–10%).
- **Digital products (owned, high margin):** AI art prints ($5–15 mass / $20–80 premium), custom oracle deck PDF ($20–50), สายมู journal template ($10–30), personalized commission ($30–100), course ($50–200).
- **Subscription (later):** Patreon daily oracle + exclusive art (99–299/mo), paid Discord.
- **Brand partnership (50K+ followers):** ของมู shops, crystal brands, hotels/restaurants near sacred sites, fashion/streetwear, anime/gaming (cyber-spiritual angle).
- **Agency retainers (Phase 2 — B2B):** client-brand service contracts — tiers Basic ~30–50K / Standard ~70–100K / Premium ~150–250K THB/mo/client + one-time campaign/launch add-ons (~50–200K). See `03_monetization.md` + `06_architecture_agency.md`.
- **Platform-intelligence services (Phase 3 — B2P, far-future):** serve TikTok Shop / Shopee / Lazada — creator/product discovery, trend reports, campaign mgmt, data products — mostly **commission on GMV** (+ retainer/data-subscription hybrids). Target ~1–10M THB/mo at scale; needs a 5–10 person team. See `session_context_export_v6.md` §15.
- **Revenue ladder (the 3-phase spine):** **50–200K → 300–700K → 1–10M THB/mo** (B2C own creator → +B2B agency clients → B2P platform).

---

## Channel Strategy

- **TikTok + Reels** — primary, ~70% (algorithm favors new creators).
- **YouTube Shorts** — repurpose, ~0% extra effort.
- **LinkedIn** — repurpose text, ~10% (authority-building for future B2B).
- **Long-form YouTube** — 1/month, ~20% (SEO).
- **Skip until audience exists:** Facebook page, IG feed (Reels only), Twitter/X.
- **Batch posts by aesthetic** (e.g. a week of cyber-spiritual, then a week of traditional) so the algorithm isn't confused by rapid style switching.

---

## Multi-Account Strategy

A core part of the plan, not an afterthought — it's how the **O&O** in "O&O MCN" is realized: Sin owns every channel. **⚠️ Accounts = Sin's OWN channels** (different content styles), **NOT** external customers self-serving a tool. The chosen path is **sequential expansion**, not parallel day-1 launch. Channel count per catalog follows the **Channel Count Formula** (`MIN(S,A) ≤ N ≤ S×A`, S = segments, A = aesthetics — see `session_context_export_v6.md` §21). See `05_*` for the full strategy + split patterns.

**Why multi-account** — algorithm favors clear positioning, audience targeting gets precise, parallel directions can be tested, risk is diversified, and **each account = a different monetization vehicle / audience pocket** (see Monetization §6). Multi-account-from-start is also a deliberate hedge against the Ruhnn failure mode (over-reliance on one top KOL). Trade-off: effort multiplies and individual growth is slower.

**Sequential expansion (chosen) — start with ONE account:**

```
Start:        ONE account, validate the library
5-10K fans:   open a 2nd account
Onward:       scale on traction; consider a 3rd
```

**Why sequential** — sustainable for a part-time creator with a full-time job; learn per stage before multiplying effort. Build the **tech backend multi-account-ready from day 1** (shared prompt library + per-account scheduling) even while running only one account.

---

## Current Decisions vs Pending

**Decided ✅**
- Project **named LUMORA** (umbrella brand) → 4 arms (LABS / STUDIO / AGENCY / INTELLIGENCE); sub-brand per catalog.
- Business model: **O&O MCN + Multi-Catalog Lab** ("Ruhnn-Beast hybrid", 3 pillars) — agency is one pillar/phase, NOT the model.
- **Catalog #1 = สายมู** (broad theme, Phase-1 start); framework is **niche-agnostic / multi-catalog** (อาหาร/สุขภาพ/ท่องเที่ยว/gadget/art, Phase 1.5+).
- Approach: **creative library** (3-axis Content × Theme × Media + account-level tags), not single-niche.
- Channels: **TikTok-first**, multi-platform repurpose; channel count per catalog via the Formula.
- Monetization spine: **3 business-model phases** B2C own creator → B2B agency → B2P platform (50–200K → 300–700K → 1–10M THB/mo); Phase 2 = **agency, NOT SaaS**.
- Architecture: **two services** (Data + Marketing = LUMORA LABS) operated internally by Sin, connected by an AI agent.
- Backend: minimum-viable, scale on need; `brand_id` / `catalog_id`-keyed so own channels → +clients → platform services need no schema change.
- **Tech stack:** lean modern — **Cloudflare (Workers/R2/Pages) + Modal + Supabase (Postgres + pgvector) + Replicate (FLUX) + Claude API**. ≤ **$200/mo** (~$80–120 Phase 1, ~$150–250 Phase 2 with clients). **100% separate from The1 — NOT GCP-native.** See `04_tech_backend.md`.
- Aesthetic references calibrated (cinematic / atmospheric / anime / cyberpunk family).

**Pending 🔄** (focused on standing up the **first account in catalog #1 / สายมู**)
1. **First account — Archetype** (Magician? Explorer? Sage? Jester?) + derived persona.
2. **First account — Audience Persona** (define 1–2 personas, e.g. "GenZ มู สาย aesthetic, 22–32, Bangkok working pro").
3. **First account — Content Pillars** — pick **2–4**.
4. **First account — Theme Clusters** — pick **2–4** to focus first.
5. **Sub-brand naming** (e.g. `@lumora.mu`) + brand identity (logo, color, typography) under the LUMORA umbrella.
6. **Show face?** — on-camera persona vs stay behind the work.
7. **Affiliate-first vs digital product day 1?**
8. **Catalog #2 trigger** — which catalog after สายมู, and on what traction signal (Phase 1.5)?
9. **Phase 2 (B2B) client target type** — which kind of brand to target first? (retail SMB? lifestyle? F&B? a specific vertical?)
10. **LUMORA trademark + domains** — file Thai TM (NICE 35/41/42); register 3–5 domain variants (lumora.co, lumoralabs.com…) + claim @lumora.* handles.

---

## Warnings

1. **Respect > satire** — สายมู comedy must be self-deprecating, never mocking others (backlash risk).
2. **AI art + sacred imagery** — frame as *respectful homage*, not casual remix; audience can be sensitive.
3. **Don't be a guru** — "fellow seeker / explorer" framing is safer.
4. **No prediction/medical/guaranteed-outcome claims** — scammy and potentially illegal.
5. **Voice consistency > aesthetic consistency** — Sin's caption/tone must stay recognizable even as visuals vary.
6. **Agency = time-bound (Phase 2 / B2B)** — Sin's time is the bottleneck; plan a team early if scaling past ~10 clients, and keep client contracts clear (IP ownership, deliverable scope, kill switch). Don't over-promise specific outcomes.
7. **Don't validate >1 catalog at once** — สายมู first; expand only on real traction. Don't scale to 5+ catalogs before #1 is proven.
8. **Don't chase Phase 3 (B2P) early** — platform-intelligence only unlocks after Phase 1+2 proof (own channels 50K+, agency 6+ months, 3+ case studies). **ห้าม** pitch platforms before that.
9. **Don't compete head-on with AnyMind** — it's brand-side BPaaS/enterprise; LUMORA is creator-side O&O / boutique. Different model.

---

*Sibling knowledge files: `01_creative_library.md` (3-axis framework), `02_content_and_channels.md`, `03_monetization.md`, `04_tech_backend.md` (lean stack + two-service architecture = LUMORA LABS + data model), `05_multi_account.md`, and `06_architecture_agency.md` (Phase 2 B2B agency model — agency-vs-SaaS, service tiers, trigger conditions). Master source: `session_context_export_v6.md` (PROJECT IDENTITY, §13 business model, §14 competitive landscape, §15 Phase 3, §21 Channel Count Formula).*
