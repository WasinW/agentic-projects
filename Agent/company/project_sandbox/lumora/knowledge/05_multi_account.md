# 05 — Multi-Account Strategy (When to Split, How to Split, In What Order)

> How **LUMORA** scales from **one account → a small portfolio** without burning Sin out.
> Catalog-agnostic — the split/sequencing logic applies to any catalog (สายมู, อาหาร/สุขภาพ, ท่องเที่ยว, gadget, art…); examples below use **catalog #1 = สายมู**.
> Source: `session_context_export_v4.md` §11 (Multi-Account Strategy) + §13 (backend implication) + §7 IG reference patterns (@hellopersonality, @abeastinside).
> Owner: Sin (part-time creator + full-time Senior DE). Constraint ที่กำหนดทุกอย่าง: **เวลาจำกัด → ขยายตามหลักฐาน ไม่ใช่ตามความอยาก.**
> Rule of thumb: **1 account validate ก่อน, ค่อยแตก. อย่าเปิด 3 account วันแรกเด็ดขาด.**
>
> **⚠️ Critical clarification (v4):**
> "Multi-account" ในเอกสารนี้ = **Sin's OWN accounts (1-3 ช่อง, content style ต่างกัน)** — ช่องที่ Sin โพสต์เองล้วน ๆ.
> **ไม่ใช่** external customers. **ไม่ใช่** SaaS ที่ลูกค้าเข้ามาใช้ platform เอง.
> การ "รับทำให้แบรนด์อื่น" (Sin operate ช่องให้คนอื่นเป็นบริการ) คือ **Phase 2 agency model** ซึ่งเป็นคนละเรื่อง — ดู `06_architecture_agency.md`. อย่าปน **Sin's multi-account (Phase 1)** กับ **agency clients (Phase 2)**.

---

## Why multi-account

หลาย account = หลาย positioning ที่ algo อ่านชัด. แต่ราคาคือ effort คูณ — ต้องชั่งให้ขาด.

### Pros

- **Algorithm favors clear positioning** — feed ที่ aesthetic/topic นิ่ง algo จัด audience ให้ถูกกว่า feed ที่ swing ไปมา.
- **Precise audience targeting** — แต่ละ account ดึง demographic ของตัวเอง (cyber crowd ≠ สายมูดั้งเดิม crowd).
- **Parallel testing** — ทดสอบ direction พร้อมกันได้ แทนที่จะเดาว่าอะไรเวิร์คในช่องเดียว.
- **Risk diversification** — account นึงโดน shadowban / algo เปลี่ยน ไม่ล้มทั้ง business.
- **Each account = different monetization angle** — cyber → art print/wallpaper margin สูง; traditional → affiliate เครื่องราง volume สูง; travel → hotel/package (ดู `03_monetization.md` cross-aesthetic upside).

### Cons

- **Effort ×N** — ทุก account ต้อง feed สม่ำเสมอ. 3 account = 3 calendar, 3 caption voice-check, 3 analytics loop.
- **Slower individual growth** — แบ่งเวลา/พลังงาน → แต่ละช่องโตช้ากว่าทุ่มช่องเดียว.
- **Cross-promote algo-unfriendly** — ดึง audience ข้ามช่องไม่ลื่นอย่างที่คิด; algo ไม่ค่อยให้รางวัล outbound shoutout. แต่ละ account ต้องพึ่ง organic ของตัวเองเป็นหลัก.

> **Net:** multi-account คือ **growth lever ตอน late-game**, ไม่ใช่ starting structure. เปิดเมื่อช่องแรกพิสูจน์ตัวแล้วเท่านั้น.

---

## Reference patterns

ทั้งสอง reference ที่ Sin calibrate มา (ดู `00_overview.md` aesthetic DNA) ใช้ multi-account แบบต่างกัน — สอง logic ที่ Sin เลือกได้:

| Main account | Secondary / side | Split logic | Takeaway สำหรับ Sin |
|---|---|---|---|
| **@hellopersonality** (2.5M) | **@hellothoughtpalace** | **Main vs secondary** — ช่องหลักดัน core format, ช่องรองเป็น overflow / experimental | เปิดช่องรองเพื่อ "ระบายของที่ไม่ fit ช่องหลัก" โดยไม่ทำลาย positioning ช่องหลัก |
| **@abeastinside** (110K) | **@ejay_portrait**, **@ejaytrip** | **Vertical split** — แตกตาม content vertical (portrait / travel) ออกจาก core | แตกตาม pillar/format ที่ชัด → แต่ละช่องมี audience + monetization ของตัวเอง |

**Pattern reading:** @hellopersonality = *hub + overflow* (1 หลัก 1 รอง). @abeastinside = *clean vertical split* (core + N verticals). Sin จะ map สองอันนี้เข้ากับ Option C vs sequential split ข้างล่าง.

---

## 4 strategy options

| Option | กลไก | Pros | Cons |
|---|---|---|---|
| **A — Single brand, multi-aesthetic mix** | ช่องเดียว ผสมทุก aesthetic (เหมือน `01_creative_library.md` divergent library ทำงานในช่องเดียว) | concentrated effort, voice เดียวชัด | algo signal ปน → audience targeting เบลอ, ceiling ต่ำกว่า |
| **B — Multi-account parallel (day 1)** | เปิด 2-3 ช่องพร้อมกันตั้งแต่แรก | positioning คมทุกช่อง | effort ×3 ตั้งแต่ยังไม่มี audience → **เผาเวลา part-time, ไม่แนะนำ** |
| **C — Hub + spoke** | ช่อง hub (brand+voice) + spoke ตาม vertical (เหมือน @abeastinside) | best of both worlds | ซับซ้อนสุด — เหมาะตอนมี team/automation พร้อม ไม่ใช่ตอนคนเดียว |
| **D — Sequential expansion** ⭐ | เริ่ม 1 ช่อง → validate → ถึง threshold → เปิดช่อง 2 → ทำซ้ำ | sustainable, เรียนรู้ต่อ stage, fit full-time job | growth ช้ากว่า B ในทางทฤษฎี (แต่ B โตไม่ได้จริงเพราะ effort ล้น) |

### Why D fits Sin (RECOMMENDED)

- **Part-time-safe** — เพิ่ม load ทีละช่อง, ไม่กระโดดเป็น 3× effort ตอนยังไม่มี traction.
- **Learning per stage** — ช่องแรกสอน Sin ว่า combo ไหนเวิร์ค, caption แบบไหน hook, affiliate angle ไหนแปลงเป็นยอด → เอา playbook นั้นเปิดช่อง 2 แบบ **ไม่เริ่มจากศูนย์**.
- **ตรงกับ progression "หนีงาน" 0→1 ก่อน 1→N** — ห้ามกระโดด stage (ดู `00_overview.md` / `04_tech_backend.md` anti-pattern).
- **Backend ได้ของจริงก่อน** — กว่าจะเปิดช่อง 2 prompt library + scheduler ผ่าน real load มาแล้ว → ช่อง 2 ขึ้นเร็วเพราะ infra พร้อม.

---

## 3 split patterns for Sin

ถ้า (และเมื่อ) แตกช่อง — แตกตามแกนไหน? สามทางที่ map กับ library axes ใน `01_creative_library.md` โดยตรง:

### Pattern 1 — By Aesthetic Family

| Account | Aesthetic family | Theme cluster |
|---|---|---|
| 1 | **Cyber-spiritual** (A2) | Future-tech / cyberpunk neon |
| 2 | **Traditional** (A1) | Historical / Contemporary สายมูดั้งเดิม |
| 3 | **Photography-travel** (M4/M5 real) | real footage + pilgrimage |

แตกตาม *look*. คมที่สุดสำหรับ algo, แต่บีบ creativity ต่อช่องมากสุด.

### Pattern 2 — By Content Pillar

| Account | Pillars | Monetization |
|---|---|---|
| 1 | **Deities** (C1 + C3 เทพ + ยันต์/คาถา) | เครื่องราง, จี้, ตะกรุด |
| 2 | **Oracle / daily reading** (C2) | oracle deck, course, subscription |
| 3 | **Temple-travel** (C4 ที่ไหว้เจ้า) | hotel, travel package |

แตกตาม *สิ่งที่ขาย* → monetization map ชัดที่สุด (align กับ `03_monetization.md`).

### Pattern 3 — By Media Format

| Account | Formats | Effort profile |
|---|---|---|
| 1 | **Art portfolio** (M1 single + M2 carousel) | low — generate-heavy |
| 2 | **Reels / animation** (M3 anim + M8 POV walk) | high — production-heavy |
| 3 | **Educational / face** (M5 vlog + M6 talking head) | high — on-camera |

แตกตาม *การผลิต*. ดีถ้า Sin อยากแยก "ช่อง batch ง่าย" จาก "ช่องที่ต้องโชว์หน้า" (ดู open question `00_overview.md` #5 show face?).

---

## Recommended path

```
Month 1-3   →  ONE account. Validate the library.
               หา combo (Aesthetic×Pillar×Format) ที่ resonate, lock voice,
               สะสม prompt library ที่ performance-tracked.

Month 4-6   →  ถ้าถึง ~3-5K followers + เห็น signal ชัดว่า audience แตกเป็น 2 กลุ่ม
               →  เปิด account 2 (เลือก split pattern จากข้างบน).
               ถ้ายังไม่ถึง → อยู่ช่องเดียวต่อ, ห้ามเปิดเพราะเบื่อ.

Month 7-12  →  Scale based on traction. ช่องไหนโต ทุ่มช่องนั้น.
               พิจารณา account 3 เฉพาะเมื่อ 2 ช่องแรกนิ่ง + backend automate caption/schedule แล้ว.
```

> **Threshold ไม่ใช่เวลา แต่เป็น signal.** 3-5K followers = proxy ว่า positioning เริ่มทำงาน. ถ้าเดือน 6 ยัง 800 followers → ปัญหาคือ content/positioning ช่องแรก, การเปิดช่อง 2 จะยิ่งซ้ำเติม.

---

## Backend implication

ตัดสินใจ "เปิดช่อง 2 ตอน Month 4-6" แต่ **build for multi-account ตั้งแต่ day 1** — เพราะ retrofit ทีหลังแพงกว่า. นี่คือ unfair advantage ของ Sin ในฐานะ DE (cross-ref `04_tech_backend.md`):

- **Shared prompt library** — prompt/combo เก็บ central, ไม่ผูกกับช่อง. ช่อง 2 reuse library ที่ผ่าน real performance มาแล้ว.
- **Per-account scheduling** — calendar/cadence แยกต่อ account แต่รัน engine เดียว (Notion + automation, ดู §Phase 1).
- **Asset router** — generate กลาง แล้ว route asset ไปช่องที่ถูก (= "multi-account router" ใน v3 §13 Phase 2). โครงนี้ต้องมี `account_id` ตั้งแต่ schema แรก.
- **Per-account analytics tags** — ทุก row metadata ใน BigQuery ต้องมี `account_id` + library tags (Content × Theme × Media). ทำให้ cohort analytics เทียบข้ามช่องได้ตั้งแต่ช่องที่สอง โผล่.

> **DE หลักการเดียว:** เพิ่ม `account_id` เป็น first-class column วันนี้ ราคาเกือบ 0. เพิ่มทีหลังตอนมี data 3 ช่องแล้ว = migration เจ็บ. Build the seam now, open the second account later.
>
> **⚠️ Phase 1 vs Phase 2 — อย่าปน scope ตรงนี้:** ทุกอย่างข้างบน (`account_id`, asset router, per-account scheduling) คือ backend สำหรับ **Sin's own accounts = Phase 1**. การเอา infra เดียวกันไป **serve แบรนด์อื่น** (Sin operate ช่องให้ลูกค้าเป็นบริการ) คือ **Phase 2 agency model** — multi-tenant, billing, client isolation เป็นโจทย์คนละชุด. ดู `06_architecture_agency.md`. เวลาออกแบบ schema/scale ตอนนี้ คิดแค่ Sin's 1-3 ช่องพอ; agency เป็น scaling problem ของอนาคต ไม่ใช่ requirement วันนี้.

---

## Decision — which split first

เมื่อถึงจุดเปิดช่อง 2 (หรือเลือก positioning ของช่อง **แรก** ให้คม) — ใช้ guide นี้:

1. **ยึด voice เป็นจุดร่วม ไม่ใช่ look.** ทุก account ต้อง feel like one creator เพราะ *perspective* เดียว (ดู `01_creative_library.md` §1 — identity = voice). อย่าให้ aesthetic split ทำลาย voice.
2. **เริ่มจาก archetype + persona ของ account แรกก่อน** (account-level tags, v3 §9). ตอบให้ได้ว่า "ช่องนี้พูดในนามใคร พูดกับใคร" *ก่อน* เลือก split axis. positioning ตามมาจากตรงนี้.
3. **เลือก split pattern ตามจุดแข็ง + monetization ที่ Sin อยากได้จริง:**
   - อยาก **art-led / portfolio + margin สูง** → Pattern 3 (M1+M2 art) หรือ Pattern 1 (cyber-spiritual). คม, batch ง่าย, fit เวลาน้อย.
   - อยาก **affiliate volume + audience สายมูดั้งเดิมกว้าง** → Pattern 2 (C1+C3 deities) หรือ Pattern 1 (traditional). audience ใหญ่ AOV ต่ำ.
   - ยังไม่ชัดว่าจะโชว์หน้าไหม → **เลี่ยง Pattern 3 account educational/face ก่อน**; เริ่มจาก generate-heavy account ที่ไม่ผูกหน้า Sin.
4. **Default แนะนำสำหรับช่องแรก:** **cyber-spiritual single account, art-led (Pattern 1 ผสม Pattern 3 ฝั่ง M1+M2)** — ตรง aesthetic DNA ที่ Sin ชอบสุด (`00_overview.md`), batch ได้ด้วย backend, margin print/wallpaper ดี, ไม่ต้องโชว์หน้า. พิสูจน์ library + voice ที่นี่ก่อน แล้วค่อยแตก traditional/travel เป็นช่อง 2 ตาม signal ที่ audience บอก.

> **อย่าเลือก split เพราะกลัวพลาด angle อื่น.** library ไม่หาย — มันรออยู่ที่ Pattern อื่นเมื่อถึงเวลา. ช่องแรกหน้าที่เดียว: **พิสูจน์ว่า Sin โพสต์สม่ำเสมอ + มีคนสน. ที่เหลือคือ scaling problem ของอนาคต.**
