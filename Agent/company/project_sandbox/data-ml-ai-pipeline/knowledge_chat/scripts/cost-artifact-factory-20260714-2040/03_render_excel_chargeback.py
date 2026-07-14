# Databricks notebook source
# MAGIC %md
# MAGIC # Layer 1b — Excel chargeback pack (PivotTable + slicers)
# MAGIC
# MAGIC For the **Finance** audience. An .xlsx they can pivot and slice in the tool they
# MAGIC already live in is *more* useful than a web chart — and it is the format chargeback
# MAGIC actually gets done in.
# MAGIC
# MAGIC Structure:
# MAGIC - `Summary`   — KPIs + charts (read-only view)
# MAGIC - `Data`      — the raw rows, as a **named Excel Table** (`ListObject`) so a
# MAGIC                 PivotTable in Excel can be inserted on top of it in two clicks
# MAGIC - `Chargeback`— one row per cost_center, ready to paste into the GL
# MAGIC - `About`     — the manifest (run_id, team, period, gold version, sha, row count)
# MAGIC
# MAGIC ⚠️ **`xlsxwriter` cannot author a PivotTable.** No Python library can (the OOXML
# MAGIC pivotCache is not writable by openpyxl/xlsxwriter either). Two honest options:
# MAGIC 1. **Ship a named table + a `Summary` sheet with pre-built charts** — the user hits
# MAGIC    *Insert → PivotTable → the table is already selected*. **This is what this script does.**
# MAGIC 2. Ship a hand-made **template .xlsx that already contains the PivotTable + slicers**
# MAGIC    pointing at a `Data` sheet, and have the job **only replace the `Data` rows**
# MAGIC    (openpyxl, `keep_vba=False`). The pivot refreshes on open. More setup, better UX.
# MAGIC    → Do (1) first; upgrade to (2) if Finance asks.

# COMMAND ----------

# MAGIC %pip install xlsxwriter
# MAGIC %restart_python

# COMMAND ----------

dbutils.widgets.text("team_tag", "")
dbutils.widgets.text("period", "")
dbutils.widgets.text("gold_version", "")
dbutils.widgets.text("run_id", "")

TEAM         = dbutils.widgets.get("team_tag")
PERIOD       = dbutils.widgets.get("period")
GOLD_VERSION = int(dbutils.widgets.get("gold_version"))
RUN_ID       = dbutils.widgets.get("run_id")

assert TEAM, "team_tag is required"

CATALOG = "<catalog>"
GOLD    = f"{CATALOG}.cost.cost_wide"
OUT_DIR = f"/Volumes/{CATALOG}/ops/artifacts/{PERIOD}/{TEAM}"

# COMMAND ----------

df = spark.sql(
    f"""
    SELECT month, resource_group, service, resource_name, cost_center,
           meter_category, SUM(cost) AS cost, SUM(cost_amortized) AS cost_amortized
    FROM   {GOLD} VERSION AS OF {GOLD_VERSION}
    WHERE  tag_team = :team
      AND  month >= add_months(to_date(:period || '01', 'yyyyMMdd'), -12)
    GROUP BY ALL
    ORDER BY month, cost DESC
    """,
    args={"team": TEAM, "period": PERIOD},
).toPandas()

assert len(df) > 0, f"No rows for {TEAM} — refusing to send a blank chargeback pack"
assert len(df) < 100_000, f"{len(df)} rows — Excel attachment caps at 100k and truncates SILENTLY"

chargeback = (df[df["month"].astype(str).str.startswith(f"{PERIOD[:4]}-{PERIOD[4:]}")]
              .groupby("cost_center", dropna=False)[["cost", "cost_amortized"]]
              .sum().reset_index().sort_values("cost", ascending=False))

# COMMAND ----------

import hashlib
import json
import pathlib

import xlsxwriter
from datetime import datetime, timezone

pathlib.Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
out = f"{OUT_DIR}/chargeback_{TEAM}_{PERIOD}.xlsx"

manifest = {
    "run_id": RUN_ID, "team_tag": TEAM, "period": PERIOD,
    "gold_version": GOLD_VERSION, "row_count": int(len(df)),
    "total_cost": float(df["cost"].sum()),
    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
}

wb = xlsxwriter.Workbook(out, {"constant_memory": True, "default_date_format": "yyyy-mm-dd"})

f_title = wb.add_format({"bold": True, "font_size": 15, "font_color": "#CC0000"})
f_hdr   = wb.add_format({"bold": True, "bg_color": "#F0F0F2", "border": 1})
f_money = wb.add_format({"num_format": "#,##0.00"})
f_kpi   = wb.add_format({"num_format": "#,##0", "bold": True, "font_size": 18})
f_note  = wb.add_format({"font_size": 9, "font_color": "#888888", "text_wrap": True})

# ---------------------------------------------------------------- Summary
s = wb.add_worksheet("Summary")
s.set_column("A:A", 26)
s.set_column("B:B", 20)
s.write("A1", f"Cloud Cost — {TEAM.replace('_',' ').title()} — {PERIOD[:4]}-{PERIOD[4:]}", f_title)
s.write("A2", f"INTERNAL — {TEAM} only. Do not forward.", f_note)

by_month = df.groupby("month")["cost"].sum().sort_index()
s.write("A4", "Total this month", f_hdr); s.write_number("B4", float(by_month.iloc[-1]), f_kpi)
s.write("A5", "Previous month",   f_hdr); s.write_number("B5", float(by_month.iloc[-2]) if len(by_month) > 1 else 0, f_money)
s.write("A6", "Rows",             f_hdr); s.write_number("B6", len(df))

s.write("A8", "Month", f_hdr); s.write("B8", "Cost", f_hdr)
for i, (m, v) in enumerate(by_month.items()):
    s.write(8 + i, 0, str(m)); s.write_number(8 + i, 1, float(v), f_money)

ch = wb.add_chart({"type": "column"})
ch.add_series({
    "name":       "Monthly cost",
    "categories": ["Summary", 8, 0, 8 + len(by_month) - 1, 0],
    "values":     ["Summary", 8, 1, 8 + len(by_month) - 1, 1],
    "fill":       {"color": "#CC0000"},
})
ch.set_title({"name": "Monthly trend"})
ch.set_legend({"none": True})
ch.set_size({"width": 620, "height": 300})
s.insert_chart("D4", ch)

# ---------------------------------------------------------------- Data (named table)
d = wb.add_worksheet("Data")
cols = list(df.columns)
d.add_table(0, 0, len(df), len(cols) - 1, {
    "name": "CostData",                       # ← Insert → PivotTable finds this instantly
    "style": "Table Style Medium 2",
    "columns": [{"header": c} for c in cols],
    "data": df.astype(object).where(df.notna(), None).values.tolist(),
})
for i, c in enumerate(cols):
    d.set_column(i, i, 22, f_money if "cost" in c else None)

# ---------------------------------------------------------------- Chargeback
c = wb.add_worksheet("Chargeback")
c.set_column("A:A", 24); c.set_column("B:C", 18)
c.write_row(0, 0, ["cost_center", "cost", "cost_amortized"], f_hdr)
for i, r in enumerate(chargeback.itertuples(index=False), start=1):
    c.write(i, 0, r.cost_center if r.cost_center is not None else "(untagged)")
    c.write_number(i, 1, float(r.cost), f_money)
    c.write_number(i, 2, float(r.cost_amortized), f_money)
c.write(len(chargeback) + 2, 0, "TOTAL", f_hdr)
c.write_formula(len(chargeback) + 2, 1, f"=SUM(B2:B{len(chargeback)+1})", f_money)

# ---------------------------------------------------------------- About (the manifest)
a = wb.add_worksheet("About")
a.set_column("A:A", 22); a.set_column("B:B", 60)
a.write("A1", "Artifact manifest", f_title)
for i, (k, v) in enumerate(manifest.items(), start=3):
    a.write(i, 0, k, f_hdr); a.write(i, 1, str(v))
a.write(len(manifest) + 5, 0, "How to pivot", f_hdr)
a.write(len(manifest) + 5, 1,
        "Go to the Data sheet → click any cell → Insert → PivotTable. "
        "The 'CostData' table is pre-selected. Add slicers from PivotTable Analyze → Insert Slicer.",
        f_note)

wb.close()

# COMMAND ----------

sha  = hashlib.sha256(pathlib.Path(out).read_bytes()).hexdigest()
size = pathlib.Path(out).stat().st_size
print(f"✓ {out}  ({size/1_048_576:.1f} MB, sha {sha[:12]})")

recipients = spark.sql(
    f"SELECT recipients_to FROM {CATALOG}.ops.team_recipient_map "
    f"WHERE team_tag = :team AND active_to IS NULL",
    args={"team": TEAM},
).collect()[0].recipients_to

spark.sql(
    f"""
    INSERT INTO {CATALOG}.ops.artifact_ledger VALUES
    (:run_id, :team, :period, :ver, :path, 'XLSX', :sha, :rows, :total,
     :recipients, 'RENDERED', current_timestamp(), NULL, NULL)
    """,
    args={"run_id": RUN_ID, "team": TEAM, "period": PERIOD, "ver": GOLD_VERSION,
          "path": out, "sha": sha, "rows": manifest["row_count"],
          "total": manifest["total_cost"], "recipients": recipients},
)
