# 05 — Library Framework & The Feedback Loop

> **Written 2026-08-07 after actually reading the Lumora KB.** This file exists because the earlier docs treated Library Framework as a footnote and designed a "control plane" that had no way to measure anything. That was wrong. This is the correction.
>
> Canonical source: `…/lumora/knowledge/01_creative_library.md` (Framework v3). The `library-framework/` directory is a pointer only — do not extend it there.

---

## 1. Status — folded, not cancelled

**Library Framework was FOLDED into Lumora as internal IP on 2026-07-18.** The "separate product vs internal IP" question is resolved: **internal IP.**

- Canonical file: Lumora KB `01_creative_library.md`
- The standalone `library-framework/knowledge/01-content-taxonomy.md` is **superseded**, kept for history only
- Revisit as standalone **only in 12 months**, and **only if ≥1 channel shows framework-attributable public growth**
- If ever externalized: **content-led authority (StoryBrand-style), NEVER SaaS**

### On calling it an "analytics platform"

Understandable instinct — it *is* the analytics layer. But two of Sin's own prior decisions push against the name:

1. **"NEVER SaaS"** is recorded twice (INDEX + CLAUDE.md). "Platform" pulls toward a product that others self-serve, which is the exact shape already rejected.
2. **Phase 2 = agency, not SaaS** was Sin's 4th recorded pushback in an earlier session. Naming an internal component a "platform" quietly re-opens a settled question.

**Suggested alternative:** call the *capability* what it is — **the measurement layer** or **the combo intelligence layer** — and keep "Library Framework" as the name of the IP. If a productized version ever happens, name it then, under the content-led-authority route, not now.

---

## 2. What the framework actually is

Two levels. This distinction is the whole design.

```
ACCOUNT-LEVEL (fixed per channel — set once, then lock)
  Voice / Archetype    Jung 12 archetypes + persona
  Audience Persona     who this channel speaks to
  Niche scope          broad vs narrow positioning

POST-LEVEL (varies every post — the divergent library)
  C — Content pillars   C1-C10, defined per channel
  T — Theme clusters    open-ended, expandable
  M — Media formats     M1-M12
  optional: JTBD, HHH funnel stage
```

**Why two levels:** account-level is identity and is slow-moving — changing it confuses both the brand and the algorithm. Post-level is where variety lives. The wide visual range is safe *precisely because* identity is pinned one level up. **Voice unifies the channel, not aesthetic.**

**Every axis is theory-grounded** — Content Pillars (HubSpot/Cloud Campaign), Jung archetypes, JTBD (Christensen), HHH (Google/YouTube), STP (Kotler). Theme is Sin's own addition and the genuinely novel axis.

**Channel Count Formula:** `1 ≤ N ≤ S × A`, where the V1/V2/V3 gates decide where N lands — V1 overlap threshold (~30%, merge above), V2 viable size (>~10K, fold below), V3 positioning distinctness. The old `MIN(S,A)` lower bound was corrected as pseudo-math on 2026-07-18. **Default to N=1;** over-splitting is the classic solo-creator failure mode.

---

## 3. The feedback loop — this is what "control" means for Lumora

The earlier architecture doc designed governance over *agents*. What Lumora actually needs governance over is **which combos to make next.** That loop already exists and is documented:

```
   ┌─────────────────────────────────────────────────────────┐
   │                                                         │
   │   ① PICK COMBO          (C × T × M + JTBD + HHH)        │
   │        │                 lumora-combo-recommend         │
   │        ▼                                                │
   │   ② PRODUCE             lumora-content-batch            │
   │        │                 lumora-art-prompt              │
   │        ▼                                                │
   │   ③ PUBLISH             manual — Sin's thumb            │
   │        │                 (auto-publisher FORBIDDEN)     │
   │        ▼                                                │
   │   ④ LOG                 post_log — one row per post     │
   │        │                 combo, hook_type, url          │
   │        ▼                                                │
   │   ⑤ MEASURE             views_24h / views_7d / saves    │
   │        │                 follows_delta / gmv            │
   │        ▼                                                │
   │   ⑥ WEEKLY REVIEW       v_post_scores — 10 min ritual   │
   │        │                 top / bottom / pillar rollup   │
   │        └────────────────────────────────────────────────┘
                             adjust next week's combo spread
```

**The C×T×M tagging is what makes step ⑥ possible at all.** Without the taxonomy, performance data is a pile of undifferentiated posts and nothing can be learned. With it, every post is a labelled experiment in a three-dimensional space, and the weekly rollup tells you which region of that space works.

**This is the real control system.** Not agent permissions — combo selection under measured feedback.

### The measurement schema (already specified)

`post_log` in `lumora_sprint.db` — SQLite or spreadsheet, one row per published post:

- Identity: `post_id` (`L{week}-D{day}`), `brand_id`, `account_handle`, `posted_at`
- **Taxonomy: `content_pillar`, `theme`, `media`** ← the three axes, the reason any of this works
- Context: `jtbd`, `funnel_stage` (Hero/Hub/Hygiene), `hook_type` (fixed tag), `ai_labeled`
- Performance: `views_24h`, `views_7d`, `likes`, `comments`, `shares`, `saves`, `follows_delta`, `gmv`

Derived in `v_post_scores`: `save_rate`, `follow_rate`, `tail_multiple` (7d/24h — separates hook strength from algorithm pickup).

> Note: the `post_log` template and the account-decisions package are sprint artifacts, not the canonical KB. The canonical Lumora knowledge set is `00_overview` · `01_creative_library` · `02_content_and_channels` · `03_monetization` · `04_tech_backend` · `05_multi_account` · `06_architecture_agency` · `07_platform_design` · `ADR-0001`.

**Design decisions worth preserving:**
- `hook_type` is a **fixed-tag lookup, not free text** — so it can be grouped and analysed. Same pattern as `reject_reasons` in the parked backend.
- Column names map **1:1 onto Supabase `posts` + `performance`** — Phase-2 ingest is a column map, not a rework.
- `brand_id` exists from day one even with one brand. This is the discipline that makes the agency phase possible without migration.
- **Empty beats fake.** Unmeasurable fields stay NULL — the log is training data, and invented numbers poison it.

### The weekly ritual (10 minutes, the actual control action)

1. **Top performer** — which combo/hook/aesthetic won → repeat as variation next week
2. **Bottom performer** — weak hook (low 24h) vs weak aesthetic vs fatigued combo → adjust or rest that combo
3. **Pillar × hook rollup (28d)** — which pillar/hook pairs earn their slot → reweight the spread
4. **Gate progress + compliance** — distance to the day-90 gate; every post AI-labeled; watch for suppression signals on labeled content and for any homage sensitivity on C1 sacred imagery

One line logged per week: *"W{n}: top=…, bottom=…, changing X next week."* That line is both the decision trail and future training signal.

---

## 4. Where the taxonomy meets governance

The earlier doc asked how the taxonomy boundary interacts with lineage. Reading the KB, the answer is simpler than the question assumed:

**The taxonomy IS the lineage for Phase 1.** A post's `(C, T, M, JTBD, HHH, hook_type)` tuple is the complete record of what decision produced it. There is no agent chain to trace because there is no agent chain — production is skills invoked by Sin in Claude Code, and publishing is manual.

**What genuinely needs governance in Phase 1** is not agent permission but **content compliance**, and it is already specified as hard rules:

| Rule | Source | Enforcement today |
|---|---|---|
| No prediction / guaranteed outcomes | Decision 2 taboo lines | Human check before publish |
| No medical claims | Decision 2 | Human check |
| No financial claims | Decision 2 | Human check |
| No fear-mongering | Decision 2 | Human check |
| Never mock believers — self-deprecating only | Overview warning #1 | Human check |
| Sacred imagery = respectful homage, watch reaction, be ready to pull | Decision 2 + ADR-0001 | Human check + homage-watch note in log |
| AI label on every post with AI visuals | AI-labeling compliance | `ai_labeled` column, checked weekly |
| PDPA-safe oracle — no personal data collected during sprint | Decision 2 | Design constraint |
| Manual posting only, never an unofficial auto-publisher | ADR-0001 hard rule #5 | Absolute |

**If a control plane is ever built for Lumora, this table is its actual policy set** — not the generic agent capabilities drafted earlier. These rules already exist, are already binding, and are currently enforced by a human. Automating a check for them is the only governance work with a real justification.

---

## 5. What was wrong in the earlier docs

| Earlier claim | Correction |
|---|---|
| Library Framework is "internal structure, could spin out as an analytics platform" | Folded as internal IP, decision already made, **never SaaS**. Spin-out gated at 12 months + framework-attributable growth. |
| Capability model built on a guessed pipeline (research → plan → produce → review → publish → track) | Real Phase-1 pipeline is **5 skills + Claude Code + Sin's thumb**. No automated publishing exists or is permitted. |
| `platform.post.create` as an agent capability | **Forbidden.** ADR-0001 hard rule #5 — an unofficial auto-publisher risks a ban that destroys the whole experiment. |
| Control plane governs agents | For Phase 1 it governs **combo selection** and **content compliance**. Agent governance has no subject yet. |
| Lineage needs an event chain from artifact to prompt version | The `(C,T,M)` tuple plus `post_log` already is the lineage at the fidelity Phase 1 needs. |
| Layer 4 evidence pack for auditors/insurers | No auditor and no insurer exists in this picture. The only external compliance reader is **TikTok's AI-labeling enforcement**. |
