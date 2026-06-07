# Loyalty Domain -- Mistakes & Rules

---

## Rules

### Rule #1: Read code before speaking, never guess
- Do not summarize path, config, or behavior without reading the actual file
- If unsure -> read first -> then answer
- Never say "probably" or "I think" -- must verify first

### Rule #2: Do not go back and forth with changes
- Think carefully before editing. No edit-revert-edit cycles
- If unsure -> ask first -> do not edit code immediately
- Every change must come from understanding the real root cause

### Rule #3: Be brief, take action
- No 3-page explanations before fixing
- User wants action, not lectures
- Fix first, then explain briefly

### Rule #4: Remember user corrections -- write them down immediately
- If user corrects wrong information -> record in memory immediately
- Never repeat the same mistake after being corrected

### Rule #5: Fix immediate problems first
- If production is broken -> provide an immediate fix (manual command) first
- Do not fix only the CI pipeline that requires a deploy -- user needs a fix NOW

### Rule #6: Verify the correct path
- **Correct path**: `loyalty/loyalty_paralel/loyalty-data/` (BLMS REST, deployed code)
- **Wrong path**: `loyalty/loyalty-data/` (Hadoop, old code -- do not touch)
- Always check path before reading files

### Rule #7: Run validation after every code change (MANDATORY)
- **Every time** code is changed, run **all 5** before reporting done:
  1. `uv sync` -- sync dependencies
  2. `ruff check .` + `ruff format .` -- lint + format
  3. `mypy src tests` -- type check
  4. `pytest` -- run all tests
  5. `pre-commit run --all-files` -- pre-commit hooks
- Never skip, never forget, never run partial
- If venv issues (hdfs, VIRTUAL_ENV) -> use `.venv/bin/ruff`, `.venv/bin/mypy`, `.venv/bin/pytest` directly
- CI YAML changes do not need Python tools, but pre-commit may check YAML

---

## Mistake 1: Read code from wrong directory
- **Wrong**: Read `loyalty/loyalty-data/` (Hadoop) -> wasted entire first session context
- **Correct**: Must read `loyalty/loyalty_paralel/loyalty-data/` (BLMS REST)
- **Cause**: Did not check path before reading

## Mistake 2: Stated wrong messaging path
- **Wrong**: Said messaging data is at `gs://bucket/source/messages/`
- **Correct**: Actually at `gs://bucket/messages/` (flat, no source/)
- **Cause**: Did not read `get_table_location()` which returns `gs://{catalog_name}/{table_name}`

## Mistake 8: CI cleanup impossible -- SA IAC lacks Service Usage Consumer
- **Wrong**: Uncommented cleanup step in .gitlab-ci.yml for all 3 collectors
- **Correct**: SA in GitLab CI is SA IAC which lacks Service Usage Consumer role -> BLMS REST API cannot be used
- **Correct**: BLMS cleanup must run in Dataflow (workload SA has the correct role)
- Reverted CI changes, added comments explaining why it cannot be done

## Mistake 9: load_table() failure does not mean table is absent
- **Wrong**: `load_table()` failed -> concluded "not in BLMS" -> did not drop
- **Correct**: BLMS entry exists (seen via `list_tables()`) but metadata file on GCS is missing -> `load_table()` crashes
- **Correct**: Must use `list_tables()` first to check if entry exists. If entry exists but `load_table()` fails = broken entry -> must drop

---

## Verified Root Cause (BLMS Stale Entry)
- Stale BLMS entry from old pipeline run (before `table_properties.location`)
- BLMS entry pointed to `gs://bucket/source/tiers/metadata/00001-xxx.metadata.json` (namespace path)
- IcebergIO LOADed existing table instead of auto-creating new one
- Fix: Delete stale BLMS entry -> IcebergIO auto-creates with correct `table_properties.location`

## Key Facts (Verified)
- `table_properties.location` only works on **CREATE**, not LOAD
- If table already exists in BLMS -> IcebergIO **LOAD** (ignores location override)
- deploy.py (SqlCatalog/SQLite) and IcebergIO (BLMS REST) are separate systems, no conflict
- Messaging and loyalty use identical writer config; only difference was stale BLMS entry
