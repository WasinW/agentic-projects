# LUMORA — Index

Sin's **multi-catalog** AI-art creator business (Phase 1: content + commerce; Phase 2: productize the backend). LUMORA spans many catalogs — สายมู, อาหาร/สุขภาพ, ท่องเที่ยว, gadget, art… — with **catalog #1 = สายมู** as the first/worked example; the frameworks are catalog-agnostic. _(Working codename was `saymu-creator`; folder is now `lumora`.)_ See `CLAUDE.md` for how to work here.

## Structure

```
lumora/
├── CLAUDE.md                 # project context (loaded when working here)
├── INDEX.md                  # this file
├── knowledge/                # project knowledge (indexed in vector DB as company=project_sandbox)
│   ├── 00_overview.md
│   ├── 01_creative_library.md
│   ├── 02_content_and_channels.md
│   ├── 03_monetization.md
│   └── 04_tech_backend.md
├── skills/                   # lumora-combo-recommend · lumora-content-batch · lumora-art-prompt · lumora-trend-scan · saymu-oracle
└── memory/                   # running notes / decisions (add as the project evolves)
```

## Knowledge

| # | File | One-liner |
|---|---|---|
| 00 | [overview](knowledge/00_overview.md) | What/who/phases/principles/meta-principles/IP boundary |
| 01 | [creative_library](knowledge/01_creative_library.md) | **v3 framework** — account-level (archetype+persona+scope) + library (Content×Theme×Media) + JTBD/HHH |
| 02 | [content_and_channels](knowledge/02_content_and_channels.md) | Account-level def, pillars, channels, batching, guardrails (10) |
| 03 | [monetization](knowledge/03_monetization.md) | Revenue streams + unit economics + multi-account monetization |
| 04 | [tech_backend](knowledge/04_tech_backend.md) | Multi-account AI-art pipeline + automation + data model + cost |
| 05 | [multi_account](knowledge/05_multi_account.md) | Multi-account strategy (Sin's OWN accounts) — sequential expansion, split patterns, backend |
| 06 | [architecture_agency](knowledge/06_architecture_agency.md) | Two-service architecture + AI-agent loop + **Agency model (NOT SaaS)** + economics + diagrams |
| 07 | [platform_design](knowledge/07_platform_design.md) | **Buildable design** (7-specialist synthesis) — orchestrator-first, ⚙️/🤖 boundary, 3 adapter seams, local↔cloud, build path + **concept primer** 🟡 5 open Qs — **frozen under ADR-0001** |
| ADR-0001 | [park-backend-2026-07-18](knowledge/adr-0001-park-backend-2026-07-18.md) | **PARK the backend, ship by hand** — adapter-build trigger (≥100 posts + >2 hr/week step), LIVE-commerce handicap, human-layer differentiation, AI labeling, no auto-publisher |

## Skills

| Skill | Use |
|---|---|
| [lumora-combo-recommend](skills/lumora-combo-recommend/SKILL.md) | Rank Content×Theme×Media combos to post next (the decide step) — trends + account context → ranked combos + product + JTBD/funnel |
| [lumora-content-batch](skills/lumora-content-batch/SKILL.md) | Generate N posts: combo → concept → hook → caption (voice) → image prompt → hashtags → affiliate angle |
| [lumora-art-prompt](skills/lumora-art-prompt/SKILL.md) | One combo (Content × Theme) → production-ready image-model prompt + params + image→video note |
| [lumora-trend-scan](skills/lumora-trend-scan/SKILL.md) | Scan trends/festivals (any catalog) → map to library combos + affiliate angles |
| [saymu-oracle](skills/saymu-oracle/SKILL.md) | Daily oracle/reading post (catalog #1, C2) — card + art prompt + reflective caption (no prediction claims) |

## Source

Distilled from `Project/project_sandbox/session_context_export.md` (+ `_v2.md`) — the original mobile session handoff.

## Status

**PIVOT (2026-07-18) — 90-day content sprint; backend FROZEN.** Ship posts by hand (5 skills + Claude Code + manual posting + per-post log); codebase parked, not deleted (see [ADR-0001](knowledge/adr-0001-park-backend-2026-07-18.md)). The **Library Framework** was folded in as internal IP — canonical = [`01_creative_library.md`](knowledge/01_creative_library.md). Pending: channel name, voice finalization, archetype (weigh the LIVE-commerce handicap), first 30-day batch, on-camera decision.
