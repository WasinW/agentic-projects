# RDT Regulatory Data Pipeline (SCB)

> **RDT = Regulatory Data Transformation.** The SCB data platform that turns curated banking data into the data sets a Thai commercial bank is legally required to submit to the **Bank of Thailand (BOT)**, the country's banking regulator. **Past project.** Wasin worked here as a **Senior Data Engineer** and owned the framework modules **validate (`vld`)**, **predefine / hotfix**, and **schema sync (`schm_sync`)**, plus the regulatory **credit domains** (credit movement, interest, credit line).
>
> This doc covers the **RDT pipeline + its stages + regulatory domain context**. For the generic config-driven engine internals (wrappers, `tbl_*_log` patterns, ADF/ADB orchestration, common functions) see the sibling doc **`framework-architecture.md`**.

Code grounding root (all `file:func/line` citations below):
`.../bk_de_etl_fw/fw(rdt)/fw/` — dated/`_bk`/`_test`/`_orig` clones ignored.

---

## 1. What RDT is and why it exists

Every Thai bank must periodically report a defined set of regulatory data sets to the BOT (loan books, credit lines, interest, counterparties, collateral, account movements, etc.). The reports follow a **BOT-mandated data model** (fixed entities, columns, code lists, referential rules) and are submitted as **encrypted files** that only the BOT can decrypt. RDT is SCB's implementation of that obligation: a controlled pipeline that takes the bank's curated data, reshapes it to the regulator's model, proves it is correct, repairs known defects so wrong data is never sent, and submits it.

Two delivery contexts existed *(from Wasin's account)*:
- **SCB RDT (Databricks + ADF era):** Azure Data Factory triggers a Databricks (ADB) notebook → the notebook reads its config → runs validation + dependency/incremental checks → executes → stamps the relevant `*_log` table → the job cluster is terminated. (See `framework-architecture.md` for the ADF↔ADB handshake.)
- **CardX RDT:** fully ADB-orchestrated, **no ADF**.

The whole platform is **config-driven**: behaviour per job lives in `{env}_config.tbl_*` tables; framework code reads config, never hardcodes a report.

### Data-zone topology (grounds the stages)
`init/db_init_rdt_datazone.py` creates the RDT medallion zones on ADLS Gen2 (`scbrdtseasta001adls{env}`), each split by **entity group** (`entity_grp`):

| Zone (db pattern) | ADLS container | Role in the pipeline |
|---|---|---|
| `{env}_persist_dss_db` | `rdt-persistence` | ingested source (from the datalake curated zone) |
| `{env}_cmmnprep_db`, `{env}_cmmn_db` | `rdt-curated` | common transform / shared dimensions |
| `{env}_model_<grp>_db` | `rdt-curated` | **the regulator data model** (the "model" stage output) |
| `{env}_modelhotfix_<grp>_db` | `rdt-curated` | **predefine / hotfix** working + corrected data |
| `{env}_fw_prep_db` / `{env}_fwprep_db` | `rdt-curated` | RI staging before promotion to model |
| `{env}_sbmtprep_db`, `{env}_sbmt_<grp>_db` | `rdt-submission` | submission-ready data sets |

Entity groups present in code (`db_init_rdt_datazone.py:26-191`): `cracct` (credit account), `appl` (application), `cltrl` (collateral), `cnprty` (counterparty), **`crline` (credit line)**, **`int` (interest)**, **`crmvmt` (credit movement)**, `rvw`, `otd`. **Wasin's three owned domains — credit movement, interest, credit line — each map to a real `crmvmt` / `int` / `crline` zone triad** (`model_*`, `modelhotfix_*`, `sbmt_*`). Every zone also has an `_acl_db` twin for the SQL-endpoint/ACL layer.

---

## 2. The 6-stage pipeline

The conceptual flow Wasin described is **ingest → transform → model → validate → predefine → submission**. In code these are realized by the framework modules below. Important up front: **there is no standalone `model/` or `predf`/`predefine` module in the RDT tree** (confirmed by exhaustive search of the non-clone tree). Those two conceptual stages are realized through other modules + zone conventions, documented explicitly under each stage.

### Stage 1 — Ingest (`ingt`)
**Purpose:** pull the upstream source (curated outputs of the datalake framework) into the RDT persistence zone.

**Implemented in** `ingt/bin/fw_ingt_main.py` with reader modules under `ingt/bin/module/`:
- `pre_proc/` readers for the source formats RDT consumes — standard delimited (`mdle_cmmn_read_stnd_delim.py`), parquet (`mdle_cmmn_read_parquet.py`), SAS7BDAT (`mdle_cmmn_read_sas7bdat.py`), Excel (`mdle_cmmn_read_excel.py`), XML (`mdle_cmmn_read_xml.py`), JSON patch (`mdle_ptch_json.py`).
- `list_file/` landing-/source-file listing (`mdle_cmmn_list_landing_file.py`, `mdle_cmmn_list_src_file.py`).
- `ctl_vld/` source/control-file validation at ingest (`mdle_cmmn_src_vld.py`, `mdle_rt_src_vld.py`).
- `audt/` row-count / business-date audit (`cstm_audt_wth_dl_data_dt.py`, `cstm_audt_wthot_bsns_dt.py`).

Config table: `init/tbl_init_ingt_config_table.py`. Output lands in `{env}_persist_dss_db` (`rdt-persistence`).

### Stage 2 — Transform (`tnfm`)
**Purpose:** reshape ingested data toward the regulator model (joins, derivations, code mapping).

**Implemented in** `tnfm/bin/fw_tnfm_main.py`. Per-job config in `tbl_tnfm_job` drives `trgt_tbl_nm`, `trgt_db_nm`, **`subj_area`** (the transform subject area / sub-folder), `script_tnfm` (the SQL/Python transform notebook), `script_audt`, and `chck_dpdc_flag` (`fw_tnfm_main.py:147-154`). The engine: validates config → checks duplicate-run → optional dependency check → runs the transform script → optional **RI check** → data audit → stamps `tbl_tnfm_log` (`fw_tnfm_main.py:133-357`). The transform notebook path is `TNFM_TNFM_PATH/<subj_area>/<script_tnfm>` (`fw_tnfm_main.py:281`).

### Stage 3 — Model (regulator data model)
**Purpose:** shape data into the **BOT-required data model** — the canonical regulatory entities/columns — ready for validate. Wasin: *"comes from cmmn's last step."*

**How it is actually implemented (verified):** there is **no `model/` module**. The model layer is a **`tnfm` transform whose target is a `{env}_model_<grp>_db` table**, gated by a **referential-integrity (RI) check + promotion**:
- The transform writes into an RI staging table in `{env}_fw_prep_db` (`fw_tnfm_main.py:235-264` chooses `fw_prep_db` + `ready_trgt_tbl_nm` when RI config exists, else writes the target directly).
- RI is enforced by `tnfm/bin/module/chk_ri/mdle_chk_ri.py`, driven by `tbl_ri_config` (`init/tbl_init_ri_config_table.py`): per check it runs **not-null checks** and **left-join RI checks** (`mdle_chk_ri.py:90-129`), logging each to `tbl_ri_log`. A check with `action='WARNING'` passes-with-warning; `action='FAILED'` blocks promotion.
- **Promotion to the model table only happens if every blocking check passed** (`cnt_sts == 0`): `INSERT OVERWRITE TABLE <chk_db>.<chk_tbl> PARTITION(...) SELECT * FROM <fw_prep_db>.<ready_trgt_tbl_nm>` then drops the prep partition (`mdle_chk_ri.py:158-189`).

So the "model" stage = **transform-into-`model_<grp>`-db + RI-checked promotion**, not a dedicated module. *(Uncertainty: the exact mapping of which `tnfm` jobs constitute "cmmn's last step" is config/data-driven and not fully recoverable from framework code alone — this is from Wasin's account.)*

### Stage 4 — Validate (`vld`) — *Wasin's module*
**Purpose:** prove the modeled data satisfies the regulator's correctness rules before anything is corrected or submitted. See deep-dive §3.

**Implemented in** `vld/bin/fw_vld_main.py`. Rules in `tbl_vld_rule` (`init/tbl_init_validation_config_table.py`), two-level logging in `tbl_vld_log` + `tbl_vld_entity_log`, violations in `tbl_vld_err_log`.

### Stage 5 — Predefine / hotfix — *Wasin's module, the distinctive one*
**Purpose:** after validate flags failing records, apply **rule-based DEFAULT values** under defined conditions — a regulatory **cleansing layer** so wrong data is **never** submitted to BOT. Output: (a) a cleaned/corrected data set, and (b) the bad records extracted and routed to hotfix. See deep-dive §4.

**How it is actually implemented (verified):** there is **no `predf`/`predefine` module** in the RDT tree. The capability is realized through the **`{env}_modelhotfix_<grp>_db` zone** (`db_init_rdt_datazone.py:80-131`) — one hotfix database per entity group, including `modelhotfix_crmvmt`, `modelhotfix_int`, `modelhotfix_crline` (Wasin's domains). The validation engine itself is **hotfix-aware**: it resolves its working database to `"{env}_modelhotfix_{entity_grp}_db"` (`fw_vld_main.py:328`). The predefine/correction logic lives as **domain SQL/Python notebooks executed via the framework against the `modelhotfix` zone**, keyed by `entity_grp`, rather than as a generic framework module. *(The rule-based-defaulting business logic and the bad-record extraction-to-hotfix behaviour are from Wasin's account; the framework code confirms the hotfix zone, the per-group databases, and the validator's hotfix database resolution.)*

### Stage 6 — Submission (`sbmt` + `outbnd`) — to BOT
**Purpose:** package the submission-ready data set and deliver it to BOT, encrypted with the BOT certificate. See deep-dive §5.

**Implemented in** `sbmt/bin/fw_sbmt_main.py` (orchestrates validate → build-data, keyed by `req_sbmt_key`) and `outbnd/bin/fw_outbnd_main.py` + `outbnd/bin/module/post_proc/mdle_enc_bot.py` (export + BOT encryption to `rdt-submission`).

---

## 3. Validation engine deep-dive (`vld/bin/fw_vld_main.py`) — Wasin's module

The validation engine is the data-quality gate of the whole pipeline. Its design is the part most worth understanding.

### 3.1 The `not(...)` trick — rules express the *passing* condition
Validation rule notebooks are authored as the **PASSING** predicate (the condition that *should* hold). The framework inverts it to SELECT the **violations**. In `cmmn/bin/module/fw_cmmn_func.py:exec_sql_notebook_rtn` (line 905), every command's `WHERE` clause is rewritten:

```python
len_to_where = cmd_find_where + len("WHERE ")
cmd = "%s%s%s%s" % (cmd[0:len_to_where], "not(", cmd[len_to_where:len(cmd)], ")")
```

i.e. `... WHERE <passing_condition>` becomes `... WHERE not(<passing_condition>)`, so the query returns exactly the rows that **fail** the rule. This lets rule authors write rules in the intuitive "what good data looks like" form while the engine consistently produces a violation set. The returned dataframe is the evidence; if `rtn_df.count() > 0` the `vld_id` is marked **not pass** (`fw_vld_main.py:466-470`).

### 3.2 Effective-dated, per-entity + global rules
Rules come from `tbl_vld_rule` (`tbl_init_validation_config_table.py:64-79`; PK `vld_id, eff_strt_dt`). The engine loads rules for the entity where `bsns_dt between eff_strt_dt and eff_end_dt and actv_flag='Y'` (`fw_vld_main.py:263`), then **unions the global `entity_nm='ALL_ENTITY'` rules** so cross-cutting checks apply everywhere (`fw_vld_main.py:276-279`). Rules are further filtered by frequency (`vld_freq` like `%D%`/`%M%` vs the job's `job_freq`).

### 3.3 NORMAL vs RERUN
- **NORMAL** (`fw_vld_main.py:288-314`): left-joins the rule set against successful rows in `tbl_vld_log` for this `job_nm/vld_tbl_nm/bsns_dt`; runs **only the `vld_id`s that have not already passed**. If all rules already passed, it exits early (skip-run, line 302-307). This makes re-execution cheap and idempotent.
- **RERUN** (`fw_vld_main.py:315-317`): runs **all** rules regardless of prior status.

### 3.4 Two-level logging + error log
- `tbl_vld_entity_log` — one row per entity run (RUNNING → SUCCESS/FAILED), `actv_flag` toggled so only the latest run is active (`fw_vld_main.py:341-357`).
- `tbl_vld_log` — one row per `vld_id` (NOT_START → RUNNING → SUCCESS/FAILED) (`fw_vld_main.py:372-389`, `410-474`).
- `tbl_vld_err_log` — the actual **violating records / column-level diffs** (`fw_vld_main.py:118-153`; schema in `tbl_init_validation_config_table.py:21-41`: `rdt_col_nm/rdt_col_val/dms_col_nm/dms_col_val/dms_diff_pcent/...`). Before each `vld_id` runs, the prior error rows are deactivated (`update_tbl_err_log`, `fw_vld_main.py:69-78`), keeping the latest violation set authoritative.

The engine also runs a **dependency check** per `vld_id` against `tbl_vld_dpdc` (must find a SUCCESS `tbl_tnfm_log` row, optionally with `cnt_trgt > 0`) before validating (`fw_vld_main.py:82-114`, `416-419`).

---

## 4. Predefine / hotfix deep-dive — the regulatory-correctness story (Wasin owned this)

This is the step that distinguishes a *correct* regulatory submission from a merely *transformed* one, and it is the part Wasin owned end-to-end.

**The problem it solves:** validation (§3) tells you which records are wrong against the BOT rules. But the bank still has a legal obligation to submit a *complete, valid* report on time. You cannot simply drop wrong rows, and you cannot submit wrong values. Predefine is the **rule-based remediation layer** that sits between validate and submission.

**What it does (from Wasin's account, grounded where possible):**
1. For records that FAIL a validation rule, apply **predefined DEFAULT values** under defined per-rule/per-column conditions — e.g. substituting a regulator-acceptable default code/value where the source value violates a BOT constraint. The logic is **regulatory-domain-specific** and authored per entity group.
2. Produce two outputs:
   - **(a)** the **cleaned / corrected data set** that proceeds toward submission, and
   - **(b)** the **bad records, filtered out and routed to hotfix** for human follow-up, so defects are tracked and fixed at source over time rather than silently masked.

**Where it lives in code (verified):** the **`{env}_modelhotfix_<grp>_db` databases** (`db_init_rdt_datazone.py:80-131`), one per entity group (`cracct, appl, cltrl, cnprty, crline, int, crmvmt, rvw, otd`). The validation engine resolves its operating database to `"{env}_modelhotfix_{entity_grp}_db"` (`fw_vld_main.py:325-330`), confirming that validation + correction operate against this hotfix zone keyed by `entity_grp`. The defaulting/cleansing notebooks themselves are domain scripts executed through the framework (config-driven), not a generic module — which is why no `predf` module exists.

**Why it matters (CV framing):** this is a domain-heavy, correctness-critical data-quality design: it guarantees the invariant *"no value that fails a BOT rule is ever submitted"* while preserving completeness and producing an auditable bad-record trail. Owning it across `crmvmt`/`int`/`crline` means owning both the engine behaviour and the regulatory semantics of three credit data domains.

---

## 5. Submission to BOT (`sbmt` + `outbnd`)

### 5.1 Submission orchestration (`sbmt/bin/fw_sbmt_main.py`)
A submission is keyed by **`req_sbmt_key`** (config `tbl_sbmt_req`, `tbl_init_sbmt_table.py:11-29` — carries `sbmt_tbl_nm, entity_nm, freq, bsns_dt`, plus adjustment metadata `adj_flag/adj_reason_type_id/adj_detail/version_key` for restatements). The orchestrator (`fw_sbmt_main.py`):
1. **Validate** — re-runs the validation job for the entity in **RERUN** mode (`adb_notebook_path = VLD_PATH + "fw_vld_main"`, `mode="RERUN"`, `batch_nm="RDTAPP"`, `fw_sbmt_main.py:128-157`). Submission therefore re-proves correctness immediately before sending.
2. **Build data** — runs the `tnfm` job whose config has **`subj_area='sbmt'`** and `trgt_tbl_nm = sbmt_tbl_nm` (`fw_sbmt_main.py:161-184`), materializing the submission-ready table in the `sbmt` zone.
3. Logs every step (Validate / Build data / BOT Submission) to **`tbl_sbmt_log`** with `sbmt_area` + `sbmt_step` (`tbl_init_sbmt_table.py:35-49`), guarding against duplicate RUNNING submissions (`fw_sbmt_main.py:120-123`).

### 5.2 Submission column zones Z4 / Z5
The framework defines two BOT submission column-set profiles (`cmmn/config/environment_config.py:475-476`):
```python
SBMT_COL_FW_Z4_LIST = ["etl_key","always_adjust_flg","rec_src_tbl","rec_newkey_sts"]
SBMT_COL_FW_Z5_LIST = ["etl_key","always_adjust_flg","rec_src_tbl","rec_newkey_sts","rec_chng_sts","rec_hash_value"]
```
Z5 carries the extra change-tracking columns (`rec_chng_sts`, `rec_hash_value`) used for change/restatement detection on top of the Z4 base set.

### 5.3 BOT certificate encryption (`outbnd/bin/module/post_proc/mdle_enc_bot.py`)
The export is delivered through `outbnd/bin/fw_outbnd_main.py`, which after building the delimited export file runs a **post-process** step (`fw_outbnd_main.py:372-403`) — for BOT, `mdle_enc_bot.py`. Encryption is done by invoking **PowerShell** + a .NET library on the cluster:
- Certificates/lib resolved from config (`environment_config.py:227-230`): `CERFORENCRYPT = .../BOTDACertificate.cer` (BOT public cert, used to encrypt), `CERFORENSIGN = .../BOTDACertificate2.cer` (SCB cert), `CERMODULE = .../DAEncryptionLib.dll`.
- The PowerShell script loads both X509 certs and calls `[DAEncryptionLib.DAEncryption]::EncryptionProcessWrapper($inputFilePath, $EncryptedPath, $X509cerForEnSign, $X509cerForEncrypt, $isSign)` (`mdle_enc_bot.py:161-185`).
- The encrypted output gets the **`.bot`** extension and is copied to the export location in the `rdt-submission` container (`mdle_enc_bot.py:200-216`).

The result is an encrypted, BOT-decryptable file — the actual artifact the bank submits to the regulator.

---

## 6. Schema sync (`schm_sync/bin/fw_schm_sync_main.py`) — Wasin's module

Schema sync keeps the RDT table definitions in lockstep with upstream schema changes from the datalake, so an upstream column add/drop/type-change does not silently break the regulatory model.

- **Inputs:** schema-extract files from the **persist** zone — an **update** file (current schema) and an **obsolete** file (tables to drop), discovered by date pattern; control-file row-count validation when `vld_ctl_flag='Y'` (`fw_schm_sync_main.py:284-421`). Note it handles a **0-byte obsolete file** gracefully (`:316-324`).
- **Schema comparison:** `compare_schema` (`:123-163`) diffs current vs new schema **column-by-column including ordinal position**, emitting per-column ops **ADD / UPDATE / REMOVE** (a position or datatype change ⇒ UPDATE; missing in new ⇒ REMOVE; new ⇒ ADD).
- **Apply:** obsolete tables are dropped (`obsolete_table`, `:465-504`); changed/new tables are **DROP + CREATE** as `USING PARQUET` with optional `LOCATION`, auto-creating the database if absent (`update_table`, `:529-634`). Both run **in parallel** via `concurrent.futures.ThreadPoolExecutor(SCHM_SYNC_MAX_PARALLEL)` (`:511`, `:647`).
- **Idempotency / audit:** if a table's schema is unchanged the op is **SKIPPED** (`:584-586`); every DDL action (with generated DDL file path + ADD/UPDATE/REMOVE detail) is logged to **`tbl_schm_sync_log`** (`:670-738`), and the run fails loudly if any table DDL FAILED (`:702-706`, `745-748`).

This is a defensive, fail-loud, idempotent schema-drift handler — exactly the kind of guardrail a regulatory pipeline needs so a model table never drifts out of spec unnoticed.

---

## 7. Regulatory credit-domain context (Wasin's domains)

*(Domain semantics below are from Wasin's account; the zone/entity-group names are grounded in `db_init_rdt_datazone.py`.)*

RDT segments regulatory data by **entity group** (`entity_grp`), each with its own `model_*`, `modelhotfix_*`, and `sbmt_*` zone triad. Wasin owned three credit-reporting domains:

- **Credit movement (`crmvmt`)** — period-over-period changes/flows on credit exposures (drawdowns, repayments, write-offs, status transitions). Reconciliation-sensitive: movements must tie out against opening/closing balances, which is why RI checks and predefine defaults matter here.
- **Interest (`int`)** — interest accrual/charge data on credit products, reported under BOT definitions (rate, accrued vs charged, basis). Defaulting rules apply where source rate/basis fields violate the regulator's allowed code sets.
- **Credit line (`crline`)** — granted vs utilized credit limits and line attributes. Referential consistency to accounts/counterparties is enforced before promotion to the model zone.

Each domain flows through the same 6 stages but with domain-specific transform notebooks, validation rules (`tbl_vld_rule` rows keyed by entity), and predefine/hotfix defaulting logic in its `modelhotfix_<grp>` zone.

---

## 8. What Wasin demonstrated here (CV-ready)

- **Owned a regulatory data pipeline end-to-end** for a Tier-1 Thai bank: built and operated the framework modules that take curated banking data to **BOT-compliant, encrypted regulatory submissions**, across three credit data domains (credit movement, interest, credit line).
- **Designed/owned the validation engine** (`vld`): an effective-dated, config-driven rule engine with a **`not(passing-condition)` violation-extraction** model, per-entity + global (`ALL_ENTITY`) rules, NORMAL/RERUN idempotent re-execution, two-level run logging and a column-level error log — a reusable data-quality gate, not one-off checks.
- **Designed/owned the predefine/hotfix cleansing layer** — rule-based defaulting of records that fail regulatory rules, with bad-record extraction to a hotfix zone — enforcing the invariant *"no rule-failing value is ever submitted to the regulator"* while keeping reports complete and auditable. (Domain-heavy, regulatory-correctness work.)
- **Built schema-sync** (`schm_sync`): a fail-loud, idempotent, parallelized schema-drift handler (ADD/UPDATE/REMOVE diff, DROP+CREATE, full DDL audit log) that protects the regulatory model from silent upstream schema breakage.
- **Worked the submission path to BOT**: `req_sbmt_key`-driven validate→build orchestration, Z4/Z5 column profiles with change/hash tracking, and **X.509 certificate encryption** (BOT + SCB certs via PowerShell/.NET) producing the encrypted `.bot` artifact in the submission zone.
- Operated within a **config-driven, log-stamped, ADF→ADB (and CardX: pure-ADB)** orchestration model with dependency/incremental checks and per-job logging — production regulatory ops discipline.

---

### Appendix — module ↔ stage map (grounding)

| Conceptual stage | Module / mechanism | Key file(s) |
|---|---|---|
| 1 ingest | `ingt` | `ingt/bin/fw_ingt_main.py` + `module/{pre_proc,list_file,ctl_vld,audt}` |
| 2 transform | `tnfm` | `tnfm/bin/fw_tnfm_main.py` |
| 3 model | `tnfm`→`model_<grp>_db` + RI promotion | `fw_tnfm_main.py:235-264`; `module/chk_ri/mdle_chk_ri.py:158-189`; `tbl_ri_config` |
| 4 validate | `vld` | `vld/bin/fw_vld_main.py`; `not()` at `cmmn/.../fw_cmmn_func.py:905`; `tbl_vld_rule/_log/_entity_log/_err_log` |
| 5 predefine/hotfix | `modelhotfix_<grp>_db` zone + domain notebooks | `db_init_rdt_datazone.py:80-131`; `fw_vld_main.py:325-330` *(no `predf` module)* |
| 6 submission | `sbmt` + `outbnd`/`enc_bot` | `sbmt/bin/fw_sbmt_main.py`; `outbnd/bin/module/post_proc/mdle_enc_bot.py`; `environment_config.py:227-230,475-476` |
| schema sync | `schm_sync` | `schm_sync/bin/fw_schm_sync_main.py` |

> **Module-existence note:** No standalone `model/` or `predf`/`predefine` module exists in the RDT framework tree. "Model" = a `tnfm` transform targeting `model_<grp>_db` gated by an RI-checked promotion; "predefine/hotfix" = domain notebooks run by the framework against the `modelhotfix_<grp>_db` zone (the validator resolves its DB to `{env}_modelhotfix_{entity_grp}_db`). Stated explicitly per the source request.
