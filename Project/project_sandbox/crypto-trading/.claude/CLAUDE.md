# CLAUDE.md — crypto-trading

Personal crypto trading **decision-support engine** (generalizes to stocks/options).
Builder/product project — **NOT** data-engineering/pipeline, **NOT** related to
The1/NTT/SCB. Do not apply a DE/pipeline lens.

## What it is (mental model — read doc/02 §2 before changing anything)
- Two distinct "indicators": (1) Pine live-signal on TradingView, (2) **this local
  analytical engine**. They do different jobs — don't try to make #2 a TV indicator.
- **Build-time vs runtime:** Claude Code/agents/skills build the engine; the engine
  runs standalone. Deterministic layer = plain code; interpretive layer = calls the
  Anthropic API from the script itself (NOT Claude Code), added later.
- **Engine = 2 layers:** deterministic (fetch/features/signals — exact, no LLM) +
  interpretive (LLM reads a digest → Elliott, summaries, plan). v1 = deterministic only.

## Current state: deterministic Step 1 + interpretive LLM layer
input symbol+TF → fetch history (ccxt/Binance) → store local (Parquet + DuckDB) →
compute features → emit JSON per **doc/02 §6 (LOCKED contract)**. Runs manual.
- Default = deterministic only; elliott/summaries/plan = `null`, no API key needed.
- `--interpret` → `interpret.py` calls Claude (Opus 4.8, adaptive thinking, structured
  outputs) over the deterministic *digest* to fill elliott/summaries/plan and fold one
  low-weight `elliott_1d` vote into confluence (ADR 0007/0008). Needs ANTHROPIC_API_KEY.

## Contract locks (also ADRs in KB)
- `confluence_score[v] = Σ(weight where vote==v) / Σ(weights of PRESENT signals)`;
  `neutral` is its own bucket; absent signals (incl. elliott v1) drop from denominator.
- `bias.direction = argmax(confluence_score)`; conviction from margin (0.15 / 0.35 bands).
- Interpretive blocks null with **stable shape** (elliott/summaries/plan = null).
- All tuning params in `config/engine.yaml` — never hardcode.
- Storage: Parquet = store-of-record (`data/candles/symbol=/timeframe=/`), DuckDB =
  query layer via `read_parquet`. Watermark on **last closed candle** only.

## Layout
- `doc/` — 00 bootstrap, 01 transcript, 02 project-context (source of truth), 03 signal-spec
- `src/crypto_engine/` — contract.py (§6 pydantic), config.py, data/, features/, signals/, engine.py, cli.py
- `config/engine.yaml` — all params · `data/` `output/` gitignored
- `tests/` — golden-value unit tests per feature

## Knowledge base (build-time)
`~/Documents/Projects/Agent/company/project_sandbox/crypto-trading/`
(memory/ · knowledge/ + knowledge/adr/ · skills/). Top index: `~/Documents/Projects/Agent/INDEX.md`.

## Agent routing (reuse, don't create new)
- architect/solution → one-time architecture sanity-check (done — GO-WITH-NOTES)
- engineer/software → lead build (Python)
- engineer/data-analyst → feature/indicator + candle analysis
- business/investment → signals/weights/playbook/invalidation spec (done → doc/03)
- (later) engineer/ml = predictive; frontend + ui + ux = dashboard

## Skills
- existing: `adr` (log decisions). To create: `crypto-ta-math`, `risk-management`
  (later: `backtesting-discipline`, `pine-script-v6`).

## Pine bridge (engine → TradingView)
`pine.py::to_pine` emits a Pine v6 overlay (hard-coded S/R, invalidation, plan
band/stop/targets, bias label) from a Step1Output. `analyze --pine` writes
`output/*.pine` to paste into TV. Deterministic; plan band only with `--interpret`.
Pine can't call back to the engine — re-run + re-paste to refresh (ADR 0009).

## Run (once deps installed)
```
pip install -e ".[dev]"
crypto-engine analyze --symbol BTCUSDT --tf 1h,4h,1d [--interpret] [--pine]
pytest
```
> venv must be python ≥3.11 (machine `python3` is 3.9). If `crypto-engine` ever
> errors "No module named crypto_engine", re-run `uv pip install -e .` (uv editable
> install occasionally needs re-registering).

## Guardrails
- Not investment advice — this systematizes discipline, it is not a predictor.
- Market currently driven by macro/ETF flow > technical → confidence haircut applied.
- No counter-trend trades in v1; low conviction → stand-aside.
