# 0001. Python + ccxt/Binance as data source

- Status: Accepted
- Date: 2026-06-07
- Deciders: Wasin + solution-architect + software-engineer
- Tags: language, data-source, prototype

## Context
The deterministic engine needs historical OHLCV for crypto across multiple
timeframes, free and key-less for a personal prototype. Language must have strong
TA/data libraries and be fast to iterate.

## Options
- **Python + ccxt (Binance public)** — one API for many exchanges, no keys for
  OHLCV, huge ecosystem (pandas/duckdb/pyarrow).
- Node/TypeScript — fine for a dashboard later, weaker for numeric/TA work now.
- Direct Binance REST — fewer deps but reinvents pagination/rate-limit/exchange
  abstraction that ccxt already solves.

## Decision
Python 3.12, `ccxt` against Binance public endpoints (no API keys) for OHLCV.
`enableRateLimit=True`; symbol-agnostic so the same code serves stocks/options
later via a different ccxt exchange or adapter.

## Consequences
- + Zero-cost, fast to prototype; exchange-swappable.
- + ccxt handles rate limiting and `parse_timeframe`/`parse8601`.
- − Binance may be region-restricted; if egress is blocked, swap the ccxt
  exchange id (the only coupling point is `data.exchange` in config).
- − Public endpoints give OHLCV only (no order-book depth) — fine for v1.
