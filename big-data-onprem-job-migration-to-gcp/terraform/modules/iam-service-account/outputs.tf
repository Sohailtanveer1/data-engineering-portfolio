output "email" {
  value       = google_service_account.this.email
  description = "The created service account's email, for use as a Dataproc cluster identity or in downstream IAM bindings."
}

output "name" {
  value       = google_service_account.this.name
  description = "The created service account's fully-qualified resource name."
}
