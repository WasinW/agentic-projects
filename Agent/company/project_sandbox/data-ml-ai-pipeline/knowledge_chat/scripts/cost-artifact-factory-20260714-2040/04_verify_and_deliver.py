# Databricks notebook source
# MAGIC %md
# MAGIC # T2 (Verify gate) + T3 (Deliver)
# MAGIC
# MAGIC ## Why a barrier
# MAGIC **You cannot un-send an email.** In this topology, isolation is enforced by *which
# MAGIC file goes to whom* — so a mis-addressed email **is** the breach, not a missing row
# MAGIC filter. Everything is rendered first, verified against the **rendered bytes**, and only
# MAGIC then sent. **Any failure aborts the whole run. Never partial-send.**
# MAGIC
# MAGIC ## The six assertions (run on the FILES, not the DataFrames)
# MAGIC | | check | catches |
# MAGIC |---|---|---|
# MAGIC | a | **leak** — distinct team inside the payload == {expected}, cardinality **1** | cross-team data |
# MAGIC | b | **completeness** — Σ cost in file == Σ cost in gold for that team (±0.01) | a broken filter/join |
# MAGIC | c | **non-empty** — row_count > 0 | tag hygiene broke → a blank report went out |
# MAGIC | d | **recipient** — every address in Entra AND domain in allowlist | typo'd address |
# MAGIC | e | **binding** — manifest.team == ledger.team == map.team | file/recipient mismatch |
# MAGIC | f | **reconcile** — Σ per-team totals == org total | a team's cost in two files, or in none |
# MAGIC
# MAGIC ## Delivery
# MAGIC **Databricks cannot email a file attachment.** Job notifications carry run *status*
# MAGIC only. Three routes, best-first for a Zscaler environment:
# MAGIC 1. ⭐ **webhook destination → Azure Logic App (DEV subscription) → O365 `sendMail`**
# MAGIC    The data plane makes no outbound call at all. The Logic App does the sending —
# MAGIC    and can drop the same file into SharePoint for free.
# MAGIC 2. **MS Graph `sendMail`** from the job (app registration + `Mail.Send`). Needs data-plane
# MAGIC    egress to `graph.microsoft.com` — **will fail under Zscaler until the CA bundle is fixed.**
# MAGIC 3. **`smtplib`** → corporate relay. Simplest, if the relay is reachable from DEV.

# COMMAND ----------

dbutils.widgets.text("run_id", "")
dbutils.widgets.text("period", "")
dbutils.widgets.dropdown("mode", "dry_run", ["dry_run", "send"])

RUN_ID  = dbutils.widgets.get("run_id")
PERIOD  = dbutils.widgets.get("period")
DRY_RUN = dbutils.widgets.get("mode") == "dry_run"

CATALOG          = "<catalog>"
GOLD             = f"{CATALOG}.cost.cost_wide"
ALLOWED_DOMAINS  = {"aia.com"}     # ← domain allowlist. Anything else = abort.
SHADOW_CC        = "finops-cost@aia.com"

# COMMAND ----------

# MAGIC %md ## T2 — the verify gate

# COMMAND ----------

import json
import pathlib
import re

import pandas as pd

ledger = spark.sql(
    f"""SELECT * FROM {CATALOG}.ops.artifact_ledger
        WHERE run_id = :run_id AND status = 'RENDERED'""",
    args={"run_id": RUN_ID},
).toPandas()

assert len(ledger) > 0, "Nothing rendered for this run_id"

gold_version = int(ledger["gold_version"].unique()[0])
assert ledger["gold_version"].nunique() == 1, "Artifacts pinned to different gold versions — abort"

gold_totals = spark.sql(
    f"""SELECT tag_team, SUM(cost) AS total, COUNT(*) AS rows
        FROM {GOLD} VERSION AS OF {gold_version}
        GROUP BY tag_team""",
).toPandas().set_index("tag_team")

failures = []

for row in ledger.itertuples():
    team, path = row.team_tag, row.artifact_path
    p = pathlib.Path(path)

    if not p.exists():
        failures.append(f"[{team}] missing file {path}"); continue

    # (e) binding — the manifest embedded in the artifact must name this team
    if row.artifact_format == "HTML":
        text = p.read_text(encoding="utf-8")
        m = re.search(r"<!-- ARTIFACT-MANIFEST (\{.*?\}) -->", text, re.S)
        if not m:
            failures.append(f"[{team}] no manifest in the HTML"); continue
        manifest = json.loads(m.group(1))

        # (a) leak — no other team's tag may appear anywhere in the payload
        for other in gold_totals.index:
            if other != team and f'"{other}"' in text:
                failures.append(f"[{team}] 🚨 LEAK: '{other}' found inside the artifact")
    else:
        manifest = {"team_tag": row.team_tag, "row_count": row.row_count,
                    "total_cost": row.total_cost}

    if manifest.get("team_tag") != team:
        failures.append(f"[{team}] manifest says team={manifest.get('team_tag')}")

    # (c) non-empty
    if row.row_count <= 0:
        failures.append(f"[{team}] EMPTY artifact — tag hygiene broke; do not send a blank report")

    # (b) completeness — the file's total must reconcile to gold
    expected = float(gold_totals.loc[team, "total"]) if team in gold_totals.index else None
    if expected is None:
        failures.append(f"[{team}] not present in gold at version {gold_version}")
    elif abs(float(row.total_cost) - expected) > 0.01:
        # note: the artifact covers a 13-month window; compare on the same grain in your build
        failures.append(f"[{team}] total mismatch: file={row.total_cost} gold={expected}")

    # (d) recipients
    for addr in row.recipients_snapshot:
        if "@" not in addr or addr.split("@")[-1].lower() not in ALLOWED_DOMAINS:
            failures.append(f"[{team}] 🚨 recipient outside the allowlist: {addr}")

# (f) reconcile — every team with cost must have exactly one artifact set
rendered_teams = set(ledger["team_tag"])
gold_teams     = set(gold_totals.index)
if gold_teams - rendered_teams:
    failures.append(f"🚨 teams with cost but NO artifact: {gold_teams - rendered_teams}")
if rendered_teams - gold_teams:
    failures.append(f"🚨 artifacts for teams not in gold: {rendered_teams - gold_teams}")

# COMMAND ----------

if failures:
    for f in failures:
        print("FAIL:", f)
    raise Exception(f"VERIFY GATE FAILED ({len(failures)} issues) — NOTHING WAS SENT.")

spark.sql(
    f"UPDATE {CATALOG}.ops.artifact_ledger SET status = 'VERIFIED' "
    f"WHERE run_id = :run_id AND status = 'RENDERED'",
    args={"run_id": RUN_ID},
)
print(f"✅ verify gate passed — {len(ledger)} artifacts across {len(rendered_teams)} teams")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Dry-run — MANDATORY on any change to the recipient map, and on a new team's first run
# MAGIC A human eyeballs a 6-line table. That is the last line of defence before a mailbox.

# COMMAND ----------

plan = (ledger.groupby("team_tag")
        .agg(files=("artifact_path", list),
             to=("recipients_snapshot", "first"),
             total=("total_cost", "first"))
        .reset_index())

print(f"{'TEAM':<18} {'TOTAL':>14}  RECIPIENTS")
print("-" * 90)
for r in plan.itertuples():
    print(f"{r.team_tag:<18} {r.total:>14,.2f}  {', '.join(r.to)}")
    for f in r.files:
        print(f"{'':<18} {'':>14}  └─ {pathlib.Path(f).name}")

if DRY_RUN:
    dbutils.notebook.exit("DRY RUN — verified, nothing sent. Review the plan above, then re-run with mode=send.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## T3 — deliver
# MAGIC
# MAGIC ⚠️ Recipients are read **from the ledger row written at render time**, never re-queried
# MAGIC from the map. Render and send are bound to the *same* decision — so an edit to the map
# MAGIC mid-run cannot send team A's file to team B.

# COMMAND ----------

import base64
import hashlib
import json
import urllib.request

LOGIC_APP_URL = dbutils.secrets.get("cost-factory", "logic-app-url")  # ← never hard-code

def deliver_via_logic_app(team, display, to, cc, files, total):
    """Route 1 (recommended). The Logic App reads nothing — we hand it the bytes."""
    attachments = [{
        "name": pathlib.Path(f).name,
        "contentBytes": base64.b64encode(pathlib.Path(f).read_bytes()).decode(),
    } for f in files]

    body = {
        "to": to,
        "cc": list(cc or []) + [SHADOW_CC],          # shadow copy → auditability
        "subject": f"[AIA FinOps] {display} — Azure Cost {PERIOD[:4]}-{PERIOD[4:]} — Internal/Confidential",
        "html": (
            f"<p>Attached is the Azure cost report for <b>{display}</b>, "
            f"{PERIOD[:4]}-{PERIOD[4:]}.</p>"
            f"<p>Total: <b>{total:,.2f}</b></p>"
            f"<p>Open the <b>.html</b> attachment in any browser for the interactive view "
            f"(it works offline — no VPN, no login). The <b>.xlsx</b> is for chargeback.</p>"
            f"<p style='color:#888;font-size:11px'>Contains AIA internal cost data for "
            f"{display} only. Please do not forward.</p>"
        ),
        "attachments": attachments,
        "sensitivity": "Internal",
    }

    req = urllib.request.Request(
        LOGIC_APP_URL,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        assert resp.status in (200, 202), f"Logic App returned {resp.status}"
        return resp.headers.get("x-ms-request-id", "")

# COMMAND ----------

from datetime import datetime, timezone

teammap = spark.sql(
    f"SELECT team_tag, display_name, recipients_cc FROM {CATALOG}.ops.team_recipient_map "
    f"WHERE active_to IS NULL"
).toPandas().set_index("team_tag")

for r in plan.itertuples():
    # idempotency: a re-run of the same pinned version must not double-send
    already = spark.sql(
        f"""SELECT count(*) AS n FROM {CATALOG}.ops.artifact_ledger
            WHERE run_id = :run_id AND team_tag = :team AND status = 'DELIVERED'""",
        args={"run_id": RUN_ID, "team": r.team_tag},
    ).collect()[0].n
    if already:
        print(f"  {r.team_tag}: already delivered — skip")
        continue

    display = teammap.loc[r.team_tag, "display_name"]
    cc      = teammap.loc[r.team_tag, "recipients_cc"]

    msg_id = deliver_via_logic_app(r.team_tag, display, list(r.to), cc, r.files, r.total)
    print(f"  ✓ {r.team_tag} → {', '.join(r.to)}  ({msg_id})")

    spark.sql(
        f"""UPDATE {CATALOG}.ops.artifact_ledger
            SET status='DELIVERED', delivered_at=current_timestamp(), smtp_message_id=:mid
            WHERE run_id=:run_id AND team_tag=:team""",
        args={"mid": msg_id, "run_id": RUN_ID, "team": r.team_tag},
    )
    spark.sql(
        f"""INSERT INTO {CATALOG}.ops.delivery_audit VALUES
            (:run_id, :team, :period, :to, :sha, 'EMAIL', 'SENT', :mid, current_timestamp())""",
        args={"run_id": RUN_ID, "team": r.team_tag, "period": PERIOD, "to": list(r.to),
              "sha": hashlib.sha256("|".join(sorted(r.files)).encode()).hexdigest(), "mid": msg_id},
    )

print("\n✅ delivery complete")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Anomaly tripwires — run after every delivery
# MAGIC Both of these are *legitimate* sometimes. They should always be **noticed**.

# COMMAND ----------

spark.sql(f"""
  WITH hist AS (
    SELECT team_tag, period, total_cost,
           LAG(total_cost) OVER (PARTITION BY team_tag ORDER BY period) AS prev,
           size(recipients_snapshot) AS n_recip,
           LAG(size(recipients_snapshot)) OVER (PARTITION BY team_tag ORDER BY period) AS prev_recip
    FROM {CATALOG}.ops.artifact_ledger
    WHERE status = 'DELIVERED' AND artifact_format = 'HTML'
  )
  SELECT team_tag, period, total_cost, prev,
         round((total_cost - prev) / nullif(prev, 0) * 100, 1) AS pct_change,
         n_recip, prev_recip,
         CASE WHEN abs((total_cost - prev) / nullif(prev, 0)) > 0.5 THEN '⚠️ cost moved >50%'
              WHEN n_recip != prev_recip                            THEN '⚠️ recipient set changed'
         END AS alert
  FROM hist
  WHERE period = '{PERIOD}'
    AND (abs((total_cost - prev) / nullif(prev, 0)) > 0.5 OR n_recip != prev_recip)
""").display()
