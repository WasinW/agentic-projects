# References — Sources for All Documents

> Aggregated sources used in research for all documents in this folder
> รวม sources ทั้งหมดจาก deep research ปี 2026

---

## 1. Books & Standard Frameworks

### Foundational Books
- **Fundamentals of Data Engineering** — Joe Reis & Matt Housley, O'Reilly 2022
  - The "6 Undercurrents" framework (Security, Data Management, DataOps, Architecture, Orchestration, Software Engineering)
  - https://www.oreilly.com/library/view/fundamentals-of-data/9781098108298/
  
- **Designing Data-Intensive Applications** — Martin Kleppmann, O'Reilly 2017
  - Bible of distributed data systems

- **The DataOps Cookbook** — DataKitchen
  - DataOps practices

- **Data Management at Scale** — Piethein Strengholt, O'Reilly 2020
  - Federated data architecture patterns

### Standards & Specifications
- **DAMA-DMBOK 2** — Data Management Body of Knowledge
  - 11 Knowledge Areas: Governance, Architecture, Modeling, Storage, Security, Integration, Content Management, Master/Reference Data, Analytics, Metadata, Quality
  - https://dama.org/learning-resources/dama-data-management-body-of-knowledge-dmbok/
  - https://atlan.com/dama-dmbok-framework/
  - https://www.snowflake.com/en/fundamentals/data-governance/framework/dama-dmbok/

- **DataOps Manifesto** — 18 principles for DataOps
  - https://dataopsmanifesto.org

- **OpenLineage Specification**
  - https://openlineage.io/
  - https://github.com/OpenLineage/OpenLineage
  - https://github.com/OpenLineage/OpenLineage/blob/main/spec/OpenLineage.md

- **Data Contract Specification**
  - https://datacontract.com
  - https://github.com/datacontract/datacontract-cli
  - http://cli.datacontract.com/

---

## 2. Modern Data Architecture (2026)

### Pattern Comparisons
- **2026 State of Modern Data Architecture: Benchmark Report**
  - https://dataforest.ai/blog/state-of-modern-data-architecture-benchmark-report

- **Data Lakehouse vs Data Warehouse vs Data Fabric: 2026 Architecture Comparison**
  - https://promethium.ai/guides/data-lakehouse-vs-data-warehouse-vs-data-fabric-2026/

- **Modern Data Architecture: Mesh, Fabric & Lakehouse** — Informatica
  - https://www.informatica.com/resources/articles/modern-data-architecture.html

- **Data Mesh vs. Lakehouse vs. Data Fabric: Which Architecture Wins in 2026?** — Engine Analytics
  - https://engineanalytics.tech/data-mesh-vs-lakehouse-vs-data-fabric-which-architecture-wins-in-2026/

- **Deciphering Data Architectures: When to Use a Warehouse, Fabric, Lakehouse, or Mesh** — James Serra
  - https://www.jamesserra.com/archive/2025/05/deciphering-data-architectures-when-to-use-a-warehouse-fabric-lakehouse-or-mesh/

- **Data Fabric vs. Data Mesh: 2026 Guide to Modern Data Architecture** — Alation
  - https://www.alation.com/blog/data-mesh-vs-data-fabric/

- **Understanding Modern Data Architecture: An Evolution from Warehouses to Mesh** — Addepto
  - https://addepto.com/blog/understanding-modern-data-architecture-an-evolution-from-warehouses-to-mesh/

- **Enterprise Data Architecture: Complete Strategy Guide [2026]**
  - https://dataforest.ai/blog/enterprise-data-architecture-guide

- **Reference Architecture Models for Big Data and Analytics** — GlobalLogic
  - https://www.globallogic.com/insights/white-papers/reference-architecture-models-for-big-data-and-analytics/

---

## 3. GCP / Cloud-Specific (Lakehouse)

### BigLake + Iceberg
- **BigLake — Apache Iceberg Lakehouse** — Google Cloud
  - https://cloud.google.com/biglake

- **BigLake tables for Apache Iceberg in BigQuery overview** — GCP Docs
  - https://docs.cloud.google.com/biglake/docs/biglake-iceberg-tables-in-bigquery

- **Apache Iceberg tables | BigQuery** — GCP Docs
  - https://docs.cloud.google.com/bigquery/docs/biglake-iceberg-tables-in-bigquery

- **BigLake metastore now supports Iceberg REST Catalog** — Google Cloud Blog
  - https://cloud.google.com/blog/products/data-analytics/biglake-metastore-now-supports-iceberg-rest-catalog

- **Building Apache Iceberg Lakehouse Architecture on GCP with BigLake, BigQuery, Pubsub and Dataflow**
  - https://gist.github.com/wayneweicheng/2f80ca7ea2f05acd1b062458d9f25e44

- **GCP Data Platform Architecture: Strategic Patterns**
  - https://adriennevermorel.com/articles/gcp-data-platform-architecture/

- **Building a modern lakehouse on Google Cloud with Apache Iceberg** — Egen
  - https://egen.ai/insights/building-a-modern-lakehouse-on-google-cloud-with-apache-iceberg/

- **The Open Data Lakehouse: Architecting with BigQuery, BigLake, and Apache Iceberg** — Kartaca
  - https://kartaca.com/en/the-open-data-lakehouse-architecting-with-bigquery-biglake-and-apache-iceberg/

- **Lakehouse Demystified — Part 1: Just enough about the lakehouse stack on Google Cloud** — Anagha Khanolkar (Google) on Medium
  - https://medium.com/google-cloud/lakehouse-demystified-part-1-just-enough-about-the-lakehouse-stack-on-google-cloud-02529daa52af

### Dataflow / Beam
- **Beam SQL: Overview** — Apache Beam
  - https://beam.apache.org/documentation/dsls/sql/overview/

- **Beam ZetaSQL overview** — Apache Beam (note: removed in 2.68.0+)
  - https://beam.apache.org/documentation/dsls/sql/zetasql/overview/

- **Using the Google Cloud Dataflow Runner** — Apache Beam
  - https://beam.apache.org/documentation/runners/dataflow/

- **Exploring Beam SQL on Google Cloud Platform** — Graham Polley
  - https://medium.com/weareservian/exploring-beam-sql-on-google-cloud-platform-b6c77f9b4af4

- **Apache Beam SQL** — mkuthan blog
  - https://mkuthan.github.io/blog/2022/09/14/beam-sql/

### Dataproc Serverless vs Dataflow
- **Serverless Spark on GCP: How does it compare with Dataflow?** — Stack Labs (DEV.to)
  - https://dev.to/stack-labs/serverless-spark-on-gcp-how-does-it-compare-with-dataflow--2o8n
  - **Key insight**: Dataproc Serverless does NOT support Spark Streaming

- **How to Choose Between Dataflow and Dataproc for Batch Data Processing on GCP**
  - https://oneuptime.com/blog/post/2026-02-17-how-to-choose-between-dataflow-and-dataproc-for-batch-data-processing-on-gcp/view

- **GCP. Detailed Comparison of Dataflow vs Dataproc** — Edhar
  - https://medium.com/@avuzia/gcp-detailed-comparison-of-dataflow-vs-dataproc-871b2f3ad72d

---

## 4. Data Quality

### Dimensions & Frameworks
- **Data Quality Dimensions: The No-BS Guide with Examples** — Soda
  - https://soda.io/blog/guide-to-data-quality-dimensions

- **Data quality dimensions: What they are and how to incorporate them** — dbt Labs
  - https://www.getdbt.com/blog/data-quality-dimensions

- **The Complete Guide to Data Quality: Frameworks, Tools, and Best Practices** — Soda
  - https://soda.io/blog/guide-data-quality-frameworks-tools-best-practices

- **6 Data Quality Dimensions: Complete Guide with Examples and Measurement Methods** — iceDQ
  - https://icedq.com/6-data-quality-dimensions

- **What Are Data Quality Dimensions?** — IBM
  - https://www.ibm.com/think/topics/data-quality-dimensions

- **How to build reliable data pipelines with data quality checks** — dbt Labs
  - https://www.getdbt.com/blog/data-pipeline-quality-checks

### Tools Comparison
- **dbt vs Great Expectations vs Soda: Which Data Quality Tool to Choose** — Cybersierra
  - https://cybersierra.co/blog/best-data-quality-tools/

---

## 5. Data Observability

### Five Pillars (Monte Carlo)
- **What Is Data Observability? 5 Key Pillars To Know In 2026** — Monte Carlo
  - https://www.montecarlodata.com/blog-what-is-data-observability/

- **Introducing the 5 Pillars of Data Observability** — Barr Moses, TDS
  - https://medium.com/data-science/introducing-the-five-pillars-of-data-observability-e73734b263d5

- **Incident Prevention For Data Teams: Introducing The 5 Pillars Of Data Observability** — Monte Carlo
  - https://www.montecarlodata.com/blog-introducing-the-5-pillars-of-data-observability/

- **5 pillars of data observability bolster data pipeline** — TechTarget
  - https://www.techtarget.com/searchdatamanagement/tip/Pillars-of-data-observability-bolster-data-pipeline

- **Data Observability: Key Concepts, Benefits & the 5 Pillars Explained** — FirstEigen
  - https://firsteigen.com/blog/data-observability-everything-you-need-to-know/

- **Data observability 101: A comprehensive guide (2026)** — Flexera
  - https://www.flexera.com/blog/finops/data-observability/

---

## 6. DataOps

### Practices & Tools
- **What is DataOps? The 2026 Enterprise Guide** — Revefi
  - https://www.revefi.com/blog/what-is-dataops

- **Best DataOps Tools Reviews 2026** — Gartner Peer Insights
  - https://www.gartner.com/reviews/market/dataops-tools

- **DataOps Best Practices and Top Tools in 2026** — lakeFS
  - https://lakefs.io/blog/dataops-best-practices/

- **DataOps in Practice: Principles, Lifecycle & Tips for Success** — Dagster
  - https://dagster.io/learn/dataops

- **DataOps: A Comprehensive Guide to Mastering Agile Data Management** — BuzzClan
  - https://buzzclan.com/data-engineering/what-is-dataops/

- **22 best DataOps tools for data management and observability (2026)** — Flexera
  - https://www.flexera.com/blog/finops/best-dataops-tools-optimize-data-management-observability-2023/

- **DataOps 101: An intro to data management and observability (2026)** — Flexera
  - https://www.flexera.com/blog/finops/dataops-101-an-introduction-to-this-essential-approach-to-data-management/

---

## 7. FinOps for Data Platforms

- **Data FinOps** — Seemore Data
  - https://seemoredata.io/glossary/data-finops/

- **AI-Powered Cloud Cost Optimization: Best Practices for FinOps** — Revefi
  - https://www.revefi.com/blog/ai-powered-cloud-cost-optimization-finops

- **Agentic FinOps for AI: autonomous optimization for Snowflake, Databricks and AI cloud costs** — Flexera
  - https://www.flexera.com/blog/finops/agentic-finops-for-ai-autonomous-optimization-for-snowflake-databricks-and-ai-cloud-costs/

- **Why Data Cloud Platform Warehouse Cost Isn't Enough to Understand Value** — FinOps Foundation
  - https://www.finops.org/insights/finops-for-data-cloud-platforms/

- **FinOps for Data Cloud Platforms: Context for Building a FinOps Practice** — FinOps Foundation
  - https://www.finops.org/wg/finops-data-cloud-platforms/

- **SELECT Announces Automated BigQuery Cost Optimization Early Access Program** — Morningstar
  - https://www.morningstar.com/news/pr-newswire/20260416sf36330/select-announces-automated-bigquery-cost-optimization-early-access-program

- **Databricks Cost Optimization & Cost Management Tool** — Finout
  - https://www.finout.io/finout-databricks-solution

- **Top FinOps Tools for Databricks Data Intelligence Platform in 2026** — SlashDot
  - https://slashdot.org/software/finops/for-databricks/

- **Databricks FinOps Genie — Cost Observability Meets Optimization Insights** — Data + AI Summit 2026
  - https://www.databricks.com/dataaisummit/session/databricks-finops-genie-cost-observability-meets-optimization-insights

---

## 8. Data Lineage (OpenLineage)

- **OpenLineage GitHub** — Open standard for lineage metadata
  - https://github.com/OpenLineage/OpenLineage

- **Getting Started | OpenLineage**
  - https://openlineage.io/getting-started/

- **OpenLineage Specification**
  - https://github.com/OpenLineage/OpenLineage/blob/main/spec/OpenLineage.md

- **How to Handle Data Lineage Tracking** — OneUptime
  - https://oneuptime.com/blog/post/2026-01-24-data-lineage-tracking/view

- **Data Lineage with OpenLineage** — Grandhi Venkata Manideep
  - https://medium.com/@manideepgrandhi02/data-lineage-with-openlineage-8cd095f9eb4e

- **The OpenLineage Standard** — apxml
  - https://apxml.com/courses/data-governance-quality-observability-production/chapter-4-data-lineage-metadata-management/openlineage-standard

- **Column level lineage in Fabric Spark with OpenLineage and stashing the lineage in Delta Lake** — Raki Rahman
  - https://www.rakirahman.me/openlineage-to-delta/

- **Understanding data lineage** — Datadog
  - https://www.datadoghq.com/blog/data-lineage/

- **OpenLineage for a unified lineage view across structured and unstructured data to enable explainable AI** — IBM
  - https://www.ibm.com/new/announcements/openlineage-for-a-unified-lineage-view-across-structured-and-unstructured-data-to-enable-explainable-ai

---

## 9. Data Contracts

### Patterns & Tools
- **Data Contracts Explained: Key Aspects, Tools, Setup in 2026** — Atlan
  - https://atlan.com/data-contracts/

- **Data Contracts for Schema Registry on Confluent Platform** — Confluent
  - https://docs.confluent.io/platform/current/schema-registry/fundamentals/data-contracts.html

- **dbt Data Contracts: Quick Primer With Notes on How to Enforce** — Atlan
  - https://atlan.com/dbt-data-contracts/

- **An Engineer's Guide to Data Contracts - Pt. 2** — Data Products Substack
  - https://dataproducts.substack.com/p/an-engineers-guide-to-data-contracts-6df

- **Data Contract CLI**
  - http://cli.datacontract.com/
  - https://github.com/datacontract/datacontract-cli

- **How to Enforce Schemas with Schema Registry in Kafka**
  - https://oneuptime.com/blog/post/2026-01-25-enforce-schemas-schema-registry-kafka/view

- **Data Contracts: What Are They & Do You Need Them?** — Airbyte
  - https://airbyte.com/data-engineering-resources/data-contracts

### Schema Formats
- **Avro vs Protobuf vs JSON Schema** — Conduktor
  - https://www.conduktor.io/glossary/avro-vs-protobuf-vs-json-schema

- **Schema Evolution in Apache Avro, Protobuf, and JSON Schema** — Java Code Geeks
  - https://www.javacodegeeks.com/2025/06/schema-evolution-in-apache-avro-protobuf-and-json-schema.html

- **Avro vs. JSON Schema vs. Protobuf: Choosing the Right Format for Kafka** — AutoMQ
  - https://www.automq.com/blog/avro-vs-json-schema-vs-protobuf-kafka-data-formats

### Shift-Left Governance
- **Shift-left governance for your dbt centered stack: Data contracts and more!** — Coalesce 2023 (YouTube)
  - https://www.youtube.com/watch?v=2JAtVhCg59o

- **The Shift Left Architecture 2.0: Operational, Analytical and AI Interfaces for Real-Time Data Products** — Kai Waehner
  - https://www.kai-waehner.de/blog/2026/03/23/the-shift-left-architecture-2-0-operational-analytical-and-ai-interfaces-for-real-time-data-products/

- **Implementing shift-left governance in your dbt stack** — dbt Labs (Coalesce 2023)
  - https://www.getdbt.com/resources/coalesce-on-demand/implementing-shift-left-governance-in-your-dbt-stack-practical-application-of-data-contracts-and

- **AI Broke the Data Stack. Now What? My 7 Predictions for 2026** — Metadata Weekly
  - https://metadataweekly.substack.com/p/ai-broke-the-data-stack-now-what

- **The Modern Data Stack's Final Act: Consolidation Masquerading as Unification** — Modern Data 101
  - https://moderndata101.substack.com/p/the-modern-data-stacks-final-act

---

## 10. ML Platform & MLOps

### MLOps Lifecycle
- **MLOps Lifecycle Explained: From Model Training to Monitoring** — Devōt
  - https://devot.team/blog/mlops-lifecycle

- **Understanding MLOps Lifecycle: From Data to Delivery and Automation Pipelines** — Ideas2IT
  - https://www.ideas2it.com/blogs/understanding-mlops-phases-data-delivery

- **MLOps Maturity Model 2026: 4 Stages to Resilient, Risk-Free Machine Learning** — Flexiana
  - https://medium.com/@flexianadevgroup/mlops-maturity-model-2026-4-stages-to-resilient-risk-free-machine-learning-468c097dc25c

- **Ultimate Guide to MLOps 2026: Lifecycle, Tools, Best Practices** — ExpertCisco
  - https://expertcisco.com/what-is-mlops/

- **MLOps Principles** — ml-ops.org
  - https://ml-ops.org/content/mlops-principles

- **Three Levels of ML Software** — ml-ops.org
  - https://ml-ops.org/content/three-levels-of-ml-software

- **What is MLOps? Lifecycle & Deployment Guide** — Ultralytics
  - https://www.ultralytics.com/glossary/machine-learning-operations-mlops

- **Understanding MLops Lifecycle: From Data to Deployment** — ProjectPro
  - https://www.projectpro.io/article/mlops-lifecycle/885

- **Ultimate Guide to MLOps Process and Best Practices, 2026** — Glasier Inc
  - https://www.glasierinc.com/blog/machine-learning-operations-mlops-guide

- **What is MLOps?** — Databricks
  - https://www.databricks.com/blog/what-is-mlops

- **MLOps: A Practical Guide To Production Machine Learning** — ml4devs
  - https://www.ml4devs.com/what-is/mlops/

### Model Registry & Versioning
- **ML Model Registry** — MLflow AI Platform
  - https://mlflow.org/docs/latest/ml/model-registry/

- **MLflow Data Versioning: Techniques, Tools & Best Practices** — lakeFS
  - https://lakefs.io/blog/mlflow-data-versioning/

- **Model Versioning Infrastructure: Managing ML Artifacts at Scale** — Introl
  - https://introl.com/blog/model-versioning-infrastructure-mlops-artifact-management-guide-2025

- **MLflow Model Registry**
  - https://mlflow.openml.io/docs/latest/ml/model-registry/

- **7 MLflow Model Registry Practices That Age Well** — Nexumo
  - https://medium.com/@Nexumo_/7-mlflow-model-registry-practices-that-age-well-4a526d0c9c64

- **Manage model lifecycle using the Workspace Model Registry** — Databricks
  - https://docs.databricks.com/aws/en/machine-learning/manage-model-lifecycle/workspace-model-registry

- **MLflow Model Registry: Workflows, Benefits & Challenges** — lakeFS
  - https://lakefs.io/blog/mlflow-model-registry/

- **Model and Data Versioning: An Introduction to mlflow and DVC** — Walmart Global Tech
  - https://medium.com/walmartglobaltech/model-and-data-versioning-an-introduction-to-mlflow-and-dvc-260347cd0f6e

- **AI Model Versioning Best Practices: MLOps Guide for Enterprises** — Atlan
  - https://atlan.com/know/ai-model-versioning-best-practices/

- **Model Registry Workflows** — MLflow AI Platform
  - https://mlflow.org/docs/latest/ml/model-registry/workflow/

### Feature Stores
- **Introduction** — Feast: the Open Source Feature Store
  - https://docs.feast.dev

- **Real-Time Feature Store in 2026: Beyond Batch ML Pipelines** — RisingWave
  - https://risingwave.com/blog/real-time-feature-store-2026/

- **Solving the Training-Serving Skew Problem with Feast Feature Store** — Dan Zimmerman
  - https://medium.com/@scoopnisker/solving-the-training-serving-skew-problem-with-feast-feature-store-3719b47e23a2

- **Feature Store Comparison: Feast vs Tecton vs Databricks [2026]** — Tacnode
  - https://tacnode.io/post/how-to-evaluate-a-feature-store

- **What Is a Feature Store?** — Tecton/Databricks
  - https://www.databricks.com/blog/what-is-a-feature-store

- **What is a Feature Store?** — Feast
  - https://feast.dev/blog/what-is-a-feature-store/

- **Top 5 Feature Stores in 2025: Tecton, Feast, and Beyond** — GoCodeo
  - https://www.gocodeo.com/post/top-5-feature-stores-in-2025-tecton-feast-and-beyond

- **Feature Stores for MLOps: Real-Time Feature Engineering, Feast & Tecton Guide** — DataTalks.Club
  - https://datatalks.club/podcast/mlops-feature-stores-feature-stores-feast-tecton.html

- **What Is a Feature Store? Feast, Tecton & AWS Compared** — Tacnode
  - https://tacnode.io/post/what-is-an-online-feature-store-definition-architecture-use-cases

- **How do feature stores work in modern ML pipelines (like Feast or Tecton)?** — NS Academy
  - https://medium.com/@sharetonschool/how-do-feature-stores-work-in-modern-ml-pipelines-like-feast-or-tecton-a94ce5c6d49c

### Model Monitoring & Drift Detection
- **Data Drift: Key Detection and Monitoring Techniques in 2026** — Label Your Data
  - https://labelyourdata.com/articles/machine-learning/data-drift

- **Drift Detection in Robust Machine Learning Systems** — Towards Data Science
  - https://towardsdatascience.com/drift-detection-in-robust-machine-learning-systems/

- **What Is Model Drift?** — IBM
  - https://www.ibm.com/think/topics/model-drift

- **Understanding Model Drift and Data Drift in LLMs (2026 Guide)** — Orq.ai
  - https://orq.ai/blog/model-vs-data-drift

- **Model Drift in Production (2026): Detection, Monitoring & Response Runbook** — All Days Tech
  - https://alldaystech.com/guides/artificial-intelligence/model-drift-detection-monitoring-response

- **From concept drift to model degradation: An overview on performance-aware drift detectors** — ScienceDirect
  - https://www.sciencedirect.com/science/article/pii/S0950705122002854

- **What is data drift in ML, and how to detect and handle it** — Evidently AI
  - https://www.evidentlyai.com/ml-in-production/data-drift

- **Model Drift in Streaming: When ML Models Degrade in Real-Time** — Conduktor
  - https://www.conduktor.io/glossary/model-drift-in-streaming

- **AI Drift Detection: We Tested the 11 Best Monitoring Tools for 2026** — AppIntent
  - https://www.appintent.com/software/ai/drift-detection/

- **Understanding Data Drift and Model Drift: Drift Detection in Python** — DataCamp
  - https://www.datacamp.com/tutorial/understanding-data-drift-model-drift

### Model Serving Patterns
- **Serving Machine Learning Models at Scale: A Guide to Inference Optimization** — Sealos
  - https://sealos.io/blog/serving-machine-learning-models-at-scale-a-guide-to-inference-optimization/

- **Model Serving Patterns: From Batch to Real-Time Inference** — Nerd Level Tech
  - https://nerdleveltech.com/model-serving-patterns-from-batch-to-real-time-inference

- **ML System Design: A Complete Guide (2026)** — System Design Handbook
  - https://www.systemdesignhandbook.com/guides/ml-system-design/

- **Real-Time ML Pipelines: Machine Learning on Streaming Data** — Conduktor
  - https://www.conduktor.io/glossary/real-time-ml-pipelines

- **Deploy models for batch inference and prediction** — Databricks
  - https://docs.databricks.com/aws/en/machine-learning/model-inference

- **Feature Serving and Model Inference** — Feast
  - https://docs.feast.dev/getting-started/architecture/model-inference

- **Serving ML Models in Production: Common Patterns** — Anyscale
  - https://www.anyscale.com/blog/serving-ml-models-in-production-common-patterns

- **Bento: Run Inference at Scale**
  - https://www.bentoml.com/

---

## 11. AI Platform & LLMOps

### LLMOps Foundations
- **The Complete MLOps/LLMOps Roadmap for 2026: Building Production-Grade AI Systems** — Sanjeeb Panda
  - https://medium.com/@sanjeebmeister/the-complete-mlops-llmops-roadmap-for-2026-building-production-grade-ai-systems-bdcca5ed2771

- **LLMOps Architecture: Managing Large Language Models in Production 2026** — Calmops
  - https://calmops.com/architecture/llmops-architecture-managing-llm-production-2026/

- **LLMOps Explained: The Complete 2026 Guide to LLM Operations** — ZedTreeo
  - https://zedtreeo.com/llmops-explained-guide-2026/

- **LLMOps: From Prototype to Production** — Comet
  - https://www.comet.com/site/blog/llmops/

- **LLMOps in 2026: The 10 Tools Every Team Must Have** — KDnuggets
  - https://www.kdnuggets.com/llmops-in-2026-the-10-tools-every-team-must-have

- **LLM Orchestration in 2026: Frameworks + Best Practices** — Orq.ai
  - https://orq.ai/blog/llm-orchestration

- **LLM Observability** — Fiddler AI
  - https://www.fiddler.ai/llmops

- **What is LLMOps? LLM Operations Guide** — MLflow
  - https://mlflow.org/llmops

- **Mastering LLM Techniques: LLMOps** — NVIDIA
  - https://developer.nvidia.com/blog/mastering-llm-techniques-llmops/

- **Secure MLOps in 2026: Guardrails, Signing, Supply Chain** — Blockchain Council
  - https://www.blockchain-council.org/ai/secure-mlops-devsecmlops/

---

## 12. RAG (Retrieval-Augmented Generation)

### RAG Production Architecture
- **Chunking, Hybrid Search, and Reranking: What Actually Improves RAG** — Garima Yadav
  - https://medium.com/@garima_yadav/chunking-hybrid-search-and-reranking-what-actually-improves-rag-de3d453c9059

- **RAG Production Guide 2026: Retrieval-Augmented Generation** — Lushbinary
  - https://lushbinary.com/blog/rag-retrieval-augmented-generation-production-guide/

- **Advanced RAG Techniques for High-Performance LLM Applications** — Neo4j
  - https://neo4j.com/blog/genai/advanced-rag-techniques/

- **Building Production RAG: Architecture, Chunking, Evaluation & Monitoring (2026 Guide)** — Premai
  - https://blog.premai.io/building-production-rag-architecture-chunking-evaluation-monitoring-2026-guide/

- **RAG Is Not Dead: Advanced Retrieval Patterns That Actually Work in 2026** — Young Gao (DEV.to)
  - https://dev.to/young_gao/rag-is-not-dead-advanced-retrieval-patterns-that-actually-work-in-2026-2gbo

- **Building Contextual RAG Systems with Hybrid Search and Reranking** — Analytics Vidhya
  - https://www.analyticsvidhya.com/blog/2024/12/contextual-rag-systems-with-hybrid-search-and-reranking/

- **9 advanced RAG techniques to know & how to implement them** — Meilisearch
  - https://www.meilisearch.com/blog/rag-techniques

- **All you need to know about RAG (in 2026)** — Aishwarya Srinivasan
  - https://aishwaryasrinivasan.substack.com/p/all-you-need-to-know-about-rag-in

- **Reranking Models Improving RAG: Boost Accuracy by 27% & Transform LLMs** — Cognitive Today
  - https://www.cognitivetoday.com/2026/05/reranking-models-improving-rag/

- **Smart Chunking & Embeddings for RAG** — Ashok (DEV.to)
  - https://dev.to/ashokan/smart-chunking-embeddings-for-rag-4ok

---

## 13. Vector Databases

- **Vector Databases for AI Agents 2026: 8 DBs Compared** — Digital Applied
  - https://www.digitalapplied.com/blog/vector-databases-for-ai-agents-pinecone-qdrant-2026

- **Vector Database Comparison: Pinecone vs Weaviate vs Qdrant vs FAISS vs Milvus vs Chroma (2025)** — LiquidMetal AI
  - https://liquidmetal.ai/casesAndBlogs/vector-comparison/

- **Vector Database Comparison 2026: Pinecone vs Weaviate vs Milvus** — Iternal
  - https://iternal.ai/blockify-vector-databases

- **Best Vector Databases in 2026: A Complete Comparison Guide** — Firecrawl
  - https://www.firecrawl.dev/blog/best-vector-databases

- **Best Vector Database 2025: Pinecone vs Weaviate vs Qdrant vs Milvus** — TensorBlue
  - https://tensorblue.com/blog/vector-database-comparison-pinecone-weaviate-qdrant-milvus-2025

- **Vector Databases Compared: Pinecone vs Qdrant vs Weaviate** — Let's Data Science
  - https://letsdatascience.com/blog/vector-databases-compared-pinecone-qdrant-weaviate-milvus-and-more

- **Choosing the Right Vector Database** — Medium
  - https://medium.com/@elisheba.t.anderson/choosing-the-right-vector-database-opensearch-vs-pinecone-vs-qdrant-vs-weaviate-vs-milvus-vs-037343926d7e

- **How to Choose the Right Vector Database: A Comparison Guide** — AltexSoft
  - https://www.altexsoft.com/blog/vector-databases-compared/

- **Best Vector Databases 2026: Pinecone, Chroma, Qdrant & More** — DataCamp
  - https://www.datacamp.com/blog/the-top-5-vector-databases

- **Exploring Vector Databases** — Mehmet Ozkaya
  - https://mehmetozkaya.medium.com/exploring-vector-databases-pinecone-chroma-weaviate-qdrant-milvus-pgvector-and-redis-f0618fe9e92d

---

## 14. LLM Evaluation

- **DeepEval: The LLM Evaluation Framework** — GitHub
  - https://github.com/confident-ai/deepeval

- **LLM as a Judge: A 2026 Guide to Automated Model Assessment** — Label Your Data
  - https://labelyourdata.com/articles/llm-as-a-judge

- **Build an LLM Evaluation Framework: Metrics, Methods & Tools** — Codecademy
  - https://www.codecademy.com/article/build-an-llm-evaluation-framework

- **Awesome AI Evaluation Guide** — GitHub (hparreao)
  - https://github.com/hparreao/Awesome-AI-Evaluation-Guide

- **Evaluation Tools for RAG & LLM Systems: Foundation** — Rachit Lohani
  - https://rlohani.medium.com/evaluation-tools-for-rag-llm-systems-foundation-af2e6a19634b

- **Ragas Documentation**
  - https://docs.ragas.io/en/stable/

- **RAGAS | DeepEval by Confident AI**
  - https://deepeval.com/docs/metrics-ragas

- **RAGAS, TruLens, DeepEval: LLM Evaluation Frameworks (2026)** — Atlan
  - https://atlan.com/know/llm-evaluation-frameworks-compared/

- **LLM Evaluation in 2025: Metrics, RAG, LLM-as-Judge & Best Practices** — QuarkAndCode
  - https://medium.com/@QuarkAndCode/llm-evaluation-in-2025-metrics-rag-llm-as-judge-best-practices-ad2872cfa7cb

- **Align an LLM as a Judge** — Ragas
  - https://docs.ragas.io/en/stable/howtos/applications/align-llm-as-judge/

---

## 15. AI Safety & Guardrails

- **NeMo Guardrails GitHub** — NVIDIA
  - https://github.com/NVIDIA-NeMo/Guardrails

- **AI Guardrails & Cybersecurity-AI Agents, Red Teaming HandsOn** — Udemy
  - https://www.udemy.com/course/ethical-secure-ai-guardrailsai-nvidia-nemo-guardrails/

- **Practical AI Guardrails: Types, Tools & Detection Methods** — Tredence
  - https://www.tredence.com/blog/ai-guardrails-types-tools-detection

- **Essential Guide to LLM Guardrails: Llama Guard, NeMo** — Sunil Rao
  - https://medium.com/data-science-collective/essential-guide-to-llm-guardrails-llama-guard-nemo-d16ebb7cbe82

- **NVIDIA NeMo Guardrails for Developers** — NVIDIA
  - https://developer.nvidia.com/nemo-guardrails

- **LLM Guardrails: The Complete Guide to AI Safety Guardrails (2026)** — AI Safety Directory
  - https://aisecurityandsafety.org/en/guides/llm-guardrails/

- **Guardrails AI and NVIDIA NeMo Guardrails - A Comprehensive Approach to AI Safety**
  - https://guardrailsai.com/blog/nemoguardrails-integration

- **What Are LLM Guardrails? A Guide to Safer AI Responses** — Openxcell
  - https://www.openxcell.com/blog/llm-guardrails/

- **NeMo Guardrails, the Ultimate Open-Source LLM Security Toolkit** — Towards Data Science
  - https://towardsdatascience.com/nemo-guardrails-the-ultimate-open-source-llm-security-toolkit-0a34648713ef/

- **LLM Guardrails: Securing LLMs for Safe AI Deployment** — WitnessAI
  - https://witness.ai/blog/llm-guardrails/

---

## 16. Agentic AI

- **CrewAI vs LangGraph vs AutoGen: Choosing the Right Multi-Agent AI Framework** — DataCamp
  - https://www.datacamp.com/tutorial/crewai-vs-langgraph-vs-autogen

- **Top 5 AI Agent Frameworks 2026: LangGraph, CrewAI & More** — Intuz
  - https://www.intuz.com/blog/top-5-ai-agent-frameworks-2025

- **Best Multi-Agent Frameworks in 2026: LangGraph, CrewAI** — GuruSup
  - https://gurusup.com/blog/best-multi-agent-frameworks-2026

- **Orchestration Frameworks for Agentic AI: LangChain, AutoGen, CrewAI** — MHTechIn
  - https://www.mhtechin.com/support/orchestration-frameworks-for-agentic-ai-langchain-autogen-crewai-the-complete-2026-guide/

- **LangGraph vs CrewAI vs AutoGen: Top 10 AI Agent Frameworks** — o-mega
  - https://o-mega.ai/articles/langgraph-vs-crewai-vs-autogen-top-10-agent-frameworks-2026

- **CrewAI vs LangGraph vs AutoGen vs OpenAgents (2026)** — OpenAgents Blog
  - https://openagents.org/blog/posts/2026-02-23-open-source-ai-agent-frameworks-compared

- **AI Agent Frameworks for Developers: LangChain vs CrewAI vs AutoGen in 2026** — Fungies
  - https://fungies.io/ai-agent-frameworks-langchain-crewai-autogen-2026/

- **CrewAI vs AutoGen vs LangGraph: Which Multi-Agent Framework in 2026?** — agdex_ai (DEV.to)
  - https://dev.to/agdex_ai/crewai-vs-autogen-vs-langgraph-which-multi-agent-framework-in-2026-51m6

- **10 AI Agent Frameworks You Should Know in 2026** — ATNO
  - https://medium.com/@atnoforgenai/10-ai-agent-frameworks-you-should-know-in-2026-langgraph-crewai-autogen-more-2e0be4055556

- **Which AI Agent Framework Should You Choose? LangChain vs LlamaIndex vs AutoGen vs CrewAI for Enterprise (2026)** — TechAhead
  - https://www.techaheadcorp.com/blog/top-agent-frameworks/

---

## 17. Recommended Substacks & Continuous Learning

### Substacks
- **moderndata101.substack.com** — 2026 trends, evolution
- **Practical Data Modeling** by Joe Reis — fundamentals
- **dataproducts.substack.com** — Data Contracts deep dives
- **Metadata Weekly** — metadata + governance
- **AI with Aish (Aishwarya Srinivasan)** — RAG, LLMs

### Communities
- **DataTalks.Club** — podcast + community
- **Latent Space** — AI engineering
- **MLOps Community** — Slack + meetups

---

## 18. Vendor Documentation (Authoritative)

### Storage / Compute
- **Apache Iceberg** — https://iceberg.apache.org/
- **Delta Lake** — https://delta.io/
- **Apache Hudi** — https://hudi.apache.org/

### Orchestration
- **Apache Airflow** — https://airflow.apache.org/
- **Dagster** — https://dagster.io/
- **Prefect** — https://www.prefect.io/

### Quality & Observability
- **Great Expectations** — https://docs.greatexpectations.io/
- **Soda** — https://docs.soda.io/
- **Evidently** — https://docs.evidentlyai.com/
- **dbt tests** — https://docs.getdbt.com/docs/build/tests

### ML Platforms
- **MLflow** — https://mlflow.org/
- **Kubeflow** — https://www.kubeflow.org/
- **Vertex AI** — https://cloud.google.com/vertex-ai
- **SageMaker** — https://aws.amazon.com/sagemaker/

### LLM Frameworks
- **LangChain** — https://langchain.com/
- **LangGraph** — https://github.com/langchain-ai/langgraph
- **CrewAI** — https://crewai.com/
- **LlamaIndex** — https://www.llamaindex.ai/
- **AutoGen** — https://microsoft.github.io/autogen/

### Vector DBs
- **Pinecone** — https://www.pinecone.io/
- **Qdrant** — https://qdrant.tech/
- **Weaviate** — https://weaviate.io/
- **Milvus** — https://milvus.io/
- **Vertex Vector Search** — https://cloud.google.com/vertex-ai/docs/matching-engine/overview

### Eval & Observability for AI
- **Langfuse** — https://langfuse.com/
- **DeepEval** — https://docs.confident-ai.com/
- **Ragas** — https://docs.ragas.io/
- **TruLens** — https://www.trulens.org/
- **Arize Phoenix** — https://phoenix.arize.com/

---

## 19. How to Use These References

### When you forget a concept
→ Look at section that covers it, click first 2-3 sources

### When you're designing
→ Read 2026 architecture references first
→ Then drill into vendor documentation for specifics

### When you're evaluating tools
→ Compare from 3+ sources
→ Always include vendor docs + independent comparison

### When you're learning
→ Books > Substacks > Vendor docs > Random Medium articles

---

## 20. Document Cross-References

Documents in this folder reference these sources for:

- **Modern_Data_AI_Platform_Blueprint.md**: Sections 2 (Architecture), 3 (GCP Lakehouse)
- **Data_Platform_Capabilities_Reference.md**: Section 1 (Joe Reis), 5 (DQ), 6 (Observability)
- **Data_Platform_Capabilities_Deep_Dive.md**: Sections 8 (Lineage), 9 (Contracts), 7 (FinOps)
- **ML/01-04**: Section 10 (ML Platform & MLOps)
- **AI/01_AI_Platform_Overview.md**: Sections 11, 12, 13, 14
- **AI/02_RAG_Architecture.md**: Sections 12, 13
- **AI/03_LLMOps_and_Evaluation.md**: Sections 11, 14, 15
- **AI/04_Agentic_AI_Patterns.md**: Section 16

---

## Note on URL Stability

URLs ใน 2026 อาจเปลี่ยน — ถ้า link พัง ค้นหาด้วย title เดิม + ปี
ส่วนใหญ่ source เหล่านี้เป็น primary sources ที่จะยังอยู่ในระยะยาว
