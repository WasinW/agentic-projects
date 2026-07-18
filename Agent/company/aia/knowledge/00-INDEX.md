# Data + ML + AI Pipeline — Curated Knowledge

> Curated reference for Wasin (Sin), Senior Data Engineer @ AIA.
> Stack: AWS + Airflow + Databricks + Spark (Structured Streaming + batch), Delta Lake, insurance domain.
> Source: distilled + deduplicated from raw chat exports in `../knowledge_chat/` (do not edit those — this folder is the clean version).

## How this set is organized

The material splits into two tiers by relevance to the AIA day-job:

**PRIMARY (DE core — the day job):**
- [`architecture-modern-data-ai.md`](architecture-modern-data-ai.md) — DE evolution, modern data+AI architecture, the extended medallion (Bronze → Silver → Gold → Platinum → Diamond → Agent-State) with layer definitions, data-type taxonomy, and the 4-Ops convergence (DevOps/DataOps/MLOps/AIOps). The "what goes where" reference.
- [`streaming-batch-patterns.md`](streaming-batch-patterns.md) — Spark / Databricks Structured Streaming + batch patterns grounded in the real pipeline scripts: Kafka(MSK) → Raw → Persist → Curated on Delta. The 14 streaming concerns enumerated, write patterns, checkpoint/trigger/watermark/idempotency discipline, DLQ, monitoring, and Databricks Workflows + Airflow deployment. **This is the load-bearing doc for AIA.**

**SECONDARY (broader interest — not the AIA day job, kept separate):**
- [`ai-rag-agent-reference.md`](ai-rag-agent-reference.md) — RAG, agents, embeddings, vector DBs, eval, LLMOps tool comparisons + the Lumora KB Thai-RAG portfolio project. Consolidated from the two heavily-overlapping tool-comparison docs. Reference only; revisit when doing AI-adjacent work.

## Quick navigation

| I need… | Go to |
|---|---|
| Where does this data/artifact live (which layer)? | architecture § Layer Definitions |
| How to write an idempotent streaming MERGE | streaming-batch § Pattern 3 + 14 concerns |
| Kafka→Raw consumer template | streaming-batch § Script 1 |
| Schema-enforce + DLQ on ingest | streaming-batch § Script 2 |
| Checkpoint / trigger / watermark rules | streaming-batch § Streaming discipline |
| Pick a vector DB / embedding / agent framework | ai-rag-agent § Tool comparisons |
| RAG retrieval / chunking / eval metrics | ai-rag-agent § RAG |
