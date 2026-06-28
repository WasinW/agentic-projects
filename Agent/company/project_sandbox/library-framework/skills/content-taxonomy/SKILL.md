---
name: content-taxonomy
description: Apply + validate Sin's Content×Theme×Media (C×T×M) library framework — assign post-level axes (C1-C10 pillars, theme clusters, M1-M12 formats), account-level tags (voice/persona/niche), per-post JTBD+HHH, and run the channel-count formula MIN(S,A)≤N≤S×A with the V1/V2/V3 gates. Use when planning a channel's content space, checking a post combo is valid/non-repetitive, or deciding how many channels to split into. Trigger on "content taxonomy", "C×T×M", "how many channels", "is this combo over-used", "assign theme/pillar/format".
---

# content-taxonomy

The validator + assigner for the Library Framework. This is Sin's own IP (not industry
standard) — full background in `library-framework/knowledge/01-content-taxonomy.md`.
Lumora is customer-zero; its concrete pillars live in the Lumora KB.

## When to use
- Laying out a channel's content space (which pillars × themes × formats).
- Sanity-checking a proposed post: is `(C, T, M)` legal, on-brand, and not a near-duplicate of recent posts?
- Deciding whether one audience should be one channel or several (channel-count formula).

## The model (axes)
A post = a point `(C_i, T_j, M_k)`:
- **C — Content pillars (C1-C10)** — topical buckets, defined per channel.
- **T — Theme clusters** — cross-cutting moods/lenses (Future-tech, Historical, Liminal, Cosmic…). Same pillar × different theme = a different-feeling post.
- **M — Media formats (M1-M12)** — video, carousel, long-form, podcast…

Account-level (set once): **Voice/Archetype**, **Audience Persona**, **Niche Scope**.
Per-post optional: **JTBD**, **HHH funnel stage** (Hero/Hub/Help).

## Validation procedure (run in order)
1. **Legality** — is `(C,T,M)` an allowed combo for this channel? (some pillars don't fit some formats.)
2. **Brand fit** — does the theme + format match the account's Voice/Persona/Niche? Flag drift.
3. **Diversity / anti-homogenization** — compare against the last N posts. If the same `(C,T)` or `(C,M)` repeats beyond a set cadence, reject or re-theme. The whole point of the framework is variety without randomness.
4. **Funnel balance** — across a calendar, keep a healthy Hero/Hub/Help mix; don't stack all Help.
5. **JTBD coverage** — are the channel's core jobs-to-be-done each served by something?

## Channel-count formula
`MIN(S, A) ≤ N ≤ S × A` — S = subject/topic breadth, A = audience segment count.
Where N lands is decided by three audience gates:
- **V1 — overlap threshold (~30%)**: segments overlapping more than this → merge.
- **V2 — viable size (> 10K)**: below → not its own channel.
- **V3 — positioning distinctness**: each channel must pass "is it meaningfully different?".

Procedure: list subjects (S) and audience segments (A) → compute the N range → apply V1 (merge overlaps) → drop sub-V2 segments → V3 test each candidate channel → final N.

## Output
A validated combo (or rejection + reason), or a channel-count recommendation with the V1/V2/V3 reasoning shown.

## Don't
- Don't treat it as Lumora-only — it's a general framework (Lumora is just first customer).
- Don't invent pillars; pull the channel's actual C-list from its account config.
