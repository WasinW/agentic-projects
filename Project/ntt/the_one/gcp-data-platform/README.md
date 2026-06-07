# GCP Data Platform

A comprehensive data platform solution for Google Cloud Platform.

## 🏗️ Architecture

```
Data Sources → Ingestion → Raw Zone → Transformation → Structured → Refined → Analysis
     ↓              ↓           ↓            ↓             ↓          ↓         ↓
   Oracle         Dataproc     GCS       Dataproc      Iceberg    BigQuery   ML/BI
   PostgreSQL     Dataflow   Iceberg      BigQuery      Format      SQL      Tools
   Files/APIs     
```

## 🚀 Quick Start

1. **Set environment variables:**
   ```bash
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export GCS_BUCKET="your-bucket-name"
   ```

2. **Deploy infrastructure:**
   ```bash
   ./deployment/scripts/build-and-deploy.sh
   ```

3. **Configure secrets:**
   ```bash
   ./deployment/scripts/setup-secrets.sh
   ```

4. **Run sample pipeline:**
   ```bash
   ./deployment/scripts/run-sample-ingestion.sh
   ```

## 📁 Project Structure

```
gcp-data-platform/
├── backend-service/          # Core Scala services
├── data-pipelines/           # Pipeline implementations  
├── dataflow-templates/       # Real-time processing
├── dataform-pipelines/       # SQL transformations
├── deployment/               # Infrastructure & scripts
├── monitoring/               # Dashboards & alerts
└── docs/                     # Documentation
```

## 📚 Documentation

- [Deployment Guide](docs/deployment-guide.md)
- [Pipeline Guide](docs/pipeline-guide.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🔧 Development

Built with:
- **Scala 2.12** - Backend services
- **Apache Spark 3.5** - Data processing
- **Apache Iceberg** - Data lake format
- **Google Cloud Platform** - Infrastructure
- **Terraform** - Infrastructure as Code

## 📄 License

Copyright 2024 - Data Platform Team
