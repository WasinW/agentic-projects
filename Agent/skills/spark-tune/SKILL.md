---
name: spark-tune
description: Diagnose a slow or expensive Spark job and produce a ranked fix checklist — skew, shuffle, small files, spill/OOM, caching, pushdown, AQE. Use when a Spark/Databricks batch or streaming job is slow, OOMing, shuffling heavily, or burning cluster cost.
---

# spark-tune

Walks a Spark job's symptoms down to root causes and emits a **ranked** list of fixes, each with the *why* — so the reader applies the high-leverage one first, not all twelve.

## When to use

- A Spark / Databricks job is slow, expensive, OOMing, or has a stage that drags.
- Heavy shuffle, obvious skew (one task lagging), or small-file explosion.
- Tuning a streaming job's batch duration / state.

## Inputs

- **Symptoms** — slow stage, OOM, skew (straggler tasks), long shuffle, spill, GC, small-file output.
- **Job type** — batch / structured streaming; SQL / DataFrame / RDD.
- **Data sizes** — input size, output size, biggest join/aggregation, partition count.
- **Current config** — executor cores/memory, shuffle partitions, AQE on/off, broadcast threshold, cluster size.

## Steps

1. **Load knowledge:**
   `mcp__agent-knowledge__search_knowledge(query="spark performance tuning skew shuffle AQE OOM spill broadcast", role_filter="de-engineer", top_k=5)`.
   Fallback: read `roles/technical/engineer/de-engineer/knowledge.md`.
2. **Locate the bottleneck first** — from symptoms (and Spark UI if available): which stage, is it skew (one slow task), shuffle, spill, or output write? Don't tune blind.
3. **Diagnose by class, in this order:**
   - **Skew** → enable AQE skew-join (`spark.sql.adaptive.skewJoin.enabled`); salt the hot key; isolate/broadcast the skewed side.
   - **Shuffle** → tune partition count (`spark.sql.shuffle.partitions` or AQE coalesce); broadcast the small side (`broadcast()` / raise `autoBroadcastJoinThreshold`); cut wide transforms.
   - **Small files** → coalesce/repartition before write; compact output; align partitioning to write volume.
   - **Spill / OOM** → more partitions (smaller tasks), raise executor memory / lower cores-per-executor, avoid `collect`/giant broadcasts, check skew as the real cause.
   - **Caching** → `cache()`/`persist()` only reused DataFrames at the right storage level; unpersist after; don't cache once-read data.
   - **Pushdown** → ensure predicate + column projection pushdown (Parquet/Delta), partition pruning, and prune columns early; avoid UDFs that block pushdown.
   - **AQE** → turn on AQE (coalesce partitions, skew join, dynamic join switch) as the cheap default win.
4. **Output a ranked fix checklist** — highest expected impact first, each with: the fix, the config/code, and the *why* (which symptom it removes). Note expected effect and any risk.
5. **For streaming** — also check trigger interval, state store size, watermark, and shuffle partition count vs micro-batch size.

## Guardrails / Notes

- Diagnose before prescribing — a generic "increase memory" without finding skew wastes cost.
- Change one lever at a time and re-measure; don't bundle five config changes blind.
- Prefer AQE + better data layout over brute-force bigger clusters (cost discipline).
- Flag when a fix belongs upstream (data layout / table format / partitioning) — point to `lakehouse-maintenance`.
