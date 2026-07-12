variable "project_id" {
  type        = string
  description = "GCP project ID this service account is created in."
}

variable "account_id" {
  type        = string
  description = "Service account ID, convention svc-<domain>-<function> per 13-infrastructure/03-naming-and-tagging-standards.md."

  validation {
    condition     = can(regex("^svc-[a-z0-9-]+$", var.account_id))
    error_message = "account_id must start with 'svc-' per naming convention."
  }
}

variable "display_name" {
  type        = string
  description = "Human-readable display name for the service account."
}

variable "project_roles" {
  type        = list(string)
  default     = []
  description = "Project-level IAM roles to grant. Keep minimal — prefer bucket_bindings/dataset_bindings for resource-scoped access per least-privilege principle in 10-security/01-iam-design.md."
}

variable "bucket_bindings" {
  type        = map(string)
  default     = {}
  description = "Map of bucket_name => role, granting this service account bucket-scoped (not project-wide) storage access."
}

variable "secret_bindings" {
  type        = map(string)
  default     = {}
  description = "Map of secret_id => role (typically roles/secretmanager.secretAccessor), granting per-secret access per 10-security/03-secret-manager-design.md."
}
