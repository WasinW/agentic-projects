# Sales Domain -- Mistakes & Rules

> Extracted from: mistakes_and_rules.md (Mistakes 10-15, sales-specific)
> Updated: 2026-04-05

---

## Rules (MUST FOLLOW for sales-collector)

### Rule #1: Read code before answering -- never guess
- Verify path, config, behavior from actual files before responding
- Never say "probably" or "I think" -- verify first

### Rule #2: Don't loop on edits
- Think through root cause before making changes
- If unsure, ask first -- don't edit then revert then edit again

### Rule #3: Be concise, take action
- No 3-page explanations before editing
- User wants action, not lectures
- Edit first, explain briefly after

### Rule #4: Log corrections immediately
- When user corrects wrong information, write to memory immediately
- Never repeat the same mistake after correction

### Rule #5: Fix production first
- If production is broken, give manual fix command immediately
- Don't only fix CI that requires a deploy cycle

### Rule #6: Validate after every code change (MANDATORY)
```bash
cd sale/sales-data/sales-collector
uv sync
uv run ruff check .
uv run mypy .
uv run poe test:cov
uv run pre-commit run --all-files
```
- Run ALL 5 steps, never skip any
- After pre-commit: `git checkout -- transactions-collector/` (Mistake 14)

### Rule #7: No git commands
- User handles git add/commit/push manually
- Agent must NOT run git commands

---

## Mistake 10: Wrong assumption -- "2 managed.Write causes crash" (2026-02-22)
- **Wrong**: Assumed 2 `managed.Write(managed.ICEBERG)` in one pipeline causes Dataflow upgrade error
- **Correct**: members-collector has **4 managed.Write** in a single pipeline and works fine
- **Cause**: Did not check members-collector before concluding
- **Lesson**: Always verify assumptions against working collectors before changing sales code

## Mistake 11: Added partition_fields unnecessarily (2026-02-22)
- **Wrong**: Added `"partition_fields": ["etlLoadTime"]` because messaging-collector had it
- **Correct**: members-collector + purchases-collector work without partition_fields
- **Cause**: Copied from messaging without checking other collectors that work
- **Lesson**: Don't copy blindly from one reference -- check multiple working examples

## Mistake 12: Added --additional-experiments without evidence (2026-02-22)
- **Wrong**: Added `--additional-experiments "use_pipeline_version_for_managed_transforms=..."` to deploy_dataflow.sh
- **Correct**: messaging/members/purchases have no experiment flags and work fine
- **Cause**: Trusted unconfirmed Beam GitHub issue #36340 workaround
- **Lesson**: Don't apply unconfirmed workarounds. Verify against working deployments first

## Mistake 13: Didn't read logs carefully -- missed artifact staging error (2026-02-22)
- **Wrong**: Kept modifying pipeline code (schema, partition, experiments) trying to fix deploy
- **Correct**: Actual error was `INTERNAL: Failed to close the writer for the artifact` = GCS staging permission issue
- **Cause**: Didn't ask user for Dataflow logs from the start
- **Lesson**: Always ask for actual error logs before debugging. The error was infra (missing `--staging-location` + `--temp-location`), not code
- **Root cause**: sales deploy script didn't pass `--staging-location` + `--temp-location`. SA couldn't write to default staging bucket. Fix: point to source bucket where SA has objectAdmin

## Mistake 14: pre-commit modified transactions-collector (2026-02-23)
- **Wrong**: `pre-commit run --all-files` -> ruff format changed trailing whitespace in `transactions-collector/src/domain/pipeline_config.py`
- **Correct**: transactions-collector is NOT ours -- must revert after every pre-commit
- **Fix**: Always run `git checkout -- transactions-collector/` after pre-commit
- **Cause**: pre-commit scope covers entire monorepo, not just our collector

## Mistake 15: Timestamp strftime Z suffix -> BQ DATETIME reject (2026-03-09)
- **Bug**: `_WrapCdcRowDoFn` used `strftime("%Y-%m-%dT%H:%M:%SZ")` with Z suffix
- **BQ DATETIME** is timezone-naive -- rejects Z suffix
- **BQ TIMESTAMP** is timezone-aware -- accepts Z suffix
- **Masked by**: Beam 2.70.0 bug in `TableRowToStorageApiProto.java:593` -- `_change_type` pseudo-column not in `SchemaInformation` -> crash masked the real error (69,356 errors logged as `Schema field not found: _change_type`)
- **Fix**: Remove Z -> `strftime("%Y-%m-%dT%H:%M:%S")`
- **Root cause**: Sales uses DATETIME columns, members-collector uses TIMESTAMP columns -- same code template, different schema types
- **Lesson**: When cross-language CDC (Python -> Java) + BQ Storage Write API, format must match BQ column type exactly. DATETIME = no timezone indicator. TIMESTAMP = with or without is fine

---

## Common Errors & Fixes (Sales-specific)

| Error | Cause | Fix |
|-------|-------|-----|
| `'int' object has no attribute 'encode'` | MasterCache returns raw BQ types | `str()` conversion in resolve functions |
| `Table metadata is too large` | Too many Iceberg snapshots | `compact-snapshots` via blms_helper.py |
| OOM (Out of Memory) | `triggering_frequency_seconds` too high | Reduce to 60s or upgrade worker memory |
| `Invalid INTERVAL value '0'` | deploy.py wrong syntax | Change to `INTERVAL '0:0:0' HOUR TO SECOND` |
| Dataform `Access Denied` cross-project | Missing IAM grant | Grant `bigquery.dataViewer` to SA on target project |
| Cache miss / stale data | BQ master not synced when Kafka arrives | Force-refresh-on-miss in MasterCache |
| CI grep fail (deploy:prod) | image-digest-ref.txt has STG path | Fix grep validation or use correct file |
| Unit test `DefaultCredentialsError` | `retry_on_miss` triggers BQ client | Add `retry_on_miss=False` to LookupConfig in tests |
| Artifact staging fail | Missing staging/temp location | Add `--staging-location` + `--temp-location` to deploy script |
