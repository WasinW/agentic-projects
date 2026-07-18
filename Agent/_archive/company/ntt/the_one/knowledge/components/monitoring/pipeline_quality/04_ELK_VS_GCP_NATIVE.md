# 04 - ELK Stack vs GCP Native

> Decision: ELK is overkill for GCP-only pipelines

## What is ELK?

- **E**lasticsearch — search engine for logs
- **L**ogstash — log ingestion/transformation
- **K**ibana — dashboard/visualization

## Comparison

| Feature | GCP Native | ELK (Self-managed) | Elastic Cloud (Managed) |
|---------|:--:|:--:|:--:|
| Setup time | Minutes | Days-weeks | Hours |
| GCP integration | Native | Requires exporters | Via Elastic agent |
| Dataflow metrics | Built-in | Must export via API | Via GCP integration |
| Query power | Good | Excellent | Excellent |
| Dashboard | Good | Excellent (Kibana) | Excellent |
| Long-term retention | Expensive (30d default) | You control | Tiered pricing |
| Cost | Included/predictable | High (infra + ops) | Medium-high |
| Multi-cloud | GCP only | Any cloud | Any cloud |
| Ops burden | Zero (managed) | HIGH | Low |

## GCP Equivalents of ELK Features

| ELK Feature | GCP Equivalent |
|-------------|----------------|
| Elasticsearch (search) | Cloud Logging Logs Explorer |
| Kibana (dashboards) | Cloud Monitoring Dashboards |
| Kibana Discover | Logs Explorer + BigQuery (via Log Router) |
| Logstash (ingest) | Log Router + Cloud Functions |
| ELK Watcher (alerts) | Cloud Monitoring Alerting + Log-based metrics |
| Index Lifecycle Mgmt | Log bucket retention policies |

## Verdict: Use GCP Native

**ELK is overkill** because:
1. All logs already flow to Cloud Logging — no additional ingestion
2. Cloud Monitoring dashboards cover 90% of needs
3. Log-based metrics + alerts = same capability as ELK Watcher
4. Log Router sinks to BQ provide SQL-based log analysis
5. GCP-only — no multi-cloud requirement
6. Self-managed ELK costs $500-2000+/month + engineering time

## When ELK WOULD Make Sense

- Multi-cloud setup (AWS + GCP + on-prem)
- Extremely complex log correlation across 50+ services
- Sub-second log search across petabytes
- Existing ELK expertise and infrastructure
- Need Kibana-specific features (Canvas, Lens)
