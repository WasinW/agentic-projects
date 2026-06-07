---
name: lumora-art-prompt
description: Turn one content idea or library combo (Content × Theme, per the v3 framework) for any LUMORA catalog (e.g. สายมู, อาหาร, ท่องเที่ยว, gadget, art...) into a production-ready image-model prompt — model recommendation, full prompt, negative prompt, params (seed/aspect/steps), and an optional image→video note. Use when Sin needs the actual prompt to generate art.
---

# lumora-art-prompt

Convert an idea or a creative-library combo into a copy-pasteable generation prompt for the **lumora** project.

## When to use

- "ขอ prompt สำหรับ ท่านท้าวเวสฯ cyberpunk" (สายมู) / "prompt จานอาหารสไตล์ minimal" (อาหาร) / "เอา combo A2+S1 ไป gen"
- Right before generating art in the backend (FLUX/Midjourney/etc.).

## Inputs

- **idea or combo** — a free-text concept OR a library code (e.g. for the สายมู catalog `C1 × Future-tech` = Thai deity in cyberpunk Neo-Bangkok; other catalogs resolve their own subject × theme)
- **catalog** — optional; which LUMORA catalog (สายมู / อาหาร / ท่องเที่ยว / gadget / art / …), so the right subject library + sensitivity rules apply
- **model** — optional; else recommend one (FLUX.1, Midjourney v7, Ideogram v3, Imagen 4) based on the need
- **count/variations** — optional (default 1 prompt + 1 variation)

## Steps

1. **Load theme direction + the library** from project knowledge:
   `mcp__agent-knowledge__search_knowledge(query="<content pillar> <theme> prompt direction", company_filter="project_sandbox", top_k=4)` and the ai-art-director knowledge (`role_filter="ai-art-director"`).
2. **Resolve the combo** — Content pillar (the subject) × Theme (the world/setting/palette) → a concrete subject + style + mood (from `01_creative_library.md`). Use the v3 prompt template in `04_tech_backend.md`.
3. **Recommend a model** with one line of why (quality vs cost vs control).
4. **Write the prompt** using prompt anatomy: **subject → style → lighting → composition → camera/lens → mood → quality tags → aspect ratio (9:16 for short-form)**. Make it specific and copy-pasteable.
5. **Add:** a **negative prompt**, key **params** (seed, aspect 9:16, steps/guidance), and 1 **variation** (swap one lever — lighting or composition).
6. **Optional image→video note** — if the post is a reel, suggest a Runway/Kling motion prompt for the still.

## Guardrails

- **Respectful homage** for deities/sacred imagery — dignified poses, no distortion/mockery of religious figures (applies esp. to the **สายมู** catalog; for **อาหาร/สุขภาพ** avoid implying medical/health outcomes in the visual).
- Keep the style on-brand for the chosen catalog + Aesthetic; don't drift mid-feed.

## Notes

- For deep model/consistency decisions (LoRA, IP-Adapter, character consistency across posts) defer to the **ai-art-director** agent.
- Pairs with `lumora-content-batch` (which produces the combo + concept this skill turns into a prompt).
