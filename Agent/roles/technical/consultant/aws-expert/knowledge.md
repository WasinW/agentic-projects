# AWS Expert — Comprehensive Knowledge

> Deep reference for the aws-expert subagent. Production AWS for data + AI workloads.

---

## 1. Foundations

### AWS positioning

| | AWS strength | Weaker |
|---|---|---|
| Breadth of services | Largest catalog | Sprawl + complexity |
| Marketplace + ISV ecosystem | Largest | — |
| Enterprise adoption | Largest market share | — |
| Data + AI | S3 + EMR + SageMaker + Bedrock | Less AI-product focus than Google |
| Pricing transparency | Improving | Still complex |

### Organization hierarchy

```
Organization (multi-account)
 └── OU (Organizational Unit)
     └── Account (the unit of isolation, billing, IAM)
         └── Resources
```

AWS best practice: many accounts, segmented by env + workload + team.
- Use AWS Control Tower / Landing Zone for setup.
- SCPs (Service Control Policies) at OU level.
- Centralized billing in management account.

### Regions + AZs

- Region: independent geographic area (us-east-1, ap-southeast-1)
- AZ: isolated datacenter within region
- Multi-AZ for HA within region; multi-region for DR
- Singapore (`ap-southeast-1`) and Jakarta (`ap-southeast-3`) closest to Thailand

---

## 2. Mental Models / Decision Frameworks

### Compute selector

| Need | Choice |
|---|---|
| Container workload | ECS / Fargate (simple), EKS (most control) |
| Stateful service | EC2 + Auto Scaling Group, EKS StatefulSets |
| Serverless function | Lambda |
| Batch / job | AWS Batch, Step Functions + Lambda, Fargate one-off |
| ML training | SageMaker Training |
| HPC | ParallelCluster, EC2 + Spot |
| Web app PaaS | App Runner |

Default for new microservices: **ECS Fargate** or **App Runner**. EKS only when need is clear.

### Data storage selector

| Need | Choice |
|---|---|
| OLTP relational | RDS (Postgres/MySQL/etc), Aurora (cloud-native) |
| Global OLTP | Aurora Global, DynamoDB Global Tables |
| OLAP / warehouse | Redshift, or Athena on S3 |
| Lakehouse | S3 + Iceberg (via Glue / EMR) |
| Object storage | S3 |
| Key-value | DynamoDB (preferred), ElastiCache (Redis) |
| Document | DocumentDB, DynamoDB |
| Time-series | Timestream |
| Vector | OpenSearch (k-NN), Aurora pgvector, Pinecone (external) |

### Account strategy

- **Foundation** accounts: log archive, audit, network hub
- **Sandbox** accounts per developer / team
- **Workload** accounts per app per env (dev/stg/prod)
- Cross-account access via IAM roles, not users

### Lakehouse on AWS

```
Sources → DMS / Kinesis / MSK → S3 + Iceberg (Glue Catalog)
                                  ↓
                          Athena (SQL)
                          EMR (Spark)
                          Redshift Spectrum (federated)
                          SageMaker (ML)
```

---

## 3. Standard Practices

### IAM best practices

- IAM Identity Center (formerly SSO) for human access
- Roles + STS, not long-lived access keys
- Cross-account roles for shared services
- IAM Access Analyzer for over-privilege detection
- Permissions Boundaries for delegated admin
- SCPs to enforce account-level guardrails

### S3 patterns

- Bucket per app + env
- Versioning + lifecycle policies + Object Lock for compliance
- Server-side encryption (SSE-S3, SSE-KMS, SSE-C)
- S3 Storage Classes: Standard / IA / Glacier / Glacier Deep Archive
- S3 Intelligent-Tiering for unpredictable access
- VPC Endpoints for private access
- Block Public Access at account level (default ON)

### Lambda patterns

- Cold start: provision concurrency for hot lambdas
- Memory ~= CPU allocation, optimize together
- 15 min max — for longer, use Step Functions or Fargate
- Async triggers: SQS, EventBridge, DynamoDB Streams
- Lambda Powertools (Python, TypeScript) for observability

### DynamoDB patterns

- Single-table design (one table per service)
- Composite keys (PK + SK)
- GSIs for alternative access patterns
- DAX for caching
- Streams for change capture (downstream to lambda)
- On-demand vs Provisioned (provisioned cheaper for stable load)
- Global Tables for multi-region

### Kinesis vs MSK vs EventBridge vs SNS+SQS

- **Kinesis Data Streams**: ordered, retain, replay (Kafka-lite)
- **MSK** (Managed Kafka): full Kafka, more cost + complexity
- **EventBridge**: schemas, rules, SaaS integrations
- **SNS+SQS**: simple pub/sub, fan-out
- **Kinesis Firehose**: stream to S3/Redshift, no code

### RDS / Aurora

- Aurora cheaper at scale (decoupled storage)
- Multi-AZ for HA (not DR)
- Read replicas for read scaling
- Performance Insights for monitoring
- Aurora Serverless v2 for variable load
- DMS for migration / CDC

### Networking

- VPC per workload account
- Transit Gateway for multi-VPC connectivity
- VPC Endpoints (Interface and Gateway) for private service access
- PrivateLink for SaaS / partner access
- AWS Network Firewall for centralized filtering
- WAF + Shield for L7 protection

### EKS / ECS

- ECS Fargate: simplest container hosting
- EKS: when need Kubernetes ecosystem
- Karpenter for EKS autoscaling
- Fargate for EKS: serverless pods

---

## 4. Services Map (2026)

### Compute
- **EC2** — VMs
- **ECS** — managed containers (with Fargate for serverless)
- **EKS** — managed Kubernetes
- **Lambda** — serverless functions
- **App Runner** — simple PaaS for containers
- **Batch** — batch jobs
- **Lightsail** — simple VPS

### Storage
- **S3** — object
- **EBS** — block storage
- **EFS** — file (NFS)
- **FSx** — managed file (Windows / Lustre / NetApp / OpenZFS)
- **Storage Gateway** — hybrid
- **DataSync** — bulk transfer

### Databases
- **RDS** — managed Postgres/MySQL/SQL Server/Oracle
- **Aurora** — cloud-native
- **DynamoDB** — NoSQL KV/document
- **DocumentDB** — Mongo-compatible
- **Neptune** — graph
- **Keyspaces** — Cassandra-compatible
- **Timestream** — time-series
- **MemoryDB** — Redis-compatible, durable
- **ElastiCache** — Redis / Memcached

### Data / Analytics
- **Redshift** — warehouse
- **Athena** — query S3 (Trino-based)
- **EMR / EMR Serverless** — Spark + Hadoop
- **Glue** — ETL, catalog, schema registry
- **Lake Formation** — lake governance
- **Kinesis** (Data Streams, Firehose, Analytics)
- **MSK** — managed Kafka
- **MWAA** — managed Airflow
- **OpenSearch** — search + vector

### AI / ML
- **SageMaker** — ML platform
- **Bedrock** — foundation model API (Anthropic Claude, Llama, Mistral, etc.)
- **Comprehend** — NLP
- **Rekognition** — image
- **Polly** — TTS
- **Transcribe** — STT
- **Translate**
- **Textract** — OCR
- **Personalize** — recommendations
- **Forecast** — time-series

### Networking
- **VPC**
- **Transit Gateway**
- **Direct Connect / VPN**
- **CloudFront** — CDN
- **Route 53** — DNS
- **API Gateway**
- **App Mesh** — service mesh
- **Global Accelerator**

### Security
- **IAM, Identity Center**
- **KMS, CloudHSM**
- **Secrets Manager, Parameter Store**
- **Shield, WAF, Network Firewall**
- **GuardDuty** — threat detection
- **Security Hub** — central view
- **Macie** — PII discovery
- **Inspector** — vulnerability scanning
- **CloudTrail** — audit

### Observability
- **CloudWatch** (metrics, logs, alarms)
- **X-Ray** — tracing
- **CloudTrail** — audit logs
- **AMP** — managed Prometheus
- **AMG** — managed Grafana

### DevOps
- **CodePipeline / CodeBuild / CodeDeploy** — CI/CD
- **CDK** — IaC in code
- **CloudFormation** — IaC declarative
- **ECR** — container registry
- **Systems Manager** — ops automation

---

## 5. Anti-Patterns

| Anti-pattern | Issue | Better |
|---|---|---|
| Long-lived IAM access keys | Credential theft risk | IAM roles + STS |
| Root account daily usage | Security | Reserve root, use IAM Identity Center |
| Single account everything | Blast radius | Multi-account org |
| EC2 for stateless services | Ops burden | ECS Fargate / Lambda |
| Public S3 buckets | Data breach | Block public access, signed URLs |
| Hot-key DynamoDB | Throttling | Distribute partition keys |
| No tagging | No cost attribution | Mandatory tag policy |
| Cross-region data transfer | Expensive egress | Single region or CDN |
| Unencrypted RDS | Compliance gap | Encrypt + KMS |
| Ad-hoc Lambda code in console | No versioning | CI/CD + IaC |
| No VPC endpoints | NAT cost + public traffic | VPC endpoints for AWS services |
| EBS for shared data | Single attach | EFS or FSx |

---

## 6. Advanced / Expert Topics

### Account vending pattern

- Control Tower for new account provisioning
- AFT (Account Factory for Terraform) for IaC-driven vending
- Centralized log archive + audit accounts
- Standard guardrails via SCPs

### Hub-and-spoke networking

- Transit Gateway connects accounts + on-prem
- Network firewall for centralized inspection
- Shared services (DNS, AD) in central hub

### Lake Formation

- Centralized data lake permissions
- Tag-based access control
- Cross-account data sharing
- Row-level + column-level + cell-level security

### Aurora deep

- Aurora I/O-Optimized: predictable cost when high I/O
- Global database for cross-region with low RPO
- Aurora Serverless v2: granular scaling, supports more features than v1
- Blue/Green deployments for major version upgrades

### SageMaker MLOps

- SageMaker Pipelines for orchestration
- Model Registry
- Endpoints (real-time, async, serverless)
- Multi-Model Endpoints for cost efficiency
- Shadow testing for safer rollouts
- Feature Store
- Model Monitor for drift

### Bedrock for GenAI

- Single API for multiple foundation models (Claude, Llama, Titan, Cohere, Mistral)
- Knowledge Bases for managed RAG
- Agents for tool use
- Guardrails for content filtering
- Provisioned throughput for guaranteed capacity

### Cost optimization

- **Compute**: Spot (60-90% off), Savings Plans, Reserved Instances
- **S3**: Intelligent-Tiering, lifecycle rules, deduplication
- **DynamoDB**: on-demand vs provisioned analysis
- **Networking**: VPC endpoints, CloudFront caching, reduce cross-AZ traffic
- **RDS**: right-size, reserved, Aurora I/O-Optimized
- **Lambda**: tune memory + concurrency, Graviton

### Multi-region strategies

- Active-active: harder (Aurora Global, DynamoDB Global Tables, Route 53 latency routing)
- Active-passive: easier, lower cost (CloudEndure / DRS for fast failover)
- Pilot light: minimal infra in DR region, scale up on failover
- Backup + restore: cheapest, slowest

---

## 7. References

### Official
- **docs.aws.amazon.com** — vast
- **AWS Well-Architected Framework** — 6 pillars
- **AWS Solutions Library** — reference architectures
- **AWS Architecture Center**

### Books
- **AWS Certified Solutions Architect Official Study Guide**
- **AWS Cookbook** (O'Reilly)
- **Modern DevOps Practices** (covers AWS heavily)

### Blogs
- **AWS Architecture Blog**
- **AWS Big Data Blog**
- **AWS Machine Learning Blog**

### Communities
- **AWS Forum** (deprecated, moved to re:Post)
- **r/aws** Reddit
- **AWS Community Builders** program

### Certifications
- Solutions Architect (Associate, Professional)
- Data Engineer
- Machine Learning Engineer
- Security Specialty

---

## 8. Working With Other Roles

| Role | Common discussion |
|---|---|
| Solution Architect | AWS service selection |
| Data Architect | S3 + Iceberg / Redshift trade-offs |
| Data Engineer | Glue / EMR / Athena |
| AI Architect | Bedrock + SageMaker patterns |
| Platform Architect | Multi-account org strategy |
| DevOps | CodePipeline / IaC |
| Security | Identity, encryption, audit |
| Finance | Savings Plans, RI strategy |

---

*AWS = breadth + maturity + complexity. Mastery is knowing which service to pick from many overlapping options.*
