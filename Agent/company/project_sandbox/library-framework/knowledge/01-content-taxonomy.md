# Library Framework — Content Taxonomy (C × T × M)

> **⚠️ SUPERSEDED — canonical lives in Lumora (folded 2026-07-18).**
> The authoritative version is `…/lumora/knowledge/01_creative_library.md`. This file
> is kept **for history only**; do not edit for content. Two known drifts are **corrected
> in the canonical** (this frozen copy still shows the old text below):
> - **Funnel = Hero / Hub / Hygiene** — the "Hero / Hub / **Help**" below is the drift; canonical uses **Hygiene**.
> - **Channel-count = `1 ≤ N ≤ S×A`, the V1/V2/V3 gates decide** — the `MIN(S,A) ≤ N` lower bound below is **pseudo-math** (a single channel can serve S×A; over-splitting is the solo-creator failure mode).

> Project-specific IP. This is Sin's own framework, not general industry knowledge —
> it stays here, not in `roles/`. Lumora is customer-zero; its bindings live in the
> Lumora KB (`…/lumora/knowledge/01_creative_library.md`). Source: master §A2.

## 1. The three post-level axes

A post = one point in a 3-axis space. Combinatorial variety without homogenization:

- **C — Content pillars (C1-C10)**: topical buckets, defined *per channel*.
- **T — Theme clusters**: cross-cutting moods/lenses — Future-tech, Historical, Liminal,
  Cosmic, etc. The same content pillar rendered through a different theme reads as a different post.
- **M — Media formats (M1-M12)**: video, carousel, long-form, podcast, etc.

A post is therefore `(C_i, T_j, M_k)`. The framework's job: pick combos that maximize
diversity + fit, not repeat the same `(C,T,M)` until the channel feels samey.

## 2. Account-level fixed tags (set once per channel)

- **Voice / Archetype** — channel personality.
- **Audience Persona** — who the channel speaks to.
- **Niche Scope** — narrowness vs breadth.

## 3. Per-post optional tags

- **JTBD** — job-to-be-done the post serves.
- **HHH funnel stage** — Hero / Hub / Help (YouTube's framework).

## 4. Channel Count Formula

`MIN(S, A) ≤ N ≤ S × A`  where **S** = subject/topic breadth, **A** = audience segment count.

Three audience-side gates decide where in that range N lands:
- **V1** — overlap threshold (~30%): segments overlapping more than this should merge.
- **V2** — viable audience size (> 10K): below this, not worth its own channel.
- **V3** — positioning distinctness: each channel must pass a "is it meaningfully different?" test.

## 5. Why this is a *framework*, not just Lumora config

Solves a general problem — systematic diverse content at scale — so it's separable
(AWS-from-Amazon logic). Productization options (master §A2, still open):
(a) internal-only for Lumora · (b) SaaS/license for other creators · (c) consulting setup ·
(d) open-source framework, monetize the agent that runs it.

**Key open question**: separate product vs pure internal IP? Resolve before building anything reusable.

## 6. How it operationalizes (skills)

- `content-taxonomy` **[specific → this project's `skills/`, to create]** — axis definitions + a
  validator (legal combos, diversity scoring, "is this combo over-used?").
- Reuse from Lumora: `lumora-combo-recommend` (picks the next `(C,T,M)` to post),
  `lumora-content-batch` (expands a combo into a full post).
- `agent-workflow-design` (common) — the agent that *runs* the framework over a calendar.

## 7. Agents to consult
content-strategist (taxonomy = content strategy) · solution-architect (system shape) ·
enterprise-architect (productize-or-not, where it sits vs Lumora) · business-analyst ·
ai-engineer (the runner agent) · ux-designer (if it becomes a tool others use).

## 8. Connection to Track B
Conceptually an "agent prompt + workflow library" → directly relevant to **NeurX**
(where agent workflows would live). If productized, could ship *as* NeurX workflows.
