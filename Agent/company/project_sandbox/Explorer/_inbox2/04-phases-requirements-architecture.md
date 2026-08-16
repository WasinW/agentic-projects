# 04 — Phases, Requirements & Architecture

> **REWRITTEN 2026-08-07** after reading the actual Lumora KB and ADR-0001.
>
> **The previous version of this file was wrong in a way that mattered.** It specified an agent control plane — event log, policy engine, SDK enforcement wrapper, halt mechanism, evidence packs — for a project whose own binding ADR says *build no new code*. It was the exact "factory before the first product" trap ADR-0001 was written to prevent. That version is retracted in full; what follows replaces it.

---

# PART I — THE BINDING CONSTRAINT

## ADR-0001 (2026-07-18, Accepted) — the backend is parked

Any plan for Lumora must pass through this. It is not advisory.

**Context at the time:** ~2,105 LOC of backend, one commit, dormant ~6 weeks, **0 tests**, every integration a mock (`ClaudeScript`, `ReplicateImage`, `KlingVideo`, scrapers, publisher all `NotImplementedError`), combo assignment was `hash(ext) % len(PILLARS)`. Business state: **0 channels, 0 posts, 0 followers, 0 THB.**

**Hard rules, binding until explicitly revisited:**

1. **No new adapter until BOTH hold:** ≥100 posts published **AND** a named, specific manual step eating >2 hrs/week. Then build only that one adapter. Nothing speculative.
2. **Phase-1 pipeline = the 5 skills + Claude Code + manual posting.** That is the whole system. Treat it as the product, not a stopgap.
3. **The only backend Phase 1 needs is a per-post log** — combo, hook, URL, views, GMV, in a spreadsheet or SQLite. It is simultaneously the ops tool and the training data the scorer currently fakes.
4. **All Phase 2/3 work frozen** — thinking *and* architecture — until a real Phase-1 case study exists.
5. **Never build or use an unofficial auto-publisher.** A ban at 10K followers destroys the entire experiment. Manual posting or official APIs only. Non-negotiable.

**Guardrail written into the ADR:** if a later session proposes building an adapter, rule #1 is the gate. If both conditions are not met, the answer is no.

> **This document previously violated rules 1, 2, 4 and 5 simultaneously.** Treat that as the cautionary example.

---

# PART II — WHAT PHASE 1 ACTUALLY IS

## The 90-day sprint

> **Status caveat (2026-08-07):** the settings table below comes from the *account-decisions recommendation package*, which explicitly says "Sin ตัดสินใจขั้นสุดท้ายเอง". Lumora's own `CLAUDE.md` and `INDEX.md` still list **channel name, voice positioning, archetype, first 30-day batch, affiliate-vs-digital-product day 1, and show-face** as **PENDING**. Treat the table as recommended-not-locked until Sin confirms.

A **publish-or-park experiment costing ~0 THB.** Not step one of an MCN — the MCN, agency and platform visions are explicitly frozen until the gate passes.

**The single thing being proved:** does a Sin-voiced (~70/30 human/AI) สายมู channel get traction on Thai TikTok?

| Decision | Setting |
|---|---|
| Channel | **@มูมีแสง** *(recommended; backup @lumora.mu as umbrella handle later)* |
| Archetype | **Explorer (primary) × Magician (secondary)**, Jester shading on comedy only *(recommended — weigh the LIVE handicap before locking)* |
| Appearance | Hybrid path-to-face — voice-led/faceless-friendly for 90 days; face + LIVE unlock *after* the gate |
| Persona | "GenZ มู สาย aesthetic" — 22-32, Bangkok working pro |
| Pillars | **C2** oracle (daily anchor) · **C1/C6** art engine (3-4/wk) · **C9** comedy (1-2/wk). C4 travelogue parked until after the gate |
| Cadence | Oracle daily + 2-3 heavier posts/week; ~30 posts/30 days; batched weekly |
| Time budget | <6 hrs/week |
| Publishing | **Manual only.** TikTok native scheduler permitted; no automation |
| Compliance | AI label from post #1; no reliance on Creator Rewards |
| **Day-90 gate** | **1 post ≥50K views OR 1,000 followers.** Pass → continue + unlock face/LIVE + consider C4. Miss → change tone/catalog **or park the whole project.** No sunk-cost continuation. |

## The material handicap on record

**LIVE-commerce handicap.** Thai TikTok affiliate conversion concentrates in LIVE commerce, which a faceless channel structurally cannot do. This caps the conversion ceiling — it is not a tuning detail. Consequences already priced in: the gate measures **reach, not GMV** (so faceless can pass), but the archetype must not foreclose showing face and going LIVE later.

## Differentiation is human, not automation

Repositioned away from "AI automation at scale" — a 2026 commodity (Korpi, FlowShorts, AutoShorts, VEO3 pipelines) and actively suppressed by TikTok's AI-content enforcement, up 340% in 2025.

The real moat: **AI-art aesthetic + สายมู cultural literacy + Sin's voice — a human layer on every post, ~70/30 human/AI.**

---

# PART III — THE PHASE 1 SYSTEM

There is no service architecture to build. The system is five skills, Claude Code, a log file, and a weekly ritual.

```
  lumora-trend-scan          → source
        ▼
  lumora-combo-recommend     → picks next (C × T × M)   [smarter than the parked hash-brain]
        ▼
  lumora-content-batch       → expands combo into a post
  lumora-art-prompt          → art prompts
        ▼
  Sin's thumb                → manual publish
        ▼
  post_log (SQLite/sheet)    → ops tracker AND training data
        ▼
  v_post_scores + weekly review ritual
        ▼
  adjusted combo spread next week ──┐
        └─────────────────────────────┘
```

**Infrastructure cost: $0. Maintenance: 0.**

The measurement layer, the taxonomy that makes it work, and the weekly ritual are specified in **file 05**. That is the real "control plane" for this phase.

---

# PART IV — REQUIREMENTS FOR PHASE 1

Deliberately small. Anything not listed here is out of scope by ADR-0001.

## R-1 The log
- R-1.1 Every published post SHALL produce exactly one `post_log` row.
- R-1.2 Every row SHALL carry `content_pillar`, `theme`, `media` — the three axes. A post logged without its combo is a lost experiment.
- R-1.3 `hook_type` SHALL be a fixed tag, never free text.
- R-1.4 Column names SHALL map 1:1 onto Supabase `posts` + `performance`.
- R-1.5 `brand_id` SHALL be present from row one.
- R-1.6 Unmeasurable fields SHALL be left NULL. Invented numbers poison the training data.
- R-1.7 Metrics SHALL be updated at two points: 24h (`views_24h`) and 7d (everything else).

## R-2 The ritual
- R-2.1 A review SHALL run on days 7/14/21/28 and take ≤10 minutes.
- R-2.2 It SHALL cover: top performer, bottom performer, 28-day pillar × hook rollup, gate progress, compliance check.
- R-2.3 It SHALL produce one written line per week recording what changes next week.

## R-3 Compliance (the actual policy set)
- R-3.1 No prediction or guaranteed-outcome claims.
- R-3.2 No medical claims.
- R-3.3 No financial claims.
- R-3.4 No fear-mongering.
- R-3.5 Comedy self-deprecating only; never mock believers or deities.
- R-3.6 Sacred imagery as respectful homage; homage-watch noted in the log; pull if reaction warrants.
- R-3.7 AI label toggled on every post containing AI visuals, from post #1.
- R-3.8 No personal data collected for oracle personalisation during the sprint (PDPA-safe).
- R-3.9 Manual publishing only. No unofficial auto-publisher, ever.

## R-4 What is explicitly NOT required
No API, no database server, no event log, no policy engine, no agent identity model, no permission scopes, no approval gates, no halt mechanism, no evidence packs, no dashboard, no multi-tenancy, no adapters of any kind.

Every item on that list was in the previous version of this document. None of it has a subject yet.

---

# PART V — WHAT UNPARKING WOULD LOOK LIKE

Do not build any of this now. It is recorded so the trigger is recognisable when it fires.

## The resurrection trigger

**≥100 posts published AND a named manual step eating >2 hrs/week.** Both. Then build **only the adapter for that one step.**

The likely first candidates, in the order the manual pain usually appears:

| Manual step | Adapter it would justify | Note |
|---|---|---|
| Collecting metrics from platform analytics by hand | Metrics ingestion service + API | Already decided as service-shaped (07 §9 decision 1) |
| Generating art prompts and images one at a time | Generator adapter (Replicate/FLUX) | Generator seam already designed |
| Scanning trends across platforms manually | Source adapter (TikTok Shop first) | Source seam already designed |
| Publishing | **Never.** Rule #5. | Official API only, if ever |

## The design that already exists

The parked backend and `07_platform_design.md` are not wasted work. Preserved decisions worth honouring whenever code resumes:

- **Orchestrator-first, LLM-surgical.** 95% of the work is deterministic (SQL, formulas, rules — $0 token). LLM only where human judgment is genuinely needed (caption in brand voice, novel combos, one-sentence rationale). ~100× cheaper than agent-does-everything.
- **Combo scoring is a weighted formula, not ML:** `score = 0.30·trend + 0.25·fit + 0.20·lift + 0.10·recency + 0.10·season − fatigue`. Debuggable, explainable, free. No model training until data volume justifies it.
- **Three seams only:** `brand_id` + Postgres RLS on every table · Source adapter · Generator adapter. Everything else deferred. The rule that keeps it honest: **draw an abstraction only where a second implementation already exists.**
- **State machine with two human approval points** — combo → asset. Prevents auto-publish structurally. Includes a `revised` state (review → edit → approve).
- **Fixed-tag reject reasons**, so the scorer learns systematically.
- **Decisions archived, never deleted** — unapproved combos become an idea bank, reviewed weekly.
- **Vector dimension 1024** (bge-m3, strong on Thai).
- **Stack, if resumed:** Cloudflare Workers + Hono · Modal · Supabase (Postgres + pgvector) · R2 · Inngest · Replicate FLUX · Claude API. ~$90-135/mo, hard cap $200. **Deliberately not GCP-native** — IP boundary from the day job.

## The `brand_id` discipline

The one piece of Phase-2 preparation that costs nothing today and is worth keeping: **`brand_id` on every row from day one, even with a single brand.** Opening a client brand later becomes an INSERT rather than a migration. The `post_log` schema already honours this.

---

# PART VI — IMPLEMENTATION ORDER

1. Create `lumora_sprint.db` (or the spreadsheet) with the `post_log` schema and `hook_types` lookup
2. Backfill any posts already published
3. Publish, log every post, update metrics at 24h and 7d
4. Run the weekly ritual on days 7/14/21/28
5. Reach day 90; evaluate against the gate
6. **Stop.** Everything past this point depends on whether the gate passed.

That is the entire build plan. If it feels too small for a Senior Data Engineer, that feeling is precisely what ADR-0001 exists to overrule.

---

# OPEN QUESTIONS

Superseding the five from the previous version, all of which assumed a system that should not be built.

1. **Is the 90-day sprint currently running?** Batch documents exist and the log template is dated 2026-07-18. Actual post count and elapsed days determine everything below.
2. **What has the log captured so far?** Any real rows change the analysis immediately.
3. **Which manual step is most painful right now?** This is what identifies the first adapter if the trigger ever fires — and the answer must come from measurement, not prediction.
4. **Is the day-90 gate still the right gate,** given the LIVE-commerce handicap is now understood? Reach-based was chosen deliberately, but worth one confirmation.
5. **One stale file in the KB.** `CLAUDE.md` is already current (Senior DE at AIA, Azure Databricks + Kafka/Strimzi/Debezium, IP boundary updated). Only `knowledge/00_overview.md` still describes the day job as The1 with a GCP/Beam/BigQuery stack — worth a small edit so the two don't contradict.
6. **Not yet read: `01-batch-30day.md`.** The first 30-day batch is a pending decision *and* a document that exists. It should be read before any further planning.
