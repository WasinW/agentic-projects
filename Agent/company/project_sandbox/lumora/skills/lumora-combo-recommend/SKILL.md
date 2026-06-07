---
name: lumora-combo-recommend
description: The "AI agent brain" as a skill — given trend/product signals + an account's context (archetype/persona/pillars/themes), recommend a ranked list of Content × Theme × Media combos to post next, each with predicted fit, the matching affiliate product, suggested JTBD + funnel stage, and a one-line concept. Use to decide WHAT to make next (the step before lumora-content-batch expands it).
---

# lumora-combo-recommend

The decision engine of the lumora Data Service, run on demand. It answers **"what should this account post next, and why"** by scoring library combos against the account, current trends, and (when available) historical performance — then hands the winners to `lumora-content-batch` to draft.

## When to use

- "วันนี้ควรโพสต์อะไร" / "แนะนำ combo สำหรับ account นี้" / weekly planning / after a `lumora-trend-scan`.
- This is the **Content × Theme × Media recommendation** the v4 AI agent makes; here Sin reviews/approves the suggestions.

## Inputs

- **account context** (required) — archetype + audience persona + active pillars (C-codes) + active themes (ask once if unknown; or read from project knowledge)
- **trend/product signals** (optional) — paste TikTok Shop / Shopee / Lazada trend data, or run `lumora-trend-scan` first, or reason from seasonality + evergreen demand (and SAY which)
- **count** — how many combos to recommend (default **5**)
- **horizon** — this week / this month (affects seasonal weighting)

## Steps

1. **Load the framework + account** from project knowledge:
   `mcp__agent-knowledge__search_knowledge(query="library framework content theme media account archetype", company_filter="project_sandbox", top_k=6)` (+ `01_creative_library.md`, `04_tech_backend.md` for how the agent scores).
2. **Gather signals** — trends (provided/scanned/seasonally-reasoned), and any known performance of past combos (if a `posts`/`performance` log exists; otherwise note "cold-start, no history").
3. **Score candidate combos** on three factors, and SHOW the reasoning:
   - **Account fit** — does `C × Theme` match the archetype/persona + active pillars/themes? (off-brand combos are dropped)
   - **Trend/opportunity** — is there a trending product or seasonal moment this combo can ride? (z-score-style intuition; name the product/affiliate category)
   - **Performance prior** — historical lift for similar combos, or evergreen reliability if cold-start.
4. **Rank + output** a table: `Combo (C × Theme × Media)` | Predicted fit (H/M/L + 1-line why) | Affiliate product/category | Suggested JTBD | Funnel stage (Hero/Hub/Hygiene) | One-line concept.
5. **Balance the slate** — aim for the HHH mix over time (~Hero 5% / Hub 35% / Hygiene 60%), don't make every pick a viral Hero swing; vary Media effort so the batch is producible.
6. **Hand-off** — the approved combos feed `lumora-content-batch` (to draft captions/prompts) → `lumora-art-prompt` (to generate).

## Guardrails

- Respect > satire; respectful homage for sacred imagery; no prediction/medical/financial claims; fellow-explorer voice. (These bite hardest for sensitive catalogs — สายมู spiritual imagery, อาหาร/สุขภาพ health claims — but the respectful, no-guarantee stance applies to every catalog.)
- **Be honest about confidence** — distinguish trend-data-backed vs seasonality-reasoned vs cold-start guess. Don't fabricate metrics.
- **Sin reviews/approves** — this recommends; it does not auto-publish.
- Diversify revenue — don't lean every combo on one platform's affiliate (TikTok Shop commission cut 2025).

## Notes

- This is the manual/assisted version of the v4 **AI agent** (`agent_decisions` table in `04_tech_backend.md`). Once the backend exists, the same logic runs automatically and logs decisions for Sin to approve.
- Multi-account: run per account (`brand_id` / account context). For Phase 2 agency, run per client brand.
