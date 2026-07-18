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

# backtest — replay stored candles -> forward-return distribution per bias/conviction
crypto-engine backtest --symbol BTCUSDT      # -> output/backtest_report.{json,md}

# trade journal (append-only output/journal.jsonl)
crypto-engine journal log --artifact BTCUSDT_<ts> --action short \
  --entry 105000 --exit 98000 --stop 108000 --planned-bias short
crypto-engine journal summary --month 2026-07   # plan-vs-actual review

pytest
```

## Automation (daily, hands-off)
`scripts/daily_analyze.sh` runs `analyze --refresh --notify` and pushes a one-line
summary: **Telegram** if `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` are exported, else a
**macOS** notification, else it just writes the `output/` artifact. No tokens are stored
in the repo. Schedule it daily at 09:00 via launchd:
```bash
cp scripts/com.sin.crypto-daily.plist ~/Library/LaunchAgents/
launchctl load  ~/Library/LaunchAgents/com.sin.crypto-daily.plist   # enable
launchctl start com.sin.crypto-daily                                 # run now (test)
launchctl unload ~/Library/LaunchAgents/com.sin.crypto-daily.plist   # disable
```
For Telegram push, add `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID` to the plist's
`<EnvironmentVariables>` (local to `~/Library/LaunchAgents` — never commit real tokens).

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

## Interpretive layer (LLM)
```bash
export ANTHROPIC_API_KEY=...
crypto-engine analyze --symbol BTCUSDT --interpret
```
`--interpret` runs Claude (model in `engine.yaml` `llm.model`, default **claude-sonnet-5**;
adaptive thinking, structured outputs) over the deterministic *digest* (never raw candles)
to fill `elliott` / `summaries` / `plan` prose. The playbook is now **deterministic**
(doc/03 §4); the LLM only adds `targets` / `r_r`. It also folds a single low-weight
`elliott_1d` vote into confluence, now grounded in the full 1d pivot series (ADR 0014).

## Status
- [x] P0 scaffold + §6 contract models
- [x] P1 data layer (ccxt → parquet/duckdb)
- [x] P2 features + golden tests
- [x] P3 signals + confluence + bias
- [x] P4 emit JSON/md + manual run
- [x] LLM interpretive layer (Elliott · summaries · plan)
- [x] Pine bridge (levels-as-Pine) — `analyze --pine` → `output/*.pine`
- [x] Backtest harness — forward-return by bias/conviction (ADR 0010)
- [x] Trade journal — append-only jsonl + plan-vs-actual (ADR 0011)
- [x] Deterministic playbook + position sizing + `confidence.floor` (ADR 0014)
- [x] Daily automation — launchd + Telegram/macOS notify
- [ ] (frozen until used — kill date 2026-08-31, ADR 0012) dashboard · webhook · predictive ML
