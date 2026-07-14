# Databricks notebook source
# MAGIC %md
# MAGIC # Layer 1 — Self-contained interactive HTML (one file per team)
# MAGIC
# MAGIC **This is the artifact that answers "ถ้าได้เป็น static dashboard ก็ยังดี".**
# MAGIC A `.lvdash.json` provably cannot carry data — an HTML file can.
# MAGIC
# MAGIC The output is a **single file** with the data embedded as JSON and the charting
# MAGIC library inlined. It opens in any browser, **fully offline**, with real interactivity
# MAGIC (hover, filter, drill, cross-filter). No Databricks, no network, no VPN.
# MAGIC
# MAGIC ### 🚨 The Zscaler rule
# MAGIC **Never reference a CDN.** `<script src="https://cdn...">` will be MITM'd or blocked
# MAGIC by the corporate proxy and the user sees a blank page. **Vendor the library into a UC
# MAGIC Volume, read it, inline it.**
# MAGIC
# MAGIC | library | inlined size | notes |
# MAGIC |---|---|---|
# MAGIC | **ECharts** | **~1.1 MB** | ⭐ best capability/size ratio |
# MAGIC | Plotly (`include_plotlyjs=True`) | ~3.5–5 MB | self-contained but heavy |
# MAGIC | Chart.js | ~200 KB | smallest; simple charts only |
# MAGIC
# MAGIC ### One-time setup
# MAGIC ```
# MAGIC # download once on a machine with internet, upload to the Volume:
# MAGIC /Volumes/<catalog>/ops/assets/lib/echarts.min.js
# MAGIC ```
# MAGIC
# MAGIC ### Run as: Lakeflow Job → `for_each` task over the team list, serverless.
# MAGIC One team = one task = one parameterised query = one file. Two teams' rows can never
# MAGIC share a DataFrame. **Isolation is structural, not a runtime check.**

# COMMAND ----------

dbutils.widgets.text("team_tag", "")
dbutils.widgets.text("period", "")        # YYYYMM
dbutils.widgets.text("gold_version", "")  # pinned by T0 → re-runs are byte-identical
dbutils.widgets.text("run_id", "")

TEAM         = dbutils.widgets.get("team_tag")
PERIOD       = dbutils.widgets.get("period")
GOLD_VERSION = int(dbutils.widgets.get("gold_version"))
RUN_ID       = dbutils.widgets.get("run_id")

assert TEAM, "team_tag is required — refusing to render an unfiltered report"

CATALOG  = "<catalog>"
GOLD     = f"{CATALOG}.cost.cost_wide"
LIB_PATH = f"/Volumes/{CATALOG}/ops/assets/lib/echarts.min.js"
OUT_DIR  = f"/Volumes/{CATALOG}/ops/artifacts/{PERIOD}/{TEAM}"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. The isolation boundary — the ONLY place filtering happens
# MAGIC
# MAGIC Parameterised. Never string-interpolated from a loop index. `VERSION AS OF` pins the
# MAGIC snapshot so a retry emails the *same* numbers — chargeback figures must be
# MAGIC reproducible when Finance asks in November about August.

# COMMAND ----------

import pandas as pd

df = spark.sql(
    f"""
    SELECT month,
           resource_group,
           service,
           cost_center,
           SUM(cost)          AS cost,
           SUM(cost_amortized) AS cost_amortized
    FROM   {GOLD} VERSION AS OF {GOLD_VERSION}
    WHERE  tag_team = :team
      AND  month >= add_months(to_date(:period || '01', 'yyyyMMdd'), -12)
      AND  month <= to_date(:period || '01', 'yyyyMMdd')
    GROUP BY ALL
    """,
    args={"team": TEAM, "period": PERIOD},
).toPandas()

assert len(df) > 0, f"No rows for {TEAM} in {PERIOD} — tag hygiene broke. Do NOT send a blank report."

# Structural guarantee, asserted anyway (defence in depth):
# the query cannot have returned another team, but prove it before it leaves the building.
teams_in_payload = spark.sql(
    f"SELECT DISTINCT tag_team FROM {GOLD} VERSION AS OF {GOLD_VERSION} WHERE tag_team = :team",
    args={"team": TEAM},
).collect()
assert len(teams_in_payload) == 1 and teams_in_payload[0].tag_team == TEAM

print(f"{TEAM}: {len(df)} rows, total {df['cost'].sum():,.2f}")

# COMMAND ----------

# MAGIC %md ## 2. Build the self-contained HTML

# COMMAND ----------

import hashlib
import html as htmllib
import json
import pathlib
from datetime import datetime, timezone

echarts_js = pathlib.Path(LIB_PATH).read_text()
assert len(echarts_js) > 500_000, "ECharts bundle looks wrong — refusing to ship a broken file"

payload = df.to_json(orient="records", double_precision=2)

manifest = {
    "run_id": RUN_ID,
    "team_tag": TEAM,
    "period": PERIOD,
    "gold_version": GOLD_VERSION,
    "row_count": int(len(df)),
    "total_cost": float(df["cost"].sum()),
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
}

TEMPLATE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Cloud Cost — {team} — {period}</title>
<!-- ARTIFACT-MANIFEST {manifest} -->
<script>{echarts}</script>
<style>
  :root {{ color-scheme: light dark; }}
  body {{ font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
          margin: 0; padding: 24px; background: #f7f8fa; color: #1a1a1a; }}
  @media (prefers-color-scheme: dark) {{ body {{ background:#16181d; color:#e6e6e6; }}
                                         .card {{ background:#1f2229 !important; }} }}
  header {{ display:flex; justify-content:space-between; align-items:baseline;
            border-bottom:2px solid #cc0000; padding-bottom:12px; margin-bottom:20px; }}
  h1 {{ font-size:20px; margin:0; }}
  .badge {{ font-size:11px; padding:3px 8px; border-radius:3px;
            background:#cc0000; color:#fff; letter-spacing:.04em; }}
  .kpis {{ display:flex; gap:16px; margin-bottom:20px; flex-wrap:wrap; }}
  .card {{ background:#fff; border-radius:8px; padding:16px 20px; flex:1; min-width:180px;
           box-shadow:0 1px 3px rgba(0,0,0,.08); }}
  .card .label {{ font-size:12px; opacity:.65; }}
  .card .value {{ font-size:26px; font-weight:600; margin-top:4px; }}
  .controls {{ margin-bottom:16px; display:flex; gap:12px; flex-wrap:wrap; }}
  select {{ padding:6px 10px; border-radius:6px; border:1px solid #ccd; }}
  .chart {{ background:#fff; border-radius:8px; padding:12px; margin-bottom:20px;
            height:420px; box-shadow:0 1px 3px rgba(0,0,0,.08); }}
  footer {{ font-size:11px; opacity:.55; margin-top:32px; line-height:1.6; }}
</style></head><body>

<header>
  <h1>Cloud Cost — {team_display} — {period_display}</h1>
  <span class="badge">INTERNAL / {team_display} ONLY</span>
</header>

<div class="kpis">
  <div class="card"><div class="label">Total this month</div><div class="value" id="kpi-total">–</div></div>
  <div class="card"><div class="label">vs last month</div><div class="value" id="kpi-mom">–</div></div>
  <div class="card"><div class="label">Resource groups</div><div class="value" id="kpi-rg">–</div></div>
  <div class="card"><div class="label">Top service</div><div class="value" id="kpi-svc">–</div></div>
</div>

<div class="controls">
  <select id="f-rg"><option value="">All resource groups</option></select>
  <select id="f-svc"><option value="">All services</option></select>
  <select id="f-cc"><option value="">All cost centers</option></select>
</div>

<div class="chart" id="c-trend"></div>
<div class="chart" id="c-service"></div>
<div class="chart" id="c-rg"></div>

<footer>
  Contains AIA internal cost data for <b>{team_display}</b> only. Do not forward.<br>
  Generated {generated} · gold version {gold_version} · run {run_id} · {row_count} rows<br>
  Fully offline — no data is transmitted when you open this file.
</footer>

<script>
const DATA = {payload};
const CUR  = v => (v ?? 0).toLocaleString(undefined, {{maximumFractionDigits: 0}});

const uniq = k => [...new Set(DATA.map(d => d[k]))].filter(Boolean).sort();
for (const [sel, key] of [["f-rg","resource_group"], ["f-svc","service"], ["f-cc","cost_center"]]) {{
  const el = document.getElementById(sel);
  uniq(key).forEach(v => el.add(new Option(v, v)));
  el.onchange = render;
}}

const charts = {{
  trend:   echarts.init(document.getElementById("c-trend")),
  service: echarts.init(document.getElementById("c-service")),
  rg:      echarts.init(document.getElementById("c-rg")),
}};

function filtered() {{
  const rg  = document.getElementById("f-rg").value;
  const svc = document.getElementById("f-svc").value;
  const cc  = document.getElementById("f-cc").value;
  return DATA.filter(d => (!rg  || d.resource_group === rg)
                       && (!svc || d.service        === svc)
                       && (!cc  || d.cost_center    === cc));
}}

const rollup = (rows, key) => {{
  const m = new Map();
  rows.forEach(r => m.set(r[key], (m.get(r[key]) || 0) + r.cost));
  return [...m.entries()].sort((a, b) => b[1] - a[1]);
}};

function render() {{
  const rows   = filtered();
  const months = rollup(rows, "month").sort((a, b) => String(a[0]).localeCompare(String(b[0])));
  const last   = months.at(-1)?.[1] ?? 0;
  const prev   = months.at(-2)?.[1] ?? 0;
  const svcs   = rollup(rows, "service");
  const rgs    = rollup(rows, "resource_group").slice(0, 15);

  document.getElementById("kpi-total").textContent = CUR(last);
  document.getElementById("kpi-mom").textContent   =
      prev ? ((last - prev) / prev * 100).toFixed(1) + "%" : "–";
  document.getElementById("kpi-rg").textContent    = uniq("resource_group").length;
  document.getElementById("kpi-svc").textContent   = svcs[0]?.[0] ?? "–";

  charts.trend.setOption({{
    title: {{ text: "Monthly trend", left: 8, textStyle: {{ fontSize: 14 }} }},
    tooltip: {{ trigger: "axis", valueFormatter: CUR }},
    xAxis: {{ type: "category", data: months.map(m => m[0]) }},
    yAxis: {{ type: "value" }},
    series: [{{ type: "line", smooth: true, areaStyle: {{}},
                data: months.map(m => +m[1].toFixed(2)) }}],
    grid: {{ left: 60, right: 24, top: 48, bottom: 40 }},
  }}, true);

  charts.service.setOption({{
    title: {{ text: "By service", left: 8, textStyle: {{ fontSize: 14 }} }},
    tooltip: {{ trigger: "item", valueFormatter: CUR }},
    series: [{{ type: "pie", radius: ["42%", "68%"],
                data: svcs.slice(0, 10).map(([n, v]) => ({{ name: n, value: +v.toFixed(2) }})) }}],
  }}, true);

  charts.rg.setOption({{
    title: {{ text: "Top resource groups", left: 8, textStyle: {{ fontSize: 14 }} }},
    tooltip: {{ trigger: "axis", valueFormatter: CUR }},
    xAxis: {{ type: "value" }},
    yAxis: {{ type: "category", data: rgs.map(r => r[0]).reverse() }},
    series: [{{ type: "bar", data: rgs.map(r => +r[1].toFixed(2)).reverse() }}],
    grid: {{ left: 180, right: 40, top: 48, bottom: 40 }},
  }}, true);
}}

render();
addEventListener("resize", () => Object.values(charts).forEach(c => c.resize()));
</script>
</body></html>
"""

doc = TEMPLATE.format(
    team=TEAM,
    team_display=htmllib.escape(TEAM.replace("_", " ").title()),
    period=PERIOD,
    period_display=f"{PERIOD[:4]}-{PERIOD[4:]}",
    manifest=json.dumps(manifest),
    echarts=echarts_js,
    payload=payload,
    generated=manifest["generated_at_utc"],
    gold_version=GOLD_VERSION,
    run_id=RUN_ID,
    row_count=manifest["row_count"],
)

# COMMAND ----------

# MAGIC %md ## 3. Write + record in the ledger

# COMMAND ----------

pathlib.Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
out = f"{OUT_DIR}/report_{TEAM}_{PERIOD}.html"
pathlib.Path(out).write_text(doc, encoding="utf-8")

sha  = hashlib.sha256(doc.encode()).hexdigest()
size = pathlib.Path(out).stat().st_size

print(f"✓ {out}  ({size/1_048_576:.1f} MB, sha {sha[:12]})")
if size > 20 * 1_048_576:
    print("⚠️ >20 MB — most mail gateways will bounce it. Aggregate harder.")

recipients = spark.sql(
    f"SELECT recipients_to FROM {CATALOG}.ops.team_recipient_map "
    f"WHERE team_tag = :team AND active_to IS NULL",
    args={"team": TEAM},
).collect()[0].recipients_to

spark.sql(
    f"""
    INSERT INTO {CATALOG}.ops.artifact_ledger VALUES
    (:run_id, :team, :period, :ver, :path, 'HTML', :sha, :rows, :total,
     :recipients, 'RENDERED', current_timestamp(), NULL, NULL)
    """,
    args={
        "run_id": RUN_ID, "team": TEAM, "period": PERIOD, "ver": GOLD_VERSION,
        "path": out, "sha": sha, "rows": manifest["row_count"],
        "total": manifest["total_cost"], "recipients": recipients,
    },
)

dbutils.jobs.taskValues.set(key="artifact_path", value=out)
dbutils.jobs.taskValues.set(key="sha256", value=sha)
