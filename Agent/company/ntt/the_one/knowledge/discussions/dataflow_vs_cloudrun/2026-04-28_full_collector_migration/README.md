# 2026-04-28 — Full Collector Migration (Cloud Run for All Data Pipelines)

CTO ของ insight-api team เปิด debate รอบใหม่ — เสนอ migrate **ทุก collector** ในโปรเจ็ค data จาก Dataflow → Cloud Run pattern. เอกสารชุดนี้ capture ทั้ง proposal, conversation, honest evaluation, cost arithmetic, และ recommendation สำหรับการประชุม

## ⚡ TL;DR

| Topic | Position |
|---|---|
| **Proposal** | แทน "Kafka → Dataflow per job → BQ per table + Storage Write API" ด้วย "Pub/Sub subscription → Cloud Run → BQ via {BQ client \| Storage Write API \| Pub/Sub direct subscription}" สำหรับ ทุก collector |
| **CTO's argument** | ง่ายกว่า + ถูกกว่า (วัดจาก size × event count); Cloud Run flexible — ทำ CDC ลง BQ ได้, ใช้ materialized view, custom logic ได้ทุกอย่างที่ Beam ทำ |
| **Honest counter** | **ยอมรับว่า Cloud Run "ทำได้"** ทุกอย่างถ้ายอม custom + เพิ่ม services. ไม่ใช่เรื่อง possibility. **เป็นเรื่อง economics + operational TCO + data correctness ที่ scale** |
| **Cost finding** | "by size × event count" เป็น **partial TCO**. รวม Pub/Sub multi-hop + state store IOPS + engineering effort + reconciliation jobs + incident response → Cloud Run **แพงกว่า** Dataflow ที่ scale > 5-10M events/day per collector |
| **Strategic finding** | "Replace ALL collectors" = forfeit Beam infra investment ที่ทีมเรามีแล้ว (loyalty members/tiers/m-t-h, customer-profile V3/V4, last-purchases, customer-svoc-interim) — sunk cost + retraining + multi-toolchain tax |

## 📋 Index

| # | File | Purpose |
|---|---|---|
| 1 | [01_proposal_and_scope.md](01_proposal_and_scope.md) | What CTO เสนอจริง ๆ + scope ของ "all collectors" |
| 2 | [02_conversation_log.md](02_conversation_log.md) | Full Q&A thread (user pushback + my responses) |
| 3 | [03_honest_evaluation.md](03_honest_evaluation.md) | ทุก capability ที่ user เถียง — Cloud Run ทำได้/ทำไม่ได้ + how |
| 4 | [04_cost_arithmetic.md](04_cost_arithmetic.md) | ตัวเลข cost ละเอียดสำหรับการประชุม — naive vs full TCO |
| 5 | [05_per_collector_assessment.md](05_per_collector_assessment.md) | Collector-by-collector: ทำได้/ไม่ได้, migrate cost, lost capabilities |
| 6 | [06_recommendation_for_cto_meeting.md](06_recommendation_for_cto_meeting.md) | What to push for + meeting playbook |

## 📚 Related Docs

- [../RISKS.md](../RISKS.md) — original risks doc (10 hard risks of Cloud Run for streaming data)
- [../STACK_COMPARISON_COUNTER.md](../STACK_COMPARISON_COUNTER.md) — feature counter
- [../../dataflow/BQ_CDC_MERGE_COMPATIBILITY.md](../../dataflow/BQ_CDC_MERGE_COMPATIBILITY.md) — BQ CDC details
- [../../dataflow/bigquery/storage_write_api/CDC_PARTIAL_UPDATE_RESEARCH.md](../../dataflow/bigquery/storage_write_api/CDC_PARTIAL_UPDATE_RESEARCH.md)
- [insight/doc/insight-api/05_BQ_WRITE_SEMANTICS_PROOF.md](../../../../../insight/doc/insight-api/05_BQ_WRITE_SEMANTICS_PROOF.md) — proof ว่า insight ปัจจุบันไม่ได้ทำ CDC จริง

## 🎯 Honest Position (ที่จะใช้ในประชุม)

> 1. **Cloud Run + Pub/Sub orchestration ทำได้** ทุก data pipeline ที่ insight/loyalty มี — ถ้ายอม:
>    - เพิ่ม service/topic หลายเท่า
>    - external state (BT/Redis)
>    - reconciliation jobs
>    - eventual consistency ระหว่าง stages
>    - approximation ของ event-time semantics
>
> 2. **"Cheap by size × event"** เป็น partial truth:
>    - Direct cloud cost: Cloud Run ถูกกว่า ที่ < 5-10M events/day/collector (truly low volume + simple pattern)
>    - Direct cloud cost: Dataflow ถูกกว่า ที่ > 10M events/day/collector (sustained streaming)
>    - Total cost (engineering + ops + incident + migration): Dataflow ถูกกว่า **แทบทุก scale** สำหรับ portfolio ที่มี > 2-3 collectors
>
> 3. **Cost crossover ที่ scale ของ The1**: loyalty + insight + messaging combined > 100M events/day → Dataflow pattern ปัจจุบัน **น่าจะถูกกว่า** ของจริง. Cloud Run pattern จะแพงกว่าจาก:
>    - Pub/Sub hops (5-10× hops × $40/M messages)
>    - Bigtable IOPS (state store)
>    - Cloud Run min-instance always-on
>    - DLQ replay infra
>    - Reconciliation pipelines
>
> 4. **Sunk cost + ecosystem**: ทีมเราลงทุนใน Beam infra ไปแล้ว (BLMS REST + Iceberg + IcebergIO + Storage Write CDC + 3 deployed collectors). Migrate ทั้งหมด = throw away investment + 6-12 weeks/collector × N collectors.

## 🎬 Action items (User → CTO meeting)

1. **เสนอ position มี nuance**: "Cloud Run for application + simple ingestion. Dataflow for CDC + Iceberg + windowed stateful streaming"
2. **ขอ design doc** จาก CTO สำหรับ Cloud Run version ของ 2 collectors ที่ซับซ้อน (members-collector CDC DELETE + customer-profile-pipeline V3 windowed S3 export)
3. **ขอ TCO calculation ครบ** — ไม่ใช่แค่ size × event ไม่อยากเสีย investment ที่มีอยู่
4. **ตั้ง POC scope แทน big-bang migration** — pick 1 simple collector, migrate, measure จริง 3 เดือน, แล้ว reassess
