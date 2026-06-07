---
name: lumora-content-batch
description: Generate a batch of creator posts for any LUMORA catalog (e.g. สายมู, อาหาร/สุขภาพ, ท่องเที่ยว, gadget, art...) — each post as Content × Theme × Media (per the v3 framework) with concept, hook, caption in the account's voice/archetype, image-model prompt, hashtags, and affiliate angle. Use when Sin wants to plan content, fill a calendar, brainstorm posts, or produce a weekly/30-day batch for an account.
---

# lumora-content-batch

Generate ready-to-produce content for the **lumora** project — catalog-agnostic (สายมู is catalog #1; works equally for อาหาร/สุขภาพ, ท่องเที่ยว, gadget, art, …) — using the v3 framework: **account-level context** (Voice/Archetype + Audience Persona + Niche/catalog scope) fixed per account, and the **post-level library** (Content × Theme × Media, + optional JTBD/HHH) varied per post.

## When to use

- "ขอ content batch อาทิตย์นี้" / "วาง 30 วัน" / "คิด post ให้หน่อย"
- Filling a calendar, brainstorming, or proving out a new account/theme.

## Inputs (ask only what's missing; otherwise use sensible defaults + state them)

**Account-level (fixed for the batch — ask once if unknown):**
- **catalog** — which LUMORA catalog this account sells (สายมู / อาหาร-สุขภาพ / ท่องเที่ยว / gadget / art / …); sets the affiliate categories + sensitivity rules
- **archetype/voice** — e.g. Magician, Sage, Explorer, Jester (pick whatever fits the catalog; the four above happen to fit สายมู)
- **audience persona** — e.g. "GenZ มู สาย aesthetic, 22-32, Bangkok working pro" (or the persona for the account's catalog)
- **niche scope** — broad or narrow

**Post-level (the batch shape):**
- **count** — how many posts (default **7**)
- **content pillars** — which of C1-C10 to draw from (default: ask, or pick 2-3)
- **theme cluster(s)** — which world/setting (Future-tech, Historical, Pastoral, Cosmic, …; open-ended). For a new account, holding ONE theme cluster for the batch keeps the algorithm's positioning clear.
- **affiliate intent** — include a ปักตะกร้า angle per post (default yes)
- **JTBD/HHH** — optional; tag each post's job + funnel stage if asked

## Steps

1. **Load the framework + account rules.** Pull from project knowledge:
   - `mcp__agent-knowledge__search_knowledge(query="framework content theme media archetype voice guardrails", company_filter="project_sandbox", top_k=6)`
   - or read `~/Documents/Projects/Agent/company/project_sandbox/lumora/knowledge/01_creative_library.md` and `02_content_and_channels.md`.
2. **Confirm account context** (archetype + persona + scope). If running for a multi-account setup, note which account this batch is for (see `05_multi_account.md`).
3. **Pick combos.** Vary **Content (C) × Media (M)** across the batch; keep **Theme** consistent for positioning (or rotate deliberately if the account is multi-aesthetic). Don't repeat the same C+M twice. Reference combos by code, e.g. `C1 × Future-tech × M3`. Optionally tag **JTBD** + **HHH** stage (aim ~Hero 5% / Hub 35% / Hygiene 60% over time).
4. **For each post, produce:**
   - **Combo** — `C# × Theme × M#` + plain-language label
   - **(opt) JTBD / HHH** — the job + funnel stage
   - **Concept** — 1 line, what the post IS
   - **Hook** — the first 1-2 seconds / first caption line that stops the scroll
   - **Caption** — in the **account's archetype voice** (e.g. Magician = evocative/transformative; Jester = playful/self-deprecating). Thai-led, "fellow explorer not guru", on-persona, no prediction/medical claims. 2-5 lines.
   - **Image prompt** — use the v3 template: *[Subject from Content pillar] in [Theme] style, volumetric atmospheric lighting, [palette per Theme], [composition], [mood per JTBD], shot on 35mm, [color grade ref], inspired by [artist/film]* — copy-pasteable, 9:16. Add a negative prompt + key params.
   - **Hashtags** — broad catalog tags + Content/Theme-specific tags (e.g. สายมู tags for the spiritual catalog; food/health/travel/gadget tags for others)
   - **Affiliate angle** — the ปักตะกร้า category tied to the Content pillar, drawn from the account's catalog (สายมู e.g. C1→เครื่องราง, C3→ยันต์/ตะกรุด, C5→น้ำมัน/ผง, C2→oracle deck, crystal…; other catalogs map to their own product lines) + a natural mention (if affiliate intent on)
   - **Format note** — production hint per Media type (single/carousel/reel beats/POV/แต่งเรื่อง)
5. **Output** as compact, mobile-friendly per-post blocks. Lead with a one-line batch summary (account/archetype, theme, content + funnel spread).

## Guardrails (hard rules — never violate)

These apply to every catalog; the first two bite hardest for the **สายมู** catalog (and the no-claims rule for **อาหาร/สุขภาพ**):

- **Respect > satire.** Comedy is self-deprecating ("ประเภทคนเข้าวัด", "ขอแล้วลืม") — never mocking believers or deities. (For สายมู especially.)
- **Respectful homage** for sacred imagery — especially **AI images of real deities** (culturally sensitive; dignified, no distortion). (For สายมู especially.)
- **No prediction / medical / financial-guarantee claims.** Frame as art, story, reflection. (Critical for สายมู *and* อาหาร/สุขภาพ — no health cures or guaranteed outcomes.)
- **Fellow explorer, not ผู้รู้/guru.**
- **Voice/archetype consistency > aesthetic consistency** — visuals can vary; the caption voice stays one recognizable person.
- **Diversify revenue** — don't make every post lean on TikTok Shop affiliate (commission cut 2025).

## Notes

- This skill plans + drafts; image generation runs in Sin's backend (FLUX/Replicate — see `knowledge/04_tech_backend.md`), and every asset should be tagged `account_id × content_pillar × theme × media` for analytics.
- Sin likes **multiple aesthetics** — don't force one. Across accounts, see `05_multi_account.md`.
- For deep visual direction → **ai-art-director** agent; for growth/positioning → **content-strategist**.
