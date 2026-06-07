output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "bucket_name" {
  description = "GCS bucket name"
  value       = google_storage_bucket.data_platform_bucket.name
}