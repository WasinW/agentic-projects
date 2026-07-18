# AIA Cost Platform — Solution Design + Architecture (Master)
### Topic 1 = Dashboard Sharing to Departmental Teams · Topic 2 = Genie Cost Monitoring + Governance Lockdown
*Teaching-grade · grounded ใน 4 skills (uc-governance-sharing · serverless-networking · cost-optimization · genie-governance) + R1–R10 requirements. วันที่ 2026-07-13. ตัวเลข/identifier = placeholder (IP boundary).*

---

## 0. How the two topics relate — the one-paragraph map

Topic 1 กับ Topic 2 **ไม่ใช่สองโปรเจกต์ — มันคือสองหน้าของ spine เดียวกัน**. ทั้งคู่วิ่งบน (1) **per-team tag** เดียว (`team=<t>` บน gold + บน warehouse) ที่ทำหน้าที่ทั้ง *RLS key*, *chargeback key*, และ *budget attribution key*; (2) **Unity Catalog grant + row filter** ตัวเดียวกัน (`is_account_group_member()` + mapping table) ที่ตัด row ต่อทีม; และ (3) **serverless SQL warehouse ต่อทีม** ตัวเดียวกันที่รัน query. สำคัญที่สุด: **คนที่เป็น "viewer" ของ dashboard ใน Topic 1 คือคนกลุ่มเดียวกับ business user ที่ถูก lock ลง Genie ใน Topic 2** — population เดียว, Consumer-access เดียว, entitlement-migration dependency เดียว. และทั้งสอง topic ตายด้วยกำแพงเดียวกันคือ **network-reachability gate** (departmental-PROD compute → coredata-DEV storage): UC grant เปิดสิทธิ์ควบคุม แต่ **byte จริงวิ่งตรงจาก compute plane ของ consumer ไปที่ ADLS ของ provider** — ถ้า network path ปิด ทั้ง dashboard (Topic 1) และ Genie (Topic 2) 403/timeout เหมือนกัน. เพราะฉะนั้นอ่าน §1 (shared spine) ให้ขึ้นใจก่อน แล้ว Topic 1/Topic 2 จะเป็นแค่ "สอง application ของ mechanic ชุดเดียวกัน".

---

# 1. THE SHARED SPINE — อ่านครั้งเดียว ใช้ทั้งสอง topic

## 1.1 สาม tier ที่คนชอบเอามาปน (90% ของบั๊ก "ทำไมเขาเห็น/ไม่เห็น")

```
IDENTITY อยู่ที่ ACCOUNT   ·   DATA อยู่ที่ METASTORE   ·   COMPUTE อยู่ที่ WORKSPACE
```

- **Identity = account groups** (`client-team-a`, `biz-consumers-claims`) สร้างที่ account console / SCIM — **ไม่ใช่ workspace-local group** ที่ไม่เดินทางข้าม workspace.
- **Data + grant = metastore** → grant ที่ออกจาก coredata DEV **resolve ข้ามไป departmental PROD ได้เอง** ถ้า same metastore + account group. นี่คือกลไกทั้งหมดของ cross-workspace sharing.
- **Compute = workspace** → ใครรัน query = ใครจ่าย DBU.

> **ศัพท์ให้เป๊ะ — "PROD" มีสองตัว.** topology มี **สาม** workspace: `coredata DEV` (provider, ของ Sin) · `coredata PROD` (ไม่ใช้ — R1 ห้าม promote มาที่นี่) · **`departmental PROD`** (consumer, ของ client). ทุกที่ที่เขียน "PROD compute → DEV storage" หมายถึง **departmental PROD** เสมอ.

## 1.2 The three gates — Grant ≠ Reachability (หัวใจของทั้งสอง topic)

Access ที่นี่ **ไม่ใช่บันไดขั้นเดียว** (catalog→schema→table). มันคือ **2 แกน governance อิสระ + 1 gate network** — ผ่านแกนนึงไม่ช่วยอีกแกน:

```
GATE A — Object privileges  (control-plane, governance)   "แตะ object ได้มั้ย"
         USE CATALOG · USE SCHEMA · SELECT · EXECUTE(row-filter fn)   <- ลืม EXECUTE บ่อยสุด

GATE B — Data filtering     (control-plane, governance)   "ได้ row/col ไหนกลับมา"
         ROW FILTER (is_account_group_member) · COLUMN MASK
         + workspace-catalog BINDING (ISOLATED -> ต้อง bind ไม่งั้น widget ว่าง)

GATE C — Network path       (DATA-plane)  == R5-network == "GATE 0" ของ Topic 2
         "packet วิ่งถึง storage มั้ย"
         departmental-PROD compute plane -> DEV ADLS (firewall/PE/NCC/NSP)
```

**กลไก credential vending (ต้องเข้าใจให้ลึก):**
> **UC GRANT = การตัดสินใจที่ control-plane** (ใครมีสิทธิ์แตะ data). **แต่ byte จริงไม่วิ่งผ่าน control plane** — เวลา consumer query, UC จะ **vend short-lived credential** ให้ **compute plane ของ departmental PROD ไปอ่านไฟล์ที่ ADLS ของ coredata DEV โดยตรง**. ⇒ **Grant ≠ Reachability.** ต้องผ่าน 2 plane: governance grant + data-plane network path.

**A + B ผ่านหมด แต่ C ปิด ⇒ query 403/timeout.** UC feature ไหนก็ route รอบ network policy ไม่ได้. นี่คือกำแพงเดียวกับที่ฆ่า Option E/E2 (Genie Agent) ใน requirements doc — และเป็น make-or-break ของทั้ง Topic 1 (D+) และ Topic 2.2 (Genie-on-cost-table).

### 403-vs-empty-vs-notfound triage (จำให้ขึ้นใจ — ประหยัดเป็นชั่วโมง)

| อาการ | ประตูที่ติด | สาเหตุ |
|---|---|---|
| grant ถูก, `is_account_group_member()`=TRUE, แต่ query **error 403 / timeout** | **GATE C (network / data-plane)** | storage firewall / PE ไม่รับ compute ของ departmental PROD |
| query รันได้ แต่ผล **ว่าง ไม่มี error** | GATE B / binding (control-plane) | catalog ISOLATED ไม่ได้ bind **หรือ** row filter คืน 0 แถว |
| **"table/catalog not found"** | control-plane | คนละ metastore, catalog ISOLATED ไม่ได้ bind, หรือ grant ไม่ครบ |

> **เครื่องมือ triage ที่เด็ดขาด** — รันจาก notebook ฝั่ง consumer (PoC ใช้ coredata UAT แทน departmental PROD):
> ```python
> dbutils.fs.ls("abfss://<container>@<devstorage>.dfs.core.windows.net/")
> # 403/timeout ทั้งที่ Catalog Explorer เห็น table  -> GATE C (network) — เปิด path ใน §2.5
> # อ่านได้ปกติ                                       -> network OK; ถ้าผลว่าง = governance (B/binding)
> ```
> อันนี้ bypass UC เพื่อแยกชั้น network ออกจาก governance ตรงๆ. เช็ค governance ก่อน (ถูกกว่า): **storage-credential / external-location binding** ผูกเฉพาะ DEV มั้ย (Workspaces tab) — ถ้าใช่ consumer อ่านไม่ได้แม้ network เปิด.

## 1.3 The per-team tag — one key, three jobs

`tag_team` (project จาก `custom_tags['team']` / `tags['team']`) เป็น key เดียวที่ทำสามหน้าที่:
1. **RLS key** — bind row filter (Topic 1 + 2.2).
2. **Chargeback key** — `system.billing.usage.custom_tags['team']` (Topic 2.1).
3. **Budget attribution key** — tag บน warehouse object (Topic 2.2 budget).

> **tag hygiene:** เก็บ MAP `custom_tags` ไว้ long-tail, แต่ **ยกเฉพาะ key ที่ govern ออกมาเป็น top-level column** `tag_team STRING` — เพราะ row filter **bind ใน MAP ไม่ได้ และ bind บน VIEW ไม่ได้** (S5). (จุดต่างของ Sin จากบูมที่ drop tags ทิ้ง.)
> **บังคับ tag ที่ต้นทาง:** `custom_tags` ไม่ auto จาก job-level → set ใน cluster spec + บังคับด้วย **cluster policy** (`custom_tags.<key>` = `fixed`/`allowlist` → cluster start ไม่ได้ถ้าไม่ tag). อย่าหวังว่าคนจะ tag เอง. **1 warehouse ต่อทีม, tag `team=<t>`** = คำตอบสะอาด (attribution + cap + result-cache).

## 1.4 RLS building blocks (ใช้เหมือนกันทั้งสอง topic)

```sql
-- (a) team key project เป็น top-level column ก่อน (bind ใน MAP / บน VIEW ไม่ได้)
--     ใน gold: SELECT ..., tags['team'] AS tag_team

-- (b) mapping-table-driven filter (แนะนำ — decouple tag hygiene ออกจาก identity)
CREATE TABLE <cat>.gold.team_access_map (team_tag STRING, account_group STRING);

CREATE OR REPLACE FUNCTION <cat>.gold.fn_team_rls(team_tag STRING)
RETURN is_account_group_member('cost-platform-admins')            -- platform/FinOps bypass เห็นทุกแถว
    OR EXISTS ( SELECT 1 FROM <cat>.gold.team_access_map m
                WHERE m.team_tag = team_tag
                  AND is_account_group_member(m.account_group) );  -- <- ไม่ใช่ is_member()

ALTER TABLE <cat>.gold.cost_wide
  SET ROW FILTER <cat>.gold.fn_team_rls ON (tag_team);            -- bind บน TABLE (ไม่ใช่ VIEW), top-level col
```

**Teaching whys (จำ 4 อันนี้):**
- **`is_account_group_member()` ไม่ใช่ `is_member()`** — `is_member()` resolve กับ *workspace-local* group → คืน **FALSE เงียบๆ** ให้ account user → ทั้ง audience เห็น 0 แถว. บั๊ก debug หลายชั่วโมงคลาสสิก.
- **mapping table > naming convention** — onboarding ทีมใหม่ = **INSERT 1 แถว** ไม่ต้อง DDL/redeploy, ไม่ผูก typo/casing ของ source tag เข้ากับชื่อ Entra group.
- **กฎเหล็ก group-consistency:** group ที่ filter เช็ค **ต้องเป็น group ที่ consumer เป็นสมาชิกจริง**. ถ้า grant ให้ `biz-consumers-claims` แต่ filter เช็ค `client-team-claims` → RLS คืน 0 row เงียบๆ (ทุกคนเห็น empty ทั้งที่ grant ถูก). PoC = เช็ค group เดียวกับที่ grant; prod = mapping table.
- **ถ้า team count โต (5→30)** → พิจารณา **ABAC row-filter policy** (GA 2026-05-13): 1 policy คุมหลาย table แทน bind ทีละ table. **WATCH-OUT:** GA มี breaking change — view/function เหนือ ABAC table ประเมินเป็น **session user** ไม่ใช่ owner (3-month grace ถ้าถูก contact).

## 1.5 GRANT — 4 บรรทัด, USE CATALOG/SCHEMA ไม่ inherit จาก SELECT

```sql
GRANT USE CATALOG  ON CATALOG  <cat>                  TO `<account-group>`;
GRANT USE SCHEMA   ON SCHEMA   <cat>.gold             TO `<account-group>`;
GRANT SELECT       ON TABLE    <cat>.gold.cost_wide   TO `<account-group>`;
GRANT EXECUTE      ON FUNCTION <cat>.gold.fn_team_rls TO `<account-group>`;  -- ลืมบ่อยสุด
```

> **อาการลืม `GRANT EXECUTE`:** user มี SELECT, row filter มีอยู่, แต่ query **fail / คืนว่าง** เพราะ execute filter UDF ที่เฝ้า table ไม่ได้. → ใส่ 4 บรรทัดใน commit เดียวกันเสมอ.

## 1.6 The chargeback ladder (ทั้งสอง topic ลงบันไดนี้)

| Rung | คือ | กลไก | ใครจ่าย |
|---|---|---|---|
| **Showback** | รายงาน cost ต่อทีม | system.billing + tags | platform team |
| **Soft chargeback** | allocate cost (งบยังกลาง) | + Azure Export actual $ | platform team |
| **Hard chargeback** | ทีมจ่ายบิลตัวเอง | **consumer query จาก warehouse ตัวเอง** (UC GRANT) | **แต่ละทีม** |

> **published AI/BI dashboard / admin-owned warehouse รัน query บน warehouse ของ publisher** → *ทีมที่ host จ่าย DBU ให้ทุก viewer* = **showback**. ประชดที่สุดสำหรับ *cost* dashboard: platform ออกเงินให้คนอื่นมานั่งดู overspend ตัวเอง. **hard chargeback ต้องให้แต่ละทีม self-serve บน warehouse ของตัวเอง** — แต่นั่นย้อนไปติด GATE C (compute ทีมเขาต้องอ่าน gold ถึง) + ทีมต้องมี warehouse เอง.

## 1.7 The shared fallback — Artifact Factory (ถ้า GATE C ปิดถาวร / client ไม่ยอมทำอะไร)

ถ้า network เปิดไม่ได้จริงๆ **หรือ** client ไม่ยอม import/สร้างอะไรเลย → **ไม่มี live-query design ไหนรอด** (ทั้ง dashboard และ Genie). เดินทางนี้แทน:

```
Databricks Job ที่ coredata DEV (compute+storage อยู่ DEV ทั้งคู่ -> ไม่แตะ network เลย)
   -> query cost_wide filter ต่อทีม -> render per-team PDF + Excel (data baked-in)
   -> ส่ง 1 ไฟล์/ทีม ไปยัง 1 email destination/ทีม (isolation by construction)
```

- ผ่าน **R1–R5 by construction** — data ฝังในไฟล์, ไม่มี live query, ไม่พึ่ง network/metastore/binding.
- automated (R10) แก้ manual-PDF (S3), monthly cadence (R8). RLS กลายเป็น "generate 1 ไฟล์/ทีม" ไม่ใช่ UC RLS.
- **ห้าม email PDF รวมทุกทีมให้ account users เด็ดขาด** — notification destination = static email **ไม่ใช่ identity** → ไม่มี per-recipient RLS → blast ทุกทีมเห็นทุกทีม = data-leak class bug. **1 query pre-filtered/ทีม → 1 destination/ทีม เท่านั้น.**
- caps: attachment **≤ 9 MB** · **≤ 100 subscribers** · table visual **≤ 100k rows** · PDF + CSV/Excel.
- cost ~**$15/mo** (serverless job ไม่กี่นาที/เดือน) — **Sin จ่าย** (ต่างจาก D+ ที่ client จ่าย).

## 1.8 Entitlement migration — shared dependency (full detail อยู่ §3.2.4)

Topic 1 viewers = Topic 2 consumers = **population เดียว** ที่ต้องมี **Consumer access**. ทั้งสอง topic ผูกกับ **entitlement additivity trap**: ก่อน migrate, `users` system group แถม Workspace+SQL access → Consumer access ไม่ restrictive จริง + RLS-for-viewer อาจพัง. Timeline: opt-in 2026-06-15 · **auto-enable 2026-07-27** · บังคับเต็ม 2026-09-14. workspace ที่ต้อง migrate = **departmental PROD (ของ client)** ที่ Sin ไม่ได้เป็นเจ้าของ → ต้อง coordinate กับ admin ของมัน. (กลไกเต็มใน §3.2.4.)

---

# 2. TOPIC 1 — Cost-Dashboard Sharing (per-team RLS + chargeback)
### Solution D+ = target · Artifact Factory = fallback

## 2.0 ทำไม D+ กลับมาจากตาย

requirements doc (2026-07-14) เขียน D+ = DEAD เพราะตอนนั้น R5 เป็นก้อนเดียว = "ห้าม share + ไม่มี network". พอ Sarunya เปิด UC-share (2026-07-15) → R5 **แตกเป็น 2**:
- **R5-sharing** → *LIFTED* (share ได้แล้ว)
- **R5-network** → *ยังไม่รู้* (GATE C, PoC pending)

D+ ตอบโจทย์ที่ Artifact Factory ตอบไม่ได้: **K3** (เห็นใน workspace ตัวเอง) + **K6** (เขาจ่าย compute = chargeback จริง) + live/refreshable — **ถ้า** GATE C เปิด **และ** client ยอมทำ 1 action (import/สร้างเอง = Q3).

## 2.1 Recommended architecture — D+ (UC GRANT + client-side dashboard)

```
        +--------------- ONE UC METASTORE (ต้อง verify same metastore — ยัง murky) ---------------+
        |  identity = ACCOUNT groups (client-team-a...)  ·  grant เก็บใน metastore                |
        |                                                                                        |
   coredata DEV (ของ Sin = PROVIDER)                          departmental PROD (ของ client = CONSUMER)
   +--------------------------+                          +--------------------------------+
   | 5-layer pipeline          |                          |  dashboard/Genie (ของ client)   |
   | bronze->persist(MAP tags)  |  -- GRANT (ctrl-plane) ->|  import .lvdash.json หรือสร้างเอง  |
   | ->prep->summary->GOLD      |     SELECT + EXECUTE      |   (WATCH: ต้องมีคน client ทำ = Q3) |
   |                           |     + USE CAT/SCHEMA      |                                 |
   |  <cat>.gold.cost_wide     |     + catalog binding     |  data identity   = client user  |
   |   + tag_team (top-level)  |      (READ_ONLY->PROD)    |     -> RLS ยิงตาม "ตัวเขา"        |
   |   + ROW FILTER            |                          |  compute identity = warehouse    |
   |                           |                          |     ของ client (publisher/viewer)|
   |  ADLS Gen2 (DEV)          |<=== read files DIRECTLY ==|  -> "เขาจ่าย DBU" = chargeback    |
   +-----------+--------------+   credential vending      +--------------------------------+
               |                   (byte ไม่ผ่าน control plane)
               |
     [GATE C] = R5-network: departmental-PROD compute plane ต้องมี network line-of-sight -> DEV ADLS
        (storage firewall rule / private endpoint / NCC-PE / NSP+service tag)
        -- ถ้าปิด: query 403/timeout ทั้งที่ grant ถูกเป๊ะ --
```

**อ่าน diagram นี้เป็น 4 คำถาม:**

| คำถาม | คำตอบใน D+ | ตอบ requirement ข้อไหน |
|---|---|---|
| ใครถือ **data** identity ตอน query? | **client user เอง** → RLS ยิงตามตัวเขา (ต้อง publish `embed_credentials:false`) | R6 (per-team rows) |
| **compute** ของใครรัน? | **warehouse ของ client** (publisher ถ้า published / viewer ถ้า self-serve) | R7/K6 (chargeback), R1 |
| dashboard อยู่ไหน? | **workspace ของ client** | K3, R2, R4 (Sin ไม่ deploy — client import เอง = Q3) |
| ใครเข้า DEV บ้าง? | **ไม่มีใคร** — table โผล่ใน Catalog Explorer ของ *เขา* | R3 (client ไม่เป็น member ของ coredata) |

ความสวยของ D+: **R3 + R4 ผ่านเพราะ "table เดินทาง ไม่ใช่คนเดินทาง"** — dashboard เป็น object ที่ *client* สร้างในบ้านตัวเอง, Sin แค่เปิดสิทธิ์ให้ data.

> **WATCH-OUT:** "table เดินทาง" ต้องมีคนฝั่ง client รับ. R4 บอกแค่ว่า *Sin* deploy ไม่ได้ — **ไม่ได้แปลว่า client จะยอม import/สร้างให้.** D+ (ทั้งทาง A และ B) ต้องพึ่ง client action อย่างน้อย 1 ครั้ง = **Q3 ยัง OPEN**. ถ้า client ไม่ยอมแตะอะไรเลย → D+ ตาย เท่ากับ GATE C ปิด → Artifact Factory.

## 2.2 Decision tree — อะไรกำหนดว่าเดินทางไหน

```
เริ่ม: R5-sharing เปิดแล้ว (2026-07-15) [OK]
|
+- same metastore? --NO--> Delta Sharing (OpenSharing)
|        |                   WATCH: share table ที่มี row filter/mask ไม่ได้!
|        |                   => materialize table แยก "1 table/team" แล้ว share ทีละ share
|        |                   (isolation by construction, ไม่ใช่ UC RLS) -> หนัก, เลี่ยงถ้าทำได้
|       YES (ยัง murky — DEV->UAT เคยได้ "table not found")
|        |
+- client ยอมทำ 1 action (import/สร้างเอง)? --NO--> Artifact Factory (§1.7)  <- Q3, ถูกลืมบ่อย
|        |YES
+- catalog OPEN หรือ bind departmental PROD ได้? --NO--> แก้ isolation ก่อน (ไม่งั้น widget ว่างเงียบ)
|        |YES
+- [GATE C] network path (departmental-PROD compute -> DEV ADLS) เปิด?
         +- YES -----------------------------> D+  (grant -> import -> RLS per team -> เขาจ่าย)
         +- เปิดได้ (infra ตกลง)? --YES-------> D+ (หลังเปิด PE/firewall §2.5)
         +- NO / เปิดไม่ได้ -------------------> Artifact Factory (fallback §1.7)
```

**หลักการเลือก:** D+ ให้ครบ K3+K6+live แต่ **แขวนอยู่บน GATE C + Q3**. Artifact Factory ทิ้ง K3/K6/live แต่ **ผ่าน R1–R5 by construction**. เลือก D+ ก่อนเสมอ ถ้า network เปิดได้ + client ยอมรับ; Artifact Factory คือ backstop ที่ "ทำงานวันนี้ได้แน่".

## 2.3 Prerequisites — verify ตามลำดับ ถูกสุด→แพงสุด (รันก่อน design)

| # | เช็ค | คำสั่ง | ถ้า fail |
|---|---|---|---|
| 1 | **same metastore** | `SELECT current_metastore();` (รันใน **notebook** ทั้ง DEV+UAT — บน SQL warehouse จะ fail) → ต้องเท่ากัน | คนละ metastore → Delta Sharing + materialize per-team |
| 2 | **catalog isolation** | `databricks workspace-bindings get-bindings catalog <cat>` (หรือ Catalog Explorer→Workspaces tab) | `ISOLATED` → **bind departmental PROD `BINDING_TYPE_READ_ONLY`**. **อย่าใช้ `--isolation-mode OPEN`** พร่ำเพรื่อ — OPEN เปิดให้ **ทุก workspace ใน metastore** เห็น catalog cost = anti-pattern สำหรับ insurer. (default workspace catalog = ISOLATED!) |
| 3 | **storage-credential / external-location binding** | Catalog Explorer → storage credential → Workspaces tab | bind เฉพาะ DEV → PROD อ่านไม่ได้แม้ network เปิด (governance, เช็คเร็วกว่า network) |
| 4 | **network (GATE C)** | `dbutils.fs.ls('abfss://<c>@<devstore>.dfs.core.windows.net/')` จากฝั่ง consumer | 403/timeout → ติด network → §2.5 |

> **ใครทำ prereq 2–3 ได้:** bind catalog / เปลี่ยน isolation ต้องเป็น **catalog owner / metastore admin** (ฝั่ง coredata = Sin/ทีม). ส่วน serverless NCC-PE (§2.5) เป็น **two-party**: client สร้าง PE จาก NCC ของ *เขา* → **storage owner (Sin) ต้อง APPROVE**.
> **S6 Zscaler:** `az login` / Databricks CLI ยังโดน TLS interception บล็อก → prereq 1–3 หลายอันต้องเช็คผ่าน **notebook / UI** แทน CLI ไปก่อน. อย่า block ทั้ง PoC เพราะ CLI ใช้ไม่ได้.

## 2.4 Deliver dashboard → ให้ไปอยู่ workspace ของ client + the embed_credentials trap

| ทาง | วิธี | หมายเหตุ |
|---|---|---|
| **A. Export → Import** (แนะนำ) | Sin สร้าง dashboard บน `cost_wide` ที่ DEV → export `.lvdash.json` → admin ฝั่ง client import เข้า workspace ตัวเอง → repoint warehouse ของเขา → publish | `.lvdash.json` = **query + widget เท่านั้น ไม่มี data/cache** (verified — ข่าวลือ "cache ฝังในไฟล์" เท็จ) → ต้องมี grant+binding+network ถึง resolve. R4 ผ่านเพราะ *client* import — แต่พึ่ง Q3 |
| **B. client สร้างเอง** | Sin แค่ grant → client สร้าง dashboard/Genie เองบน `cost_wide` | control น้อยกว่า แต่ยืดหยุ่น, R4 ชัดกว่า — ก็ยังพึ่ง Q3 |

**publish mode — the embed_credentials trap (#1 field failure):**

| UI label | API | query รันเป็นใคร (data) | RLS |
|---|---|---|---|
| **"Share data permissions"** (**DEFAULT — อันตราย**) | `embed_credentials: true` | **publisher** | row filter ประเมินเป็น publisher → **ทุก viewer เห็น full result ของ publisher** |
| **"Individual data permissions"** | `embed_credentials: false` | **viewer** | per-viewer RLS |

> **data identity = VIEWER · compute identity = PUBLISHER.** ถ้าใครพูดว่า "ลอง AI/BI แล้ว RLS ไม่ทำงาน/ไม่ปลอดภัย" → เกือบ 100% เขา publish ด้วย default. **config bug ไม่ใช่ product flaw.** Pin `embed_credentials: false` ใน DAB, อย่าเชื่อ UI default.
> **entitlement caveat:** สำหรับกลไก published-URL viewer เปิด link ได้โดย **ไม่ต้องมี CAN USE warehouse**. แต่ **RLS ต้องมี Consumer access รึเปล่า = doc CONTESTED** (§2.6 gotcha #12 — test 1 real identity). bare account user **อ่าน workspace-bound catalog ไม่ได้ + เห็น Genie Agent ไม่ได้** → เหตุผลจริงที่ต้องให้ **Consumer access** อยู่ดี. ใน D+ consumers = departmental-PROD workspace users ที่มี Consumer access (Topic 2.2) อยู่แล้ว → ประเด็นส่วนใหญ่ moot แต่ยัง confirm ด้วย test.

## 2.5 GATE C — network path ที่ต้องเปิด (ที่ DEV ADLS, เลือก 1 ตามชนิด compute)

| consumer compute | เปิดอะไร |
|---|---|
| **Classic (VNet-injected, NPIP)** | private endpoint จาก departmental-PROD VNet → DEV storage (**ต้องทั้ง `dfs` และ `blob` sub-resource**) · **หรือ** VNet/subnet rule บน storage firewall · **หรือ** peering + firewall rule |
| **Serverless** | associate DEV storage กับ **NSP** + allow `AzureDatabricksServerless.<region>` service tag · **หรือ** private endpoint จาก **NCC** ของ departmental PROD (storage owner ต้อง **APPROVE**) |
| ทั้งคู่ | **same region strongly preferred** — region-scoping กัดเฉพาะ path แบบ NSP/service-tag (serverless); classic PE ข้าม region ได้แต่มี egress cost. ถ้า public access ปิด → เปิด **"Allow Azure trusted services"** ให้ UC access connector |

> **HARD DEADLINE 2026-06-09 (ผ่านไปแล้ว):** legacy serverless firewall (allowlist serverless *subnet-ID*) EOL → ต้องเป็น **NSP + service tag**. ถ้า DEV storage ยังพึ่ง subnet-ID = แตกเงียบตอนนี้.

**ข้อขอ infra (แคบ, มาตรฐาน — พูดให้ชัด):**
> *"ขอ private endpoint / firewall rule จาก **departmental-PROD compute plane → coredata DEV storage account**."* **นี่ไม่ใช่ data-movement exception** — ไม่มี data ตกลงที่ PROD, PROD compute อ่าน DEV storage ตรงๆ ผ่าน short-lived vended credential. **ไม่ได้ละเมิด R1/R3** (ไม่มีอะไร promote, ไม่มีใครเป็น member) — แค่เปิด packet path.

## 2.6 Chargeback granularity ของ D+ (precise)

| แบบ D+ | ใครจ่าย | granularity |
|---|---|---|
| client admin publish dashboard เดียว (embed=false) ใน departmental PROD | **warehouse ของ publisher (client admin)** จ่ายให้ทุก viewer | **department-level** (ไม่ itemize ต่อทีม) |
| แต่ละทีม self-serve บน table (UC GRANT) ด้วย **warehouse ของตัวเอง** (หรือ Power BI) | **แต่ละทีมจ่ายเอง** | **per-team จริง** ← สะอาดสุด = K6/R7 = hard chargeback |

## 2.7 Gotchas เฉพาะ Topic 1 (เรียงตามความเจ็บ; อันที่ shared อยู่ §1 แล้ว)

1. **Grant success บอกอะไรเรื่อง network ไม่ได้เลย** — verify GATE C แยก (theme ของ R5-network).
2. **catalog ISOLATED (default) → widget ว่างเงียบ** — เช็ค binding ก่อนทุกอย่าง. bind READ_ONLY เฉพาะ departmental PROD; อย่า OPEN ทั้ง metastore.
3. **publish default `embed_credentials: true` leak ทุกแถว** — pin `false`. kernel จริงของ K1.
4. **ADLS Gen2 ต้อง PE ทั้ง `dfs` และ `blob`** — ขาดตัวใดตัวนึง half-work เงียบ. PE ต้องถูก **APPROVE** โดย storage owner (PE pending หน้าตาเหมือน network fail).
5. **Delta Sharing share table ที่มี row filter/mask ไม่ได้** → ถ้าคนละ metastore ต้อง materialize per-team.
6. **[#12] RLS-tier = doc CONTESTED** — entitlements table บอก ✓ ให้ทั้ง Consumer access + bare account user; AI/BI admin matrix บอก ✗ ให้ bare account user. **อย่า assert — test 1 real identity.** confirmed: bare account user อ่าน workspace-bound catalog ไม่ได้ + เห็น Genie ไม่ได้ → เหตุผลจริงที่ต้องให้ Consumer access. ผูกกับ entitlement migration (§3.2.4).
7. **[#13] RLS test ต้องใช้ non-bypass identity** — test ในนาม admin/bypass group = false positive (§4).
8. **Lock-in note:** gold = portable Delta, row filter = rewritable SQL UDF (low lock-in) — แต่ **published-dashboard + account-user sharing model = Databricks-proprietary**. ถ้าอยากคุม lock-in: UC GRANT + Power BI ของ client เองบน UC (ตัด dashboard product ออก).

---

# 3. TOPIC 2 — Genie: Cost Monitoring + Governance Lockdown

## 3.0 The one idea ของ Topic 2

ทั้ง 2.1 และ 2.2 หมุนรอบ **spine เดียว** = `system.billing.usage`:

```
                          system.billing.usage  (ONE spine, account-level)
                          +----------------------------------------------+
   2.1  MONITORING  ------|  "ใคร/ทีมไหน กิน DBU เท่าไหร่"  (attribution)  |
                          |   = DBU x LIST price  (ไม่ใช่เงินจริง)          |
   2.2  GOVERNANCE  ------|  "Genie LLM ต่อ user"  +  "warehouse ต่อทีม"   |
                          +----------------------------------------------+
                                            |
              เงินจริง ($, incl VM+discount+tax) อยู่คนละที่ = Azure Cost Mgmt Export
```

> `system.billing.usage` ตอบ **"who used what DBU"** (attribution, list price). Azure Cost Management Export ตอบ **"เราจ่ายจริงเท่าไหร่"** (money truth, incl. classic VM). **สองตารางนี้ตั้งใจให้ต่างกัน — reconcile DBU-meter ↔ DBU-meter เท่านั้น ห้ามเทียบ DBU ↔ total.**

> **CRITICAL — network gate ก็กัด Topic 2 เหมือนกัน.** ถ้า dashboard/Genie query **cost gold table ใน DEV** จาก warehouse นอก DEV → ติด **GATE C/§1.2** เหมือน Topic 1 (นี่คือกำแพงที่ฆ่า Option E/E2 Genie Agent). แต่ถ้า query **system tables (account-level)** → ไม่แตะ ADLS ของ gold → **ไม่ติด R5**. แยกให้ออก.

---

## 3.1 — COST MONITORING: ทำไม `system.billing` ≠ Azure Portal

### 3.1.1 สอง ledger สองคำถาม

| | `system.billing.usage × list_prices` | Azure Cost Mgmt Export → ADLS |
|---|---|---|
| ตอบคำถาม | **"ใครใช้ DBU เท่าไหร่"** (attribution) | **"จ่ายจริงเท่าไหร่"** (money truth) |
| มีอะไร | DBU consumption อย่างเดียว @ **LIST** price | actual $ รวม **classic VM/disk/IP** + discount + tax |
| classic compute VM | **ไม่มี** (บิลแยกใน managed RG) | มี (meter *Virtual Machines*) |
| scope | account-level (ทุก workspace) | subscription / RG |
| ราคา | list (pre-discount, pre-tax, USD) | actual (EA/MCA/DBCU, FX, tax) |

### 3.1.2 สองช่องว่างใหญ่ที่ทำให้ไม่มีวันตรง

```
Azure Databricks total (classic cluster)
   = DBU charge  --------->  อยู่ใน system.billing  (meter "Azure Databricks")
   + VM charge   --------->  ไม่อยู่ใน system.billing  (managed RG, meter "Virtual Machines")
                            +-- 40-60% ของ cost cluster ก้อนหนึ่ง (directional — skill บอก "often")
```

1. **classic VM gap (ใหญ่สุด, ~40–60% ต่อ cluster, directional)** — VM/disk/NIC อยู่ใน **managed resource group** (tag `Vendor: Databricks`) → คนละ meter category กับ DBU และ **ไม่เคยโผล่ใน `system.billing`**. **Serverless ต่างออกไป** — VM bundle เข้า DBU price แล้ว → workload serverless ล้วน `usage × effective_list` **ใกล้ Portal มากขึ้น** (เหลือแค่ list-vs-actual + tax + latency).
2. **list vs actual** — `effective_list` = ราคา list. EA/MCA discount, DBCU drawdown, promo, FX, tax apply ตอน invoice เท่านั้น → list สูงกว่า invoice ตาม discount% (10–40%+).

> **Gotcha ในตัว Portal เอง:** filter Portal ด้วย subcategory *"Azure Databricks Regional"* จะ **ตัด VM ใน managed RG ออก** → นับผิดได้แม้อยู่ในฝั่ง Portal.

### 3.1.3 Reconciliation dataflow — สอง mode อย่าปน

```
   +------------------------- DATABRICKS SIDE (attribution) -------------------------+
   |  system.billing.usage --join--> system.billing.list_prices  (point-in-time)     |
   |       | usage_metadata.{job_id,warehouse_id,...}  = attribution                  |
   |       | custom_tags['team']                       = chargeback key (= Topic 1)   |
   |       v                                                                          |
   |   DBU$ @ LIST  แบ่งตาม team / job / warehouse / SKU / surface                     |
   +---------------------------------------+----------------------------------------+
                                           |  reconcile: DBU-meter <-> DBU-meter เท่านั้น
   +---------------------------------------v---------------- AZURE SIDE (money) -----+
   |  Cost Mgmt Export -> ADLS  (Topic 1 มี pipeline นี้อยู่แล้ว -> REUSE)             |
   |       +- DBU meter line  ("Azure Databricks")   <-- เทียบกับ DBU$ ข้างบน (ผ่าน discount)
   |       +- VM meter line   ("Virtual Machines", managed RG)  <-- บวกเพื่อ approach total
   |            allocate VM$ ต่อทีม: (ก) cluster tag propagate ไป VM  หรือ (ข) pro-rate ตาม DBU share
   +--------------------------------------------------------------------------------+
```

| โหมด | สูตร | residual |
|---|---|---|
| **Export ↔ Export** (money truth) | `Portal Databricks total = Export DBU-meter$ + Export VM-meter$` | **≈ 0** — สองก้อนมาจาก Export เดียวกัน → บวกได้ total เป๊ะ **ไม่มี residual** |
| **system.billing ↔ Export** (attribution check) | `system.billing DBU × effective_list ≈ Export DBU-meter$ ÷ (1 − discount%) + tax + latency` | residual = discount · FX · tax · latency — เทียบ DBU-line ↔ DBU-line เท่านั้น |

> **อย่าเขียน `Portal total ≈ Export-DBU$ + Export-VM$ − (tax/latency)`** — ผิด logic: ถ้าทั้งคู่มาจาก Export จะ *ไม่มี* residual ให้ลบ. residual โผล่เฉพาะตอนเอา **list price ของ system.billing** ไปเทียบ.

**Whose compute/identity:** query เป็น read-only บน system tables (account-level) — รันจาก warehouse ของทีม Sin. ต้อง enable `system.billing` โดย account admin + reader ต้องมี `SELECT` บน `usage` + `list_prices`.

### 3.1.4 Genie cost — the trap: **อย่าลบ 150**

ตั้งแต่ **2026-07-08** Genie = pay-as-you-go LLM DBU เกิน free allowance (**~150 LLM DBU/user/เดือน, pooled ข้ามทั้ง 3 surface** One+Agents+Code — ไม่ใช่ 150 ต่อ surface).

> **CRITICAL:** `system.billing.usage` มีเฉพาะ DBU ที่ **BILLED แล้ว (post-free-tier)** สำหรับ `GENIE` — 150 free DBU **ไม่โผล่**. ถ้าไปลบ 150 เองใน SQL = **double-deduct → understate cost.**

**Canonical SQL — Genie cost ต่อ user/เดือน (net, ไม่ลบ 150):**

```sql
SELECT
  date_trunc('MONTH', u.usage_date)   AS usage_month,
  u.identity_metadata.run_as          AS user_identity,   -- billed principal
  u.usage_metadata.genie.surface      AS genie_surface,   -- One / Agents / Code (informational)
  SUM(u.usage_quantity)               AS billed_dbus,      -- NET ของ free tier แล้ว — อย่าลบ 150
  SUM(u.usage_quantity * lp.pricing.effective_list.default) AS list_cost_usd
FROM system.billing.usage u
JOIN system.billing.list_prices lp
  ON  u.cloud    = lp.cloud
  AND u.sku_name = lp.sku_name                             -- JOIN, ไม่ hardcode
  AND u.usage_start_time >= lp.price_start_time
  AND (lp.price_end_time IS NULL OR u.usage_start_time < lp.price_end_time)  -- point-in-time
WHERE u.billing_origin_product = 'GENIE'                   -- ครอบทั้ง 3 surface (One/Agent/Code)
  AND u.usage_unit = 'DBU'                                 -- bill บน DBU ไม่ใช่ TOKEN/ANSWER meter
GROUP BY ALL
-- SUM() self-nets RETRACTION/RESTATEMENT correction — อย่าอ่าน raw row / อย่า COUNT
```

- **Point-in-time join = หัวใจ.** branch `IS NULL` จับราคาปัจจุบัน. ถ้าไม่ bound → **fan-out** (usage × N price rows) → cost บวมหลายเท่า. bound ด้วย `usage_start_time` (canonical) หรือ `usage_end_time` (2.1 reference) **ก็ได้ทั้งคู่** ขอแค่ consistent.
- อีก 2 error ที่เจอบ่อย: ใช้ `pricing.default` (ต้อง `pricing.effective_list.default`) และ hardcode Genie `sku_name` (ต้อง filter `billing_origin_product='GENIE'` แล้ว join SKU).

> **Honest caveat (doc-silent):** gross-vs-net behavior ไม่ระบุตรงๆ ใน official docs. "net / อย่าลบ 150" = inference จาก canonical query. **Validate ด้วย data:** ภายใต้ net model → user ที่ใช้ **DBU รวมข้ามทุก surface** < 150 ในเดือนนั้น ควร **ไม่มี GENIE row เลย** (รวมทุก surface ก่อนเทียบ 150 — pooled). ถ้าเจอ row เล็กๆ ของคน light-use → อาจเป็น gross → ทบทวน. เลข 150 มาจาก **pricing page** ไม่ใช่ Learn → verify ต่อ region.

### 3.1.5 ทำไมยังไงก็ไม่ตรง Portal เป๊ะ (irreducible) + watch-outs

`effective_list` = **list**. Azure invoice apply 4 อย่าง downstream: **discount · FX · tax · timing**. → to-the-cent = **Azure Export** เท่านั้น; system-table = layer **attribution** (per-user/per-surface/per-job).

- **latency ไม่มี SLA** → อย่า reconcile intra-day; reconcile ตอน month-close หลัง invoice finalize.
- **tag propagation:** job-level tag ไม่ auto กลายเป็น cluster tag → set ใน cluster spec + **บังคับด้วย cluster policy** (§1.3). test 1 cluster ก่อนเชื่อ chargeback.
- **retention:** system table ย้อนไกลไม่ได้ → snapshot ลง Delta เองถ้าต้องเก็บ long history.
- **ไม่มี "actual/priced cost" system view** — actual $ ต้องมาจาก Azure billing (hard limit). อยาก native actual-rate → escalate `data-architect`.

---

## 3.2 — LOCK BUSINESS USERS ลง Genie/AI-BI + Budget ต่อทีม

### 3.2.1 Mental model: 3 gate อิสระ 3 กลไก (+ gate 4 accuracy) — **+ gate 0 = reachability**

> **ก่อน 3 gate ต้องผ่าน gate 0 (network = GATE C §1.2):** ถ้า warehouse อ่าน gold table ไม่ถึง → grant/RLS/budget สวยแค่ไหนก็ query error 403.
>
> **Gate 1 ENTITLEMENT** = ได้ *surface ไหน* → Consumer access เท่านั้น (สร้าง job ไม่ได้)
> **Gate 2 UC GRANT** = เห็น *data ไหน* → SELECT + row filter (**Genie ไม่ใช่รั้ว UC ต่างหากคือรั้ว**)
> **Gate 3 BUDGET** = ใช้ได้ *เท่าไหร่* → block ได้เฉพาะ Genie LLM, อื่นๆ alert-only
> **Gate 4 ACCURACY** = คำตอบ *ถูกมั้ย* → trusted SQL function (Genie non-deterministic)

คนที่งงเพราะเอา gate มาปนกัน — คิดว่า "ให้ Consumer access แล้วปลอดภัยหมด". ไม่ใช่ — แต่ละ gate แยกกันเด็ดขาด.

### 3.2.2 Architecture — per-team setup (ตัวอย่างทีม `claims`)

```
   Entra ID --SCIM--> ACCOUNT GROUP  biz-consumers-claims   (ต้องเป็น account group)
                               |
        +-----------------------+-----------------------------------------------+
        | GATE 1 ENTITLEMENT     | GATE 2 UC GRANT          | GATE 3 BUDGET       |
        | workspace-consume ONLY | SELECT gold view เท่านั้น  | Genie LLM = BLOCK   |
        | (Consumer access)      | + EXECUTE row-filter fn  | warehouse = ALERT   |
        +-----------------------+---------------------------+---------------------+
                               |
                               v  login -> เด้งเข้า Genie One (ไม่ใช่ full workspace)
   +----------------------------------------------------------------------------+
   |  GENIE ONE  (surface เดียวที่เห็น)                                           |
   |     |  ask NL question                                                       |
   |     v                                                                        |
   |  serverless SQL warehouse  wh-claims   <-- admin-owned; group = CAN USE only |
   |     |  tag: team=claims (-> system.billing.custom_tags = chargeback)         |
   |     |  auto-stop 5-10 min + max scaling จำกัด  <-- cap ที่ config             |
   |     v                                                                        |
   |  [GATE 0] compute plane ของ wh-claims ต้อง reachable -> ADLS ของ gold  <-- §1.2|
   |     v                                                                        |
   |  UC: <cat>.gold.cost_by_team  + row filter is_account_group_member(...)       |
   |     +- เห็นเฉพาะ row ทีม claims                                               |
   +----------------------------------------------------------------------------+

   Whose compute?  warehouse ของ departmental workspace (admin-owned) — consumer ไม่จ่าย/ไม่เห็น
                   -> "platform team จ่าย compute แทนทุก viewer" = showback ยังไม่ใช่ hard chargeback (§3.2.6)
   Whose identity? viewer's identity (Genie ใช้ end-user data creds -> RLS eval ตอน query)
```

**เสาหลัก 2 อัน:**
1. **Consumer access ต้องเป็น SOLE entitlement** → login แล้วเด้งเข้า Genie One, สร้าง object ใน workspace ไม่ได้.
2. **Genie ไม่ใช่ security boundary** → user prompt Genie ให้ join table อื่นได้ทุกตัวที่เขามี `SELECT` → **รั้วจริงคือ UC grant ที่แคบ**.

### 3.2.3 Decision tree

```
business user ต้องทำอะไร?
+- แค่ถาม Genie / ดู dashboard ที่ share มา -> Consumer access (workspace-consume) ONLY  <- requirement ของ Sin
+- author dashboard / SQL editor / ad-hoc  -> Databricks SQL access (คนละ population)
+- สร้าง notebook / JOB / pipeline / model -> Workspace access  <- ห้ามให้ population นี้ (ตัวเปิด Jobs)

gold table ที่ Genie จะถาม อยู่ที่ไหนเทียบกับ warehouse? (GATE 0 — เช็คก่อน setup)
+- co-located / metastore+storage เดียวกัน + reachable -> เดินหน้า
+- คนละ env (cost table ใน DEV, warehouse ใน departmental PROD)
      -> ติด R5 wall (เหมือน Option E/E2) -> เปิด NCC-PE/NSP ก่อน หรือ fallback Artifact Factory

workspace migrate entitlement behaviour แล้วยัง?
+- ยัง (users-group ยังแถม Workspace+SQL access) -> Consumer access LEAK -> migrate เลย  <- STEP 0
+- migrate แล้ว -> Consumer access restrictive จริง -> เดินหน้า

budget: cost component ไหน?
+- Genie LLM DBU        -> Genie budget + per-user "Block usage"  = HARD BLOCK
+- serverless SQL warehouse -> general budget = ALERT only -> cap ที่ auto-stop + max scaling
+- classic compute      -> ALERT only -> cap ที่ cluster policy
```

### 3.2.4 GATE 1 — Entitlement lockdown + THE ADDITIVITY TRAP (shared dependency กับ Topic 1)

**3 entitlement เท่านั้น:**

| ความสามารถ | **Consumer access** `workspace-consume` | SQL access `databricks-sql-access` | Workspace access `workspace-access` |
|---|:--:|:--:|:--:|
| อ่าน/รัน dashboard, Genie Agent, App ที่ share | Y | Y | Y |
| query warehouse ผ่าน BI tool | Y | Y | |
| author dashboard/Genie, SQL editor | | Y | |
| **notebook, JOB, pipeline, model** | | | Y |

→ **job authoring อยู่หลัง `workspace-access`. ไม่ให้ตัวนี้ = ไม่มี Jobs surface.** Consumer-access user *"cannot create new objects in the workspace"* (doc-confirmed).

**THE TRAP — additivity + users-group migration:**
> **Entitlement เป็น additive. Consumer access lock ได้จริง ก็ต่อเมื่อมันเป็น entitlement เดียวของ user.** ก่อน migrate → `users` system group แถม Workspace+SQL access ให้ทุกคน default → consumer **inherit สิทธิ์ author** → lockdown พังเงียบ (สร้าง job ได้ทั้งที่ตั้งใจบล็อก). Doc: *"Until your workspace migrates… users with consumer access also inherit all entitlements granted to the `users` system group."*

```
2026-06-15  opt-in ได้
2026-07-27  auto-enable (ถ้ายังไม่เลือก)   <-- ใกล้แล้ว
2026-09-14  บังคับเต็ม ไม่มี opt-out
```

> **สำหรับ AIA (insurer, ตึง): migrate workspace นี้เลย (opt-in) อย่ารอ 14 ก.ย.** workspace ที่ต้อง migrate = **departmental PROD (ของ client)** ที่ Sin ไม่ได้เป็นเจ้าของ → **coordinate กับ admin ของ workspace นั้น**.
> **Pre-work ก่อนกด migrate:** repoint SCIM/Terraform → account group (หลัง migrate เขียน entitlement ของ system group จะ fail) · เลิก nest `users`/`admins` · ตั้ง SCIM ให้เก็บ clone group.
> **หลัง migrate:** `users` group = ไม่มี entitlement; สิทธิ์เดิมย้ายไป `users-clone-<TS>` → audit clone group · ยืนยัน `biz-consumers-*` **ไม่เป็นสมาชิก** clone group.

**ปิดประตูหลัง (สร้าง job):** ไม่ให้ `workspace-access` + ไม่ให้ `allow-cluster-create` · ปิด **dashboard email subscriptions** (Settings→Notifications) · entitlement enforce server-side (Jobs API reject เหมือน UI) · เช็คไม่มี PAT/SP สิทธิ์สูงปนใน group.

### 3.2.5 GATE 2 — UC grant (Genie ไม่ใช่รั้ว)

```sql
GRANT USE CATALOG  ON CATALOG  <cat>                    TO `biz-consumers-claims`;
GRANT USE SCHEMA   ON SCHEMA   <cat>.gold               TO `biz-consumers-claims`;
GRANT SELECT       ON TABLE    <cat>.gold.cost_by_team  TO `biz-consumers-claims`;
GRANT EXECUTE      ON FUNCTION <cat>.gold.fn_team_rls   TO `biz-consumers-claims`;
-- ใช้ is_account_group_member(...) — ไม่ใช่ is_member()
-- อย่า grant กว้าง (catalog / schema อื่น) — Genie จะ reach ได้หมด
```

> **BUG ที่ต้องระวัง — group ที่ RLS เช็ค ต้อง match group ที่ consumer เป็นสมาชิก.** ถ้า grant `biz-consumers-claims` แต่ filter เช็ค `client-team-claims` → RLS คืน 0 row เงียบๆ (ทุกคนเห็น empty ทั้งที่ grant ถูก). PoC = เช็ค group เดียวกับที่ grant; prod = **mapping table** (§1.4). row filter binds **TABLE ไม่ใช่ VIEW**, และ **bind ใน MAP ไม่ได้** → project `tag_team` เป็น top-level column ก่อน.
>
> **RLS-for-bare-account-user = doc-CONTESTED → test, อย่า assert** (เหมือน Topic 1 gotcha #6). moot สำหรับ population นี้ (มี Consumer access อยู่แล้ว); เหตุผล confirmed ที่ต้องมี Consumer access = **Genie/App visibility** + อ่าน workspace-bound catalog (bare account user มองไม่เห็น Genie Agent).

### 3.2.6 GATE 3 — Budget: asymmetry ที่ surprise ทุกคน

> **Per-user override + usage blocking มีเฉพาะ Genie budgets.**

| Spend type | Block ได้? |
|---|---|
| **Genie budgets** (Unity AI Gateway + tag `databricks-product: genie`) | **BLOCK** — per-user threshold + "Block usage"; near-real-time; อาจเกิน threshold นิด (in-flight) |
| Unity AI Gateway LLM อื่น (Pay-Per-Token serving, `ai_query` batch) | **ALERT only** |
| **serverless SQL warehouse / classic compute** | **ALERT only** — ไม่มี enforcement |

→ **warehouse DBU cap ที่ compute config แทน:** 1 warehouse ต่อทีม · auto-stop 5–10 นาที · max scaling/cluster จำกัด · tag ต่อทีม.

**Genie LLM budget (ตัวเดียวที่ enforce ได้จริง):** scope = **Resource type = Unity AI Gateway** + tag `databricks-product: genie` เดียว (ห้ามใส่ตัวอื่น) · **shared threshold = ALERT** (pool) + **per-user threshold + "Block usage"** (hard cap เช่น $30) + group override · resolution: ใน budget เดียว group **permissive สุดชนะ**, ข้าม budget **restrictive สุดชนะ** · compute ที่รัน Genie's SQL **บิลแยก ไม่อยู่ใน Genie budget** · free 150 DBU/user/เดือน (pooled) **เอาออกไม่ได้** ด้วย budget · reset วันที่ 1 · **SP ไม่มี free tier**.

> **Serverless usage (budget) policies = Preview** — attribute ไม่ enforce + **ไม่ครอบ serverless SQL warehouse + ไม่ครอบ Genie** → population นี้คือ slice ที่ policy ไม่ tag → **tag ที่ warehouse object เอง** (1 warehouse/team → attribution + cap).

**"Who pays" trap — ต้องพูดกับ Sarunya ก่อน build:**
> warehouse **admin-owned** → "consumer ไม่จ่าย" ฟังดูดี แต่แปลว่า **platform team จ่าย compute แทนทุก viewer** → **showback ยังไม่ใช่ hard chargeback** (ironic สำหรับ *cost* dashboard). hard chargeback = consumer query จาก **warehouse ของทีมตัวเอง** (UC GRANT ให้ account group เขา) — แต่ย้อนไปติด **GATE 0 network** + ทีมต้องมี warehouse เอง (ดู ladder §1.6). ถ้าเป้าคือ chargeback จริง (K5/K6) → คุยตั้งแต่ต้น.

### 3.2.7 GATE 4 — Answer quality (Genie ถูกมั้ย?)

Gate 1–3 ทำให้ Genie **ปลอดภัย + ถูกเงิน** — ไม่ได้ทำให้ **ถูกต้อง**. Genie = non-deterministic NL-to-SQL. คำตอบ confidently-wrong แย่กว่าไม่มี Genie.

| Lever | ทำอะไร |
|---|---|
| **Metadata (80%)** | column/table comment, ชื่อชัด, semantic layer. *"Genie quality = 80% metadata quality"* — แก้ก่อน |
| **General instructions + SQL guidelines** | NL steering ("ปีงบเริ่ม เม.ย.", "filter is_current=true เสมอ") |
| **Trusted assets** | certified SQL + **parameterized UC SQL function** = deterministic. ตัวเลข exact/auditable → ให้ Genie **call function** แทน generate SQL |
| **Benchmark questions** | eval set Q→A, วัด accuracy **ก่อน** เปิดให้ business group |
| **Scope narrow** | gold table น้อยๆ model ดีๆ > raw หลายตัว (ผูกกับ Gate 2) |

> **Honest caveat ที่ต้องบอก business:** ตัวเลข exact/auditable (chargeback total, regulatory figure) → back ด้วย **trusted SQL function** หรือ **certified dashboard** — อย่าเสนอ free-form Genie output เป็น system of record. **นี่คือ DE deliverable ไม่ใช่ของแถม.**

### 3.2.8 Build runbook + Terraform (per-team)

```
STEP 0a  GATE 0 — verify gold table reachable จาก warehouse   <- ห้ามข้าม
          test: notebook ใน consumer WS -> dbutils.fs.ls("abfss://<gold-container>@<storage>...")
                -> 403/timeout = network ปิด -> เปิด NCC-PE/NSP หรือ fallback Artifact Factory
          ถ้า gold อยู่ DEV + warehouse อยู่ departmental PROD (R1/R2/R5) -> คาดว่าติดกำแพงนี้
STEP 0b  Prerequisite — migrate workspace entitlement behaviour (opt-in)   <- ห้ามข้าม
          check: users system group ยังมี Workspace/SQL access อยู่มั้ย -> ถ้ามี = ยังไม่ปลอดภัย
          coordinate กับ admin ของ departmental workspace (Sin ไม่ได้เป็นเจ้าของ)
STEP 1  account group biz-consumers-claims (Entra->SCIM)  · verify: SELECT is_account_group_member(...) -> true
STEP 2  grant Consumer access (workspace-consume) ONLY   <- ทุกตัวอื่น false (additivity!)
STEP 3  serverless SQL warehouse wh-claims: tag team=claims · auto-stop 5-10min · max scaling จำกัด · CAN USE (ไม่ใช่ CAN MANAGE)
STEP 4  UC: GRANT SELECT gold view แคบ + EXECUTE row-filter fn (Gate 2)
          ยืนยัน group ที่ filter เช็ค = group ที่ consumer เป็นสมาชิก (ไม่งั้น 0 row เงียบ)
STEP 5  hardening: ปิด dashboard email subscription · ปิด SQL results download · ไม่มี PAT/SP ปนใน group
STEP 6  budget: Genie LLM = per-user Block usage ($30) [enforce] · warehouse tag = general budget alert [alert only -> พึ่ง STEP 3]
STEP 7  verify (checklist §4)  ·  STEP 8  monitor (spine เดียวกับ 2.1)
```

```hcl
resource "databricks_entitlements" "biz_consumers_claims" {
  group_id          = databricks_group.biz_consumers_claims.id
  workspace_consume = true    # ทุกตัวอื่นปล่อย default false — ห้าม set true
}
```

### 3.2.9 Watch-outs เฉพาะ Topic 2 (อันที่ shared อยู่ §1)

0. **GATE 0 network** — grant สำเร็จ ≠ compute อ่าน storage ถึง; gold คนละ env (R5) → 403 → NCC-PE/NSP หรือ fallback (serverless-firewall EOL 2026-06-09).
1. **additivity ทำ lockdown พังเงียบ** — migrate + audit clone group.
2. **budget block ได้เฉพาะ Genie/AI-Gateway LLM** — warehouse/classic = alert-only → cap ที่ compute config.
3. **อย่าลบ 150** ใน SQL — pre-excluded + pooled ข้าม surface.
4. ใช้ `pricing.effective_list.default` (ไม่ใช่ `pricing.default`); **join** `sku_name` (ไม่ hardcode).
5. **CAN USE ไม่ใช่ CAN MANAGE** บน warehouse.
6. **Genie ต้องมี warehouse รัน** — admin provision (consumer สร้างเองไม่ได้).
7. **budget policies (Preview) ไม่ครอบ warehouse + Genie** → tag warehouse object เอง.
8. **who-pays** — admin-owned warehouse = showback ไม่ใช่ hard chargeback.

---

# 4. Unified what-to-do-next — PoC + migration check + SQL validation

**รันตามลำดับนี้ ที่ coredata UAT (รัน departmental PROD เองไม่ได้). แต่ละ step ตอบ open item ตัวใดตัวหนึ่ง.**

### Step A — Prereq sweep (ถูกสุด→แพงสุด, notebook/UI เพราะ Zscaler บล็อก CLI)
```sql
-- A1 same metastore? (notebook ทั้ง DEV + UAT — บน SQL warehouse fail)
SELECT current_metastore();                    -- ต้องเท่ากัน (Open item: เคยได้ "table not found")
```
```python
# A2 network triage (GATE C / GATE 0) — bypass UC, แยก network ออกจาก governance
dbutils.fs.ls("abfss://<container>@<devstorage>.dfs.core.windows.net/")
# 403/timeout -> GATE C ปิด (§2.5) ; อ่านได้ -> network OK
```
- A3 catalog isolation → bind departmental PROD `BINDING_TYPE_READ_ONLY` (อย่า OPEN ทั้ง metastore).
- A4 storage-credential/external-location binding → ผูกเฉพาะ DEV มั้ย.

### Step B — Migration check (STEP 0b, ทั้งสอง topic พึ่ง)
- เช็ค `users` system group ยังมี Workspace/SQL access มั้ย → ถ้ามี = ยังไม่ migrate = Consumer access ไม่ restrictive.
- workspace = **departmental PROD ของ client** → coordinate กับ admin นั้น. auto-enable **2026-07-27** → รีบ opt-in.

### Step C — SQL validation (grant + RLS, decisive test)
```sql
-- C1 grant 4 บรรทัด (§1.5) ที่ DEV ให้ test user
-- C2 decisive test — รันที่ UAT (ฝั่ง consumer):
SELECT * FROM <cat>.gold.cost_wide LIMIT 10;
```
อ่านผล: เห็นแถวที่ filter ตัดถูก = governance+network+RLS ครบ · 403 = GATE C · ว่าง 0 แถว = row filter false/mapping · not-found = metastore/isolation/grant.

> **RLS test trap — อย่า test ด้วย identity ใน bypass group** (`cost-platform-admins`) → คืน TRUE ทุกแถว = false positive. test ด้วย identity **นอก bypass group** map ไปทีมเดียว → assert เห็นแค่แถวทีมนั้น. แล้ว negative-test identity ที่ไม่อยู่ทีมไหน → 0 แถว (ไม่ใช่ error, ไม่ใช่เห็นหมด).

### Step D — Decisive publish/Genie test (1 real identity)
- **Topic 1:** publish dashboard **Individual data permissions** → 1 real consumer identity (ไม่ใช่ member workspace) เปิด link → assert (a) load, (b) เห็นแค่แถวตัวเอง, (c) ไม่มี sidebar/workspace surface.
- **Topic 2 verify checklist:**
  - [ ] notebook ใน consumer WS → `dbutils.fs.ls` บน gold storage → อ่านได้ (ไม่ 403)
  - [ ] login test user → เด้งเข้า Genie One (ไม่ใช่ full workspace)
  - [ ] กด "สร้าง job/notebook/cluster" → ไม่มี surface / block
  - [ ] เปิด SQL editor → ไม่มีสิทธิ์ · ดู warehouse list → มองไม่เห็น
  - [ ] ถาม Genie cost ทีมตัวเอง → เห็นเฉพาะ row ทีม (ยืนยันไม่ใช่ empty จาก group mismatch)
  - [ ] prompt Genie ให้ query table นอก grant → empty / no access
  - [ ] (ถ้าเทสได้) Genie budget: spam จน >$30 → โดนหยุด

### Step E — Validate Genie cost SQL (net model)
- รัน canonical SQL (§3.1.4) → assert user ที่ใช้ DBU รวมทุก surface < 150 → **ไม่มี GENIE row** (ยืนยัน net, ไม่ลบ 150). ถ้าเจอ row เล็กของ light-user → อาจ gross → ทบทวน.

> **UAT ผ่าน ≠ PROD ผ่าน.** coredata UAT↔DEV network ง่ายกว่า departmental PROD↔DEV มาก. UAT พิสูจน์ **กลไก** (grant+RLS+binding+import+publish-mode+Genie-lockdown) ได้จริง; แต่ **GATE C ของ departmental PROD ต้อง confirm กับ infra แยก** — นี่คือ single most-important open item.

---

# 5. Honest OPEN items (merged — ต้องได้คำตอบก่อน commit)

| # | Open item | Topic | ทำไม decisive |
|---|---|---|---|
| **R5-network / GATE C** | departmental-PROD compute → DEV ADLS เปิดได้มั้ย? | 1 + 2 | **make-or-break ของทั้งสอง.** ปิด = ตกไป Artifact Factory ทั้งคู่. PoC/infra confirm pending |
| **same metastore?** | เดิมว่า "same" แต่ DEV→UAT เคย "table not found" → murky | 1 + 2 | คนละ metastore = Delta Sharing + materialize (RLS ไม่ travel) |
| **Q3 — client ยอมทำ 1 action** | import `.lvdash.json` / สร้าง object เอง | 1 | R4 บอกแค่ *Sin* deploy ไม่ได้; ถ้า client ไม่แตะ → D+ ตายแม้ network เปิด |
| **consumer compute ชนิดไหน** | classic (VNet) vs serverless | 1 + 2 | กำหนด path เป็น VNet-rule/PE vs NCC/NSP (§2.5) |
| **workspace migrated แล้วยัง** | departmental-PROD (Sin ไม่ได้เป็นเจ้าของ) | 1 + 2 | RLS-for-viewer + lockdown พังถ้าไม่ทำ; auto 2026-07-27 |
| **RLS group = grant group?** | latent zero-row bug ถ้าใช้คนละชื่อ | 2 | ยืนยัน consumer เป็นสมาชิก group ที่ filter เช็ค; prod → mapping table |
| **RLS enforce บน bare account user** | doc-CONTESTED (docs ขัดกัน) | 1 + 2 | test in-tenant; moot ถ้ามี Consumer access — แต่ยัง confirm |
| **net vs gross ของ Genie usage** | doc-silent inference | 2 | validate: user <150 DBU (pooled) ควรไม่มี GENIE row |
| **เลข 150 free LLM DBU** | จาก pricing page ไม่ใช่ Learn | 2 | verify ต่อ region |
| **team count 5 vs 30** | จุดตัดไป ABAC policy | 1 + 2 | 30 → ABAC คุ้มกว่า bind ทีละ table (มี session-user breaking change) |
| **VM cost allocation ต่อทีม** | cluster-tag propagate vs pro-rate ตาม DBU | 2 | test tag propagation 1 cluster ก่อนเชื่อ chargeback |
| **actual-rate DBU native** | ไม่มี — hard limit | 2 | escalate `data-architect` / ingest Azure billing |
| **chargeback จริง vs showback** | admin-owned warehouse = showback | 1 + 2 | hard chargeback (K5/K6) → consumer's own warehouse + GATE C |
| **who owns grant lifecycle** | onboarding/offboarding = INSERT mapping row + group membership | 1 + 2 | operating model ของ chargeback |

**Escalate:** NCC/NSP/PrivateLink + Entra/SCIM plumbing + Cost-Export IAM → `azure-expert` · regulatory sign-off (chargeback เป็น official number) → `governance-consultant` · actual-rate native / storage layout / vendor-neutral table format → `data-architect`.

---

# 6. 4 things Sin should be able to teach back

1. **Grant ≠ Reachability (2 planes, credential vending).** UC grant = control-plane decision; byte จริงวิ่งจาก consumer compute plane → provider ADLS ตรงๆ ผ่าน short-lived vended credential. เพราะฉะนั้น A+B ผ่าน แต่ C ปิด = 403/timeout. อธิบายได้ว่านี่คือกำแพงเดียวที่ฆ่าทั้ง D+ (Topic 1) และ Genie Agent (Option E/E2, Topic 2), และ triage 403-vs-empty-vs-notfound.

2. **"Table เดินทาง ไม่ใช่คนเดินทาง" + data-vs-compute identity.** D+ เปิดสิทธิ์ให้ table โผล่ใน workspace ของ client (K3), client query ด้วย warehouse ตัวเอง (K6/chargeback), RLS ยิงต่อทีม, ไม่มีใครเข้า DEV (R3). กุญแจ RLS: `is_account_group_member()` (ไม่ใช่ `is_member()`) + mapping table + top-level column + `embed_credentials:false` (data identity = viewer, compute identity = publisher).

3. **สอง ledger: `system.billing` (DBU@list, attribution) ≠ Azure Export (money truth).** reconcile DBU-meter ↔ DBU-meter เท่านั้น; classic VM gap ~40–60% อยู่ใน managed RG ไม่โผล่ใน system.billing; และ **Genie cost อย่าลบ 150** (net แล้ว, pooled ข้าม 3 surface).

4. **Genie lockdown = 3 gate อิสระ + additivity trap.** Consumer access ต้องเป็น **sole entitlement** (Genie ไม่ใช่รั้ว — UC คือรั้ว); budget block ได้ **เฉพาะ Genie LLM** (warehouse = alert-only → cap ที่ config); และ **entitlement additivity** ทำ lockdown พังเงียบก่อน migrate (auto 2026-07-27, workspace = departmental PROD ที่ต้อง coordinate). อธิบาย showback-vs-hard-chargeback ได้ (admin-owned warehouse = platform จ่ายแทน = ยังไม่ chargeback).

---

## 7. Reference files (absolute)
- `/Users/wasin/Documents/Projects/Agent/company/aia/_inbox/solution-d-plus-resurrection-20260718.md`
- `/Users/wasin/Documents/Projects/Agent/company/aia/_inbox/requirements-and-concerns-20260714.md` (R1–R10, Option E/E2 = DEAD ที่ R5)
- `/Users/wasin/Documents/Projects/Agent/company/aia/_inbox/topic-2.1-cost-reconciliation-20260717.md` · `.../topic-2.2-consumer-access-genie-budget-20260717.md` · `.../topic-2.2-setup-runbook-20260717.md`
- Skills: `/Users/wasin/Documents/Projects/Agent/company/aia/skills/databricks-uc-governance-sharing/SKILL.md` · `.../databricks-serverless-networking/SKILL.md` · `.../databricks-cost-optimization/SKILL.md` · `.../databricks-genie-governance/SKILL.md`

---

### สรุป 1 บรรทัดให้ Sarunya
> Topic 1 (share cost dashboard) กับ Topic 2 (lock business users ลง Genie + cost monitoring) = **application สองตัวของ spine เดียว** (per-team tag + UC RLS + serverless warehouse), viewer กลุ่มเดียวกัน, และตายด้วยกำแพงเดียวกันคือ **network path departmental-PROD→DEV storage**. เปิด GATE C ได้ + client ยอมทำ 1 action + same metastore + migrate entitlement → เดินหน้า D+ (client เห็น cost ตัวเองใน workspace ตัวเอง, query ด้วย warehouse ตัวเอง = chargeback จริง) + Genie-on-cost lockdown; ขาดข้อใดแบบแก้ไม่ได้ → **Artifact Factory per-team PDF+Excel ที่ทำงานได้วันนี้** สำหรับทั้งสอง topic.