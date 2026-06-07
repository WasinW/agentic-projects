# lumora — Project Overview

> Project-context knowledge base for Sin's part-time creator business in the Thai สายมู (spiritual/mystical) niche.
> Distilled from `session_context_export.md` (v1) + `session_context_export_v2.md` + `session_context_export_v3.md` (v3 supersedes — adds the **2-level framework** grounded in established marketing theory + **multi-account strategy**).

---

## What This Project Is

**One-paragraph summary** — A part-time creator business in the Thai **สายมู** (spiritual / mystical) niche that ships **AI-generated mystical art** with a **comedy / anime / cinematic** tone across short-form video. The front end is content + commerce: affiliate selling (**ปักตะกร้า** on TikTok Shop) plus owned high-margin digital products (art prints, oracle decks, journals, commissions). The back end is an **invisible tech moat** — an automated AI-art + content pipeline that lets Sin scale output other creators can't match by hand, and that later gets **productized for SME/B2B**. The unifier is not a single aesthetic but a consistent **creator voice**: a curious explorer of spiritual aesthetics — Thai roots × global art language — sometimes contemplative, sometimes funny, never a guru.

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

**Communication style** — Thai mixed with English technical terms. Practical, specific, mobile-friendly. **Pushes back** when an answer drifts off-topic (happened twice in source sessions). Wants **honest takes, not generic positivity**. Short or deep depending on topic. Likes tables / structured comparison; avoids over-formatting and excess emoji.

---

## The Phased Roadmap

```
Phase 1 (NOW):
  Content + Multi-channel + Online selling   ← the creator business
  + Internal tech backend (own tool, NOT for sale)

Phase 2 (Later):
  Productize the backend → serve SME / B2B
  (data micro-service, recommendation system, SMB loyalty SaaS)
```

**The pattern** — build a creator business first → grow an invisible tooling moat underneath it → productize that tooling later. Same playbook as **Pieter Levels, Justin Welsh, Marc Lou**.

- **Phase 1** is the only active phase. Content + audience + selling come first; the backend stays internal and minimal-viable, scaled only on actual need.
- **Phase 2** leverages Sin's real moat: 10+ yrs The1 retail/loyalty domain expertise → an **SMB loyalty SaaS** or data-microservice for SMEs. Premature to build now.

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
6. **Respect the topic** — a สายมู audience detects insincerity fast. Comedy must be self-deprecating, never mocking others. Position as a "fellow explorer," not a guru.
7. **Domain expertise > technical novelty** — Sin's 10+ yrs retail/loyalty is the real moat for Phase 2, more than any clever stack.

### Meta-principles — how Claude should work with Sin

These govern *how* Claude collaborates with Sin, distilled from the v3 session (§18 "Key Meta-Lessons"). They matter as much as the content above.

1. **Don't converge prematurely** — Sin thinks in breadth. Offer options; don't collapse to a single answer too early.
2. **Multi-direction > single-direction** — present multiple viable paths with their trade-offs rather than one "right" recommendation.
3. **Verify frameworks against established theory** — Sin wants frameworks grounded in real marketing/industry theory, not invented on the spot. Check before proposing.
4. **Confirm understanding before deep-dive** — restate the ask and confirm scope before going deep (Sin pushed back 3× in-session when Claude drifted or dove into the wrong layer).
5. **Library mindset** — keep options expandable and modular; structure things so new ideas can be added later without rework.

---

## The1 IP Boundary

A hard line to protect both the day job and the side business.

- **OK to use** — patterns, mental models, lessons learned that are publicly shareable.
- **Not OK** — proprietary code, proprietary data, anything internal/confidential to The1.
- **Sequence** — build (and ideally validate) the side business **before leaving**. Safer than burning bridges first.
- Use The1 only as a *sandbox for personal skill-building* and general brand credibility — never as a source of assets.

---

## Theme & Creative Approach

**Theme (locked):** Spiritual / Mystical (**สายมู**) — treated as a **broad theme**, not a narrow aesthetic.

**Why this theme won** — it was the only answer appearing across all 3 discovery questions (what Sin spends time/money on, what friends ask about, what content Sin never tires of: "อยากทำ art สายมู"). Convergence signal = ของมู + Art + multi-interest (anime, comedy, tech).

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

A core part of the plan (v3), not an afterthought. The chosen path is **sequential expansion**, not parallel day-1 launch. See `05_*` for the full strategy + split patterns.

**Why multi-account** — algorithm favors clear positioning, audience targeting gets precise, parallel directions can be tested, and **each account = a different monetization vehicle / audience pocket** (see Monetization §6). Trade-off: effort multiplies and individual growth is slower.

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
- Theme **locked**: สายมู (broad theme).
- Approach: **creative library** (4 dimensions × selective combinations), not single-niche.
- Channels: **TikTok-first**, multi-platform repurpose.
- Phase structure: creator-first → productize later.
- Backend: minimum-viable, scale on need.
- Aesthetic references calibrated (cinematic / atmospheric / anime / cyberpunk family).

**Pending 🔄** (v3 §17 — focused on standing up the **first account**)
1. **First account — Archetype** (Magician? Explorer? Sage? Jester?) + derived persona.
2. **First account — Audience Persona** (define 1–2 personas, e.g. "GenZ มู สาย aesthetic, 22–32, Bangkok working pro").
3. **First account — Content Pillars** — pick **2–4**.
4. **First account — Theme Clusters** — pick **2–4** to focus first.
5. **Channel naming** + brand identity (logo, color, typography).
6. **Show face?** — on-camera persona vs stay behind the work.
7. **Affiliate-first vs digital product day 1?**

---

## Warnings

1. **Respect > satire** — สายมู comedy must be self-deprecating, never mocking others (backlash risk).
2. **AI art + sacred imagery** — frame as *respectful homage*, not casual remix; audience can be sensitive.
3. **Don't be a guru** — "fellow seeker / explorer" framing is safer.
4. **No prediction/medical/guaranteed-outcome claims** — scammy and potentially illegal.
5. **Voice consistency > aesthetic consistency** — Sin's caption/tone must stay recognizable even as visuals vary.

---

*See sibling knowledge files for tech backend architecture, content pillars/calendar, and Phase 2 productization details as they get written.*
