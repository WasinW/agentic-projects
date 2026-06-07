# 04 — Tech Backend Architecture (Data Fabric Stack — v4)

> Technical-architecture knowledge สำหรับ backend ภายในของ **LUMORA** (catalog-agnostic — รองรับหลาย catalog: สายมู, อาหาร/สุขภาพ, ท่องเที่ยว, gadget, art…; ตัวอย่างในไฟล์ใช้ catalog #1 = สายมู)
> Owner: Sin (Senior DE — GCP/Beam/BigQuery ที่ The1). เขียน concrete ได้เพราะ Sin อ่าน schema/infra รู้เรื่อง.
> Source: `session_context_export_v4.md` — §12 (Two-Service Architecture) + §15 (Tech Implementation: Data Fabric Stack)
> **v4 shift:** stack เปลี่ยนจาก GCP-native (Cloud Run + BigQuery + Cloudflare D1) → **lean modern stack** (Cloudflare Workers + Modal + Supabase + Replicate). เหตุผล: ของเล่นส่วนตัว **ต้องแยกจากงานประจำ** + $200/mo cap + ship เร็ว.
> Rule of thumb: **content + audience มาก่อน, backend ตามมาเท่าที่จำเป็นจริง** — แต่ schema พร้อม multi-brand ตั้งแต่วันแรก.
>
> 📐 **Refined design → see `07_platform_design.md`** (orchestrator-first + adapter seams + ⚙️/🤖 boundary + concept-อธิบายภาษาคน). 07 คือ authoritative "จะ build ยังไง"; diagram ในไฟล์นี้เป็น **conceptual two-service view**. 🟡 5 open questions ยังไม่ตอบ (07 §9).

---

## Backend philosophy

Creator สายมูทั่วไปทำ content **ด้วยมือล้วน** — generate ทีละภาพ, จด prompt ใน Notes, จำเอาว่า combo ไหนเวิร์ค, scrape trend ด้วยตา. Sin มี unfair advantage: **automate สิ่งที่คนอื่นทำมือ แล้ว scale ที่ระดับที่คนทำมือทำไม่ได้.**

หลักการ:

1. **Invisible moat** ⭐ — audience ไม่เห็น backend, เห็นแค่ feed ที่ output สูง + สม่ำเสมอ + ตรง trend. โครงสร้างที่ scale + AI agent ที่ตัดสินใจคือ moat, ไม่ใช่ feature ที่โชว์. คู่แข่งเห็นผลลัพธ์แต่ไม่เห็นเครื่องจักร.
2. **Build once, serve multiple** ⭐ — backend ตัวเดียว `brand_id` ทุกตาราง.
   - **Phase 1:** `brand_id` = Sin's own brand เดียว (type `own`, retainer 0).
   - **Phase 2:** เพิ่ม row brand ใหม่ (type `client`, retainer NN) → **agency** สำหรับ client brands. **ไม่มี schema change** — แค่ insert brand + filter ด้วย `brand_id`.
   - นี่คือสิ่งที่ creator มือ-ล้วน scale ไม่ได้: เขาทำ 1 brand ก็เหนื่อย, Sin มี shared pipeline → เปิด brand ที่ 2-5 แทบไม่มี marginal infra cost.
3. **≤ $200/month total** — hard budget. Phase 1 lean ~$80-120/mo, Phase 2 (มี client) ~$150-250/mo (ลูกค้า absorb cost ผ่าน retainer fee). Architecture (serverless idle ≈ $0 + pay-per-use AI) คือตัวคุม cost ที่ใหญ่สุด.
4. **Separate from The1** — 100% แยกจาก day job. **ไม่ใช่ GCP-native** (จงใจ — กัน IP boundary + ไม่อยากเอา day-job stack มาเล่นต่อตอนเย็น). ใช้ pattern + lesson learned ที่ public ได้เท่านั้น, ห้าม proprietary code/data ของ The1.

> Anti-pattern ที่ต้องเลี่ยง: build full multi-brand workflow + client dashboard ก่อนมี content 30 ชิ้น และ follower 10K. ผิด progression "หนีงาน" (ขั้น 0→1, ห้ามกระโดด). Phase 2 (agency) trigger เมื่อ Sin's own creator พิสูจน์แล้ว + มี informal customer ถามจริง.

---

## Two-service architecture

> Sin คุมเองทั้งหมด (internal infrastructure) — **ไม่ใช่ SaaS**, ไม่มี customer-facing API. แบ่งเป็น 2 services เชื่อมกันด้วย output ของ AI agent. (ดู `06_architecture_agency.md` — Phase 2 agency model + diagram 3/4.)

### Service 1: Data Service (the "Brain")

**Responsibility:** Aggregate data, detect patterns, **decide what to create.**

- **Sources** — multi-platform feeds (TikTok Shop, Shopee, Lazada, social analytics).
- **Data Fabric** — aggregate, normalize, embed (pgvector), store. Entity resolution ข้าม platform → 1 canonical product.
- **AI Agents** — detect trends (z-score), recommend combinations (Content × Theme × Media), predict performance, trigger generation.

**Output:** combos + asset specifications → ส่งให้ Marketing Service.

### Service 2: Marketing Service (the "Hands")

**Responsibility:** Execute creation, distribution, tracking.

- **Content Production** — AI art generation, video creation, caption writing, copy.
- **Multi-Account Post** — schedule, deploy ข้าม platform, community management.
- **Performance Track** — analytics collection → feedback กลับ Data Service (closes the loop).

### How the AI agent connects both services

```text
[Data Service]
  Sources → Data Fabric → AI Agents
                              ↓
              "Combo X + Theme Y + Media Z → trending NOW"
                              ↓
[Marketing Service]
  Production → Posting → Tracking
                            ↓ (feedback)
                  Back to Data Service AI Agents
```

**AI agent's specific jobs:**
- **Watch** trending product data → identify opportunities
- **Match** opportunity กับ library combo (Content × Theme × Media)
- **Predict** performance per combo จาก historical data
- **Trigger** content generation (AI art prompts, video specs, captions)
- **Schedule** optimal posting time
- **Analyze** post performance → update model
- **Recommend** next moves

**Critical:** AI agent คือสิ่งที่ทำให้ framework **operational at scale** — ถ้าไม่มี agent, Sin ต้องเลือก combo เองทุกวัน. ถ้ามี agent, Sin แค่ review/approve suggestion. ใน Phase 2 agent ทำงาน per-brand (`brand_id` isolated) → Sin review per-brand แล้ว Marketing Service execute ให้ทุก brand.

---

## The lean modern stack

> **Scope:** personal side project, 100% separate from The1. **Stack:** lighter/modern, **explicitly NOT GCP-native** (กัน IP boundary + แยกจากงานประจำ). Internal tool ใช้ได้ทั้ง Phase 1 (Sin solo) และ Phase 2 (Sin's agency).

| Layer | Choice | Why | Cost |
|---|---|---|---|
| HTTP/cron | **Cloudflare Workers + Hono** | No egress, edge-fast | $5/mo |
| Heavy/AI compute | **Modal** | Pay-per-second | $10-30/mo |
| Database | **Supabase** (Postgres + pgvector + auth) | All-in-one | Free→$25/mo |
| Object storage | **Cloudflare R2** | No egress fee | $1-5/mo |
| Queue/Events | **Inngest** | Free tier | Free |
| AI image gen | **Replicate** (FLUX.1 dev) | Pay-per-image | $40-60/mo |
| AI animation | **Kling / Runway / Luma** | Pay-per-credit | $20-50/mo |
| AI text/agent | **Claude API** | Best Thai support | $15-30/mo |
| Code runtime | **Bun + Hono** | Modern, fast | $0 |
| Frontend | **Next.js on CF Pages** | Free | $0 |
| Notifications | **LINE / Telegram** | Free | $0 |

### Why this shape

- **Cloudflare Workers + R2** — zero egress สำคัญมากสำหรับ image-heavy workload (asset เยอะ, ดึงบ่อย). Edge = scraper/cron/API เร็วและถูก.
- **Modal** — pay-per-second compute สำหรับ scraper + embedding + heavy job. ไม่ต้องดูแล server, idle = $0.
- **Supabase** — Postgres + **pgvector** (embedding ในตัว) + auth ในที่เดียว. Postgres = Sin คุ้น, pgvector = ไม่ต้องแยก vector DB.
- **Inngest** — durable queue/cron/workflow (เช่น scrape → resolve → embed → notify) บน free tier.
- **Replicate FLUX.1 dev** — pay-per-image, ไม่ self-host จนกว่า volume จะคุ้ม.
- **Claude API** — best Thai support สำหรับ agent reasoning + caption. ใช้ **prompt caching** (system prompt = brand voice + rules ที่ใช้ซ้ำ → cache hit ลดต้นทุน).

### Cost breakdown ($200 budget)

| Bucket | $/month |
|---|---|
| Infra (Workers + Modal + Supabase + R2 + Inngest) | $20-65 |
| AI generation (Replicate + Kling/Runway/Luma + Claude) | $75-140 |
| **Phase 1 lean** | **~$80-120/mo** |
| **Phase 2 (with clients)** | **~$150-250/mo** — clients absorb cost via retainer fees |

---

## Data model

Supabase Postgres + pgvector. **`brand_id` everywhere** — supports both Phase 1 (Sin's own brand only) และ Phase 2 (Sin's brand + multiple client brands) **without schema changes**. เปิด client ใหม่ = insert row ใน `brands` (type `client`) แล้ว filter ด้วย `brand_id`.

```sql
-- Brands tenant (Sin's own + clients)
CREATE TABLE brands (
  brand_id          UUID PRIMARY KEY,
  name              TEXT,
  type              TEXT,           -- 'own' or 'client'
  retainer_amount   DECIMAL,        -- 0 for own, NN for clients
  active_since      DATE
);

CREATE TABLE products (
  product_id        UUID PRIMARY KEY,
  canonical_name    TEXT,
  category          TEXT,           -- มู / art / etc
  embedding         VECTOR(768),    -- pgvector
  created_at        TIMESTAMP,
  last_updated      TIMESTAMP
);

CREATE TABLE product_listings (
  listing_id        UUID PRIMARY KEY,
  product_id        UUID REFERENCES products,
  platform          TEXT,           -- 'tiktok_shop'/'shopee'/'lazada'
  external_id       TEXT,
  url               TEXT,
  price             DECIMAL,
  commission_pct    DECIMAL,
  rating            DECIMAL,
  reviews_count     INT,
  last_scraped      TIMESTAMP
);

CREATE TABLE trends (
  trend_id          UUID PRIMARY KEY,
  product_id        UUID REFERENCES products,
  metric            TEXT,
  value             DECIMAL,
  z_score           DECIMAL,
  timestamp         TIMESTAMP
);

CREATE TABLE accounts (
  account_id        UUID PRIMARY KEY,
  brand_id          UUID REFERENCES brands,  -- which brand owns this account
  platform          TEXT,                    -- tiktok/ig/youtube
  handle            TEXT,
  archetype         TEXT,                    -- voice
  audience_persona  JSONB,
  active_pillars    TEXT[],                  -- C1, C2...
  active_themes     TEXT[]                   -- Future-tech, Historical...
);

CREATE TABLE posts (
  post_id           UUID PRIMARY KEY,
  account_id        UUID REFERENCES accounts,
  content_pillar    TEXT,                    -- C1, C2...
  theme             TEXT,
  media_format      TEXT,                    -- M1, M2...
  jtbd              TEXT,
  funnel_stage      TEXT,                    -- Hero/Hub/Hygiene
  product_ids       UUID[],
  posted_at         TIMESTAMP,
  caption           TEXT,
  asset_url         TEXT
);

CREATE TABLE performance (
  perf_id           UUID PRIMARY KEY,
  post_id           UUID REFERENCES posts,
  views             INT,
  likes             INT,
  shares            INT,
  saves             INT,
  clicks            INT,
  conversions       INT,
  revenue           DECIMAL,
  measured_at       TIMESTAMP
);

-- AI Agent decisions log
CREATE TABLE agent_decisions (
  decision_id       UUID PRIMARY KEY,
  trigger_type      TEXT,                    -- trend/scheduled/manual
  recommendation    JSONB,                   -- combo suggestion
  approved_by       TEXT,                    -- Sin or auto
  executed          BOOLEAN,
  outcome           JSONB,
  created_at        TIMESTAMP
);
```

**Key relationships:**
- `brands` → `accounts` (1 brand มีหลาย account ต่าง platform) → `posts` → `performance`. ทุก analytics วิ่ง up the chain ไปถึง `brand_id` ได้ → **brand-isolated analytics** ใน Phase 2 ฟรี.
- `products` (canonical, มี `embedding`) ← `product_listings` (per-platform raw). **Entity resolution** = ยุบหลาย listing → 1 product → `trends` คำนวณ z-score ต่อ product.
- `posts.product_ids` = array โยง post → affiliate products → ตอบ "combo ไหนขายของอะไรได้".
- `agent_decisions` = audit log ของ AI agent (trigger → recommendation → approve → outcome) → feed กลับเข้า model + เป็น approval-workflow record ใน Phase 2.

> **The `brand_id` discipline:** ทุก query ต้อง scope ด้วย `brand_id` ตั้งแต่ Phase 1 (แม้มี brand เดียว). Phase 2 เปิด client = ไม่มี migration, ไม่มี backfill — แค่ filter. นี่คือ sticky decision ที่ทำให้ agency model เกิดได้โดยไม่ rewrite.

---

## Phased build plan

### Phase 1.A (Week 1-2) — Foundation
- Supabase project + schema setup (ตารางข้างบนทั้งหมด + pgvector extension)
- Cloudflare Workers + Hono API skeleton
- Modal scraper account + first job stub
- R2 bucket สำหรับ asset

### Phase 1.B (Week 3-4) — Single-platform MVP
- **TikTok Shop scraper** (Modal job)
- Daily **cron** (Inngest / CF cron) → scrape → write `product_listings`
- **Trend detection (z-score)** → write `trends`
- Basic **dashboard** (Next.js on CF Pages)

### Phase 1.C (Week 5-8) — Multi-platform + AI
- **Shopee + Lazada scrapers**
- **Entity resolution** — ยุบ listing ข้าม platform → canonical `products`
- **Embedding pipeline** — fill `products.embedding` (pgvector, 768-dim)
- **AI agent: combo suggestion** — watch trends → match library combo → write `agent_decisions`

### Phase 1.D (Week 9-12) — Creator workflow
- **AI art** (Replicate FLUX.1) — trigger generation จาก approved combo → R2 → `posts.asset_url`
- **Auto-tagging** — tag asset ด้วย Content × Theme × Media + product_ids (รู้จาก combo, ไม่ต้อง ML classify)
- **Performance tracking** — collect metrics → `performance`, feedback loop กลับ agent
- **LINE / Telegram bot** — notify Sin: "combo นี้กำลังมา, approve มั้ย?" + daily digest

### Phase 2 (Month 4+) — Agency-ready
> Trigger: Sin's own creator พิสูจน์แล้ว (10K+ followers) + 3-5 informal customer ถามว่าใช้ tool/process อะไร + backend stable.

- **Multi-brand workflow management** — agent + production วิ่ง per `brand_id` พร้อมกัน
- **Client reporting dashboard** — per-brand metrics → ส่ง client
- **Approval workflows** — Sin review agent suggestions per brand (ผ่าน `agent_decisions.approved_by`)
- **Brand-isolated analytics** — ทุก report scope ด้วย `brand_id`, ไม่มี data leak ข้าม client

**Discipline:** อย่า build Phase 2 multi-brand UI / client reporting ตอน Phase 1. Schema เผื่อ `brand_id` ไว้แล้ว (seam พร้อม) — เย็บ workflow จริงเมื่อมี paying signal. premature productization = architecture astronaut.

---

## Cross-references
- Library axes (Content C1–C10 × Theme × Media M1–M12 + JTBD/funnel) — `01_creative_library`
- Voice/positioning ที่ Caption AI ต้อง pin + channel batching — `02_content_and_channels`
- Monetization (affiliate %, digital product, retainer fees) — `03_monetization`
- **Multi-account strategy** (sequential expansion, split patterns) — `05_multi_account`
- **Agency model + two-service diagrams** (Phase 2, SaaS vs agency, `brand_id` scaling) — `06_architecture_agency`
- Business progression "หนีงาน" ขั้น 0→4 — roadmap (อย่ากระโดด phase)
