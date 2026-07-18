# SCB Config-Driven ETL Framework — Architecture

> **Context:** SCB Data Engineering. A config-table-driven, notebook-based ETL framework on
> Azure (Databricks + ADF + SQL Server) that Wasin (Senior Data Engineer) built and operated
> across three platform generations. **Past project — Wasin has left SCB.** This document
> captures the *framework architecture*; the regulatory pipeline stages (BOT/RDT submission
> logic, validation rules, etc.) are covered in a sibling doc.
>
> **Grounding rule:** every technical claim below is verified against the surviving RDT/SCB-DL
> source unless explicitly tagged **(from Wasin's account — original code not retained)**.
> Citations use `file:function` or `file:line`. The two surviving code roots:
> - **RDT FW:** `…/scb_datalake/bk_de_etl_fw/fw(rdt)/fw/`
> - **SCB-DL FW:** `…/scb_datalake/bk_de_etl_fw/wks_dev(scb_dl)/framework/dldev/fw/`

---

## 1. Three-era lineage

The *same architectural concept* — a config-table-driven dispatcher running per-stage notebooks
against a SQL Server control plane — was carried across three platform generations, with the
compute and orchestration layer modernised each time.

| Era | Compute | Orchestration | Business domain | Code status |
|-----|---------|---------------|-----------------|-------------|
| **1. SCB Datalake** (~7–8y ago) | HDInsight; shell-on-VM driving `spark-submit` | Azure Data Factory (ADF) schedules/triggers the VM jobs | General datalake ingestion/transform | **Original code not retained** — described from Wasin's account only |
| **2. SCB RDT** (Regulatory Data … submission) | Azure Databricks (Spark notebooks) | ADF orchestrates *and* performs the file copy (blob→ADLS); Databricks does the load/transform | Regulatory reporting (BOT data submission) | **Surviving** — primary code basis for this doc (`fw(rdt)/`, `wks_dev(scb_dl)/`) |
| **3. CardX RDT** | Fully Azure Databricks, **no ADF** | Databricks-native (notebook/job orchestration; no ADF file-copy step) | Different business logic (CardX) | **(from Wasin's account — original code not retained)** |

**What stayed constant across all three** (the architectural invariant): a control-plane config DB
holding one row per job; a thin dispatcher that reads config and fans out to per-stage runners;
per-stage runners that drive *pluggable, config-named* SQL/Python scripts; and a uniform
log/idempotency model keyed on `(job_nm, bsns_dt, job_id)`.

**What changed era-to-era:** the compute engine (HDInsight → Databricks), and whether ADF was in
the loop. Era-1's `spark-submit`-on-VM was replaced by Databricks notebooks that `%run` a shared
library; era-2 kept ADF only for the data-transfer (copy) activity; era-3 dropped ADF entirely.
The RDT-era continuity is verifiable: the SCB-DL `fw_cmmn_func.py` and the RDT `fw_cmmn_func.py`
share the same `jaydebeapi` JDBC layer, the same dynamic-partition-overwrite setting, and the same
single-active-row `get_config` guarantee (see §5) — confirming the framework concept survived the
compute migration intact.

---

## 2. Architecture overview

Three planes:

1. **Control plane — SQL Server (Azure SQL DB).** A config database (`rdt{ENV}_config`, e.g.
   `rdtdev_config`; SCB-DL: `dldev_config`) holds the job catalogue and run logs. Connection is
   defined in `cmmn/config/environment_config.py:53-64` (`SQLDB_CONF_*`, driver
   `com.microsoft.sqlserver.jdbc.SQLServerDriver`, `database = "rdt%s_config" % ENV`). Credentials
   come from Databricks secret scopes (`dbutils.secrets.get(...)`), never hard-coded.

2. **Dispatch plane — Databricks notebooks.** Every stage is a Databricks notebook. There is no
   monolithic driver: an *area runner* reads a config table, groups jobs, and dispatches each job
   to the per-stage `*_main` notebook via `dbutils.notebook.run(...)`. All notebooks pull the shared
   engine with `# MAGIC %run ../../cmmn/bin/module/fw_cmmn_func` (e.g.
   `ingt/bin/fw_ingt_main.py:14`, `tnfm/bin/fw_tnfm_main.py:7`), which itself `%run`s
   `environment_config` and the auth module (`fw_cmmn_func.py:27,32`).

3. **Data plane — Spark + Delta/Parquet on ADLS/blob.** Actual data movement is expressed as
   *SQL scripts stored as notebooks*, named in config and executed by the engine's SQL-templating
   runner (§4). The engine sets dynamic partition overwrite globally
   (`fw_cmmn_func.py:22`: `spark.conf.set("spark.sql.sources.partitionOverwriteMode","dynamic")`).

The key design property: **adding or changing a pipeline is a config + script change, not a
framework change.** New jobs are rows in `tbl_*_job`; new per-step logic is a new SQL/Python
notebook referenced by a `script_*` column. The Python framework code is generic and rarely touched.

---

## 3. main vs wrapper vs area-wrapper

Three notebook tiers, with a deliberate thin/thick split.

### 3.1 `*_wrapper` — thin entry point
Parses widget params, validates them, generates a `job_id` if absent, then delegates. It holds
**no** job lifecycle logic. Example — `ingt/bin/fw_ingt_wrapper.py`:
- reads `bsns_dt`, `job_nm`, optional `trnf_flag`/`load_flag`/`job_id`/`bypass_dpdc_flag`
  (`fw_ingt_wrapper.py:20-43`);
- validates date + Y/N flags (`:49-52`);
- `if not job_id : job_id = get_job_id(job_nm,bsns_dt)` (`:57`);
- `dbutils.notebook.run(INGT_PATH+"fw_ingt_main", DEFAULT_WRAPPER_TIMEOUT, dict_param)` (`:62`).

`tnfm/bin/fw_tnfm_wrapper.py` is the same shape (`:18-43`). The wrapper is what a human or an
external scheduler invokes for a *single* job.

### 3.2 `*_main` — full job lifecycle
The thick notebook. It owns: config fetch + validation, duplicate-run guard, log INSERT (RUNNING),
the stage work, audit/reconciliation, and log UPDATE (SUCCESS/FAILED). It defines local
`exit_prog_success` / `exit_prog_fail` helpers so *every* exit path writes a terminal log row and
fires an email alert.

- **`fw_ingt_main.py`** lifecycle: read params (`:62-105`) → validate + assign
  (`staging_view`, tmp parquet path, `ingt_upd_where_cond`) (`:111-130`) →
  `get_config("tbl_ingt_job", …)` + `vld_config`/`vld_flag_config`/`vld_path_config` (`:140-152`) →
  `chck_dup_job("tbl_ingt_log", …RUNNING…)` (`:184-185`) → `insert_log` status RUNNING (`:202`) →
  list source files (`:208-226`) → **ADF copy** blob→ADLS with `run_adf_pipeline` and post-copy
  read=write validation (`:236-318`, status `RUNNING-COPY`) → list landing files + `vld_adf_copy_file`
  (`:322-376`) → `RUNNING-LOAD` (`:387-390`) → source validation against control file (`:397-416`) →
  pre-processing into temp parquet + staging temp view (`:420-478`) → **data load** via SQL-notebook
  templating or Python module (`:504-520`) → audit / source-vs-target row-count reconciliation
  (`:524-597`) → `exit_prog_success` (`:603-604`).
- **`fw_tnfm_main.py`** lifecycle: params/validate (`:62-123`) → `get_config("tbl_tnfm_job", …)`
  + validate (`:133-140`) → `chck_dup_job("tbl_tnfm_log", …)` + `insert_log` RUNNING (`:165-183`) →
  **dependency check** (if `chck_dpdc_flag=Y`, runs `fw_cmmn_chck_dpdc`) (`:193-215`) →
  RI config load + manage-table prep (`:224-266`) → **execute transform script** (`:279-326`) →
  **RI check** via `mdle_chk_ri` (`:299-320`) → audit (`:335-351`) → `exit_prog_success` (`:356-357`).

### 3.3 `fw_cmmn_area_wrapper.py` — the area runner (multi-job dispatcher)
This is the orchestration heart. It runs a whole *area* (a logical batch of jobs) in dependency
order with bounded parallelism.

- **Input:** `bsns_dt`, `area_nm` (`fw_cmmn_area_wrapper.py:23-34`).
- **Config:** `get_config("tbl_cmmn_area","WHERE area_nm ='"+area_nm+"'", True)` then validates
  not-null / flag / list-of-value, and rejects duplicate `(job_type, job_nm)` (`:63-78`).
- **Sequencing:** iterates `job_seq` from `min` to `max` (`:152-163`); for each `job_seq` it
  collects all rows with that sequence and runs them **in parallel**:
  ```python
  with ThreadPoolExecutor(AREA_MAX_JOB_PARALLEL) as pool:
      results = pool.map(execute_job, seq_df.collect())
  ```
  `AREA_MAX_JOB_PARALLEL = 2` (`environment_config.py:113`). So *same-sequence jobs run
  concurrently (2 at a time); different sequences run strictly in order* — a simple, config-driven
  dependency model.
- **Dispatch map** (`execute_job`, `:113-137`): `job_type` selects the target `*_main` notebook:

  | `job_type` | Target notebook |
  |-----------|-----------------|
  | `INGT` | `INGT_PATH + "fw_ingt_main"` |
  | `TNFM` | `TNFM_PATH + "fw_tnfm_main"` |
  | `OUTBND` | `OUTBND_PATH + "fw_outbnd_main"` |
  | `STRM` | `STRM_PATH + "fw_strm_main"` |
  | `UTLT` | `UTLT_PATH + "fw_utlt_main"` |
  | `VLD` | `VLD_PATH + "fw_vld_main"` (extra params: `batch_nm`, `mode='RERUN'`) |

  The allowed set is enforced as config validation:
  `AREA_CONFIG_LIST_OF_VAL = {'job_type':['INGT','TNFM','OUTBND','STRM','UTLT','VLD']}`
  (`environment_config.py:112`).
- **Per-job:** generates `job_id`, runs `dbutils.notebook.run(adb_notebook_path,
  DEFAULT_WRAPPER_TIMEOUT, dict_param)`, captures SUCCESS/FAILED (`:142-150`).
- **After all sequences:** updates each per-type log table's `area_end_*` columns
  (`update_log("tbl_ingt_log"/"tbl_tnfm_log"/…)`, `:198-256`), builds a result-summary DataFrame,
  sends an area email alert, and finally raises if *any* job failed (`:301-325`).

Note the deliberate asymmetry: the area runner calls `fw_*_main` **directly** (not the thin
wrapper), because it already generates the `job_id` and passes the area context
(`area_nm`, `area_strt_dt`, `job_seq`) so the `*_main` lifecycle can stamp it into the log.

---

## 4. Common engine — `cmmn/bin/module/fw_cmmn_func.py`

The shared library `%run` by every notebook. It is the framework's standard library. Key surface:

**Date / id / printing.** `get_current(dt_type)` (Asia/Bangkok tz, `:41-52`); `chck_bsns_dt`
(accepts `YYYY-MM-DD` or `YYYYMMDD`, else raises, `:57-64`); `get_job_id(job_nm,bsns_dt)` →
`JOB_NM_YYYYMMDD_yyyymmdd_HHMMSS` (`:128-130`); `print_std`/`print_info` structured logging.

**Config + validation.** `get_config` (§5); `vld_config` (not-null), `vld_flag_config` (Y/N),
`vld_path_config` (trailing slash), `vld_val_config` (list-of-value + uppercase enforcement)
(`:162-220`). Config-driven not-null/flag/path/value column sets live in `environment_config.py`
per stage (e.g. `INGT_CONFIG_COL_NOT_NULL`, `TNFM_CONFIG_COL_FLAG`).

**Logging (control-plane writes).** `insert_log` / `update_log` build SQL against the config DB
and execute over JDBC; `insert_log` only writes columns present in the target table schema
(introspected via `select top 0 *`) and drops empty values (`:225-299`). `chck_dup_job` (§6).

**SQL Server JDBC layer.** `sql_exec(query)` uses `jaydebeapi.connect(...)` for DML/DDL;
`sql_select(query)` uses `spark.read.jdbc(... table=f"({query}) qry" ...)` for reads
(`:567-585`). All config reads/writes go through these two functions — the framework never assumes
the config tables are Spark tables.

**Databricks REST helpers.** `get_notebook_content` (Workspace `export` API, base64-decoded),
`get_notebook_language` (Workspace `list` API), `api_run_notebook`, `api_get_run_info`,
`get_run_info` (resolves the run URL written into the log as `job_log`), `export_log`,
`api_jobs_runs_list/cancel/submit`, `get_cluster_template` (builds a cluster spec from a config
`clstr_ppty` string) (`:317-700`).

**ADF REST helpers.** `get_access_token` (Azure AD client-credentials), `run_adf_pipeline`,
`get_adf_run_info`, `get_adf_run_dtl`, and `vld_adf_copy_file` — which reconciles ADF Copy activity
`filesRead == filesWritten`, file count, and per-file size against the blob landing files
(`:444-544`). This is the ADF-era file-transfer integration (era 2).

**RI (referential-integrity) engine.** `process_ri(dict_ri, config_ri_df)` (`:705-830`): for each
RI rule row it runs a NOT-NULL check and/or a left-anti-join orphan check
(`src LEFT JOIN ri … WHERE ri.key IS NULL`), records per-rule status in `tbl_ri_log`, and — only if
all FAILED-action rules pass — promotes the data from the framework prep DB into the real curated
table via `INSERT OVERWRITE … PARTITION(...)` then drops the prep partition. `get_desc_table_name` /
`get_partition_name` / `create_manage_table` discover the partition spec dynamically from
`DESCRIBE`. In RDT, `fw_tnfm_main.py` invokes this as a separate notebook `mdle_chk_ri`
(`fw_tnfm_main.py:307-320`).

### 4.1 The SQL-notebook templating executor — `exec_sql_notebook` (highlight)

This is the mechanism that makes the framework "config-driven SQL". `exec_sql_notebook(adb_notebook_path,
replace_var, insert_vld=False)` (`fw_cmmn_func.py:857-879`):

1. **Fetch** the SQL script's source via the Workspace export API (`get_notebook_content`) — the
   script lives as a notebook in the workspace, not on disk.
2. **Substitute variables.** It rewrites `${var}` → `{var}` (`data.replace("${","{")`) then
   `.format(**replace_var)`, where `replace_var` is the per-stage `*_REPLACE_VAR` dict
   (`eval`-ed). For ingest, `INGT_REPLACE_VAR` supplies `env`, `bsns_dt`, `bsns_dt_yyyymmdd`,
   `stg_tbl` (the staging view), `trgt_tbl_nm`, `trgt_db_nm`, etc.
   (`environment_config.py:131-146`); for transform, `TNFM_REPLACE_VAR` (`:175-189`).
3. **Split & execute cell-by-cell.** It splits the text on the cell delimiter
   `SQL_SPLIT_CELL = '-- COMMAND ----------'` (`environment_config.py:81`), then each cell on
   `SQL_SPLIT_CMD = ';'` (`:82`). Each statement is comment-stripped with `sqlparse.format(...,
   strip_comments=True)` and run individually via `spark.sql(clean_cmd)`; blank statements are
   skipped.

A variant `exec_sql_notebook_rtn` (`:883-918`) additionally rewrites a trailing `WHERE <cond>`
into `WHERE not(<cond>)` — used by the validation stage to count rule-violating rows and return a
DataFrame.

The engine also **switches on notebook language**: `get_notebook_language` lets `*_main` run the
config-named script either as templated SQL (`exec_sql_notebook`) or as a parameterised Python
notebook (`run_notebook`) — see `fw_ingt_main.py:508-520` and `fw_tnfm_main.py:286-297`.

**Why it matters:** pipeline authors write plain parameterised SQL (`${bsns_dt}`, `${stg_tbl}`,
`${env}`) and register the script name in a config column. The engine handles fetch, templating,
splitting, comment-stripping, and per-statement execution — no per-pipeline Python.

---

## 5. Config model

The config DB is the framework's API. Each stage has a **job-catalogue** table and a **run-log**
table; plus cross-cutting `tbl_cmmn_area` (orchestration) and `tbl_cmmn_dpdc` (dependencies).

| Table | Role | DDL |
|-------|------|-----|
| `tbl_ingt_job` | Ingest job catalogue | `init/tbl_init_ingt_config_table.sql:8-27` |
| `tbl_ingt_log` | Ingest run log (partitioned `bsns_dt,job_nm`) | `:32-59` |
| `tbl_tnfm_job` | Transform job catalogue | `tbl_init_tnfm_config_table.sql:8-17` |
| `tbl_tnfm_log` | Transform run log | `:22-43` |
| `tbl_cmmn_area` | Area → ordered list of `(job_type, job_nm, job_seq, job_hldy_flag)` | `tbl_init_cmmn_area.sql:8-14` |
| `tbl_cmmn_dpdc` | Per-job upstream dependencies | `tbl_init_cmmn_dpdc.sql:8-16` |
| `tbl_ri_config` / `tbl_ri_log` | RI rules + RI results | `init/tbl_init_ri_config_table.py` |
| `tbl_outbnd_job` / `tbl_outbnd_log`, `tbl_vld_*`, `tbl_strm_*`, `tbl_utlt_*`, `tbl_schm_sync_*`, `tbl_email_alrt_config/log` | other stages | various `init/` DDLs |

Config DB name is `rdt{ENV}_config` (RDT) / `dldev_config` (SCB-DL)
(`environment_config.py:59,87`).

### 5.1 `script_*` columns = pluggable per-step notebooks (the extension mechanism)

The job-catalogue tables don't store logic — they store the **names of notebooks to run at each
step**. `tbl_ingt_job` (`tbl_init_ingt_config_table.sql:8-27`) has a full pipeline-as-columns:

```
script_list_src_file   -- how to enumerate source files
script_ctl_file_vld     -- control-file validation
script_pre_proc         -- pre-processing (parser per file format)
script_qlty             -- quality check
script_load             -- the raw→persist load SQL  (mandatory)
script_audt             -- custom audit (else default)
```

`fw_ingt_main.py` reads each of these (`:169-174`) and, at the matching lifecycle step, runs the
named notebook from the matching module folder (e.g. `INGT_MODULE_LIST_FILE_PATH + script_list_src_file`,
`:210`; `INGT_LOAD_PATH/<src_sys>/<script_load>`, `:506`). Empty `script_*` ⇒ step skipped
(e.g. `:381-383`, `:422`). `tbl_tnfm_job` is analogous with `script_tnfm` (the transform) and
`script_audt`, plus `subj_area` to namespace the script path and `chck_dpdc_flag` to gate the
dependency check (`tbl_init_tnfm_config_table.sql:8-17`, used at `fw_tnfm_main.py:150-152,281`).

This is the core extensibility: **new behaviour = new notebook + a config cell**, with reusable
modules (Excel/XML/SAS/Parquet/delimited readers under `ingt/bin/module/pre_proc/`; custom audit
under `…/audt/`; custom dependency under `cmmn/bin/module/cstm_dpdc/`).

### 5.2 `get_config` — single-active-row guarantee (fail-loud-at-config)

`get_config(tbl_nm, where_cond, tbl_area=False, chck_cnt=True)` (`fw_cmmn_func.py:135-157`) reads
the config row(s) over JDBC and, for job tables, enforces **exactly one active row**:

```python
actv_y_cnt = conf_df.filter("UPPER(actv_flag) = 'Y'").count()
...
if   actv_y_cnt == 0 and actv_n_cnt == 0: raise "Configuration not found"
elif actv_y_cnt == 0:                      raise "Active configuration not found (Inactive found)"
elif actv_y_cnt  > 1:                      raise "Duplicate active configuration found"
```

So a job with zero, only-inactive, or multiple active rows fails *immediately at config read*,
before any data is touched. `actv_flag='N'` is a soft delete (per the column comment in
`tbl_init_tnfm_config_table.sql:54`). `tbl_cmmn_area` is read with `tbl_area=True` (the area is a
multi-row set), so the single-active-row rule is skipped there — but the area runner instead
enforces no-duplicate `(job_type, job_nm)` (`fw_cmmn_area_wrapper.py:75-76`). This single-active-row
guarantee is identical in the SCB-DL era engine (`wks_dev(scb_dl)/…/fw_cmmn_func.py:141-142`),
confirming it as a cross-era invariant.

---

## 6. Data layers

The framework's logical data flow (confirmed by Wasin):

```
source  →  raw (landing)  →  persist (standardized)  →  curated (transforms)  →  outbound
```

- **source** — the system-of-origin files (delimited / Excel / XML / SAS7BDAT / Parquet).
- **raw / landing** — files copied into the lake (ADF copy in era 2) and read into a Spark staging
  temp view; in `fw_ingt_main.py` this is `staging_view = job_nm+"_"+bsns_dt` created from the
  pre-processed parquet (`:123,474`).
- **persist** — a *standardized* table conforming to the target schema. **An ingest job creates
  BOTH the raw and persist representations and runs a `script_load` that standardizes raw→persist**
  *(from Wasin's account)*. The canonical shape of that load SQL is an `INSERT OVERWRITE …
  PARTITION(bsns_dt)` that casts/renames raw columns into the persist schema, e.g.:

  ```sql
  INSERT OVERWRITE TABLE persist.a PARTITION (bsns_dt)
  SELECT raw.cola AS cola, ...
       , TO_DATE('${bsns_dt}') AS bsns_dt
  FROM   ${stg_tbl};
  ```

  *(layer names `raw`/`persist` from Wasin's account.)* The **mechanism** is verifiable in a
  surviving load script — same templating and partition pattern, though it targets a `*_src_*` DB
  in that particular (different) project, so it is cited only as evidence of the load idiom, not as
  the canonical layer name:
  `wks_dev(scb_dl)/…/dlrdt/job/ingt/script/fes/tbl_load_user_edit_hist_cc.sql:7,44`
  (`INSERT OVERWRITE TABLE ${env}_src_fes_db.user_edit_hist_cc PARTITION (bsns_dt) SELECT cast(...)
  … TO_DATE('${bsns_dt}') as bsns_dt FROM ${stg_tbl}`).

  > **Naming caveat:** an early code dump showed a `src`-prefixed DB; that was a *different*
  > project. Do **not** treat `src` as the canonical layer name — the canonical layers are
  > **raw → persist**.

- **curated** — derived from persist via transform jobs (`tbl_tnfm_job` / `script_tnfm`). Curated
  tables all derive from persist *(from Wasin's account)*; the transform stage writes into the
  target curated DB/table, with the RI engine optionally staging through a `*_fw_prep_db` before
  promoting into the curated table (`fw_cmmn_func.py:process_ri:808-829`).
- **outbound** — export jobs (`OUTBND`, `fw_outbnd_main`) that materialize files (delimited export,
  control-file generation, BOT encryption post-proc) from curated tables.

---

## 7. Idempotency & replay

Two complementary guarantees make any business date safe to re-run:

1. **Concurrency guard — `chck_dup_job`.** Before inserting a RUNNING log row, `*_main` queries the
   log for an existing in-flight run of the same `(job_nm, bsns_dt)`:
   ```python
   where_cond = "WHERE job_nm ='"+job_nm+"' AND bsns_dt ='"+bsns_dt+"' AND job_sts LIKE '%RUNNING%'"
   chck_dup_job("tbl_ingt_log", where_cond)   # raises if any RUNNING/RUNNING-COPY/RUNNING-LOAD row exists
   ```
   (`fw_ingt_main.py:184-185`, `fw_tnfm_main.py:165-166`; impl `fw_cmmn_func.py:114-123`). Because
   the status passes through `RUNNING → RUNNING-COPY → RUNNING-LOAD → SUCCESS/FAILED`
   (`fw_ingt_main.py:239,389,603` and `exit_prog_fail`), the `LIKE '%RUNNING%'` test blocks any
   overlapping execution of the same job/date.

2. **Replayable writes — dynamic partition overwrite.** The engine globally sets
   `spark.sql.sources.partitionOverwriteMode = dynamic` (`fw_cmmn_func.py:22`), and load/transform
   scripts write with `INSERT OVERWRITE … PARTITION(bsns_dt)`. Re-running a business date therefore
   **replaces exactly that date's partition** and leaves other partitions untouched — no duplicate
   rows, no manual cleanup. The RI promotion path does the same and then explicitly drops the prep
   partition (`process_ri:808-829`). Log/run tables are also partitioned by `(bsns_dt, job_nm)`
   (`tbl_init_ingt_config_table.sql:59`, `tbl_init_tnfm_config_table.sql:43`).

Every `*_main` exit path (success *and* failure) writes a terminal status row and fires an email
alert via local `exit_prog_success` / `exit_prog_fail`, so a re-run always starts from a clean,
known state and the operator always has a record (`fw_ingt_main.py:20-51`,
`fw_tnfm_main.py:17-47`).

---

## 8. What Wasin demonstrated here (CV-ready)

- **Designed and built a config-driven ETL framework on Azure Databricks** that turns new pipelines
  into config rows + parameterised SQL — no framework code change per pipeline — backed by a SQL
  Server control plane (job catalogue + run logs) accessed over JDBC (`jaydebeapi` / Spark JDBC).
- **Authored a metadata-driven dispatcher/orchestrator** (`fw_cmmn_area_wrapper`) that sequences
  jobs by `job_seq`, runs same-sequence jobs in parallel via a bounded `ThreadPoolExecutor`, and
  fans out by `job_type` (INGT/TNFM/OUTBND/STRM/UTLT/VLD) to per-stage runners.
- **Implemented a SQL-notebook templating engine** (`exec_sql_notebook`): fetches scripts via the
  Databricks Workspace API, performs `${var}` substitution, splits into cells/statements,
  comment-strips with `sqlparse`, and executes statement-by-statement — with language detection to
  run either templated SQL or parameterised Python.
- **Engineered fail-loud config validation** — a single-active-row (`actv_flag='Y'`) guarantee plus
  not-null / flag / path / list-of-value checks — so bad configuration fails before any data is
  written.
- **Built idempotent, replayable pipelines** using a RUNNING-status concurrency guard
  (`chck_dup_job`) and dynamic-partition `INSERT OVERWRITE PARTITION(bsns_dt)`, making any business
  date safe to re-run.
- **Implemented a referential-integrity / data-quality engine** (NOT-NULL + left-anti-join orphan
  checks) that gates promotion from a framework prep DB into curated tables and logs per-rule
  results.
- **Integrated Azure Data Factory** for blob→ADLS file transfer with post-copy reconciliation
  (files read = written, file count, per-file size) before loading.
- **Operability:** structured logging, run-URL capture into the log, and config-driven email
  alerting (fail/success/always × severity).
- **Carried one architecture across three platform generations** (HDInsight + spark-submit + ADF →
  Databricks + ADF → Databricks-only / CardX), modernising compute and orchestration while keeping
  the config-driven model and idempotency contract intact.
