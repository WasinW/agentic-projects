# GCP Expert — Comprehensive Knowledge

> Deep reference for the gcp-expert subagent. Production GCP for data + AI workloads.

---

## 1. Foundations

### GCP positioning vs AWS / Azure

| | GCP strength | Weaker |
|---|---|---|
| Data + analytics | BigQuery, Dataflow, Vertex AI | Enterprise stickiness |
| AI | Gemini, Vertex AI, TPUs | Smaller market share |
| Networking | Best global network | Fewer regions |
| Pricing | Per-second billing, sustained-use discounts | Less mature commit programs |
| Open source | Kubernetes origin, Istio, OpenTelemetry | Less SaaS marketplace |

GCP wins on data engineering + ML / AI. AWS wins on breadth. Azure wins on enterprise integration.

### Organization hierarchy

```
Organization
 └── Folder (optional, for separating BUs / envs)
     └── Project (the unit of isolation, billing, IAM)
         └── Resources (BQ datasets, GCE instances, etc.)
```

Best practice: one project per (app, environment, owner).

### Billing
- Billing account → projects (one billing account can fund many projects)
- Cost attribution via labels + folder hierarchy
- Use **Committed Use Discounts (CUDs)** for predictable workloads
- **Sustained-use discounts** apply automatically

---

## 2. Mental Models / Decision Frameworks

### Region + zone strategy

- Most workloads: pick one region (Singapore `asia-southeast1` or Bangkok `asia-southeast2` for Thailand)
- Multi-region only when you genuinely need DR / global latency
- Cross-region egress is expensive

### Compute selector

| Need | Choice |
|---|---|
| Container workload | Cloud Run (simplest), GKE (most control) |
| Stateful service | GKE, or Compute Engine + managed groups |
| Serverless function | Cloud Run Functions (formerly Cloud Functions Gen 2) |
| Batch / job | Cloud Run Jobs, or Batch service |
| ML training | Vertex AI Training |
| Notebooks | Vertex AI Workbench, Colab Enterprise |

Default for new microservices: **Cloud Run**. Move to GKE only when need is clear.

### Data storage selector

| Need | Choice |
|---|---|
| OLTP relational | Cloud SQL (Postgres/MySQL) or AlloyDB (high perf) |
| Global OLTP | Spanner |
| OLAP / warehouse | BigQuery |
| Lakehouse | BigLake Iceberg (Iceberg on GCS) |
| Object storage | Cloud Storage (GCS) |
| Key-value | Memorystore (Redis), Bigtable (large scale) |
| Document | Firestore |
| Vector | Vertex Vector Search, or BQ Vector, or pgvector on Cloud SQL |
| Search | Vertex AI Search |

### BigQuery pricing model decision

- **On-demand** ($6.25/TiB scanned 2026): default for unpredictable workloads
- **Capacity** (commit slots): predictable usage, lower bills above ~2TB/month scanned
- **Editions** (Standard / Enterprise / Enterprise Plus): pick by feature need

Use BigQuery Editions Autoscaler for elasticity.

### Open lakehouse on GCP

The modern pattern (2024-2026):
```
Sources → Dataflow / Datastream → Iceberg on GCS (via BigLake)
                                    ↓
                          BigQuery (external table) for SQL
                          Spark on Dataproc Serverless for transform
                          Vertex AI for ML
```

Benefits: open format, multi-engine, predictable cost. Beats pure BQ for >50TB scenarios.

---

## 3. Standard Practices

### IAM best practices

- Workload Identity > long-lived service account keys
- Service accounts per service, not per env
- Least privilege (use predefined roles + custom roles)
- Folder-level IAM for org-wide policies
- VPC Service Controls for data exfiltration prevention
- Regular access reviews

### Networking

- Default VPC: ok for prototyping, replace for prod
- Shared VPC: central networking team, decentralized projects
- Private Service Connect: connect to managed services privately
- Cloud Load Balancing: global L7 (HTTP), regional L4 (TCP)
- Cloud NAT for outbound from private subnets
- VPC Service Controls: API-level perimeter (data exfiltration prevention)

### Cloud Storage best practices

- Buckets are global names — use unique prefixes
- Storage classes: Standard / Nearline / Coldline / Archive
- Lifecycle policies for auto-transition + delete
- Versioning for important data
- Bucket-level uniform IAM (newer best practice)
- CMEK for encryption with your keys
- Signed URLs for time-limited access
- VPC-SC + Public Access Prevention for sensitive buckets

### BigQuery best practices

- Partition tables on date / int (always)
- Cluster on common filter columns (high cardinality)
- Use Iceberg tables (BigLake) for >50TB
- Materialized views for hot queries
- Avoid SELECT * (scanned bytes = cost)
- INFORMATION_SCHEMA for self-introspection
- BI Engine for sub-second dashboards
- BigQuery ML for in-warehouse models
- Reservations for predictable load

### Dataflow best practices

- Beam Python SDK is fine for most; Java for max perf
- Streaming Engine + Shuffle Service: turn ON
- Flex templates for parameterized jobs
- Tag pipeline with team, app, env labels
- Use Pub/Sub Dead Letter Topic for poison messages
- Monitor system lag + freshness

### Cloud Run patterns

- Stateless services scale 0 → N
- Set CPU "always on" for background work, otherwise CPU only during request
- Min instances > 0 for latency-critical
- Concurrency tuning matters (default 80 might be too high)
- Cloud Run Jobs for batch (replace Cloud Functions for batch use)
- Cloud Run + Vertex AI for ML serving

### Pub/Sub patterns

- Subscriber acks within ack deadline (default 10s, adjustable)
- Dead Letter Topic for failed messages
- Exactly-once delivery (newer feature)
- Schema enforcement (Avro/Protobuf)
- BigQuery / GCS subscriptions for managed sinks

### Vertex AI patterns

- Vertex AI Pipelines (KFP) for orchestration
- Vertex AI Training for managed training
- Vertex AI Model Registry
- Vertex AI Endpoints for online inference
- Vertex AI Feature Store
- Vertex AI Model Monitoring for drift

---

## 4. Tools / Services Map (2026)

### Compute
- **Compute Engine** — VMs
- **GKE / GKE Autopilot** — managed Kubernetes
- **Cloud Run** — serverless containers
- **Cloud Run Functions** — serverless functions
- **Cloud Run Jobs** — batch jobs
- **Batch** — HPC-style batch
- **Cloud Workstations** — managed dev environment

### Storage
- **Cloud Storage** — object
- **Cloud SQL** — managed Postgres/MySQL/SQL Server
- **AlloyDB** — high-perf Postgres
- **Spanner** — global SQL
- **Bigtable** — wide-column NoSQL
- **Firestore** — document
- **Memorystore** — Redis / Memcached
- **Filestore** — managed NFS

### Data / Analytics
- **BigQuery** — warehouse
- **BigLake** — open lakehouse (Iceberg)
- **Dataflow** — stream + batch (Beam)
- **Dataproc** — Spark/Hadoop managed (Serverless and Cluster)
- **Cloud Composer** — managed Airflow
- **Pub/Sub** — messaging
- **Dataform** — SQL transforms (dbt-like)
- **Dataplex** — data fabric / catalog
- **Datastream** — CDC (managed)
- **Data Fusion** — visual ETL (less used)

### AI / ML
- **Vertex AI** — ML platform
- **Vertex AI Generative AI Studio** — model garden
- **Gemini API** — Google's LLM
- **Vertex AI Search** — semantic search
- **Document AI** — document parsing
- **Speech-to-Text / Text-to-Speech**
- **Translation**

### Networking
- **VPC**
- **Cloud Load Balancing**
- **Cloud CDN**
- **Cloud NAT**
- **Cloud Interconnect / VPN**
- **Private Service Connect**

### Security
- **IAM**
- **VPC Service Controls**
- **Cloud KMS / HSM**
- **Secret Manager**
- **Security Command Center**
- **Sensitive Data Protection (DLP)**
- **Identity-Aware Proxy (IAP)**
- **reCAPTCHA Enterprise**

### Observability
- **Cloud Monitoring**
- **Cloud Logging**
- **Cloud Trace**
- **Cloud Profiler**
- **Error Reporting**

### DevOps
- **Cloud Build** — CI/CD
- **Artifact Registry** — container/package registry
- **Cloud Deploy** — managed deploy
- **Cloud Source Repositories** (deprecated path; use GitHub/GitLab)

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Default VPC in production | Wide network, security gaps | Custom VPC + subnets |
| SELECT * in BigQuery | Cost explosion | Specific columns |
| No partition on big tables | Full scans | Partition + cluster |
| Service account keys in code | Credential leak | Workload Identity |
| Cross-region without need | Expensive egress | Single region |
| Cloud SQL for analytics | Wrong tool | BQ |
| Compute Engine for stateless services | Ops burden | Cloud Run |
| No labels | No cost attribution | Mandatory labels |
| Single project for everything | Blast radius, IAM complexity | Project per app/env |
| Public buckets | Data leak risk | Uniform bucket-level access + restrict |
| Streaming everything | Over-cost | Tiered: batch most, stream truly real-time |

---

## 6. Advanced / Expert Topics

### BigQuery internals

- **Dremel-based**: distributed columnar execution
- **Capacitor**: columnar storage format
- **Colossus**: underlying GFS-evolved
- **Slot-hours**: compute unit

Query optimization:
- Avoid wildcards in WHERE on partition column
- Use `_PARTITIONTIME` for ingestion-time partition
- ARRAY/STRUCT for nested (cheaper than joins)
- Approximate aggregations (APPROX_COUNT_DISTINCT) — much cheaper
- BI Engine for sub-second on hot data

### Dataflow internals

- Beam model: ParDo, GroupByKey, Combine, Windowing
- Streaming Engine: separates state from workers
- Shuffle Service: managed shuffle
- Autoscaling: target backlog seconds
- Flex Templates: containerized parameterized jobs
- Iceberg sink (managed I/O) for lakehouse writes

### Open lakehouse with BigLake + Iceberg

- BigLake Iceberg tables: BQ-managed metadata, files in GCS
- BigLake Metastore: catalog for cross-engine access
- Iceberg REST Catalog support (Polaris-compatible)
- Cost: GCS storage (~10x cheaper than BQ active storage at scale)
- Multi-engine: BQ, Spark on Dataproc, Trino

### Vertex AI deep

- **Pipelines** — KFP-based orchestration
- **Custom training** — bring your own image
- **Pre-built models** — Gemini, embedding, code
- **Model Garden** — open models hosted on Vertex
- **Generative AI Studio** — prompt + tuning UI
- **Agent Builder** — RAG + agent toolkit
- **TPU access** — Vertex Training only path (no direct TPU)

### IAM advanced

- Conditional IAM (resource + request attributes)
- Custom roles with specific permissions
- Service account impersonation chains
- Workload Identity Federation (external identities → GCP)
- Organization policies (constraints across projects)

### Networking advanced

- Shared VPC + Service Project pattern
- Private Service Connect for managed services privately
- Network Connectivity Center (hub-spoke)
- Cloud Load Balancer features (URL Maps, backend buckets, IAP, Cloud Armor)
- Cloud Armor: WAF + DDoS

### Multi-region active-active

Rare. Requires:
- Spanner (multi-region instances)
- Global load balancer with backend services per region
- Application-level conflict resolution (or eventually consistent design)
- Higher cost (often 2-3x)

### Cost optimization deep

- **BigQuery**: partition + cluster, materialized views, Iceberg for >50TB, reservations for stable workloads, BQ Editions Autoscaler
- **Compute Engine**: Spot VMs (60-91% off), CUDs for stable
- **GKE**: Spot pods + node pools, autoscaling
- **Storage**: lifecycle policies, Coldline/Archive for backups
- **Networking**: avoid cross-region egress, use Premium Tier for global, Standard for cost-sensitive regional
- **Dataflow**: use Shuffle Service, autoscaling, spot VMs

### Thailand / Asia-Pacific specifics

- Regions available: `asia-southeast1` (Singapore), `asia-southeast2` (Jakarta), `asia-east1` (Taiwan), `asia-east2` (Hong Kong)
- Bangkok region (`asia-southeast3`) — check availability for new launches
- Data residency: PDPA (Thailand) and similar APAC laws
- Latency from Bangkok: Singapore ~30ms, Jakarta ~25ms

---

## 7. References

### Official docs
- **cloud.google.com/docs** — always start here
- **Google Cloud Architecture Center** — reference architectures
- **Solution Guides** for common patterns

### Books
- **Google Cloud Certified Professional Cloud Architect Study Guide** — official prep
- **Google Cloud for Developers** — Hassan Khattak

### Blogs
- **Google Cloud blog** — product announcements
- **Google Cloud Community Medium** — practitioner content
- **GCP Pricing Calculator** — always validate cost claims

### Communities
- **Google Cloud Community** (official forum)
- **r/googlecloud** Reddit
- **Cloud Native Computing Foundation** (CNCF) — broader

### Certifications (signaling)
- Cloud Architect (Professional)
- Data Engineer (Professional)
- Machine Learning Engineer (Professional)

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| Solution Architect | GCP service selection for system design |
| Data Architect | BigLake / BigQuery design |
| Data Engineer | Pipeline implementation |
| AI Architect | Vertex AI patterns |
| Platform Architect | Multi-team GCP org setup |
| DevOps | Cloud Build, GKE, Cloud Run |
| Security | IAM, VPC SC, DLP, KMS |
| Finance | Cost optimization, CUD strategy |

---

*GCP excels for data + AI workloads. Lean into BigQuery + BigLake + Vertex AI as primary differentiators.*
