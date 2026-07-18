# Topic 1 — Solution D+ (resurrected): UC share → dashboard in the client's own workspace

> **วันที่:** 2026-07-18 · **สถานะ:** TARGET solution (conditional on R5-network) · fallback = Artifact Factory
> **ที่มา:** Sarunya เปิดให้ share UC ได้ (2026-07-15) → D+ ที่เคยคิดว่าตาย กลับมาเป็นตัวเลือกที่ดีที่สุด
> **คู่กับ:** skill `databricks-uc-governance-sharing` (§6b network gate, §3 RLS, §7 publish modes) · `context-20260715-vscode-uc-share-pivot.md`
> Generic template — ไม่มี AIA identifier

---

## 0. ทำไม D+ ชนะ Artifact Factory (เมื่อ network เปิด)

| | Artifact Factory (email) | **D+ (UC share)** |
|---|---|---|
| K3 เห็นใน workspace ตัวเอง | ❌ | ✅ |
| K6 client จ่าย compute | ❌ เราจ่าย | ✅ เขาจ่าย (warehouse ของเขา) |
| live / refreshable | ❌ static snapshot | ✅ live |
| interactive | ⚠️ Excel pivot | ✅ dashboard เต็ม |
| isolation | by construction (1 file/team) | UC row filter |
| R5b (browser→DEV) | ไม่เกี่ยว | ✅ ไม่ติด (เปิด workspace ตัวเอง) |
| effort | job + delivery | grant + import ครั้งเดียว |

---

## 1. Architecture

```
     ┌──────────── ONE UC metastore (ต้อง verify: same metastore) ────────────┐
     │                                                                        │
 coredata DEV                                              departmental PROD
 ┌────────────────┐                                    ┌──────────────────────┐
 │ pipeline (ของเรา)│──write──► <cat>.gold.cost_wide     │ dashboard (ของเขา)     │
 │ compute: DEV     │           + tag_team (top-level col)│  import .lvdash.json  │
 │                  │           + ROW FILTER              │  หรือสร้างเอง           │
 │ 💾 ADLS (DEV)     │◄─────── read files directly ────────│ 💰 warehouse (PROD)   │
 └────────────────┘         (credential vending)         │ 👤 user เปิด ws ตัวเอง  │
        ▲                                                 └──────────────────────┘
        │  🚨 R5-network: PROD compute plane ต้องมี network line-of-sight
        │     ไป ADLS ของ DEV (storage firewall / private endpoint / NCC)
        └─────────────────────────────────────────────────────────────────
 GRANT (governance) = จำเป็นแต่ไม่พอ · network reachability = gate ที่ 2
```

**หลักการที่ทำให้ "ห้ามเข้า DEV" ผ่าน:**
> UC GRANT = สิทธิ์บน **data** ไม่ใช่ membership ของ **workspace** → table โผล่ใน Catalog Explorer *ของเขา*, query ด้วย warehouse *ของเขา*, **ไม่มีใครเข้า DEV** (R3 ✓)

---

## 2. Prerequisites — verify ก่อน (ตามลำดับ, ถูกสุด→แพงสุด)

| # | เช็ค | คำสั่ง / วิธี | ถ้า fail |
|---|---|---|---|
| 1 | **same metastore** | `SELECT current_metastore();` ทั้ง DEV + PROD → ต้องเท่ากัน | คนละ metastore → ต้องใช้ Delta Sharing (row filter ไม่เดินทางผ่าน share → materialize table แยกต่อทีม) |
| 2 | **catalog isolation** | `databricks workspace-bindings get-bindings catalog <cat>` | `ISOLATED` → bind PROD เป็น `BINDING_TYPE_READ_ONLY` (หรือ `--isolation-mode OPEN`) ไม่งั้น **widget ว่างเงียบ** |
| 3 | **external-location / storage-credential binding** | Catalog Explorer → storage credential → Workspaces tab | bind เฉพาะ DEV → PROD อ่านไม่ได้แม้ network เปิด (governance, เช็คเร็ว) |
| 4 | 🚨 **R5-network** | จาก notebook ฝั่ง consumer: `dbutils.fs.ls('abfss://<c>@<devstore>.dfs.core.windows.net/')` | **403/timeout = ติด network** → ต้องเปิด 1 path (§4) |

---

## 3. Build — grant + row filter (รันที่ coredata DEV)

```sql
-- 3.1 row filter function (team key ต้องเป็น top-level column — bind ใน MAP ไม่ได้)
CREATE OR REPLACE FUNCTION <cat>.gold.fn_team_rls(team_tag STRING)
RETURN is_account_group_member('cost-platform-admins')                 -- platform bypass
    OR EXISTS ( SELECT 1 FROM <cat>.gold.team_access_map m              -- mapping-table driven (แนะนำ)
                WHERE m.team_tag = team_tag
                  AND is_account_group_member(m.account_group) );

ALTER TABLE <cat>.gold.cost_wide SET ROW FILTER <cat>.gold.fn_team_rls ON (tag_team);

-- 3.2 grant ให้ account group ของแต่ละทีม (4 อย่าง — USE CATALOG/SCHEMA ไม่ inherit จาก SELECT)
GRANT USE CATALOG  ON CATALOG  <cat>                 TO `client-team-a`;
GRANT USE SCHEMA   ON SCHEMA   <cat>.gold            TO `client-team-a`;
GRANT SELECT       ON TABLE    <cat>.gold.cost_wide  TO `client-team-a`;
GRANT EXECUTE      ON FUNCTION <cat>.gold.fn_team_rls TO `client-team-a`;  -- ⚠️ ลืมบ่อยสุด
```
- **`is_account_group_member()` ไม่ใช่ `is_member()`** (อย่างหลังคืน FALSE เงียบให้ account user)
- **account group ไม่ใช่ workspace-local** (สร้างที่ account console / SCIM)
- row filter บังคับใช้ก็ต่อเมื่อ viewer เป็น **Consumer access ขึ้นไป** (bare account user ไม่ได้ RLS) → ผูกกับ Topic 2.2

---

## 4. R5-network — path ที่ต้องเปิด (ที่ DEV ADLS, เลือก 1)

| consumer compute | เปิดอะไร |
|---|---|
| **Classic (VNet-injected)** | private endpoint จาก PROD VNet → DEV storage · หรือ VNet/subnet rule บน storage firewall · หรือ peering + rule · (NPIP clusters) |
| **Serverless** | associate DEV storage กับ **NSP** + allow `AzureDatabricksServerless.<region>` · หรือ private endpoint จาก **NCC** ของ PROD |
| ทั้งคู่ | **region เดียวกัน** + ถ้า public access ปิด → เปิด "Allow Azure trusted services" |

⏰ deadline 2026-06-09: storage ที่ allowlist serverless subnet-ID ต้องย้ายไป NSP + service tag
**ข้อขอ infra (แคบ, มาตรฐาน):** *"private endpoint / firewall rule จาก PROD compute plane → DEV storage"* — **ไม่ใช่ data-movement exception** (data ไม่ลง PROD, PROD compute อ่าน DEV storage ตรงผ่าน vended credential)

---

## 5. Deliver dashboard ให้ไปอยู่ workspace เขา — 2 ทาง

| ทาง | วิธี | หมายเหตุ |
|---|---|---|
| **A. Export → Import** ⭐ | เราสร้าง dashboard บน `cost_wide` ที่ DEV → export `.lvdash.json` → **admin ฝั่งเขา import เข้า workspace เขา** → repoint warehouse ฝั่งเขา → publish | dashboard อยู่ workspace เขา · เขา query ด้วย warehouse เขา · `.lvdash.json` = query+widget เท่านั้น (ไม่มี data) → ต้องมี grant(§3)+network(§4) ถึงจะ resolve |
| **B. เขาสร้างเอง** | เราแค่ grant → เขาสร้าง dashboard/Genie เองบน `cost_wide` | control น้อยกว่าแต่ยืดหยุ่น |

**publish mode:** ถ้า publish ต้อง **"Individual data permissions"** (`embed_credentials: false`) → RLS ประเมินตาม viewer · **default "Share data permissions" = อันตราย** (รันในนาม publisher → ทุกคนเห็นทุกแถว)

---

## 6. PoC (Sin รันเอง — รันที่ departmental ไม่ได้ ใช้ coredata UAT แทน)

```sql
-- 1) same metastore?
SELECT current_metastore();          -- รันทั้ง DEV และ UAT → ต้องเท่ากัน
-- 2) grant ให้ user ตัวเอง (ที่ DEV) — 4 บรรทัดใน §3.2 เปลี่ยน group เป็น user ตัวเอง
-- 3) decisive test (ที่ UAT):
SELECT * FROM <cat>.gold.cost_wide LIMIT 10;
```
```
เห็นแถว (filter ตัดถูก)   → ✅ governance+network+RLS ครบ → D+ ทำงาน (ในขอบเขต coredata)
403 / connectivity        → ❌ ติด NETWORK → §4
ว่าง 0 แถว                → ⚠️ row filter คืน false (ทุกอย่างทำงาน แค่ logic)
table/catalog not found   → ⚠️ คนละ metastore / ISOLATED / grant ไม่ครบ
```
> ⚠️ **UAT ผ่าน ≠ PROD ผ่าน** — coredata UAT↔DEV network ง่ายกว่า departmental PROD↔DEV → UAT พิสูจน์ *กลไก* · PROD network ยังต้อง confirm กับ infra แยก

---

## 7. Decision

```
same metastore? ──no──► Delta Sharing (materialize per-team) หรือ Artifact Factory
     │yes
network path เปิด? ──no──► เปิดได้มั้ย (§4)? ──no──► Artifact Factory (fallback)
     │yes                              │yes → เปิด แล้วเดิน D+
     ▼
  D+ ✅  (grant §3 → import §5 → RLS per team → เขาจ่าย compute)
```

## 8. ยังต้องได้คำตอบ
- metastore เดียวกัน? (Q1/Q2) · catalog OPEN/ISOLATED? · network path เปิด/เปิดได้มั้ย? (R5-network) · Delta Sharing option (Sarunya re-check) · team count 5/30 (จำนวน account group + grant)
