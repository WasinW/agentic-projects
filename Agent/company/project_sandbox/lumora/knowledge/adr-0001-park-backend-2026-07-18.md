# ADR-0001 — Park the LUMORA backend; ship content by hand first

- **Status:** Accepted
- **Date:** 2026-07-18
- **Deciders:** Sin
- **Supersedes:** the implicit "build the invisible tech backend first" assumption in `04_tech_backend.md` / `06_architecture_agency.md` / `07_platform_design.md`
- **Source:** portfolio review `…/projects-knowledge-base/portfolio-review-20260718.md` §3.1 (Lumora — VERDICT: PIVOT)

---

## Context

LUMORA has ~2,105 LOC of backend (`app/`, `cli.py`, `docker-compose`, one commit 2026-06-07, dormant ~6 weeks, **0 tests**) plus ~2,400 lines of KB and 5 working skills. The business itself has **0 channels, 0 posts, 0 followers, 0 THB**. Pending decisions are still step-one questions (channel name, archetype, persona, first 30-day batch).

The backend is a well-built skeleton (adapter registry, 11-state human-approval decision machine, deterministic weighted scorer, per-step cost tracing, `brand_id` from day 1) — **but every integration is a mock**: `ClaudeScript` / `ReplicateImage` / `KlingVideo` / scrapers / publisher are all `NotImplementedError`, and combo assignment is `hash(ext) % len(PILLARS)` (a pseudo-random "brain"). The hard, un-built parts (ToS-hostile scraping, TikTok-app-review publishing) are exactly the parts that are mocked. This is the classic engineer's trap: **building the factory before making the first product by hand.**

Two facts make the backend not just premature but partly redundant:

1. **The 5 skills + Claude Code already ARE the Phase-1 pipeline** — `lumora-trend-scan` (source) → `lumora-combo-recommend` (a *smarter* scorer than the hash-brain) → `lumora-content-batch` / `lumora-art-prompt` (generator) → **Sin's thumb** (publisher). $0 infra, 0 maintenance.
2. **The scorer is data-starved by construction** — lift / fatigue / season weights need performance history that only exists *after* posting. There is nothing to learn from until posts ship.

## Decision

**PARK the backend. Do not delete it.** The skeleton is good and may be resurrected later; deleting it loses real design work. Freeze it and ship content by hand.

### Hard rules (binding until explicitly revisited)

1. **No new adapter — ever — until BOTH are true:**
   - **≥ 100 posts published**, AND
   - a **named, specific manual step eats > 2 hrs/week**.

   When both hold, build **only that one adapter** for that one step. Nothing speculative. No "while we're in here."
2. **Phase-1 pipeline = the 5 skills + Claude Code + manual posting.** That is the whole system. Treat it as the product, not a stopgap.
3. **The only backend LUMORA needs in Phase 1 is a per-post log** — `combo, hook, URL, views, GMV` in a spreadsheet or SQLite. It is both the ops tool *and* the training data the scorer is currently faking. Use `saymu-oracle` (folded into `lumora-content-batch`) as the **daily anchor** — consistency beats sophistication for a new channel.
4. **Freeze all Phase 2 / 3 work** — thinking *and* architecture — until a real Phase-1 case study exists.
5. **NEVER build or use an unofficial / unauthorized auto-publisher.** A ban at 10K followers destroys the entire experiment. Manual posting (or official APIs only) is non-negotiable.

## Two things this decision must carry forward

### The LIVE-commerce handicap (record before choosing archetype)

Thai affiliate conversion **concentrates in LIVE commerce**, which a **faceless AI channel structurally cannot do.** This is not a tuning detail — it caps the conversion ceiling of the faceless archetype and **must be weighed explicitly when choosing the channel archetype** (faceless-AI vs face/persona vs hybrid). Do not pick the archetype without pricing this in.

### Differentiation is human, not automation

Reposition the moat away from *"AI automation at scale"* (a 2026 commodity — Korpi, FlowShorts, AutoShorts, VEO3 pipelines — and actively **suppressed** by TikTok's AI-content enforcement). The real differentiation is:

> **AI-art aesthetic + สายมู cultural literacy + Sin's voice/identity — a human layer on every post (~70/30 human/AI).**

This keeps LUMORA on the right side of the AI-suppression line and apart from AI slop. Corollary: **AI labeling from post #1** (comply with TikTok's mandatory AI disclosure — non-negotiable, day one).

## Options considered

| Option | Verdict |
|---|---|
| **A. Keep building the backend first** (finish adapters, then post) | ✗ Rejected — factory-before-product; hard parts still un-built; scorer data-starved; duplicates the skills. |
| **B. Delete the backend, go pure-manual** | ✗ Rejected — throws away good skeleton work; a real per-post-log need already exists; resurrection stays cheap if parked, not deleted. |
| **C. Park backend, ship by hand via the 5 skills + a per-post log** | ✓ **Chosen** — $0 infra, 0 maintenance, generates the exact data the backend needs, un-blocks the only thing that matters (posting). |

## Consequences

**Positive**
- Zero infra cost / maintenance during Phase 1; effort goes to the one thing that creates value (shipping posts).
- Every post produces the performance data the future scorer needs — parking now makes the backend *better* later.
- A clear, testable resurrection trigger (≥100 posts + a >2 hr/week named step) prevents backend drift and stops a future session from resuming the build by default.

**Negative / accepted**
- No automation; posting cadence is bounded by Sin's manual throughput.
- The skeleton bit-rots slowly (no tests, single dev) — accepted; it is frozen reference, not live code.

**Guardrail for future sessions:** if a later session proposes building an adapter, the resurrection trigger in "Hard rules" #1 is the gate. If both conditions are not met, the answer is no — point back to this ADR.
