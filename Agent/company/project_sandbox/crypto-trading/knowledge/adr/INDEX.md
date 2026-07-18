# ADR Index — crypto-trading

Architecture Decision Records. One decision = one file. Source of the locked
constraints: `Project/project_sandbox/crypto-trading/doc/02-project-context.md` §5–§6
and `doc/03-signal-logic-spec.md`.

| # | Decision | Tags |
|---|---|---|
| [0001](0001-python-ccxt-binance-data-source.md) | Python + ccxt/Binance as data source | language, data-source |
| [0002](0002-storage-parquet-plus-duckdb.md) | Parquet store-of-record + DuckDB query layer | storage |
| [0003](0003-two-layer-engine-deterministic-interpretive.md) | Two-layer engine: deterministic code + interpretive LLM | architecture, llm |
| [0004](0004-step1-json-contract-null-shape.md) | Step 1 JSON contract + null-shape for interpretive blocks | data-contract, schema |
| [0005](0005-confluence-formula-bias-derivation.md) | Confluence formula + bias/conviction/confidence | signals, scoring |
| [0006](0006-macro-haircut-no-counter-trend.md) | Macro confidence haircut + no-counter-trend/stand-aside | signals, risk |
| [0007](0007-elliott-wave-lowest-weight-supporting-view.md) | Elliott Wave = lowest weight, supporting view only | signals, elliott |
| [0008](0008-interpretive-llm-layer.md) | Interpretive LLM layer (Elliott / summaries / plan) | llm, architecture |
| [0009](0009-pine-bridge-levels-as-pine.md) | Pine bridge — levels-as-Pine (generated snippet) | pine, tradingview |
| [0010](0010-backtest-before-trust.md) | Backtest harness before trusting the weights | backtest, validation |
| [0011](0011-journal-required.md) | Trade journal required (append-only jsonl + plan-vs-actual) | journal, discipline |
| [0012](0012-kill-date-2026-08-31.md) | Hard kill date 2026-08-31 — archive if unused | scope, lifecycle |
| [0013](0013-model-choice-sonnet.md) | LLM model = claude-sonnet-5, config-driven (was hardcoded Opus) | llm, config, cost |
| [0014](0014-deterministic-playbook-sizing-floor.md) | Deterministic playbook + sizing + confidence.floor wired; Elliott digest fixed | signals, plan, sizing, elliott |

Next number: 0015.
