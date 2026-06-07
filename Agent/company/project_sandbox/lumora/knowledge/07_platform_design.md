# 07 — Platform Design (synthesized)

> Design สังเคราะห์จาก 7 specialists (solution-arch, ai-arch, ai-engineer, software-eng, system-analyst, platform-arch, devops). นี่คือ **authoritative technical design** ของระบบ — 04 (stack/data model) + 06 (business/agency) ยังถูกต้อง, ไฟล์นี้คือ "จะ build ยังไง".
>
> 🟢 **STATUS: design agreed + 5 decisions resolved (2026-06-03)** (ดู §9). Design พร้อมใช้เริ่ม build. (Project = **LUMORA**, multi-catalog — §0.5 แกน B; design นี้ catalog-agnostic อยู่แล้ว.)
>
> 📚 **ถ้าไม่คุ้น AI agent / ML / platform — อ่าน §1 (อธิบายภาษาคน) ก่อน** แล้วค่อยอ่านที่เหลือ.

---

## 0. TL;DR (ตัดสินใจอะไรไปบ้าง)

1. **Build เป็น "app ที่มี seam ระดับ platform"** — ไม่ใช่ platform เต็ม, ไม่ใช่ one-off app. (modular monolith: 1 app + 1 API + 1 orchestrator)
2. **Orchestrator-first, LLM-surgical** — งานกลไก 95% ใช้ระบบ deterministic (ฟรี), เรียก AI (LLM) เฉพาะตอนต้อง "เขียน/ตัดสินใจแบบคน" → ประหยัด token ~100 เท่า
3. **ทำ 3 seam ให้แข็งตั้งแต่แรก**: `brand_id`+RLS · Source adapter · Generator adapter. ที่เหลือ defer
4. **Phase 1 = cloud อยู่แล้ว** (serverless, idle ≈ $0) — local แค่ตอน dev
5. **Cost ~$90-135/mo** — ตัวหลักคือ AI generate รูป/วิดีโอ

---

## 0.5 สามแกน (business / catalog / tech) + tech ต้อง extensible ตั้งแต่ Phase 1

> เวลาพูดคำว่า "phase" มันมี **3 แกนที่ขนานกัน** — อย่าปนกัน

| แกน | phase 1 | phase 1.n | phase 2 | phase 3 |
|---|---|---|---|---|
| **A. Business model** | own creator | — | **B2B** (รับ brand) | **B2P** (serve e-commerce platform) + scale service ecosystem |
| **B. Catalog** (subset ของ business) | สายมู | + catalog เพิ่ม (อาหาร/สุขภาพ/...) | + client catalogs | scaled |
| **C. Tech platform** | **extensible ตั้งแต่แรก** → รองรับ plug micro-service / push-to-platform / dealer service | (เพิ่ม feature แบบ plug-in) | | |

### 🔑 Key requirement: tech ต้องพร้อม Phase 1 แม้ business ยังไม่ถึง
**Business ไป B2P ตอน Phase 3** ก็จริง — **แต่ tech ต้อง architect ให้พร้อม plug "serve-platform / dealer / micro-service" ได้ตั้งแต่ Phase 1** ไม่ใช่ไปรื้อทีหลัง. นี่คือเหตุผลที่เลือก **"app ที่มี platform seam"** (§0 ข้อ 1):
- **push content → social platform** = เพิ่ม **Publisher adapter** 1 ตัว
- **serve e-commerce platform / dealer service (Phase 3)** = เพิ่ม service เข้า core เดิม (Data+Marketing service + adapter registry) — ไม่รื้อ
- **micro-services ต่างๆ** = adapter/registry pattern + `brand_id` ที่วางไว้ = extensible by design

→ เราแค่ build **core ให้ดี** + ขีด 3 seam (§4) ให้ถูก แล้ว feature/service เสียบเพิ่มเรื่อยๆ โดยไม่รื้อ. metrics ingestion (§9 ข้อ 1) ก็ทำเป็น service/API ด้วยเหตุผลนี้ — reuse ให้ dealer service อื่นได้.

---

## 1. 📚 อธิบาย concept แบบภาษาคน (เทียบกับที่ DE คุ้น)

> ส่วนนี้สำหรับคนที่ไม่คุ้น AI agent / ML / platform — เทียบกับ Airflow, SQL, interface ที่คุณรู้อยู่แล้ว

### "AI agent" คืออะไร vs "orchestrator"
- **Orchestrator** = เหมือน **Airflow DAG**. คุณเขียนไว้ชัดว่า step ไหนทำอะไร ลำดับไหน. มัน deterministic (รันกี่ครั้งก็ได้ผลเดิม), debug ได้, **ฟรี** (ไม่มีค่า token). เราใช้ **Inngest** เป็น orchestrator (= Airflow แบบ serverless สำหรับ event/cron).
- **AI agent** = ให้ **LLM (เช่น Claude) เป็นคนตัดสินใจเองว่าจะทำ step ไหนต่อ**. ยืดหยุ่นเหมือนคน แต่ (1) จ่ายเงินต่อทุกคำที่อ่าน+เขียน (2) ตอบไม่เหมือนเดิมทุกครั้ง (3) ช้า.
- **หลักของเรา:** ใช้ orchestrator (Airflow-style) ทำ 95% ของงาน — เรียก LLM **เฉพาะจุดที่ต้องใช้วิจารณญาณ/ความครีเอทีฟจริงๆ** (เขียน caption, คิด combo แปลกใหม่). นี่คือที่มาของ "orchestrator-first, LLM-surgical".

### ทำไม LLM ถึงแพง / deterministic ถึงฟรี
- **Deterministic** = SQL query / สูตรคณิต. รัน 1 ล้านครั้งก็ไม่มีค่าใช้จ่ายต่อครั้ง (แค่ CPU). ได้คำตอบเดิมเสมอ.
- **LLM** = จ่ายต่อ "token" (คร่าวๆ = คำ) ทั้งที่ส่งเข้าและที่มันเขียนออก. ถ้าให้ LLM ตัดสินใจ 200 combo/วัน = อ่าน context ยาวๆ 200 รอบ = เงินบานปลาย.
- → เราเลย **คิดคะแนน combo ด้วย SQL/สูตร (ฟรี)** แล้วค่อยให้ LLM แค่ "เขียนสรุปเหตุผล 1 ประโยค" กับ "เขียน caption" เท่านั้น.

### "Embedding / vector" คืออะไร (ทำไมมี pgvector)
- **Embedding** = แปลงข้อความเป็น **list ของตัวเลข** (เช่น 1024 ตัว) ที่ "ความหมายใกล้กัน = ตัวเลขใกล้กัน".
- ประโยชน์: หา "สินค้าที่เข้ากับ vibe ของ account นี้" ได้ด้วย **คณิตศาสตร์** (วัดระยะ cosine) แทนที่จะให้ LLM อ่านทีละอัน.
- **pgvector** = extension ของ Postgres ที่เก็บ vector พวกนี้ + ค้นแบบ "ใกล้สุด" ได้. → คุณเก็บใน **Supabase (Postgres)** ที่เดียว ไม่ต้องมี vector DB แยก. (คุณคุ้น Postgres อยู่แล้ว = ง่าย)

### "Scorer / recommender" — ไม่ใช่เวทมนตร์ ML
- มันคือ **สูตรถ่วงน้ำหนัก** เหมือน SQL `ORDER BY`:
  `score = 0.30·trend + 0.25·fit + 0.20·lift + 0.10·recency + 0.10·season − fatigue`
- ทุกตัวแปร normalize เป็น 0..1 แล้วบวกกัน → จัดอันดับ combo. **ไม่ต้องเทรนโมเดล** จนกว่าจะมีข้อมูลเยอะมาก (Phase 2+). เริ่มจากสูตรก่อน = debug ง่าย, อธิบายได้, ฟรี.

### "Adapter / plugin seam" — คือ interface ที่คุณรู้จัก
- เหมือน **abstract class / interface**: กำหนดว่า "Source ทุกตัวต้องมี method `scrape()`" แล้ว TikTok/Shopee/Lazada ต่างคน implement.
- เพิ่ม Instagram = **เขียน class ใหม่ 1 ไฟล์** แล้ว register — ไม่ต้องแก้ core. นี่คือ "seam" ที่ทำให้ feature โตแบบ "บวกเพิ่ม" ไม่ใช่ "รื้อ".

### "RLS (Row-Level Security)" — กันข้อมูลลูกค้าปนกัน
- feature ของ Postgres: **กรอง row อัตโนมัติตามกฎ** (เช่น `brand_id = ของ user คนนี้`).
- ผล: ตอน Phase 2 มีหลาย client brand ในตารางเดียวกัน — client A **มองไม่เห็น** row ของ client B เด็ดขาด แม้โค้ดเผลอ query ผิด. เปิดไว้ตั้งแต่ Phase 1 (มี brand เดียว) = ฟรี, กันพลาดตอน Phase 2.

### "Serverless / always-on" — ทำไม Phase 1 ก็ต้องมี cloud
- **Serverless** = โค้ดรันตอนมี request เท่านั้น, ไม่ต้องดูแล server, จ่ายตามใช้, ว่าง = เกือบ $0 (เช่น Cloudflare Workers, Modal).
- **Always-on** = บางอย่างต้อง "เปิดตลอด 24 ชม." เช่น cron (scrape ทุกเช้า) + webhook (รอ Replicate ยิงกลับมาว่า gen เสร็จ). ของพวกนี้รันบน laptop ไม่ได้ (ปิดเครื่อง = ตาย) → **ต้องอยู่ cloud**. แต่เป็น cloud ถูกๆ ไม่ใช่ server ใหญ่.

### "Modular monolith / platform" — ตรงกลางระหว่าง 2 ขั้ว
- **Monolith** = code base เดียว (ไม่แตกเป็น microservices หลายตัว — overkill สำหรับคนเดียว).
- **Modular** = ข้างในมี "เส้นแบ่งสะอาด" ตรงจุดที่จะโต (3 seam ข้างบน).
- **Platform-ness** = มี "core ที่ใช้ซ้ำ" + "feature ที่เสียบเพิ่มได้". เราทำ platform-ness **ภายใน** (เพื่อตัวเอง+ทีม) แต่ไม่เปิดให้ลูกค้าใช้เอง (นั่นคือ SaaS ที่เราไม่เอา).

---

## 2. สถาปัตยกรรมรวม (orchestrator-first)

```
   UI (Next.js บน CF Pages) ── 2 โหมด: Data dashboard · Marketing studio
        │ อ่าน sync / สั่งงาน (enqueue)        ▲ Sin approve (2 จุด)
        ▼                                       │
   CF Workers + Hono  (edge บางๆ, scope ด้วย brand_id)
        │ ส่งงานเข้าคิว
        ▼
  ╔═══ INNGEST = orchestrator (⚙️ deterministic, $0 token) ═══╗
  ║  cron · queue · retry · step-functions · fan-out/brand    ║
  ╚══╤═════════╤═══════════╤════════════════╤═════════════════╝
     │         │           │ (in-step)      │ webhook กลับ
  ┌──▼───┐ ┌──▼────┐ ┌─────▼────────┐  ┌────▼─────────────────────┐
  │Modal │ │Modal  │ │DECISION       │  │ 🤖 Claude  🎨 Replicate   │
  │scrape│ │embed  │ │ENGINE ⚙️       │  │ /Kling   (เรียกเฉพาะจุด)  │
  └──┬───┘ └──┬────┘ │score สูตร      │  └──────────────────────────┘
     │        │      │+🤖 LLM บางๆ    │      │ asset เสร็จ
     ▼        ▼      └────────────────┘      ▼
  Supabase (Postgres + pgvector + auth + RLS)  ←─ system of record   →  CF R2 (assets)
     │
     └─ brand_id ทุก table → Phase1 (1 brand) → Phase2 (N brands) = INSERT ไม่ใช่ migrate
```

**อ่าน flow:** cron ปลุก → Modal scrape สินค้า → Modal embed → Decision Engine คิดคะแนน combo (สูตร) → เสนอ top-N เข้า **approval queue** + ปิง LINE → **Sin กด approve** → Inngest สั่ง generate (🎨 รูป + 🤖 caption) → เข้า studio ให้ Sin ดูอีกรอบ → schedule → publish → เก็บผล → ป้อนกลับ Decision Engine.

---

## 2.5 Marketing Service — Content Production pipeline (ขยาย ④)

> "Production" ในไดอะแกรมหลักคือกล่องเดียว — จริงๆ ข้างในเป็น **gen-pipeline หลายสเต็ป** ที่ **เรียก 🤖 LLM (script/scenario/prompt) + 🎨 gen-API (รูป/วิดีโอ)**. แตกต่างตาม `media_format`.

```
[approved combo: Content×Theme×Media + product + JTBD + account voice]
        │
   ④ CONTENT PRODUCTION (orchestrated recipe ต่อ media_format)
   ── เคส "วิดีโอ/reel" (M3, ซับซ้อนสุด): ──
   🤖 1 Script/Hook (LLM) ............. hook 1-2s + beats + CTA
   🤖 2 Storyboard (LLM) .............. แตกเป็น shot list (กล้อง/มู้ด/ความยาว)
        ├── ต่อ shot: 🤖 3 image prompt (LLM) → 🎨 4 image gen (FLUX)
        └── ต่อ shot: 🤖 5 motion prompt (LLM) → 🎨 6 video gen (Kling/Runway, image→vdo)
   🎵 7 (opt) voiceover TTS + music
   ⚙️ 8 Assemble (ffmpeg): ต่อคลิป + subtitle + audio → 9:16 mp4
   🤖 9 Caption/copy (LLM, cached brand voice) + hashtags
   ⚙️ 10 store asset (R2/fs) + tag metadata → posts
        │ asset_ready (Sin review/regenerate)
   ⑤ MULTI-ACCOUNT POST: ⚙️ calendar+schedule → PublisherAdapter (TikTok/IG/YT) + community
   ⚙️ ⑥ PERFORMANCE TRACK: engagement + affiliate conv/revenue → feedback กลับ scorer
```

### Recipe ต่อ media_format
| media | 🤖 LLM | 🎨 gen-API | ⚙️ deterministic |
|---|---|---|---|
| M1 single image | image prompt → caption | FLUX | store+tag |
| M2 carousel | prompt/copy ต่อสไลด์ + caption | FLUX ×N | assemble+tag |
| M3 video/reel | script→storyboard→img prompt→motion prompt→caption | FLUX ×shots + Kling/Runway ×shots (+TTS) | ffmpeg stitch+sub+encode |
| M5/M6 vlog/talking-head | script + b-roll prompts + caption | b-roll gen (+ Sin ถ่ายเอง) | edit/encode |
| M7 แต่งเรื่อง (fiction) | story + scene scripts + prompts | FLUX + video (heavy) | assemble |

### Sub-adapter decomposition (extensibility)
`GeneratorAdapter.generate()` (ตอนนี้ 1 step) → แตกเป็น **production pipeline** ที่ประกอบ sub-adapter ที่เสียบเปลี่ยนได้:
```
ScriptGen(LLM) · StoryboardGen(LLM) · ImageGen(FLUX|MJ|Ideogram) ·
VideoGen(Kling|Runway|Luma) · CaptionGen(LLM) · Assembler(ffmpeg)
   └── ProductionRecipe[media_format] = orchestrator เลือกว่า media นี้รัน sub-adapter ไหน
```
ยังอยู่ใน Generator seam เดิม — ข้างในเป็น recipe หลาย step. เพิ่ม model = swap sub-adapter.

### 💰 cost (ตัวขับหลัก = 🎨 gen)
image (FLUX) ~$0.025 · video (Kling) ~$0.07-0.4/clip · LLM script+prompts+caption ~$0.01-0.03 (cached) · ffmpeg $0. **reel 5 shots ≈ ~$0.5-2/ตัว** → gen เฉพาะที่ approve เท่านั้น.

---

## 3. ⚙️ deterministic vs 🤖 LLM (จุดที่ประหยัด token)

| งาน | ใช้ | ค่าใช้จ่าย |
|---|---|---|
| scrape · normalize · trend z-score · **combo scoring** · tagging · schedule · publish · track | ⚙️ rules/SQL/stats | **$0 token** |
| combo **rationale** (สรุปให้ Sin อ่าน 1 ประโยค) | 🤖 Claude Haiku | ~$0.005/batch |
| **caption/copy** (เสียงแบรนด์) | 🤖 Claude Sonnet (cache system prompt) | ~$0.0008/caption |
| **novel combo** (คิดนอกตำรา, นานๆครั้ง ~5%) | 🤖 Sonnet | bounded |
| **art / video** | 🎨 Replicate FLUX / Kling | $30-60/mo (ตัวหลัก) |

**ผล:** scorer ตัดสิน 200 combo/วัน = $0 · LLM ยิงจริง ~10-20 ครั้ง/วัน → ถูกกว่า "agent ทำทุกอย่าง" ~100 เท่า. **เคล็ดลับ caption:** เอา "เสียงแบรนด์ + กฎ guardrail" ใส่ system prompt แล้ว **cache** ไว้ (จ่ายเต็มครั้งแรก, ครั้งต่อไป ~10%) + ยิงทีละ batch หลาย caption.

---

## 4. 3 seam ที่ต้องทำตั้งแต่แรก (ที่เหลือ defer — กัน over-engineer)

| ทำเลย (มี implementation #2 จริงแล้ว = คุ้ม) | defer จนกว่ามีของจริง |
|---|---|
| ① **brand_id + Postgres RLS** ทุก table | Publisher registry (P1 มีแค่ TikTok+Reels) |
| ② **Source adapter** (TikTok/Shopee/Lazada = 3 ตัว) | Scorer plugin (z-score ตัวเดียวพอ) |
| ③ **Generator adapter** (image ตอนนี้ → video เร็วๆนี้) | client UI / reporting / RBAC (Phase 2) |
| + **state machine** กัน auto-publish (approve 2 จุด: combo → asset) | pillar/theme เป็น DB table (เริ่มเป็น config file) |

**ตัวอย่างผล:** เพิ่ม IG publish = เขียน adapter 1 ไฟล์ · เพิ่ม content pillar = **แก้ data ไม่ใช่ code** · เพิ่ม client brand = INSERT row + config (ไม่แตะ code).

> หลักกัน over-engineer: **ขีดเส้น (abstraction) เฉพาะตรงที่ "มี implementation ตัวที่ 2 อยู่แล้ว"** — ถ้ายังมีตัวเดียว เขียนตรงๆ ไปก่อน, abstract ตอนเจอตัวที่ 3.

---

## 5. ☁️ Local vs Cloud

- **ต้อง cloud ตั้งแต่ Phase 1.A** (always-on): Workers, Inngest cron, Supabase, R2, LINE/TG webhook
- **Local แค่ตอน dev**: ทุกตัวมี emulator (`wrangler dev`, `modal run`, Inngest dev server, Supabase branch)
- ไม่ใช่ "ทำ local ก่อนแล้วย้าย" — แต่ **deploy serverless cloud ตั้งแต่แรก** stack เดียวกันยาวถึง Phase 2 (ไม่ migrate)

| รัน | ที่ local (dev) | ที่ production |
|---|---|---|
| API/webhook | `wrangler dev` | **CF Workers** (edge) |
| cron/queue | Inngest dev | **Inngest** (managed) |
| scrape/embed | `modal run` | **Modal** (idle=$0) |
| DB+vector | Supabase branch | **Supabase** (managed) |
| assets | R2 dev bucket | **CF R2** |
| dashboard | `next dev` | **CF Pages** (free) |

---

## 6. 💰 Cost
**Phase 1 ~$90-135/mo** (งบ $200): ตัวหลัก = AI gen (Replicate $40-60 + video $20-40), Claude ~$15-25 (cache ช่วย), infra ที่เหลือ ~$20-50. **lever กันบานปลาย:** (1) cap รูป/วัน/brand (2) gen **เฉพาะ combo ที่ approve** (3) cache prompt (4) batch. **Phase 2:** retainer ลูกค้า 1 คน (30-100K฿) กลบ infra ลูกค้านั้น ~50-90 เท่า → กำไรตั้งแต่ลูกค้าคนแรก, คอขวด = เวลา Sin.

---

## 7. 🔨 Build path (Phase 1.A-1.D, ~12 สัปดาห์)
- **1.A** (wk1-2): core types + state machine + Supabase schema+RLS + Workers skeleton + 3 adapter interfaces
- **1.B** (wk3-4): TikTok scraper + cron + trend z-score + Data dashboard
- **1.C** (wk5-8): +Shopee/Lazada + entity resolution + embedding + Decision Engine
- **1.D** (wk9-12): FLUX art + caption + Studio UI + publish + LINE/TG bot

---

## 8. 7 facet (ใครออกแบบส่วนไหน — ref)
| Specialist | facet |
|---|---|
| solution-architect | system spine, integration, NFR, build-vs-buy, risk |
| ai-architect | orchestrator-vs-agent boundary, decision framework, eval/safety |
| ai-engineer | scorer สูตร, embedding, caption+caching, cost/op |
| software-engineer | app/repo structure, 3 adapter interfaces, state machine, RLS |
| system-analyst | workflows, user stories (MoSCoW), screens, edge cases |
| platform-architect | platform-vs-app, capability map, extensibility, multi-tenancy |
| devops-engineer | local↔cloud, IaC/CI-CD, FinOps, observability, scaling |

---

## 9. ✅ DECISIONS (resolved 2026-06-03)

> 5 ข้อที่เคยเปิดไว้ — Sin ตอบครบแล้ว. นี่คือ design decisions ที่ใช้ build ได้เลย.

1. **Metrics ingestion** → **ทำเป็น service + API** (ไม่ใช่ manual paste). ออกแบบให้ reuse ได้ → รองรับ dealer/platform service อื่นในอนาคต (ตรงกับ tech-extensibility, §0.5).
2. **Approval granularity** → เริ่ม **ทีละ combo** ก่อน → ค่อยเพิ่ม batch ทีหลัง. **ต้องมี feature "ปรับแก้/revise"** ในขั้น approve (เหมือน production + marketing-ads workflow: review → edit → approve). [state machine มี `revised` อยู่แล้ว]
3. **Vector dimension** → **1024** (bge-m3, ดีกับภาษาไทย). → schema เปลี่ยน `VECTOR(768)` เป็น `VECTOR(1024)`.
4. **Decision TTL** → **ไม่ลบ → archive**. combo ที่ไม่ approve/ตกเทรนด์ ย้ายเข้า archive, **review รายสัปดาห์**: อันดีเก็บเป็น **idea bank / context** ไว้ creative รอบหน้า, อันไร้ค่าค่อยลบ. (ไม่มี hard auto-expire; เพิ่ม `archived` status + idea-reuse)
5. **Reject reason** → **fixed tags** (ไม่ใช่ free-text) → scorer เรียนรู้เป็นระบบ.

---

## Cross-refs
- `04_tech_backend.md` — stack + SQL data model + phased build (รายละเอียด)
- `06_architecture_agency.md` — two-service + agency model + diagrams (business)
- `01_creative_library.md` — Content×Theme×Media framework ที่ generator/scorer ใช้
