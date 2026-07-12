output "bucket_name" {
  value       = google_storage_bucket.this.name
  description = "The created bucket's name, for reference by other modules (e.g., IAM bindings)."
}

output "bucket_self_link" {
  value       = google_storage_bucket.this.self_link
  description = "The created bucket's self_link."
}

output "bucket_url" {
  value       = google_storage_bucket.this.url
  description = "The gs:// URL of the created bucket."
}
