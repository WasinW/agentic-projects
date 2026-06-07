# Project: LUMORA

> Sin's part-time **multi-catalog creator business** — AI-generated art + comedy/anime tone,
> monetized via affiliate (ปักตะกร้า) + digital products, powered by an **invisible tech backend**
> that gets productized later.
> _(The working codename was `saymu-creator`; the project is now **LUMORA** and the folder is `lumora`.)_
> **Multi-catalog:** LUMORA spans many catalogs — สายมู, อาหาร/สุขภาพ, ท่องเที่ยว, gadget, art… —
> with **catalog #1 = สายมู** (Thai spiritual/mystical) as the first/worked example. The frameworks
> (Content×Theme×Media, two-service architecture, platform design) are **catalog-agnostic**.

## What this is (one line)

Build a creator audience + content + selling first (Phase 1); the AI-art/automation backend is the moat; productize it for SME/B2B (data-microservice) in Phase 2.

## Who

**Sin** — Data Engineer at The1 (Central Group, Thailand). 10+ yrs. GCP/Beam/BigQuery/Iceberg stack. Divergent creative thinker (keeps a *library* of ideas, combines selectively — does NOT force single-niche convergence).

**Communication:** Thai + English technical terms. Practical, specific, mobile-friendly. Pushes back when an answer drifts off-point. Wants honest takes, not generic positivity. Tables/structured comparisons welcome; avoid over-formatting / excess emoji.

## How to work in this project

1. **Search project knowledge first** — it's in the vector DB under `company_filter="project_sandbox"`. Call `mcp__agent-knowledge__search_knowledge(query="...", company_filter="project_sandbox", top_k=5)`, or read `knowledge/` directly.
2. **Respect the divergent style** — diverge → keep diverging → combine selectively. Don't prematurely converge to one aesthetic/niche.
3. **Voice > aesthetic** — what unifies the brand is Sin's voice, not a single visual style.
4. **Honor the guardrails** (see `knowledge/02_content_and_channels.md` §Warnings): respect > satire, sacred imagery = respectful homage, "fellow explorer" not guru, NO prediction/medical claims.
5. **The1 IP boundary** — patterns + lessons OK; never proprietary code/data.

## Knowledge map (`knowledge/`)

| File | Covers |
|---|---|
| `00_overview.md` | Business model, phased roadmap, "หนีงาน" ladder, strategic + meta principles, IP boundary |
| `01_creative_library.md` | **The v3 framework** — account-level (Voice/Archetype + Audience Persona + Niche scope) + post-level library (Content C1-10 × Theme clusters × Media M1-12) + optional JTBD/HHH; grounded in marketing theory |
| `02_content_and_channels.md` | Account-level definition, content pillars, channels, batching, archetype voice, short-form mechanics, guardrails (10) |
| `03_monetization.md` | Affiliate / digital products / subscription / partnership + unit economics + multi-account monetization |
| `04_tech_backend.md` | **v4 lean stack** (Cloudflare/Modal/Supabase/Replicate, ≤$200/mo, not GCP) + two-service architecture + full SQL data model (brand_id everywhere) + phased build plan |
| `05_multi_account.md` | Multi-account strategy (Sin's OWN accounts, not customers) — sequential expansion, split patterns, backend |
| `06_architecture_agency.md` | Two-service architecture (Data brain + Marketing hands + AI agent loop) + **Agency model (NOT SaaS)** + economics + 4 diagrams |

## Skills (`skills/`)

| Skill | Use |
|---|---|
| `lumora-combo-recommend` | The "AI agent brain" — given trends + account context, rank Content×Theme×Media combos to post next (the decide step) |
| `lumora-content-batch` | Expand chosen combos into posts: concept → hook → caption (account voice) → image prompt → hashtags → affiliate |
| `lumora-art-prompt` | One combo (Content × Theme) → production-ready image-model prompt + params + image→video note |
| `saymu-oracle` | Daily oracle/reading post (C2) — card + art prompt + reflective caption (no prediction claims) |
| `lumora-trend-scan` | Scan สายมู trends/festivals → map to combos + affiliate angles |

## Which agents to pull in

- **content-strategist** *(to be created)* — creator-economy / short-form growth, pillars, hooks, voice
- **ai-art-director** *(to be created)* — generative image/video prompt engineering, aesthetic direction
- **marketing-consultant** — audience growth, channel strategy, segmentation
- **sales-consultant** — affiliate / TikTok Shop conversion, commerce
- **finance-consultant** — creator-business unit economics, margins
- **investment-consultant** — Phase-2 productization go/no-go
- **ai-engineer** — Claude API caption gen, RAG prompt library, automation
- **solution-architect** / **de-engineer** / **software-engineer** — the backend build + analytics
- **platform-ops** — cost/infra (~$60-150/mo); **security-engineer** — API keys, scraping ToS, content safety

## Phase

**Phase 1 (now):** content + multichannel + selling + minimum-viable backend. Still employed full-time (หนีงาน ขั้น 1). Don't jump phases.

## Pending decisions (open)

Channel name + bio + visual identity · voice positioning (finalize 1-2 sentences) · first 30-day batch (which 2-3 combos to prove first) · affiliate-first vs digital-product day-1 · show face on camera?
