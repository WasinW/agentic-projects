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

Next number: 0008.
