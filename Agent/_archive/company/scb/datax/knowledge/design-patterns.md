# SCB Data-X ETL Framework — Reusable Design Patterns

Project-agnostic engineering patterns distilled from Wasin's metadata-driven ETL
framework on Databricks (RDT data-zone + SCB Datalake). This file captures the
**why-it-was-designed-this-way** and the reusable lessons; architecture and the
end-to-end RDT pipeline are covered in sibling files (`architecture.md`,
`etl_framework.md`) and are not repeated here. All claims are grounded in the
surviving framework code under
`.../bk_de_etl_fw/fw(rdt)/fw/` and `.../bk_de_etl_fw/wks_dev(scb_dl)/framework/`;
facts not present in code are marked **(from Wasin's account)**.

---

## Pattern 1 — Config-driven dispatch / pluggable scripts

**Pattern.** A "job" is a row in a SQL Server config table, not a piece of code.
Per-stage behavior is selected by `script_*` columns whose values name a notebook
that the generic engine loads and runs at runtime. Adding a new source or
transform = inserting a config row + dropping a notebook in the right folder; the
engine binary never changes.

**How it works (grounded).**
- Ingest config table `tbl_ingt_job` declares the pluggable hooks as columns:
  `script_list_src_file, script_ctl_file_vld, script_pre_proc, script_qlty,
  script_load, script_audt` (DDL: `fw(rdt)/fw/init/tbl_init_ingt_config_table.py`,
  lines 23–28). Only `script_load` is `not null`; the rest are optional hooks.
- The engine `fw_ingt_main.py` reads exactly one config row, binds each `script_*`
  to a variable (`fw_ingt_main.py:169-174`), then resolves each to a notebook path
  by prefixing a stage-specific base path and dispatching via `run_notebook(...)`:
  list-file (`:210-215`), control-file validation (`:403-406`), pre-proc
  (`:424-433`), load (`:506-515`), audit (`:531-555`). Base paths are centralized
  in `environment_config.py` (`INGT_MODULE_LIST_FILE_PATH`, `INGT_MODULE_PRE_PROC_PATH`,
  `INGT_LOAD_PATH`, …).
- A hook left empty is skipped, not failed: e.g. `if script_pre_proc:` else
  `...Skipped...` (`fw_ingt_main.py:422-446`); empty `script_load` flips
  `load_flag='N'` and exits success early (`:381-386`).
- Transform mirrors this: `tbl_tnfm_job.script_tnfm` + `subj_area` resolve to
  `TNFM_TNFM_PATH/<subj_area>/<script_tnfm>` (`fw_tnfm_main.py:150,281`).
- Pre-proc readers are the swappable plug-ins (`ingt/.../pre_proc/`):
  `mdle_cmmn_read_stnd_delim`, `mdle_cmmn_read_excel`, `mdle_cmmn_read_sas7bdat`,
  `mdle_cmmn_read_xml`, `mdle_cmmn_read_parquet` — one per source format, each a
  drop-in selected by config.

**Why / trade-offs.** Onboarding a new feed becomes a config + content change,
reviewable and deployable without touching (or re-testing) the engine — critical
in a regulated bank where engine changes trigger heavyweight change control.
Trade-off: indirection. The engine binds notebooks by string at runtime, so a
typo'd `script_*` value or a missing notebook fails late (`run_notebook` raises
`Notebook not found`, `fw_cmmn_func.py:309`) rather than at deploy. There is no
compile-time contract between engine and plug-in beyond the `rtn_cd`/`rtn_val`
return convention.

**Reusable lesson.** Treat per-step behavior as data, not code. A small fixed set
of named, optional hooks ("list → validate → pre-proc → load → audit") covers most
batch ingest shapes; keep the orchestrator generic and push variability into
config rows + pluggable, single-responsibility modules.

---

## Pattern 2 — SQL-as-templated-notebook execution

**Pattern.** Business transform logic lives in plain SQL files containing
`${var}` placeholders. The engine fetches the SQL at runtime, substitutes config
values, splits it into executable units, and runs each via `spark.sql`. Logic and
engine are physically separate artifacts.

**How it works (grounded).** `exec_sql_notebook(adb_notebook_path, replace_var)`
in `fw_cmmn_func.py:857-879`:
1. `get_notebook_content()` pulls the SQL via the Databricks Workspace Export API
   (`fw_cmmn_func.py:317-334`) — so the script is a versioned workspace object, not
   inlined.
2. Variable substitution: `data.replace("${","{").format(**replace_var)`
   (`:864`). `replace_var` is built per-stage from config — `INGT_REPLACE_VAR` /
   `TNFM_REPLACE_VAR` in `environment_config.py` expose `bsns_dt`, `trgt_db_nm`,
   `trgt_tbl_nm`, `stg_tbl`, `job_nm`, env, etc.
3. Split into cells on `SQL_SPLIT_CELL = '-- COMMAND ----------'` and into
   statements on `SQL_SPLIT_CMD = ';'` (`environment_config.py:81-82`).
4. Each statement is cleaned with `sqlparse.format(..., strip_comments=True)` and,
   if non-empty, run via `spark.sql` cell-by-cell (`:866-879`).
- The engine chooses SQL-vs-Python execution dynamically:
  `get_notebook_language()` (`fw_cmmn_func.py:837-852`) queries the Workspace API,
  and `fw_ingt_main.py:508-515` / `fw_tnfm_main.py:286-291` branch on it — SQL goes
  to `exec_sql_notebook`, Python goes to `run_notebook` with the same param dict.
- `exec_sql_notebook_rtn` (`:883-918`) is the validation variant: it wraps the
  predicate after `WHERE` in `not(...)` so the same rule SQL can be inverted to
  return offending rows.

**Why / trade-offs.** SQL is the lingua franca for the analysts/data modellers who
own the business rules; keeping logic as flat SQL files means they are
diff-able in Git, reviewable, and deployable independently of the Python engine.
The `${var}` convention keeps SQL parameter-safe across business dates and
environments without string-concatenating in the engine. Trade-off: the homemade
splitter is fragile — a `;` inside a string literal or a comment, or a
non-standard cell marker, breaks tokenization; statement-by-statement execution
also loses set-level atomicity. (A modern equivalent would be dbt or
parameterized Spark SQL with proper binding.)

**Reusable lesson.** Externalize transformation logic as parameterized SQL that
domain owners can edit and version, and keep a thin, uniform execution contract
(fetch → substitute → split → run) in the engine. Decide SQL-vs-imperative at
runtime from the artifact itself so one orchestrator serves both.

---

## Pattern 3 — Dependency & incremental via a dependency table

**Pattern.** Cross-job dependencies are declared as data in `tbl_cmmn_dpdc`, one
row per upstream the job waits on. The dependency *kind* and the *date to check*
are both data-driven — incremental/look-back behavior is NOT hardcoded in the
engine.

**How it works (grounded).** Table schema
(`fw(rdt)/fw/init/tbl_init_cmmn_dpdc.py:11-19`):
`job_nm, pndng_type, pndng_db, pndng_tbl, pndng_job_nm, alw_zero_rec_flag,
script_chck_dpdc`. The checker `fw_cmmn_chck_dpdc.py` reads all rows for the job
(`:39`) and routes by `pndng_type ∈ {LAKE, INGT, TNFM, UTLT}` (`:121-140`):
- **INGT/TNFM/UTLT** → success is verified against the audit log. `chck_log`
  (`:223-254`) joins the upstream's job + log tables, takes the **latest run per
  (job, table, bsns_dt)** via
  `ROW_NUMBER() OVER(PARTITION BY job_nm,trgt_tbl_nm,bsns_dt ORDER BY job_strt_dttm DESC)`
  and keeps `rank = 1`, then requires `job_sts='SUCCESS'` **and**, unless
  `alw_zero_rec_flag='Y'`, `cnt_trgt > 0` (`:227-229`). `alw_zero_rec_flag='Y'`
  relaxes the row-count gate for legitimately-empty feeds.
- **LAKE** → no log; `chck_lake` (`:154-220`) globs a `.success` marker file in the
  lake zone path keyed by date (`CMMN_DPDC_LAKE_SUCCESS_PATH`,
  `environment_config.py:23`) and regex-matches
  `<tbl>.<job>.<yyyymmdd>...*.success`.
- **Incremental / look-back is per-row, via `script_chck_dpdc`.** If a dependency
  row names a custom date script, the checker runs it and uses its returned list of
  dates as the dates to check (`fw_cmmn_chck_dpdc.py:98-112`); otherwise it defaults
  to `[bsns_dt]`. The custom script decides the look-back: `t1_check_bsns-1.py`
  returns `[bsns_dt - 1 day]` (`cstm_dpdc/t1_check_bsns-1.py:26-27`), i.e. "wait for
  the named table's **prior-day** success"; `t1_check_eom.py` and `bypass_dpdc.py`
  are other policies. **The named `pndng_tbl` may be the job's own target table or a
  different table A — you must read the dpdc row to know which.** **(Wasin
  confirmed this nuance.)**
- Final gate: any `CHCK_RESULT='N'` fails the whole check (`:357-364`); the
  transform engine raises on `rtn_sts='N'` (`fw_tnfm_main.py:209-210`).

**Why / trade-offs.** Declaring dependencies as rows decouples scheduling from job
code: the same engine handles "wait for upstream same-day", "wait for prior-day"
(incremental), "wait for EOM", and "wait for a lake `.success`" purely by config.
Checking success through the audit log (latest run + status + row count) rather
than a scheduler edge means re-runs and partial reloads are respected. Trade-off:
the dependency graph is implicit — scattered across rows rather than a visible DAG;
the `script_chck_dpdc` indirection means a reviewer cannot tell a job's true
look-back semantics without opening both the dpdc row and the named script.

**Reusable lesson.** Model "is the upstream ready?" as a query against your own
state (audit log latest-success + count gate) plus a pluggable date-policy hook —
not as a hardcoded `T-1`. A `allow_zero_records` flag and a `.success`-marker
fallback for foreign zones are cheap and prevent both false-greens and
false-reds.

---

## Pattern 4 — Audit-log state machine

**Pattern.** Every stage drives a per-run row through an explicit status lifecycle
in a `tbl_*_log` table, with an idempotency guard at entry and an area-level
rollup at the top.

**How it works (grounded).** In `fw_ingt_main.py` the run row transitions
`RUNNING` → `RUNNING-COPY` → `RUNNING-LOAD` → `SUCCESS | FAILED`:
- Insert `RUNNING` after config load (`:191-202`).
- `RUNNING-COPY` before file transfer (`:239-240`); `RUNNING-LOAD` before load
  (`:389-390`); `SUCCESS` with `cnt_src/cnt_trgt/cnt_diff` at the end (`:603-604`).
  Any exception routes through `exit_prog_fail()` → `FAILED` + error message
  (`:20-35`). Transform uses the same pattern (`fw_tnfm_main.py:36-47`,
  `:355-357`).
- **Idempotency guard:** before inserting `RUNNING`, `chck_dup_job` queries the log
  for `job_sts LIKE '%RUNNING%'` on the same `(job_nm, bsns_dt)` and raises if any
  in-flight run exists (`fw_cmmn_func.py:114-123`; called `fw_ingt_main.py:184-185`,
  `fw_tnfm_main.py:165-166`) — prevents concurrent double-runs.
- **Append-then-update model:** `insert_log` writes the row, `update_log` patches it
  by a precise `where_cond` (start dt + job_nm + bsns_dt + job_id + start_dttm), and
  `update_log` can itself guard against duplicate updates (`vld_dup_flag='Y'` →
  raise if `>1` match, `fw_cmmn_func.py:287-293`).
- **Area-level rollup:** `fw_cmmn_area_wrapper.py` runs a set of jobs (per
  `tbl_cmmn_area`), collects each job's `job_sts`, and the area succeeds only if no
  child is `FAILED` (`:269-280, 319-325`) — composing per-job state into a batch
  outcome and a single email alert.

**Why / trade-offs.** The intermediate `RUNNING-COPY`/`RUNNING-LOAD` states make a
stuck run diagnosable (you can see *where* it died), and the log is the single
source of truth that Pattern 3 queries for dependencies. The duplicate-running
guard gives at-most-one-active-run semantics cheaply. Trade-off: state lives in
SQL Server outside the Spark transaction, so a crash between `spark.sql` and
`update_log` can leave a row stuck in `RUNNING-LOAD`; recovery relies on the
duplicate guard + manual/operational cleanup rather than a transactional outbox.

**Reusable lesson.** Give every pipeline run a row with an explicit, queryable
status lifecycle (not just success/fail), guard entry against concurrent
duplicates, and roll child statuses up to a batch verdict. The log then doubles as
your dependency oracle, your observability surface, and your idempotency anchor.

---

## Pattern 5 — Fail-loud config contract

**Pattern.** Configuration is validated hard at job start and the engine refuses to
proceed on anything ambiguous — exactly-one-active-row, no nulls in key columns,
flags ∈ {Y,N}, paths well-formed, values within allow-lists.

**How it works (grounded).** All in `fw_cmmn_func.py`:
- `get_config(tbl_nm, where_cond)` (`:135-157`) loads the row(s) and asserts a
  single active config: raises on **0 active** ("Configuration not found" /
  "Active configuration not found (Inactive found)") and on **>1 active**
  ("Duplicate active configuration found"). The `actv_flag='Y'` uniqueness is the
  core contract.
- `vld_config` (`:162-171`) — listed columns must be non-null/non-"NULL".
- `vld_flag_config` (`:176-190`) — flag columns must be exactly `Y`/`N` (and upper
  case), via `chck_y_n`.
- `vld_path_config` (`:195-203`) — path columns must end with `/` or `\`.
- `vld_val_config` (`:208-220`) — values must be in a per-column allow-list, case
  enforced.
- The expected column sets live in config, e.g. `INGT_CONFIG_COL_NOT_NULL`,
  `INGT_CONFIG_COL_FLAG`, `INGT_CONFIG_COL_PATH`
  (`environment_config.py:128-130`); the engine calls the validators immediately
  after `get_config` (`fw_ingt_main.py:140-152`).
- Input parameters get the same treatment: `bsns_dt` is parsed/normalized by
  `chck_bsns_dt` (`:57-64`), flags by `chck_y_n`, and missing mandatory widgets
  raise before any side effect (`fw_ingt_main.py:62-73`).

**Why / trade-offs.** In a metadata-driven engine the config *is* the program, so a
bad row is a bug. Failing loud at ingest — before any copy, load, or log insert —
stops bad data from propagating and makes misconfiguration a clear, early error
instead of a silent half-load. The exactly-one-active-row rule lets config evolve
by toggling `actv_flag` while guaranteeing deterministic selection. Trade-off:
validation is centralized but the *expected* column lists are themselves config
constants that must be kept in sync with table DDL; over-strict path/flag rules can
reject otherwise-valid edge cases.

**Reusable lesson.** Validate config and inputs at the top of the job and crash
loudly with a specific message; enforce a single-active-version selection rule so
configuration changes are deterministic and auditable. "Fail at ingest, not
downstream" applies as much to config as to data.

---

## Pattern 6 — Schema-versioning / data-contract via Excel mapping

**Pattern.** Each table's schema, datatypes and source-file format are described in
a **versioned Excel mapping spec** that is the human-owned source of truth; a
generator turns that spec into the runtime artifacts (config rows, `CREATE TABLE`
DDL, and the SQL load script). When an upstream source changes, you bump the spec
version, regenerate, and redeploy — and the old spec remains as a dated, auditable
record that the team designed to the documented contract.

**How it works (grounded).** The surviving generator is the config-helper layer
under `wks_dev(scb_dl)/framework/.../fw/config_helper/`:
- `fw_mpng_helper.py` reads a versioned Excel file from
  `EXCEL_MPNG_PATH = ".../ingt/spec_mpng/<src_sys>/"`
  (`environment_config.py:34`), worksheet `'Table Mapping'` (`:60`). Columns are
  positionally mapped via `EXCEL_MPNG_DICT_IDX`
  (`environment_config.py:247-257`: `db_nm, tbl_nm, col_nm, data_type, data_lnth,
  mandatory, tbl_lctn, src_fmt`).
- From that one spec it generates two artifacts per table and pushes them into the
  workspace via the Import API:
  1. **DDL init script** — `gen_init_script` (`fw_mpng_helper.py:81-128`) emits
     `CREATE TABLE ... USING PARQUET PARTITIONED BY (BSNS_DT)` with `LOAD_DTTM`,
     `BSNS_DT` appended and `DECIMAL(len)` handling, plus a RELEASE/ROLLBACK
     deployment wrapper.
  2. **SQL load script** — `gen_load_script` (`:184-223`) emits
     `INSERT OVERWRITE TABLE ... PARTITION (BSNS_DT) SELECT <casts> FROM ${stg_tbl}`,
     deriving per-column casts from the spec (`TO_DATE/TO_TIMESTAMP/CAST/DECIMAL`,
     `gen_load_str:169-182`) and a `WHERE col IS NOT NULL` clause for columns flagged
     mandatory in the spec (`:194-198`).
- A sibling, `fw_config_helper.py` (`:144-191`), reads a `'Consolidated Files'`
  worksheet and generates the `tbl_ingt_job` config-row `INSERT` statements,
  choosing `script_pre_proc`/`script_ctl_file_vld` from the spec's declared file
  type (delimiter/excel/sas7bdat) — so the spec also drives Pattern 1's dispatch.
- So the chain is: **Excel spec (versioned) → generator → {DDL, load SQL, config
  rows} → engine executes**. The spec is the contract; the generated SQL/DDL are
  derived, not hand-maintained.

**(From Wasin's account.)** In the earlier, non-retained framework the mapping
binding was itself a runtime table (`tbl_ingest_mapping`-style, ~ `job_nm, tbl_nm,
excel_mapping_name`) pointing each table at a versioned file such as
`Mapping_table_<src>_v1.xlsx`. On an unexpected upstream change the practice was to
bump to `v2`, redeploy, and keep the prior version as a dated reference — the spec
served as a **change-management / data-contract artifact to defend the team** when
sources changed without notice ("we built to the agreed v1 spec; here it is").
The surviving `fw_mpng_helper.py` / `EXCEL_MPNG_*` config is the related, verifiable
artifact of that practice; the runtime mapping *table* itself is not present in the
retained code.

**Why / trade-offs.** A single versioned spec keeps schema, types, mandatory-ness,
source format and partitioning consistent across DDL and load logic — no drift
between "what the table is" and "how we load it", because both are generated from
the same row. Versioning gives an auditable contract that protects the team in a
bank's blame-sensitive, multi-vendor environment. Trade-offs: Excel is a clumsy,
positional (column-index) interface that is easy to break and hard to diff; the
generator's correctness depends on rigid worksheet layout; and generated artifacts
must be regenerated (not hand-edited) or they silently diverge from the spec.

**Reusable lesson.** Keep schema + source-format as a single versioned data
contract, and **generate** DDL, load SQL and pipeline config from it rather than
hand-maintaining each. Version the contract so an upstream surprise becomes a
visible "bump v1→v2 + redeploy" with a defensible paper trail. (Today: prefer a
schema registry / dbt sources + YAML contracts over Excel, but the
single-source-of-truth-with-versioning principle stands.)

---

## Pattern 7 — Idempotent partition-overwrite

**Pattern.** Loads write a whole business-date partition with
`INSERT OVERWRITE ... PARTITION(bsns_dt)` under dynamic partition-overwrite mode,
so re-running a job for a given `bsns_dt` is safe and self-correcting — the latest
run wins, no duplicates, no manual delete.

**How it works (grounded).**
- Dynamic partition overwrite is set once, framework-wide, at module load:
  `spark.conf.set("spark.sql.sources.partitionOverwriteMode","dynamic")`
  (`fw_cmmn_func.py:22`). With dynamic mode, `INSERT OVERWRITE` replaces only the
  partitions present in the written data, not the entire table.
- Tables are created partitioned by `BSNS_DT` (DDL generator
  `fw_mpng_helper.py:103`: `... USING PARQUET PARTITIONED BY (BSNS_DT)`).
- Generated load SQL writes exactly that partition:
  `INSERT OVERWRITE TABLE <db>.<tbl> PARTITION (BSNS_DT) SELECT ... ,
  TO_DATE('${bsns_dt}') AS BSNS_DT FROM ${stg_tbl}` (`fw_mpng_helper.py:200`).
- The RI/promotion path uses the same idiom dynamically:
  `process_ri` derives the partition spec from `DESC TABLE`
  (`get_partition_name`, `fw_cmmn_func.py:935-946`) and runs
  `insert overwrite table ... partition (<par>)` then drops the staged partition
  (`:809-828`).
- Post-load the audit step recounts the target partition
  (`cnt_trgt = ...filter(bsns_dt == bsns_dt).count()`, `fw_ingt_main.py:582`) and
  fails if `cnt_src != cnt_trgt` (`:594-595`) — so re-runs are also reconciled.

**Why / trade-offs.** Per-`bsns_dt` overwrite makes the pipeline replayable: a
failed or corrected run for a date can simply be re-run, and the count-reconcile
audit confirms the result. Combined with Pattern 4's duplicate guard and Pattern
3's latest-run dependency check, the whole framework is safe to re-run by business
date. Trade-offs: dynamic overwrite is non-transactional on plain Parquet (a job
killed mid-overwrite can leave a partition partially written — Delta/atomic-commit
formats mitigate this); and partition granularity = reprocessing granularity, so a
single late record forces rewriting the entire date partition.

**Reusable lesson.** Make business-date the partition key and overwrite the whole
partition on every run; idempotency-by-partition-overwrite is simpler and more
robust than delete-then-insert or merge for full-snapshot daily loads. Always pair
it with a post-load source-vs-target count reconcile so a silent partial write is
caught.

---

## Promote to roles/de-engineer

These patterns are project-agnostic and worth adding to
`/Users/wasin/Documents/Projects/Agent/roles/technical/engineer/de-engineer/knowledge.md`
(listed only — not edited here):

- **Config-driven dispatch / pluggable scripts** — jobs as config rows; per-step
  behavior as named, optional hook modules; keep the orchestrator generic.
- **Externalized parameterized SQL execution** — logic as versioned `${var}` SQL
  fetched + substituted + run by a thin uniform engine; runtime SQL-vs-imperative
  branching.
- **Dependency-as-data with audit-log readiness check** — upstream-ready =
  latest-run-success + row-count gate; pluggable date-policy hook for incremental /
  look-back instead of hardcoded T-1; `.success`-marker fallback for foreign zones.
- **Run-level audit-log state machine** — explicit status lifecycle, at-most-one
  active-run guard, child→batch rollup; log doubles as dependency oracle +
  observability.
- **Fail-loud config/input contract** — validate at job start; exactly-one-active
  -version selection; non-null / flag / path / allow-list checks before side
  effects.
- **Versioned data contract → generated DDL + load SQL + config** — single
  spec-of-truth, generate don't hand-maintain, version for auditable change
  management.
- **Idempotent partition-overwrite by business date** — dynamic
  `INSERT OVERWRITE PARTITION(bsns_dt)` + post-load count reconcile for safe
  replay.
