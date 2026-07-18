# AIA — Project Context (CURRENT JOB)

> โหลดทุกครั้งที่ทำงานสาย AIA. บริบทของงานปัจจุบันของสิน.
> knowledge/ = curated · _inbox/ = raw dumps · skills/ = 9 skills (ดู INDEX.md).

## Role
- **สิน (วศิน) = Senior Data Engineer @ AIA** (life-insurance), เริ่ม **2026-07-01**. ต่างจาก The-1 (ที่เป็น onsite-consultant ในนาม NTT) — AIA คืองานปัจจุบันของเขาเอง. เรียกเขาว่า **สิน / ศิน / sin** (ไม่มี s ต่อท้าย).
- โฟกัสจริง 2 ขา: (1) **producer / Kafka side** (งานที่รับเข้ามา), (2) **ADB compute + cost-dashboard PoC** (งานที่ขยับไปทำ).

## ⚠️ STACK GUARD — AIA = AZURE, ไม่ใช่ AWS
เคยเข้าใจผิดเป็น AWS/Airflow/MSK/MWAA มาก่อน (แก้ไข 2026-07-01). **ของจริง = Azure ทั้งหมด:** Azure Databricks (ADB) + Azure Data Factory (ADF + Integration Runtime = orchestrator, ไม่ใช่ Airflow) + ADLS Gen2 + Azure SQL MI/Synapse + AKS + ACR + Key Vault + PowerBI. CI = **Jenkins** (ไม่ใช่ Azure DevOps), repo = **Bitbucket** (`aia-th`). อย่าเผลออ้าง S3/Glue/EMR/Redshift/MWAA.

## Architecture (สรุป — ดู knowledge/data-platform-architecture.md)
`SOURCES → CDC (Qlik Replicate + Debezium) → EVENT PROCESSING (Kafka/Strimzi บน AKS) → COMPUTATION (Azure Databricks real-time+batch, config-driven ผ่าน Azure SQL MI "Framework DB") → ADLS medallion (RAW→Persist→Staging) → serving (Azure SQL MI ODS + Synapse EDW/marts) → PowerBI/ESB/apps`. Governance = Purview + Data 360. หลาย Databricks workspace ต่อ business unit (Departmental/Common/Amplify/DS-Lab, UC-shared).
- **Producer domain (Sin):** Debezium CDC → Kafka Connect → Strimzi broker บน AKS. Repos `dtp_kafka_{build_ci,cluster,connector}` (YAML-heavy, deploy = Jenkins→ACR→AKS→operator reconcile). Platform แบรนด์ "Kafka MFEC".
- **Consumer side:** ADB Structured Streaming + batch consume topics → Delta tables.

## Current workstreams
1. **Topic 1 — Cost dashboard sharing PoC** (primary): share Azure-infra cost (Cost Mgmt Export → ADLS → Databricks 5-layer, tag ต่อทีมเป็น top-level col) ให้ departmental teams แบบ per-team RLS. **D+ (UC share) = target** — client query จาก workspace ตัวเอง, เขาจ่าย compute. 🚨 conditional: UC GRANT ไม่พอ, ต้องเปิด **network path (PROD compute → DEV ADLS)** ด้วย. Fallback = Artifact Factory (per-team PDF+Excel email). Pending PoC ที่ coredata UAT.
2. **Topic 2.1 — DBU cost monitoring:** `system.billing.usage` = DBU@LIST-price only ≠ Azure Portal (Portal รวม classic VM ~40-60% + discount + tax). Reconcile DBU↔DBU เท่านั้น; $ จริงมาจาก Cost Mgmt Export.
3. **Topic 2.2 — Genie governance + budget:** business user ใช้ได้แค่ Genie/AI-BI, สร้าง job ไม่ได้ = **Consumer access entitlement**. Gotcha: entitlement additive + ต้อง migrate `users`-group behaviour ไม่งั้น lockdown พัง. Budget **block ได้เฉพาะ Genie LLM DBU**; compute อื่น = ALERT-only → คุมที่ warehouse config.
4. **Topic 3 — Observability dashboard: DEFERRED** จนกว่า 1+2 เสร็จ.

## Team (จาก sources)
- **พี่ Sarunya** — เจ้าของ requirement, เป็นคนตัดสิน (สินเสนอ, Sarunya decide). เปิด UC-share ให้ 2026-07-15.
- **บูม** — ดูแล cost pipeline เดิม (opaque, **drop tags**); สิน keep tags เป็น `MAP<STRING,STRING>` = จุดต่าง.
- **MFEC** — SI ที่สร้าง/ดูแล Kafka platform ("Kafka MFEC").

## Skills (9 ตัวใน ./skills/ — ดู INDEX.md บรรทัดเดียวต่อตัว)
kafka-strimzi-cdc · databricks-streaming-pattern · airflow-databricks-orchestration · de-solution-architecture · databricks-cost-optimization · databricks-uc-governance-sharing · databricks-serverless-networking · databricks-genie-governance · databricks-observability.

## Pointers
- **knowledge/** = curated, auditable knowledge units (clean). **_inbox/** = raw dumps (chat exports, session notes, solution drafts). **kb-synth** promotes _inbox → knowledge/ (interview → diff → approve → embed). อย่า edit raw dumps ให้เป็น "ความจริง"; ผ่าน curation ก่อน.
- อ่าน `knowledge/data-platform-architecture.md` ก่อนเสมอ = AIA-actual ที่ยืนยันแล้ว.

## 🔒 IP boundary (สำคัญ — insurer เข้ม)
AIA = insurer แบบดั้งเดิม, policy เข้ม: สินexport code/data ไม่ได้ (screenshots only), เหตุ = กลัว data leak + liability. **รายละเอียด internal ของ AIA อยู่ใน private KB นี้เท่านั้น — ห้ามหลุดไป public repo/โพสต์/แชร์ภายนอกเด็ดขาด.** เวลา reason ให้อ้างจาก architecture/screenshot; อย่าให้เขา paste code หรือ generate "AIA code". Skill/knowledge ที่เป็น generic pattern ok, แต่ตัด AIA identifier ออก.
