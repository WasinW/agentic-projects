#!/usr/bin/env python3
"""
GCP Data Platform Project Parser
Parses gcp_data_platform_project.scala and creates project structure with actual content
"""

import os
import re
import sys
from pathlib import Path

def create_project_structure(content):
    """Parse the scala file content and create project structure"""
    
    project_name = "gcp-data-platform"
    base_path = Path(project_name)
    
    print(f"=== Creating GCP Data Platform Project from Source Content ===")
    print(f"Project: {project_name}")
    
    # Create base directory
    base_path.mkdir(exist_ok=True)
    os.chdir(base_path)
    
    print("Parsing content and creating files...")
    
    # Split content by file markers
    file_pattern = r'// File: (.+?)(?=\n)'
    files = re.split(file_pattern, content)
    
    current_file = None
    current_content = []
    created_files = []
    
    for i, part in enumerate(files):
        if i == 0:
            continue  # Skip content before first file marker
            
        if i % 2 == 1:  # File path
            # Save previous file if exists
            if current_file and current_content:
                save_file(current_file, '\n'.join(current_content))
                created_files.append(current_file)
            
            current_file = part.strip()
            current_content = []
            
        else:  # File content
            # Clean up the content
            lines = part.strip().split('\n')
            # Remove empty lines at the beginning and end
            while lines and not lines[0].strip():
                lines.pop(0)
            while lines and not lines[-1].strip():
                lines.pop()
            
            current_content = lines
    
    # Save the last file
    if current_file and current_content:
        save_file(current_file, '\n'.join(current_content))
        created_files.append(current_file)
    
    # Create additional required directories and files
    create_additional_structure()
    
    # Create README and other root files
    create_root_files()
    
    print(f"\n✅ Successfully created {len(created_files)} files!")
    print("\n📁 Files created:")
    for file_path in sorted(created_files):
        print(f"   ✓ {file_path}")
    
    print("\n🚀 Next steps:")
    print(f"1. cd {project_name}")
    print("2. Set environment variables:")
    print("   export GOOGLE_CLOUD_PROJECT='your-project-id'")
    print("   export GCS_BUCKET='your-bucket-name'")
    print("3. Run deployment: ./deployment/scripts/build-and-deploy.sh")

def save_file(file_path, content):
    """Save content to file, creating directories as needed"""
    path = Path(file_path)
    
    # Create parent directories
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write content to file
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Make scripts executable
    if file_path.endswith('.sh'):
        os.chmod(path, 0o755)

def create_additional_structure():
    """Create additional directories and files that might be missing"""
    
    additional_dirs = [
        "backend-service/src/test/scala",
        "dataflow-templates/file-streaming-processor/src/main/java/com/dataplatform/dataflow",
        "dataform-pipelines/materialized-views/definitions",
        "deployment/configs",
        "monitoring/alerts"
    ]
    
    for dir_path in additional_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create missing files with basic content
    missing_files = {
        "backend-service/src/main/scala/com/dataplatform/ingestion/BatchIngestion.scala": """package com.dataplatform.ingestion

import org.apache.spark.sql.SparkSession
import com.dataplatform.core._

object BatchIngestion {
  def main(args: Array[String]): Unit = {
    // TODO: Implement batch ingestion logic
    println("Batch Ingestion - To be implemented")
  }
}""",
        
        "backend-service/src/main/scala/com/dataplatform/ingestion/FileIngestion.scala": """package com.dataplatform.ingestion

import org.apache.spark.sql.SparkSession
import com.dataplatform.core._

object FileIngestion {
  def main(args: Array[String]): Unit = {
    // TODO: Implement file ingestion logic
    println("File Ingestion - To be implemented")
  }
}""",
        
        "backend-service/src/main/scala/com/dataplatform/transformation/DataTransformer.scala": """package com.dataplatform.transformation

import org.apache.spark.sql.{DataFrame, SparkSession}

class DataTransformer(spark: SparkSession) {
  
  def transform(df: DataFrame): DataFrame = {
    // TODO: Implement transformation logic
    df
  }
}""",
        
        "backend-service/src/main/scala/com/dataplatform/transformation/DataQuality.scala": """package com.dataplatform.transformation

import org.apache.spark.sql.{DataFrame, SparkSession}

class DataQuality(spark: SparkSession) {
  
  def checkQuality(df: DataFrame): Boolean = {
    // TODO: Implement data quality checks
    true
  }
}""",
        
        "backend-service/src/main/scala/com/dataplatform/monitoring/MetricsCollector.scala": """package com.dataplatform.monitoring

import org.apache.spark.sql.SparkSession

class MetricsCollector(spark: SparkSession) {
  
  def collectMetrics(): Unit = {
    // TODO: Implement metrics collection
    println("Collecting metrics...")
  }
}""",
        
        "backend-service/src/main/scala/com/dataplatform/config/ConfigManager.scala": """package com.dataplatform.config

import org.apache.spark.sql.SparkSession
import com.typesafe.config.{Config, ConfigFactory}

class ConfigManager(spark: SparkSession, projectId: String) {
  
  private val config: Config = ConfigFactory.load()
  
  def getProjectId: String = {
    sys.env.getOrElse("GOOGLE_CLOUD_PROJECT", 
      config.getString("dataplatform.project-id"))
  }
  
  def getGcsBucket: String = {
    sys.env.getOrElse("GCS_BUCKET", 
      config.getString("dataplatform.gcs-bucket"))
  }
}""",
        
        "backend-service/src/main/resources/application.conf": """dataplatform {
  project-id = ${?GOOGLE_CLOUD_PROJECT}
  gcs-bucket = ${?GCS_BUCKET}
  
  iceberg {
    warehouse = "gs://"${dataplatform.gcs-bucket}"/iceberg-warehouse"
    catalog-type = "hadoop"
  }
  
  monitoring {
    audit-table = ${dataplatform.project-id}".monitoring.audit_logs"
    lineage-table = ${dataplatform.project-id}".monitoring.data_lineage"
  }
  
  validation {
    quality-threshold = 0.5
    max-error-rate = 0.1
  }
}""",
        
        "data-pipelines/ingestion/postgres-ingestion.scala": """// PostgreSQL Ingestion Pipeline
// TODO: Implement PostgreSQL ingestion logic""",
        
        "data-pipelines/ingestion/file-ingestion.scala": """// File Ingestion Pipeline
// TODO: Implement file ingestion logic""",
        
        "data-pipelines/ingestion/kafka-ingestion.scala": """// Kafka Ingestion Pipeline
// TODO: Implement Kafka ingestion logic""",
        
        "data-pipelines/transformation/structured-to-refined.scala": """// Structured to Refined Transformation
// TODO: Implement structured to refined transformation""",
        
        "data-pipelines/transformation/refined-to-analysis.scala": """// Refined to Analysis Transformation
// TODO: Implement refined to analysis transformation""",
        
        "data-pipelines/validation/data-quality-check.scala": """// Data Quality Check Pipeline
// TODO: Implement data quality validation""",
        
        "dataflow-templates/file-streaming-processor/pom.xml": """<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.dataplatform</groupId>
    <artifactId>file-streaming-processor</artifactId>
    <version>1.0.0</version>
    
    <properties>
        <beam.version>2.50.0</beam.version>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.apache.beam</groupId>
            <artifactId>beam-sdks-java-core</artifactId>
            <version>${beam.version}</version>
        </dependency>
    </dependencies>
</project>""",
        
        "dataform-pipelines/materialized-views/dataform.json": """{
  "defaultSchema": "analysis",
  "assertionSchema": "dataform_assertions",
  "warehouse": "bigquery",
  "defaultLocation": "US"
}""",
        
        "deployment/terraform/variables.tf": """variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "bucket_name" {
  description = "GCS Bucket Name"
  type        = string
}""",
        
        "deployment/terraform/outputs.tf": """output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "bucket_name" {
  description = "GCS bucket name"
  value       = google_storage_bucket.data_platform_bucket.name
}""",
        
        "deployment/configs/dev.conf": """dataplatform {
  project-id = "dev-project"
  gcs-bucket = "dev-bucket"
  validation.quality-threshold = 0.3
}""",
        
        "deployment/configs/prod.conf": """dataplatform {
  project-id = "prod-project"
  gcs-bucket = "prod-bucket"
  validation.quality-threshold = 0.8
}""",
        
        "monitoring/alerts/pipeline-alerts.yaml": """# Pipeline Alert Policies
alertPolicy:
  displayName: "Data Pipeline Failures"
  documentation:
    content: "Alert when data pipeline jobs fail"
  conditions:
  - displayName: "Job failure rate"
    conditionThreshold:
      filter: 'resource.type="dataproc_cluster"'
      comparison: "COMPARISON_GT"
      thresholdValue: 0
  enabled: true""",
        
        "docs/troubleshooting.md": """# Troubleshooting Guide

## Common Issues

### 1. Build Failures
- Check sbt version compatibility
- Clear sbt cache: `sbt clean`

### 2. Deployment Issues
- Verify GCP authentication
- Check required APIs are enabled

### 3. Pipeline Failures
- Review Dataproc logs
- Check Secret Manager permissions

## Getting Help
- Check GCP Console logs
- Review BigQuery audit tables
- Contact platform team
"""
    }
    
    for file_path, content in missing_files.items():
        if not Path(file_path).exists():
            save_file(file_path, content)

def create_root_files():
    """Create root-level files"""
    
    # .gitignore
    gitignore_content = """# Scala/SBT
target/
*.class
*.log
*.jar
*.war
*.nar
*.ear
*.zip
*.tar.gz
*.rar

# IDE
.idea/
*.iml
*.ipr
*.iws
.vscode/

# OS
.DS_Store
Thumbs.db

# Terraform
*.tfstate
*.tfstate.*
.terraform/
.terraform.lock.hcl

# Logs
logs/
*.log

# Temporary files
tmp/
temp/
"""
    
    # README.md
    readme_content = """# GCP Data Platform

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
"""
    
    save_file(".gitignore", gitignore_content)
    save_file("README.md", readme_content)

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python3 create_gcp_project.py <path_to_gcp_data_platform_project.scala>")
        sys.exit(1)
    
    scala_file_path = sys.argv[1]
    
    if not os.path.exists(scala_file_path):
        print(f"Error: File {scala_file_path} not found!")
        sys.exit(1)
    
    # Read the scala file
    try:
        with open(scala_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # Extract content starting from "BACKEND SERVICE CORE"
    backend_start = content.find("// BACKEND SERVICE CORE")
    if backend_start == -1:
        print("Error: Could not find '// BACKEND SERVICE CORE' marker in the file")
        sys.exit(1)
    
    relevant_content = content[backend_start:]
    
    # Create project structure
    try:
        create_project_structure(relevant_content)
    except Exception as e:
        print(f"Error creating project structure: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
