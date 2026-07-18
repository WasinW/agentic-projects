# AIA — INDEX

> Map ของ `Agent/company/aia/`. บริบทงานปัจจุบันของสิน (Senior DE @ AIA, Azure stack). ดู `CLAUDE.md` สำหรับ role/stack-guard/workstreams/IP boundary.

## knowledge/ — curated (clean, auditable)
- **00-INDEX.md** — index เดิมของชุด curated (PRIMARY/SECONDARY tiering). ⚠️ header ยัง frame เป็น AWS — legacy, ของจริง = Azure (ดู aia-new-job.md).
- **aia-new-job.md** — role + stack (แก้เป็น Azure), Kafka producer domain, 3 repos, Strimzi/Debezium confirmed, goals ของสิน, policy เข้ม. จุดเริ่มบริบท AIA.
- **data-platform-architecture.md** — ⭐ AIA-actual architecture ยืนยันจาก org diagram (2026-07-12): sources → CDC (Qlik+Debezium) → Kafka/AKS → ADB → ADLS → ODS/Synapse. อ่านก่อนเสมอ.
- **event-processing-kafka-aks.md** — Kafka-on-AKS learning notes; §0 หลักฐาน Strimzi confirmed จาก git, connector anatomy, "Kafka MFEC".
- **repo-navigation-and-deployment.md** — confusion-buster ของ `dtp_kafka_*`: AKS = infra ไม่ใช่ code, หา "live/main" ยังไง, deploy = Jenkins→ACR→AKS→operator reconcile.
- **databricks-uc-cross-workspace-access.md** — deliver dashboard cross-workspace ผ่าน UC share (client จ่าย compute); GRANT ≠ network, credential vending, 403-vs-empty triage. (Topic 1 target = D+.)
- **databricks-dashboard-account-sharing-rls.md** — share AI/BI dashboard ให้ทีมที่ไม่ใช่ workspace member + per-viewer RLS (publisher จ่าย); publish-mode trap, `is_account_group_member()`. (Topic 1 sibling.)
- **corp-proxy-zscaler-tls.md** — unblock az/databricks/pip/git หลัง Zscaler TLS interception (master CA bundle: certifi + Zscaler root+intermediates). Generic ops, ยัง UNRESOLVED ที่ AIA.
- **streaming-batch-patterns.md** — PRIMARY (DE core): Spark Structured Streaming + batch บน Delta, 14 streaming concerns, checkpoint/trigger/watermark/idempotency, DLQ. ⚠️ header legacy MSK/AWS framing.
- **architecture-modern-data-ai.md** — PRIMARY: modern data+AI architecture, extended medallion, data-type taxonomy, 4-Ops convergence. "what goes where" map.
- **ai-rag-agent-reference.md** — SECONDARY (ไม่ใช่ day job): RAG/agents/embeddings/vector DB/eval/LLMOps + Lumora KB. reference only.
- **first-week-questions.md** — day-1 question set (architecture/cost/scope/practices/OIC-PDPA/access). ⚠️ header legacy AWS framing; ส่วนใหญ่ยังใช้ได้.

## skills/ — 9 skills
- **kafka-strimzi-cdc** — AIA Kafka platform: Strimzi/AKS/Debezium, `dtp_kafka_*` repos, add source/promote/migrate. (STARTER — verify กับ live setup.)
- **databricks-streaming-pattern** — Spark Structured Streaming + Delta write correctness (Auto Loader vs Kafka source, checkpoint, trigger, idempotent MERGE). (STARTER.)
- **airflow-databricks-orchestration** — Airflow orchestrating Databricks jobs (operators, retries, backfill, idempotency, env promotion). (STARTER — AIA จริงใช้ ADF, เก็บไว้อ้างอิง.)
- **de-solution-architecture** — เลือก/เทียบ streaming platform architecture 3 layers (producer / consumer-pipeline / ML-AI ext) + Part 4 cross-workspace serving.
- **databricks-cost-optimization** — DBU cost-reduction/re-platform playbook + serving-layer cost + §0.1 cost-monitoring reconciliation (Topic 2.1).
- **databricks-uc-governance-sharing** — UC governance + cross-workspace data-product sharing, RLS/row filter/column mask, publish modes, §6b network gate. (Topic 1.)
- **databricks-serverless-networking** — data-plane cross-workspace reachability: UC grant ≠ network, NCC/NSP/PE, serverless-firewall EOL, 403-vs-empty. (Topic 1 network gate.)
- **databricks-genie-governance** — Genie AI + Consumer-access lockdown + additivity/migration trap + Budgets (block เฉพาะ Genie LLM) + Genie cost formula. (Topic 2.2.)
- **databricks-observability** — operational + DQ observability จาก system tables (lakeflow/compute/access.audit/query.history) + Lakehouse Monitoring + SQL Alerts. (Topic 3, deferred.)

## _inbox/ — raw dumps (ไม่ curated)
Raw material ก่อนกลั่นเข้า knowledge/: chat exports, session notes, solution drafts, reference SQL, agenda. Convention ชื่อไฟล์ = **`YYYYMMDD-topic.md`** (บางไฟล์ `topic-YYYYMMDD.md`) — วันที่ + หัวข้อ. เนื้อหาอาจซ้ำ/ค้าง/ขัดกันได้ (เป็น raw). **kb-synth** เป็นตัวเลือกวัสดุที่นี่ → interview → diff → approve → เขียนเป็น knowledge unit ที่ clean. ไฟล์ที่ hot ล่าสุด: `topics-agenda-20260717.md` (3 workstreams), `topic-2.1-*` / `topic-2.2-*-20260717.md`, `solution-d-plus-resurrection-20260718.md`. (ไม่ list ทั้งหมด — ดูใน `_inbox/` ตรงๆ.)
