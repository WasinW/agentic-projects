# Common -- Pending Work

## 1. Version Alignment Across Domains

**Status:** Different domains pin different tags of common packages
**Details:**
- `common-data-python-cloudrun`: Partner uses tag `0.0.35` (package version 0.0.7 internally). Other domains may use different tags.
- `common-data-python-dataflow`: Loyalty collectors reference various tags. No centralized version matrix is enforced.
- No automated mechanism to detect stale versions or breaking changes across consumers.

**Action:** Audit all domain `pyproject.toml` files for common package versions, establish minimum supported version policy.

## 2. V2 CI Templates Migration

**Status:** V2 templates exist but not universally adopted
**Location:** `pipeline/v2/` (base, dataflow, scan, terraform, example-service)
**Details:**
- V2 templates provide cleaner separation (scan templates split out, improved structure)
- Most domains still use V1 (`pipeline/common.gitlab-ci.yml` + `pipeline/common-base.gitlab-ci.yml`)
- V1 `common.gitlab-ci.yml` duplicates some definitions from `common-base.gitlab-ci.yml` (rules, gcp-prepare, terraform scripts)
- Partner domain has its own override layer in `.gitlab/ci/dataform-template.gitlab-ci.yml` that re-declares rules

**Action:** Plan migration path for each domain from V1 to V2 templates. Document breaking changes.

## 3. TestContainers Standardization

**Status:** Available in common-python-dataflow but adoption varies
**Location:** `common-python-dataflow/src/common/beam/testing/containers.py`
**Details:**
- `common.beam.testing.containers` provides TestContainers integration (Bigtable, Kafka)
- `common.beam.testing.fakes` provides FakeSink for unit tests
- `common.beam.testing.fixtures` provides DirectRunner fixtures
- Not all domains use the common testing utilities consistently; some have their own test infrastructure

**Action:** Document recommended testing patterns, ensure all domains use common testing utilities where applicable.

## 4. Dataflow Deploy Script Dual-Source Pattern

**Status:** Works but creates maintenance burden
**Details:**
- `.dataflow-deploy` template supports both remote download (`COMMON_DATA_REF`) and local copy (`SCRIPTS_LOCAL_PATH`)
- Some domains copy scripts locally (loyalty has `scripts/` dir), others download at CI time
- Version drift risk when local copies get out of sync with common-data

**Action:** Consider standardizing on one approach (prefer remote download with pinned ref).

## 5. common-python-cloudrun Missing Adapters

**Status:** Framework is young (v0.0.7), some adapters not yet built
**Details:**
- Input adapters: only `api_source` (REST API). No Kafka source, no PubSub source, no GCS source for CloudRun pattern.
- Output adapters: only `gcs_iceberg`. No BQ writer, no Bigtable writer for CloudRun.
- These exist in the dataflow package but not in the cloudrun package.

**Action:** Build additional adapters as new CloudRun-based collectors need them, or document that CloudRun pattern is specifically for API-to-Iceberg batch loads.
