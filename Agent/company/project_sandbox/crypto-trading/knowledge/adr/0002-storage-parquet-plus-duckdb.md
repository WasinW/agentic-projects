# 0002. Storage: Parquet store-of-record + DuckDB query layer

- Status: Accepted
- Date: 2026-06-07
- Deciders: Wasin + solution-architect
- Tags: storage, data

## Context
Constraint (doc/02 §5): ingest history once, store local, never hammer the API.
This is "save candles to a file", explicitly NOT a data pipeline. Need fast
re-query for feature computation and idempotent incremental top-ups.

## Options
- Parquet files only — columnar, cheap, but awkward incremental merge.
- DuckDB only — great SQL, single file, but raw store less portable.
- **Parquet (store-of-record) + DuckDB (query layer)** — Parquet partitioned by
  `symbol=/timeframe=/`, DuckDB reads via `read_parquet`. No duplicated storage.

## Decision
Parquet is the store-of-record at `data/candles/symbol=<S>/timeframe=<TF>/data.parquet`.
DuckDB is the query/read layer (`read_parquet`). Upsert by `timestamp`
(idempotent). **Watermark on the last CLOSED candle only — the in-progress
candle is dropped on write** (else every indicator flickers). Incremental backfill
starts from `watermark + tf` else `history_start`.

## Consequences
- + Idempotent re-runs, no dup rows; portable columnar files; SQL when needed.
- + `data/` is gitignored — never commit market data.
- − Single file per partition rewritten on update (fine at this scale; revisit if
  partitions get huge).
