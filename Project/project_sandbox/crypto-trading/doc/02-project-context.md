# Project Context — Crypto Trading Decision-Support Tool

> Handoff document. Generated from a claude.ai design session on 2026-06-07.
> Purpose: bootstrap a Claude Code (local / VS Code) session with full context,
> since memory/context does NOT carry over between claude.ai and Claude Code.
> วิธีใช้: ให้ Claude Code อ่านไฟล์นี้ก่อน แล้วเริ่มจากหัวข้อ "Open Decisions" / "Next Actions"

---

## 1. What we're building (one paragraph)

เครื่องมือ **decision-support สำหรับเทรด crypto** (ออกแบบให้ generalize ไปหุ้น/options ได้)
มองในมุม **builder/innovator** ไม่ใช่ data-engineering/pipeline project — **ไม่เกี่ยวกับงาน The1
และไม่มี data pipeline (Beam/BigQuery) ใดๆ**. แกนหลัก: เอา historical candle ของแต่ละ timeframe
มาวิเคราะห์ pattern/predictive (Elliott หรือไม่ก็ได้) แล้วได้ออกมาเป็นสัญญาณ **short/long**
พร้อมเหตุผล + invalidation. ไม่ใช่เครื่องทำนาย — เป็นตัว systematize วินัย + รวม context + ตัดอารมณ์.

---

## 2. Core mental model (สำคัญสุด — กันสับสน)

### "Indicator" = 2 อย่างคนละเรื่อง
1. **Live signal indicator (Pine บน TradingView)** — คำนวณ short/long สดบนชาร์ต real-time,
   นั่งข้าง RSI ได้, self-contained, เห็นได้แค่ price/volume. ทำ Elliott/ML ลึกไม่ได้.
2. **Analytical engine (agent บน local)** — อ่าน candle history, วิเคราะห์หลายทฤษฎี,
   สรุป daily/weekly/monthly, พ่นแผน short/long + เหตุผล. รวยกว่า แต่เป็น offline ไม่ใช่ indicator บนชาร์ต.

→ **ต้องการทั้งสองตัว ทำคนละหน้าที่. อย่าฝืนทำ #2 ให้เป็น TradingView indicator** (Pine ดึง API ของ engine ไม่ได้).

### Build-time vs Runtime
- **Claude Code + agents/skills/KB** = ใช้ตอน *build time* เท่านั้น — ช่วย *เขียน* engine.
- **Engine (Step 1)** = ตัวที่รันจริงตอน *runtime*. ชั้น deterministic เป็น code ธรรมดา;
  ชั้น interpretive จะ **call LLM ผ่าน Anthropic API ในสคริปต์เอง** (ไม่ใช่ Claude Code).

### Engine = 2 ชั้น
- **Deterministic (code):** fetch/refresh history, คำนวณ RSI/ATR/MA, detect candle pattern,
  หา pivot/swing. แม่น ถูก ไม่พึ่ง LLM.
- **Interpretive (LLM agent):** รับ *digest ที่ย่อแล้ว* (ไม่ใช่ candle ดิบ) ไปอ่าน Elliott,
  สังเคราะห์หลายทฤษฎี, เขียนแผน. → ประหยัด token, เร็ว, reproducible.

---

## 3. Architecture (Hybrid = option B + C)

```
Data sources           Signal layer (Python)        Decision
-----------            ---------------------        --------
flow & positioning  →                            →  Dashboard (web)
macro               →   ingest → features →       →  TradingView
on-chain            →   regime + confluence          (Pine + alerts)
price / volume      →

                    Claude Code = builds & maintains every layer (build-time only)
```

**กฎเหล็ก:** สมองหนักอยู่ local; TradingView ทำหน้าที่ "ตา + ที่ผสมกับ RSI".
สิ่งที่ข้ามไป TV คือ *ผลลัพธ์* (เส้น/โซน/bias) ไม่ใช่ตัว engine.

### สะพานเชื่อม engine → TradingView (เรียงง่าย→ยาก)
1. **Manual review** — engine พ่นแผน, เปิด TV ดู price+RSI ควบ dashboard, ตัดสินใจเอง. (เริ่มจากนี่)
2. **Levels-as-Pine** — engine คำนวณ levels/zones/bias → generate Pine snippet ที่ hardcode ค่าล่าสุด → paste ลง TV.
3. **Webhook action leg** — alert TV ยิง outbound กลับมาที่ service. (ขั้นสูง ค่อยทำ)

---

## 4. Workflow (2 steps)

- **Step 1 — `analyze` (local, scheduled/manual):** refresh history → code คำนวณ feature →
  agent สังเคราะห์ → emit artifact (JSON + markdown summary) = regime, bias, levels, invalidation,
  confidence, สรุป daily/weekly/monthly.
- **Step 2 — review + act (human + TV):** อ่าน artifact → เปิด TV ดู price action + RSI +
  (เลือก) เส้นจาก engine ที่ paste เป็น Pine → ตัดสินใจ + วางแผน.

---

## 5. Locked constraints / decisions

- **Pine Script** รันเฉพาะใน TradingView, ยิง HTTP/ดึง external API ไม่ได้, รับ external series เข้ามาไม่ได้.
  request.*() ดึงได้เฉพาะ symbol ที่มีบน TV. Webhook เป็น outbound ขาเดียว (สำหรับ alert).
- **"TradingView plugin บน VS Code" ที่ execute/backtest ได้จริง ไม่มี** — มีแค่ extension syntax highlight.
- **Ingest history ทีเดียวเก็บ local** (ไฟล์ / DuckDB) — อย่า call API รัวๆ ทุกครั้ง.
  (หมายเหตุ: นี่แค่ "เซฟ candle ลงไฟล์" ไม่ใช่การสร้าง pipeline.)
- **Elliott Wave = ชิ้นที่เชื่อถือน้อยสุด + auto-compute ยากสุด** → weight ต่ำใน signals[],
  ใช้เป็น "มุมมองเสริม" เท่านั้น. ตัวขับหลัก = structure / MA / levels (ฝั่ง deterministic).
- ตลาดปัจจุบันขับด้วย **macro / ETF flow > technical** (ดู §8).

---

## 6. Step 1 output contract (LOCKED — engine ต้อง emit แบบนี้)

Symbol-agnostic. เปลี่ยน `symbol` / `asset_class` แล้วใช้ซ้ำกับหุ้น/options ได้.
ดีไซน์ให้ **โปร่งใส** — เห็นว่าแต่ละ signal โหวตอะไร + weight เท่าไหร่ (ไม่ใช่กล่องดำ).

```json
{
  "meta": {
    "symbol": "BTCUSDT",
    "asset_class": "crypto",
    "timeframes": ["1h", "4h", "1d"],
    "generated_at": "2026-06-07T12:00:00Z",
    "data_window": { "from": "2024-01-01", "to": "2026-06-07" },
    "engine_version": "0.1.0"
  },
  "regime": {
    "trend": "down",
    "structure": "lower-highs / lower-lows",
    "note": "ใต้ MA 20/50/100 ทุกตัว, oversold"
  },
  "bias": {
    "direction": "short",
    "conviction": "medium",
    "timeframe_alignment": { "1h": "neutral", "4h": "short", "1d": "short" }
  },
  "levels": {
    "support": [60000, 55000, 48000],
    "resistance": [65000, 68000],
    "invalidation": { "price": 55000, "rule": "weekly close above flips bias" }
  },
  "elliott": {
    "tf_1d": {
      "degree": "Primary",
      "current_wave": "C",
      "structure": "ABC correction (down)",
      "sub_wave": "3 of C",
      "implied_direction": "down",
      "primary_count": "wave C — ลงต่อ",
      "alt_count": "wave 4 ของ impulse ใหญ่ — เด้งขึ้น",
      "invalidation": 70000,
      "confidence": "medium"
    },
    "tf_4h": {
      "degree": "Minor",
      "current_wave": "3 of C",
      "sub_wave": "iii of 3",
      "implied_direction": "down",
      "invalidation": 66000,
      "confidence": "medium"
    },
    "tf_1h": {
      "degree": "Minute",
      "current_wave": "iii of 3 (extending)",
      "note": "noisy — low reliability",
      "confidence": "low"
    }
  },
  "signals": [
    { "name": "rsi_1d",            "value": 28,          "vote": "neutral", "weight": 0.15 },
    { "name": "ma_stack",          "value": "bearish",   "vote": "short",   "weight": 0.25 },
    { "name": "structure_4h",      "value": "LH/LL",     "vote": "short",   "weight": 0.30 },
    { "name": "candle_pattern_1d", "value": "none",      "vote": "neutral", "weight": 0.10 },
    { "name": "elliott_1d",        "value": "wave 3-of-C","vote": "short",  "weight": 0.10 }
  ],
  "confluence_score": { "long": 0.12, "short": 0.55, "neutral": 0.33 },
  "plan": {
    "playbook": "sell-the-rip (trend-following)",
    "entry_zone": [65000, 68000],
    "stop": 70000,
    "targets": [60000, 55000],
    "r_r": 2.5,
    "sizing_note": "leverage ต่ำ, ระวัง short squeeze ตอน oversold"
  },
  "summaries": { "daily": "...", "weekly": "...", "monthly": "..." },
  "confidence": 0.55,
  "caveats": ["ขับด้วย macro/ETF flow > technical", "ไม่ใช่คำแนะนำการลงทุน"]
}
```

### Field provenance
- มาจาก **code (deterministic):** regime, levels, signals (rsi/ma/structure/pattern), confluence_score.
- มาจาก **LLM (interpretive):** elliott, summaries, plan.note, การสังเคราะห์ภาพรวม.

---

## 7. Elliott Wave notes (กัน misread)

- **`alt_count` = การนับแบบทางเลือกของกราฟเดียวกัน** (ไม่ใช่ wave ของคนละ TF). EW กำกวมโดยธรรมชาติ —
  มี primary thesis + alternate ที่เก็บไว้กันพลาด.
- **`sub_wave` = อยู่ตรงไหนภายใน wave ปัจจุบัน** (ลึกลง 1 degree).
- **`wave 3-of-C` = ขาลงที่แรงที่สุด ไม่ใช่ขาเด้ง.** โครงสร้าง C (ลง) = 1↓ 2↑(เด้ง) 3↓(แรงสุด) 4↑(เด้ง) 5↓(low สุดท้าย).
  ขาเด้งภายใน C คือ 2 และ 4.
- **Notation convention:** degree สูงใช้ตัวใหญ่ (A,B,C / 1-5), degree ต่ำใช้ roman ตัวเล็ก (i,ii,iii).
- **Reliability แปรตาม TF:** 1w/1m = count หลักน่าเชื่อสุด; 1h = noise → confidence ต่ำ/optional.

---

## 8. Market context snapshot (2026-06-07, อ้างอิงเฉยๆ — ไม่ใช่คำแนะนำการลงทุน)

- **BTC** ~$60–62K. ลง ~50% จาก ATH ต.ค. 2025 (~$128K). ใต้ MA 20/50/100. ETF outflow ~$4.4B/13 วัน. RSI oversold.
- **ETH** ~$1,566. ลง ~40% จาก high ม.ค. (~$3,500). death cross. support สำคัญ $1,500–1,600.
- **Driver:** macro hawkish (Fed), เงินหมุนเข้าหุ้น AI, ETF bid หาย. → flow/macro สำคัญกว่า technical.
- **EW primary count:** จบ 5-wave impulse (2023→ต.ค.2025), ตอนนี้อยู่ ABC correction, น่าจะ wave C.
  alt bullish = wave 4 (เป้า $164K); alt bearish = ลงถึง ~$48K.

---

## 9. Open Decisions (เคลียร์ก่อน/ระหว่างเริ่ม build)

- [ ] Language: **Python** (สมมติไว้) — ยืนยัน?
- [ ] Data source สำหรับ prototype: **Binance public API / `ccxt`** (ฟรี) — ยืนยัน?
- [ ] Local storage: ไฟล์ (parquet/csv) หรือ **DuckDB** — เลือก?
- [ ] TFs ที่ ingest ใน prototype: 1h / 4h / 1d? (เพิ่ม 1w/1m ทีหลัง)
- [ ] First build target: **deterministic Step 1 ที่ emit JSON ตาม §6 (ยังไม่ต่อ LLM)**
- [ ] Scheduling: manual ก่อน → แล้วค่อย cron/scheduler

---

## 10. Next Actions (บน Claude Code / local)

1. สร้าง repo + `.claude/` พร้อม **CLAUDE.md** (seed จากไฟล์นี้).
2. สร้าง **skills**: `pine-script-v6`, `crypto-ta-math`, `risk-management`, `backtesting-discipline`.
   (เริ่มจาก CLAUDE.md + skills ก่อน — เพิ่ม subagent เฉพาะงานที่แยกขาดได้จริง เพราะ subagent มี latency.)
3. สร้าง **knowledge base**: Pine v6 docs (หน้าสำคัญ), playbook/กฎเทรด, API docs ของ data source,
   spec ของ indicator ที่อยากได้, นิยาม market regime.
4. Build **engine prototype Step 1 (deterministic)**: รับ symbol+TF → ดึง history → คำนวณ feature ชุดเล็ก → พ่น JSON ตาม §6.
5. (ทีหลัง) ต่อ **LLM interpretive layer** + elliott block → **Pine bridge (levels-as-Pine)** → **dashboard**.

> Bootstrap line สำหรับวางใน Claude Code:
> "อ่าน 02-project-context.md ทั้งไฟล์. เรากำลัง build engine Step 1 (deterministic) ที่ emit JSON ตาม §6.
>  เริ่มจาก Open Decisions §9 แล้วไป Next Actions §10 ข้อ 4."
