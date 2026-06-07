# 06 — Architecture + Business Model (Business × System, Canonical)

> Business-model + system-architecture knowledge สำหรับ lumora — สอง service ที่ Sin คุมเองทั้งหมด + business model = **O&O MCN + Multi-Catalog Lab, ไม่ใช่ SaaS** (agency = Phase 2 / หนึ่ง slice ของ commerce pillar เท่านั้น).
> Owner: Sin (Senior DE). อ่าน schema/infra รู้เรื่อง → เขียน concrete ได้.
> Source: `session_context_export_v6.md` §12 (Two-Service Architecture) + §13 (O&O MCN + Multi-Catalog Lab — replaces "Agency" as THE model) + §15 (Phase 3 Platform Intelligence Service) + §22 (4 Diagrams Reference). SVG source ของ diagram อยู่ใน v6 appendix §25.
> Cross-ref: `04_tech_backend.md` (AI agent + pipeline concrete), `05_multi_account.md` (sequential expansion), `03_monetization.md` (revenue map).
> **Critical:** §13 เป็น **major reframe** — เดิมเรียก business model ว่า "Agency" (และก่อนหน้านั้น multi-tenant SaaS, **ผิด**). ตอนนี้ THE model = **O&O MCN + Multi-Catalog Lab** (3 pillars). Agency demote เป็น **Phase 2 ของ commerce pillar**. Sin ไม่ต้องการ SaaS — ทั้ง agency (B2B) และ platform-intelligence (B2P) เป็น service ที่ Sin รันเอง ไม่ใช่ self-serve tool.
>
> 📐 **Technical "จะ build ยังไง" → see `07_platform_design.md`** (orchestrator-first, ⚙️/🤖 boundary, 3 adapter seams, local-vs-cloud, build path + concept-อธิบายภาษาคน). ไฟล์นี้คือ business + system model; 07 คือ buildable design. 🟡 5 open questions ยังไม่ตอบ.
>
> 🏢 **Business model นำทาง = O&O MCN + Multi-Catalog Lab** (3 pillars: own multi-channel creator / multi-catalog incubator / multi-platform commerce). Agency = Phase 2 ของ Pillar 3. Platform Intelligence (B2P) = Phase 3.

---

## Two-service architecture

Architecture แบ่งเป็น **2 services** ที่ Sin **คุมเองทั้งหมด** (internal infrastructure — ไม่มี external API, ไม่มี customer-facing UI). เชื่อมกันด้วย **output ของ AI agent** + **feedback loop**.

### Service 1: Data Service — the "Brain"

**หน้าที่:** aggregate data, detect patterns, **decide what to create**.

| Component | สิ่งที่ทำ |
|---|---|
| **Sources** | Multi-platform feeds — TikTok Shop, Shopee, Lazada, social analytics |
| **Data Fabric** | Aggregate → normalize → embed → store (architectural concept, **ไม่ใช่** Microsoft Fabric) |
| **AI Agents** | Detect trends, recommend combinations (Content × Theme × Media), trigger generation |

**Output:** combos + asset specifications → ส่งต่อให้ Marketing Service.

### Service 2: Marketing Service — the "Hands"

**หน้าที่:** execute creation, distribution, tracking.

> 📐 **Content Production แตกข้างในเป็น gen-pipeline หลายสเต็ป** (🤖 LLM script/storyboard/prompt + 🎨 gen-API รูป/วิดีโอ + ⚙️ ffmpeg assemble), แตกต่างตาม media_format → ดูรายละเอียด `07_platform_design.md §2.5`.

| Component | สิ่งที่ทำ |
|---|---|
| **Content Production** | AI art generation, video creation, caption writing, copy |
| **Multi-Account Post** | Schedule, deploy ข้าม platforms, community management |
| **Performance Track** | Analytics collection → feedback กลับเข้า Data Service (**closes the loop**) |

### How the two connect

```
[Data Service — Brain]
  Sources → Data Fabric → AI Agents
                              │
              "Combo X + Theme Y + Media Z → trending NOW"
                              ▼
[Marketing Service — Hands]
  Production → Posting → Tracking
                              │ (feedback: views/saves/sales)
                              ▼
                  back to Data Service AI Agents
```

Brain ตัดสินใจว่า **จะสร้างอะไร** → Hands **ลงมือสร้าง+กระจาย+วัดผล** → ผลลัพธ์วิ่งกลับเข้า Brain เพื่อปรับ model. นี่คือ closed loop ที่ทำให้ระบบฉลาดขึ้นเรื่อยๆ โดยไม่ต้อง Sin คอยป้อนมือ.

---

## The AI agent (what makes it operational at scale)

AI agent คือชิ้นที่เปลี่ยน framework จาก "ตารางที่ Sin ต้องเลือกเอง" → **"ระบบที่ทำงานได้จริงที่ scale"**. มันคือสะพานระหว่าง Brain กับ Hands.

**งานเฉพาะของ agent (เรียงตาม flow):**

1. **Watch** — เฝ้า trending product data จาก sources → ระบุ opportunity
2. **Match** — จับคู่ opportunity กับ library combo (Content × Theme × Media)
3. **Predict** — ทำนาย performance ต่อ combo จาก historical data
4. **Trigger** — สั่ง generate content (AI art prompts, video specs, captions)
5. **Schedule** — เลือก optimal posting time
6. **Analyze** — วิเคราะห์ post performance → update model
7. **Recommend** — เสนอ next moves

> **Critical point:**
> - **ไม่มี agent** → Sin ต้องเลือก combo **เองทุกวัน** (manual, scale ไม่ได้, เหนื่อยแค่ 1 account ก็เต็มมือ).
> - **มี agent** → Sin **review/approve** suggestions ของ agent → scale ไป N accounts/brands ได้โดย marginal effort ต่ำ.

Concrete implementation ของ pipeline (FLUX/Replicate, D1 metadata, multi-account router, ETL→BigQuery) อยู่ใน `04_tech_backend.md` — ไฟล์นี้พูดถึง **role** ของ agent ในภาพ business, ไม่ใช่ stack.

---

## Business model — O&O MCN + Multi-Catalog Lab (THE model)

> **⚠️ Major reframe.** Business model นำทางคือ **Owned & Operated Multi-Channel Network (O&O MCN) + Multi-Catalog Product R&D Lab** — **ไม่ใช่** SaaS, **ไม่ใช่** pure agency, **ไม่ใช่** single-creator brand. "Agency" = **หนึ่ง slice ของ Pillar 3 (commerce), Phase 2** เท่านั้น — ดู section ถัดไป.

Sin **เป็นเจ้าของ channels เองทั้งหมด** (O&O) ไม่ใช่บริหาร KOL คนอื่น (= affiliate MCN แบบ AnyMind/Studio71). Model = **"Ruhnn–Beast hybrid"**: 3-pillar influencers+incubator+supply-chain ของ Ruhnn + content→demand→product→content loop ของ Beast (MrBeast) — แต่เพิ่ม **AI-automated production** (cost edge), **multi-vertical R&D**, และ **Thai cultural specificity**.

### 3 Pillars

```
PILLAR 1 — Multi-Channel Creator   (own channels, NOT contracted)
  3-5 channels/catalog · แต่ละ channel = distinct (Segment × Aesthetic)
  Sin's role: ideate + review (AI agent ทำ production)

PILLAR 2 — Multi-Catalog Incubator (R&D for product/market)
  multi-catalog (Phase 1 เริ่มที่ catalog แรก) → อาหาร, ท่องเที่ยว, gadget, art (Phase 1.5+)
  catalog ทดสอบผ่าน own channels ก่อน → ตัวที่เวิร์ค expand/productize

PILLAR 3 — Multi-Platform Commerce (affiliate + agency + platform services)
  Phase 1: Affiliate (TikTok Shop / Shopee / Lazada)
  Phase 2: Agency services (boutique, SMB brands)        ← "agency" อยู่ตรงนี้
  Phase 3: Platform Intelligence Service (B2P)            ← ดู section ท้ายไฟล์
```

> หมายเหตุ catalog: เดิมพูดเป็น "สายมู" เป็น niche เดียว — จริงๆ คือ **multi-catalog** (สายมูเป็น catalog แรกของ Pillar 2, ไม่ใช่ทั้งหมดของ business). Framework เดียว serve ได้ทุก catalog.
> Defensible moats: O&O multi-catalog (ไม่มีใครทำในไทย) · AI-automated cost edge · cultural specificity · lean ops ($150-300/mo) · multi-direction creative (Library Framework กัน homogenization).

---

## Phase 2 (commerce pillar) — Boutique Agency, NOT SaaS

> Agency = **Phase 2 ของ Pillar 3**, ไม่ใช่ "the model". เดิม Phase 2 ถูกวาดเป็น multi-tenant SaaS — **WRONG**. Sin ยืนยัน: เป็น **boutique agency** (B2B service, Sin รันเอง). Sin **ไม่ต้องการ** ทำ SaaS.

### SaaS (ผิด) vs Agency (ถูก)

| | SaaS (WRONG) | Agency (CORRECT) |
|---|---|---|
| **ใครใช้ Data Fabric** | Customer self-serve | **Sin only (internal)** |
| **Customer relationship** | Subscription | Service contract |
| **Sin's role** | Tool provider | **Service provider** |
| **Pricing** | $50-200/mo subscription | **30K-150K THB/mo retainer** |
| **Backend access** | Multi-tenant API exposed | **Internal only** |
| **Effort per client** | Low (self-serve) | High (Sin runs everything) |
| **Margin** | High (software) | Medium (services) |
| **Moat** | Tool features | **Tool + Sin's expertise** |
| **Scale model** | Exponential | **Linear (1 Sin = 3-10 clients)** |

### Why agency over SaaS (5 เหตุผล)

1. **Higher ticket per client** — 30K-150K THB vs $50-200/mo
2. **Sin คุม quality control** — output ดีกว่า (เพราะ Sin ทำเอง ไม่ปล่อยลูกค้าใช้ tool ดิบ)
3. **ไม่ต้องมี customer-facing UI** — ship เร็วกว่ามาก
4. **ลูกค้ายอมจ่ายมากกว่า** — เขา **ไม่ต้อง learn tool**, จ่ายเพื่อผลลัพธ์
5. **Tool ยังเป็นความลับ** — competitive moat ไม่หาย (ถ้าเปิด API ลูกค้าเห็นหมด → moat หาย)

> Mental model: Sin ขาย **ผลลัพธ์ + expertise**, ไม่ได้ขาย **access to tool**. Backend = invisible moat (cross-ref `04_tech_backend.md §1`).
> หมายเหตุศัพท์: multi-**account** (Sin เปิด N channel เอง = Pillar 1) ≠ multi-**tenant** (ลูกค้าภายนอกเข้า backend). Agency = Sin รัน multi-account/multi-brand **ภายใน** ให้ลูกค้า, ไม่ใช่เปิด tenant.
> **Never SaaS, ทั้ง 2 phase:** agency (Phase 2, B2B) และ platform-intelligence (Phase 3, B2P) **ต่างก็เป็น Sin-operated service** — ลูกค้าจ่ายเพื่อ service/ผลลัพธ์ ไม่ใช่ self-serve access เข้า tool. Tool ยังเป็น invisible moat ตลอด.

---

## Agency economics (Phase 2 of commerce pillar)

### Sweet spot

```
  3-5 clients @ 50-100K THB/mo/client   =  200-500K THB/mo  (agency fees)
+ Sin's own creator income (at scale)   =   50-200K THB/mo  (affiliate + own products)
─────────────────────────────────────────────────────────────────────────
= 300-700K THB/month total              →  เพียงพอออกจาก The1 ได้สบาย
```

### Constraints (ข้อจำกัดที่ต้องยอมรับ)

- **Linear scale** — รายได้โตตาม **เวลา Sin**, ไม่ exponential
- **1 person → 3-10 clients max** — เกินนั้นคนเดียวไม่ไหว
- **> 10 clients → ต้อง hire team** (cost เพิ่ม, margin ลด)
- **Revenue ขึ้นกับ client retention** — เสียลูกค้า = รายได้หายเป็นก้อน (ไม่เหมือน SaaS ที่ churn ทีละน้อย)

### Phase 2 trigger conditions (5 ข้อ — ต้องครบก่อนขยับ Phase 1 → Phase 2)

1. **Own stack proven** — creator stack ของ Sin เอง พิสูจน์ traction แล้ว: 10K+ followers อย่างน้อย 1 account
2. **Predictable affiliate income** — รายได้ affiliate จาก account ตัวเอง คาดเดาได้
3. **3-5 informal customer requests** — มีคนถาม "ใช้ tool/process อะไร" จริง 3-5 ราย
4. **Backend stable for multi-brand** — tech backend นิ่ง + รองรับ multi-brand workflow ได้
5. **Time bandwidth** — Sin มีเวลา onboard ลูกค้า (น่าจะต้องลด commitment กับ The1)

> อย่ากระโดด Phase 2 เพราะ "ดูคุ้ม" — กระโดดเมื่อ **5 ข้อนี้ครบเท่านั้น**. ผิด progression "หนีงาน" = พัง (cross-ref `00_overview.md`).

---

## The 4 diagrams (reference)

> Render แล้วใน chat. **SVG source อยู่ใน v4 export appendix §22** — ถ้าต้องการ re-render ดึงจากที่นั่น.

### Diagram 1 — Library Framework Anatomy
แสดง **post หนึ่งชิ้นถูกประกอบยังไง**. Top tier (amber) = account-level constraints (Voice, Audience Persona, Niche Scope) → set context. Middle tier (teal) = post-level library 3 คอลัมน์ (Content × Theme × Media) → mix 1×1×1. Bottom (purple) = "one unique post" output tagged สำหรับ analytics (optional JTBD/Funnel).

### Diagram 2 — Multi-Account Sequential Expansion
Timeline โต 1 → 3 accounts. 3 คอลัมน์ (เดือน 1-3 / 4-6 / 7-12). Account 1 อยู่ทั้ง 3 คอลัมน์ (NEW → growing → established), Account 2 เริ่มคอลัมน์ 2, Account 3 เริ่มคอลัมน์ 3. **ทุก account purple (ของ Sin เอง)**. Key insight: **อย่าเปิด 3 account วันแรก** — validate Account 1 (5K+ followers) ก่อน. ทุก account share **Data Fabric เดียวกัน**.

### Diagram 3 — Phase 1 Two-Service Architecture (Sin Solo)
2-service internal architecture สำหรับ creator business ของ Sin เอง. บนลงล่าง: **Data Service container (purple)** [Sources → Data Fabric → AI Agents] → arrow "combos + assets" → **Marketing Service container (purple)** [Content Production → Multi-account Post → Performance Track] → 3 accounts ของ Sin (purple) → Audience (gray) → Sin's revenue (purple: affiliate + own products). Performance loop กลับเข้า brain.

### Diagram 4 — Phase 2 Agency Model (CORRECTED — เดิมเป็น SaaS)
**สถาปัตยกรรมเดิม** แต่ output ขยายไปหลาย brand. **Agency stack (purple)** [Data Service + Marketing Service, collapsed, internal only] → arrow "agency operates for" → 3 branches: Sin's own accounts (purple → affiliate revenue) + Client brand A (coral → agency fee) + Client brand B (coral → agency fee) → converge → Sin's combined revenue (purple). **Legend: purple = ของ Sin, coral = client brands.**

**Diagram 3 vs 4:**
- D3: architecture เดียว serve **1 brand** (ของ Sin)
- D4: architecture **เดียวกัน** serve **N brands** (Sin + clients)
- **ไม่มี SaaS, ไม่มี customer API** — Sin keeps **100% backend control**, รันทุกอย่าง internal. ลูกค้าจ่ายเพื่อ **service ไม่ใช่ access**.

---

## Agency-specific warnings

### 1. Time-bound — Sin's time = bottleneck
Agency scale **linear** → เวลา Sin คือเพดาน. ถึง 3-5 clients แล้วชนเพดานเร็ว. **วางแผน team ตั้งแต่เนิ่นๆ** ก่อนจะ overload — อย่ารอจน 10 clients แล้วค่อยคิดเรื่อง hire. ถ้าไม่ plan team = ติดกับดัก "ทำงานหนักกว่าเดิม" (ตรงข้ามกับเป้า "หนีงาน").

### 2. Client contract clarity
ก่อนรับลูกค้า เคลียร์ให้ชัดเป็นลายลักษณ์อักษร:
- **IP ownership** — content/asset ที่สร้างให้ลูกค้า เป็นของใคร? (ลูกค้า? Sin? license?)
- **Deliverable scope** — กี่ post/เดือน, รวมอะไรบ้าง, แก้กี่รอบ — กันงานบาน (scope creep)
- **Kill switch** — เงื่อนไขเลิกสัญญา, notice period, ส่งมอบ asset ตอนจบยังไง

> **Backend tool ห้ามเขียนใน contract ว่าลูกค้ามีสิทธิ์เข้าถึง** — moat อยู่ตรงนี้. ขายผลลัพธ์ ไม่ใช่ access.

### 3. Don't over-promise
Predict performance ได้ ≠ **garantee** performance. อย่าสัญญาตัวเลข (followers/sales) ที่ขึ้นกับ platform algorithm + ปัจจัยนอกการควบคุม. ขาย **process + consistency + expertise**, ไม่ใช่ผลลัพธ์ตายตัว — ไม่งั้นเสีย reputation + ติดข้อพิพาทกับลูกค้า.

### 4. Retention > acquisition
รายได้ผูกกับ retention (ดู constraints). ลูกค้า 1 รายหาย = รายได้หายเป็นก้อนใหญ่ทันที (ต่างจาก SaaS). ลงทุนกับ **ความสัมพันธ์ + ผลลัพธ์สม่ำเสมอ** มากกว่าวิ่งหาลูกค้าใหม่ตลอด.

---

## Phase 3 — B2P Platform Intelligence Service (commerce pillar, far-future)

> **Phase 3 = far-future vision (Year 3+)** — เริ่มได้เมื่อ Phase 1+2 มี proof + track record แล้ว. ห้ามกระโดดข้าม. ยังคงหลัก **never SaaS**: นี่คือ **Sin-operated B2P service**, ไม่ใช่ self-serve tool.

### "Service to Platform" คืออะไร

จาก Phase 1 (B2C affiliate) → Phase 2 (B2B agency ให้ brand) → Phase 3 **ขยับขึ้นไป serve ตัว e-commerce platform เอง** (B2P).

**Customer = TikTok Shop / Shopee / Lazada / Bukalapak / etc.** Edge ของ Sin = มี **real audience data จาก O&O channels** (ไม่ใช่ scraped public data) + multi-catalog scope + AI-automated execution.

### 6 service types (brief)

| # | Service | Pricing |
|---|---|---|
| 1 | **Creator/Product Discovery** — "จาก data ของ O&O channels นี่คือ 50 creators/products ที่ platform ควร promote" | Retainer 100-300K THB/mo หรือ per-discovery |
| 2 | **Trend Intelligence** — quarterly "Thai consumer trends ข้าม catalog" จาก real behavior | $5-20K/report หรือ subscription |
| 3 | **Campaign Management for Platform** — รัน platform-level campaign (9.9, 11.11) ให้ | Commission on incremental GMV |
| 4 | **Audience Insights / Data Product** — เช่น "Thai GenZ ใน catalog X" + multi-catalog profiles | Annual data sub ฿500K-2M |
| 5 | **Content Library Licensing** — premium content จาก channels license ให้ platform feature | Per-piece หรือ revenue share |
| 6 | **MCN Partnership Program** — O&O channels ดัน platform campaign (TikTok Shop Prime Partner-style) | Commission on creator-driven GMV |

> Default monetization = **commission-on-GMV** (services 1/3/6); retainer/subscription/licensing เป็น mix ตาม service.

### Prerequisites (ต้องครบก่อนเริ่ม Phase 3)

```
✓ own channels ที่ 50K+ followers ต่อ channel
✓ Phase 2 agency รัน 6+ เดือน + มี measurable client outcomes
✓ brand authority ใน 2+ catalog verticals
✓ relationships กับ platform-side decision makers
✓ documented case studies (3+ wins)
✓ tech infra พิสูจน์ at scale + legal/contract framework สำหรับ B2P deals
```

> **ห้าม:** pitch platform ก่อนมี Phase 1+2 proof. Cultural moat compounds ตามเวลา → Phase 3 ค่อย unlock เป็น natural evolution. เริ่มจาก 1 service (น่าจะ Service 6 — MCN partnership) แล้วค่อยขยาย.
