# crypto-trading

Personal crypto trading **decision-support engine** — turns historical candles into
a transparent, weighted short/long bias with reasons + invalidation. Not a predictor;
it systematizes discipline and removes emotion. Generalizes to stocks/options.

> Decision-support only. **Not investment advice.**

## Architecture (two layers)
- **Deterministic (code):** fetch history → compute features (MA/RSI/ATR, swing
  structure, pivots, S/R) → signals → confluence → bias. Exact, no LLM.
- **Interpretive (LLM, later):** reads a digest → Elliott, summaries, plan prose.

v1 ships the **deterministic Step 1** only: emits JSON per the locked contract
(`doc/02-project-context.md` §6) with `elliott`/`summaries`/`plan` = `null`.

## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# analyze (manual run)
crypto-engine analyze --symbol BTCUSDT --tf 1h,4h,1d
# -> output/BTCUSDT_<ts>.json  (+ .md summary)

pytest
```

## Storage
Parquet = store-of-record (`data/candles/symbol=BTCUSDT/timeframe=1h/*.parquet`),
DuckDB = query layer. Ingest-once-store-local; only closed candles are stored.
`data/` and `output/` are gitignored.

## Config
All tuning params (signal weights, indicator periods, thresholds, invalidation,
macro-regime knob) live in `config/engine.yaml`. See `doc/03-signal-logic-spec.md`.

## Docs
| File | What |
|---|---|
| `doc/02-project-context.md` | Source of truth — mental model + **§6 LOCKED output contract** |
| `doc/03-signal-logic-spec.md` | Signal set, weights, confluence, playbook, invalidation |
| `.claude/CLAUDE.md` | Working guidance for Claude Code sessions |

## Status
- [x] P0 scaffold + §6 contract models
- [ ] P1 data layer (ccxt → parquet/duckdb)
- [ ] P2 features + golden tests
- [ ] P3 signals + confluence + bias
- [ ] P4 emit JSON/md + manual run
- [ ] (later) LLM interpretive layer · Elliott · Pine bridge · dashboard
