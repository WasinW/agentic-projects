# Azure Expert — Comprehensive Knowledge

> Deep reference for the azure-expert subagent. Production Azure for data + AI workloads.

---

## 1. Foundations

### Azure positioning

| | Azure strength | Weaker |
|---|---|---|
| Enterprise integration (Office, Entra ID, AD) | Best-in-class | — |
| Hybrid cloud (Azure Arc, Stack) | Best in industry | — |
| OpenAI integration | Azure OpenAI exclusivity | — |
| Microsoft ecosystem (M365, Power Platform) | Native | — |
| Data + AI | Synapse, Fabric, Databricks partnership | Sprawl across products |
| Linux maturity | Improving | Historically Windows-first |

Strong for banking + government + traditional enterprise. Common in Asia financial services.

### Organization hierarchy

```
Tenant (Entra ID)
 └── Management Group (optional, for policy)
     └── Subscription (billing + isolation)
         └── Resource Group (lifecycle unit)
             └── Resource
```

Best practice: Management Group hierarchy for policy, Subscriptions for billing + workload separation, Resource Groups for lifecycle.

### Regions + AZs

- Bangkok region (`Southeast Asia Thailand`) launched 2024
- Other close regions: Singapore (`Southeast Asia`), Jakarta (`Indonesia Central`)
- Region pairs for paired DR
- Availability Zones (3 in major regions)

---

## 2. Mental Models / Decision Frameworks

### Compute selector

| Need | Choice |
|---|---|
| Container workload | Container Apps (simple), AKS (most control) |
| Stateful service | AKS, VM Scale Sets |
| Serverless function | Functions |
| Batch / job | Batch service, Container Apps Jobs |
| ML training | Azure ML |
| Web PaaS | App Service, Container Apps |
| Windows-specific | Cloud Services / VM |

Default for new microservices: **Container Apps**. AKS only when need is clear.

### Data storage selector

| Need | Choice |
|---|---|
| OLTP relational | Azure SQL Database, PostgreSQL Flexible, MySQL Flexible |
| Global OLTP | Cosmos DB |
| OLAP / warehouse | Synapse (legacy path) or Fabric Warehouse (new path) |
| Lakehouse | OneLake (Fabric) or ADLS Gen2 + Databricks |
| Object storage | ADLS Gen2 / Blob |
| Key-value / document | Cosmos DB |
| Vector | Cosmos DB vector, Azure AI Search, AI Foundry |
| Search | Azure AI Search |

### The Azure data platform fork (2026 reality)

You'll likely choose:
- **Synapse Analytics** (legacy SQL DW + Spark) — established but Microsoft is steering away
- **Microsoft Fabric** (unified analytics platform) — strategic direction
- **Databricks on Azure** — best Spark experience, mature
- **ADLS Gen2 + Synapse Spark** — hybrid

Microsoft's stated direction is Fabric. But Databricks remains the choice for serious lakehouse + ML.

### Banking + financial services specific

Banking on Azure typical pattern:
- Synapse + Databricks for analytics + ML
- Azure SQL + Cosmos for OLTP
- Service Bus for messaging
- Sentinel for SIEM
- Defender for Cloud for security posture
- Strong Entra ID integration with on-prem AD

---

## 3. Standard Practices

### Identity (Entra ID — formerly Azure AD)

- Workload Identity (Managed Identity) > SP secrets
- Conditional Access for adaptive auth
- Privileged Identity Management (PIM) for just-in-time elevated access
- B2B Collaboration for partner access
- B2C for customer-facing apps
- Federation with on-prem AD via AD Connect

### RBAC

- Built-in roles + custom roles
- Scope: Management Group → Subscription → RG → Resource
- Least privilege
- Access reviews quarterly

### Networking

- VNet per workload
- Hub-and-spoke topology common (Azure Firewall in hub)
- Private Endpoints for PaaS (replaces Service Endpoints)
- Application Gateway for L7 WAF
- Front Door for global routing + CDN
- ExpressRoute for hybrid

### ADLS Gen2 best practices

- Hierarchical namespace ON
- Lifecycle policies (Hot → Cool → Archive)
- Soft delete + versioning
- Private Endpoints
- CMEK with Key Vault
- Diagnostic logging to Log Analytics

### Synapse / Fabric patterns

**Synapse**:
- Dedicated SQL pool (legacy MPP) — predictable workloads
- Serverless SQL pool — ad-hoc on lake
- Spark pool — Spark managed
- Pipelines (Data Factory-derived)

**Fabric**:
- OneLake = unified data lake
- Warehouse (T-SQL)
- Lakehouse (Delta tables)
- Notebooks (Spark)
- Pipelines
- Real-Time Analytics (KQL)
- Power BI integration

### Azure ML patterns

- Workspaces as the unit of org
- Compute clusters for training
- Endpoints (managed, K8s)
- Model registry
- Pipelines
- AutoML for baseline

### Azure OpenAI

- Microsoft's exclusive OpenAI partnership advantage
- Deployments in your tenant + region
- Provisioned Throughput Units (PTU) for guaranteed capacity
- Content Safety
- On Your Data feature for managed RAG

### Cosmos DB patterns

- Multi-API (SQL, MongoDB, Cassandra, Gremlin, Table)
- Multi-region writes
- Consistency levels (5 — strong to eventual)
- Partition key design is critical
- Vector search (recent feature)
- RU-based billing or serverless

---

## 4. Services Map (2026)

### Compute
- **Virtual Machines** + VM Scale Sets
- **AKS** — managed Kubernetes
- **Container Apps** — serverless containers
- **Container Instances** — single containers
- **Functions** — serverless functions
- **App Service** — web apps PaaS
- **Batch** — batch jobs
- **Service Fabric** — legacy
- **Spring Apps**

### Storage
- **Storage Account** (Blob, ADLS Gen2, Files, Queue, Table)
- **Managed Disks**
- **NetApp Files** — high-perf NFS/SMB

### Databases
- **Azure SQL Database** (single + elastic pool + managed instance)
- **PostgreSQL / MySQL Flexible**
- **Cosmos DB** — multi-API NoSQL
- **Cache for Redis**
- **Database for MariaDB** (deprecating)

### Data / Analytics
- **Microsoft Fabric** — unified analytics
- **Synapse Analytics** — SQL DW + Spark + Pipelines
- **Databricks (Azure)** — best Spark + ML
- **Data Factory** — orchestration / ETL
- **Stream Analytics** — managed streaming
- **Event Hubs** — Kafka-like
- **Event Grid** — eventing
- **Service Bus** — messaging
- **HDInsight** — legacy Hadoop

### AI / ML
- **Azure ML** — ML platform
- **Azure OpenAI** — OpenAI models
- **AI Foundry** (formerly Azure AI Studio) — GenAI building
- **AI Search** (formerly Cognitive Search)
- **AI Document Intelligence** (formerly Form Recognizer)
- **AI Vision / Speech / Translator / Language**
- **Bot Service**
- **AI Content Safety**

### Networking
- **VNet, Subnets, NSGs**
- **VPN Gateway**
- **ExpressRoute** — dedicated
- **Application Gateway** — L7 + WAF
- **Front Door** — global L7 + CDN
- **Traffic Manager** — DNS-based
- **Firewall** — network firewall
- **Private Link / Endpoints**

### Security
- **Entra ID** (formerly Azure AD)
- **Key Vault**
- **Defender for Cloud** — security posture
- **Sentinel** — SIEM + SOAR
- **Microsoft Purview** — data governance + DLP

### Observability
- **Monitor** — metrics + logs
- **Application Insights** — APM
- **Log Analytics** — log queries (KQL)
- **Managed Grafana / Prometheus**

### DevOps
- **DevOps Services** (Boards, Repos, Pipelines)
- **GitHub Enterprise + Actions** (Microsoft-owned, increasingly preferred)
- **Container Registry**
- **Bicep / ARM Templates** — IaC
- **Terraform** support

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Service Principal secrets in code | Credential theft | Managed Identity |
| Default network rules | Open SQL/storage | NSG + Private Endpoints |
| Mixing IaaS + PaaS in same RG | Mixed lifecycle | Separate RGs by lifecycle |
| Synapse dedicated SQL for variable workloads | Idle cost | Serverless or Fabric |
| Public Blob containers | Data exposure | Private + signed URLs |
| Single subscription | Quota + blast radius | Multi-subscription |
| No Defender for Cloud | Security blind spots | Enable Defender |
| ADF dataflow over Spark | Limited debugging | Databricks/Synapse Spark for transforms |
| Hardcoded connection strings | Secrets in code | Key Vault references |
| No backup configured | Data loss | Backup vault + policy |

---

## 6. Advanced / Expert Topics

### Microsoft Fabric architecture

OneLake = single logical lake across the org:
- Storage on ADLS Gen2 with Delta Parquet
- Shortcuts (no-copy data sharing)
- Multiple compute experiences (Warehouse SQL, Lakehouse Spark, KQL Real-Time, Notebooks, Power BI)
- Capacity unit billing (F-SKUs)

Strong for Microsoft-aligned shops. Newer + evolving.

### Databricks on Azure deep

- Unity Catalog for governance
- Photon engine for SQL acceleration
- Delta Live Tables for declarative pipelines
- Mosaic ML / MLflow for ML
- Databricks SQL for serving

### Azure Landing Zone

The Microsoft Cloud Adoption Framework standard:
- Management group hierarchy
- Connectivity subscription
- Identity subscription
- Management subscription
- Workload landing zones

Setup via the Azure Landing Zone accelerator.

### Hybrid + multi-cloud

- **Azure Arc**: manage non-Azure resources
- **Azure Stack** (Edge, Hub, HCI): on-prem Azure
- **Azure Local** (next-gen, 2025+)

Strong story but operational complexity.

### Service Bus vs Event Hubs vs Event Grid

| | Service Bus | Event Hubs | Event Grid |
|---|---|---|---|
| Pattern | Queue / topic | Stream (Kafka-like) | Event routing |
| Use | Business messages, FIFO | Telemetry, high throughput | Reactive events, SaaS integration |
| Retention | Days | Days | Brief |

### Cosmos DB design

- Choose partition key for even distribution + access pattern
- Pre-compute aggregates with change feed
- Auto-scale or manual RU/s
- Multi-region writes for global apps
- Continuous backup option

### Azure ML production

- Endpoint types: managed online, batch, K8s
- Pipelines for orchestration
- Component-based design
- Model registry
- Data drift monitoring
- Responsible AI dashboard

### Cost optimization

- **Compute**: Reserved Instances (1y / 3y), Spot VMs, B-series for burstable
- **Azure Hybrid Benefit**: Windows + SQL licensing reuse
- **ADLS**: lifecycle policies, Cool/Archive tiers
- **Synapse**: pause dedicated SQL pools, use Serverless for ad-hoc
- **Networking**: avoid cross-region, use Private Link
- **Right-size weekly**

### Compliance

- Microsoft Purview for data governance + DLP
- Microsoft Defender for Cloud for posture
- Compliance Manager for regulatory mapping
- ISO/IEC 27001, SOC, GDPR, PDPA — Azure has broad compliance coverage

### Fabric Real-Time Intelligence (RTI)

**What it is**: The 2025 rebrand of Fabric Real-Time Analytics into a full streaming stack. Core pieces:
- **Eventstream** — no-code ingest + transform (Kafka, Event Hubs, CDC, IoT) routed to destinations
- **Eventhouse** — the database container; holds one or more **KQL databases** (Kusto engine) tuned for time-series + semi/unstructured events, billions of rows queried in seconds. OneLake availability mirrors data to Delta automatically
- **Real-Time Dashboards** + **Activator** (GA early 2025) for event-driven alerting/actions

**When to use vs Databricks/Synapse**: RTI is the answer สำหรับ sub-second telemetry, log/event analytics, and "act on a stream" patterns — not batch ETL or heavy ML. Reach for Databricks when you need serious Spark/lakehouse + MLflow; Synapse only on legacy estates. RTI + Databricks coexist via OneLake shortcuts (no copy).

**Banking relevance**: real-time fraud signals, transaction-stream monitoring, card-auth telemetry, AML alerting. KQL is the same dialect as Sentinel/Log Analytics — security + data teams share skills.

Ref: https://learn.microsoft.com/en-us/fabric/real-time-intelligence/

### Microsoft Purview (unified)

**What it is**: Microsoft's consolidated governance + security suite (the old "Azure Purview" standalone is now folded into the unified Purview portal). Pillars: **Data Map** (automated scanning/lineage across Azure, on-prem, AWS/GCP, Fabric), **Unified Catalog** (business glossary + data products), **classification** (200+ built-in sensitive-info types + custom), **sensitivity labels**, and **DLP** that now covers structured data in Fabric/OneLake (lakehouses, warehouses, semantic models).

**When to use**: any regulated estate needing a single data-map + governance plane; native governance for Fabric is Purview.

**Banking relevance**: PDPA/GDPR data subject mapping, PII discovery + masking, lineage for BCBS 239 / regulator audit, Adaptive Protection feeds insider-risk signals into Conditional Access. Pair with Defender for Cloud (posture) and Compliance Manager (control mapping).

Ref: https://learn.microsoft.com/en-us/purview/purview

### Entra ID Conditional Access (adaptive)

**What it is**: the Zero Trust policy engine that goes well beyond static RBAC — evaluates signals at sign-in and grants/blocks/steps-up. Key conditions: **sign-in & user risk** (needs Entra ID Protection, P2 — leaked-credential/anomaly scoring), **device compliance** (Intune-managed / hybrid-joined required), **named locations** (IP ranges, countries, trusted HQ/VPN), and **compliant network** check via Global Secure Access to blunt token theft/replay.

**When to use**: default for every tenant — enforce MFA + compliant device on admin and data-platform access; risk-based step-up for the rest.

**Banking relevance**: regulator-grade access control over Synapse/Fabric/Databricks workspaces and Key Vault; block foreign-country sign-ins, require managed devices for production data, just-in-time elevation via PIM layered on top.

Ref: https://learn.microsoft.com/en-us/entra/identity/conditional-access/overview

### Azure Arc (deep)

**What it is**: projects non-Azure resources into Azure Resource Manager so they get one control plane — **Arc-enabled servers** (on-prem/other-cloud VMs get Policy, Defender, Monitor, Update Manager), **Arc-enabled Kubernetes** (any CNCF cluster incl. EKS/GKE — GitOps, Policy, Defender), and **Arc-enabled data services** (run Azure SQL Managed Instance / PostgreSQL on your own K8s, edge or cloud). Note: indirectly-connected mode retired Sept 2025 — plan for connected mode.

**When to use**: multi-cloud or hybrid governance, consistent policy/security posture across estates, or keeping data on-prem for residency while using Azure tooling.

**Banking relevance**: data-residency mandates (run managed SQL on-prem yet govern from Azure), unified Defender/Policy compliance across legacy datacenter + cloud, single audit surface.

Ref: https://learn.microsoft.com/en-us/azure/azure-arc/overview

---

## 7. References

### Official
- **docs.microsoft.com/azure** — vast
- **Azure Well-Architected Framework**
- **Azure Architecture Center**
- **Cloud Adoption Framework**

### Books
- **Cloud Adoption Framework for Azure**
- **Azure for Architects** — Ritesh Modi
- **The Developer's Guide to Microsoft Azure**

### Communities
- **Microsoft Tech Community**
- **Microsoft Learn** (training + certs)
- **r/AZURE** Reddit

### Certifications
- AZ-104 (Administrator)
- AZ-204 (Developer)
- AZ-305 (Solutions Architect Expert)
- DP-203 (Data Engineer)
- AI-102 (AI Engineer)

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| Solution Architect | Azure service selection |
| Data Architect | Synapse / Fabric / Databricks trade-offs |
| Data Engineer | ADF + Databricks pipelines |
| AI Architect | Azure OpenAI + AI Foundry |
| Platform Architect | Landing Zone, multi-subscription |
| DevOps | Azure DevOps / GitHub Actions |
| Security | Entra ID, Defender, Sentinel |
| Compliance | Purview |

---

*Azure = best for Microsoft-aligned + regulated enterprise. Strong AI story via Azure OpenAI exclusivity.*
