# crypto-trading — KB Index

Project-scoped knowledge base for the personal **crypto trading decision-support
engine**. Builder/product project — not data-engineering, not The1/NTT/SCB.

- Code + docs: `~/Documents/Projects/Project/project_sandbox/crypto-trading/`
- Auto-memory scope: that working dir.

## Layout
```
crypto-trading/
├── CLAUDE.md         ← how to work in this project (build-time)
├── INDEX.md          ← this file
├── memory/           ← durable project facts
├── knowledge/
│   └── adr/          ← architecture decision records (locked constraints)
└── skills/           ← project-specific skills (pointers; live in ~/.claude/skills)
```

## Key references
- [ADR Index](knowledge/adr/INDEX.md) — locked constraints + contract decisions.
- Project context (source of truth): `…/crypto-trading/doc/02-project-context.md` (§6 = LOCKED output contract).
- Signal logic spec: `…/crypto-trading/doc/03-signal-logic-spec.md`.

## Build status (v1 deterministic Step 1 — COMPLETE)
fetch (ccxt/Binance) → store (Parquet + DuckDB, watermark) → features
(Wilder RSI/ATR, MA stack, fractal pivots, HH-HL/LH-LL, S/R, vol regime) →
signals → confluence → bias/confidence → emit §6 JSON (elliott/summaries/plan=null).
24 tests passing; runs manual via `crypto-engine analyze`.

## Agents used
solution-architect (sanity-check, GO-WITH-NOTES) · investment-consultant (signal
spec → doc/03) · software-engineer + data-analyst (build, lead by main session).

## Skills (in ~/.claude/skills)
- `crypto-ta-math` — indicator math (TradingView parity).
- `risk-management` — sizing, stops, R:R, leverage discipline.
- `adr` — decision logging (existing).
- later: `backtesting-discipline`, `pine-script-v6`.

## Next phases
LLM interpretive layer (Elliott/summaries/plan) → Pine bridge (levels-as-Pine) →
dashboard (frontend/ui/ux). Predictive ML (ml-engineer) optional later.
