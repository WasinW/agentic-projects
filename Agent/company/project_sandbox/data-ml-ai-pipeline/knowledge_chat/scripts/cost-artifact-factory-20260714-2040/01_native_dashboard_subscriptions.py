# Databricks notebook source
# MAGIC %md
# MAGIC # Layer 0 — Native per-team AI/BI Dashboards + Subscriptions
# MAGIC
# MAGIC **Zero custom rendering code.** Databricks' own scheduler produces the PDF and the
# MAGIC Excel/CSV attachment and emails them. We only generate one dashboard per team.
# MAGIC
# MAGIC **Isolation is by construction:** each team's dashboard has `WHERE tag_team = 'X'`
# MAGIC baked into its dataset SQL. There is no code path that can put team B's rows in
# MAGIC team A's PDF. No UC row filter needed — which also sidesteps the `embed_credentials`
# MAGIC trap (a published dashboard's queries run as the *publisher*, silently defeating RLS).
# MAGIC
# MAGIC ### ⚠️ The one thing this script CANNOT do
# MAGIC The Databricks SDK's `Schedule` object exposes only
# MAGIC `cron_schedule / warehouse_id / display_name / pause_status / etag`.
# MAGIC **There is no field for attachments or page selection.**
# MAGIC → Create the schedule here, then open each dashboard once in the UI:
# MAGIC   **Schedule → Advanced settings → ☑ Include pages (PDF) + ☑ Include data (Excel/CSV)**
# MAGIC   It is a one-time click per dashboard; it then runs forever unattended.
# MAGIC
# MAGIC ### Hard limits (docs)
# MAGIC | limit | value | if exceeded |
# MAGIC |---|---|---|
# MAGIC | attachment size | **9 MB** (PDF + data, combined) | only the PDF is sent, with a "open the dashboard" link the client **cannot open** |
# MAGIC | Excel rows | **100,000** | silently truncated |
# MAGIC | chart widget rows | 10,000 | |
# MAGIC | table widget rows | 100,000 | |
# MAGIC | subscribers per destination | 100 | |
# MAGIC
# MAGIC → **Aggregate to `resource_group × month`, never `resource × day`.**

# COMMAND ----------

# MAGIC %pip install --upgrade databricks-sdk
# MAGIC %restart_python

# COMMAND ----------

import json

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.dashboards import (
    CronSchedule,
    Dashboard,
    Schedule,
    Subscription,
    SubscriptionSubscriberDestination,
)

w = WorkspaceClient()  # picks up the notebook's own auth in DEV

CATALOG      = "<catalog>"
SCHEMA       = "cost"
TABLE        = "cost_wide"
WAREHOUSE_ID = "<serverless_sql_warehouse_id>"
PARENT_PATH  = "/Workspace/Shared/CostReports"
CRON         = "0 0 9 8 * ?"   # 09:00 on the 8th of each month (D+8: Azure cost data has settled)
TIMEZONE     = "Asia/Bangkok"

# COMMAND ----------

# MAGIC %md ## 1. Read the teams from the mapping table (single source of truth)

# COMMAND ----------

teams = spark.sql(f"""
    SELECT team_tag, display_name, recipients_to, recipients_cc
    FROM   {CATALOG}.ops.team_recipient_map
    WHERE  active_to IS NULL
""").collect()

# FAIL CLOSED: every team that has cost must have a recipient.
orphans = spark.sql(f"""
    SELECT DISTINCT g.tag_team
    FROM   {CATALOG}.{SCHEMA}.{TABLE} g
    LEFT ANTI JOIN (SELECT team_tag FROM {CATALOG}.ops.team_recipient_map WHERE active_to IS NULL) m
           ON g.tag_team = m.team_tag
""").collect()
assert not orphans, f"Unmapped teams have cost — refusing to run: {[r.tag_team for r in orphans]}"

print(f"{len(teams)} active teams")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. The dashboard template
# MAGIC
# MAGIC Build ONE dashboard by hand in the UI, export it (`⋮ → Export → .lvdash.json`), and
# MAGIC drop it in a UC Volume. Put the literal token `__TEAM__` where the team tag goes.
# MAGIC
# MAGIC Its dataset SQL should look like:
# MAGIC ```sql
# MAGIC SELECT month, resource_group, service, SUM(cost) AS cost
# MAGIC FROM   <catalog>.cost.cost_wide
# MAGIC WHERE  tag_team = '__TEAM__'          -- ← the isolation boundary
# MAGIC   AND  month >= add_months(current_date(), -13)
# MAGIC GROUP BY ALL
# MAGIC ```
# MAGIC
# MAGIC ⚠️ `.lvdash.json` carries **query text + widget config only — never data.**
# MAGIC That is exactly why it can't be handed to the client's workspace to open.

# COMMAND ----------

TEMPLATE_PATH = f"/Volumes/{CATALOG}/ops/assets/cost_dashboard_template.lvdash.json"

with open(TEMPLATE_PATH) as f:
    template = f.read()

assert "__TEAM__" in template, "Template has no __TEAM__ token — isolation would break silently."

# COMMAND ----------

# MAGIC %md ## 3. Generate one dashboard per team

# COMMAND ----------

created = {}

for t in teams:
    serialized = template.replace("__TEAM__", t.team_tag)

    # Belt-and-braces: the rendered SQL must reference exactly this team and no other.
    for other in teams:
        if other.team_tag != t.team_tag:
            assert f"'{other.team_tag}'" not in serialized, \
                f"LEAK: {other.team_tag} appears in {t.team_tag}'s dashboard"

    dash = w.lakeview.create(
        dashboard=Dashboard(
            display_name=f"Cloud Cost — {t.display_name}",
            parent_path=PARENT_PATH,
            warehouse_id=WAREHOUSE_ID,
            serialized_dashboard=serialized,
        )
    )

    # embed_credentials=True → queries run as the publisher (us, in DEV).
    # That is CORRECT here: nobody views this dashboard. It exists only to be rendered
    # by the scheduler. Isolation comes from the WHERE clause, not from the viewer's identity.
    w.lakeview.publish(
        dashboard_id=dash.dashboard_id,
        embed_credentials=True,
        warehouse_id=WAREHOUSE_ID,
    )

    created[t.team_tag] = dash.dashboard_id
    print(f"  {t.team_tag:20s} → {dash.dashboard_id}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Email notification destinations
# MAGIC
# MAGIC **Created once, by a workspace admin, in the UI:**
# MAGIC `Settings → Notifications → + Add destination → Email → <team DL>`
# MAGIC
# MAGIC Docs: *"You can configure account users, distribution lists, and **external users
# MAGIC (such as partners or clients)** as email notification destinations."*
# MAGIC → **the client teams do NOT need to be Databricks users.**
# MAGIC
# MAGIC ⚠️ **Unsubscribe footer:** if one person on a DL clicks it, the **whole DL** is
# MAGIC removed from the subscription. Warn the teams, or use an IT-controlled DL.

# COMMAND ----------

# Map team_tag → destination_id (from the admin UI, or list them):
DESTINATIONS = {
    "team_a": "<destination_id_a>",
    # ...
}

for d in w.notification_destinations.list():
    print(f"{d.id}  {d.display_name}  ({d.destination_type})")

# COMMAND ----------

# MAGIC %md ## 5. Schedule + subscription per dashboard

# COMMAND ----------

for team_tag, dashboard_id in created.items():
    sched = w.lakeview.create_schedule(
        dashboard_id=dashboard_id,
        schedule=Schedule(
            cron_schedule=CronSchedule(quartz_cron_expression=CRON, timezone_id=TIMEZONE),
            display_name=f"Monthly cost report — {team_tag}",
            warehouse_id=WAREHOUSE_ID,
        ),
    )

    w.lakeview.create_subscription(
        dashboard_id=dashboard_id,
        schedule_id=sched.schedule_id,
        subscription=Subscription(
            subscriber=SubscriptionSubscriberDestination(
                destination_id=DESTINATIONS[team_tag]
            )
        ),
    )
    print(f"  {team_tag}: schedule {sched.schedule_id} + subscription ✓")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. ⚠️ MANUAL STEP — attachments (the SDK cannot do this)
# MAGIC
# MAGIC For **each** dashboard, once:
# MAGIC 1. Open the dashboard → **Schedule** → click the schedule you just created → **Edit**
# MAGIC 2. **Advanced settings**
# MAGIC    - ☑ **Include pages** → pick the pages, in order → this is the **PDF**
# MAGIC    - ☑ **Include data** → pick the widgets → format **Excel** (or CSV/TSV)
# MAGIC 3. Save.
# MAGIC
# MAGIC 🆕 *The tabular-attachment option shipped **2026-04-16** and is GA. Before that,
# MAGIC subscriptions could only send a PDF — which is precisely why the old answer to this
# MAGIC problem was "email a PDF".*
# MAGIC
# MAGIC ## 7. Verify before you trust it
# MAGIC - Trigger one schedule manually. Confirm the email lands with **both** attachments.
# MAGIC - Open the Excel: `SELECT DISTINCT team` in it must return **exactly one** value.
# MAGIC - Check the combined size is **well under 9 MB**. If Databricks drops the attachment
# MAGIC   it substitutes a link to the dashboard — **which your clients cannot open.** That
# MAGIC   failure mode is silent from our side and looks like "the report stopped working"
# MAGIC   from theirs.
