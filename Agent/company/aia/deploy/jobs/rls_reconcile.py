# Databricks notebook source
# =====================================================================================
# rls_reconcile.py — L4 control-table-driven RLS / grant reconciliation job
# -------------------------------------------------------------------------------------
# GENERIC TEMPLATE. No company identifiers. Set the job parameters below at deploy time.
#
# WHAT IT DOES (governance-as-data):
#   reads DESIRED state (control.access_control) -> reads ACTUAL state (information_schema +
#   SHOW GRANTS) -> diffs -> applies ONLY the delta (grant/revoke/set-filter/drop-filter/mask).
#   Idempotent: re-running on an unchanged control table applies ZERO statements.
#
# DEPLOY AS: a scheduled Databricks Job (daily). CI (Jenkins/DAB) ships THIS code + schedule;
#   the daily reconciliation itself runs here, NOT in CI. See Doc 2 §"Jenkins vs job".
#
# RUN-AS: a dedicated service principal that OWNS the managed securables (or is metastore admin)
#   — required, else information_schema is privilege-filtered and under-reads actual state,
#   causing spurious re-GRANTs. Creds in a Key-Vault-backed secret scope.
#
# SAFETY: dry-run by default. Set apply=true ONLY after watching the planned diff for a few runs.
# =====================================================================================
from pyspark.sql import functions as F

# ---- job parameters (dbutils.widgets in a real job) --------------------------------
GOV_CATALOG   = "main"                 # ${gov_catalog}
GOV           = f"{GOV_CATALOG}.control"
ENV           = "prod"                 # scopes which control rows this run touches
APPLY         = False                  # <-- dry-run guard. False = plan only, apply nothing.
MANAGED_CATALOGS          = ["main"]                       # only ever touch these catalogs
MANAGED_PRINCIPAL_PREFIXES = ("consumer-", "biz-consumers-")  # only ever touch these principals
MAX_REVOKES   = 50                     # circuit breaker: abort if the plan wants more revokes
MAX_REVOKE_FRACTION = 0.20             # ...or more than this fraction of actual grants
RUN_ID        = spark.sql("SELECT uuid()").first()[0]

def esc(fqn: str) -> str:
    return ".".join(f"`{p}`" for p in fqn.split("."))

_planned = []   # collected for audit + circuit-breaker
def plan(action, statement, rule_id=None):
    _planned.append((RUN_ID, action, statement, rule_id))

def run(statement):
    """Apply a DDL statement (only when APPLY); always safe to call — no-op in dry-run."""
    if APPLY:
        spark.sql(statement)

# =====================================================================================
# 1) DESIRED state (scoped to this env + enabled)
# =====================================================================================
desired = spark.table(f"{GOV}.access_control").where(
    (F.col("enabled") == True) & (F.col("environment") == ENV)
)

# =====================================================================================
# 2) ACTUAL state — object grants. UNION the *_privileges views, then apply scope guard.
#    NOTE: information_schema is privilege-filtered; the run-as SP MUST own the securables.
# =====================================================================================
def read_actual_grants():
    parts = []
    for cat in MANAGED_CATALOGS:
        parts.append(f"""
          SELECT grantee AS principal, privilege_type AS privilege,
                 concat_ws('.', table_catalog, table_schema, table_name) AS securable_fqn, 'TABLE' AS securable_type
          FROM {cat}.information_schema.table_privileges
          UNION ALL
          SELECT grantee, privilege_type, concat_ws('.', catalog_name, schema_name), 'SCHEMA'
          FROM {cat}.information_schema.schema_privileges
          UNION ALL
          SELECT grantee, privilege_type, catalog_name, 'CATALOG'
          FROM {cat}.information_schema.catalog_privileges
          UNION ALL
          SELECT grantee, privilege_type,
                 concat_ws('.', specific_catalog, specific_schema, specific_name), 'FUNCTION'
          FROM {cat}.information_schema.routine_privileges
        """)
    df = spark.sql(" UNION ALL ".join(parts))
    # scope guard: only principals we manage
    pref = "|".join(p for p in MANAGED_PRINCIPAL_PREFIXES)
    return df.where(F.col("principal").rlike(f"^({pref})"))

actual_g = read_actual_grants()

desired_g_present = (desired.where("rule_type='GRANT' AND desired_state='PRESENT'")
                     .select("securable_type", "securable_fqn", "principal", "privilege"))
desired_g_absent  = (desired.where("rule_type='GRANT' AND desired_state='ABSENT'")
                     .select("securable_type", "securable_fqn", "principal", "privilege"))

to_grant  = desired_g_present.subtract(actual_g)
to_revoke = (actual_g.subtract(desired_g_present)          # drift: exists but not desired
             .unionByName(desired_g_absent.intersect(actual_g)))  # + explicit ABSENT still present

# =====================================================================================
# 3) SAFETY — circuit breaker BEFORE any apply
# =====================================================================================
n_revoke, n_actual = to_revoke.count(), actual_g.count()
if n_revoke > MAX_REVOKES or (n_actual and n_revoke > MAX_REVOKE_FRACTION * n_actual):
    raise Exception(f"ABORT: plan wants {n_revoke} revokes (actual grants={n_actual}) — exceeds safety threshold. "
                    f"Check the control table for a bad push / wrong env filter. Nothing applied.")

# =====================================================================================
# 4) APPLY grants first, then RLS bindings, then revokes last (ordering matters)
# =====================================================================================
for r in to_grant.collect():
    stmt = f"GRANT `{r.privilege}` ON {r.securable_type} {esc(r.securable_fqn)} TO `{r.principal}`"
    plan("GRANT", stmt); run(stmt)

# Row filters: a table holds AT MOST ONE filter → DROP-then-SET (SET-over-existing errors).
def actual_row_filter_fn(table_fqn):
    cat = table_fqn.split(".")[0]
    rows = spark.sql(f"SELECT * FROM {cat}.information_schema.row_filters").collect()
    # FLAG: column names not doc-verified — DESCRIBE in-tenant and adjust the match below.
    for x in rows:
        d = x.asDict()
        full = ".".join([d.get("table_catalog", ""), d.get("table_schema", ""), d.get("table_name", "")])
        if full == table_fqn:
            return d.get("filter_name") or d.get("function_name")
    return None

for r in desired.where("rule_type='ROW_FILTER' AND desired_state='PRESENT'").collect():
    cols = ", ".join(f"`{c}`" for c in r.target_columns)
    current = actual_row_filter_fn(r.securable_fqn)
    if current is None:
        stmt = f"ALTER TABLE {esc(r.securable_fqn)} SET ROW FILTER {esc(r.function_fqn)} ON ({cols})"
        plan("SET_ROW_FILTER", stmt); run(stmt)
    elif current != r.function_fqn:
        for stmt in (f"ALTER TABLE {esc(r.securable_fqn)} DROP ROW FILTER",
                     f"ALTER TABLE {esc(r.securable_fqn)} SET ROW FILTER {esc(r.function_fqn)} ON ({cols})"):
            plan("SET_ROW_FILTER", stmt); run(stmt)
    # same fn already bound -> no-op (idempotent)

for r in desired.where("rule_type='ROW_FILTER' AND desired_state='ABSENT'").collect():
    if actual_row_filter_fn(r.securable_fqn):
        stmt = f"ALTER TABLE {esc(r.securable_fqn)} DROP ROW FILTER"
        plan("DROP_ROW_FILTER", stmt); run(stmt)

# Column masks (per column, same DROP-then-SET discipline)
for r in desired.where("rule_type='COLUMN_MASK' AND desired_state='PRESENT'").collect():
    for col in r.target_columns:
        stmt = f"ALTER TABLE {esc(r.securable_fqn)} ALTER COLUMN `{col}` SET MASK {esc(r.function_fqn)}"
        plan("SET_MASK", stmt); run(stmt)   # DROP MASK first if changing an existing mask
for r in desired.where("rule_type='COLUMN_MASK' AND desired_state='ABSENT'").collect():
    for col in r.target_columns:
        stmt = f"ALTER TABLE {esc(r.securable_fqn)} ALTER COLUMN `{col}` DROP MASK"
        plan("DROP_MASK", stmt); run(stmt)

# ABAC policies (idempotent via CREATE OR REPLACE). Compute floor: DBR 16.4+/serverless on all consumers.
for r in desired.where("rule_type='ABAC_POLICY' AND desired_state='PRESENT'").collect():
    cols = ", ".join(r.target_columns) if r.target_columns else ""
    stmt = (f"CREATE OR REPLACE POLICY {r.policy_name} ON {r.securable_type} {esc(r.securable_fqn)} "
            f"ROW FILTER {esc(r.function_fqn)} TO `{r.principal}` "
            f"FOR TABLES WHEN {r.tag_predicate}" + (f" USING COLUMNS ({cols})" if cols else ""))
    plan("CREATE_POLICY", stmt); run(stmt)
for r in desired.where("rule_type='ABAC_POLICY' AND desired_state='ABSENT'").collect():
    stmt = f"DROP POLICY IF EXISTS {r.policy_name} ON {r.securable_type} {esc(r.securable_fqn)}"
    plan("DROP_POLICY", stmt); run(stmt)

# revokes LAST
for r in to_revoke.collect():
    stmt = f"REVOKE `{r.privilege}` ON {r.securable_type} {esc(r.securable_fqn)} FROM `{r.principal}`"
    plan("REVOKE", stmt); run(stmt)

# =====================================================================================
# 5) Audit write-back + surfacing
# =====================================================================================
audit = spark.createDataFrame(
    [(rid, act, st, rl) for (rid, act, st, rl) in _planned],
    "run_id string, action string, statement string, rule_id string"
).withColumn("ts", F.current_timestamp()) \
 .withColumn("status", F.lit("APPLIED" if APPLY else "PLANNED")) \
 .withColumn("error", F.lit(None).cast("string")) \
 .withColumn("dry_run", F.lit(not APPLY))
audit.write.mode("append").saveAsTable(f"{GOV}.reconcile_audit")

print(f"run_id={RUN_ID} env={ENV} apply={APPLY} planned={len(_planned)} "
      f"grants+={to_grant.count()} revokes={n_revoke}")
audit.select("action", "statement").show(200, truncate=False)
# If APPLY and any statement fails: fail the task so workspace alerting fires; never leave a table
# with a row filter bound while its EXECUTE grant failed (grants are ordered first for this reason).
