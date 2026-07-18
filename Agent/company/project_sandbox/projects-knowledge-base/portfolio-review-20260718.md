# Portfolio Review — Final Consulting Report

**Date:** 2026-07-18
**Scope:** ทั้ง 6 sandbox projects — lumora, library-framework, crypto-trading, neurx, regent-ai, sentientnet
**Inputs:** per-project deep dives (code + KB + market ตรวจจริง), 3 portfolio lenses (portfolio-VC, chief-architect, market-skeptic), owner vision/strategy/assumptions
**Audience:** Sin — one person, full-time Senior DE ที่ AIA (เริ่ม 2026-07-01), side-project hours จำกัดและกำลังหดในช่วง ramp-up

---

## 1. Executive Summary

### คำตอบตรงๆ ต่อคำถาม "เวิร์คมั้ย"

**Portfolio นี้ยัง "ไม่เวิร์ค" — ไม่ใช่เพราะ idea ผิด แต่เพราะทุกโปรเจ็คหยุดอยู่หนึ่งก้าวก่อนแตะตลาดจริง** ตัวเลขที่โหดที่สุดจากการ review: ~8 เดือน, ~9,000+ บรรทัด docs+KB, ~3,700 LOC (เกือบทั้งหมด mock หรือ dormant ตั้งแต่ 2026-06-07) — แลกกับ **0 posts, 0 followers, 0 users, 0 บาท** ทุกโปรเจ็ค doc-mature แต่ market-zero

สิ่งที่เวิร์คจริง:
- **วิธีคิด** — agent-centric reframe (2024→2026) ถูกและมาก่อน consensus, engineering discipline สูงผิดปกติสำหรับ solo (locked contract, ADR trail, deterministic-core/LLM-surgical)
- **Agent OS ส่วนตัว** (Claude Code + 33 subagents + 23 skills + KB/Qdrant) — นี่คือ platform เดียวที่มีจริง ใช้จริงทุกวัน และเป็น asset ที่ production-ready ที่สุดในทุกโปรเจ็ค (skills ของ Lumora 5 ตัวทำงานได้วันนี้ — backend ทำไม่ได้)
- **crypto-trading** — v1 เสร็จจริง test ผ่านจริง สร้างใน ~1 วัน พิสูจน์ว่า execution capacity สูงเมื่อ scope เล็ก

สิ่งที่ไม่เวิร์ค:
- **การ execute สู่ตลาด** — Lumora สร้าง factory ก่อนทำสินค้าชิ้นแรกด้วยมือ, คำถามเดียวที่ตัดสินทั้งธุรกิจ ("ช่อง สายมู แบบ Sin-voiced ได้ traction บน Thai TikTok มั้ย?") ราคา ~0 บาท 30 วัน — 8 เดือนแล้วยังไม่ถูกถาม
- **Track B ทั้งสาม** — window ปิดเร็วกว่า prerequisites จะโต: Linux Foundation (AAIF) กำลัง consolidate registry, Entra Agent ID/Okta/Microsoft free OSS toolkit ยึด enforcement point ของ Regent, x402/AP2 ชนะ payments rail ของ SentientNet ไปแล้ว
- **สมการเวลา** — master doc ไม่มีการ model hours/week เลยสักบรรทัด ขณะที่งาน AIA เพิ่งเริ่ม 17 วัน; 6 โปรเจ็ค + meta-infrastructure กิน budget หมดที่ "maintenance" ก่อนจะ ship อะไรที่คนนอกเห็นได้

### Verdict ต่อโปรเจ็ค

| Project | Verdict | เหตุผล 1 บรรทัด | Next action |
|---|---|---|---|
| **Lumora** | **PIVOT** (โปรเจ็คเดียวที่ได้ oxygen) | Concept ใช้ได้ แต่ต้อง invert: หยุดสร้าง platform → ไปเป็น creator; business evidence = 0 และวิธีเดียวที่ถูกคือ publish ไม่ใช่ engineer | Freeze backend, 90-day content sprint ด้วย 5 skills ที่มีอยู่, gate: 1 post ≥50K views หรือ 1K followers ภายใน day 90 |
| **Library Framework** | **PARK → fold เข้า Lumora** | Methodology ดีแต่ standalone ขายไม่ได้ (ตลาด commodity, ไม่มี proof); moat เดียวที่เป็นไปได้ (combo-performance data) เกิดได้ใน Lumora เท่านั้น | Collapse เหลือ canonical file เดียว (Lumora 01_creative_library.md v3), archive repo เปล่า, revisit 12 เดือน |
| **Crypto Trading** | **GO-VIABLE แบบมีเงื่อนไข** | Engine ดีจริง maintenance ~0 แต่ dormant ตั้งแต่ 6 มิ.ย. (ก่อน AIA เริ่ม 3 สัปดาห์ — friction คือ tool ไม่ใช่งาน) | 1 weekend: automation + backtest + journal; ถ้ายังไม่ใช้ภายใน 2026-08-31 → archive ไม่ต้องรู้สึกผิด |
| **NeurX** | **KILL as registry, MERGE เข้า Regent** | Neutral registry window ถูก AAIF + hyperscaler marketplaces ปิด; solo part-time ชนะ two-sided cold-start ไม่ได้; trust/provenance คือ pillar เดียวที่รอด และมัน overlap ~80% กับ Regent | เขียน ADR kill-as-registry, ย้าย trust IP เข้าโปรเจ็ค Track B ที่ merge แล้ว |
| **Regent AI** | **PARK as product, CONVERT เป็น career capital** | ตลาด validate thesis แต่ compliance buyer ซื้อจาก solo unaudited vendor ไม่ได้ (vendor-risk = locked door ไม่ใช่ hard sell) | Dogfood policy-hook + hash-chained audit บน agent fleet ตัวเอง (1 weekend), position ตัวเองเป็นคน agent-governance ใน AIA |
| **SentientNet** | **PARK indefinite** | P(activation) = ผลคูณ 4 เงื่อนไขที่แต่ละตัว <50% ≈ 0; micropayments rail แพ้แล้ว (x402/AP2); sovereign lane กำลังถูก incumbents ยึด | ลบ micropayments pillar + 3 phantom skills, donate sovereign-deployment angle ให้ Regent, stamp KB "FROZEN" |

**Net: 6 โปรเจ็ค → 1.5 active workstreams** (Lumora content sprint + Trust & Governance practice แบบ capped) + 1 tool ที่ run ตัวเอง (crypto) ไม่มีอะไรมีค่าหายไป — 4 ใน 6 มี 0 LOC หรือ mock-only อยู่แล้ว

---

## 2. Portfolio-Level Strategy

### 2.1 Focus / Kill / Merge

ถ้ามองแบบ seed-fund portfolio review: นี่ไม่ใช่ 6 โปรเจ็ค — มันคือ **1 bet (Lumora), 1 tool (crypto), 1 career asset (Regent-as-practice), และ 3 narratives (NeurX/SentientNet/Library-standalone)**

- **FUND:** Lumora เท่านั้น และ fund แค่ 90-day content sprint (check size: ~$150/mo + evenings) — ไม่ fund backend
- **HOLD:** crypto-trading — 1 weekend timebox, hard trigger สิ้นสิงหา
- **MERGE:** NeurX + Regent → 1 parked "Agent Trust & Governance" project (registry = thin UI ทับ trust layer; สอง vision projects แชร์ evening hours เดียวกันแย่กว่าหนึ่งเสมอ) + ดูด sovereign-deployment angle จาก SentientNet เข้ามา
- **KILL as standalone:** library-framework (→ Lumora internal IP), SentientNet (เก็บ 150 บรรทัด narrative ไว้ฟรีๆ, ลบ pillar ที่ตายแล้ว)

### 2.2 เวลาที่มีจริง vs ที่ต้องใช้ — constraint ที่ไม่เคยถูก price

Verified: master doc **ไม่มี hours/week modeling เลย** นี่คือช่องโหว่ที่ใหญ่ที่สุดของทั้ง strategy

ความจริง: AIA เริ่ม 2026-07-01 — ตอนนี้อยู่ใน 90 วันที่แย่ที่สุดสำหรับ side projects (ramp-up + สร้าง credibility กับทีมใหม่) Budget ที่ซื่อสัตย์: **6–10 hrs/week quarter นี้** อาจขึ้น 10–15 หลัง ramp Portfolio ตามที่ document ไว้ (6 โปรเจ็ค + 33-agent infra + Qdrant reindex + KB hygiene) กิน budget นั้นหมดที่ maintenance ก่อน ship อะไรเลย

**Action ที่มาก่อนทุก roadmap: track ชั่วโมงจริง 4 สัปดาห์** ตัวเลขนี้ — ไม่ใช่ roadmap ไหนๆ — เป็นตัวตัดสินทุกอย่าง ถ้าได้ <6 hrs/week ให้ rescope sprint (เช่น 3 posts/week โดยมี saymu-oracle เป็น daily anchor) แทนที่จะพลาดเงียบๆ

### 2.3 "Track A funds Track B" ยืนได้มั้ย — ไม่ได้ ในรูปปัจจุบัน

Dependency chain ตามแผน: Lumora Phase-1 revenue (50–200K THB/mo) → NeurX → Regent → SentientNet ปัญหาคือ **สองข้างของสมการวิ่งสวนทางกัน**:

- ฝั่ง funding: modeling ที่ซื่อสัตย์ = 0–10K THB/mo ใน 6 เดือนแรก *ของการโพสต์* (ซึ่งยังไม่เริ่ม) → Track B unlock เร็วสุดปลาย 2027
- ฝั่ง window: AAIF registry consolidation, Entra/Okta/free MS toolkit, x402/AP2 — ปิด **ตอนนี้** พอ Track A fund ได้ spec ของ Track B จะเป็น archaeology (KB landscape ตัวเองก็ rot ไปแล้วใน <13 เดือน — "the lane is open" เป็น false statement แล้ววันนี้)

**Thesis ต้อง rewrite ไม่ใช่ enforce:**
> Track A funds **Sin's exit from employment**. Track B เป็น **option** ที่ต้อง re-underwrite จาก fresh landscape scan ณ เวลา unlock — ไม่ใช่ roadmap ที่รอ execute

Track B value เดียวที่เก็บได้บน horizon ปัจจุบัน = **career capital**: Sin ทำงานใน regulated insurer ที่กำลังจะเจอคำถาม agent governance จริงๆ — Regent KB monetize ได้*ทันที*ในรูป "คนที่เข้าใจ agent audit/policy ใน AIA" ด้วย build cost = 0

### 2.4 Revealed preference — ปัญหาที่ต้องพูดตรงๆ

ระบบปัจจุบัน reward การผลิต meta-artifacts ที่ปลอดภัย (KB files, skills, ADRs, กระทั่ง review นี้เอง) มากกว่า act เดียวที่สร้าง information จริง: **publish สิ่งที่คนแปลกหน้า judge ได้** Knowledge infrastructure กลายเป็นโปรเจ็คที่ 7 ที่ไม่ได้ fund — และเป็นตัวเดียวที่มี maintenance record ดีที่สุด หลักฐานแย้งคือ crypto: เสร็จจริงใน ~1 วันเมื่อ scope เล็กและไม่มีใครดู แปลว่า bottleneck ไม่ใช่ความสามารถหรือเวลา — คือ comfort zone

**Rule ใหม่ portfolio-wide (จาก market-skeptic, ผมเห็นด้วยเต็มที่): market-contact rule** — ห้ามโปรเจ็คไหนได้ engineering/docs/KB hour เพิ่ม จนกว่าจะทำ market-facing action ถัดไปของตัวเองก่อน (Lumora: โพสต์; crypto: ใช้จริง 1 สัปดาห์; Track B: ไม่มี → parked) Planning hours บนโปรเจ็คที่ยังไม่แตะตลาด = procrastination by definition

### 2.5 Exit ladder — ปรับความคาดหวัง

Day-job-exit threshold (revenue ≥ salary × 1.5 นาน 6 เดือน) เป็น **2028+ event** ในทุก credible scenario โอเคเลย — fail-cheap คือ posture ที่ประกาศไว้อยู่แล้ว — แต่ ladder docs ต้องหยุด imply Year-1 escape velocity เพราะความคาดหวังนั้นแหละที่เลี้ยง 6 โปรเจ็คไว้ทั้งที่ตัวเดียวควรได้ oxygen และอย่าลืม: **restate employer IP boundary สำหรับ AIA** (ของเดิมเขียนไว้สำหรับ The1)

---

## 3. รายโปรเจ็ค

### 3.1 Lumora — VERDICT: PIVOT

**สถานะจริง:** ~2,105 LOC (FastAPI + CLI + docker-compose, commit เดียว 2026-06-07, dormant 6 สัปดาห์, **0 tests**) + KB ~2,400 บรรทัด 9 files + 5 working skills ธุรกิจ: **0 channels, 0 posts, 0 followers, 0 บาท** Pending decisions ยังเป็นเรื่อง step-one: ชื่อช่อง, archetype, persona, first 30-day batch Ratio: ~4,500 บรรทัด docs+code : 0 published posts

**Tech assessment:** โครงดีผิดปกติ — adapter registry 5 seams, 11-state decision machine ที่บังคับ human approval, deterministic weighted scorer, per-step cost tracing, `brand_id` ตั้งแต่ day 1 **แต่ทุก integration เป็น mock** — ClaudeScript/ReplicateImage/KlingVideo/scrapers/publisher ทั้งหมดคือ `NotImplementedError` และ combo assignment คือ `hash(ext) % len(PILLARS)` — "สมอง" ตอนนี้สุ่ม pseudo-random ส่วนที่ mock ไว้ (scraping ที่ ToS-hostile, publishing ที่ต้องผ่าน TikTok app review) คือส่วนยากทั้งหมด — สร้าง factory ก่อนทำสินค้าชิ้นแรกด้วยมือ classic engineer's trap

จุดที่เจ็บกว่านั้น: **backend duplicate สิ่งที่มีอยู่แล้ว** — 5 skills + Claude Code *คือ* Phase-1 pipeline (trend-scan = source, combo-recommend = scorer ที่ฉลาดกว่า hash-brain, content-batch/art-prompt = generator, นิ้วโป้ง Sin = publisher) ที่ $0 infra, 0 maintenance และ scorer ก็ data-starved by construction — lift/fatigue/season ต้องการ performance history ที่จะมีก็ต่อเมื่อโพสต์แล้วเท่านั้น

**Business assessment:** ตลาดจริง — TikTok Shop TH affiliate + สายมู เป็น vertical belief-driven conversion สูง (commission 5–20%) แต่ 3 headwinds ที่ KB ประเมินต่ำไป:

1. **"Invisible tech moat" ไม่ใช่ moat** — faceless AI TikTok automation เป็น commodity ปี 2026 (Korpi, FlowShorts, AutoShorts, VEO3 pipelines) ทุกคน generate volume ได้; principle #7 ของ Sin เองก็ยอมรับแล้วว่า asset จริงคือ voice + cultural depth + curation
2. **Platform risk เป็น structural แล้ว** — TikTok 2026: C2PA auto-detection, mandatory AI labels, Creator Rewards แบน AI content, enforcement +340% ใน 2025; labeled AI content โดน suppress ขณะที่ affiliate เป็นเกม views-volume; agencies แนะนำ ~70/30 human/AI blend Pure AI-slop MCN คือ category ที่ platform กำลังไล่ปราบพอดี
3. **Revenue band ฝันไป** — 50–200K THB/mo Phase 1 คือ outcome top-percentile ที่ถูกเขียนเป็น base case; ซื่อสัตย์คือ 0–10K THB/mo ใน 6 เดือนแรก และ market-skeptic ชี้จุดที่ docs ไม่เคยพูดถึง: **Thai conversion เกิดที่ LIVE commerce ซึ่งช่อง faceless ทำไม่ได้ structural** — ต้อง record handicap นี้ก่อนตัดสิน archetype

**สิ่งที่ควรปรับ:**
- *Architecture:* **PARK backend** (ไม่ลบ — skeleton ดี) Hard rule: ห้ามเขียน adapter ใหม่จนกว่า ≥100 posts published AND มี manual step ที่ระบุชื่อได้กิน >2 hrs/week — แล้วสร้างเฉพาะ adapter ตัวนั้น
- *Design:* reposition differentiation จาก "AI automation at scale" (โดน suppress, commodity) → **"AI-art aesthetic + สายมู cultural literacy + เสียง/ตัวตนของ Sin"** — human layer ทุกโพสต์ (~70/30) เพื่ออยู่ฝั่งถูกของเส้น AI-suppression และแยกตัวจาก AI slop
- *Features:* backend เดียวที่ Phase 1 ต้องการคือ **per-post log** (combo, hook, URL, views, GMV) ใน spreadsheet/SQLite — เป็นทั้ง ops tool และ training data ที่ scorer fake อยู่ตอนนี้ ใช้ saymu-oracle เป็น daily anchor (consistency ชนะ sophistication สำหรับช่องใหม่)
- *Business model:* freeze Phase 2/3 ทั้ง thinking และ architecture work จนกว่า Phase-1 case study จะมีจริง; comply AI labeling ตั้งแต่ day 1; ห้ามสร้าง/ใช้ unofficial auto-publisher เด็ดขาด — ban ที่ 10K followers = ทั้ง experiment พัง
- *Ops:* KB hygiene — ลบ `00_overview 2.md` duplicate, แก้ The1→AIA, บันทึก PARK decision เป็น ADR กัน session หน้า resume backend โดย default

**Risks:** zero-execution (8 เดือน 0 โพสต์ + ชั่วโมงหดจาก AIA), TikTok AI policy พลิกได้ทุก quarter (sharecropping), moat illusion → sunk effort ต่อเนื่อง, สายมู sensitivity (AI sacred imagery + no-claims compliance), affiliate commission compression (fee ขึ้น พ.ค. 2026), solo maintenance ของ codebase ที่สองที่ไม่มี test

### 3.2 Library Framework — VERDICT: PARK (fold เข้า Lumora)

**สถานะจริง:** standalone แทบไม่มีอะไร — README 17 บรรทัด + `doc/` ว่างเปล่า + KB ~190 บรรทัด ของจริงอยู่ใน Lumora ทั้งหมด: `01_creative_library.md` (223 บรรทัด, v3 canonical — doc ที่เขียนดีที่สุดใน cluster), taxonomy ฝังใน code/schema ของ Lumora แล้ว, skills operationalize อยู่แล้ว

**Tech assessment:** core insight จริงและไม่ trivial (แยก slow-moving account identity ออกจาก fast-varying C×T×M) + theory-grounding ดี + operationalize เป็น skills แทน app คือ call ที่ถูกสำหรับ one-person shop **แต่:** (1) premature abstraction — AWS-from-Amazon analogy กลับหัว: AWS ถูก extract *หลัง* proven internal load หลายปี ที่นี่ customer-zero ยังโพสต์ 0 ครั้งแต่ framework มี **4 copies** แล้ว; (2) **drift เริ่มแล้ว** — Hero/Hub/**Hygiene** (Lumora, ถูก) vs Hero/Hub/**Help** (KB+skill); (3) **channel-count formula เป็น pseudo-math** — lower bound `MIN(S,A) ≤ N` เป็นเท็จ (ช่องเดียว serve S subjects × A segments ได้ และ default ของ Lumora เองก็ violate มัน) พลังตัดสินใจจริงอยู่ที่ V1/V2/V3 gates ทั้งหมด แก้เป็น `1 ≤ N ≤ S×A`, gates decide — formula เดิมเสี่ยงดันไปทาง over-splitting ซึ่งคือ failure mode คลาสสิกของ solo creator; (4) **zero feedback loop** — claim กลาง (diversity → sustained engagement) ไม่เคยแตะ data

**Business assessment:** standalone product = ตายตั้งแต่เกิด ตลาด AI content-planning saturate สุดขั้ว (~96% ของ SMM ใช้ AI daily; content pillars เป็น free built-in ทุก tool) — taxonomy ไม่ใช่ product มันคือ blog post ที่ copy ได้ในหนึ่งรอบอ่าน Moat เดียวที่เป็นไปได้ = **performance dataset** (combo ไหน work per niche/platform) ซึ่ง accrue ได้*ใน Lumora เท่านั้น* — นั่นคือ argument ที่แข็งที่สุดว่านี่คือ internal IP และมัน monetize ทางอ้อมผ่าน Phase-2 agency pitch ("เรามี proprietary diversity system + data")

**สิ่งที่ควรปรับ:** collapse เหลือ canonical เดียว (Lumora v3), ที่เหลือเป็น pointer; แก้ formula + reconcile Hygiene/Help ใน pass เดียว; archive repo เปล่า; สร้าง measurement loop เมื่อ Lumora เริ่มโพสต์ (DB columns มีแล้วใน 001_init.sql); ตอบ open question ใน KB อย่างชัดเจน: **internal IP, revisit ใน 12 เดือน** เมื่อมี ≥1 channel ที่มี framework-attributable growth ตัวเลข public ถ้า externalize จริง path คือ content-led authority (StoryBrand-style) ไม่ใช่ SaaS — **never (b) SaaS license**

**Risks:** 4-copy drift ที่จะแย่ลงทุกการแก้, zero validation ใต้ productization thesis ทั้งก้อน, commodity market, pseudo-rigor ดันสู่ over-splitting, opportunity cost — ทุกชั่วโมง packaging คือชั่วโมงที่ขโมยจากสิ่งเดียว (Lumora shipping) ที่จะทำให้ IP นี้มีค่า

### 3.3 Crypto Trading Engine — VERDICT: GO-VIABLE (มีเงื่อนไข)

**สถานะจริง:** โปรเจ็คที่ engineer ดีที่สุดใน sandbox — 1,623 LOC / 13 modules, 30 tests ผ่านหมด (verified), 9 ADRs, locked pydantic contract, config-driven ทุก param สร้างใน ~1 วัน (2026-06-07) แล้ว **ไม่ถูกแตะอีกเลย 6 สัปดาห์** — run แค่ 2 ครั้ง deterministic-only, LLM path ไม่เคย run live จุดสำคัญ: หยุดใช้ 3 สัปดาห์*ก่อน* AIA เริ่ม — **friction คือ manual CLI ไม่ใช่งานใหม่**

**Tech assessment:** layering textbook, discipline rules ที่ encode ไว้คือ IP จริง (oversold ≠ long, no counter-trend, stand-aside default, macro haircut) แต่มี gaps ที่ทำให้ tool ยัง**อันตรายกว่าไม่มี tool**:
1. **Zero validation — gap ใหญ่สุด**: weights (0.22/0.16/0.20…) กับ conviction bands เป็น opinion จาก design session ไม่เคย test กับ candles 2.5 ปีที่มีอยู่บน disk — "confidence 0.493" คือ false precision ที่ launder gut feel ผ่านตัวเลข
2. **Elliott LLM layer structurally unsound**: digest ส่งแค่ 3 swing highs/lows — นับ wave ไม่ได้ → confabulation ที่ดู authoritative
3. Dead knob `confidence.floor: 0.45` — อยู่ใน config+spec แต่ code ไม่เคย reference (verified by grep); playbook decision table ใน doc/03 §4 spec ครบแต่ถูก delegate ไป LLM prose
4. `interpret.py` hardcode `claude-opus-4-8` — ผิด rule ตัวเอง; Opus overkill → Sonnet
5. ไม่มี deterministic position sizing (~20 บรรทัด, มีค่ากว่า Elliott block ทั้งก้อน) และ**ไม่มี journal** — discipline tool ที่ไม่มี journal คือ signal printer

**Business assessment:** ไม่มี business model — **โดย design และถูกแล้ว** ตลาด AI crypto-signal saturate, zero moat, ขาย recommendation ใน TH = Thai SEC advisory licensing/liability **Never productize** Frame ที่ถูกคือ personal ROI: value (b) — proving ground ของ agent-build workflow — **เก็บเกี่ยวไปแล้ว** (เห็นชัดในวิธีที่ Sin run AIA sandbox ตอนนี้); value (a) — discipline ถ้าใช้ — ตอนนี้ = 0 เพราะไม่ได้ใช้

**สิ่งที่ควรปรับ (ทั้งหมดใน 1 weekend, ตามลำดับ):**
1. **Backtest harness ก่อนทุกอย่าง** (~200 บรรทัด): replay candles → bias ทุก close → forward-return distribution ต่อ bias/conviction bucket ถ้า short-bias forward returns ไม่ negative → retune หรือเลิกเชื่อ weights
2. **Automate หรือตาย**: launchd/cron daily analyze + push artifact เข้า Telegram — tool ต้องมาหาเรา
3. **Trade journal** (append-only jsonl): artifact id, action taken, entry/exit, R + monthly plan-vs-actual review
4. Elliott: feed full pivot series (30+) หรือตัดทิ้ง เก็บ LLM ไว้แค่ summaries/plan; Opus→Sonnet, model name เข้า engine.yaml
5. Implement playbook table deterministic + wire `confidence.floor` + position sizing `(risk% × equity) / stop_distance`
6. หลัง automation แล้วเท่านั้น: เพิ่ม ETHUSDT (config-only)

**Hard trigger: ถ้าสิ้นเดือนสิงหา 2026 ยังไม่ได้ใช้ → archive พร้อม KB** — บทเรียน agent-workflow คือ payoff ที่จ่ายแล้ว parking ไม่มี loss Freeze roadmap: no dashboard, no predictive ML, no webhook

**Risks:** เชื่อ unvalidated weights ด้วยเงินจริง (แย่กว่าไม่มี tool), abandonment (manual CLI + full-time job = death rate ~100%), Elliott confabulation, scope creep จาก README roadmap, bit-rot (hardcoded model string, ccxt drift)

### 3.4 NeurX — VERDICT: KILL as registry / MERGE เข้า Regent

**สถานะจริง:** vision-stage แท้ — ~200 บรรทัด prose สองที่, **0 code, 0 schemas, 0 prototypes** README สัญญา `doc/` มี architecture notes แต่โฟลเดอร์ว่าง ของดีชิ้นเดียว: landscape note (2026-06-27, sourced) + agent-registry-patterns skill ที่ map ถูกกับ A2A v1.0 จริง 1 ปีของ idea = 100% thinking / 0% artifact; 4 open questions copy ไว้ 3 ไฟล์โดยไม่มีการตัดสินใจ — copy คำถามไม่ใช่ progress

**Tech assessment:** wedge analysis ครึ่งถูก — "MCP-server registry เป็น commodity, build ทับ official registry" ถูก แต่: (1) **scope fantasy** — 4 pillars (Registry/Interop/Runtime/Observability) = 4 บริษัท; Runtime pillar เดียวคือ Bedrock-AgentCore-class undertaking; unbounded scope คือเหตุผลที่ไม่มีอะไรถูกสร้าง; (2) **existential risk อยู่ใน KB ตัวเองแต่ไม่เคยถูกถาม** — A2A roadmap ที่ KB cite เองมี registry consolidation ใต้ Linux Foundation AAIF (OpenAI, Anthropic, Google, Microsoft, AWS, Block) และ A2A v1.2 ship signed AgentCards แล้ว — spec กำลังดูด wedge สุดท้าย (card signing/trust) เข้าตัวมันเอง; (3) trust เป็น pillar เดียวที่ defensible (hyperscaler แต่ละเจ้า verify แค่ walled garden ตัวเอง) — และมัน overlap ~80% กับ Regent → **NeurX กับ Regent คือระบบเดียวที่แกล้งเป็นสองโปรเจ็ค**

**Business assessment:** macro จริง (A2A 150+ orgs, MCP ~97M monthly downloads) — และนั่นแหละคือปัญหา: layer ที่ระเบิดขนาดนี้ไม่ถูกทิ้งไว้ให้ neutral third party Enterprise distribution ถูก hyperscaler ยึด (Microsoft Marketplace 4,000+ agents ที่ 3% fee, Gemini Enterprise, AWS category, AgentExchange); dev registry layer แน่น (official MCP Registry, Smithery 430K devs/mo); Solo.io ship enterprise Agent Registry แล้ว (ก.ค. 2026) และ registry monetize แย่แม้ตอนชนะ — npm รอดเพราะโดนซื้อ, Docker Hub ลากอยู่สิบปี Two-sided cold-start solo part-time unfunded vs foundation gravity = แพ้ก่อนเขียนบรรทัดแรก Customer-zero logic ก็เพี้ยน: Lumora ต้องการ internal orchestration + policy/guardrails = customer-zero ของ *Regent* ไม่ใช่ NeurX

**สิ่งที่ควรปรับ:** เขียน **ADR kill-as-registry อย่างเป็นทางการ** (ไม่ใช่ soft park — ตาม market-skeptic ซึ่งผมเห็นด้วย เพราะ "parked registry" จะกลับมาหลอกใน session อนาคต); ตัด Runtime + Observability **permanent** ไม่ใช่ deferred; merge trust/provenance IP เข้าโปรเจ็ค Track B เดียว; ตอบ 4 open questions ลง ADR ใน 30 นาที (default: open-source tooling, global DX, Lumora = Regent's customer-zero, sit above Smithery); stamp landscape file perishable + rule "re-scan ก่อนเชื่อ positioning ใดๆ ตอน unpark"; ถ้าคันมือจริง: 1 weekend probe — CLI `neurx-card validate|sign|verify` สำหรับ A2A cards, zero infra — ถ้าไม่มีใคร care ก็ kill trust thesis แบบถูกๆ ได้เลย ถ้า Lumora ต้องการ agent infra ให้สร้างเป็น Lumora-internal plumbing — **platform-from-one-customer คือวิธีที่ solo founder จมน้ำ**

**Risks:** AAIF ประกาศเดียว wedge หาย, hyperscaler distribution lock, two-sided cold-start, registry monetization แย่ by nature, Track B cannibalization (NeurX/Regent แย่ง evening hours ก้อนเดียวกัน), perpetual vision-stage (KB scaffolding สร้าง motion-feeling โดยไม่มี information gain)

### 3.5 Regent AI — VERDICT: PARK as product / CONVERT เป็น practice + career capital

**สถานะจริง:** positioning brief ไม่ใช่โปรเจ็ค — repo 2 ไฟล์ 4KB **0 LOC**, `doc/` ว่างทั้งที่ README สัญญา, KB ~220 บรรทัด ของดี: 2 skills (agent-policy-engine, audit-trail-design) — design primitives ถูกและ dense (default-deny, least-privilege-per-task, policy-as-data, enforce ที่ tool-call boundary, hash-chained audit, provenance graph) Effort จริง ≈ 1 research session และ dependency คือ "layer on top of NeurX" — vision ซ้อน vision ที่ยังไม่ถูกสร้าง

**Tech assessment:** thesis ถูกและมาก่อน consensus (agent autonomy/liability ไม่ใช่ model explainability — ตลาด converge ตรง 3-part stack ที่ KB บรรยายเป๊ะ) แต่: (1) **ไม่มี architecture ให้ประเมิน** — 4 pillars, 0 decisions: ไม่มี policy language choice, ไม่มี schema draft, ไม่มี enforcement-point design — สำหรับโปรเจ็คที่ product *คือ* schema + enforcer การไม่มีแม้ strawman schema หลัง 1 ปีคือ tell; (2) **policy-language blind spot** — KB ไม่พูดถึง OPA/Rego หรือ Cedar เลย ทั้งที่มัน dominate MCP/agent authorization ปี 2026 — invent DSL เองคือ classic mistake; (3) **Art. 12 over-claim ที่ผิด convention ตัวเอง** — "plain DB ไม่ compliant ต้อง hash-chained + signed" เกิน literal text ของ regulation (tamper-evidence เป็น defensible interpretation ผ่าน Art. 15 ไม่ใช่ mandate ตรงๆ) — พูดแบบนี้ต่อหน้า compliance buyer จริงเสีย credibility ตรงจุดที่ Regent จะขาย; (4) **commodity erosion** — Microsoft agent-governance-toolkit ฟรี OSS ครบ OWASP Agentic 10/10 sub-ms policy eval; pillars 1–2 กลายเป็น table stakes ที่ compose ไม่ใช่ build; pillar เปิดจริงเหลือ **multi-agent provenance ข้าม vendors (A2A)** เดียว; (5) **ไม่เคย dogfood ทั้งที่ dogfood นั่งอยู่ตรงหน้า** — Claude Code PreToolUse hooks *คือ* runtime enforcement point; hash-chained JSONL audit ของ fleet ตัวเอง = weekend project เขียน checklist เกี่ยวกับมันโดยไม่ทำ = vision-stage trap

**Business assessment:** ตลาด validate เร็ว — และนั่นคือปัญหา: (1) identity incumbents ยึด enforcement point (Entra Agent ID GA เม.ย. 2026, Okta for AI Agents, AgentCore Identity); (2) governance-platform tier แน่น (Credo AI, Arthur ฯลฯ); (3) OSS floor สูง (ฟรีจาก Microsoft) และ **why-buy พังแบบ structural**: buyer ที่ care (regulated enterprises, EU AI Act enforcement 2 ส.ค. 2026) **ซื้อจาก solo part-time unaudited vendor ไม่ได้** — vendor-risk review, SOC 2 ของ vendor เอง, references, SLA — นี่คือประตูล็อค ไม่ใช่ GTM ที่ยาก Angles ที่รอด: customer-zero/internal (จริง ตอนนี้), **career capital ที่ AIA** (จริง ตอนนี้ ฟรี), Thai/SEA content play (gap จริง timing ยังไม่ถึง — Thai AI Act ยัง draft), standalone global product (ไม่ viable — window ปิดขณะ Regent อยู่ที่ 0 LOC)

**สิ่งที่ควรปรับ:** lock ใน master doc §B2: "no product build จนกว่า merged Track B มี ≥1 external user AND Lumora Phase-1 revenue"; **dogfood weekend project**: PreToolUse policy enforcer + hash-chained JSONL audit บน agent fleet ตัวเอง (permission matrix, spend/rate caps, HITL threshold, chain verification) — เป็นทั้ง Regent demo, protection จริงให้ Lumora content agents, และ pressure test ที่เปลี่ยน skills จาก notes เป็น IP; **ADR: Cedar (หรือ OPA) เป็น substrate, never invent DSL** — novelty ของ Regent อยู่ชั้นบน (HITL thresholds, spend caps first-class, A2A handoff trust gates, cross-vendor provenance); แก้ Art. 12 wording ให้ cite ตรง; redirect compliance depth ไป AIA ทันที; Thai AI Act = tracked option — เมื่อ law ออกจริง เป็นคนแรกที่ publish Thai-language mapping (content/consulting ไม่ใช่ SaaS); หลัง dogfood ให้ fold สิ่งที่พังจริง (latency, policy ergonomics) กลับเข้า skills

**Risks:** market window ปิดสำหรับ solo greenfield, vendor-risk = locked door, triple-stacked dependency (Regent←NeurX←Lumora revenue — P รวม ≈ 0), Art. 12 over-claim ทำลาย credibility ที่จะขาย, attention tax จาก Lumora + AIA ramp

### 3.6 SentientNet — VERDICT: PARK indefinite

**สถานะจริง:** บางที่สุดใน 6 — named placeholder + mood board ~150 บรรทัด markdown, 0 LOC, `doc/` ว่าง, skills ว่าง (3 planned skills ไม่เคย scaffold) Source of truth จริงคือ §B3 ของ master doc (~30 บรรทัด) Open questions ทั้ง 3 (crypto rails? buyer? horizon?) ไม่ถูกตอบตั้งแต่ 2024

**Tech assessment:** สิ่งที่ดี — self-discipline หายาก ("VISION-STAGE — do not build" + default skepticism on crypto rails = restraining order ที่เขียนให้ตัวเอง เก็บไว้) และ reframe 2024→2026 ถูก (จาก dead crypto narrative → sovereignty จริง) สิ่งที่ผิด: (1) **third-order dependency = compounded improbability** — P(activate) = P(Track A profit) × P(NeurX users) × P(Regent established) × P(lane ยังเปิดใน 3–5 ปี) — แต่ละ factor <50% ผลคูณ ≈ 0 นี่ไม่ใช่โปรเจ็ค มันคือ*อนุประโยคที่สี่ของประโยคที่อนุประโยคแรกยังไม่เกิด*; (2) 4 pillars = 4 บริษัทคนละ buyer ไม่มี wedge เดียว ไม่มี MVP เดียว; (3) **KB rot แล้วใน <13 เดือน** — micropayments ถูก standardize โดยคนอื่น (x402: 165M+ txns, 69K agents; Google AP2; Skyfire; card networks) และ "none own the sovereign-agent framing" เป็นเท็จแล้ว (ioMoVo GA พ.ค. 2026, Nagent, Lyzr, hyperscaler sovereign clouds) — structural problem ของ vision-stage KB ใน fast market: **มัน decay เร็วกว่า prerequisites จะโต** ถึงตอน NeurX+Regent มีจริง (2029+?) ไฟล์นี้คือ archaeology

**Business assessment:** macro จริงมาก — และนั่นคือปัญหา: Thailand launch ThaiLLM (รัฐทำเอง — **buyer สร้างของเองแล้ว**), THB 500B+ cloud pledges, Thailand AI Cloud, ETDA roadmap Buyer (gov/regulated enterprise sovereign procurement) ต้องการ certifications, local entity, references, BD headcount — **solo DE ที่มี full-time job ไม่มี structural path ถึง customer นี้** และจะไม่มีอีกหลายปี มูลค่าจริงวันนี้ = **narrative** — apex ของ Track B stack diagram ที่ทำให้ NeurX+Regent รู้สึกเป็นบันไดสู่อะไรที่ใหญ่ มี motivational value จริงและ cost ~0 — as a company EV ≈ 0 บนทุก horizon ที่ Sin act ได้ **Asset เดียวที่ salvage ได้:** "sovereign deployment for Thai/SEA regulated enterprises" เป็น *feature* ไม่ใช่บริษัท — และมันเป็นของ **Regent** (compliance-first governance + data-residency/self-host ขายให้ buyer เดียวกัน เร็วกว่า ~5 ปี)

**สิ่งที่ควรปรับ (30 นาทีแล้วเลิกแตะ):** ทำ PARK เป็นทางการใน master doc + README พร้อม 3 un-park triggers (Track A sustained cash-flow / NeurX external users / real sovereign-buyer conversation — ครบทั้งสามเท่านั้น); **ลบ (ไม่ใช่ defer) micropayments pillar** — ถ้าอนาคต agents ต้อง pay ให้ adopt x402/AP2 as consumer, never build rails; migrate sovereign angle เข้า Regent เดี๋ยวนี้; stamp landscape file "FROZEN 2026-07 — assume stale" + 5-line addendum (x402/AP2, ioMoVo, ThaiLLM); ลบ 3 planned skills ออกจาก roadmaps — deferred-skills list คือ fake progress; README บอกตรงๆ "no docs by design"; zero recurring maintenance — ไม่ re-research, ไม่ embed refresh, re-research from scratch ตอน un-park เท่านั้น

**Risks:** compounded dependency ≈ 0, lane closure ก่อน prerequisites โต, buyer inaccessibility, KB rot ป้อน false premises เข้า future agent sessions, portfolio attention tax (แม้ 0-code ก็กิน narrative/planning cycles ที่ Track A ต้องการกว่า)

---

## 4. 90-Day Action Plan (ranked)

**Rule เดียวที่คุมทั้งหมด: market-contact rule** — โปรเจ็คไหนไม่ทำ market-facing action ถัดไปของตัวเอง = ไม่ได้ hour เพิ่ม

### Priority 0 — สัปดาห์นี้ (half-day doc-surgery, ครั้งเดียวจบ)
- Merge NeurX+Regent → 1 parked "Agent Trust & Governance" project; ADR kill-NeurX-as-registry; ดูด sovereign angle จาก SentientNet
- Fold library-framework เข้า Lumora (canonical = 01_creative_library.md v3, ที่เหลือ pointer); archive repo เปล่า; แก้ Hygiene/Help + channel formula
- Stamp ทุก parked landscape file "FROZEN — assume stale"; ลบ phantom skills lists; ลบ `00_overview 2.md`; แก้ The1→AIA; restate IP boundary สำหรับ AIA
- Rewrite thesis ใน master doc: "Track A funds exit; Track B = option, re-underwrite at unlock" + un-park triggers + rule ห้าม parked project กิน sessions
- เริ่ม track ชั่วโมงจริง/สัปดาห์ (4 สัปดาห์) — ตัวเลขนี้ตัดสินทุก schedule ข้างล่าง

### Priority 1 — Lumora 90-day content sprint (โปรเจ็คเดียวที่ funded)
- **สิ่งเดียวที่ต้อง prove: ช่อง สายมู แบบ Sin-voiced (~70/30 human/AI) ได้ traction บน Thai TikTok ได้หรือไม่**
- ตัดสิน 4 account decisions (archetype — โดย record LIVE-commerce handicap ก่อน, persona, pillars, ชื่อช่อง) **ในหนึ่งนั่ง** — ห้ามลากเป็น research
- ~30 posts ใน 30 วัน: skills ที่มี + Replicate + CapCut + manual posting; saymu-oracle = daily anchor; AI labeling ตั้งแต่โพสต์แรก; ห้าม auto-publisher
- Per-post log ทุกโพสต์ (combo, hook, URL, views, GMV) — spreadsheet/SQLite พอ
- **Gate ตั้งวันนี้: 1 post ≥50K views หรือ 1K followers ภายใน day 90** → ต่อ; พลาด → เปลี่ยน tone/catalog หรือ park ทั้งโปรเจ็ค
- Zero backend code — repo frozen ทั้ง sprint

### Priority 2 — Crypto: 1 weekend, จบ
- **สิ่งเดียวที่ต้อง prove: automation ทำให้ tool ถูกใช้จริงหรือไม่**
- ลำดับ: backtest harness → cron + Telegram push → journal → (ถ้าเหลือเวลา) playbook table + confidence.floor + sizing + Elliott fix
- **Kill date: 2026-08-31 ยังไม่ใช้ → archive** ไม่ต่อรอง

### Priority 3 — Trust & Governance practice (capped ~4 hrs/month)
- **สิ่งเดียวที่ต้อง prove: dogfood (PreToolUse policy hook + hash-chained audit บน fleet ตัวเอง) เป็นสิ่งที่ Sin เก็บ run ต่อจริงหรือไม่**
- 1 weekend สร้าง → fold บทเรียนกลับเข้า 2 skills → position ตัวเองใน AIA เป็นคน agent-governance สำหรับ regulated insurer
- Track Thai AI Act draft; law ออก → publish Thai mapping คนแรก (content play)

### Priority 4 — Portfolio meta
- **สิ่งเดียวที่ต้อง prove: AIA เหลือ ≥8 hrs/week หลัง ramp หรือไม่** — ถ้า <6 → rescope sprint เป็น 3 posts/week ไม่ใช่ปล่อยพลาดเงียบ
- Meta-infrastructure freeze: no new skills/KB/agents ให้ parked projects; hygiene pass เดียวแล้วหยุด — **knowledge system serve portfolio, ห้ามเป็น portfolio เสียเอง**
- นัด portfolio re-review Q1 2027 — checkpoint แรก: AAIF registry-consolidation status + ผล Lumora gate

---

## 5. Appendix — จุดที่ Critics ขัดกับ Analysts และคำตัดสิน

**1. Lumora: PIVOT (analyst) vs "MCN vision fails on three fronts" (market-skeptic)**
Analyst ให้เก็บ concept ไว้แล้ว invert execution; skeptic ชี้ว่า MCN/platform vision พังเชิงโครงสร้าง (commodity production, TikTok = landlord ที่เกลียดคุณ, affiliate math ไปไม่ถึง target + LIVE handicap) **คำตัดสิน: ทั้งคู่ถูกคนละชั้น — เดินตาม skeptic เชิง framing, ตาม analyst เชิง action** สิ่งที่รอดคือ "90-day publish-or-park experiment ราคา ~0 บาท" ไม่ใช่ "O&O MCN vision" — sprint คือการทดสอบ ไม่ใช่ก้าวแรกของ MCN; วิสัยทัศน์ MCN/Phase-2/3 frozen จนกว่า gate จะผ่าน และผม adopt ข้อเรียกร้องของ skeptic ที่ให้ record LIVE-commerce handicap ลง KB *ก่อน*ตัดสิน archetype เพราะมัน material ต่อ decision นั้นจริง

**2. NeurX: "PARK with pre-decided pivot" (analyst) vs "KILL formally with ADR" (skeptic)**
**คำตัดสิน: ไปทาง skeptic — KILL-as-registry เป็น ADR ไม่ใช่ soft park** เหตุผล: ระบบของ Sin มีแนวโน้มพิสูจน์แล้วว่า "parked" project ยังกิน narrative/planning cycles (SentientNet กินมาปีนึงทั้งที่ 0 LOC) และ landscape ที่ปิดแล้ว (AAIF + Solo.io shipping + A2A v1.2 signed cards) ไม่ใช่สิ่งที่จะ reopen สำหรับ solo Soft park ของสิ่งที่ตายแล้วคือ liability ใน KB — ADR ตายชัดๆ ถูกกว่า

**3. Agent OS: "the only platform, ลงทุน governance ให้มัน" (chief-architect) vs "the unfunded 7th project / procrastination machine" (VC + skeptic)**
**คำตัดสิน: ประนีประนอมแบบมีเงื่อนไข** Architect ถูกที่ Agent OS เป็น platform เดียวที่จริงและ layering (Claude Code → Agent OS → projects as thin config) คือ end-state ที่ถูก แต่ VC/skeptic ถูกกว่าในเรื่อง*ลำดับ*: ระบบที่ maintain ดีที่สุดใน portfolio คือระบบที่ไม่มี market contact — นั่นคือ warning sign ไม่ใช่ความสำเร็จ ดังนั้น: hygiene pass **ครั้งเดียว** (canonical-file rule, FROZEN stamps, The1→AIA sweep) แล้ว **freeze** — automated reindex, meta-governance เพิ่มเติม ฯลฯ รอจนกว่า Lumora sprint จะจบ ข้อยกเว้นเดียว: dogfood policy-hook (Priority 3) เพราะมัน overlap เป็น Regent demo + career capital พร้อมกัน — ROI สามชั้นใน weekend เดียว

**4. Outcome ledger: "build once, shared component" (chief-architect) vs "อย่าสร้าง infra เพิ่มก่อน market contact" (skeptic)**
Architect เสนอ append-only outcome ledger ตัวเดียว serve ทั้ง Lumora per-post log + crypto journal + framework data **คำตัดสิน: เอา concept, ลด scope** — สร้างเป็น 2 ไฟล์แยกง่ายๆ (spreadsheet/SQLite ของ Lumora, jsonl ของ crypto) ก่อน; unify เป็น shared component เมื่อทั้งคู่มี data จริง >1 เดือน การ design shared schema ก่อนมี consumer จริงคือ trap เดียวกับที่ Lumora backend ตกไปแล้ว

**5. "Track A funds Track B": enforce gate (owner strategy + neurx analyst) vs rewrite thesis (VC)**
**คำตัดสิน: rewrite (ตาม VC)** Enforce gate เฉยๆ แปลว่ายอมรับ premise ว่า Track B specs วันนี้จะยัง valid ตอน unlock — ซึ่ง review นี้พิสูจน์แล้วว่าเท็จ (ทุก landscape file rot ใน <13 เดือน) Track B ที่ unlock ตอน 2027–28 ต้อง underwrite ใหม่จากศูนย์ ดังนั้น thesis ที่ถูกคือ "Track A funds exit; Track B = option + mandatory fresh scan" — และมันปลดภาระทางใจด้วย: Sin ไม่ต้อง "รักษา" Track B vision ระหว่าง sprint

**6. Crypto: GO-VIABLE (analyst) vs "time-sink with authoritative styling" (skeptic)**
**คำตัดสิน: ตาม analyst แต่ยืม teeth ของ skeptic** — เก็บเพราะ finished + tiny + ค่า parking ~0 แต่ hard kill date 2026-08-31 ไม่เลื่อน และ insight ที่สำคัญที่สุดของ skeptic ต้อง underline: **unvalidated tool ที่ดู rigorous อันตรายต่อเงินตัวเองกว่าไม่มี tool** — เพราะงั้น backtest มาก่อน automation ในลำดับงาน weekend

**7. Phase-1 revenue: 50–200K THB/mo (owner docs) vs 0–10K/6mo (ทุก lens)**
ไม่มี lens ไหนเถียงกันเรื่องนี้ — ทุกตัวเห็นตรงข้าม owner docs **คำตัดสิน: re-model ทันทีใน master doc** 50–200K คือ top-percentile outcome ที่ถูกเขียนเป็น base case; ladder หนีงานที่พึ่งตัวเลขนี้จะเลี้ยง 6 โปรเจ็คไว้ต่อด้วยความหวังผิดๆ Base case ใหม่: 0–10K THB/mo ใน 6 เดือนแรกของการโพสต์, exit = 2028+ event, ให้ Lumora gate — ไม่ใช่ revenue band ใน doc — เป็นตัวตัดสินว่า Track A มีอยู่จริงมั้ย

---

*Report นี้ synthesize จาก 6 per-project deep dives + 3 portfolio lenses (portfolio-vc, chief-architect, market-skeptic) — จุดที่ขัดแย้งถูกตัดสินใน Appendix ไม่ได้เฉลี่ยให้กลมกล่อม*
