# Shared Mistakes & Rules -- All Domains

## Rules (MUST FOLLOW every session)

### Rule 1: Read code before answering -- never guess
- Never summarize paths, config, or behavior without reading the actual file
- If unsure, read first, then answer
- Never say "probably" or "I think" -- verify first

### Rule 2: Revision discipline -- think before editing
- Think carefully before editing. Do not edit-revert-edit cycles.
- If unsure, ask first -- do not edit code immediately
- Every edit must be based on confirmed root cause understanding

### Rule 3: Be concise, take action
- No 3-page explanations before making a fix
- User wants action, not lectures
- Fix first, then explain briefly

### Rule 4: Record corrections immediately
- When user corrects wrong information, write to memory immediately
- Never repeat the same mistake after being corrected

### Rule 5: Fix production issues immediately
- If production is broken, provide immediate manual fix (command to run NOW)
- Do not only fix CI that requires a deploy -- user needs a fix NOW

### Rule 6: Verify file paths before reading
- Always check you are in the correct directory before reading files
- Monorepo has similar structures -- wrong path = wasted session

### Rule 7: Run full validation after every code change (MANDATORY)
Run all 5 in order before declaring done:
1. `uv sync` -- sync dependencies
2. `ruff check .` + `ruff format .` -- lint + format
3. `mypy src tests` -- type check
4. `pytest` -- run all tests
5. `pre-commit run --all-files` -- pre-commit hooks

After pre-commit: revert changes to files outside your scope (e.g., `git checkout -- transactions-collector/`).

---

## Shared Mistakes (cross-domain, recurring patterns)

### Mistake: Editing dead code (deploy.py)
- Edited `register_table_in_biglake_catalog` to fix drop+re-register
- The function was never called (no `--enable-biglake-catalog` flag passed)
- **Lesson**: Before editing a function, verify it is actually called in the execution path

### Mistake: pre-commit modifying other team's files
- `pre-commit run --all-files` reformatted `transactions-collector/` files
- transactions-collector belongs to another team
- **Lesson**: Always `git checkout -- transactions-collector/` after pre-commit in monorepo

### Mistake: Guessing OOM/experiments without log evidence
- SDK crash assumed to be OOM, added `num_storage_api_streams` + experiments
- Actual root cause: missing `--staging-location` / `--temp-location` for managed transforms
- **Lesson**: Get actual logs/errors before hypothesizing. Do not add flags without evidence.

### Mistake: Assuming "2 managed.Write breaks pipeline"
- Hypothesized that 2 `managed.Write` transforms cause Dataflow upgrade errors
- members-collector has 4 managed.Write in one pipeline and works fine
- **Lesson**: Check existing working examples before making assumptions

### Mistake: Timestamp format mismatch (DATETIME vs TIMESTAMP)
- `strftime("%Y-%m-%dT%H:%M:%SZ")` -- Z suffix works for BQ TIMESTAMP but fails for BQ DATETIME
- members-collector uses TIMESTAMP (Z ok), sales uses DATETIME (Z rejected)
- **Lesson**: When cross-applying patterns, verify the target schema's column types match

---

## 5 Verification Patterns (from production incidents)

### Pattern 1: Guessing root cause then deploying to prod
- Example: SDK crash assumed OOM, S3 stuck assumed epoch-related
- **Rule**: Never change prod without a proven root cause. Never guess.

### Pattern 2: Not verifying against actual data/schema
- Examples: CSV column count mismatch, INT64 vs STRING type change breaking CDC, wrong JSON field casing
- **Rule**: Before any change, verify against actual BQ schema, actual data, actual file format

### Pattern 3: Endless revision without stepping back
- Example: S3 write crash -- tried 5 different fixes without reconsidering the approach
- **Rule**: If 2 fixes fail, STOP. Step back and rethink the approach entirely.

### Pattern 4: Not checking cross-system impact
- Examples: Changing CSV mapping broke DTS sync, changing alias broke downstream CDC/EXPORT
- **Rule**: Before editing any file, trace who reads it and what downstream systems will be affected

### Pattern 5: Overconfidence without verification
- Said "no problem" or "exactly right" without actually verifying
- **Rule**: If not verified, say "not yet verified" -- never guarantee

---

## How to Apply (before every prod change)

1. Find the real root cause from logs/data -- do not guess
2. Verify against actual BQ schema, actual data, actual formats
3. Compare with the last working version, field by field
4. Trace impact: who reads this file? which pipelines use it? will DTS sync?
5. If unsure, say so honestly
6. If 2 fixes fail, stop and rethink -- do not keep patching
