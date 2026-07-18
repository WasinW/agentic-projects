# Topic 2.1 — ทำไม `system.billing.usage` ไม่เท่า Azure Portal Cost Management

> **วันที่:** 2026-07-17 · verify กับ Microsoft Learn / Databricks docs · [CONFIRMED-DOCS] vs [INFERENCE]
> **สำหรับ:** สิน — Databricks-consumption cost dashboard (Topic 2.1)
> **สรุปสั้น:** ตัวเลข**ควรต่างกัน**อยู่แล้ว — มันวัดคนละอย่าง

---

## 🎯 BLUF (bottom line up front)

```
system.billing.usage × list_prices  =  DBU consumption × ราคา LIST         → ledger สำหรับ "attribution"
Azure Portal Cost Management        =  เงินจริงที่จ่าย (รวม VM/disk/IP/storage/network + discount + tax)
```

**2 ช่องว่างใหญ่สุด:**
1. **classic compute → VM/disk/IP จริง ถูกบิลแยกใน Azure (managed resource group) และ *ไม่เคย* อยู่ใน `system.billing`** ← ตัวใหญ่สุด (บ่อยครั้ง VM = 40-60% ของ cost ก้อนหนึ่ง)
2. **`list_prices` = ราคา list ไม่ใช่ราคาจริง** (ไม่รวม EA/MCA discount, DBCU prepurchase drawdown, promo)

→ **จะไม่มีวันตรงเป๊ะ** เว้นแต่เอา actual-price data มาเสริม — ซึ่งคุณ**มีอยู่แล้ว** (Cost Management Export → ADLS ของ Topic 1)

---

## 📊 ตาราง "ทำไมไม่ตรง"

| component | ใน system.billing? | ใน Portal? | magnitude |
|---|:--:|:--:|---|
| **DBU consumption** (Databricks service layer) | ✅ (เป็น DBU) | ✅ (เป็น $) | ตัวเดียวที่ทั้งคู่มี |
| **classic-compute VM จริง** | ❌ **ไม่มี** | ✅ (managed RG, meter *Virtual Machines*) | 🔴 **ใหญ่สุด — 40-60%** |
| managed disk (VM OS/local) | ❌ | ✅ | เล็ก-กลาง |
| public IP / networking (managed RG) | ❌ | ✅ | เล็ก |
| **list vs actual price** (discount/DBCU/promo) | list only | actual $ | **10-40%+ ที่ list สูงเกิน** |
| ADLS storage / egress / NAT / private endpoint | ❌ | ✅ | varies |
| **serverless VM** | ✅ **bundle อยู่ใน DBU price** | ✅ (meter Databricks) | serverless → 2 ตัวใกล้กันกว่า |
| tax / rounding / currency | ❌ (pre-tax USD list) | ✅ (post-tax, billing currency) | ไม่กี่ % |
| timezone / period | UTC hourly | Azure billing period | noise ขอบเดือน |
| latency (record ยังทยอยเข้า) | delayed, ไม่มี SLA | finalized ตอน invoice | **same-day จะดูขาดเสมอ** |

### 🔑 classic VM คือตัวการหลัก [CONFIRMED]
```
Azure Databricks total (classic) = DBU charge (Databricks meter) + VM charge (Microsoft, managed RG)
                                    └─ อยู่ใน system.billing ─┘   └─ ไม่อยู่ใน system.billing ─┘
```
- VM/disk/NIC อยู่ใน **managed resource group** (tag `Vendor: Databricks`) → meter category *Virtual Machines* / *Storage* แยกจาก meter *Azure Databricks* (DBU)
- ⚠️ gotcha: filter Portal ด้วย subcategory *"Azure Databricks Regional"* จะ **ตัด VM ใน managed RG ออก** → นับผิดได้แม้อยู่ใน Portal เอง

### serverless ต่าง [CONFIRMED-ish]
serverless → VM bundle เข้า DBU price สูงขึ้น ไม่มี VM line แยก → workload serverless ล้วน `usage × effective_list` **ใกล้ Portal มาก** (เหลือแค่ list-vs-actual + tax + latency)

---

## 🧭 วิธี reconcile

### mental model ที่ถูก
> **Azure Cost Management = source of truth ของ "เงินจริง"** · **`system.billing.usage` = source of truth ของ "DBU attribution"** (ต่อ job/cluster/warehouse/user/tag) — **ตอบคนละคำถาม อย่าคาดว่าจะเท่ากัน**

| คำถาม | ใช้แหล่งไหน |
|---|---|
| "เดือนนี้ Databricks จ่ายจริงเท่าไหร่ (finance/invoice)" | **Cost Mgmt Export → ADLS** (มีแล้ว) filter `Vendor=Databricks` + managed RG → รวม DBU+VM+disk+IP ที่ราคาจริง+tax |
| "ทีม/job/warehouse ไหนกิน DBU / trend / chargeback" | **`system.billing.usage`** join `list_prices` → list-normalized cost แบ่งได้ |

### วิธี join 2 แหล่งให้ dashboard reconcile [INFERENCE grounded]
1. **actual $ (authoritative):** จาก Export รวม workspace + managed RG → split ตาม meter category (แยก DBU line กับ VM line)
2. **attribution:** จาก `system.billing.usage` แบ่ง DBU ต่อ team/job/tag → คิด share ของ DBU รวม
3. **allocate VM cost ให้ทีม:** VM ใน Export ไม่ได้ tag ต่อ job — 2 ทาง:
   - (ก) **cluster custom tag propagate ไป VM ใน managed RG** → group VM cost ใน Export ตาม team tag ตรงๆ *(ต้อง verify tag propagation ใน env ตึงๆ)*
   - (ข) **pro-rate VM cost ตาม DBU share** จากขั้น 2
4. **reconcile check:** `(system.billing DBU × effective_list)` ควรอยู่ใน *discount% + tax* ของ **DBU-meter-only** slice ใน Export → **เทียบ DBU-line กับ DBU-line เท่านั้น ห้ามเทียบ DBU-line กับ total** (นี่คือ error คลาสสิกที่ทำให้คนคิดว่า table ผิด)

> **ถ้าอยากให้ตัวเลข system.billing เข้าใกล้ Portal total → ต้องบวก classic VM cost (จาก Export, join ด้วย managed RG / cluster tag) เข้าไปบน DBU$**

### ❗ actual (ไม่ใช่ list) หาจากใน Databricks ได้มั้ย → **ไม่ได้**
ไม่มี system view ไหนที่ราคา = rate จริงที่ negotiate ไว้ · `list_prices` = list ชัดเจน · account-console Usage dashboard ก็ใช้ `effective_list` = list estimate → **actual $ ต้องมาจาก Azure billing เท่านั้น**

---

## 💻 SQL ที่ถูกต้อง (point-in-time price join)

```sql
-- LIST-PRICE ESTIMATE ของ DBU cost, แบ่งตาม workspace / SKU / team tag
-- CAVEAT 1: DBU cost ที่ราคา LIST เท่านั้น — ไม่รวม classic VM/disk/IP (อยู่บน Azure bill, managed RG)
--           serverless VM bundle อยู่ในนี้แล้ว
-- CAVEAT 2: effective_list = ราคา LIST ไม่ใช่ rate จริง (EA/MCA/DBCU) → สูงกว่า invoice จริงตาม discount%
-- CAVEAT 3: เวลาเป็น UTC — align reporting period เป็น UTC กัน drift ขอบเดือน
-- CAVEAT 4: SUM(usage_quantity) net RETRACTION/RESTATEMENT correction แล้ว — อย่า COUNT rows
SELECT
    u.workspace_id,
    u.sku_name,
    u.billing_origin_product,
    u.custom_tags['team']             AS team,        -- chargeback key (ดู note tag)
    u.product_features.is_photon      AS is_photon,    -- Photon baked ใน usage_quantity แล้ว
    u.product_features.is_serverless  AS is_serverless,
    SUM(u.usage_quantity)                                    AS dbus,
    SUM(u.usage_quantity * p.pricing.effective_list.default) AS list_cost_usd
FROM system.billing.usage u
JOIN system.billing.list_prices p
  ON  p.sku_name = u.sku_name
  AND p.cloud    = u.cloud                        -- กัน SKU-name ชนข้าม cloud
  AND u.usage_end_time >= p.price_start_time
  AND (p.price_end_time IS NULL OR u.usage_end_time < p.price_end_time)  -- ราคา active ปัจจุบัน
WHERE u.usage_date BETWEEN :start_date AND :end_date   -- UTC calendar boundary
GROUP BY ALL
ORDER BY list_cost_usd DESC;
```

**จุดถูกต้องสำคัญ:**
- **point-in-time join** `usage_end_time >= price_start_time AND (price_end_time IS NULL OR usage_end_time < price_end_time)` — branch `IS NULL` จับราคาปัจจุบัน (ไม่มี end) · ถ้าไม่ bound → **fan-out** (usage × N price rows) cost บวม
- **`pricing.effective_list.default`** = field ที่ถูก (resolve list+promo) อย่าใช้ `pricing.default` ถ้ามี promo active
- **`custom_tags['team']`** = attribution key · classic → tag ที่ **cluster/warehouse** · serverless → **usage/budget policy** ให้ tag ลง `custom_tags`
- **`usage_metadata`** (`.job_id/.warehouse_id/.cluster_id/.dlt_pipeline_id`) = attribution ที่ระบบการันตี เชื่อถือกว่า user tag ตอน tag หาย

---

## ⚠️ Gotchas
- **หลาย price row ต่อ SKU** — ไม่ bound point-in-time = fan-out cost บวม
- **currency** — `currency_code` มัก USD list · invoice จริงอาจ local currency + FX → อย่าปน
- **cross-cloud SKU ชน** — join `cloud` ด้วยถ้า multi-cloud
- **tag propagation → system.billing:** `custom_tags` = tag บน **compute resource** (cluster/warehouse) + serverless-policy tag · **job-level tag ไม่ auto กลายเป็น cluster tag** → job บน job compute ต้อง set tag ใน cluster spec · **env ตึงๆ ต้อง test 1 cluster ก่อนเชื่อ chargeback**
- **tag propagation → Azure VM:** cluster custom tag propagate ไป VM ใน managed RG (กลไกเดียวกับ `Vendor:Databricks`) → allocate VM cost ตาม team ได้ · แต่มี **delay** + บาง resource ไม่รับ tag ทุกตัว → validate ใน Export
- **account vs workspace scope:** system table = **account-level** (เห็นทุก workspace) · Cost Mgmt = subscription/RG → align scope ตอน reconcile
- **ต้อง enable `system.billing`** โดย account admin + reader ต้องมี `SELECT` บน `usage` + `list_prices` (env ตึงๆ = prerequisite จริง ไม่ใช่ของแถม)
- **retention:** query ย้อนไกลไม่ได้ → snapshot ลง Delta เองถ้าต้องเก็บ long history
- **latency ไม่มี SLA:** อย่า reconcile intra-day/same-day → รอ record settle (+ invoice finalize)

---

## 🆕 2025-2026 features
- **Usage Dashboard v2.0 (Preview)** — import จาก account-console Usage tab · เพิ่ม cost forecasting + object-level drill-down + breakdown ตาม product/SKU/custom tag · ราคายังเป็น **list**
- **Serverless usage/budget policies** — attach policy ให้ serverless → tag ลง `custom_tags` (`usage_metadata.usage_policy_id` · `budget_policy_id` **deprecated**) → **วิธี attribution ต่อทีมบน serverless** (ไม่มี cluster ให้ tag) ← เชื่อมกับ Topic 2.2(b)
- **`system.compute.clusters` / `node_timeline`** — join ด้วย `cluster_id` → `owned_by` + node type → map DBU ไป VM SKU เพื่อ line up กับ VM meter ใน Export
- **ยังไม่มี "actual/priced cost" system view** — actual $ ต้องมาจาก Azure billing (hard limit วันนี้)

---

## 🔒 สิ่งที่ต้องยอมรับว่าแก้ไม่ได้
1. `system.billing × list_prices` = **LIST-PRICE, DBU-ONLY estimate** — ไม่มีวันเท่า Portal เว้นแต่ (ก) บวก classic VM/disk/IP จาก Export (ข) แทน list ด้วย rate จริง → ทั้งคู่ต้องใช้ Azure-side data
2. **ตัวเลข $ ที่ authoritative = Azure Cost Management** (Export) → ใช้ทำ finance/invoice · ใช้ `system.billing` ทำ attribution/trend · reconcile **DBU-meter ↔ DBU-meter** ไม่ใช่ DBU ↔ total
3. **best match ที่ทำได้:** `system.billing DBU$-at-actual (Export DBU meter)` + `classic VM$ (Export VM meter, allocate ตาม cluster tag/DBU pro-rata)` ≈ Portal Databricks total − (tax/rounding/latency)

---

## 🔗 เชื่อมกับ workstream อื่น
- **custom_tags['team']** = chargeback key เดียวกับ Topic 1 (per-team) → ใช้ tag เดียวกันได้
- **serverless budget policy tag** = สะพานไป **Topic 2.2(b) budget** (attribution ต่อทีมบน serverless)
- **Cost Mgmt Export → ADLS** ที่ Topic 1 มีอยู่แล้ว = แหล่ง actual $ ของ Topic 2.1 ด้วย → **reuse ได้**

## ➡️ next (ถ้าจะต่อ)
- อยากได้ actual-rate DBU (ไม่ใช่ list) native → เป็นเรื่อง data-architect / ต้อง ingest Azure billing
- schema Export + managed-RG IAM plumbing สำหรับ join → azure-expert
- **ขอ SQL ปัจจุบันของสินมาดู → ไล่ทีละบรรทัดว่าขาด/เกินตรงไหนเทียบกับ pattern ข้างบน**
