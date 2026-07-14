# AIA Cost Dashboard — Compare Matrix (ทุก solution × ทุก requirement)

> **วันที่:** 2026-07-14 20:40 · **คู่กับ:** `solutions-catalog-20260714-2040.md` (design + architecture ของแต่ละ option)
> **Requirement:** `requirements-and-concerns-20260714.md` — R1-R10 / K1-K6 / S1-S7 / Q1-Q8
> **จุดประสงค์:** *validate & verify* — แสดงว่า **ทุก** option ถูกพิจารณาแล้ว และ **ตกเพราะข้อไหน** เพื่อให้ไม่มีใครถามซ้ำ (รวมทั้งตัวเราเองใน session หน้า)

---

## 0. ตัวย่อ

| | |
|---|---|
| ✅ | ผ่าน |
| ❌ | ตก — **ตัวเลขในวงเล็บคือข้อที่ฆ่ามัน** |
| ⚠️ | ผ่านแบบมีเงื่อนไข |
| — | ไม่เกี่ยว |
| 💰 | ใครจ่ายค่า compute |
| **Tier** | 0 = ไม่ต้องมี identity · 1 = account user · 2 = consumer access · 3 = workspace member |

### 🧨 ตัวฆ่า 3 ตัว (ทุก option ตายด้วย 1 ใน 3 นี้)
```
🔴 R5   PROD compute → DEV data ไม่ได้ (network) + ห้ามย้าย data ข้าม env
🔴 R5b  browser ของ client → DEV workspace URL ไม่ได้
🔴 R4   เรา deploy object ลง departmental workspace ไม่ได้
```

---
---

# 1. 📊 MASTER MATRIX — ทุก option × requirement หลัก

| # | Option | R1<br>table อยู่ DEV | R2<br>user จาก PROD | R3<br>ไม่เข้า coredata | R4<br>ไม่ deploy ลง PROD | **R5**<br>ไม่มี live path | **R5b**<br>browser เข้า DEV | R6<br>row-level | R7<br>chargeback | R8<br>monthly | R9<br>multi-team | R10<br>automated | 💰 | Tier | **ผล** |
|---|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|---|
| **A1** | Dashboard — share data perms | ✅ | ✅ | ✅ | ✅ | ✅ | **❌** | **❌ leak** | ✅ | ✅ | ✅ | ✅ | เรา | 1 | ☠️ **ตาย R5b + K1** |
| **A2** | Dashboard — individual data perms | ✅ | ✅ | ✅ | ✅ | ✅ | **❌** | ⚠️ Tier2 | ✅ | ✅ | ✅ | ✅ | เรา | 2 | ☠️ **ตาย R5b** |
| **A3** | Per-team dashboards (pre-filtered) | ✅ | ✅ | ✅ | ✅ | ✅ | **❌** | ✅ | ✅ | ✅ | ⚠️ ≤20 | ✅ | เรา | 1 | ⚠️ **ตัวมันเองตาย R5b — แต่เป็นรากฐานของ A5** ⭐ |
| **A4** | Export/import `.lvdash.json` *(= D+)* | ✅ | ✅ | ✅ | ⚠️ เขา import | **❌** | ✅ | ✅ | **✅ เขาจ่าย** | ✅ | ✅ | ✅ | **เขา** | 3 | ☠️ **ตาย R5** — "table not found" เสมอ |
| **A5** ⭐ | **Scheduled subscription (PDF + Excel)** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **✅ by construction** | ✅ | ✅ | ✅ | ✅ | เรา (~$5-20/ปี) | **0** | ✅✅ **ผ่าน — ชั้น 0** |
| **A6** | External embedding | ✅ | ✅ | ✅ | **❌** app server | ✅ | **❌** | ⚠️ เราเขียนเอง | ✅ | ✅ | ✅ | ✅ | เรา | **0** | ☠️ **ตาย R4 + R5b** |
| **A7** | Basic embedding (iframe) | ✅ | ✅ | ✅ | ✅ | ✅ | **❌** | = A1/A2 | ✅ | ✅ | ✅ | ✅ | เรา | 1 | ☠️ **ตาย R5b** |
| **B9** | Genie Agent → account users | ✅ | ✅ | ✅ | ✅ | ✅ | **❌** | ⚠️ Tier2 | ✅ | ⚠️ | ✅ | ⚠️ | เรา + LLM | 1/2 | ☠️ **ตาย R5b** |
| **B10** | Genie iframe embed | ✅ | ✅ | ✅ | ✅ | ✅ | **❌** | = B9 | ✅ | — | ✅ | — | เรา | 1/2 | ☠️ **ตาย R5b** |
| **B11** | Genie Conversation API | ✅ | ✅ | **❌** token ใน DEV | ✅ | **❌** | ✅ | ⚠️ | ✅ | — | ✅ | ✅ | เรา | token | ☠️ **ตาย R3 + R5** |
| **B12** | Genie One (account-level) | ✅ | ✅ | ✅ | ✅ | ✅ | **❌** | ⚠️ Tier2 | ✅ | ✅ | ✅ | ✅ | เรา | 1/2 | ☠️ **ตาย R5b** |
| **B13d** | Genie Agent ผ่าน OpenSharing (Beta) | ✅ | ✅ | ✅ | ⚠️ เขา mount | **❌** | ✅ | ⚠️ share-level | **✅ เขาจ่าย** | ⚠️ snapshot | ✅ | ⚠️ | **เขา** | 3 | ☠️ **ตาย R5** + Beta |
| **C14** | Databricks App — system auth (SP) | ✅ | ✅ | ✅ | **❌** | ✅ | **❌** | **❌ ทุกคนเห็นเท่ากัน** | ✅ | ⚠️ | ✅ | ⚠️ | เรา ×2 | 2/3 | ☠️ **ตาย R4 + R5b + R6** |
| **C15** | Databricks App — user auth | ✅ | ✅ | ✅ | **❌** | ✅ | **❌** | ⚠️ ถ้าไม่ลืม forward | ✅ | ⚠️ | ✅ | ⚠️ | เรา ×2 | 2/3 | ☠️ **ตาย R4 + R5b** + 🟡 Preview |
| **C16** | App เป็น static host | ✅ | ✅ | ✅ | **❌** | ✅ | **❌** | ✅ | ✅ | ✅ | ✅ | ✅ | เรา 24/7 | 2/3 | ☠️ **ตาย R4 + R5b** + dominated by G29 |
| **D17** ⭐💔 | **UC cross-workspace GRANT** | ✅ | ✅ | ✅ | ✅ | **❌** | ✅ | **✅ native** | **✅✅ เขาจ่าย** | ✅ | ✅ | ✅ | **เขา** | 3 | ☠️ **ตาย R5 — อันที่เจ็บที่สุด** |
| **D19** | OpenSharing D2D | ✅ | ✅ | ✅ | ⚠️ เขา mount | **❌** | ✅ | **❌ share-level** | **✅ เขาจ่าย** | ✅ | ⚠️ 1 share/ทีม | ✅ | **เขา** | 3 | ☠️ **ตาย R5** + metastore เดียวกัน ⇒ offer ไม่ได้ |
| **D20** | OpenSharing open protocol | ✅ | ✅ | ✅ | ✅ | **❌** | ✅ | ❌ | ✅ | ✅ | ⚠️ | ✅ | เขา | **0** | ☠️ **ตาย R5** + แจก bearer credential |
| **D21** | Clean Rooms | ✅ | ✅ | ✅ | ⚠️ | **❌** | ✅ | ⚠️ | — | ⚠️ | ⚠️ | ❌ approve ทีละ nb | ทั้งคู่ | — | ☠️ **ตาย R5 + $7,500/เดือน + ให้ table ไม่ใช่ dashboard** |
| **F23** | Table copy / CTAS → catalog เขา | ✅ | ✅ | ✅ | ⚠️ | **❌** | ✅ | ✅ filter ตอน write | **✅ เขาจ่าย** | ✅ | ✅ | ✅ | **เขา** | 3 | ☠️ **ตาย R5** *(ปลดล็อกได้ถ้า Q1/Q2=YES)* |
| **F24** | ADLS write + external table | ✅ | ✅ | ✅ | ⚠️ | **❌** | ✅ | ✅ | **✅** | ✅ | ✅ | ✅ | **เขา** | 3 | ☠️ **ตาย R5** + governance 2 ระบบ |
| **F25** | Delta clone (deep/shallow) | ✅ | ✅ | ✅ | ⚠️ | **❌** | ✅ | ⚠️ | ✅ | ✅ | ✅ | ✅ | เขา | 3 | ☠️ **ตาย R5** + shallow พังเมื่อ VACUUM |
| **F26** | Promote pipeline ไป workspace B | **❌ R1** | ✅ | ✅ | **❌** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | เขา | 3 | ☠️ **ตาย R1 + R4** |
| **G27** | Notebook → HTML export | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ per-team | ✅ | ✅ | ✅ | ✅ | เรา | **0** | ✅ **ผ่าน — แต่ G29 ดีกว่าทุกทาง** |
| **G28** | UC Volume file drop | ✅ | ✅ | ✅ | ✅ | **❌** | ✅ | ⚠️ volume-level | ✅ | ✅ | ⚠️ 1 vol/ทีม | ✅ | ~0 | 2 | ☠️ **ตาย R5** — Volume อยู่ใน UC ของ DEV |
| **G29** ⭐⭐ | **Custom self-contained HTML / Excel** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **✅ by construction** | ✅ | ✅ | ✅ | ✅ | เรา (~$15/เดือน) | **0** | ✅✅✅ **ผ่าน — ชั้น 1 · ตอบ S4 ตรงๆ** |
| **G30** | SQL Statement Exec API / download | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | เรา | 0 | ⚠️ **ใช้เป็นชิ้นส่วนได้** (admin ปิดได้ทั้ง ws) |
| **G31** ⭐ | **Webhook notification destination** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | ✅ | ✅ | ✅ | เรา | 0 | ✅ **ผ่าน — นี่คือกลไกส่งของ G29** |
| **G32** | SQL Alert | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ | ✅ | เรา | **0** | ✅ **ผ่าน — ใช้เสริม (tripwire)** |
| ~~H33~~ | ~~Power BI บน warehouse เขา~~ | ✅ | ✅ | ✅ | ✅ | **❌** | ✅ | **✅ native** | **✅✅** | ✅ | ✅ | ✅ | **เขา** | 2/3 | ☠️ **ตาย R5 + นโยบายทีม (ไม่แตะ PBI)** |
| **H34** | Publish UC catalog → Fabric | ✅ | ✅ | ✅ | ✅ | **❌** | ✅ | ⚠️ verify | ✅ | ✅ | ✅ | ✅ | เขา | 0 | ☠️ **ตาย R5** + 🟡 Preview + PBI/Fabric out |
| **H36** | JDBC/ODBC จาก PROD → DEV warehouse | ✅ | ✅ | **❌** | ✅ | **❌** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | เรา | ต้องมีสิทธิ์ใน DEV | ☠️ **ตาย R3 + R5** — *"ให้สิทธิ์ coredata ทางประตูหลัง"* |
| **H37** | Databricks Connect / Statement API B→A | ✅ | ✅ | **❌** | ✅ | **❌** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | เรา | ต้องมีสิทธิ์ใน DEV | ☠️ **ตาย R3 + R5** (= H36) |
| **H38** | Partner Connect | — | — | — | — | — | — | — | — | — | — | — | — | — | ☠️ **ไม่ใช่กลไก share — เป็น onboarding wizard** |
| **H40** | Lakebase (managed Postgres) | ✅ | ✅ | ✅ | ✅ | **❌** | ✅ | ❌ ต้องทำใน PG | ✅ | ✅ | ✅ | ✅ | เรา (24/7) | **0** | ☠️ **ตาย R5** + DB ตัวที่สอง + UC RLS ไม่ตามไป |
| **H41** | Lakehouse//RT | — | — | — | — | — | — | — | — | — | — | — | — | — | ☠️ **ไม่ใช่กลไก share** — เป็น compute shape (🔴 Beta) |
| **H42** ⭐💔 | **Private Marketplace listing** | ✅ | ✅ | ✅ | **✅✅ เขา install!** | **❌** | ✅ | ⚠️ share-level | **✅ เขาจ่าย** | ✅ | ✅ | ✅ | **เขา** | 3 | ☠️ **ตาย R5** — **แต่แก้ R4 ได้สง่างามที่สุด** *(ปลดล็อกถ้า Q1/Q2=YES)* |
| **I-j** ⭐💔 | เขา grant **Consumer access** เอง → เปิด dashboard เรา | ✅ | ✅ | ✅ | **✅✅ ไม่ deploy อะไรเลย** | ✅ | **❌** | ✅ | ✅ | ✅ | ✅ | ✅ | เรา | 2 | ☠️ **ตาย R5b** — ต่อให้เขาติ๊กช่อง browser ก็ยังเข้า DEV ไม่ได้ |

---
---

# 2. 🔬 ทำไมถึงตก — ทีละ option (สำหรับ verify)

## 2.1 กลุ่มที่ตาย **R5b** — *browser เข้า DEV workspace URL ไม่ได้*
> **ทุกอันในกลุ่มนี้ "ทำงานได้จริง" ทางเทคนิค แค่ user เปิดหน้ามันไม่ได้**

| option | ตรรกะการตาย |
|---|---|
| **A1 / A2 / A3 / A7** | dashboard object อยู่ DEV → user ต้องเปิด `https://<DEV>.azuredatabricks.net/...` → **network จาก PROD-side บล็อก** → ไม่มีทางเห็น |
| **A6** External embedding | ต่อให้ห่อด้วย app ของเรา JS client ก็ยัง**ต้องคุยกับ DEV workspace โดยตรง** → บล็อกเหมือนกัน **+ ยังต้องมี app server ที่เรา host (❌R4)** |
| **B9 / B10 / B12** Genie | เหมือนกันเป๊ะ — Genie object อยู่ DEV |
| **C14 / C15 / C16** Apps | เหมือนกัน **+ ❌R4** (ต้อง deploy) |
| **I-j** | ต่อให้ admin เขา grant Consumer access ครบ → **ก็ยังเปิด URL ไม่ได้** ⇒ entitlement ไม่ใช่ปัญหา *network ต่างหาก* |

**✅ ข้อสรุปที่ต้อง verify กับ Sarunya:** *ทุก option ที่ผู้ใช้ต้อง "เปิด link/หน้าเว็บของ DEV" ตายหมด ไม่มีข้อยกเว้น*

---

## 2.2 กลุ่มที่ตาย **R5** — *ไม่มี live path จาก PROD compute → DEV data + ห้ามย้าย data ข้าม env*

| option | ตรรกะการตาย |
|---|---|
| **A4** `.lvdash.json` (= Option D+) | ไฟล์นี้มี **query text + widget config เท่านั้น — ไม่มี data** → import ไปฝั่งเขาแล้ว dashboard จะยิง **live query กลับมาที่ `catalog.gold.cost_wide` ใน DEV** → **"table not found" เสมอ** ไม่ว่าจะ grant/bind ยังไง ⇒ **นี่คือสาเหตุที่ D+ ตาย** |
| **D17** UC GRANT | 💔 **เจ็บที่สุด** — ในทางเทคนิคคือ option ที่ดีที่สุดในทั้ง catalogue (RLS native · เขาจ่าย · ไม่ต้อง deploy · $0 กับเรา) แต่มันคือ **PROD compute อ่าน DEV data** = สิ่งที่ R5 ห้ามตรงๆ **และจะไม่เปิด shared แม้อยู่ใน UC metastore เดียวกัน** |
| **D19 / D20** OpenSharing | (1) metastore เดียวกัน ⇒ offer share ไม่ได้ (2) ถ้าคนละ metastore ก็ยังคือ **การย้าย data ข้าม env** (3) 🚨 **row filter/column mask ไม่เดินทางผ่าน share** → ต้อง materialize table แยกต่อทีม |
| **D21** Clean Rooms | ตาย R5 + **$7,500/เดือน** + ให้ **table ไม่ใช่ dashboard** + approve ทีละ notebook ⇒ *"เอาตู้เซฟธนาคารมาเก็บ Post-it"* |
| **F23/F24/F25** data movement | นิยามของมันคือการย้าย data → **R5 ห้ามตรงตัว** |
| **G28** UC Volume | Volume อยู่ใน UC ของ **DEV** → PROD เข้าไม่ถึงเหมือน table |
| **H34** Fabric mirror · **H40** Lakebase | data ต้องเดินทางออกจาก DEV → R5 |
| **H42** Marketplace | 💔 **แก้ R4 ได้สง่างามที่สุดใน catalogue** (pull model — *เขา* install เอง เราไม่ deploy อะไรเลย) **แต่เบื้องหลังคือ OpenSharing → ย้าย data → ตาย R5** |
| **B13d** Genie via OpenSharing | เหมือน D19 + ยัง Beta |

---

## 2.3 กลุ่มที่ตาย **R4** — *เรา deploy อะไรลง departmental workspace ไม่ได้*
| option | ตรรกะการตาย |
|---|---|
| **C14 / C15 / C16** Databricks Apps | App เป็น **workspace-scoped object** → ต้อง deploy · และถ้า deploy ใน DEV → ตาย R5b แทน ⇒ **ตายทั้งสองทาง** |
| **A6** External embedding | ต้องมี **application server ที่เรา host** ให้ user PROD เข้าถึงได้ |
| **F26** promote pipeline | ตาย R1 ด้วย (pipeline ห้ามออกจาก DEV) |

---

## 2.4 กลุ่มที่ตาย **R3** — *client ต้องไม่เป็นสมาชิก coredata*
| option | ตรรกะการตาย |
|---|---|
| **H36 / H37** JDBC / Databricks Connect / Statement API | ทางเทคนิค**ทำงานได้** — ไม่มีกำแพง network ระหว่าง workspace *ในกรณีทั่วไป* กำแพงคือ **การครอบครอง credential** → แต่ credential ที่ต้องใช้คือ **สิทธิ์ใน coredata** ⇒ **นี่คือ "ให้สิทธิ์ coredata ทางประตูหลัง" = ผิด R3** *(และในเคส AIA network ก็บล็อกจริงด้วย = R5)* |
| **B11** Genie Conversation API | เหมือนกัน — ต้องมี token ของ principal ใน DEV |

---

## 2.5 กลุ่มที่ตาย **R6** — *row-level isolation*
| option | ตรรกะการตาย |
|---|---|
| **A1** share data perms | 🚨 query ของทุกคนรันในนาม **publisher** → **row filter ประเมินในนามเรา → ทุกทีมเห็นทุกแถว เงียบๆ** — **และนี่คือ default** |
| **C14** App system auth | *"All users… share the same permissions defined for the service principal"* → **ทุก viewer เห็น data เหมือนกันเป๊ะ** |
| **D19/D20** OpenSharing | granularity = **share ไม่ใช่ row** |
| **A5** ถ้าใช้ผิด | 🚨 **snapshot render ครั้งเดียว identity เดียว** → ส่ง PDF รวมทุกทีมให้ DL ผสม = **leak โดยโครงสร้าง** ⇒ **ต้องคู่กับ A3 (per-team dashboard) เสมอ** |

---
---

# 3. ⚖️ SOFT — เทียบกับ concerns ของ Sarunya (K) และ Sin (S)

| | **A5** subscription | **G29** interactive HTML | ~~A4/D+~~ | ~~D17~~ | ~~C15~~ App | ~~H42~~ Marketplace |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| **K1** "AI/BI ไม่ปลอดภัย" (กลัว link หลุด) | ✅ **ไม่มี link เลย** | ✅ **ไม่มี link เลย** | ⚠️ | ✅ | ❌ | ✅ |
| **K2** "self-contained ใน Databricks" | ⚠️ **ขึ้นกับการตีความ (Q5)** — ผลิตจาก Databricks 100% แต่ปลายทางเป็นอีเมล | ⚠️ เหมือนกัน | ✅ | ✅ | ✅ | ✅ |
| **K3** user เปิด workspace ตัวเองแล้วเห็น | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| **K4** monthly notification | ✅ **native scheduler** | ✅ Job cron | ✅ | ⚠️ | ⚠️ | ✅ |
| **K5** chargeback by tag | ✅ | ✅ **+ Excel ให้ Finance** | ✅ | ✅ | ✅ | ✅ |
| **K6** "client ควรจ่าย compute" | ❌ **เราจ่าย** (~$5-20/ปี) | ❌ เราจ่าย (~$15/เดือน) | **✅ เขาจ่าย** | **✅✅ เขาจ่าย** | ❌ เรา ×2 | **✅ เขาจ่าย** |
| **S1** ไม่ deploy ลง departmental | ✅ | ✅ | ⚠️ เขา import | ✅ | ❌ | **✅✅** |
| **S2** ไม่ promote ไป coredata PROD | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **S3** เลิก manual PDF | ✅ **automated** | ✅ automated | ✅ | ✅ | ✅ | ✅ |
| **S4** ⭐ **static dashboard file ที่ user import เอง** | ⚠️ ได้ Excel (pivot เองได้) | ✅✅ **ได้เต็ม — HTML interactive offline** | ❌ **`.lvdash.json` พก data ไม่ได้** | ❌ | ❌ | ❌ |
| **S5** tag ใน MAP → ต้อง project ขึ้น top-level col | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **S6** Zscaler บล็อก CLI | ⚠️ ตั้งใน UI ได้ | ⚠️ **ต้อง vendor chart lib ห้าม CDN** | ⚠️ | ⚠️ | ⚠️ | ⚠️ |
| **S7** บูม's pipeline opaque | — | — | — | — | — | — |
| | | | ☠️ R5 | ☠️ R5 | ☠️ R4+R5b | ☠️ R5 |

### 🔑 อ่านตารางนี้ยังไง
1. **K6 (client จ่าย compute) — เราแพ้ทุกทาง** ทุก option ที่รอด = **เราจ่าย** · ทุก option ที่ให้เขาจ่าย = **ตาย R5** ⇒ **ต้องบอก Sarunya ตรงๆ ว่าข้อนี้แลกไม่ได้** (แต่ ~$5-20/เดือน ไม่ใช่ประเด็นทางการเงิน)
2. **K3 (เห็นใน workspace ตัวเอง) — เราแพ้ทุกทาง** ⇒ **ต้องบอกตรงๆ ว่าเป็นไปไม่ได้ภายใต้ policy ปัจจุบัน**
3. **K2 คลุมเครือ → ต้องถาม (Q5)** — ถ้า "self-contained" = *"object ใน workspace เขา"* → ตายหมด · ถ้า = *"ไม่ต้องมี portal แยก"* → **A5/G29 ผ่านสบาย**
4. **S4 = จุดที่ G29 ชนะขาด** — คุณขอ *"static dashboard file ที่ user import เอง"* → **`.lvdash.json` ทำไม่ได้ (พก data ไม่ได้) แต่ HTML ทำได้**

---
---

# 4. 🎯 3 อันที่รอด — และทำไม

```
                     ┌── ต้องมี live path จาก PROD → DEV? ──┐
                     │                                      │
                   YES ☠️                                   NO
        (A1 A2 A3 A4 A6 A7 B9 B10 B11 B12                   │
         C14 C15 C16 D17 D19 D20 D21 F23-26                 │
         G28 H33 H34 H36 H37 H40 H42 I-j)                   │
                                                            ▼
                                          ┌── ต้อง deploy ลง departmental? ──┐
                                          │                                  │
                                        YES ☠️                              NO
                                     (A6 C14 C15 C16 F26)                    │
                                                                             ▼
                                                          ┌──────────────────────────────┐
                                                          │  ✅ A5  native subscription   │
                                                          │  ✅ G27 notebook HTML export  │
                                                          │  ✅ G29 custom HTML/Excel  ⭐  │
                                                          │  ✅ G31 webhook (delivery)    │
                                                          │  ✅ G32 SQL alert (tripwire)  │
                                                          └──────────────────────────────┘
```

| ชั้น | solution | requirement ที่ตอบ | จุดที่ยังขาด |
|---|---|---|---|
| **0** — ship สัปดาห์นี้ | **A3 + A5** — per-team dashboard + native subscription → email **PDF + Excel** · **0 บรรทัดโค้ด** | R1-R10 ✅ · K1 ✅ · K4 ✅ · K5 ✅ · S1-S3 ✅ | K3 ❌ · K6 ❌ · S4 ⚠️ (ได้แค่ Excel) |
| **1** — เดือนนี้ ⭐ | **G29 + G31** — Artifact Factory: for_each job → **interactive HTML offline** + Excel → webhook → Logic App → email | ทุกอย่างข้างบน **+ S4 ✅✅** + portable 100% | K3 ❌ · K6 ❌ |
| **เสริม** | **G32** — SQL Alert (cost ทีมไหนพุ่ง >3σ / recipient set เปลี่ยน) | ตรวจจับความผิดปกติโดยไม่ต้องมี identity ฝั่งรับ | — |

**ยังตอบไม่ได้ 2 ข้อ: K3 (dashboard ใน workspace เขา) และ K6 (เขาจ่าย compute)**
→ **ทั้งสองข้อกลับมาทันทีถ้า policy เปลี่ยน 1 ข้อ** (ดู §6)

---
---

# 5. 🔓 ถ้า Q1/Q2 ตอบว่า **YES** — ตารางเปลี่ยนทั้งหมด

> **Q1:** *มีที่เก็บ/ช่องทางไหนที่ DEV เขียนได้และ PROD อ่านได้มั้ย?*
> **Q2:** *R5 ห้าม "data export" ด้วย หรือห้ามแค่ "live connection"?*

**ถ้า YES → Shape 2 กลับมามีชีวิต** และ ranking เปลี่ยนเป็น:

| อันดับ | option | ทำไมชนะ |
|---|---|---|
| 🥇 | **H42 Private Marketplace listing** | **แก้ R4 ได้อย่างสง่างามที่สุด** — pull model: เรา publish, **เขา install เอง** ของไปโผล่ **ใน workspace เขา** (✅ K3!) **เขาจ่าย** (✅ K6!) เราไม่เคย deploy อะไรลง B เลย |
| 🥈 | **F23 table copy → catalog ที่เขาเป็นเจ้าของ** | ง่ายที่สุด น่าเบื่อที่สุด ใช้ได้แน่นอน · filter ต่อทีมตอน write → ไม่ต้องพึ่ง RLS เลย |
| 🥉 | **F24 ADLS + external table** | ถ้า Q1 = "มี ADLS container กลาง" — ⚠️ แต่ governance คร่อม 2 ระบบ |
| 4 | **D17 UC GRANT** | ดีที่สุดทางเทคนิค **แต่ต้องให้ PROD compute อ่าน DEV ได้** = ข้อขอที่หนักกว่า Q1/Q2 |

⇒ ✅ **K3 กลับมา** (dashboard ใน workspace เขา) · ✅ **K6 กลับมา** (เขาจ่าย) · ✅ **live + refreshable**

> ## 🔴 **⇒ Q1 + Q2 คือคำถามที่มีมูลค่าสูงสุดในโปรเจกต์นี้ ถามให้ได้คำตอบก่อนออกแบบอย่างอื่น**

---
---

# 6. 🔑 ข้อขอ policy — ข้อเดียว (ถ้าอยากได้ K3 คืน โดยไม่ย้าย data)

> **"ขอเปิดให้ browser ของ user (เฉพาะ Entra group `finops-cost-viewers`) เข้าถึง host ของ coredata DEV workspace — HTTPS 443, front-end, read-only"**

**นี่คือการปลด R5b ไม่ใช่ R5** — **ไม่มี data movement · ไม่มี copy · ไม่มี share · ไม่มี object ลง PROD · PROD compute ไม่แตะ DEV** มีแค่ **คนเปิดหน้าเว็บดู** แล้ว UC row filter คัดแถวให้

**ถ้าผ่าน → ปลดล็อกทันที:** A2 (individual data perms + RLS) · A3 · B9 (Genie) · B12 (Genie One) · **I-j**
**ยังต้องขอเพิ่ม:** admin ฝั่งเขา grant **Consumer access entitlement** (ไม่งั้น RLS ไม่บังคับใช้ — capability matrix ✗) — **แต่นั่นเป็นการติ๊กช่องใน workspace ของ*เขาเอง* ไม่ใช่การเข้ามาใน coredata (ไม่ผิด R3)**

| | วันนี้ (email artifact) | ถ้าอนุมัติ (link) |
|---|---|---|
| data ออกจาก DEV | **ใช่ — เป็นไฟล์ ถาวร** | **ไม่ — pixels เท่านั้น** |
| isolation บังคับด้วย | string ในช่อง To: | **UC row filter บน identity** |
| ถอนสิทธิ์ | **ไม่ได้** | ✅ ทันที |
| audit การอ่าน | **ไม่ได้** | ✅ ทุก query |
| forward ต่อ | ✅ (มองไม่เห็นด้วย) | ❌ link ไร้ประโยชน์ถ้าไม่มีสิทธิ์ |
| network exposure ใหม่ | ไม่มี | 1 host · 443 · 1 group · read-only |

> **policy ปัจจุบัน — เมื่อใช้กับ dataset ชุดนี้ — กำลังบังคับให้เราเลือกช่องทางที่ปลอดภัย *น้อยกว่า*** และ data ชุดนี้คือค่าใช้จ่าย Azure ราย resource **ไม่มี PII ไม่มี PHI ไม่มีข้อมูลผู้เอาประกัน**

---
---

# 7. ✅ Checklist สำหรับ verify กับทีม

| # | ข้อความที่ต้องให้ Sarunya/security ยืนยัน | ถ้าตอบต่างจากที่เราเข้าใจ → เกิดอะไร |
|---|---|---|
| 1 | *browser ของ client เปิด URL ของ coredata DEV **ไม่ได้*** | ถ้า **ได้** → **A2/A3/B9/B12/I-j ฟื้นทั้งหมด** → กลับไป Option D-family |
| 2 | *ห้าม data ลงระบบ PROD ทุกรูปแบบ (ADLS/table/catalog/share)* — **Q1/Q2** | ถ้า **ยกเว้นได้** → **H42 Marketplace / F23 / D17 ฟื้น** → ได้ K3 + K6 คืน |
| 3 | *เรา deploy อะไรลง departmental workspace ไม่ได้เลย* (R4) | ถ้า **ทำได้** → C15 App / F26 กลับมาพิจารณา |
| 4 | *email เป็นช่องทางที่ได้รับอนุญาต* (status quo = manual PDF) | ถ้า **ไม่ใช่** → **ไม่เหลือ solution ใดๆ เลย** ต้องแก้ policy สถานเดียว |
| 5 | **K2/K5** *"self-contained ใน Databricks" หมายถึงอะไรกันแน่* (Q5) | ถ้าแปลว่า *"object ใน workspace เขา"* → **ทุก option ตาย** ต้องขอ policy |
| 6 | *client team มี Consumer access entitlement ใน workspace ตัวเองมั้ย* | สำคัญเฉพาะเมื่อข้อ 1 ปลดล็อก |
| 7 | *DEV ยิง outbound ไป Logic App / Graph API / SMTP relay ได้มั้ย* | ถ้า **ไม่ได้** → **G29 ส่งของไม่ออก** → เหลือแค่ A5 (native subscription) |
| 8 | *tag `tag_team` ครอบคลุมกี่ %* | ถ้า <95% → ถัง "untagged" เป็นปัญหา chargeback ที่ใหญ่กว่าเรื่อง delivery |

---

# 8. 📌 3 ข้อที่ต้องแก้ในเอกสาร/skill เก่าของเรา

| # | เดิมเขียนว่า | ที่ถูกคือ | กระทบ |
|---|---|---|---|
| 1 | *"account user + UC row filter = ใช้ได้"* | 🚨 **Account user (Tier 1) ไม่ได้ RLS บังคับใช้** — capability matrix ✗ ชัดเจน ตัวปลดล็อกคือ **Consumer access entitlement** ซึ่ง **admin ฝั่งเขา grant เองได้** | `aia-cost-dashboard-solution-VERIFIED_20260713.md` §2 (ที่เขียนว่า "docs ขัดกัน ต้องเทส") — **docs ไม่ได้ขัดกัน matrix ชัดเจน** |
| 2 | *"Genie BLOCKED — ใช้กับ account user ไม่ได้ อย่าเสนอ"* | 🚨 **ผิดแล้ว** — *"including all account users"* มีใน doc ชัดเจน · capability matrix ให้ ✓ · Genie ใช้ **data credential ของ end user** ⚠️ แต่หน้า AI/BI admin ยังมีประโยคเก่าที่ขัดกัน (ทั้งสองหน้าอัปเดต 2026-07-08) → **เทสจริง อย่าเดา** | skill `databricks-uc-governance-sharing/SKILL.md` — **แถว "Genie BLOCKED" ต้องแก้** *(ไม่กระทบเคส AIA — Genie ตาย R5b อยู่ดี)* |
| 3 | *"ABAC GA 2025"* | **ABAC GA = 2026-04-28** และ **GA มี breaking change**: view/function เหนือ table ที่มี ABAC ประเมินในนาม **session user** ไม่ใช่ owner (grace 3 เดือน) | skill เดียวกัน |

---

# 9. 🗣️ ประโยคสรุปสำหรับห้องประชุม

> **"เราพิจารณา ~25 option ที่ Databricks มีจริงในปี 2026 ทั้ง GA และ Preview — dashboard ทุกโหมด, Genie ทุกแบบ, Apps ทั้ง 2 auth mode, Delta Sharing/OpenSharing, Clean Rooms, Marketplace, external embedding, Lakebase, Fabric mirroring**
> **~22 อันตายด้วยเหตุผลเดียวกันหมด: มันต้องการ *live path* จาก PROD ไป DEV — ไม่ว่าจะเป็น compute วิ่งไป query หรือ browser วิ่งไปเปิดหน้า**
> **เหลือ 3 อันที่รอด และทั้ง 3 อันคือเรื่องเดียวกัน: render ใน DEV แล้วส่งไฟล์ให้คน**
> **นี่ไม่ใช่ข้อจำกัดของ Databricks — Databricks มี feature พร้อมหมด **มันคือข้อจำกัดของ network policy** และไม่มี feature ใดของ vendor ไหนอ้อม network policy ได้"**
