---
name: incident-runbook
description: Produce (or run) a runbook for a data/pipeline incident — detect → severity (SEV1-4) → triage → diagnose (5 whys, lineage blast radius) → mitigate (rollback / object redeploy / backfill / DLQ replay / pause) → validate → resolve → blameless postmortem with action items. Use when a pipeline fails, data goes stale or bad, or cost spikes — or to pre-write a runbook for that incident class.
---

# incident-runbook

Turns a data/pipeline incident (or incident class) into a concrete, step-ordered runbook: how it's detected, how severe, who acts, how to diagnose the blast radius, how to mitigate safely, and how to close it out with a blameless postmortem. Tailored to the incident type — not a generic template.

## When to use

- A live incident: stale data, pipeline failure, bad/corrupt data, or a cost spike.
- Pre-writing a runbook for an incident class so on-call isn't improvising at 2am.
- Someone asks "what do we do when X breaks?" — answer with the ordered runbook.

## Inputs (ASK for any that are missing BEFORE writing the runbook)

- **Incident type / symptom** — stale data, pipeline fail, bad data, schema break, cost/runtime spike.
- **Affected datasets / pipelines** — and their **tier** (gold/critical vs bronze/exploratory).
- **Downstream consumers** — dashboards, ML features, marts, external SLAs.
- **Available levers** — can you rollback? redeploy a single object? backfill? replay a DLQ? pause upstream?

## Steps

1. **Load data-ops knowledge:**
   `mcp__agent-knowledge__search_knowledge(query="data pipeline incident response runbook severity SEV on-call backfill DLQ replay rollback postmortem", role_filter="data-ops", top_k=5)`.
   Fallback if MCP is down: read that role's `knowledge.md`.
2. **Detect** — name the alert/signal that fires (freshness SLA, job failure, DQ check, anomaly, cost guardrail) and where it routes.
3. **Severity** — classify **SEV1** (critical data wrong/outage, external SLA breach) → **SEV4** (cosmetic/no consumer impact). Tie severity to consumer + tier impact, set response time.
4. **Triage / on-call** — who's paged, who's IC, the comms channel, when to escalate.
5. **Diagnose** — **5 whys** to root cause; trace **lineage** to size the **blast radius** (which downstream objects/consumers are tainted).
6. **Mitigate** — pick the safe lever: rollback to last-good version / **object-level redeploy** / **backfill** the affected window / **DLQ replay** / **pause** upstream to stop spread. State preconditions + the un-do.
7. **Validate** — re-run DQ checks, reconcile row counts/metrics, confirm freshness, confirm downstream recovered.
8. **Resolve** — mark resolved, notify consumers, lift any pauses.
9. **Blameless postmortem** — timeline, root cause, what made it worse/better, and **action items with owners + dates** (detection gap, missing check, guardrail).

## Guardrails / Notes

- Stop the spread first — **pause upstream / quarantine bad data** before backfilling, or you reprocess garbage.
- Always size the **blast radius via lineage** before declaring scope; gold-tier consumers raise severity.
- Prefer the **smallest safe lever** (object-level redeploy / windowed backfill) over a full reprocess.
- Postmortem is **blameless** and produces tracked action items — a runbook with no follow-up repeats the incident.
- For bad-data incidents, capture the corrupt sample before overwriting — you need it for root cause.
