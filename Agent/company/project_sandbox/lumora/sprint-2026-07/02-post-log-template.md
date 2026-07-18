# Lumora Sprint — Per-Post Log Template

> **สถานะ:** ops template สำหรับ 90-day sprint (backend **frozen** ต่อ ADR-0001 — zero new code).
> เครื่องมือ = **spreadsheet หรือ SQLite ไฟล์เดียว** (`lumora_sprint.db`). เป็นทั้ง (1) ops tracker + (2) **training data** สำหรับ backend เฟสหลัง.
> **หลักสำคัญ:** column ตั้งชื่อให้ map 1:1 เข้า Postgres `posts` + `performance` (Supabase) ตอน Phase 2 → ingest = column-map ตรงๆ ไม่ต้อง rework. `brand_id` มีตั้งแต่วันแรก (discipline จาก 04_tech_backend §brand_id).
> ทุกโพสต์ต้อง log — combo (C×T×M), hook, URL, views, GMV.

---

## 1. CSV header (copy บรรทัดแรกลง spreadsheet)

```csv
post_id,date,content_pillar,theme,media,hook_type,url,views_24h,views_7d,likes,comments,shares,saves,follows_delta,gmv,notes
```

> `combo C/T/M` = 3 คอลัมน์ `content_pillar,theme,media` (แยกตาม 3-axis tagging ของ framework → filter/สรุปต่อ axis ได้; ตรงกับ `posts.content_pillar/theme/media_format` ใน DB). อยากได้ combo string ก็ concat: `content_pillar || "×" || theme || "×" || media`.

### ตัวอย่างแถว (จาก batch วัน 1–2)

```csv
L1-D01,2026-07-18,C2,Cosmic,M11,curiosity-choice,https://tiktok.com/@mumeesang/video/xxx,,,,,,,,0,launch card 3-choice
L1-D02,2026-07-18,C1,Future-tech,M1,statement,https://tiktok.com/@mumeesang/video/yyy,,,,,,,,0,ท่านท้าวเวสฯ cyber; homage-watch 24h
```

---

## 2. Column definitions

| Column | Type | คำอธิบาย | map → DB |
|---|---|---|---|
| `post_id` | TEXT | ID อ่านได้เอง `L{week}-D{day2หลัก}` เช่น `L1-D01`, `L4-D28` (stable, ไม่ใช่ UUID เพื่อกรอกมือง่าย) | `posts.post_id` (แปลงเป็น UUID ตอน ingest, เก็บ `L#-D#` เป็น external ref) |
| `date` | DATE | วันโพสต์จริง `YYYY-MM-DD` | `posts.posted_at` (date part) |
| `content_pillar` | TEXT | `C1`–`C10` (C2 oracle / C1 เทพ / C6 art / C9 comedy) | `posts.content_pillar` |
| `theme` | TEXT | theme cluster: `Cosmic` / `Future-tech` / `Historical` / `Pastoral` / `Contemporary` | `posts.theme` |
| `media` | TEXT | `M1`–`M12` (M1 single / M2 carousel / M11 interactive / M6 voice reel) | `posts.media_format` |
| `hook_type` | TEXT | ประเภท hook (fixed-tag, ดู §3) — ไม่ใช่ข้อความ hook แต่เป็น *ชนิด* เพื่อวิเคราะห์ | (ใหม่; เก็บใน `posts` note หรือ column เสริม) |
| `url` | TEXT | ลิงก์โพสต์ TikTok/IG/YT | `posts.asset_url` / listing url |
| `views_24h` | INT | ยอด view 24 ชม.แรก (ตัดสิน hook/cold-start) | `performance.views` (snapshot@24h) |
| `views_7d` | INT | ยอด view 7 วัน (ตัดสิน long-tail/algo pickup) | `performance.views` (snapshot@7d) |
| `likes` | INT | ยอด like (วัดที่ 7 วัน) | `performance.likes` |
| `comments` | INT | ยอด comment (proxy engagement/ชุมชน) | (`performance` เพิ่ม column) |
| `shares` | INT | ยอด share (proxy virality/reach) | `performance.shares` |
| `saves` | INT | ยอด save (**signal แรงสุดของ oracle/wallpaper** = intent เก็บไว้) | `performance.saves` |
| `follows_delta` | INT | follower ที่ได้จากโพสต์นี้ (ประมาณจาก analytics "follows from this video") | (derive จาก account growth) |
| `gmv` | DECIMAL | ยอดขาย affiliate/digital product ที่ผูกโพสต์นี้ (บาท) | `performance.revenue` |
| `notes` | TEXT | อิสระ: homage-watch, AI-label ok, trend ที่ขี่, สมมติฐานที่ทดสอบ | `posts.caption`/note |

**ที่ track ไม่ได้ก็เว้นว่าง** (SQLite/CSV = NULL). อย่ากรอกมั่ว — ข้อมูลว่างดีกว่าข้อมูลปลอมสำหรับ training.

---

## 3. `hook_type` fixed-tags (เลือก 1 — วิเคราะห์ได้ว่า hook แบบไหน stop-scroll)

| tag | ความหมาย | ตัวอย่างจาก batch |
|---|---|---|
| `curiosity-choice` | ชวนเลือก/ทายก่อนเฉลย | "เลือกใบที่ตาไปหยุดก่อน" (D1) |
| `statement` | ประโยคยืนยัน/ทัศนะ | "ท่านในปี 2087 ก็ยังสง่า" (D2) |
| `relatable-callout` | "ประเภทคนที่..." (self-deprecating) | "ประเภทคนขอครบใน 1 ธูป" (D4) |
| `question` | ตั้งคำถามตรงกับผู้ชม | "วันนี้มีอะไรที่ควรวางลงไหม?" (D5) |
| `list-promise` | สัญญาว่ามีของให้เลือก N อย่าง | "5 วอลเปเปอร์...เลื่อนเลย" (D6) |
| `milestone` | หมุด/โอกาส/ครบรอบ | "ครบ 7 วันแรก" (D7) · "วันพระนี้" (D29) |
| `other` | อื่นๆ (fixed bucket, ไม่ free text) | — |

> เลียนแบบ pattern `reject_reasons` ใน `001_init.sql` — hook_type เป็น **fixed-tag lookup ไม่ใช่ free text** → group-by วิเคราะห์ได้ตรงๆ.

---

## 4. SQLite schema (`lumora_sprint.db`)

> ตาม Lumora DB conventions (`db/migrations/001_init.sql`): `brand_id` ทุกตาราง · posts/performance แยกหน้าที่ · fixed-tag lookup (hook_types) แทน free text · `funnel_stage` CHECK · timestamps.
> SQLite ไม่มี `gen_random_uuid()`/`UUID`/`TIMESTAMPTZ` → ใช้ `TEXT` id (`L#-D#`) + `TEXT` ISO-8601 datetime. Postgres seam: ชื่อ column ตรงกับ `posts`+`performance` เพื่อ ingest ทีหลัง.

```sql
-- lumora_sprint.db — manual per-post log (Phase-1 sprint, backend frozen per ADR-0001)
-- Maps 1:1 onto Supabase posts + performance for later ingest. brand_id everywhere.
PRAGMA foreign_keys = ON;

-- ── fixed-tag lookup (hook types) — pattern จาก reject_reasons ──────────
CREATE TABLE hook_types (
  hook_type    TEXT PRIMARY KEY,
  description  TEXT
);
INSERT INTO hook_types (hook_type, description) VALUES
  ('curiosity-choice',  'ชวนเลือก/ทายก่อนเฉลย'),
  ('statement',         'ประโยคยืนยัน/ทัศนะ'),
  ('relatable-callout', 'ประเภทคนที่... (self-deprecating)'),
  ('question',          'ตั้งคำถามตรงกับผู้ชม'),
  ('list-promise',      'สัญญาว่ามีของให้เลือก N อย่าง'),
  ('milestone',         'หมุด/โอกาส/ครบรอบ'),
  ('other',             'อื่นๆ (fixed bucket, not free text)');

-- ── the log (one row per published post) ───────────────────────────────
CREATE TABLE post_log (
  post_id         TEXT PRIMARY KEY,               -- 'L1-D01' (stable, hand-entered)
  brand_id        TEXT NOT NULL DEFAULT 'own',    -- brand_id discipline (Phase1 own → Phase2 client)
  account_handle  TEXT NOT NULL DEFAULT '@มูมีแสง',
  posted_at       TEXT NOT NULL,                  -- ISO-8601 'YYYY-MM-DD' or full datetime

  -- 3-axis tagging (→ posts.content_pillar/theme/media_format)
  content_pillar  TEXT NOT NULL,                  -- C1..C10
  theme           TEXT NOT NULL,                  -- Cosmic / Future-tech / Historical / Pastoral / Contemporary
  media           TEXT NOT NULL,                  -- M1..M12
  jtbd            TEXT,                            -- optional job-to-be-done
  funnel_stage    TEXT DEFAULT 'Hub',             -- Hero | Hub | Hygiene
  hook_type       TEXT REFERENCES hook_types(hook_type),  -- fixed tag only
  ai_labeled      INTEGER NOT NULL DEFAULT 1,      -- 0/1: เปิด AI-label toggle แล้วหรือยัง (default yes)
  url             TEXT,

  -- performance snapshots (→ performance.*)
  views_24h       INTEGER,
  views_7d        INTEGER,
  likes           INTEGER,
  comments        INTEGER,
  shares          INTEGER,
  saves           INTEGER,
  follows_delta   INTEGER,
  gmv             REAL DEFAULT 0,                  -- บาท (→ performance.revenue)

  notes           TEXT,
  created_at      TEXT DEFAULT (datetime('now')),
  updated_at      TEXT DEFAULT (datetime('now')),

  CHECK (funnel_stage IN ('Hero','Hub','Hygiene')),
  CHECK (ai_labeled IN (0,1))
);

CREATE INDEX idx_postlog_pillar  ON post_log(brand_id, content_pillar);
CREATE INDEX idx_postlog_date    ON post_log(brand_id, posted_at);
CREATE INDEX idx_postlog_combo   ON post_log(content_pillar, theme, media);

-- derived engagement view (save-rate = signal แรงสุดของ oracle/wallpaper)
CREATE VIEW v_post_scores AS
SELECT
  post_id, posted_at, content_pillar, theme, media, hook_type, funnel_stage,
  views_7d, saves, follows_delta, gmv,
  CASE WHEN views_7d > 0 THEN ROUND(1.0*saves        /views_7d, 4) END AS save_rate,
  CASE WHEN views_7d > 0 THEN ROUND(1.0*follows_delta/views_7d, 4) END AS follow_rate,
  CASE WHEN views_24h > 0 THEN ROUND(1.0*views_7d    /views_24h, 2) END AS tail_multiple
FROM post_log;
```

### insert ตัวอย่าง

```sql
INSERT INTO post_log (post_id, posted_at, content_pillar, theme, media, funnel_stage, hook_type, url, notes)
VALUES ('L1-D01','2026-07-18','C2','Cosmic','M11','Hub','curiosity-choice',
        'https://tiktok.com/@mumeesang/video/xxx','launch card 3-choice');

-- อัปเดต metrics ตอนครบ 24h / 7d
UPDATE post_log SET views_24h=8200, updated_at=datetime('now') WHERE post_id='L1-D01';
UPDATE post_log SET views_7d=15400, likes=1120, comments=240, shares=95, saves=980, follows_delta=63, updated_at=datetime('now') WHERE post_id='L1-D01';
```

---

## 5. Weekly review ritual (10 นาที · ทุกวันปิดสัปดาห์ = day 7/14/21/28)

> เป้า: อ่านสัญญาณ → ปรับ combo สัปดาห์หน้า (feed กลับเข้า aesthetic-week + pillar mix ของ batch). ไม่เกิน 10 นาที.

**Step 1 — Top performer (2 นาที):** รันคิวรี → โพสต์ที่ดีสุด 1–2 ชิ้น
```sql
SELECT post_id, content_pillar, theme, media, hook_type, views_7d, save_rate, follow_rate, gmv
FROM v_post_scores
WHERE posted_at >= date('now','-7 day')
ORDER BY views_7d DESC, save_rate DESC
LIMIT 3;
```
→ **double down:** combo/hook/aesthetic ที่ชนะ = ทำซ้ำ (variation) สัปดาห์หน้า.

**Step 2 — Bottom performer (2 นาที):**
```sql
SELECT post_id, content_pillar, theme, media, hook_type, views_24h, views_7d, save_rate
FROM v_post_scores
WHERE posted_at >= date('now','-7 day')
ORDER BY views_7d ASC
LIMIT 2;
```
→ **diagnose:** hook อ่อน? (views_24h ต่ำ) · aesthetic ไม่โดน? · combo ล้า? → ปรับหรือพัก combo นั้น (mark `notes='fatigued'`).

**Step 3 — Pillar × hook rollup (3 นาที):** pillar/hook ไหนคุ้มสุด
```sql
SELECT content_pillar, hook_type,
       COUNT(*) n, ROUND(AVG(views_7d)) avg_views,
       ROUND(AVG(save_rate),4) avg_save_rate, ROUND(SUM(gmv)) total_gmv
FROM v_post_scores
WHERE posted_at >= date('now','-28 day')
GROUP BY content_pillar, hook_type
ORDER BY avg_views DESC;
```
→ ปรับ **combo spread** สัปดาห์หน้า: เพิ่มน้ำหนัก pillar/hook ที่ avg_views + save_rate สูง, ลดที่แป้ก.

**Step 4 — Gate progress + compliance (3 นาที):**
```sql
-- ใกล้ gate แค่ไหน: best-post views + follower รวม
SELECT MAX(views_7d) best_post_views, SUM(follows_delta) followers_gained
FROM post_log WHERE posted_at >= '2026-07-18';   -- นับจาก day 1
```
→ เทียบ **gate = 1 post ≥50K views หรือ 1,000 followers ใน day 90**. On-track ไหม?
→ เช็ค `ai_labeled=1` ครบทุกโพสต์ · ดู reach ของ C1 sacred imagery ว่ามีเสียงติงเรื่อง homage ไหม (ถ้ามี → ดึงออก) · ดูว่ามีสัญญาณ AI-suppression (labeled posts reach ตกผิดปกติ) → เพิ่มสัดส่วน C9 voice/comedy (human layer).

**บันทึกผล 1 บรรทัด/สัปดาห์** ใน notes หรือไฟล์แยก: *"W{n}: top=Lx-Dyy ({combo}), bottom=..., ปรับ = {อะไร}สัปดาห์หน้า"* → เป็น decision trail + training signal.

---

## 6. Notes

- **อย่า over-engineer** — SQLite ไฟล์เดียว หรือ Google Sheet ก็พอ; schema นี้คือ *ceiling* ไม่ใช่ requirement. กรอก `post_id,date,content_pillar,theme,media,hook_type,url,views_7d,saves,follows_delta,gmv` ก็วิเคราะห์ได้แล้ว.
- **1 โพสต์ = 1 แถว.** metrics อัปเดต 2 จุด: ครบ 24 ชม. (`views_24h`) และครบ 7 วัน (ที่เหลือ).
- **Phase-2 seam:** เมื่อ backend un-park (≥100 posts + manual step >2 ชม./สัปดาห์ ต่อ ADR-0001) → `post_log` → `INSERT ... SELECT` เข้า Supabase `posts`+`performance`; `brand_id='own'` map ตรง, `L#-D#` เก็บเป็น external ref.
