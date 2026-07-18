# AIA Cost Dashboard — Context Export (VS Code session, 2026-07-15)

> **สำหรับ:** สิน — เอาไปอัปเดต web chat
> **หัวข้อหลักของ session นี้:** พี่ Sarunya ยอมให้ **share table ผ่าน UC ได้** → **D+ ฟื้นจากตาย (แบบมีเงื่อนไข)** + verify ว่า UC cross-workspace ติด network layer ไหนกันแน่
> **ไฟล์ที่เกี่ยวข้อง:** `solutions-catalog-20260714-2040.md` · `solutions-compare-matrix-20260714-2040.md` · `solution-artifact-factory-20260714-2040.md` · `requirements-and-concerns-20260714.md`

---

## 🔑 THE BIG PIVOT (สำคัญสุดของวันนี้)

**พี่ Sarunya update (2026-07-15):**
> **"เปิด shared table ผ่าน UC ได้ — แต่ห้ามเข้า workspace dev เรา"**

→ R5 เดิม (*"จะไม่เปิด shared แม้อยู่ใน UC เดียวกัน"*) **ถูกยกเลิก**
→ R5 ถูกผ่าครึ่ง:

| | เดิม (R5) | ใหม่ (2026-07-15) |
|---|---|---|
| share table ผ่าน UC | ❌ ห้าม | ✅ **ได้แล้ว** |
| เข้า workspace DEV | ❌ ห้าม | ✅ ยังห้าม (= R3 เดิม) |

**ข้อมูลเพิ่มจากสิน:**
- "share ผ่าน UC" = **UC GRANT (metastore เดียวกัน)** — คุ้นๆ ว่าอย่างนั้น *(แต่ยังไม่ทิ้ง Delta Sharing/OpenSharing — ขอ re-check)*
- metastore เดียวกันมั้ย = เหมือนข้อบน (ยังไม่ยืนยัน 100%)
- catalog OPEN/ISOLATED = **ไม่แน่ใจ ต้องดู**
- network path (PROD compute → DEV storage) เปิดมั้ย = **"ไม่น่าเปิด น่าจะแค่ชั้น governance"** ⭐

---

## 🧟 D+ / D17 ฟื้นจากตาย — และดีกว่า email artifact ทุกทาง

**architecture:**
```
coredata DEV                              departmental PROD
┌──────────────┐                      ┌────────────────────────┐
│ gold.cost_wide│◄──── shared via UC ──│ dashboard ของเขา        │
│ + ROW FILTER  │      (GRANT SELECT)  │   (import .lvdash.json)  │
│ 💾 data ที่ DEV │◄─ compute PROD อ่าน ─│ 💰 warehouse ของเขา      │
└──────────────┘                      │ 👤 เปิด workspace ตัวเอง  │
                                       │    — ไม่แตะ DEV เลย       │
                                       └────────────────────────┘
```

**"ห้ามเข้า DEV" ตอบโจทย์ด้วย UC GRANT พอดี:**
> **UC GRANT = สิทธิ์บน data ไม่ใช่ membership ของ workspace** — table โผล่ใน Catalog Explorer *ของเขา*, query ด้วย warehouse *ของเขา*, ไม่มีใครเข้า DEV

**สิ่งที่ได้กลับคืน:**
| | email artifact | **D+ (ฟื้น)** |
|---|---|---|
| K3 เห็นใน workspace ตัวเอง | ❌ | ✅ |
| K6 client จ่าย compute | ❌ เราจ่าย | ✅ เขาจ่าย |
| live / refreshable | ❌ static | ✅ live |
| interactive | ⚠️ Excel | ✅ dashboard เต็ม |
| R5b browser เข้า DEV | ติด | ✅ **ไม่ติดแล้ว** (เปิด workspace ตัวเอง) |

---

## ⚠️ VERIFY จาก Azure Databricks docs — UC cross-workspace ติด network ไหน

**คำถาม:** governance บอก "share ได้" แต่ตอน query จริง compute อ่าน storage ข้าม network ได้มั้ย?

### 🎯 VERDICT: **NO — UC GRANT (metastore เดียวกัน) ไม่พอ ถ้า network path ปิด**

> *"Cloud storage URLs must be accessible through firewall and network controls."*
> — [UC credential vending, Requirements](https://learn.microsoft.com/en-us/azure/databricks/external-access/credential-vending)

**กลไก (confirmed จาก docs):**
```
PROD warehouse รัน SELECT
   ↓ UC vend short-lived credential ให้ compute
   ↓ compute plane ของ PROD ── อ่านไฟล์ตรงๆ ──► ADLS storage ของ DEV
                                    ▲             (ไม่ผ่าน control plane)
                          ถ้า storage firewall ไม่ให้ PROD subnet → 403 / connectivity error
```

**⇒ grant = "necessary but not sufficient" · network reachability = gate ที่ 2 แยกกันคนละชั้น**

### ข้อเท็จจริงที่ verify มา (มี citation):
1. **UC = credential vending** → consumer compute (PROD) อ่าน ADLS ของ DEV **โดยตรง** data ไม่ผ่าน control plane
2. **compute ของ PROD เป็นตัวต่อ storage** ไม่ใช่ compute ของ DEV (metastore แชร์ / compute ไม่แชร์)
3. **ถ้า firewall ปิด → error 403 ไม่ใช่ widget ว่างเงียบๆ** *(แก้ที่เคยเข้าใจผิด: ว่างเปล่า = row filter คืน 0 แถว คนละเรื่องกับ network)*
4. **row filter ทำงานข้าม workspace ได้** (metastore เดียวกัน — Databricks compute บังคับใช้ตอน query) ✅
5. **serverless ก็ต้องเปิด** ผ่าน NSP service tag `AzureDatabricksServerless.<region>` หรือ NCC private endpoint (⏰ deadline 2026-06-09 ผ่านแล้ว — subnet-ID allowlist ต้องย้ายไป NSP)
6. **classic VNet-injected** ต้องมี private endpoint / VNet rule / peering + firewall rule
7. **Delta Sharing/OpenSharing = requirement เดียวกัน** (recipient อ่าน provider storage ตรงๆ) + **row filter/column mask ไม่เดินทางผ่าน share**
8. **ไม่มี UC mode ไหนที่ proxy data ผ่าน control plane** เพื่อเลี่ยง network requirement (ยกเว้น Lakehouse Federation ซึ่งเป็น data path คนละแบบ = JDBC ไป foreign engine ไม่ใช่เคสนี้)

### 🆕 governance gate อีกตัว (เช็คก่อน firewall เพราะเร็วกว่า):
**external-location / storage-credential "workspace binding"** — ถ้า bind ไว้เฉพาะ DEV → PROD/UAT อ่านไม่ได้**แม้ network เปิด + grant ครบ** (เช็คแท็บ Workspaces บน storage credential)

---

## 🔑 network ask เปลี่ยนไป — และดีขึ้น

เดิม §6 เขียนว่า *"เปิด browser → DEV workspace"* (ขอแปลกๆ)
**แต่ D+ variant นี้ user เปิด workspace ตัวเอง — ไม่แตะ DEV (ไม่ติด R5b)**
→ ข้อขอจริงคือ:

> **"เปิด private endpoint / firewall rule จาก PROD compute plane → DEV storage account"**

= **pattern มาตรฐานของ Azure** ที่ UC cross-workspace ออกแบบมาให้ทำอยู่แล้ว → **เถียงกับ infra ง่ายกว่าเยอะ**

**network path ที่ต้องเปิด 1 ใน:**
| PROD compute | เปิดอะไร (ที่ DEV ADLS) |
|---|---|
| Classic (VNet-injected) | private endpoint จาก PROD VNet · หรือ VNet/subnet rule บน storage firewall · หรือ peering + rule |
| Serverless | associate DEV storage กับ NSP + allow `AzureDatabricksServerless.<region>` · หรือ private endpoint จาก NCC ของ PROD |
| ทั้งคู่ | region เดียวกัน + ถ้า public access ปิด → เปิด "Allow Azure trusted services" |

---

## 🧪 PoC PLAN (สิน จะลองเอง)

**ข้อจำกัด:** สินรัน `dbutils.fs.ls` ที่ departmental ไม่ได้ (ไม่มีสิทธิ์/มองไม่เห็น compute ทุก env)
**ทางออก:** ทดสอบที่ **coredata UAT** (สินมีสิทธิ์เต็ม) → ตัดตัวแปร "user ไม่มีสิทธิ์" ออก

**⚠️ UAT พิสูจน์อะไร / ไม่พิสูจน์อะไร:**
- ✅ UAT ผ่าน → กลไก share + row filter + dashboard import **ทำงาน** (governance ครบ)
- ❌ **ไม่ได้พิสูจน์ network ของ departmental PROD** (UAT↔DEV ต่อ network ง่ายกว่า PROD↔DEV)
- ⇒ UAT ผ่าน = เหลือตัวแปรเดียวสำหรับ PROD = network path → เอาไปคุย infra

### วิธี "แชร์ให้ไปขึ้นที่ปลายทาง" — แยก 2 กลไก:

**1️⃣ TABLE → UC GRANT ให้ principal (ไม่ใช่ให้ workspace)**
> metastore เดียวกัน + catalog OPEN → ชื่อ catalog โผล่ใน Catalog Explorer ทุก workspace อยู่แล้ว · grant = เพื่อให้ *query ได้*
```sql
-- รันใน coredata DEV
GRANT USE CATALOG  ON CATALOG  <cat>                  TO `<your-user-or-group>`;
GRANT USE SCHEMA   ON SCHEMA   <cat>.cost             TO `<your-user-or-group>`;
GRANT SELECT       ON TABLE    <cat>.cost.cost_wide   TO `<your-user-or-group>`;
GRANT EXECUTE      ON FUNCTION <cat>.cost.fn_cost_rls TO `<your-user-or-group>`;  -- ⚠️ ลืมบ่อยสุด
```

**2️⃣ DASHBOARD → ไม่ auto ขึ้น (เป็น workspace object)** มี 2 ทาง ทดสอบคนละเรื่อง:
| ทาง | ทำยังไง | ทดสอบอะไร |
|---|---|---|
| A. Publish + share URL | publish ที่ DEV → share account user → เปิด URL | 🚨 URL ชี้ DEV → เทส browser→DEV (R5b) **ไม่ใช่ D+** |
| **B. Export → Import** ⭐ | export `.lvdash.json` → import เข้าปลายทาง → repoint warehouse → เปิด | ✅ **D+ จริง** |
→ **PoC ใช้ทาง B** (ทาง A จะหลอก เพราะใน UAT เปิด DEV URL ได้อยู่แล้ว)

### 🧪 test ที่เด็ดขาดสุด — ไม่ต้องใช้ dashboard ด้วยซ้ำ:
```sql
-- รันใน SQL editor / notebook ของ coredata UAT
SELECT * FROM <cat>.cost.cost_wide LIMIT 10;
```
**decision tree:**
```
เห็นแถว (filter ตัดถูก)      → ✅ governance + network + RLS ครบ → D+ ทำงาน (ในขอบเขต coredata)
403 / connectivity error    → ❌ ติด NETWORK → ตัวที่ต้องเปิด (เอาไปคุย infra)
ว่างเปล่า 0 แถว              → ⚠️ row filter คืน false — ทุกอย่างทำงาน แค่ filter logic
table/catalog not found     → ⚠️ คนละ metastore / catalog ISOLATED (ยัง bind UAT) / grant ไม่ครบ
```

### ลำดับที่แนะนำ:
1. **เช็ค metastore** (30 วิ): `SELECT current_metastore();` รันทั้ง DEV + UAT → **ต้องได้ค่าเดียวกัน** (ต่าง = คนละ metastore → Delta Sharing → row filter ไม่ผ่าน share)
2. **GRANT 4 บรรทัด** ให้ user ตัวเอง (ที่ DEV)
3. **รัน `SELECT ... LIMIT 10` ที่ UAT** → อ่าน decision tree
4. ผ่าน → **export/import dashboard เข้า UAT** (ทาง B) → widget ขึ้นมั้ย
5. ได้ผล → เขียน D+ resurrection doc + network ask

### caveat 2 ข้อ (grant แล้วยังอ่านไม่ได้ทั้งที่ควรได้):
- **catalog ISOLATED** → `databricks catalogs update <cat> --isolation-mode OPEN` (หรือ add binding READ_ONLY)
- **storage-credential/external-location bind เฉพาะ DEV** → เช็คแท็บ Workspaces (governance ไม่ใช่ network เช็คเร็ว)

---

## 🔄 REPOSITION (สถานะล่าสุด)

```
email artifact (PDF + Excel)  →  ✅ ship สัปดาห์นี้ = INTERIM ระหว่างรอ network
D+ (UC share + dashboard ฝั่ง PROD)  →  🎯 TARGET — ปลดล็อกทันทีถ้าเปิด storage network path
```
**pipeline + gold table + row filter ที่ทำไว้ = ใช้ต่อได้ทั้งหมด ไม่มีอะไรเสียเปล่า**

---

## 📝 corrections จาก session นี้ (แก้ความเข้าใจเดิม)
1. ~~"D+ ตายแล้ว"~~ → **D+ conditional — ฟื้นถ้า network path เปิด** (Sarunya ยอม share UC แล้ว)
2. ~~"UC share ติด network เสมอ"~~ → **ติดเฉพาะถ้า storage firewall ปิด — เป็น layer ที่เปิดได้ด้วย private endpoint/firewall rule มาตรฐาน**
3. **row filter ทำงานข้าม workspace ได้** (metastore เดียวกัน) — ยืนยันแล้ว
4. **firewall block = error 403 ไม่ใช่ widget ว่าง** — widget ว่าง = row filter คืน 0 แถว (คนละสาเหตุ)
5. network ask เปลี่ยนจาก "browser→DEV" เป็น **"PROD compute→DEV storage (private endpoint/firewall)"** — standard Azure pattern

## ❓ ยังค้าง (ต้องได้คำตอบ)
- metastore เดียวกันจริงมั้ย (Q ข้อ 1-2 รวมกัน)
- catalog OPEN/ISOLATED
- storage network path เปิดมั้ย (PoC จะตอบ)
- Delta Sharing option (Sarunya re-check)
- external-location workspace binding
