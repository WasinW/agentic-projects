# Bootstrap & Delegation Prompts — Crypto Trading Engine

> วาง prompt เหล่านี้ใน Claude Code (working dir = โฟลเดอร์ crypto-tranding).
> Routed ตาม structure จริง: subagents `~/.claude/agents/`, skills `~/.claude/skills/`,
> KB `~/Documents/Projects/Agent/` (INDEX.md).

---

## 0) MAIN BOOTSTRAP (paste อันนี้ก่อน)

```
Bootstrap โปรเจกต์ใหม่: crypto trading decision-support engine

1) อ่านก่อนตามลำดับ:
   - /Users/wasin/Documents/projects/Project/project_sandbox/crypto-tranding/doc/02-project-context.md  (อ่านทั้งไฟล์)
   - ~/Documents/Projects/Agent/INDEX.md  (entry point KB — เพื่อรู้ว่ามี roles/skills/playbooks อะไร)

2) นี่เป็นโปรเจกต์เทรด crypto ส่วนตัว — ไม่ใช่ data-engineering/pipeline, ไม่เกี่ยว the_one/NTT/SCB
   อย่าใช้มุม DE/pipeline. มองเป็น builder/product project.

3) Project home + memory:
   - working dir = .../crypto-tranding/  → auto-memory scope ที่นี่
   - สร้าง KB home ตาม pattern เดิม: ~/Documents/Projects/Agent/company/project_sandbox/crypto-trading/
     (memory/ + knowledge/ + skills/ มิเรอร์ layout ของ lumora)
   - flag: โฟลเดอร์ doc สะกด "crypto-tranding" จะ standardize เป็น "crypto-trading" ไหม

4) Agent routing (reuse subagent เดิม อย่าสร้างใหม่):
   - architect/solution → one-time: validate architecture + Step 1 contract (§2–§6) อย่า redesign แค่ sanity-check
   - engineer/software → lead build engine (Python)
   - engineer/data-analyst → feature/indicator computation + candle analysis
   - business/investment → signals + weights + playbook→plan + invalidation logic
   - (เฟสหลัง) engineer/ml = predictive; engineer/frontend + design/ui + design/ux = dashboard

5) Skills:
   - ใช้ที่มี: adr → log decisions (§5) เป็น ADR ใน KB
   - สร้างใหม่ใต้ ~/.claude/skills/: crypto-ta-math, risk-management  [backtesting-discipline + pine-script-v6 = เฟสหลัง]

6) งานแรก (ยืนยัน Open Decisions §9 ก่อน):
   build deterministic Step 1 — input symbol+TF → fetch history (Binance/ccxt) → เก็บ local (DuckDB/parquet)
   → คำนวณ feature (MA stack, RSI, ATR, structure HH/HL·LH/LL, pivots, S/R) → emit JSON ตาม §6 เป๊ะ
   ยังไม่ต่อ LLM, elliott block = null, รัน manual ได้ก่อน

เริ่มจากอ่าน 2 ไฟล์ → ยืนยัน Open Decisions → เสนอ repo structure + build plan → รอ OK ก่อนเขียน code
```

---

## A) DELEGATION — architecture sanity-check (one-time)

```
spawn architect/solution:
อ่าน doc/02-project-context.md §2–§6. validate two-layer engine + hybrid architecture + Step 1 JSON contract.
flag inconsistency / ฟิลด์ที่ขาด. อย่า redesign. output: review สั้นๆ + go/no-go.
```

## B) DELEGATION — build deterministic Step 1

```
spawn engineer/software (lead) + engineer/data-analyst (feature logic):
build deterministic Step 1 ตาม §6 contract. ใช้ skill crypto-ta-math.
ยืนยัน Open Decisions §9 ก่อน. output: repo scaffold + engine module ที่ emit JSON ของ BTCUSDT บน 1h/4h/1d
(elliott=null, ยังไม่มี LLM). รัน manual ได้.
```

## C) DELEGATION — signal & trading logic (spec)

```
spawn business/investment:
นิยาม signals[] set + weights + confluence scoring + mapping playbook→plan + invalidation rules สำหรับ §6.
ให้ EW weight ต่ำ (เชื่อถือน้อยสุด, มุมมองเสริม). output: spec ที่ engineer เอาไป implement ได้.
```

## D) DELEGATION — log decisions as ADR

```
ใช้ skill adr:
แปลง §5 (Locked constraints / decisions) ของ doc/02-project-context.md เป็น ADR แยกใบ
เก็บใน KB: ~/Documents/Projects/Agent/company/project_sandbox/crypto-trading/knowledge/adr/
```

---

## ลำดับแนะนำ
0 (bootstrap) → A (sanity-check) → C (signal spec) → B (build) → D (log ADR ตอนไหนก็ได้).
เฟสหลัง: backtesting-discipline + pine-script-v6 skills → Pine bridge → dashboard (frontend/ui/ux).
