# Combined Priority Matrix: CVE Audit + Code Structure + Insight Refactor

**Date**: 2026-04-05
**Status**: open
**Author**: architect-solution (cross-review synthesis)

---

## Scoring Method

Each action scored on two axes:
- **Risk**: What is the blast radius and severity if we do nothing? (1=low, 5=critical)
- **Effort**: How much work to implement? (1=trivial, 5=major project)
- **Priority Score** = Risk / Effort (higher = do first)

---

## TOP 10 Actions (Ranked by Priority Score)

| Rank | Action | Source | Risk (1-5) | Effort (1-5) | Score | Rationale |
|------|--------|--------|-----------|-------------|-------|-----------|
| **1** | **grpcio upgrade to >=1.70.0 across 10 collectors** | CVE Audit (VUL-01) | 5 | 1 | 5.0 | Single `uv lock --upgrade-package grpcio` per collector. 2 HIGH CVEs (HTTP/2 DoS + use-after-free). Affects all GCP API communication. 30 minutes total. |
| **2** | **Generate uv.lock for backward-compatible-collector** | CVE Audit (VUL-05) | 4 | 1 | 4.0 | `uv lock` takes 30 seconds. Eliminates non-reproducible builds (supply chain risk). |
| **3** | **Batch minor patches: cryptography, certifi, authlib, confluent-kafka, protobuf** | CVE Audit (VUL-10-13,16) | 3 | 1 | 3.0 | Single PR per collector with `uv lock --upgrade-package` for 5 packages. All patch-level upgrades, zero breaking change risk. 1 hour total. |
| **4** | **Copy boot-builder Dockerfile.base from sales-collector to 7 others** | CVE Audit (VUL-09) | 5 | 2 | 2.5 | CRITICAL CVE-2025-68121 (TLS hijack) in boot binary of every Dataflow worker. sales-collector already has the fix -- copy the boot-builder stage. Half-day of work + testing across 7 collectors. |
| **5** | **Switch customer-profile-collector Dockerfile to new entrypoint** | Insight Refactor (Phase 1) | 5 | 2 | 2.5 | Production currently runs LEGACY code despite refactored code existing. The new src/ structure is dead code in deployed containers. Phase 1 (migrate bq_transformers + switch Dockerfile + verify) is ~1 day. |
| **6** | **Add `enable_lineage=true` to members-collector** | Code Structure (4.1) | 3 | 1 | 3.0 | 5-minute config change. members-collector is the only loyalty Dataflow collector missing data lineage. Affects audit trail and data governance. |
| **7** | **Add DLQ pattern to common-data-python-dataflow lib** | Code Structure (DLQ) | 4 | 3 | 1.3 | No streaming collector has DLQ today -- any malformed message crashes/blocks the pipeline. Design a shared `DlqSink` PTransform using Beam's `.with_exception_handling()`. 1 week for library + rollout to members (highest-risk streaming collector). |
| **8** | **products-collector: remove legacy SettingsLoader, rename files** | Code Structure (4.6) | 3 | 1 | 3.0 | 2 hours. Dual config systems (SettingsLoader + ConfigurationAdapter) are the most confusing pattern in the codebase. Also rename `bigquery_purchases_config.py` to `bigquery_products_config.py`. |
| **9** | **Modernize customer-profile-pipeline: uv + Dockerfile.base + Beam 2.71.0** | CVE Audit (VUL-03, VUL-04) | 4 | 4 | 1.0 | The highest-risk build in the fleet (no lockfile, pip install, Python 3.11, Beam 2.69.0). But also the highest effort -- requires Dockerfile rewrite, Python 3.11->3.12 migration, Beam upgrade, and full regression testing. 1-2 weeks. |
| **10** | **Eliminate `to_legacy_config_dict()` bridge in customer-profile-collector** | Insight Refactor (Phase 3) | 3 | 2 | 1.5 | After Phase 1 (rank 5), refactor builder.py to use typed attribute access instead of untyped dict access. Prevents runtime key-miss errors and enables mypy validation. 1-2 days. |

---

## What's NOT in Top 10 (and why)

| Action | Why deferred |
|--------|-------------|
| pyarrow upgrade to 18.x | Beam 2.71.0 declares `<18.0.0` -- lifting this before Beam supports it risks subtle arrow compatibility bugs. Wait for Beam 2.73+. tiers/m-t-h at 18.1.0 should be monitored for issues. |
| boto3/botocore chain upgrade | High effort (s3fs/aiobotocore cascade), limited to 2 collectors with internal S3 access. Risk is real but blast radius is contained. |
| domain/config/ subdir for D-H collectors | Cosmetic alignment. No functional or security impact. |
| PipelineConfig type standardization (Pydantic vs dataclass) | Both work. Frozen dataclass is arguably better (true immutability). Not worth the churn. |
| Integration tests for untested collectors | High value but very high effort. Add incrementally alongside feature work, not as a standalone project. |
| Protocol ports adoption | Nice pattern from customer-profile-pipeline V3 but no other collector needs it today. |
| PubSub vs Kafka standardization | Wrong question -- transport should match the source system. Standardize the message envelope, not the transport. |
| Shared GAR base image for Dockerfile.base | Correct long-term architecture but requires CI/CD changes, versioning strategy, and cross-team coordination. Plan for Month 2. |
| numpy `<2` constraint removal | Stale constraint but only 4 collectors affected, no active CVE exploitation risk. |
| sshtunnel replacement | Unmaintained but batch-only, internal network, minimal attack surface. |

---

## Execution Roadmap

### Week 1: Quick wins (Rank 1, 2, 3, 6, 8)
- grpcio upgrade across 10 collectors
- backward-compatible lockfile generation
- Batch minor package patches
- members-collector lineage flag
- products-collector SettingsLoader cleanup
- **Expected outcome**: 14 CVE findings resolved, 2 structural issues fixed

### Week 2: Critical infrastructure (Rank 4, 5)
- Propagate boot-builder Dockerfile.base to 7 collectors
- customer-profile-collector Phase 1 (switch entrypoint to new src/)
- **Expected outcome**: Boot binary CVE patched fleet-wide, insight collector runs new code in production

### Week 3-4: Platform hardening (Rank 7, 9, 10)
- Design and implement DLQ in common lib, roll out to members-collector first
- Begin customer-profile-pipeline modernization (uv + Dockerfile.base + Beam 2.71.0)
- Eliminate to_legacy_config_dict() bridge in customer-profile-collector
- **Expected outcome**: Streaming resilience for highest-risk collector, last legacy pipeline on path to modernization

### Month 2: Strategic improvements
- Shared GAR base image for Dockerfile.base
- Add `uv-secure` as CI gate for all collectors
- Monthly dependency refresh cycle established
- pyarrow upgrade when Beam 2.73+ releases

---

## Risk of Doing Nothing for 3 Months

**CRITICAL risks that compound with time:**

1. **Boot binary CVE (VUL-09)**: CVE-2025-68121 is a TLS session hijacking vulnerability in every Dataflow worker's PID 1 process. Every day this is unpatched, all Dataflow pipelines processing sensitive loyalty data (member tiers, purchase history, PII) are exposed. If a network attacker can intercept worker-to-worker gRPC traffic, they can hijack the TLS session.

2. **customer-profile-collector running dead code**: The refactored code is NOT running in production. If a bug is found in the legacy code, the team will face a choice between fixing dead legacy code or rushing the entrypoint switch under pressure. The gap between "code in repo" and "code in production" will only widen.

3. **grpcio CVE chain**: 10 collectors with gRPC HTTP/2 DoS vulnerability. A targeted denial-of-service against any Dataflow worker's gRPC endpoint can crash the worker, causing pipeline instability and data delays.

4. **Version drift acceleration**: Without a monthly refresh cycle, the gap between current and deployed versions will grow. By July 2026, grpcio could be 3+ minor versions behind, pyarrow 2+ versions behind, and the effort to upgrade safely will multiply.

5. **No DLQ on streaming collectors**: Any malformed Kafka message in members-collector or coupons-collector currently causes the DoFn to throw, the element to be retried, and potentially the pipeline to stall. Three months of accumulated edge cases in production data without DLQ means potential data loss or silent pipeline degradation.

**Bottom line**: The biggest single risk is VUL-09 (boot binary). The biggest systemic risk is the absence of DLQ on streaming pipelines. Both are addressable within 2 weeks.
